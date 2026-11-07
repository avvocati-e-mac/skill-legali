#!/usr/bin/env python3
"""Test per la skill ricerca-giurisprudenza (offline, solo libreria standard).

Esecuzione:  python3 -B -m unittest discover -s ricerca-giurisprudenza/tests -v
"""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
SKILL_ROOT = TEST_DIR.parent
INNER = SKILL_ROOT / "ricerca-giurisprudenza"
SKILL_MD = INNER / "SKILL.md"
ARCHIVE = SKILL_ROOT / "ricerca-giurisprudenza.skill"
SCRIPTS = INNER / "scripts"


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise AssertionError("SKILL.md deve iniziare con frontmatter YAML.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("Frontmatter YAML non chiuso.")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line.strip() and ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def sorgenti() -> dict[str, bytes]:
    files = {}
    for p in sorted(INNER.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store":
            files[str(p.relative_to(SKILL_ROOT))] = p.read_bytes()
    return files


class TestStruttura(unittest.TestCase):
    def test_frontmatter(self):
        fm = frontmatter(SKILL_MD.read_text(encoding="utf-8"))
        self.assertEqual(fm.get("name"), "ricerca-giurisprudenza")
        desc = fm.get("description", "")
        self.assertTrue(desc, "description mancante")
        self.assertLessEqual(len(desc), 1024, "description oltre 1024 caratteri (Cowork la rifiuta)")

    def test_file_citati_esistono(self):
        testi = [SKILL_MD.read_text(encoding="utf-8")]
        testi += [p.read_text(encoding="utf-8") for p in (INNER / "references").rglob("*.md")]
        citati = set()
        for t in testi:
            citati |= set(re.findall(r"`((?:references|scripts)/[\w./-]+\.(?:md|py|sh))`", t))
        self.assertTrue(citati)
        for rel in sorted(citati):
            with self.subTest(file=rel):
                self.assertTrue((INNER / rel).is_file(), f"file citato ma assente: {rel}")

    def test_openai_yaml(self):
        testo = (INNER / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$ricerca-giurisprudenza", testo)
        self.assertIn("allow_implicit_invocation: true", testo)

    def test_ambienti_coprono_tre_runtime(self):
        testo = (INNER / "references" / "ambienti.md").read_text(encoding="utf-8")
        for parola in ("Claude_Browser", "claude-in-chrome", "Codex", "robots.txt"):
            self.assertIn(parola, testo)

    def test_script_compilano(self):
        with tempfile.TemporaryDirectory() as tmp:
            for p in SCRIPTS.glob("*.py"):
                with self.subTest(script=p.name):
                    py_compile.compile(str(p), cfile=str(Path(tmp) / (p.name + "c")), doraise=True)

    def test_archivio_allineato(self):
        self.assertTrue(ARCHIVE.is_file(), "manca il file .skill")
        with zipfile.ZipFile(ARCHIVE) as z:
            nell_archivio = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
        self.assertFalse([n for n in nell_archivio if "__pycache__" in n or ".DS_Store" in n or "__MACOSX" in n])
        self.assertEqual(nell_archivio, sorgenti(), "il .skill non corrisponde ai sorgenti: rigeneralo")


SCHEDA = {
    "id": "123",
    "estremi": {
        "ufficio": "Tribunale di Prova", "sezione": "Sezione Prima", "grado": "primo grado",
        "tipo": "sentenza", "data_decisione": "2025-03-14", "data_deposito": "2025-03-20",
        "numero": "1/2025", "rg": "2/2024", "giudice": "giudice monocratico",
    },
    "url_scheda": "non indicato", "url_file": "non indicato",
    "fonte_testo": "provvedimento", "testo_letto": "integrale", "chi": "giudice",
    "come_emerge": "rilievo d'ufficio", "fatti": "fatti sintetici di prova",
    "parte_rilevante": "il giudice rileva il tema", "norme_applicate": ["art. 96 c.p.c."],
    "esito": "rigetta", "definitivo": "non indicato", "motivo_reale_dell_esito": "infondatezza",
    "tema_causa_dell_esito": "no", "ruolo_del_tema": "concorrente",
    "conseguenze_legate_al_tema": ["spese"], "importi": [],
    "citazioni": [{"testo": "il ricorso è infondato e va rigettato", "pagina": "2"}],
    "precedenti_citati": [], "dubbi": [],
}


class TestScriptSuFixture(unittest.TestCase):
    """Esegue controlli.py e conteggi.py su una cartella di lavoro sintetica."""

    def test_controlli_e_conteggi(self):
        with tempfile.TemporaryDirectory() as tmp:
            lav = Path(tmp) / "lavoro"
            (lav / "schede").mkdir(parents=True)
            (lav / "testi").mkdir()
            (Path(tmp) / "pdf").mkdir()
            (lav / "elenco.csv").write_text(
                "id,ufficio,sezione,grado,tipo,data,numero,rg,url_scheda,url_file,pertinenza,motivo,da_leggere,formato\n"
                "123,Tribunale di Prova,Prima,primo grado,sentenza,2025-03-20,1/2025,2/2024,-,-,alta,prova,si,pdf\n",
                encoding="utf-8")
            (lav / "scartati.csv").write_text("id,titolo,motivo\n", encoding="utf-8")
            (lav / "ricognizione.md").write_text("Ambiente e browser: test\n", encoding="utf-8")
            (lav / "testi" / "123.txt").write_text(
                "[pag. 2]\nIn conclusione il ricorso è infondato e va rigettato.\n", encoding="utf-8")
            (lav / "schede" / "123.json").write_text(json.dumps(SCHEDA, ensure_ascii=False), encoding="utf-8")

            r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "controlli.py"), str(lav)],
                               capture_output=True, text=True)
            rapporto = (lav / "controlli.txt").read_text(encoding="utf-8")
            self.assertEqual(r.returncode, 0, rapporto + r.stdout + r.stderr)

            r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "conteggi.py"), str(lav)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("123", (lav / "tabelle.md").read_text(encoding="utf-8"))

    def test_citazione_inventata_segnalata(self):
        with tempfile.TemporaryDirectory() as tmp:
            lav = Path(tmp) / "lavoro"
            (lav / "schede").mkdir(parents=True)
            (lav / "testi").mkdir()
            (lav / "elenco.csv").write_text(
                "id,ufficio,sezione,grado,tipo,data,numero,rg,url_scheda,url_file,pertinenza,motivo,da_leggere,formato\n"
                "123,T,P,primo grado,sentenza,2025-03-20,1/2025,2/2024,-,-,alta,prova,si,pdf\n", encoding="utf-8")
            (lav / "scartati.csv").write_text("id,titolo,motivo\n", encoding="utf-8")
            (lav / "ricognizione.md").write_text("x\n", encoding="utf-8")
            (lav / "testi" / "123.txt").write_text("[pag. 2]\nTesto che non contiene la frase.\n", encoding="utf-8")
            scheda = dict(SCHEDA, citazioni=[{"testo": "frase mai scritta dal giudice in alcun punto", "pagina": "2"}])
            (lav / "schede" / "123.json").write_text(json.dumps(scheda, ensure_ascii=False), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "controlli.py"), str(lav)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, "una citazione assente dal testo deve far fallire i controlli")


if __name__ == "__main__":
    unittest.main()
