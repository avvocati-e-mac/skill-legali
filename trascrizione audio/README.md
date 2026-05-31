# Trascrizione audio → testo — Guida per avvocati

Questa skill dà a Claude la capacità di **trasformare un file audio in testo** (e in sottotitoli),
direttamente in **Claude Code** e **Claude Desktop**, lavorando **sul tuo computer**.

> **A chi è rivolta questa guida**
> A colleghi avvocati che non si occupano di informatica. I passaggi sono spiegati uno per uno.

---

## 1. Cosa fa

Dai a Claude un file audio (una registrazione, una nota vocale) e ottieni:

- un **testo** (`.txt`) di quello che è stato detto;
- dei **sottotitoli con i tempi** (`.srt` / `.vtt`), utili se l'audio viene da un video.

La skill sceglie **da sola** lo strumento giusto in base al tuo computer (Mac, Windows o Linux):
non devi capire quale usare.

---

## 2. Riservatezza: tutto resta sul tuo computer

> **L'audio non viene mai caricato su internet.** La trascrizione avviene **interamente sul tuo
> computer**, in locale. L'unica cosa che viene scaricata da internet è il "modello" di
> riconoscimento vocale, **una volta sola**, al primo utilizzo — e comunque non è il tuo audio.
>
> Questo rende lo strumento adatto a materiale **coperto da segreto professionale** e al rispetto
> del **GDPR**: registrazioni di clienti e atti riservati non lasciano il tuo studio.

---

## 3. A cosa serve nello studio legale

- **Udienze e verbali** — trascrivere la registrazione di un'udienza, di un interrogatorio o di
  sommarie informazioni per ricavarne un testo da rileggere o verbalizzare.
- **Colloqui con il cliente** — trasformare in testo un colloquio registrato (col consenso),
  per poterlo riassumere e archiviare.
- **Note vocali e memo** — dettare a voce un'idea, una bozza di atto o un appunto e ottenerne
  subito il testo.

In tutti questi casi puoi poi chiedere a Claude di **riassumere**, **riordinare** o **cercare** un
passaggio nel testo trascritto.

---

## 4. Installazione

### Claude Desktop / claude.ai

Scarica il file **[`audio-transcription.skill`](https://github.com/avvocati-e-mac/skill-legali/raw/main/trascrizione%20audio/audio-transcription.skill)**
e trascinalo nella finestra di Claude, poi conferma l'installazione. (I passi completi sono nel
[README generale](../README.md#come-installare-una-skill).)

### Claude Code (terminale)

Modo automatico, dalla cartella del progetto:

```bash
bash "trascrizione audio/install.sh"
```

Oppure copia la cartella a mano in `~/.claude/skills/` e riavvia Claude Code.

---

## 5. Primo utilizzo

1. Apri Claude e scrivi semplicemente, ad esempio: **«trascrivi questo file: udienza.mp3»**.
2. **Solo la prima volta**, Claude installerà lo strumento adatto al tuo computer e scaricherà il
   modello (alcune centinaia di MB): è un'attesa che avviene una volta sola.
3. Al termine trovi il file di testo (e i sottotitoli) nella stessa cartella dell'audio.

---

## 6. Quanto è veloce? (dipende dal computer)

La velocità cambia molto a seconda dell'hardware. In particolare, i **PC Windows o Linux senza una
scheda grafica NVIDIA** lavorano con la sola **CPU** e sono **molto più lenti**.

| Il tuo computer | Velocità indicativa (1 ora di audio) |
|---|---|
| **Mac con chip Apple** (M1/M2/M3/M4) | veloce — circa **12–30 minuti** |
| **PC/Linux con scheda grafica NVIDIA** | molto veloce — pochi minuti |
| **PC/Linux senza scheda NVIDIA** (solo CPU) | **lento** — circa **20–40 minuti o più** |
| **Mac Intel** (senza chip Apple) | lento — da ~15 a ~90 minuti secondo il modello |

> **Consiglio pratico:** se hai un PC **senza scheda grafica NVIDIA**, chiedi a Claude di usare un
> modello più piccolo (`small` o `medium`): la trascrizione sarà molto più rapida, con una perdita
> minima di accuratezza. Su Mac con chip Apple non serve: è già veloce.

---

## 7. Problemi frequenti

| Sintomo | Soluzione |
|---|---|
| La prima trascrizione è lentissima | è il download del modello (una volta sola) + computer senza GPU: usa un modello più piccolo |
| Esce un file `nome.wav.srt` | rinominalo in `nome.srt` (Claude può farlo per te) |
| "ffmpeg non trovato" (Mac Intel) | installa con `brew install ffmpeg` |
| La skill non compare in `/doctor` | rilancia `install.sh` o ricopia la cartella in `~/.claude/skills/` |

Per i dettagli tecnici di ogni piattaforma, la skill consulta automaticamente i file in
`audio-transcription/references/`.
