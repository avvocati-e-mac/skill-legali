# Ricerca integrativa sul web (Perplexity)

Usala **solo** se l'utente l'ha autorizzata in Fase 0, e solo quando le banche dati scelte non bastano. Per i comandi e le quote carica la skill `perplexity-web-mcp`: controlla prima la quota (`pplx_usage` / `pwm usage`), perché la ricerca approfondita ha pochi usi al mese.

## A che cosa serve
- Ritrovare una pronuncia NON REPERITA quando gli estremi dell'atto sono forse sbagliati: un motore web incrocia numero, tema e anno e suggerisce i candidati.
- Capire se un precedente è stato **superato** (Sezioni Unite successive, riforme) quando lo strumento giuridico non offre le massime successive.
- Individuare la **dottrina** citata (titolo, rivista, anno).
- Orientamenti del merito su un punto, per valutare un precedente isolato.

Usa `intent="quick"` per i riscontri puntuali. La *deep research* serve solo per una questione complessa e decisiva, e solo dopo aver chiesto all'utente, perché consuma quota mensile.

## Regole
- **Query anonime.** Niente nomi di parti, persone, luoghi identificativi o numeri di R.G. della causa. Solo estremi pubblici della pronuncia e il tema giuridico in termini generali.
- **Non caricare mai il testo dell'atto** né documenti del fascicolo.
- **Fonte secondaria.** La risposta di Perplexity è prodotta da un modello: può contenere le stesse allucinazioni che stai cercando. Un riscontro web serve solo a sapere *dove* cercare. Il verdetto si dà dopo aver letto la pronuncia su una fonte primaria (banca dati ufficiale o testo integrale).
- **Divieto di ricerca circolare.** Se l'atto è stato scritto con un motore web, quello stesso motore non può confermarlo.
- Registra nel `registro_verifica.jsonl` la query (anonima), la data e gli URL indicati, con `"fonte": "secondaria"`.
