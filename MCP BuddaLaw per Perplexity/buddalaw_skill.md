# BuddaLaw Legal Research Skill — Guida per Perplexity

## Scopo

Questa skill descrive come usare il connettore MCP BuddaLaw per gestire quesiti legali complessi che richiedono ricerche multi-step su giurisprudenza, normativa e prassi amministrativa italiana.

---

## Workflow consigliato per quesiti complessi

Quando un quesito legale tocca più argomenti (es. A, B e C), seguire questi passaggi in sequenza:

### 1. Scomposizione del quesito

Prima di lanciare qualsiasi ricerca, scomporre il quesito in sotto-problemi:

- Identificare le **questioni giuridiche distinte** (es. requisiti formali, presupposti sostanziali, orientamento della Cassazione)
- Identificare le **norme rilevanti** (codice civile, penale, tributario, ecc.)
- Identificare il **tipo di fonte** più utile per ciascuna questione (sentenze, prassi, normativa)

### 2. Ricerca normativa (search_articles)

Per ogni argomento, cercare prima la base normativa:

| Dominio | Quando usarlo |
|---------|---------------|
| `civil_code` | Contratti, obbligazioni, famiglia, proprietà |
| `civil_procedure` | Processo civile ordinario |
| `special_civil` | Leggi speciali (locazioni, consumatori, ecc.) |
| `criminal` | Reati, pene, procedura penale |
| `tax` | IVA, imposte dirette, accertamento |
| `privacy` | GDPR, Codice Privacy |

### 3. Ricerca giurisprudenziale (search_case_law)

Dopo la norma, cercare l'interpretazione giurisprudenziale. Scegliere la banca dati in base all'argomento:

| Banca dati (`search_category`) | Contenuto |
|-------------------------------|-----------|
| `civile` | Cassazione civile (sezioni unite, sezioni semplici) |
| `penale` | Cassazione penale |
| `tributari` | Corti di Giustizia Tributaria I° e II° grado |
| `prassi` | Circolari, Provvedimenti, Interpelli Agenzia Entrate |
| `merito` | Tribunali e Corti d'Appello |
| `privacy` | Provvedimenti del Garante della Privacy |
| `amministrativo` | TAR e Consiglio di Stato |

### 4. Approfondimento sentenza specifica (get_judgement)

Quando un risultato di ricerca è particolarmente rilevante:

- Recuperare il testo completo con `get_judgement` passando `dominio` e `idatto`
- Per sentenze di Cassazione: usare sempre `dominio = "civile"` o `"penale"` (non "lavoro" o "tributario")
- Per scaricare il PDF originale: usare `get_judgement_pdf`

---

## Schema operativo per quesiti multi-argomento

```
QUESITO COMPLESSO (es. argomenti A, B, C)
│
├── Argomento A
│   ├── search_articles (norma di riferimento)
│   └── search_case_law (orientamento giurisprudenziale)
│
├── Argomento B
│   ├── search_articles (norma di riferimento)
│   └── search_case_law + eventuale get_judgement
│
└── Argomento C
    ├── search_articles
    ├── search_case_law
    └── (se tributario) search_case_law su "prassi" per circolari AE
```

---

## Come formulare le query

Usare linguaggio naturale giuridico italiano. Esempi efficaci:

- `"responsabilità del vettore per perdita del bagaglio"`
- `"deducibilità fiscale spese di rappresentanza professionista"`
- `"opposizione a decreto ingiuntivo termini decadenza"`
- `"licenziamento per giustificato motivo soggettivo reintegra"`

Parametri opzionali utili:
- `anno`: filtrare per anno (es. 2023, 2024)
- `numero`: numero specifico di sentenza
- `ufficio`: es. `"Cassazione civile"`, `"Tribunale Milano"`
- `semantic_weight`: aumentare verso `1.0` per ricerche concettuali; diminuire verso `0.3` per ricerche per parole chiave esatte

---

## Ricerca contratti e atti processuali

Per contratti e atti processuali, usare i tool dedicati:

- `search_contracts` → trova template contrattuali per parole chiave
- `get_contract_requirements` → requisiti normativi obbligatori per un contratto
- `search_processual_acts` → trova atti processuali (citazioni, ricorsi, memorie)
- `get_processual_act` → template completo con istruzioni per la generazione

---

## Esempio pratico

**Quesito:** "Quali sono le conseguenze del mancato pagamento del canone di locazione commerciale? Cercare norme, sentenze di merito e della Cassazione."

**Piano di ricerca:**

1. `search_articles(domain="special_civil", query="locazione commerciale risoluzione per inadempimento")`
2. `search_case_law(search_category="merito", query="risoluzione contratto locazione commerciale morosità")`
3. `search_case_law(search_category="civile", query="risoluzione locazione commerciale mancato pagamento canone")`
4. Se trovata sentenza rilevante → `get_judgement(dominio="merito", idatto=...)` o `get_judgement(dominio="civile", idatto=...)`

---

## Note operative

- **Verificare l'accesso** con `check_access` all'inizio di ogni sessione
- **Max results**: usare `max_results=10` per ricerche esplorative, `max_results=3` per ricerche mirate
- **Iterare**: se i risultati della prima ricerca sono poco pertinenti, riformulare la query con termini più specifici o cambiare `semantic_weight`
- **Citare sempre**: ogni affermazione estratta da BuddaLaw deve essere attribuita alla fonte (numero sentenza, anno, ufficio)

