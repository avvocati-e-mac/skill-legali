# Errori tipici degli atti scritti con IA, verdetti e gravità

## Perché serve
Un modello linguistico non «ricorda» le sentenze: genera testo plausibile. Per questo i suoi errori non sono casuali. Producono citazioni che hanno la forma giusta e il contenuto sbagliato, e superano un controllo superficiale. Il verificatore (anche tu) ha gli stessi bias del generatore: tende a trovare plausibile ciò che è plausibile. L'unico rimedio è **trovare il passo nella fonte**.

## Tipologia: che cosa cercare

| Codice | Errore | Come si scopre |
|---|---|---|
| IA1 | **Pronuncia inventata**: nessuna decisione con quegli estremi | Ricerca per estremi negativa su più fonti, o il numero appartiene a un'altra decisione (vedi IA2) |
| IA2 | **Chimera**: numero vero con un contenuto diverso; oppure numero di una pronuncia e data o sezione di un'altra | Regola delle tre chiavi (sotto) |
| IA3 | Sezione, data, tipo (sent./ord.) o Rv **errati** | Confronto con l'intestazione ufficiale |
| IA4 | **Rv inventato** o di un'altra massima della stessa pronuncia | Lettura della massima con quel Rv |
| IA5 | **Virgolettato plausibile ma inesistente** | `confronta_verbatim.py` → ASSENTE sul testo integrale |
| IA6 | **Virgolettato ritoccato**: parole sostituite, aggiunte o tagliate, ellissi che nascondono un «salvo che» | `confronta_verbatim.py` → VARIANTE |
| IA7 | Frase **vera ma attribuita alla pronuncia sbagliata** (spesso è un'altra della stessa serie o dello stesso relatore) | La frase c'è altrove, non lì |
| IA8 | **Massima o riassunto spacciati per testo**: si cita tra virgolette la massima come se fosse la motivazione | La frase coincide con la massima ma non con il testo |
| IA9 | **Principio rovesciato o esteso**: la fonte dice «salvo che», «solo se», «per i materiali», e l'atto generalizza | Lettura del periodo intero |
| IA10 | **Motivazione del giudice inferiore** presentata come principio della Corte | Il testo dice «la sentenza impugnata ha…», «la Corte d'appello ha ritenuto…» |
| IA11 | **Inciso o rinvio** (parentesi con «cfr.») presentato come ratio | Posizione nel periodo e funzione |
| IA12 | **Pronuncia favorevole solo in apparenza**: esito contrario, o principi contrari nello stesso paragrafo | Dispositivo ed esito del motivo; ricerca dei passi contrari |
| IA13 | **Soggetto diverso**: il principio riguarda il venditore e non il DL, l'appaltatore e non il professionista | Lettura della fattispecie |
| IA14 | **«Costante giurisprudenza»** o «è pacifico» senza alcuna fonte | Inventario: affermazione da sostenere |
| IA15 | **Catene riempitive** «conf.», «v. anche», «nello stesso senso» con pronunce non pertinenti o contrarie | Verifica di ogni anello, non solo del primo |
| IA16 | **Norma o comma inesistente**, numerazione dei commi inventata | Testo ufficiale dell'articolo |
| IA17 | **Norma non pertinente** al contenuto che le si attribuisce | Lettura dell'articolo |
| IA18 | **Norma abrogata, modificata o non applicabile ratione temporis** | Vigenza alla data dei fatti e alla data attuale |
| IA19 | **Norma contraria a un orientamento consolidato o alle Sezioni Unite** (es. un termine di decadenza che le SU escludono) | Ricerca mirata «norma + soggetto + SU» |
| IA20 | **Documento di causa citato male**: pagina, numero di documento, frase del perito | Lettura del documento nella cartella del fascicolo |

## Regola delle tre chiavi (identità della pronuncia)
1. **Numero e anno**: la pronuncia esiste?
2. **Sezione, data, tipo**: coincidono con l'intestazione ufficiale?
3. **Materia e oggetto**: la fattispecie e il tema sono coerenti con il principio per cui la si cita?

Esiti:
- se la chiave 1 regge ma la 3 no, è una **chimera** (IA2) finché non si prova il contrario;
- se la chiave 2 non torna ma le altre sì, è un estremo da correggere (IA3).

## Verdetti (scala unica)

| Verdetto | Quando usarlo |
|---|---|
| **VERIFICATA** | Estremi corretti, verbatim IDENTICO al testo (o alla massima, dichiarandolo), principio pertinente |
| **ESTREMI DA CORREGGERE** | Pronuncia giusta, ma sezione, data, tipo, numero o Rv errati |
| **VERBATIM ALTERATO** | La frase c'è, ma con differenze (VARIANTE), oppure è la massima citata come testo |
| **ESISTE MA NON DICE CIÒ** | La pronuncia esiste, ma il principio è diverso, è rovesciato, è una motivazione riferita, un inciso, riguarda un altro soggetto o è contrario |
| **NON REPERITA** | Nessun riscontro con gli strumenti usati. È un **limite dello strumento**, non un giudizio sulla pronuncia. Indica dove hai cercato |
| **INESISTENTE** | Solo con **prova positiva**: (a) il numero e l'anno corrispondono a un'altra decisione, e nessuna con quegli estremi tratta il tema; oppure (b) ricerca negativa su almeno **due fonti indipendenti, di cui una ufficiale**, per estremi e per frase |
| **AFFERMAZIONE DA SOSTENERE** | Asserzione giurisprudenziale senza fonte (IA14) |
| **NON VERIFICABILE** | Dottrina o fonti fuori dagli strumenti scelti: dichiaralo, senza giudizio |

### Casi di confine
- **Frase vera, pronuncia sbagliata (IA7).**
  - Se il principio è lo stesso e cambia solo la fonte: ESTREMI DA CORREGGERE (attribuzione). Nella scheda indica la pronuncia giusta.
  - Se la frase è stata anche ritoccata o «stirata» (es. «anche» diventato «solo se»): VERBATIM ALTERATO.
- **Inciso omesso senza ellissi.** VERBATIM ALTERATO. `confronta_verbatim.py` lo segnala come «inciso omesso». Un ASSENTE con somiglianza intorno a 0,6 merita comunque una lettura: può essere una frase presente con un inciso tolto.
- **Massima citata come testo.** VERBATIM ALTERATO, gravità FORMALE se la massima è fedele al principio, GRAVE se lo stringe o lo allarga.

Perché tanta cautela su «inesistente»: dire a un avvocato che una sentenza non esiste quando esiste lo porta a togliere un argomento valido e a non fidarsi più del controllo. Una banca dati non indicizza tutto; un archivio di massime contiene solo le massimate.

## Gravità

| Gravità | Criterio | Esempi |
|---|---|---|
| **BLOCCANTE** | Se la controparte o il giudice lo scoprono, l'atto perde credibilità o un argomento crolla | Pronuncia inesistente o chimera; verbatim inventato; principio rovesciato; norma inapplicabile secondo le SU; pronuncia citata a favore ma contraria |
| **GRAVE** | Errore visibile che indebolisce un argomento | Sezione o data errate; virgolettato ritoccato; massima citata come testo; precedente non pertinente nella catena |
| **FORMALE** | Non cambia il senso | Refusi negli estremi, spazi, corsivi, link mancanti o non aggiornati |

**Regola di aumento.** Se la citazione è **decisiva**, cioè regge da sola un motivo, un'eccezione o una conclusione, la gravità sale di un livello: FORMALE diventa GRAVE, GRAVE diventa BLOCCANTE. Scrivi nella scheda perché è decisiva. La gravità di base è quella della tabella sopra; l'aumento va motivato.

Il report si apre sempre con i bloccanti.
