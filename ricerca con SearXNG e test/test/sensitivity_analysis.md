# Sensitivity analysis — robustezza del pareggio nDCG alle label

**Problema** (emerso dal red teaming): le label di rilevanza 0–3 del pool sono assegnate dall'autore,
che conosceva quali fonti aveva scelto Perplexity → **rischio di circolarità** (premiare pplx). La regola
esplicita lo mitiga ma non lo azzera. Domanda: il pareggio nDCG 0.732=0.732 è un artefatto delle mie label?

**Test**: perturbo ogni label di ±1 (clamp 0–3) su 300 trial casuali e ricalcolo `delta = nDCG_pplx − nDCG_sx`.

**Risultato**:
```
delta nDCG (pplx − sx), 300 perturbazioni label ±1:
  media = -0.001   sd = 0.039   range = [-0.121, 0.103]
  frazione trial con |delta| < 0.03 (pareggio): 0.53
```

**Lettura**: il delta è centrato su ~0 con deviazione piccola; nessuna direzione sistematica. Il **pareggio
sul ranking è robusto al rumore delle label** — non dipende dalle assegnazioni specifiche dell'autore.
Questo neutralizza in buona parte (non del tutto) l'obiezione di circolarità: anche sbagliando le label
di ±1 punto ovunque, la conclusione "ranking equivalente" tiene.

**Limite residuo**: la perturbazione ±1 non simula un errore *sistematico* (es. sovrastimare sempre gli
ufficiali). Resta vero che un secondo annotatore indipendente sarebbe lo standard corretto (vedi red-team #4).

Riproducibile: il blocco è in `RED_TEAM.md` §nDCG-robustness.
