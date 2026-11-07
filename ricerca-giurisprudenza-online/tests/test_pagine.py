#!/usr/bin/env python3
"""Test di pagine.py e della riga di riepilogo di conteggi.py (offline, solo libreria standard).

Esecuzione:  python3 -B -m unittest discover -s ricerca-giurisprudenza-online/tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parent / "ricerca-giurisprudenza-online" / "scripts"
FIXTURE = TEST_DIR / "fixtures" / "provvedimento-minimo.pdf"

CITAZIONI = [
    "il principio di diritto va affermato nei termini seguenti",   # a cavallo pp. 2-3
    "Il ricorso è fondato per le seguenti ragioni",                # sillabazione, p. 1
    "l’appello è inammissibile",                                   # apostrofo tipografico, p. 3
    "frase che nel provvedimento non compare affatto",             # non ritrovata
    "Spese compensate tra le parti",                               # pp. 1 e 3: ambigua
]


def prepara(tmp, citazioni=CITAZIONI, copia_pdf=True):
    lav = Path(tmp) / "lavoro"
    (lav / "schede").mkdir(parents=True)
    (Path(tmp) / "pdf").mkdir()
    if copia_pdf:
        shutil.copy(FIXTURE, Path(tmp) / "pdf" / "2025-03-20_tribunale_1-2025_abc-1.pdf")
    scheda = {"id": "abc-1", "citazioni": [{"testo": t, "pagina": "9"} for t in citazioni]}
    (lav / "schede" / "abc-1.json").write_text(json.dumps(scheda, ensure_ascii=False), encoding="utf-8")
    return lav


def esegui(script, lav, *extra, home=None):
    env = dict(os.environ)
    if home:
        env["HOME"] = str(home)
        env.pop("CODEX_HOME", None)
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / script), str(lav), *extra],
                          capture_output=True, text=True, env=env)


def righe(lav):
    return [json.loads(x) for x in (lav / "pagine.jsonl").read_text(encoding="utf-8").splitlines()]


def finta_skill_b(cartella, corpo):
    (cartella / "scripts").mkdir(parents=True)
    (cartella / "scripts" / "check_pdf_quote.py").write_text(corpo, encoding="utf-8")
    return cartella


@unittest.skipUnless(shutil.which("pdftotext"), "pdftotext non disponibile")
class TestPaginePdftotext(unittest.TestCase):
    def test_stati_e_pagine(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp)
            r = esegui("pagine.py", lav, home=home)  # skill B assente
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rr = righe(lav)
            self.assertEqual([x["i"] for x in rr], [0, 1, 2, 3, 4])
            self.assertTrue(all(x["metodo"] == "pdftotext" for x in rr))
            self.assertEqual((rr[0]["stato"], rr[0]["pagina_fisica"]), ("trovata", 2))
            self.assertIn("cavallo", rr[0]["note"])
            self.assertEqual((rr[1]["stato"], rr[1]["pagina_fisica"]), ("trovata", 1))
            self.assertEqual((rr[2]["stato"], rr[2]["pagina_fisica"]), ("trovata", 3))
            self.assertEqual((rr[3]["stato"], rr[3]["pagina_fisica"]), ("non_ritrovata_nel_pdf", None))
            self.assertEqual((rr[4]["stato"], rr[4]["pagina_fisica"]), ("ambigua", None))
            self.assertEqual(len(rr[0]["sha256_pdf"]), 64)

    def test_riscrittura_senza_duplicati(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp)
            esegui("pagine.py", lav, home=home)
            esegui("pagine.py", lav, home=home)
            rr = righe(lav)
            self.assertEqual(len(rr), len(CITAZIONI))
            self.assertEqual(len({(x["id"], x["i"]) for x in rr}), len(CITAZIONI))

    def test_html_senza_righe(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp, copia_pdf=False)
            (Path(tmp) / "pdf" / "2025-03-20_tribunale_1-2025_abc-1.html").write_text("<p>x</p>")
            self.assertEqual(esegui("pagine.py", lav, home=home).returncode, 0)
            self.assertEqual(righe(lav), [])

    def test_b_senza_pypdfium2_ricade_su_pdftotext(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp)
            b = finta_skill_b(Path(home) / "b", "import sys\n"
                "print('{\"status\": \"check_unavailable\", \"error\": \"No module named pypdfium2\"}')\n"
                "sys.exit(2)\n")
            esegui("pagine.py", lav, "--skill-docling", str(b), home=home)
            rr = righe(lav)
            self.assertTrue(all(x["metodo"] == "pdftotext" for x in rr))
            self.assertEqual(rr[0]["pagina_fisica"], 2)

    def test_b_disponibile_ha_la_precedenza(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp, citazioni=["frase qualsiasi"])
            b = finta_skill_b(Path(home) / "b", "import json\n"
                "print(json.dumps({'status': 'text_match_found', 'physical_page_count': 3,\n"
                "                  'selected_physical_pages': [3], 'citation_verified': False}))\n")
            esegui("pagine.py", lav, "--skill-docling", str(b), home=home)
            x = righe(lav)[0]
            self.assertEqual((x["metodo"], x["stato"], x["pagina_fisica"]), ("check_pdf_quote", "trovata", 3))


class TestPagineSenzaStrumenti(unittest.TestCase):
    def test_nessuno_strumento_non_verificabile(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as home:
            lav = prepara(tmp)
            # PATH vuoto: pdftotext non trovato; skill B assente (HOME vuota)
            env = dict(os.environ, HOME=home, PATH="")
            env.pop("CODEX_HOME", None)
            r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "pagine.py"), str(lav)],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rr = righe(lav)
            self.assertEqual(len(rr), len(CITAZIONI))
            self.assertTrue(all(x["stato"] == "non_verificabile" and x["pagina_fisica"] is None
                                and x["metodo"] == "nessuno" for x in rr))


class TestConteggiConPagine(unittest.TestCase):
    def _lavoro(self, tmp):
        lav = prepara(tmp, citazioni=["x"])
        (lav / "elenco.csv").write_text(
            "id,ufficio,sezione,grado,tipo,data,numero,rg,url_scheda,url_file,pertinenza,motivo,da_leggere,formato\n"
            "abc-1,T,P,primo grado,sentenza,2025-03-20,1/2025,2/2024,-,-,alta,prova,si,pdf\n", encoding="utf-8")
        return lav

    def test_senza_e_con_pagine_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            lav = self._lavoro(tmp)
            r = esegui("conteggi.py", lav)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("pagine.jsonl", (lav / "conteggi.txt").read_text(encoding="utf-8"))
            righe_ok = [
                {"id": "abc-1", "i": 0, "metodo": "pdftotext", "stato": "trovata", "pagina_fisica": 2},
                {"id": "abc-1", "i": 5, "metodo": "pdftotext", "stato": "trovata", "pagina_fisica": 2},  # i fuori scheda
            ]
            (lav / "pagine.jsonl").write_text(
                "\n".join(json.dumps(x) for x in righe_ok) + "\nnon json\n", encoding="utf-8")
            r = esegui("conteggi.py", lav)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("pagina trovata:        1/1 (per metodo: pdftotext 1)",
                          (lav / "conteggi.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
