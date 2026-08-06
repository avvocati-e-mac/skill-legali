# Normattiva – Riferimento esteso

Leggi questo file quando la norma da linkare **non è nella quick lookup** del SKILL.md,
o quando hai bisogno di dettagli su partizioni, errori comuni o tipi di atto rari.

---

## Tabella completa dei tipi di atto (`tipo_atto`)

| Abbreviazione comune  | Tipo atto URN-NIR                                         |
|-----------------------|-----------------------------------------------------------|
| Cost.                 | `costituzione`                                            |
| l. / L.               | `legge`                                                   |
| r.d.                  | `regio.decreto`                                           |
| d.lgs. / d.l.gs.      | `decreto.legislativo`                                     |
| d.l.                  | `decreto.legge`                                           |
| D.P.R.                | `decreto.del.presidente.della.repubblica`                 |
| D.P.C.M.              | `decreto.del.presidente.del.consiglio.dei.ministri`       |
| ~~D.M.~~              | ~~`decreto.ministeriale`~~ — **non risolve nulla**: Normattiva non pubblica i decreti ministeriali (verificato sul d.m. 55/2014, parametri forensi) |
| d.lgt.                | `decreto.luogotenenziale`                                 |
| l.cost.               | `legge.costituzionale`                                    |

---

## Lookup table completa

> **⚠️ Colonna "Allegato"**: per i Regi Decreti storici, il numero indica
> quale allegato del R.D. contiene il testo del codice. Va inserito dopo il numero
> dell'atto separato da `:` (es. `262:2`). Per atti moderni il campo è `—`.

> **Verificate contro l'API Normattiva il 2026-08-06.** Ogni riga è stata
> interrogata davvero e restituisce l'articolo richiesto. Vedi
> `api-e-verifica.md` per il metodo e per i limiti di questa verifica.

### Codici e testi fondamentali

| Nome comune                          | Sigla        | Tipo URN                                              | Data URN       | Numero | Allegato |
|--------------------------------------|--------------|-------------------------------------------------------|----------------|--------|:--------:|
| **Preleggi** (disp. sulla legge in gen.) | disp. prel. | `regio.decreto`                                   | `1942-03-16`   | `262`  | **`:1`** |
| Codice Civile                        | c.c.         | `regio.decreto`                                       | `1942-03-16`   | `262`  | **`:2`** |
| Cod. Proc. Civile                    | c.p.c.       | `regio.decreto`                                       | `1940-10-28`   | `1443` | **`:1`** |
| Codice Penale                        | c.p.         | `regio.decreto`                                       | `1930-10-19`   | `1398` | **`:1`** |
| Cod. Proc. Penale                    | c.p.p.       | `decreto.del.presidente.della.repubblica`             | `1988-09-22`   | `447`  | —        |
| Costituzione                         | Cost.        | `costituzione`                                        | `1947-12-27`   | —      | —        |
| Legge Fallimentare ⚠ abrogata        | l.fall.      | `regio.decreto`                                       | **`1942-03-16`** | `267` | **`:1`** |
| **Cod. Proc. Amministrativo**        | c.p.a.       | `decreto.legislativo`                                 | `2010-07-02`   | `104`  | **`:2`** |
| Cod. Navigazione                     | cod. nav.    | `regio.decreto`                                       | `1942-03-30`   | `327`  | **`:1`** |
| **Avvocatura dello Stato**           | —            | `regio.decreto`                                       | `1933-10-30`   | `1611` | **`:1`** |

> ⚠ **Legge Fallimentare, data corretta `1942-03-16`** — lo stesso giorno del
> codice civile. La data `1942-01-16` che compariva qui fino al 2026-08-06 era
> sbagliata: sul portale il link funzionava lo stesso (vedi
> `api-e-verifica.md`), ma qualunque uso programmatico dava 404.
>
> ⚠ **Cod. Navigazione: allegato `:1`, che qui mancava.** Senza allegato
> `~art422` dà 404 e `~art1` restituisce il preambolo del R.D. — cioè *sembra*
> funzionare.

