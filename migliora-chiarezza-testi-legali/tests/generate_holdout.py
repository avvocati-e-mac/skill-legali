#!/usr/bin/env python3
"""Genera il set HOLDOUT con un modello non-Claude e lo congela con SHA-256.

Protocollo anti-contaminazione (vedi REPORT e red_team.md):
- i casi li scrive un modello di un'altra famiglia (default: GPT via OpenRouter),
  che riceve solo la descrizione del compito, non la skill;
- lo script NON stampa il contenuto dei casi: chi scrive la v2 della skill non deve
  leggerli prima della valutazione finale;
- i casi il cui gold non supera il harness vengono corretti dallo stesso modello
  (al massimo 2 volte) o scartati;
- il file viene congelato: holdout.sha256 permette di verificare che non cambi.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

TEST_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TEST_DIR))

import clarity_eval  # noqa: E402
import openrouter_client  # noqa: E402

HOLDOUT_PATH = TEST_DIR / "holdout.json"
HASH_PATH = TEST_DIR / "holdout.sha256"
DEFAULT_AUTHOR = "openai/gpt-5.6-terra"

TASK = """Sei un avvocato italiano esperto di tecnica redazionale. Devi scrivere casi di test per valutare
un assistente che RISCRIVE testi legali italiani per renderli chiari, senza cambiarne il significato giuridico
e mantenendo il registro forense. L'assistente produce blocchi PRIMA:/DOPO:/Motivo: e, per i testi lunghi,
un TESTO RISCRITTO integrale.

