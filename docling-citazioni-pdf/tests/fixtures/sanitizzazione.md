# Copia pubblicabile della fixture Docling

Il JSON deriva dalla conversione MCP del PDF interamente sintetico accanto.
Per la distribuzione del 29 ottobre 2026 sono stati modificati soltanto
`texts[7].orig` e `texts[7].text`: il paragrafo tecnico `source:` conteneva un
percorso locale ed è stato reso relativo. Quel paragrafo non ha provenienze
(`prov` vuoto) e non è una citazione del PDF. Tutti gli altri valori, compresi
testi citati, anchor e provenienze, sono invariati.

Il nuovo SHA-256 è registrato in `smoke-summary.json`, insieme al digest della
risposta originale. I vecchi rapporti descrivono i byte ricevuti nella prova
iniziale; la copia pubblicata attuale è esplicitamente una fixture sanificata,
non un JSON originale byte per byte. Per una pratica reale la skill continua
a richiedere gli originali immutati e una gestione autorizzata delle copie.

La rimozione riguarda i file correnti e il pacchetto distribuito. Non è stata
riscritta la cronologia Git del repository.
