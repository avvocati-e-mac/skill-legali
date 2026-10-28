# Intervalli avanzati e profilo delle evidenze

Usa questo metodo solo quando occorre mappare automaticamente un intervallo
negli anchor Docling. Per localizzare una frase leggendo direttamente il PDF
non serve creare un profilo.

`citation_provenance.py` deriva dal sistema Hermes e usa solo Python standard.
Verifica dichiarazioni e corrispondenza degli hash; **non autentica le prove
inserite nel profilo**, non controlla la versione del convertitore in esecuzione
e non legge il testo del PDF. `origin.binary_hash` non sostituisce SHA-256.

Il profilo deve legare **quel PDF e quel JSON** alle semantiche osservate del
produttore: versione dello schema e del pacchetto, base degli intervalli (`orig`
oppure `text`), unità (`python_codepoint` oppure `utf16_code_unit`), intervalli
semiaperti e pagine fisiche 1-based. Non inferire queste proprietà solo perché
gli indici rientrano nella lunghezza della stringa. Verificale tramite codice
installato/documentazione e prove discriminanti sul produttore effettivo; il
confronto di una frase ASCII non distingue Python da UTF-16.

Schema di partenza volutamente incompleto, da NON promuovere compilando
meccanicamente `verified: true`:

```json
{
  "schema_name": "DoclingDocument",
  "schema_version": "VERSIONE_LETTA_NEL_JSON",
  "source_json_sha256": "SHA256_BYTE_JSON",
  "document_sha256": "SHA256_BYTE_PDF",
  "docling_core_version": "VERSIONE_PRODUTTORE_VERIFICATA",
  "span_base": "DA_ACCERTARE",
  "index_unit": "DA_ACCERTARE",
  "charspan_semantics": "DA_ACCERTARE",
  "page_numbering": "DA_ACCERTARE",
  "evidence": {
    "span_base": {"verified": false, "method": "", "reference": ""},
    "index_unit": {"verified": false, "method": "", "reference": ""},
    "charspan_semantics": {"verified": false, "method": "", "reference": ""},
    "page_numbering": {"verified": false, "method": "", "reference": ""}
  }
}
```

Quando stabilite, usa `charspan_semantics: half_open` e
`page_numbering: physical_1_based`. Ogni evidenza richiede metodo e riferimento
concreto, preferibilmente hash/file/righe della prova. Se riguarda solo alcuni
elementi restringi con `"anchors": ["#/texts/46"]`, sostituendo l'anchor reale.
Un cambio di produttore/file/versione richiede nuove prove. Un profilo respinto
è un limite da spiegare, non una ragione per cambiare i flag.

```sh
python3 '/percorso/SKILL/scripts/citation_provenance.py' \
  --json '/pratica/lavoro/D01.docling.json' \
  --document '/pratica/originali/D01.pdf' \
  --profile '/pratica/lavoro/D01.profilo.json' \
  --quote 'passo estratto' --anchor '#/texts/46' \
  --output '/pratica/lavoro/C01.provenienza.json'
```

Senza `--profile` la ricerca funziona ma l'attribuzione delle pagine resta
non verificata. Mantieni tutte le occorrenze fino a disambiguare con un anchor
o intervalli espliciti. Il helper non indicizza tutte le celle senza `self_ref`
né le immagini: `not_found` non prova assenza nel documento.

Interseca **ogni** provenienza con l'intervallo richiesto: `[s,e)` interseca
`[a,b)` se `max(s,a) < min(e,b)`. Il helper conserva record invalidi, spazi non
coperti, sovrapposizioni e ambiguità; non corregge o tronca gli intervalli.
Marcatori di elenco possono restare in `orig` ma non in `text`; fusioni di righe
e de-sillabazioni possono produrre indici incoerenti anche nella stessa versione.
Un `bbox` di paragrafo non è una geometria dei singoli caratteri.

Per citazioni fra più elementi, usa `--ranges` con un JSON:

```json
{"segments": [
  {"anchor": "#/texts/46", "base": "orig", "start": 0, "end": 10, "index_unit": "python_codepoint"},
  {"anchor": "#/texts/47", "base": "orig", "start": 0, "end": 12, "index_unit": "python_codepoint"}
], "separator": " "}
```

Gli indici sopra sono solo esempi: usa intervalli davvero verificati e ordine
accertato sull'originale. Il separatore non ha pagina. Con anche `--quote`, il
testo assemblato deve corrispondere dopo la normalizzazione dichiarata.

La normalizzazione preserva la mappa al testo intatto e non elimina accenti.
La ricerca distingue maiuscole salvo `--casefold` esplicito. Rifiuta tagli nelle
espansioni di normalizzazione e nelle sequenze combinanti; non implementa tutta
la segmentazione grafemica/emoji UAX #29. Non trasferire indici Python a
`String.slice` JavaScript: non-BMP e coppie surrogate cambiano le unità.

Il risultato resta candidato e `citation_verified` resta falso anche dopo un
profilo formalmente valido. Completa il controllo sul PDF e il supporto della
frase come indicato in [citazioni.md](citazioni.md). L'output non sovrascrive
file, link simbolici o hardlink già esistenti.
