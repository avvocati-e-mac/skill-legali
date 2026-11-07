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

## Come si usa

Basta chiedere, per esempio: *"Cerca su ilcaso.it le sentenze degli ultimi due anni sull'uso dell'IA negli atti e sulla condanna ex art. 96 c.p.c."*. L'assistente ti fa una sola domanda con i dati mancanti (periodo, uffici, quante pronunce leggere, se scaricarle) e poi procede. Alla fine trovi `report.md` e la cartella `pdf/` in `Documenti/Ricerche/<tema>`.

## Limiti

- È una ricerca su un **campione**: il report dice "non risultano nella ricerca", mai "non esistono".
- Rispetta il file `robots.txt` dei siti, non digita credenziali e non aggira login, captcha o SPID.
- Per lo scaricamento automatico gli script si presentano al sito come un normale browser Chrome, con una pausa di 2 secondi tra un file e l'altro.
- Il metodo di lettura dei PDF con Claude in Chrome non è ancora stato provato su ogni sito: al primo uso l'assistente lo verifica e lo annota.
- Non sostituisce la lettura dei provvedimenti da parte dell'avvocato.
