#!/usr/bin/env python3
"""Harness standard library per i golden packet della skill di chiarezza legale."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = BASE_DIR / "cases.json"
DEFAULT_RUBRIC = BASE_DIR / "rubric.md"

REQUIRED_FIELDS = (
    "id",
    "title",
    "document_type",
    "input_text",
    "expected_issues",
    "legal_invariants",
    "acceptable_rewrites",
    "forbidden_changes",
    "required_reference",
    "human_notes",
    "adjudication_status",
    "validation_rationale",
    "genre",
    "expected_references_v2",
)

VALID_STATUSES = {
    "draft_codex",
    "opus_reviewed",
    "human_reviewed",
    "gold",
    "ambiguous",
    "expert_review_only",
}

VALID_GENRES = {"contratto", "atto", "parere", "diffida"}

REQUIRED_GOLD_ANNOTATORS = {"opus", "human"}
LEGAL_REFERENCE_PATTERNS = (
    re.compile(
        r"\b(?:Cass\.|Cassazione|Corte di Cassazione)\s+[^;\n]*?(?:n\.\s*)?\d{2,}(?:/\d{4}| del \d{4})?",
        re.IGNORECASE,
    ),
    re.compile(r"\bartt?\.\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bD\.M\.\s*[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bD\.Lgs\.\s*[^.;:\n]*", re.IGNORECASE),
    # "l." solo se non fa parte di una sigla (S.r.l.) e se seguito da un numero.
    re.compile(r"(?<![.\w])(?:legge|l\.)\s+(?:n\.\s*)?\d+[^.;:\n]*", re.IGNORECASE),
    re.compile(r"\bCost\.\s*[^.;:\n]*", re.IGNORECASE),
)
LEGAL_REF_NUMBER_RE = re.compile(r"\d+")
SECTION_HEADER_RE = re.compile(
    r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?"
    r"(PRIMA|DOPO|Motivo|TESTO RISCRITTO|Sommario|Scheda|Controllo|PROPOSTA)"
    r"(?:\s*\([^:\n]*\))?"
    r"(?:(:)(?:\*\*)?|(?:\*\*)|[ \t]*$)[ \t]*",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class EvalResult:
    case_id: str
    fatal_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return not self.fatal_failures

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "fatal_failures": self.fatal_failures,
            "warnings": self.warnings,
            "notes": self.notes,
            "metrics": self.metrics,
        }


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("cases.json deve contenere una lista di casi.")
    return data


def validate_cases(cases: list[dict[str, Any]], repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    root = repo_root or BASE_DIR.parent

    for index, case in enumerate(cases, start=1):
        prefix = f"case #{index}"
        case_id = case.get("id", prefix)
        if case_id in seen:
            errors.append(f"{case_id}: id duplicato.")
        seen.add(case_id)

        for field_name in REQUIRED_FIELDS:
            if field_name not in case:
                errors.append(f"{case_id}: campo obbligatorio mancante: {field_name}.")

        status = case.get("adjudication_status")
        if status not in VALID_STATUSES:
            errors.append(f"{case_id}: adjudication_status non ammesso: {status!r}.")

        for list_field in (
            "expected_issues",
            "legal_invariants",
            "acceptable_rewrites",
            "forbidden_changes",
            "required_reference",
        ):
            value = case.get(list_field)
            if not isinstance(value, list) or not value:
                errors.append(f"{case_id}: {list_field} deve essere una lista non vuota.")

        for issue in case.get("expected_issues", []):
            if not isinstance(issue, dict) or not {"code", "severity", "description"} <= set(issue):
                errors.append(f"{case_id}: ogni expected_issue richiede code, severity, description.")

        for rewrite in case.get("acceptable_rewrites", []):
            if not isinstance(rewrite, dict) or not rewrite.get("label") or not rewrite.get("text"):
                errors.append(f"{case_id}: ogni acceptable_rewrite richiede label e text.")

        # I reference dipendono dalla versione della skill: required_reference vale per
        # la v1 (tag chiarezza-v1.0), expected_references_v2 per la v2. L'esistenza dei
        # file si controlla nei test statici, versione per versione.
        if case.get("genre") not in VALID_GENRES:
            errors.append(f"{case_id}: genre non ammesso: {case.get('genre')!r}.")
        if not isinstance(case.get("expect_no_change", False), bool):
            errors.append(f"{case_id}: expect_no_change deve essere true o false.")
        persona = case.get("persona", {})
        if not isinstance(persona, dict):
            errors.append(f"{case_id}: persona deve essere un oggetto.")
        else:
            for pattern in persona.get("forbidden", []) + persona.get("required_one_of", []):
                try:
                    re.compile(pattern)
                except re.error as error:
                    errors.append(f"{case_id}: regex persona non valida {pattern!r}: {error}.")

        annotations = case.get("annotations", {})
        if not isinstance(annotations, dict):
            errors.append(f"{case_id}: annotations deve essere un oggetto.")
        elif status == "gold":
            reviewed = {
                name
                for name, payload in annotations.items()
                if isinstance(payload, dict) and payload.get("status") not in {None, "", "not_run", "pending"}
            }
            if not REQUIRED_GOLD_ANNOTATORS <= reviewed:
                errors.append(f"{case_id}: un caso gold richiede almeno review Opus e umana.")
            if annotations.get("codex", {}).get("status") and reviewed <= {"codex"}:
                errors.append(f"{case_id}: un caso con sola annotazione Codex non puo' essere gold.")
            if not case.get("validation_rationale"):
                errors.append(f"{case_id}: un caso gold richiede validation_rationale.")

        automation = case.get("automation", {})
        if not isinstance(automation, dict):
            errors.append(f"{case_id}: automation deve essere un oggetto.")
        else:
            markers = automation.get("required_output_markers", [])
            if markers and set(markers) != {"PRIMA:", "DOPO:", "Motivo:"}:
                errors.append(f"{case_id}: required_output_markers deve contenere PRIMA, DOPO e Motivo.")

    return errors


def find_case(cases: list[dict[str, Any]], case_id: str) -> dict[str, Any]:
    for case in cases:
        if case.get("id") == case_id:
            return case
    raise KeyError(f"Caso non trovato: {case_id}")


def extract_section_text(output: str, name: str) -> str:
    sections = list(SECTION_HEADER_RE.finditer(output))
    blocks: list[str] = []
    for index, section in enumerate(sections):
        if section.group(1).lower() != name.lower():
            continue
        start = section.end()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(output)
        blocks.append(unwrap_quotes(output[start:end].strip()))
    return "\n".join(block for block in blocks if block)


_WRAPPING_QUOTES_RE = re.compile(r'^\s*(?:\*\*)?["“«](.*)["”»](?:\*\*)?\s*$', re.DOTALL)


def unwrap_quotes(block: str) -> str:
    """I modelli spesso racchiudono l'intero DOPO tra virgolette: le si toglie,
    altrimenti il filtro sulle citazioni cancellerebbe tutto il testo prodotto."""
    match = _WRAPPING_QUOTES_RE.match(block)
    if match and not re.search(r'["“”«»]', match.group(1)):
        return match.group(1).strip()
    return block


def extract_do_text(output: str) -> str:
    text = extract_section_text(output, "DOPO")
    if text:
        return text
    matches = re.findall(r"DOPO:\s*(.*?)(?=\n\s*(?:PRIMA:|Motivo:)|\Z)", output, flags=re.DOTALL | re.IGNORECASE)
    return "\n".join(match.strip() for match in matches)


def extract_rewritten_text(output: str) -> str:
    return extract_section_text(output, "TESTO RISCRITTO")


def produced_text(output: str) -> str:
    """Testo che l'avvocato incollera' nell'atto: blocchi DOPO piu' TESTO RISCRITTO."""
    parts = [extract_do_text(output), extract_rewritten_text(output)]
    return "\n".join(part for part in parts if part)


# Abbreviazioni giuridiche che non chiudono la frase: senza questa lista
# "art. 1365 c.c." verrebbe spezzato in piu' frasi e le metriche di cadenza
# segnalerebbero un falso "singhiozzo".
LEGAL_ABBREVIATIONS = (
    "art", "artt", "c.c", "c.p.c", "c.p", "c.p.p", "cost", "disp", "att", "n", "nn",
    "cass", "civ", "pen", "sez", "ss", "ord", "sent", "d.lgs", "d.l", "d.m", "d.p.r",
    "l", "r.d", "reg", "lett", "co", "comma", "cfr", "cod", "cons", "doc", "docc",
    "all", "pag", "pagg", "p", "pp", "s.p.a", "s.r.l", "s.n.c", "s.a.s", "spa", "srl",
    "ill.mo", "ill.ma", "ecc.mo", "ecc.ma", "on", "avv", "dott", "dr", "prof", "sig",
    "sigg", "sig.ra", "trib", "app", "tar", "cds", "ecc", "es", "rv", "cit", "vol",
    "gg", "u.s", "c.d", "cd", "ca", "min", "max", "tab", "rif", "prot",
)
_ABBR_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(a) for a in sorted(LEGAL_ABBREVIATIONS, key=len, reverse=True)) + r")\.",
    re.IGNORECASE,
)
_PLACEHOLDER_DOT = "․"  # one dot leader, invisibile ai divisori


def split_sentences(text: str) -> list[str]:
    protected = _ABBR_RE.sub(lambda m: m.group(0)[:-1] + _PLACEHOLDER_DOT, text)
    # numeri con punti (1.000, 15.01.2018, 4.2) e iniziali puntate non chiudono la frase
    protected = re.sub(r"(?<=\d)\.(?=\d)", _PLACEHOLDER_DOT, protected)
    protected = re.sub(r"\b([A-Z])\.(?=\s*[A-Z])", r"\1" + _PLACEHOLDER_DOT, protected)
    pieces = re.split(r"(?<=[.!?])\s+|\n{2,}|\n(?=\s*(?:[-*•]|\(?[a-z0-9]{1,2}[.)])\s)", protected)
    return [piece.replace(_PLACEHOLDER_DOT, ".").strip() for piece in pieces if piece and piece.strip()]


def sentence_word_counts(text: str) -> list[int]:
    counts: list[int] = []
    for sentence in split_sentences(text):
        words = re.findall(r"\b\w+\b", sentence)
        if words:
            counts.append(len(words))
    return counts


def extract_legal_references(text: str) -> set[str]:
    refs: set[str] = set()
    for pattern in LEGAL_REFERENCE_PATTERNS:
        refs.update(match.group(0).strip().lower() for match in pattern.finditer(text))
    return refs


def normalize_reference(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def same_reference(candidate: str, known: str) -> bool:
    candidate_norm = normalize_reference(candidate)
    known_norm = normalize_reference(known)
    if candidate_norm == known_norm:
        return True
    if candidate_norm in known_norm or known_norm in candidate_norm:
        return True

    candidate_numbers = set(LEGAL_REF_NUMBER_RE.findall(candidate_norm))
    known_numbers = set(LEGAL_REF_NUMBER_RE.findall(known_norm))
    if candidate_numbers and not candidate_numbers <= known_numbers:
        return False

    # Stessi numeri (articolo, legge, sentenza e anno) = stesso riferimento, anche se
    # le parole che seguono sono diverse ("art. 1495 c.c. perche'..." / "art. 1495 c.c., non...").
    return bool(candidate_numbers) and candidate_numbers <= known_numbers


def is_known_reference(candidate: str, known_refs: set[str]) -> bool:
    return any(same_reference(candidate, known) for known in known_refs)


# --- Cancelli "delta": il testo prodotto non puo' contenere piu' occorrenze del PRIMA ---

# Intensificatori e fatti di comodo che i modelli aggiungono spesso (red team 2026-09).
INTENSIFIER_PATTERNS = {
    "interamente": r"\binteramente\b",
    "esclusivamente (come rafforzativo)": r"\besclusivamente\b",
    "totalmente": r"\btotalmente\b",
    "assolutamente": r"\bassolutamente\b",
    "palesemente": r"\bpalese(?:mente)?\b",
    "evidentemente": r"\bevidente(?:mente)?\b",
    "chiaramente": r"\bchiaramente\b",
    "macroscopico": r"\bmacroscopic\w*",
    "gravissimo": r"\bgravissim\w*",
    "del tutto": r"\bdel tutto\b",
    "pienamente": r"\bpienamente\b",
    "pacificamente": r"\bpacificamente\b",
    "indubbiamente": r"\bindubbiamente\b",
    "radicalmente": r"\bradicalmente\b",
    "invano": r"\binvano\b",
    "senza riscontro": r"\b(?:priv[ao]|senza|rimast[ao] senza) (?:di )?(?:alcun )?riscontro\b",
    "ingiustificato": r"\bingiustificat\w*",
}

# Esimenti e clausole di rischio: aggiungerle sposta l'allocazione del rischio.
EXEMPTION_PATTERNS = {
    "caso fortuito": r"\bcaso fortuito\b",
    "forza maggiore": r"\bforza maggiore\b",
    "non imputabile": r"\bnon (?:a lui |a lei |loro )?imputabil\w*",
    "salvo dolo o colpa grave": r"\bdolo o colpa grave\b",
}

# Tic da IA ad alta precisione (catalogo in references/frasi-da-ia.md della v2).
AI_TIC_HIGH = {
    "e' importante sottolineare": r"\b(?:è|e'|risulta) (?:importante|fondamentale|cruciale|essenziale) (?:sottolineare|notare|evidenziare|ricordare|precisare)\b",
    "vale la pena notare": r"\bvale la pena (?:di )?(?:notare|sottolineare|ricordare|evidenziare)\b",
    "analizziamo ora": r"\b(?:analizziamo|scomponiamo|entriamo nel merito|ed è qui che|ecco il punto)\b",
    "chiusura da chat": r"(?:certamente!|\bspero (?:che )?(?:questo|questa|sia|ti)\b|\bnon esit(?:are|ate) a\b)",
    "consulta un professionista": r"\bsi (?:consiglia|raccomanda) di (?:consultare|rivolgersi a) (?:un|una) (?:professionista|avvocato|legale|esperto)",
    "non costituisce consulenza": r"\bnon costituisce (?:consulenza|parere) legale\b",
    "commento sulla riscrittura": r"\b(?:versione (?:riscritta|migliorata|più chiara|piu' chiara)|testo riformulato)\b",
    "in un mondo in cui": r"\bin (?:un mondo|un['’]epoca|un['’]era) in cui\b|\bal giorno d['’]oggi\b",
    "navigare la complessita'": r"\bnavigar(?:e|ne) (?:la|le|tra le) (?:complessità|sfide|sfumature)\b",
    "hedging a cascata": r"\bpotrebber?o? (?:eventualmente|potenzialmente|forse)\b",
    "lineetta lunga": "—",
}

# Tic a media precisione: solo avvisi (colpiscono anche prosa legittima).
AI_TIC_MEDIUM = {
    "enfasi": r"\b(?:crucial[ei]|fondamentalmente|pivotal[ei]|imprescindibil[ei])\b",
    "calchi": r"\b(?:gioca(?:no|re|to)? un ruolo|fa(?:re|nno)? la differenza|impatta(?:re|no|to|ndo)?)\b",
    "lessico gonfiato": r"\b(?:panorama|sfaccettat[oaie]|multiform[ei]|robust[oaie]|approfondi(?:re|remo))\b",
    "gerundio finale": r",\s+(?:evidenziando|sottolineando|testimoniando|riflettendo)\b",
    "chiusura riassuntiva": r"(?:^|\n)\s*(?:in (?:conclusione|sintesi|definitiva)|riassumendo|per riassumere)\b",
    "contrasto costruito": r"\bnon (?:si tratta|è) (?:solo |soltanto |semplicemente )?(?:di )?[^.;]{1,60}?,\s*(?:ma|bensì)\b",
}

# Verbi dispositivi: "si obbliga a vendere" (effetto obbligatorio) non equivale a "vende" (effetto reale).
DISPOSITIVE_STEMS = ("vend", "trasfer", "ced", "costitu", "don", "permut", "assegn")
_OBLIGATION_RE = re.compile(
    r"\b(?:si obblig\w*|si impegn\w*|promett\w*) a (" + "|".join(DISPOSITIVE_STEMS) + r")\w*",
    re.IGNORECASE,
)

# Operatori giuridici che non possono sparire nel DOPO (se presenti nel PRIMA).
PRESERVED_OPERATORS = {
    "garanzia ('garantisce')": r"\bgarantisc\w*|\bgarant\w+ che\b",
    "eccezione (salvo/tranne/eccetto)": r"\b(?:salvo|salva|tranne|eccetto|ad eccezione)\b",
    "solidarieta'": r"\bsolidal\w*",
    "a pena di": r"\ba pena di\b",
    "elenco chiuso ('esclusivamente')": r"\besclusivamente\b",
    "elenco aperto ('esemplificativo')": r"\besemplificativ\w*|\bad esempio\b|\bdi esempio\b",
}

NO_CHANGE_RE = re.compile(r"\bnessuna modifica (?:è )?necessaria\b", re.IGNORECASE)

# Numeri "significativi": date, importi, termini, numeri di almeno due cifre.
_SIGNIFICANT_NUMBER_RE = re.compile(
    r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b"  # date
    r"|\b\d{1,3}(?:\.\d{3})+(?:,\d+)?\b"  # importi con separatore
    r"|\b\d+(?:,\d+)?\s*(?:%|euro|€|giorni|gg|mesi|anni|ore|settimane)\b"
    r"|\b\d{2,}\b",
    re.IGNORECASE,
)


MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7,
    "agosto": 8, "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
}
_NUMERIC_DATE_RE = re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b")
_TEXT_DATE_RE = re.compile(r"\b(\d{1,2})(?:°|º)?\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b", re.IGNORECASE)


def dates_in(text: str) -> set[tuple[int, int, int]]:
    """Date del testo normalizzate (giorno, mese, anno), in forma numerica o per esteso."""
    found: set[tuple[int, int, int]] = set()
    for day, month, year in _NUMERIC_DATE_RE.findall(text):
        full_year = int(year) + (2000 if len(year) == 2 else 0)
        found.add((int(day), int(month), full_year))
    for day, month, year in _TEXT_DATE_RE.findall(text):
        found.add((int(day), MONTHS[month.lower()], int(year)))
    return found


def count_pattern(pattern: str, text: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))


def strip_quotations(text: str) -> str:
    """Esclude i passi citati tra virgolette dai controlli sui tic."""
    return re.sub(r"[\"“«][^\"”»]{0,400}[\"”»]", " ", text)


def significant_numbers(text: str) -> set[str]:
    found: set[str] = set()
    for match in _SIGNIFICANT_NUMBER_RE.finditer(text):
        found.add(re.sub(r"\s+", " ", match.group(0).lower()))
    return found


def delta_additions(patterns: dict[str, str], before: str, after: str) -> list[str]:
    added: list[str] = []
    for label, pattern in patterns.items():
        if count_pattern(pattern, after) > count_pattern(pattern, before):
            added.append(label)
    return added


def gulpease(text: str) -> float | None:
    words = re.findall(r"\b\w+\b", text)
    sentences = split_sentences(text)
    if len(words) < 20 or not sentences:
        return None
    letters = sum(len(word) for word in words)
    return round(89 + (300 * len(sentences) - 10 * letters) / len(words), 1)


LOGICAL_CONNECTIVES = (
    "ma", "però", "pero'", "poiché", "poiche'", "perché", "perche'", "quindi", "dunque",
    "infatti", "tuttavia", "cioè", "cioe'", "invece", "bensì", "bensi'", "pertanto",
    "inoltre", "anzi", "mentre", "sicché", "sicche'", "perciò", "percio'", "ne consegue",
)


def cadence_metrics(text: str) -> dict[str, Any]:
    counts = sentence_word_counts(text)
    total_words = sum(counts)
    metrics: dict[str, Any] = {"words": total_words, "sentences": len(counts)}
    if not counts:
        return metrics
    mean = total_words / len(counts)
    metrics["mean_sentence_words"] = round(mean, 1)
    metrics["gulpease"] = gulpease(text)
    if total_words < 150 or len(counts) < 5:
        metrics["cadence"] = "non calcolata (testo sotto 150 parole o meno di 5 frasi)"
        return metrics
    variance = sum((count - mean) ** 2 for count in counts) / len(counts)
    runs_of_short = 0
    streak = 0
    for count in counts:
        streak = streak + 1 if count < 10 else 0
        if streak == 3:
            runs_of_short += 1
    starts = [sentence.lstrip("*-• (").lower() for sentence in split_sentences(text)]
    connective_starts = sum(
        1 for start in starts if any(re.match(rf"{re.escape(word)}\b", start) for word in LOGICAL_CONNECTIVES)
    )
    bands = [0 if count < 10 else 1 if count <= 25 else 2 for count in counts]
    same_band = sum(1 for a, b in zip(bands, bands[1:]) if a == b)
    metrics.update(
        {
            "cv_sentence_length": round((variance ** 0.5) / mean, 2) if mean else None,
            "short_runs_3plus": runs_of_short,
            "share_under_10": round(sum(1 for c in counts if c < 10) / len(counts), 2),
            "share_over_40": round(sum(1 for c in counts if c > 40) / len(counts), 2),
            "connective_start_share": round(connective_starts / len(counts), 2),
            "same_band_share": round(same_band / max(1, len(counts) - 1), 2),
        }
    )
    return metrics


def word_edit_ratio(before: str, after: str) -> float:
    a = re.findall(r"\b\w+\b", before.lower())
    b = re.findall(r"\b\w+\b", after.lower())
    if not a and not b:
        return 0.0
    return round(1 - difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio(), 2)


def evaluate_output(case: dict[str, Any], output: str) -> EvalResult:
    result = EvalResult(case_id=case["id"])
    automation = case.get("automation", {})
    markers = automation.get("required_output_markers", ["PRIMA:", "DOPO:", "Motivo:"])
    input_text = case.get("input_text", "")
    expect_no_change = bool(case.get("expect_no_change"))
    says_no_change = bool(NO_CHANGE_RE.search(output))

    if expect_no_change:
        if not says_no_change:
            result.fatal_failures.append(
                "Sovra-modifica: il testo era gia' chiaro e andava lasciato invariato ('Nessuna modifica necessaria')."
            )
        result.metrics["no_change_declared"] = says_no_change
        return result
    if says_no_change and not extract_do_text(output):
        result.fatal_failures.append("Sotto-modifica: dichiarata 'nessuna modifica' su un testo che andava migliorato.")
        return result

    headers = {match.group(1).lower() for match in SECTION_HEADER_RE.finditer(output)}
    for marker in markers:
        if marker not in output and marker.rstrip(":").lower() not in headers:
            result.fatal_failures.append(f"Formato obbligatorio mancante: {marker}")

    do_text = extract_do_text(output)
    if not do_text:
        result.fatal_failures.append("Blocco DOPO non trovato o vuoto.")
        do_text = output
    scope = produced_text(output) or do_text
    # Per i conteggi "delta" il testo prodotto va confrontato con il suo originale
    # corrispondente, senza doppioni: il TESTO RISCRITTO con l'input intero, oppure i
    # blocchi DOPO con i blocchi PRIMA (che il modello cita con la stessa divisione).
    rewritten = extract_rewritten_text(output)
    if rewritten:
        count_after, count_before = rewritten, input_text
    else:
        count_after, count_before = do_text, (extract_section_text(output, "PRIMA") or input_text)
    scope_no_quotes = strip_quotations(count_after)
    input_no_quotes = strip_quotations(count_before)

    # Vecchio controllo (v1): letterali sull'intero output. Tenuto per compatibilita'.
    for literal in automation.get("must_preserve_literals", []):
        if literal.lower() not in output.lower():
            result.fatal_failures.append(f"Elemento da preservare assente: {literal}")

    # Nuovo controllo: i letterali devono stare nel testo prodotto, non basta ricopiarli nel PRIMA.
    scope_dates = dates_in(scope)
    for literal in automation.get("must_preserve_in_dopo", []):
        if literal.lower() in scope.lower():
            continue
        literal_dates = dates_in(literal)
        if literal_dates and literal_dates <= scope_dates:
            continue  # stessa data scritta in altra forma: "1/3/2024" = "1° marzo 2024"
        result.fatal_failures.append(f"Elemento da preservare assente dal DOPO: {literal}")

    for forbidden in automation.get("fatal_forbidden_after", []):
        if forbidden.lower() in scope.lower():
            result.fatal_failures.append(f"Espressione vietata nel DOPO: {forbidden}")

    for group in automation.get("must_include_one_of", []):
        label = group.get("label", "gruppo obbligatorio")
        terms = group.get("terms", [])
        if terms and not any(term.lower() in output.lower() for term in terms):
            result.fatal_failures.append(
                f"Manca almeno uno dei termini richiesti per {label}: {', '.join(terms)}"
            )

    persona = case.get("persona", {})
    for forbidden in persona.get("forbidden", []):
        if re.search(forbidden, scope, flags=re.IGNORECASE):
            result.fatal_failures.append(f"Persona invertita nel DOPO: {forbidden}")
    required_persona = persona.get("required_one_of", [])
    if required_persona and not any(re.search(p, scope, flags=re.IGNORECASE) for p in required_persona):
        result.fatal_failures.append("Persona attesa assente dal DOPO: " + " / ".join(required_persona))

    allowed_new = {item.lower() for item in automation.get("allowed_new_literals", [])}
    input_digits = set(re.findall(r"\d+", input_text)) | {re.sub(r"\D", "", n) for n in significant_numbers(input_text)}
    new_numbers = sorted(
        number
        for number in significant_numbers(scope) - significant_numbers(input_text)
        if number not in allowed_new and re.sub(r"\D", "", number) not in input_digits
    )
    if new_numbers:
        result.fatal_failures.append("Numeri, date o termini nuovi nel DOPO: " + ", ".join(new_numbers))

    added_intensifiers = [
        label for label in delta_additions(INTENSIFIER_PATTERNS, input_no_quotes, scope_no_quotes)
        if label not in allowed_new
    ]
    if added_intensifiers:
        result.fatal_failures.append("Intensificatori o fatti di comodo aggiunti: " + ", ".join(added_intensifiers))

    added_exemptions = [
        label for label in delta_additions(EXEMPTION_PATTERNS, input_no_quotes, scope_no_quotes)
        if label not in allowed_new
    ]
    if added_exemptions:
        result.fatal_failures.append(
            "Esimenti aggiunte nel DOPO (vanno proposte come PROPOSTA:): " + ", ".join(added_exemptions)
        )

    lost_operators = [
        label
        for label, pattern in PRESERVED_OPERATORS.items()
        if count_pattern(pattern, strip_quotations(input_text)) and not count_pattern(pattern, strip_quotations(scope))
    ]
    if lost_operators:
        result.fatal_failures.append("Operatore giuridico eliminato nel DOPO: " + ", ".join(lost_operators))

    input_obligations = {m.group(1).lower() for m in _OBLIGATION_RE.finditer(input_text)}
    output_obligations = {m.group(1).lower() for m in _OBLIGATION_RE.finditer(scope)}
    if input_obligations - output_obligations:
        result.fatal_failures.append(
            "Verbo dispositivo cambiato: 'si obbliga a' eliminato per " + ", ".join(sorted(input_obligations - output_obligations))
        )
    if output_obligations - input_obligations:
        result.fatal_failures.append(
            "Verbo dispositivo cambiato: 'si obbliga a' introdotto per " + ", ".join(sorted(output_obligations - input_obligations))
        )

    added_ai = delta_additions(AI_TIC_HIGH, input_no_quotes, scope_no_quotes)
    if added_ai:
        result.fatal_failures.append("Tic da IA aggiunti nel DOPO: " + ", ".join(added_ai))
    added_ai_medium = delta_additions(AI_TIC_MEDIUM, input_no_quotes, scope_no_quotes)
    if added_ai_medium:
        result.warnings.append("Possibili tic da IA (da verificare): " + ", ".join(added_ai_medium))

    allowed_refs = {ref.lower() for ref in automation.get("allowed_legal_references", [])}
    input_refs = extract_legal_references(input_text)
    known_refs = input_refs | allowed_refs
    # I rinvii con segnaposto ("art. [●]", "art. [da decidere]") non sono fonti nuove.
    output_refs = {ref for ref in extract_legal_references(scope) if re.search(r"\d", ref)}
    unknown_refs = sorted(ref for ref in output_refs if not is_known_reference(ref, known_refs))
    if unknown_refs:
        message = "Fonti nuove non presenti nel testo: " + "; ".join(unknown_refs)
        if automation.get("new_sources_warning_only"):
            result.warnings.append(message)
        else:
            result.fatal_failures.append(message)

    long_sentences = [count for count in sentence_word_counts(do_text) if count > 45]
    if long_sentences:
        result.warnings.append(f"Frasi ancora lunghe nel DOPO: {long_sentences}")

    before_words = len(re.findall(r"\b\w+\b", input_text))
    after_words = len(re.findall(r"\b\w+\b", extract_rewritten_text(output) or do_text))
    result.metrics.update(
        {
            "length_ratio": round(after_words / before_words, 2) if before_words else None,
            "edit_ratio": word_edit_ratio(input_text, extract_rewritten_text(output) or do_text),
            "before": cadence_metrics(input_text),
            "after": cadence_metrics(extract_rewritten_text(output) or do_text),
            "has_full_text": bool(extract_rewritten_text(output)),
        }
    )

    if case.get("adjudication_status") in {"ambiguous", "expert_review_only"}:
        result.notes.append(
            "Caso non adatto a fallimento automatico rigido senza revisione esperta."
        )

    return result


def build_ab_prompt(case: dict[str, Any], output_a: str, output_b: str, order: str = "AB") -> str:
    if order not in {"AB", "BA"}:
        raise ValueError("order deve essere AB o BA.")
    first, second = (output_a, output_b) if order == "AB" else (output_b, output_a)
    rubric = DEFAULT_RUBRIC.read_text(encoding="utf-8")
    payload = {
        "case_id": case["id"],
        "document_type": case["document_type"],
        "input_text": case["input_text"],
        "legal_invariants": case["legal_invariants"],
        "forbidden_changes": case["forbidden_changes"],
        "required_reference": case["required_reference"],
    }
    return (
        "Valuta i due output anonimi per la skill di chiarezza legale.\n"
        "Non premiare lunghezza, tono elegante o formattazione se la fedelta' giuridica peggiora.\n"
        "Restituisci JSON con score 0-3 per criterio, fatal_failures e preferenza motivata.\n\n"
        f"RUBRICA:\n{rubric}\n\n"
        f"PACKET:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        f"OUTPUT A:\n{first}\n\n"
        f"OUTPUT B:\n{second}\n"
    )


def cmd_validate(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    errors = validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {len(cases)} casi validi.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for case in load_cases(args.cases):
        print(f"{case['id']}\t{case['adjudication_status']}\t{case['document_type']}\t{case['title']}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    case = find_case(cases, args.case)
    output = Path(args.output).read_text(encoding="utf-8")
    result = evaluate_output(case, output)
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0 if result.passed else 1


def cmd_ab_prompt(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    case = find_case(cases, args.case)
    output_a = Path(args.output_a).read_text(encoding="utf-8")
    output_b = Path(args.output_b).read_text(encoding="utf-8")
    print(build_ab_prompt(case, output_a, output_b, args.order))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="valida cases.json")
    validate_parser.set_defaults(func=cmd_validate)

    list_parser = subparsers.add_parser("list", help="elenca i casi")
    list_parser.set_defaults(func=cmd_list)

    eval_parser = subparsers.add_parser("evaluate", help="valuta un output per un caso")
    eval_parser.add_argument("--case", required=True)
    eval_parser.add_argument("--output", required=True)
    eval_parser.set_defaults(func=cmd_evaluate)

    ab_parser = subparsers.add_parser("ab-prompt", help="genera prompt A/B con ordine invertibile")
    ab_parser.add_argument("--case", required=True)
    ab_parser.add_argument("--output-a", required=True)
    ab_parser.add_argument("--output-b", required=True)
    ab_parser.add_argument("--order", choices=("AB", "BA"), default="AB")
    ab_parser.set_defaults(func=cmd_ab_prompt)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        args = parser.parse_args(["validate"])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
