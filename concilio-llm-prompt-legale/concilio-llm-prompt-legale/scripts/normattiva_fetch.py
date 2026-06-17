#!/usr/bin/env python3
"""Fetch Italian statute articles from Normattiva for source verification."""

from __future__ import annotations

import argparse
import hashlib
import html
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from legal_panel import (
    ACT_THEN_ARTICLE_RE,
    ARTICLE_THEN_ACT_RE,
    detect_source_citations,
    expand_article_numbers,
    load_cases_json,
    norm_act,
    normattiva_url_for,
    now_iso,
    official_url_for_source,
    source_gate_from_records,
    source_records_from_payload,
    today_iso,
    verification_status_summary,
)


NORMATTIVA_URN_PREFIX = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
NORMATTIVA_ORIGIN = "https://www.normattiva.it"
LIVE_STATUSES = {"verified", "mismatch", "not_found"}


def normalize_text(text: str) -> str:
    replacements = str.maketrans(
        {
            "à": "a",
            "è": "e",
            "é": "e",
            "ì": "i",
            "ò": "o",
            "ù": "u",
        }
    )
    return re.sub(r"\s+", " ", text.lower().translate(replacements)).strip()


def compact_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def write_text_no_overwrite(path: Path, text: str, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json_no_overwrite(path: Path, data: Any, *, force: bool = False) -> None:
    write_text_no_overwrite(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n", force=force)


def safe_stem(*parts: str) -> str:
    base = "__".join(part for part in parts if part)
    base = re.sub(r"[^A-Za-z0-9_.-]+", "-", base).strip("-").lower()
    if len(base) > 80:
        digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
        base = base[:69].rstrip("-") + "-" + digest
    return base or "normattiva-record"


def legacy_act_slug(act: str) -> str | None:
    key = norm_act(act).lower()
    return {
        "d.lgs. 14/2019": "ccii",
        "c.c.": "cc",
        "l.fall.": "lfall",
        "cost.": "cost",
        "c.p.c.": "cpc",
        "c.p.": "cp",
        "c.p.p.": "cpp",
        "c.p.a.": "cpa",
        "tuir": "tuir",
    }.get(key)


def cached_article_html_path(articles_dir: Path, target: dict[str, Any], article: str | None) -> Path | None:
    if not article:
        return None
    slug = legacy_act_slug(str(target.get("act") or ""))
    candidates: list[Path] = []
    if slug:
        candidates.extend(
            [
                articles_dir / f"{slug}-art{article}.html",
                articles_dir / f"{slug}-art{article}.article.html",
            ]
        )
    candidates.extend(sorted(articles_dir.glob(f"*art{article}.html")))
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def excerpt(text: str, limit: int = 700) -> str:
    text = compact_ws(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "..."


def parse_article_and_act(text: str) -> tuple[str | None, str | None]:
    for pattern in (ARTICLE_THEN_ACT_RE, ACT_THEN_ARTICLE_RE):
        match = pattern.search(text)
        if not match:
            continue
        articles = expand_article_numbers(match.group("arts"))
        if not articles:
            continue
        return articles[0], norm_act(match.group("act"))
    return None, None


def normattiva_target_from_record(record: dict[str, Any]) -> dict[str, Any]:
    citation = str(record.get("citation") or "")
    raw_match = str(record.get("raw_match") or "")
    article = str(record.get("article") or "").strip() or None
    act = str(record.get("act") or "").strip() or None
    if not (article and act):
        parsed_article, parsed_act = parse_article_and_act(f"{citation}\n{raw_match}")
        article = article or parsed_article
        act = act or parsed_act

    official_url = str(record.get("official_url") or record.get("urn_url") or "")
    source_type = str(record.get("source_type") or "")
    if source_type != "italian_statute" and (official_url.startswith(NORMATTIVA_URN_PREFIX) or (article and act)):
        source_type = "italian_statute"
    if source_type != "italian_statute":
        return {
            **record,
            "status": "unsupported",
            "finding": "Normattiva fetch supports only Italian statute records.",
        }

    if article and act and (not official_url.startswith(NORMATTIVA_URN_PREFIX) or "~art" not in official_url):
        official_url = normattiva_url_for(act, article)

    return {
        **record,
        "citation": citation or (f"art. {article} {act}" if article and act else "citazione normativa"),
        "article": article,
        "act": act or "",
        "source_type": source_type,
        "preferred_tool": "normattiva",
        "official_url": official_url,
    }


def records_from_cases(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in load_cases_json(path):
        for item in detect_source_citations(case):
            if item.get("source_type") != "italian_statute":
                continue
            records.append(
                {
                    "candidate_id": case.get("candidate_id"),
                    "citation": item.get("citation"),
                    "article": item.get("article"),
                    "act": item.get("act"),
                    "source_type": item.get("source_type"),
                    "preferred_tool": "normattiva",
                    "tool_used": None,
                    "official_url": official_url_for_source(item),
                    "status": "not_performed",
                    "raw_match": item.get("raw_match"),
                }
            )
    return records


def load_input_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.sources:
        payload = json.loads(Path(args.sources).read_text(encoding="utf-8"))
        records = source_records_from_payload(payload)
    else:
        records = records_from_cases(Path(args.cases))

    targets: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        target = normattiva_target_from_record(record)
        if target.get("source_type") != "italian_statute":
            continue
        key = (
            str(target.get("candidate_id") or ""),
            normalize_text(str(target.get("citation") or "")),
            str(target.get("official_url") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        targets.append(target)
    return targets


def article_numeric_id(article: str | None) -> str | None:
    if not article:
        return None
    match = re.match(r"(\d+)", str(article))
    return match.group(1) if match else None


def ensure_endpoint_suffix(endpoint: str) -> str:
    endpoint = html.unescape(endpoint).strip()
    if endpoint.endswith("&"):
        endpoint += "riferimenti=false&qId=&art.imUpdate=false"
    elif "riferimenti=" not in endpoint:
        sep = "&" if "?" in endpoint else "?"
        endpoint += f"{sep}riferimenti=false&qId=&art.imUpdate=false"
    endpoint = endpoint.replace(" ", "%20")
    return urllib.parse.urljoin(NORMATTIVA_ORIGIN, endpoint)


def extract_article_endpoint(page_html: str, article: str | None) -> str | None:
    numeric = article_numeric_id(article)
    if not numeric:
        return None
    matches = re.findall(r"showArticle\((['\"])(.*?)\1\)", page_html, flags=re.DOTALL)
    endpoints: list[str] = []
    for _, raw_endpoint in matches:
        endpoint = html.unescape(raw_endpoint)
        if f"art.idArticolo={numeric}" not in endpoint:
            continue
        if "art.imUpdate=true" in endpoint:
            continue
        endpoints.append(endpoint)
    if not endpoints:
        return None
    return ensure_endpoint_suffix(endpoints[0])


def text_in_vigore_dal(raw_html: str) -> str | None:
    text = re.sub(r"<[^>]+>", " ", raw_html)
    text = html.unescape(text)
    match = re.search(r"Testo\s+in\s+vigore\s+dal:\s*([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})", text, flags=re.I)
    return match.group(1) if match else None


def clean_article_html(raw_html: str, article: str | None) -> str:
    raw_html = re.sub(r"(?is)<!--.*?-->", " ", raw_html)
    raw_html = re.sub(r"(?is)<script.*?</script>", " ", raw_html)
    raw_html = re.sub(r"(?is)<style.*?</style>", " ", raw_html)
    raw_html = re.sub(r"(?i)<br\s*/?>", "\n", raw_html)
    raw_html = re.sub(r"(?i)</(p|div|li|h[1-6]|tr)>", "\n", raw_html)
    raw_html = re.sub(r"<[^>]+>", " ", raw_html)
    text = html.unescape(raw_html).replace("\xa0", " ")
    lines = []
    skip = {
        "articoli",
        "approfondimenti e funzioni",
        "articolo precedente",
        "articolo successivo",
        "torna all'atto",
    }
    for line in text.splitlines():
        line = compact_ws(line)
        if not line or line.lower() in skip:
            continue
        lines.append(line)
    text = "\n".join(lines)
    marker = article_marker_regex(article)
    if marker:
        match = marker.search(text)
        if match:
            text = text[match.start() :]
    for marker_text in ("\nTorna all'atto", "\nMostra riferimenti normativi", "\nApprofondimenti"):
        idx = text.find(marker_text)
        if idx != -1:
            text = text[:idx]
    return text.strip()


def article_marker_regex(article: str | None) -> re.Pattern[str] | None:
    if not article:
        return None
    match = re.match(r"(?P<num>\d+)(?P<suffix>[a-zA-Z]+)?", str(article))
    if not match:
        return None
    num = re.escape(match.group("num"))
    suffix = match.group("suffix")
    if suffix:
        suffix_pattern = r"(?:\s*[- ]?\s*" + re.escape(suffix) + r")"
    else:
        suffix_pattern = ""
    return re.compile(rf"\bArt\.?\s*{num}{suffix_pattern}\b", flags=re.IGNORECASE)


def article_marker_found(text: str, article: str | None) -> bool:
    marker = article_marker_regex(article)
    return bool(marker and marker.search(text))


def vigency_date_from_url(url: str) -> str:
    match = re.search(r"!vig=(\d{4}-\d{2}-\d{2})", url)
    return match.group(1) if match else today_iso()


def request_with_headers(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    timeout: int,
    headers: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    base_headers = {"User-Agent": "Mozilla/5.0"}
    if headers:
        base_headers.update(headers)
    request = urllib.request.Request(url, headers=base_headers)
    with opener.open(request, timeout=timeout) as response:
        status = getattr(response, "status", response.getcode())
        final_url = response.geturl()
        body = response.read().decode("utf-8", errors="replace")
    return int(status), final_url, body


def fetch_normattiva_article(
    target: dict[str, Any],
    *,
    articles_dir: Path,
    timeout: int,
    no_network: bool,
    force: bool,
) -> dict[str, Any]:
    article = str(target.get("article") or "").strip() or None
    official_url = str(target.get("official_url") or "")
    citation = str(target.get("citation") or "")
    stem = safe_stem(str(target.get("candidate_id") or ""), citation, article or "")
    page_file = articles_dir / f"{stem}.page.html"
    html_file = articles_dir / f"{stem}.article.html"
    text_file = articles_dir / f"{stem}.article.txt"

    record = {
        **target,
        "preferred_tool": "normattiva",
        "tool_used": "normattiva_http",
        "official_url": official_url,
        "status": "not_performed",
        "vigente_al": vigency_date_from_url(official_url) if official_url else None,
        "article_text_excerpt": "",
        "finding": "",
        "score_impact": "manual_relevance_check_required",
        "normattiva": {
            "urn_url": official_url,
            "endpoint_url": None,
            "page_html_file": str(page_file),
            "raw_html_file": str(html_file),
            "plain_text_file": str(text_file),
        },
    }

    if not article:
        record.update(
            {
                "status": "unsupported",
                "tool_used": None,
                "finding": "Record normativo senza articolo: lo scarico automatico articolo Normattiva non e' applicabile.",
                "score_impact": "manual_official_check_required",
            }
        )
        return record
    if not official_url.startswith(NORMATTIVA_URN_PREFIX) or "~art" not in official_url:
        record.update(
            {
                "status": "unsupported",
                "tool_used": None,
                "finding": "URL Normattiva URN-NIR articolo non disponibile o atto non presente nella lookup affidabile.",
                "score_impact": "manual_official_check_required",
            }
        )
        return record

    try:
        cached_html = cached_article_html_path(articles_dir, target, article) if no_network else None
        if no_network and not (page_file.exists() or html_file.exists() or cached_html):
            raise RuntimeError("no_network enabled and no cached Normattiva files found")

        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        if page_file.exists() and no_network:
            page_html = page_file.read_text(encoding="utf-8", errors="replace")
            page_status = None
            final_url = official_url
        elif no_network:
            page_html = ""
            page_status = None
            final_url = official_url
        else:
            page_status, final_url, page_html = request_with_headers(opener, official_url, timeout=timeout)
            write_text_no_overwrite(page_file, page_html, force=force)

        endpoint = extract_article_endpoint(page_html, article) if page_html else None
        record["normattiva"]["endpoint_url"] = endpoint
        record["normattiva"]["urn_page_status"] = page_status
        record["normattiva"]["urn_final_url"] = final_url

        if html_file.exists() and no_network:
            article_html = html_file.read_text(encoding="utf-8", errors="replace")
            article_status = None
        elif cached_html:
            article_html = cached_html.read_text(encoding="utf-8", errors="replace")
            article_status = None
            record["normattiva"]["raw_html_file"] = str(cached_html)
        elif endpoint:
            article_status, _, article_html = request_with_headers(
                opener,
                endpoint,
                timeout=timeout,
                headers={
                    "Accept": "text/html, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": official_url,
                },
            )
            write_text_no_overwrite(html_file, article_html, force=force)
        elif page_html:
            article_html = page_html
            article_status = page_status
        else:
            raise RuntimeError("article endpoint not found in Normattiva page")

        text = clean_article_html(article_html, article)
        if not text:
            record.update(
                {
                    "status": "not_found",
                    "finding": "Normattiva ha risposto, ma il testo articolo e' vuoto.",
                    "score_impact": "human_review_required",
                }
            )
            return record
        write_text_no_overwrite(text_file, text + "\n", force=force)
        marker_ok = article_marker_found(text, article)
        record["normattiva"].update(
            {
                "article_status": article_status,
                "plain_text_chars": len(text),
                "text_in_vigore_dal": text_in_vigore_dal(article_html),
            }
        )
        record["article_text_excerpt"] = excerpt(text)
        if marker_ok:
            record.update(
                {
                    "status": "verified",
                    "finding": "Testo articolo scaricato da Normattiva; pertinenza giuridica da verificare separatamente.",
                    "score_impact": "text_exists_relevance_not_checked",
                }
            )
        else:
            record.update(
                {
                    "status": "mismatch",
                    "finding": "Testo scaricato, ma non contiene un marcatore articolo coerente con la citazione.",
                    "score_impact": "human_review_required",
                }
            )
        return record
    except urllib.error.HTTPError as exc:
        status = "not_found" if exc.code == 404 else "unavailable"
        record.update(
            {
                "status": status,
                "finding": f"Errore HTTP Normattiva {exc.code}: {exc.reason}",
                "score_impact": "human_review_required",
            }
        )
        return record
    except (urllib.error.URLError, TimeoutError, RuntimeError, OSError) as exc:
        record.update(
            {
                "status": "unavailable",
                "finding": f"Scarico Normattiva non disponibile: {exc}",
                "score_impact": "manual_official_check_required",
            }
        )
        return record


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# Verifica Normattiva",
        "",
        f"Stato complessivo: `source_verification: {result['status']}`.",
        f"Gate fonti: `source_gate: {result['source_gate']['status']}`.",
        "",
        "Lo scarico conferma reperibilita' e testo dell'articolo su Normattiva. Non decide da solo se la norma sostiene l'uso giuridico fatto dal candidato.",
        "",
        "| Candidato | Citazione | Stato | Link Normattiva | File testo | Esito |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in result["records"]:
        norm = record.get("normattiva") or {}
        text_file = norm.get("plain_text_file") or ""
        finding = compact_ws(str(record.get("finding") or ""))
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(record.get("candidate_id")),
                    md_cell(record.get("citation")),
                    md_cell(record.get("status")),
                    md_cell(record.get("official_url"), maximum=120),
                    md_cell(text_file, maximum=80),
                    md_cell(finding, maximum=120),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def md_cell(value: Any, *, maximum: int = 90) -> str:
    text = "" if value is None else str(value)
    text = compact_ws(text).replace("|", "\\|")
    if len(text) > maximum:
        text = text[: maximum - 1].rstrip() + "..."
    return text or "n.d."


def run(args: argparse.Namespace) -> dict[str, Any]:
    targets = load_input_records(args)
    articles_dir = Path(args.articles_dir)
    articles_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for target in targets:
        records.append(
            fetch_normattiva_article(
                target,
                articles_dir=articles_dir,
                timeout=args.timeout,
                no_network=args.no_network,
                force=args.force,
            )
        )
        if not args.no_network and args.sleep > 0:
            time.sleep(args.sleep)

    status = verification_status_summary(records)
    return {
        "generated_at": now_iso(),
        "status": status,
        "source_verification": {
            "status": status,
            "notes": [
                "Normattiva fetch verifies official article text availability.",
                "Legal relevance remains separate from existence/text verification.",
                "Statuses verified/mismatch/not_found are live official-source outcomes.",
            ],
        },
        "articles_dir": str(articles_dir),
        "source_gate": source_gate_from_records(records),
        "records": records,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--sources", help="source-verification JSON produced by legal_panel.py verify-sources.")
    source.add_argument("--cases", help="panel-input/cases JSON produced by extract or prepare-live.")
    parser.add_argument("--output-json", default="normattiva-verification.json", help="Write verification JSON here.")
    parser.add_argument("--output-md", default="normattiva-verification.md", help="Write Markdown summary here.")
    parser.add_argument("--articles-dir", default="normattiva-articles", help="Directory for downloaded article HTML/TXT.")
    parser.add_argument("--timeout", type=int, default=40, help="HTTP timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.25, help="Delay between live Normattiva requests.")
    parser.add_argument("--no-network", action="store_true", help="Use existing files in --articles-dir; do not call Normattiva.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting generated files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = run(args)
    write_json_no_overwrite(Path(args.output_json), result, force=args.force)
    write_text_no_overwrite(Path(args.output_md), markdown_report(result), force=args.force)
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "status": result["status"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
