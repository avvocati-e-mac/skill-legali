"""
Test end-to-end della skill normattiva via Claude API (Livello B).

Carica SKILL.md + lookup-extended.md come system prompt, invia una query
in linguaggio naturale per ciascuno dei 15 casi critici, e verifica che
la risposta contenga i link e i comportamenti attesi.

Requisiti:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Esecuzione:
    python test_claude_skill.py
    python test_claude_skill.py --verbose    # mostra la risposta completa
    python test_claude_skill.py --case B03   # esegue solo un caso specifico
"""

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


SKILL_MD = Path(__file__).parent.parent / "normattiva" / "SKILL.md"
LOOKUP_MD = Path(__file__).parent.parent / "normattiva" / "references" / "lookup-extended.md"

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1024


@dataclass
class TestCase:
    id: str
    desc: str
    query: str
    checks: list[dict] = field(default_factory=list)


# Ogni check può essere:
#   {"type": "contains_url", "pattern": "regex"}   — risposta deve contenere URL matching
#   {"type": "not_contains",  "pattern": "regex"}  — risposta NON deve contenere
#   {"type": "contains_text", "pattern": "regex"}  — presenza di testo (es. avviso)

CASES: list[TestCase] = [
    TestCase(
        id="B01",
        desc="Norma vigente base: art. 2051 c.c.",
        query="Cita l'art. 2051 c.c. sulla responsabilità del custode.",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*regio\.decreto:1942-03-16;262:2~art2051"},
        ],
    ),
    TestCase(
        id="B02",
        desc="Norma abrogata generica: art. 42 l.fall.",
        query="Cita l'art. 42 della legge fallimentare sullo spossessamento del fallito.",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*regio\.decreto:1942-01-16;267:1~art42"},
            {"type": "contains_text",
             "pattern": r"(?i)(abrogate?|non.*pi[uù].*vigente|15.?07.?2022|luglio.*2022|codice.*crisi)"},
        ],
    ),
    TestCase(
        id="B03",
        desc="Norma abrogata + contesto storico: l.fall. procedura 2018",
        query=(
            "Sto difendendo in una procedura fallimentare aperta nel gennaio 2018. "
            "Cita l'art. 42 l.fall. nella versione vigente all'epoca."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*267:1~art42!vig=201[78]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B04",
        desc="Art. modificato + data fatti: art. 18 L. 300/1970 ante Jobs Act",
        query=(
            "Il licenziamento è avvenuto nel settembre 2011, prima della riforma Jobs Act. "
            "Cita l'art. 18 dello Statuto dei Lavoratori nella versione allora vigente."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*legge:1970-05-20;300~art18!vig=201[01]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B05",
        desc="D.Lgs. 81/2008 versione originaria: infortunio maggio 2008",
        query=(
            "L'infortunio è avvenuto a maggio 2008, subito dopo l'entrata in vigore del D.Lgs. 81/2008 "
            "e prima del correttivo del 2009. Cita l'art. 29 nella versione originaria."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*decreto\.legislativo:2008-04-09;81~art29!vig=200[89]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B06",
        desc="D.Lgs. 50/2016 abrogato: gara del 2022",
        query=(
            "Per una gara d'appalto bandita nel 2022 (prima del nuovo codice), "
            "cita l'art. 105 D.Lgs. 50/2016 sul subappalto."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*decreto\.legislativo:2016-04-18;50~art105"},
            {"type": "contains_text",
             "pattern": r"(?i)(abrogate?|01.?07.?2023|luglio.*2023|D\.?Lgs\.?\s*36.?2023)"},
        ],
    ),
    TestCase(
        id="B07",
        desc="Art. c.c. riformato: art. 155 c.c. ante riforma 2006",
        query=(
            "In un giudizio di separazione del 2003, prima della legge 54/2006 "
            "sull'affidamento condiviso, cita l'art. 155 c.c. nella versione allora vigente."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*262:2~art155!vig=200[0-5]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B08",
        desc="Art. inserito ex novo: art. 25-septies D.Lgs. 231/2001, infortunio 2007",
        query=(
            "Un infortunio mortale è avvenuto nel 2007, prima che il D.Lgs. 81/2008 "
            "inserisse l'art. 25-septies nel D.Lgs. 231/2001. "
            "Cita l'art. 25-septies D.Lgs. 231/2001 in relazione a questo caso."
        ),
        checks=[
            {"type": "contains_text",
             "pattern": r"(?i)(non.*era.*vigente|introdotto|inserito|D\.?Lgs\.?\s*81.?2008|15.?05.?2008|maggio.*2008|2008)"},
        ],
    ),
    TestCase(
        id="B09",
        desc="Art. con comma + data storica: art. 2477 co. 3 c.c., SRL del 2013",
        query=(
            "Nel 2013 una SRL aveva i requisiti per la nomina del sindaco unico. "
            "Cita l'art. 2477 comma 3 c.c. nella versione vigente nel 2013."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*262:2~art2477-com3!vig=201[0-3]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B10",
        desc="Bulk link: mix norme vigenti e storiche",
        query=(
            "Genera i link per: "
            "art. 2051 c.c. (vigente oggi); "
            "art. 24 Cost. (vigente oggi); "
            "art. 42 l.fall. nella versione del 2018; "
            "art. 18 L. 300/1970 nella versione del 2010."
        ),
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*262:2~art2051(?!!vig=)"},
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*costituzione:1947-12-27~art24(?!!vig=)"},
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*267:1~art42!vig=201[78]-\d{2}-\d{2}"},
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*300~art18!vig=201[0]-\d{2}-\d{2}"},
        ],
    ),
    TestCase(
        id="B11",
        desc="Codice penale: art. 110 c.p. — allegato :1",
        query="Cita l'art. 110 c.p. sul concorso nel reato.",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*regio\.decreto:1930-10-19;1398:1~art110"},
        ],
    ),
    TestCase(
        id="B12",
        desc="Costituzione: art. 24 Cost. — nessun numero nell'URN",
        query="Cita l'art. 24 della Costituzione sul diritto di difesa.",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*costituzione:1947-12-27~art24"},
            {"type": "not_contains",
             "pattern": r"costituzione:1947-12-27;\d+"},
        ],
    ),
    TestCase(
        id="B13",
        desc="Articolo bis: art. 30bis c.p.c.",
        query="Cita l'art. 30bis c.p.c. sulla competenza per le cause di lavoro.",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*1443:1~art30bis"},
        ],
    ),
    TestCase(
        id="B14",
        desc="D.P.R.: art. 1 D.P.R. 380/2001 — tipo decreto.del.presidente.della.repubblica",
        query="Cita l'art. 1 del D.P.R. 380/2001 (Testo Unico Edilizia).",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*decreto\.del\.presidente\.della\.repubblica:2001-06-06;380~art1"},
        ],
    ),
    TestCase(
        id="B15",
        desc="Norma non in quick lookup: art. 3 D.Lgs. 36/2023 — data 2023-03-31",
        query="Cita l'art. 3 del D.Lgs. 36/2023 (nuovo Codice dei contratti pubblici).",
        checks=[
            {"type": "contains_url",
             "pattern": r"normattiva\.it.*decreto\.legislativo:2023-03-31;36~art3"},
        ],
    ),
]


