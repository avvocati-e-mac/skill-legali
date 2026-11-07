# Link a Normattiva (Fase 8)

Schema: `https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:<tipo>:<AAAA-MM-GG>;<numero>[:<allegato>]~art<N>`
Non codificare `:` `;` `~`. Articoli bis/ter: `~art696bis`. Comma: `~art96-com3`.

| Norma | Parte fissa dell'URN |
|---|---|
| Codice civile (c.c.) | `regio.decreto:1942-03-16;262:2` |
| Codice di procedura civile (c.p.c.) | `regio.decreto:1940-10-28;1443:1` |
| Codice penale (c.p.) | `regio.decreto:1930-10-19;1398:1` |
| Codice di procedura penale (c.p.p.) | `decreto.del.presidente.della.repubblica:1988-09-22;447` |
| Costituzione | `costituzione:1947-12-27` |
| Codice del processo amministrativo (c.p.a.) | `decreto.legislativo:2010-07-02;104:1` |
| Codice della proprietà industriale (c.p.i.) | `decreto.legislativo:2005-02-10;30` |
| L. 132/2025 (intelligenza artificiale) | `legge:2025-09-23;132` |

Esempio: art. 96 c.p.c. → `https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443:1~art96`
Per altri atti: tipo (`legge`, `decreto.legislativo`, `decreto.legge`, `decreto.del.presidente.della.repubblica`), data e numero dell'atto. Se non sei sicuro, scrivi la norma senza link e segnalalo nei limiti. Norme abrogate o in versione storica: aggiungi `!vig=AAAA-MM-GG` in coda.