### Lavoro e previdenza

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| Statuto dei Lavoratori (L. 300/1970) | `legge` | `1970-05-20` | `300` |
| L. 604/1966 (licenziamenti individuali) | `legge` | `1966-07-15` | `604` |
| D.Lgs. 81/2015 (Jobs Act – contratti) | `decreto.legislativo` | `2015-06-15` | `81` |
| D.Lgs. 81/2008 (Sicurezza sul lavoro) | `decreto.legislativo` | `2008-04-09` | `81` |

### Civile, famiglia, locazioni

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| L. 392/1978 (equo canone) | `legge` | `1978-07-27` | `392` |
| L. 431/1998 (locazioni abitative) | `legge` | `1998-12-09` | `431` |
| L. 898/1970 (divorzio) | `legge` | `1970-12-01` | `898` |
| L. 54/2006 (affido condiviso) | `legge` | `2006-02-08` | `54` |
| L. 76/2016 (unioni civili) | `legge` | `2016-05-20` | `76` |
| D.Lgs. 206/2005 (Cod. Consumo) | `decreto.legislativo` | `2005-09-06` | `206` |
| D.Lgs. 209/2005 (Cod. Assicurazioni) | `decreto.legislativo` | `2005-09-07` | `209` |
| D.Lgs. 122/2005 (acquirenti immobili da costruire) | `decreto.legislativo` | `2005-06-20` | `122` |
| D.Lgs. 231/2002 (ritardi di pagamento) | `decreto.legislativo` | `2002-10-09` | `231` |

### Procedura, ADR, professione forense

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| D.P.R. 115/2002 (spese di giustizia, gratuito patrocinio) | `decreto.del.presidente.della.repubblica` | `2002-05-30` | `115` |
| D.Lgs. 28/2010 (mediazione civile) | `decreto.legislativo` | `2010-03-04` | `28` |
| D.L. 132/2014 (negoziazione assistita) | `decreto.legge` | `2014-09-12` | `132` |
| L. 3/2012 (sovraindebitamento) | `legge` | `2012-01-27` | `3` |
| L. 247/2012 (ordinamento forense) | `legge` | `2012-12-31` | `247` |
| L. 89/2001 (legge Pinto) | `legge` | `2001-03-24` | `89` |

### Amministrativo

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| L. 241/1990 (procedimento amministrativo) | `legge` | `1990-08-07` | `241` |
| L. 689/1981 (sanzioni amministrative) | `legge` | `1981-11-24` | `689` |
| D.P.R. 445/2000 (documentazione amministrativa) | `decreto.del.presidente.della.repubblica` | `2000-12-28` | `445` |
| D.Lgs. 267/2000 (TUEL) | `decreto.legislativo` | `2000-08-18` | `267` |
| D.Lgs. 165/2001 (lavoro alle dipendenze della P.A.) | `decreto.legislativo` | `2001-03-30` | `165` |
| D.Lgs. 36/2023 (Cod. Appalti vigente) | `decreto.legislativo` | `2023-03-31` | `36` |
| D.Lgs. 50/2016 (Cod. Appalti) ⚠ abrogato | `decreto.legislativo` | `2016-04-18` | `50` |
| D.P.R. 380/2001 (T.U. Edilizia) | `decreto.del.presidente.della.repubblica` | `2001-06-06` | `380` |
| D.Lgs. 42/2004 (Cod. Beni Culturali) | `decreto.legislativo` | `2004-01-22` | `42` |
| D.Lgs. 152/2006 (Cod. Ambiente) | `decreto.legislativo` | `2006-04-03` | `152` |
| D.Lgs. 285/1992 (Cod. della Strada) | `decreto.legislativo` | `1992-04-30` | `285` |
| D.Lgs. 286/1998 (T.U. Immigrazione) | `decreto.legislativo` | `1998-07-25` | `286` |

### Tributario ⚠ larga parte riformata nel 2026

