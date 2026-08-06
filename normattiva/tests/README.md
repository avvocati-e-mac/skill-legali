# Test suite – skill normattiva

Questa cartella contiene **tre** livelli di test per verificare la correttezza della skill normattiva.

---

## Struttura

```
tests/
├── cases.json              ← Dataset: 100 casi di test URN-NIR
├── test_normattiva.py      ← Livello A: test strutturali (pytest, offline)
├── test_claude_skill.py    ← Livello B: 15 test end-to-end via Claude API
├── test_api_live.py        ← Livello C: conformità contro l'API Normattiva (rete)
└── README.md
```

---

## ⚠ Perché il livello A da solo non basta

Il livello A verifica che `build_urn_link()` riproduca l'URL scritto a mano in
`cases.json`. Funzione e dataset codificano **la stessa convinzione**: è una
tautologia. Se la convinzione è sbagliata, i test restano verdi.

Il 2026-08-06 la verifica contro l'API ha trovato questi difetti in una suite
che passava al 100%:

| Difetto | Perché il livello A non poteva vederlo |
|---|---|
| **Legge fallimentare con data `1942-01-16`** (corretta: `1942-03-16`) | `regio.decreto:1942-01-16;267:1~art67` è un URN **formalmente perfetto**. Punta al nulla |
| **Cod. navigazione senza l'allegato `:1`** | Idem: forma valida, contenuto sbagliato. Senza allegato `~art1` restituisce il preambolo del R.D. — *sembra* funzionare |
| **21 casi con comma o lettera nell'URN** | Sintassi che Normattiva **ignora** (portale: pagina identica) o rifiuta (API) |
| **`c.p. art. 1-ter` e `c.c. art. 2477-bis`** | Articoli che **non esistono**: il dataset li aveva inventati |
| **5 casi con `~art1`** su decreti moderni | L'API restituisce il **preambolo**, non l'articolo 1 |

Non erano visibili nemmeno cliccando: il portale risponde con una pagina
praticamente sempre, anche per URN inventati, e risolve per **anno + numero**
ignorando tipo e giorno. **L'unico oracolo è l'API.**

---

## Livello C – Conformità contro l'API (richiede rete)

```bash
NORMATTIVA_LIVE=1 pytest test_api_live.py -v
```

Senza la variabile d'ambiente i test sono saltati: **non va nel gate**.

Cosa verifica:

1. Per ogni caso del dataset, che il **numero d'articolo restituito coincida con
   quello richiesto** — è il solo controllo che avrebbe scoperto entrambi gli
   errori della lookup.
2. Che gli URN volutamente sbagliati **falliscano** (c.c. senza `:2`, cod. nav.
   senza `:1`, l.fall. con la vecchia data, articolo inesistente, atto
   inesistente). Un controllo che non sa dire di no non è un controllo.
3. Che le sintassi che la skill non deve generare (`-com`, `-let`, `~art N-bis`,
   `~all`, `~pre`) **diano errore**. Se un giorno diventassero valide, il test
   diventa rosso: sarebbe il momento di rimetterle in `lookup-extended.md`.

Cosa **non** verifica, e perché:

| | |
|---|---|
| Lunghezza o hash del testo | Cambiano a ogni novella: l'art. 51 T.U.I.R. è passato da 23.681 a 69 caratteri quando è stato abrogato |
| Il portale | Risponde 200 a tutto |
| L'uguaglianza fra due URN | `~art9999` restituisce la stessa pagina di `~art1`: trovarli uguali non prova nulla |

Esito atteso al 2026-08-06: **94 verificati, 3 saltati** (articoli abrogati, che
restituiscono la sola formula di abrogazione), 0 fallimenti.

**Avvertenza:** l'endpoint è un servizio interno del portale, non un'API
pubblica versionata. Può cambiare senza preavviso, e un rosso qui non significa
per forza che la skill sia sbagliata. Eseguirlo a mano, o al massimo una volta a
settimana.

---

## Livello A – Test strutturali (veloce, gratuito)

Verifica che la funzione `build_urn_link()` produca URL URN-NIR corretti per tutti i 100 casi del dataset. Non richiede API key, si esegue in ~1 secondo.

**Requisiti:**
```bash
pip install pytest
```

**Esecuzione:**
```bash
cd normattiva/tests
pytest test_normattiva.py -v
```

**Output atteso:** `1403 passed`

### Categorie dei 100 casi

| Cat | N | Descrizione |
|-----|---|-------------|
| A   | 15 | Norme correnti (quick lookup) |
| B   | 10 | Codici storici con allegato `:N` |
| C   | 15 | Partizioni: bis/ter, comma, lettera |
| D   | 20 | Versioni storiche con `!vig=` |
| E   | 10 | Norme abrogate (l.fall., D.Lgs. 50/2016) |
| F   | 15 | Norme da lookup-extended |
| G   | 10 | Regression: nessun `!vig=` indesiderato |
| H   | 5  | Edge case (Cost. senza numero, ordine parametri) |

---

## Livello B – Test Claude API (spot check su 15 casi critici)

Chiama Claude via API con la skill caricata come system prompt e verifica che le risposte contengano i link attesi.

**Requisiti:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
```

**Esecuzione:**
```bash
python test_claude_skill.py                  # tutti i 15 casi
python test_claude_skill.py --verbose        # mostra la risposta completa
python test_claude_skill.py --case B03       # esegue solo il caso B03
python test_claude_skill.py --delay 2        # 2 secondi tra le chiamate
```

**Output atteso:** `15/15 passed`

### Casi del Livello B

| ID  | Scenario |
|-----|----------|
| B01 | Norma vigente base: `art. 2051 c.c.` |
| B02 | Norma abrogata generica: `art. 42 l.fall.` → deve avvertire dell'abrogazione |
| B03 | Norma abrogata + data storica: `l.fall. procedura 2018` → `!vig=2018-...` |
| B04 | Art. modificato + data fatti: `art. 18 L. 300/1970 ante Jobs Act` → `!vig=2011-...` |
| B05 | Art. modificato più volte: `D.Lgs. 81/2008 versione originaria` → `!vig=2008-...` |
| B06 | Norma abrogata + norma sostituta: `D.Lgs. 50/2016 gara 2022` |
| B07 | Art. c.c. riformato: `art. 155 c.c. ante L. 54/2006` → `!vig=200x-...` |
| B08 | Art. inserito ex novo: `art. 25-septies D.Lgs. 231/2001, infortunio 2007` → avviso |
| B09 | Art. con comma + data storica: `art. 2477 co. 3 c.c., SRL 2013` |
| B10 | Bulk link misto vigenti/storici (4 norme) |
| B11 | Codice penale: `art. 110 c.p.` → allegato `:1` |
| B12 | Costituzione: `art. 24 Cost.` → nessun numero nell'URN |
| B13 | Articolo bis: `art. 30bis c.p.c.` |
| B14 | D.P.R.: `art. 1 D.P.R. 380/2001` → tipo `decreto.del.presidente.della.repubblica` |
| B15 | Norma non in quick lookup: `art. 3 D.Lgs. 36/2023` → data `2023-03-31` |

---

## Rollback

Per tornare a una versione precedente della skill:

```bash
# Vedere la storia dei commit
git log --oneline normattiva/normattiva/SKILL.md

# Ripristinare un file a un commit specifico
git checkout <hash> -- normattiva/normattiva/SKILL.md

# Oppure annullare un commit specifico (metodo sicuro)
git revert <hash>
```
