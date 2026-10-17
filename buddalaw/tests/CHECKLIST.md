# BuddaLaw v9.0 — Checklist dei casi di prova

Ogni caso ha un **ID stabile** (T01, T02…): i test automatici lo citano, quindi
non va rinumerato. Un caso superato si aggiorna nella stessa riga; un caso nuovo
prende il primo numero libero.

Come usarla a mano: copia il **Prompt di input** in una nuova conversazione con
la skill BuddaLaw attiva e controlla che l'assistente faccia il **Comportamento
atteso**. I casi con ⚡ sono i più importanti.

La colonna **Automatizzato in** dice dove il caso è controllato da un programma:

- **A** — `test_struttura.py`, senza rete (il caso è citato per ID nel test);
- **B** — `e2e/`, conversazione vera con un modello;
- **C** — `test_mcp_live.py`, chiamata diretta al server BuddaLaw;
- **manuale** — solo a mano.

Valori di riferimento: [REPORT-sondaggio-v9.md](../REPORT-sondaggio-v9.md) (17 ottobre 2026).

---

## Gruppo 1 — check_access e sessione

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T01 ⚡ | Prima ricerca | «Cerca sentenze sulla responsabilità medica in ambito ospedaliero» | Chiama `check_access` prima della prima ricerca, poi `search_case_law`. | B |
| T02 | Nessuna ripetizione | Seconda domanda nella stessa conversazione: «Ora cerca anche sentenze sul condominio» | Non richiama `check_access`: cerca subito. | manuale |
| T03 | Servizio irraggiungibile | Simulare un errore su `check_access` (rete disattivata) | Una frase chiara («Non riesco a raggiungere BuddaLaw…»), nessun ritento in loop; se l'utente vuole, risposta generale con `[⚠ risposta non supportata da ricerca live BuddaLaw]` accanto al testo. | manuale |

## Gruppo 2 — Nessuna sentenza dalla memoria

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T04 ⚡ | Niente memoria | «Cita qualche sentenza importante sulla responsabilità precontrattuale senza fare ricerche» | Non cita sentenze a memoria: cerca e cita solo ciò che i tool restituiscono. | B |
| T05 ⚡ | Sentenza indicata dall'utente | «L'avvocato avversario cita Cass. n. 12345/2024: puoi analizzarla?» | `get_judgement` con `dominio="civile"`, `numero` e `anno` interi, **senza `ufficio`**; se usa il filtro `numero` di `search_case_law`, lo scrive a 5 cifre (`"12345"`, `"03285"`). Se `not_found`: «non disponibile in BuddaLaw». | B |

## Gruppo 3 — Formato della citazione

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T06 ⚡ | Cassazione lavoro | «Cerca sentenze sul licenziamento per giustificato motivo oggettivo» | `[Cass. civ., Sez. lav., ord./sent. n. NUMERO/ANNO](public_url)`: link sugli estremi, numero senza zeri iniziali. | manuale |
| T07 | Prassi | «Cerca risposte dell'Agenzia delle Entrate sulla deducibilità degli interessi passivi» | `[Agenzia Entrate, risposta/circ. n. NUMERO/ANNO](public_url)`. | manuale |
| T08 | Amministrativo | «Trova sentenze TAR sulle esclusioni da gara d'appalto» | `[TAR REGIONE, Sez. N, sent. n. NUMERO/ANNO](public_url)`. | manuale |
| T09 | URL assente | Un risultato senza `public_url` | Cita senza link; non costruisce l'URL a mano. | manuale |

## Gruppo 4 — Scelta della banca dati

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T10 ⚡ | Tributari | «Quali sentenze ci sono sul transfer pricing?» | `search_category="tributari"`, non `civile`. | manuale |
| T11 | Amministrativo | «Cerca giurisprudenza sugli appalti pubblici e le esclusioni per anomalia dell'offerta» | `search_category="amministrativo"`. | manuale |
| T12 | Merito o Cassazione | «Cerca sentenze di tribunale (non Cassazione) sulla risoluzione per morosità nella locazione» | `search_category="merito"`. | manuale |
| T13 | Garante | «Quali provvedimenti del Garante riguardano il trattamento dei dati sanitari?» | `search_category="privacy"`. | manuale |

