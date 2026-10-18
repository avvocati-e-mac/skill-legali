#!/usr/bin/env python3
"""Confronta offline i nomi MCP osservati con l'inventario di questa skill."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

PREFISSI = ("mcp__claude_ai_BuddaLaw__", "mcp__buddalaw__", "buddalaw_")


def inventario(skill: Path) -> dict:
    blocchi = [json.loads(m.group(1)) for m in re.finditer(
        r"```json\s*\n(.*?)\n```", skill.read_text(encoding="utf-8"), re.S)]
    trovati = [b for b in blocchi if isinstance(b, dict) and "inventario_tool_buddalaw" in b]
    if len(trovati) != 1:
        raise ValueError("atteso un solo inventario nella skill")
    return trovati[0]


def confronta(nomi: list[str], totale: int, dati: dict) -> dict:
    if totale < 1 or len(nomi) != totale:
        raise ValueError("catalogo incompleto: il totale osservato non coincide con i nomi forniti")
    normalizzati = []
    for nome in nomi:
        for prefisso in PREFISSI:
            if nome.startswith(prefisso):
                nome = nome[len(prefisso):]
                break
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nome) or nome.startswith("mcp__"):
            raise ValueError("nome non riconosciuto come tool BuddaLaw: " + nome)
        normalizzati.append(nome)
    if len(set(normalizzati)) != totale:
        raise ValueError("nomi duplicati: impossibile attestare un catalogo completo")
    attesi = dati["inventario_tool_buddalaw"]
    if not attesi or len(attesi) != len(set(attesi)):
        raise ValueError("inventario vuoto o duplicato")
    nuovi = sorted(set(normalizzati) - set(attesi))
    avviso = ""
    if nuovi:
        avviso = ("⚠ BuddaLaw è stato aggiornato: " + ", ".join(nuovi)
                  + f". Questa skill (v{dati['versione_skill']}) potrebbe non essere aggiornata; "
                  "controlla se c'è una nuova versione su github.com/avvocati-e-mac/skill-legali.")
    return {"totale_server": totale, "totale_inventario": len(attesi),
            "nuovi": nuovi, "non_visibili": sorted(set(attesi) - set(normalizzati)),
            "avviso": avviso}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--totale", type=int, required=True, help="numero di tool osservati nel catalogo completo")
    ap.add_argument("--nomi", nargs="+", required=True, help="tutti i nomi osservati, anche con prefisso")
    a = ap.parse_args()
    try:
        dati = inventario(Path(__file__).resolve().parents[1] / "SKILL.md")
        esito = confronta(a.nomi, a.totale, dati)
    except (ValueError, KeyError, TypeError, OSError) as e:
        print(json.dumps({"errore": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(esito, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
