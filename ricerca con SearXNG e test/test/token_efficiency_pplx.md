# Efficienza token — classifica separata (NON entra nei punteggi qualità)

Esclusa dai criteri di qualità per evitare **verbosity bias** (Dubois 2024): un giudice LLM sovra-premia
le risposte lunghe. Qui misurata oggettivamente e riportata a parte.

## Due metriche NON direttamente confrontabili (design diversi)

| | SearXNG-skill | Perplexity (pwm) |
|---|---|---|
| **Cosa entra nel contesto Claude** | search output (~3.000) + letture mirate (~900–1.800) | solo la risposta finale via CLI |
| **Chars contesto ingeriti (media)** | ~3.200 (fact) / ~4.200 (deep/recipe/comparison) | risposta = ~4.100 (media), 173–8.950 |
| **Risposta prodotta** | concisa (sintesi mirata) | verbosa (report strutturato lungo) |
| **Controllo token** | esplicito (`maxLength`, `paragraphRange`, skip lettura su fact) | nessun controllo lato utente |

## Lunghezza risposta Perplexity (chars)
T01 204 · T07 173 (fact: brevi) · T03 2.256 · N02 2.348 · T04 3.060 · T06 5.481 · N01 5.954 · N04 6.193 · T11 6.265 · N03 8.950.
Media ≈ 4.100. Su deep/comparison Perplexity produce 6.000–9.000 chars.

## Lettura
- Sui **fact** (T01, T07) Perplexity è efficientissimo (≈180 chars) e la skill pareggia (0 letture URL, risponde da snippet).
- Sui **deep/comparison** la skill mantiene il contesto ingerito sotto ~4.900 chars con letture mirate
  (`section`/`paragraphRange`), mentre Perplexity restituisce risposte 6–9k chars. Per un agente che deve
  **conservare budget di contesto** su task multi-step, la skill ha un vantaggio strutturale (output controllabile).
- Questo è il punto di forza progettuale della skill (token-efficiency), indipendente dalla qualità del contenuto.

## Implicazione
Nessun cambiamento di rubrica: la qualità resta giudicata sui booleani. L'efficienza è un asse a sé in cui
SearXNG-skill è competitiva/superiore per uso agentico. Da NON confondere con qualità.
