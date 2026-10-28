# Controllo e installazione guidata

Procedura controllata il 28 ottobre 2026 sulle fonti ufficiali elencate in fondo.
Verifica la documentazione e l'help installato prima di adattarla a versioni
diverse. La skill è un insieme di istruzioni: non include Docling, modelli o
server, e non li installa semplicemente caricando il file `.skill`.

## Capire cosa manca

| Riscontro | Cosa dire/fare |
|---|---|
| Nessun tool Docling nella chat | Connessione non disponibile; non basta per concludere che il programma manchi dal computer |
| Pacchetti assenti nel Python del server identificato | Preparare l'installazione in un ambiente dedicato |
| Pacchetti presenti ma nessuna conversione riuscita | Controllare avvio, modelli e accesso al PDF sintetico |
| Conversione riuscita, export non leggibile dalla shell | Risolvere il passaggio autorizzato fra host; non fingere di aver letto il JSON |
| Motore su un altro host non ispezionabile | Requisito non verificabile; chiedere l'esito della diagnostica su quell'host |

Esegui `scripts/check_environment.py` con il Python usato dal server, non
necessariamente quello chiamato `python3` nella chat. Legge solo metadati dei
pacchetti e disponibilità dei comandi. `docling-slim` può fornire il motore anche
se la distribuzione `docling` manca. La presenza dei metadati non prova import,
modelli o conversione; il comando server può esistere nel venv anche se non è
nel `PATH`. Il JSON diagnostico non legge token o configurazioni MCP complete.

Se non c'è shell, guida l'utente con un passaggio alla volta e chiedi solo
l'errore pertinente, senza fargli incollare configurazioni contenenti segreti.

## Installare il motore locale e il server

Prima identifica sistema operativo, Python compatibile e cartella scelta per
l'ambiente. Python 3.12 è quello collaudato in questa release; non installarlo
o aggiornare un ambiente esistente alla cieca. Non usare `sudo pip`.

Esempio Mac/Linux, da adattare a una **nuova** cartella autorizzata:

```sh
python3 -m venv '/percorso/scelto/docling-venv'
'/percorso/scelto/docling-venv/bin/python' -m pip install 'docling-mcp[local]'
'/percorso/scelto/docling-venv/bin/python' '/percorso/SKILL/scripts/check_environment.py'
```

Esempio PowerShell Windows, con un Python compatibile già installato:

```powershell
py -3.12 -m venv 'C:\PercorsoScelto\docling-venv'
& 'C:\PercorsoScelto\docling-venv\Scripts\python.exe' -m pip install 'docling-mcp[local]'
& 'C:\PercorsoScelto\docling-venv\Scripts\python.exe' 'C:\PercorsoSkill\scripts\check_environment.py'
```

L'extra `[local]` è necessario nelle versioni attuali per la conversione locale;
il pacchetto base del server può usare un servizio remoto. Se fallisce, conserva
l'errore e verifica requisiti/versione senza ripetere installazioni identiche o
passare al cloud. `docling-mcp>=3` richiede compatibilità del client con il suo
SDK MCP: una connessione fallita va diagnosticata, non risolta promettendo che
qualsiasi client sia compatibile.

Imposta esplicitamente `DOCLING_MCP_CONVERSION_MODE=local` e trasporto `stdio`.
Esegui `docling-mcp-server --help` nel venv per confermare opzioni e gruppi di
tool. Per il server 3.4.0 i gruppi necessari sono `conversion generation
manipulation`; questi espongono conversione, salvataggio e ricerca, senza
attivare strumenti di generazione esterna. Non sostituire un launcher locale
già protetto e funzionante (per esempio quello Hermes) con un avvio più ampio.

Il primo uso può scaricare modelli: spiega dimensioni/rete rilevanti senza
confonderlo con l'invio del fascicolo. Docling documenta il pre-caricamento con
`docling-tools models download` e l'uso di `DOCLING_ARTIFACTS_PATH`. Dopo aver
scaricato e provato i modelli si può configurare un ambiente offline secondo
la piattaforma; non dichiarare assenza di rete dal solo flag `local`.
Disabilita descrizioni immagini remote nella configurazione proposta con
`DOCLING_MCP_DO_PICTURE_DESCRIPTION=false`. Chat e modello possono comunque
ricevere il testo estratto: verifica la politica della pratica prima dei file reali.

## Collegare Codex

Per un Codex locale con CLI, conferma `codex mcp add --help` e usa il percorso
assoluto dell'eseguibile del venv. Esempio documentato adattato a Docling:

```sh
codex mcp add docling --env DOCLING_MCP_CONVERSION_MODE=local --env DOCLING_MCP_DO_PICTURE_DESCRIPTION=false -- '/percorso/scelto/docling-venv/bin/docling-mcp-server' --transport stdio conversion generation manipulation
codex mcp list
```

