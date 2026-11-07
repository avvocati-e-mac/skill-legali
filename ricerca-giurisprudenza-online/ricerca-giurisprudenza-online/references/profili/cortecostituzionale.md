# Profilo: cortecostituzionale.it - CON BLOCCO (captcha) - ricognizione 2026-11-07

Tipo di sito: pubblico

BLOCCO: le pagine delle pronunce (actionSchedaPronuncia.do e documenti/download/...) mostrano un captcha Radware ("sembri un bot"). Non aggirarlo mai (ne cambiando user-agent ne risolvendo il captcha). robots.txt inesistente (404).

## Cosa fare
- Proponi all'utente di aprire la pagina nel browser e risolvere LUI il captcha; poi la skill prosegue un provvedimento alla volta (come per i login).
- In alternativa: l'utente passa i testi gia scaricati, oppure si usa un'altra fonte.

## Campi
- Pagina d'ingresso: www.cortecostituzionale.it
- Come si cerca: WebSearch con allowed_domains ["cortecostituzionale.it"]; URL actionPronuncia.do?anno=&numero= (da terminale restituisce solo la home con i menu, non la pronuncia).
- URL della scheda e del file: da verificare (dopo il captcha risolto dall'utente)
- Formato: da verificare
- Strumento che funziona: curl NO (captcha). Browser con captcha risolto dall'utente: da verificare.
- id consigliato: cost-<anno>-<numero>
- Provvedimento di prova: nessuno letto.
