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
import glob
import json
import math
import os
import re
import shutil
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
SANDBOX = QUI / ".opencode-sandbox"
TAG_V84 = "buddalaw-v8.4"

PREFISSI = ("mcp__claude_ai_BuddaLaw__", "mcp__buddalaw__", "buddalaw_")
MODELLO_CLAUDE = "claude-haiku-5-5"
MODELLI_OPENCODE = ["openrouter/qwen/qwen3.8-flash", "openrouter/deepseek/deepseek-v4.1-flash"]
CONFIG_VALIDE = ("v9", "v8.4", "nessuna", "v9-ridotta")
# server MCP dell'utente da tenere fuori dalle prove con Claude Code
MCP_VIETATI = [
    "mcp__bdm", "mcp__italgiure", "mcp__normattiva", "mcp__claude-in-chrome",
    "mcp__claude_ai_Claude_Docs", "mcp__claude_ai_Corpus_gestiolex", "mcp__claude_ai_Gmail",
    "mcp__claude_ai_Google_Calendar", "mcp__claude_ai_Google_Drive",
]
AVVISO_RE = re.compile(r"⚠️?\s*BuddaLaw è stato aggiornato")
ESTREMI_RE = re.compile(r"\bn\.\s?(\d{1,5})/((?:19|20)\d{2})\b")
VIRGOLETTATO_RE = re.compile(r"«([^»]{40,})»|\"([^\"]{40,})\"")
LINK_MD_RE = re.compile(r"\[([^\]]+)\]\(<?(https?://[^)\s>]+)>?\)")
URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
DOMINI_LINK = ("platform.buddalaw.com", "normattiva.it")
# blocco del server: solo su risultati di errore o brevi, per non scambiare un
# «art. 403» in una sentenza per un codice HTTP
BLOCCO_RE = re.compile(
    r"(?i)(\b(http|status(code)?|errore?|error|codice)\b\W{0,3}\D{0,12}\b(403|429)\b"
    r"|too many requests|rate.?limit|forbidden|troppe richieste|account (bloccato|sospeso)|quota (esaurita|exceeded)"
    # guasto del server (osservato il 2026-10-17): le prove successive non misurano la skill
    r"|circuit breaker|backend temporaneamente non disponibile|servizio non è momentaneamente disponibile)"
)


class Blocco(Exception):
    """403/429 o blocco del server: ci si ferma, senza ritentare."""


class Salta(Exception):
    """Runtime non utilizzabile (es. autenticazione mancante): si salta e lo si dice."""


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
        righe = testo.splitlines(keepends=True)
        for i, r in enumerate(righe):
            if "inventario_tool_buddalaw" in r:
                nuova = r.replace(', "search_similar_cases"', "").replace('"search_similar_cases", ', "")
                if nuova == r:
                    raise RuntimeError("v9-ridotta: search_similar_cases non trovato nell'inventario")
                righe[i] = nuova
        sk.write_text("".join(righe), encoding="utf-8")
    return dest


def prompt_di_sistema(skill: Path) -> str:
    testo = (skill / "SKILL.md").read_text(encoding="utf-8")
    testo = testo.replace("](references/", f"]({skill}/references/")
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
           "--no-session-persistence", "--max-turns", "8", "--max-budget-usd", f"{budget_run:.2f}",
           "--disable-slash-commands", "--tools", "Read,ToolSearch",
           "--allowedTools", "mcp__claude_ai_BuddaLaw__*,Read,ToolSearch",
           "--disallowedTools", ",".join(MCP_VIETATI)]
    if modello:
        cmd += ["--model", modello]
    if spf:
        cmd += ["--append-system-prompt-file", str(spf)]
    return cmd


def testo_risultato(contenuto) -> str:
    if isinstance(contenuto, str):
        return contenuto
    if isinstance(contenuto, list):
        return "\n".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in contenuto)
    return json.dumps(contenuto, ensure_ascii=False)


