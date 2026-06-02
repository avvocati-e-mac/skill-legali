---
name: audio-transcription
description: "Trascrivi file audio in testo in locale (SRT/VTT/TXT) su qualsiasi piattaforma, scegliendo il tool giusto in base all'hardware: Apple Silicon (parakeet-mlx), Intel Mac (whisper.cpp), Linux/Windows con GPU NVIDIA (faster-whisper), Linux/Windows senza GPU (whisper.cpp / faster-whisper CPU). MANDATORY TRIGGERS: l'utente vuole trascrivere audio o video, generare sottotitoli SRT/VTT o un testo TXT da un file audio, installare o configurare un tool di trascrizione, oppure nomina parakeet, whisper o faster-whisper."
metadata:
  version: "2.1.0"
  author: "filippostrozzi"
---

# Audio Transcription

Trascrizione audio locale su qualsiasi piattaforma. La trascrizione avviene **interamente sul
computer dell'utente**: il file audio non viene mai caricato online (solo il modello viene
scaricato una volta, al primo uso). Adatto a materiale riservato.

Questo file è l'entry point: rileva la piattaforma e poi **carica il reference della piattaforma
corrispondente** — i dettagli di installazione e i comandi sono lì, non qui (progressive disclosure).

## Compatibilità runtime

Questa skill deve funzionare sia in ambienti Claude sia in ambienti OpenAI/Codex.

- **Se stai operando in Claude Desktop, Claude for Work/Cowork o Claude Code:** esegui i comandi tramite gli strumenti shell/terminale disponibili nell'ambiente Claude; se il runtime non consente comandi locali, fornisci istruzioni passo-passo all'utente.
- **Se stai operando in Codex o in un ambiente OpenAI:** esegui i comandi tramite gli strumenti shell disponibili nel workspace; se installazioni o download richiedono rete o permessi esterni, usa il flusso di approvazione del runtime prima di procedere.
- In ogni runtime, preserva l'obiettivo principale: trascrizione locale e nessun upload dell'audio a servizi esterni, salvo richiesta esplicita dell'utente.

## Step 1 — Rileva la piattaforma

Esegui sempre questo comando per primo (funziona anche su Windows, dove `uname` non è affidabile):

```bash
python3 -c "import platform; print(platform.system(), platform.machine())"
```

## Step 2 — Vai al reference della piattaforma

Sulla base dell'output, **leggi il file `references/` indicato** e segui i suoi passi:

| Output del comando | Piattaforma | Tool | Reference da leggere |
|---|---|---|---|
| `Darwin arm64` | Apple Silicon (M1+) | parakeet-mlx | `references/apple-silicon.md` |
| `Darwin x86_64` | Intel Mac | whisper.cpp | `references/intel-mac.md` |
| `Linux …` (con o senza GPU NVIDIA) | Linux | faster-whisper | `references/linux.md` |
| `Windows AMD64` (con o senza GPU NVIDIA) | Windows | faster-whisper / whisper.cpp | `references/windows.md` |

Per la verifica GPU NVIDIA (Linux/Windows) usa `nvidia-smi`: se risponde con info sulla GPU →
percorso CUDA (veloce); altrimenti → percorso CPU (più lento). I dettagli sono nei reference.

## Note operative

- **Lingua:** per l'italiano i tool sono già impostati di default sui modelli giusti (Parakeet v3
  multilingue EU, oppure Whisper `--language it`). I comandi nei reference lo riflettono.
- **Formato di output:** SRT è il default. Per ottenere anche VTT/TXT/JSON i reference indicano i
  flag (`--output-format all` su parakeet-mlx; `--output-srt` su whisper.cpp; `--output_format` su
  faster-whisper).
- **Velocità:** su computer **senza GPU NVIDIA** (PC Windows/Linux comuni, Mac Intel) la
  trascrizione gira sulla CPU ed è sensibilmente più lenta (indicativamente 5–20× più lenta di una
  GPU). Su quei sistemi suggerisci un modello più piccolo (`small`/`medium`) per ridurre i tempi.
  Apple Silicon e GPU NVIDIA sono molto più rapidi. Tabella tempi in `references/troubleshooting.md`.
- **Problemi** (download lento, `.srt` rinominato, ffmpeg/CUDA mancanti): `references/troubleshooting.md`.

Carica un solo reference per volta: quello della piattaforma rilevata. Consulta
`references/troubleshooting.md` solo se emerge un errore.
