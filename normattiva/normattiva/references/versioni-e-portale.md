# Versioni del testo e comportamento del portale: osservazioni

Regole operative in SKILL.md, sezione "Quale versione del testo". Qui ci sono le osservazioni che le motivano, con le date dei controlli.

## Vista senza suffisso e posizione del selettore

`!vig=` è il default perché dice in modo esplicito che si vuole il testo in vigore. Senza suffisso si apre la vista multivigente, che spesso coincide con il testo vigente ma può mostrare modifiche con decorrenza futura: nel controllo dell'autore del 7 ottobre 2026 l'art. 2 del d.P.R. 633/1972 senza suffisso appariva "ABROGATO" con decorrenza 1° gennaio 2027, mentre con `!vig=` mostrava il testo in vigore. Un link senza suffisso trovato in un testo non è quindi di per sé sbagliato: non correggerlo e non segnalarlo per questo solo motivo.

**Dove mettere il selettore.** Scrivi `@originale` o `!vig=...` dopo l'articolo: `;262:2~art2043@originale`. È una scelta pratica, non una regola del portale:

- la FAQ documenta `@originale` prima dell'articolo (`;300@originale~art18`) e `!vig=` dopo;
- negli atti senza allegato controllati (l. 300/1970, l. 241/1990, d.lgs. 28/2010, c.p.p.) le due posizioni hanno aperto lo stesso articolo nella stessa versione;
- nei codici in allegato controllati (c.c., c.p.c., c.p., c.p.a.) il selettore scritto prima dell'articolo ha aperto l'art. 1 del decreto di approvazione, quello scritto dopo ha aperto l'articolo richiesto.

Sono osservazioni del 6 e 7 ottobre 2026 su questi atti, non una garanzia per tutti gli altri. Un link si giudica da ciò che apre, non da come è scritto: non dichiarare sbagliato un link solo perché il selettore è in un'altra posizione.

## Limiti noti

- Nei controlli dell'autore Normattiva ha identificato l'atto soprattutto da anno e numero: se gli estremi nel testo sono sbagliati, il link può aprire senza avvisi un altro atto. Lo script annota tipo o data diversi alla voce "estremi URN".
- Articoli numerati con il solo punto (es. art. 190.1 TUF) non sempre si aprono; quelli con estensione (art. 190-bis.1, `~art190bis.1`) sì.
- La tabella dice dove si trova l'articolo, non se è in vigore: la vigenza la mostra Normattiva. Il diritto tributario è in corso di riscrittura in testi unici (2024-2026): i vecchi decreti restano collegabili.
- Abrogato non vuol dire inesistente: un articolo abrogato ha la sua pagina e si collega normalmente.
- Le osservazioni sul comportamento del portale (posizione dei selettori, tolleranze sugli estremi, vista senza suffisso) valgono per gli atti e le date indicati e possono cambiare.

## Norme abrogate o sostituite

Quando citi una di queste norme, dillo nelle note e indica la norma che l'ha sostituita. Il link alla norma storica resta valido: se contano i fatti di un'epoca, usa `!vig=` con la data dei fatti (es. per una procedura fallimentare aperta nel 2018, `;267:1~art42!vig=2018-06-30`). Una data qui sotto che non è scritta per esteso non va presentata come certa: la decorrenza esatta la mostra Normattiva.

| Norma storica | Sostituita da | Da quando | Nota |
|---|---|---|---|
| l. fall. (r.d. 267/1942) | CCII (d.lgs. 14/2019) | 15 luglio 2022 | resta applicabile alle procedure aperte prima |
| d.lgs. 50/2016 (codice appalti) | d.lgs. 36/2023 | 1° luglio 2023 | regime transitorio per le procedure avviate prima |
| art. 18 St. lav. (tutela reale) | art. 3 d.lgs. 23/2015 | 7 marzo 2015 | vale per gli assunti da quella data; l'art. 18 resta in vigore per gli altri |
| d.lgs. 196/2003, testo originario | d.lgs. 101/2018 (adeguamento al GDPR) | 19 settembre 2018 | il codice privacy resta in vigore nel testo modificato, insieme al reg. (UE) 2016/679 |
| d.lgs. 546/1992 (processo tributario) | t.u. giust. trib. (d.lgs. 175/2024) | vedi Normattiva | |
| d.P.R. 633/1972 (IVA) | t.u. IVA (d.lgs. 10/2026) | vedi Normattiva | nel controllo del 7 ottobre 2026 l'art. 2 risultava abrogato con decorrenza 1° gennaio 2027 |
| d.P.R. 917/1986 (TUIR) | t.u. redditi (d.lgs. 117/2026) | vedi Normattiva | verificare articolo per articolo |

Un articolo abrogato chiesto con `!vig=` di oggi mostra soltanto la formula di abrogazione, poche decine di caratteri: non è una pagina vuota né un link sbagliato.
