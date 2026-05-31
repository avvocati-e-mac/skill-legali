# Report di confronto a 3 vie — v3 (rubrica booleana fondata sulla letteratura)

Data: 2026-05-29 · Terza revisione metodologica. v1 (metriche non definite, giudice contaminato)
→ v2 (rubrica booleana cieca + letteratura) → **v3** (regola di disambiguazione su M2 per alzare
l'accordo tra giudici, con verifica sui file).

Topic: guida per installare un server SearXNG su macOS Apple Silicon (Docker + OrbStack) con
JSON API per un client MCP. Tre metodi di ricerca a confronto:
WebSearch · MCP SearXNG + skill (progressive disclosure) · MCP SearXNG grezzo.

---

## Cosa è cambiato rispetto alla v1 (e perché)

Su segnalazione dell'utente, due difetti sono stati corretti con scelte **ancorate alla
letteratura** (bibliografia completa in `references_literature.md`):

1. **"Qualità fonti" premiava la provenienza** (ufficiale = buono). Sostituita da **M3 Supporto
   & corroborazione** derivata dal **CRAAP test** (che separa *Currency*/attualità da
   *Authority*/provenienza) e dalla letteratura **truth discovery** (Dong/Berti-Équille/
   Srivastava, VLDB 2009): la corroborazione conta solo tra **fonti indipendenti** (il
   *circular reporting* non aggiunge conferme), e una **fonte singola corretta non è penalizzata**
   (la maggioranza non è prova di verità — fino al 30% di errore col solo majority voting).
2. **Punteggi Likert 1–10 soggettivi.** Sostituiti da **conteggi booleani** (item sì/no →
   normalizzato 0–10), che la letteratura mostra dare **inter-rater agreement più alto**
   (Reference-Guided Verdict, arXiv:2408.09235).
3. Metriche correlate (Completezza/Eseguibilità/OrbStack) **fuse in una M1 pesata** (no doppio
   conteggio della copiosità). Efficienza token tenuta **separata**. Accordo tra giudici
   riportato con **Krippendorff's α** (non più scarto ad hoc).

Giudizio **cieco** confermato: guide anonime da template unico, ordine randomizzato per
ciascun giudice, mappatura sigillata (`_KEY.md`) non vista dai giudici, cecità verificata via
grep. Un-blinding: `guide_1`=MCP grezzo · `guide_2`=WebSearch · `guide_3`=MCP+skill.

---

## Risultati — media dei 3 giudici (± dev. std.)

| Metrica | MCP grezzo | WebSearch | MCP + skill |
|---|---|---|---|
| M1 Completezza pesata | 5.0 | 10.0 | 10.0 |
| M2 Accuratezza (v3, validata sui file) | 7.0 | 10.0 | 10.0 |
| M3 Supporto & corroborazione | 7.0 | 6.7 | 4.7 |
| **Totale qualità /30** | **19.0** | **26.7** | **24.7** |

### Affidabilità tra giudici (Krippendorff's α, ordinale, soglia 0.80)

| Metrica | α | Lettura |
|---|---|---|
| M1 Completezza | **1.000** | accordo perfetto — checklist booleana pesata pienamente riproducibile |
| M2 Accuratezza (v3) | vedi sotto | rifatta in v3 con regola di disambiguazione |
| M3 Supporto/corrobor. | **0.798** | borderline: l'indipendenza delle fonti resta in parte di giudizio |

### M2 in v3 — regola di disambiguazione + verifica su ground truth

In v2 M2 aveva α=0.43 (disaccordo sul caso "config presente ma mal posizionata"). In v3 la
rubrica è stata estesa con una **regola di eseguibilità letterale** ("se copio-incollo esatto,
ottengo il risultato della fact-key? sì/no") e M2 è stata **rivalutata da 3 nuovi giudici ciechi**.

Esito istruttivo:
- **2 giudici su 3** hanno dato `guide_1`=7 (il suo `formats:` è a livello radice → non abilita
  JSON → errato) e `guide_2`=`guide_3`=10 (`formats:` sotto `search:` → corretto).
- **1 giudice ha invertito** le etichette (ha creduto che fosse guide_2/3 ad avere l'errore).
- **Verifica oggettiva sui file** (`grep` sul blocco `formats:` nelle 3 guide blind): `guide_1`
  ha davvero `formats:` a **radice**; `guide_2` e `guide_3` lo hanno sotto `search:`. → i **2
  giudici concordi sono fattualmente corretti**, il terzo ha sbagliato.

Quindi:
- α tra i **3 come riportati** = **−0.20** (apparente disaccordo, causato dall'errore del 3°).
- α tra i **2 validati dal ground truth** = **1.000**.
- **M2 finale (validato sui file): guide_1=7, guide_2=10, guide_3=10.**

> Questo è il valore aggiunto del disegno multi-giudice + metrica booleana: la regola è così
> netta che un controllo umano sui file **decide** chi ha ragione (non è opinione). Il design
> ha **catturato l'outlier** invece di mediarlo silenziosamente. Lo riportiamo per intero.

### Efficienza token (misura oggettiva, classifica SEPARATA — `token_efficiency.md`)

| | MCP grezzo | WebSearch | MCP + skill |
|---|---|---|---|
| Char ingeriti | ~14.580 | ~6.690 | **~5.200** |
| Qualità/1000 char (descrittivo) | 1.3 | 4.0 | **4.7** |

> L'indice qualità/token è **descrittivo**: con qualità vicine (WebSearch vs skill) dividere
> amplifica il rumore, quindi non è un ranking primario.

---

## Classifica

**Per qualità (cieca, /30):** 1) WebSearch 26.7 · 2) MCP+skill 24.7 · 3) MCP grezzo 19.0
**Per efficienza token:** 1) MCP+skill (~5.200) · 2) WebSearch (~6.690) · 3) MCP grezzo (~14.580)
**Rapporto qualità/token:** 1) MCP+skill 4.7 · 2) WebSearch 4.0 · 3) MCP grezzo 1.3

