---
name: migliora-chiarezza-testi-legali
description: >
  Rende più chiari atti giudiziari, pareri, diffide e contratti in italiano
  senza cambiarne il significato giuridico e senza perdere il registro
  forense. Due percorsi: atti e pareri (deep issue, frase tematica, niente
  enfasi, D.M. 110/2023) e contratti (un verbo per ogni funzione, definizioni,
  e/o, eccezioni, elenchi). Vieta di aggiungere fatti, date, esimenti,
  intensificatori e frasi tipiche dell'IA; consegna coppie PRIMA/DOPO, testo
  riscritto integrale e sommario. MANDATORY TRIGGERS: revisione o riscrittura
  di un contratto, di una clausola, di un parere, di una diffida o di un atto
  giudiziario (citazione, comparsa, memoria, appello, ricorso) quando
  l'obiettivo, anche implicito, è chiarezza, leggibilità, sintesi o minore
  ambiguità. Non usarla per redigere un atto da zero, per un memo interno o
  per cercare norme e sentenze.
---

# Migliora chiarezza testi legali

Obiettivo: rendere il testo chiaro e scorrevole per chi deve leggerlo e
applicarlo (giudice, controparte, cliente) senza cambiarne il significato
giuridico. Il registro resta forense: si tolgono oscurità e ridondanza, non
la tecnica.

## 1. Quale file aprire

| Testo | Apri |
|---|---|
| Atto giudiziario, memoria, ricorso, appello, parere, diffida | `references/atti-e-pareri.md` |
| Contratto o clausola | `references/contratti.md` |
| Clausola che si presta a più letture | anche `references/interpretazione-civilistica.md` |
| Richiesta esplicita di fonti, di Manzoni o dell'elenco dei tic da IA | `references/bibliografia.md`, `references/lezione-manzoni.md`, `references/frasi-da-ia.md` |

Apri al massimo due file per richiesta. Se non puoi leggere file, bastano le
regole di questa pagina.

## 2. Procedura

<!-- step:inizio -->
1. **Scheda**, prima di riscrivere, in 3-5 righe: tipo di testo; chi scrive
   e a chi (chi è "nostro", chi è "Vostro"); elementi che non devono
   cambiare: soggetti, obblighi, garanzie, eccezioni, condizioni, date,
   importi, termini tecnici. Se chi scrive o il destinatario non si ricavano
   dal testo, scrivi "[da confermare]": non indovinare.
<!-- step:fine -->
2. **Diagnosi**: trova i punti oscuri con le regole della sezione 4 e del file
   di genere.
3. **Riscrittura**: per ogni punto scrivi un blocco con questa forma:

   PRIMA: il testo originale
   DOPO: il testo riscritto
   Motivo: una riga concreta sul perché

4. **Testi lunghi** (più di una pagina): tratta la prima sezione, oppure le
   cinque criticità più importanti, poi chiedi se continuare. Se l'utente ha
   già chiesto di procedere con tutto, o risponde "tutto", vai fino in fondo
   senza fermarti.
5. **Chiusura**: scrivi `TESTO RISCRITTO:` con il testo integrale pronto da
   incollare, poi `Sommario:` in 3-5 righe con le modifiche principali e le
   decisioni lasciate all'avvocato. Se il testo è una sola frase o clausola,
   il DOPO basta: ometti il TESTO RISCRITTO.
<!-- step:inizio -->
6. **Controllo**: prima di consegnare, confronta ogni DOPO con la Scheda. Se
   puoi eseguire codice, lancia `scripts/controlla_invarianti.py` (istruzioni
   in testa al file) e correggi ciò che segnala. Altrimenti ripassa uno per
   uno gli otto divieti della sezione 3 e correggi. Chiudi con una riga
   `Controllo:` con l'esito: "nessuna violazione" oppure che cosa hai
   corretto.
<!-- step:fine -->

## 3. Otto divieti (valgono per il DOPO e per il TESTO RISCRITTO)

