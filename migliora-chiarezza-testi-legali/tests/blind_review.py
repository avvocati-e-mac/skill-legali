#!/usr/bin/env python3
"""Revisione umana CIECA A/B per la skill migliora-chiarezza-testi-legali.

Prende output gia' generati da run_live.py per due "bracci" (arm =
f"{version}__{variant}"), li appaia (stesso modello, caso, campione), ne
sceglie n coppie stratificate per caso, ripulisce gli output da tutto cio'
che potrebbe rivelare quale braccio li ha prodotti (sezioni Scheda/Controllo,
nomi di file della skill) e li mostra a un avvocato come "Testo 1" / "Testo 2"
assegnati a caso. Le risposte si incrociano con la mappa segreta solo dopo la
revisione, con `unblind`.

Uso:
    python3 blind_review.py serve --session prova-01 \\
        --run-dir runs/2026-09-23/dev \\
        --arm-a chiarezza-v1.0__completa --arm-b working__completa \\
        --pairs 15 --port 8766

    python3 blind_review.py unblind --session prova-01
"""

from __future__ import annotations

import argparse
import json
import random
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from math import comb
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import clarity_eval


BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "blind_review.html"
BLIND_DIR = BASE_DIR / "blind"
DEFAULT_SEED = 42
DEFAULT_PORT = 8766

CRITERIA: tuple[str, ...] = ("fedelta_giuridica", "chiarezza", "fluidita", "naturalezza")
CRITERIA_LABELS = {
    "fedelta_giuridica": "Fedelta' giuridica",
    "chiarezza": "Chiarezza",
    "fluidita": "Fluidita' (si legge bene, non a singhiozzo)",
    "naturalezza": "Suona naturale (non sembra scritto da un'IA)",
}

SESSION_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
PAIR_FILENAME_RE = re.compile(r"^(?P<case>.+)__s(?P<sample>\d+)\.json$")

_FILE_REF_RE = re.compile(r"`?references/[\w\-./]+`?", re.IGNORECASE)
_SKILL_MD_RE = re.compile(r"`?SKILL\.md`?", re.IGNORECASE)
_BLANK_LINES_RE = re.compile(r"\n{3,}")

