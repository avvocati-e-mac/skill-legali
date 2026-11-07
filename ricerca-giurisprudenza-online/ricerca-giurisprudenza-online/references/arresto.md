# Regola di arresto

Fermati e fai all'utente UNA domanda, con 2-3 opzioni, se si verifica una di queste condizioni:

a) il sito richiede login, SPID o captcha;
b) WebFetch rifiuta le pagine e nessun browser è disponibile o connesso (o il sito ha bisogno del browser e questo manca);
c) un subagente ha usato 5 chiamate senza aprire alcun provvedimento;
d) i risultati pertinenti potenziali superano 200 (proponi come restringere: periodo, ufficio, parole chiave);
e) un file atteso manca o è vuoto anche dopo un secondo tentativo.

## Come si fa
- Spiega in una frase che cosa è successo, poi le opzioni numerate, con quella prudente indicata per prima.
- Se l'utente non risponde, scegli l'opzione più prudente, annotala in cima al report e prosegui.
- Per login, SPID e captcha: non tentare di aggirarli e non digitare mai credenziali. Se l'utente vuole procedere, accede lui nel browser e tu continui da lì.
- Contenuti riservati o in abbonamento visibili perché l'utente è già collegato nel suo Chrome: fermati e chiedi; procedi solo con il suo sì esplicito per quel sito, e comunque senza scaricamenti in massa dal browser.
- Robots: decide il `robots.txt` del sito (regola in `ambienti.md`, sezione 3). Se vieta il percorso, non usare nessuno strumento per ottenere quelle pagine. Se lo permette ma WebFetch rifiuta, puoi leggere nel browser.

## Opzioni tipiche
- (a) accedo io nel browser e poi continui | cambiamo sito o fonte | ci fermiamo.
- (b) secondo l'ambiente: apri la sessione dall'app desktop di Claude con il browser integrato attivo, oppure (Claude Code) attiva o ricollega l'estensione Claude in Chrome, oppure (Codex) configura uno strumento browser | uso solo le pagine raggiungibili senza browser | ci fermiamo.
- (c) restringo o cambio le interrogazioni | provo con un altro metodo di lettura | ci fermiamo.
- (d) restringo per periodo | restringo per ufficio o sezione | leggo comunque i primi N per pertinenza.
- (e) riprovo con un altro metodo | segno il provvedimento come non letto e proseguo.