| Nome comune | Tipo URN | Data URN | Numero | Stato |
|---|---|---|---|---|
| D.P.R. 600/1973 (accertamento) | `decreto.del.presidente.della.repubblica` | `1973-09-29` | `600` | vigente |
| L. 212/2000 (statuto del contribuente) | `legge` | `2000-07-27` | `212` | vigente |
| D.P.R. 917/1986 (T.U.I.R.) | `decreto.del.presidente.della.repubblica` | `1986-12-22` | `917` | **⚠ abrogato 2026** |
| D.P.R. 633/1972 (IVA) | `decreto.del.presidente.della.repubblica` | `1972-10-26` | `633` | **⚠ abrogato 2026** |
| D.Lgs. 546/1992 (processo tributario) | `decreto.legislativo` | `1992-12-31` | `546` | **⚠ abrogato 2024** |
| D.Lgs. 74/2000 (reati tributari) | `decreto.legislativo` | `2000-03-10` | `74` | **⚠ vari artt. abrogati** |

### Impresa, banche, finanza, terzo settore

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| D.Lgs. 14/2019 (Cod. Crisi d'Impresa) | `decreto.legislativo` | `2019-01-12` | `14` |
| D.Lgs. 231/2001 (responsabilità enti) | `decreto.legislativo` | `2001-06-08` | `231` |
| D.Lgs. 385/1993 (T.U. Bancario) | `decreto.legislativo` | `1993-09-01` | `385` |
| D.Lgs. 58/1998 (T.U. Finanza) | `decreto.legislativo` | `1998-02-24` | `58` |
| D.Lgs. 30/2005 (Cod. Proprietà Industriale) | `decreto.legislativo` | `2005-02-10` | `30` |
| D.Lgs. 117/2017 (Cod. Terzo Settore) | `decreto.legislativo` | `2017-07-03` | `117` |
| D.Lgs. 159/2011 (Cod. Antimafia) | `decreto.legislativo` | `2011-09-06` | `159` |

### Privacy

| Nome comune | Tipo URN | Data URN | Numero |
|---|---|---|---|
| D.Lgs. 196/2003 (Cod. Privacy, consolidato) | `decreto.legislativo` | `2003-06-30` | `196` |
| D.Lgs. 101/2018 (adeguamento GDPR) | `decreto.legislativo` | `2018-08-10` | `101` |

> Per la Costituzione ometti il numero: `urn:nir:stato:costituzione:1947-12-27~art{N}`

### Cosa NON si trova su Normattiva

| Fonte | Perché |
|---|---|
| **D.M. 55/2014 (parametri forensi)** e ogni altro decreto ministeriale | **Verificato 404.** Normattiva non pubblica i decreti ministeriali. Il tipo `decreto.ministeriale` non risolve nulla |
| Codice deontologico forense | È una delibera del CNF, non un atto normativo statale: non ha URN-NIR |
| Regolamenti e direttive UE (GDPR), CEDU | Non sono atti statali italiani. Usare EUR-Lex |
| Giurisprudenza | Normattiva pubblica solo normativa |

---

## Partizioni sotto-articolo — **solo due esistono**

**Verificato il 2026-08-06: l'unica partizione supportata è l'articolo.**

| Partizione       | Sintassi URN  | Esempio    | Stato |
|------------------|---------------|------------|-------|
| Articolo         | `~art{N}`     | `~art83`   | ✅ funziona |
| Articolo bis/ter | `~art{N}bis`  | `~art30bis` | ✅ funziona — **senza trattino** |

**Non esistono** — producono un errore, oppure sul portale la stessa identica
pagina di `~art{N}`, cioè non fanno nulla:

| Sintassi | Cosa succede davvero |
|---|---|
| `~art{N}-com{C}` (comma) | Errore sull'API; sul portale **pagina byte-identica** a `~art{N}` |
| `~art{N}-com{C}-let{L}` (lettera) | idem |
| `~art{N}-bis` (col trattino) | Errore sull'API; sul portale apre una pagina che **non aggancia l'articolo** |
| `~all{N}` (allegato) | Errore. L'allegato si indica con `:{N}` **prima** della tilde, non dopo |
| `~dis{N}` (disp. transitorie) | Errore |
| `~pre` (preambolo) | Errore |

> **Come si cita un comma.** Non si chiede nell'URN: si linka **l'articolo
> intero** e si indica il comma nell'etichetta.
>
> ```markdown
> [art. 7, co. 1, L. 300/1970](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art7)
> ```

---

## Note sugli allegati nei codici storici

I grandi codici del periodo pre-repubblicano furono approvati come *allegati numerati* a
Regi Decreti. Il numero `:N` nell'URN identifica quale allegato contiene la norma,
non una versione storica.

**Verificato il 2026-08-06: esistono solo gli allegati elencati qui.** Le
disposizioni di attuazione e transitorie **non sono raggiungibili** con un URN di
allegato — `262:3`, `1443:2`, `1443:3`, `1398:2` restituiscono tutti «atto non
trovato».

| Codice / testo      | R.D.            | Allegati che esistono davvero |
|---------------------|-----------------|-------------------------------|
| Preleggi            | R.D. 262/1942   | **`:1`** — disp. sulla legge in generale |
| Codice Civile       | R.D. 262/1942   | **`:2`** |
| Cod. Proc. Civile   | R.D. 1443/1940  | **`:1`** (solo questo) |
| Codice Penale       | R.D. 1398/1930  | **`:1`** (solo questo) |
| Legge Fallimentare  | R.D. 267/1942   | **`:1`** (solo questo) |
| Cod. Navigazione    | R.D. 327/1942   | **`:1`** |
| Avvocatura Stato    | R.D. 1611/1933  | **`:1`** |

> **L'allegato non riguarda solo i quattro codici.** Il r.d. 1611/1933
> sull'Avvocatura dello Stato lo richiede, e non è un codice. Davanti a un regio
> decreto, non dare mai per scontato che l'allegato non serva: **provalo**.

---

## ⚠ `~art1` restituisce il preambolo, non l'articolo 1

Su molti atti moderni `~art1` non dà l'art. 1 ma la **formula di promulgazione**
(«IL PRESIDENTE DELLA REPUBBLICA, Visti gli articoli 76 e 87…»). Verificato su
almeno 13 atti, fra cui Statuto dei Lavoratori, D.Lgs. 231/2001, TUEL, D.Lgs.
81/2008, Cod. Consumo, Cod. della Strada.

Non è un errore dell'URN: la risposta è formalmente valida e il testo è
plausibile. **Se il testo che ricevi comincia con «IL PRESIDENTE DELLA
REPUBBLICA», «Visti», oppure «La Camera dei deputati ed il Senato hanno
approvato», stai leggendo il preambolo:** dillo invece di citarlo come art. 1.

Non sono affetti: gli atti con allegato (c.c., c.p.c., c.p., l.fall., cod. nav.)
e Cost., c.p.p., T.U. Edilizia, T.U.I.R., D.Lgs. 50/2016.

---

## Errori comuni

| Errore                                             | Corretto                                              |
|----------------------------------------------------|-------------------------------------------------------|
| **Sbagliare l'anno** dell'atto                     | È l'errore **più pericoloso**: il portale risolve per anno+numero, quindi apre **un atto diverso** con una pagina plausibile. Sbagliare tipo o giorno è invece innocuo |
| Omettere `:2` nel c.c.                             | `262:2~art2043`                                       |
| Omettere `:1` nel c.p.c.                           | `1443:1~art83`                                        |
| Omettere `:1` nel c.p.                             | `1398:1~art110`                                       |
| Omettere `:1` nella l.fall.                        | `267:1~art42`                                         |
| Usare `1942-01-16` per la l.fall.                  | La data corretta è **`1942-03-16`**                   |
| Omettere `:1` nel cod. navigazione                 | `327:1~art422`                                        |
| Aggiungere allegato al c.p.p. (D.P.R. 447/1988)   | Il c.p.p. è un D.P.R. moderno: nessun allegato        |
| Chiedere un comma o una lettera nell'URN           | Non esistono: si linka l'articolo e si scrive il comma nell'etichetta |
| Scrivere `~art30-bis` col trattino                 | `~art30bis`, attaccato                                |
| Citare `~art1` come articolo 1                     | Su molti atti moderni restituisce il **preambolo**: controlla l'incipit |
| Citare una norma abrogata senza dirlo              | Aggiungi `!vig=` alla data dei fatti e segnala l'abrogazione |
| Usare la data della G.U. invece di quella di firma | Usare sempre la data di **emanazione**                |
| Scrivere `art.2043` senza spazio                   | Label: `art. 2043 c.c.`                               |
| Omettere il `;` prima del numero                   | `1942-03-16;262`                                      |
| URL-encodare i `:` → `%3A`                         | Lasciarli come `:` nella query string                 |
| Fidarsi del fatto che «il link si apre»            | Il portale risponde sempre con una pagina, anche a URN inventati. **Un URN non si valida cliccandoci sopra** |

---

## Formato citazionale italiano completo

| Norma                   | Label consigliata             |
|-------------------------|-------------------------------|
| Codice civile           | `art. 1218 c.c.`              |
| Cod. proc. civile       | `art. 83 c.p.c.`              |
| Codice penale           | `art. 575 c.p.`               |
| Cod. proc. penale       | `art. 192 c.p.p.`             |
| Costituzione            | `art. 24 Cost.`               |
| Legge fallimentare      | `art. 42 l.fall.`             |
| Legge con numero/anno   | `art. 18, L. 300/1970`        |
| Decreto legislativo     | `art. 5, D.Lgs. 231/2001`     |
| D.P.R.                  | `art. 1, D.P.R. 380/2001`     |
| Decreto-legge           | `art. 3, D.L. 23/2020`        |
| D.P.C.M.                | `art. 1, D.P.C.M. 11/03/2020` |

---

## Versioni storiche e multivigenza

Normattiva.it supporta la **multivigenza**: è possibile consultare la versione di un atto vigente a una data specifica tramite il parametro `!vig=`.

### Sintassi `!vig=`

| Caso d'uso | Sintassi | Esempio | Stato |
|---|---|---|---|
| Versione vigente oggi | **ometti `!vig=`** | `...;81~art29` | ✅ |
| Versione vigente a data X | `!vig=AAAA-MM-GG` | `...;81!vig=2022-12-31` | ✅ verificato su tutti i tipi di atto |
| Articolo + versione storica | `~artN!vig=AAAA-MM-GG` | `...;81~art29!vig=2022-12-31` | ✅ |
| ~~`!vig=` senza data~~ | — | — | ❌ **non usarlo**: dà errore e sul portale apre una pagina diversa. Per il testo vigente si omette il parametro |

**Posizione nel link**: `!vig=` va sempre in coda all'URL, dopo `~artN` se presente.

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{numero}[:{all}][~artN]!vig=AAAA-MM-GG
```

### Quando usarlo

- **Contenzioso su fatti passati**: usare la versione vigente alla data dei fatti (`!vig=data-fatti`)
- **Norma abrogata ancora applicabile**: es. l.fall. per procedure fallimentari aperte prima del 15/07/2022
- **Norma ante-riforma**: es. art. 18 L. 300/1970 nella versione pre-Jobs Act (`!vig=2012-06-30`)
- **Verifica requisiti storici**: es. soglie D.Lgs. 81/2008 prima delle modifiche del 2023

### Esempi concreti

```markdown
<!-- Legge fallimentare: versione vigente il giorno prima dell'abrogazione -->
<!-- nota: la data dell'atto e' 1942-03-16, non 1942-01-16 -->
[art. 42 l.fall. (testo ante 15/7/2022)](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;267:1~art42!vig=2022-07-14)

<!-- Art. 18 Statuto Lavoratori: versione pre-Jobs Act -->
[art. 18 L. 300/1970 (testo ante D.Lgs. 23/2015)](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art18!vig=2015-03-06)

<!-- D.Lgs. 81/2008 prima del correttivo 2009 -->
[art. 29 D.Lgs. 81/2008 (versione originaria)](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art29!vig=2009-08-02)
```

---

## Norme abrogate o integralmente riformate

Quando citi queste norme, **segnala sempre** lo stato di vigenza e indica la norma sostituta.

| Norma storica | Abrogata/riformata da | Data decorrenza | Norma sostituta vigente |
|---|---|---|---|
| R.D. 267/1942 — Legge Fallimentare | D.Lgs. 14/2019 (Cod. Crisi d'Impresa) | **15/07/2022** | D.Lgs. 14/2019 |
| D.Lgs. 50/2016 — Codice Appalti | D.Lgs. 36/2023 | **01/07/2023** | D.Lgs. 36/2023 |
| Art. 18 L. 300/1970 — tutela reale | D.Lgs. 23/2015 (per assunzioni post 7/3/2015) | **07/03/2015** | Art. 3 D.Lgs. 23/2015 |
| D.Lgs. 196/2003 — Privacy (testo originario) | D.Lgs. 101/2018 (adeguamento GDPR) | **19/09/2018** | D.Lgs. 196/2003 (consolidato post 2018) + Reg. UE 2016/679 |
| **D.P.R. 917/1986 — T.U.I.R.** | D.Lgs. 117/2026 | **giugno 2026** | verificare la norma sostituta |
| **D.P.R. 633/1972 — IVA** | D.Lgs. 10/2026 | **gennaio 2026** | verificare la norma sostituta |
| **D.Lgs. 546/1992 — processo tributario** | D.Lgs. del novembre 2024 | **2024** | verificare la norma sostituta |
| **D.Lgs. 74/2000 — reati tributari** (artt. 4 e 10) | riforma successiva | — | verificare articolo per articolo |

> **Nota**: per le norme abrogate con regime transitorio (l.fall., D.Lgs. 50/2016), il testo storico rimane applicabile alle procedure avviate prima della data di decorrenza. Usa `!vig=data-precedente` per linkare la versione storica corretta.

> ### ⚠ Le norme abrogate restituiscono una riga vuota
>
> Chiedendo un articolo abrogato senza `!vig=` si ottiene **solo** la formula di
> abrogazione, poche decine di caratteri: «ARTICOLO ABROGATO DAL D.LGS. …».
> Nessun testo. Misurato: l'art. 51 T.U.I.R. restituisce **69 caratteri** oggi e
> **23.681** con `!vig=2020-12-31`; l'art. 19 IVA rispettivamente **64** e
> **11.174**.
>
> **Quindi:** se il risultato è brevissimo e contiene «ABROGATO», non concludere
> che la norma non esista. Rilancia con `!vig=` alla data dei fatti — o al giorno
> prima dell'abrogazione, che la formula stessa dichiara — e **presenta le due
> versioni etichettate**, dicendo quale è vigente e quale no.
>
> La riforma fiscale del 2026 ha abrogato buona parte del T.U.I.R. e del decreto
> IVA: in materia tributaria questo caso è la regola, non l'eccezione. **La
> tabella qui sopra è aggiornata al 2026-08-06 e invecchia:** in caso di dubbio,
> è la risposta di Normattiva a fare fede, non questa pagina.

---

## Se la norma non è in tabella

1. Identifica il `tipo_atto` dalla tabella sopra.
2. La data è quella di **emanazione/firma** (non di pubblicazione in G.U.).
3. **L'anno è la parte che non puoi sbagliare.** Tipo e giorno sono tollerati dal
   portale, l'anno no: un anno sbagliato apre un atto diverso senza alcun segnale.
4. Se è un Regio Decreto, verifica se il testo è un **allegato numerato**: capita
   anche fuori dai quattro codici.
5. Se non sei sicuro, cerca su web: `"{tipo atto} {numero}/{anno}" normattiva urn nir`.
6. **Se hai il dubbio e puoi verificare, verifica contro l'API** — è l'unica che
   dice di no. Vedi `api-e-verifica.md`.
7. Se non puoi verificare, **dillo**: meglio «non sono certo dell'URN di questa
   norma» che un link plausibile verso l'atto sbagliato.
