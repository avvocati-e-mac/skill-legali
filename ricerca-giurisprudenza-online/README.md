# Ricerca giurisprudenza online

Skill per assistenti AI che **cerca le pronunce su un tema in un sito pubblico** (ad esempio ilcaso.it o giustizia-amministrativa.it), ne compila una scheda per ciascuna, controlla che le frasi citate compaiano davvero nel testo, scarica i provvedimenti sul tuo computer e scrive un report con le linee di tendenza. Prima del report un revisore indipendente (red team) cerca le generalizzazioni non giustificate.

Presentata al convegno di Ravenna (9 ottobre 2026).

## Che cosa serve

- **Python 3** sul Mac (se manca, la skill te lo dice: si installa con `xcode-select --install`).
- **Un browser utilizzabile dall'assistente**, per i siti che non si lasciano leggere direttamente. La skill guarda da sola in quale ambiente sta lavorando e sceglie:

| Dove usi la skill | Browser |
|---|---|
| App desktop di Claude (Cowork, Claude Code nell'app) | il **browser integrato** dell'app: non serve altro |
| Claude Code dal Terminale o da un editor | l'estensione **Claude in Chrome**, installata e collegata. L'assistente lavora in una scheda nuova, legge solo pagine pubbliche e si ferma se vede contenuti in abbonamento visibili perché sei già collegato |
| Codex | il browser configurato in Codex, se c'è; altrimenti solo le pagine leggibili senza browser |

Se nessun browser è disponibile e il sito ne ha bisogno, l'assistente si ferma e ti dice che cosa attivare.

## Come si installa

- **Claude (Desktop, Cowork, Claude Code):** scarica [`ricerca-giurisprudenza-online.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/ricerca-giurisprudenza-online/ricerca-giurisprudenza-online.skill) e installalo dalle impostazioni delle skill. Se avevi già la versione del convegno, **reinstallala**: quella vecchia non conosce Claude in Chrome.
- **Codex:** copia la cartella interna `ricerca-giurisprudenza-online/` nella cartella delle skill di Codex.

## Su quali siti funziona

| Sito | Tipo | Come lavora |
|---|---|---|
| giustizia-amministrativa.it (TAR, Consiglio di Stato) | pubblico | legge da sola, senza browser |
| Garante privacy, ANAC, AGCM | pubblici | legge da sola, senza browser |
| Banca dati della giustizia tributaria | pubblico | cerca nel browser; per leggere scarica le sentenze scelte, dopo il tuo sì |
| ilcaso.it | privato | browser per i PDF |
| Corte di giustizia UE | pubblico | serve il browser |
| Corte costituzionale, EUR-Lex | pubblici | hanno captcha o blocchi anti-robot: la skill si ferma (un captcha puoi risolverlo tu) |

Sui siti **pubblici** la skill legge i singoli provvedimenti della ricerca anche dove il file robots.txt lo sconsiglia, perché sono atti pubblici e la ricerca è mirata; sui siti **privati** controlla prima i termini d'uso. Non aggira mai captcha o blocchi.

## Quanto costa

Ogni compito è affidato al modello più economico capace di svolgerlo bene: i modelli piccoli leggono e schedano, quelli intermedi scrivono la bozza e la rivedono criticamente; i controlli delle citazioni e i conteggi li fanno programmi, senza consumare l'IA.

## Come si usa

Basta chiedere, per esempio: *"Cerca su ilcaso.it le sentenze degli ultimi due anni sull'uso dell'IA negli atti e sulla condanna ex art. 96 c.p.c."*. L'assistente ti fa una sola domanda con i dati mancanti (periodo, uffici, quante pronunce leggere, se scaricarle) e poi procede. Alla fine trovi `report.md` e la cartella `pdf/` in `Documenti/Ricerche/<tema>`.

## Limiti

- È una ricerca su un **campione**: il report dice "non risultano nella ricerca", mai "non esistono".
- Rispetta il file `robots.txt` dei siti, non digita credenziali e non aggira login, captcha o SPID.
- **Nota sullo scaricamento automatico.** Gli script di download si presentano al sito con il proprio nome (`ricerca-giurisprudenza-online/1.0`) e l'indirizzo di questo progetto, non travestiti da browser: il sito sa chi sta scaricando e può decidere. Fanno una pausa di 2 secondi tra un file e l'altro e rispettano il file robots.txt. Qualche sito potrebbe rifiutare uno scaricamento non fatto da un browser: in quel caso la skill non insiste e non si camuffa, ma elenca nel report i link da aprire a mano.
- Il metodo di lettura dei PDF con Claude in Chrome non è ancora stato provato su ogni sito: al primo uso l'assistente lo verifica e lo annota.
- Non sostituisce la lettura dei provvedimenti da parte dell'avvocato.
