# Normattiva: MCP `normattiva` / CLI `norm`

Testo ufficiale delle norme statali italiane, vigente e storico. Per i dettagli carica la skill `normattiva-mcp`.

## Che cosa dà
- `normattiva_leggi_articolo(fonte, articolo)`: testo vigente, con alias dei codici (es. «codice civile», «codice di procedura civile»).
- `normattiva_leggi_urn(urn)`: per le fonti senza alias (d.P.R., d.lgs.), con URN `urn:nir:stato:<tipo>:<data>;<numero>~art<N>`.
- `normattiva_link(fonte, articolo)`: link verificato.
- Il parametro `vigenza` dà il testo a una data storica (ratione temporis).

## Limiti e cautele
- **Quota giornaliera** per attività (es. 30 consultazioni): chiama `normattiva_stato_rete` prima di iniziare. Se il livello è «critico» o «bloccato», fermati.
- Un permalink può rispondere anche a un URN sbagliato: usa le funzioni con verifica.
- L'articolo è un testo continuo: **i commi non sono numerati**. Contali tu.
- Un alias mancante (es. «dpr 115/2002») non vuol dire che la fonte manchi: usa l'URN.
- Allegati: c.p.c. = `regio.decreto:1940-10-28;1443:1`, c.c. = `regio.decreto:1942-03-16;262:2`.
- Per le norme UE usa EUR-Lex (`fonti-pubbliche.md`).
