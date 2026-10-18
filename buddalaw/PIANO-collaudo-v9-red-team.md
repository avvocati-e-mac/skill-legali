# BuddaLaw v9 — revisione critica e piano di collaudo

Data: 17–18 ottobre 2026. Obiettivo: decidere se la skill sia pronta, distinguendo difetti delle istruzioni, limiti dei modelli ed errori del programma di prova. Il maintainer ha autorizzato test live e correzioni; restano invariati lo stop su blocchi/guasti, il tetto di spesa e il divieto di aggiornare copie installate o unire la PR senza autorizzazione.

**Istruzione successiva del maintainer (18 ottobre):** completare il collaudo
con l'abbonamento Claude, escludendo ulteriori chiamate OpenRouter. Usare
`--solo-abbonamento`, che verifica l'accesso prima di avviare i modelli.
Le soglie e le tornate Qwen/DeepSeek sotto riportate restano obiettivi storici
non conclusi, senza promozione di quei modelli. Il passaggio a `main` al termine
dei test è già autorizzato dalla richiesta di ripresa. Una pubblicazione beta
deve indicare esplicitamente i controlli mancanti e i difetti ancora osservati.

## Critiche al piano precedente

| Attacco al piano | Evidenza o rischio concreto | Correzione prima dei nuovi test |
|---|---|---|
| Il programma promuove una risposta che viola la skill | Sul caso sanitario i controlli generali davano verde anche con più di quattro ricerche | Controlli comuni per budget delle ricerche per quesito, schema, provenienza dei link e distinzione fra integrali richiesti e ottenuti; regole specifiche della v9 separate dal confronto con versioni precedenti |
| Il test dell'avviso non arriva al modello | Riprodotto: `prepara_skill('v9-ridotta')` modifica anche righe descrittive e solleva un errore | Alterare soltanto l'elenco JSON dell'inventario; prova offline prima delle chiamate live |
| Una fonte può essere soltanto un esempio della skill | Riprodotto: un URL presente nel testo delle istruzioni passa il controllo del corpus indistinto | Conservare il nome e l'origine di ogni risultato; escludere skill, ricerca dei tool e file estranei dal corpus probatorio |
| Il controllo delle citazioni può sbagliare in entrambe le direzioni | Riprodotto: due brevi parole tra virgolette fanno catturare il paragrafo intermedio; numero e anno erano cercati separatamente in tutto il corpus | Abbinare le virgolette prima di valutarne la lunghezza; controllare il passo nel testo della fonte, non nella sintesi; associare numero e anno allo stesso risultato |
| Nessuna prova eseguita può risultare verde | Il ritorno `all([])` promuove una suite vuota o tutta saltata | Copertura pianificata esplicita, errore su ID sconosciuti, ripetizioni incomplete non promosse, isolamento persistito per le rivalutazioni |
| Lo stop non è davvero immediato | Gli eventi erano analizzati dopo l'uscita del processo e dopo tutti i turni | Leggere gli eventi mentre arrivano; fermare processo e figli al primo blocco, senza inviare il turno successivo; conservare trace e costo parziale noto |
| Le tre ripetizioni possono diventare quattro e consumare inutilmente | Il piano chiedeva una tornata completa più altre tre ripetizioni | Un solo piano: casi ordinari una volta, critici tre volte complessive; registro della spesa e versione congelata |
| Il confronto GPT/OpenCode confonde modello e ambiente | GPT aveva Normattiva e MCP nativi; OpenCode solo BuddaLaw e limiti diversi | Non usare il singolo caso come classifica generale. Confrontare v9/v8.4/nessuna nello stesso ambiente e registrare modello reale, configurazione, hash di skill/casi/schema |
| Una prova riuscita di isolamento non garantisce le successive | Nella nuova partenza OpenCode ha selezionato la copia globale omonima; il controllo ha fermato il modello | Separare la configurazione con `XDG_CONFIG_HOME`, senza spostare o leggere credenziali; verificare il percorso esatto prima di ogni esecuzione |
| Una diagnostica vuota viene scambiata per un cambiamento del servizio | Il proxy Claude non esponeva definizioni MCP con ToolSearch disattivato automaticamente | Errore esplicito invece di fixture vuota; attivazione documentata di ToolSearch per il proxy. Il nuovo confronto live ha confermato lo schema invariato |
| Un collegamento fallito viene attribuito al modello | B03 r2: Qwen dichiara tool assenti; il log della stessa sessione conferma `server unavailable`, `key=buddalaw`, `status=failed` | Controllare anche gli errori di avvio mentre arrivano, fermare la tornata e classificare la prova come non valutabile; non inserirla nel denominatore comportamentale |
| Il modello principale non è l'unico che genera costi | OpenCode avvia anche un modello ausiliario per i titoli, ereditato dalle impostazioni | Impostare anche `small_model` sul modello richiesto e non presentare i soli costi degli step come fatturazione totale garantita |
| Una percentuale alta può nascondere un errore grave | Qwen ha alterato un URL; tre ripetizioni non misurano l'affidabilità generale | Nessun via libera stabile con URL giurisprudenziali alterati o fonti attribuite impropriamente. Mostrare anche i singoli errori; escludere l'isolamento dal punteggio di qualità |
| Correggere sul solo quesito del chirurgo può adattare la skill all'esempio | È un solo caso e contiene questioni fattuali e cliniche non verificate dai controlli automatici | Prima riprodurre i fallimenti; modifiche brevi e generali soltanto quando sostenute dai dati; provare poi quesiti diversi, senza cambiare attese per farli passare |

