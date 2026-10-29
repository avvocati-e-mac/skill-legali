# Revisione indipendente: modalità remota Docling

Revisione statica e simulata. Nessuna richiesta di rete, installazione, modifica di configurazioni, conversione o trasmissione di documenti. Nessuna sorgente modificata. Non sono stati letti TEST-REPORT né precedenti rapporti di revisione.

## Percorso di lettura

Partenza da `SKILL.md`. Sono state aperte `references/server-remoto.md` e `references/estrazione.md` per i passaggi fra host; `references/citazioni.md` per il caso C e i criteri di verifica; `references/contesto.md` per controllare gli avvisi sulle letture parziali; `references/installazione.md` per valutare compatibilità dichiarata e coerenza della documentazione. Letti inoltre `README.md` e `agents/openai.yaml` per la valutazione del materiale destinato all'utente e dell'entrypoint grafico.

`README.md` è nella cartella esterna della distribuzione, non accanto a `SKILL.md`: il primo tentativo di apertura accanto all'entrypoint ha restituito file assente; è stato poi individuato con un elenco di nomi, senza aprire i rapporti esclusi. Non sono servite le guide su scansioni, prestazioni o intervalli avanzati: i casi non forniscono documenti da ispezionare né richiedono profili o stime.

## A — PDF sul computer, conversione locale disponibile

Primo messaggio simulato:

> Uso Docling sul tuo computer e preparo il riassunto con i riferimenti alle pagine. Indicami il PDF da esaminare. Userò la numerazione delle pagine fisiche del file, partendo da 1, salvo una tua preferenza diversa. Se sarà necessario l'OCR o non potrò leggere tutto il contenuto insieme, ti avviserò prima.

Passi concretamente autorizzati:

1. Ottenere soltanto l'identificazione del PDF se non già presente nella conversazione; rispettare una preferenza di citazione già espressa.
2. Verificare catalogo, schemi, host e accesso al file sul computer locale. Non aprire la modalità remota né proporre installazioni se la conversione locale è disponibile.
3. Conservare originale e impronta, ispezionare il tipo di PDF e dichiarare l'eventuale campionamento. Aprire la guida sulle scansioni soltanto in presenza di indizi o dubbi; avvisare preventivamente se l'OCR è previsto.
4. Convertire e salvare Markdown, JSON e ricevuta. Rendere il contenuto integrale disponibile nel contesto quando possibile; altrimenti avvisare prima di procedere con una copertura ridotta.
5. Riscontrare le affermazioni sull'originale e consegnare il riassunto nello stile richiesto, distinguendo dichiarazioni e inferenze.

Esito: instradamento locale chiaro. La richiesta non autorizza cambi di rete o il passaggio a un altro host.

## B — Server funzionante, file soltanto sul portatile, nessun trasferimento

Primo messaggio simulato:

> Userò il server già indicato: Docling non deve essere installato anche sul portatile. Prima della conversione serve un canale autorizzato per trasferire il PDF e recuperare Markdown, JSON ed eventuali immagini. Quale canale possiamo usare fra portatile e server? Intanto posso verificare il collegamento MCP esistente e i tool disponibili, senza cambiare configurazioni.

Passi concretamente autorizzati:

1. Riutilizzare endpoint e rete privata esistenti. Se la disponibilità fornita non è stata già verificata nella sessione, controllare inizializzazione MCP e catalogo dal processo client effettivo; evitare domande su hardware o installazioni che non risolvono il requisito mancante.
2. Identificare il canale di trasferimento e ritorno realmente disponibile. La richiesta di conversione remota non crea una condivisione di cartelle né autorizza implicitamente ad aprirne una.
3. Fermare le operazioni dipendenti dal trasferimento finché il canale non è concordato. Non passare al server il percorso Download del client.
4. Dopo l'autorizzazione pertinente, trasferire il solo PDF necessario, confrontare le impronte di origine e copia e registrare la provenienza. Verificare anche il ritorno degli export prima di convertire.
5. Convertire sul server con la modalità locale del motore, usando il percorso leggibile da quel server. Recuperare gli originali degli export, verificarne l'integrità e procedere ai riferimenti di pagina.

