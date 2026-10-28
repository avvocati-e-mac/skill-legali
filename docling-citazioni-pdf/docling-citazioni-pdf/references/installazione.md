# Controllo e installazione standard Docling MCP

Apri questa guida se serve una nuova conversione e manca un requisito.
Leggi diagnosi e installazione, poi solo la sezione del client interessato.
Per una conversione già fornita basta il riscontro sull'originale: l'assenza
del collegamento MCP non impone una reinstallazione.

La procedura segue il **README ufficiale del pacchetto Docling MCP**, verificato
il 28 ottobre 2026. Usa il server pubblicato dal progetto e le sue opzioni
ordinarie: nessun launcher, sandbox o cartella di cache personalizzati. La skill
non contiene il server né lo installa da sola caricando il file `.skill`.

## Capire cosa manca

| Riscontro | Conseguenza |
|---|---|
| Nessun tool Docling nella chat | Connessione assente; non prova assenza del programma dal computer |
| Pacchetti assenti nel Python del server identificato | Predisporre installazione standard o avvio tramite uvx |
| Pacchetti presenti, conversione non riuscita | Controllare avvio, modelli e accesso al PDF sintetico |
| Conversione riuscita, export non leggibile | Risolvere il passaggio autorizzato fra host, senza fingere di aver letto il JSON |
| Host/interprete non ispezionabile | Dichiarare requisito non verificabile da questa sessione |

Se il Python del server è identificabile, usa `scripts/check_environment.py`
con quell'interprete: `docling-slim` può fornire il motore anche quando manca
la distribuzione `docling`. Metadati e PATH non provano una conversione.
Con uvx l'ambiente è gestito da uv: non usare il Python della chat per negare
l'installazione in quell'ambiente. Quando non puoi ispezionarlo, verifica
catalogo MCP e conversione di prova. Non chiedere configurazioni intere o token.

## Avvio standard locale con uvx

Il progetto indica uvx come modalità semplice di avvio. La sua installazione
**locale** ufficiale richiede `docling-mcp[local]` e
`DOCLING_MCP_CONVERSION_MODE=local`; il pacchetto base nelle versioni correnti
può essere orientato a Docling Serve remoto. Il trasporto `stdio` collega il
processo al client, senza avviare un endpoint pubblico.

Se uvx è già disponibile, il comando server da configurare è:

```sh
DOCLING_MCP_CONVERSION_MODE=local uvx --from 'docling-mcp[local]' docling-mcp-server --transport stdio
```

