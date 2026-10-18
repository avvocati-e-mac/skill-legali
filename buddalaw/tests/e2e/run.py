#!/usr/bin/env python3
"""Livello B: esegue la skill buddalaw end-to-end con BuddaLaw live e valuta tool call e testo.

Runtime
-------
- ``claude``  : Claude Code headless (``claude -p``), connettore claude.ai BuddaLaw.
  Isolamento: ``--disable-slash-commands`` spegne TUTTE le skill installate (anche la
  vecchia ~/.claude/skills/buddalaw v8.3); la skill in prova viene copiata in una
  cartella temporanea e iniettata con ``--append-system-prompt-file`` (i reference si
  leggono con Read dal percorso assoluto). Tool built-in ridotti a Read e ToolSearch,
  gli altri server MCP vietati. Il messaggio ``system/init`` viene controllato: tool
  BuddaLaw presenti, nessuna skill attiva.
- ``opencode``: ``opencode run --format json`` nella cartella di prova stabile
  ``.opencode-sandbox/`` (vedi prepara_opencode.sh), con BuddaLaw come MCP remoto OAuth
  e la skill copiata in ``.opencode/skills/buddalaw/`` prima di ogni esecuzione.
  Isolamento: ``OPENCODE_DISABLE_EXTERNAL_SKILLS=1`` (niente ~/.claude/skills né
  ~/.agents/skills), ``OPENCODE_DISABLE_CLAUDE_CODE=1`` (niente CLAUDE.md), skill
  diverse da buddalaw negate da ``permission.skill`` e un repository git nella sandbox
  che ferma la risalita a AGENTS.md. Database delle sessioni separato (OPENCODE_DB).

Formato degli eventi ``opencode run --format json`` (osservato con opencode 1.16.0)
-------------------------------------------------------------------------------
Una riga JSON per evento: ``{"type", "timestamp", "sessionID", "part": {...}}``.
- ``step_start``  : inizio di un passo del modello.
- ``tool_use``    : ``part.tool`` (nome, es. ``buddalaw_search_case_law``),
  ``part.state.status`` (``completed``/``error``), ``part.state.input`` (argomenti),
  ``part.state.output`` (risultato testuale) o ``part.state.error``.
- ``text``        : ``part.text`` (testo del modello).
- ``step_finish`` : ``part.reason`` (``tool-calls``/``stop``), ``part.tokens``
  (input, output, reasoning, cache.read/write) e ``part.cost`` in dollari.
- ``error``       : ``error.name``, ``error.data.message``, ``error.data.statusCode``.

Uso
---
    python buddalaw/tests/e2e/run.py --config v9                  # Haiku, tutti i casi, 1 esecuzione
    python buddalaw/tests/e2e/run.py --config v9 --runs 3 --solo-lampo
    python buddalaw/tests/e2e/run.py --config v9,v8.4,nessuna --casi B00,B02
    python buddalaw/tests/e2e/run.py --runtime opencode --config v9
    python buddalaw/tests/e2e/run.py --modello default             # Claude Code col modello predefinito: solo casi ⚡
    python buddalaw/tests/e2e/run.py --prova                        # costruisce i comandi senza eseguirli

Spesa: tetto per modello (--budget, default 5 $). Ogni esecuzione Claude ha anche
``--max-budget-usd``. Stop immediato e definitivo su 403/429/blocco del server
BuddaLaw: nessun ritento.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import glob
import hashlib
import json
import math
import os
import re
import shutil
import signal
import shlex
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent
REPO = QUI.parents[2]
SKILL_DIR = REPO / "buddalaw" / "buddalaw"
CASI = QUI / "casi.json"
RISULTATI = QUI / "results"
SANDBOX = Path(os.environ.get("BUDDALAW_SANDBOX", str(QUI / ".opencode-sandbox"))).resolve()
sys.path.insert(0, str(QUI.parent / "tools"))
from valida_schema import errori_chiamata
TAG_V84 = "buddalaw-v8.4"

PREFISSI = ("mcp__claude_ai_BuddaLaw__", "mcp__buddalaw__", "buddalaw_")
MODELLO_CLAUDE = os.environ.get("BUDDALAW_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
MAX_TURNI_CLAUDE = 16
MODELLI_OPENCODE = ["openrouter/qwen/qwen3.8-flash", "openrouter/deepseek/deepseek-v4.1-flash"]
CONFIG_VALIDE = ("v9", "v8.4", "nessuna", "v9-ridotta")
# server MCP dell'utente da tenere fuori dalle prove con Claude Code
MCP_VIETATI = [
    "mcp__mindnode", "mcp__perplexity", "mcp__cloudflare",
    "mcp__bdm", "mcp__italgiure", "mcp__normattiva", "mcp__claude-in-chrome",
    "mcp__claude_ai_Claude_Docs", "mcp__claude_ai_Corpus_gestiolex", "mcp__claude_ai_Gmail",
    "mcp__claude_ai_Google_Calendar", "mcp__claude_ai_Google_Drive",
]
AVVISO_RE = re.compile(r"⚠️?\s*BuddaLaw è stato aggiornato")
ESTREMI_RE = re.compile(r"\bn\.\s?(\d{1,5})/((?:19|20)\d{2})\b")
VIRGOLETTATO_RE = re.compile(r'«([^»]+)»|“([^”]+)”|"([^"\n]+)"')
LINK_MD_RE = re.compile(r"\[([^\]]+)\]\(<?(https?://[^)\s>]+)>?\)")
URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
# blocco del server: solo su risultati di errore o brevi, per non scambiare un
# «art. 403» in una sentenza per un codice HTTP
BLOCCO_RE = re.compile(
    r"(?i)(\b(http|status(code)?|errore?|error|codice)\b\W{0,3}\D{0,12}\b(403|429|500)\b"
    r"|too many requests|rate.?limit|forbidden|troppe richieste|account (bloccato|sospeso)|quota (esaurita|exceeded)"
    # guasto del server (osservato il 2026-10-17): le prove successive non misurano la skill
    r"|circuit breaker|backend temporaneamente non disponibile|servizio non è momentaneamente disponibile)"
)


class Blocco(Exception):
    """403/429 o blocco del server: ci si ferma, senza ritentare."""


class Salta(Exception):
    """Runtime non utilizzabile (es. autenticazione mancante): si salta e lo si dice."""


class LimiteSpesa(Exception):
    """Interrompe lo step successivo quando la spesa nota raggiunge il tetto."""


def verifica_abbonamento_claude(runtimes: list[str], modello: str | None) -> dict:
    """Modalità esplicita che esclude API e OpenRouter prima di avviare i modelli."""
    if runtimes != ["claude"]:
        raise ValueError("--solo-abbonamento consente soltanto --runtime claude")
    if not modello or not (modello.startswith("claude-") or modello in ("haiku", "sonnet", "opus")):
        raise ValueError("--solo-abbonamento richiede un modello Claude esplicito, non 'default'")
    api_env = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
               "CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_USE_BEDROCK",
               "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY")
    if any(os.environ.get(k) for k in api_env):
        raise ValueError("--solo-abbonamento: presente una variabile API o di un altro provider; nessun modello avviato")
    try:
        out = subprocess.run(["claude", "auth", "status", "--json"],
                             capture_output=True, text=True, check=True, timeout=20)
        auth = json.loads(out.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        raise ValueError("Impossibile verificare l'abbonamento Claude; nessun modello avviato") from None
    if not (isinstance(auth, dict) and auth.get("loggedIn") is True
            and auth.get("authMethod") == "claude.ai" and auth.get("apiProvider") == "firstParty"
            and auth.get("subscriptionType") in ("pro", "max", "team", "enterprise")):
        raise ValueError("Abbonamento Claude non verificato; nessun modello avviato")
    # Non salvare email, identificativi personali o altri dettagli dell'account.
    return {k: auth[k] for k in ("authMethod", "apiProvider", "subscriptionType")}


def verifica_stop_condiviso():
    path = os.environ.get("BUDDALAW_STOP_FILE")
    if path and Path(path).exists():
        raise Blocco("arresto condiviso: collaudo fermato; nessun nuovo tentativo")


def condividi_stop():
    path = os.environ.get("BUDDALAW_STOP_FILE")
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)


# --------------------------------------------------------------------------- utilità

def tipografia(s: str) -> str:
    """Apostrofi e virgolette tipografiche come quelle dritte: il modello non le copia sempre."""
    return s.translate(str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'}))


def norm_tool(nome: str) -> str:
    for p in PREFISSI:
        if nome.startswith(p):
            return nome[len(p):]
    return nome


def e_buddalaw(nome: str) -> bool:
    return any(nome.startswith(p) for p in PREFISSI)


@dataclass
class Esecuzione:
    """Ciò che serve alla valutazione, indipendente dal runtime."""
    chiamate: list = field(default_factory=list)   # [{"tool", "nome_originale", "argomenti"}]
    risultati: list = field(default_factory=list)  # testi dei tool_result
    fonti: list = field(default_factory=list)     # risultati con origine, argomenti e stato
    testi: list = field(default_factory=list)      # testi del modello, in ordine
    testo_finale: str = ""
    costo: float = 0.0
    token: dict = field(default_factory=dict)
    errore: str = ""
    init: dict = field(default_factory=dict)
    durata: float = 0.0

    @property
    def testo_visibile(self) -> str:
        return "\n\n".join(t for t in self.testi if t)


# --------------------------------------------------------------------------- skill

def prepara_skill(config: str, base: Path) -> Path | None:
    """Copia la skill della configurazione in base/buddalaw e ne restituisce il percorso."""
    if config == "nessuna":
        return None
    dest = base / "buddalaw"
    if dest.exists():
        shutil.rmtree(dest)
    if config in ("v9", "v9-ridotta"):
        shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__"))
    elif config == "v8.4":
        dest.mkdir(parents=True)
        arch = subprocess.run(["git", "-C", str(REPO), "archive", TAG_V84, "buddalaw/buddalaw"],
                              capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(dest), "--strip-components", "2"], input=arch, check=True)
    else:
        raise ValueError(config)
    if config == "v9-ridotta":
        sk = dest / "SKILL.md"
        testo = sk.read_text(encoding="utf-8")
        modificati = []
        def riduci(m):
            dati = json.loads(m.group(1))
            if not isinstance(dati, dict) or "inventario_tool_buddalaw" not in dati:
                return m.group(0)
            dati["inventario_tool_buddalaw"].remove("search_similar_cases")
            modificati.append(True)
            return "```json\n" + json.dumps(dati, ensure_ascii=False) + "\n```"
        testo = re.sub(r"```json\s*\n(.*?)\n```", riduci, testo, flags=re.S)
        if len(modificati) != 1:
            raise RuntimeError("v9-ridotta: atteso un solo inventario JSON")
        sk.write_text(testo, encoding="utf-8")
    return dest


def prompt_di_sistema(skill: Path) -> str:
    testo = (skill / "SKILL.md").read_text(encoding="utf-8")
    testo = testo.replace("](references/", f"]({skill}/references/")
    testo = testo.replace("](scripts/", f"]({skill}/scripts/")
    testo = testo.replace("<cartella-skill>", str(skill))
    return (
        "# Skill attiva: buddalaw\n\n"
        f"Le istruzioni che seguono sono la skill `buddalaw`, installata nella cartella {skill}. "
        f"I file references citati si aprono con il tool Read dal percorso assoluto {skill}/references/<nome>.md.\n\n"
        + testo
    )


# --------------------------------------------------------------------------- runtime Claude Code

def comando_claude(prompt: str | None, modello: str | None, budget_run: float, spf: Path | None) -> list[str]:
    """prompt=None: più turni, i messaggi arrivano da stdin (--input-format stream-json)."""
    cmd = ["claude", "-p"] + ([prompt] if prompt is not None else ["--input-format", "stream-json"])
    cmd += ["--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--max-turns", str(MAX_TURNI_CLAUDE), "--max-budget-usd", f"{budget_run:.2f}",
           "--disable-slash-commands", "--tools", "Read,ToolSearch",
           "--allowedTools", "mcp__claude_ai_BuddaLaw__*,Read,ToolSearch",
           "--disallowedTools", ",".join(MCP_VIETATI)]
    if modello:
        cmd += ["--model", modello]
    if spf:
        cmd += ["--append-system-prompt-file", str(spf)]
        helper = spf.parent / "buddalaw" / "scripts" / "verifica_catalogo.py"
        if helper.is_file():
            cmd[cmd.index("--tools") + 1] = "Read,ToolSearch,Bash"
            i = cmd.index("--allowedTools") + 1
            cmd[i] += f",Bash(python3 {helper} *)"
            cmd[i] += f',Bash(python3 "{helper}" *)'
    return cmd


def testo_risultato(contenuto) -> str:
    if isinstance(contenuto, str):
        return contenuto
    if isinstance(contenuto, list):
        return "\n".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in contenuto)
    return json.dumps(contenuto, ensure_ascii=False)


def parsifica_claude(righe: list[str], rileva_blocchi: bool = True) -> Esecuzione:
    ex = Esecuzione()
    turn = 1
    tool_ids = {}
    tools_scoperti = set()
    accesso_provato = False
    for riga in righe:
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        tipo = ev.get("type")
        if tipo == "system" and ev.get("subtype") == "init":
            ex.init = {k: ev.get(k) for k in ("tools", "mcp_servers", "skills", "slash_commands", "model", "cwd")}
        elif tipo == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if b.get("type") == "text":
                    ex.testi.append(b.get("text", ""))
                elif b.get("type") == "tool_use":
                    call = {"tool": norm_tool(b.get("name", "")), "nome_originale": b.get("name", ""),
                            "argomenti": b.get("input") or {}, "id": b.get("id"), "turno": turn}
                    ex.chiamate.append(call)
                    tool_ids[b.get("id")] = call
        elif tipo == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    t = testo_risultato(b.get("content"))
                    ex.risultati.append(t)
                    call = tool_ids.get(b.get("tool_use_id"), {})
                    if (call.get("tool") == "check_access" and e_buddalaw(call.get("nome_originale", ""))
                            and not b.get("is_error")):
                        try:
                            accesso = json.loads(t)
                            accesso_provato |= isinstance(accesso, dict) and accesso.get("has_access") is True
                        except ValueError:
                            pass
                    if (call.get("tool") == "ToolSearch" and not b.get("is_error")
                            and isinstance(b.get("content"), list)):
                        tools_scoperti.update(c["tool_name"] for c in b["content"]
                                              if isinstance(c, dict) and c.get("type") == "tool_reference"
                                              and isinstance(c.get("tool_name"), str))
                    ex.fonti.append({"tool": call.get("tool", "sconosciuto"), "output": t,
                                     "argomenti": call.get("argomenti", {}), "is_error": bool(b.get("is_error"))})
                    if rileva_blocchi and e_buddalaw(call.get("nome_originale", "")):
                        controlla_blocco(t, bool(b.get("is_error")))
        elif tipo == "result":
            ex.testo_finale = ev.get("result") or ""
            # con più turni c'è un result per turno e total_cost_usd è cumulativo (osservato)
            ex.costo = max(ex.costo, float(ev.get("total_cost_usd") or 0))
            ex.token = ev.get("usage") or {}
            if ev.get("subtype") not in (None, "success"):
                ex.errore = str(ev.get("subtype"))
            elif ev.get("is_error"):
                ex.errore = ex.testo_finale[:200]
            turn += 1
    if not ex.testo_finale and ex.testi:
        ex.testo_finale = ex.testi[-1]
    if ex.init and tools_scoperti:
        ex.init["tools_scoperti"] = sorted(tools_scoperti)
    if ex.init and accesso_provato:
        ex.init["buddalaw_accesso_provato"] = True
    return ex


def verifica_init_claude(init: dict, config: str) -> list[str]:
    problemi = []
    tools = list(init.get("tools") or []) + list(init.get("tools_scoperti") or [])
    if not any(t.startswith("mcp__claude_ai_BuddaLaw__") for t in tools) and not init.get("buddalaw_accesso_provato"):
        stato = [s for s in init.get("mcp_servers") or [] if "BuddaLaw" in str(s.get("name"))]
        # «pending»: il connettore si sta ancora collegando (osservato in B00 v8.4, 2026-10-17);
        # non è un difetto di isolamento, e se poi i tool servono lo dicono gli altri controlli
        if not any(s.get("status") == "pending" for s in stato):
            problemi.append(f"tool BuddaLaw assenti in claude -p (connettore claude.ai: {stato or 'non elencato'})")
    if init.get("skills"):
        problemi.append(f"skill attive nonostante --disable-slash-commands: {init['skills']}")
    if any("buddalaw" in str(c).lower() for c in init.get("slash_commands") or []):
        problemi.append("comando/skill buddalaw installato visibile")
    estranei = [t for t in tools if t.startswith("mcp__") and not t.startswith("mcp__claude_ai_BuddaLaw__")]
    if estranei:
        problemi.append(f"tool MCP estranei visibili: {estranei[:5]}")
    return problemi


def esegui_claude(turni: list[str], config: str, modello: str | None, budget_run: float, cartella: Path) -> tuple[Esecuzione, list[str]]:
    lavoro = Path(tempfile.mkdtemp(prefix="buddalaw-e2e-"))
    t0 = time.time()
    skill = prepara_skill(config, lavoro)
    meta = {"runtime":"claude", "config":config, "modello_richiesto":modello,
            "completata":False, "turni_previsti":len(turni),
            "skill_sha256":hashlib.sha256((skill/"SKILL.md").read_bytes()).hexdigest() if skill else None}
    meta_path = cartella.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    try:
        spf = None
        if skill:
            spf = lavoro / "skill-prompt.md"
            spf.write_text(prompt_di_sistema(skill), encoding="utf-8")
        cmd = comando_claude(turni[0] if len(turni) == 1 else None, modello, budget_run, spf)
        env = dict(os.environ, CLAUDE_CODE_DISABLE_AUTO_MEMORY="1", ENABLE_TOOL_SEARCH="true")
        error = ""
        try:
            code = _processo_su_file(cmd, lavoro, env, cartella, 900 if len(turni)>1 else 600,
                                    callback=controllore_live(), turni=turni if len(turni)>1 else None)
        except subprocess.TimeoutExpired:
            code, error = -1, "timeout; costo parziale noto conservato"
        except Blocco as exc:
            exc.esecuzione = parsifica_claude(cartella.read_text().splitlines() if cartella.exists() else [],rileva_blocchi=False)
            exc.esecuzione.errore = str(exc)
            meta["errore"] = str(exc)
            meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
            raise
        ex = parsifica_claude(cartella.read_text().splitlines())
        ex.durata = time.time()-t0
        if error:
            ex.errore = error
        elif not ex.testi:
            ex.errore = f"nessun testo del modello (exit {code})"
        problems = verifica_init_claude(ex.init,config) if ex.init else ["system/init assente"]
        meta.update({"completata":not bool(ex.errore),"errore":ex.errore,
                     "problemi_isolamento":problems,"modello_effettivo":ex.init.get("model"),"costo_usd_noto":ex.costo})
        meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
        return ex, problems
    finally:
        shutil.rmtree(lavoro,ignore_errors=True)


# --------------------------------------------------------------------------- runtime opencode

def trova_opencode() -> str | None:
    if os.environ.get("OPENCODE_BIN"):
        return os.environ["OPENCODE_BIN"]
    p = shutil.which("opencode")
    if p:
        return p
    cand = sorted(glob.glob("/usr/local/Cellar/opencode/*/bin/opencode") + glob.glob("/opt/homebrew/Cellar/opencode/*/bin/opencode")
                  + glob.glob(os.path.expanduser("~/.opencode/bin/opencode")))
    return cand[-1] if cand else None


def env_opencode() -> dict:
    return dict(os.environ,
                XDG_CONFIG_HOME=str(SANDBOX / ".isolated-config"),
                OPENCODE_DB=str(SANDBOX / ".opencode-test.db"),
                OPENCODE_DISABLE_EXTERNAL_SKILLS="1",
                OPENCODE_DISABLE_CLAUDE_CODE="1",
                OPENCODE_DISABLE_AUTOUPDATE="1",
                OPENCODE_DISABLE_SHARE="1",
                NO_COLOR="1")


def _pulisci(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def preflight_opencode(oc: str) -> None:
    """Controlla sandbox, autenticazioni (senza leggere file di credenziali) e isolamento."""
    verifica_stop_condiviso()
    if not (SANDBOX / "opencode.json").exists():
        raise Salta(f"cartella di prova assente: esegui bash {QUI / 'prepara_opencode.sh'}")
    env = env_opencode()
    resolved = subprocess.run([oc, "debug", "config"], cwd=SANDBOX, capture_output=True,
                              text=True, env=env, timeout=60)
    if resolved.returncode:
        raise Salta("impossibile verificare la configurazione risolta di opencode")
    try:
        mcp_config = json.loads(resolved.stdout).get("mcp", {})
    except (ValueError, AttributeError):
        raise Salta("configurazione risolta di opencode non leggibile")
    estranei = [name for name, cfg in mcp_config.items()
                if name != "buddalaw" and cfg.get("enabled", True)]
    if estranei:
        raise Salta(f"server MCP estranei abilitati: {', '.join(estranei)}; rilancia prepara_opencode.sh")
    auth = _pulisci(subprocess.run([oc, "auth", "list"], cwd=SANDBOX, capture_output=True, text=True, env=env, timeout=60).stdout)
    if "openrouter" not in auth.lower():
        raise Salta("OpenRouter non autenticato in opencode: esegui `opencode auth login` e scegli OpenRouter")
    try:
        mcp = _pulisci(subprocess.run([oc, "mcp", "list"], cwd=SANDBOX, capture_output=True, text=True, env=env, timeout=120).stdout)
    except subprocess.TimeoutExpired as exc:
        raise Blocco("collegamento BuddaLaw non verificabile: timeout del controllo MCP") from exc
    riga = next((r for r in mcp.splitlines() if "buddalaw" in r.lower()), "")
    if not riga:
        raise Salta("server MCP buddalaw non configurato nella sandbox: rilancia prepara_opencode.sh")
    if "needs authentication" in riga or "needs_auth" in riga:
        raise Salta(f"BuddaLaw non autenticato in opencode ({riga.strip(' │●')}): "
                    f"cd \"{SANDBOX}\" && OPENCODE_DB=\"{SANDBOX / '.opencode-test.db'}\" {oc} mcp auth buddalaw")
    if "✗" in riga or "failed" in riga.lower() or "connected" not in riga.lower():
        lines = mcp.splitlines()
        pos = lines.index(riga)
        dettaglio = " ".join(lines[pos:pos + 3]).strip()
        controlla_blocco(dettaglio, True)
        raise Blocco(f"collegamento BuddaLaw non riuscito: {dettaglio}")


def verifica_skill_opencode(oc: str, config: str) -> list[str]:
    out = _stdout_su_file([oc, "debug", "skill"], timeout=120)
    problemi = []
    try:
        skills = json.loads(out[out.index("["):]) if "[" in out else []
    except (ValueError, json.JSONDecodeError):
        return ["impossibile leggere `opencode debug skill`"]
    luoghi = {s.get("name"): str(s.get("location")) for s in skills if isinstance(s, dict)}
    for nome, luogo in luoghi.items():
        if "/.claude/" in luogo or "/.agents/" in luogo:
            problemi.append(f"skill esterna caricata: {nome} da {luogo}")
    if config == "nessuna":
        # La copia globale può essere scoperta, ma deve essere nascosta dal modello.
        cfg = json.loads((SANDBOX / "opencode.json").read_text())
        perm = cfg.get("agent",{}).get("build",{}).get("permission",{}).get("skill",{})
        if perm != {"*":"deny"}:
            problemi.append("config nessuna senza divieto di caricamento delle skill")
    elif Path(luoghi.get("buddalaw", "")).resolve() != (SANDBOX / ".opencode/skills/buddalaw/SKILL.md").resolve():
        problemi.append(f"skill buddalaw non caricata dalla sandbox: {luoghi.get('buddalaw')}")
    return problemi


def controllore_live(budget=None):
    """Controlla la quota nativa del provider e i risultati MCP BuddaLaw."""
    budda_ids = set()
    costo = 0.0
    def controlla(ev):
        nonlocal costo
        tipo = ev.get("type")
        if tipo == "rate_limit_event":
            info = ev.get("rate_limit_info") or ev.get("rateLimitInfo") or {}
            if info.get("status") == "rejected":
                raise Blocco("limite di utilizzo Claude raggiunto; nessun ritento o cambio di provider")
        if tipo == "step_finish":
            costo += float((ev.get("part") or {}).get("cost") or 0)
            if budget is not None and costo >= budget:
                raise LimiteSpesa(f"tetto di spesa raggiunto: costo noto {costo:.5f} $")
        if tipo in ("tool_use", "error"):
            parsifica_opencode([json.dumps(ev)])
        elif tipo == "assistant":
            for b in (ev.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use" and e_buddalaw(b.get("name", "")):
                    budda_ids.add(b.get("id"))
        elif tipo == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_result" and b.get("tool_use_id") in budda_ids:
                    controlla_blocco(testo_risultato(b.get("content")), bool(b.get("is_error")))
        elif tipo == "result" and ev.get("is_error"):
            controlla_blocco(str(ev.get("result", "")), True)
    return controlla


def ferma_processo(proc):
    if proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=2)


def controlla_avvio_mcp(linea):
    """OpenCode può proseguire col modello dopo un MCP fallito all'avvio."""
    try:
        campi = dict(p.split("=",1) for p in shlex.split(linea) if "=" in p)
    except ValueError:
        return
    if campi.get("key") == "buddalaw" and campi.get("status") == "failed":
        raise Blocco("collegamento MCP BuddaLaw fallito all'avvio; prova non valutabile")


