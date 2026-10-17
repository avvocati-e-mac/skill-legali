"""
Livello A — controlli strutturali della skill BuddaLaw (offline, gratuito, gate).

Esecuzione (dalla radice del repository):

    pytest buddalaw/tests/test_struttura.py

Perché non è una tautologia
---------------------------
Il riferimento non è scritto a mano accanto alla skill: è
`fixtures/tool_schema.json`, estratto dal server reale con
`tools/estrai_schema.py`. Gli esempi di chiamata della skill vengono confrontati
con quello schema (nomi dei tool, parametri, tipi, valori ammessi), non con una
copia di se stessi. Quando il server cambia, il livello C se ne accorge e la
fixture viene rigenerata: da quel momento questi test segnalano gli esempi
rimasti indietro.

Il confronto con l'archivio `buddalaw.skill` è rosso finché l'archivio non
viene rigenerato dopo una modifica ai sorgenti: è voluto.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
RADICE = TESTS.parent                      # buddalaw/
SKILL_DIR = RADICE / "buddalaw"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"
ARCHIVIO = RADICE / "buddalaw.skill"
CHECKLIST = TESTS / "CHECKLIST.md"
SCHEMA = json.loads((TESTS / "fixtures" / "tool_schema.json").read_text(encoding="utf-8"))
TOOLS = {t["name"]: t for t in SCHEMA["tools"]}

ESCLUSI_ARCHIVIO = {".DS_Store", "__pycache__", "__MACOSX"}


# ---------------------------------------------------------------------------
# Lettore YAML minimo (PyYAML se c'è, altrimenti un sottoinsieme rigoroso)
# ---------------------------------------------------------------------------

def _scalare(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        corpo = v[1:-1]
        return corpo.replace('\\"', '"') if v[0] == '"' else corpo.replace("''", "'")
    if v in ("true", "false"):
        return v == "true"
    if v in ("null", "~", ""):
        return None
    return v


def _yaml_minimo(testo: str):
    """Mappe annidate, liste, scalari, blocchi `>` e `|`. Rifiuta il resto."""
    righe = [r.rstrip("\n") for r in testo.splitlines()]

    def rientro(r: str) -> int:
        return len(r) - len(r.lstrip(" "))

    def significativa(r: str) -> bool:
        s = r.strip()
        return bool(s) and not s.startswith("#")

    def blocco(i: int, ind: int, stile: str):
        pezzi = []
        while i < len(righe) and (not righe[i].strip() or rientro(righe[i]) > ind):
            pezzi.append(righe[i].strip())
            i += 1
        if stile.startswith(">"):
            return " ".join(p for p in pezzi if p), i
        return "\n".join(pezzi).strip("\n"), i

    def nodo(i: int, ind: int):
        while i < len(righe) and not significativa(righe[i]):
            i += 1
        if i >= len(righe):
            return None, i
        if righe[i].strip().startswith("- "):
            return lista(i, rientro(righe[i]))
        return mappa(i, rientro(righe[i]))

    def valore_dopo_chiave(resto: str, i: int, ind: int):
        if resto in (">", "|", ">-", "|-"):
            return blocco(i + 1, ind, resto)
        if resto == "":
            return nodo(i + 1, ind)
        return _scalare(resto), i + 1

    def mappa(i: int, ind: int):
        out = {}
        while i < len(righe):
            r = righe[i]
            if not significativa(r):
                i += 1
                continue
            if rientro(r) < ind:
                break
            if rientro(r) > ind:
                raise ValueError(f"rientro inatteso alla riga {i + 1}: {r!r}")
            m = re.match(r"^\s*([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$", r)
            if not m:
                raise ValueError(f"riga YAML non valida {i + 1}: {r!r}")
            chiave, resto = m.group(1), (m.group(2) or "").strip()
            if chiave in out:
                raise ValueError(f"chiave duplicata {chiave!r}")
            out[chiave], i = valore_dopo_chiave(resto, i, ind)
        return out, i

    def lista(i: int, ind: int):
        out = []
        while i < len(righe):
            r = righe[i]
            if not significativa(r):
                i += 1
                continue
            if rientro(r) < ind or not r.strip().startswith("- "):
                break
            resto = r.strip()[2:].strip()
            m = re.match(r"^([A-Za-z_][\w-]*)\s*:(?:\s+(.*))?$", resto)
            if m and not resto.startswith(("\"", "'")):
                # elemento mappa: «- chiave: valore» più eventuali righe sotto
                righe[i] = " " * (ind + 2) + resto
                v, i = mappa(i, ind + 2)
                out.append(v)
            else:
                out.append(_scalare(resto))
                i += 1
        return out, i

    valore, _ = nodo(0, 0)
    return valore


def carica_yaml(testo: str):
    try:
        import yaml  # type: ignore
    except ImportError:
        return _yaml_minimo(testo)
    return yaml.safe_load(testo)


def frontmatter_e_corpo() -> tuple[dict, str]:
    testo = SKILL_MD.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", testo, re.DOTALL)
    assert m, "SKILL.md deve iniziare con un frontmatter YAML tra due righe ---"
    return carica_yaml(m.group(1)), m.group(2)


FM, CORPO = frontmatter_e_corpo()


def file_skill_md() -> list[Path]:
    return [SKILL_MD, *sorted(REFERENCES.glob("*.md"))]


# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def test_frontmatter_campi_obbligatori():
    assert isinstance(FM, dict), "il frontmatter non è una mappa YAML"
    assert FM.get("name") == "buddalaw"
    versione = FM.get("version")
    assert isinstance(versione, str) and re.fullmatch(r"\d+\.\d+(\.\d+)?", versione), (
        f"version deve essere una stringa tipo \"9.0\", trovato {versione!r}")


def test_description_appiattita_entro_1024_caratteri():
    """Cowork rifiuta l'installazione oltre 1024 caratteri (vedi CLAUDE.md)."""
    d = FM.get("description")
    assert isinstance(d, str) and d.strip(), "description mancante"
    piatta = " ".join(d.split())
    assert len(piatta) <= 1024, f"description di {len(piatta)} caratteri: massimo 1024"


