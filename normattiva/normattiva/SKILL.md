---
name: normattiva
description: >
  Genera link ipertestuali a riferimenti normativi italiani usando il servizio
  Normattiva.it tramite URN-NIR (Uniform Resource Name – Norme In Rete).
  MANDATORY TRIGGERS: qualsiasi risposta contenente riferimenti normativi italiani
  (es. "art. X c.c.", "art. X c.p.c.", "d.lgs.", "legge n.", "r.d.", "d.p.r."),
  pareri legali, analisi giuridiche, atti processuali, contratti.
  Invocare PRIMA di formulare la risposta.
---

# Normattiva – Link a norme italiane

## Compatibilità runtime

Questa skill deve funzionare sia in ambienti Claude sia in ambienti OpenAI/Codex.

- **Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** quando la skill suggerisce una delega, puoi usare il subagente Haiku o il meccanismo `Agent(...)` se disponibile.
- **Se stai operando in Codex o in un ambiente OpenAI:** usa un subagente/tool multi-agent solo se l'ambiente lo espone esplicitamente; altrimenti genera i link direttamente nel modello principale seguendo le stesse regole.
- In ogni runtime, non produrre riferimenti normativi italiani nudi: il requisito principale della skill non cambia.

## Regola fondamentale

**Non è ammesso produrre testo con riferimenti normativi nudi.**
Ogni citazione di un articolo di legge, decreto, codice o disposizione normativa italiana
deve essere un link cliccabile verso Normattiva.it.

Esempi di output **non ammesso**:
- `art. 2122 c.c.`
- `art. 7 d.lgs. 231/2001`
- `art. 24 Cost.`

Esempi di output **corretto**:
- `[art. 2122 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2122)`
- `[art. 7 d.lgs. 231/2001](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2001-06-08;231~art7)`
- `[art. 24 Cost.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:costituzione:1947-12-27~art24)`

Prima di scrivere qualsiasi risposta che includa citazioni normative:
1. estrai tutti i riferimenti normativi presenti nella risposta pianificata;
2. genera i link corrispondenti usando il pattern e la quick lookup sotto;
3. sostituisci ogni riferimento nudo con il link inline nel testo finale.

---

## Pattern URL

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{YYYY-MM-DD};{numero}[:{allegato}][~art{N}][!vig=]
```

- Non URL-encodare `:` `;` `~` `!` — Normattiva li accetta testuali nella query string.
- Per i **codici storici (Regi Decreti)** il testo del codice è un allegato numerato del R.D.:
  includi sempre `:N` dopo il numero dell'atto (es. `262:2` per il c.c.).

---

## Quick Lookup – norme più frequenti

| Nome                  | Sigla       | Tipo URN          | Data           | Numero | All. |
|-----------------------|-------------|-------------------|----------------|--------|:----:|
| Codice Civile         | c.c.        | `regio.decreto`   | `1942-03-16`   | `262`  | `:2` |
| Cod. Proc. Civile     | c.p.c.      | `regio.decreto`   | `1940-10-28`   | `1443` | `:1` |
| Codice Penale         | c.p.        | `regio.decreto`   | `1930-10-19`   | `1398` | `:1` |
| Cod. Proc. Penale     | c.p.p.      | `decreto.del.presidente.della.repubblica` | `1988-09-22` | `447` | — |
| Legge Fallimentare    | l.fall.     | `regio.decreto`   | `1942-01-16`   | `267`  | `:1` |
| Costituzione          | Cost.       | `costituzione`    | `1947-12-27`   | —      | — |
| Statuto Lavoratori    | L. 300/1970 | `legge`           | `1970-05-20`   | `300`  | — |
| D.Lgs. 231/2001       | —           | `decreto.legislativo` | `2001-06-08` | `231` | — |
| D.Lgs. 196/2003 (Privacy) | —       | `decreto.legislativo` | `2003-06-30` | `196` | — |
| D.Lgs. 81/2008 (Sic. Lav.) | —      | `decreto.legislativo` | `2008-04-09` | `81`  | — |

> Per altri atti (D.Lgs. 36/2023, TUEL, T.U.I.R., ecc.) leggi `references/lookup-extended.md`.

### Tipo atto (principali)

`legge` · `regio.decreto` · `decreto.legislativo` · `decreto.legge` ·
`decreto.del.presidente.della.repubblica` · `costituzione`

---

## Versioni storiche di una norma

Quando il contesto riguarda fatti passati, norme ante-riforma o atti abrogati,
aggiungi `!vig=AAAA-MM-GG` all'URL per puntare alla versione vigente a quella data.

**Posizione del parametro**: sempre in coda, dopo `~artN` se presente:
- Solo atto: `...;numero[:{all}]!vig=AAAA-MM-GG`
- Con articolo: `...;numero[:{all}]~artN!vig=AAAA-MM-GG`

**Regole operative**:
1. Se l'utente specifica una data di riferimento (es. "fatti del 2019", "prima della riforma") → usa `!vig=` con la data appropriata.
2. Se citi una norma che risulta abrogata o integralmente riformata → segnalalo in testo, indica la norma sostituta e la data di decorrenza, e usa `!vig=data-anteriore` per linkare il testo storico.
3. Per la versione vigente oggi → ometti `!vig=` (comportamento default già corretto).

Consulta la tabella "Norme abrogate o integralmente riformate" in `references/lookup-extended.md` per l.fall., D.Lgs. 50/2016, art. 18 L. 300/1970 e Privacy.

---

## Template Markdown

```markdown
<!-- Codice storico (con allegato) -->
[art. {N} {sigla}](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{numero}:{all}~art{N})

