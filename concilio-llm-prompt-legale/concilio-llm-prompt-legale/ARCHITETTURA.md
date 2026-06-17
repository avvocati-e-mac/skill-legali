# Concilio di LLM per valutazione risposta legale - Architettura

Questo documento descrive l'architettura della skill `concilio-llm-prompt-legale`, il suo modello di scoring, i presidi contro bias e drift, e i riferimenti scientifici usati per motivare le scelte metodologiche.

La skill e' uno strumento di screening, ranking e quality control di risposte legali generate da AI, sui quattro rami del diritto italiano (civile, penale, tributario, amministrativo). Il caso d'uso primario e' confrontare la risposta base di un LLM con la versione ottenuta tramite un miglioratore di prompt, sullo stesso quesito; la skill supporta comunque confronto A/B/C e valutazione singola. Non produce consulenza legale, non sostituisce l'avvocato italiano e non certifica la verita' delle citazioni. Ogni fonte usata in un fascicolo, in una comunicazione al cliente o in un atto deve essere verificata dal professionista su fonte ufficiale o banca dati autorizzata.

## Panoramica operativa

La skill valuta una o piu' risposte candidate rispetto a un quesito, una ground truth o checklist, e una rubric pesata. Nel confronto base-vs-prompt-migliorato i due testi sono trattati come candidati anonimi (ID neutri A/B) per evitare che il giudice premi la versione etichettata come "migliorata". La CLI `scripts/legal_panel.py` offre workflow locali/offline per estrazione, mock scoring, confronto, preparazione di prompt live, normalizzazione di output live, verifica fonti e report.

Principi:

- la route locale/offline oppure online/live va chiesta all'utente se non e' gia' esplicita;
- cloud e live model solo dopo scelta esplicita della route e disclosure dei provider/tool;
- giudici indipendenti, prompt separati e raw output separati;
- giudizio LLM separato dalla verifica fonti;
- output JSON strutturato e kappa-ready;
- ranking utile per triage, non per affidamento legale automatico.

## File principali

| Percorso | Ruolo |
| --- | --- |
| `SKILL.md` | Istruzioni rapide e canone operativo per l'agente. |
| `ARCHITETTURA.md` | Architettura, scoring, bias controls e bibliografia scientifica. |
| `references/rubric.md` | Rubric a sei criteri, pesi e soglie operative. |
| `references/model-routing.md` | Regole di scelta tra giudici live e fallback. |
| `references/live-judging.md` | Preparazione prompt live, raw output e normalizzazione. |
| `references/source-workflow.md` | Verifica fonti separata dal giudizio LLM. |
| `references/case-schema.md` | Schema JSON per casi, verdetti, aggregati e verifiche fonti. |
| `references/reporting.md` | Struttura dei report per lettori non specialisti. |
| `scripts/legal_panel.py` | CLI operativa offline/live/source verification/report. |
| `scripts/normattiva_fetch.py` | Scarico ufficiale Normattiva per norme italiane dopo autorizzazione della route fonti. |
| `scripts/quick_validate.py` | Validatore documentale e anti-drift. |
| `CLAUDE.md`, `AGENTS.md` | Promemoria identici per runtime agentici diversi. |

## Architettura dati

### Evaluation Case

Un caso normalizzato contiene:

- `candidate_id`: identificativo anonimo o stabile del candidato;
- `source_file`: file sorgente;
- `quesito`: domanda da valutare;
- `risposta`: risposta candidata estratta e pulita;
- `ground_truth`: risposta di riferimento o checklist strutturata;
- `data_riferimento`: data di aggiornamento normativo richiesta;
- `fonti`: citazioni rilevate o fonti attese;
- `confidential`: si basa su segnali FORTI di dato personale reale (email non placeholder, codice fiscale), non sulle sole parole-tema; un parere anonimizzato con sole email-esempio (es. `nome.cognome@azienda.it`) resta `false`. Accompagnato da `confidential_reason` che spiega perché il flag è (o non è) scattato;
- `extraction`: formato, timestamp e note di estrazione.

