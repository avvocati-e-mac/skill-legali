# GestioLex Corpus

Questa skill aiuta Claude, Claude Code, Codex e altri assistenti compatibili a usare il server MCP **GestioLex Corpus** per ricerche legali italiane.

## A cosa serve

GestioLex Corpus serve a dare all'assistente accesso controllato a fonti giuridiche italiane tramite MCP, senza affidarsi alla memoria interna del modello.

La skill guida l'assistente nella scelta tra tre percorsi:

- lettura del testo esatto di un articolo di codice;
- ricerca della norma pertinente quando il riferimento preciso non è noto;
- ricerca di massime e orientamenti giurisprudenziali.

L'obiettivo pratico è ridurre ricerche inutili, risultati rumorosi e consumo di token, mantenendo un flusso adatto al lavoro dell'avvocato.

## Chi lo ha sviluppato

Il server MCP remoto è sviluppato e messo a disposizione da **GestioLex** tramite l'endpoint:

```text
https://corpus.gestiolex.it/mcp
```

Questo repository non contiene il server MCP: contiene solo la **skill** che spiega all'assistente come usarlo correttamente.

## Cosa installare

Per usare GestioLex Corpus servono due cose distinte:

1. la **skill** `gestiolex-corpus`, che contiene le istruzioni per l'assistente;
2. il collegamento al **server MCP GestioLex Corpus**, che espone gli strumenti di ricerca.

Se installi solo la skill ma non configuri l'MCP, l'assistente saprà quando dovrebbe usare GestioLex Corpus ma non potrà chiamare gli strumenti.

## Installare la skill

### Claude Desktop, Claude for Work/Cowork e Claude Code

Scarica e installa il file:

```text
gestiolex-corpus.skill
```

La skill è il pacchetto pronto per Claude.

### Codex e ambienti OpenAI

Usa la cartella:

```text
gestiolex-corpus/
```

La cartella contiene:

- `SKILL.md`;
- `references/query-patterns.md`;
- `agents/openai.yaml`.

## Configurare l'MCP GestioLex Corpus

### Codex

Apri il file di configurazione di Codex e aggiungi:

```toml
[mcp_servers.gestiolex_corpus]
enabled = true
url = "https://corpus.gestiolex.it/mcp"
```

Poi riavvia Codex.

### Claude Code

Se la tua versione di Claude Code supporta l'aggiunta di server MCP remoti da terminale, usa:

```bash
claude mcp add --transport http gestiolex_corpus https://corpus.gestiolex.it/mcp
```

Poi riavvia Claude Code.

Se il comando cambia nella tua versione, apri le impostazioni MCP di Claude Code e aggiungi un server remoto con questi dati:

```text
Nome: gestiolex_corpus
URL: https://corpus.gestiolex.it/mcp
Trasporto: HTTP remoto
```

### Claude Desktop

Nelle versioni di Claude Desktop che supportano server MCP remoti, aggiungi un nuovo server MCP con:

```text
Nome: gestiolex_corpus
URL: https://corpus.gestiolex.it/mcp
Trasporto: HTTP remoto
```

Poi riavvia Claude Desktop.

## Strumenti esposti dall'MCP

La skill è pensata per questi strumenti:

- `leggi_articolo`: recupera il testo esatto di un articolo di un codice italiano;
- `cerca_norma`: cerca articoli pertinenti nella normativa italiana;
- `cerca_giurisprudenza`: cerca massime e principi di diritto.

Se questi strumenti non compaiono nell'ambiente in uso, il server MCP non è configurato correttamente o non è disponibile in quella sessione.