def test_changelog_parte_dalla_versione_corrente():
    log = FM.get("changelog")
    if log is None:
        pytest.skip("nessun changelog nel frontmatter")
    assert isinstance(log, list) and log, "changelog deve essere una lista"
    assert str(log[0]).startswith(FM["version"] + " "), (
        f"la prima voce del changelog ({str(log[0])[:30]!r}) non è la versione {FM['version']}")


def test_versione_citata_nel_testo_coincide():
    """L'avviso di aggiornamento dice «Questa skill (vX)»: X deve essere la versione."""
    citate = set(re.findall(r"skill \(v(\d+\.\d+(?:\.\d+)?)\)", CORPO))
    assert citate, "nessuna «skill (vX)» nel testo dell'avviso di aggiornamento"
    assert citate == {FM["version"]}, f"versioni nel testo {citate} ≠ frontmatter {FM['version']}"


# ---------------------------------------------------------------------------
# Link e file references
# ---------------------------------------------------------------------------

_LINK = re.compile(r"\]\(([^)\s]+)\)")


def _slug(titolo: str) -> str:
    """Ancora come la genera GitHub: minuscole, via la punteggiatura, spazi → «-»."""
    t = titolo.strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def _ancore(p: Path) -> set[str]:
    return {_slug(m) for m in re.findall(r"^#+\s+(.*)$", p.read_text(encoding="utf-8"), re.M)}


