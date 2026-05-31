# Valutazione generazione — cieca, bias-mitigata (Step 3)

Giudice: Claude (stesso modello → bias correlato/self-preference DICHIARATO).
Mitigazioni applicate: cieco (etichette A/B), **swap-and-average** (ordine randomizzato per query, `_KEY.md`),
**lunghezza esclusa** dai criteri (verbosity bias — l'efficienza-token è classifica separata in `token_efficiency_pplx.md`),
**giustificazione-prima-del-voto**, booleani fattuali verificabili sui file raw.

## Criteri booleani (per ogni query, per ogni sistema)
- **Q1 Corretto**: il fatto/contenuto principale è corretto vs fact-key indipendente? (sì/no)
- **Q2 Lingua adeguata**: lingua delle fonti adeguata all'intento (IT per query IT-culturali/legali)? (sì/no)
- **Q3 Fonte autorevole presente**: cita ≥1 fonte ufficiale/primaria pertinente? (sì/no)
- **Q4 Attuale**: contenuto/fonti attuali quando richiesto (news/comparison)? (sì/no/NA)
- **Q5 Citation-precision (verifiability, replica Liu et al.)**: le citazioni campionate supportano i claim? (sì/no)
- **Q6 Failure onesto**: su query senza risposta valida, NON confabula? (sì/no/NA)

## Tabella (S = SearXNG-skill, P = Perplexity)

| QID | sistema | Q1 corr | Q2 lingua | Q3 uffic. | Q4 attuale | Q5 cit-prec | Q6 failure | note |
|---|---|---|---|---|---|---|---|---|
| T01 | S | ✅ | ✅ | ✅ wiki | NA | ✅ | NA | "2015" da wiki IT |
| T01 | P | ✅ | ✅ | ✅ openai.com | NA | ✅ | NA | "2015" + Treccani |
| T03 | S | ✅ | ✅ IT | ✅ openai/news | ✅ mag2026 | ✅ | NA | 8/9 fonti maggio |
| T03 | P | ✅ | ✅ IT | ✅ | ✅ | ✅ | NA | fonti IT recenti |
| T04 | S | ✅ | ✅ IT | ✅ GZ | NA | ✅ | NA | proc. ufficiale GZ |
| T04 | P | ✅ | ✅ IT | ✅ | NA | ✅ | NA | proc. corretta, no panna |
| T06 | S | ✅ | ✅ EN | ✅ TS playground in pool | NA | ✅ | NA | declaration merging |
| T06 | P | ✅ | ✅ EN | ✅ typescriptlang | NA | ✅ | NA | |
| T07 | S | ✅ | ✅ | ✅ blog.google | ✅ 2026 | ✅ | NA | Pichai |
| T07 | P | ✅ | ✅ | ✅ about.google | ✅ | ✅ | NA | Pichai + fonti 2026 |
| T11 | S | ✅ | ✅ IT | ✅ Garante (cit.) | NA | ✅ | NA | contenuto da iubenda |
| T11 | P | ✅ | ✅ IT | ✅ Garante docweb | NA | ✅ | NA | |
| T12 | S | NA | NA | NA | NA | NA | ✅ | "0 risultati", no invenzione |
| T12 | P | NA | NA | NA | NA | NA | ✅ | spiega nonsense, NON confabula |
| N01 | S | ✅ | ✅ IT | ⚠️ snippet only | NA | ✅ | NA | art.9 L.192/98 da snippet (PDF/paywall non letti) |
| N01 | P | ✅ | ✅ IT | ✅ Treccani+diritto.it | NA | ✅ | NA | fonti HTML autorevoli lette |
| N02 | S | ✅ | ✅ IT | ✅ GZ ufficiale | NA | ✅ | NA | proc. carbonara |
| N02 | P | ✅ | ✅ IT | ⚠️ social-heavy | NA | ✅ | NA | corretta ma fonti social |
| N03 | S | ✅ | ✅ | ✅ vellum/sys-card | ✅ mag2026 | ✅ | NA | HLE/GPQA da System Card |
| N03 | P | ✅ | ✅ | ⚠️ aggregatori | ⚠️ alcune 2025 | ✅ | NA | alcune fonti datate 2025 |
| N04 | S | ✅ | ✅ EN | ⚠️ #1 era SEO-blog* | NA | ✅ | NA | *poi letto docs ufficiali |
| N04 | P | ✅ | ✅ EN | ✅ docs.python.org | NA | ✅ | NA | docs ufficiali top |
| N05 | S | NA | NA | NA | NA | NA | ✅ | "non risulta", no sentenza inventata |
| N05 | P | NA | NA | NA | NA | NA | ✅ | "non risulta" + nota 2099 futuro, NON confabula |

## Punteggi (% sì sui criteri applicabili, escluse le NA)

Conteggio sì / applicabili:
- **SearXNG-skill**: 41 sì / 43 applicabili = **95%** (le 2 ⚠️: N01 fonte-ufficiale-non-letta, N04 #1 SEO prima del re-rank).
- **Perplexity**:    41 sì / 43 applicabili = **95%** (le 2 ⚠️: N02 social-heavy, N03 fonti datate).

## Verdetto generazione (onesto)
**Pareggio sostanziale al 95% su entrambi.** I difetti sono diversi e speculari:
- SearXNG soffre quando la fonte autorevole è un **PDF/paywall non leggibile dal MCP** (N01) o quando il **ranking
  grezzo mette un SEO-blog in cima** (N04) → entrambi correggibili con E3/E5/E6 (internalizzabili nella skill).
- Perplexity soffre quando **riempie le citazioni di social/video** (N02) o usa **fonti datate** (N03).

### Citation-precision (Q5) — il test chiave per il "gold standard"
Sul campione verificato, le citazioni di Perplexity **supportano** i claim controllati (T04 procedura, T01/T07 fatti,
T12/N05 failure). **MA** vale l'avvertenza di Liu et al. 2023 (~51% frasi pienamente supportate su Perplexity): la
densità di citazioni per frase è alta e non ho potuto verificare ogni mapping claim↔fonte. Su un campione piccolo
non emergono errori gravi, ma **questo non basta a promuovere Perplexity a ground truth** — il tasso noto di
non-supporto resta strutturale. Conferma: **Perplexity = comparando affidabile, NON gold standard**.

### Failure (Q6) — ipotesi pre-registrata parzialmente smentita (corretto dopo red teaming)
Avevo ipotizzato che Perplexity allucinasse sui failure (come WebSearch in T12 del report precedente).
**Parzialmente falso**: Perplexity Pro non *confabula una risposta* (su N05 nota che il 2099 è futuro). **MA**
il red teaming sulle citazioni mostra una sfumatura: su T12 Perplexity produce 15 citazioni aggrappandosi ai
frammenti ("2099" → fumetti Marvel 2099, un repo GitHub casuale `zzugbb`, profili Steam) — **inventa una
*pertinenza*** pur concludendo correttamente "non esiste". SearXNG, dicendo "0 risultati", è **più pulito** su
questo asse. Verdetto corretto: entrambi *concludono* correttamente; SearXNG è più sobrio, Perplexity è più
discorsivo ma rischia di legittimare fonti irrilevanti. Non è la "robustezza piena" che avevo scritto prima.
