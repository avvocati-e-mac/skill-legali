# Regola di arresto

Fermati e fai all'utente UNA domanda, con 2-3 opzioni, se si verifica una di queste condizioni:

a) il sito richiede login, SPID o captcha, o mostra un blocco anti-robot;
b) WebFetch rifiuta le pagine e nessun browser è disponibile o connesso (o il sito ha bisogno del browser e questo manca);
c) un subagente ha usato 5 chiamate senza aprire alcun provvedimento;
d) i risultati pertinenti potenziali superano 200 (proponi come restringere: periodo, ufficio, parole chiave);
e) un file atteso manca o è vuoto anche dopo un secondo tentativo;
f) sito PRIVATO con `robots.txt` che vieta il percorso e termini d'uso che vietano l'uso automatico.

## Come si fa
- Spiega in una frase che cosa è successo, poi le opzioni numerate, con quella prudente indicata per prima.
- Se l'utente non risponde, scegli l'opzione più prudente, annotala in cima al report e prosegui.
- Per login, SPID e captcha: non tentare di aggirarli e non digitare mai credenziali. Se l'utente vuole procedere, accede lui nel browser e tu continui da lì.
- Contenuti riservati o in abbonamento visibili perché l'utente è già collegato nel suo Chrome: fermati e chiedi; procedi solo con il suo sì esplicito per quel sito, e comunque senza scaricamenti in massa dal browser.
- Robots (regola in `ambienti.md`, sezione 3): sui siti pubblici e istituzionali la lettura mirata è sempre ammessa, anche se `robots.txt` vieta il percorso, e va dichiarata nei limiti del report; sui siti privati, se `robots.txt` vieta il percorso e i termini d'uso vietano l'uso automatico, è arresto (f). Lo scaricamento automatico rispetta sempre `robots.txt`: se vieta, il report elenca i link da aprire a mano.
- Blocchi anti-robot (403 Akamai, sfide JavaScript, captcha Radware): mai aggirarli, né cambiando user-agent né risolvendo il captcha. Se compare un captcha nel browser lo risolve l'utente, poi si prosegue un provvedimento alla volta.

## Opzioni tipiche
- (a) accedo io nel browser e poi continui | cambiamo sito o fonte | ci fermiamo.
- (b) secondo l'ambiente: apri la sessione dall'app desktop di Claude con il browser integrato attivo, oppure (Claude Code) attiva o ricollega l'estensione Claude in Chrome, oppure (Codex) configura uno strumento browser | uso solo le pagine raggiungibili senza browser | ci fermiamo.
- (c) restringo o cambio le interrogazioni | provo con un altro metodo di lettura | ci fermiamo.
- (d) restringo per periodo | restringo per ufficio o sezione | leggo comunque i primi N per pertinenza.
- (f) cambiamo fonte | leggo solo ciò che l'utente mi passa | ci fermiamo.
- (e) riprovo con un altro metodo | segno il provvedimento come non letto e proseguo.
