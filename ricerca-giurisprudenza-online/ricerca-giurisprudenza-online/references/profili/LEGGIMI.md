# Come aggiungere il profilo di un nuovo sito

Un profilo è una nota breve che dice all'assistente come cercare e leggere un sito, così la prossima ricerca salta la ricognizione (Fase 1) e fa meno chiamate.

## Quando
Dopo una ricognizione riuscita (`lavoro/ricognizione.md` compilato e un provvedimento di prova letto davvero).

## Come
1. Crea `references/profili/<dominio-senza-www>.md` (esempio: `ilcaso.md`; vedi quel file come modello).
2. Copia da `ricognizione.md` solo ciò che è verificato, con questi campi:
   - Tipo di sito: pubblico (istituzionale) o privato (rivista, editore, banca dati commerciale); va scritto in testa al profilo, perché decide la regola su robots.txt (`ambienti.md`, sezione 3)
   - Pagina d'ingresso
   - Come si cerca (URL con parametri o solo modulo; il filtro funziona davvero?)
   - URL della scheda
   - URL del file
   - Formato (PDF testuale, PDF scansione, HTML)
   - Strumento che funziona (WebFetch, WebSearch con allowed_domains, browser integrato, Claude in Chrome, pdf.js...)
   - `id` consigliato
   - Provvedimento di prova
   - Da verificare al primo uso
3. Ciò che non hai verificato scrivilo come "da verificare", non come fatto.
4. Il nome del file deve contenere il dominio, così l'assistente lo trova.

Chi chiede all'assistente di farlo può dire: "salva il profilo di questo sito tra i profili della skill ricerca-giurisprudenza-online".

## Profili esistenti
- Verificati: `ilcaso.md` (privato), `giustizia-amministrativa.md`, `garanteprivacy.md`, `anac.md`, `agcm.md` (pubblici).
- Con browser da provare: `curia.md`.
- Con blocco (non aggirare; vedi `ambienti.md`, sezione 3): `cortecostituzionale.md` (captcha: lo risolve l'utente nel browser), `eur-lex.md` (sfida anti-robot).
- Da completare: `giustizia-tributaria.md` (blocco Akamai da terminale, browser da verificare), `cassazione.md` (modello vuoto).
Quando un profilo da completare è finito, togli la riga "DA COMPLETARE".