## Esecuzione migliorata

1. Correggere e attaccare offline il programma di prova. I test devono fallire sui difetti sopra, poi passare dopo la correzione. Non aggiungere istruzioni alla skill per compensare errori del programma.
2. Risolvere il canale Claude senza aggiornamenti automatici: la CLI installata è 2.1.289, mentre la documentazione richiede almeno 2.1.293 per Haiku 5.5. Provare una versione compatibile, registrare il modello effettivo e tenere separati i nuovi risultati dal vecchio campione dichiarato Haiku 5.5. Fonte: [documentazione Claude Code](https://code.claude.com/docs/en/model-config).
3. Una sola prova `check_access`, quindi livello C. Se il server segnala blocco o guasto, stop globale senza tentativi automatici. Un limite del canale non è un difetto della skill; se il canale non è disponibile, documentarlo e proseguire soltanto col lavoro indipendente.
4. Congelare v9, casi, schema e configurazione. Collaudo completo OpenCode con DeepSeek e Qwen: casi ordinari una volta, critici tre volte complessive. Nessun limite imposto dal programma alle ricerche del modello: violerebbe la misurazione del comportamento della skill. Il programma ferma invece spesa, guasti e durata.
5. Verificare prima i fallimenti già osservati: limite ricerche, copia esatta dei link, formato di `anno`/`paragraphs`, avviso presente e assente, turni multipli e `not_found`. Sul quesito sanitario controllare manualmente anche la cronologia dei fatti; le risposte originali rimangono immutate.
6. Valutare correzioni della skill soltanto su fallimenti riprodotti e attribuibili alle istruzioni. Ogni candidata resta distinta dalla v9 iniziale, con archivio rigenerato e confronto sullo stesso modello. Nessuna correzione della risposta dopo il test può contare come successo del modello.
7. Confronto v8.4/nessuna sugli stessi casi critici nello stesso ambiente; controlli comuni confrontabili e controlli propri della v9 riportati separatamente. Per i punti controversi conservare fonti grezze e segnalare ciò che non è verificabile.
8. Report conclusivo con copertura completa/incompleta, esiti per modello e versione, fallimenti gravi, costi noti e limiti metodologici. Non promuovere un modello o la skill per un aggregato che nasconde errori nelle fonti. PR sempre in bozza finché il maintainer non decide il rilascio.

## Primi risultati della revisione

- Prima delle correzioni, 11 dei primi 12 attacchi offline riproducevano difetti
  del valutatore. Dopo le correzioni e i controlli sulle date complete e
  sull'avvio MCP: **89/89 controlli offline** superati.
- **12/12 controlli del livello C** superati con Haiku 4.5: 11 test di
  comportamento in una tornata e T74 sullo schema dopo la correzione del canale.
  La fixture non è stata riscritta. Le 13 chiamate dei test di comportamento
  hanno riportato 0,4923 $, esclusi controllo di accesso e diagnostica.
- OpenCode riautorizzato con successo; tre inventari consecutivi nella nuova
  configurazione vedono soltanto la skill di prova e una skill incorporata
  comunque negata al modello. La copia globale non è stata modificata.
- Suite completa avviata sulla v9 originale congelata. Il tetto della nuova
  tornata è **3 $ per modello**. **Interrotta** dopo aver diagnosticato il
  collegamento intermittente di OpenCode: 13 esecuzioni registrate su 124
  previste, 11 valide e 2 non valutabili. Nessuna promozione complessiva.
- Il singolo controllo B00 senza skill di DeepSeek è fallito per la lingua
  inglese, senza contaminazione della skill. Si conserva come fallimento;
  B00 resta escluso dal punteggio di qualità giuridica/comportamentale.
- Nessuna modifica alle istruzioni della skill o all'archivio installabile:
  le correzioni finora riguardano il metodo di misura e il collegamento.

La prossima tornata deve verificare il collegamento nell'avvio effettivo del
processo che usa il modello: un `mcp list` riuscito in un processo precedente
non è sufficiente. Il nuovo controllo è stato provato offline con un processo
che segnala il guasto e poi tenterebbe un'altra azione: viene fermato prima
che l'azione avvenga. Non sono stati effettuati ritenti di ricerca dopo lo stop.

Per gli esiti finali e la copertura effettiva vale il report di collaudo; questi
risultati intermedi non costituiscono una promozione della skill.

## Criteri della decisione

- Controlli offline e contratto live del server verificati, oppure impedimento esattamente documentato.
- Copertura prevista effettivamente eseguita; un caso senza risposte valide non è superato.
- Soglia descrittiva del piano originario (90% Haiku, 80% DeepSeek/Qwen sui casi critici) accompagnata dai singoli conteggi; non equivale a una garanzia statistica.
- Zero URL giurisprudenziali alterati o fonti inventate nel campione finale; anomalie di metadata del servizio distinte dalle alterazioni del modello.
- Avviso di aggiornamento verificato presente, assente e non ripetuto; gestione corretta di `not_found` e guasti.
- Nessuna pretesa di qualità giuridica generale fondata soltanto su regex, numero di chiamate o autocertificazioni del modello.
