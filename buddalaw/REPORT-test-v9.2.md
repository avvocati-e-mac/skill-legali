# BuddaLaw v9.2 — red teaming e decisione di rilascio

Data: 19 ottobre 2026. **Revisione conclusa; v9.2 definitiva con limiti,
non promossa a stabile sui modelli leggeri.** Nuova campagna, successiva
alla C6 congelata della v9.1.

Le migliorie sono concrete: passaggio esplicito ai tool MCP, confronto locale
dei link su file e conservazione degli estremi normativi. Non bastano a
garantire che il modello svolga la ricerca e rispetti sempre la procedura.
La campagna è chiusa per esito comportamentale, non sospesa in attesa di quota.

## Piano registrato prima delle nuove prove

1. C7: rendere concreto il passaggio dal confronto locale ai tool MCP, con
   selezione mirata del tool e promemoria nell'output del confronto. Chiarire
   l'uso degli estremi normativi prima degli alias. Stesso runner, permessi,
   limiti e valutatore della C6: nessuna correzione delle risposte a posteriori.
2. Diagnostica Haiku: B12 e B13, tre prove ciascuno. Test Luna indipendenti
   con MCP nativo e abbonamento corrente, su copia congelata; non equivalgono
   al runner Claude e non si sommano alle sue percentuali.
3. Se la diagnosi è favorevole, estendere al resto della suite; se restano
   errori gravi, una sola ulteriore candidata motivata dai dati. Nessun ciclo
   di ritenti sulla stessa candidata per cancellare una bocciatura.
4. Verificare offline la possibilità di controllare i link prima dell'invio.
   Un controllo su file copiati dall'assistente non può attestare da solo la
   provenienza MCP; un controllo successivo all'invio non previene l'errore.
5. Promozione stabile solo con copertura completa prevista, almeno 90% dei
   casi critici Haiku, avvisi corretti e nessun URL alterato o fonte inventata.
   Altrimenti chiusura definitiva di questa revisione con limiti pubblici:
   «definitiva» non equivale a «affidabilità dimostrata».

Solo abbonamento Claude con modello esplicito e `--solo-abbonamento`, tetto
di 5 USD stimati per modello/invocazione; nessun OpenRouter o proxy API.
Luna usa i subagenti di questo abbonamento. Stop al primo guasto, rifiuto o
quota esaurita; vecchi STOP e risultati conservati. Non aggiornare le copie
installate né pubblicare tracce grezze o nomi delle parti.

## C7: prima diagnosi e attacco al valutatore

Hash `SKILL.md`: `c23a7d750a821ab17bf4a8d49585411fa6dad30ff5809b67c584a0970b301173`.
Tornata Haiku: `20261019-071357-946829`, sei prove B12/B13 pianificate.
Il runner originario segnala almeno due comandi di catalogo con `2>&1`
come estranei: la shell unisce stderr a stdout, senza cambiare i nomi
passati a Python e senza aggiungere un comando. È un falso negativo.
Il valutatore aggiornato ammette esclusivamente questa coda diagnostica,
con test negativi per pipeline, altri comandi e altre redirezioni. Le tracce
originali restano intatte; l'esito corretto va ricavato senza nuovi tentativi.

## C8: controllo locale dei link e verifica estesa

Hash `SKILL.md`: `7f2b0e918afbd3f93243be0e0962069210b69e4157ded20f99ba1b29fd712025`.
La candidata conserva il passaggio esplicito ai tool, aggiunge lo script
`verifica_link.py` e il riferimento operativo; segnala le discordanze fra
richiesta normativa e contenuto restituito, osservate anche nel test Luna.

Il controllo opera prima dell'invio solo se bozza e risposte MCP originali
sono già su file. Non crea copie di fonte dall'output del modello. Il runner
consente il comando locale e ne verifica i percorsi di fonte contro quelli
effettivamente restituiti dal servizio; senza file resta il controllo manuale.

Prima delle nuove prove: **170 controlli offline superati**, 12 live saltati.
Il controllo locale è stato applicato alla bozza originale C6 Sonnet B23:
rileva esattamente l'URL alterato terminante in `66194758`, senza modificare
la risposta. Questo non trasforma la vecchia bocciatura in un successo.

Piano C8, registrato prima dell'avvio: tutti i 26 casi B00–B25 una volta su
Haiku, con tetto complessivo di 5 USD stimati e massimo 1 per esecuzione.
Gli stessi stop di servizio della C7 valgono anche per questa tornata.
Un test Luna separato controlla l'uso del verificatore sui file della C6,
senza nuove ricerche. Nessuna somma di successi fra C7 e C8 per la promozione.