def parsifica_claude(righe: list[str]) -> Esecuzione:
    ex = Esecuzione()
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
                    ex.chiamate.append({"tool": norm_tool(b.get("name", "")), "nome_originale": b.get("name", ""),
                                        "argomenti": b.get("input") or {}, "id": b.get("id")})
        elif tipo == "user":
            for b in (ev.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    t = testo_risultato(b.get("content"))
                    ex.risultati.append(t)
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
    if not ex.testo_finale and ex.testi:
        ex.testo_finale = ex.testi[-1]
    return ex


def verifica_init_claude(init: dict, config: str) -> list[str]:
    problemi = []
    tools = init.get("tools") or []
    if not any(t.startswith("mcp__claude_ai_BuddaLaw__") for t in tools):
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


def _claude_piu_turni(cmd: list[str], turni: list[str], cwd: Path, env: dict) -> tuple[str, str, int]:
    """Un messaggio per volta: il successivo parte solo dopo l'evento `result` del turno
    precedente (se si scrivono tutti subito, Claude Code li fonde in un solo turno)."""
    err = tempfile.TemporaryFile(mode="w+")
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=err, text=True, bufsize=1)
    righe: list[str] = []
    scadenza = time.time() + 900

    def invia(t: str) -> None:
        proc.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": t}}, ensure_ascii=False) + "\n")
        proc.stdin.flush()

    invia(turni[0])
    da_inviare = list(turni[1:])
    for riga in proc.stdout:
        righe.append(riga)
        if time.time() > scadenza:
            proc.kill()
            break
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            if ev.get("subtype") not in (None, "success") or not da_inviare:
                proc.stdin.close()
                da_inviare = []
            else:
                invia(da_inviare.pop(0))
    proc.wait(timeout=60)
    err.seek(0)
    return "".join(righe), err.read(), proc.returncode


def esegui_claude(turni: list[str], config: str, modello: str | None, budget_run: float, cartella: Path) -> tuple[Esecuzione, list[str]]:
    lavoro = Path(tempfile.mkdtemp(prefix="buddalaw-e2e-"))
    try:
        skill = prepara_skill(config, lavoro)
        spf = None
        if skill:
            spf = lavoro / "skill-prompt.md"
            spf.write_text(prompt_di_sistema(skill), encoding="utf-8")
        cmd = comando_claude(turni[0] if len(turni) == 1 else None, modello, budget_run, spf)
        env = dict(os.environ, CLAUDE_CODE_DISABLE_AUTO_MEMORY="1")
        t0 = time.time()
        if len(turni) == 1:
            proc = subprocess.run(cmd, cwd=lavoro, capture_output=True, text=True, timeout=600, env=env)
            stdout, stderr, codice = proc.stdout, proc.stderr, proc.returncode
        else:
            stdout, stderr, codice = _claude_piu_turni(cmd, turni, lavoro, env)
        righe = stdout.splitlines()
        cartella.write_text(stdout, encoding="utf-8")
        if stderr.strip():
            cartella.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")
        ex = parsifica_claude(righe)
        ex.durata = time.time() - t0
        if not righe:
            ex.errore = f"nessun output (exit {codice}): {stderr[:300]}"
        return ex, verifica_init_claude(ex.init, config) if ex.init else ["system/init assente"]
    finally:
        shutil.rmtree(lavoro, ignore_errors=True)


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
    mcp = _pulisci(subprocess.run([oc, "mcp", "list"], cwd=SANDBOX, capture_output=True, text=True, env=env, timeout=120).stdout)
    riga = next((r for r in mcp.splitlines() if "buddalaw" in r.lower()), "")
    if not riga:
        raise Salta("server MCP buddalaw non configurato nella sandbox: rilancia prepara_opencode.sh")
    if "needs authentication" in riga or "needs_auth" in riga or "✗" in riga or "failed" in riga.lower():
        raise Salta(f"BuddaLaw non autenticato in opencode ({riga.strip(' │●')}): "
                    f"cd \"{SANDBOX}\" && OPENCODE_DB=\"{SANDBOX / '.opencode-test.db'}\" {oc} mcp auth buddalaw")


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
        if "buddalaw" in luoghi:
            problemi.append(f"config nessuna ma skill buddalaw presente: {luoghi['buddalaw']}")
    elif not luoghi.get("buddalaw", "").startswith(str(SANDBOX)):
        problemi.append(f"skill buddalaw non caricata dalla sandbox: {luoghi.get('buddalaw')}")
    return problemi


