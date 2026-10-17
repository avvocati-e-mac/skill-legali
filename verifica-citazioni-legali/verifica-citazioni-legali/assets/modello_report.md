# Verifica delle citazioni — <titolo dell'atto>

<data> · modalità <rapida|completa> · skill verifica-citazioni-legali · strumenti: <elenco>

## Esito in breve
- **<N> bloccanti** · **<N> gravi** · <N> formali · <N> non verificabili · <N> verificate senza rilievi (su <TOT> citazioni esaminate; se l'ambito è ristretto: «<M> voci dell'inventario fuori ambito»).
- Rischio: <una frase. Es.: «Due citazioni reggono un motivo e vanno sostituite prima del deposito: una norma che le Sezioni Unite escludono per il direttore dei lavori e un principio attribuito alla Cassazione che è della corte d'appello».>
- **Ancora da controllare prima del deposito**: <che cosa e perché, in una riga. Es.: «dottrina (nessuno strumento); 1 sentenza non reperita (archivio incompleto); 15 voci fuori ambito»>. Ciò che non è stato verificato **non** è da considerare a posto. Elenco: <ID con una parola ciascuno, es. «C02 Corte cost., C14 art. 1669, C16-C18 virgolettati»>.
- Base della verifica: <testo integrale | massima | OCR riscontrato> per le pronunce; <fonte> per le norme.
- Le correzioni che cambiano un argomento sono segnate **DECIDE L'AVVOCATO**.

## Azioni
Cerca nell'atto la stringa della colonna «Cerca» (Trova, Cmd/Ctrl+F); la riga è solo indicativa. Le correzioni brevi sono già nella colonna «Intervento»; le altre hanno il testo pronto nella scheda.

| ID | Gravità | Cerca (riga) | Problema | Azione | Intervento |
|---|---|---|---|---|---|
| C07 | BLOCCANTE | `art. 2226 secondo comma c.c.` (r. 198) | Termine escluso dalle SU per il DL | ELIMINA · DECIDE L'AVVOCATO | Togli la frase «…e, in ogni caso, l'ipotetica azione di garanzia è decaduta…» fino a «c.c.». [C07](#c07) |
| C12 | GRAVE | `Sez. III, ord. n. 18405/2025` (r. 202) | Sezione errata: è la II | CORREGGI | `Sez. III` → `Sez. II` |
| C15 | GRAVE | `per colpa professionale` (r. 203) | Virgolettato ritoccato | CORREGGI | `«contribuito, per colpa professionale,` → `«comunque contribuito, per colpa,` |
| … | | | | | |

Verificate senza rilievi: <C01, C03, …>.

## Schede

### C07
**In una frase.** <verdetto in linguaggio semplice. Es.: «L'eccezione di decadenza ex art. 2226 c.c. non regge: le Sezioni Unite escludono quei termini per il direttore dei lavori».>

**Cosa dice davvero la fonte.** «<passo letterale essenziale>» (<estremi verificati>, <testo integrale | massima | OCR riscontrato>).

**Cosa fare.** <ELIMINA | CORREGGI | SOSTITUISCI | RIFORMULA | VERIFICA SUL PDF | DECIDE L'AVVOCATO> — <una frase operativa>.

**Testo da incollare** (<formato>):
```<latex|markdown|text>
<testo pronto, con virgolettati verificati>
```

**Diff**
```diff
- <originale>
+ <proposta>
```

<facoltativo, al massimo 3 righe: passi contrari, avvertenze, nota sulla natura del passo>

### C12
…

## Appendice A — Norme
| ID | Nell'atto | Testo/URN verificato | Vigenza | Pertinenza | Azione |
|---|---|---|---|---|---|

## Appendice B — Rilievi non di citazione (solo segnalati)
- <refusi, date incoerenti, numerazione dei documenti, nomi non anonimizzati>

## Appendice C — Limiti e metodo
- Strumenti, esito del collaudo, archivi lacunosi, testi OCR.
- Inventario: lo script ha trovato <X> voci, la lettura integrale <Y>; differenze: <…>.
- Registro completo: `registro_verifica.jsonl`. Passi letterali: `fonti/estratti_verificati.md`.
- Questo report è un controllo delle fonti e non sostituisce la rilettura professionale dell'atto.
