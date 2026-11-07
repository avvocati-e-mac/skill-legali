# Verifica delle norme

## a) Identificazione
- Fonte esatta: codice, legge, d.lgs., d.P.R., r.d., regolamento UE. Numero dell'articolo, comma, lettera.
- **Commi**: molte banche dati ufficiali presentano l'articolo come testo continuo, senza numerare i commi. Conta i commi sul testo ufficiale. Se l'atto cita un «secondo comma» che non esiste (IA16), è un errore; se il comma esiste ma il contenuto è nel primo, è un errore di comma.
- Allegati: alcuni codici sono allegati a un atto normativo (il c.p.c. è l'allegato 1 del R.D. 1443/1940, il c.c. è nel R.D. 262/1942 con la sua struttura). Un URN senza l'allegato può puntare all'atto sbagliato.

## b) Link
- Se l'atto ha un link (Normattiva, EUR-Lex), verifica che punti all'articolo giusto. Un permalink può rispondere anche a un URN sbagliato.
- Se manca e l'utente vuole i link, costruiscili con lo strumento delle norme e verificali.
- Un URN con una data di vigenza fissa (es. `!vig=AAAA-MM-GG`) mostra un testo storico: usalo solo se serve davvero quella versione.

## c) Vigenza
- **Vigenza attuale**: l'articolo è vigente, modificato o abrogato? Indica la data dell'abrogazione o della modifica.
- **Ratione temporis**: quale testo si applica ai fatti o al rapporto (data del contratto, dei fatti, della domanda)? Le riforme processuali hanno discipline transitorie: verificale (es. d.lgs. 149/2022).
- Le declaratorie di illegittimità costituzionale vanno lette insieme al testo.

## d) Pertinenza del contenuto
- Leggi l'articolo e chiediti: dice davvero ciò per cui è citato? Errore frequente (IA17): norma citata per un contenuto che non ha. Esempio reale: una norma sull'esecuzione personale dell'incarico citata per la «competenza specialistica».
- **Applicabilità al soggetto**: verifica che la norma si applichi alla figura in questione. Esempio reale: i termini di una garanzia del contratto d'opera manuale sono stati dichiarati dalle Sezioni Unite inapplicabili al professionista intellettuale (IA19). Una ricerca mirata «articolo + figura + Sezioni Unite» lo fa emergere.
- Coerenza interna dell'atto: la stessa norma non può essere invocata in un punto e smentita, implicitamente, in un altro.

## e) Esiti
Usa i verdetti di `allucinazioni-ia.md`, adattati:
- VERIFICATA;
- ESTREMI DA CORREGGERE: articolo, comma, fonte o link;
- ESISTE MA NON DICE CIÒ: norma non pertinente o inapplicabile;
- NON VIGENTE / NON APPLICABILE RATIONE TEMPORIS;
- NON REPERITA: limite dello strumento.

Nel report, la tabella delle norme ha queste colonne: citazione nell'atto · testo/URN verificato · vigenza · pertinenza · azione.
