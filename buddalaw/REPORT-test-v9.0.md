# BuddaLaw — Report di collaudo v9.0

**Data:** 2026-10-17, aggiornamenti del 18 ottobre
**Versione collaudata:** 9.0 (branch `feat/buddalaw-v9`)
**Confronto previsto:** v8.4 (tag `buddalaw-v8.4`) e nessuna skill
**Metodo:** tre livelli. A = controlli sui file, senza rete. B = conversazioni vere con BuddaLaw. C = chiamate dirette al server.

> **Esito conclusivo del 18 ottobre — rilascio beta su main.** **128 controlli offline superati**. Le 62 esecuzioni previste della candidata C3 sono state tentate con Claude Pro: **61 valide**, una fermata dal limite di turni. Le sette prove bloccate dalla quota sono state completate dopo il ripristino delle 15:00, senza API o OpenRouter. **16/24 casi di qualità valutabili promossi; 12/16 critici**. Restano errori nei link e nell'avviso: **criteri per il rilascio stabile non superati**. Le sezioni storiche non sostituiscono questo risultato.


## Risultati conclusivi della candidata C3

| Controllo | Esito |
|---|---|
| Livello A, senza rete | **128/128**, archivio e sorgenti coerenti; 12 live saltati nel comando ordinario |
| Contratto del server | 11 comportamenti verificati e T74 separato; catalogo aggiornato a **48 tool**; calcolatori non collaudati |
| C3, copertura delle prove previste | **62/62 tentate, 61 valide**; B04 r3 raggiunge il limite di otto turni |
| C3, qualità escluso B00 | **16/24 casi valutabili**; un caso non valutabile (B04) |
| C3, casi critici escluso B00 | **12/16 valutabili (75%)**; soglia descrittiva del 90% non raggiunta |
| Confronto v8.4 / nessuna skill | **11/16** e **5/15**; 34 prove, 33 valide; B22 senza skill raggiunge il limite di turni |
| Avviso aggiornamento | B12 **0/3**, B23 **0/1**; nessun falso avviso in B13 **3/3**, B24 **1/1** |
| URL non fedeli nella v9 | Due prove: B01 r1 e B19 r1; il criterio di assenza di link alterati non è superato |
| Canale dei nuovi collaudi conclusivi | **Claude Pro**, crediti extra disabilitati negli eventi osservati; nessuna chiamata OpenRouter sostitutiva |
| Decisione | **Beta**: test conclusi e limiti documentati; nessuna promozione stabile né dei modelli OpenRouter |

La quota Pro si è ripristinata come indicato dalla CLI. La tornata
`20261018-150152-757858` completa **7/7 prove valide** sullo stesso hash e sugli
stessi quesiti: B21 **2/3**, B22 **3/3**, B25 **1/1**. Non ripete risposte già
bocciate per comportamento: sostituisce soltanto le sei registrazioni senza
prova valida per quota/arresto, e avvia B25 che mancava. Gli originali restano
conservati. Si contano così **68 registrazioni grezze per 62 prove previste**,
senza usare le sei interruzioni come risposte del modello o come tentativi utili
per raggiungere la maggioranza.

Il controllo aggiuntivo dei tre B22 conferma che i frammenti citati compaiono
nei campi `testo`/`text` delle fonti lette, separati dalle sintesi automatiche.
Questo verifica la letteralità del campione, non la qualità giuridica generale.
B21 supera il caso con 2 risposte su 3: l'errore di formato della prima rimane
nel rapporto e non viene riscritto.

Il confronto usa i medesimi casi critici dove applicabili, ma la v9 ha tre prove
per caso critico e controlli aggiuntivi su budget e link normativi; v8.4 e nessuna
skill hanno una prova per caso. Le percentuali non sono una misura statistica
comparabile di affidabilità generale. B00 è solo isolamento ed è escluso dai
punteggi di qualità. Non vengono dichiarati esiti per Sonnet corrente, Codex o
altri modelli sulla suite completa C3.

Consumo riportato dalla CLI: **7,750 USD di token stimati per C3**, più circa
**2,145 USD** per il confronto. Sono stime, non addebiti aggiuntivi attestati;
le tornate usano l'abbonamento con consumo extra disabilitato. I costi storici
OpenRouter rimangono distinti.

### Esiti per caso

Il numeratore indica le prove promosse, il denominatore le prove previste.
«Non valutabile» e l'asterisco indicano un limite di esecuzione: non sono
promozioni. «—» indica che il confronto non prevedeva quel caso.

| Caso | v9 C3 | v8.4 | Nessuna skill |
|---|---|---|---|
| B00 | 3/3 ✓ | 1/1 | 1/1 |
| B01 | 1/3 ✗ | 0/1 | 0/1 |
| B02 | 3/3 ✓ | 1/1 | 0/1 |
| B03 | 3/3 ✓ | 1/1 | 0/1 |
| B04 | 1/3 — non valutabile | 1/1 | 0/1 |
| B05 | 3/3 ✓ | 0/1 | 0/1 |
| B06 | 3/3 ✓ | 1/1 | 1/1 |
| B07 | 0/3 ✗ | 0/1 | 1/1 |
| B08 | 1/1 ✓ | — | — |
| B09 | 3/3 ✓ | 0/1 | 0/1 |
| B10 | 1/1 ✓ | — | — |
| B11 | 0/1 ✗ | — | — |
| B12 | 0/3 ✗ | — | — |
| B13 | 3/3 ✓ | 1/1 | 0/1 |
| B14 | 3/3 ✓ | 1/1 | 1/1 |
| B15 | 0/1 ✗ | — | — |
| B16 | 3/3 ✓ | 1/1 | 0/1 |
| B17 | 3/3 ✓ | 1/1 | 1/1 |
| B18 | 3/3 ✓ | 1/1 | 0/1 |
| B19 | 1/3 ✗ | 0/1 | 0/1 |
| B20 | 0/1 ✗ | — | — |
| B21 | 2/3 ✓ | 1/1 | 1/1 |
| B22 | 3/3 ✓ | 1/1 | 0/1 * |
| B23 | 0/1 ✗ | — | — |
| B24 | 1/1 ✓ | — | — |
| B25 | 1/1 ✓ | — | — |

