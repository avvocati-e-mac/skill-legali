# Controllare i link prima dell'invio

Usa `scripts/verifica_link.py` solo quando hai già una bozza Markdown e le
risposte originali BuddaLaw in file JSON, forniti dall'utente oppure salvati
dal runtime MCP. Verifica il percorso restituito dal tool e leggi il file:
un file arbitrario, un esempio o una ricostruzione dell'assistente non provano
la provenienza della fonte. Non creare un elenco di URL dalla memoria per
far passare il controllo.

Con shell e Python disponibili, esegui il comando diretto, usando percorsi
assoluti e racchiudendoli fra virgolette quando serve:

```text
python3 <cartella-skill>/scripts/verifica_link.py --bozza /percorso/bozza.md --fonte /percorso/risposta-mcp.json
```

Per più risposte aggiungi un altro `--fonte /percorso/risposta.json`. Lo script
legge i file senza modificarli, senza rete, installazioni o credenziali.
Confronta gli URL della bozza soltanto con i campi `public_url`: non accetta
URL trovati nel testo di una sentenza, nella sintesi o nei campi normativi.

- Codice 0: URL riscontrati nei file e collegamenti Markdown completi.
- Codice 1: URL non riscontrato o collegamento incompleto. Torna alla fonte
  e correggi la bozza; non ricostruire l'URL a partire da quello sbagliato.
- Codice 2: dati insufficienti o file non leggibili; confronto non verificabile.

Controlla la stessa bozza che invierai: modifiche successive, anche minime,
richiedono un nuovo confronto. `bozza_sha256` identifica il file controllato;
non assicura che il messaggio inviato dall'assistente sia rimasto identico.

Il controllo **non verifica** gli estremi accostati al link, la pertinenza,
i virgolettati o l'autenticità del file. Anche una bozza senza citazioni non
supera il controllo. Eventuali link prodotti da un'altra skill richiedono
una verifica separata e possono risultare non riscontrati in queste fonti.

Senza i file originali, shell o Python, resta il confronto manuale con il
risultato letto. Non sostituire il controllo con altri comandi, richieste HTTP
o dichiarazioni di verifica automatica. La skill non impone un blocco tecnico
all'invio di una risposta sbagliata.
