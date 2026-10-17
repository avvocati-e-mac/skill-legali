# BuddaLaw — esempi di query per materia

Punti di partenza da adattare al caso concreto. Le query più efficaci sono frasi complete in linguaggio giuridico italiano, non parole isolate. Per i filtri (ufficio, giudice, anno) vedi [filtri-e-uffici.md](filtri-e-uffici.md).

## Indice

- Giurisprudenza: civile, lavoro, penale, tributario, prassi, merito, amministrativo, privacy, Corte costituzionale, Unione europea
- Casi simili (`search_similar_cases`)
- Lettura di un articolo (`get_law_article`)
- Contratti e atti processuali

---

## Diritto civile (`search_category="civile"`)

| Quesito tipo | Query efficace |
|---|---|
| Responsabilità del vettore | `"responsabilità del vettore per perdita del bagaglio"` |
| Risoluzione contratto | `"risoluzione contratto per inadempimento grave obbligazione principale"` |
| Usucapione | `"acquisto per usucapione possesso continuato ultraventennale"` |
| Responsabilità medica | `"responsabilità medica struttura sanitaria omissione diagnosi"` |
| Condominio | `"delibera condominiale invalidità vizio procedura convocazione"` |
| Successioni | `"collazione donazione erede quota legittima"` |
| Prescrizione | `"prescrizione ordinaria decennale interruzione atto stragiudiziale"` |
| Clausola abusiva consumatori | `"clausola abusiva contratto consumatore nullità parziale"` |

---

## Diritto del lavoro (`search_category="civile"`)

La Cassazione lavoro sta in `civile` (non esiste `search_category="lavoro"`); per i tribunali usa `merito`.

| Quesito tipo | Query efficace |
|---|---|
| Licenziamento | `"licenziamento per giustificato motivo soggettivo reintegra tutela reale"` |
| Mobbing | `"mobbing comportamento persecutorio danno esistenziale lavoratore"` |
| Demansionamento | `"demansionamento illegittimo risarcimento professionalità"` |
| Ferie non godute | `"ferie non godute monetizzazione illegittimità accordo forfettario"` |
| Sedi protette | `"sede aziendale sedi protette trasferimento divieto"` |
| Lavoro part-time | `"lavoro part-time trasformazione diritto precedenza tempo pieno"` |

---

## Diritto penale (`search_category="penale"`)

| Quesito tipo | Query efficace |
|---|---|
| Truffa contrattuale | `"truffa contrattuale artifici raggiri danno patrimoniale"` |
| Appropriazione indebita | `"appropriazione indebita elemento soggettivo uso temporaneo"` |
| Bancarotta fraudolenta | `"bancarotta fraudolenta distrazione beni fallimento dolo specifico"` |
| Reati informatici | `"accesso abusivo sistema informatico condizioni configurabilità"` |
| Stalking | `"atti persecutori stalking misure cautelari ammonimento questura"` |
| Diffamazione | `"diffamazione mezzo stampa social media diritto di critica"` |

---

## Diritto tributario (`search_category="tributari"`)

| Quesito tipo | Query efficace |
|---|---|
| IVA operazioni inesistenti | `"operazioni inesistenti IVA responsabilità cessionario buona fede"` |
| Accertamento sintetico | `"accertamento sintetico redditometro onere prova contribuente"` |
| Sanzioni cumulo | `"sanzioni tributarie cumulo giuridico violazioni plurime"` |
| Transfer pricing | `"prezzi di trasferimento documentazione esimente sanzioni"` |
| Abuso del diritto | `"abuso del diritto elusione fiscale operazione priva di sostanza economica"` |
| Compensazione IVA | `"compensazione crediti IVA limite annuale visto conformità"` |

---

## Prassi Agenzia Entrate (`search_category="prassi"`)

| Quesito tipo | Query efficace |
|---|---|
| Spese di rappresentanza | `"deducibilità fiscale spese di rappresentanza professionista autonomo"` |
| Bonus edilizi | `"superbonus 110 cessione credito responsabilità cessionario"` |
| IVA servizi digitali | `"IVA servizi digitali residenza fiscale criteri identificazione"` |
| Fatturazione elettronica | `"fatturazione elettronica obbligo professionisti regime forfettario"` |
| Agevolazioni R&S | `"credito imposta ricerca e sviluppo requisiti documentazione"` |