C3 resta congelata sull'hash
`1ce58fd6d54a617eb7bd176df5a9b304e4f89a012c2646a6d2f2f46897f0647f`.
La conclusione usa il valutatore corretto e conserva risposte, impronte e
metadati originali. Le cronologie seguenti documentano le tappe precedenti.

## Ambiente e isolamento

| Voce | Valore |
|---|---|
| Runtime | Claude Code headless (`claude -p`), connettore claude.ai BuddaLaw |
| Modello | `claude-haiku-5-5`. Il modello predefinito non è stato provato (server fuori servizio) |
| Isolamento | `--disable-slash-commands`: nessuna skill installata è attiva, nemmeno la v8.3 in `~/.claude/skills`. Skill iniettata con `--append-system-prompt-file`. Tool ridotti a Read e ToolSearch, altri server MCP vietati. `system/init` controllato a ogni esecuzione |
| opencode (Qwen 3.8 Flash-Next, DeepSeek V4.1 Flash) | Prima tornata saltata per accesso mancante; nella ripresa entrambi hanno concluso il quesito mirato descritto sotto, con OpenCode 1.18.19 e OpenRouter |
| GPT Astra / Luna | Nella ripresa: due subagenti indipendenti con i tool MCP BuddaLaw nativi. Questo non equivale a un collaudo della CLI Codex o della sua configurazione locale |

## Cronologia

| # | Comando | `results/` | Esito |
|---|---|---|---|
| 1 | `run.py --config v9 --runs 1` (26 casi) | 20261017-155125 | valido |
| 2 | `--config v9 --solo-lampo --runs 3` | 20261017-161258 | guasto del server da B03 run 3: colpite 38 esecuzioni su 54 |
| 3 | `--config v8.4,nessuna --solo-lampo --runs 1` | 20261017-163716 | guasto: colpite 28 esecuzioni su 34 |
| — | una chiamata di prova | — | `RetryError`: stop, nessun nuovo tentativo |
| 4 | `--modello default --solo-lampo` | — | non eseguito |
| C | `BUDDALAW_LIVE=1 pytest test_mcp_live.py` | — | non eseguito in questa tornata. Era verde (12/12) poco prima, nel collaudo di S3 |

Un'esecuzione è «colpita» se almeno una risposta di BuddaLaw diceva «Circuit breaker aperto», «backend temporaneamente non disponibile» o «HTTP 500». Le esecuzioni colpite sono escluse dal conteggio. Durante il guasto la skill si è comportata bene: nessuna sentenza a memoria, nessun link inventato, il guasto riferito con le parole del server, nessun ciclo di nuovi tentativi.

## Livello A

52 test passati su 52, con l'archivio `.skill` rigenerato dopo le correzioni. Nella ripresa si aggiungono 9 controlli offline del runner: **61/61**. Description: 941 caratteri (limite 1024). `SKILL.md`: 187 righe; nessuna modifica alla skill durante il confronto mirato.

## Livello B — esiti v9.0 con Haiku

Formato: esecuzioni promosse / esecuzioni valide. «—» = nessuna esecuzione valida.

| Caso | ⚡ | Tema | v9 | v8.4 | nessuna |
|---|---|---|---|---|---|
| B00 | ⚡ | isolamento | 4/4 | 1/1 | 1/1 |
| B01 | ⚡ | IVA: tributari/tributario | 4/4 | — | — |
| B02 | ⚡ | Cassazione per numero | 4/4 | — | — |
| B03 | ⚡ | Corte costituzionale | 3/3 | — | — |
| B04 | ⚡ | CGUE con numero di causa | 1/1 | — | 0/1 |
| B05 | ⚡ | casi simili di merito | 1/1 | — | — |
| B06 | ⚡ | list_uffici → codiceufficio | 1/1 | — | — |
| B07 | ⚡ | get_law_article al 2022 | 3/3 | 1/1 | — |
| B08 | | articolo abrogato | 1/1 | | |
| B09 | ⚡ | SU 577/2008 non disponibile | 1/1 | — | — |
| B10 | | Sezioni Unite e contrasto | 1/1 | | |
| B11 | | domanda in inglese | 1/1 | | |
| B12 | ⚡ | avviso di aggiornamento vero | **0/1** | n.a. | n.a. |
| B13 | ⚡ | nessun falso avviso | 1/1 | — | — |
| B14 | ⚡ | passa la mano a verifica-citazioni | 1/1 | — | — |
| B15 | | solo link a una norma | 1/1 | | |
| B16 | ⚡ | check_access prima di tutto | 1/1 | — | — |
| B17 | ⚡ | niente sentenze a memoria | 4/4 | 1/1 | 1/1 |
| B18 | ⚡ | numero e anno interi | 2/2 | — | — |
| B19 | ⚡ | «più recenti» con anno | 1/1 | — | — |
| B20 | | warning di get_law_article | 1/1 | | |
| B21 | ⚡ | not_found penale | 1/1 | — | — |
| B22 | ⚡ | virgolettati letterali | 1/1 | — | — |
| B23 | | avviso su tre turni | **0/1** | n.a. | n.a. |
| B24 | | check_access una sola volta | 1/1 | | |
| B25 | | contratto, ID interi | 1/1 | | |

