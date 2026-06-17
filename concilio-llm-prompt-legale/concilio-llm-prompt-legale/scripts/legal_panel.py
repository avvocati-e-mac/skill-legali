#!/usr/bin/env python3
"""Offline helpers for the Italian Legal LLM Panel skill."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


MAX_SCORE = 39
WEIGHTS = {
    "correttezza_normativa": 3,
    "aggiornamento": 2,
    "completezza": 2,
    "assenza_allucinazioni": 3,
    "citazione_fonti": 2,
    "segnalazione_incertezza": 1,
}

CRITERION_ORDER = list(WEIGHTS)
CRITERION_LABELS = {
    "correttezza_normativa": "Correttezza normativa",
    "aggiornamento": "Aggiornamento",
    "completezza": "Completezza",
    "assenza_allucinazioni": "Assenza allucinazioni",
    "citazione_fonti": "Citazione fonti",
    "segnalazione_incertezza": "Segnalazione incertezza",
}

LIVE_JUDGE_PROFILES = {
    "claude_opus_4_8": {
        "judge_id": "claude_opus_4_8",
        "display_name": "Claude Opus 4.8",
        "model_route": "claude-code:claude-opus-4-8",
        "tool": "claude",
        "priority": 10,
        "role": "primary legal-quality judge, risk and uncertainty review",
        "command_hint": (
            "claude --model claude-opus-4-8 --effort xhigh --print "
            "--output-format text '<prompt>'"
        ),
    },
    "codex_gpt_5_5_xhigh": {
        "judge_id": "codex_gpt_5_5_xhigh",
        "display_name": "Codex GPT-5.5 xhigh",
        "model_route": "codex:gpt-5.5:xhigh",
        "tool": "codex",
        "priority": 9,
        "role": "primary citation-discipline and structured rubric judge",
        "command_hint": (
            "codex exec --skip-git-repo-check --ephemeral -m gpt-5.5 "
            "-c model_reasoning_effort=\\\"xhigh\\\" '<prompt>'"
        ),
    },
    "claude_sonnet_recent": {
        "judge_id": "claude_sonnet_recent",
        "display_name": "Claude Sonnet recent",
        "model_route": "claude-code:sonnet",
        "tool": "claude",
        "priority": 6,
        "role": "fallback legal-quality judge",
        "command_hint": "claude --model sonnet --print --output-format text '<prompt>'",
    },
    "perplexity_gpt55": {
        "judge_id": "perplexity_gpt55",
        "display_name": "Perplexity GPT-5.5",
        "model_route": "perplexity:gpt55",
        "tool": "pwm",
        "priority": 5,
        "role": "fallback or tie-breaker judge; avoid as primary when Codex GPT-5.5 is already in panel",
        "command_hint": "pwm ask --json --source none --model gpt55 '<prompt>'",
    },
    "perplexity_gpt54": {
        "judge_id": "perplexity_gpt54",
        "display_name": "Perplexity GPT-5.4",
        "model_route": "perplexity:gpt54",
        "tool": "pwm",
        "priority": 4,
        "role": "single fallback or tie-breaker judge",
        "command_hint": "pwm ask --json --source none --model gpt54 '<prompt>'",
    },
    "perplexity_gemini_pro": {
        "judge_id": "perplexity_gemini_pro",
        "display_name": "Perplexity Gemini Pro",
        "model_route": "perplexity:gemini_pro",
        "tool": "pwm",
        "priority": 3,
        "role": "first-pass judge with Perplexity Gemini Pro route",
        "command_hint": "pwm ask --json --source none --model gemini_pro '<prompt>'",
    },
    "perplexity_kimi_k26": {
        "judge_id": "perplexity_kimi_k26",
        "display_name": "Perplexity Kimi K2.6",
        "model_route": "perplexity:kimi_k26",
        "tool": "pwm",
        "priority": 2,
        "role": "first-pass judge with Kimi route for model-family diversity",
        "command_hint": "pwm ask --json --source none --model kimi_k26 '<prompt>'",
    },
    "perplexity_nemotron": {
        "judge_id": "perplexity_nemotron",
        "display_name": "Perplexity Nemotron",
        "model_route": "perplexity:nemotron",
        "tool": "pwm",
        "priority": 2,
        "role": "diverse fallback judge when Kimi or Gemini is unavailable",
        "command_hint": "pwm ask --json --source none --model nemotron '<prompt>'",
    },
}

MIN_LIVE_JUDGES = 3
PRIMARY_LIVE_JUDGES = ["codex_gpt_5_5_xhigh", "perplexity_gemini_pro", "perplexity_kimi_k26"]
FALLBACK_LIVE_JUDGES = [
    "perplexity_nemotron",
    "claude_sonnet_recent",
    "perplexity_gpt55",
    "perplexity_gpt54",
]
DEFAULT_SUPERVISOR_JUDGE = "claude_opus_4_8"

JUDGES = [
    {
        "judge_id": "gemini_pro",
        "model_route": "perplexity:gemini_pro",
        "role": "structured reasoning and issue spotting",
    },
    {
        "judge_id": "kimi_k26",
        "model_route": "perplexity:kimi_k26",
        "role": "completeness and long-context critique",
    },
    {
        "judge_id": "gpt",
        "model_route": "codex/openai:gpt-family",
        "role": "citation discipline and normative precision",
    },
    {
        "judge_id": "claude_opus",
        "model_route": "claude-code:opus",
        "role": "supervisory risk and uncertainty review",
    },
]

# Preset tematici generici per i quattro rami del diritto italiano.
# Le checklist sono volutamente generali: nessun fatto di parte, solo criteri di qualita'
# della risposta legale e norme da verificare sempre su fonte ufficiale.
PRESETS = {
    "civile": {
        "quesito": (
            "Valutare una risposta di diritto civile italiano su una questione di "
            "obbligazioni, contratti, responsabilita o prescrizione."
        ),
        "ground_truth": (
            "La risposta deve individuare e citare l'articolo del codice civile o la "
            "legge speciale pertinente nel testo vigente; distinguere fattispecie e "
            "discipline simili (es. prescrizione ordinaria e termini speciali, "
            "responsabilita contrattuale ed extracontrattuale); segnalare gli "
            "orientamenti giurisprudenziali rilevanti senza inventare sentenze; "
            "raccomandare la verifica di norme e pronunce su fonti ufficiali o "
            "banche dati autorizzate."
        ),
        "required_topics": [
            "codice civile",
            "norma vigente",
            "articolo",
            "giurisprudenza",
            "verifica fonti",
        ],
        "fonti": [
            "Codice civile da verificare su Normattiva",
            "Giurisprudenza da verificare su banca dati autorizzata",
        ],
    },
    "penale": {
        "quesito": (
            "Valutare una risposta di diritto penale italiano su una questione di "
            "fattispecie di reato, elemento soggettivo, cause di non punibilita o "
            "prescrizione del reato."
        ),
        "ground_truth": (
            "La risposta deve citare l'articolo del codice penale o della legge "
            "speciale nel testo vigente; distinguere dolo, colpa e preterintenzione "
            "quando rilevante; trattare correttamente prescrizione e cause di "
            "estinzione; segnalare contrasti giurisprudenziali senza inventare "
            "pronunce; raccomandare la verifica su fonti ufficiali."
        ),
        "required_topics": [
            "codice penale",
            "norma vigente",
            "elemento soggettivo",
            "prescrizione",
            "verifica fonti",
        ],
        "fonti": [
            "Codice penale da verificare su Normattiva",
            "Giurisprudenza di legittimita da verificare su banca dati autorizzata",
        ],
    },
    "tributario": {
        "quesito": (
            "Valutare una risposta di diritto tributario italiano su una questione di "
            "accertamento, termini di decadenza, sanzioni o processo tributario."
        ),
        "ground_truth": (
            "La risposta deve citare la norma tributaria pertinente nel testo "
            "vigente (es. statuto del contribuente, d.lgs. sul processo tributario); "
            "trattare correttamente termini di decadenza e prescrizione; distinguere "
            "tributi e fasi del procedimento; segnalare prassi e giurisprudenza "
            "tributaria senza inventarle; raccomandare verifica su fonti ufficiali."
        ),
        "required_topics": [
            "norma tributaria",
            "norma vigente",
            "decadenza",
            "processo tributario",
            "verifica fonti",
        ],
        "fonti": [
            "Statuto del contribuente e d.lgs. 546/1992 da verificare su Normattiva",
            "Prassi e giurisprudenza tributaria da verificare su banca dati autorizzata",
        ],
    },
    "amministrativo": {
        "quesito": (
            "Valutare una risposta di diritto amministrativo italiano su una "
            "questione di provvedimento, vizi dell'atto, termini di ricorso o "
            "giurisdizione."
        ),
        "ground_truth": (
            "La risposta deve citare la norma pertinente nel testo vigente (es. "
            "l. 241/1990, codice del processo amministrativo); distinguere i vizi "
            "dell'atto e i termini di impugnazione; individuare correttamente "
            "giurisdizione e competenza; segnalare orientamenti del giudice "
            "amministrativo senza inventarli; raccomandare verifica su fonti "
            "ufficiali."
        ),
        "required_topics": [
            "norma amministrativa",
            "norma vigente",
            "termini di ricorso",
            "giurisdizione",
            "verifica fonti",
        ],
        "fonti": [
            "L. 241/1990 e d.lgs. 104/2010 (c.p.a.) da verificare su Normattiva",
            "Giurisprudenza amministrativa da verificare su banca dati autorizzata",
        ],
    },
}

LEGAL_SKILLS_REPO = "avvocati-e-mac/skill-legali"
NORMATTIVA_SKILL_PATH = "normattiva/normattiva"
SKILL_INSTALLER = (
    Path.home()
    / ".codex"
    / "skills"
    / ".system"
    / "skill-installer"
    / "scripts"
    / "install-skill-from-github.py"
)
NORMATTIVA_INSTALL_COMMAND = (
    f"python3 {SKILL_INSTALLER} --repo {LEGAL_SKILLS_REPO} --path {NORMATTIVA_SKILL_PATH}"
)

SOURCE_STATUSES = {"verified", "mismatch", "not_found", "unavailable", "unsupported"}
SOURCE_TYPES = {"italian_statute", "eu_law", "case_law_or_authority", "unknown"}
NORMATTIVA_BASE_URL = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"
NORMATTIVA_ACT_URLS = {
    "c.c.": NORMATTIVA_BASE_URL + "regio.decreto:1942-03-16;262:2",
    "codice civile": NORMATTIVA_BASE_URL + "regio.decreto:1942-03-16;262:2",
    "c.p.c.": NORMATTIVA_BASE_URL + "regio.decreto:1940-10-28;1443:1",
    "codice procedura civile": NORMATTIVA_BASE_URL + "regio.decreto:1940-10-28;1443:1",
    "codice di procedura civile": NORMATTIVA_BASE_URL + "regio.decreto:1940-10-28;1443:1",
    "c.p.": NORMATTIVA_BASE_URL + "regio.decreto:1930-10-19;1398:1",
    "codice penale": NORMATTIVA_BASE_URL + "regio.decreto:1930-10-19;1398:1",
    "c.p.p.": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1988-09-22;447",
    "codice procedura penale": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1988-09-22;447",
    "codice di procedura penale": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1988-09-22;447",
    "cost.": NORMATTIVA_BASE_URL + "costituzione:1947-12-27",
    "costituzione": NORMATTIVA_BASE_URL + "costituzione:1947-12-27",
    "l. 300/1970": NORMATTIVA_BASE_URL + "legge:1970-05-20;300",
    "statuto dei lavoratori": NORMATTIVA_BASE_URL + "legge:1970-05-20;300",
    "l.fall.": NORMATTIVA_BASE_URL + "regio.decreto:1942-01-16;267:1",
    "legge fallimentare": NORMATTIVA_BASE_URL + "regio.decreto:1942-01-16;267:1",
    "r.d. 267/1942": NORMATTIVA_BASE_URL + "regio.decreto:1942-01-16;267:1",
    "d.lgs. 14/2019": NORMATTIVA_BASE_URL + "decreto.legislativo:2019-01-12;14",
    "ccii": NORMATTIVA_BASE_URL + "decreto.legislativo:2019-01-12;14",
    "codice crisi": NORMATTIVA_BASE_URL + "decreto.legislativo:2019-01-12;14",
    "d.lgs. 151/2015": NORMATTIVA_BASE_URL + "decreto.legislativo:2015-09-14;151",
    "d.lgs. 81/2015": NORMATTIVA_BASE_URL + "decreto.legislativo:2015-06-15;81",
    "d.lgs. 81/2008": NORMATTIVA_BASE_URL + "decreto.legislativo:2008-04-09;81",
    "d.lgs. 231/2001": NORMATTIVA_BASE_URL + "decreto.legislativo:2001-06-08;231",
    "d.lgs. 196/2003": NORMATTIVA_BASE_URL + "decreto.legislativo:2003-06-30;196",
    "d.lgs. 206/2005": NORMATTIVA_BASE_URL + "decreto.legislativo:2005-09-06;206",
    "d.lgs. 209/2005": NORMATTIVA_BASE_URL + "decreto.legislativo:2005-09-07;209",
    "d.lgs. 50/2016": NORMATTIVA_BASE_URL + "decreto.legislativo:2016-04-18;50",
    "d.lgs. 36/2023": NORMATTIVA_BASE_URL + "decreto.legislativo:2023-03-31;36",
    "d.lgs. 267/2000": NORMATTIVA_BASE_URL + "decreto.legislativo:2000-08-18;267",
    "d.lgs. 165/2001": NORMATTIVA_BASE_URL + "decreto.legislativo:2001-03-30;165",
    "d.lgs. 286/1998": NORMATTIVA_BASE_URL + "decreto.legislativo:1998-07-25;286",
    "l. 241/1990": NORMATTIVA_BASE_URL + "legge:1990-08-07;241",
    "d.lgs. 104/2010": NORMATTIVA_BASE_URL + "decreto.legislativo:2010-07-02;104",
    "c.p.a.": NORMATTIVA_BASE_URL + "decreto.legislativo:2010-07-02;104",
    "codice processo amministrativo": NORMATTIVA_BASE_URL + "decreto.legislativo:2010-07-02;104",
    "codice del processo amministrativo": NORMATTIVA_BASE_URL + "decreto.legislativo:2010-07-02;104",
    "d.lgs. 152/2006": NORMATTIVA_BASE_URL + "decreto.legislativo:2006-04-03;152",
    "codice ambiente": NORMATTIVA_BASE_URL + "decreto.legislativo:2006-04-03;152",
    "d.lgs. 33/2013": NORMATTIVA_BASE_URL + "decreto.legislativo:2013-03-14;33",
    "d.lgs. 82/2005": NORMATTIVA_BASE_URL + "decreto.legislativo:2005-03-07;82",
    "cad": NORMATTIVA_BASE_URL + "decreto.legislativo:2005-03-07;82",
    "d.lgs. 546/1992": NORMATTIVA_BASE_URL + "decreto.legislativo:1992-12-31;546",
    "l. 212/2000": NORMATTIVA_BASE_URL + "legge:2000-07-27;212",
    "statuto del contribuente": NORMATTIVA_BASE_URL + "legge:2000-07-27;212",
    "d.p.r. 917/1986": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1986-12-22;917",
    "tuir": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1986-12-22;917",
    "d.p.r. 600/1973": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1973-09-29;600",
    "d.p.r. 602/1973": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1973-09-29;602",
    "d.p.r. 633/1972": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:1972-10-26;633",
    "d.lgs. 472/1997": NORMATTIVA_BASE_URL + "decreto.legislativo:1997-12-18;472",
    "d.lgs. 74/2000": NORMATTIVA_BASE_URL + "decreto.legislativo:2000-03-10;74",
    "d.p.r. 380/2001": NORMATTIVA_BASE_URL + "decreto.del.presidente.della.repubblica:2001-06-06;380",
    "r.d. 327/1942": NORMATTIVA_BASE_URL + "regio.decreto:1942-03-30;327",
    "codice navigazione": NORMATTIVA_BASE_URL + "regio.decreto:1942-03-30;327",
}
EURLEX_GDPR_URL = "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX%3A32016R0679"

STOPWORDS = {
    "alla",
    "alle",
    "allo",
    "anche",
    "come",
    "con",
    "dalla",
    "delle",
    "degli",
    "deve",
    "devi",
    "dove",
    "dopo",
    "essere",
    "fatto",
    "gli",
    "nel",
    "nella",
    "nelle",
    "non",
    "per",
    "piu",
    "puo",
    "quale",
    "quando",
    "sono",
    "sul",
    "sulla",
    "tra",
    "una",
    "uno",
    "verificare",
}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return dt.date.today().isoformat()


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    return re.sub(r"\s+", " ", text)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def emit_json(data: Any, output: str | None = None) -> None:
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        Path(output).write_text(raw + "\n", encoding="utf-8")
    else:
        print(raw)


def command_result(cmd: list[str], timeout: int = 8) -> dict[str, Any]:
    if not shutil.which(cmd[0]):
        return {"available": False, "command": cmd, "error": "not_found"}
    try:
        proc = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "available": True,
            "command": cmd,
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip()[-4000:],
            "stderr": proc.stderr.strip()[-4000:],
        }
    except subprocess.TimeoutExpired:
        return {"available": True, "command": cmd, "error": "timeout"}
    except Exception as exc:  # pragma: no cover - defensive
        return {"available": True, "command": cmd, "error": str(exc)}


def check_result_by_command(tool_data: dict[str, Any], command_prefix: list[str]) -> dict[str, Any] | None:
    for result in tool_data.get("checks", []):
        command = result.get("command", [])
        if command[: len(command_prefix)] == command_prefix:
            return result
    return None


def output_text(result: dict[str, Any] | None) -> str:
    if not result:
        return ""
    return f"{result.get('stdout', '')}\n{result.get('stderr', '')}".strip()


def command_ok(result: dict[str, Any] | None) -> bool:
    return bool(result and result.get("available") and result.get("exit_code") == 0)


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()


def skills_root() -> Path:
    return codex_home() / "skills"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def relative_files(path: Path) -> dict[str, str]:
    if not path.exists() or not path.is_dir():
        return {}
    files: dict[str, str] = {}
    for item in sorted(path.rglob("*")):
        if not item.is_file():
            continue
        rel = str(item.relative_to(path))
        files[rel] = sha256_file(item)
    return files


def installed_skill_delta(workspace_skill: Path | None = None) -> dict[str, Any]:
    workspace_skill = workspace_skill or Path(__file__).resolve().parents[1]
    installed = skills_root() / workspace_skill.name
    workspace_files = relative_files(workspace_skill)
    installed_files = relative_files(installed)
    workspace_keys = set(workspace_files)
    installed_keys = set(installed_files)
    changed = sorted(
        key
        for key in workspace_keys & installed_keys
        if workspace_files.get(key) != installed_files.get(key)
    )
    only_workspace = sorted(workspace_keys - installed_keys)
    only_installed = sorted(installed_keys - workspace_keys)
    return {
        "workspace_path": str(workspace_skill),
        "installed_path": str(installed),
        "installed_exists": installed.exists(),
        "differs": bool(changed or only_workspace or only_installed or not installed.exists()),
        "changed_files": changed[:40],
        "only_in_workspace": only_workspace[:40],
        "only_in_installed": only_installed[:40],
        "truncated": len(changed) > 40 or len(only_workspace) > 40 or len(only_installed) > 40,
    }


def skill_dir_status(name: str, aliases: list[str] | None = None) -> dict[str, Any]:
    root = skills_root()
    aliases = aliases or []
    expected = root / name
    matches: list[str] = []
    if root.exists():
        names = {name, *aliases}
        for item in sorted(root.iterdir()):
            if not item.is_dir():
                continue
            item_name = item.name.lower()
            if item_name in names or any(alias in item_name for alias in aliases):
                matches.append(str(item))
    return {
        "name": name,
        "expected_path": str(expected),
        "present": expected.exists() or bool(matches),
        "matches": matches,
    }


def config_marker_hits(config_paths: list[Path], markers: list[str]) -> list[str]:
    hits: list[str] = []
    lowered = [marker.lower() for marker in markers]
    for path in config_paths:
        if not path.exists() or not os.access(path, os.R_OK):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
        except Exception:
            continue
        if any(marker in text for marker in lowered):
            hits.append(str(path))
    return hits


def command_paths(names: list[str]) -> dict[str, str | None]:
    return {name: shutil.which(name) for name in names}


def source_tool_statuses(
    tools: dict[str, Any],
    config_paths: list[Path],
    workspace_skill: Path | None = None,
) -> dict[str, Any]:
    normattiva = skill_dir_status("normattiva", aliases=["normattiva"])
    buddalaw_skill = skill_dir_status("buddalaw", aliases=["budda", "buddalaw"])
    gestiolex_skill = skill_dir_status("gestiolex", aliases=["gestiolex", "gestiolex-corpus", "corpus"])
    searxng_skill = skill_dir_status("searxng", aliases=["searx", "searxng"])
    buddalaw_commands = command_paths(["buddalaw", "buddalaw-mcp"])
    gestiolex_commands = command_paths(["gestiolex", "gestiolex-corpus", "gestiolex-mcp"])
    searxng_commands = command_paths(["searxng", "searxng-mcp", "searx"])
    normattiva_commands = command_paths(["normattiva", "normattiva-mcp"])
    buddalaw_config_hits = config_marker_hits(config_paths, ["buddalaw", "budda-law"])
    gestiolex_config_hits = config_marker_hits(config_paths, ["gestiolex", "gestiolex-corpus"])
    searxng_config_hits = config_marker_hits(config_paths, ["searxng", "searx"])
    return {
        "normattiva": {
            **normattiva,
            "commands": normattiva_commands,
            "install_required": not normattiva["present"],
            "install_requires_user_approval": True,
            "install_command": NORMATTIVA_INSTALL_COMMAND,
            "status_message": (
                "Normattiva skill present."
                if normattiva["present"]
                else "Normattiva skill missing; ask the user before installing from avvocati-e-mac/skill-legali."
            ),
        },
        "buddalaw": {
            **buddalaw_skill,
            "commands": buddalaw_commands,
            "mcp_config_detected": bool(buddalaw_config_hits),
            "mcp_config_paths": buddalaw_config_hits,
            "requires_account_or_config": True,
            "install_or_config_requires_user_approval": True,
            "status_message": (
                "BuddaLaw appears installed/configured."
                if buddalaw_skill["present"] or any(buddalaw_commands.values()) or buddalaw_config_hits
                else "BuddaLaw not detected; do not configure paid/legal database access without approval."
            ),
        },
        "gestiolex": {
            **gestiolex_skill,
            "commands": gestiolex_commands,
            "mcp_config_detected": bool(gestiolex_config_hits),
            "mcp_config_paths": gestiolex_config_hits,
            "requires_account_or_config": True,
            "install_or_config_requires_user_approval": True,
            "status_message": (
                "GestioLex Corpus appears installed/configured."
                if gestiolex_skill["present"] or any(gestiolex_commands.values()) or gestiolex_config_hits
                else "GestioLex Corpus not detected; do not configure the MCP route without approval."
            ),
        },
        "searxng": {
            **searxng_skill,
            "commands": searxng_commands,
            "mcp_config_detected": bool(searxng_config_hits),
            "mcp_config_paths": searxng_config_hits,
            "install_or_config_requires_user_approval": True,
            "status_message": (
                "SearXNG appears installed/configured."
                if searxng_skill["present"] or any(searxng_commands.values()) or searxng_config_hits
                else "SearXNG not detected; fallback continues to Perplexity or web base."
            ),
        },
        "perplexity": {
            "cli_available": bool(tools.get("pwm", {}).get("available")),
            "auth_quota_ok": perplexity_auth_ok(tools),
            "cloud_route_requires_user_approval": True,
            "status_message": (
                "Perplexity CLI auth/quota appears usable."
                if perplexity_auth_ok(tools)
                else "Perplexity CLI detected; sandboxed auth/quota check is inconclusive or failed."
            ),
        },
        "workspace_skill_copy": installed_skill_delta(workspace_skill),
    }


def perplexity_auth_ok(tools: dict[str, Any]) -> bool:
    pwm = tools.get("pwm", {})
    login = check_result_by_command(pwm, ["pwm", "login", "--check"])
    usage = check_result_by_command(pwm, ["pwm", "usage"])
    usage_text = normalize_for_match(output_text(usage))
    if not pwm.get("available") or not command_ok(login):
        return False
    if "token expired" in usage_text or "could not fetch" in usage_text:
        return False
    return True


def route_available(profile: dict[str, Any], tools: dict[str, Any]) -> bool:
    tool = profile["tool"]
    if tool == "pwm":
        return bool(tools.get(tool, {}).get("available"))
    return bool(tools.get(tool, {}).get("available"))


def select_model_routes(tools: dict[str, Any]) -> dict[str, Any]:
    available = [
        LIVE_JUDGE_PROFILES[judge_id]
        for judge_id in [*PRIMARY_LIVE_JUDGES, *FALLBACK_LIVE_JUDGES]
        if route_available(LIVE_JUDGE_PROFILES[judge_id], tools)
    ]
    selected = [
        LIVE_JUDGE_PROFILES[judge_id]
        for judge_id in PRIMARY_LIVE_JUDGES
        if route_available(LIVE_JUDGE_PROFILES[judge_id], tools)
    ]
    fallback_order = [
        LIVE_JUDGE_PROFILES[judge_id]
        for judge_id in FALLBACK_LIVE_JUDGES
        if route_available(LIVE_JUDGE_PROFILES[judge_id], tools)
    ]
    if len(selected) < MIN_LIVE_JUDGES:
        for profile in fallback_order:
            if profile["judge_id"] not in {item["judge_id"] for item in selected}:
                selected.append(profile)
            if len(selected) >= MIN_LIVE_JUDGES:
                break

    warnings: list[str] = []
    if not tools.get("claude", {}).get("available"):
        warnings.append("Claude CLI not available; cannot select Claude Opus route.")
    if not tools.get("codex", {}).get("available"):
        warnings.append("Codex CLI not available; cannot select GPT-5.5 route.")
    if tools.get("pwm", {}).get("available") and not perplexity_auth_ok(tools):
        warnings.append("Perplexity CLI is installed; verify auth/quota outside the sandbox if live calls fail.")
    if len(selected) < MIN_LIVE_JUDGES:
        warnings.append("Fewer than three live judge routes are available.")

    spare = None
    for profile in fallback_order:
        if profile["tool"] == "pwm":
            spare = profile
            break

    return {
        "policy": "Use three independent live judges, then a separate supervisor/meta-judge after normalization.",
        "selected_primary_judges": [compact_profile(profile) for profile in selected[:MIN_LIVE_JUDGES]],
        "supervisor_judge": compact_profile(LIVE_JUDGE_PROFILES.get(DEFAULT_SUPERVISOR_JUDGE)),
        "fallback_order": [compact_profile(profile) for profile in fallback_order],
        "perplexity_spare_judge": compact_profile(spare) if spare else None,
        "pwm_council_default_allowed": False,
        "pwm_council_requires_explicit_user_approval": True,
        "fallback_triggers": [
            "primary_judge_failed_or_malformed",
            "same_candidate_primary_score_divergence_above_8",
            "top_two_candidates_within_3_points",
        ],
        "warnings": warnings,
    }


def compact_profile(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    if not profile:
        return None
    return {
        "judge_id": profile["judge_id"],
        "display_name": profile["display_name"],
        "model_route": profile["model_route"],
        "tool": profile["tool"],
        "role": profile["role"],
        "command_hint": profile["command_hint"],
    }


def extract_docx(path: Path) -> tuple[str, list[str]]:
    notes: list[str] = []
    chunks: list[str] = []
    with zipfile.ZipFile(path) as archive:
        xml_names = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]
        for name in xml_names:
            if name not in archive.namelist():
                continue
            root = ET.fromstring(archive.read(name))
            for para in root.iter():
                if not para.tag.endswith("}p"):
                    continue
                text_bits: list[str] = []
                for node in para.iter():
                    if node.tag.endswith("}t") and node.text:
                        text_bits.append(node.text)
                    elif node.tag.endswith("}tab"):
                        text_bits.append("\t")
                    elif node.tag.endswith("}br"):
                        text_bits.append("\n")
                para_text = clean_text("".join(text_bits))
                if not para_text:
                    continue
                style = ""
                for node in para.iter():
                    if node.tag.endswith("}pStyle"):
                        style = (
                            node.attrib.get(
                                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val",
                                "",
                            )
                            or ""
                        )
                        break
                style_norm = normalize_for_match(style)
                if "heading" in style_norm or "titolo" in style_norm:
                    chunks.append(f"## {para_text}")
                else:
                    chunks.append(para_text)
    if not chunks:
        notes.append("No paragraphs found in DOCX.")
    return clean_text("\n\n".join(chunks)), notes


def extract_pdf(path: Path) -> tuple[str, list[str]]:
    notes: list[str] = []
    for module_name in ("pypdf", "PyPDF2", "pdfplumber"):
        try:
            if module_name == "pypdf":
                from pypdf import PdfReader  # type: ignore

                reader = PdfReader(str(path))
                text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                return clean_text(text), notes
            if module_name == "PyPDF2":
                from PyPDF2 import PdfReader  # type: ignore

                reader = PdfReader(str(path))
                text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                return clean_text(text), notes
            if module_name == "pdfplumber":
                import pdfplumber  # type: ignore

                with pdfplumber.open(str(path)) as pdf:
                    text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)
                return clean_text(text), notes
        except ImportError:
            continue
        except Exception as exc:
            notes.append(f"{module_name} failed: {exc}")
    if shutil.which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            result = command_result(["pdftotext", str(path), str(tmp_path)], timeout=30)
            if result.get("exit_code") == 0 and tmp_path.exists():
                return clean_text(tmp_path.read_text(encoding="utf-8", errors="replace")), notes
            notes.append(f"pdftotext failed: {result}")
        finally:
            tmp_path.unlink(missing_ok=True)
    raise RuntimeError("PDF extraction requires pypdf, PyPDF2, pdfplumber, or pdftotext.")


def extract_text(path: Path) -> tuple[str, dict[str, Any]]:
    suffix = path.suffix.lower()
    notes: list[str] = []
    if suffix == ".docx":
        text, notes = extract_docx(path)
        fmt = "docx"
    elif suffix == ".pdf":
        text, notes = extract_pdf(path)
        fmt = "pdf"
    elif suffix in {".md", ".markdown", ".txt"}:
        text = path.read_text(encoding="utf-8", errors="replace")
        fmt = suffix.lstrip(".")
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        fmt = suffix.lstrip(".") or "text"
        notes.append(f"Unknown extension {suffix}; read as text.")
    return clean_text(text), {"format": fmt, "extracted_at": now_iso(), "notes": notes}


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {"risposta": []}
    current = "risposta"
    heading_map = {
        "quesito": "quesito",
        "domanda": "quesito",
        "quesito giuridico": "quesito",
        "oggetto": "quesito",
        "oggetto del quesito": "quesito",
        "si chiede": "quesito",
        "problema": "quesito",
        "problema giuridico": "quesito",
        "richiesta": "quesito",
        "question": "quesito",
        "prompt": "quesito",
        "risposta": "risposta",
        "answer": "risposta",
        "parere": "risposta",
        "analisi": "risposta",
        "ground truth": "ground_truth",
        "risposta di riferimento": "ground_truth",
        "checklist": "ground_truth",
        "fonti": "fonti",
        "sources": "fonti",
        "riferimenti": "fonti",
    }
    for raw_line in text.splitlines():
        stripped = raw_line.strip().strip("#:").strip()
        key = normalize_for_match(stripped)
        matched = None
        for marker, section in heading_map.items():
            if key == marker or key.startswith(marker + " "):
                matched = section
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            remainder = re.sub(r"^[#\s:.-]*", "", raw_line, count=1).strip()
            if ":" in remainder:
                after = remainder.split(":", 1)[1].strip()
                if after and normalize_for_match(after) != key:
                    sections[current].append(after)
            continue
        sections.setdefault(current, []).append(raw_line)
    return {key: clean_text("\n".join(value)) for key, value in sections.items()}


def extract_sources(text: str) -> list[str]:
    patterns = [
        r"\bartt?\.?\s+\d+[a-zA-Z-]*(?:\s*(?:,|e|-)\s*\d+[a-zA-Z-]*)*(?:\s*,?\s*(?:co\.|comma)\s*\d+)?(?:\s+(?:c\.c\.|c\.p\.c\.|c\.p\.p\.|c\.p\.(?![a-z])|Cost\.?|GDPR|Statuto dei lavoratori|L\.?\s*\d+/\d{4}|D\.?\s*Lgs\.?\s*\d+/\d{4}|D\.?\s*P\.?\s*R\.?\s*\d+/\d{4}|R\.?\s*D\.?\s*\d+/\d{4}))?",
        r"\b(?:GDPR|Regolamento\s+\(UE\)\s+2016/679)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Codice civile|c\.c\.)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Codice\s+(?:di\s+)?procedura\s+civile|c\.p\.c\.)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Codice penale|c\.p\.)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Codice\s+(?:di\s+)?procedura\s+penale|c\.p\.p\.)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Cost\.?|Costituzione)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:c\.p\.a\.|Codice\s+(?:del\s+)?processo\s+amministrativo)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\b(?:Statuto del contribuente|TUIR|T\.?\s*U\.?\s*I\.?\s*R\.?|CAD)\s*(?:artt?\.?|articoli?)?\s+\d+(?:\s*(?:,|e|-)\s*\d+)*",
        r"\bD\.?\s*Lgs\.?\s+\d+/\d{4}",
        r"\bD\.?\s*L\.?\s+\d+/\d{4}",
        r"\bD\.?\s*P\.?\s*R\.?\s+\d+/\d{4}",
        r"\bR\.?\s*D\.?\s+\d+/\d{4}",
        r"\bL\.?\s+\d+/\d{4}",
        r"\bRegolamento\s+\(UE\)\s+\d+/\d{4}",
        r"\bCass\.?\s+(?:civ\.?|pen\.?)?.{0,50}?\b\d{1,6}/\d{4}",
        r"\bCorte\s+di\s+Cassazione.{0,80}?\b\d{1,6}/\d{4}",
        r"\bGarante\s+Privacy\b.{0,80}",
        r"\bEDPB\b.{0,80}",
        r"\bNormattiva\b",
        r"\bEUR-?Lex\b",
    ]
    found: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = clean_text(match.group(0).strip(" .;,\n"))
            if value and value not in found:
                found.append(value)
    return found[:80]


def compact_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def norm_act(value: str) -> str:
    normalized = normalize_for_match(value)
    normalized = normalized.replace("cod. civ.", "codice civile")
    normalized = normalized.replace("cod civ", "codice civile")
    normalized = normalized.replace("cod. proc. civ.", "codice procedura civile")
    normalized = normalized.replace("cod proc civ", "codice procedura civile")
    normalized = normalized.replace("cod. proc. pen.", "codice procedura penale")
    normalized = normalized.replace("cod proc pen", "codice procedura penale")
    normalized = re.sub(r"\bd\s*lgs\b", "d.lgs.", normalized)
    normalized = re.sub(r"\bd\s*l\b", "d.l.", normalized)
    normalized = re.sub(r"\bd\s*p\s*r\b", "d.p.r.", normalized)
    normalized = re.sub(r"\br\s*d\b", "r.d.", normalized)
    normalized = re.sub(r"\bl\s+(\d+/\d{4})", r"l. \1", normalized)
    normalized = re.sub(r"\blegge\s+n?\.?\s*(\d+/\d{4})", r"l. \1", normalized)
    normalized = re.sub(r"\bd\.lgs\.?\s+(\d+/\d{4})", r"d.lgs. \1", normalized)
    normalized = re.sub(r"\bd\.l\.?\s+(\d+/\d{4})", r"d.l. \1", normalized)
    normalized = re.sub(r"\bd\.p\.r\.?\s+(\d+/\d{4})", r"d.p.r. \1", normalized)
    normalized = re.sub(r"\br\.d\.?\s+(\d+/\d{4})", r"r.d. \1", normalized)
    normalized = re.sub(r"\bl\.?\s*fall\.?", "l.fall.", normalized)
    if normalized in {"cc", "c.c", "c.c.", "codice civile"}:
        return "c.c."
    if normalized in {"cpc", "c.p.c", "c.p.c.", "codice procedura civile", "codice di procedura civile"}:
        return "c.p.c."
    if normalized in {"cp", "c.p", "c.p.", "codice penale"}:
        return "c.p."
    if normalized in {"cpp", "c.p.p", "c.p.p.", "codice procedura penale", "codice di procedura penale"}:
        return "c.p.p."
    if normalized in {"cost", "cost.", "costituzione"}:
        return "cost."
    if normalized in {"l.fall", "l.fall.", "legge fallimentare"}:
        return "l.fall."
    if "codice della crisi" in normalized or "codice crisi" in normalized or normalized == "ccii":
        return "d.lgs. 14/2019"
    if normalized in {"cpa", "c.p.a", "c.p.a.", "codice processo amministrativo", "codice del processo amministrativo"}:
        return "c.p.a."
    if "statuto del contribuente" in normalized:
        return "l. 212/2000"
    if normalized in {"tuir", "t.u.i.r.", "t.u.i.r"}:
        return "tuir"
    if normalized in {"cad", "codice amministrazione digitale", "codice dell amministrazione digitale"}:
        return "cad"
    if "codice ambiente" in normalized or "codice dell ambiente" in normalized:
        return "d.lgs. 152/2006"
    if "statuto dei lavoratori" in normalized:
        return "l. 300/1970"
    if "gdpr" in normalized or "regolamento (ue) 2016/679" in normalized:
        return "GDPR"
    return compact_ws(normalized)


def expand_article_numbers(raw: str) -> list[str]:
    cleaned = normalize_for_match(raw)
    cleaned = cleaned.replace(" e ", ",")
    cleaned = re.sub(r"\s+", "", cleaned)
    parts = [part for part in re.split(r",|;", cleaned) if part]
    numbers: list[str] = []
    for part in parts:
        range_match = re.fullmatch(r"(\d+)-(\d+)", part)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            if 0 < start <= end <= start + 20:
                numbers.extend(str(number) for number in range(start, end + 1))
            continue
        for item in re.findall(r"\d+[a-z]?", part):
            numbers.append(item)
    deduped: list[str] = []
    for number in numbers:
        if number not in deduped:
            deduped.append(number)
    return deduped


ITALIAN_ACT_PATTERN = (
    r"c\.c\.|codice civile|cod\.?\s*civ\.?|"
    r"c\.p\.c\.|codice\s+(?:di\s+)?procedura\s+civile|cod\.?\s*proc\.?\s*civ\.?|"
    r"c\.p\.p\.|codice\s+(?:di\s+)?procedura\s+penale|cod\.?\s*proc\.?\s*pen\.?|"
    r"c\.p\.a\.|codice\s+(?:del\s+)?processo\s+amministrativo|"
    r"c\.p\.|codice penale|"
    r"Cost\.?|Costituzione|"
    r"l\.?\s*fall\.?|legge fallimentare|"
    r"Statuto dei lavoratori|"
    r"Statuto del contribuente|"
    r"L\.?\s*\d+/\d{4}|Legge\s+n?\.?\s*\d+/\d{4}|"
    r"D\.?\s*Lgs\.?\s*\d+/\d{4}|D\.?\s*L\.?\s*\d+/\d{4}|"
    r"D\.?\s*P\.?\s*R\.?\s*\d+/\d{4}|R\.?\s*D\.?\s*\d+/\d{4}|"
    r"CCII|Codice della crisi|Codice crisi|T\.?\s*U\.?\s*I\.?\s*R\.?|TUIR|CAD|"
    r"Codice\s+(?:dell['’]\s*)?amministrazione\s+digitale|Codice\s+(?:dell['’]\s*)?ambiente|"
    r"GDPR|Regolamento\s+\(UE\)\s*2016/679"
)
ARTICLE_THEN_ACT_RE = re.compile(
    rf"\bartt?\.?\s*(?P<arts>\d+[a-zA-Z]?(?:\s*(?:,|e|-)\s*\d+[a-zA-Z]?)*)(?:\s*,?\s*(?:co\.|comma)\s*\d+)?\s*(?:del(?:la)?\s+)?(?P<act>{ITALIAN_ACT_PATTERN})",
    flags=re.IGNORECASE,
)
ACT_THEN_ARTICLE_RE = re.compile(
    rf"\b(?P<act>{ITALIAN_ACT_PATTERN})(?:\s*(?:,|:|-|\(|\)|del|della|articoli?))*\s*(?:artt?\.?|articoli?)\s*(?P<arts>\d+[a-zA-Z]?(?:\s*(?:,|e|-)\s*\d+[a-zA-Z]?)*)",
    flags=re.IGNORECASE,
)


def source_type_for(act: str, raw: str) -> str:
    norm = normalize_for_match(f"{act} {raw}")
    if "gdpr" in norm or "regolamento (ue) 2016/679" in norm or "eur-lex" in norm:
        return "eu_law"
    if any(marker in norm for marker in ("cass", "tar", "cgt", "corte di cassazione", "garante", "provvedimento", "sentenza")):
        return "case_law_or_authority"
    if any(
        marker in norm
        for marker in (
            "c.c",
            "c.p.c",
            "c.p.p",
            "c.p",
            "codice civile",
            "codice penale",
            "cost",
            "costituzione",
            "statuto dei lavoratori",
            "l. ",
            "l.fall",
            "legge",
            "d.lgs",
            "d.l.",
            "d.p.r",
            "r.d",
            "decreto",
            "ccii",
            "tuir",
            "c.p.a",
            "statuto del contribuente",
            "cad",
        )
    ):
        return "italian_statute"
    return "unknown"


def valid_detected_source(item: dict[str, Any]) -> bool:
    source_type = item.get("source_type")
    article = str(item.get("article") or "")
    if source_type == "eu_law" and article.isdigit() and int(article) > 99:
        return False
    return True


def raw_eu_article_out_of_range(raw: str) -> bool:
    norm = normalize_for_match(raw)
    if "gdpr" not in norm and "regolamento (ue) 2016/679" not in norm:
        return False
    article_match = re.search(r"\b(?:artt?\.?|articoli?)\s*(\d+)", norm)
    if not article_match:
        article_match = re.search(r"\bgdpr\s+(\d+)", norm)
    if not article_match:
        return False
    return int(article_match.group(1)) > 99


def canonical_citation(article: str | None, act: str, raw: str) -> str:
    act_label = norm_act(act) if act else ""
    if article and act_label:
        return f"art. {article} {act_label}"
    if raw:
        return compact_ws(raw)
    if act_label:
        return act_label
    return "citazione non classificata"


def source_citation_key(item: dict[str, Any]) -> tuple[str, str]:
    normalized = normalize_for_match(item.get("citation", ""))
    normalized = normalized.replace("artt.", "art.").replace("artt ", "art ")
    normalized = re.sub(r"\bc\.?\s*c\.?\b", "c.c.", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.rstrip(" .")
    return (normalized, item.get("source_type", "unknown"))


def detect_source_citations(case: dict[str, Any]) -> list[dict[str, Any]]:
    text_parts = [
        str(case.get("risposta", "")),
        "\n".join(str(source) for source in (case.get("fonti") or [])),
    ]
    text = "\n".join(part for part in text_parts if part)
    detected: list[dict[str, Any]] = []

    for pattern in (ARTICLE_THEN_ACT_RE, ACT_THEN_ARTICLE_RE):
        for match in pattern.finditer(text):
            if pattern is ACT_THEN_ARTICLE_RE:
                before = text[max(0, match.start() - 24) : match.start()]
                if re.search(r"\bartt?\.?\s*\d+[a-zA-Z]?\s*$", before, flags=re.IGNORECASE):
                    continue
            act = match.group("act")
            for article in expand_article_numbers(match.group("arts")):
                raw = compact_ws(match.group(0))
                item = {
                    "citation": canonical_citation(article, act, raw),
                    "article": article,
                    "act": norm_act(act),
                    "source_type": source_type_for(act, raw),
                    "raw_match": raw,
                }
                if valid_detected_source(item):
                    detected.append(item)

    for raw in extract_sources(text):
        if ARTICLE_THEN_ACT_RE.search(raw) or ACT_THEN_ARTICLE_RE.search(raw):
            continue
        raw_type = source_type_for("", raw)
        if raw_type == "unknown":
            continue
        if raw_type == "eu_law" and raw_eu_article_out_of_range(raw):
            continue
        item = {
            "citation": compact_ws(raw),
            "article": None,
            "act": norm_act(raw) if raw_type == "italian_statute" else "",
            "source_type": raw_type,
            "raw_match": compact_ws(raw),
        }
        if valid_detected_source(item):
            detected.append(item)

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in detected:
        key = source_citation_key(item)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    acts_with_articles = {
        str(item.get("act") or "")
        for item in deduped
        if item.get("source_type") == "italian_statute" and item.get("article") and item.get("act")
    }
    filtered = [
        item
        for item in deduped
        if not (
            item.get("source_type") == "italian_statute"
            and not item.get("article")
            and str(item.get("act") or "") in acts_with_articles
        )
    ]
    return filtered[:120]


# Domini/local-part chiaramente fittizi: una email che li usa NON è un dato personale reale.
PLACEHOLDER_EMAIL_DOMAINS = (
    "azienda.it",
    "esempio.it",
    "esempio.com",
    "example.com",
    "example.org",
    "email.com",
    "dominio.it",
    "test.it",
    "pec.it",
)
PLACEHOLDER_EMAIL_LOCALPARTS = (
    "nome.cognome",
    "nome",
    "cognome",
    "mario.rossi",
    "info",
    "amministrazione",
    "utente",
    "user",
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# Codice fiscale persona fisica: 6 lettere, 2 cifre, lettera, 2 cifre, lettera, 3 cifre, lettera.
CODICE_FISCALE_RE = re.compile(r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b")


def is_placeholder_email(addr: str) -> bool:
    addr = addr.lower()
    local, _, domain = addr.partition("@")
    if domain in PLACEHOLDER_EMAIL_DOMAINS:
        return True
    if local in PLACEHOLDER_EMAIL_LOCALPARTS:
        return True
    return False


def real_emails(text: str) -> list[str]:
    """Email che non sembrano placeholder/esempi."""
    found = []
    for addr in EMAIL_RE.findall(text):
        if not is_placeholder_email(addr):
            found.append(addr)
    return sorted(set(found))


def infer_confidential_detail(text: str) -> tuple[bool, list[str]]:
    """Restituisce (confidential, reasons).

    Si basa su segnali FORTI di dato personale reale (email non placeholder, codici
    fiscali). Le parole-tema (email, società, lavoratore, GDPR) da sole non bastano:
    indicano l'argomento, non la riservatezza. Così un parere anonimizzato con sole
    email-esempio (es. nome.cognome@azienda.it) non viene trattato come riservato.
    """
    reasons: list[str] = []
    emails = real_emails(text)
    if emails:
        reasons.append(f"email reale rilevata ({', '.join(emails[:3])})")
    if CODICE_FISCALE_RE.search(text):
        reasons.append("codice fiscale rilevato")
    if reasons:
        return True, reasons
    # Nessun dato personale reale: segnaliamo solo che il tema è sensibile.
    norm = normalize_for_match(text)
    topic_markers = [
        "dipendente",
        "lavoratore",
        "email",
        "mailbox",
        "casella",
        "dati personali",
        "contenzioso",
        "licenziamento",
        "gdpr",
        "privacy",
    ]
    if any(marker in norm for marker in topic_markers):
        return False, ["solo tema lavoro/privacy/dati, nessun dato personale reale rilevato"]
    return False, ["nessun segnale di materiale riservato"]


def infer_confidential(text: str) -> bool:
    confidential, _ = infer_confidential_detail(text)
    return confidential


def candidate_id_for(path: Path, explicit: str | None = None, index: int = 0) -> str:
    if explicit:
        return explicit
    stem = path.stem.strip()
    match = re.search(r"(?:^|[-_\s])([A-Z])(?:$|[-_\s])", stem)
    if match:
        return match.group(1)
    return chr(ord("A") + index)


def build_case(
    path: Path,
    *,
    candidate_id: str | None = None,
    index: int = 0,
    preset: str | None = None,
    quesito: str | None = None,
    ground_truth: str | None = None,
    confidential: bool | None = None,
    data_riferimento: str | None = None,
) -> dict[str, Any]:
    text, extraction = extract_text(path)
    sections = split_sections(text)
    preset_data = PRESETS.get(preset or "", {})
    answer_text = sections.get("risposta") or text
    inferred_confidential, confidential_reason = infer_confidential_detail(text)
    if confidential is None:
        case_confidential = inferred_confidential
    else:
        case_confidential = confidential
        confidential_reason = [f"override esplicito: --{'confidential' if confidential else 'no-confidential'}"]
    case = {
        "candidate_id": candidate_id_for(path, candidate_id, index),
        "source_file": str(path),
        "quesito": quesito or sections.get("quesito") or preset_data.get("quesito", ""),
        "risposta": answer_text,
        "ground_truth": ground_truth
        or sections.get("ground_truth")
        or preset_data.get("ground_truth", ""),
        "data_riferimento": data_riferimento or today_iso(),
        "fonti": extract_sources(text) or preset_data.get("fonti", []),
        "confidential": case_confidential,
        "confidential_reason": confidential_reason,
        "extraction": extraction,
    }
    if preset:
        case["preset"] = preset
        case["required_topics"] = preset_data.get("required_topics", [])
    if not (case["quesito"] or "").strip():
        case.setdefault("warnings", []).append(
            "Quesito non trovato nel documento e non fornito: passa --quesito o usa --preset, "
            "altrimenti i giudici valutano senza la domanda di riferimento."
        )
    return case


def load_ground_truth(raw: str | None) -> str | None:
    if not raw:
        return None
    path = Path(raw)
    if path.exists():
        text, _ = extract_text(path)
        return text
    return raw


def keyword_set(text: str) -> set[str]:
    norm = normalize_for_match(text)
    words = re.findall(r"[a-z0-9]{4,}", norm)
    return {word for word in words if word not in STOPWORDS}


def score_to_discrete(score: float) -> int:
    if score < 20:
        return 0
    if score < 27:
        return 1
    if score < 34:
        return 2
    return 3


def clamp_score(value: int) -> int:
    return max(0, min(3, value))


def find_risks(answer: str) -> dict[str, list[str]]:
    norm = normalize_for_match(answer)
    hallucinations: list[str] = []
    stale: list[str] = []
    privacy: list[str] = []
    if re.search(r"\b99999/\d{4}\b", answer):
        hallucinations.append("Implausible judgment number detected.")
    if "sentenza inventata" in norm or "cassazione inesistente" in norm:
        hallucinations.append("Answer refers to invented case law.")
    if "art. 18" in norm and ("pre-2012" in norm or "reintegra sempre" in norm):
        stale.append("Potential stale article 18 Workers' Statute framing.")
    if "forward" in norm or "inoltro" in norm or "reindirizz" in norm:
        if not any(term in norm for term in ("minimizz", "informativa", "base giuridica", "limitazione")):
            privacy.append("Email forwarding discussed without core GDPR safeguards.")
    return {"hallucinations": hallucinations, "stale": stale, "privacy": privacy}


def topic_coverage(answer: str, ground_truth: str, required_topics: list[str]) -> tuple[float, list[str]]:
    norm = normalize_for_match(answer)
    if required_topics:
        missing = [topic for topic in required_topics if normalize_for_match(topic) not in norm]
        return (len(required_topics) - len(missing)) / max(1, len(required_topics)), missing
    required = keyword_set(ground_truth)
    if not required:
        return 0.0, []
    present = {word for word in required if word in norm}
    missing = sorted(required - present)[:20]
    return len(present) / max(1, len(required)), missing


def base_scores(case: dict[str, Any]) -> dict[str, Any]:
    answer = case.get("risposta", "")
    ground_truth = case.get("ground_truth", "")
    required_topics = case.get("required_topics") or []
    citations = extract_sources(answer)
    risks = find_risks(answer)
    norm = normalize_for_match(answer)
    coverage, missing_topics = topic_coverage(answer, ground_truth, required_topics)

    source_score = 0
    if citations:
        source_score = 2
        if any(("comma" in normalize_for_match(c) or "co." in normalize_for_match(c)) for c in citations):
            source_score = 3
        if any(("cass" in normalize_for_match(c) or "garante" in normalize_for_match(c)) for c in citations):
            source_score = max(source_score, 3)
    elif any(term in norm for term in ("codice civile", "gdpr", "statuto dei lavoratori", "garante")):
        source_score = 1

    hallucination_score = 0 if risks["hallucinations"] else 2
    if hallucination_score == 2 and any(term in norm for term in ("verific", "non posso", "limite", "fonte ufficiale")):
        hallucination_score = 3

    normative_score = 0 if risks["hallucinations"] else 1
    if source_score >= 2:
        normative_score = 2
    if source_score >= 2 and coverage >= 0.55:
        normative_score = 3

    update_score = 0 if risks["stale"] else (2 if source_score >= 1 else 1)
    if any(term in norm for term in ("vigente", "aggiornat", "riforma", "verificare su normattiva")):
        update_score = max(update_score, 3)

    if coverage >= 0.75:
        completeness_score = 3
    elif coverage >= 0.45:
        completeness_score = 2
    elif coverage >= 0.2:
        completeness_score = 1
    else:
        completeness_score = 0

    uncertainty_score = 0
    if any(term in norm for term in ("dipende", "salvo", "rischio", "opportuno", "prudenza")):
        uncertainty_score = 1
    if any(term in norm for term in ("controvers", "orientament", "non univoc", "da verificare", "verificare")):
        uncertainty_score = 2
    if any(term in norm for term in ("orientamenti contrapposti", "giurisprudenza divisa", "prevalente")):
        uncertainty_score = 3

    return {
        "scores": {
            "correttezza_normativa": normative_score,
            "aggiornamento": update_score,
            "completezza": completeness_score,
            "assenza_allucinazioni": hallucination_score,
            "citazione_fonti": source_score,
            "segnalazione_incertezza": uncertainty_score,
        },
        "coverage": coverage,
        "missing_topics": missing_topics,
        "citations": citations,
        "risks": risks,
    }


def judge_adjusted_scores(scores: dict[str, int], judge_id: str, context: dict[str, Any]) -> dict[str, int]:
    adjusted = dict(scores)
    coverage = context["coverage"]
    citations = context["citations"]
    risks = context["risks"]
    if judge_id == "kimi_k26" and coverage < 0.65:
        adjusted["completezza"] -= 1
    if judge_id == "gpt" and not citations:
        adjusted["correttezza_normativa"] -= 1
        adjusted["citazione_fonti"] -= 1
    if judge_id == "claude_opus" and (risks["privacy"] or risks["hallucinations"]):
        adjusted["assenza_allucinazioni"] -= 1
        adjusted["segnalazione_incertezza"] -= 1
    if judge_id == "gemini_pro" and coverage >= 0.75 and citations:
        adjusted["completezza"] += 0
    return {key: clamp_score(int(value)) for key, value in adjusted.items()}


def criterion_reason(
    name: str,
    score: int,
    context: dict[str, Any],
) -> str:
    if name == "citazione_fonti":
        if context["citations"]:
            return f"Found {len(context['citations'])} legal/source reference(s), not live-verified."
        return "No specific legal source detected."
    if name == "completezza":
        missing = context["missing_topics"][:8]
        if missing:
            return f"Estimated topic coverage {context['coverage']:.0%}; missing examples: {', '.join(missing)}."
        return f"Estimated topic coverage {context['coverage']:.0%}."
    if name == "assenza_allucinazioni":
        risks = context["risks"]["hallucinations"]
        if risks:
            return "; ".join(risks)
        return "No deterministic hallucination trap detected; live verification still required."
    if name == "aggiornamento":
        risks = context["risks"]["stale"]
        if risks:
            return "; ".join(risks)
        return "No deterministic stale-law trap detected."
    if name == "segnalazione_incertezza":
        return "Score based on uncertainty, verification, and caution markers in the answer."
    return "Score based on source presence, topic coverage, and deterministic risk markers."


def evaluate_case(case: dict[str, Any], mode: str = "offline_mock") -> dict[str, Any]:
    context = base_scores(case)
    verdicts: list[dict[str, Any]] = []
    for judge in JUDGES:
        scores = judge_adjusted_scores(context["scores"], judge["judge_id"], context)
        criteria: dict[str, Any] = {}
        total = 0
        for name, score in scores.items():
            weight = WEIGHTS[name]
            weighted = score * weight
            total += weighted
            criteria[name] = {
                "score": score,
                "weight": weight,
                "weighted": weighted,
                "motivazione": criterion_reason(name, score, context),
            }
        flag = (
            total < 20
            or bool(context["risks"]["hallucinations"])
            or bool(context["risks"]["stale"])
            or bool(context["risks"]["privacy"])
            or case.get("confidential", False)
        )
        points: list[str] = []
        if context["risks"]["privacy"]:
            points.extend(context["risks"]["privacy"])
        if context["risks"]["hallucinations"]:
            points.extend(context["risks"]["hallucinations"])
        if not context["citations"]:
            points.append("Verify legal basis and add precise citations.")
        if context["missing_topics"]:
            points.append("Review omitted topics against the ground-truth checklist.")
        if case.get("confidential", False):
            points.append("Confidential material: approve any cloud route before live judging.")
        verdicts.append(
            {
                "judge_id": judge["judge_id"],
                "model_route": judge["model_route"],
                "role": judge["role"],
                "mode": mode,
                "criteria": criteria,
                "score_ponderato": total,
                "score_massimo": MAX_SCORE,
                "percentuale": round(total / MAX_SCORE * 100, 1),
                "kappa_discrete_score": score_to_discrete(total),
                "flag_revisione_umana": flag,
                "punti_critici_per_avvocato": sorted(set(points)),
            }
        )
    return aggregate_candidate(case, verdicts, context)


def source_check_notes(case: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    notes = ["Offline deterministic extraction only; citations were not live-verified."]
    if context["citations"]:
        notes.append(f"Detected citations/sources: {len(context['citations'])}.")
    if context["risks"]["hallucinations"]:
        notes.extend(context["risks"]["hallucinations"])
    if context["risks"]["stale"]:
        notes.extend(context["risks"]["stale"])
    if case.get("confidential"):
        notes.append("Route gate active: ask the user to choose local/offline or online/live unless already specified.")
    return {
        "status": "not_performed",
        "detected_sources": context["citations"],
        "notes": notes,
    }


def aggregate_candidate(
    case: dict[str, Any],
    verdicts: list[dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    scores = [v["score_ponderato"] for v in verdicts]
    mean_score = sum(scores) / len(scores)
    divergence = max(scores) - min(scores)
    flags = []
    if mean_score < 20:
        flags.append("mean_score_below_20")
    if divergence > 8:
        flags.append("judge_divergence_above_8")
    if any(v["flag_revisione_umana"] for v in verdicts):
        flags.append("judge_flagged_review")
    if context["risks"]["hallucinations"]:
        flags.append("possible_hallucinated_citation")
    if context["risks"]["stale"]:
        flags.append("possible_stale_law")
    if context["risks"]["privacy"]:
        flags.append("privacy_or_employment_law_risk")
    if case.get("confidential"):
        flags.append("confidential_material")
    return {
        "candidate_id": case["candidate_id"],
        "source_file": case["source_file"],
        "score_medio": round(mean_score, 2),
        "score_massimo": MAX_SCORE,
        "percentuale_media": round(mean_score / MAX_SCORE * 100, 1),
        "divergenza_max": divergence,
        "kappa_discrete_score": score_to_discrete(mean_score),
        "flag_revisione_umana": bool(flags),
        "human_review_flags": sorted(set(flags)),
        "confidential_reason": case.get("confidential_reason", []),
        "warnings": case.get("warnings", []),
        "source_check": source_check_notes(case, context),
        "coverage": round(context["coverage"], 3),
        "missing_topics": context["missing_topics"][:20],
        "verdetti_individuali": verdicts,
    }


def aggregate_comparison(candidates: list[dict[str, Any]], availability: dict[str, Any] | None = None) -> dict[str, Any]:
    ranking = sorted(candidates, key=lambda item: item["score_medio"], reverse=True)
    for idx, item in enumerate(ranking, start=1):
        item["rank"] = idx
    aggregated_warnings = sorted(
        {w for item in ranking for w in item.get("warnings", [])}
    )
    compact_ranking = [
        {
            "rank": item["rank"],
            "candidate_id": item["candidate_id"],
            "score_medio": item["score_medio"],
            "percentuale_media": item["percentuale_media"],
            "flag_revisione_umana": item["flag_revisione_umana"],
            "human_review_flags": item["human_review_flags"],
        }
        for item in ranking
    ]
    return {
        "generated_at": now_iso(),
        "mode": "offline_mock",
        "score_massimo": MAX_SCORE,
        "warnings": aggregated_warnings,
        "ranking": compact_ranking,
        "panel_ranking": {
            "status": "available" if compact_ranking else "not_available",
            "best_candidate_id": compact_ranking[0]["candidate_id"] if compact_ranking else None,
            "ranking": compact_ranking,
            "notes": ["Ranking del panel LLM: non equivale a valutazione legale finale."],
        },
        "legal_final_assessment": {
            "status": "non_determinato",
            "reason": "Nessuna revisione umana esplicita registrata nel risultato.",
        },
        "source_gate": {
            "status": "not_performed",
            "source_verification_status": "not_performed",
            "legal_final_assessment": "non_determinato",
            "notes": ["Le fonti non sono state verificate su fonti ufficiali o banche dati autorizzate."],
        },
        "candidates": ranking,
        "model_tool_availability": availability or {},
        "kappa_ready": [
            {
                "candidate_id": item["candidate_id"],
                "judge_scores": [
                    verdict["kappa_discrete_score"] for verdict in item["verdetti_individuali"]
                ],
                "aggregate_discrete_score": item["kappa_discrete_score"],
            }
            for item in ranking
        ],
        "notes": [
            "Offline results are screening signals, not legal opinions.",
            "Run live source verification before relying on citations or current-law claims.",
        ],
    }


def safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("_") or "item"


def write_text_no_overwrite(path: Path, text: str, *, force: bool = False) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json_no_overwrite(path: Path, data: Any, *, force: bool = False) -> None:
    raw = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    write_text_no_overwrite(path, raw, force=force)


def load_cases_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        return data["cases"]
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and data.get("candidate_id"):
        return [data]
    raise ValueError(f"Cannot find cases in {path}")


def normattiva_article_anchor(article: str | None) -> str:
    if not article:
        return ""
    cleaned = normalize_for_match(article)
    cleaned = re.sub(r"[^0-9a-z]+", "", cleaned)
    return f"~art{cleaned}" if cleaned else ""


def normattiva_url_for(act: str, article: str | None = None) -> str:
    key = norm_act(act).lower()
    if key in NORMATTIVA_ACT_URLS:
        return NORMATTIVA_ACT_URLS[key] + normattiva_article_anchor(article)
    if not key:
        return "https://www.normattiva.it/"
    query = urllib.parse.quote_plus(act)
    return f"https://www.normattiva.it/ricerca/semplice?query={query}"


def official_url_for_source(item: dict[str, Any]) -> str:
    source_type = item.get("source_type")
    act = str(item.get("act") or "")
    citation = str(item.get("citation") or "")
    if source_type == "italian_statute":
        return normattiva_url_for(act or citation, item.get("article"))
    if source_type == "eu_law":
        return EURLEX_GDPR_URL
    if "garante" in normalize_for_match(citation):
        return "https://www.garanteprivacy.it/"
    return ""


def verification_status_summary(records: list[dict[str, Any]]) -> str:
    if not records:
        return "not_performed"
    statuses = {record.get("status") for record in records}
    live_statuses = {"verified", "mismatch", "not_found"}
    if statuses == {"verified"}:
        return "verified"
    if statuses & live_statuses:
        return "partial"
    return "not_performed"


def preferred_tool_for_source(source_type: str) -> str:
    if source_type == "italian_statute":
        return "normattiva"
    if source_type == "eu_law":
        return "eur-lex"
    if source_type == "case_law_or_authority":
        return "buddalaw_mcp"
    return "manual_review"


def unavailable_record(
    item: dict[str, Any],
    *,
    preferred_tool: str,
    official_url: str,
    finding: str,
    tool_used: str | None = None,
    status: str = "unavailable",
    score_impact: str = "human_review_required",
) -> dict[str, Any]:
    if status not in SOURCE_STATUSES:
        raise ValueError(f"Unsupported source verification status: {status}")
    return {
        "citation": item.get("citation", ""),
        "article": item.get("article"),
        "act": item.get("act", ""),
        "source_type": item.get("source_type", "unknown"),
        "preferred_tool": preferred_tool,
        "tool_used": tool_used,
        "official_url": official_url,
        "status": status,
        "vigente_al": None,
        "article_text_excerpt": "",
        "finding": finding,
        "score_impact": score_impact,
    }


def has_any_command(tool_status: dict[str, Any]) -> bool:
    return any(tool_status.get("commands", {}).values())


def verify_italian_statute(item: dict[str, Any], source_tools: dict[str, Any]) -> dict[str, Any]:
    official_url = official_url_for_source(item)
    normattiva = source_tools.get("normattiva", {})
    if not normattiva.get("present") and not has_any_command(normattiva):
        return unavailable_record(
            item,
            preferred_tool="normattiva",
            official_url=official_url,
            finding=(
                "Normattiva skill missing. Install only after user approval: "
                f"{NORMATTIVA_INSTALL_COMMAND}"
            ),
        )
    return unavailable_record(
        item,
        preferred_tool="normattiva",
        tool_used="normattiva_skill",
        official_url=official_url,
        status="unsupported",
        finding=(
            "Normattiva appears available, but this wrapper did not fetch the article text. "
            "Use the Normattiva skill to read the official text, verify vigency, and paste the excerpt."
        ),
        score_impact="manual_official_check_required",
    )


def verify_eu_law(item: dict[str, Any]) -> dict[str, Any]:
    return unavailable_record(
        item,
        preferred_tool="eur-lex",
        official_url=official_url_for_source(item),
        finding=(
            "GDPR/EU law must be verified on EUR-Lex or another official EU source. "
            "Normattiva is intentionally not used for this citation."
        ),
    )


def verify_case_or_authority(
    item: dict[str, Any],
    source_tools: dict[str, Any],
    *,
    allow_cloud: bool = False,
    allow_web: bool = False,
) -> dict[str, Any]:
    official_url = official_url_for_source(item)
    attempts: list[str] = []
    buddalaw = source_tools.get("buddalaw", {})
    if buddalaw.get("present") or has_any_command(buddalaw) or buddalaw.get("mcp_config_detected"):
        return unavailable_record(
            item,
            preferred_tool="buddalaw_mcp",
            tool_used="buddalaw_mcp",
            official_url=official_url,
            status="unsupported",
            finding=(
                "BuddaLaw appears available/configured; use its MCP or approved legal-database route "
                "to verify existence and holding. The local wrapper did not invoke the MCP directly."
            ),
            score_impact="manual_case_law_check_required",
        )
    attempts.append("BuddaLaw unavailable")

    searxng = source_tools.get("searxng", {})
    if searxng.get("present") or has_any_command(searxng) or searxng.get("mcp_config_detected"):
        return unavailable_record(
            item,
            preferred_tool="buddalaw_mcp",
            tool_used="searxng",
            official_url=official_url,
            status="unsupported",
            finding=(
                "BuddaLaw unavailable; SearXNG appears available as fallback. "
                "Run targeted search and confirm against an official or authorized legal source."
            ),
            score_impact="manual_case_law_check_required",
        )
    attempts.append("SearXNG unavailable")

    perplexity = source_tools.get("perplexity", {})
    if perplexity.get("auth_quota_ok"):
        if allow_cloud:
            return unavailable_record(
                item,
                preferred_tool="buddalaw_mcp",
                tool_used="perplexity",
                official_url=official_url,
                status="unsupported",
                finding=(
                    "BuddaLaw and SearXNG unavailable; Perplexity auth/quota appears usable, "
                    "but this wrapper did not spend a cloud search call. Verify output against source links."
                ),
                score_impact="manual_case_law_check_required",
            )
        attempts.append("Perplexity available but cloud route not approved for this command")
    else:
        attempts.append("Perplexity unavailable or auth/quota not confirmed")

    if allow_web:
        return unavailable_record(
            item,
            preferred_tool="buddalaw_mcp",
            tool_used="web_base",
            official_url=official_url,
            status="unsupported",
            finding=(
                "BuddaLaw, SearXNG, and approved Perplexity route unavailable; use base web search "
                "only as discovery, then confirm against official or authorized legal sources."
            ),
            score_impact="manual_case_law_check_required",
        )

    return unavailable_record(
        item,
        preferred_tool="buddalaw_mcp",
        official_url=official_url,
        finding="; ".join(attempts) + "; base web fallback not enabled.",
    )


def verify_source_item(
    item: dict[str, Any],
    source_tools: dict[str, Any],
    *,
    allow_cloud: bool = False,
    allow_web: bool = False,
) -> dict[str, Any]:
    source_type = item.get("source_type", "unknown")
    if source_type == "italian_statute":
        return verify_italian_statute(item, source_tools)
    if source_type == "eu_law":
        return verify_eu_law(item)
    if source_type == "case_law_or_authority":
        return verify_case_or_authority(item, source_tools, allow_cloud=allow_cloud, allow_web=allow_web)
    return unavailable_record(
        item,
        preferred_tool=preferred_tool_for_source(source_type),
        official_url=official_url_for_source(item),
        status="unsupported",
        finding="Citation type not supported by the automatic source-verification wrapper.",
        score_impact="manual_review_required",
    )


def verify_sources_for_cases(
    cases: list[dict[str, Any]],
    *,
    allow_cloud: bool = False,
    allow_web: bool = False,
    availability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    availability = availability or doctor()
    source_tools = availability.get("source_tools", {})
    records: list[dict[str, Any]] = []
    per_case: list[dict[str, Any]] = []
    for case in cases:
        detected = detect_source_citations(case)
        case_records = [
            {
                **verify_source_item(
                    item,
                    source_tools,
                    allow_cloud=allow_cloud,
                    allow_web=allow_web,
                ),
                "candidate_id": case.get("candidate_id"),
                "raw_match": item.get("raw_match"),
            }
            for item in detected
        ]
        records.extend(case_records)
        per_case.append(
            {
                "candidate_id": case.get("candidate_id"),
                "source_file": case.get("source_file"),
                "detected_count": len(detected),
                "records": case_records,
            }
        )

    status = verification_status_summary(records)
    return {
        "generated_at": now_iso(),
        "status": status,
        "source_verification": {
            "status": status,
            "notes": [
                "Source verification is separate from LLM judging.",
                "Norme italiane: Normattiva; GDPR/UE: EUR-Lex; giurisprudenza/provvedimenti: BuddaLaw, SearXNG, Perplexity, web base.",
                "Statuses unavailable/unsupported mean no official text or holding was confirmed by this run.",
            ],
        },
        "policy_order": [
            "Norme italiane: Normattiva skill, official text, vigency, URL, excerpt.",
            "GDPR/UE: EUR-Lex or official EU source, not Normattiva.",
            "Giurisprudenza/provvedimenti: BuddaLaw MCP, then SearXNG, then Perplexity if approved/authenticated, then base web discovery.",
            "No live source available: source_verification remains not_performed.",
        ],
        "allow_cloud": allow_cloud,
        "allow_web": allow_web,
        "tool_availability": source_tools,
        "records": records,
        "cases": per_case,
    }


def selected_judge_ids(raw: str | None, routing: dict[str, Any]) -> list[str]:
    if not raw or raw == "auto":
        selected = [
            item["judge_id"]
            for item in routing.get("selected_primary_judges", [])
            if item and item.get("judge_id")
        ]
        return selected or list(PRIMARY_LIVE_JUDGES)
    judge_ids = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = [judge_id for judge_id in judge_ids if judge_id not in LIVE_JUDGE_PROFILES]
    if unknown:
        raise ValueError(f"Unknown live judge id(s): {', '.join(unknown)}")
    return judge_ids


def judge_prompt_schema(case: dict[str, Any], profile: dict[str, Any]) -> str:
    return json.dumps(
        {
            "judge_id": profile["judge_id"],
            "model_route": profile["model_route"],
            "mode": "live_model",
            "candidate_id": case["candidate_id"],
            "source_verification": {
                "status": "not_performed",
                "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
            },
            "criteria": {
                name: {
                    "score": 0,
                    "weight": weight,
                    "weighted": 0,
                    "motivazione": "Motivazione breve in italiano.",
                }
                for name, weight in WEIGHTS.items()
            },
            "score_ponderato": 0,
            "score_massimo": MAX_SCORE,
            "percentuale": 0.0,
            "flag_revisione_umana": True,
            "punti_critici_per_avvocato": ["..."],
            "sintesi": "Sintesi breve della valutazione.",
        },
        ensure_ascii=False,
        indent=2,
    )


def build_judge_prompt(case: dict[str, Any], profile: dict[str, Any]) -> str:
    criteria_lines = [
        f"- {CRITERION_LABELS[name]}: score 0-3, peso {WEIGHTS[name]}, massimo {WEIGHTS[name] * 3}"
        for name in CRITERION_ORDER
    ]
    return clean_text(
        f"""
