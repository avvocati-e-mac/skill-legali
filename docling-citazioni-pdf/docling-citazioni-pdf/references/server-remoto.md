# Docling su un altro computer tramite rete privata

Apri questa guida **solo** se l'utente richiede la modalità remota o usa già un
server su un altro computer. Il flusso predefinito resta Docling sullo stesso
computer, con collegamento locale standard. Qui «client» è il computer da cui
si lavora; «server» è quello che esegue Docling. Non occorre installare Docling
anche sul client per collegarsi al server; gli helper PDF possono invece usare
un lettore locale disponibile.

Questa modalità usa il server Docling MCP ufficiale. Cambia il collegamento,
non introduce una distribuzione personalizzata o un servizio di conversione
pubblico. Mantieni **`DOCLING_MCP_CONVERSION_MODE=local` sul server**: il valore
`remote` configura invece la delega a Docling Serve, un'architettura diversa.

## 1. Verifica iniziale, senza riconfigurare

Raccogli solo le informazioni mancanti, anche con una domanda breve:

> Hai già Tailscale o un'altra VPN privata che collega i due computer? Quale
> computer deve eseguire Docling e con quale sistema operativo, processore,
> memoria ed eventuale accelerazione grafica? Docling è già funzionante?
> Come saranno disponibili i PDF sul server e come recupereremo i risultati?

Se endpoint e collegamento sono già configurati, provali prima di proporre
installazioni o nuove domande. Non dedurre che Docling manchi dal server perché
non è nel Python o nel PATH del client. Esegui la diagnostica sul server solo
tramite un canale disponibile e autorizzato; altrimenti dichiara il limite.

Valuta l'hardware sul server: anche la CPU può eseguire Docling. Per un lotto
impegnativo, se utile, proponi una conversione sintetica o rappresentativa
autorizzata per osservare tempi, memoria ed errori. Non inventare soglie minime
universali e non considerare una GPU obbligatoria. Per stime apri
[prestazioni.md](prestazioni.md). La sola diagnosi di rete non richiede di
convertire un documento della pratica.

Prima di trasferire un PDF controlla anche il percorso di ritorno dei risultati:
un endpoint MCP funzionante non garantisce la consegna di file al client.

## 2. Scegli il collegamento privato

Mantieni la soluzione scelta dall'utente o già funzionante. Le alternative sono:

| Soluzione | Dove ascolta Docling | Come si collega il client |
|---|---|---|
| Diretto tramite VPN | Solo sull'indirizzo VPN del server | URL privato con porta e percorso MCP verificati |
| Proxy privato, ad esempio Tailscale Serve | Sull'indirizzo di loopback `127.0.0.1` | URL HTTPS del proxy, disponibile nella rete privata |

Il loopback è raggiungibile soltanto dal computer che lo ospita: non passarne
l'URL a un altro computer come se fosse l'indirizzo del server. Per il
collegamento diretto verifica che la VPN protegga effettivamente il percorso;
non presentare HTTP come HTTPS. Non usare ascolto su tutte le interfacce
(`0.0.0.0` o `::`) come scorciatoia. Con altre VPN accerta interfacce, instradamento
e restrizioni equivalenti, senza presumere il comportamento di Tailscale.

Tailscale Serve condivide il servizio nella tailnet, cioè la rete privata dei
dispositivi collegati. **Funnel lo espone a Internet**: non è un'alternativa
equivalente e non fa parte di questa modalità. Non attivarlo per risolvere un
errore di connessione. Non presumere che la sola appartenenza alla VPN limiti
l'accesso ai dispositivi voluti: verifica le regole effettive, soprattutto se
il server MCP non richiede un'autenticazione aggiuntiva.

Le regole di accesso vanno valutate insieme: aggiungere una concessione stretta
non annulla una concessione più ampia già presente. Non modificare regole VPN,
firewall o altre applicazioni come conseguenza implicita di una lettura PDF.

## 3. Preparazione sul server, soltanto se necessaria

Riusa l'installazione standard funzionante. Rileva eseguibile, versione e
opzioni reali con `--help`, stato della VPN e disponibilità della porta scelta.
I segnaposto sotto **vanno sostituiti**: non sono una configurazione pronta.

Per l'ascolto diretto sull'indirizzo VPN, il comando di riferimento è:

```sh
DOCLING_MCP_CONVERSION_MODE=local uvx --from 'docling-mcp[local]' docling-mcp-server --transport streamable-http --host 'IP_VPN_DEL_SERVER' --port PORTA_SCELTA
```

Per un proxy privato cambia l'host in `127.0.0.1`, poi configura il proxy verso
quella porta con la sintassi effettivamente disponibile. Con Tailscale verifica
`tailscale serve --help` e `tailscale serve status`; il comando può richiedere
l'abilitazione di funzioni HTTPS. Non azzerare configurazioni Serve esistenti.
Non aggiungere wrapper o preset hardware/cache alla procedura standard.

Mostra prima le configurazioni proposte e ottieni l'autorizzazione per le
modifiche non già approvate: avvio del servizio, collegamento persistente,
proxy, regole di accesso e avvio automatico sono operazioni distinte. Non
richiedere di nuovo un'approvazione già valida. Non sostituire configurazioni
esistenti o reinstallare componenti funzionanti.

