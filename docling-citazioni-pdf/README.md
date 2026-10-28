# Docling: trovare nei PDF la pagina da cui proviene un'affermazione

Questa skill aiuta l'assistente IA a preparare riassunti, cronologie e appunti
indicando **in quale pagina del documento si trova il passaggio utilizzato**.
È pensata per il lavoro dell'avvocato con contratti, lettere, perizie e altri
PDF della pratica.

Esempio di richiesta:

> Leggi il contratto e le lettere. Prepara una cronologia e, per ogni fatto,
> indica la pagina del documento da cui lo ricavi. Segnala le contraddizioni
> e ciò che non riesci a verificare.

**Prima di usare documenti riservati:** Docling può estrarne il contenuto sul
tuo computer. Se poi usi Claude o ChatGPT per analizzarlo, il contenuto che
l'assistente legge viene inviato ai server del rispettivo fornitore:
**Anthropic per Claude, OpenAI per ChatGPT**. Questo vale anche quando il PDF
originale resta nella cartella della pratica e l'app è installata sul computer.

## Come funziona: la scrivania e il collaboratore esterno

Immagina due passaggi del lavoro di studio.

1. **Docling prepara le copie sulla tua scrivania.** Legge il PDF, ne estrae
   testo e tabelle e annota i riferimenti alle pagine. Nella configurazione
   locale descritta dalla guida, questo lavoro avviene sul tuo computer.
2. **L'assistente legge le copie e prepara la risposta.** Se l'assistente è
   Claude o ChatGPT, è come affidare le copie a un collaboratore che lavora
   in un altro ufficio: il contenuto necessario all'analisi deve raggiungerlo
   attraverso Internet. I server sono i computer del fornitore che elaborano
   la richiesta e producono la risposta.

La **skill** è il foglio di istruzioni dato a questo collaboratore: gli spiega
come leggere, controllare e citare. Il collegamento chiamato **MCP** permette
all'assistente di chiedere il lavoro a Docling e riceverne i risultati.
La presenza di questo collegamento sul computer non impedisce l'invio di quei
risultati al servizio IA online.

## Riservatezza: quali informazioni escono dal computer

**Docling locale significa estrazione locale. Non significa che anche
l'analisi di Claude o ChatGPT avvenga sul tuo computer.**

Per esempio, `contratto.pdf` contiene nome del cliente, indirizzo e codice
fiscale. Docling ne ricava il testo sul computer. Quando quel testo viene
fornito a Claude per ottenere un riassunto, quei dati vengono trasmessi ad
Anthropic; usando ChatGPT, vengono trasmessi a OpenAI. Lo stesso vale per le
immagini delle pagine mostrate all'assistente per controllare una scansione.
Non è necessario inviare il PDF originale perché il suo contenuto venga
comunicato all'esterno: anche il testo estratto contiene le informazioni.

È come fotocopiare un fascicolo in studio e poi spedire le copie a un
collaboratore esterno. La fotocopiatrice è in studio, ma le copie escono.

Tieni distinti tre aspetti:

- **Invio per ottenere la risposta:** il servizio online riceve il contenuto
  che deve analizzare.
- **Conservazione:** per quanto tempo e con quali modalità il servizio
  conserva conversazioni, allegati o altri dati.
- **Uso per migliorare i modelli:** se quei contenuti possono essere impiegati
  anche per sviluppare il sistema IA.

Le condizioni degli ultimi due aspetti dipendono dal servizio, dal piano e
dalle impostazioni effettive. Un'opzione che esclude l'uso per migliorare i
modelli **non impedisce l'invio necessario a ottenere la risposta online**.
Questa guida non attribuisce a tutti gli abbonamenti le stesse condizioni.

Prima di usare una pratica riservata, verifica quali contenuti lo studio può
affidare al servizio scelto e le condizioni applicabili. Se prepari una copia
con dati oscurati, controlla che siano stati rimossi davvero: chiamare il file
`contratto-anonimo.pdf` non cancella il nome del cliente scritto al suo interno.

