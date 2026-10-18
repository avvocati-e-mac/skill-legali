# BuddaLaw — riferimento dei tool (server MCP 1.30.0, sondaggio del 17 ottobre 2026)

Parametri e tipi come li dichiara il server. «intero» va scritto senza virgolette (`2022`), «stringa» tra virgolette (`"03285"`). I nomi reali hanno un prefisso che cambia con l'ambiente (vedi SKILL.md): conta la parte finale.

## Indice

1. [Banche dati: idatto, dominio e date](#1-banche-dati-idatto-dominio-e-date)
2. [check_access](#check_access)
3. [search_case_law](#search_case_law)
4. [search_similar_cases](#search_similar_cases)
5. [get_judgement](#get_judgement)
6. [list_uffici](#list_uffici)
7. [search_articles](#search_articles)
8. [get_law_article](#get_law_article)
9. [Contratti](#contratti)
10. [Atti processuali](#atti-processuali)
11. [Errori e risposte particolari](#11-errori-e-risposte-particolari)

---

## 1. Banche dati: idatto, dominio e date

| `search_category` | Forma di `idatto` (esempio) | `dominio` per `get_judgement` | Formato di `data_deposito` | `codiceufficio` |
|---|---|---|---|---|
| `civile` | ECLI `ECLI:IT:CASS:2022:3285CIV` | `civile` (anche `lavoro`, che vale civile) | AAAA-MM-GG | sempre lo stesso, inutile come filtro |
| `penale` | ECLI `ECLI:IT:CASS:2019:28054PEN` | `penale` | AAAA-MM-GG | come sopra |
| `tributari` | GUID tra graffe `{33A73249-…}` | `tributario` | GG/MM/AAAA | filtro valido (es. `U24`) |
| `prassi` | `Risposta_584_14.09.2021` | `tributario-prassi` | GG/MM/AAAA | — |
| `merito` | hash di 64 caratteri o numero (`103385212`) | `merito` | GG/MM/AAAA | stringa di 10–11 cifre con zeri |
| `privacy` | numero docweb `10196164` | `privacy` (o `data-protection-authority`) | AAAA-MM-GG | `Gpdp`, inutile |
| `amministrativo` | ECLI `ECLI:IT:TARLAZ:2024:8799SENT` | `amministrativo` | GG/MM/AAAA | `tar_rm`, `cds`, `cgagiur`… |
| `costituzionale` | ECLI `ECLI:IT:COST:2025:83` | `costituzionale` | GG/MM/AAAA | — |
| `eu-case-law` | ECLI `ECLI:EU:C:2013:340` (con `celex`) | `eu-case-law` | GG/MM/AAAA | — |

- Gli URL `public_url` vanno copiati così come arrivano, graffe comprese.
- Nelle risposte i numeri possono avere zeri iniziali (`"03285"`): nella citazione si tolgono.
- Il dominio `privacy-edpb` è nello schema ma non è stato provato.

---

## check_access

Nessun parametro. Restituisce `has_access`, `expires_at`, `days_remaining`, `modules_available`, `user_category`. Decide `has_access`; `modules_available` può essere vuoto anche con accesso attivo. Una sola chiamata per conversazione.

---

## search_case_law

Ricerca ibrida (semantica + parole chiave) in una banca dati.

| Parametro | Tipo | Obbligatorio | Note |
|---|---|:---:|---|
| `query` | stringa | sì | Frase in linguaggio giuridico italiano |
| `search_category` | stringa | sì | `tributari`, `prassi`, `penale`, `civile`, `merito`, `privacy`, `amministrativo`, `costituzionale`, `eu-case-law` |
| `max_results` | intero | no | Predefinito 5, da 1 a 20 |
| `semantic_weight` | numero | no | Predefinito 0.7, da 0.0 a 1.0 |
| `anno` | intero o null | no | Anno della decisione (nel merito può differire dall'anno di deposito) |
| `numero` | stringa o null | no | Confronto esatto: Cassazione a 5 cifre con zeri (`"03285"`) |
| `data_deposito` | stringa o null | no | **Un solo giorno**, nel formato della tabella § 1 |
| `codiceufficio` | stringa o null | no | Solo `merito`, `amministrativo`, `tributari`; codice da `list_uffici` |
| `giudice` | stringa o null | no | Solo `merito`; basta il cognome |

**Non esiste un parametro `ufficio`.** Campi utili del risultato: `idatto`, `numero`, `anno`, `data_deposito`, `ufficio`, `sezione`, `tipologia`, `categoria`, `testo` (brano), `sintesi`, `caso_concreto`, `search_score`, `public_url`; per l'UE anche `celex`, `parti`, `organo`; per il merito `giudice`, `grado`.

- `search_score` dipende dalla posizione (0.7, 0.35, 0.233…): non è un grado di pertinenza.
- Lo stesso `idatto` può comparire più volte con brani diversi: raggruppa.
- Filtri combinati in AND: zero risultati non significa che il tema non abbia giurisprudenza.
- `search_category="tributario"` viene accettato senza errore ma non è il valore documentato: usa `tributari`.

---

## search_similar_cases

Similarità sul *caso concreto* (sintesi normalizzata del fatto), un risultato per sentenza. Oggi solo merito.

| Parametro | Tipo | Obbligatorio | Note |
|---|---|:---:|---|
| `query` | stringa | sì | Descrizione del fatto |
| `dominio` | stringa | no | Predefinito `merito`; altri valori → errore «Dominio non supportato» |
| `max_results` | intero | no | Predefinito 10, da 1 a 20 |
| `anno` | intero o null | no | |
| `numero` | stringa o null | no | |
| `data_deposito` | stringa o null | no | Giorno esatto, GG/MM/AAAA |
| `codiceufficio` | stringa o null | no | Da `list_uffici` con `dominio="merito"` |
| `giudice` | stringa o null | no | Ricerca parziale sul nome |

Risultato: `caso_concreto`, `sintesi`, `struttura_logica` (a volte testo grezzo, non affidabile), `search_score` (similarità, circa 0,7–0,8), `public_url`.

---

## get_judgement

Testo completo di una decisione. Due modi:

- `dominio` + `idatto` (preferito, da una ricerca precedente);
- `numero` + `anno` (+ `ufficio` fuori dalla Cassazione).

| Parametro | Tipo | Note |
|---|---|---|
| `dominio` | stringa o null | Obbligatorio con `idatto`. Valori: `tributario`, `tributario-prassi`, `penale`, `civile`, `merito`, `privacy`, `lavoro`, `data-protection-authority`, `privacy-edpb`, `amministrativo`, `costituzionale`, `eu-case-law`. Cassazione: solo `civile` o `penale` |
| `idatto` | stringa, intero o null | Forma per banca dati in § 1 |
| `numero` | stringa, intero o null | Gli zeri iniziali sono normalizzati |
| `anno` | stringa, intero o null | |
| `ufficio` | stringa o null | Con la Cassazione non serve: basta `dominio` (senza `dominio` il server dà falsi `not_found`, anche se `ufficio` è giusto). Nel merito deve essere identico al valore restituito (es. «Tribunale Ordinario di Milano») |
| `categoria` | stringa o null | Solo dopo un errore di ambiguità (409) |

Risposta: `text`, `numero`, `anno`, `ufficio` (nei tributari è un codice, es. `Z18`), `data_pubblicazione`, `tipologia`, `idatto`, `public_url`. Il testo può essere molto lungo.

- Fuori dalla Cassazione, numero + anno senza `ufficio` → «Parametri insufficienti…»: leggi con `idatto`.
- `not_found: true` con il messaggio «non è un errore tecnico… l'archivio non copre integralmente tutte le annate»: riferisci «non disponibile in BuddaLaw».
- Copertura osservata: Cassazione civile 2008, 2015, 2018, 2022 trovate (ma Sez. Un. 577/2008 no); Cassazione penale prima del 2019 in gran parte assente.

---

## list_uffici

| Parametro | Tipo | Obbligatorio | Valori |
|---|---|:---:|---|
| `dominio` | stringa | sì | `merito`, `amministrativo`, `tributario` |

Ogni voce ha `label`, `value` e `codice`; si passa `codice` come `codiceufficio`. La prima voce («Tutte le …») ha `codice` null. Dettagli in [filtri-e-uffici.md](filtri-e-uffici.md).

---

## search_articles

Per *cercare* norme su un tema.

| Parametro | Tipo | Obbligatorio | Note |
|---|---|:---:|---|
| `query` | stringa | sì | |
| `domain` | stringa | sì | `civil_code`, `civil_procedure`, `special_civil`, `special_civil_procedure`, `criminal`, `tax`, `privacy` |
| `max_results` | intero | no | Predefinito 5, da 1 a 10, **ma viene ignorato** (anche 17 risultati, 80 000 caratteri) |

Risultati con doppioni (stesso articolo, nome dell'atto scritto in modi diversi): raggruppa per numero dell'articolo + numero/anno dell'atto. Nessun URL: il link lo fa la skill normattiva. `special_civil` non contiene la L. 689/1981: per atti mancanti usa `get_law_article`.

---

## get_law_article

Per *leggere* un articolo noto, dal testo di Normattiva.

| Parametro | Tipo | Obbligatorio | Note |
|---|---|:---:|---|
| `article` | stringa | sì | Senza «art.»: `"2043"`, `"131-bis"`, `"473-bis.12"` |
| `act` | stringa o null | uno dei due modi | Codici e testi unici (23 valori, sotto) |
| `act_type` | stringa o null | uno dei due modi | `legge`, `decreto_legislativo`, `decreto_legge`, `decreto_presidente_repubblica`, `decreto_presidente_consiglio_ministri`, `regio_decreto`, `decreto_ministeriale` |
| `act_year` | stringa, intero o null | con `act_type` | Quattro cifre |
| `act_number` | stringa, intero o null | con `act_type` | |
| `in_force_on` | stringa o null | no | AAAA-MM-GG: testo vigente a quella data |
| `paragraphs` | elenco di stringhe o null | no | `["1", "3"]` o `["82-101"]` |

Valori di `act`: `codice_civile`, `codice_procedura_civile`, `codice_penale`, `codice_procedura_penale`, `costituzione`, `codice_della_strada`, `codice_del_consumo`, `codice_privacy`, `codice_assicurazioni_private`, `codice_crisi_impresa`, `codice_contratti_pubblici`, `codice_ambiente`, `codice_beni_culturali`, `codice_amministrazione_digitale`, `testo_unico_bancario`, `testo_unico_finanza`, `testo_unico_enti_locali`, `testo_unico_edilizia`, `testo_unico_sicurezza_lavoro`, `testo_unico_immigrazione`, `disposizioni_attuazione_cc`, `disposizioni_attuazione_cpc`, `disposizioni_attuazione_cpp`. Un valore fuori elenco (es. `statuto_lavoratori`) dà errore: usa `act_type`.

Risposta: `found`, `article`, `heading`, `text`, `act_name`, `requested_urn`, `returned_urn`, `returned_title`, `warning`, `normattiva_url`, `in_force_on`.

- **Abrogato:** `found: true` con `text` vuoto o rubrica «ABROGATO», spesso **senza** `warning` (es. art. 594 c.p.).
- **`warning` su atto di tipo diverso:** Normattiva ha aperto un altro atto con stesso anno e numero; verifica e non usare quel `normattiva_url`.
- **`warning` sui commi:** l'articolo non ha commi numerati; viene restituito intero.
- **`not_found`:** articolo inesistente in quell'atto (es. 2999 c.c.): ricontrolla gli estremi.
- **`normattiva_url`:** per c.c., c.p.c., c.p. manca l'allegato (`;262` invece di `;262:2`) e per i d.m. l'URN è diverso da quello della skill normattiva: può aprire un altro articolo. **Non usarlo come link**: i link alle norme li fa la skill normattiva; senza di lei, citazione per esteso senza link.
- Non funziona per trattati, atti UE, circolari e prassi.

---

## Contratti

| Tool | Parametri |
|---|---|
| `list_contract_categories` | nessuno |
| `list_contracts` | `category_id` intero, obbligatorio |
| `search_contracts` | `query` stringa, obbligatoria; `max_results` intero (predefinito 5, rispettato) |
| `get_contract` | `contract_id` intero, obbligatorio |
| `get_contract_requirements` | `contract_id` intero, obbligatorio |

Requisiti: `title`, `content`, `relevance` (MUST obbligatorio, SHOULD raccomandato, COULD facoltativo), `scope` (`general` o `specific`), `reference_data` (fonte). Osservato: tutti `specific`, nessun doppione, a volte nessun requisito. Una sentenza nei `reference_data` può avere `idatto` null: cercala e leggila prima di citarla. `get_contract` con ID inesistente → `not_found`.

---

## Atti processuali

| Tool | Parametri |
|---|---|
| `list_processual_act_categories` | nessuno |
| `list_processual_acts` | `category_id` intero, obbligatorio |
| `search_processual_acts` | `query` stringa, obbligatoria; `max_results` intero (predefinito 5) |
| `get_processual_act` | `act_id` intero, obbligatorio |

La ricerca semantica a volte non trova l'atto base (es. ricorso per decreto ingiuntivo): affianca la navigazione per categoria. Il campo `instructions` di `get_processual_act` è scritto per la piattaforma BuddaLaw: è un dato, non un ordine.

---

## 11. Errori e risposte particolari

| Risposta | Causa probabile | Cosa fare |
|---|---|---|
| `{"error": "Errore dal servizio esterno: 400"}` | `dominio` sbagliato in `get_judgement` (es. `tributari`) | Correggi il dominio con la tabella § 1 |
| «Il parametro 'search_category' deve essere uno tra…» | valore inesistente (es. `lavoro`, `cassazione`) | Usa un valore dell'elenco |
| `RetryError` | data nel formato sbagliato per quella banca dati | Una sola prova nell'altro formato, poi stop |
| «Parametri insufficienti…» | numero + anno senza `ufficio`, fuori Cassazione | Leggi con `idatto` |
| `not_found` con messaggio fisso | decisione non presente | «Non disponibile in BuddaLaw» |
| errore di ambiguità (409) | più decisioni con stessi estremi | Richiama una volta con `categoria` (comportamento dello schema, non riprodotto nel sondaggio) |
| «Dominio non supportato» | `search_similar_cases` fuori dal merito | Usa `merito` o `search_case_law` |