1. Non aggiungere fatti, date, importi, termini, esiti, condizioni o
   esimenti ("caso fortuito", "forza maggiore", "invano", "senza
   riscontro"). Se un'aggiunta migliorerebbe il testo, proponila nel Motivo
   con `PROPOSTA:` oppure lascia nel DOPO un segnaposto `[da decidere: ...]`
   senza valori.
2. Non cambiare le persone: chi è "nostro" resta nostro, chi è "Vostro"
   resta Vostro. Non attribuire ruoli (ricorrente, locatore, conduttore) che
   il testo non dà.
3. Non cambiare la natura giuridica: una garanzia resta garanzia
   ("garantisce"), un'eccezione resta eccezione ("salvo"), "a pena di" resta.
   Non trasformare mai "si obbliga a vendere, trasferire o cedere" in "vende,
   trasferisce o cede", né il contrario: il primo crea un obbligo, il secondo
   trasferisce il diritto.
4. Non aggiungere intensificatori ("interamente", "palesemente", "del
   tutto", "gravissimo", "esclusivamente" usato come rafforzativo).
5. Non sostituire i termini tecnici: prescrizione, decadenza, recesso,
   risoluzione, caparra, penale, diritto azionato, legittimazione restano.
6. Non cambiare il contenuto di conclusioni, domande ed eccezioni
   processuali: puoi cambiarne solo la forma.
7. Non aggiungere frasi da IA né commenti dentro il testo: "è importante
   sottolineare", "gioca un ruolo cruciale", "non solo... ma anche" di
   maniera, gerundi di commento in coda ("..., evidenziando"), triadi di
   comodo, chiusure riassuntive ("In conclusione"), frasi sulla riscrittura
   o su di te ("versione più chiara", "spero sia utile"), la lineetta lunga.
8. Non citare norme o sentenze che il testo non cita. Se il testo è già
   chiaro, rispondi "Nessuna modifica necessaria" e spiega perché in una riga.

## 4. Regole comuni

- **Un concetto, una parola**: scegli un termine e usalo sempre, senza
  sinonimi.
- **Un'idea per frase, poi ricuci**: dopo aver diviso, rileggi. Se due frasi
  brevi sono legate da una causa, un'opposizione o una conseguenza, uniscile
  con un connettivo (poiché, quindi, tuttavia, infatti, ma). Il testo deve
  essere chiaro e scorrevole, non a singhiozzo.
- **Periodo lungo solo se articolato**: va bene se è diviso da punti e
  virgola in parti complete, ciascuna con soggetto e verbo.
- **Chi agisce si vede**: usa la forma attiva quando la passiva nasconde chi
  decide o chi deve fare.
- **Condizioni ed eccezioni accanto a ciò che modificano**; elementi dello
  stesso tipo nella stessa forma.
- **Via la zavorra**: doppiette ("nullo e privo di effetto"), formule vuote
  ("si fa presente che", "in ordine a quanto
  dedotto"), arcaismi ("codesto", "trattasi", "ut supra", "all'uopo").
- **Tecnicismi sì, gergo di comodo no**: il latinismo rivolto al cliente si
  traduce accanto.
- **Informazione decisiva in fondo**: chiudi la frase su ciò che conta, non
  su "ai sensi di legge" o "di cui sopra".
- **Se le regole confliggono** vale quest'ordine: fedeltà giuridica, divieti,
  chiarezza, scorrevolezza, brevità.

## 5. Esempi

Contratto:
PRIMA: "Resta inteso che l'Appaltatore dovrà provvedere alla consegna delle
opere entro il termine di cui all'art. 4 e/o comunque entro la data che verrà
eventualmente comunicata dal Committente."
DOPO: "L'Appaltatore consegna le opere entro il termine dell'art. 4 oppure,
se il Committente comunica una data diversa, entro quella data [da decidere:
se la data comunicata può anticipare il termine dell'art. 4]."
Motivo: "dovrà provvedere alla consegna" diventa "consegna"; "e/o comunque"
non dice quale termine prevale, quindi la scelta resta all'avvocato.

Atto:
PRIMA: "Giova evidenziare come l'odierna esponente abbia, sin dalla missiva
del 3 marzo 2025, palesato la propria contrarietà alla proroga, con ciò
manifestando in maniera inequivocabile la volontà di non rinnovare."
DOPO: "Già con la lettera del 3 marzo 2025 l'esponente si è opposta alla proroga:
ha così manifestato in modo inequivocabile la volontà di non rinnovare."
Motivo: via la formula vuota e l'arcaismo; soggetto e verbo in apertura; il
nesso tra i due fatti è reso esplicito.

## 6. Ambienti diversi

In Claude (Desktop, Cowork, Code) e in Codex leggi i file e lancia lo script
con gli strumenti disponibili. Senza accesso ai file o senza esecuzione di
codice usa solo questa pagina: non inventare strumenti che non hai.
