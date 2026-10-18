#!/usr/bin/env python3
"""Esegue UNA chiamata a un tool MCP BuddaLaw e restituisce il tool_result grezzo.

Canale (lo stesso di estrai_schema.py): il connettore BuddaLaw di claude.ai usa
OAuth e non esiste un token locale da passare a un client HTTP. Si usa quindi
`claude -p` in modalita' headless con un prompt che chiede al modello di fare
una sola chiamata con gli argomenti JSON dati. Il risultato NON e' il testo del
modello: e' il blocco `tool_result` letto dallo stream-json (messaggi `user`).

Controlli:
- l'input del `tool_use` deve coincidere con gli argomenti richiesti: se il
  modello li ha cambiati (per esempio un intero messo tra virgolette), la
  chiamata e' scartata con un errore, non riportata come risposta del server;
- 403, 429 o un messaggio di blocco/quota alzano `Bloccato`: chi chiama deve
  fermarsi, senza ritentare;
- nessun ritento automatico in nessun caso.

Uso da riga di comando (una chiamata, costo circa 0,01-0,03 $ con Haiku):
    python3 buddalaw/tests/tools/chiama_mcp.py get_law_article \
        '{"act": "codice_civile", "article": "2043"}'
"""
from __future__ import annotations

import json
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from dataclasses import dataclass, field