---

## Verdetto

- **Qualità del contenuto: WebSearch e MCP+skill sono pari** su Completezza (10/10) e
  Accuratezza (10/10). L'unica differenza è **M3**: WebSearch (6.7) > skill (4.7) perché aveva
  citato fonti realmente **indipendenti** (repo + docs SearXNG + docs OrbStack, due-tre origini
  distinte), mentre la sintesi della skill si appoggiava a guide di terzi (OpenWebUI/Msty/
  OpenClaw) che — con la regola dependence-aware — i tre giudici hanno concordemente segnalato
  come **circular reporting** (ricavate dalla stessa origine ufficiale) → contano come 1 fonte.
  Differenza **reale e indipendente dal tool**: dipende da *quali* fonti la sintesi mette in
  evidenza, non dal motore di ricerca.
- **Miglior rapporto qualità/token: MCP+skill** — qualità ~pari a WebSearch con il **costo token
  più basso** (~1/3 del grezzo, ~22% meno di WebSearch).
- **Risultato più solido (B vs C): la skill batte il MCP grezzo di +5.7 punti** (24.7 vs 19.0)
  con **~1/3 dei token**. Il grezzo legge una sola pagina full-page off-topic e resta scoperto
  sugli item bloccanti (secret key, limiter, porta, OrbStack, ARM) → M1 = 5.0; in più il suo
  `formats:` è a livello radice (errato per la regola v3) → M2 = 7.0.
  *Nota:* il grezzo prende M3 alto (7.0) **non** perché le sue fonti siano migliori, ma perché
  la regola "minoranza-corretta ammessa" non lo penalizza per avere **una sola** fonte sui
  pochi fatti che tratta — un effetto-bordo corretto della metrica, da leggere insieme a M1.

---

## Limiti dichiarati (red teaming residuo)

1. **Pesi M1 e fact-key M2 li definisco io** → oggettività *condizionata* a quelle assunzioni;
   sono separate, versionabili e contestabili. In v3 la regola di eseguibilità letterale ha reso
   M2 verificabile sui file (i 2 giudici corretti concordano, α=1.000); l'outlier del 3° giudice
   è stato individuato e scartato col controllo oggettivo, non mediato.
2. **Indipendenza delle fonti** stimata dai giudici leggendo gli URL → la detection rigorosa
   del copying richiederebbe analisi bayesiana (truth-discovery) fuori scope. M3 α=0.798 riflette
   questa residua soggettività.
3. **Task tarato sulla skill** (porta 8100) → validità esterna limitata.
4. **3 giudici stesso modello** → errori potenzialmente **correlati**; α misura l'accordo, non
   l'assenza di bias condiviso.

---

## Tracciabilità
Rubrica: `test/rubric.md` (v3) · Bibliografia: `test/references_literature.md` · Guide cieche:
`test/blind/guide_{1,2,3}.md` · Chiave: `test/blind/_KEY.md` · Token: `test/token_efficiency.md`
· Materiale grezzo: `test/guide_{A,B,C}_*.md`.