L'avvio automatico è facoltativo e dipende dal sistema operativo. Se richiesto,
prepara il file appropriato con percorsi stabili, log e modalità per fermare o
riavviare il servizio. Un eseguibile individuato dentro una cache eliminabile
è un percorso fragile, non un modello da copiare nella guida. Distingui avvio
all'accesso dell'utente da avvio all'accensione e prova il caso effettivamente
richiesto, compresa la disponibilità iniziale della VPN.

## 4. Collegamento dal client

Prima verifica che il **processo client MCP** possa raggiungere la rete privata.
Un browser locale che apre l'URL non prova che possa farlo un connettore avviato
nel cloud di un fornitore. Un indirizzo privato non diventa automaticamente
raggiungibile dai server di Anthropic o OpenAI. In Cowork/Desktop verifica il
tipo di connettore e il luogo in cui gira, senza promettere accesso dalla sola
presenza dell'app. Se manca un percorso supportato, dichiara il limite; eventuali
soluzioni del fornitore per reti private richiedono valutazione distinta.

Su client Codex o Claude Code che gira nel computer collegato alla VPN, verifica
l'help e l'eventuale voce `docling` già presente. Conserva le altre connessioni
e scegli esplicitamente cosa fare in caso di conflitto. Esempi di collegamento
a un URL **illustrativo**, da sostituire con quello verificato:

```sh
codex mcp add docling --url https://server-docling.example/mcp
```

Oppure, in `config.toml` di Codex:

```toml
[mcp_servers.docling]
url = "https://server-docling.example/mcp"
```

Per Claude Code:

```sh
claude mcp add --transport http docling https://server-docling.example/mcp
```

Controlla lo scope della configurazione prima di aggiungerla. Il trasporto HTTP
di Claude Code comprende l'uso dell'URL HTTPS; non trasformare automaticamente
un endpoint diretto HTTP in HTTPS o viceversa. La variabile di conversione si
configura **sul server**: non aggiungere `--env` al collegamento HTTP del client
come se questo avviasse il server remoto.

## 5. PDF in ingresso e risultati in uscita

La VPN collega i computer, **non condivide automaticamente le cartelle**.
`source` deve indicare un percorso assoluto leggibile dal server. Un percorso
del portatile o del suo ambiente isolato non vale automaticamente sull'altro
computer. Se il PDF è soltanto sul client, usa una condivisione o un trasferimento
già autorizzato; in mancanza, concorda il canale prima della conversione.
Trasferisci solo i file necessari, conserva gli originali e confronta gli SHA-256
di origine e copia, con gli strumenti effettivamente disponibili.

I percorsi `md_file` e `json_file` restituiti da `save_docling_document` sono
percorsi **del server**. L'URL MCP non è un servizio di download di quei file.
Usa strumenti di recupero realmente esposti, una cartella condivisa oppure un
trasferimento autorizzato, ad esempio SFTP; non inventare endpoint `/download`
o `/exports`, mount o tool mancanti. Non aprire nuove condivisioni per aggirare
il problema. Recupera i file originali senza ricrearli dal testo dei tool e
verifica l'integrità fra server e client; considera anche le immagini referenziate.

Dopo il recupero genera gli indici di pagina dal JSON originale come indicato
in [citazioni.md](citazioni.md). Per le verifiche sull'originale usa il PDF
esatto a cui si riferisce la conversione, anche se copiato sul client: nome
uguale non basta. Conserva ricevuta, chiave, hash, provenienze e luoghi dei file.
Un server condiviso non implica cache separate per utente: usa le chiavi della
propria conversione e non cancellare documenti altrui.

Se il recupero non è possibile, dichiara quali consegne mancano. Non presentare
un dossier completo o metadati come citazioni verificate. Un passo controllato
direttamente su un originale accessibile può essere citato con quel metodo,
distinguendolo dal dossier Docling rimasto incompleto. Per contenuti lunghi e
limiti del prompt continua ad applicare [contesto.md](contesto.md).

## 6. Prova e dichiarazione dell'esito

Distingui le prove e falle dalla macchina corretta:

1. Risposta del servizio sul server stesso.
2. Inizializzazione MCP ed elenco dei tool dal client che sarà usato.
3. Conversione dal client di un PDF sintetico autorizzato e accessibile al server.
4. Salvataggio, recupero di Markdown/JSON e confronto degli hash.
5. Generazione dei riferimenti e riscontro di una citazione sul PDF originale.
6. Se richiesti, controllo delle restrizioni di accesso e prova dell'avvio automatico.

HTTP 200, `mcp list` o un processo attivo da soli non provano il flusso completo.
Non dichiarare una prova dal client se è stata svolta solo dal server, né una
prova di riavvio mai eseguita. Registra esiti, file prodotti e limiti effettivi,
senza pubblicare identificativi della rete o configurazioni personali.

## Riservatezza e riferimenti

I PDF possono lasciare il client per raggiungere il computer di conversione
autorizzato. La VPN protegge quel collegamento secondo la propria configurazione;
non rende locale l'analisi di un assistente online. Il testo e le immagini
forniti a Claude o ChatGPT continuano a essere inviati al relativo servizio.
Prima di utilizzare documenti riservati rendi chiari questi passaggi, come nel
README della skill. Non equiparare un server privato a un ambiente totalmente offline.

Fonti: [Docling MCP](https://github.com/docling-project/docling-mcp/blob/main/README.md),
[Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve),
[regole di accesso Tailscale](https://tailscale.com/docs/features/access-control/acls),
[MCP di Claude Code](https://code.claude.com/docs/en/mcp),
[connettori remoti Claude](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).