def _stdout_su_file(cmd: list[str], timeout: int, salva: Path | None = None) -> str:
    """opencode (bun) tronca lo stdout su pipe a 64 KB quando esce: si scrive su file."""
    dest = salva or Path(tempfile.mkstemp(prefix="opencode-", suffix=".out")[1])
    err = dest.with_suffix(".stderr.txt")
    with open(dest, "w", encoding="utf-8") as fo, open(err, "w", encoding="utf-8") as fe:
        subprocess.run(cmd, cwd=SANDBOX, stdout=fo, stderr=fe, text=True, timeout=timeout, env=env_opencode())
    testo = dest.read_text(encoding="utf-8")
    if not salva:
        dest.unlink(missing_ok=True)
    if not err.read_text(encoding="utf-8").strip() or not salva:
        err.unlink(missing_ok=True)
    return testo


def parsifica_opencode(righe: list[str]) -> Esecuzione:
    ex = Esecuzione()
    passo: list[str] = []
    ultimi: list[str] = []
    tok = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0}
    for riga in righe:
        try:
            ev = json.loads(riga)
        except json.JSONDecodeError:
            continue
        tipo, part = ev.get("type"), ev.get("part") or {}
        if tipo == "step_start":
            passo = []
        elif tipo == "text":
            ex.testi.append(part.get("text", ""))
            passo.append(part.get("text", ""))
        elif tipo == "tool_use":
            st = part.get("state") or {}
            nome = part.get("tool", "")
            ex.chiamate.append({"tool": norm_tool(nome), "nome_originale": nome,
                                "argomenti": st.get("input") or {}, "id": part.get("callID")})
            out = st.get("output") if st.get("status") == "completed" else (st.get("error") or "")
            t = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
            ex.risultati.append(t)
            if e_buddalaw(nome):
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
            if dati.get("statusCode") in (403, 429):
                raise Blocco(f"opencode/provider: {ex.errore}")
    ex.token = tok
    ex.testo_finale = "\n\n".join(ultimi or passo)
    return ex


def esegui_opencode(oc: str, turni: list[str], config: str, modello: str, cartella: Path) -> tuple[Esecuzione, list[str]]:
    skills = SANDBOX / ".opencode" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    prepara_skill(config, skills)  # crea o sostituisce .opencode/skills/buddalaw
    if config == "nessuna" and (skills / "buddalaw").exists():
        shutil.rmtree(skills / "buddalaw")
    problemi = verifica_skill_opencode(oc, config)
    if problemi:
        return Esecuzione(errore="isolamento della skill non verificato"), problemi
    t0 = time.time()
    stdout, sessione = "", None
    for i, prompt in enumerate(turni):
        cmd = [oc, "run", "--format", "json", "--dir", str(SANDBOX), "-m", modello]
        if sessione:
            cmd += ["--session", sessione]  # turni successivi nella stessa sessione
        parziale = _stdout_su_file(cmd + [prompt], timeout=600,
                                   salva=cartella if i == 0 else cartella.with_suffix(f".t{i + 1}.jsonl"))
        stdout += parziale
        if sessione is None:
            m = re.search(r'"sessionID"\s*:\s*"([^"]+)"', parziale)
            sessione = m.group(1) if m else None
            if len(turni) > 1 and not sessione:
                break
    if len(turni) > 1:
        cartella.write_text(stdout, encoding="utf-8")
    ex = parsifica_opencode(stdout.splitlines())
    ex.durata = time.time() - t0
    ex.init = {"skill_check": problemi}
    if not stdout.strip():
        ex.errore = f"nessun output: vedi {cartella.with_suffix('.stderr.txt').name}"
    nomi = {c["nome_originale"] for c in ex.chiamate}
    if any("non disponibil" in t.lower() and "tool" in t.lower() for t in ex.testi) and not any(e_buddalaw(n) for n in nomi):
        problemi.append("dichiara i tool non disponibili senza averli chiamati (prefisso buddalaw_?)")
    return ex, problemi


def controlla_blocco(testo: str, errore: bool) -> None:
    if (errore or len(testo) < 3000) and BLOCCO_RE.search(testo):
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


def corpus_risultati(ex: Esecuzione) -> str:
    """Testo dei tool_result, grezzo e con le stringhe JSON decodificate (\\n, \\", \\u00e8...)."""
    parti = []
    for r in ex.risultati:
        parti.append(r)
        try:
            parti.extend(_stringhe(json.loads(r)))
        except (json.JSONDecodeError, TypeError):
            pass
    grezzo = "\n".join(parti)
    return grezzo + "\n" + grezzo.replace("\\/", "/").replace("\\u0026", "&")