### Judge Verdict

Ogni giudice produce un verdetto JSON per singolo candidato. Campi principali:

- `judge_id`, `model_route`, `mode`;
- `criteria` con score 0-3, peso, weighted score e motivazione per criterio;
- `score_ponderato`, `score_massimo: 39`, `percentuale`;
- `kappa_discrete_score`;
- `source_verification`;
- `flag_revisione_umana`;
- `punti_critici_per_avvocato`;
- `raw_file` quando il verdetto deriva da live output.

### Aggregated Result

L'aggregato ordina i candidati per `score_medio`, calcola `divergenza_max`, propaga flag di revisione umana e mantiene `kappa_ready` per calibrazione futura. I campi di interpretazione restano separati:

- `panel_ranking`: classifica tecnica del panel LLM;
- `source_gate`: gate fonti calcolato dai registri Normattiva/BuddaLaw/GestioLex allegati;
- `legal_final_assessment`: resta `non_determinato` finche' non risulta una revisione umana esplicita.

## Workflow offline

Il workflow offline non spende chiamate live e non verifica fonti ufficiali. Serve a validare estrazione, rubric, scoring deterministico, mock traps e regressioni.

```text
file .docx/.pdf/.md/.txt
        |
        v
extract_text + split_sections
        |
        v
Evaluation Case JSON
        |
        v
offline mock judges
        |
        v
weighted scoring 0-39
        |
        v
ranking + human_review_flags + kappa_ready
```

Comandi:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py doctor
python3 concilio-llm-prompt-legale/scripts/legal_panel.py extract "answer.docx" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py single "answer.docx" --ground-truth ground_truth.md
python3 concilio-llm-prompt-legale/scripts/legal_panel.py compare "A.docx" "B.docx" "C.docx" --preset civile
python3 concilio-llm-prompt-legale/scripts/legal_panel.py mock
```

## Workflow live

Il workflow live prepara prompt separati per candidato e giudice. Il default operativo e' tre giudici indipendenti per candidato, seguiti da un supervisore/meta-giudice dopo la normalizzazione. L'indipendenza include diversita' di famiglia/modello: se Codex GPT-5.5 e' gia' giudice primario, Perplexity GPT-5.5 non deve essere un altro giudice primario di default; usare invece Gemini, Kimi o Nemotron. Non deve combinare piu' candidati o piu' giudici nello stesso raw file, per evitare contaminazione, errori di normalizzazione e perdita di audit trail.

```text
cases normalized locally
        |
        v
route/privacy gate
        |
        +-- user chooses local/offline --> stop at local workflow
        |
        v
prepare-live
        |
        v
case-A.json       A__judge1.prompt.md       A__judge2.prompt.md
case-B.json       B__judge1.prompt.md       B__judge2.prompt.md
        |
        v
run approved live routes
        |
        v
A__judge1.raw.txt A__judge2.raw.txt B__judge1.raw.txt ...
        |
        v
normalize-live
        |
        v
aggregated live JSON + raw_errors + kappa_ready
        |
        v
prepare-supervisor
        |
        v
supervisor prompt + supervisor raw output
```

Comandi:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py prepare-live \
  "A.docx" "B.docx" "C.docx" \
  --preset civile \
  --output-dir panel-results-raw \
  --cases-output panel-input.json

python3 concilio-llm-prompt-legale/scripts/legal_panel.py normalize-live \
  --cases panel-input.json \
  --raw-dir panel-results-raw \
  --output panel-results-normalized.json
```

## Source verification

La verifica fonti e' un layer separato dal giudizio LLM. Il giudice puo' valutare plausibilita', completezza e rischio, ma non puo' trasformare una citazione non controllata in citazione verificata.

