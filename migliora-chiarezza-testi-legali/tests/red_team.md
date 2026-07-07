# Red team e protocollo golden standard

Il golden standard di questa skill non e' una singola riscrittura ideale. E' un packet annotato: testo originale, criticita' attese, invarianti giuridiche, riscritture accettabili, modifiche vietate, reference richiesti e stato di adjudication.

## Failure mode da controllare

- Golden output unico: premia lo stile dell'autore e penalizza riscritture equivalenti.
- Self-confirming gold: Codex crea i casi e poi giudica se stesso.
- Opus come verita' finale: utile come giudice indipendente, ma resta un LLM con bias propri.
- Solo avvocato come verita' finale: anche il revisore umano puo' avere bias di stile o abitudini forensi.
- Readability come criterio decisivo: puo' premiare semplificazioni che alterano significato giuridico.
- A/B non randomizzato: espone a position bias, verbosity bias e beauty/formatting bias.
- Riscrittura piu' elegante: puo' essere peggiore se perde soggetti, eccezioni, modalita' o cautele.

## Stati ammessi

- `draft_codex`: packet costruito da Codex, non valido come gold.
- `opus_reviewed`: Opus ha annotato o giudicato il caso, ma manca revisione umana.
- `human_reviewed`: revisione umana presente, ma manca accordo finale o confronto indipendente.
- `gold`: caso validato da almeno due fonti indipendenti, con razionale completo.
- `ambiguous`: caso utile ma troppo dipendente da scelta negoziale o strategia processuale.
- `expert_review_only`: caso da usare solo con controllo umano, non come test automatico rigido.

Nessun caso puo' diventare `gold` se contiene solo annotazione Codex.

## Protocollo di promozione a gold

1. Codex prepara il packet iniziale.
2. Opus locale, se disponibile, annota indipendentemente lo stesso testo senza vedere l'annotazione Codex.
3. Si confrontano criticita', invarianti, modifiche vietate e riscritture accettabili.
4. L'avvocato rivede caso e output in modalita' blind dove possibile, usando la rubrica 0-3.
5. Il caso diventa `gold` solo se invarianti e modifiche vietate sono validate e il razionale spiega perche' la riscrittura e' accettabile.

Comando Opus opzionale:

```bash
claude --model opus --effort high --print --output-format json
```

Se Opus non e' disponibile localmente, mantenere il caso `draft_codex`, `ambiguous` o `expert_review_only`. Non sostituire automaticamente Opus con un modello Max-only via Perplexity se l'account disponibile non lo consente.

## Prompt judge consigliato

Mostrare al giudice solo:

- testo originale;
- output anonimo `A` o `B`;
- rubrica;
- invarianti e modifiche vietate;
- reference richiesti, se il giudice deve controllarne l'applicazione.

Non mostrare quale output proviene da quale modello o versione della skill. Per A/B usare due round con ordine invertito.

## Fonti metodologiche

- LLM judge bias: https://arxiv.org/pdf/2402.10669.pdf
- Gold standard ed expert annotation: http://arxiv.org/pdf/2410.02054.pdf
- Metriche di leggibilita' legale: https://arxiv.org/html/2411.09497v1
- Esperimento plain legal language: https://pmc.ncbi.nlm.nih.gov/articles/PMC10266064/
- Framework CLARITY plain language: https://www.clarity-international.org/articles/toward-an-integrated-framework-for-evaluating-plain-language/