def _processo_su_file(cmd, cwd, env, dest, timeout, callback=None, turni=None, callback_stderr=None):
    """NDJSON su file, controllo mentre arriva, timeout anche con stdout muto."""
    verifica_stop_condiviso()
    err = dest.with_suffix(".stderr.txt")
    t0 = time.monotonic()
    with dest.open("w") as fo, err.open("w") as fe:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=fo, stderr=fe,
                                stdin=subprocess.PIPE if turni else subprocess.DEVNULL,
                                text=True, start_new_session=True)
        pending = list(turni or [])
        def invia():
            if pending and proc.poll() is None:
                prompt = pending.pop(0)
                proc.stdin.write(json.dumps({"type":"user","message":{"role":"user","content":prompt}},ensure_ascii=False)+"\n")
                proc.stdin.flush()
        if pending:
            invia()
        buffer = ""
        try:
            with dest.open() as reader, err.open() as err_reader:
                err_buffer = ""
                while True:
                    verifica_stop_condiviso()
                    err_buffer += err_reader.read()
                    while "\n" in err_buffer:
                        err_line, err_buffer = err_buffer.split("\n",1)
                        if callback_stderr:
                            callback_stderr(err_line)
                    buffer += reader.read()
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        try:
                            ev = json.loads(line)
                        except ValueError:
                            continue
                        if callback:
                            callback(ev)
                        if turni and ev.get("type") == "result":
                            if pending and ev.get("subtype") in (None, "success"):
                                invia()
                            elif proc.stdin and not proc.stdin.closed:
                                proc.stdin.close()
                    if proc.poll() is not None:
                        # Un ultimo giro per leggere i byte scritti prima dell'uscita.
                        last = reader.read()
                        if last:
                            buffer += last
                            continue
                        if buffer.strip() and callback:
                            try:
                                ev = json.loads(buffer)
                            except ValueError:
                                ev = None
                            if isinstance(ev, dict):
                                callback(ev)
                        if err_buffer.strip() and callback_stderr:
                            callback_stderr(err_buffer)
                        return proc.returncode
                    if time.monotonic() - t0 >= timeout:
                        raise subprocess.TimeoutExpired(cmd, timeout)
                    time.sleep(0.03)
        except Blocco:
            condividi_stop()
            raise
        finally:
            ferma_processo(proc)
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()


