# Layer-retrieval eval — SearXNG-skill vs Perplexity (nDCG@10 + pool TREC)

Metodo: two-layer (RAGAS/Thakur) — qui si valutano **solo le fonti**, separate dalla risposta.
Pool stile TREC (unione top-K dei due sistemi). Label rilevanza 0–3 con **regola esplicita** (non a gusto),
nDCG standard (Järvelin & Kekäläinen 2002). Script riproducibile: `compute_ndcg.py`. Data: 2026-05-30.

## Regola label (test oggettivo per ogni URL del pool, per quella query)
- **3** = fonte PRIMARIA/UFFICIALE pertinente (sito ufficiale dell'oggetto, docs ufficiali, ente regolatore, enciclopedia di riferimento).
- **2** = SECONDARIA AUTOREVOLE pertinente (testata/blog tecnico riconosciuto, sito ricette affermato, rivista giuridica).
- **1** = pertinente ma DEBOLE (forum, social, video, aggregatore, SEO-blog generico).
- **0** = non pertinente / irraggiungibile-vuoto.

## Risultati

| QID | tema | nDCG pplx | nDCG SearXNG | fonti-ufficiali@top3 pplx | …SearXNG | vincitore retrieval |
|---|---|---|---|---|---|---|
| T01 | fondazione OpenAI | 0.784 | 0.716 | 3 | 1 | pplx (lieve) |
| T03 | news OpenAI mag 2026 | 0.531 | **0.724** | 0 | 1 | **SearXNG** |
| T04 | cacio e pepe | 0.727 | **0.867** | 0 | 1 | **SearXNG** |
| T06 | TS interfaces vs types | 0.782 | 0.742 | 1 | 0 | pplx (lieve) |
| T07 | CEO Google | 0.799 | 0.765 | 2 | 2 | ~pari |
| T11 | cookie/GDPR | 0.785 | 0.736 | 2 | 1 | pplx (lieve) |
| N01 | dottrina dip. economica | 0.811 | 0.753 | 1 | 0 | pplx |
| N02 | carbonara | 0.636 | **0.754** | 0 | 1 | **SearXNG** |
| N03 | Opus vs GPT reasoning | 0.664 | 0.689 | 0 | 0 | ~pari |
| N04 | async Python 3.12 | **0.799** | 0.572 | 2 | 1 | **pplx (forte)** |
| **MEDIA** | | **0.732** | **0.732** | | | **pari** |

## Lettura dei risultati (onesta)

**Il ranking è equivalente in media (0.732 = 0.732), ma con profili opposti per dominio.**

### Dove SearXNG vince (e perché → euristica)
- **T04 cacio e pepe (+0.14), N02 carbonara (+0.12)**: il motore SearXNG mette le fonti ricette ufficiali
  (ricette.giallozafferano.it) in alto, mentre **Perplexity riempie le citazioni di YouTube/Facebook/TikTok**
  (label 1). → Per `cucina` SearXNG è già forte; nessun intervento necessario, semmai conferma `language:it`.
- **T03 news (+0.19)**: SearXNG espone openai.com/news (ufficiale) e testate IT recenti; pplx pesca blog SEO IT minori.

### Dove Perplexity vince (e perché → euristica AZIONABILE)
- **N04 async Python (−0.23, il gap più ampio a sfavore di SearXNG)**: il ranking grezzo SearXNG ha messo in #1
  un blog dev.to SEO-spam ("41% higher throughput") **sopra docs.python.org**. Perplexity privilegia i **docs
  ufficiali**. → **EURISTICA E5 (boost docs ufficiali)**: per dominio `informatica`, ri-ordinare gli URL candidati
  alla lettura promuovendo i domini ufficiali (docs.python.org, developer.mozilla.org, *.readthedocs.io, doc ufficiali
  del linguaggio/framework) PRIMA dei blog/aggregatori, indipendentemente dal relevance score grezzo.
- **N01 dottrina (−0.06), T01 (+0.07 pplx)**: pplx mette Treccani / diritto.it / openai.com ufficiale in top-3.
  → **EURISTICA E6 (re-rank per autorevolezza di dominio)**: prima di scegliere quale URL leggere, applicare un
  ordine di preferenza per tipo-fonte per dominio (vedi `references/search_strategy.md` da arricchire):
  - informatica → docs ufficiali > MDN > blog tecnici noti > SO/forum
  - legale-it/dottrina → Treccani/enciclopedie giuridiche > riviste (Altalex, Diritto.it) > PDF accademici > forum
  - cucina → siti ricette affermati > food blog > social/video
  - ai-generativa → blog/vendor ufficiali + paper > testate tech > aggregatori SEO

## Conclusione layer-retrieval
La skill SearXNG **non è inferiore** a Perplexity nel ranking (pari in media). Il suo unico tallone misurato è
quando il **ranking grezzo del motore promuove un SEO-blog sopra una fonte ufficiale** (N04). Si corregge con un
**re-rank per autorevolezza prima della lettura** (E5/E6), che è 100% internalizzabile nella skill e **non dipende
da Perplexity a runtime**. Perplexity, dal canto suo, paga su cucina per l'inclusione di social/video.