<!-- Atto moderno (senza allegato) -->
[art. {N} {sigla}](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{numero}~art{N})
```

---

## Esempi

```markdown
[art. 2051 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2051)
[art. 83 c.p.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443:1~art83)
[art. 30bis c.p.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443:1~art30bis)
[art. 42 l.fall.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-01-16;267:1~art42)
[art. 24 Cost.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:costituzione:1947-12-27~art24)
[art. 35, L. 300/1970](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art35)
[art. 7, co. 1, L. 300/1970](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:1970-05-20;300~art7-com1)
```

---

## Workflow

### 1. Norma nella quick lookup → link inline

Preleva tipo, data, numero e allegato dalla tabella. Componi e restituisci subito il link.

### 2. Norma NON nella quick lookup → leggi il riferimento esteso

Leggi `references/lookup-extended.md` per la tabella completa, i tipi di atto rari,
le partizioni dettagliate (comma, lettera, allegato…) e gli errori comuni.

### 3. Più link in un singolo blocco di testo → delega condizionale

Quando l'utente chiede di linkare **tutti i riferimenti normativi** presenti in un documento
o in un elenco (tipicamente 5+ link), puoi delegare la generazione se il runtime offre
un subagente adatto. Questo libera il modello principale per attività più complesse e riduce
il consumo di token.

**Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** usa il subagente
Haiku quando disponibile.

**Se stai operando in Codex o in un ambiente OpenAI:** usa un subagente OpenAI/Codex solo se
disponibile; se non lo è, resta nel modello principale e genera direttamente l'elenco dei link.

**Percorso Claude — come spawna il subagente:**

```
Agent(
  model="haiku",
  prompt="""
Sei un assistente legale italiano. Genera link Normattiva in formato Markdown.

REGOLA PRINCIPALE:
URL = https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{YYYY-MM-DD};{numero}[:{allegato}][~art{N}][!vig=AAAA-MM-GG]
Non URL-encodare : ; ~ !

LOOKUP (tipo | data | numero | allegato):
- c.c.           → regio.decreto | 1942-03-16 | 262  | :2
- c.p.c.         → regio.decreto | 1940-10-28 | 1443 | :1
- c.p.           → regio.decreto | 1930-10-19 | 1398 | :1
- c.p.p.         → decreto.del.presidente.della.repubblica | 1988-09-22 | 447 | (nessuno)
- l.fall.        → regio.decreto | 1942-01-16 | 267  | :1  ⚠️ ABROGATA dal 15/07/2022
- Cost.          → costituzione  | 1947-12-27 | —    | (nessuno)
- L.300/1970     → legge         | 1970-05-20 | 300  | (nessuno)
- D.Lgs.231/2001 → decreto.legislativo | 2001-06-08 | 231 | (nessuno)
- D.Lgs.196/2003 → decreto.legislativo | 2003-06-30 | 196 | (nessuno)
- D.Lgs.81/2008  → decreto.legislativo | 2008-04-09 | 81  | (nessuno)
- D.Lgs.14/2019  → decreto.legislativo | 2019-01-12 | 14  | (nessuno)  [sostituisce l.fall. dal 15/07/2022]

Per articoli "bis/ter": ~art30bis, ~art1ter ecc.
Per comma: ~art{N}-com{C}
Per versioni storiche: aggiungi !vig=AAAA-MM-GG in coda (es. ~art18!vig=2015-03-06)

NORME ABROGATE — segnala in output:
- l.fall. → abrogata dal 15/07/2022; per procedure ante-2022 usa !vig=2022-07-14
- D.Lgs.50/2016 → abrogato dal 01/07/2023; sostituito da D.Lgs.36/2023

RIFERIMENTI DA LINKARE:
{lista_riferimenti}

Restituisci SOLO i link Markdown, uno per riga. Se una norma è abrogata, aggiungi nota inline.
"""
)
```

Sostituisci `{lista_riferimenti}` con i riferimenti estratti dal testo dell'utente.
