# Linux

Su Linux il tool consigliato è `faster-whisper` (CTranslate2). Il percorso dipende dalla presenza
di una **GPU NVIDIA**.

**Verifica GPU:**
```bash
nvidia-smi   # se risponde con info sulla GPU → percorso CUDA; altrimenti → percorso CPU
```

---

## Linux con GPU NVIDIA (veloce)

**Requisiti:** CUDA 12 + cuDNN 9, driver NVIDIA aggiornati. Con CUDA `faster-whisper` è fino a ~4×
più veloce di Whisper originale (fino a ~20× real-time).

### Installazione

```bash
pip install faster-whisper faster-whisper-cli
pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
```

### Trascrizione

```bash
# Italiano, SRT, GPU
faster-whisper-cli "episodio.mp3" \
  --language it \
  --model large-v3 \
  --device cuda \
  --output_format srt
```

### Alternativa: Parakeet via onnx-asr

Se vuoi usare Parakeet v3 (lo stesso modello di Apple Silicon) invece di Whisper:

```bash
pip install onnx-asr

# Trascrizione (output testo, non SRT nativo)
onnx-asr transcribe --model nemo-parakeet-tdt-0.6b-v3 episodio.wav
```

> **Limitazione:** `onnx-asr` non genera SRT — restituisce solo testo grezzo. Per l'SRT usa
> `faster-whisper-cli`.

---

## Linux CPU / Linux ARM (più lento)

Senza GPU NVIDIA si usa `faster-whisper` in modalità CPU con quantizzazione int8.

### Installazione

```bash
pip install faster-whisper faster-whisper-cli
```

### Trascrizione

```bash
# CPU con int8 (più veloce su CPU)
faster-whisper-cli "episodio.mp3" \
  --language it \
  --model medium \
  --device cpu \
  --compute_type int8 \
  --output_format srt
```

> Su CPU un'ora di audio con modello `medium` richiede circa 20–40 minuti. Usa `small` per ridurre
> i tempi. Problemi CUDA/download → vedi `troubleshooting.md`.