Scrivi {n} casi NUOVI, realistici e vari (settori diversi: appalto, software, locazione commerciale, agenzia,
lavoro, condominio, trasporti, sanita' privata, franchising, societario, successioni, ecc.), in italiano.
Distribuzione richiesta per questo lotto: {distribution}.

Ogni caso deve contenere difetti di chiarezza reali e metterne alla prova uno o piu' di questi rischi:
fatti/date/importi/termini inventati nella riscrittura; persona invertita (nostro/Vostro); garanzia trasformata
in semplice dichiarazione; "si obbliga a vendere/cedere" trasformato in "vende/cede" (o viceversa);
intensificatori aggiunti; termini tecnici sostituiti con parole comuni (decadenza/prescrizione, recesso/
risoluzione, caparra/penale); conclusioni o domande giudiziali alterate; testo gia' chiaro che non va toccato;
"e/o"; "fermo restando"/"purche'"/"salvo che"; elenchi esemplificativi o tassativi; rinvii vaghi ("come sopra");
formule arcaiche ("codesto", "ut supra", "all'uopo"); periodi lunghissimi; frasi spezzate a singhiozzo;
tic tipici dei testi generati da IA ("e' importante sottolineare", "gioca un ruolo cruciale", "in conclusione").

Restituisci SOLO un oggetto JSON: {{"cases": [ ... ]}}. Ogni caso ha ESATTAMENTE questi campi:
- "title": stringa breve;
- "document_type": "contratto" | "atto_giudiziario" | "parere" | "diffida";
- "genre": "contratto" | "atto" | "parere" | "diffida" (coerente con document_type);
- "input_text": il testo da migliorare;
- "context": oggetto con chi scrive, a chi e il documento (es. {{"documento": "diffida", "mittente": "...", "destinatario": "..."}});
- "persona": {{}} oppure, se la persona conta, {{"forbidden": [regex Python], "required_one_of": [regex Python]}};
- "expect_no_change": true solo se il testo e' gia' chiaro e va lasciato com'e' (al massimo 1 caso per lotto);
- "expected_issues": lista di {{"code", "severity" (alta|media|bassa), "description"}};
- "legal_invariants": lista di stringhe (cosa non deve cambiare);
- "forbidden_changes": lista di stringhe;
- "acceptable_rewrites": lista con almeno un {{"label", "text"}}: una riscrittura corretta che NON aggiunge fatti,
  date, numeri, termini, esimenti ("caso fortuito", "forza maggiore"), intensificatori o fonti, NON cambia la persona
  e conserva garanzie, eccezioni ("salvo"), "a pena di", "esclusivamente", "esemplificativo" se presenti. Se manca un
  dato usa un segnaposto tra parentesi quadre senza numeri, es. "[da decidere: termine]";
- "automation": {{"required_output_markers": ["PRIMA:", "DOPO:", "Motivo:"], "must_preserve_in_dopo": [letterali che
  devono restare nel testo riscritto, presi dall'input], "fatal_forbidden_after": [espressioni prolisse/arcaiche
  dell'input che non devono restare], "allowed_legal_references": [riferimenti normativi o giurisprudenziali gia'
  presenti nell'input], "allowed_new_literals": []}};
- "validation_rationale": una frase su cosa misura il caso.
Per i casi con expect_no_change true: acceptable_rewrites = [{{"label": "invariato", "text": <input_text>}}] e
must_preserve_in_dopo = [].
Non citare sentenze inesistenti: se un caso contiene una sentenza, usa estremi generici e mettili in
allowed_legal_references."""

BATCHES = (
    {"n": 6, "distribution": "3 contratti, 2 atti giudiziari, 1 diffida; tutti brevi (30-120 parole)"},
    {"n": 6, "distribution": "2 contratti, 2 atti giudiziari, 1 parere, 1 diffida; brevi (30-150 parole); uno con expect_no_change"},
    {"n": 4, "distribution": "1 contratto, 1 atto giudiziario, 1 parere, 1 diffida; brevi-medi (60-200 parole)"},
    {"n": 4, "distribution": "LUNGHI: 1 contratto (500-800 parole, piu' articoli), 1 atto giudiziario (500-900 parole, fatti e motivi), 1 parere (600-1000 parole), 1 atto giudiziario (400-600 parole)"},
)


def request_cases(model: str, batch: dict[str, Any]) -> list[dict[str, Any]]:
    response = openrouter_client.chat(
        model,
        [{"role": "user", "content": TASK.format(**batch)}],
        temperature=0.7,
        max_tokens=24000,
        response_format={"type": "json_object"},
        timeout=600,
    )
    content = response["choices"][0]["message"]["content"] or "{}"
    content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE)
    return json.loads(content).get("cases", [])


def complete_case(case: dict[str, Any], case_id: str) -> dict[str, Any]:
    case = dict(case)
    case["id"] = case_id
    case.setdefault("required_reference", ["(v1) routing non valutato sul holdout"])
    case["expected_references_v2"] = (
        ["references/contratti.md"] if case.get("genre") == "contratto" else ["references/atti-e-pareri.md"]
    )
    case.setdefault("human_notes", "")
    case["adjudication_status"] = "draft_codex"
    case["annotations"] = {
        "author": {"status": "drafted", "model": DEFAULT_AUTHOR},
        "codex": {"status": "not_run"},
        "opus": {"status": "not_run"},
        "human": {"status": "pending"},
    }
    case.setdefault("persona", {})
    case.setdefault("expect_no_change", False)
    case.setdefault("automation", {})
    case["automation"].setdefault("required_output_markers", ["PRIMA:", "DOPO:", "Motivo:"])
    case["automation"].setdefault("allowed_new_literals", [])
    return case


def gold_problems(case: dict[str, Any]) -> list[str]:
    errors = clarity_eval.validate_cases([case])
    if errors:
        return errors
    if case.get("expect_no_change"):
        ok = clarity_eval.evaluate_output(case, "Nessuna modifica necessaria: il testo e' gia' chiaro.")
        return [] if ok.passed else ok.fatal_failures
    problems: list[str] = []
    for rewrite in case["acceptable_rewrites"]:
        output = f"PRIMA: {case['input_text']}\nDOPO: {rewrite['text']}\nMotivo: verifica."
        result = clarity_eval.evaluate_output(case, output)
        problems.extend(result.fatal_failures)
    return problems


def repair(model: str, case: dict[str, Any], problems: list[str]) -> dict[str, Any] | None:
    prompt = (
        "Questo caso di test ha un problema di coerenza: la riscrittura accettabile non supera i controlli "
        "automatici elencati. Correggi il caso (di solito: la riscrittura, must_preserve_in_dopo o "
        "fatal_forbidden_after) senza cambiare il testo di input. Restituisci SOLO il JSON del caso corretto.\n\n"
        f"PROBLEMI:\n- " + "\n- ".join(problems) + "\n\nCASO:\n" + json.dumps(case, ensure_ascii=False)
    )
    response = openrouter_client.chat(
        model, [{"role": "user", "content": prompt}], temperature=0.2, max_tokens=12000,
        response_format={"type": "json_object"}, timeout=600,
    )
    try:
        fixed = json.loads(response["choices"][0]["message"]["content"])
    except (json.JSONDecodeError, TypeError):
        return None
    return fixed.get("case", fixed) if isinstance(fixed, dict) else None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--author", default=DEFAULT_AUTHOR)
    parser.add_argument("--verify", action="store_true", help="verifica soltanto l'hash del file congelato")
    args = parser.parse_args(argv)

    if args.verify:
        expected = HASH_PATH.read_text(encoding="utf-8").split()[0]
        actual = sha256(HOLDOUT_PATH)
        print("OK: holdout integro." if expected == actual else "ATTENZIONE: holdout modificato dopo il congelamento!")
        return 0 if expected == actual else 1
    if HOLDOUT_PATH.exists():
        raise SystemExit("holdout.json esiste gia' ed e' congelato: non si rigenera.")

    kept: list[dict[str, Any]] = []
    dropped = repaired = 0
    for number, batch in enumerate(BATCHES, start=1):
        raw_cases = request_cases(args.author, batch)
        print(f"Lotto {number}: ricevuti {len(raw_cases)} casi.", flush=True)
        for raw in raw_cases:
            case = complete_case(raw, f"H{len(kept) + 1:03d}")
            problems = gold_problems(case)
            attempts = 0
            while problems and attempts < 2:
                attempts += 1
                fixed = repair(args.author, case, problems)
                if not fixed:
                    break
                case = complete_case(fixed, case["id"])
                problems = gold_problems(case)
                repaired += 1
            if problems:
                dropped += 1
                # Si stampano solo le categorie di errore, non il contenuto del caso.
                kinds = sorted({problem.split(":")[0] for problem in problems})
                print(f"  scartato un caso ({'; '.join(kinds)})", flush=True)
                continue
            kept.append(case)

    HOLDOUT_PATH.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
    digest = sha256(HOLDOUT_PATH)
    HASH_PATH.write_text(f"{digest}  holdout.json\n", encoding="utf-8")
    genres: dict[str, int] = {}
    for case in kept:
        genres[case["genre"]] = genres.get(case["genre"], 0) + 1
    long_cases = sum(1 for case in kept if len(case["input_text"].split()) >= 400)
    print(f"Holdout congelato: {len(kept)} casi {genres}, {long_cases} lunghi; riparazioni {repaired}, scartati {dropped}.")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