def url_nel_testo(testo: str) -> list[str]:
    out = []
    for u in URL_RE.findall(testo):
        u = u.rstrip(".,;:!?*_>")
        if any(d in urllib.parse.urlsplit(u).netloc for d in DOMINI_LINK):
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
        corpus = corpus or corpus_risultati(ex)
        orfani = []
        for num, anno in ESTREMI_RE.findall(testo):
            n = num.lstrip("0")
            if not (re.search(rf"(?<!\d)0*{n}(?!\d)", corpus) and anno in corpus):
                orfani.append(f"{num}/{anno}")
        esiti.append(("estremi citati presenti nei tool_result (niente memoria)", not orfani, ", ".join(orfani[:4])))
    if caso.get("virgolettati_fedeli"):
        corpus = corpus or corpus_risultati(ex)
        piatto = re.sub(r"\s+", " ", tipografia(corpus)).lower()
        falsi = []
        for m in VIRGOLETTATO_RE.finditer(testo):
            v = m.group(1) or m.group(2)
            # i tagli «[…]» o «...» separano frammenti: ognuno deve essere letterale
            for pezzo in re.split(r"\[?(?:…|\.\.\.)\]?", v):
                pezzo = re.sub(r"\s+", " ", tipografia(pezzo)).strip(" .,;:").lower()
                if len(pezzo) >= 25 and pezzo not in piatto:
                    falsi.append(pezzo)
        esiti.append(("virgolettati letterali dai tool_result", not falsi, " | ".join(f[:60] for f in falsi[:2])))
    for rx in caso.get("deve_contenere") or []:
        esiti.append((f"testo contiene /{rx}/", bool(re.search(rx, testo)), ""))
    for rx in caso.get("non_deve_contenere") or []:
        m = re.search(rx, testo)
        esiti.append((f"testo non contiene /{rx}/", not m, m.group(0)[:120] if m else ""))
    if "avviso" in caso:
        n = len(AVVISO_RE.findall(testo))
        esiti.append((f"avviso di aggiornamento = {caso['avviso']}", n == caso["avviso"], f"{n}"))
    return esiti


def controlli_generali(ex: Esecuzione) -> list[tuple[str, bool, str]]:
    esiti = []
    corpus = corpus_risultati(ex)
    corpus_dec = urllib.parse.unquote(corpus)
    inventati = [u for u in url_nel_testo(ex.testo_visibile)
                 if u not in corpus and urllib.parse.unquote(u) not in corpus_dec]
    esiti.append(("fedeltà link (URL identici ai tool_result)", not inventati, " ".join(inventati[:3])))
    generici = [t for t, u in LINK_MD_RE.findall(ex.testo_visibile)
                if any(d in urllib.parse.urlsplit(u).netloc for d in DOMINI_LINK) and not re.search(r"\d", t)]
    esiti.append(("link sugli estremi (non su «qui», «link»…)", not generici, " | ".join(generici[:3])))
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


def valuta(caso: dict, config: str, ex: Esecuzione, problemi_isolamento: list[str]) -> dict:
    duri = controlli_specifici(caso, ex)
    extra = (caso.get("per_config") or {}).get(config)
    if extra:
        duri += controlli_specifici({k: v for k, v in extra.items()}, ex)
    duri += controlli_generali(ex)
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
        "token": ex.token,
        "durata_s": round(ex.durata, 1),
        "errore": ex.errore,
        "testo_finale": ex.testo_finale,
    }


# --------------------------------------------------------------------------- orchestrazione

def turni_di(caso: dict) -> list[str]:
    return [caso["prompt"]] + list(caso.get("turni_successivi") or [])


def soglia(n: int) -> int:
    return 1 if n == 1 else math.ceil(2 * n / 3)


