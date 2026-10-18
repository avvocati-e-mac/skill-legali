#!/usr/bin/env python3
"""Estrae lo schema reale dei tool MCP BuddaLaw, senza trascriverlo a mano.

Canale usato (verificato il 2026-10-17):
  `claude -p` headless + proxy HTTP locale su ANTHROPIC_BASE_URL.

Perche' cosi': in `claude -p` il tool_result di ToolSearch NON contiene i blocchi
<function>{json}</function>, ma solo riferimenti (`{"type":"tool_reference",
"tool_name":...}`): lo schema viene espanso lato API. Le definizioni complete
dei tool (anche differiti) viaggiano invece nel corpo della richiesta
POST /v1/messages, campo `tools`. Il proxy locale inoltra la richiesta ad
api.anthropic.com senza modificarla e salva SOLO i `tools` dei server BuddaLaw.
Gli header (che contengono le credenziali) non vengono mai scritti su disco.
Il modello non interpreta nulla: lo schema e' quello che Claude Code riceve dal
server MCP.

La scoperta usa ToolSearch `+BuddaLaw`, senza selezionare solo i nomi già noti.
Confronta le definizioni con tutti i tool_reference restituiti. Un catalogo
assente, al limite dei risultati o con definizioni parziali non viene salvato.

Uso:
    python3 buddalaw/tests/tools/estrai_schema.py            # scrive la fixture
    python3 buddalaw/tests/tools/estrai_schema.py --stdout   # stampa e basta
    python3 buddalaw/tests/tools/estrai_schema.py --check    # exit 1 se diverso dalla fixture

Requisiti: Claude Code installato e autenticato, connettore claude.ai BuddaLaw
attivo. Costo: una chiamata breve a Haiku (circa 0,02 $). Nessuna chiamata ai
tool BuddaLaw.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import ssl
import subprocess
import tempfile
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

PREFIX = "mcp__claude_ai_BuddaLaw__"
ATTESI = [
    "check_access",
    "search_case_law",
    "search_similar_cases",
    "get_judgement",
    "get_law_article",
    "list_uffici",
    "search_articles",
    "search_contracts",
    "list_contract_categories",
    "list_contracts",
    "get_contract",
    "get_contract_requirements",
    "search_processual_acts",
    "list_processual_act_categories",
    "list_processual_acts",
    "get_processual_act",
]
MODELLO = os.environ.get("BUDDALAW_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
UPSTREAM = "https://api.anthropic.com"
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "tool_schema.json"
_ESCLUSI_REQ = {"host", "content-length", "accept-encoding", "connection"}
_ESCLUSI_RESP = {"transfer-encoding", "content-length", "connection", "content-encoding"}


def _crea_proxy(raccolta: list):
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):  # silenzioso
            pass

        def _inoltra(self, metodo: str):
            n = int(self.headers.get("Content-Length") or 0)
            corpo = self.rfile.read(n) if n else None
            if corpo and self.path.startswith("/v1/messages"):
                try:
                    payload = json.loads(corpo)
                    tools = payload.get("tools") or []
                    raccolta.append([t for t in tools if str(t.get("name", "")).startswith(PREFIX)])
                except (json.JSONDecodeError, AttributeError):
                    pass
            hdr = {k: v for k, v in self.headers.items() if k.lower() not in _ESCLUSI_REQ}
            req = urllib.request.Request(UPSTREAM + self.path, data=corpo, headers=hdr, method=metodo)
            try:
                r = urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=300)
                codice, rh, dati = r.status, r.headers, r.read()
            except urllib.error.HTTPError as e:
                codice, rh, dati = e.code, e.headers, e.read()
            self.send_response(codice)
            for k, v in rh.items():
                if k.lower() not in _ESCLUSI_RESP:
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(dati)))
            self.end_headers()
            self.wfile.write(dati)

        def do_POST(self):
            self._inoltra("POST")

        def do_GET(self):
            self._inoltra("GET")

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def _nomi_tool_reference(stdout: str) -> set[str]:
    nomi = set()
    for riga in stdout.splitlines():
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        for b in (ev.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_result" and isinstance(b.get("content"), list):
                for c in b["content"]:
                    if isinstance(c, dict) and c.get("type") == "tool_reference":
                        nomi.add(str(c.get("tool_name", "")))
    return {n[len(PREFIX):] for n in nomi if n.startswith(PREFIX)}


LIMITE_SCOPERTA = 100


def lancia(timeout: int = 240) -> tuple[list[dict], set[str]]:
    raccolta: list = []
    srv = _crea_proxy(raccolta)
    # Una selezione dei soli nomi già noti non può scoprire tool nuovi.
    # Il + rende obbligatoria la corrispondenza col nome del server.
    prompt = (
        'Esegui una sola volta ToolSearch con query esattamente "+BuddaLaw" '
        f'e max_results {LIMITE_SCOPERTA}. Cerca tutti i tool del server BuddaLaw, '
        'non soltanto quelli di ricerca. Non chiamare altri tool. Poi rispondi solo: FATTO.'
    )
    env = dict(os.environ, ANTHROPIC_BASE_URL=f"http://127.0.0.1:{srv.server_address[1]}",
               ENABLE_TOOL_SEARCH="true")
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--no-session-persistence", "--max-turns", "3",
        "--allowedTools", "ToolSearch", "--model", MODELLO,
        "--max-budget-usd", "0.10", "--disable-slash-commands",
    ]
    try:
        with tempfile.TemporaryDirectory() as vuota:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env, cwd=vuota)
    finally:
        srv.shutdown()
    if not raccolta:
        raise RuntimeError(f"il proxy non ha visto richieste /v1/messages (exit {proc.returncode}): {proc.stderr[:400]}")
    tools = max(raccolta, key=len)
    if not tools:
        raise RuntimeError("il canale proxy non ha esposto definizioni BuddaLaw: schema non verificabile; non è prova che il server abbia rimosso i tool")
    riferimenti = _nomi_tool_reference(proc.stdout)
    if not riferimenti:
        raise RuntimeError("inventario ToolSearch non verificabile: nessun tool_reference BuddaLaw")
    if len(riferimenti) >= LIMITE_SCOPERTA:
        raise RuntimeError("inventario ToolSearch al limite dei risultati: completezza non verificabile")
    estratti = {t["name"][len(PREFIX):] for t in tools}
    if estratti != riferimenti:
        raise RuntimeError(f"schema incompleto rispetto al catalogo ToolSearch: mancanti {sorted(riferimenti - estratti)}, extra {sorted(estratti - riferimenti)}")
    return tools, riferimenti


def _ordina(obj):
    """Chiavi ordinate; le liste restano nel loro ordine (enum e required)."""
    if isinstance(obj, dict):
        return {k: _ordina(obj[k]) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_ordina(x) for x in obj]
    return obj


def costruisci() -> dict:
    tools, riferimenti = lancia()
    trovati = {
        t["name"][len(PREFIX):]: {
            "name": t["name"][len(PREFIX):],
            "description": t.get("description", ""),
            "parameters": t.get("input_schema", {}),
        }
        for t in tools
    }
    mancanti = [n for n in ATTESI if n not in trovati]
    if mancanti:
        print(f"ATTENZIONE: tool attesi assenti dal server: {mancanti}", file=sys.stderr)
    extra = sorted(n for n in trovati if n not in ATTESI)
    if riferimenti != set(trovati):
        print(f"ATTENZIONE: tool_reference dello stream {sorted(riferimenti)} "
              f"diversi dai tool del proxy", file=sys.stderr)
    return {
        "server": "claude.ai BuddaLaw",
        "prefisso": PREFIX,
        "canale": "claude -p + proxy locale ANTHROPIC_BASE_URL (campo tools di /v1/messages)",
        "tools": [_ordina(trovati[n]) for n in sorted(trovati)],
        "mancanti_attesi": mancanti,
        "extra_non_attesi": extra,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out", type=Path, default=FIXTURE)
    a = ap.parse_args()
    dati = costruisci()
    testo = json.dumps(dati, ensure_ascii=False, indent=2) + "\n"
    if a.stdout:
        sys.stdout.write(testo)
        return 0
    if a.check:
        vecchio = a.out.read_text(encoding="utf-8") if a.out.exists() else ""
        if vecchio == testo:
            print("schema invariato")
            return 0
        print("SCHEMA CAMBIATO rispetto alla fixture", file=sys.stderr)
        return 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(testo, encoding="utf-8")
    print(f"scritto {a.out}: {len(dati['tools'])} tool; mancanti {dati['mancanti_attesi']}; "
          f"extra {dati['extra_non_attesi']}")
    return 0 if not dati["mancanti_attesi"] else 2


if __name__ == "__main__":
    sys.exit(main())
