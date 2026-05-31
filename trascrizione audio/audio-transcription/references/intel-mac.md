# Intel Mac (Darwin x86_64)

**Tool:** `whisper.cpp` — ottimizzato per CPU, il più veloce su Mac Intel (Core ML non è
disponibile su x86). Gira su CPU: per audio lunghi i tempi sono significativi (vedi
`troubleshooting.md`).

> **Nota:** whisper.cpp accetta solo WAV 16kHz mono. Il passo ffmpeg è obbligatorio per i file MP3.

## Installazione

```bash
brew install whisper-cpp ffmpeg
```

Scarica il modello (prima volta):
```bash
# Modello medium — miglior bilanciamento qualità/velocità su CPU Intel
curl -L -o ~/Downloads/ggml-medium.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
```

## Trascrizione

```bash
# Step 1: converti MP3 → WAV (obbligatorio)
ffmpeg -i "episodio.mp3" -ar 16000 -ac 1 episodio.wav

# Step 2: trascrivi in SRT (italiano)
whisper-cpp --language it \
  --model ~/Downloads/ggml-medium.bin \
  --output-srt \
  episodio.wav
```

> **Output:** whisper.cpp genera `episodio.wav.srt` — rinomina se necessario:
> ```bash
> mv episodio.wav.srt episodio.srt
> ```

## Modelli disponibili

| Modello | Accuratezza IT | Dimensione | Tempo (CPU Intel) |
|---|---|---|---|
| `ggml-small.bin` | buona | 244 MB | ~15 min/ora audio |
| `ggml-medium.bin` | ottima | 769 MB | ~45 min/ora audio |
| `ggml-large-v3.bin` | eccellente | 1.5 GB | ~90 min/ora audio |

> Su Mac Intel senza GPU dedicata, per audio lunghi conviene `small` o `medium`. Errori ffmpeg →
> vedi `troubleshooting.md`.
