# Rubrica di valutazione per chiarezza legale

Questa rubrica non premia il testo piu' elegante. Premia la riscrittura che rende il testo piu' chiaro senza spostare il significato giuridico.

## Cancelli di esclusione

Assegna fallimento immediato, anche se il testo e' scorrevole, quando l'output:

- altera soggetti, obblighi, eccezioni, termini, date o importi;
- inventa fatti, documenti, fonti, norme, sentenze, allegati o numeri;
- elimina un rischio giuridico invece di chiarirlo;
- omette il formato richiesto `PRIMA:`, `DOPO:`, `Motivo:`;
- presenta come certa una conseguenza giuridica che nel testo originale e' solo eventuale.

## Scala 0-3

Usa sempre la scala 0-3. Non usare voti 1-10: danno una falsa precisione e amplificano preferenze stilistiche del giudice.

### 1. Fedelta' giuridica

- 0: altera il significato giuridico o la posizione delle parti.
- 1: conserva il tema generale, ma cambia un obbligo, un'eccezione o un rischio.
- 2: conserva il significato, con una piccola imprecisione non decisiva.
- 3: conserva integralmente significato, modalita', condizioni ed effetti.

### 2. Preservazione di soggetti, obblighi, eccezioni, date e importi

- 0: perde o cambia un elemento essenziale.
- 1: conserva alcuni elementi, ma ne omette uno rilevante.
- 2: conserva gli elementi essenziali, ma lascia un riferimento meno preciso.
- 3: conserva tutti gli elementi richiesti dal packet.

### 3. Riduzione dell'ambiguita'

- 0: introduce nuova ambiguita' o lascia intatto il problema principale.
- 1: riduce un'ambiguita' secondaria ma non quella centrale.
- 2: chiarisce il problema principale, con qualche residuo da rifinire.
- 3: trasforma il punto ambiguo in regola, condizione o domanda operativa chiara.

### 4. Chiarezza sintattica

- 0: resta opaco, prolisso o grammaticalmente fragile.
- 1: migliora singole parole ma mantiene struttura difficile.
- 2: spezza frasi e rende il soggetto piu' visibile.
- 3: usa frasi lineari, voce attiva quando utile e ordine logico leggibile.

### 5. Utilita' pratica per l'avvocato

- 0: non aiuta a decidere cosa modificare nel testo.
- 1: segnala un problema, ma senza indicare una riscrittura utilizzabile.
- 2: offre una riscrittura utile ma richiede ancora molto lavoro.
- 3: offre una revisione pronta da valutare o una scelta negoziale esplicita quando serve.

### 6. Rispetto del formato PRIMA/DOPO/Motivo

- 0: manca uno dei tre blocchi o l'output e' solo commento.
- 1: usa i blocchi, ma in modo disordinato o incompleto.
- 2: usa i blocchi correttamente, con motivo generico.
- 3: usa `PRIMA:`, `DOPO:`, `Motivo:` in modo coerente e spiega la ragione concreta della modifica.

### 7. Uso corretto dei reference

- 0: ignora un reference obbligatorio o cita una fonte non verificata.
- 1: richiama un principio pertinente ma lo applica male.
- 2: applica il reference giusto senza sovraccaricare la risposta.
- 3: usa il reference necessario, specialmente per atti giudiziari o ambiguita' contrattuali, e non apre fonti inutili.

### 8. Assenza di invenzioni normative o fattuali

- 0: inventa norme, sentenze, date, importi, allegati o fatti.
- 1: aggiunge dettagli plausibili ma non presenti.
- 2: usa un segnaposto o segnala correttamente l'informazione mancante.
- 3: non inventa nulla e distingue chiaramente dato disponibile, proposta redazionale e punto da verificare.

## Confronti A/B

Per confrontare due output, usare ID neutri `A` e `B`. Eseguire almeno due passaggi con ordine invertito:

- round 1: output originale come `A`, output alternativo come `B`;
- round 2: output alternativo come `A`, output originale come `B`.

Il report deve distinguere:

- regressioni vere;
- differenze stilistiche accettabili;
- casi soggettivi da lasciare `ambiguous` o `expert_review_only`.

Non premiare lunghezza, markdown, tono piu' brillante o spiegazioni piu' ornate se la fedelta' giuridica non migliora.