def _stdout_su_file(cmd: list[str], timeout: int, salva: Path | None = None, controlla: bool = False, budget=None) -> str:
    """opencode (bun) tronca lo stdout su pipe a 64 KB quando esce: si scrive su file."""
    if salva:
        dest = salva
    else:
        fd, nome = tempfile.mkstemp(prefix="opencode-", suffix=".out")
        os.close(fd)
        dest = Path(nome)
    err = dest.with_suffix(".stderr.txt")
    try:
        codice = _processo_su_file(cmd, SANDBOX, env_opencode(), dest, timeout,
                                  controllore_live(budget) if controlla else None,
                                  callback_stderr=controlla_avvio_mcp if controlla else None)
    except subprocess.TimeoutExpired as exc:
        exc.output = dest.read_text(encoding="utf-8")
        raise
    testo = dest.read_text(encoding="utf-8")
    if not salva:
        dest.unlink(missing_ok=True)
    if not err.read_text(encoding="utf-8").strip() or not salva:
        err.unlink(missing_ok=True)
    if codice and not testo.strip():
        raise Salta(f"comando terminato con codice {codice}, senza output; vedi {err.name}")
    return testo


def parsifica_opencode(righe: list[str], rileva_blocchi: bool = True) -> Esecuzione:
    ex = Esecuzione()
    passo: list[str] = []
    ultimi: list[str] = []
    tok = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0}
    turn = 1
    for riga in righe:
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        tipo, part = ev.get("type"), ev.get("part") or {}
        if tipo == "benchmark/turn_start":
            turn = ev["turn"]
        elif tipo == "step_start":
            passo = []
        elif tipo == "text":
            ex.testi.append(part.get("text", ""))
            passo.append(part.get("text", ""))
        elif tipo == "tool_use":
            st = part.get("state") or {}
            nome = part.get("tool", "")
            ex.chiamate.append({"tool": norm_tool(nome), "nome_originale": nome,
                                "argomenti": st.get("input") or {}, "id": part.get("callID"), "turno": turn})
            out = st.get("output") if st.get("status") == "completed" else (st.get("error") or "")
            t = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
            ex.risultati.append(t)
            ex.fonti.append({"tool": norm_tool(nome), "output": t, "argomenti": st.get("input") or {},
                             "is_error": st.get("status") == "error", "metadata": st.get("metadata") or {}})
            if rileva_blocchi and e_buddalaw(nome):
                controlla_blocco(t, st.get("status") == "error")
        elif tipo == "step_finish":
            ex.costo += float(part.get("cost") or 0)
            tk = part.get("tokens") or {}
            for k in ("input", "output", "reasoning"):
                tok[k] += int(tk.get(k) or 0)
            tok["cache_read"] += int((tk.get("cache") or {}).get("read") or 0)
            if passo:
                ultimi = passo
        elif tipo == "error":
            dati = (ev.get("error") or {}).get("data") or {}
            ex.errore = f"{(ev.get('error') or {}).get('name')}: {dati.get('message')} ({dati.get('statusCode')})"
            if rileva_blocchi and dati.get("statusCode") in (403, 429, 500):
                raise Blocco(f"opencode/provider: {ex.errore}")
    ex.token = tok
    ex.testo_finale = "\n\n".join(ultimi or passo)
    return ex


