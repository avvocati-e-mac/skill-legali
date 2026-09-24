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

Obiettivo: testo chiaro e scorrevole per chi deve applicarlo (giudice,
controparte, cliente), con lo stesso significato giuridico. Il registro resta
forense: si tolgono oscurità e ridondanza, non la tecnica.

## 1. Quale file aprire

| Testo | Apri |
|---|---|
| Atto giudiziario, memoria, ricorso, appello, parere, diffida | `references/atti-e-pareri.md` |
| Contratto o clausola | `references/contratti.md` |
| Clausola che si presta a più letture | anche `references/interpretazione-civilistica.md` |
| Richiesta esplicita di fonti, di Manzoni o dell'elenco dei tic da IA | `references/bibliografia.md`, `references/lezione-manzoni.md`, `references/frasi-da-ia.md` |

Apri al massimo due file. Senza file bastano le regole di questa pagina.

## 2. Procedura

1. **Serve davvero?** Una frase breve, tecnica e già chiara non si tocca:
   rispondi "Nessuna modifica necessaria" e spiega perché in una riga.
2. **Chi scrive a chi**: ricavalo dal testo o dal contesto (chi è "nostro",
   chi è "Vostro"). Se non si ricava, scrivi "[da confermare]": non
   indovinare.
3. **Riscrittura**: per ogni punto oscuro (regole della sezione 4 e del file
   di genere) scrivi un blocco con questa forma, senza una diagnosi a parte:

   PRIMA: il testo originale
   DOPO: il testo riscritto
   Motivo: una riga concreta sul perché

4. **Testi lunghi** (più di una pagina): tratta la prima sezione, oppure le
   cinque criticità principali, poi chiedi se continuare. Se l'utente ha già
   chiesto di procedere con tutto, o risponde "tutto", vai fino in fondo.
5. **Chiusura**: scrivi `TESTO RISCRITTO:` con il testo integrale pronto da
   incollare, poi `Sommario:` in 3-5 righe con le modifiche principali e le
   decisioni lasciate all'avvocato. Se il testo è una sola frase o clausola,
   il DOPO basta: ometti il TESTO RISCRITTO.
6. **Verifica**: se puoi eseguire codice, lancia
   `scripts/controlla_invarianti.py` e correggi ciò che segnala. Altrimenti
   rileggi ogni DOPO contro gli otto divieti prima di consegnare.

## 3. Otto divieti (valgono per il DOPO e per il TESTO RISCRITTO)

1. Non aggiungere fatti, date, importi, termini, esiti, condizioni o
   esimenti ("caso fortuito", "forza maggiore", "invano", "senza
   riscontro", "con il consenso scritto"). Se un'aggiunta migliorerebbe il testo, proponila nel Motivo
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
5. Non togliere né sostituire date, importi, numeri di atti e termini
   tecnici: prescrizione, decadenza, recesso, risoluzione, caparra, penale,
   diritto azionato, legittimazione, travisamento restano. Una data può
   cambiare forma ("1/3/2024" diventa "1° marzo 2024"), non valore.
6. Non cambiare il contenuto di conclusioni, domande ed eccezioni
   processuali: puoi cambiarne solo la forma.
7. Non aggiungere frasi da IA né commenti dentro il testo: "è importante
   sottolineare", "gioca un ruolo cruciale", "non solo... ma anche" di
   maniera, gerundi di commento in coda ("..., evidenziando"), triadi di
   comodo, chiusure riassuntive ("In conclusione"), frasi sulla riscrittura
   o su di te ("versione più chiara", "spero sia utile"), la lineetta lunga.
8. Non citare norme o sentenze che il testo non cita, né completarne gli
   estremi. Se il testo è già chiaro, non riscriverlo (passo 1).

## 4. Regole comuni

- **Un concetto, una parola**: scegli un termine e usalo sempre, senza
  sinonimi.
- **Un'idea per frase, poi ricuci**: dopo aver diviso, rileggi. Se due frasi
  brevi sono legate da una causa, un'opposizione o una conseguenza, uniscile
  con un connettivo (poiché, quindi, tuttavia, infatti, ma). Il testo deve
  essere chiaro e scorrevole, non a singhiozzo.
- **Periodo lungo solo se articolato** in parti complete, separate da punti e
  virgola, ciascuna con soggetto e verbo.
- **Chi agisce si vede**: usa la forma attiva quando la passiva nasconde chi
  decide o chi deve fare.
- **Condizioni ed eccezioni accanto a ciò che modificano**; elementi dello
  stesso tipo nella stessa forma.
- **Via la zavorra**: doppiette ("nullo e privo di effetto"), formule vuote
  ("si fa presente che", "in ordine a quanto
  dedotto"), arcaismi e formule di stile ("codesto", "trattasi", "ut supra", "all'uopo",
  "come sopra rappresentato e difeso").
- **Tecnicismi sì, gergo no**: il latinismo per il cliente si traduce accanto.
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
Motivo: "dovrà provvedere alla consegna" diventa "consegna"; "e/o" non dice
quale termine prevale: decide l'avvocato.

Atto:
PRIMA: "Giova evidenziare come l'odierna esponente abbia, sin dalla missiva
del 3 marzo 2025, palesato la propria contrarietà alla proroga, con ciò
manifestando in maniera inequivocabile la volontà di non rinnovare."
DOPO: "Già con la lettera del 3 marzo 2025 l'esponente si è opposta alla proroga:
ha così manifestato in modo inequivocabile la volontà di non rinnovare."
Motivo: via formula vuota e arcaismo; soggetto e verbo in apertura; nesso
esplicito.

## 6. Ambienti diversi

In Claude (Desktop, Cowork, Code) e in Codex usa gli strumenti disponibili
per leggere i file e lanciare lo script. Senza di essi usa solo questa
pagina: non inventare strumenti.
