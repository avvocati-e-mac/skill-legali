#!/usr/bin/env python3
"""Costruisce 5 prompt-giudice anonimi A/B. Mappa A/B da blind_pplx/_KEY.md (cecità preservata)."""
import json, os
HERE=os.path.dirname(__file__); RAW_P=os.path.join(HERE,"..","perplexity_raw")
os.makedirs(os.path.join(HERE,"prompts"),exist_ok=True)

# Mappa _KEY.md: chi è A e chi è B per le 5 query contestabili
KEY={"T11":("SearXNG","Perplexity"),"N01":("SearXNG","Perplexity"),
     "N02":("Perplexity","SearXNG"),"N03":("SearXNG","Perplexity"),"N04":("Perplexity","SearXNG")}

# Risposte SearXNG sintetizzate dai searxng_raw (testo + fonti citate)
SX={
"T11":("I siti che usano cookie non tecnici (profilazione/tracciamento) devono raccogliere il consenso preventivo, "
 "libero e specifico (Linee guida Garante 10 giugno 2021 + GDPR Reg. UE 2016/679 art. 13); i cookie tecnici sono "
 "esenti ma serve l'informativa; vietati i cookie wall puri; consenso granulare preimpostato su off; va conservata "
 "la prova del consenso.",
 ["garanteprivacy.it/faq/cookie (ufficiale)","iubenda.com/banner-cookie-obbligatorio","orizzontegiuridico.com"]),
"N01":("L'abuso di dipendenza economica è vietato dall'art. 9 L. 192/1998 (subfornitura), con nullità del patto "
 "abusivo; la dottrina (Colangelo; Delli Priscoli, Abuso di dipendenza economica e abuso del diritto, Contr. 2010) "
 "lo colloca tra disciplina della concorrenza e diritto dei contratti; dibattito sul rapporto con l'abuso del "
 "diritto; riforma 2021. [Nota: fonti primarie PDF/paywall non leggibili, sintesi dagli estratti di ricerca].",
 ["tesi.luiss.it (PDF)","orizzontideldirittocommerciale.it (PDF)","archiviofscpo.unict.it"]),
"N02":("Procedimento carbonara GialloZafferano: guanciale (non pancetta) a striscioline ~1cm rosolato ~10 min senza "
 "bruciare; crema di soli tuorli + pecorino romano + pepe nero amalgamata con frusta; mantecatura fuori fuoco con "
 "acqua di cottura; niente panna.",
 ["ricette.giallozafferano.it/Spaghetti-alla-Carbonara.html (ufficiale GZ)"]),
"N03":("A maggio 2026 sul reasoning Opus 4.8 guida su Humanity's Last Exam (49.8% no-tool / 57.9% con tool) davanti "
 "a GPT-5.5 (41.4% / 52.2%) e Gemini 3.1 Pro; su GPQA Diamond i tre sono statisticamente pari (~94%). Opus 4.8 #1 "
 "su Artificial Analysis (Elo 1890). GPT-5.5 più veloce sul 'speed-of-correct-answer'.",
 ["vellum.ai/claude-opus-4-8-benchmarks (cita System Card Opus 4.8)","artificialanalysis.ai"]),
"N04":("In Python 3.12 async/await è sintatticamente invariato vs 3.10; cambiano gli internals di asyncio: I/O su "
 "socket più veloce (sendmsg, zero-copy) e nuove asyncio.eager_task_factory()/create_eager_task_factory() "
 "(eager task execution, 2x-5x in alcuni casi), oltre ai miglioramenti generali di performance 3.12.",
 ["docs.python.org/3/whatsnew/3.12.html (ufficiale)"]),
}
CRITERIA={
"T11":["Q1_corretto","Q2_lingua_IT_adeguata","Q3_fonte_autorevole","Q5_citazioni_supportano_claim"],
"N01":["Q1_corretto","Q2_lingua_IT_adeguata","Q3_fonte_autorevole","Q5_citazioni_supportano_claim"],
"N02":["Q1_corretto","Q2_lingua_IT_adeguata","Q3_fonte_autorevole"],
"N03":["Q1_corretto","Q3_fonte_autorevole","Q4_attuale","Q5_citazioni_supportano_claim"],
"N04":["Q1_corretto","Q2_lingua_adeguata","Q3_fonte_autorevole","Q5_citazioni_supportano_claim"],
}
QUESTION={
"T11":"Cosa prevede la normativa italiana sui cookie e il GDPR per i siti web?",
"N01":"Commenti dottrinali sull'abuso di dipendenza economica nel diritto italiano.",
"N02":"Procedimento della carbonara di Giallozafferano.",
"N03":"Confronto aggiornato tra Claude Opus 4.x e GPT-5.x per task di reasoning.",
"N04":"Come usare async/await in Python 3.12 e differenze rispetto a 3.10.",
}
FACTKEY={
"T11":"Cookie tecnici: esenti da consenso, serve informativa. Cookie di profilazione: consenso preventivo libero/specifico/informato (GDPR Reg. UE 2016/679, art.122 Codice Privacy d.lgs.196/2003, Linee guida Garante 10/6/2021). Vietati cookie wall puri. Consenso granulare preimpostato off, conservazione prova del consenso.",
"N01":"Art. 9 L. 192/1998 vieta l'abuso di dipendenza economica (subfornitura); nullità del patto abusivo. Fattispecie tra diritto della concorrenza e dei contratti; dottrina rilevante (Delli Priscoli, Colangelo).",
"N02":"Carbonara romana: guanciale (NON pancetta), tuorli, pecorino romano, pepe; NO panna; mantecatura fuori fuoco. Procedura GialloZafferano coerente con questo.",
"N03":"A maggio 2026 i frontier su reasoning sono Claude Opus 4.x e GPT-5.x; su benchmark hard (HLE) Opus 4.8 in testa, GPQA ~pari. Dati corretti se citano System Card / benchmark riconosciuti e recenti (2026).",
"N04":"async/await sintatticamente invariato 3.10→3.12; differenze in asyncio (eager task factory, I/O socket più veloce) e performance. Fonte autorevole = docs.python.org.",
}

