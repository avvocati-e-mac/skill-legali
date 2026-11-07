# Come aggiungere il profilo di un nuovo sito

Un profilo è una nota breve che dice a Claude come cercare e leggere un sito, così la prossima ricerca salta la ricognizione (Fase 1) e fa meno chiamate.

## Quando
Dopo una ricognizione riuscita (`lavoro/ricognizione.md` compilato e un provvedimento di prova letto davvero).

## Come
1. Crea `references/profili/<dominio-senza-www>.md` (esempio: `ilcaso.md`; vedi quel file come modello).
2. Copia da `ricognizione.md` solo ciò che è verificato, con questi campi:
   - Pagina d'ingresso
   - Come si cerca (URL con parametri o solo modulo; il filtro funziona davvero?)
   - URL della scheda
   - URL del file
   - Formato (PDF testuale, PDF scansione, HTML)
   - Strumento che funziona (WebFetch, WebSearch con allowed_domains, browser integrato, pdf.js...)
   - `id` consigliato
   - Provvedimento di prova
   - Da verificare al primo uso
3. Ciò che non hai verificato scrivilo come "da verificare", non come fatto.
4. Il nome del file deve contenere il dominio, così Claude lo trova.

Chi chiede a Claude di farlo può dire: "salva il profilo di questo sito tra i profili della skill ricerca-giurisprudenza".

## Modelli vuoti
Per ora esistono solo modelli da completare con la prima ricognizione: `giustizia-amministrativa.md`, `giustizia-tributaria.md`, `cassazione.md`. Quando un modello è completato, togli la riga "DA COMPLETARE".