```text
candidate answers + extracted citations
        |
        v
classify citation type
        |
        +-- Italian statute ------------> verify-sources -> normattiva_fetch.py -> official text files
        |
        +-- EU/GDPR law ----------------> EUR-Lex / official EU source
        |
        +-- case law or authority ------> approved legal DB -> SearXNG -> Perplexity if approved -> base discovery
        |
        v
verification record per citation
        |
        v
score impact + source_verification status
```

Stati ammessi:

- `verified`: fonte ufficiale o banca dati approvata conferma il contenuto rilevante;
- `mismatch`: la fonte esiste ma non sostiene l'uso fatto dal candidato;
- `not_found`: citazione non trovata;
- `unavailable`: strumento o accesso non disponibile;
- `unsupported`: tipo fonte non gestito.

Regola di reporting: `source_verification: not_performed` significa che le citazioni non sono state controllate su fonti ufficiali. Non deve essere presentato come verifica parziale o implicita.

Workflow operativo:

```bash
python3 concilio-llm-prompt-legale/scripts/legal_panel.py verify-sources --cases panel-input.json --output source-verification.json
python3 concilio-llm-prompt-legale/scripts/normattiva_fetch.py --sources source-verification.json --output-json normattiva-verification.json --output-md normattiva-verification.md --articles-dir normattiva-articles
python3 concilio-llm-prompt-legale/scripts/legal_panel.py report --input panel-results-normalized.json --sources source-verification.json --sources normattiva-verification.json --output panel-results-report.md
```

`normattiva_fetch.py` effettua una chiamata web ufficiale a Normattiva e va eseguito solo quando
l'utente ha autorizzato la route fonti. Il suo `verified` conferma esistenza e testo dell'articolo,
non la pertinenza giuridica dell'uso fatto dalla risposta candidata.

`source_gate` usa gli stati dei record:

- `passed`: tutti i record allegati sono verificati;
- `passed_with_findings`: almeno una fonte e' verificata, ma restano record problematici o non risolti;
- `failed`: ci sono `mismatch`/`not_found` senza fonti verificate;
- `not_performed`: nessun controllo ufficiale o banca dati approvata e' stato eseguito.

## Privacy gate

```text
input text
   |
   v
route already explicit in the user request?
   |
   +-- yes --> use requested route, naming providers/tools for online/live
   |
   +-- no  --> ask: local/offline only or online/live too?
   |
   v
classify confidentiality as risk metadata, not as an automatic route decision
   |
   v
local/offline choice --> offline/report only
online/live choice  --> run approved live workflow
```

Il gate vale anche quando l'utente ha installato gli strumenti live: disponibilita' tecnica non equivale ad autorizzazione. L'agente non deve decidere da solo "solo locale" o "online"; se la route non e' chiara, deve chiederla.