def pplx(qid):
    d=json.load(open(os.path.join(RAW_P,qid+".json")))
    return d["answer"][:1100], d["citations"][:5]

for qid in KEY:
    a_sys,b_sys=KEY[qid]
    sx_txt,sx_cit=SX[qid]; p_txt,p_cit=pplx(qid)
    A=(sx_txt,sx_cit) if a_sys=="SearXNG" else (p_txt,p_cit)
    B=(sx_txt,sx_cit) if b_sys=="SearXNG" else (p_txt,p_cit)
    crit=CRITERIA[qid]
    schema='{"A":{'+",".join(f'"{c}":true/false' for c in crit)+'},"B":{'+",".join(f'"{c}":true/false' for c in crit)+'}}'
    prompt=f"""Sei un giudice esperto e imparziale. NON cercare online: valuta SOLO i due testi qui sotto rispetto alla FACT-KEY data.
Regole: (1) giudica i FATTI, NON premiare la risposta più lunga o più verbosa. (2) Una risposta breve ma corretta vale quanto una lunga e corretta. (3) Rispondi SOLO con il JSON richiesto, nessun altro testo.

DOMANDA UTENTE: "{QUESTION[qid]}"

FACT-KEY (verità di riferimento indipendente): {FACTKEY[qid]}

--- RISPOSTA A ---
{A[0]}
Fonti citate da A: {A[1]}

--- RISPOSTA B ---
{B[0]}
Fonti citate da B: {B[1]}

Per A e per B valuta questi criteri booleani (true=soddisfatto):
{chr(10).join('- '+c for c in crit)}
  (Q3_fonte_autorevole = cita almeno UNA fonte ufficiale/primaria pertinente; per i social/video da soli = false.
   Q5_citazioni_supportano_claim = le fonti citate sono coerenti col contenuto e non lo contraddicono.)

Output SOLO questo JSON: {schema}"""
    open(os.path.join(HERE,"prompts",qid+".txt"),"w").write(prompt)
    print(f"{qid}: A={a_sys} B={b_sys} criteri={len(crit)} chars={len(prompt)}")
print("OK 5 prompt scritti")
