# Legal Routing — Query Legali IT

## Albero decisionale completo

```
Query dominio legale-it
│
├── Sotto-tipo: NORMATIVA
│   (art. X c.c., d.lgs. N/AAAA, legge N/AAAA, Cost., c.p.c., ecc.)
│   │
│   ├── Skill Normattiva installata?
│   │   ├── Sì → Invoca skill Normattiva — 0 chiamate SearXNG
│   │   └── No → SearXNG IT, query su Brocardi/Normattiva.it
│   │              + avviso installazione (1 volta per sessione)
│
├── Sotto-tipo: GIURISPRUDENZA
│   (sentenze, Cassazione, TAR, Corte d'Appello, pronunce, ordinanze)
│   │
│   ├── MCP BuddaLaw disponibile?
│   │   (verifica: tool `search_case_law` o `get_judgement` attivi in sessione)
│   │   │
│   │   ├── Sì → Chiedi all'utente:
│   │   │         "Per questa ricerca posso usare:
│   │   │          A) BuddaLaw — banca dati giuridica strutturata (più preciso)
│   │   │          B) SearXNG — ricerca web generale (più ampio)
│   │   │          Quale preferisci?"
│   │   │         → Esegui la fonte scelta dall'utente
│   │   │
│   │   └── No → SearXNG IT, `time_range: year` se "ultime/recenti"
│
└── Sotto-tipo: DOTTRINA / PRASSI / COMMENTI
    (commenti, prassi, circolari, interpretazioni, note a sentenza,
     pareri, articoli di dottrina, notizie giuridiche)
    │
    └── SearXNG IT sempre
        Fonti: Altalex, Il Sole 24 Ore Diritto, Diritto.it, Studio Cataldi,
               Giurisprudenza Italiana, Riviste online specializzate
```

---

## Come rilevare BuddaLaw disponibile

Verifica che almeno uno di questi tool sia nella lista tool attivi della sessione:
- `search_case_law`
- `get_judgement`
- `mcp__068e2081-c206-42db-be65-2e6e321cc5a0__search_case_law`

Se questi tool non compaiono tra quelli disponibili → BuddaLaw non è connesso → vai diretto a SearXNG senza chiedere all'utente.

---

## Tool BuddaLaw rilevanti per tipo

| Tipo ricerca | Tool BuddaLaw | Note |
|---|---|---|
| Sentenze per argomento | `search_case_law` | Passa la query come testo libero |
| Sentenza specifica (numero noto) | `get_judgement` | Richiede identificativo sentenza |
| Articoli di legge nel DB | `search_articles` | Cerca testo normativo nel DB BuddaLaw |
| Contratti tipo | `search_contracts`, `list_contracts` | Per template contrattuali |
| Atti processuali | `search_processual_acts` | Per modelli di atti |

---

## Messaggi avviso standard

### Normattiva non installata (mostra 1 volta per sessione)
```
ℹ️ La skill Normattiva non è installata. Puoi installarla da:
https://github.com/avvocati-e-mac/skill-legali/blob/main/normattiva
Una volta installata, ogni riferimento normativo nella risposta diventerà
un link cliccabile diretto alla norma su Normattiva.it.
```

### BuddaLaw non disponibile (nessun avviso — vai silenziosamente a SearXNG)
Nessun messaggio. Usa SearXNG IT come fallback naturale.

---

## Combinazione SearXNG + Normattiva nella stessa risposta

Scenario tipico: ricerca di dottrina che nel testo cita articoli di legge.

**Sequenza corretta:**
1. SearXNG cerca la dottrina → restituisce contenuto con citazioni normative nude
2. Sonnet sintetizza la risposta in bozza (con art. X c.c. come testo)
3. Sonnet estrae tutti i riferimenti normativi dalla bozza
4. Se Normattiva installata → invoca skill Normattiva sulla lista estratta
5. Sostituisce ogni riferimento nudo con il link Normattiva.it
6. Presenta la risposta finale

**Non** invocare Normattiva prima della sintesi — serve prima avere il testo per sapere quali norme linkare.

---

## Segnali per classificare sotto-tipo legale

### GIURISPRUDENZA — parole chiave
`sentenza`, `sentenze`, `pronuncia`, `ordinanza`, `decreto`, `Cassazione`, `TAR`,
`Corte d'Appello`, `Consiglio di Stato`, `Corte Costituzionale`, `giurisprudenza`,
`massima`, `precedenti`, `orientamento giurisprudenziale`, `in sede di legittimità`

### NORMATIVA — parole chiave
`art.`, `articolo`, `comma`, `c.c.`, `c.p.c.`, `c.p.`, `Cost.`, `d.lgs.`, `d.l.`,
`legge`, `r.d.`, `d.p.r.`, `normativa`, `disposizione`, `testo unico`, `codice`

### DOTTRINA — parole chiave
`dottrina`, `commento`, `prassi`, `circolare`, `interpretazione`, `parere`,
`nota a sentenza`, `articolo`, `contributo`, `in dottrina`, `secondo la dottrina`,
`opinione`, `orientamento dottrinale`, `notizia giuridica`, `aggiornamento normativo`

Se la query contiene segnali misti (es. "art. 1341 c.c. secondo la Cassazione"):
- Presenza di art. + sentenza → tratta come **normativa** per Normattiva + **giurisprudenza** per BuddaLaw
- Esegui entrambe se entrambe le skill sono disponibili, combina i risultati

---

## Multi-dominio: legale-it + altro dominio (tie-break)

Caso diverso dai segnali misti *interni* al legale (sopra): qui la query mescola il dominio
legale con un dominio **non** legale (es. ai-generativa, informatica). Esempio:
"implicazioni legali GDPR dell'uso di LLM in azienda".

Regola di tie-break (allineata a Step 0c punto 5 in SKILL.md):
1. Se il **verbo/oggetto principale** indica chiaramente l'ambito → usa quello senza chiedere
   (es. "*quali norme* regolano gli LLM" → primario = legale-it; "*come funziona* l'LLM che
   tratta dati personali" → primario = ai-generativa).
2. Se i due ambiti sono **paritari** → chiedi all'utente con lo stesso pattern A/B usato per
   BuddaLaw-vs-SearXNG:
   ```
   La tua domanda tocca due ambiti. Su cosa mi concentro?
    A) Profilo legale (norme/sentenze IT) — fonti giuridiche italiane
    B) Profilo tecnico (come funziona la tecnologia) — fonti AI/tech
   ```
3. Dopo la scelta → **1 sola ricerca** sul dominio scelto, con i suoi parametri. Niente
   doppia ricerca salvo richiesta esplicita.