Se l'esigenza è che **nessun contenuto lasci il computer**, serve un ambiente
in cui anche l'assistente che svolge l'analisi e gli strumenti usati lavorino
localmente, senza trasmettere i documenti a servizi esterni. La sola
installazione locale di Docling, usata insieme a Claude o ChatGPT online,
non soddisfa questa esigenza.

## Come vengono scritte le citazioni

Con un solo PDF, il riferimento resta breve:

> Il pagamento è previsto entro trenta giorni (p. 4).

Con più PDF viene aggiunto il nome del documento:

> Il pagamento è previsto entro trenta giorni (p. 4 del documento `contratto.pdf`).

Puoi scegliere il tuo stile. Per esempio:

> Usa «pag.» e il numero dell'allegato: «all. 3, pag. 4».

Se non dai indicazioni diverse, i numeri contano le pagine del PDF partendo
dalla prima, compresa un'eventuale copertina. È la numerazione usata quando
sfogli il file dall'inizio. Un numero stampato sulla pagina può essere diverso:
la terza pagina del PDF potrebbe riportare «41». L'assistente deve distinguere
le due numerazioni e può usare quella stampata se l'ha controllata e glielo chiedi.

## Che cosa viene controllato e che cosa resta da verificare

Il riferimento di pagina dato da Docling è come un **segnalibro provvisorio**:
indica dove cercare. L'assistente deve confrontare il passaggio con l'originale
prima di presentarlo come verificato. Se non può farlo, deve dirlo chiaramente.

Conta anche il significato del passaggio. Se una lettera dice «il fornitore
dichiara di avere consegnato», il riassunto deve conservare questa distinzione:
la lettera documenta una dichiarazione, non dimostra da sola la consegna.

La skill aiuta a ritrovare e controllare le fonti. La rilettura dell'avvocato
resta necessaria per scegliere i passaggi da utilizzare, valutarne il peso e
controllare le citazioni importanti. Per stabilire se una norma è aggiornata
o una sentenza è pertinente occorre anche la verifica sulle fonti giuridiche.

## Se il PDF è una scansione

Una scansione può contenere soltanto l'immagine della pagina. Per ricavarne
parole utilizzabili serve l'**OCR**, cioè il riconoscimento automatico del testo.
Pensalo come la trascrizione di una fotocopia: una cifra poco chiara può essere
letta male.

La skill cerca gli indizi di scansione e avvisa prima dell'elaborazione quando
è previsto l'OCR. Deve distinguere un controllo su tutte le pagine da un
controllo soltanto su alcune. Se non riesce ad accertare il tipo del PDF o le
impostazioni di riconoscimento, deve segnalare il dubbio.

Una scansione può anche avere già un testo selezionabile ricavato in precedenza
con OCR. Quel testo può essere sbagliato: in una prova l'immagine mostrava
**1.200 euro**, mentre il testo associato riportava **12.000 euro**. Per questo
nomi, date, importi e citazioni delicate richiedono il confronto con l'immagine
originale, anche quando il testo si riesce a selezionare.

## Se il fascicolo è troppo grande

Pensa allo spazio di lavoro dell'assistente come a una **scrivania di dimensioni
limitate**. I file conservati nell'armadio sono disponibili, ma non sono per
questo tutti aperti sulla scrivania nello stesso momento.

Quando c'è spazio, la skill richiede di rendere disponibile all'assistente
l'intero contenuto dei documenti per l'analisi. Con Claude o ChatGPT online,
questo comporta l'invio di quel contenuto al servizio, come spiegato sopra.

Se non entra tutto insieme, l'assistente deve avvertirti **prima** di procedere
con estratti, riassunti o gruppi di documenti. Per esempio:

