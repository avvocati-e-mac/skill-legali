# BuddaLaw — Report di collaudo v9.0

**Data:** 2026-10-17
**Versione collaudata:** 9.0 (branch `feat/buddalaw-v9`)
**Confronto previsto:** v8.4 (tag `buddalaw-v8.4`) e nessuna skill
**Metodo:** tre livelli. A = controlli sui file, senza rete. B = conversazioni vere con BuddaLaw. C = chiamate dirette al server.

> **In una riga.** Nella prima tornata completa, con il server funzionante, la v9.0 con Haiku supera 24 casi su 26, e 17 su 18 fra quelli critici ⚡ (94%), senza nessun link inventato. Poi il server BuddaLaw ha smesso di rispondere («Circuit breaker aperto — backend temporaneamente non disponibile»). Le ripetizioni, il confronto con la v8.4 e il livello C sono quindi da rifare. Il collaudo ha trovato un difetto vero, l'avviso di aggiornamento che non compariva mai: è corretto nella skill, ma la correzione non è ancora stata provata dal vivo.

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
| Zero link inventati | sì: 114 esecuzioni su 114 |
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