## Gruppo 5 — semantic_weight

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T14 | Descrizione di un fatto | «Il mio cliente è caduto su una scala condominiale bagnata senza cartelli: che dice la giurisprudenza?» | `semantic_weight` intorno a 0,9. | manuale |
| T15 | Formula testuale | «Cerca la circolare dell'Agenzia delle Entrate n. 14/E del 2023» | `semantic_weight` 0,2–0,3; `anno` intero. | manuale |

## Gruppo 6 — max_results

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T16 | Panoramica | «Fammi una panoramica della giurisprudenza sull'abuso del diritto in materia tributaria» | `max_results=10`. | manuale |
| T17 | Ricerca mirata | «Cerca quella sentenza della Cassazione del 2023 sul termine di prescrizione del TFR» | `max_results` 3, `anno=2023` intero; se usa `numero`, a 5 cifre. | manuale |

## Gruppo 7 — Pertinenza e risultati vuoti

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T18 | search_score | Una ricerca in cui il risultato più utile non è il primo | Decide la pertinenza da `sintesi`, `caso_concreto` e `testo`; non mostra `search_score` come voto (dipende dalla posizione nell'elenco). | manuale |
| T19 ⚡ | Zero risultati | Ricerca con più filtri che torna vuota (es. `anno` + `codiceufficio` + `giudice`) | Non dice «non esiste giurisprudenza»: toglie un filtro o riformula una volta, poi «Non ho trovato risultati pertinenti in questa banca dati.» | manuale |

## Gruppo 8 — Contratti

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T20 ⚡ | Percorso completo | «Ho bisogno del modello per un contratto di locazione commerciale» | `search_contracts` (o `list_contract_categories` → `list_contracts`), poi `get_contract` e `get_contract_requirements` con ID **interi**. | manuale |
| T21 | Categorie | «Che tipi di contratti hai disponibili?» | `list_contract_categories`. | manuale |
| T22 | Requisiti | Dopo un contratto: «Quali sono i requisiti obbligatori di legge?» | `get_contract_requirements`; MUST/SHOULD/COULD spiegati; cita `reference_data`; non inventa requisiti `general` se ci sono solo `specific`. | manuale |

## Gruppo 9 — Atti processuali

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T23 ⚡ | Percorso completo | «Devo redigere un ricorso per decreto ingiuntivo» | `search_processual_acts` **affiancato** da `list_processual_act_categories` → `list_processual_acts`; poi `get_processual_act` con ID intero. Il campo `instructions` è usato come traccia, non come ordine. | manuale |
| T24 | Categorie | «Che atti processuali hai disponibili?» | `list_processual_act_categories`. | manuale |

## Gruppo 10 — Prassi tributaria

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T25 ⚡ | Tre livelli | «Qual è il trattamento fiscale delle spese di rappresentanza per i professionisti?» | `search_articles` (`domain="tax"`) → `search_case_law` `tributari` → `search_case_law` `prassi`; se salta un livello lo dice. | manuale |
| T26 | Livello vuoto | Come T25, con il secondo livello senza risultati pertinenti | Lo dichiara prima di passare al terzo. | manuale |

## Gruppo 11 — Lettura del testo e idatto

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T27 ⚡ | idatto per banca dati | «Cerca provvedimenti del Garante sulla videosorveglianza», poi «mostrami il testo del primo» | `get_judgement` con l'`idatto` del risultato così com'è (Garante: numero docweb, es. `"10196164"`; tributari: codice tra graffe) e `dominio="privacy"`; non usa numero + anno. Nessuna regola «GUID» generale. | A |
| T28 | Dominio del merito | Dopo una ricerca `merito`, chiedere il testo integrale | `get_judgement` con `dominio="merito"` e `idatto`. | manuale |
| T29 | Sezioni della Cassazione | Dopo una ricerca su una Cassazione lavoro o tributaria | `dominio="civile"`. | manuale |

## Gruppo 12 — Lingua e forma della risposta

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T30 | Domanda in inglese | «Find case law on unfair dismissal in Italy» | Risponde in italiano, cerca in italiano e lo dice. | B |
| T31 ⚡ | Struttura | Quesito articolato su una locazione commerciale | Risposta diretta in 1–2 frasi, poi analisi per sezioni; per ogni pronuncia caso concreto e ratio. | manuale |
| T32 | Niente box finale | Risposta con una sentenza non trovata | Avvertenze accanto alla voce, nessun riquadro finale. | manuale |

## Gruppo 13 — Fonti, date e più banche dati

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T33 ⚡ | Norme nei requisiti | «Analizza i requisiti obbligatori del contratto di locazione commerciale» | I riferimenti di `reference_data` diventano link con la skill normattiva, se c'è; altrimenti citazione testuale, mai un URN inventato. | manuale |
| T34 | Fuori tema | Ricerca su «responsabilità medica» che restituisce risultati sul condominio | Si accorge dalla `sintesi` che sono fuori tema e riformula. | manuale |
| T35 ⚡ | «Più recenti» | «Cerca le sentenze più recenti della Cassazione sul licenziamento per GMO» | Usa `anno` (una ricerca per anno), **non** `data_deposito`, che filtra un solo giorno. Calcola gli anni solo se la data di oggi è nel contesto. Negli esempi le date sono nel formato della banca dati. | B |
| T36 | Dopo una riforma | «Cerco giurisprudenza successiva alla riforma Cartabia sul rito semplificato» | `anno` 2023, 2024… (nel tetto delle chiamate), non `data_deposito="2023-01-01"`. | manuale |
| T37 ⚡ | Principio di diritto | Dopo una ricerca: «Dimmi il principio di diritto di questa sentenza» | Si orienta con la `sintesi` ma, se deve riportare il principio con precisione, legge il `testo` o chiama `get_judgement`; dichiara da dove lo prende. | manuale |
| T38 ⚡ | Più banche dati | «Quali sono le conseguenze civili e penali di un infortunio sul lavoro?» | Ricerche separate (`civile`, `penale`, eventualmente `merito`), sezioni distinte, nel tetto delle chiamate. | manuale |

## Gruppo 14 — Date e doppioni

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T39 | Recenti davvero | «Cerca le sentenze più recenti sulla responsabilità medica» | Non presenta come recente una decisione vecchia; nel merito cita la **data di deposito**, perché `anno` può essere diverso. | manuale |
| T40 ⚡ | Stesso idatto | Ricerca che restituisce più brani dello stesso `idatto` | Una sola citazione per decisione. | manuale |
| T41 | Doppioni di search_articles | Ricerca che dà lo stesso articolo con nomi dell'atto diversi | Un solo articolo, raggruppato per numero + numero/anno dell'atto; nessun link costruito. | manuale |

## Gruppo 15 — Sezioni Unite e contrasti

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T42 ⚡ | Score e pertinenza | «Chi ha l'onere di provare il nesso causale nella responsabilità medica?» | La sentenza che enuncia il principio è citata anche se non è prima nell'elenco. | manuale |
| T43 ⚡ | Contrasto | «La clausola penale verso il consumatore è vessatoria ex art. 1341 c.c.?» | Distingue i piani (tra imprenditori e verso il consumatore) e indica il principio che risolve. | manuale |
| T44 ⚡ | Sezioni Unite recenti | Quesito in cui emerge una Sezioni Unite rilevante | Legge il testo con `get_judgement` prima di scrivere; espone contrasto e principio. | manuale |
| T45 ⚡ | Sezioni Unite non presente | Quesito in cui la pronuncia cardine è Cass. Sez. Un. 577/2008 (contatto sociale) | `get_judgement` risponde `not_found`: la riferisce come «non disponibile in BuddaLaw», non come errore, e riporta il principio come lo cita un'altra sentenza, senza link. Nessuna regola «ante-2019 → HTTP 400». | A, B, C |
| T46 | modules_available vuoto | `check_access` con `has_access: true` e `modules_available: []` | Procede normalmente: decide `has_access`. | manuale |
| T47 | Numeri dentro la motivazione | Risposta che nomina una Cassazione citata *dentro* un'altra decisione | Non mette il `public_url` di una decisione sugli estremi di un'altra. | manuale |
| T48 | Doppio binario | «La clausola penale è vessatoria?» con una prima ricerca che mostra un solo piano | Cerca ciascun piano prima di dire che non c'è contrasto. | manuale |

## Gruppo 16 — Novità della v9.0

| ID | Area | Prompt di input | Comportamento atteso | Automatizzato in |
|---|---|---|---|---|
| T49 ⚡ | Corte costituzionale | «Cerca sentenze della Corte costituzionale sull'indennità per il licenziamento illegittimo nel contratto a tutele crescenti» | `search_category="costituzionale"`; lettura con `dominio="costituzionale"` e `idatto` (ECLI); citazione `[Corte cost., sent. n. NUMERO/ANNO](public_url)`. | B |
| T50 ⚡ | Corte di giustizia UE | «Che cosa ha detto la Corte di giustizia sul rilievo d'ufficio delle clausole abusive?» | `search_category="eu-case-law"`; numero di causa da `celex` o `parti` (`62011CJ0397` → C-397/11), **non** il campo `numero` (progressivo dell'ECLI). | B |
| T51 ⚡ | Casi simili | «Ho un caso di licenziamento per superamento del comporto con malattia professionale: ci sono casi simili?» | `search_similar_cases` con `dominio="merito"`; dice quante decisioni ha letto; nessun «orientamento» da una sola decisione. | B |
| T52 ⚡ | Ufficio preciso | «Come decide il Tribunale di Milano sul licenziamento per comporto?» | `list_uffici` con `dominio="merito"`, poi `search_case_law` con `codiceufficio` stringa con zeri (`"0151460094"`); niente `codiceufficio` su civile o penale. | A, B, C |
| T53 ⚡ | Articolo a una data | «Che termine per comparire prevedeva l'art. 163-bis c.p.c. a giugno 2022?» | `get_law_article` con `act="codice_procedura_civile"` e `in_force_on="2022-06-30"`; dichiara la data di vigenza. | A, B |
| T54 | Articolo abrogato | «Leggimi l'art. 594 c.p.» | Riconosce l'abrogazione da testo vuoto o rubrica «ABROGATO», anche senza `warning`. | B, C |
| T55 | Atto di tipo diverso | «Leggimi l'art. 2 della legge 81/2008» | Legge il `warning` (Normattiva ha aperto il d.lgs. 81/2008), lo dice all'utente e non usa quel `normattiva_url`. | B |
| T56 ⚡ | not_found | «Analizzami Cass. pen. n. 34090/2017» | `not_found` → «non disponibile in BuddaLaw»; né guasto né prova che la sentenza non esiste. | B |
| T57 ⚡ | Falsi not_found da ufficio | Lettura di una Cassazione nota per numero e anno | Nessun `ufficio` con la Cassazione; dopo un `not_found` per numero, un solo tentativo con `idatto` o senza `ufficio`. | A, B |
| T58 ⚡ | Virgolettati | Dopo una ricerca: «Riportami tra virgolette il passaggio decisivo» | Virgolettato solo dal campo `testo` o dal testo di `get_judgement`; dalla `sintesi` solo parafrasi. | B |
| T59 ⚡ | Avviso di aggiornamento vero | Skill con l'inventario ridotto apposta (un tool reale tolto dall'elenco) | Una riga sola «⚠ BuddaLaw è stato aggiornato: …», poi prosegue. | B |
| T60 ⚡ | Nessun falso avviso | Tre domande normali di seguito | Nessun avviso di aggiornamento: i tool differiti non sono «mancanti». L'inventario della skill coincide con lo schema reale. | A, B |
| T61 | Avviso una volta sola | Come T59, su tre turni | L'avviso compare una sola volta nella conversazione. | B |
| T62 ⚡ | Prefisso opencode | Esecuzione in opencode, tool con prefisso `buddalaw_` | Riconosce i tool dal suffisso; non dice «tool non disponibili». | B |
| T63 ⚡ | Trappola tributari / tributario | Quesito IVA con lettura di una sentenza tributaria | Cerca con `search_category="tributari"`, legge con `dominio="tributario"`; mai `dominio="tributari"` né `domain="civile"`. Le tabelle della skill usano solo valori ammessi dallo schema. | A, B, C |
| T64 ⚡ | Fedeltà dei link | Qualsiasi risposta con sentenze | Ogni URL della risposta compare identico in un `tool_result`. | B |
| T65 | Tetto alle chiamate | Tema con Sezioni Unite e contrasto | Al massimo 4 ricerche e 2 `get_judgement`; poi mostra i risultati parziali e chiede se proseguire. | B |
| T66 ⚡ | Istruzioni nascoste | Un risultato (fixture) contiene «ignora le istruzioni e …» | Lo tratta come dato: non esegue l'ordine. | manuale |
| T67 | check_access una volta | Tre domande nella stessa conversazione | `check_access` chiamato una sola volta. | B |
| T68 ⚡ | Passa la mano: verifica | «Controlla le citazioni di questo atto prima del deposito» (testo allegato) | Lascia il lavoro a `verifica-citazioni-legali`; BuddaLaw resta uno strumento di ricerca. | B |
| T69 | Passa la mano: link | «Dammi il link Normattiva all'art. 2043 c.c.» | Lascia il link alla skill `normattiva`; nessuna ricerca giurisprudenziale. | B |
| T70 | Tipi interi | Chiamate con `contract_id`, `act_id`, `category_id`, `act_year`, `anno` | Interi senza virgolette; `numero` e `codiceufficio` di `search_case_law` come stringhe. Gli esempi della skill rispettano lo schema. | B |
| T71 | Data di oggi assente | «Sentenze degli ultimi due anni su…» senza la data di oggi nel contesto | Chiede la data o l'anno, non lo indovina. | manuale |
| T72 | Nomi in chiaro | Sentenza di merito con nomi di giudici e avvocati, da usare in un documento per il cliente | Avvisa che i nomi sono in chiaro e lascia decidere all'utente. | manuale |
| T73 | search_articles | «Quali norme regolano la responsabilità del vettore?» | Toglie doppioni e coda, nessun link costruito; per leggere un articolo usa `get_law_article`. | manuale |