In alternativa prepara una sezione in `config.toml`, preservando le altre
configurazioni e controllando se `docling` esista già:

```toml
[mcp_servers.docling]
command = "/percorso/scelto/docling-venv/bin/docling-mcp-server"
args = ["--transport", "stdio", "conversion", "generation", "manipulation"]

[mcp_servers.docling.env]
DOCLING_MCP_CONVERSION_MODE = "local"
DOCLING_MCP_DO_PICTURE_DESCRIPTION = "false"
```

Le opzioni dell'app possono differire dalla CLI. Riapri la sessione quando
necessario e verifica i tool effettivi; `mcp list` prova una configurazione,
non l'avvenuta conversione. Un ambiente OpenAI ospitato nel cloud non ottiene
accesso al computer solo copiando questa configurazione locale.

## Collegare Claude Code

Controlla `claude mcp add --help`; il comando seguente usa lo scope locale
predefinito del progetto. Per uno scope personale serve una scelta coerente con
la richiesta, senza modificare implicitamente tutti i progetti.

```sh
claude mcp add --env DOCLING_MCP_CONVERSION_MODE=local --env DOCLING_MCP_DO_PICTURE_DESCRIPTION=false --transport stdio docling -- '/percorso/scelto/docling-venv/bin/docling-mcp-server' --transport stdio conversion generation manipulation
claude mcp list
claude mcp get docling
```

Il separatore `--` precede il comando server. Usa `/mcp` quando disponibile,
poi il catalogo strumenti della nuova conversazione. Su Windows sostituisci
l'eseguibile con il percorso `Scripts\docling-mcp-server.exe` verificato.

## Collegare Claude Desktop e Cowork

In **Claude Desktop**, dove supportato, aggiungi alla configurazione MCP locale
la sola voce necessaria, senza rimpiazzare `mcpServers` esistenti:

```json
{
  "mcpServers": {
    "docling": {
      "command": "/percorso/scelto/docling-venv/bin/docling-mcp-server",
      "args": ["--transport", "stdio", "conversion", "generation", "manipulation"],
      "env": {
        "DOCLING_MCP_CONVERSION_MODE": "local",
        "DOCLING_MCP_DO_PICTURE_DESCRIPTION": "false"
      }
    }
  }
}
```

In **Cowork** non presumere che la configurazione legacy Desktop venga ereditata.
Controlla connettori della sessione, versione, policy dell'organizzazione e
posizione di esecuzione. La documentazione corrente consente MCP locali tramite
plugin; se occorre prepara un plugin seguendo i formati ufficiali (manifest in
`.claude-plugin/plugin.json`, configurazione `.mcp.json` con `mcpServers` come
sopra), usando il comando assoluto sul computer dell'utente. Spiega e verifica
il risultato prima di considerarlo collegato: il file `.skill` di questa
release non è un plugin MCPB e non include quel server.

I task Cowork possono avere esecuzione cloud o locale secondo piano/versione.
Per i connettori locali può servire l'app desktop aperta; nei task locali la
shell può essere in una VM mentre il server gira sull'host. Identifica il
percorso letto dal server e il canale autorizzato per recuperare JSON/Markdown.
Se il client non espone MCP locale o non concede accesso ai file, spiega il
blocco e proponi l'uso locale in Claude Code/Codex oppure un collegamento
supportato dalla versione in uso. Non esporre automaticamente il server con
un tunnel e non sostituirlo con un convertitore remoto.

## Prova conclusiva

Crea un PDF sintetico di due pagine nella cartella autorizzata: una frase
distinta per pagina, con numeri stampati diversi da quelli fisici. Converti
tramite MCP, salva MD/JSON, leggi davvero entrambi i file e genera i riferimenti
con lo script. Controlla nell'originale una frase della seconda pagina: deve
restare p. PDF 2 anche se il piè di pagina dice 41. Registra host, interprete,
versioni, nome tool, chiave, hash, pagine, esito e file prodotti. Se la conversione
funziona ma il JSON resta inaccessibile, le citazioni non sono pronte.

Per il helper di confronto testuale, `pypdfium2` è spesso già nel venv locale;
se manca, predisponi l'installazione in quell'ambiente oppure usa un lettore
già disponibile. Non installare un secondo Docling nel Python isolato della
chat solo per leggere JSON o controllare il livello testo.

## Fonti ufficiali

- [Docling MCP: installazione, modalità e avvio](https://github.com/docling-project/docling-mcp/blob/main/README.md)
- [Docling: modelli offline e servizi remoti](https://docling-project.github.io/docling/usage/advanced_options/)
- [Codex: configurazione MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Claude Code: MCP](https://code.claude.com/docs/en/mcp)
- [Claude Desktop: server MCP locali](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Plugin Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) e [formati del plugin](https://code.claude.com/docs/en/plugins-reference)
- [Cowork: piattaforme e accesso locale](https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile) e [architettura](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)
