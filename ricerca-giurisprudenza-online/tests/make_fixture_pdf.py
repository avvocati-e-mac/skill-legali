#!/usr/bin/env python3
"""Genera tests/fixtures/provvedimento-minimo.pdf (3 pagine, solo libreria standard).

Contenuto pensato per i test di pagine.py: una frase divisa con sillabazione a fine riga
(pag. 1), una frase a cavallo tra pag. 2 e 3, un apostrofo tipografico (pag. 3) e una
frase ripetuta in pag. 1 e 3 (ambigua).
"""
import sys
from pathlib import Path

PAGINE = [
    ["Sentenza di prova n. 1/2025",
     "Il ricorso e\xa0fondato per le seguenti ra-",
     "gioni esposte di seguito.",
     "Spese compensate tra le parti."],
    ["Il Collegio ritiene che la clausola sia nulla e che",
     "il principio di diritto va"],
    ["affermato nei termini seguenti.",
     "Pertanto l\x92appello \xe8 inammissibile.",
     "Spese compensate tra le parti."],
]
PAGINE[0][1] = "Il ricorso \xe8 fondato per le seguenti ra-"


def esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def costruisci():
    oggetti = {}
    n_pagine = len(PAGINE)
    oggetti[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join("%d 0 R" % (4 + 2 * i) for i in range(n_pagine))
    oggetti[2] = ("<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, n_pagine)).encode()
    oggetti[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    for i, righe in enumerate(PAGINE):
        num_p, num_c = 4 + 2 * i, 5 + 2 * i
        flusso = "BT /F1 12 Tf 14 TL 72 720 Td\n" + "\n".join("(%s) Tj T*" % esc(r) for r in righe) + "\nET"
        dati = flusso.encode("latin-1")
        oggetti[num_p] = ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                          "/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % num_c).encode()
        oggetti[num_c] = b"<< /Length %d >>\nstream\n" % len(dati) + dati + b"\nendstream"
    out = bytearray(b"%PDF-1.4\n")
    offset = {}
    for num in sorted(oggetti):
        offset[num] = len(out)
        out += b"%d 0 obj\n" % num + oggetti[num] + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(oggetti) + 1)
    for num in sorted(oggetti):
        out += b"%010d 00000 n \n" % offset[num]
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(oggetti) + 1, xref)
    return bytes(out)


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures" / "provvedimento-minimo.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(costruisci())
    print(dest)