Esito: guida adeguata. L'assenza di Docling sul portatile non dimostra nulla sull'installazione del server e non giustifica installazioni sul client.

## C — Conversione riuscita, export irrecuperabili, originale non legato tramite hash

Primo messaggio simulato:

> La conversione risulta riuscita, ma Markdown e JSON sono ancora sul server: al momento non posso consegnarti quei file né un dossier Docling completo. Manca anche il collegamento verificabile fra questa conversione e il PDF sul portatile. Serve recuperare gli export e identificare il PDF effettivamente convertito tramite un canale autorizzato. Se il PDF locale è leggibile, posso intanto controllarne direttamente i passi e le pagine, dichiarando questo metodo distinto.

Passi concretamente autorizzati:

1. Conservare chiave, ricevuta, percorsi restituiti e limiti già noti; non fingere accesso ai file salvati.
2. Verificare il catalogo disponibile senza inventare un tool di download o un percorso HTTP per scaricare file. In questo caso è dato che tali strumenti non ci sono.
3. Concordare un canale di recupero; non aprire nuove condivisioni come ripiego. Un export testuale può essere materiale letto con limiti dichiarati, ma non sostituisce i byte originali del Markdown e del JSON salvati.
4. Se disponibile sul server, identificare la copia effettivamente convertita e confrontarla con l'originale client, conservando la ricevuta. Un hash calcolato oggi su un file che potrebbe essere stato sostituito non prova retroattivamente quale file fu convertito. Se il collegamento non è ricostruibile, mantenerlo come limite o valutare una nuova conversione dopo avere risolto ingresso e uscita.
5. Non generare un registro di provenienze Docling da un JSON mai letto. Non promettere le tre consegne richieste finché sono irrealizzabili.
6. Un passo controllato direttamente sul PDF locale può invece avere pagina verificata su quel PDF, documentando il metodo e senza attribuirgli una provenienza Docling non dimostrata. Se si legge solo una parte, avvisare preventivamente.

Esito: `references/server-remoto.md` gestisce correttamente sia la consegna incompleta sia la possibilità di riscontro diretto. Il mancato hash iniziale impedisce di presumere l'identità della conversione; non rende impossibile qualunque verifica sul PDF attualmente leggibile.

## D — Browser locale raggiunge il server, connettore cloud fuori dalla VPN

Primo messaggio simulato:

> Il browser del portatile e il connettore nel cloud usano percorsi di rete diversi: l'apertura dell'URL nel browser non dimostra che il connettore possa raggiungerlo. Posso verificare dove gira il client MCP e quali collegamenti privati supporta. Per renderlo operativo servirà scegliere un percorso supportato, per esempio un client locale già collegato alla VPN; eventuali installazioni o modifiche alla rete richiedono una proposta concreta e un'autorizzazione distinta.

Passi concretamente autorizzati:

1. Leggere stato e tipo del connettore, sede del processo ed errore osservato, utilizzando solo accessi già disponibili.
2. Dichiarare il limite di raggiungibilità dal cloud. Non confondere la prova del browser con una prova del processo MCP.
3. Identificare un client locale supportato già disponibile oppure documentare una soluzione privata del fornitore se verificabile, senza attivarla.
4. Preparare soltanto la proposta necessaria e chiedere l'autorizzazione alle modifiche effettivamente necessarie prima di applicarle. Non esporre il servizio pubblicamente, ampliare regole o installare componenti come effetto della frase «falla funzionare» nelle condizioni esplicitamente date dal caso.

Esito: limite dichiarato correttamente; non emerge una soluzione operativa già autorizzata. Non si deve dichiarare completato il collegamento.

## E — Soltanto raggiungibilità del server privato

Primo messaggio simulato:

> Controllo la raggiungibilità dal processo che userà il collegamento MCP e distinguo l'accesso al servizio dall'inizializzazione del protocollo. Non occorre convertire un documento per questo controllo.

Passi concretamente autorizzati:

1. Usare l'endpoint già fornito o chiedere solo l'URL se manca, ad esempio `https://server-docling.example/mcp`.
2. Eseguire la verifica di connessione dal processo appropriato e, se necessario per verificare il servizio MCP, inizializzazione e catalogo. Registrare da dove è stato fatto il controllo.
3. Riferire con precisione il livello accertato: risposta di rete/servizio o sessione MCP funzionante. Un controllo dal server stesso non prova l'accesso dal client.
4. Non trasferire PDF, convertire documenti sintetici o della pratica, installare programmi o modificare il servizio. La prova completa del flusso descritta nella guida non è necessaria alla richiesta limitata.

Esito: la frase esplicita sulla diagnosi di rete in `references/server-remoto.md` impedisce l'estensione automatica alla conversione.

## Standard Docling e limiti della verifica

La documentazione mantiene la distribuzione ufficiale, separa l'esecuzione locale del motore sul server dalla delega a Docling Serve e lascia la configurazione del motore sul server. Non introduce wrapper, cache personalizzate, preset hardware obbligatori o un secondo motore sul client. Le istruzioni richiedono help, schemi e catalogo effettivi e distinguono percorsi server e client.

Questa è una valutazione di coerenza statica. Non è stata verificata la corrispondenza dei comandi con una versione installata, non sono state consultate fonti di rete e non è stata provata la compatibilità dei client o dei trasporti. La guida stessa rende le verifiche operative condizionali: il rapporto non le dichiara eseguite.

## README, privacy e regole conservate

Il README è adatto a non tecnici: distingue skill, collegamento MCP e programma, spiega VPN e filesystem con esempi leggibili e avverte chiaramente che analisi online e conversione locale sono passaggi distinti. Spiega anche la differenza fra invio dei contenuti, conservazione e miglioramento dei modelli senza equiparare i piani. La sezione remota resta opzionale e conserva il percorso locale predefinito.

La scansione testuale dei file distribuiti della skill e del README non ha evidenziato nomi di persone, percorsi personali, indirizzi di rete privata specifici, chiavi o token. Gli esempi di endpoint remoto usano un dominio `.example`; gli esempi di percorsi sono segnaposto. Si tratta di una verifica testuale mirata, non di una certificazione forense del pacchetto binario o dei file di test.

Restano esplicite le preferenze di citazione, la numerazione fisica e quella stampata, la verifica dell'originale, il controllo logico del supporto, il trattamento prudente dell'OCR, la conservazione degli originali e l'avviso prima di ridurre il contesto. La guida remota non li sostituisce con una semplice fiducia nel salvataggio del server.

## Difetto concreto e circoscritto

In `references/installazione.md`, sezione «Prova conclusiva», la frase «Senza JSON accessibile le citazioni non sono pronte, anche se la conversione è riuscita» è assoluta. In `references/server-remoto.md`, sezione «PDF in ingresso e risultati in uscita», è invece consentito citare un passo controllato direttamente su un originale accessibile, distinguendo quel metodo dal dossier Docling incompleto. La seconda regola è più precisa.

Conseguenza dimostrabile: un agente che si arrestasse alla prima frase potrebbe negare anche citazioni direttamente verificate sul PDF nel caso C. La guida remota contiene già la correzione sostanziale, quindi non è un difetto bloccante del flusso remoto. Correzione consigliata: limitare la frase di installazione alle citazioni basate sulle provenienze Docling o al completamento del dossier, richiamando la verifica diretta distinta.

Non sono emersi altri difetti dimostrabili nei cinque casi con le condizioni date. L'assenza di prove reali di rete e conversione è un limite deliberato della revisione, non un successo operativo né un difetto accertato della skill.

## Addendum — ricontrollo mirato dopo la correzione

Riletto soltanto il passaggio corretto della sezione «Prova conclusiva» in `references/installazione.md` e confrontato con il paragrafo sulle consegne irrecuperabili in `references/server-remoto.md`.

Il conflitto segnalato è risolto. Il testo di installazione ora limita correttamente l'impedimento, in assenza di JSON accessibile, alla generazione degli indici Docling e alla dichiarazione di completezza del dossier. Consente esplicitamente il riscontro diretto sul PDF accessibile come metodo distinto, senza inventare provenienze Docling. La guida remota esprime la stessa distinzione.

La sezione precedente conserva il rilievo storico della prima lettura e non descrive più un difetto aperto della versione corretta. Non sono stati ripetuti i cinque casi né eseguite prove di rete o modifiche delle sorgenti.
