# Troubleshooting e tempi

## Tempi indicativi per 1 ora di audio

I tempi dipendono molto dall'hardware. Regola generale: **su CPU (senza GPU NVIDIA) la trascrizione
è 5–20× più lenta** che su GPU.

| Hardware | Tool | Tempo per ~1 ora di audio |
|---|---|---|
| Mac Apple Silicon (M1/M2/M3/M4) | parakeet-mlx | molto veloce (~12–30 min, ~2–5× real-time) |
| PC/Linux con GPU NVIDIA | faster-whisper CUDA | molto veloce (fino a ~20× real-time) |
| PC/Linux senza GPU (CPU) | faster-whisper int8 / whisper.cpp | lento: ~20–40+ min con `medium`, di più con `large` |
| Mac Intel (CPU) | whisper.cpp | ~15 min (`small`) / ~45 min (`medium`) / ~90 min (`large-v3`) |

> Consiglio: su sistemi **senza GPU** usa un modello più piccolo (`small` o `medium`) per non
> aspettare troppo, accettando un calo minimo di accuratezza.

---

## Problemi frequenti

**`whisper.cpp` genera `episodio.wav.srt` invece di `episodio.srt`**
```bash
mv episodio.wav.srt episodio.srt          # macOS/Linux
ren episodio.wav.srt episodio.srt         # Windows cmd
```

**ffmpeg non trovato (Intel Mac)**
```bash
brew install ffmpeg
```

**CUDA non rilevato da faster-whisper**
```bash
nvidia-smi          # verifica che i driver siano attivi
pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
```

**Download HuggingFace lento / rate limited**
```bash
export HF_TOKEN="hf_tuotoken"   # macOS/Linux
$env:HF_TOKEN="hf_tuotoken"     # Windows PowerShell
```
Genera il token su: huggingface.co → Settings → Access Tokens

**Errore MLX all'avvio di parakeet-mlx**
→ Il Mac non è Apple Silicon. Passa al reference `intel-mac.md`.

**`parakeet-mlx` non trovato dopo l'installazione con uv**
```bash
source ~/.zshrc
# oppure usa il path completo:
~/.local/bin/parakeet-mlx "episodio.mp3" --output-dir ./
```