**Confronto prima/dopo: non conclusivo.** Sui 3 casi validi in comune (B00, B07, B17) v9 e v8.4 sono pari. Le esecuzioni colpite dal guasto mostrano comunque, a titolo indicativo, gli errori che la v9 corregge: senza le sue istruzioni Haiku usa `dominio="tributari"` (B01), non chiama `list_uffici` (B06), non usa `anno` (B19) e, senza skill, non cerca in `eu-case-law` (B04).

## Chiamate e costo

| Tornata | Esecuzioni | Chiamate BuddaLaw | $ |
|---|---|---|---|
| 1 | 26 | 82 | 0,46 |
| 2 | 54 | 154 | 0,33 |
| 3 | 34 | 87 | 0,15 |
| Totale | 114 | ≈ 324 | **≈ 0,94** (tetto 5 $) |

## Criteri di successo del piano

| Criterio | Esito |
|---|---|
| Livello A verde | sì |
| Livello C verde o fermo dichiarato | verde poco prima del guasto (S3, 12/12); da rifare dopo le correzioni |
| ≥ 90% dei casi ⚡ con Haiku (2 su 3) | sì sui dati validi (94%); le 3 ripetizioni complete non sono state possibili |
| ≥ 80% con Qwen e DeepSeek | non verificato sull'intera suite; accesso OpenCode risolto e confronto mirato completato, con violazioni rilevate in entrambi i modelli |
| Zero link inventati | Il vecchio valutatore segnalava zero su 114; dato storico non ricertificato dal controllo attuale |
| Costo dichiarato | sì, ≈ 0,94 $ |
| v9 ≥ v8.4, migliore sui divari G1–G8 | non verificato (guasto); pari sui 3 casi validi |
| Avviso presente quando serve, assente quando non serve | assente quando non serve: sì (B13, B24). Presente quando serve: **no** (B12, B23) → corretto, da riprovare |
| Description ≤ 1024; SKILL.md < 500 righe | sì |

## Fallimenti, classificati

Classi: (a) difetto della skill · (b) limite del modello · (c) falso errore del controllo · (g) guasto del server

| Caso | Classe | Causa | Rimedio |
|---|---|---|---|
| B12, B23 | (a) | Nessun passo della procedura richiamava il controllo di aggiornamento | Applicato: richiamo al passo 2 e voce 6 della checklist riscritta |
| B14 | (b)/(a) lieve | Non nominava `verifica-citazioni-legali` | Applicato: regola di precedenza esplicita |
| B15 | (c) | «it» di normattiva.it contato come parola inglese | Runner corretto |
| B07 | (c) | «non ha segnalato avvertenze» letto come box finale; «novanta» in lettere | Runner e caso corretti |
| B22 (prima tornata) | (c) | Apostrofo tipografico ’ contro apostrofo dritto ' | Runner corretto |
| B00 v8.4 | (c) | Connettore `pending` all'avvio | Runner corretto |
| B04 nessuna | (b) | Senza skill non cerca in `eu-case-law` | Atteso (G2) |
| tornate 2–3 | (g) | Circuit breaker, HTTP 500, RetryError | Esclusi, da rifare |

## Correzioni applicate dopo il collaudo e la revisione indipendente

Applicate alla skill dopo questi dati. Sono controllate dal livello A, ma non ancora dal vivo:

- avviso di aggiornamento richiamato al passo 2 della procedura; il secondo motivo di avviso vale solo per un valore della tabella che il server non accetta più;
- link alle norme fatti solo dalla skill normattiva: il `normattiva_url` di BuddaLaw per i codici e i d.m. può aprire un altro articolo;
- tetto delle chiamate definito con precisione (contano le `search_*`);
- `not_found` nella Cassazione: una nuova lettura con il solo `dominio`; se l'utente non dice civile o penale, prima civile e poi penale;
- di nuovo la tabella materia → `domain` di `search_articles`, che era nella v8.4;
- segnaposto al posto di estremi ed esempi presi da casi veri;
- `chiama_mcp.py` si ferma anche sul «circuit breaker».

## Lavoro generale ancora da completare dopo la ripresa autorizzata

1. Livello C, dopo aver risolto l'ID Haiku rifiutato nella ripresa.
2. `--config v9 --solo-lampo --runs 3` (in particolare B12, B13, B23, B24), poi `--config v8.4,nessuna --solo-lampo` e `--modello default --solo-lampo`.
3. Applicare la preparazione OpenCode aggiornata e completare `--runtime opencode --config v9 --runs 1`, poi `--solo-lampo --runs 3`. BuddaLaw e OpenRouter risultano autenticati.
4. Aggiornare questo report.

## Ripresa: confronto mirato con quattro modelli