Prima di attivare il gate, l'agente deve leggere `confidential_reason`: se il flag `confidential` e' scattato solo per il tema (o non e' scattato) e non risultano dati personali reali, non trattare il materiale come riservato e non sovra-attivare il gate. La riservatezza si valuta sui dati effettivi (email reali, codici fiscali, parti nominate), non sulla presenza di parole come "email" o "GDPR".

## Scoring 0-39

La rubric usa sei criteri da 0 a 3 con pesi differenziati. Il massimo e' 39.

| Criterio | Peso | Massimo ponderato | Ragione |
| --- | ---: | ---: | --- |
| `correttezza_normativa` | 3 | 9 | Errore sulla norma o sull'applicazione invalida la risposta. |
| `aggiornamento` | 2 | 6 | Il diritto cambia; una risposta vecchia puo' essere dannosa. |
| `completezza` | 2 | 6 | Una risposta corretta ma incompleta puo' omettere rischi decisivi. |
| `assenza_allucinazioni` | 3 | 9 | Fonti inventate o fatti inventati sono rischio massimo. |
| `citazione_fonti` | 2 | 6 | Le coordinate verificabili sono necessarie per controllo professionale. |
| `segnalazione_incertezza` | 1 | 3 | Segnalare incertezza e orientamenti diversi e' parte della qualita' legale. |

Formula:

```text
score_ponderato = sum(score_criterio_0_3 * peso_criterio)
score_massimo = 39
percentuale = score_ponderato / 39 * 100
```

Soglie operative:

- `>= 27/39`: utile per drafting interno solo se le fonti sono verificate;
- `20-26/39`: segnale di screening, revisione sostanziale richiesta;
- `< 20/39`: risposta ad alto rischio, usare solo per identificare problemi da riscrivere.

Flag sempre attivi:

- media sotto 20/39;
- divergenza massima tra giudici sopra 8 punti;
- qualunque giudice richiede revisione umana;
- citazioni allucinate o non verificabili;
- diritto potenzialmente superato;
- materiale confidenziale trattato con route cloud non approvata;
- verifica fonti non eseguita quando la risposta dipende da citazioni contestate.

## Scoring e kappa

```text
judge verdicts
   |
   v
criterion scores 0-3
   |
   v
weighted score out of 39
   |
   v
discrete bucket for agreement
   |
   +-- <20    -> 0
   +-- 20-26  -> 1
   +-- 27-33  -> 2
   +-- >=34   -> 3
   |
   v
kappa_ready rows per candidate
```

`kappa_discrete_score` e' una discretizzazione operativa. Non sostituisce il calcolo statistico di Cohen/Fleiss kappa su un set pilota. Serve a rendere i risultati esportabili verso un calcolo di inter-rater agreement.

Procedura consigliata per calibrazione:

1. Preparare 30-50 casi pilota con ground truth strutturato e datato.
2. Far valutare ogni caso da almeno tre giudici indipendenti, evitando duplicazioni di famiglia/modello tra giudici primari.
3. Calcolare Fleiss kappa sui bucket 0-3 o kappa pesato su score ordinali.
4. Se kappa `< 0.40`, trattare il problema come difetto della rubric o del dataset, non come semplice difetto del modello.
5. Target operativo: kappa `>= 0.60` per screening ripetibile.

## Bias e presidi

La skill assume che ogni giudice LLM sia soggetto a bias. Il panel riduce il rischio solo se mantiene indipendenza, rubric esplicita e audit trail.

| Bias | Rischio per la skill | Presidio |
| --- | --- | --- |
| Style bias | Risposte in markdown o con formattazione ricca ricevono score artificiale. | Prompt che impone di ignorare polish; mock markdown-vs-prosa; possibilita' di normalizzare formato prima del giudizio. |
| Self-enhancement bias | Un giudice favorisce output simili alla propria famiglia di modello. | Giudici di famiglie diverse; candidate_id anonimi; raw separati. |
| Position bias | Il primo candidato puo' ricevere preferenza indebita. | Valutazione one-candidate-per-prompt dove possibile; se pairwise, randomizzazione o swap solo quando utile. |
| Verbosity/concision bias | Lunghezza o concisione vengono confuse con completezza. | Criteri separati per completezza e citazione fonti; istruzione di ignorare lunghezza non sostanziale. |
| Authority bias | Citazioni numerose sembrano autorevoli anche se false. | Source verification separata; override o flag se fonte non verificata. |
| Prompt leakage/cross contamination | Un giudice vede output o raw di altri giudici. | Prompt e raw file separati per candidato e giudice. |
| Model drift | Provider aggiorna il modello e rende il benchmark non comparabile. | Salvare `model_route`, raw output, data e metadata; preferire versioni esatte quando disponibili. |

Mock traps da mantenere nel casario:

- norma superata presentata come vigente;
- numero di decisione implausibile o inventato;
- risposta lunga ma senza fonti;
- risposta corretta ma operativamente inutile;
- coppie con stesso contenuto in markdown e prosa;
- certezza eccessiva su questione controversa;
- email/forwarding senza analisi di minimizzazione, informativa e limiti operativi.

## Come la ricerca influenza la skill

LLM-as-a-judge:

- motiva giudici indipendenti invece del giudice singolo;
- richiede rubric esplicita e output JSON;
- impone audit trail di prompt, raw e normalizzazione.

Benchmark legal/civil-law:

- motiva ground truth strutturati come checklist, non risposte narrative uniche;
- giustifica peso alto su correttezza normativa, allucinazioni e citazioni;
- suggerisce test su ragionamento multi-step, applicazione ai fatti e citazioni verificabili.

Inter-rater agreement:

- motiva `kappa_discrete_score`;
- impone calibrazione su set pilota;
- sposta il focus dal solo score medio alla concordanza tra giudici.

Bias research:

- motiva separazione candidati/giudici;
- richiede mock markdown-vs-prosa;
- impone attenzione a stile, posizione, self-preference e lunghezza.

Legal evaluation:

- motiva source verification separata dal giudizio LLM;
- vieta di presentare citazioni non controllate come affidabili;
- mantiene revisione professionale obbligatoria per l'uso pratico.

## Fondamenti scientifici e riferimenti per approfondire

Questa sezione e' strutturata per agenti: ogni riga contiene tema, fonte, identificatore stabile, link, uso nella skill e query consigliata. Le fonti core privilegiano paper, benchmark o pagine stabili. Fonti divulgative, Reddit, YouTube e pagine prodotto non sono base metodologica e sono isolate nell'appendice.

### Bibliografia ragionata

| Tema | Fonte | Identificatore stabile | Link | Perche conta nella skill | Query agent consigliata |
| --- | --- | --- | --- | --- | --- |
| LLM-as-judge fondativo | Fonte primaria: Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, Ion Stoica, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" | arXiv:2306.05685 | https://arxiv.org/abs/2306.05685 | Base del paradigma: giudici LLM, agreement con umani, bias di posizione, verbosity e self-enhancement. Giustifica judge prompts strutturati e controllo dei bias. | `arXiv 2306.05685 LLM-as-a-Judge MT-Bench Chatbot Arena bias` |
| Survey LLM-as-judge | Survey/metodo: Haitao Li, Qian Dong, Junjie Chen, Huixue Su, Yujia Zhou, Qingyao Ai, Ziyi Ye, Yiqun Liu, "LLMs-as-Judges: A Comprehensive Survey on LLM-based Evaluation Methods" | arXiv:2412.05579 | https://arxiv.org/abs/2412.05579 | Mappa funzionalita', metodologie, applicazioni, meta-valutazione e limiti. Supporta architettura modulare e distinzione tra valutazione, aggregazione e calibrazione. | `arXiv 2412.05579 LLMs-as-Judges comprehensive survey methodology limitations` |
| Bias mitigation recente | Fonte primaria: Sadman Kabir Soumik, "Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines" | arXiv:2604.23178 | https://arxiv.org/abs/2604.23178 | Confronta strategie di debiasing e segnala style bias dominante, position bias ridotto nei modelli recenti e preferenza per concisione. Motiva mock markdown-vs-prosa, rubric esplicita e attenzione alla lunghezza. | `arXiv 2604.23178 bias mitigation LLM-as-a-Judge style bias position bias` |
| Tassonomia bias | Fonte primaria: Jiayi Ye et al., "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" | OpenReview id 3GTtZFiajM; arXiv:2410.02736 | https://openreview.net/forum?id=3GTtZFiajM | Identifica 12 bias e propone quantificazione automatica. Motiva catalogo bias, candidate anonymization e red-team traps. | `OpenReview 3GTtZFiajM Justice or Prejudice Quantifying Biases LLM-as-a-Judge` |
| Kappa e interpretazione | Survey/metodo: Mary L. McHugh, "Interrater reliability: the kappa statistic" | PMC3900052 | https://pmc.ncbi.nlm.nih.gov/articles/PMC3900052/ | Riferimento pratico per interpretare kappa e distinguere accordo osservato da accordo casuale. Giustifica kappa come metrica di calibrazione, non come score legale. | `PMC3900052 McHugh Interrater reliability kappa statistic interpretation` |
| Metriche IAA per NLP | Survey/metodo: Joseph James, "Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric for NLP Annotation and Evaluation" | arXiv:2603.06865 | https://arxiv.org/html/2603.06865v2 | Aiuta a scegliere tra Cohen, Fleiss, kappa pesato, ICC e altre metriche in base al tipo di label. Supporta futura calibrazione del panel. | `arXiv 2603.06865 inter-annotator agreement metric NLP Fleiss kappa weighted kappa` |
| Benchmark civil-law europeo | Benchmark legale: Yu Fan et al., "LEXam: Benchmarking Legal Reasoning on 340 Law Exams" | arXiv:2505.12864 | https://arxiv.org/abs/2505.12864 | Benchmark su esami di diritto in inglese e tedesco con validazione esperta. Motiva ground truth con guidance esplicita e valutazione del reasoning multi-step. | `arXiv 2505.12864 LEXam legal reasoning 340 law exams LLM judge validation` |
| Legal writing civil-law | Benchmark legale: Ramon Pires, Roseval Malaquias Junior, Rodrigo Nogueira, "Automatic Legal Writing Evaluation of LLMs" | arXiv:2504.21202 | https://arxiv.org/abs/2504.21202 | OAB-Bench usa domande aperte e linee guida di correzione. Motiva checklist strutturate e scoring su risposte legali discorsive. | `arXiv 2504.21202 Automatic Legal Writing Evaluation OAB-Bench LLM judge` |
| Citazioni normative in civil-law | Benchmark legale: Odysseas S. Chlapanis, Dimitrios Galanis, Nikolaos Aletras, Ion Androutsopoulos, "GreekBarBench: A Challenging Benchmark for Free-Text Legal Reasoning and Citations" | arXiv:2505.17267 | https://arxiv.org/abs/2505.17267 | Richiede citazioni ad articoli e fatti del caso, con scoring tridimensionale e meta-valutazione. Motiva peso su `citazione_fonti` e source verification separata. | `arXiv 2505.17267 GreekBarBench legal reasoning citations span-based rubrics` |
| Task professionali legali | Benchmark legale: Scale AI, "Professional Reasoning Benchmark - Legal" | PRBench Legal leaderboard | https://labs.scale.com/leaderboard/prbench-legal | Benchmark professionale multi-giurisdizionale con rubriche pesate e judge validation. Motiva criteri pesati, penalizzazione di advice dannoso e focus su incertezza/auditability. | `PRBench Legal Scale AI professional reasoning benchmark legal rubric judge validation` |
| Survey legal LLM evaluation | Survey/metodo: Yiran Hu et al., "Evaluation of Large Language Models in Legal Applications: Challenges, Methods, and Future Directions" | arXiv:2601.15267 | https://arxiv.org/html/2601.15267v1 | Inquadra outcome accuracy, legal reasoning e trustworthiness. Motiva valutazione multi-dimensionale e attenzione a privacy, robustezza e hallucination legale. | `arXiv 2601.15267 evaluation large language models legal applications challenges methods` |
| Meta-judging multi-agent | Fonte primaria: Yuran Li, Jama Hussein Mohamud, Chongren Sun, Di Wu, Benoit Boulet, "Leveraging LLMs as Meta-Judges: A Multi-Agent Framework for Evaluating LLM Judgments" | arXiv:2504.17087 | https://arxiv.org/html/2504.17087v1 | Supporta l'idea di valutare anche la qualita' dei giudizi, usare piu' agenti e soglie. Nella skill resta riferimento per evoluzione futura, non comportamento runtime obbligatorio. | `arXiv 2504.17087 multi-agent framework evaluating LLM judgments meta-judge` |

### Contesto italiano e linguistico

Queste fonti non sono benchmark legali italiani. Servono a contestualizzare la valutazione in lingua italiana e il gap metodologico.

| Tema | Fonte | Identificatore stabile | Link | Perche conta nella skill | Query agent consigliata |
| --- | --- | --- | --- | --- | --- |
| Benchmark e modello italiano | Contesto italiano: Andrea Bacciu, Cesare Campagnano, Giovanni Trappolini, Fabrizio Silvestri, "DanteLLM: Let's Push Italian LLM Research Forward!" | LREC-COLING 2024, pp. 4343-4355 | https://www.diag.uniroma1.it/en/publication/29211 | Mostra un benchmark e leaderboard per italiano, ma non specifico legale. Motiva cautela su lingua e dominio. | `DanteLLM Let's Push Italian LLM Research Forward LREC COLING 2024 benchmark Italian` |
| Benchmark nativo italiano | Contesto italiano: Bernardo Magnini, Roberto Zanoli, Michele Resta, Martin Cimmino, Paolo Albano, Marco Madeddu, Viviana Patti, "Evalita-LLM: Benchmarking Large Language Models on Italian" | arXiv:2502.02289 | https://arxiv.org/abs/2502.02289 | Usa task nativi italiani e prompt multipli. Motiva attenzione a prompt sensitivity e risorse native. | `arXiv 2502.02289 Evalita-LLM Benchmarking Large Language Models on Italian` |
| Suite italiana generale | Contesto italiano: Luca Moroni, Simone Conia, Federico Martelli, Roberto Navigli, "Towards a More Comprehensive Evaluation for Italian LLMs" / ITA-Bench | CLiC-it 2024; repository SapienzaNLP/ita-bench | https://github.com/SapienzaNLP/ita-bench | Suite generale per LLM in italiano su QA, reasoning, matematica e altri task. Non copre diritto italiano ma offre pattern di evaluation suite. | `SapienzaNLP ITA-Bench Italian benchmarks LLM evaluation Moroni Conia Martelli Navigli` |

Nota metodologica: al 16 giugno 2026 non risultano, nella documentazione incorporata in questa skill, benchmark pubblici peer-reviewed specifici per il diritto italiano con copertura sistematica di legislazione, giurisprudenza e prassi professionale italiane. La skill quindi adatta evidenze da LLM-as-judge, benchmark legal/civil-law e benchmark generali per la lingua italiana. Questo trasferimento deve restare esplicito nei report.

### Fonti secondarie o non-core

Queste fonti possono servire come contesto, discovery o confronto di prodotto, ma non sono fondamento scientifico della skill:

- YouTube o video divulgativi su panel of judges;
- Reddit o post tecnici informali su RAG legale;
- pagine marketing di piattaforme AI legali;
- blog vendor su LLM-as-judge, RAG o evaluation;
- leaderboard senza paper o protocollo auditabile.

Regola: se una fonte e' secondaria/non-core, non usarla per giustificare scoring, soglie, kappa o source verification. Usarla al massimo per generare query verso paper, documentazione ufficiale o benchmark stabili.

## Roadmap tecnica

Possibili evoluzioni senza modificare la promessa di base:

- calcolo automatico di Fleiss kappa su `kappa_ready`;
- normalizzazione esplicita markdown-vs-prosa prima dei giudizi live;
- supervisor/meta-judge come fase standard dopo `normalize-live`, mantenendo raw separati;
- esportazione di casari pilota con ground truth firmato e datato;
- registry di rubric versionate con hash;
- test automatico che confronta coppie semanticamente identiche ma stilisticamente diverse.

## Invarianti da non rompere

- Non modificare scoring o routing runtime dentro `quick_validate.py`.
- Non presentare `source_verification: not_performed` come verifica.
- Non combinare raw di piu' giudici o candidati.
- Non scegliere local/offline o online/live in autonomia quando la route non e' esplicita: chiedere prima all'utente.
- Non far divergere `CLAUDE.md` e `AGENTS.md`: ogni modifica a uno richiede modifica identica dell'altro.