def main() -> int:
    ap = argparse.ArgumentParser(description="Livello B end-to-end della skill buddalaw")
    ap.add_argument("--runtime", default="claude", help="claude, opencode o claude,opencode")
    ap.add_argument("--config", default="v9", help="v9, v8.4, nessuna (anche separate da virgola)")
    ap.add_argument("--modello", default=None,
                    help=f"claude: id del modello (default {MODELLO_CLAUDE}) o 'default' = modello predefinito, solo casi ⚡; "
                         f"opencode: provider/modello (default {', '.join(MODELLI_OPENCODE)})")
    ap.add_argument("--casi", default=None, help="id separati da virgola, es. B00,B02")
    ap.add_argument("--solo-lampo", action="store_true", help="solo i casi ⚡")
    ap.add_argument("--runs", type=int, default=1, help="esecuzioni per caso (con 3: promosso con almeno 2)")
    ap.add_argument("--budget", type=float, default=5.0, help="tetto di spesa in $ per modello (default 5)")
    ap.add_argument("--budget-run", type=float, default=0.60, help="--max-budget-usd per singola esecuzione Claude")
    ap.add_argument("--prova", action="store_true", help="prepara e stampa i comandi senza eseguirli")
    ap.add_argument("--rivaluta", type=Path, default=None,
                    help="rivaluta i transcript già salvati in results/<data> senza nuove chiamate")
    a = ap.parse_args()
    if a.rivaluta:
        return rivaluta(a.rivaluta)

    casi = json.loads(CASI.read_text(encoding="utf-8"))["casi"]
    if a.casi:
        voluti = [c.strip() for c in a.casi.split(",")]
        casi = [c for c in casi if c["id"] in voluti]
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

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = RISULTATI / stamp
    base.mkdir(parents=True, exist_ok=True)
    righe_esiti: list[dict] = []
    spesa: dict[str, float] = {}
    note: list[str] = []
    fermo = ""
    oc = trova_opencode()

    for rt, modello in obiettivi:
        etichetta = f"{rt}:{modello or 'predefinito'}"
        spesa.setdefault(etichetta, 0.0)
        if rt == "opencode":
            if not oc:
                note.append(f"{etichetta}: saltato, opencode non trovato (imposta OPENCODE_BIN)")
                continue
            if not a.prova:
                try:
                    preflight_opencode(oc)
                except Salta as e:
                    note.append(f"{etichetta}: saltato, {e}")
                    print(f"[salto] {etichetta}: {e}")
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
                for r in range(1, a.runs + 1):
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
                    print(f"[{etichetta} {config}{'→' + cfg_eff if cfg_eff != config else ''}] {caso['id']} run {r}/{a.runs} …", flush=True)
                    try:
                        if rt == "claude":
                            br = min(a.budget_run, max(0.05, a.budget - spesa[etichetta]))
                            ex, probl = esegui_claude(turni_di(caso), cfg_eff, modello, br, file_ev)
                        else:
                            ex, probl = esegui_opencode(oc, turni_di(caso), cfg_eff, modello, file_ev)
                    except Blocco as e:
                        fermo = f"STOP: {etichetta} {caso['id']}: {e}"
                        print(fermo)
                        break
                    except subprocess.TimeoutExpired:
                        ex, probl = Esecuzione(errore="timeout 600 s"), []
                    spesa[etichetta] += ex.costo
                    valutazione = valuta(caso, config, ex, probl)
                    (cartella / f"{caso['id']}__r{r}.esito.json").write_text(
                        json.dumps(valutazione, ensure_ascii=False, indent=2), encoding="utf-8")
                    riuscite += valutazione["promosso"]
                    runs.append(valutazione)
                    falliti = [c["nome"] + (f" [{c['dettaglio']}]" if c["dettaglio"] else "") for c in valutazione["controlli"] if not c["ok"]]
                    print(f"    {'OK ' if valutazione['promosso'] else 'NO '} {ex.costo:.4f} $ · {len([c for c in ex.chiamate if e_buddalaw(c['nome_originale'])])} chiamate BuddaLaw"
                          + (f" · falliti: {'; '.join(falliti)}" if falliti else ""), flush=True)
                if runs:
                    righe_esiti.append({
                        "runtime": etichetta, "config": config, "caso": caso["id"], "checklist": caso.get("checklist"),
                        "lampo": caso.get("lampo", False), "titolo": caso["titolo"], "runs": len(runs), "ok": riuscite,
                        "promosso": riuscite >= soglia(len(runs)),
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
    riepilogo = componi_riepilogo(righe_esiti, spesa, note, fermo, stamp)
    (base / "esiti.json").write_text(json.dumps({"esiti": righe_esiti, "spesa": spesa, "note": note, "fermo": fermo},
                                                ensure_ascii=False, indent=2), encoding="utf-8")
    (base / "riepilogo.txt").write_text(riepilogo, encoding="utf-8")
    print("\n" + riepilogo)
    print(f"Transcript ed esiti in {base}")
    return 2 if fermo else (0 if all(r["promosso"] for r in righe_esiti) else 1)


def rivaluta(cartella: Path) -> int:
    """Rilegge i .jsonl salvati e riapplica i controlli attuali (nessuna chiamata ai modelli)."""
    casi = {c["id"]: c for c in json.loads(CASI.read_text(encoding="utf-8"))["casi"]}
    righe, spesa, esclusi = [], {}, []
    for sotto in sorted(p for p in cartella.iterdir() if p.is_dir()):
        rt, modello, config = sotto.name.split("__")
        etichetta = f"{rt}:{modello}"
        per_caso: dict[str, list] = {}
        for f in sorted(sotto.glob("B*__r*.jsonl")):
            cid = f.name.split("__")[0]
            if cid not in casi:
                continue
            caso = casi[cid]
            linee = f.read_text(encoding="utf-8").splitlines()
            try:
                if rt == "claude":
                    ex = parsifica_claude(linee)
                    probl = verifica_init_claude(ex.init, config) if ex.init else ["system/init assente"]
                else:
                    ex, probl = parsifica_opencode(linee), []
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
            righe.append({"runtime": etichetta, "config": config, "caso": cid, "checklist": caso.get("checklist"),
                          "lampo": caso.get("lampo", False), "titolo": caso["titolo"], "runs": len(runs), "ok": ok,
                          "promosso": ok >= soglia(len(runs)), "costo": sum(x["costo_usd"] for x in runs),
                          "chiamate_medie": sum(sum(c["buddalaw"] for c in x["chiamate"]) for x in runs) / len(runs),
                          "falliti": sorted({c["nome"] for x in runs for c in x["controlli"] if not c["ok"]}),
                          "morbidi_ko": sorted({c["nome"] for x in runs for c in x["morbidi"] if not c["ok"]})})
    note = ["rivalutazione dei transcript salvati, nessuna nuova chiamata"]
    if esclusi:
        note.append(f"{len(esclusi)} esecuzioni escluse per blocco o guasto del server: " + "; ".join(e.split(":")[0] for e in esclusi))
    testo = componi_riepilogo(righe, spesa, note, "", cartella.name)
    (cartella / "riepilogo.txt").write_text(testo, encoding="utf-8")
    print(testo)
    return 0 if all(r["promosso"] for r in righe) else 1


def componi_riepilogo(righe: list[dict], spesa: dict, note: list[str], fermo: str, stamp: str) -> str:
    out = [f"## Livello B buddalaw — {stamp}", "",
           "| Runtime | Config | Caso | ⚡ | T | Esito | OK/run | Chiamate | $ | Controlli falliti | Morbidi KO |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in righe:
        out.append(f"| {r['runtime']} | {r['config']} | {r['caso']} {r['titolo']} | {'⚡' if r['lampo'] else ''} | {r['checklist'] or ''} | "
                   f"{'promosso' if r['promosso'] else 'BOCCIATO'} | {r['ok']}/{r['runs']} | {r['chiamate_medie']:.1f} | {r['costo']:.3f} | "
                   f"{'; '.join(r['falliti'])} | {'; '.join(r['morbidi_ko'])} |")
    out.append("")
    for rt in sorted({r["runtime"] for r in righe}):
        for cfg in sorted({r["config"] for r in righe if r["runtime"] == rt}):
            sel = [r for r in righe if r["runtime"] == rt and r["config"] == cfg]
            lampo = [r for r in sel if r["lampo"]]
            out.append(f"- {rt} {cfg}: {sum(r['promosso'] for r in sel)}/{len(sel)} promossi"
                       + (f", ⚡ {sum(r['promosso'] for r in lampo)}/{len(lampo)}" if lampo else ""))
    out.append("- spesa: " + ", ".join(f"{k} {v:.3f} $" for k, v in spesa.items()) + f" · totale {sum(spesa.values()):.3f} $")
    for n in dict.fromkeys(note):
        out.append(f"- nota: {n}")
    if fermo:
        out.append(f"- **{fermo}** (nessun ritento: decide l'utente se e quando riprovare)")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.exit(main())