È un avvio server, non un test automatico che termina da solo: normalmente
lo avvia il client MCP. Se manca uv, guida l'utente tramite la
[documentazione ufficiale di installazione uv](https://docs.astral.sh/uv/getting-started/installation/)
oppure usa l'alternativa pip sotto, con un Python compatibile già presente.
Non installare o aggiornare componenti senza l'autorizzazione necessaria.

Mantieni i gruppi di strumenti e le impostazioni predefinite del server.
Il README corrente documenta OCR attivo e descrizioni immagini disattive per
default; verifica comunque le opzioni effettive prima di promettere OCR.
Non aggiungere preset di GPU/CPU, thread, cache, download offline o restrizioni
del sistema come requisiti dell'installazione standard. Il primo uso può
scaricare modelli; modalità locale non significa assenza di rete né modello
conversazionale offline. Un uso offline preparato è un'esigenza ulteriore.

Se il client non supporta la versione del protocollo/server installata,
diagnostica l'incompatibilità. Il README del progetto distingue `docling-mcp>=3`
con SDK MCP 2 da `docling-mcp` 2.x con SDK 1; non imporre un downgrade senza
averne stabilito la necessità. Usa l'help e lo schema della versione effettiva.

## Alternativa ufficiale pip, in ambiente dedicato

Il venv isola i pacchetti Python senza cambiare il server. È un'alternativa
standard, non un prerequisito per uvx. Esempio Mac/Linux, cartella nuova scelta
dall'utente e Python compatibile già installato:

```sh
python3 -m venv '/percorso/scelto/docling-venv'
'/percorso/scelto/docling-venv/bin/python' -m pip install 'docling-mcp[local]'
```

In PowerShell Windows usa il Python compatibile presente e l'eseguibile
`Scripts` del nuovo ambiente:

```powershell
py -m venv 'C:\PercorsoScelto\docling-venv'
& 'C:\PercorsoScelto\docling-venv\Scripts\python.exe' -m pip install 'docling-mcp[local]'
```

In questo caso sostituisci il comando uvx nei client con il percorso assoluto
di `docling-mcp-server` nel venv, argomenti `--transport stdio` e la stessa
variabile `DOCLING_MCP_CONVERSION_MODE=local`. Non usare `sudo pip`, launcher
aggiuntivi o pin di versioni copiati da un'altra installazione. Non sovrascrivere
configurazioni funzionanti né convertire sul cloud per aggirare un errore.

## Codex

Conferma `codex mcp add --help`; esempio con uvx:

```sh
codex mcp add docling --env DOCLING_MCP_CONVERSION_MODE=local -- uvx --from 'docling-mcp[local]' docling-mcp-server --transport stdio
codex mcp list
```

Alternativa in `config.toml`, preservando le altre voci:

```toml
[mcp_servers.docling]
command = "uvx"
args = ["--from", "docling-mcp[local]", "docling-mcp-server", "--transport", "stdio"]

[mcp_servers.docling.env]
DOCLING_MCP_CONVERSION_MODE = "local"
```

Se l'app non risolve `uvx` dal PATH, ricava il suo percorso assoluto effettivo.
Riapri la sessione quando necessario e verifica i tool reali; `mcp list` prova
una configurazione, non una conversione. Un ambiente ospitato nel cloud non
ottiene accesso al computer copiando una configurazione locale.

## Claude Code

Conferma `claude mcp add --help`. Questo esempio usa lo scope del progetto;
uno scope personale è una scelta ulteriore:

```sh
claude mcp add --env DOCLING_MCP_CONVERSION_MODE=local --transport stdio docling -- uvx --from 'docling-mcp[local]' docling-mcp-server --transport stdio
claude mcp list
claude mcp get docling
```

Il separatore `--` precede il comando server. Usa `/mcp` se disponibile e
verifica i tool della conversazione. Se serve, usa il percorso assoluto di
uvx individuato sul computer del server.

## Claude Desktop e Cowork

In Desktop aggiungi la sola voce necessaria, preservando `mcpServers` esistenti:

```json
{
  "mcpServers": {
    "docling": {
      "command": "uvx",
      "args": ["--from", "docling-mcp[local]", "docling-mcp-server", "--transport", "stdio"],
      "env": {"DOCLING_MCP_CONVERSION_MODE": "local"}
    }
  }
}
```

Se il client grafico non risolve uvx dal PATH, usa il percorso assoluto
verificato. Non presumere che Cowork erediti la configurazione legacy Desktop:
controlla connettori della sessione, versione, policy e host. Dove supportato,
il MCP locale si collega con un plugin nei formati ufficiali
(`.claude-plugin/plugin.json` e `.mcp.json`), usando lo stesso comando standard.
Il file `.skill` non contiene quel plugin o il server.

Cowork può usare esecuzione locale o cloud; i connettori locali possono
richiedere l'app desktop aperta. Shell e server possono vedere percorsi diversi:
verifica accesso del server al PDF e recupero di JSON/Markdown. Se il client non
lo consente, spiega il limite e proponi un ambiente locale supportato; nessun
tunnel o convertitore remoto implicito.

## Prova conclusiva

Verifica catalogo e una vera conversione MCP su PDF sintetico di due pagine,
con una frase diversa per pagina e numeri stampati diversi dai fisici. Salva
MD/JSON, leggi davvero i file e genera i riferimenti. Una frase sulla seconda
pagina resta p. 2 anche se il piè di pagina dice 41. Registra host, versioni,
strumento, chiave, hash e file. Senza JSON accessibile le citazioni non sono
pronte, anche se la conversione è riuscita.

Gli helper di ispezione/confronto PDF richiedono `pypdfium2`, spesso già presente
nell'ambiente locale. Se manca, usa un lettore disponibile o predisponi quella
sola dipendenza entro il mandato; non serve un secondo Docling nel Python della
chat per leggere il JSON.

## Fonti primarie

- [Docling MCP: README del pacchetto, modalità locale, avvio e configurazione](https://github.com/docling-project/docling-mcp/blob/main/README.md)
- [Codex: MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
- [Claude Code: MCP](https://code.claude.com/docs/en/mcp)
- [Claude Desktop: MCP locali](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [Plugin Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) e [formati](https://code.claude.com/docs/en/plugins-reference)
- [Cowork: piattaforme](https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile) e [architettura](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview)