---

## Merito (`search_category="merito"`)

Per un tribunale preciso: `list_uffici` con `dominio="merito"`, poi `codiceufficio`. Cita con ufficio e data di deposito.

| Quesito tipo | Query efficace |
|---|---|
| Locazione commerciale | `"risoluzione contratto locazione commerciale morosità grave inadempimento"` |
| Responsabilità amministratore | `"responsabilità amministratore società di capitali azione revocatoria"` |
| Decreto ingiuntivo | `"opposizione decreto ingiuntivo termini decadenza fondatezza"` |
| Sfratto | `"sfratto per morosità locazione abitativa convalida"` |
| Separazione | `"separazione giudiziale assegno mantenimento figli minorenni"` |

---

## Diritto amministrativo (`search_category="amministrativo"`)

| Quesito tipo | Query efficace |
|---|---|
| Esclusione gara appalto | `"esclusione gara appalto irregolarità documentazione offerta"` |
| Silenzio-inadempimento PA | `"silenzio inadempimento PA termine procedimentale ricorso TAR"` |
| Espropriazione | `"indennità espropriazione calcolo valore venale area edificabile"` |
| Autorizzazione edilizia | `"diniego permesso di costruire motivazione vizi procedimentali"` |
| Accesso agli atti | `"accesso documentale diniego PA interesse diretto concreto attuale"` |

---

## Privacy e GDPR (`search_category="privacy"`)

| Quesito tipo | Query efficace |
|---|---|
| Videosorveglianza lavoro | `"videosorveglianza luoghi di lavoro informativa dipendenti"` |
| Marketing diretto | `"consenso trattamento dati marketing diretto revoca effetti"` |
| Data breach | `"violazione dati personali obbligo notifica Garante 72 ore"` |
| Diritto all'oblio | `"diritto all'oblio deindicizzazione motore di ricerca interesse pubblico"` |
| Profilazione | `"profilazione automatizzata decisione individuale contestazione"` |

---

## Corte costituzionale (`search_category="costituzionale"`)

| Quesito tipo | Query efficace |
|---|---|
| Illegittimità di una norma | `"questione di legittimità costituzionale indennità licenziamento illegittimo tutele crescenti"` |
| Principio di uguaglianza fiscale | `"capacità contributiva principio di progressività imposta illegittimità"` |
| Diritti in materia di famiglia | `"attribuzione del cognome ai figli illegittimità costituzionale"` |

Lettura: `get_judgement` con `dominio="costituzionale"` e l'`idatto` del risultato (ECLI, es. `ECLI:IT:COST:2025:83`). Con il solo numero serve anche `ufficio`: meglio cercare prima. Citazione: `[Corte cost., sent. n. NUMERO/ANNO](public_url)`, `ord. n.` per le ordinanze.

---

## Unione europea (`search_category="eu-case-law"`)

| Quesito tipo | Query efficace |
|---|---|
| Clausole abusive | `"clausole abusive contratti stipulati con i consumatori rilievo d'ufficio giudice nazionale"` |
| Rinvio pregiudiziale | `"rinvio pregiudiziale interpretazione direttiva effetto diretto"` |
| Trasferimento dati | `"trasferimento dati personali paesi terzi adeguatezza garanzie"` |

Il campo `numero` è il progressivo dell'ECLI, non il numero di causa: ricava C-…/… o T-…/… da `parti` o da `celex` (`62011CJ0397` → C-397/11). Citazione: `[CGUE, sent. 30 maggio 2013, C-397/11](url)`; per il Tribunale `[Trib. UE, sent. …, T-…/…](url)`. Lettura: `dominio="eu-case-law"` con l'`idatto`.

---

## Casi simili (`search_similar_cases`, solo merito)

Descrivi il fatto, non il principio:

| Situazione | Query efficace |
|---|---|
| Comporto | `"lavoratore licenziato per superamento del periodo di comporto con assenze per malattia professionale"` |
| Infiltrazioni | `"infiltrazioni d'acqua dal lastrico solare danni all'appartamento sottostante responsabilità del condominio"` |
| Sinistro stradale | `"pedone investito sulle strisce pedonali concorso di colpa"` |

```json
{"tool": "search_similar_cases", "arguments": {"query": "lavoratore licenziato per superamento del periodo di comporto con assenze per malattia professionale", "dominio": "merito", "max_results": 10}}
```

Restringi con `codiceufficio` (da `list_uffici`) o `anno`. Di' quante decisioni hai letto: una sola non fa un orientamento.

---

## Lettura di un articolo (`get_law_article`)

| Richiesta | Chiamata |
|---|---|
| art. 2043 c.c. vigente | `{"act": "codice_civile", "article": "2043"}` |
| art. 163-bis c.p.c. nel 2022 | `{"act": "codice_procedura_civile", "article": "163-bis", "in_force_on": "2022-06-30"}` |
| art. 14 L. 689/1981 | `{"act_type": "legge", "act_year": 1981, "act_number": 689, "article": "14"}` |
| art. 2 d.lgs. 81/2008 | `{"act_type": "decreto_legislativo", "act_year": 2008, "act_number": 81, "article": "2"}` |
| art. 4 d.m. 55/2014 | `{"act_type": "decreto_ministeriale", "act_year": 2014, "act_number": 55, "article": "4"}` |
| art. 18 Statuto dei lavoratori | `{"act_type": "legge", "act_year": 1970, "act_number": 300, "article": "18"}` |

```json
{"tool": "get_law_article", "arguments": {"act": "testo_unico_sicurezza_lavoro", "article": "2", "paragraphs": ["1"]}}
```

`paragraphs` serve solo per articoli lunghi con commi numerati: nei codici storici i commi spesso non sono numerati e il server restituisce l'articolo intero con un `warning`.

Testo vuoto o «ABROGATO» = abrogato. Con `in_force_on` dichiara la data a cui il testo è vigente. Per cercare norme su un tema senza conoscere l'articolo usa `search_articles`.

---

## Contratti (`search_contracts`)

| Tipo contratto | Query efficace |
|---|---|
| Locazione commerciale | `"contratto locazione uso commerciale"` |
| NDA | `"accordo riservatezza non disclosure"` |
| Appalto privato | `"contratto appalto opere"` |
| Agenzia | `"contratto di agenzia monomandatario"` |
| Franchising | `"contratto di franchising affiliazione commerciale"` |
| Fornitura | `"contratto fornitura beni servizi"` |

---

## Atti processuali (`search_processual_acts`)

| Tipo atto | Query efficace |
|---|---|
| Decreto ingiuntivo | `"ricorso per decreto ingiuntivo credito liquido esigibile"` (se non lo trova, naviga con `list_processual_act_categories` → `list_processual_acts`) |
| Opposizione a DI | `"atto di citazione opposizione decreto ingiuntivo"` |
| Ricorso rito lavoro | `"ricorso impugnazione licenziamento rito lavoro"` |
| Ricorso TAR | `"ricorso TAR annullamento provvedimento amministrativo"` |
| ATP | `"accertamento tecnico preventivo consulenza tecnica preventiva"` |
| Mediazione | `"domanda di mediazione obbligatoria materie civili commerciali"` |

---

## Normativa (`search_articles`): quale `domain`

| Materia | `domain` |
|---|---|
| Contratti, obbligazioni, famiglia, proprietà, successioni | `civil_code` |
| Processo civile ordinario | `civil_procedure` |
| Leggi speciali civili (locazioni, consumatori, lavoro) | `special_civil` |
| Riti speciali (decreto ingiuntivo, ATP, procedimenti cautelari) | `special_civil_procedure` |
| Codice penale e processo penale | `criminal` |
| IVA, imposte dirette, accertamento | `tax` |
| GDPR e Codice privacy | `privacy` |

Per un articolo di una legge speciale già noto (es. L. 689/1981) usa `get_law_article` con `act_type`: `search_articles` non contiene tutte le leggi speciali.
