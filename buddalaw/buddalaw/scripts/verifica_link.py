#!/usr/bin/env python3
"""Confronta una bozza Markdown con i public_url di risposte MCP salvate in JSON.

Nessuna rete, modifica o correzione automatica. La provenienza dei file deve
essere verificata da chi li fornisce; l'esito non certifica il contenuto legale.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

URL = re.compile(r'https?://[^\s<>()[\]"\x27`]+')
LINK = re.compile(r'\[([^\]\n]+)\]\(<?(https?://[^\s<>()[\]]+)>?\)')


def public_urls(obj):
    """Non usare URL nel testo di una sentenza, nei warning o negli esempi."""
    if isinstance(obj, dict):
        url = obj.get("public_url")
        if isinstance(url, str) and url:
            parsed = urlsplit(url)
            if (parsed.scheme not in ("http", "https") or not parsed.hostname
                    or parsed.username or parsed.password or re.search(r"\s", url)):
                raise ValueError("public_url non valido")
            yield url
        # Anche la risposta MCP grezza: content=[{type:text,text:JSON}].
        if obj.get("type") == "text" and isinstance(obj.get("text"), str):
            try:
                yield from public_urls(json.loads(obj["text"]))
            except json.JSONDecodeError:
                pass
        for key, value in obj.items():
            if key not in ("text", "testo", "sintesi", "instructions", "warning"):
                yield from public_urls(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from public_urls(value)


def verifica(bozza: str, fonti: list) -> dict:
    ammessi = {url for fonte in fonti for url in public_urls(fonte)}
    if not ammessi:
        raise ValueError("nessun public_url nelle fonti: controllo non verificabile")
    spans = [m.span() for m in LINK.finditer(bozza)]
    riscontrati, estranei, incompleti = set(), set(), set()
    for match in URL.finditer(bozza):
        url = match.group(0).rstrip(".,;:!?*_>")
        completo = any(a <= match.start() < b for a, b in spans)
        # Dentro un link, confrontare l'URL esatto: niente normalizzazioni.
        if completo:
            url = next(m.group(2) for m in LINK.finditer(bozza)
                       if m.start() <= match.start() < m.end())
        if url in ammessi:
            riscontrati.add(url)
        else:
            estranei.add(url)
        if not completo:
            incompleti.add(url)
    if not riscontrati and not estranei:
        raise ValueError("nessun URL nella bozza: non è una verifica di citazioni")
    return {"ok": not estranei and not incompleti,
            "url_riscontrati": sorted(riscontrati),
            "url_non_riscontrati": sorted(estranei),
            "url_senza_link_completo": sorted(incompleti),
            "limite": "Solo identità degli URL nei file forniti; provenienza MCP, estremi, pertinenza, virgolettati e risposta successiva non verificati."}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bozza", type=Path, required=True)
    ap.add_argument("--fonte", type=Path, action="append", required=True)
    args = ap.parse_args()
    try:
        esito = verifica(args.bozza.read_text(encoding="utf-8"),
                         [json.loads(p.read_text(encoding="utf-8")) for p in args.fonte])
        esito["bozza_sha256"] = hashlib.sha256(args.bozza.read_bytes()).hexdigest()
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "errore": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(esito, ensure_ascii=False, indent=2))
    return 0 if esito["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
