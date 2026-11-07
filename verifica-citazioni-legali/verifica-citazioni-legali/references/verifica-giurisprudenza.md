# Verifica della giurisprudenza

I livelli si applicano in ordine. In modalità *rapida* fermati al livello b; in modalità *completa* li fai tutti. Per verdetti e gravità vedi `allucinazioni-ia.md`.

## a) Esistenza ed estremi
- Cerca **per estremi** (numero, anno, organo) nello strumento scelto per la categoria. Annota l'identificativo univoco (ECLI, Rv, id della banca dati, R.G. per il merito).
- Applica le **tre chiavi**: numero e anno; sezione, data, tipo; materia coerente.
- **Data**: nelle citazioni italiane di solito è la data di deposito o di pubblicazione. Se l'atto indica la data della decisione (camera di consiglio), segnalalo come formale.
- **Sezione**: verificala sull'intestazione o sulla formula di chiusura («nella camera di consiglio della Seconda Sezione civile»). Le citazioni interne di altre pronunce («Sez. 2, Ordinanza n. …») sono un buon riscontro incrociato.
- Se la ricerca dà zero: prova con forme diverse (numero con zeri iniziali, anno, tipo). Prova un altro archivio, ricordando che un archivio di massime contiene solo le pronunce massimate. Il verdetto resta NON REPERITA finché non c'è prova positiva.

## b) Verbatim
- Ottieni il **testo integrale**: testo digitale, oppure OCR dichiarato. Se hai solo la massima, dillo, e il verdetto massimo diventa «verificata sulla massima».
- Salva il testo in un file nella cartella di lavoro (`fonti/<numero>_<anno>.txt`):
  - se lo strumento dà un PDF, usa `pdftotext`;
  - se restituisce il testo nella risposta, scrivilo su file con lo strumento di scrittura, per intero o almeno le sezioni pertinenti, dichiarandolo;
  - se la risposta è troppo lunga e il sistema la salva in un file temporaneo, copia quel file.

  Poi esegui:
  `python3 <skill>/scripts/confronta_verbatim.py --fonte <testo> --citazione "<virgolettato>"`
  oppure `--lotto` per più frasi.
- Interpreta gli esiti:
  - IDENTICA: ok;
  - VARIANTE: riporta il diff, e valuta se cambia il senso (gravità);
  - ASSENTE: cerca la frase nella massima e nelle pronunce citate nel testo (IA7, IA8).
- **Ellissi**: lo script controlla i segmenti in ordine. Leggi tu che cosa c'era nella parte omessa: un «salvo che» tagliato cambia il principio.
- **OCR**: una VARIANTE di una o due lettere («ed m quanto») può essere un errore di riconoscimento. Riscontrala sull'immagine prima di decidere.
- Frase senza virgolette ma attribuita («la Corte ha affermato che…»): verifica che la parafrasi sia fedele (livello d).

## c) Natura del passo
Classifica il passo citato:
- **ratio decidendi**: sorregge la decisione sul motivo;
- **principio di diritto** enunciato (art. 384 c.p.c.);
- **obiter dictum**;
- **richiamo** di precedenti, spesso tra parentesi con «cfr.», o massima ripetuta;
- **motivazione del giudice inferiore riferita** («la sentenza impugnata ha…»);
- **argomento della parte** riportato («deducono i ricorrenti che…»).

Solo i primi due sono «ciò che la Corte ha affermato». Gli altri si possono citare, ma dicendo che cosa sono.

## d) Esito e pertinenza
- Leggi il **dispositivo** e l'esito del **motivo** su cui verte il passo: accolto, rigettato, inammissibile, assorbito. «La Corte ha respinto il motivo» va verificato motivo per motivo; la sentenza può essere cassata per altro.
- **Fattispecie**: il soggetto (DL o appaltatore, venditore o costruttore, P.A.), il tipo di contratto e la materia sono gli stessi del caso dell'atto?
- **Pertinenza**: la pronuncia sostiene proprio la proposizione per cui è citata? Se la sostiene solo in parte, scrivi esattamente in che parte.

## e) Passi contrari (modalità completa)
- Nella stessa pronuncia cerca frasi che la controparte userebbe: affermazioni della regola opposta, eccezioni, esito sfavorevole al soggetto nella posizione del cliente.
- Ogni pronuncia citata a favore riceve una nota «uso con cautela» se contiene passi contrari rilevanti.

## f) Validità nel tempo (modalità completa)
- Il precedente è stato **superato**? Cerca:
  - Sezioni Unite successive sullo stesso punto;
  - massime successive conformi o difformi, se lo strumento le offre;
  - dichiarazioni di illegittimità costituzionale della norma applicata;
  - riforme legislative che ne hanno cambiato la base.
- Se lo strumento non lo permette, scrivi: «superamento non verificabile con questo strumento».

## Merito e Corte costituzionale
- **Merito**: gli estremi sono ufficio, tipo, R.G. con anno e data. Un solo provvedimento non è un orientamento: dillo. Verifica anche la **ratio**. Un'inammissibilità ex art. 696-bis per difetto di attitudine conciliativa, per esempio, non è un'inammissibilità per difetto di rilevanza.
- **Corte costituzionale**: cita la sentenza o l'ordinanza, la data di deposito e il punto del *Considerato in diritto*. Il testo ufficiale è sul sito della Corte.
- **CGUE e Corte EDU**: numero di causa, data, ECLI, punto (paragrafo).

## Pronunce citate «per catena»
Ogni elemento di «conf.», «v. anche» o «nello stesso senso» è una citazione autonoma con il suo verdetto. Spesso solo il primo anello è pertinente (IA15).