> Il fascicolo non entra tutto insieme nello spazio disponibile. Posso esaminarlo
> per gruppi, tenendo un registro dei passaggi e delle pagine. Nei confronti fra
> documenti dovrò riaprire i brani originali: il registro non sostituisce il
> contenuto integrale di tutti i PDF.

La skill carica invece le proprie istruzioni di dettaglio solo quando servono:
è come consultare il capitolo pertinente di un manuale. Questo risparmio sulle
istruzioni non autorizza a leggere soltanto pezzi dei documenti senza avvisarti.

## Come inserirla nel lavoro dello studio

Puoi mantenere la cartella della pratica che usi già. Indica all'assistente i
PDF da esaminare e, dopo avere valutato l'invio dei dati al servizio scelto,
concedi l'accesso necessario. Gli originali vengono conservati.

Per una risposta breve bastano le citazioni vicino alle frasi. Per una
cronologia o un lavoro con più documenti, la skill prepara anche un **registro
delle fonti**: un elenco che collega ogni affermazione al documento, al passo
e alla pagina controllati. Puoi usarlo mentre scrivi in Word o in altri programmi.

Il registro conserva anche un'impronta digitale del file: un codice che cambia
se cambia il contenuto. È come il numero identificativo di una particolare
copia del fascicolo. Se sostituisci un PDF con una versione diversa, le sue
citazioni devono essere ricontrollate.

## Che cosa serve e come si installa

Servono due cose: le istruzioni della skill nell'assistente e il programma
Docling collegato correttamente. Installare le sole istruzioni è come
consegnare il manuale di una fotocopiatrice senza avere ancora la macchina.

- **Codex:** copia la cartella interna `docling-citazioni-pdf/`, quella che
  contiene `SKILL.md`, in `~/.agents/skills/` oppure nella cartella
  `.agents/skills/` del progetto.
- **Claude Code:** copia la stessa cartella in `~/.claude/skills/` oppure in
  `.claude/skills/` del progetto. Puoi richiamarla con `/docling-citazioni-pdf`.
- **Cowork/Claude Desktop:** carica [il pacchetto della skill](docling-citazioni-pdf.skill)
  attraverso la gestione delle skill disponibile nella tua versione.

Il file `.skill` è il pacchetto pronto da installare. Se il programma Docling
o il collegamento mancano, la skill aiuta a individuare il problema e prepara
la procedura adatta. La disponibilità del collegamento dipende dall'applicazione
che usi: installare una skill non concede da solo accesso ai file del computer.

La [guida di installazione](docling-citazioni-pdf/references/installazione.md)
contiene i passaggi tecnici per l'installazione standard ufficiale di Docling
MCP. Puoi seguirla con l'assistente o affidarla a chi cura i computer dello
studio. Per fascicoli lunghi, specialmente con scansioni e tabelle, un computer
senza accelerazione grafica può impiegare più tempo: l'assistente deve avvisarti.
I dettagli e i confronti pubblicati sono nella
[guida ai tempi di elaborazione](docling-citazioni-pdf/references/prestazioni.md).

## Verifiche e approfondimenti

Il [rapporto delle prove](TEST-REPORT.md) descrive i controlli eseguiti e quelli
ancora non coperti. I documenti di prova sono inventati e non contengono dati
di clienti. Le prove non garantiscono che ogni PDF, ogni versione dell'app o
ogni risposta dell'IA funzioni allo stesso modo.

<details>
<summary>Per chi cura il repository: verifiche tecniche</summary>

Dalla cartella principale del repository:

```sh
python3 -B -m unittest discover -s docling-citazioni-pdf/tests -v
```

I requisiti delle prove facoltative sono indicati nel rapporto. Non usare
fascicoli riservati nei test pubblici.

Fonti per l'installazione delle skill: [Codex](https://learn.chatgpt.com/docs/build-skills)
e [Claude Code](https://code.claude.com/docs/en/skills).

</details>
