# Windows

Il percorso dipende dalla presenza di una **GPU NVIDIA**.

**Verifica GPU NVIDIA:**
```powershell
nvidia-smi   # se risponde con info sulla GPU → faster-whisper (CUDA); altrimenti → whisper.cpp (CPU)
```

---

## Windows con GPU NVIDIA → faster-whisper (veloce)

```bash
pip install faster-whisper faster-whisper-cli
pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"

faster-whisper-cli "episodio.mp3" --language it --model large-v3 --device cuda --output_format srt
```

---

## Windows senza GPU → whisper.cpp (CPU, più lento)

Senza GPU NVIDIA la trascrizione gira sulla CPU: per audio lunghi i tempi sono significativi
(indicativamente 5–20× più lento di una GPU). Conviene un modello `small`/`medium`.

1. Scarica l'archivio da `github.com/ggml-org/whisper.cpp/releases` → `whisper-bin-x64.zip`
2. Estrai in `C:\whisper.cpp\`
3. Installa ffmpeg: `winget install ffmpeg` oppure `choco install ffmpeg`
4. Scarica un modello ggml dalla stessa pagina release

```powershell
# Step 1: converti MP3 → WAV
ffmpeg -i episodio.mp3 -ar 16000 -ac 1 episodio.wav

# Step 2: trascrivi
C:\whisper.cpp\main.exe -l it -m C:\whisper.cpp\ggml-medium.bin -f episodio.wav --output-srt
```

> **Output:** genera `episodio.wav.srt` — rinomina in `episodio.srt` se necessario
> (`ren episodio.wav.srt episodio.srt`).

> **Nota:** non usare `uname` su Windows — usa sempre il comando Python dello Step 1 nel SKILL.md
> per rilevare la piattaforma. Problemi vari → vedi `troubleshooting.md`.