@pytest.mark.parametrize("sorgente", file_skill_md(), ids=lambda p: p.name)
def test_link_locali_esistono(sorgente: Path):
    rotti = []
    for link in _LINK.findall(sorgente.read_text(encoding="utf-8")):
        if re.match(r"^[a-z]+:", link):          # http:, https:, mailto:
            continue
        if not (link.startswith("#") or "/" in link or link.endswith(".md")):
            continue                             # segnaposto dei modelli: (public_url), (url)
        percorso, _, ancora = link.partition("#")
        bersaglio = (sorgente.parent / percorso).resolve() if percorso else sorgente
        if not bersaglio.exists():
            rotti.append(f"{link} (file assente)")
        elif ancora and bersaglio.suffix == ".md" and ancora not in _ancore(bersaglio):
            rotti.append(f"{link} (ancora assente)")
    assert not rotti, f"link rotti in {sorgente.name}: {rotti}"


def test_nessun_reference_orfano():
    """Ogni file di references/ deve essere raggiungibile da SKILL.md."""
    linkati = {Path(l.partition("#")[0]).name for l in _LINK.findall(SKILL_MD.read_text(encoding="utf-8"))
               if l.startswith("references/")}
    presenti = {p.name for p in REFERENCES.iterdir() if p.is_file() and p.name not in ESCLUSI_ARCHIVIO}
    assert linkati, "SKILL.md non linka nessun file references/"
    orfani = presenti - linkati
    assert not orfani, f"file references/ non linkati da SKILL.md: {sorted(orfani)}"


# ---------------------------------------------------------------------------
# Archivio .skill
# ---------------------------------------------------------------------------

def _escluso(parti) -> bool:
    return any(p in ESCLUSI_ARCHIVIO or p.endswith(".pyc") for p in parti)


def test_archivio_skill_uguale_ai_sorgenti():
    """Il .skill installato da Claude Desktop/Cowork deve contenere i sorgenti attuali.

    Rosso dopo ogni modifica ai sorgenti finché non si rigenera l'archivio:
        cd buddalaw && rm buddalaw.skill && zip -r buddalaw.skill buddalaw/ -x '*.DS_Store'
    """
    assert ARCHIVIO.exists(), f"archivio mancante: {ARCHIVIO}"
    sorgenti = {
        "buddalaw/" + p.relative_to(SKILL_DIR).as_posix(): p.read_bytes()
        for p in SKILL_DIR.rglob("*")
        if p.is_file() and not _escluso(p.relative_to(SKILL_DIR).parts)
    }
    with zipfile.ZipFile(ARCHIVIO) as z:
        archivio = {
            n: z.read(n) for n in z.namelist()
            if not n.endswith("/") and not _escluso(n.split("/"))
        }
    mancanti = sorted(set(sorgenti) - set(archivio))
    in_piu = sorted(set(archivio) - set(sorgenti))
    diversi = sorted(n for n in set(sorgenti) & set(archivio) if sorgenti[n] != archivio[n])
    assert not (mancanti or in_piu or diversi), (
        "buddalaw.skill non corrisponde ai sorgenti: rigeneralo.\n"
        f"  mancano nell'archivio: {mancanti}\n"
        f"  in più nell'archivio: {in_piu}\n"
        f"  contenuto diverso: {diversi}")


# ---------------------------------------------------------------------------
# agents/openai.yaml
# ---------------------------------------------------------------------------

def test_openai_yaml_leggibile():
    dati = carica_yaml(OPENAI_YAML.read_text(encoding="utf-8"))
    assert isinstance(dati, dict), "openai.yaml non è una mappa"
    interfaccia = dati.get("interface")
    assert isinstance(interfaccia, dict), "manca la sezione interface"
    for campo in ("display_name", "short_description"):
        v = interfaccia.get(campo)
        assert isinstance(v, str) and v.strip(), f"interface.{campo} mancante o vuoto"
    prompt = interfaccia.get("default_prompt")
    if prompt is not None:
        assert "$buddalaw" in prompt, "default_prompt deve richiamare $buddalaw"


# ---------------------------------------------------------------------------
# Esempi di chiamata contro lo schema reale
# ---------------------------------------------------------------------------

_TIPI = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
    "null": lambda v: v is None,
}


