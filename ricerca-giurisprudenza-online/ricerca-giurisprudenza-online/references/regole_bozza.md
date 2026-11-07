# Regole della bozza e del report

Si scrive solo dopo i controlli della Fase 5 e leggendo solo le schede (`lavoro/schede/`), `lavoro/conteggi.txt` e `lavoro/tabelle.md`. Non rileggere i provvedimenti interi.

## Struttura di `lavoro/bozza.md`
1. **Sintesi** (max 5 righe): principi condivisi e conseguenze, distinguendo decisivo, concorrente e obiter, e indicando le conseguenze che il provvedimento collega al tema quando ci sono.
2. **Tabella degli estremi**: incolla quella di `tabelle.md`. Colonne fisse: ufficio, sezione, tipo, data decisione, data deposito, numero, R.G., giudice o collegio (con l'`id` in prima colonna per i rinvii).
3. **Una scheda per provvedimento**: estremi, cosa dice, perché rileva.
4. **Tabella cronologica**: incolla quella di `tabelle.md`. Colonne: peso del tema, esito, conseguenze legate al tema.
5. **Linee di tendenza**.
6. **Contrasti** (obbligatoria): per ogni punto del quesito indica se le pronunce lette concordano o divergono (con id) e se la divergenza è tra gradi. Se non hai cercato la tesi opposta, dillo.
7. **Fonti secondarie** (commenti, riviste) in una sezione a parte.
8. **Numeri della ricerca** (risultati totali, pertinenti, letti, scaricati: valori di `conteggi.txt`) e **limiti** (siti e periodo coperti, interrogazioni fatte, schede senza testo integrale, controlli manuali se manca python3).

## Regole anti-generalizzazione
- Ogni affermazione generale cita gli id che la reggono. Con meno di tre pronunce concordi scrivi "in una pronuncia" o "in due pronunce".
- Con meno di 10 schede usa "in N pronunce lette" al posto di qualsiasi formula di prevalenza.
- Vietati "costante", "consolidato", "primo", "unico", "orientamento prevalente" senza prova nelle schede.
- Un esito si attribuisce al tema solo se `tema_causa_dell_esito` = "si". Una conseguenza che il provvedimento collega al tema si attribuisce al tema solo se `ruolo_del_tema` è decisivo o concorrente.
- Distingui sempre decisivo / concorrente / obiter: un obiter non è una ratio.
- Tieni separato ciò che il provvedimento dice da ciò che deduci tu; le deduzioni dichiarale come tali.
- Un campione di ricerca non è l'universo: non scrivere che "non esistono" altre pronunce, solo che "non risultano nella ricerca".
- Le citazioni "da verificare" non entrano nel testo finché non sono ricontrollate sul testo completo; non sono mai "inesistenti", solo non ritrovate nell'estratto.

## Fonti secondarie
Commenti, note a sentenza, articoli di riviste: sezione separata, mai come conferma di un indirizzo. Non riprodurre massime o note redazionali di riviste o banche dati private: solo riferimento e link.

## Norme
Metti il link a Normattiva sulle norme statali: usa la skill "normattiva" se disponibile, altrimenti gli schemi di `references/normattiva.md`; segnala i link non verificati.

## Persone
Non cercare di identificare persone oscurate nei provvedimenti (parti, minori, professionisti anonimizzati), nemmeno per deduzione da fatti o da altre fonti.

## Report (`report.md`, radice della cartella)
Parti dalla bozza corretta dopo il red team e crealo una sola volta. In cima: eventuali scelte prudenti prese per le regole di arresto e le avvertenze (controlli manuali, schede senza testo integrale). In fondo: sezione **Esito del red teaming** (rilievi, gravità, correzioni applicate o non applicate). Elenca i file scaricati e dove sono (`pdf/`), contando solo quelli arrivati davvero. Il messaggio finale all'utente è di tre righe.
