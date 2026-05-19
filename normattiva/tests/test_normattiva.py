"""
Suite di test strutturali per la skill normattiva.

Testa la funzione build_urn_link() che implementa la logica URN-NIR
documentata in normattiva/normattiva/SKILL.md e references/lookup-extended.md.

Esecuzione:
    pip install pytest
    pytest test_normattiva.py -v
    pytest test_normattiva.py -v --tb=short   # output compatto
"""

import json
import re
from pathlib import Path


BASE_URL = "https://www.normattiva.it/uri-res/N2Ls?urn:nir:"

FORBIDDEN_ENCODINGS = ["%3A", "%3B", "%7E", "%21", "%3D"]


def build_urn_link(
    tipo: str,
    data_atto: str,
    numero: str | None,
    allegato: str | None = None,
    articolo: int | None = None,
    comma: int | None = None,
    lettera: str | None = None,
    art_suffix: str | None = None,
    data_storica: str | None = None,
) -> str:
    """
    Implementa la logica di composizione URN-NIR della skill normattiva.

    Pattern:
        stato:{tipo}:{data};{numero}[:{allegato}][~art{N}[suffix][-com{C}][-let{L}]][!vig=AAAA-MM-GG]

    Regole:
    - allegato (:N) va dopo il numero per i Regi Decreti storici (c.c., c.p.c., c.p., l.fall.)
    - articolo (art~N) va dopo l'allegato
    - art_suffix (bis, ter, septies…) va attaccato al numero articolo
    - comma (-comN) va dopo articolo
    - lettera (-letX) va dopo comma
    - !vig=data va sempre in coda, dopo tutto il resto
    - Costituzione: nessun numero nell'URN
    - Nessun URL-encoding di : ; ~ ! =
    """
    urn = f"stato:{tipo}:{data_atto}"

    if numero is not None:
        urn += f";{numero}"
        if allegato is not None:
            urn += f":{allegato}"

    if articolo is not None:
        fragment = f"~art{articolo}"
        if art_suffix:
            fragment += art_suffix
        if comma is not None:
            fragment += f"-com{comma}"
            if lettera is not None:
                fragment += f"-let{lettera}"
        urn += fragment

    if data_storica is not None:
        urn += f"!vig={data_storica}"

    return BASE_URL + urn


def load_cases():
    cases_path = Path(__file__).parent / "cases.json"
    with open(cases_path, encoding="utf-8") as f:
        return json.load(f)


CASES = load_cases()


def case_ids():
    return [f"{c['id']} – {c['desc']}" for c in CASES]


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", CASES, ids=case_ids())


def test_url_corretto(case):
    """Verifica che build_urn_link() produca esattamente l'url_atteso."""
    url = build_urn_link(
        tipo=case["tipo"],
        data_atto=case["data_atto"],
        numero=case["numero"],
        allegato=case["allegato"],
        articolo=case["articolo"],
        comma=case["comma"],
        lettera=case["lettera"],
        art_suffix=case["art_suffix"],
        data_storica=case["data_storica"],
    )
    assert url == case["url_atteso"], (
        f"\n  Atteso:  {case['url_atteso']}"
        f"\n  Ottenuto: {url}"
        f"\n  Note: {case['note']}"
    )


def test_formato_base(case):
    """Verifica che l'URL inizi sempre con il prefisso corretto."""
    url = case["url_atteso"]
    assert url.startswith("https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:"), (
        f"URL non inizia con il prefisso corretto: {url}"
    )


def test_nessun_url_encoding(case):
    """Verifica che i caratteri speciali URN non siano URL-encoded."""
    url = case["url_atteso"]
    for enc in FORBIDDEN_ENCODINGS:
        assert enc not in url, (
            f"URL-encoding vietato {enc!r} trovato in: {url}\n"
            f"Note: {case['note']}"
        )


def test_allegato_presente_per_codici_storici(case):
    """Verifica che i codici storici (c.c., c.p.c., c.p., l.fall.) abbiano l'allegato :N."""
    CODICI_CON_ALLEGATO = {
        "c.c.": "262:2",
        "c.p.c.": "1443:1",
        "c.p.": "1398:1",
        "l.fall.": "267:1",
    }
    norma = case["norma"]
    if norma in CODICI_CON_ALLEGATO:
        expected_fragment = CODICI_CON_ALLEGATO[norma]
        assert expected_fragment in case["url_atteso"], (
            f"Allegato mancante per {norma}: atteso '{expected_fragment}' in {case['url_atteso']}"
        )


