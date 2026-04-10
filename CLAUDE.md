# CLAUDE.md — Contesto del progetto skill-legali

Questo file contiene informazioni di contesto per Claude. Leggilo all'inizio di ogni sessione di lavoro su questo repository.

---

## Cos'è questo progetto

`skill-legali` è un repository pubblico GitHub che raccoglie **skill per Claude** dedicate alla pratica legale italiana. Le skill sono "istruzioni comportamentali" che insegnano a Claude come agire in specifici contesti legali (es. generare link a norme, redigere atti processuali, ecc.).

**Repository GitHub:** `filippostrozzi/skill-legali`  
**Maintainer:** Filippo Strozzi (avvocato)  
**Target utenti finali:** avvocati italiani, **non tecnici** — le istruzioni devono sempre essere semplici e prive di gergo tecnico

---

## Skill presenti

### normattiva
- **Cartella:** `normattiva/`
- **Scopo:** Genera link cliccabili verso [Normattiva.it](https://www.normattiva.it) per ogni riferimento normativo italiano nel testo, usando il formato URN-NIR
- **Trigger:** qualsiasi risposta che contiene citazioni normative (art. X c.c., d.lgs., legge n., r.d., d.p.r., Cost., ecc.)
- **Comportamento:** Claude NON produce mai riferimenti normativi "nudi" — ogni citazione diventa un link inline
- **File chiave:** `normattiva/normattiva/SKILL.md` (istruzioni per Claude), `normattiva/normattiva/references/lookup-extended.md` (tabella completa tipi di atto e norme storiche)
- **File installazione:** `normattiva/normattiva.skill` (file ZIP precompilato)

---

## Struttura standard di una skill

Ogni skill segue questa struttura di cartelle:

```
nome-skill/
├── nome-skill/
│   ├── SKILL.md                    ← frontmatter YAML + istruzioni comportamentali per Claude
│   └── references/                 ← (opzionale) tabelle, lookup, documenti di supporto
│       └── nome-riferimento.md
└── nome-skill.skill                ← file ZIP preconfezionato per installazione drag&drop
```

Il file `.skill` è un archivio ZIP che contiene la cartella interna `nome-skill/` (con SKILL.md e references). Viene generato comprimendo la cartella interna.

### Frontmatter SKILL.md

Ogni SKILL.md inizia con un frontmatter YAML obbligatorio:

```yaml
---
name: nome-skill
description: >
  Descrizione concisa di cosa fa la skill e quando si attiva.
  MANDATORY TRIGGERS: condizioni che devono far scattare la skill.
---
```

---

## Come aggiungere una nuova skill

1. Crea la cartella `nome-skill/` nella root del repository
2. Al suo interno, crea la sottocartella `nome-skill/nome-skill/` con il file `SKILL.md`
3. Se la skill usa tabelle di riferimento, aggiungile in `nome-skill/nome-skill/references/`
4. Crea il file `.skill` comprimendo la cartella interna:
   ```bash
   cd nome-skill
   zip -r nome-skill.skill nome-skill/
   ```
5. Aggiorna la tabella "Skill disponibili" nel `README.md`
6. Fai commit e push

---

## Note tecniche

### MCP BuddaLaw
- Il server MCP `buddalaw` è configurato ma **disabilitato localmente** in `.claude/settings.local.json`
- BuddaLaw è un servizio di ricerca giurisprudenziale e normativa italiana — potrebbe essere integrato in future skill
- Per abilitarlo temporaneamente: rimuovere `"buddalaw"` dall'array `disabledMcpjsonServers` in `.claude/settings.local.json`

### File da non committare
- `.DS_Store` (file di sistema macOS) — escluso via `.gitignore`
- `.claude/settings.local.json` — contiene impostazioni locali, ma può essere incluso per documentare la configurazione consigliata

---

## Workflow di release

Per pubblicare una nuova versione di una skill:

1. Modifica `SKILL.md` e/o i file in `references/`
2. Rigenera il file `.skill`:
   ```bash
   cd nome-skill && zip -r nome-skill.skill nome-skill/ && cd ..
   ```
3. Aggiorna `README.md` se necessario
4. Commit e push:
   ```bash
   git add .
   git commit -m "feat(normattiva): descrizione della modifica"
   git push
   ```
5. (Opzionale) Crea un tag di versione:
   ```bash
   git tag v1.1.0 && git push --tags
   ```

---

## Tono e comunicazione

- Gli utenti finali sono avvocati italiani, non programmatori
- Il README deve sempre usare linguaggio semplice, istruzioni passo-passo, niente abbreviazioni tecniche non spiegate
- Se si aggiungono nuove sezioni al README, mantieni lo stesso tono accessibile
- Le skill stesse (SKILL.md) sono scritte in italiano per Claude, con linguaggio tecnico-giuridico appropriato