PREFIX = "mcp__claude_ai_BuddaLaw__"
MODELLO = os.environ.get("BUDDALAW_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
BUDGET_USD = "0.2"

# Una voce per ogni chiamata eseguita (tool, costo): il conftest la riassume.
REGISTRO: list[dict] = []

# Segnali di rifiuto o limitazione del servizio: chi li riceve si ferma.
_BLOCCO = re.compile(
    r"\b(403|429|500)\b|too many requests|rate.?limit|forbidden|quota|"
    r"troppe richieste|limite di (richieste|frequenza)|bloccat|sospes|"
    r"circuit breaker|backend temporaneamente non disponibile|momentaneamente disponibile",
    re.IGNORECASE,
)


class Bloccato(RuntimeError):
    """Il server (o il canale) ha rifiutato o limitato la richiesta."""


class ChiamataNonRiuscita(RuntimeError):
    """La chiamata non e' avvenuta come richiesto (nessun tool_result utile)."""


@dataclass
class Esito:
    tool: str
    argomenti: dict
    grezzo: str                    # testo del tool_result, cosi' com'e'
    is_error: bool
    dati: object = None            # JSON del tool_result, se lo e'
    costo_usd: float = 0.0
    eventi: list = field(default_factory=list, repr=False)

    @property
    def testo(self) -> str:
        return self.grezzo


def _testo_tool_result(blocco: dict) -> str:
    c = blocco.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    return ""


def _sembra_blocco(testo: str, is_error: bool, dati: object) -> bool:
    """Solo sui messaggi di errore: un testo di sentenza puo' contenere «403»."""
    if isinstance(dati, dict) and ("error" in dati or "detail" in dati):
        return bool(_BLOCCO.search(json.dumps(dati, ensure_ascii=False)))
    if is_error or testo.lstrip().lower().startswith(("error", "errore")):
        return bool(_BLOCCO.search(testo[:2000]))
    return False


def chiama(tool: str, argomenti: dict, timeout: int = 300) -> Esito:
    """Una sola chiamata `tool(argomenti)`; nessun ritento."""
    nome = PREFIX + tool
    args_json = json.dumps(argomenti, ensure_ascii=False)
    prompt = (
        "Sei un client di collaudo. Esegui UNA SOLA chiamata al tool "
        f"{nome} con questi argomenti JSON, identici, senza aggiungere, togliere "
        f"o convertire nulla (gli interi restano interi, le stringhe stringhe):\n{args_json}\n"
        "Se il tool e' differito, caricalo prima con ToolSearch "
        f'(query "select:{nome}"). Non chiamare nessun altro tool, non ritentare '
        "se la risposta e' un errore. Poi rispondi solo: FATTO."
    )
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--model", MODELLO,
        "--max-turns", "3",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--allowedTools", nome,
        "--max-budget-usd", BUDGET_USD,
    ]
    # Cartella vuota: niente CLAUDE.md di progetto nel contesto (meno token).
    with tempfile.TemporaryDirectory(prefix="buddalaw-c-") as cwd:
        spec = importlib.util.spec_from_file_location("buddalaw_live_runtime", Path(__file__).resolve().parents[1]/"e2e/run.py")
        runtime = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = runtime
        spec.loader.exec_module(runtime)
        dest = Path(cwd)/"trace.jsonl"
        try:
            code = runtime._processo_su_file(cmd, cwd, dict(os.environ), dest, timeout,
                                            callback=runtime.controllore_live())
        except runtime.Blocco as exc:
            raise Bloccato(str(exc)) from exc
        proc = SimpleNamespace(stdout=dest.read_text(),stderr=dest.with_suffix(".stderr.txt").read_text(),returncode=code)

    eventi, costo = [], 0.0
    for riga in proc.stdout.splitlines():
        try:
            eventi.append(json.loads(riga))
        except json.JSONDecodeError:
            continue
    for ev in eventi:
        if ev.get("type") == "result":
            costo = float(ev.get("total_cost_usd") or 0.0)
    REGISTRO.append({"tool": tool, "costo_usd": costo})
    for ev in eventi:
        if ev.get("type") == "result":
            if ev.get("is_error") and _BLOCCO.search(str(ev.get("result", ""))):
                raise Bloccato(f"canale claude -p rifiutato: {str(ev.get('result'))[:300]}")

    # tool_use del tool richiesto -> id; poi il suo tool_result
    usi = {}
    for ev in eventi:
        if ev.get("type") != "assistant":
            continue
        for b in (ev.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == nome:
                usi[b["id"]] = b.get("input") or {}
    if not usi:
        raise ChiamataNonRiuscita(
            f"nessuna chiamata a {nome} (exit {proc.returncode}, costo {costo:.3f} $). "
            f"stderr: {proc.stderr[:300]!r}")
    if len(usi) > 1:
        raise ChiamataNonRiuscita(f"il modello ha chiamato {nome} {len(usi)} volte: atteso una sola")
    id_uso, input_usato = next(iter(usi.items()))
    if input_usato != argomenti:
        raise ChiamataNonRiuscita(
            f"il modello ha cambiato gli argomenti: chiesti {args_json}, "
            f"usati {json.dumps(input_usato, ensure_ascii=False)}")

    for ev in eventi:
        if ev.get("type") != "user":
            continue
        for b in (ev.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") == id_uso:
                grezzo = _testo_tool_result(b)
                is_error = bool(b.get("is_error"))
                try:
                    dati = json.loads(grezzo)
                except (json.JSONDecodeError, TypeError):
                    dati = None
                if _sembra_blocco(grezzo, is_error, dati):
                    raise Bloccato(f"{tool}: {grezzo[:300]}")
                if is_error and "permission" in grezzo.lower() and "MCP" not in grezzo:
                    raise ChiamataNonRiuscita(f"permesso negato dal canale: {grezzo[:300]}")
                return Esito(tool, argomenti, grezzo, is_error, dati, costo, eventi)
    raise ChiamataNonRiuscita(f"tool_use {id_uso} senza tool_result (costo {costo:.3f} $)")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    try:
        e = chiama(sys.argv[1], json.loads(sys.argv[2]))
    except Bloccato as ex:
        print(f"FERMO (nessun ritento): {ex}", file=sys.stderr)
        return 3
    print(json.dumps({"is_error": e.is_error, "costo_usd": e.costo_usd}, ensure_ascii=False), file=sys.stderr)
    print(e.grezzo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