Sei un giudice indipendente per valutare una risposta di diritto italiano.

CONTESTO E LIMITI
- Giudice: {profile['display_name']} ({profile['model_route']}).
- Valuta un solo candidato: {case['candidate_id']}.
- Materiale confidenziale nel caso: {str(bool(case.get('confidential'))).lower()}.
- source_verification: not_performed.
- Non fare ricerche web, Normattiva, Garante, banche dati o altre verifiche esterne.
- Non presentare citazioni, norme, sentenze o provvedimenti come verificati.
- Ignora vantaggi di stile, markdown, lunghezza o impaginazione salvo impatto sulla chiarezza legale.

QUESITO
{case.get('quesito', '')}

CHECKLIST / GROUND TRUTH OPERATIVA
{case.get('ground_truth', '')}

RUBRICA 0-39
{chr(10).join(criteria_lines)}

ISTRUZIONI
- Valuta criterio per criterio.
- Calcola weighted = score * weight e score_ponderato come somma dei weighted.
- Usa flag_revisione_umana=true se fonti non verificate, materiale confidenziale, punteggio basso, citazioni sospette, o lacune rilevanti.
- Restituisci SOLO JSON valido, senza markdown e senza testo prima o dopo.
- Usa esattamente questo schema e questi nomi di criterio:

{judge_prompt_schema(case, profile)}

CANDIDATO {case['candidate_id']}
SOURCE_FILE: {case.get('source_file', '')}
DATA_RIFERIMENTO: {case.get('data_riferimento', '')}
FONTI_ESTRATTE_NON_VERIFICATE:
{json.dumps(case.get('fonti', []), ensure_ascii=False, indent=2)}

RISPOSTA DA VALUTARE
{case.get('risposta', '')}
"""
    )


def supervisor_prompt_schema() -> str:
    return json.dumps(
        {
            "supervisor_id": DEFAULT_SUPERVISOR_JUDGE,
            "model_route": LIVE_JUDGE_PROFILES[DEFAULT_SUPERVISOR_JUDGE]["model_route"],
            "mode": "supervisor_meta_judge",
            "source_verification": {
                "status": "not_performed",
                "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
            },
            "ranking_confermato": True,
            "ranking_finale": [
                {"rank": 1, "candidate_id": "A", "score_supervisionato": 0}
            ],
            "disaccordi_rilevanti": [
                {
                    "candidate_id": "A",
                    "tema": "Motivo del disaccordo.",
                    "impatto": "Impatto sul ranking o sui flag.",
                }
            ],
            "override_flags": [
                {
                    "candidate_id": "A",
                    "flag": "human_review_required",
                    "motivo": "Motivo sintetico.",
                }
            ],
            "decisione_operativa": "Sintesi della decisione supervisionata.",
            "punti_da_verificare": ["..."],
        },
        ensure_ascii=False,
        indent=2,
    )


def build_supervisor_prompt(result: dict[str, Any]) -> str:
    return clean_text(
        f"""