def esegui_opencode(oc: str, turni: list[str], config: str, modello: str, cartella: Path, budget_run=None) -> tuple[Esecuzione, list[str]]:
    skills = SANDBOX / ".opencode" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    prepara_skill(config, skills)  # crea o sostituisce .opencode/skills/buddalaw
    if config == "nessuna" and (skills / "buddalaw").exists():
        shutil.rmtree(skills / "buddalaw")
    config_path = SANDBOX / "opencode.json"
    resolved = json.loads(config_path.read_text())
    skill_permission = {"*":"deny"} if config == "nessuna" else {"*":"deny","buddalaw":"allow"}
    resolved.setdefault("permission", {})["skill"] = skill_permission
    resolved.setdefault("agent", {}).setdefault("build", {}).setdefault("permission", {})["skill"] = skill_permission
    # OpenCode genera anche il titolo con un modello ausiliario: non ereditare
    # un modello diverso da quello richiesto per questa prova.
    resolved["small_model"] = modello
    config_path.write_text(json.dumps(resolved, ensure_ascii=False, indent=2) + "\n")
    problemi = verifica_skill_opencode(oc, config)
    meta_path = cartella.with_suffix(".meta.json")
    meta = {"runtime":"opencode", "config":config, "modello_richiesto":modello,
            "problemi_isolamento":problemi, "completata":False, "turni_previsti":len(turni),
            "skill_sha256":hashlib.sha256((skills/"buddalaw/SKILL.md").read_bytes()).hexdigest() if config != "nessuna" else None,
            "config_sha256":hashlib.sha256(config_path.read_bytes()).hexdigest()}
    meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    if problemi:
        return Esecuzione(errore="isolamento della skill non verificato"), problemi
    t0 = time.time()
    stdout, sessione, execution_error = "", None, ""
    for i, prompt in enumerate(turni):
        cmd = [oc, "--print-logs", "--log-level", "WARN", "run", "--format", "json", "--dir", str(SANDBOX), "-m", modello]
        if sessione:
            cmd += ["--session", sessione]  # turni successivi nella stessa sessione
        file_turno = cartella.with_suffix(f".t{i + 1}.jsonl")
        try:
            residuo = budget_run-parsifica_opencode(stdout.splitlines()).costo if budget_run is not None else None
            parziale = _stdout_su_file(cmd + [prompt], timeout=600, salva=file_turno, controlla=True, budget=residuo)
        except LimiteSpesa as exc:
            parziale = file_turno.read_text() if file_turno.exists() else ""
            execution_error = str(exc)
        except subprocess.TimeoutExpired as exc:
            parziale = exc.output or ""
            execution_error = "timeout 600 s; costo parziale noto conservato"
        except Blocco as exc:
            parziale = file_turno.read_text() if file_turno.exists() else ""
            stdout += json.dumps({"type":"benchmark/turn_start","turn":i+1})+"\n"+parziale
            cartella.write_text(stdout)
            exc.esecuzione = parsifica_opencode(stdout.splitlines(), rileva_blocchi=False)
            exc.esecuzione.errore = str(exc)
            meta["errore"] = str(exc)
            meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
            raise
        stdout += json.dumps({"type":"benchmark/turn_start","turn":i+1})+"\n"+parziale
        cartella.write_text(stdout, encoding="utf-8")
        if execution_error:
            break
        # Controllare il turno prima di inviare il successivo.
        parsed_turn = parsifica_opencode(parziale.splitlines())
        if parsed_turn.errore:
            execution_error = parsed_turn.errore
            break
        if sessione is None:
            m = re.search(r'"sessionID"\s*:\s*"([^"]+)"', parziale)
            sessione = m.group(1) if m else None
            if len(turni) > 1 and not sessione:
                break
    ex = parsifica_opencode(stdout.splitlines())
    ex.durata = time.time() - t0
    ex.init = {"skill_check": problemi}
    if not stdout.strip():
        ex.errore = f"nessun output: vedi {cartella.with_suffix('.stderr.txt').name}"
    if execution_error:
        ex.errore = execution_error
    nomi = {c["nome_originale"] for c in ex.chiamate}
    if any("non disponibil" in t.lower() and "tool" in t.lower() for t in ex.testi) and not any(e_buddalaw(n) for n in nomi):
        problemi.append("dichiara i tool non disponibili senza averli chiamati (prefisso buddalaw_?)")
    meta.update({"completata":not bool(ex.errore),"errore":ex.errore,"costo_usd_noto":ex.costo})
    if sessione:
        try:
            with sqlite3.connect(f"file:{SANDBOX / '.opencode-test.db'}?mode=ro",uri=True) as db:
                # Soltanto identificativi del modello, mai contenuti di ragionamento o credenziali.
                rows = db.execute("select distinct json_extract(data,'$.providerID'), json_extract(data,'$.modelID') from message where session_id=? and json_extract(data,'$.role')='assistant'",(sessione,)).fetchall()
                meta["modelli_effettivi"] = [f"{provider}/{model}" for provider,model in rows if provider and model]
        except sqlite3.Error:
            meta["modelli_effettivi"] = None
    meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    return ex, problemi


def controlla_blocco(testo: str, errore: bool) -> None:
    messaggio = testo
    strutturato = False
    try:
        dati = json.loads(testo)
        if isinstance(dati, dict):
            campi = [dati[k] for k in ("error", "detail", "message", "status", "statusCode") if k in dati]
            if "error" in dati or "detail" in dati or dati.get("statusCode") in (403, 429, 500):
                strutturato = True
                messaggio = json.dumps(campi, ensure_ascii=False)
    except (ValueError, TypeError):
        pass
    if (errore or strutturato or len(testo) < 3000) and BLOCCO_RE.search(messaggio):
        raise Blocco(f"risposta del server: {testo[:300]}")


# --------------------------------------------------------------------------- valutazione

def _vincolo(valore, atteso) -> bool:
    if isinstance(atteso, dict):
        if atteso.get("assente"):
            return valore in (None, "")
        if atteso.get("presente"):
            if valore in (None, ""):
                return False
        if "regex" in atteso and (valore is None or not re.search(atteso["regex"], str(valore))):
            return False
        if "tipo" in atteso:
            tipi = {"int": int, "str": str}
            if not isinstance(valore, tipi[atteso["tipo"]]) or isinstance(valore, bool):
                return False
        if "in" in atteso and not any(_uguale(valore, x) for x in atteso["in"]):
            return False
        if "non" in atteso and _uguale(valore, atteso["non"]):
            return False
        return True
    return _uguale(valore, atteso)