## Esito C7 e verifiche del valutatore

Sei prove valide, **5/6 promosse** dopo rivalutazione senza nuove chiamate:
B12 **3/3**, B13 **2/3**. La terza B13 tenta di creare uno script di ricerca
con `cat > /tmp/buddalaw_search.py`: resta bocciata, anche se il runtime nega
il comando e le successive ricerche MCP riescono. Il criterio a maggioranza
del runner promuove entrambi i casi; non significa assenza di violazioni.
Stima CLI **1,115 USD**, uso in abbonamento, non fatturazione aggiuntiva.

Il red teaming del valutatore aggiunge anche il confronto fra numero/anno
del link e lo **stesso oggetto** che fornisce `public_url`. Un URL presente
solo nel corpo di una sentenza o in istruzioni iniettate nel testo non vale
come URL della fonte. Il controllo non verifica tutti i metadati: restano
fuori, per esempio, organo e sezione in forma libera.

B00 conservava l'attesa fissa «9.0» anche quando il modello leggeva la 9.2.
La rivalutazione usa ora la versione della copia congelata nel campione,
non la versione attualmente nel repository. Nessuna risposta è cambiata.

## Luna: prove native con l'abbonamento corrente

Modello **gpt-6-luna**, ragionamento `high`, tre subagenti con conversazioni
indipendenti; copia C7 congelata, inventario completo o ridotto secondo il
caso. Nessuna CLI di modelli, OpenRouter o proxy API. Il livello di ragionamento
fa parte dell'ambiente: non è un test del comportamento predefinito di Luna.

| Conversazione | Prove | Esito osservato |
|---|---:|---|
| Cassazione → tribunali → caso del ciclista | 3 turni | 8 chiamate MCP; limiti di ricerca rispettati, accesso una sola volta, 8 link fedeli e numero/anno associati alla fonte. Nei link di merito manca la data di deposito, riportata fuori dal collegamento. Il catalogo è confrontato manualmente pur essendo disponibile Python: scostamento dalla procedura |
| Tipo di atto normativo errato | 2 turni | 4 chiamate MCP; tipo chiesto conservato, warning riportato. Nel secondo caso rileva che rubrica e contenuto non soddisfano la richiesta; non presenta il testo come risposta verificata. Anche qui confronto manuale anziché script |
| Inventario ridotto, ricerca stradale | 1 turno | 5 chiamate MCP; nuovo nome rilevato, 5 link fedeli. L'audit contiene due copie del messaggio di avviso; l'agente dichiara in una nota separata di averlo emesso una volta. Mancando una traccia nativa indipendente, il conteggio non viene certificato |

Sono **6 risposte di ricerca**, 17 chiamate MCP complessive e **13 link**
confrontati con i risultati conservati: nessun URL alterato o accoppiamento
numero/anno errato osservato. Questo non basta per promuovere integralmente
le prove né per affermare che Luna segua sempre la skill. La ricerca su tre
turni è una conversazione, non tre campioni indipendenti.

Un settimo test, solo locale sulla C8, esegue `verifica_link.py` sulla bozza
C6 senza conoscere l'esito atteso: rileva lo stesso URL errato con codice 1,
sei URL riscontrati e nessun collegamento incompleto. Nessun file originale
modificato e nessuna nuova chiamata BuddaLaw.

Gli audit, le note d'ambiente, le copie congelate e le impronte sono conservati
in `tests/e2e/results/20261019-luna-c7/` (ignorato da Git). Sono file compilati
dagli agenti, non tracce native del runner Claude. La valutazione su link e
parametri è stata riapplicata dal coordinatore; le dichiarazioni degli agenti
non sostituiscono una prova mancante. Le percentuali Luna e Claude non si sommano.

## Decisione finale C8

Tornata `20261019-072050-161495`: **4/26 prove avviate, 3 valide**.
B00 supera il controllo di versione dopo la correzione del valutatore;
B01 e B02 sono risposte valide ma bocciate. B03 viene interrotta dal
coordinatore e resta **non valutabile**, senza trasformarla in un errore del
servizio o in una bocciatura completa del modello. Gli altri 22 casi non sono
avviati. Nessun ritento e nessuna sostituzione delle risposte.