Sei il supervisore/meta-giudice di un Panel of Judges per risposte di diritto italiano.

CONTESTO E LIMITI
- Ricevi risultati gia' normalizzati di tre giudici indipendenti per candidato.
- Non fare ricerche web, Normattiva, Garante, banche dati o altre verifiche esterne.
- Non presentare citazioni, norme, sentenze o provvedimenti come verificati.
- Il tuo compito non e' rifare tutti i giudizi, ma spiegare disaccordi, ranking finale, override e punti da controllare.
- Mantieni separata la verifica fonti dal giudizio LLM.

ISTRUZIONI
- Analizza divergenza tra giudici, raw_errors, flag e ranking.
- Se i giudici discordano per piu' di 8 punti su un candidato, spiega il tema del disaccordo.
- Se il ranking va mantenuto, confermalo; se va corretto, spiega il motivo.
- Usa flag_revisione_umana quando fonti non verificate, citazioni sospette o lacune rilevanti restano aperte.
- Restituisci SOLO JSON valido, senza markdown e senza testo prima o dopo.
- Usa questo schema:

{supervisor_prompt_schema()}

RISULTATI NORMALIZZATI DA SUPERVISIONARE
{json.dumps(result, ensure_ascii=False, indent=2)}
"""
    )


def shell_quote(path: Path) -> str:
    return "'" + str(path).replace("'", "'\"'\"'") + "'"


# Wrapper di timeout portabile (macOS non ha sempre `timeout`/`gtimeout`).
# `perl alarm` interrompe il comando dopo N secondi con exit code 142.
TIMEOUT_WRAPPER = "perl -e 'alarm shift; exec @ARGV' {seconds} "


def with_timeout(inner: str, raw: str, timeout: int | None) -> str:
    """Avvolge `inner` (comando-giudice senza redirezione) con timeout e redirige su raw."""
    if timeout and timeout > 0:
        return TIMEOUT_WRAPPER.format(seconds=timeout) + inner + f" > {raw}"
    return inner + f" > {raw}"


def command_for_prompt(
    profile: dict[str, Any],
    prompt_path: Path,
    raw_path: Path,
    timeout: int | None = None,
) -> str:
    prompt = f"$(cat {shell_quote(prompt_path)})"
    raw = shell_quote(raw_path)
    if profile["judge_id"] == "claude_opus_4_8":
        inner = (
            "claude --model claude-opus-4-8 --effort xhigh --print "
            f"--output-format text \"{prompt}\""
        )
        return with_timeout(inner, raw, timeout)
    if profile["judge_id"] == "codex_gpt_5_5_xhigh":
        inner = (
            "codex exec --skip-git-repo-check --ephemeral -m gpt-5.5 "
            "-c 'model_reasoning_effort=\"xhigh\"' "
            f"\"{prompt}\""
        )
        return with_timeout(inner, raw, timeout)
    if profile["tool"] == "pwm":
        model = profile["model_route"].split(":", 1)[1]
        inner = f"pwm ask --json --source none --model {model} \"{prompt}\""
        return with_timeout(inner, raw, timeout)
    if profile["judge_id"] == "claude_sonnet_recent":
        inner = f"claude --model sonnet --print --output-format text \"{prompt}\""
        return with_timeout(inner, raw, timeout)
    return f"# No command template for {profile['judge_id']}"


def cmd_prepare_supervisor(args: argparse.Namespace) -> None:
    result = json.loads(Path(args.input).read_text(encoding="utf-8"))
    supervisor_id = args.supervisor
    if supervisor_id not in LIVE_JUDGE_PROFILES:
        raise ValueError(f"Unknown supervisor id: {supervisor_id}")
    profile = LIVE_JUDGE_PROFILES[supervisor_id]
    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise FileExistsError(f"Refusing to write into non-empty directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = output_dir / f"supervisor__{supervisor_id}.prompt.md"
    raw_path = output_dir / f"supervisor__{supervisor_id}.raw.txt"
    prompt_text = build_supervisor_prompt(result)
    write_text_no_overwrite(prompt_path, prompt_text + "\n", force=args.force)
    command = command_for_prompt(profile, prompt_path, raw_path)
    run_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Review command before running the live supervisor/meta-judge call.",
        command,
    ]
    metadata = {
        "generated_at": now_iso(),
        "supervisor": compact_profile(profile),
        "normalized_input": str(args.input),
        "prompt_file": str(prompt_path),
        "expected_raw_file": str(raw_path),
        "command": command,
        "run_supervisor_script": str(output_dir / "run-supervisor.sh"),
        "notes": [
            "Run only after the user has chosen the online/live route.",
            "The supervisor reviews judge disagreement and ranking; it does not verify sources.",
        ],
    }
    write_json_no_overwrite(output_dir / "metadata.json", metadata, force=args.force)
    write_text_no_overwrite(output_dir / "run-supervisor.sh", "\n".join(run_lines) + "\n", force=args.force)
    emit_json(metadata, args.output)


def cmd_prepare_live(args: argparse.Namespace) -> None:
    if args.input_json:
        cases = load_cases_json(Path(args.input_json))
    else:
        if not args.files:
            raise SystemExit("prepare-live requires files or --input-json.")
        ground_truth = load_ground_truth(args.ground_truth)
        cases = [
            build_case(
                Path(path),
                index=idx,
                preset=args.preset,
                quesito=args.quesito,
                ground_truth=ground_truth,
                confidential=args.confidential,
                data_riferimento=args.data_riferimento,
            )
            for idx, path in enumerate(args.files)
        ]

    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise FileExistsError(f"Refusing to write into non-empty directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    availability = doctor()
    judge_ids = selected_judge_ids(args.judges, availability["routing"])
    profiles = [LIVE_JUDGE_PROFILES[judge_id] for judge_id in judge_ids]

    if args.cases_output:
        write_json_no_overwrite(Path(args.cases_output), {"cases": cases}, force=args.force)

    judge_timeout = getattr(args, "judge_timeout", 240)
    fallback_ids = [
        prof.get("judge_id")
        for prof in availability["routing"].get("fallback_order", [])
        if prof.get("judge_id") and prof.get("judge_id") not in judge_ids
    ]
    prompt_records: list[dict[str, Any]] = []
    run_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "# Review commands before running live model calls.",
        f"# Ogni chiamata ha un timeout di {judge_timeout}s (exit 142 = timeout).",
        "# FALLBACK SINGOLA CELLA: se UN giudice va in timeout o errore, NON rifare l'intero",
        "#   panel. Rilancia solo quel candidato x giudice con un modello di FAMIGLIA DIVERSA",
        f"#   tra i fallback disponibili: {', '.join(fallback_ids) or '(nessuno)'}.",
        "#   Mantieni lo stesso numero di giudici per ogni candidato per un confronto equo.",
    ]
    for case in cases:
        candidate = safe_id(case["candidate_id"])
        write_json_no_overwrite(output_dir / f"case-{candidate}.json", case, force=args.force)
        for profile in profiles:
            judge_id = profile["judge_id"]
            prompt_path = output_dir / f"{candidate}__{judge_id}.prompt.md"
            raw_path = output_dir / f"{candidate}__{judge_id}.raw.txt"
            prompt_text = build_judge_prompt(case, profile)
            write_text_no_overwrite(prompt_path, prompt_text + "\n", force=args.force)
            command = command_for_prompt(profile, prompt_path, raw_path, timeout=judge_timeout)
            prompt_records.append(
                {
                    "candidate_id": case["candidate_id"],
                    "judge_id": judge_id,
                    "model_route": profile["model_route"],
                    "prompt_file": str(prompt_path),
                    "expected_raw_file": str(raw_path),
                    "command": command,
                }
            )
            run_lines.append(command)

    metadata = {
        "generated_at": now_iso(),
        "source_verification": {
            "status": "not_performed",
            "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
        },
        "candidate_order": [case["candidate_id"] for case in cases],
        "judges": [compact_profile(profile) for profile in profiles],
        "routing": availability["routing"],
        "model_tool_availability": availability,
        "prompts": prompt_records,
        "run_live_script": str(output_dir / "run-live.sh"),
        "judge_timeout_seconds": judge_timeout,
        "single_cell_fallback": {
            "rule": "Se un giudice va in timeout/errore, sostituisci solo quella cella (candidato x giudice) con un fallback di famiglia diversa; non rifare l'intero panel.",
            "fallback_judges": fallback_ids,
        },
        "warnings": sorted({w for case in cases for w in case.get("warnings", [])}),
        "notes": [
            "Prompts are separate per candidate and judge.",
            "Run live commands only after the user has chosen the online/live route.",
            "Use prepare-supervisor after normalize-live to create the separate supervisor/meta-judge prompt.",
        ],
    }
    write_json_no_overwrite(output_dir / "metadata.json", metadata, force=args.force)
    write_text_no_overwrite(output_dir / "run-live.sh", "\n".join(run_lines) + "\n", force=args.force)
    emit_json(metadata, args.output)


def strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def text_candidates_from_json(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for key in ("result", "answer", "content", "text", "message", "final_message", "output"):
            item = value.get(key)
            if isinstance(item, str):
                found.append(item)
        choices = value.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                found.extend(text_candidates_from_json(choice))
        messages = value.get("messages")
        if isinstance(messages, list):
            for message in messages:
                found.extend(text_candidates_from_json(message))
    elif isinstance(value, list):
        for item in value:
            found.extend(text_candidates_from_json(item))
    return found


def parse_json_from_text(text: str) -> tuple[Any | None, str | None]:
    text = strip_code_fence(text)
    try:
        return json.loads(text), None
    except json.JSONDecodeError as direct_error:
        pass

    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(text[first : last + 1]), None
        except json.JSONDecodeError as exc:
            return None, f"JSON parse failed: {exc}"
    return None, "No JSON object found in raw output."


def payloads_from_raw(path: Path) -> tuple[list[Any], list[str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    payload, error = parse_json_from_text(raw)
    if payload is not None:
        nested_payloads: list[Any] = [payload]
        for text in text_candidates_from_json(payload):
            nested, nested_error = parse_json_from_text(text)
            if nested is not None and nested != payload:
                nested_payloads.append(nested)
            elif nested_error is None:
                continue
        return nested_payloads, []

    payloads: list[Any] = []
    errors = [error or "JSON parse failed."]
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        parsed, line_error = parse_json_from_text(line)
        if parsed is None:
            if line_error:
                errors.append(line_error)
            continue
        payloads.append(parsed)
        for text in text_candidates_from_json(parsed):
            nested, _ = parse_json_from_text(text)
            if nested is not None:
                payloads.append(nested)
    if payloads:
        return payloads, []
    return [], errors[:3]


def normalize_points(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def score_from_raw(raw: Any) -> int:
    try:
        return clamp_score(int(round(float(raw))))
    except (TypeError, ValueError):
        return 0


def normalize_verdict_record(
    record: dict[str, Any],
    *,
    fallback_candidate: str,
    fallback_judge: str,
    fallback_route: str,
    raw_file: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    criteria_raw = record.get("criteria")
    if not isinstance(criteria_raw, dict):
        return None, ["Verdict has no criteria object."]

    criteria: dict[str, Any] = {}
    total = 0
    for name in CRITERION_ORDER:
        item = criteria_raw.get(name)
        if not isinstance(item, dict):
            errors.append(f"Missing criterion: {name}")
            score = 0
            motivation = ""
        else:
            score = score_from_raw(item.get("score"))
            motivation = str(item.get("motivazione") or item.get("reason") or item.get("reasoning") or "")
        weight = WEIGHTS[name]
        weighted = score * weight
        total += weighted
        criteria[name] = {
            "score": score,
            "weight": weight,
            "weighted": weighted,
            "motivazione": motivation,
        }

    declared_total = record.get("score_ponderato")
    if declared_total is not None:
        try:
            if int(round(float(declared_total))) != total:
                errors.append(f"Declared score_ponderato {declared_total} recalculated as {total}.")
        except (TypeError, ValueError):
            errors.append(f"Invalid score_ponderato: {declared_total}.")

    source_verification = record.get("source_verification")
    if not isinstance(source_verification, dict):
        source_verification = {
            "status": "not_performed",
            "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
        }

    verdict = {
        "judge_id": str(record.get("judge_id") or fallback_judge),
        "model_route": str(record.get("model_route") or fallback_route),
        "mode": str(record.get("mode") or "live_model"),
        "candidate_id": str(record.get("candidate_id") or fallback_candidate),
        "source_verification": source_verification,
        "criteria": criteria,
        "score_ponderato": total,
        "score_massimo": MAX_SCORE,
        "percentuale": round(total / MAX_SCORE * 100, 1),
        "kappa_discrete_score": score_to_discrete(total),
        "flag_revisione_umana": bool(record.get("flag_revisione_umana", True)),
        "punti_critici_per_avvocato": normalize_points(record.get("punti_critici_per_avvocato")),
        "sintesi": str(record.get("sintesi") or record.get("summary") or ""),
        "raw_file": raw_file,
    }
    return verdict, errors


def verdict_records_from_payload(
    payload: Any,
    *,
    fallback_candidate: str,
    fallback_judge: str,
    fallback_route: str,
    raw_file: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    verdicts: list[dict[str, Any]] = []
    errors: list[str] = []
    if isinstance(payload, list):
        for item in payload:
            sub_verdicts, sub_errors = verdict_records_from_payload(
                item,
                fallback_candidate=fallback_candidate,
                fallback_judge=fallback_judge,
                fallback_route=fallback_route,
                raw_file=raw_file,
            )
            verdicts.extend(sub_verdicts)
            errors.extend(sub_errors)
        return verdicts, errors

    if not isinstance(payload, dict):
        return [], ["Payload is not a JSON object."]

    if isinstance(payload.get("judges"), list):
        for judge in payload["judges"]:
            if not isinstance(judge, dict):
                continue
            judge_id = str(judge.get("judge_id") or fallback_judge)
            route = str(judge.get("model_route") or fallback_route)
            for record in judge.get("verdicts", []):
                if not isinstance(record, dict):
                    continue
                verdict, sub_errors = normalize_verdict_record(
                    record,
                    fallback_candidate=fallback_candidate,
                    fallback_judge=judge_id,
                    fallback_route=route,
                    raw_file=raw_file,
                )
                if verdict:
                    verdicts.append(verdict)
                errors.extend(sub_errors)
        return verdicts, errors

    if isinstance(payload.get("verdicts"), list):
        for record in payload["verdicts"]:
            if not isinstance(record, dict):
                continue
            verdict, sub_errors = normalize_verdict_record(
                record,
                fallback_candidate=fallback_candidate,
                fallback_judge=fallback_judge,
                fallback_route=fallback_route,
                raw_file=raw_file,
            )
            if verdict:
                verdicts.append(verdict)
            errors.extend(sub_errors)
        return verdicts, errors

    if isinstance(payload.get("criteria"), dict):
        verdict, sub_errors = normalize_verdict_record(
            payload,
            fallback_candidate=fallback_candidate,
            fallback_judge=fallback_judge,
            fallback_route=fallback_route,
            raw_file=raw_file,
        )
        if verdict:
            verdicts.append(verdict)
        errors.extend(sub_errors)
        return verdicts, errors

    return [], ["Payload contains no judge verdict."]


def raw_identity_from_path(path: Path) -> tuple[str, str]:
    match = re.match(r"(.+?)__(.+?)\.raw\.(?:txt|json)$", path.name)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def criterion_averages(verdicts: list[dict[str, Any]]) -> dict[str, float]:
    if not verdicts:
        return {}
    return {
        name: round(
            sum(verdict["criteria"][name]["weighted"] for verdict in verdicts) / len(verdicts),
            2,
        )
        for name in CRITERION_ORDER
    }


def aggregate_live_results(
    *,
    cases: list[dict[str, Any]],
    verdicts: list[dict[str, Any]],
    raw_errors: list[dict[str, Any]],
    raw_dir: Path,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    by_candidate: dict[str, list[dict[str, Any]]] = {case["candidate_id"]: [] for case in cases}
    for verdict in verdicts:
        by_candidate.setdefault(verdict["candidate_id"], []).append(verdict)

    candidates: list[dict[str, Any]] = []
    for case in cases:
        candidate_id = case["candidate_id"]
        candidate_verdicts = by_candidate.get(candidate_id, [])
        scores = [verdict["score_ponderato"] for verdict in candidate_verdicts]
        flags: list[str] = []
        if not scores:
            flags.append("no_live_verdicts")
            mean_score = None
            divergence = None
        else:
            mean_score = sum(scores) / len(scores)
            divergence = max(scores) - min(scores)
            if mean_score < 20:
                flags.append("mean_score_below_20")
            if divergence > 8:
                flags.append("judge_divergence_above_8")
        if any(verdict.get("flag_revisione_umana") for verdict in candidate_verdicts):
            flags.append("judge_flagged_review")
        if case.get("confidential"):
            flags.append("confidential_material")
        flags.append("source_verification_not_performed")

        candidates.append(
            {
                "candidate_id": candidate_id,
                "source_file": case.get("source_file"),
                "score_medio": round(mean_score, 2) if mean_score is not None else None,
                "score_massimo": MAX_SCORE,
                "percentuale_media": round(mean_score / MAX_SCORE * 100, 1) if mean_score is not None else None,
                "divergenza_max": divergence,
                "criterion_averages": criterion_averages(candidate_verdicts),
                "flag_revisione_umana": True,
                "human_review_flags": sorted(set(flags)),
                "source_check": {
                    "status": "not_performed",
                    "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
                },
                "verdetti_individuali": candidate_verdicts,
                "punti_critici_per_avvocato": sorted(
                    {
                        point
                        for verdict in candidate_verdicts
                        for point in verdict.get("punti_critici_per_avvocato", [])
                    }
                ),
            }
        )

    ranked = sorted(
        [candidate for candidate in candidates if candidate["score_medio"] is not None],
        key=lambda item: item["score_medio"],
        reverse=True,
    )
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx
    unranked = [candidate for candidate in candidates if candidate["score_medio"] is None]
    for item in unranked:
        item["rank"] = None

    ranking = [
        {
            "rank": item["rank"],
            "candidate_id": item["candidate_id"],
            "score_medio": item["score_medio"],
            "percentuale_media": item["percentuale_media"],
            "flag_revisione_umana": item["flag_revisione_umana"],
            "human_review_flags": item["human_review_flags"],
        }
        for item in [*ranked, *unranked]
    ]

    fallback_reasons: list[str] = []
    for candidate in candidates:
        if candidate["score_medio"] is None:
            fallback_reasons.append(f"{candidate['candidate_id']}: no live verdicts.")
        if candidate["divergenza_max"] is not None and candidate["divergenza_max"] > 8:
            fallback_reasons.append(f"{candidate['candidate_id']}: judge divergence above 8.")
    if len(ranked) >= 2 and abs(ranked[0]["score_medio"] - ranked[1]["score_medio"]) <= 3:
        fallback_reasons.append("Top two candidates are within 3 points.")

    model_routes = sorted(
        {
            f"{verdict.get('judge_id')} ({verdict.get('model_route')})"
            for verdict in verdicts
        }
    )
    source_verification = {
        "status": "not_performed",
        "notes": ["Le citazioni non sono state controllate su fonti ufficiali."],
    }
    return {
        "generated_at": now_iso(),
        "mode": "live_normalized",
        "score_massimo": MAX_SCORE,
        "candidate_order": [case["candidate_id"] for case in cases],
        "ranking": ranking,
        "panel_ranking": {
            "status": "available" if ranking else "not_available",
            "best_candidate_id": ranked[0]["candidate_id"] if ranked else None,
            "ranking": ranking,
            "notes": ["Ranking del panel LLM: non equivale a valutazione legale finale."],
        },
        "legal_final_assessment": {
            "status": "non_determinato",
            "reason": "Nessuna revisione umana esplicita registrata nel risultato.",
        },
        "source_gate": {
            "status": "not_performed",
            "source_verification_status": "not_performed",
            "legal_final_assessment": "non_determinato",
            "notes": ["Le fonti non sono state verificate su fonti ufficiali o banche dati autorizzate."],
        },
        "candidates": [*ranked, *unranked],
        "source_verification": source_verification,
        "source_check": source_verification,
        "raw_dir": str(raw_dir),
        "raw_errors": raw_errors,
        "model_routes_used": model_routes,
        "model_tool_availability": (metadata or {}).get("model_tool_availability", {}),
        "routing": (metadata or {}).get("routing", {}),
        "fallback_recommended": bool(fallback_reasons),
        "fallback_reasons": fallback_reasons,
        "human_review_flags": sorted(
            {
                flag
                for candidate in candidates
                for flag in candidate.get("human_review_flags", [])
            }
        ),
        "kappa_ready": [
            {
                "candidate_id": item["candidate_id"],
                "judge_scores": [
                    verdict["kappa_discrete_score"] for verdict in item["verdetti_individuali"]
                ],
                "aggregate_discrete_score": score_to_discrete(item["score_medio"])
                if item["score_medio"] is not None
                else None,
            }
            for item in [*ranked, *unranked]
        ],
        "notes": [
            "Live LLM results are screening signals, not legal opinions.",
            "No official-source verification was performed.",
        ],
    }


def cmd_normalize_live(args: argparse.Namespace) -> None:
    cases = load_cases_json(Path(args.cases))
    raw_dir = Path(args.raw_dir)
    metadata_path = raw_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    prompt_metadata = {
        (safe_id(item["candidate_id"]), item["judge_id"]): item
        for item in metadata.get("prompts", [])
        if isinstance(item, dict) and item.get("candidate_id") and item.get("judge_id")
    }
    case_by_safe = {safe_id(case["candidate_id"]): case["candidate_id"] for case in cases}

    verdicts: list[dict[str, Any]] = []
    raw_errors: list[dict[str, Any]] = []
    raw_paths = [*raw_dir.glob("*.raw.txt"), *raw_dir.glob("*.raw.json")]
    for raw_path in sorted(raw_paths):
        candidate_safe, judge_id = raw_identity_from_path(raw_path)
        candidate_id = case_by_safe.get(candidate_safe, candidate_safe)
        prompt_record = prompt_metadata.get((candidate_safe, judge_id), {})
        route = prompt_record.get("model_route") or LIVE_JUDGE_PROFILES.get(judge_id, {}).get("model_route", judge_id)
        payloads, parse_errors = payloads_from_raw(raw_path)
        if parse_errors:
            raw_errors.append({"raw_file": str(raw_path), "candidate_id": candidate_id, "judge_id": judge_id, "errors": parse_errors})
            continue
        file_verdicts: list[dict[str, Any]] = []
        file_errors: list[str] = []
        for payload in payloads:
            extracted, errors = verdict_records_from_payload(
                payload,
                fallback_candidate=candidate_id,
                fallback_judge=judge_id,
                fallback_route=route,
                raw_file=str(raw_path),
            )
            file_verdicts.extend(extracted)
            file_errors.extend(errors)
        if file_verdicts:
            file_errors = [error for error in file_errors if error != "Payload contains no judge verdict."]
        if not file_verdicts:
            raw_errors.append(
                {
                    "raw_file": str(raw_path),
                    "candidate_id": candidate_id,
                    "judge_id": judge_id,
                    "errors": file_errors or ["No verdict found."],
                }
            )
            continue
        verdicts.extend(file_verdicts)
        for error in file_errors:
            raw_errors.append({"raw_file": str(raw_path), "candidate_id": candidate_id, "judge_id": judge_id, "errors": [error]})

    result = aggregate_live_results(
        cases=cases,
        verdicts=verdicts,
        raw_errors=raw_errors,
        raw_dir=raw_dir,
        metadata=metadata,
    )
    emit_json(result, args.output)


def display_score(value: Any, maximum: int) -> str:
    if value is None:
        return "n.d."
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n.d."
    if number.is_integer():
        rendered = str(int(number))
    else:
        rendered = f"{number:.1f}"
    return f"{rendered}/{maximum}"


def reliability_label(score: float | None, source_status: str) -> str:
    if score is None:
        return "non valutabile: mancano verdict live validi."
    if score >= 27 and source_status == "verified":
        return "buona per bozza operativa, sempre sotto revisione legale."
    if score >= 27:
        return "utile come bozza interna, ma non affidabile per uso professionale finché le fonti non sono verificate."
    if score >= 20:
        return "utile solo come screening: serve revisione sostanziale di un avvocato."
    return "alto rischio: usare solo per capire cosa riscrivere."


def md_cell(value: Any, *, maximum: int = 90) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("|", "\\|")
    if len(text) > maximum:
        text = text[: maximum - 1].rstrip() + "…"
    return text or "n.d."


SOURCE_STATUS_PRIORITY = {
    "not_performed": 0,
    "unsupported": 1,
    "unavailable": 2,
    "verified": 3,
    "not_found": 4,
    "mismatch": 5,
}


def source_records_from_payload(sources: dict[str, Any] | list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not sources:
        return []
    if isinstance(sources, list):
        records: list[dict[str, Any]] = []
        for item in sources:
            if not isinstance(item, dict):
                continue
            if item.get("citation") or item.get("source_type"):
                records.append(item)
            else:
                records.extend(source_records_from_payload(item))
        return records
    if isinstance(sources.get("records"), list):
        return [item for item in sources["records"] if isinstance(item, dict)]
    records: list[dict[str, Any]] = []
    for case in sources.get("cases", []):
        if isinstance(case, dict) and isinstance(case.get("records"), list):
            records.extend(item for item in case["records"] if isinstance(item, dict))
    return records


def source_record_merge_key(record: dict[str, Any]) -> tuple[str, str, str]:
    citation = normalize_for_match(str(record.get("citation") or ""))
    citation = citation.replace("artt.", "art.").replace("artt ", "art ")
    citation = re.sub(r"\bc\.?\s*c\.?\b", "c.c.", citation)
    citation = re.sub(r"\s+", " ", citation).strip(" .")
    return (
        str(record.get("candidate_id") or ""),
        citation,
        str(record.get("source_type") or "unknown"),
    )


def stronger_source_record(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_status = str(left.get("status") or "not_performed")
    right_status = str(right.get("status") or "not_performed")
    if SOURCE_STATUS_PRIORITY.get(right_status, 0) > SOURCE_STATUS_PRIORITY.get(left_status, 0):
        base, extra = right, left
    else:
        base, extra = left, right
    merged = dict(extra)
    merged.update({key: value for key, value in base.items() if value not in (None, "", [])})
    if extra.get("raw_match") and not merged.get("raw_match"):
        merged["raw_match"] = extra["raw_match"]
    return merged


def source_status_from_records(records: list[dict[str, Any]]) -> str:
    return verification_status_summary(records)


def merge_source_payloads(payloads: list[dict[str, Any] | list[dict[str, Any]]]) -> dict[str, Any]:
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for payload in payloads:
        for record in source_records_from_payload(payload):
            key = source_record_merge_key(record)
            if key in by_key:
                by_key[key] = stronger_source_record(by_key[key], record)
            else:
                by_key[key] = dict(record)
    records = list(by_key.values())
    status = source_status_from_records(records)
    return {
        "generated_at": now_iso(),
        "status": status,
        "source_verification": {
            "status": status,
            "notes": [
                "Registro fonti unificato da uno o piu' file --sources.",
                "Il record piu' verificato prevale sui record grezzi di routing.",
            ],
        },
        "records": records,
        "source_gate": source_gate_from_records(records),
    }


def source_gate_from_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {status: 0 for status in ["verified", "mismatch", "not_found", "unavailable", "unsupported", "not_performed"]}
    for record in records:
        status = str(record.get("status") or "not_performed")
        counts[status] = counts.get(status, 0) + 1

    verified = counts.get("verified", 0)
    problems = counts.get("mismatch", 0) + counts.get("not_found", 0)
    unresolved = counts.get("unavailable", 0) + counts.get("unsupported", 0) + counts.get("not_performed", 0)
    performed = verified + problems

    if not records or performed == 0:
        status = "not_performed"
        passed = False
        notes = ["Nessuna fonte e' stata confermata da fonte ufficiale o banca dati autorizzata."]
    elif problems:
        status = "passed_with_findings" if verified else "failed"
        passed = False
        notes = ["Almeno una fonte e' stata verificata, ma esistono mismatch o fonti non trovate."]
    elif unresolved:
        status = "passed_with_findings"
        passed = False
        notes = ["Almeno una fonte e' verificata, ma restano citazioni non risolte o non supportate."]
    else:
        status = "passed"
        passed = True
        notes = ["Le fonti nel registro allegato risultano verificate."]

    return {
        "status": status,
        "passed": passed,
        "source_verification_status": source_status_from_records(records),
        "counts": counts,
        "legal_final_assessment": "non_determinato",
        "notes": notes,
    }


def source_gate_from_payload(
    data: dict[str, Any],
    sources: dict[str, Any] | list[dict[str, Any]] | None,
) -> dict[str, Any]:
    records = source_records_from_payload(sources)
    if records:
        return source_gate_from_records(records)
    gate = data.get("source_gate")
    if isinstance(gate, dict):
        return gate
    return source_gate_from_records([])


def source_status_from_payload(
    data: dict[str, Any],
    sources: dict[str, Any] | list[dict[str, Any]] | None,
) -> str:
    if isinstance(sources, dict):
        if isinstance(sources.get("source_gate"), dict):
            return str(sources["source_gate"].get("source_verification_status") or sources.get("status") or "not_performed")
        if isinstance(sources.get("source_verification"), dict):
            return str(sources["source_verification"].get("status") or sources.get("status") or "not_performed")
        if sources.get("status"):
            return str(sources.get("status"))
    if isinstance(data.get("source_verification"), dict):
        return str(data["source_verification"].get("status") or "not_performed")
    return "not_performed"


def append_source_verification_section(
    lines: list[str],
    data: dict[str, Any],
    sources: dict[str, Any] | list[dict[str, Any]] | None,
) -> None:
    records = source_records_from_payload(sources)
    source_status = source_status_from_payload(data, sources)
    source_gate = source_gate_from_payload(data, sources)
    lines.extend(
        [
            "## Verifica fonti ufficiali",
            "",
            "Ordine applicato: norme italiane su Normattiva; GDPR e diritto UE su EUR-Lex; giurisprudenza e provvedimenti con BuddaLaw, poi SearXNG, poi Perplexity se approvato e autenticato, poi ricerca web base solo come scoperta.",
            "",
            f"Gate fonti: `source_gate: {source_gate.get('status', 'not_performed')}`. Valutazione legale finale: `legal_final_assessment: non_determinato` finché non risulta una revisione umana esplicita.",
            "",
        ]
    )
    if not records:
        lines.extend(
            [
                f"Stato: `source_verification: {source_status}`. Non ci sono record di verifica fonti allegati al report.",
                "",
            ]
        )
        return

    lines.append(f"Stato complessivo: `source_verification: {source_status}`.")
    lines.append("")
    lines.append(
        "Quando una citazione normativa risulta nel testo ufficiale, resta comunque da controllare se sostiene esattamente l'uso fatto dal candidato: questa verifica di pertinenza giuridica è distinta dalla semplice esistenza dell'articolo."
    )
    lines.append("")

    statute_records = [
        record
        for record in records
        if record.get("source_type") in {"italian_statute", "eu_law"}
    ]
    authority_records = [
        record
        for record in records
        if record.get("source_type") not in {"italian_statute", "eu_law"}
    ]

    if statute_records:
        lines.append("### Norme")
        lines.append("")
        lines.append("| Citazione | Fonte ufficiale | Contenuto verificato | Vigenza | Impatto |")
        lines.append("| --- | --- | --- | --- | --- |")
        for record in statute_records:
            source = record.get("tool_used") or record.get("preferred_tool") or "n.d."
            url = record.get("official_url")
            if url:
                source = f"{source}: {url}"
            content = record.get("article_text_excerpt") or f"{record.get('status', 'n.d.')}: {record.get('finding', '')}"
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_cell(record.get("citation")),
                        md_cell(source, maximum=120),
                        md_cell(content, maximum=130),
                        md_cell(record.get("vigente_al")),
                        md_cell(record.get("score_impact")),
                    ]
                )
                + " |"
            )
        lines.append("")

    if authority_records:
        lines.append("### Giurisprudenza e provvedimenti")
        lines.append("")
        lines.append("| Citazione | Tool usato | Stato | Esito | Impatto |")
        lines.append("| --- | --- | --- | --- | --- |")
        for record in authority_records:
            lines.append(
                "| "
                + " | ".join(
                    [
                        md_cell(record.get("citation")),
                        md_cell(record.get("tool_used") or record.get("preferred_tool")),
                        md_cell(record.get("status")),
                        md_cell(record.get("finding"), maximum=130),
                        md_cell(record.get("score_impact")),
                    ]
                )
                + " |"
            )
        lines.append("")


def report_from_result(data: dict[str, Any], sources: dict[str, Any] | list[dict[str, Any]] | None = None) -> str:
    candidates_by_id = {candidate["candidate_id"]: candidate for candidate in data.get("candidates", [])}
    candidate_order = data.get("candidate_order") or [candidate["candidate_id"] for candidate in data.get("candidates", [])]
    ranking = [item for item in data.get("ranking", []) if item.get("rank")]
    best = ranking[0] if ranking else None
    source_status = source_status_from_payload(data, sources)
    source_gate = source_gate_from_payload(data, sources)
    best_candidate = candidates_by_id.get(best["candidate_id"]) if best else None
    best_score = best_candidate.get("score_medio") if best_candidate else None

    if best:
        panel_ranking_text = (
            f"Il candidato migliore è {best['candidate_id']} con "
            f"{display_score(best_score, MAX_SCORE)}. "
            f"Affidabilità pratica: {reliability_label(best_score, source_status)}"
        )
    else:
        panel_ranking_text = "Non c'è un candidato migliore: mancano verdict live validi."

    provisional = source_gate.get("status") != "passed"
    report_status = (
        "Report tecnico provvisorio: il gate fonti non è pienamente superato."
        if provisional
        else "Report tecnico con gate fonti superato; resta necessaria revisione legale umana."
    )

    lawyer_checks = (
        "Un avvocato deve verificare norme, sentenze, provvedimenti del Garante, "
        "statuto, deleghe/procure, poteri di firma, contratti e policy IT/privacy "
        "prima di riutilizzare il contenuto."
    )

    lines: list[str] = [
        "# Report Panel Legale A/B/C",
        "",
        "## Risposta breve",
        "",
        report_status,
        "",
        f"Panel ranking: {panel_ranking_text}",
        "",
        "Legal final assessment: `non_determinato`. Il panel non registra una revisione umana esplicita e non sostituisce il giudizio dell'avvocato.",
        "",
        lawyer_checks,
        "",
        "## A colpo d'occhio",
        "",
    ]

    header = ["Criterio", *candidate_order]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---", *["---:" for _ in candidate_order]]) + " |")
    for criterion in CRITERION_ORDER:
        maximum = WEIGHTS[criterion] * 3
        row = [f"{CRITERION_LABELS[criterion]} (/{maximum})"]
        for candidate_id in candidate_order:
            candidate = candidates_by_id.get(candidate_id, {})
            row.append(display_score(candidate.get("criterion_averages", {}).get(criterion), maximum))
        lines.append("| " + " | ".join(row) + " |")
    total_row = ["Totale (/39)"]
    rank_row = ["Ranking"]
    for candidate_id in candidate_order:
        candidate = candidates_by_id.get(candidate_id, {})
        total_row.append(display_score(candidate.get("score_medio"), MAX_SCORE))
        rank = candidate.get("rank")
        rank_row.append(str(rank) if rank else "n.d.")
    lines.append("| " + " | ".join(total_row) + " |")
    lines.append("| " + " | ".join(rank_row) + " |")

    lines.extend(
        [
            "",
            "## Come leggere il risultato",
            "",
            f"`source_verification: {source_status}` e `source_gate: {source_gate.get('status', 'not_performed')}` riguardano solo il controllo delle fonti. I punteggi misurano la qualità interna delle risposte, non la verità delle citazioni né la pertinenza giuridica finale.",
            "",
        ]
    )

    append_source_verification_section(lines, data, sources)

    lines.append("## Note per candidato")
    lines.append("")
    for candidate_id in candidate_order:
        candidate = candidates_by_id.get(candidate_id, {})
        lines.append(f"### Candidato {candidate_id}")
        lines.append("")
        lines.append(f"- Punteggio medio: {display_score(candidate.get('score_medio'), MAX_SCORE)}.")
        lines.append(f"- Revisione umana: {'sì' if candidate.get('flag_revisione_umana', True) else 'no'}.")
        flags = candidate.get("human_review_flags") or []
        if flags:
            lines.append(f"- Flag principali: {', '.join(flags[:6])}.")
        points = candidate.get("punti_critici_per_avvocato") or []
        if points:
            lines.append("- Punti da controllare:")
            for point in points[:5]:
                lines.append(f"  - {point}")
        else:
            lines.append("- Punti da controllare: verificare comunque fonti e presupposti fattuali.")
        lines.append("")

    lines.extend(
        [
            "## Appendice tecnica",
            "",
            f"- Modelli/rotte usate: {', '.join(data.get('model_routes_used') or ['nessun verdict live valido'])}.",
            f"- Raw salvati in: `{data.get('raw_dir', 'n.d.')}`.",
            f"- Errori JSON/raw: {len(data.get('raw_errors') or [])}.",
        ]
    )
    for error in (data.get("raw_errors") or [])[:10]:
        lines.append(f"  - `{error.get('raw_file')}`: {'; '.join(error.get('errors', []))}")

    routing = data.get("routing") or {}
    spare = routing.get("perplexity_spare_judge")
    if spare:
        lines.append(f"- Perplexity route disponibile: {spare.get('display_name')} ({spare.get('model_route')}).")
    else:
        lines.append("- Perplexity route non usata o non disponibile; auth/quota non confermata nel risultato.")
    availability = data.get("model_tool_availability") or {}
    pwm = (availability.get("tools") or {}).get("pwm") or {}
    if pwm:
        pwm_notes: list[str] = []
        for check in pwm.get("checks", []):
            command = " ".join(check.get("command", []))
            if command in {"pwm login --check", "pwm usage"}:
                text = " ".join(
                    part
                    for part in (check.get("stdout", ""), check.get("stderr", ""))
                    if part
                ).strip()
                if text:
                    text = re.sub(r"\s+", " ", text)
                    pwm_notes.append(f"{command}: {text}")
        perplexity_live_routes = [
            route for route in (data.get("model_routes_used") or []) if "perplexity:" in str(route)
        ]
        if pwm_notes:
            lines.append(f"- Perplexity check sandbox: {' | '.join(pwm_notes)}")
        if perplexity_live_routes:
            lines.append("- Perplexity live: raw acquisiti e normalizzati; il check sandbox non e' stato trattato come indisponibilita'.")
    if data.get("fallback_recommended"):
        reasons = [str(reason).strip().rstrip(".") for reason in (data.get("fallback_reasons") or [])]
        lines.append(f"- Fallback consigliato: sì ({'; '.join(reasons)}).")
    else:
        lines.append("- Fallback consigliato: no, secondo le soglie del normalizzatore.")
    lines.extend(
        [
            "- Limitazione principale: nessuna verifica ufficiale delle fonti e nessuna consulenza legale sostitutiva.",
            "",
        ]
    )
    return "\n".join(lines)


def cmd_report(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    source_payloads = [json.loads(Path(path).read_text(encoding="utf-8")) for path in (args.sources or [])]
    sources = merge_source_payloads(source_payloads) if source_payloads else None
    report = report_from_result(data, sources=sources)
    if args.output:
        write_text_no_overwrite(Path(args.output), report + "\n", force=args.force)
    else:
        print(report)


def cmd_verify_sources(args: argparse.Namespace) -> None:
    cases = load_cases_json(Path(args.cases))
    result = verify_sources_for_cases(
        cases,
        allow_cloud=args.allow_cloud,
        allow_web=args.allow_web,
    )
    emit_json(result, args.output)


def doctor() -> dict[str, Any]:
    tools = {}
    checks = {
        "pwm": [
            (["pwm", "--version"], 5),
            (["pwm", "login", "--check"], 8),
            (["pwm", "usage"], 8),
        ],
        "pwm-mcp": [],
        "nlm": [["nlm", "--version"]],
        "notebooklm-mcp": [],
        "claude": [["claude", "--version"]],
        "codex": [["codex", "--version"]],
    }
    for name, commands in checks.items():
        path = shutil.which(name)
        results = []
        for item in commands:
            if isinstance(item, tuple):
                cmd, timeout = item
            else:
                cmd, timeout = item, 5
            if path:
                results.append(command_result(cmd, timeout=timeout))
        tools[name] = {"path": path, "available": bool(path), "checks": results}

    config_paths = [
        Path.home() / ".codex" / "settings.json",
        Path.home() / ".codex" / "config.toml",
        Path.home() / ".claude.json",
        Path.home() / ".claude" / "settings.json",
        Path.home() / ".claude" / "mcp.json",
    ]
    configs = []
    for path in config_paths:
        configs.append({"path": str(path), "exists": path.exists(), "readable": os.access(path, os.R_OK)})
    warnings = []
    if not tools["pwm"]["available"]:
        warnings.append("Perplexity CLI pwm not found.")
    if tools["pwm"]["available"]:
        auth_check = check_result_by_command(tools["pwm"], ["pwm", "login", "--check"])
        if auth_check and auth_check.get("exit_code") not in (0, None):
            warnings.append("Perplexity sandboxed auth check failed or was inconclusive; verify outside sandbox before treating it as unavailable.")
    if not tools["nlm"]["available"]:
        warnings.append("NotebookLM CLI nlm not found.")
    routing = select_model_routes(tools)
    warnings.extend(routing["warnings"])
    source_tools = source_tool_statuses(tools, config_paths)
    if source_tools["normattiva"].get("install_required"):
        warnings.append("Normattiva skill missing.")
    if not (
        source_tools["buddalaw"].get("present")
        or source_tools["buddalaw"].get("mcp_config_detected")
        or has_any_command(source_tools["buddalaw"])
    ):
        warnings.append("BuddaLaw MCP/legal database not detected.")
    if not (
        source_tools["gestiolex"].get("present")
        or source_tools["gestiolex"].get("mcp_config_detected")
        or has_any_command(source_tools["gestiolex"])
    ):
        warnings.append("GestioLex Corpus MCP/legal database not detected.")
    if not (
        source_tools["searxng"].get("present")
        or source_tools["searxng"].get("mcp_config_detected")
        or has_any_command(source_tools["searxng"])
    ):
        warnings.append("SearXNG skill/MCP not detected.")
    if source_tools["workspace_skill_copy"].get("differs"):
        warnings.append("Installed concilio-llm-prompt-legale skill differs from workspace copy.")
    return {
        "generated_at": now_iso(),
        "no_model_calls_spent": True,
        "tools": tools,
        "routing": routing,
        "source_tools": source_tools,
        "mcp_config_candidates": configs,
        "warnings": sorted(set(warnings)),
    }


def cmd_extract(args: argparse.Namespace) -> None:
    ground_truth = load_ground_truth(args.ground_truth)
    cases = [
        build_case(
            Path(path),
            index=idx,
            candidate_id=args.candidate_id if len(args.files) == 1 else None,
            preset=args.preset,
            quesito=args.quesito,
            ground_truth=ground_truth,
            confidential=args.confidential,
            data_riferimento=args.data_riferimento,
        )
        for idx, path in enumerate(args.files)
    ]
    emit_json(cases[0] if len(cases) == 1 else {"cases": cases}, args.output)


def cmd_single(args: argparse.Namespace) -> None:
    ground_truth = load_ground_truth(args.ground_truth)
    case = build_case(
        Path(args.file),
        candidate_id=args.candidate_id,
        preset=args.preset,
        quesito=args.quesito,
        ground_truth=ground_truth,
        confidential=args.confidential,
        data_riferimento=args.data_riferimento,
    )
    result = evaluate_case(case)
    emit_json(result, args.output)


def cmd_compare(args: argparse.Namespace) -> None:
    ground_truth = load_ground_truth(args.ground_truth)
    candidates = []
    for idx, file_name in enumerate(args.files):
        case = build_case(
            Path(file_name),
            index=idx,
            preset=args.preset,
            quesito=args.quesito,
            ground_truth=ground_truth,
            confidential=args.confidential,
            data_riferimento=args.data_riferimento,
        )
        candidates.append(evaluate_case(case))
    result = aggregate_comparison(candidates)
    emit_json(result, args.output)


# Checklist orientata al delta per il confronto base-vs-prompt-migliorato.
PROMPT_EVAL_DELTA_CHECKLIST = (
    "Confronto risposta base vs versione da miglioratore di prompt sullo stesso quesito. "
    "Valutare se la versione migliorata: aggiunge norme/citazioni corrette e pertinenti; "
    "riduce allucinazioni e citazioni non verificabili; resta pertinente al quesito senza "
    "andare fuori tema; migliora completezza e segnalazione dell'incertezza senza gonfiare "
    "lo stile. Non premiare la versione 'migliorata' per lunghezza o formattazione: contano "
    "solo correttezza, fonti verificabili e pertinenza."
)


def cmd_prompt_eval(args: argparse.Namespace) -> None:
    """Caso d'uso primario: risposta base (A) vs versione da prompt migliorato (B).

    ID neutri A/B per evitare bias verso la versione 'migliorata'; stesso quesito condiviso;
    checklist orientata al delta. Riusa build_case/evaluate_case/aggregate_comparison.
    """
    ground_truth = load_ground_truth(args.ground_truth)
    if ground_truth:
        ground_truth = f"{ground_truth}\n\n{PROMPT_EVAL_DELTA_CHECKLIST}"
    else:
        ground_truth = PROMPT_EVAL_DELTA_CHECKLIST
    pairs = [("A", args.baseline), ("B", args.improved)]
    candidates = []
    shared_quesito = args.quesito
    for idx, (cand_id, file_name) in enumerate(pairs):
        case = build_case(
            Path(file_name),
            candidate_id=cand_id,
            index=idx,
            preset=args.preset,
            quesito=shared_quesito,
            ground_truth=ground_truth,
            confidential=args.confidential,
            data_riferimento=args.data_riferimento,
        )
        # Il quesito del primo candidato (se estratto dal file) diventa quello condiviso.
        if not shared_quesito:
            shared_quesito = case.get("quesito") or None
            case["quesito"] = shared_quesito or case.get("quesito", "")
        candidates.append(evaluate_case(case))
    result = aggregate_comparison(candidates)
    result["mode"] = "prompt_eval_base_vs_improved"
    result.setdefault("notes", []).insert(
        0, "A = risposta base; B = risposta da miglioratore di prompt (ID anonimi per i giudici)."
    )
    emit_json(result, args.output)


def mock_cases() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "correct",
            "source_file": "mock",
            "quesito": PRESETS["civile"]["quesito"],
            "risposta": (
                "Il termine di prescrizione ordinario è decennale ai sensi "
                "dell'art. 2946 c.c., salvo i termini speciali previsti dalla "
                "legge. Per il risarcimento da fatto illecito si applica il "
                "termine quinquennale dell'art. 2947 c.c., distinto dalla "
                "responsabilità contrattuale. La norma va verificata nel testo "
                "vigente su fonte ufficiale e gli orientamenti giurisprudenziali "
                "vanno controllati su banca dati autorizzata, senza citare "
                "sentenze non verificabili."
            ),
            "ground_truth": PRESETS["civile"]["ground_truth"],
            "required_topics": PRESETS["civile"]["required_topics"],
            "data_riferimento": today_iso(),
            "fonti": [],
            "confidential": False,
            "extraction": {"format": "mock", "extracted_at": now_iso(), "notes": []},
        },
        {
            "candidate_id": "hallucinated_citation",
            "source_file": "mock",
            "quesito": "Verifica citazione",
            "risposta": "La Cass. civ. Sez. II, n. 99999/2024 conferma tutto.",
            "ground_truth": "Le sentenze citate devono essere verificabili.",
            "required_topics": [],
            "data_riferimento": today_iso(),
            "fonti": [],
            "confidential": False,
            "extraction": {"format": "mock", "extracted_at": now_iso(), "notes": []},
        },
        {
            "candidate_id": "stale_law",
            "source_file": "mock",
            "quesito": "Articolo 18",
            "risposta": "L'art. 18 pre-2012 comporta sempre reintegra sempre e comunque.",
            "ground_truth": "Distinguere il testo vigente e le riforme applicabili.",
            "required_topics": [],
            "data_riferimento": today_iso(),
            "fonti": [],
            "confidential": False,
            "extraction": {"format": "mock", "extracted_at": now_iso(), "notes": []},
        },
        {
            "candidate_id": "style_bias_plain",
            "source_file": "mock",
            "quesito": "Prescrizione",
            "risposta": "Il termine ordinario e decennale ai sensi dell'art. 2946 c.c.; va distinta l'azione aquiliana ex art. 2947 c.c.",
            "ground_truth": "Prescrizione ordinaria decennale art. 2946 c.c. Distinguere art. 2947 c.c.",
            "required_topics": [],
            "data_riferimento": today_iso(),
            "fonti": [],
            "confidential": False,
            "extraction": {"format": "mock", "extracted_at": now_iso(), "notes": []},
        },
        {
            "candidate_id": "style_bias_markdown",
            "source_file": "mock",
            "quesito": "Prescrizione",
            "risposta": "## Risposta\n\n**Art. 2946 c.c.**: termine decennale. Distinguere **art. 2947 c.c.** per responsabilita aquiliana.",
            "ground_truth": "Prescrizione ordinaria decennale art. 2946 c.c. Distinguere art. 2947 c.c.",
            "required_topics": [],
            "data_riferimento": today_iso(),
            "fonti": [],
            "confidential": False,
            "extraction": {"format": "mock", "extracted_at": now_iso(), "notes": []},
        },
    ]


def cmd_mock(args: argparse.Namespace) -> None:
    evaluated = [evaluate_case(case) for case in mock_cases()]
    result = aggregate_comparison(evaluated)
    failures = []
    by_id = {item["candidate_id"]: item for item in evaluated}
    if "possible_hallucinated_citation" not in by_id["hallucinated_citation"]["human_review_flags"]:
        failures.append("Hallucinated citation trap was not flagged.")
    if "possible_stale_law" not in by_id["stale_law"]["human_review_flags"]:
        failures.append("Stale-law trap was not flagged.")
    plain = by_id["style_bias_plain"]["score_medio"]
    markdown = by_id["style_bias_markdown"]["score_medio"]
    if abs(plain - markdown) > 4:
        failures.append("Markdown/prose style-bias pair diverged by more than 4 points.")
    result["mock_assertions"] = {"passed": not failures, "failures": failures}
    emit_json(result, args.output)
    if failures:
        sys.exit(1)


def add_case_args(parser: argparse.ArgumentParser, multiple: bool = False) -> None:
    file_arg = "files" if multiple else "file"
    parser.add_argument(file_arg, nargs="+" if multiple else None)
    parser.add_argument("--preset", choices=sorted(PRESETS), help="Built-in case checklist.")
    parser.add_argument("--quesito", help="Question text override.")
    parser.add_argument("--ground-truth", help="Ground-truth text or path.")
    parser.add_argument("--candidate-id", help="Candidate ID for single-file operations.")
    parser.add_argument("--data-riferimento", help="Reference date, default today.")
    parser.add_argument(
        "--confidential",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override confidentiality inference.",
    )
    parser.add_argument("--output", help="Write JSON to this path.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor_parser = sub.add_parser("doctor", help="Check local tools and MCP config candidates.")
    doctor_parser.set_defaults(func=lambda args: emit_json(doctor(), args.output))
    doctor_parser.add_argument("--output", help="Write JSON to this path.")

    extract_parser = sub.add_parser("extract", help="Extract files into normalized case JSON.")
    add_case_args(extract_parser, multiple=True)
    extract_parser.set_defaults(func=cmd_extract)

    single_parser = sub.add_parser("single", help="Evaluate one candidate file offline.")
    add_case_args(single_parser, multiple=False)
    single_parser.set_defaults(func=cmd_single)

    compare_parser = sub.add_parser("compare", help="Compare multiple candidate files offline.")
    add_case_args(compare_parser, multiple=True)
    compare_parser.set_defaults(func=cmd_compare)

    prompt_eval_parser = sub.add_parser(
        "prompt-eval",
        help="Caso primario: confronta risposta base vs versione da miglioratore di prompt (ID neutri A/B).",
    )
    prompt_eval_parser.add_argument("--baseline", required=True, help="Risposta base (candidato A).")
    prompt_eval_parser.add_argument("--improved", required=True, help="Risposta da prompt migliorato (candidato B).")
    prompt_eval_parser.add_argument("--preset", choices=sorted(PRESETS), help="Built-in case checklist.")
    prompt_eval_parser.add_argument("--quesito", help="Quesito condiviso (se assente, usa quello del file A).")
    prompt_eval_parser.add_argument("--ground-truth", help="Ground-truth text or path.")
    prompt_eval_parser.add_argument("--data-riferimento", help="Reference date, default today.")
    prompt_eval_parser.add_argument(
        "--confidential",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override confidentiality inference.",
    )
    prompt_eval_parser.add_argument("--output", help="Write JSON to this path.")
    prompt_eval_parser.set_defaults(func=cmd_prompt_eval)

    prepare_parser = sub.add_parser("prepare-live", help="Prepare one prompt per candidate and live judge.")
    prepare_parser.add_argument("files", nargs="*", help="Candidate files to extract.")
    prepare_parser.add_argument("--input-json", help="Existing cases JSON instead of files.")
    prepare_parser.add_argument("--preset", choices=sorted(PRESETS), help="Built-in case checklist.")
    prepare_parser.add_argument("--quesito", help="Question text override.")
    prepare_parser.add_argument("--ground-truth", help="Ground-truth text or path.")
    prepare_parser.add_argument("--data-riferimento", help="Reference date, default today.")
    prepare_parser.add_argument(
        "--confidential",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Override confidentiality inference.",
    )
    prepare_parser.add_argument("--judges", default="auto", help="Comma-separated live judge ids, or auto.")
    prepare_parser.add_argument(
        "--judge-timeout",
        type=int,
        default=240,
        help="Timeout per chiamata giudice in run-live.sh (secondi, 0 = nessun timeout).",
    )
    prepare_parser.add_argument("--output-dir", required=True, help="Directory for prompts, metadata, and raw outputs.")
    prepare_parser.add_argument("--cases-output", help="Write extracted cases JSON to this path.")
    prepare_parser.add_argument("--output", help="Write metadata JSON to this path as well as stdout.")
    prepare_parser.add_argument("--force", action="store_true", help="Allow overwriting generated files.")
    prepare_parser.set_defaults(func=cmd_prepare_live)

    normalize_parser = sub.add_parser("normalize-live", help="Normalize separate raw live judge outputs.")
    normalize_parser.add_argument("--cases", required=True, help="Cases JSON from extract or prepare-live.")
    normalize_parser.add_argument("--raw-dir", required=True, help="Directory containing *.raw.txt or *.raw.json files.")
    normalize_parser.add_argument("--output", help="Write normalized JSON to this path.")
    normalize_parser.set_defaults(func=cmd_normalize_live)

    supervisor_parser = sub.add_parser("prepare-supervisor", help="Prepare the supervisor/meta-judge prompt from normalized live results.")
    supervisor_parser.add_argument("--input", required=True, help="Normalized JSON from normalize-live.")
    supervisor_parser.add_argument("--output-dir", required=True, help="Directory for supervisor prompt, metadata, and raw output.")
    supervisor_parser.add_argument("--supervisor", default=DEFAULT_SUPERVISOR_JUDGE, help="Supervisor judge id.")
    supervisor_parser.add_argument("--output", help="Write metadata JSON to this path as well as stdout.")
    supervisor_parser.add_argument("--force", action="store_true", help="Allow overwriting generated files.")
    supervisor_parser.set_defaults(func=cmd_prepare_supervisor)

    verify_parser = sub.add_parser("verify-sources", help="Plan/check source verification for case citations.")
    verify_parser.add_argument("--cases", required=True, help="Cases JSON from extract or prepare-live.")
    verify_parser.add_argument("--output", help="Write source-verification JSON to this path.")
    verify_parser.add_argument(
        "--allow-cloud",
        action="store_true",
        help="Allow approved cloud-search fallbacks to be selected when authenticated.",
    )
    verify_parser.add_argument(
        "--allow-web",
        action="store_true",
        help="Allow base web fallback to be selected for unsupported citation types.",
    )
    verify_parser.set_defaults(func=cmd_verify_sources)

    report_parser = sub.add_parser("report", help="Generate a non-technical Markdown report from normalized JSON.")
    report_parser.add_argument("--input", required=True, help="Normalized JSON input.")
    report_parser.add_argument(
        "--sources",
        action="append",
        help="Source-verification JSON; repeat to merge Normattiva and case-law checks.",
    )
    report_parser.add_argument("--output", help="Write Markdown report to this path.")
    report_parser.add_argument("--force", action="store_true", help="Allow overwriting the report path.")
    report_parser.set_defaults(func=cmd_report)

    mock_parser = sub.add_parser("mock", help="Run deterministic offline trap tests.")
    mock_parser.add_argument("--output", help="Write JSON to this path.")
    mock_parser.set_defaults(func=cmd_mock)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