def load_system_prompt() -> str:
    skill = SKILL_MD.read_text(encoding="utf-8")
    lookup = LOOKUP_MD.read_text(encoding="utf-8")
    return f"{skill}\n\n---\n\n{lookup}"


def run_case(client, system_prompt: str, case: TestCase, verbose: bool = False) -> dict:
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": case.query}],
        )
        text = response.content[0].text
    except Exception as e:
        return {"id": case.id, "desc": case.desc, "passed": False,
                "error": str(e), "text": "", "failures": []}

    failures = []
    for check in case.checks:
        pattern = check["pattern"]
        if check["type"] == "contains_url":
            if not re.search(pattern, text):
                failures.append(f"URL non trovato: /{pattern}/")
        elif check["type"] == "not_contains":
            if re.search(pattern, text):
                failures.append(f"Pattern inatteso trovato: /{pattern}/")
        elif check["type"] == "contains_text":
            if not re.search(pattern, text):
                failures.append(f"Testo atteso non trovato: /{pattern}/")

    return {
        "id": case.id,
        "desc": case.desc,
        "passed": len(failures) == 0,
        "failures": failures,
        "text": text,
        "error": None,
    }


def print_result(result: dict, verbose: bool):
    status = "PASS" if result["passed"] else "FAIL"
    icon = "✓" if result["passed"] else "✗"
    print(f"  {icon} [{result['id']}] {result['desc']}")
    if not result["passed"]:
        if result.get("error"):
            print(f"      ERROR: {result['error']}")
        for f in result["failures"]:
            print(f"      → {f}")
    if verbose and result.get("text"):
        print(f"      RISPOSTA: {result['text'][:300]}{'…' if len(result['text']) > 300 else ''}")


def main():
    parser = argparse.ArgumentParser(description="Test end-to-end skill normattiva via Claude API")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--case", "-c", help="Esegui solo il caso con questo ID (es. B03)")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Secondi di attesa tra le chiamate API (default: 1.0)")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Errore: ANTHROPIC_API_KEY non impostata.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("Errore: libreria anthropic non installata.")
        print("  pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = load_system_prompt()

    cases_to_run = CASES
    if args.case:
        cases_to_run = [c for c in CASES if c.id == args.case.upper()]
        if not cases_to_run:
            print(f"Caso '{args.case}' non trovato. ID disponibili: {[c.id for c in CASES]}")
            sys.exit(1)

    print(f"\nSkill normattiva – Test Livello B (Claude API)")
    print(f"Modello: {MODEL}")
    print(f"Casi: {len(cases_to_run)}")
    print("─" * 60)

    results = []
    for i, case in enumerate(cases_to_run):
        if i > 0:
            time.sleep(args.delay)
        result = run_case(client, system_prompt, case, verbose=args.verbose)
        results.append(result)
        print_result(result, args.verbose)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print("─" * 60)
    print(f"Risultato: {passed}/{total} passed")

    if passed < total:
        print(f"\nCasi falliti:")
        for r in results:
            if not r["passed"]:
                print(f"  [{r['id']}] {r['desc']}")
        sys.exit(1)
    else:
        print("Tutti i test superati.")


if __name__ == "__main__":
    main()