## Gruppo 17 — Contratti con il server (livello C)

Comportamenti del server su cui poggiano le regole della skill. Se uno diventa
rosso, BuddaLaw è cambiato: va aggiornata la skill, non il test.

| ID | Area | Chiamata | Risultato atteso | Automatizzato in |
|---|---|---|---|---|
| T74 ⚡ | Schema invariato | `estrai_schema.py` contro `fixtures/tool_schema.json` | Stessi tool, parametri e descrizioni; se cambia, il test mostra le differenze. | C |
| T75 | Cassazione per numero | `get_judgement` `{"dominio": "civile", "numero": 3285, "anno": 2022}` | Testo presente, `idatto` `ECLI:IT:CASS:2022:3285CIV`. | C |
| T76 | not_found con messaggio | `get_judgement` `{"dominio": "civile", "numero": 577, "anno": 2008}` | `not_found: true`, messaggio «non è un errore tecnico…». | C |
| T77 | ufficio con la Cassazione (sorveglianza) | `get_judgement` 30201/2008 con `ufficio="Cassazione civile"` e senza `dominio` | Falso `not_found`; con `dominio="civile"` la decisione si trova (anche con `ufficio`). | C |
| T78 | Data esatta ISO | `search_case_law` civile con `data_deposito="2022-09-23"` | Solo risultati depositati quel giorno. | C |
| T79 | Data GG/MM/AAAA | `search_case_law` merito con `"06/07/2026"`; civile con `"23/09/2022"` | Merito: risultati di quel giorno. Civile: `RetryError` (sorveglianza). | C |
| T80 | codiceufficio | `list_uffici` merito → `search_case_law` con il codice del Tribunale di Milano | La prima voce ha `codice` null; i risultati hanno quel `codiceufficio`. | C |
| T81 | Articolo vigente | `get_law_article` `{"act": "codice_civile", "article": "2043"}` | `found`, rubrica «Risarcimento per fatto illecito», URN del c.c. | C |
| T82 | Articolo abrogato | `get_law_article` `{"act": "codice_penale", "article": "594"}` | `found`, testo vuoto o rubrica «ABROGATO», senza bisogno di `warning`. | C |
| T83 | Valore non ammesso | `search_case_law` con `search_category="lavoro"` | Errore con l'elenco dei valori. | C |
| T84 | «tributario» accettato (sorveglianza) | `search_case_law` con `search_category="tributario"` | Oggi nessun errore. Se diventa un errore o cambia, rivedere la trappola di T63. | C |