Il maintainer ha autorizzato la ripresa e poi richiesto un unico quesito di
responsabilità sanitaria, identico per quattro modelli. La suite generale è
stata interrotta per dare precedenza a questo confronto: Qwen aveva concluso
B00–B02, tutti passati; questo campione non dimostra il raggiungimento della
soglia dell'80%. Le ripetizioni preparatorie con isolamento fallito sono escluse.

| Modello e ambiente | `search_*` | `get_judgement` richiesti / integrali ottenuti | `get_law_article` | Esiti osservati |
|---|---:|---:|---:|---|
| GPT Astra, subagente MCP nativo, ragionamento high | 4 | 2 / 1 | 16 | Limiti rispettati, zero errori di schema; 5 link giurisprudenziali tutti presenti nei grezzi |
| GPT Luna, subagente MCP nativo, ragionamento low | 3 | 2 / 2 dichiarati | 7 | Limiti rispettati; 2 link e letture descritti nell'audit, grezzi non conservati |
| DeepSeek V4.1 Flash, OpenCode/OpenRouter | **10** | 1 / 0 (`not_found`) | 6 | Tetto ricerche superato; link normativi usati senza Normattiva; zero URL giurisprudenziali alterati su 16 |
| Qwen 3.8 Flash-Next, OpenCode/OpenRouter | **7** | 1 / 0 (`not_found`) | 21 | Tetto ricerche superato; 4 chiamate non conformi allo schema; **1 URL alterato su 12** |

I conteggi includono i tentativi rifiutati: per Qwen due ricerche usano `anno`
come stringa e due letture normative inviano `paragraphs` come stringa anziché
elenco. Il link alterato aggiunge uno zero al numero nell'ECLI: non dimostra una
sentenza inventata, ma viola la copia identica di `public_url`.

I due subagenti GPT hanno usato anche Normattiva per il formato dei link, come
richiesto dal loro ambiente; OpenCode aveva soltanto BuddaLaw. Il confronto non
isola quindi il solo effetto del modello. Astra distingue con maggiore
precisione gli adempimenti processuali e i rapporti interni; Luna è meno
dettagliata su questi punti. Nelle due risposte OpenRouter sono presenti
passaggi da verificare sul mantenimento della cronologia clinica e
sull'applicazione concreta delle norme. Nessuna risposta è stata riscritta.

**Costo riportato da OpenCode per le due risposte concluse:** DeepSeek
0,02265 $, Qwen 0,03515 $, totale **0,05780 $**; durata rispettivamente 84,4 e
444,6 secondi. Esclusi preparazione e tentativo incompleto; costi GPT non
disponibili. Non sono stati osservati blocchi 403/429, HTTP 500 o circuit
breaker nelle quattro prove concluse. I controlli tecnici non certificano ogni
conclusione giuridica.

**Correzioni al runner nate dalle prove:** tutti i server MCP globali estranei
vengono disabilitati nella sola sandbox; una skill caricata dalla posizione
sbagliata impedisce l'avvio del modello; deleghe interne e domande interattive
sono escluse; i guasti MCP non vengono più descritti come login mancante e
HTTP 500 provoca lo stop. Un primo tentativo DeepSeek rimasto aperto su un
subagente `explore` è stato interrotto e conservato separatamente. Per il solo
quesito articolato sono stati consentiti 16 passi OpenCode, contro gli 8 della
suite ordinaria; i limiti comportamentali della skill restano invariati.

Risposte, audit e tracce sono conservati localmente in
`tests/e2e/results/20261017-caso-chirurgo/`, esclusa da git. Le quattro risposte
originali e il confronto sono stati copiati, con verifica dell'integrità, nella
cartella Downloads richiesta dal maintainer. Nessuna copia installata della
skill è stata aggiornata. Rimangono da completare la suite generale, le tre
ripetizioni critiche e il confronto v8.4/nessuna; il vecchio canale di livello C
ha inoltre rifiutato l'ID Haiku configurato, senza effettuare chiamate BuddaLaw.

## Revisione critica e nuova ripresa del 17–18 ottobre

**Decisione attuale: beta utilizzabile, collaudo per il rilascio stabile ancora
incompleto.** Il piano rivisto è in
[`PIANO-collaudo-v9-red-team.md`](PIANO-collaudo-v9-red-team.md).
Le istruzioni della skill e l'archivio installabile non sono stati modificati.
L'impronta di `SKILL.md` resta
`094c811dee02e6f0468b07aed6b48136aa8c70ae34a1b45c624234343810ffd1`.

| Controllo | Risultato verificato | Limite |
|---|---|---|
| Offline, struttura e attacchi al programma di prova | **89/89** | Non misura la qualità giuridica delle risposte |
| C, comportamenti del servizio | **11/11**, 13 chiamate con Haiku 4.5 | Tornata separata dal controllo di schema |
| C, schema T74 | **1/1**, schema invariato | Superato dopo la correzione del canale proxy; fixture non riscritta |
| OpenCode, controllo breve B00 v9/nessuna | 4 esecuzioni valide; versioni isolate correttamente | DeepSeek senza skill risponde in inglese e fallisce il controllo della lingua |
| Nuova suite OpenCode v9 | **13/124 esecuzioni registrate, 11 valide** | Interrotta durante Qwen; DeepSeek non ancora raggiunto in questa tornata |

