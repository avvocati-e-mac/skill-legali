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
| D.M.                  | `decreto.ministeriale`                                    |
| d.lgt.                | `decreto.luogotenenziale`                                 |
| l.cost.               | `legge.costituzionale`                                    |

---

## Lookup table completa

> **⚠️ Colonna "Allegato"**: per i Regi Decreti storici, il numero indica
> quale allegato del R.D. contiene il testo del codice. Va inserito dopo il numero
> dell'atto separato da `:` (es. `262:2`). Per atti moderni il campo è `—`.

| Nome comune                          | Sigla        | Tipo URN                                              | Data URN       | Numero | Allegato |
|--------------------------------------|--------------|-------------------------------------------------------|----------------|--------|:--------:|
| Codice Civile                        | c.c.         | `regio.decreto`                                       | `1942-03-16`   | `262`  | **`:2`** |
| Cod. Proc. Civile                    | c.p.c.       | `regio.decreto`                                       | `1940-10-28`   | `1443` | **`:1`** |
| Codice Penale                        | c.p.         | `regio.decreto`                                       | `1930-10-19`   | `1398` | **`:1`** |
| Cod. Proc. Penale                    | c.p.p.       | `decreto.del.presidente.della.repubblica`             | `1988-09-22`   | `447`  | —        |
| Costituzione                         | Cost.        | `costituzione`                                        | `1947-12-27`   | —      | —        |
| Statuto Lavoratori                   | L. 300/1970  | `legge`                                               | `1970-05-20`   | `300`  | —        |
| Legge Fallimentare                   | l.fall.      | `regio.decreto`                                       | `1942-01-16`   | `267`  | **`:1`** |
| D.Lgs. 14/2019 (Cod. Crisi)         | —            | `decreto.legislativo`                                 | `2019-01-12`   | `14`   | —        |
| D.Lgs. 81/2008 (Sic. Lav.)          | —            | `decreto.legislativo`                                 | `2008-04-09`   | `81`   | —        |
| D.Lgs. 196/2003 (Privacy)           | —            | `decreto.legislativo`                                 | `2003-06-30`   | `196`  | —        |
| D.Lgs. 231/2001                      | —            | `decreto.legislativo`                                 | `2001-06-08`   | `231`  | —        |
| D.Lgs. 206/2005 (Cod. Consumo)      | —            | `decreto.legislativo`                                 | `2005-09-06`   | `206`  | —        |
| D.Lgs. 209/2005 (Cod. Assicurazioni)| —            | `decreto.legislativo`                                 | `2005-09-07`   | `209`  | —        |
| D.Lgs. 50/2016 (Appalti)            | —            | `decreto.legislativo`                                 | `2016-04-18`   | `50`   | —        |
| D.Lgs. 36/2023 (Nuovo Cod. Appalti) | —            | `decreto.legislativo`                                 | `2023-03-31`   | `36`   | —        |
| D.Lgs. 267/2000 (TUEL)              | —            | `decreto.legislativo`                                 | `2000-08-18`   | `267`  | —        |
| D.Lgs. 165/2001 (P.A.)              | —            | `decreto.legislativo`                                 | `2001-03-30`   | `165`  | —        |
| D.Lgs. 81/2015 (Jobs Act)           | —            | `decreto.legislativo`                                 | `2015-06-15`   | `81`   | —        |
| D.Lgs. 286/1998 (T.U. Immigrazione) | —            | `decreto.legislativo`                                 | `1998-07-25`   | `286`  | —        |
| T.U.I.R. (D.P.R. 917/1986)          | —            | `decreto.del.presidente.della.repubblica`             | `1986-12-22`   | `917`  | —        |
| T.U. Edilizia (D.P.R. 380/2001)     | —            | `decreto.del.presidente.della.repubblica`             | `2001-06-06`   | `380`  | —        |
| Cod. Navigazione                     | —            | `regio.decreto`                                       | `1942-03-30`   | `327`  | —        |

> Per la Costituzione ometti il numero: `urn:nir:stato:costituzione:1947-12-27~art{N}`

---

## Partizioni sotto-articolo

Dopo `~art{N}` puoi aggiungere:

| Partizione          | Sintassi URN            | Esempio                  |
|---------------------|-------------------------|--------------------------|
| Articolo            | `~art{N}`               | `~art83`                 |
| Articolo bis/ter    | `~art{N}bis`            | `~art30bis`              |
| Comma               | `~art{N}-com{C}`        | `~art8-com2`             |
| Lettera             | `~art{N}-com{C}-let{L}` | `~art5-com1-letb`        |
| Allegato            | `~all{N}`               | `~all1`                  |
| Disposizione trans. | `~dis{N}`               | `~dis1`                  |
| Preambolo           | `~pre`                  | `~pre`                   |

---

## Note sugli allegati nei codici storici

I grandi codici del periodo pre-repubblicano furono approvati come *allegati numerati* a
Regi Decreti, che contenevano anche disposizioni di attuazione e transitorie.
Il numero `:N` nell'URN identifica quale allegato del R.D. contiene la norma, non una versione storica.

| Codice              | R.D.           | N. allegato | Struttura del R.D.                                         |
|---------------------|----------------|:-----------:|------------------------------------------------------------|
| Codice Civile       | R.D. 262/1942  | **2**       | All. 1 = disp. preliminari; **all. 2 = c.c.**; all. 3 = disp. att. |
| Cod. Proc. Civile   | R.D. 1443/1940 | **1**       | **All. 1 = c.p.c.**; all. 2 = disp. att.; all. 3 = disp. trans. |
| Codice Penale       | R.D. 1398/1930 | **1**       | **All. 1 = c.p.**; all. 2 = disp. att. e coord.           |
| Legge Fallimentare  | R.D. 267/1942  | **1**       | **All. 1 = l.fall.**; all. 2 = disp. att. e coord.        |

---

## Errori comuni

| Errore                                             | Corretto                                              |
|----------------------------------------------------|-------------------------------------------------------|
| Omettere `:2` nel c.c.                             | `262:2~art2043`                                       |
| Omettere `:1` nel c.p.c.                           | `1443:1~art83`                                        |
| Omettere `:1` nel c.p.                             | `1398:1~art110`                                       |
| Omettere `:1` nella l.fall.                        | `267:1~art42`                                         |
| Aggiungere allegato al c.p.p. (D.P.R. 447/1988)   | Il c.p.p. è un D.P.R. moderno: nessun allegato        |
| Usare la data della G.U. invece di quella di firma | Usare sempre la data di **emanazione**                |
| Scrivere `art.2043` senza spazio                   | Label: `art. 2043 c.c.`                               |
| Omettere il `;` prima del numero                   | `1942-03-16;262`                                      |
| URL-encodare i `:` → `%3A`                         | Lasciarli come `:` nella query string                 |

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

## Se la norma non è in tabella

1. Identifica il `tipo_atto` dalla tabella sopra.
2. La data è quella di **emanazione/firma** (non di pubblicazione in G.U.).
3. Se è un Regio Decreto storico, verifica se il testo del codice è un allegato numerato.
4. Se non sei sicuro, cerca su web: `"{tipo atto} {numero}/{anno}" normattiva urn nir`.