REMOVED_SECTION_NAMES = {"scheda", "controllo"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# --- Pulizia degli output (anonimizzazione) --------------------------------


def strip_named_sections(text: str, remove_names: set[str]) -> str:
    """Rimuove i blocchi di sezione (header + contenuto fino alla sezione
    successiva) i cui nomi sono in remove_names, usando lo stesso
    riconoscimento di intestazioni di clarity_eval (SECTION_HEADER_RE)."""
    matches = list(clarity_eval.SECTION_HEADER_RE.finditer(text))
    if not matches:
        return text
    parts = [text[: matches[0].start()]]
    for index, match in enumerate(matches):
        name = match.group(1).lower()
        block_start = match.start()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if name not in remove_names:
            parts.append(text[block_start:block_end])
    return "".join(parts)


def strip_file_names(text: str) -> str:
    """Rimuove i riferimenti a file della skill (references/..., SKILL.md)
    che potrebbero far intuire quale versione ha prodotto l'output."""
    text = _FILE_REF_RE.sub("[riferimento skill]", text)
    text = _SKILL_MD_RE.sub("[skill]", text)
    return text


def clean_output(text: str) -> str:
    cleaned = strip_named_sections(text or "", REMOVED_SECTION_NAMES)
    cleaned = strip_file_names(cleaned)
    cleaned = _BLANK_LINES_RE.sub("\n\n", cleaned)
    return cleaned.strip()


# --- Scoperta delle coppie appaiate -----------------------------------------


def discover_pairs(
    run_dirs: list[Path], arm_a: str, arm_b: str
) -> dict[str, list[tuple[str, int, Path, Path]]]:
    """Trova, per ciascun caso, le coppie di output (stesso modello e
    campione) presenti in entrambi i bracci. Ritorna case_id -> lista di
    (model, sample, path_arm_a, path_arm_b), in ordine deterministico."""
    candidates: dict[str, list[tuple[str, int, Path, Path]]] = {}
    for run_dir in run_dirs:
        run_dir = Path(run_dir)
        dir_a = run_dir / arm_a
        dir_b = run_dir / arm_b
        if not dir_a.is_dir() or not dir_b.is_dir():
            continue
        for model_dir in sorted(p for p in dir_a.iterdir() if p.is_dir()):
            model = model_dir.name
            sibling = dir_b / model
            if not sibling.is_dir():
                continue
            for file_a in sorted(model_dir.glob("*.json")):
                match = PAIR_FILENAME_RE.match(file_a.name)
                if not match:
                    continue
                file_b = sibling / file_a.name
                if not file_b.is_file():
                    continue
                case_id = match.group("case")
                sample = int(match.group("sample"))
                candidates.setdefault(case_id, []).append((model, sample, file_a, file_b))
    return candidates


def load_case_lookup(cases_paths: list[Path]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for path in cases_paths:
        for case in clarity_eval.load_cases(Path(path)):
            lookup.setdefault(case["id"], case)
    return lookup


def _read_output(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("output", ""))


def build_blind_pairs(
    run_dirs: list[Path],
    arm_a: str,
    arm_b: str,
    n_pairs: int,
    seed: int,
    cases_paths: list[Path],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Costruisce n_pairs coppie cieche, stratificate per caso (al massimo una
    coppia per caso se possibile), pescando a caso quale braccio diventa
    "Testo 1" e quale "Testo 2". Ritorna (coppie_anonime, mappa_segreta)."""
    rng = random.Random(seed)

    candidates_by_case = discover_pairs(run_dirs, arm_a, arm_b)
    case_ids = sorted(candidates_by_case)
    rng.shuffle(case_ids)

    pools = {case_id: candidates_by_case[case_id][:] for case_id in case_ids}
    for case_id in case_ids:
        rng.shuffle(pools[case_id])

    selected: list[tuple[str, str, int, Path, Path]] = []

    # Prima passata: al massimo una coppia per caso.
    for case_id in case_ids:
        if len(selected) >= n_pairs:
            break
        if pools[case_id]:
            model, sample, path_a, path_b = pools[case_id].pop()
            selected.append((case_id, model, sample, path_a, path_b))

    # Passate successive: solo se servono piu' coppie dei casi disponibili.
    while len(selected) < n_pairs and any(pools[case_id] for case_id in case_ids):
        progressed = False
        for case_id in case_ids:
            if len(selected) >= n_pairs:
                break
            if pools[case_id]:
                model, sample, path_a, path_b = pools[case_id].pop()
                selected.append((case_id, model, sample, path_a, path_b))
                progressed = True
        if not progressed:
            break

    cases_by_id = load_case_lookup(cases_paths)

    pairs: list[dict[str, Any]] = []
    secret: dict[str, dict[str, Any]] = {}

    for index, (case_id, model, sample, path_a, path_b) in enumerate(selected, start=1):
        pair_id = f"P{index:02d}"
        output_a = clean_output(_read_output(path_a))
        output_b = clean_output(_read_output(path_b))

        if rng.random() < 0.5:
            text1_arm, text1_output = arm_b, output_b
            text2_arm, text2_output = arm_a, output_a
        else:
            text1_arm, text1_output = arm_a, output_a
            text2_arm, text2_output = arm_b, output_b

        case = cases_by_id.get(case_id, {})
        context = dict(case.get("context") or {})
        if case.get("document_type") and "tipo_documento" not in context:
            context["tipo_documento"] = case["document_type"]

        pairs.append(
            {
                "pair_id": pair_id,
                "input_text": case.get("input_text", ""),
                "context": context,
                "testo_1": text1_output,
                "testo_2": text2_output,
            }
        )
        secret[pair_id] = {
            "arm_testo_1": text1_arm,
            "arm_testo_2": text2_arm,
            "model": model,
            "case_id": case_id,
            "sample": sample,
        }

    return pairs, secret


# --- Sessioni su disco -------------------------------------------------------


def session_path(session: str) -> Path:
    if not SESSION_NAME_RE.match(session):
        raise SystemExit(
            f"Nome sessione non valido: {session!r}. Usa solo lettere, cifre, - e _."
        )
    return BLIND_DIR / session


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def save_session(
    session_dir: Path,
    pairs: list[dict[str, Any]],
    secret: dict[str, dict[str, Any]],
    meta: dict[str, Any] | None = None,
) -> Path:
    session_dir = Path(session_dir)
    _write_json(session_dir / "coppie.json", {"created_at": utc_now(), "meta": meta or {}, "pairs": pairs})
    _write_json(session_dir / "mappa_segreta.json", secret)
    answers_path = session_dir / "risposte.json"
    if not answers_path.exists():
        _write_json(answers_path, {"version": 1, "updated_at": None, "answers": {}})
    return session_dir


def load_pairs(session_dir: Path) -> dict[str, Any]:
    path = Path(session_dir) / "coppie.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_secret(session_dir: Path) -> dict[str, dict[str, Any]]:
    path = Path(session_dir) / "mappa_segreta.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_answers(session_dir: Path) -> dict[str, Any]:
    path = Path(session_dir) / "risposte.json"
    if not path.exists():
        return {"version": 1, "updated_at": None, "answers": {}}
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
        raise ValueError("risposte.json non contiene risposte valide.")
    payload.setdefault("version", 1)
    payload.setdefault("updated_at", None)
    return payload


def save_answers(payload: dict[str, Any], session_dir: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Le risposte devono essere un oggetto JSON.")
    answers = payload.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("Campo answers mancante o non valido.")
    data = {"version": 1, "updated_at": utc_now(), "answers": answers}
    _write_json(Path(session_dir) / "risposte.json", data)
    return data


def ensure_session(
    session: str,
    run_dirs: list[Path],
    arm_a: str,
    arm_b: str,
    n_pairs: int,
    seed: int,
    cases_paths: list[Path],
) -> Path:
    sdir = session_path(session)
    if (sdir / "coppie.json").exists():
        return sdir
    pairs, secret = build_blind_pairs(run_dirs, arm_a, arm_b, n_pairs, seed, cases_paths)
    if not pairs:
        raise SystemExit(
            "Nessuna coppia trovata: controlla --run-dir, --arm-a e --arm-b "
            "(devono esistere output appaiati per lo stesso modello/caso/campione)."
        )
    meta = {
        "run_dirs": [str(path) for path in run_dirs],
        "arm_a": arm_a,
        "arm_b": arm_b,
        "n_pairs_richieste": n_pairs,
        "n_pairs_trovate": len(pairs),
        "seed": seed,
    }
    save_session(sdir, pairs, secret, meta)
    return sdir


# --- Unblind -----------------------------------------------------------------


def exact_sign_test(wins_a: int, wins_b: int) -> float:
    """Test dei segni esatto a due code (Binom(n, 0.5)) sulle preferenze,
    escludendo i pareggi."""
    n = wins_a + wins_b
    if n == 0:
        return 1.0
    k = min(wins_a, wins_b)
    cumulative = sum(comb(n, i) for i in range(0, k + 1)) / (2**n)
    return min(1.0, round(2 * cumulative, 4))


def unblind(session_dir: Path) -> dict[str, Any]:
    session_dir = Path(session_dir)
    secret = load_secret(session_dir)
    answers_payload = load_answers(session_dir)
    answers = answers_payload.get("answers", {})

    arm_scores: dict[str, dict[str, list[float]]] = {}
    arm_fatti: dict[str, list[bool]] = {}
    wins: dict[str, int] = {}
    ties = 0
    n_answered = 0

    for pair_id, meta in secret.items():
        answer = answers.get(pair_id)
        if not answer:
            continue
        n_answered += 1
        arm_for_slot = {"testo_1": meta["arm_testo_1"], "testo_2": meta["arm_testo_2"]}

        for slot, arm in arm_for_slot.items():
            slot_answer = answer.get(slot) or {}
            scores = arm_scores.setdefault(arm, {criterion: [] for criterion in CRITERIA})
            for criterion in CRITERIA:
                value = slot_answer.get(criterion)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    scores[criterion].append(float(value))
            fatti = slot_answer.get("fatti_aggiunti_persi")
            if isinstance(fatti, bool):
                arm_fatti.setdefault(arm, []).append(fatti)

        preference = answer.get("preferenza")
        if preference == "testo_1":
            arm = arm_for_slot["testo_1"]
            wins[arm] = wins.get(arm, 0) + 1
        elif preference == "testo_2":
            arm = arm_for_slot["testo_2"]
            wins[arm] = wins.get(arm, 0) + 1
        elif preference == "equivalenti":
            ties += 1

    arms = sorted(set(arm_scores) | set(wins))
    per_arm: dict[str, Any] = {}
    for arm in arms:
        scores = arm_scores.get(arm, {criterion: [] for criterion in CRITERIA})
        medie = {
            criterion: (round(sum(values) / len(values), 2) if values else None)
            for criterion, values in scores.items()
        }
        n_valutazioni = max((len(values) for values in scores.values()), default=0)
        fatti_list = arm_fatti.get(arm, [])
        per_arm[arm] = {
            "medie": medie,
            "n_valutazioni": n_valutazioni,
            "preferenze": wins.get(arm, 0),
            "fatti_aggiunti_persi_segnalati": sum(1 for f in fatti_list if f),
        }

    sign_test = None
    if len(arms) == 2:
        arm_x, arm_y = arms
        wins_x, wins_y = wins.get(arm_x, 0), wins.get(arm_y, 0)
        sign_test = {
            "arm_a": arm_x,
            "wins_a": wins_x,
            "arm_b": arm_y,
            "wins_b": wins_y,
            "pareggi": ties,
            "p_value": exact_sign_test(wins_x, wins_y),
        }

    return {
        "session": session_dir.name,
        "n_pairs_totali": len(secret),
        "n_pairs_con_risposta": n_answered,
        "pareggi": ties,
        "per_arm": per_arm,
        "sign_test": sign_test,
    }


def format_markdown(result: dict[str, Any]) -> str:
    lines = [f"# Risultati revisione cieca — {result['session']}", ""]
    lines.append(
        f"Coppie totali: {result['n_pairs_totali']} — "
        f"Risposte raccolte: {result['n_pairs_con_risposta']} — "
        f"Pareggi (\"equivalenti\"): {result['pareggi']}"
    )
    lines.append("")
    lines.append("## Punteggi medi per braccio (scala 0-3)")
    lines.append("")
    header = ["Braccio", "N valutazioni"] + [CRITERIA_LABELS[c] for c in CRITERIA] + [
        "Preferenze",
        "Fatti aggiunti/persi segnalati",
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for arm, data in sorted(result["per_arm"].items()):
        medie = data["medie"]
        row = [arm, str(data["n_valutazioni"])]
        row += [("n.d." if medie[c] is None else str(medie[c])) for c in CRITERIA]
        row += [str(data["preferenze"]), str(data["fatti_aggiunti_persi_segnalati"])]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    sign_test = result.get("sign_test")
    if sign_test:
        lines.append("## Preferenza complessiva")
        lines.append("")
        lines.append(
            f"Braccio **{sign_test['arm_a']}** preferito in {sign_test['wins_a']} coppie, "
            f"braccio **{sign_test['arm_b']}** in {sign_test['wins_b']}, "
            f"pareggio in {sign_test['pareggi']}."
        )
        n_totale = sign_test["wins_a"] + sign_test["wins_b"]
        if n_totale == 0:
            lines.append("Nessuna preferenza netta espressa: test dei segni non applicabile.")
        else:
            significativo = "significativo" if sign_test["p_value"] < 0.05 else "non significativo"
            lines.append(
                f"Test dei segni esatto (escluse le coppie 'equivalenti', n={n_totale}): "
                f"p = {sign_test['p_value']} ({significativo} a soglia 0.05)."
            )
        lines.append("")
    else:
        lines.append("Impossibile calcolare il test dei segni: servono esattamente due bracci con risposte.")
        lines.append("")

    return "\n".join(lines)


# --- Server HTTP locale -------------------------------------------------------


class BlindReviewHandler(BaseHTTPRequestHandler):
    server_version = "BlindReview/1.0"

    @property
    def session_dir(self) -> Path:
        return self.server.session_dir  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, status: HTTPStatus = HTTPStatus.OK, content_type: str = "text/html") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        self.send_json({"error": message}, status)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path in {"/", "/index.html"}:
                self.send_text(HTML_PATH.read_text(encoding="utf-8"))
                return
            if path == "/api/pairs":
                self.send_json(load_pairs(self.session_dir))
                return
            if path == "/api/risposte":
                self.send_json(load_answers(self.session_dir))
                return
            self.send_error_json("Risorsa non trovata.", HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - confine difensivo HTTP
            self.send_error_json(str(exc), HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/risposte":
            self.send_error_json("Risorsa non trovata.", HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self.send_json(save_answers(payload, self.session_dir))
        except Exception as exc:  # pragma: no cover - confine difensivo HTTP
            self.send_error_json(str(exc), HTTPStatus.BAD_REQUEST)


def run_server(host: str, port: int, session_dir: Path) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), BlindReviewHandler)
    server.session_dir = session_dir  # type: ignore[attr-defined]
    return server


# --- CLI -----------------------------------------------------------------------


def cmd_serve(args: argparse.Namespace) -> int:
    sdir = session_path(args.session)
    if (sdir / "coppie.json").exists():
        print(f"Sessione '{args.session}' gia' esistente: la riuso senza rigenerarla.")
    else:
        if not args.run_dir or not args.arm_a or not args.arm_b:
            raise SystemExit(
                "Per creare una nuova sessione servono --run-dir, --arm-a, --arm-b e --pairs."
            )
        cases_paths = [Path(path) for path in (args.cases or [clarity_eval.DEFAULT_CASES])]
        sdir = ensure_session(
            args.session,
            [Path(path) for path in args.run_dir],
            args.arm_a,
            args.arm_b,
            args.pairs,
            args.seed,
            cases_paths,
        )
        pairs_payload = load_pairs(sdir)
        print(f"Sessione '{args.session}' creata con {len(pairs_payload['pairs'])} coppie in {sdir}")

    server = run_server(args.host, args.port, sdir)
    print(f"Revisione cieca: http://{args.host}:{args.port}/")
    print(f"Sessione: {sdir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


def cmd_unblind(args: argparse.Namespace) -> int:
    sdir = session_path(args.session)
    if not sdir.exists():
        raise SystemExit(f"Sessione non trovata: {sdir}")
    result = unblind(sdir)
    print(format_markdown(result))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="genera (se serve) e serve una sessione di revisione cieca")
    serve_parser.add_argument("--session", required=True, help="Nome della sessione (cartella in tests/blind/).")
    serve_parser.add_argument(
        "--run-dir", action="append", help="Cartella runs/<run-id>/<split> con i bracci dentro. Ripetibile."
    )
    serve_parser.add_argument("--arm-a", help="Nome del primo braccio, es. chiarezza-v1.0__completa.")
    serve_parser.add_argument("--arm-b", help="Nome del secondo braccio, es. working__completa.")
    serve_parser.add_argument("--pairs", type=int, default=15, help="Numero di coppie da generare.")
    serve_parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    serve_parser.add_argument("--cases", nargs="+", help="File cases.json/holdout.json da cui leggere i casi.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    serve_parser.set_defaults(func=cmd_serve)

    unblind_parser = subparsers.add_parser("unblind", help="stampa il riepilogo di una sessione gia' revisionata")
    unblind_parser.add_argument("--session", required=True)
    unblind_parser.set_defaults(func=cmd_unblind)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