def _tipi_ammessi(spec: dict) -> set[str]:
    if "type" in spec:
        t = spec["type"]
        return set(t) if isinstance(t, list) else {t}
    return {a.get("type") for a in spec.get("anyOf", []) if a.get("type")}


def enum_di(tool: str, param: str) -> list[str] | None:
    """Valori ammessi: dal campo enum o dalla frase «Valori: a, b, c.» della description."""
    spec = TOOLS[tool]["parameters"]["properties"][param]
    if spec.get("enum"):
        return list(spec["enum"])
    m = re.search(r"Valori:\s*(.+?)\.(?:\s|$)", spec.get("description") or "")
    return [v.strip() for v in m.group(1).split(",")] if m else None


def _limiti(spec: dict) -> tuple[float, float] | None:
    m = re.search(r"\((\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\)", spec.get("description") or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def errori_chiamata(tool: str, argomenti: dict) -> list[str]:
    if tool not in TOOLS:
        return [f"tool inesistente: {tool!r}"]
    schema = TOOLS[tool]["parameters"]
    props = schema.get("properties", {})
    errori = []
    for p in schema.get("required", []):
        if p not in argomenti:
            errori.append(f"{tool}: manca il parametro obbligatorio {p!r}")
    for nome, valore in argomenti.items():
        if nome not in props:
            errori.append(f"{tool}: parametro inesistente {nome!r} (ammessi: {sorted(props)})")
            continue
        spec = props[nome]
        ammessi = _tipi_ammessi(spec)
        if ammessi and not any(_TIPI[t](valore) for t in ammessi if t in _TIPI):
            errori.append(f"{tool}.{nome}={valore!r}: tipo {type(valore).__name__}, ammessi {sorted(ammessi)}")
        valori = enum_di(tool, nome)
        if valori and isinstance(valore, str) and valore not in valori:
            errori.append(f"{tool}.{nome}={valore!r}: non è fra {valori}")
        lim = _limiti(spec)
        if lim and _TIPI["number"](valore) and not (lim[0] <= valore <= lim[1]):
            errori.append(f"{tool}.{nome}={valore!r}: fuori dall'intervallo {lim}")
        if isinstance(valore, list):
            for a in spec.get("anyOf", []) + [spec]:
                tipo_el = (a.get("items") or {}).get("type")
                if tipo_el and not all(_TIPI[tipo_el](x) for x in valore):
                    errori.append(f"{tool}.{nome}: elementi non di tipo {tipo_el}")
    return errori


def blocchi_json() -> list[tuple[str, int, str]]:
    out = []
    for p in file_skill_md():
        testo = p.read_text(encoding="utf-8")
        for m in re.finditer(r"```json\n(.*?)```", testo, re.DOTALL):
            riga = testo[: m.start()].count("\n") + 1
            out.append((f"{p.name}:{riga}", riga, m.group(1)))
    return out


BLOCCHI = blocchi_json()


def chiamate_negli_esempi() -> list[tuple[str, str, dict]]:
    """Blocchi ```json {"tool","arguments"} e, nella tabella di get_law_article
    di query-examples.md, gli argomenti scritti in linea."""
    out = []
    for dove, _, testo in BLOCCHI:
        dati = json.loads(testo)
        if isinstance(dati, dict) and "tool" in dati:
            out.append((dove, dati.get("tool"), dati))
    qe = REFERENCES / "query-examples.md"
    if qe.exists():
        sezione = re.search(r"^## Lettura di un articolo.*?(?=^## |\Z)", qe.read_text(encoding="utf-8"),
                            re.M | re.DOTALL)
        if sezione:
            for frammento in re.findall(r"^\|.*?`(\{.*?\})`\s*\|", sezione.group(0), re.M):
                out.append(("query-examples.md (tabella get_law_article)", "get_law_article",
                            {"tool": "get_law_article", "arguments": json.loads(frammento)}))
    return out


CHIAMATE = chiamate_negli_esempi()


@pytest.mark.parametrize("dove,riga,testo", BLOCCHI, ids=[b[0] for b in BLOCCHI])
def test_blocchi_json_validi(dove, riga, testo):
    json.loads(testo)


def test_ci_sono_esempi_di_chiamata():
    """Guardia contro un passaggio a vuoto: senza esempi i test sotto non provano nulla."""
    usati = {t for _, t, _ in CHIAMATE}
    assert len(CHIAMATE) >= 10, f"solo {len(CHIAMATE)} esempi di chiamata trovati"
    for attesi in ("get_judgement", "get_law_article", "search_case_law", "search_similar_cases", "list_uffici"):
        assert attesi in usati, f"nessun esempio di {attesi}"


@pytest.mark.parametrize("dove,tool,dati", CHIAMATE, ids=[f"{c[0]}-{c[1]}" for c in CHIAMATE])
def test_esempio_di_chiamata_conforme_allo_schema(dove, tool, dati):
    """T53 T70 — tool esistente, solo parametri dello schema, tipi e valori ammessi."""
    assert set(dati) == {"tool", "arguments"}, f"{dove}: chiavi {sorted(dati)}, attese tool e arguments"
    assert isinstance(dati["arguments"], dict)
    errori = errori_chiamata(tool, dati["arguments"])
    assert not errori, f"{dove}: " + "; ".join(errori)


_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_IT = re.compile(r"^\d{2}/\d{2}/\d{4}$")
DATA_ISO = {"civile", "penale", "privacy"}
CON_CODICEUFFICIO = {"merito", "amministrativo", "tributari"}


@pytest.mark.parametrize("dove,tool,dati", [c for c in CHIAMATE if c[1] == "search_case_law"],
                         ids=lambda x: str(x)[:40])
def test_regole_del_sondaggio_negli_esempi_di_ricerca(dove, tool, dati):
    """T05 T35 T52 — data esatta nel formato della banca dati, codiceufficio
    solo dove funziona, numero di Cassazione a 5 cifre."""
    a = dati["arguments"]
    cat = a.get("search_category")
    if a.get("data_deposito"):
        formato = _ISO if cat in DATA_ISO else _IT
        assert formato.match(a["data_deposito"]), f"{dove}: data {a['data_deposito']!r} nel formato sbagliato per {cat}"
    if a.get("codiceufficio"):
        assert cat in CON_CODICEUFFICIO, f"{dove}: codiceufficio con {cat} azzera i risultati"
    if a.get("numero") and cat in ("civile", "penale"):
        assert re.fullmatch(r"\d{5}", str(a["numero"])), f"{dove}: numero di Cassazione a 5 cifre con zeri"


def test_inventario_coincide_con_lo_schema():
    """T60 — l'elenco del «Controllo di aggiornamento» è quello del server reale."""
    trovati = [json.loads(t) for d, _, t in BLOCCHI if d.startswith("SKILL.md")
               and "inventario_tool_buddalaw" in t]
    assert len(trovati) == 1, f"attesi 1 blocco inventario in SKILL.md, trovati {len(trovati)}"
    inv = trovati[0]
    nomi = inv["inventario_tool_buddalaw"]
    assert len(nomi) == len(set(nomi)), "nomi duplicati nell'inventario"
    attesi = set(TOOLS)
    assert set(nomi) == attesi, (
        f"inventario ≠ fixture. In più: {sorted(set(nomi) - attesi)}; "
        f"mancano: {sorted(attesi - set(nomi))}")
    assert inv.get("versione_skill") == FM["version"], (
        f"versione_skill {inv.get('versione_skill')!r} ≠ version {FM['version']!r}")


# ---------------------------------------------------------------------------
# Tabelle di instradamento
# ---------------------------------------------------------------------------

def tabelle(testo: str) -> list[list[list[str]]]:
    out, corrente = [], []
    for riga in testo.splitlines():
        if riga.startswith("|"):
            celle = [c.strip() for c in riga.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in celle):
                corrente.append(celle)
        elif corrente:
            out.append(corrente)
            corrente = []
    if corrente:
        out.append(corrente)
    return out


# intestazione di colonna → (tool, parametro)
COLONNE = [
    (re.compile(r"`search_category`"), ("search_case_law", "search_category")),
    (re.compile(r"`dominio`.*get_judgement"), ("get_judgement", "dominio")),
    (re.compile(r"`dominio`.*list_uffici"), ("list_uffici", "dominio")),
    (re.compile(r"`domain`"), ("search_articles", "domain")),
]


def valori_di_colonna() -> list[tuple[str, str, str, str]]:
    """(file, tool, parametro, valore) per ogni valore citato in quelle colonne."""
    out = []
    for p in file_skill_md():
        for tab in tabelle(p.read_text(encoding="utf-8")):
            intest = tab[0]
            for j, cella in enumerate(intest):
                for regex, (tool, param) in COLONNE:
                    if regex.search(cella):
                        for r in tab[1:]:
                            if j < len(r):
                                for v in re.findall(r"`([^`]+)`", r[j]):
                                    out.append((p.name, tool, param, v))
                        break
    return out


VALORI_TABELLE = valori_di_colonna()


def test_valori_delle_tabelle_ammessi_dallo_schema():
    """T63 — nessuna tabella insegna un valore che il server rifiuta (es. dominio «tributari»)."""
    assert len(VALORI_TABELLE) >= 20, f"solo {len(VALORI_TABELLE)} valori letti dalle tabelle"
    sbagliati = [f"{f}: {t}.{p}={v!r}" for f, t, p, v in VALORI_TABELLE
                 if v not in (enum_di(t, p) or [v])]
    assert not sbagliati, "valori non ammessi dallo schema: " + "; ".join(sbagliati)


def test_instradamento_copre_ogni_banca_dati():
    """Ogni valore di search_category ha una riga nella tabella di instradamento di SKILL.md."""
    in_skill = {v for f, t, p, v in VALORI_TABELLE if f == "SKILL.md" and p == "search_category"}
    mancanti = set(enum_di("search_case_law", "search_category")) - in_skill
    assert not mancanti, f"banche dati senza riga di instradamento: {sorted(mancanti)}"


# ---------------------------------------------------------------------------
# Regressioni vietate (regole della v8.x smentite dal sondaggio)
# ---------------------------------------------------------------------------

def test_nessun_mandatory():
    assert "MANDATORY" not in SKILL_MD.read_text(encoding="utf-8")


def test_nessun_ufficio_in_search_case_law():
    """T57 — il parametro `ufficio` non esiste in search_case_law: si usa codiceufficio."""
    errati = [d for d, t, dati in CHIAMATE if t == "search_case_law" and "ufficio" in dati["arguments"]]
    assert not errati, f"esempi di search_case_law con ufficio: {errati}"
    for p in file_skill_md():
        testo = p.read_text(encoding="utf-8")
        assert not re.search(r"search_case_law\([^)]*(?<![a-z])ufficio\s*=", testo), (
            f"{p.name}: search_case_law(... ufficio=...)")


def test_nessuna_regola_http_400():
    """T45 — la vecchia regola «ante-2019 → HTTP 400» è superata da not_found."""
    for p in file_skill_md():
        corpo = CORPO if p == SKILL_MD else p.read_text(encoding="utf-8")
        assert not re.search(r"HTTP\s*400", corpo), f"{p.name}: regola «HTTP 400»"
        assert "ante-2019" not in corpo, f"{p.name}: regola «ante-2019»"


def test_guid_solo_per_i_tributari():
    """T27 — «GUID» non è l'identificatore generale: idatto ha una forma per banca dati."""
    assert "GUID" not in CORPO, "SKILL.md parla di GUID: la forma di idatto dipende dalla banca dati"
    for p in sorted(REFERENCES.glob("*.md")):
        for riga in p.read_text(encoding="utf-8").splitlines():
            if "GUID" in riga:
                assert "tributari" in riga, f"{p.name}: GUID fuori dalla riga dei tributari: {riga[:80]!r}"


# ---------------------------------------------------------------------------
# CHECKLIST.md
# ---------------------------------------------------------------------------

def righe_checklist() -> tuple[list[str], list[list[str]]]:
    testo = CHECKLIST.read_text(encoding="utf-8")
    righe, intest = [], None
    for tab in tabelle(testo):
        if tab and tab[0] and tab[0][0].upper() in ("ID", "#"):
            intest = intest or tab[0]
            righe.extend(tab[1:])
    assert intest, "CHECKLIST.md: nessuna tabella di casi con colonna ID"
    return intest, righe


def test_checklist_versione():
    prima = CHECKLIST.read_text(encoding="utf-8").splitlines()[0]
    assert f"v{FM['version']}" in prima, f"il titolo di CHECKLIST.md non cita v{FM['version']}: {prima!r}"


def test_checklist_id_univoci_e_colonna_automatizzato():
    intest, righe = righe_checklist()
    col = [i for i, c in enumerate(intest) if "automatizzato in" in c.lower()]
    assert col, f"manca la colonna «Automatizzato in»: {intest}"
    ids, errori = [], []
    for r in righe:
        m = re.match(r"^(T\d{2,3})\b", r[0])
        if not m:
            errori.append(f"id non valido: {r[0]!r}")
            continue
        ids.append(m.group(1))
        v = r[col[0]] if col[0] < len(r) else ""
        if not re.fullmatch(r"(A|B|C|manuale)(\s*,\s*(A|B|C|manuale))*", v):
            errori.append(f"{m.group(1)}: «automatizzato in» = {v!r} (ammessi A, B, C, manuale)")
    doppi = sorted({i for i in ids if ids.count(i) > 1})
    assert not doppi, f"id ripetuti: {doppi}"
    assert len(ids) >= 60, f"solo {len(ids)} casi nella checklist"
    assert not errori, "; ".join(errori)


@pytest.mark.parametrize("livello,file", [("A", "test_struttura.py"), ("C", "test_mcp_live.py")])
def test_casi_dichiarati_automatici_esistono(livello, file):
    """Un caso segnato A o C deve essere citato (per id) nel file di test di quel livello."""
    intest, righe = righe_checklist()
    col = next(i for i, c in enumerate(intest) if "automatizzato in" in c.lower())
    dichiarati = [re.match(r"T\d+", r[0]).group(0) for r in righe
                  if col < len(r) and livello in re.split(r"\s*,\s*", r[col])]
    sorgente = (TESTS / file).read_text(encoding="utf-8")
    assenti = [i for i in dichiarati if not re.search(rf"\b{i}\b", sorgente)]
    assert not assenti, f"casi segnati {livello} ma non citati in {file}: {assenti}"


def test_casi_b_hanno_un_caso_e2e():
    intest, righe = righe_checklist()
    e2e = TESTS / "e2e"
    if not e2e.exists():
        pytest.skip("livello B non ancora presente (cartella e2e/)")
    col = next(i for i, c in enumerate(intest) if "automatizzato in" in c.lower())
    dichiarati = [re.match(r"T\d+", r[0]).group(0) for r in righe
                  if col < len(r) and "B" in re.split(r"\s*,\s*", r[col])]
    testo = "".join(p.read_text(encoding="utf-8", errors="ignore")
                    for p in e2e.rglob("*") if p.is_file() and p.suffix in (".py", ".json", ".yaml", ".md")
                    and "results" not in p.parts)
    if not re.search(r"\bT\d{2,3}\b", testo):
        pytest.skip("e2e/ non contiene ancora casi con ID della checklist")
    assenti = [i for i in dichiarati if not re.search(rf"\b{i}\b", testo)]
    assert not assenti, f"casi segnati B ma assenti da e2e/: {assenti}"