def _uguale(a, b) -> bool:
    if isinstance(a, str) and isinstance(b, str):
        return a.strip().lower() == b.strip().lower()
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    return a == b


def _soddisfa(chiamata: dict, voce: dict) -> bool:
    if chiamata["tool"] != voce["tool"]:
        return False
    args = chiamata.get("argomenti") or {}
    return all(_vincolo(args.get(k), v) for k, v in (voce.get("argomenti") or {}).items())


def _voce_ok(chiamate: list, voce: dict) -> bool:
    if "uno_di" in voce:
        return any(_voce_ok(chiamate, v) for v in voce["uno_di"])
    return any(_soddisfa(c, voce) for c in chiamate)


def _descr(voce: dict) -> str:
    if "uno_di" in voce:
        return " oppure ".join(_descr(v) for v in voce["uno_di"])
    return f"{voce['tool']}({json.dumps(voce.get('argomenti') or {}, ensure_ascii=False)})"


def _stringhe(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _stringhe(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _stringhe(v)


def fonti_probatorie(ex: Esecuzione) -> list[dict]:
    fonti = [f for f in ex.fonti if f.get("tool") in {
        "get_judgement", "get_law_article", "search_case_law", "search_similar_cases", "search_articles",
        "get_contract", "get_contract_requirements", "get_processual_act",
        "search_contracts", "search_processual_acts", "list_contracts", "list_processual_acts"}
        and not f.get("is_error")]
    # Un Read è una fonte solo quando legge un file esplicitamente restituito da BuddaLaw.
    percorsi = set()
    for fonte in fonti:
        for path in re.findall(r"Full output saved to:[ \t]*(/[^\r\n]+)", fonte.get("output", "")):
            if "/tool-results/" in path or "/tool-output/" in path:
                percorsi.add(path.strip())
        for value in _stringhe(fonte.get("metadata", {})):
            if value.startswith("/") and "/tool-output/" in value:
                percorsi.add(value)
    for f in ex.fonti:
        path = (f.get("argomenti") or {}).get("filePath") or (f.get("argomenti") or {}).get("file_path")
        if f.get("tool", "").lower() == "read" and not f.get("is_error") and path in percorsi:
            fonte = dict(f)
            # Read di Claude numera le righe: il prefisso non appartiene al JSON.
            fonte["output"] = re.sub(r"(?m)^\s*\d+\t", "", f.get("output", ""))
            fonti.append(fonte)
    return fonti


def oggetti_fonte(ex: Esecuzione):
    def visita(obj):
        if isinstance(obj, str):
            try:
                dati = json.loads(obj)
            except ValueError:
                return
            if dati != obj:
                yield from visita(dati)
        elif isinstance(obj, dict):
            yield obj
            for valore in obj.values():
                yield from visita(valore)
        elif isinstance(obj, list):
            for valore in obj:
                yield from visita(valore)
    for f in fonti_probatorie(ex):
        yield from visita(f["output"])


def corpus_risultati(ex: Esecuzione) -> str:
    """Testo dei tool_result, grezzo e con le stringhe JSON decodificate (\\n, \\", \\u00e8...)."""
    parti = []
    for f in fonti_probatorie(ex):
        r = f["output"]
        parti.append(r)
        try:
            parti.extend(_stringhe(json.loads(r)))
        except (json.JSONDecodeError, TypeError):
            pass
    grezzo = "\n".join(parti)
    return grezzo + "\n" + grezzo.replace("\\/", "/").replace("\\u0026", "&")


def corpus_testi(ex: Esecuzione) -> str:
    """Soltanto campi testuali della fonte, mai sintesi automatiche o skill."""
    parti = []
    for obj in oggetti_fonte(ex):
        for k in ("testo", "text"):
            valore = obj.get(k)
            if not isinstance(valore, str):
                continue
            try:
                contenuto = json.loads(valore)
            except (ValueError, TypeError):
                contenuto = None
            if not isinstance(contenuto, (dict, list)):
                parti.append(valore)
    return "\n".join(parti)


def url_nel_testo(testo: str, tutti: bool = False) -> list[str]:
    out = []
    citazioni = {u for label, u in LINK_MD_RE.findall(testo)
                 if re.search(r"(?i)\b(?:Cass\.?|CGT|Corte|Trib\.?|Tribunale|App\.?|TAR|CGUE|Garante|Agenzia|art\.)", label)
                 or ESTREMI_RE.search(label)}
    for u in URL_RE.findall(testo):
        u = u.rstrip(".,;:!?*_>")
        parsed = urllib.parse.urlsplit(u)
        # Controllare solo domini noti lasciava passare URL inventati su altri
        # host. Un riferimento al repository o a una pagina iniziale di
        # navigazione non è una citazione, salvo che l'etichetta lo presenti così.
        repo = (parsed.hostname == "github.com" and
                (parsed.path == "/avvocati-e-mac/skill-legali" or
                 parsed.path.startswith("/avvocati-e-mac/skill-legali/")))
        homepage = (bool(parsed.hostname) and parsed.path in ("", "/")
                    and not parsed.query and not parsed.fragment and not parsed.username and not parsed.password)
        if tutti or not (repo or homepage) or u in citazioni:
            out.append(u)
    return out


def controlli_specifici(caso: dict, ex: Esecuzione) -> list[tuple[str, bool, str]]:
    esiti = []
    bl = [c for c in ex.chiamate if e_buddalaw(c["nome_originale"])]
    for voce in caso.get("deve_chiamare") or []:
        esiti.append((f"chiama {_descr(voce)}", _voce_ok(bl, voce), ""))
    for voce in caso.get("non_deve_chiamare") or []:
        trovate = [c for c in bl if _soddisfa(c, voce)]
        esiti.append((f"non chiama {_descr(voce)}", not trovate,
                      json.dumps(trovate[0]["argomenti"], ensure_ascii=False)[:200] if trovate else ""))
    utili = [c for c in bl if c["tool"] != "check_access"]
    if "max_chiamate" in caso:
        esiti.append((f"chiamate BuddaLaw ≤ {caso['max_chiamate']}", len(utili) <= caso["max_chiamate"], f"{len(utili)}"))
    if "max_ricerche" in caso:
        n = sum(1 for c in utili if c["tool"].startswith("search_"))
        esiti.append((f"ricerche ≤ {caso['max_ricerche']}", n <= caso["max_ricerche"], f"{n}"))
    for tool, tetto in (caso.get("max_per_tool") or {}).items():
        n = sum(1 for c in utili if c["tool"] == tool)
        esiti.append((f"{tool} ≤ {tetto}", n <= tetto, f"{n}"))
    for prima, dopo in caso.get("prima_di") or []:
        ip = next((i for i, c in enumerate(bl) if c["tool"] == prima), None)
        idd = next((i for i, c in enumerate(bl) if c["tool"] == dopo), None)
        esiti.append((f"{prima} prima di {dopo}", ip is not None and (idd is None or ip < idd), f"{ip} / {idd}"))
    if "max_check_access" in caso:
        n = sum(1 for c in bl if c["tool"] == "check_access")
        esiti.append((f"check_access ≤ {caso['max_check_access']} in tutta la conversazione", n <= caso["max_check_access"], f"{n}"))
    testo = ex.testo_visibile
    corpus = None
    if caso.get("estremi_da_tool"):
        orfani = []
        for num, anno in ESTREMI_RE.findall(testo):
            n = num.lstrip("0")
            associati = any(str(o.get("numero", "")).lstrip("0") == n and str(o.get("anno", "")) == anno
                            for o in oggetti_fonte(ex))
            mesi = "gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre"
            giorno_mese = rf"(?:\d{{1,2}}[/.-]\d{{1,2}}[/.-]|\d{{1,2}}[°º]?\s+(?:{mesi})\s+)"
            citato = re.search(rf"(?<!\d)0*{n}\s*(?:/|del\s+(?:{giorno_mese})?)\s*{anno}(?!\d)",
                               corpus_testi(ex), re.I)
            if not (associati or citato):
                orfani.append(f"{num}/{anno}")
        esiti.append(("estremi citati presenti nei tool_result (niente memoria)", not orfani, ", ".join(orfani[:4])))
    if caso.get("virgolettati_fedeli"):
        piatto = re.sub(r"\s+", " ", tipografia(corpus_testi(ex))).lower()
        falsi = []
        citazioni = []
        for m in VIRGOLETTATO_RE.finditer(testo):
            v = next(g for g in m.groups() if g is not None)
            if len(v) < 25:
                continue
            citazioni.append(v)
            # i tagli «[…]» o «...» separano frammenti: ognuno deve essere letterale
            for pezzo in re.split(r"\[?(?:…|\.\.\.)\]?", v):
                pezzo = re.sub(r"\s+", " ", tipografia(pezzo)).strip(" .,;:").lower()
                if len(pezzo) >= 25 and pezzo not in piatto:
                    falsi.append(pezzo)
        if caso.get("richiede_virgolettato", True):
            esiti.append(("virgolettato richiesto presente", bool(citazioni), ""))
        esiti.append(("virgolettati letterali dai tool_result", not falsi, " | ".join(f[:60] for f in falsi[:2])))
    for rx in caso.get("deve_contenere") or []:
        esiti.append((f"testo contiene /{rx}/", bool(re.search(rx, testo, re.I)), ""))
    for rx in caso.get("non_deve_contenere") or []:
        m = re.search(rx, testo, re.I)
        esiti.append((f"testo non contiene /{rx}/", not m, m.group(0)[:120] if m else ""))
    if "avviso" in caso:
        n = len(AVVISO_RE.findall(testo))
        esiti.append((f"avviso di aggiornamento = {caso['avviso']}", n == caso["avviso"], f"{n}"))
    return esiti


def controlli_generali(ex: Esecuzione) -> list[tuple[str, bool, str]]:
    esiti = []
    corpus = corpus_risultati(ex)
    noti = set(url_nel_testo(corpus, tutti=True))
    url_risposta = url_nel_testo(ex.testo_visibile)
    inventati = [u for u in url_risposta
                 if u not in noti]
    esiti.append(("fedeltà link (URL identici ai tool_result)", not inventati, " ".join(inventati[:3])))
    generici = [t for t, u in LINK_MD_RE.findall(ex.testo_visibile)
                if u in url_risposta and not re.search(r"\d", t)]
    esiti.append(("link sugli estremi (non su «qui», «link»…)", not generici, " | ".join(generici[:3])))
    md_spans = [m.span() for m in LINK_MD_RE.finditer(ex.testo_visibile)]
    fonti_url = set(url_risposta)
    non_cliccabili = [m.group(0) for m in URL_RE.finditer(ex.testo_visibile)
                     if m.group(0).rstrip(".,;:!?*_>") in fonti_url
                     and not any(a <= m.start() < b for a, b in md_spans)]
    esiti.append(("citazioni con link Markdown completo", not non_cliccabili, " ".join(non_cliccabili[:3])))
    esiti.append(("nessun box finale di avvertenze", not box_finale(ex.testo_finale), box_finale(ex.testo_finale)[:120]))
    # gli URL non contano (il «.it» di normattiva.it era letto come la parola inglese «it»)
    # e una risposta di meno di 3 parole riconoscibili (es. un solo link) non si giudica
    it, en = conta_lingua(URL_RE.sub(" ", ex.testo_finale))
    esiti.append(("risposta in italiano",
                  True if (it + en) < 3 else (it >= max(3, en * 1.5) if (it + en) >= 8 else it >= en),
                  f"it={it} en={en}"))
    n_ca = sum(1 for c in ex.chiamate if c["tool"] == "check_access" and e_buddalaw(c["nome_originale"]))
    esiti.append(("check_access al massimo una volta", n_ca <= 1, f"{n_ca}"))
    esiti.append(("risposta presente, senza errore di esecuzione", bool(ex.testo_finale.strip()) and not ex.errore, ex.errore[:120]))
    schema_errors = [e for c in ex.chiamate if e_buddalaw(c["nome_originale"])
                     for e in errori_chiamata(c["tool"], c.get("argomenti") or {})]
    esiti.append(("chiamate conformi allo schema reale", not schema_errors, "; ".join(schema_errors[:4])))
    return esiti


_BOX = re.compile(
    # «il tool non ha segnalato avvertenze», «senza avvertenze del server»: parla del campo
    # warning di get_law_article, non è un riquadro di avvertenze (B07, 2026-10-17)
    r"(?i)((?<!segnalato )(?<!senza )avvertenz[ae](?! del server)|disclaimer|nota bene|nota importante|⚠️?\s*\*\*|non (sostituisce|costituisce) (un )?(parere|consulenza)"
    r"|si (consiglia|raccomanda) (sempre )?di verificare|verifica(re)? sempre (le fonti|con)|rivolgersi a un professionista)")


def box_finale(testo: str) -> str:
    """Restituisce il blocco finale se sembra un riquadro di avvertenze (euristica)."""
    blocchi = [b.strip() for b in re.split(r"\n\s*\n|\n-{3,}\n", testo.strip()) if b.strip()]
    for b in blocchi[-2:]:
        senza_avviso = "\n".join(r for r in b.splitlines() if not AVVISO_RE.search(r))
        if _BOX.search(senza_avviso) and len(senza_avviso) < 900:
            # un'avvertenza dentro un paragrafo di analisi con citazione è inline, non un box
            if "](http" in senza_avviso and not senza_avviso.lstrip().startswith((">", "**", "#", "⚠")):
                continue
            return senza_avviso
    return ""


_IT = set("il lo la gli le di del della dei delle che non per una un con nel nella alla sono è ha questo questa sentenza corte anche come più dal sul".split())
_EN = set("the and of to is that for with this are was court which on from be by an it as has have".split())


def conta_lingua(testo: str) -> tuple[int, int]:
    parole = re.findall(r"[a-zàèéìòù]+", testo.lower())
    return sum(p in _IT for p in parole), sum(p in _EN for p in parole)


def controllo_shell_catalogo(ex: Esecuzione) -> list[tuple[str, bool, str]]:
    """Un comando estraneo resta una violazione anche se il runtime lo rifiuta."""
    calls = [c for c in ex.chiamate if c["tool"] == "Bash"]
    if not calls:
        return []
    cwd = ex.init.get("cwd")
    helper = (Path(cwd) / "buddalaw/scripts/verifica_catalogo.py").resolve() if cwd else None
    visibili = {norm_tool(t) for t in list(ex.init.get("tools") or [])
                + list(ex.init.get("tools_scoperti") or []) if e_buddalaw(t)}
    estranei = []
    for c in calls:
        command = c.get("argomenti", {}).get("command", "")
        try:
            a = shlex.split(command)
            ok = (len(a) >= 6 and a[0] == "python3" and helper is not None
                  and Path(a[1]).is_absolute() and Path(a[1]).resolve() == helper
                  and a[2] == "--totale" and a[4] == "--nomi")
            if ok:
                nomi = [norm_tool(n) for n in a[5:]]
                ok = int(a[3]) == len(nomi) == len(set(nomi)) and set(nomi) == visibili
        except (ValueError, OSError):
            ok = False
        if not ok:
            estranei.append(command[:100])
    return [("v9: shell solo per il catalogo osservato", not estranei, "; ".join(estranei[:3]))]


def valuta(caso: dict, config: str, ex: Esecuzione, problemi_isolamento: list[str]) -> dict:
    duri = controlli_specifici(caso, ex)
    extra = (caso.get("per_config") or {}).get(config)
    if extra:
        duri += controlli_specifici({k: v for k, v in extra.items()}, ex)
    duri += controlli_generali(ex)
    if config == "v9":
        duri += controllo_shell_catalogo(ex)
        turni = {c.get("turno", 1) for c in ex.chiamate}
        for turn in sorted(turni):
            calls = [c for c in ex.chiamate if c.get("turno", 1) == turn and e_buddalaw(c["nome_originale"])]
            searches = sum(c["tool"].startswith("search_") for c in calls)
            judgements = sum(c["tool"] == "get_judgement" for c in calls)
            duri += [(f"v9: ricerche turno {turn} ≤ 4", searches <= 4, str(searches)),
                     (f"v9: get_judgement turno {turn} ≤ 2", judgements <= 2, str(judgements))]
        norm_links = [u for u in url_nel_testo(ex.testo_visibile) if "normattiva.it" in urllib.parse.urlsplit(u).netloc]
        # Questa suite isola BuddaLaw: non installa né carica Normattiva.
        duri.append(("v9: nessun link normativo senza skill normattiva", not norm_links, " ".join(norm_links[:2])))
    if problemi_isolamento:
        duri.append(("isolamento (init e skill caricate)", False, "; ".join(problemi_isolamento)[:300]))
    morbidi = controlli_specifici(caso.get("morbidi") or {}, ex)
    return {
        "promosso": all(ok for _, ok, _ in duri),
        "controlli": [{"nome": n, "ok": ok, "dettaglio": d} for n, ok, d in duri],
        "morbidi": [{"nome": n, "ok": ok, "dettaglio": d} for n, ok, d in morbidi],
        "chiamate": [{"tool": c["tool"], "buddalaw": e_buddalaw(c["nome_originale"]), "argomenti": c["argomenti"]}
                     for c in ex.chiamate],
        "costo_usd": round(ex.costo, 5),
        "costo_parziale": bool(ex.errore),
        "token": ex.token,
        "durata_s": round(ex.durata, 1),
        "errore": ex.errore,
        "classe": "esecuzione" if ex.errore or problemi_isolamento else "comportamento",
        "perimetro": "Controlli tecnici e di comportamento; non certificano la correttezza giuridica.",
        "testo_finale": ex.testo_finale,
    }


# --------------------------------------------------------------------------- orchestrazione

def turni_di(caso: dict) -> list[str]:
    return [caso["prompt"]] + list(caso.get("turni_successivi") or [])


def soglia(n: int) -> int:
    return 1 if n == 1 else math.ceil(2 * n / 3)


@contextlib.contextmanager
def sandbox_lock():
    SANDBOX.mkdir(parents=True, exist_ok=True)
    with (SANDBOX/".benchmark.lock").open("w") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(lock,fcntl.LOCK_UN)


def main() -> int:
    try:
        with sandbox_lock():
            return _main()
    except BlockingIOError:
        print("Sandbox già occupata da un collaudo: nessuna esecuzione avviata.")
        return 2


def _main() -> int:
    global SKILL_DIR
    ap = argparse.ArgumentParser(description="Livello B end-to-end della skill buddalaw")
    ap.add_argument("--runtime", default="claude", help="claude, opencode o claude,opencode")
    ap.add_argument("--config", default="v9", help="v9, v8.4, nessuna (anche separate da virgola)")
    ap.add_argument("--modello", default=None,
                    help=f"claude: id del modello (default {MODELLO_CLAUDE}) o 'default' = modello predefinito, solo casi ⚡; "
                         f"opencode: provider/modello (default {', '.join(MODELLI_OPENCODE)})")
    ap.add_argument("--casi", default=None, help="id separati da virgola, es. B00,B02")
    ap.add_argument("--casi-file", type=Path, default=CASI, help="raccolta casi alternativa, copiata nel campione")
    ap.add_argument("--solo-lampo", action="store_true", help="solo i casi ⚡")
    ap.add_argument("--runs", type=int, default=1, help="esecuzioni per caso (con 3: promosso con almeno 2)")
    ap.add_argument("--runs-lampo", type=int, default=None, help="ripetizioni complessive dei soli casi critici")
    ap.add_argument("--budget", type=float, default=5.0, help="tetto di spesa in $ per modello (default 5)")
    ap.add_argument("--budget-run", type=float, default=0.60, help="--max-budget-usd per singola esecuzione Claude")
    ap.add_argument("--solo-abbonamento", action="store_true",
                    help="solo Claude con accesso claude.ai verificato; esclude API e OpenRouter")
    ap.add_argument("--prova", action="store_true", help="prepara e stampa i comandi senza eseguirli")
    ap.add_argument("--rivaluta", type=Path, default=None,
                    help="rivaluta i transcript già salvati in results/<data> senza nuove chiamate")
    a = ap.parse_args()
    if a.rivaluta:
        return rivaluta(a.rivaluta)

    if a.runs < 1 or (a.runs_lampo is not None and a.runs_lampo < 1):
        ap.error("le ripetizioni devono essere positive")
    casi = json.loads(a.casi_file.read_text(encoding="utf-8"))["casi"]
    if a.casi:
        voluti = [c.strip() for c in a.casi.split(",")]
        sconosciuti = set(voluti) - {c["id"] for c in casi}
        if sconosciuti:
            ap.error(f"casi sconosciuti: {', '.join(sorted(sconosciuti))}")
        casi = [c for c in casi if c["id"] in voluti]
    if a.solo_lampo:
        casi = [c for c in casi if c.get("lampo")]
    if not casi:
        ap.error("nessun caso selezionato")
    configs = [c.strip() for c in a.config.split(",")]
    for c in configs:
        if c not in CONFIG_VALIDE:
            ap.error(f"configurazione sconosciuta: {c}")
    runtimes = [r.strip() for r in a.runtime.split(",")]

    obiettivi = []  # (runtime, modello)
    for rt in runtimes:
        if rt == "claude":
            m = a.modello or MODELLO_CLAUDE
            obiettivi.append(("claude", None if m == "default" else m))
        elif rt == "opencode":
            for m in ([a.modello] if a.modello else MODELLI_OPENCODE):
                obiettivi.append(("opencode", m))
        else:
            ap.error(f"runtime sconosciuto: {rt}")

    autenticazione = None
    if a.solo_abbonamento:
        try:
            autenticazione = verifica_abbonamento_claude(runtimes, obiettivi[0][1])
        except ValueError as e:
            ap.error(str(e))

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    base = RISULTATI / stamp
    base.mkdir(parents=True, exist_ok=True)
    shutil.copy2(a.casi_file, base / "casi.json")
    snapshot = prepara_skill("v9", base / "snapshot-skill")
    SKILL_DIR = snapshot
    manifest = {"skill_sha256":hashlib.sha256((snapshot/"SKILL.md").read_bytes()).hexdigest(),
                "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "file_skill_sha256":{str(p.relative_to(snapshot)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(snapshot.rglob("*")) if p.is_file()},
                "casi_sha256":hashlib.sha256(a.casi_file.read_bytes()).hexdigest(),
                "schema_sha256":hashlib.sha256((QUI.parent/"fixtures/tool_schema.json").read_bytes()).hexdigest(),
                "configs":configs,"modelli":obiettivi,"runs":a.runs,"runs_lampo":a.runs_lampo,
                "max_turni_claude": MAX_TURNI_CLAUDE,
                "budget_per_modello":a.budget,"piano":[]}
    manifest["sandbox"] = str(SANDBOX)
    manifest["stop_condiviso"] = bool(os.environ.get("BUDDALAW_STOP_FILE"))
    if autenticazione:
        manifest["autenticazione_abbonamento"] = autenticazione
    righe_esiti: list[dict] = []
    spesa: dict[str, float] = {}
    note: list[str] = []
    if autenticazione:
        note.append("Accesso con abbonamento Claude verificato. I valori USD sono stime dei token della CLI, non addebiti attestati; OpenRouter escluso.")
    fermo = ""
    oc = trova_opencode()
    for rt, modello in obiettivi:
        for config in configs:
            for c in casi:
                if c.get("solo_se_config") and config not in c["solo_se_config"]:
                    continue
                if rt == "claude" and modello is None and not a.casi and not c.get("lampo"):
                    continue
                n = a.runs_lampo if c.get("lampo") and a.runs_lampo is not None else a.runs
                manifest["piano"].append({"runtime":rt,"modello":modello,"config":config,"caso":c["id"],"runs":n})
    (base/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")

    for rt, modello in obiettivi:
        etichetta = f"{rt}:{modello or 'predefinito'}"
        spesa.setdefault(etichetta, 0.0)
        try:
            verifica_stop_condiviso()
        except Blocco as e:
            fermo = str(e)
            break
        if rt == "opencode":
            if not oc:
                note.append(f"{etichetta}: saltato, opencode non trovato (imposta OPENCODE_BIN)")
                continue
            if not a.prova:
                try:
                    preflight_opencode(oc)
                except (Salta, Blocco) as e:
                    note.append(f"{etichetta}: saltato, {e}")
                    print(f"[salto] {etichetta}: {e}")
                    if isinstance(e, Blocco):
                        condividi_stop()
                        fermo = str(e)
                        break
                    continue
        casi_rt = casi
        if rt == "claude" and modello is None and not a.casi:
            casi_rt = [c for c in casi if c.get("lampo")]
        elif a.solo_lampo:
            casi_rt = [c for c in casi if c.get("lampo")]
        for config in configs:
            for caso in casi_rt:
                if caso.get("solo_se_config") and config not in caso["solo_se_config"]:
                    continue
                cfg_eff = caso.get("config") or config
                cartella = base / f"{rt}__{(modello or 'predefinito').replace('/', '_')}__{config}"
                cartella.mkdir(exist_ok=True)
                riuscite = 0
                runs = []
                n_runs = a.runs_lampo if caso.get("lampo") and a.runs_lampo is not None else a.runs
                for r in range(1, n_runs + 1):
                    if spesa[etichetta] >= a.budget:
                        note.append(f"{etichetta}: tetto di {a.budget:.2f} $ raggiunto, esecuzioni interrotte")
                        break
                    file_ev = cartella / f"{caso['id']}__r{r}.jsonl"
                    if a.prova:
                        if rt == "claude":
                            print(" ".join(comando_claude(caso["prompt"][:40] + "…", modello, a.budget_run, Path("<skill-prompt.md>") if cfg_eff != "nessuna" else None)))
                        else:
                            print(f"{oc} run --format json --dir {SANDBOX} -m {modello} '{caso['prompt'][:40]}…'")
                        continue
                    print(f"[{etichetta} {config}{'→' + cfg_eff if cfg_eff != config else ''}] {caso['id']} run {r}/{n_runs} …", flush=True)
                    try:
                        if rt == "claude":
                            br = min(a.budget_run, a.budget - spesa[etichetta])
                            ex, probl = esegui_claude(turni_di(caso), cfg_eff, modello, br, file_ev)
                        else:
                            ex, probl = esegui_opencode(oc, turni_di(caso), cfg_eff, modello, file_ev, budget_run=a.budget-spesa[etichetta])
                    except Blocco as e:
                        condividi_stop()
                        fermo = f"STOP: {etichetta} {caso['id']}: {e}"
                        print(fermo)
                        ex, probl = getattr(e, "esecuzione", Esecuzione(errore=str(e))), []
                    except subprocess.TimeoutExpired:
                        ex, probl = Esecuzione(errore="timeout 600 s"), []
                    except Salta as e:
                        ex, probl = Esecuzione(errore=str(e)), [str(e)]
                    spesa[etichetta] += ex.costo
                    valutazione = valuta(caso, config, ex, probl)
                    (cartella / f"{caso['id']}__r{r}.esito.json").write_text(
                        json.dumps(valutazione, ensure_ascii=False, indent=2), encoding="utf-8")
                    riuscite += valutazione["promosso"]
                    runs.append(valutazione)
                    falliti = [c["nome"] + (f" [{c['dettaglio']}]" if c["dettaglio"] else "") for c in valutazione["controlli"] if not c["ok"]]
                    print(f"    {'OK ' if valutazione['promosso'] else 'NO '} {ex.costo:.4f} $ · {len([c for c in ex.chiamate if e_buddalaw(c['nome_originale'])])} chiamate BuddaLaw"
                          + (f" · falliti: {'; '.join(falliti)}" if falliti else ""), flush=True)
                    if fermo:
                        break
                if runs:
                    validi = sum(x["classe"] != "esecuzione" for x in runs)
                    righe_esiti.append({
                        "runtime": etichetta, "config": config, "caso": caso["id"], "checklist": caso.get("checklist"),
                        "lampo": caso.get("lampo", False), "titolo": caso["titolo"], "runs": len(runs), "ok": riuscite,
                        "promosso": len(runs) == n_runs and validi == n_runs and riuscite >= soglia(n_runs),
                        "validi": validi,
                        "valutabile": validi == n_runs,
                        "runs_previsti": n_runs,
                        "costo": sum(x["costo_usd"] for x in runs),
                        "chiamate_medie": sum(sum(c["buddalaw"] for c in x["chiamate"]) for x in runs) / len(runs),
                        "falliti": sorted({c["nome"] for x in runs for c in x["controlli"] if not c["ok"]}),
                        "morbidi_ko": sorted({c["nome"] for x in runs for c in x["morbidi"] if not c["ok"]}),
                    })
                if fermo:
                    break
            if fermo:
                break
        if fermo:
            break

    if a.prova:
        shutil.rmtree(base, ignore_errors=True)
        return 0
    previsti = sum(p["runs"] for p in manifest["piano"])
    eseguiti = sum(r["runs"] for r in righe_esiti)
    validi = sum(r["validi"] for r in righe_esiti)
    completo = previsti > 0 and eseguiti == previsti and validi == previsti
    note.append(f"copertura: {eseguiti}/{previsti} esecuzioni, {validi} valide; {'completa' if completo else 'INCOMPLETA'}")
    riepilogo = componi_riepilogo(righe_esiti, spesa, note, fermo, stamp)
    (base / "esiti.json").write_text(json.dumps({"esiti": righe_esiti, "spesa": spesa, "note": note, "fermo": fermo},
                                                ensure_ascii=False, indent=2), encoding="utf-8")
    (base / "riepilogo.txt").write_text(riepilogo, encoding="utf-8")
    print("\n" + riepilogo)
    print(f"Transcript ed esiti in {base}")
    return codice_uscita(righe_esiti, completo, fermo)


def codice_uscita(righe, completo=True, fermo=""):
    if fermo or not righe or not completo:
        return 2
    gravi = any("fedeltà link (URL identici ai tool_result)" in r.get("falliti", []) for r in righe)
    return 0 if all(r["promosso"] for r in righe) and not gravi else 1


def rivaluta(cartella: Path) -> int:
    """Rilegge i .jsonl salvati e riapplica i controlli attuali (nessuna chiamata ai modelli)."""
    casi_file = cartella / "casi.json" if (cartella / "casi.json").exists() else CASI
    casi = {c["id"]: c for c in json.loads(casi_file.read_text(encoding="utf-8"))["casi"]}
    manifest = json.loads((cartella/"manifest.json").read_text()) if (cartella/"manifest.json").exists() else {}
    righe, spesa, esclusi = [], {}, []
    for sotto in sorted(p for p in cartella.iterdir() if p.is_dir()):
        if len(sotto.name.split("__")) != 3:
            continue
        rt, modello, config = sotto.name.split("__")
        etichetta = f"{rt}:{modello}"
        per_caso: dict[str, list] = {}
        for f in sorted(sotto.glob("*__r*.jsonl")):
            cid = f.name.split("__")[0]
            if cid not in casi or not re.fullmatch(re.escape(cid)+r"__r\d+\.jsonl", f.name):
                continue
            caso = casi[cid]
            linee = f.read_text(encoding="utf-8").splitlines()
            try:
                if rt == "claude":
                    ex = parsifica_claude(linee)
                    probl = verifica_init_claude(ex.init, config) if ex.init else ["system/init assente"]
                else:
                    ex = parsifica_opencode(linee)
                    meta_path = f.with_suffix(".meta.json")
                    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
                    probl = list(meta.get("problemi_isolamento") or [])
                    if not meta:
                        probl.append("prova di isolamento non conservata: esecuzione storica non verificabile")
                    if not meta.get("completata", False):
                        ex.errore = meta.get("errore") or "esecuzione non documentata come completa"
                if rt == "claude":
                    meta_path = f.with_suffix(".meta.json")
                    if meta_path.exists():
                        meta = json.loads(meta_path.read_text())
                        scoperta_budda = ex.init.get("buddalaw_accesso_provato") or any(
                            t.startswith("mcp__claude_ai_BuddaLaw__") for t in ex.init.get("tools_scoperti", []))
                        probl.extend(p for p in meta.get("problemi_isolamento", []) if p not in probl
                                     and not (scoperta_budda and p.startswith("tool BuddaLaw assenti in claude -p")))
                        if not meta.get("completata", False):
                            ex.errore = meta.get("errore") or "esecuzione non documentata come completa"
            except Blocco as e:
                # esecuzione colpita da un blocco o guasto del server: non misura la skill
                esclusi.append(f"{sotto.name}/{f.name}: {str(e)[:120]}")
                continue
            v = valuta(caso, config, ex, probl)
            (f.with_name(f.name.replace(".jsonl", ".esito.json"))).write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
            per_caso.setdefault(cid, []).append(v)
            spesa[etichetta] = spesa.get(etichetta, 0.0) + ex.costo
        for cid, runs in per_caso.items():
            caso = casi[cid]
            ok = sum(x["promosso"] for x in runs)
            expected = next((p["runs"] for p in manifest.get("piano", []) if p["runtime"]==rt
                             and (p["modello"] or "predefinito").replace("/","_")==modello
                             and p["config"]==config and p["caso"]==cid), len(runs))
            validi = sum(x["classe"] != "esecuzione" for x in runs)
            righe.append({"runtime": etichetta, "config": config, "caso": cid, "checklist": caso.get("checklist"),
                          "lampo": caso.get("lampo", False), "titolo": caso["titolo"], "runs": len(runs), "ok": ok,
                          "runs_previsti":expected,
                          "promosso": len(runs)==expected and validi==expected and ok >= soglia(expected),
                          "validi":validi,"valutabile":validi==expected,
                          "costo": sum(x["costo_usd"] for x in runs),
                          "chiamate_medie": sum(sum(c["buddalaw"] for c in x["chiamate"]) for x in runs) / len(runs),
                          "falliti": sorted({c["nome"] for x in runs for c in x["controlli"] if not c["ok"]}),
                          "morbidi_ko": sorted({c["nome"] for x in runs for c in x["morbidi"] if not c["ok"]})})
    note = ["rivalutazione dei transcript salvati, nessuna nuova chiamata"]
    if manifest.get("autenticazione_abbonamento"):
        note.append("Accesso con abbonamento Claude verificato. I valori USD sono stime dei token della CLI, non addebiti attestati; OpenRouter escluso.")
    previsti = sum(p["runs"] for p in manifest.get("piano", []))
    eseguiti = sum(r["runs"] for r in righe)
    completo = bool(previsti) and eseguiti == previsti and all(r["valutabile"] for r in righe)
    note.append(f"copertura: {eseguiti}/{previsti or 'non documentato'}; {'completa' if completo else 'INCOMPLETA'}")
    if esclusi:
        note.append(f"{len(esclusi)} esecuzioni escluse per blocco o guasto del server: " + "; ".join(e.split(":")[0] for e in esclusi))
    testo = componi_riepilogo(righe, spesa, note, "", cartella.name)
    (cartella / "riepilogo.txt").write_text(testo, encoding="utf-8")
    (cartella / "rivalutazione.json").write_text(json.dumps({
        "data":datetime.now().isoformat(),
        "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "copertura_completa":completo, "esiti":righe,"spesa_nota":spesa,
        "note":note},ensure_ascii=False,indent=2)+"\n")
    print(testo)
    return codice_uscita(righe, completo)


def componi_riepilogo(righe: list[dict], spesa: dict, note: list[str], fermo: str, stamp: str) -> str:
    out = [f"## Livello B buddalaw — {stamp}", "",
           "| Runtime | Config | Caso | ⚡ | T | Esito | OK/run | Chiamate | $ | Controlli falliti | Morbidi KO |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in righe:
        out.append(f"| {r['runtime']} | {r['config']} | {r['caso']} {r['titolo']} | {'⚡' if r['lampo'] else ''} | {r['checklist'] or ''} | "
                   f"{'promosso' if r['promosso'] else 'BOCCIATO' if r.get('valutabile',True) else 'NON VALUTABILE'} | {r['ok']}/{r['runs']} | {r['chiamate_medie']:.1f} | {r['costo']:.3f} | "
                   f"{'; '.join(r['falliti'])} | {'; '.join(r['morbidi_ko'])} |")
    out.append("")
    for rt in sorted({r["runtime"] for r in righe}):
        for cfg in sorted({r["config"] for r in righe if r["runtime"] == rt}):
            sel = [r for r in righe if r["runtime"] == rt and r["config"] == cfg and r["caso"] != "B00"]
            validi = [r for r in sel if r.get("valutabile",True)]
            lampo = [r for r in validi if r["lampo"]]
            out.append(f"- {rt} {cfg}: {sum(r['promosso'] for r in validi)}/{len(validi)} casi valutabili promossi"
                       + (f", ⚡ {sum(r['promosso'] for r in lampo)}/{len(lampo)}" if lampo else "")
                       + f"; {len(sel)-len(validi)} non valutabili")
    out.append("- spesa nota registrata: " + ", ".join(f"{k} {v:.3f} $" for k, v in spesa.items()) + f" · totale {sum(spesa.values()):.3f} $")
    out.append("- il punteggio comportamentale esclude B00 (isolamento); una prova interrotta può avere costi non ancora riportati dal provider.")
    for n in dict.fromkeys(note):
        out.append(f"- nota: {n}")
    if fermo:
        out.append(f"- **{fermo}** (nessun ritento: decide l'utente se e quando riprovare)")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
