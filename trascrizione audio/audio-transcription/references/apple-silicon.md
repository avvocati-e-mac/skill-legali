# Apple Silicon (Darwin arm64)

**Tool:** `parakeet-mlx` — Parakeet TDT v3, 25 lingue EU, ~4.3% WER sull'italiano. È l'opzione più
veloce ed efficiente per Mac con chip M1/M2/M3/M4.

## Installazione

```bash
# Verifica se già installato
which parakeet-mlx

# Installa (prima esecuzione scarica il modello, ~1.2 GB)
uv tool install parakeet-mlx
```

## Trascrizione

```bash
# SRT (formato default — nessun flag necessario)
parakeet-mlx "episodio.mp3" \
  --model mlx-community/parakeet-tdt-0.6b-v3 \
  --output-dir ./

# Tutti i formati insieme (SRT + VTT + TXT + JSON)
parakeet-mlx "episodio.mp3" --output-format all --output-dir ./
```

## Modelli disponibili

| Modello | Lingue | RAM | Quando usarlo |
|---|---|---|---|
| `mlx-community/parakeet-tdt-0.6b-v3` | 25 EU | ~2 GB | **Default — italiano e lingue EU** |
| `animaslabs/parakeet-tdt-0.6b-v3-mlx-8bit` | 25 EU | ~1 GB | RAM limitata |
| `animaslabs/parakeet-tdt-0.6b-v3-mlx-4bit` | 25 EU | ~0.5 GB | Mac con poca RAM |
| `mlx-community/parakeet-tdt-0.6b-v2` | Solo EN | ~1.2 GB | Audio in inglese puro |

## Opzioni avanzate

```bash
# Qualità migliore, più lento
parakeet-mlx "episodio.mp3" --decoding beam --output-dir ./

# Riduce uso memoria per audio molto lunghi (>30 min)
parakeet-mlx "episodio.mp3" --local-attention --output-dir ./

# Controlla segmentazione SRT (righe troppo lunghe o tagli errati)
parakeet-mlx "episodio.mp3" --silence-gap 1.0 --max-words 12 --output-dir ./

# Debug con confidence score
parakeet-mlx "episodio.mp3" --verbose --output-dir ./
```

> Errori comuni (es. `parakeet-mlx` non trovato dopo l'installazione, errore MLX) →
> vedi `troubleshooting.md`.