La CLI Claude installata rifiutava l'ID Haiku 5.5. È stato usato il modello
esplicito `claude-haiku-4-5-20251001`, senza aggiornare software o configurazioni
globali. I suoi risultati restano separati dal vecchio campione dichiarato
Haiku 5.5. Il proxy disattivava automaticamente ToolSearch: l'attivazione
esplicita, prevista dalla
[documentazione Claude Code](https://code.claude.com/docs/en/mcp#configure-tool-search),
ha reso nuovamente verificabile lo schema. Un'estrazione vuota ora produce
un errore del canale, senza suggerire che siano spariti tutti i tool.

### Esiti della suite interrotta

| Caso Qwen v9 | Esecuzioni | Esito |
|---|---:|---|
| B00, isolamento | 3/3 riuscite | Escluso dal punteggio comportamentale |
| B01, tributario | 2/3 riuscite | Un fallimento reale: avvertenze in fondo anziché accanto alla voce interessata |
| B02, Cassazione nota | 3/3 riuscite | Promosso nel campione osservato |
| B03, Corte costituzionale | 2 riuscite, 1 non valutabile | Il log della sessione non valutabile conferma il collegamento MCP fallito |
| B04, Corte di giustizia UE | 1 interrotta | Non valutabile; costo parziale noto conservato |

Per B03 r2 il modello dichiarava assenti i tool. Il log ufficiale OpenCode
della stessa sessione riporta `server unavailable`, `key=buddalaw`,
`status=failed`: **non è un errore della skill o del modello**. La diagnosi è
arrivata dopo altre due esecuzioni; la tornata è stata quindi fermata e
rivalutata senza nuove chiamate. Il controllo iniziale `mcp list` era riuscito,
ma non provava il collegamento delle conversazioni successive.

Il nuovo programma controlla anche gli errori MCP all'avvio mentre arrivano
e ferma la tornata, prima che prosegua col modello. La prova offline usa un
processo che segnala il guasto e tenterebbe poi un'altra azione: viene fermato
prima di quell'azione. Il controllo aggiornato non è stato presentato come
superato da una nuova suite live: la ricerca non è stata ritentata dopo lo stop.
I risultati non valutabili sono esclusi dal denominatore comportamentale,
ma impediscono comunque la promozione complessiva per copertura incompleta.

### Correzioni giustificate dal red teaming

- Casi vuoti, ID sconosciuti, prove tutte saltate o ripetizioni incomplete
  non possono produrre un esito positivo.
- Solo risultati di ricerca identificati come tali possono provare un link
  o una citazione; gli esempi della skill e la ricerca dei tool sono esclusi.
- I link sono confrontati per uguaglianza. Anche un solo URL alterato impedisce
  la promozione, senza essere nascosto dalle altre due ripetizioni riuscite.
- Le chiamate sono verificate contro lo schema e i limiti v9 sono controllati
  per quesito; la distinzione tra integrali richiesti e ottenuti resta necessaria.
- Corrette le virgolette che catturavano prosa intermedia e le citazioni con
  data completa: una fonte «n. … del 31/07/2024» prova il relativo numero/anno.
- Corretto il profilo con inventario ridotto: modifica soltanto il JSON e può
  finalmente arrivare al modello. Gli avvisi B12/B23 restano da provare dal vivo.
- La configurazione OpenCode ora è separata da quella globale. Prima una copia
  omonima installata poteva prevalere; il controllo ha bloccato quel tentativo
  prima del modello. Nessuna copia installata è stata modificata.
- Modello ausiliario per i titoli impostato sul modello richiesto: il log
  aveva mostrato chiamate ereditate a un altro modello. Non riguardavano la
  risposta principale, ma rendono incompleti i soli costi degli step.
- Conservate copie dei casi e della skill, impronte dei file, modello effettivo,
  isolamento, costi noti, interruzioni e versione del valutatore usato nella
  rivalutazione. Una sola tornata può usare la stessa sandbox.

La rivalutazione offline del quesito sanitario conferma i fallimenti già
descritti: DeepSeek supera il tetto e usa link normativi senza Normattiva;
Qwen supera il tetto, sbaglia quattro input e altera un URL. Un primo sospetto
aggiuntivo sugli estremi era invece un falso positivo sulle date complete ed
è stato corretto. Le risposte originali non sono state riscritte.

**Costi noti separati:** test C di comportamento **0,4923 $**; controllo breve
OpenCode **0,01102 $**; suite interrotta **0,07019 $**, inclusi costi parziali
noti. Sono esclusi accesso, diagnostica, estrazioni dello schema e possibili
chiamate ausiliarie: non è una fatturazione complessiva. Una diagnostica OpenCode
che non ha intercettato gli schemi è stata scartata; non è conteggiata come
prova gratuita o riuscita. Nessuna percentuale generale di affidabilità è
ricavabile da questa tornata incompleta.

Tracce e prove locali: `tests/e2e/results/redteam-20261017/`,
`tests/e2e/results/20261018-074007-371138/` e
`tests/e2e/results/20261018-074418-850333/`, escluse da git.
Le nuove risposte e gli audit sono salvati anche in
`Downloads/Test_BuddaLaw_v9_RedTeam_2026-10-18/`; i quattro originali del caso
del chirurgo restano nella loro cartella del 17 ottobre.

**Ancora aperti:** completamento delle suite sui due modelli OpenCode dopo
aver verificato il collegamento nell'avvio effettivo; tre prove complessive
per i casi critici, soprattutto B12/B13/B23/B24; confronto v8.4/nessuna nello
stesso ambiente; nuova coorte Haiku esplicitamente identificata. Le soglie
del piano storico non sono state dimostrate. PR sempre in bozza.


## Ripresa del 18 ottobre: catalogo completo e confronto dell'avviso

Il maintainer ha autorizzato il completamento dei test e il passaggio a `main`
al termine della verifica. Le risposte originali sono conservate; non sono
state aggiornate copie installate.

### Schema e programma di prova

- **104/104 controlli offline**, con 12 live saltati nell'esecuzione ordinaria.
- **48 strumenti** nel catalogo, 32 aggiunti rispetto alla fixture del 17.
  Parametri e descrizioni dei 16 strumenti di ricerca e lettura invariati.
  Nessun calcolo eseguito o dichiarato collaudato.
- T74 inizialmente dava un falso verde: `select:` caricava solo i 16 nomi già
  noti. La scoperta ora usa `+BuddaLaw`, controlla i riferimenti restituiti
  e rifiuta definizioni parziali o il limite dei risultati. T74 è diventato
  rosso, poi verde con la fixture aggiornata. I 48 nomi coincidono anche con
  quelli del server MCP nativo in Codex.
- Claude: ToolSearch attivato esplicitamente e nuovi MCP personali esclusi
  dai tool visibili. `--strict-mcp-config` con configurazione vuota è stato
  scartato: esclude anche il connettore cloud necessario al collaudo.
- I file MCP lunghi salvati dal runtime sono ammessi come fonti solo quando
  il percorso è quello esatto restituito da BuddaLaw e la lettura è riuscita.
  Questa correzione elimina un falso errore di fedeltà dei link in B24; i link
  erano presenti nel file letto dal modello. Nessuna lettura aggiuntiva del
  valutatore, nessuna modifica alla risposta originale.
- Sandbox separate e arresto condiviso permettono prove indipendenti in
  parallelo: al primo guasto si fermano anche i processi già attivi. Il file
  di arresto non viene cancellato automaticamente. Le richieste già inviate
  possono completarsi; nessun ritento automatico.

### Tornate precedenti alla correzione del catalogo differito

| Tornata locale | Candidata | Risultato | Costo noto |
|---|---|---|---:|
| `20261018-104844-616772` | v9 originale | B00 2/2, Qwen e DeepSeek isolati | 0,00965 $ |
| `20261018-105044-367098` | inventario da 16 tool, server da 48 | Interrotta dopo la scoperta del cambio di catalogo; non usata per la promozione | 0,01941 $ sui tre B12 conclusi, esclusa l'interruzione |
| `20261018-110402-539508` | inventario da 48 tool | Qwen B12 0/3; interrotta per confronto con Haiku | 0,03169 $ sui tre B12 conclusi, esclusa l'interruzione |
| `20261018-111126-924546` | stessa candidata da 48 tool | Haiku: B12 0/3, B13 3/3, B23 0/1, B24 1/1 dopo rivalutazione | 0,86945 $ |

La candidata da 48 tool di queste due ultime righe ha impronta
`87bde6f179b716b8fd748c0678860478abf3a0b4edb94ecd0a6a380ecc9205a3`.
La tornata Haiku è completa per i quattro casi selezionati (8/8 esecuzioni),
non per l'intera suite. I tool BuddaLaw funzionavano: i fallimenti dell'avviso
non sono attribuiti a un guasto MCP.

Nelle tracce Haiku la ricerca dei tool caricava soltanto i due o tre strumenti
utili al quesito. Non scopriva il catalogo completo: selezionare i nomi già
noti non permette di scoprire le aggiunte. La nuova candidata impone una
scoperta del catalogo differito per conversazione e avvicina l'inventario alla
procedura. Impronta della candidata in verifica:
`5b470efdd3587b8e4107a0b8e23bf9dd3fb71ea956392eec88d2eee440872c3d`.

I costi della tabella sono parziali e separati: non comprendono tutte le
diagnostiche, l'estrazione dello schema o eventuali ausiliari. Non sono un
totale di fatturazione. Le tornate con istruzioni o inventari differenti non
sono sommate per ricavare una percentuale generale di affidabilità.


### Fermo della candidata con scoperta esplicita

| Modello | Tornata locale | Esecuzione effettiva | Esito |
|---|---|---|---|
| Haiku 4.5 | `20261018-112344-442115` | 1/3 registrata, zero valide | Fermata dallo stop condiviso durante la prima prova |
| Qwen 3.8 Flash | `20261018-112345-576791` | 0/3 | Preflight MCP fallito, modello non avviato |
| DeepSeek V4.1 Flash | `20261018-112345-939757` | 0/3 | Preflight MCP fallito, modello non avviato |

Le due nuove sandbox OpenCode riportano
`SSE error: Non-200 status code (400)` durante il collegamento a BuddaLaw.
Il primo guasto attiva `results/20261018-c2-validation/STOP`; anche il processo
Haiku già attivo viene fermato. Le due verifiche MCP erano già in corso:
nessun modello OpenCode è partito e non sono stati effettuati ritenti dopo
il fermo. L'arresto condiviso è quindi verificato anche dal vivo.

La configurazione MCP è identica a quella della sandbox precedente; le tre
configurazioni isolate hanno lo stesso contenuto e usano la stessa cartella
degli output MCP. Non sono stati letti file di credenziali. Questi controlli
locali non provano né un guasto generale del servizio né la necessità di
un nuovo login. Il collegamento delle nuove cartelle resta da diagnosticare.

La traccia parziale di Haiku mostra `ToolSearch` con query `+BuddaLaw` e
`max_results=100`, quindi la scoperta esplicita è stata eseguita; non c'è
una risposta conclusa che provi la comparsa dell'avviso. I costi parziali di
Haiku non sono disponibili: lo zero riportato dal runner non significa che
non siano maturati costi. I modelli OpenCode non sono stati invocati.

**Decisione: beta, PR in bozza.** La candidata e l'archivio sono pubblicati
nel commit `d1815d7`; 104 controlli offline passano e lo schema completo è
verificato. Restano da completare la prova dell'avviso, le suite generali,
il confronto v8.4/nessuna e il modello predefinito. I dati non permettono
una promozione stabile. Il passaggio a `main` richiesto dal maintainer resta
in attesa del completamento del collaudo o di una sua decisione esplicita
di pubblicare la beta con questi limiti.

La regola dell'handoff ferma le nuove chiamate al primo nuovo blocco o
guasto: nessun ritento automatico. Il file di arresto è conservato; per
riprendere occorre una nuova autorizzazione del maintainer.


## Ripresa con il solo abbonamento Claude Pro

Il maintainer ha chiesto di usare l'abbonamento Claude ed escludere altre
spese OpenRouter. Accesso verificato con `claude auth status --json`:
`authMethod=claude.ai`, `apiProvider=firstParty`, `subscriptionType=pro`;
nessuna variabile API nell'ambiente. Il nuovo comando `--solo-abbonamento`
ferma runtime diversi, variabili API e autenticazione non verificata prima
dei modelli; conserva nel manifest soltanto il tipo di accesso, senza dati
personali. Dieci test offline della protezione portano il totale a **114/114**.

I valori USD delle tornate Claude, anche nelle sezioni storiche, sono valori
di consumo stimati dalla CLI, **non fatture o addebiti aggiuntivi attestati**.
La [documentazione Anthropic](https://code.claude.com/docs/en/costs) distingue
le stime della sessione dall'uso incluso in Pro/Max. Non sono stati attivati
crediti aggiuntivi né modificate impostazioni di fatturazione.

Dopo l'autorizzazione del maintainer, un controllo OpenCode nella sandbox
originale è riuscito; il successivo è fallito con SSE 400 prima dei modelli
(`20261018-121903-721116`). La prova Claude accoppiata è stata fermata senza
chiamate BuddaLaw (`20261018-121904-779603`). Le verifiche indipendenti Claude
sono proseguite secondo il piano; OpenRouter resta escluso dal resto del
collaudo per istruzione del maintainer.

| Candidata / modello | Campione | Copertura ed esito |
|---|---|---|
| C2 / Haiku 4.5 | `20261018-122434-829842` | B12: 3/3 valide, **0/3** avvisi |
| C2 / Sonnet 4.6 | `20261018-123248-635574` | B12: prima prova valida senza avviso; seconda fermata manualmente, esclusa. 1/8 esecuzioni valide previste: nessuna promozione della tornata |
| C3 / Haiku 4.5 | `20261018-123513-403307` | B12: 3/3 valide, **0/3** avvisi |
| C3 / Haiku 4.5 | `20261018-123724-623063` | **58/59 registrate, 51 valide** dopo rivalutazione offline; interrotta sulla quota Pro, B25 non avviata |
| v8.4 / nessuna, Haiku 4.5 | `20261018-123806-605934` | **34/34 eseguite, 33 valide**. B22 senza skill non valutabile per limite di turni; esiti di qualità finali: **11/16** v8.4, **5/15** senza skill |

Due avvii Sonnet nella sandbox senza accesso di rete non hanno prodotto
risposte o chiamate BuddaLaw (`20261018-122852-523710`,
`20261018-123032-869731`): esclusi dalla valutazione della skill.
L'arresto di C2 Sonnet dopo il primo difetto riprodotto è una scelta di
collaudo, non un guasto del server. La dicitura generica di arresto condiviso
nei riepiloghi originali va letta con questa precisazione.

C3 (`bcc34e6`) rende l'inventario leggibile una voce per riga e richiede la
differenza tra l'insieme dei nomi del server e il solo array JSON, inclusa la
verifica del numero di nomi distinti. Hash della skill:
`1ce58fd6d54a617eb7bd176df5a9b304e4f89a012c2646a6d2f2f46897f0647f`.
Sorgenti e archivio `.skill` coincidono. La riscrittura **non risolve B12**
nel campione Haiku; la documentazione pubblica indica esplicitamente questo
limite e mantiene lo stato beta. Il controllo T74 per il maintainer resta
separato dall'avviso comportamentale dell'assistente.


### Correzioni del valutatore osservate durante C3

La skill e i quesiti restano congelati; cambia soltanto il controllo delle
tracce, nei commit `a89ce62` e `a0e2859`. Totale offline: **123/123**.
Le risposte originali non vengono modificate e non si ripetono le chiamate
per correggere un punteggio del programma.

- **B01 r1 v9:** URL con dominio `buddaslaw.com` e parentesi Markdown finale
  mancante. Il vecchio controllo esaminava solo domini già noti: il caso
  falliva il vincolo specifico, ma sfuggiva alla categoria grave «fedeltà
  link». Ora il confronto comprende anche URL di documenti su domini diversi
  e citazioni riconoscibili su altri siti; verifica anche il Markdown completo.
- **B01 r3 v9:** l'elenco iniziale omette BuddaLaw, ma la chiamata nativa
  `check_access` restituisce `has_access=true`. È prova di collegamento,
  indipendente da una dichiarazione del modello. Il falso errore di isolamento
  viene rimosso in rivalutazione; restano gli errori reali: quattro chiamate
  `get_judgement` con `dominio="tribunario"` e superamento del tetto di letture.
- Anche i riferimenti strutturati di ToolSearch possono provare la scoperta
  dei tool dopo l'avvio. Le citazioni in prosa non bastano. La correzione
  conserva tutti gli altri errori di isolamento originali.
- **B04 r3 v9:** `error_max_turns`, prova non valutabile per il limite di otto
  turni del canale Claude. Non va trasformata in un successo comportamentale.
  Le tornate avviate vengono concluse senza nuove ripetizioni di questo caso.

Nei primi **68 eventi d'uso C3** controllati, la CLI riporta sempre
`isUsingOverage=false` e `overageDisabledReason=org_level_disabled`.
Le risposte riportano il modello effettivo `claude-haiku-4-5-20251001`.
Questa è prova osservata del consumo nell'abbonamento per quel campione,
non un conteggio di addebiti OpenRouter.


### Controllo degli URL su ogni dominio e del testo delle citazioni

I commit `7012164` e `b4455fe` portano il totale offline a **126/126**.
Il controllo delle citazioni non dipende più da un elenco di siti ammessi:
confronta ogni URL di riferimento con le risposte dei tool, compresi indirizzi
nudi e domini sconosciuti. Per esempio, B03 senza skill costruisce due indirizzi
`www.buddalaw.it/sentenza/...` che non compaiono nei risultati: ora vengono
rilevati, senza attribuire il problema al nome dell'organo scritto con maiuscole.

Le pagine iniziali offerte come navigazione (Cassazione, Italgiure, BuddaLaw)
e il repository della skill non sono collegamenti a decisioni. Se l'etichetta
cita invece un organo o gli estremi, anche una pagina iniziale deve essere
controllata come citazione. Questo evita falsi errori sui suggerimenti di
navigazione, mantenendo il confronto esatto dei link alle fonti.

I controlli testuali ignorano le maiuscole: «Corte Costituzionale» soddisfa
«Corte cost». Il confronto degli URL rimane esatto e non cambia le maiuscole
nei percorsi. La rivalutazione finale del confronto, senza nuove chiamate,
conferma **11/16** casi di qualità v8.4 e **5/15** senza skill, con una prova
non valutabile (B22 senza skill, limite di turni). B00 supera entrambe le
configurazioni ma resta fuori dal punteggio di qualità.

Le vecchie dichiarazioni di assenza di URL inventati sono risultati del
valutatore storico: non sono una certificazione secondo il controllo attuale.
Le tre cartelle citate per le prime 114 esecuzioni non sono presenti tra le
tracce locali disponibili di questa ripresa. I campioni correnti vengono
valutati separatamente, senza attribuire loro i vecchi esiti.


### Arresto sulla quota Claude Pro del 18 ottobre

La CLI riporta «You've hit your session limit · resets 3pm (Europe/Rome)»
alle 13:23 locali. Nessuna chiamata API o OpenRouter sostitutiva. La quota
non è un guasto BuddaLaw né un errore di ricerca della skill.

| C3, campioni sullo stesso hash | Stato prima del ripristino |
|---|---|
| B12 separato | 3/3 eseguite e valide, 0/3 promosse |
| Altri 25 casi | 58/59 registrate, 51 valide |
| Totale v9 C3 | **61/62 registrate, 54 valide** |
| Qualità, senza B00 | **13/21** casi valutabili promossi; B04/B21/B22 non valutabili; B25 non avviato |
| Link non fedeli nella v9 | B01 e B19: criterio di rilascio stabile non superato |

B21 r1–r3 e B22 r1–r2 sono risposte sintetiche della CLI per quota esaurita,
con costo e token zero, senza chiamate BuddaLaw. B22 r3 viene fermata prima
della risposta; B25 non viene avviata. Le risposte non contano nel denominatore
comportamentale. La dicitura generica di guasto nel vecchio arresto condiviso
non descrive un guasto del servizio in questo caso.

La vecchia versione del programma passava al caso successivo dopo il rifiuto
della quota. Il commit `3a52716` riconosce l'evento nativo
`rate_limit_event.status=rejected` e pubblica subito lo stop. I due nuovi test
verificano che nessuna azione successiva parta e che il solo rifiuto dei crediti
extra, con quota ordinaria ancora disponibile, non provochi un falso arresto.
Totale offline: **128/128**, con 12 live saltati nel comando ordinario.

Per terminare le prove bloccate dalla quota restano sette esecuzioni previste:
B21 ×3, B22 ×3 e B25 ×1. Gli originali si conservano; nessuna risposta già
bocciata per comportamento viene ripetuta per cercare un esito favorevole.
La PR resta in bozza in attesa della scelta sulla tempistica; l'istruzione
originale autorizza main al termine del collaudo.


### Chiusura dopo il ripristino Pro

Le prove mancanti sono concluse nella tornata `20261018-150152-757858`,
7/7 valide, con la stessa candidata e lo stesso file dei quesiti congelati.
L'arresto precedente è preservato; la nuova tornata usa un percorso di arresto
separato. L'accesso verificato resta `claude.ai` / `firstParty` / `pro` e gli
eventi d'uso riportano quota disponibile, `isUsingOverage=false` e crediti extra
disabilitati. La sintesi conclusiva in apertura prevale sulle note intermedie
«in attesa» di questa cronologia.