| Caso | Risultato | Difetto |
|---|---|---|
| B00 | promosso | Segue correttamente la versione 9.2; l'attesa fissa 9.0 era un difetto del test |
| B01 | bocciato | Ricerca e lettura MCP riuscite, link fedeli; tenta anche un comando `echo ... && exit 0` estraneo agli script ammessi. Violazione della procedura, distinta dalla fedeltà delle fonti |
| B02 | bocciato | Nessuna chiamata BuddaLaw. Tenta comandi shell preparatori; la risposta finale dice soltanto che invocherà i tool. La richiesta resta insoddisfatta |
| B03 | non valutabile | Interrotta prima della risposta finale; si conserva anche il tentativo shell estraneo osservato, senza attribuirle un esito completo |

La suite contiene **17 casi critici di qualità**, escluso B00. Due sono già
bocciati: anche ipotizzando il successo di tutti gli altri, la candidata
arriverebbe al massimo a **15/17 = 88,2%**, sotto il 90% stabilito prima delle
prove. Per questo il coordinatore ferma l'esecuzione durante B03: ulteriori
chiamate non potrebbero consentire la promozione. È un arresto motivato dai
risultati; **non è un collaudo completo** né una stima del tasso reale di errore.

Stima C8 nota: **0,40061 USD** di token, escluso il costo non comunicato della
prova interrotta. In C7 sono **1,11486 USD**: totale noto **1,51547 USD**,
non una fattura né un costo aggiuntivo attestato. Nei 21 eventi nativi Claude
controllati, `isUsingOverage=false` e consumo extra disabilitato. Nessuna API
modelli esterna o OpenRouter. I costi dei subagenti Luna non sono disponibili.

### Limiti aperti e significato di «definitiva»

- **Modelli leggeri:** le istruzioni riducono alcuni errori locali, ma non
  impediscono derive nella shell o l'omissione della ricerca. C7 e C8 usano
  casi differenti: non si attribuisce una regressione allo script dei link
  senza un confronto controllato sugli stessi casi.
- **Link:** il verificatore riconosce l'errore reale C6, ma serve una bozza
  salvata e fonti originali accessibili. Non impone un blocco tecnico all'invio,
  non impedisce modifiche successive e non certifica fonti copiate dal modello.
- **Contenuto:** URL, numero e anno corretti non certificano organo, sezione,
  ricostruzione giuridica, fedeltà di tutti i virgolettati o pertinenza. Nel test
  normativo Luna sono emerse risposte del servizio discordanti dalla richiesta.
- **Copertura:** niente nuova certificazione completa di Sonnet, Claude Desktop
  senza shell, modelli OpenRouter o calcolatori. Luna ha soltanto prove mirate,
  con audit compilati dagli agenti e limiti di osservabilità dichiarati.
- **Contratto del server:** i cataloghi osservati hanno 48 nomi, coerenti con
  la fixture. Non si ripete il livello C già completato il 18 ottobre e non
  si dichiara una nuova verifica live di tutti i parametri.

«Definitiva» chiude questa revisione e rende disponibile il pacchetto finale;
non attribuisce una stabilità smentita dai test. Non è dimostrata l'impossibilità
assoluta di migliorare ancora: entro le due candidate e le risorse autorizzate
la soglia non è raggiunta. L'ulteriore passo più solido richiede controlli
nel programma che esegue l'assistente: limitare davvero la shell, verificare
la provenienza dei risultati e bloccare una bozza non conforme prima dell'invio.
Questi vincoli non possono essere garantiti da sole istruzioni `SKILL.md`.


## Confezionamento finale

Il pacchetto 9.2 chiude la revisione senza attribuirle stabilità non dimostrata.
Rispetto alla C8 cambia soltanto l'etichetta di stato nella prima voce del
changelog: corpo delle istruzioni, script e riferimenti sono identici a quelli
congelati. Nessuna risposta o fonte del collaudo è stata riscritta.

- `SKILL.md` finale: `6be2bea52b49b84cdd7828941d1cb59cacf327b79e562d17255acaca90c80b2f`.
- Archivio installabile: `1c1e664910c729879601b8dddfc7881115d4bc7ae5d5fc69a4bda8100b6f51e7`.
- Verifica finale: **177 controlli offline superati**, 12 live saltati;
  `CLAUDE.md` e `AGENTS.md` equivalenti, archivio coerente con i sorgenti.


Il pacchetto è pubblicato nella [PR #2](https://github.com/avvocati-e-mac/skill-legali/pull/2),
pronta per revisione. Il merge in `main` non è stato eseguito: il controllo
automatico richiede un'autorizzazione esplicita del maintainer per integrare
una versione che non ha raggiunto la soglia stabile. Conferma richiesta;
nessun aggiramento del blocco. Il pacchetto disponibile nella PR è definitivo.
