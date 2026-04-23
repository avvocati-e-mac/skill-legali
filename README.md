# Skill legali per Claude

Raccolta di **skill** per Claude dedicate alla pratica legale italiana.  
Ogni skill insegna a Claude comportamenti specifici utili per gli avvocati — come generare automaticamente link alle norme, redigere atti processuali con il formato corretto, e altro ancora.

> **A chi è rivolto questo repository**  
> Queste istruzioni sono scritte per avvocati che non hanno familiarità con la programmazione. Niente paura: installare una skill richiede solo pochi clic.

---

## Skill disponibili

| Skill | Descrizione |
|-------|-------------|
| [**normattiva**](./normattiva/) | Genera link ipertestuali cliccabili verso Normattiva.it per ogni riferimento normativo italiano citato nel testo (art. X c.c., d.lgs., legge n., r.d., ecc.), usando il formato standard URN-NIR. Claude non produce mai riferimenti normativi "nudi": ogni citazione diventa automaticamente un link verificabile. |
| [**BuddaLaw per Perplexity**](./"MCP BuddaLaw per Perplexity"/) | Guida operativa per usare il connettore MCP BuddaLaw con Perplexity su quesiti legali complessi: ricerca giurisprudenziale multi-step (Cassazione, merito, TAR), ricerca normativa per dominio (civile, penale, tributario, privacy), template di contratti e atti processuali. Include schema di lavoro, esempi pratici e parametri di ricerca consigliati. |

---

## Come installare una skill

Scegli il prodotto Claude che usi:

### Claude Desktop (app per Mac e Windows)

1. Scarica il file `.skill` della skill che ti interessa (ad esempio `normattiva.skill`) cliccando su di esso in questa pagina GitHub e poi su **Download raw file**
2. Apri **Claude Desktop**
3. Vai su **Impostazioni** → **Skill** (o trascina il file `.skill` direttamente nella finestra di Claude)
4. Clicca su **Installa** quando compare la finestra di conferma
5. La skill è attiva: Claude la userà automaticamente quando pertinente

### Claude.ai / Claude for Work (Cowork)

1. Scarica il file `.skill` come descritto sopra
2. Apri [claude.ai](https://claude.ai) nel browser
3. Clicca sull'icona del tuo profilo in alto a destra → **Impostazioni** → **Skill**
4. Trascina il file `.skill` nell'area di caricamento, oppure clicca **Sfoglia** e selezionalo
5. Conferma l'installazione: la skill sarà disponibile in tutte le tue conversazioni

### Claude Code (terminale / riga di comando)

> Questa modalità è per utenti più avanzati che usano Claude Code dal terminale o dall'estensione per VS Code.

**Metodo 1 — Installa tramite file `.skill`:**
```
Apri Claude Code e scrivi:
/install normattiva.skill
```
oppure trascina il file `.skill` direttamente nella finestra di Claude Code.

**Metodo 2 — Installazione manuale della cartella:**

1. Scarica l'intera cartella della skill (ad esempio la cartella `normattiva/normattiva/`)
2. Copiala in:
   - **Mac/Linux:** `~/.claude/skills/`
   - **Windows:** `%APPDATA%\Claude\skills\`
3. Riavvia Claude Code

---

## Come aggiornare una skill

Quando viene pubblicata una nuova versione di una skill:

1. Torna su questa pagina GitHub
2. Scarica il nuovo file `.skill` (o la cartella aggiornata)
3. Installala seguendo gli stessi passi di sopra: la vecchia versione verrà sostituita automaticamente

Per ricevere notifiche sugli aggiornamenti, clicca su **Watch** → **Releases only** in alto a destra su questa pagina GitHub.

---

## Struttura del repository

Ogni skill è organizzata in una propria cartella:

```
nome-skill/
├── nome-skill/
│   ├── SKILL.md          ← istruzioni per Claude (non modificare)
│   └── references/       ← tabelle e riferimenti di supporto (se presenti)
└── nome-skill.skill      ← file preconfezionato, pronto per l'installazione
```

Il file `.skill` è quello che serve per installare la skill. La cartella interna contiene i dettagli tecnici, utili solo se vuoi capire come funziona la skill o modificarla.

---

## Suggerimenti e richieste

Hai bisogno di una skill per un'altra area del diritto?  
Apri una [Issue](../../issues) su questa pagina descrivendo cosa ti servirebbe — o scrivi direttamente a Filippo.

---

## Licenza

Rilasciato sotto licenza [MIT](LICENSE). Puoi usare, condividere e modificare liberamente queste skill, anche in ambito professionale.
