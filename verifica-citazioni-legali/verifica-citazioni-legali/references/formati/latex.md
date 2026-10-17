# Atto in LaTeX (.tex)

## Lettura
- `estrai_citazioni.py` legge la sorgente e indica la posizione come **riga**.
- Le parti commentate (`%`) sono segnalate a parte: non vanno nel PDF, ma possono rientrare nella versione finale. Verificale solo se l'utente lo chiede.
- Se l'atto usa `\input{}` o `\include{}`, estrai anche i file inclusi.
- Le macro dei segnaposto (`\Cliente`, `\RG`…) vanno lasciate come sono: non risolverle.
- La **stringa da cercare** è scritta come appare nel PDF: senza comandi e con la tilde resa come spazio («n. 222»). Nel sorgente lo stesso punto può essere `n.~222`. Per cercare nel sorgente, usa la ricerca con espressioni regolari (`n.[ ~]222`) oppure la riga indicata.

## Stile del «testo da incollare»
- Estremi in corsivo: `\textit{Cass. civ., sez.~II, 13.11.2024, n.~29331, Rv.~673088-02}`.
- Spazio non divisibile: `n.~`, `art.~`, `sez.~`, `co.~`.
- Norme con link: `\href{https://www.normattiva.it/uri-res/N2Ls?urn:...~art1669}{art.~1669 c.c.}`. Se la compilazione fallisce sulla `~` dell'URL, usa `\string~`.
- Virgolette basse «…» (con XeLaTeX o LuaLaTeX vanno bene così; con pdfLaTeX servono `\usepackage[T1]{fontenc}` e `\usepackage[utf8]{inputenc}`).
- Pinpoint: «§ 9.1», «punto 4.4.1 del Considerato in diritto».
- Il diff va in un blocco ```diff```, con righe `-` (originale) e `+` (proposta).

## Applicazione selettiva (Fase 6)
- Copia l'originale in `02_versione_corretta.tex` e applica le modifiche con sostituzioni esatte della **stringa da cercare**, controllando prima che sia univoca.
- Se il progetto ha uno script di generazione (pandoc o latexmk), proponi di ricompilare ma non lanciarlo senza consenso.