def test_nessun_allegato_per_atti_moderni(case):
    """Verifica che gli atti moderni (D.Lgs., legge, D.P.R., c.p.p.) non abbiano allegato."""
    ATTI_SENZA_ALLEGATO = ["D.Lgs.", "legge", "D.P.R.", "c.p.p.", "Cost."]
    norma = case["norma"]
    if any(norma.startswith(p) or norma == p for p in ATTI_SENZA_ALLEGATO):
        url = case["url_atteso"]
        numero = case.get("numero")
        if numero:
            # Dopo il numero non deve esserci :N (allegato)
            # Pattern atteso: ;numero~ oppure ;numero! oppure ;numero (fine)
            pattern = rf";{re.escape(numero)}(?:[~!]|$)"
            assert re.search(pattern, url), (
                f"Allegato inatteso per atto moderno {norma}: {url}"
            )


def test_vig_presente_per_versioni_storiche(case):
    """Se data_storica è impostata, !vig= deve essere nell'URL."""
    if case.get("data_storica"):
        expected = f"!vig={case['data_storica']}"
        assert expected in case["url_atteso"], (
            f"Parametro !vig= mancante o data errata in: {case['url_atteso']}\n"
            f"Atteso: {expected}"
        )


def test_nessun_vig_per_norme_correnti(case):
    """Se data_storica è null, !vig= NON deve comparire nell'URL."""
    if case.get("no_vig") or case.get("data_storica") is None:
        assert "!vig=" not in case["url_atteso"], (
            f"!vig= inatteso in norma senza data storica: {case['url_atteso']}"
        )


def test_vig_in_coda(case):
    """Se presente, !vig= deve essere l'ultima parte dell'URL."""
    url = case["url_atteso"]
    if "!vig=" in url:
        vig_pos = url.index("!vig=")
        after_vig = url[vig_pos + len("!vig="):]
        # Dopo !vig= ci deve essere solo la data (AAAA-MM-GG), nient'altro
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", after_vig), (
            f"!vig= non è in coda o data malformata in: {url}"
        )


def test_articolo_nel_frammento(case):
    """Se articolo è specificato, ~artN deve essere presente nell'URL."""
    if case.get("articolo") is not None:
        art = case["articolo"]
        suffix = case.get("art_suffix") or ""
        expected_fragment = f"~art{art}{suffix}"
        assert expected_fragment in case["url_atteso"], (
            f"Frammento articolo '{expected_fragment}' mancante in: {case['url_atteso']}"
        )


def test_comma_nel_frammento(case):
    """Se comma è specificato, -comN deve essere presente nell'URL."""
    if case.get("comma") is not None:
        expected = f"-com{case['comma']}"
        assert expected in case["url_atteso"], (
            f"Frammento comma '{expected}' mancante in: {case['url_atteso']}"
        )


def test_lettera_nel_frammento(case):
    """Se lettera è specificata, -letX deve essere presente nell'URL."""
    if case.get("lettera") is not None:
        expected = f"-let{case['lettera']}"
        assert expected in case["url_atteso"], (
            f"Frammento lettera '{expected}' mancante in: {case['url_atteso']}"
        )


def test_tipo_atto_corretto(case):
    """Verifica che il tipo atto nell'URL corrisponda a quello nel dataset."""
    url = case["url_atteso"]
    tipo = case["tipo"]
    assert f"stato:{tipo}:" in url, (
        f"Tipo atto '{tipo}' non trovato in: {url}"
    )


def test_data_atto_corretta(case):
    """Verifica che la data di emanazione sia nel formato AAAA-MM-GG e nell'URL."""
    data = case["data_atto"]
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", data), f"Formato data errato: {data}"
    assert data in case["url_atteso"], f"Data atto '{data}' non trovata in: {case['url_atteso']}"


def test_costituzione_senza_numero(case):
    """La Costituzione non deve avere il numero nell'URN."""
    if case["norma"] == "Cost.":
        url = case["url_atteso"]
        # Dopo la data non deve esserci ;numero
        assert "1947-12-27;" not in url, (
            f"Numero inatteso nella Costituzione: {url}"
        )


def test_id_unici():
    """Verifica che tutti gli ID nel dataset siano unici."""
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids)), f"ID duplicati: {[x for x in ids if ids.count(x) > 1]}"


def test_totale_100_casi():
    """Verifica che il dataset contenga esattamente 100 casi."""
    assert len(CASES) == 100, f"Attesi 100 casi, trovati {len(CASES)}"


def test_categorie_presenti():
    """Verifica che tutte le 8 categorie siano rappresentate."""
    cats = {c["cat"] for c in CASES}
    expected = {"A", "B", "C", "D", "E", "F", "G", "H"}
    assert cats == expected, f"Categorie mancanti: {expected - cats}"
