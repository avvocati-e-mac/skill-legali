#!/usr/bin/env python3
"""A6: prompt-giudice anonimi per le 5 query NON contestabili (stima contaminazione self-preference V1)."""
import json, os
HERE=os.path.dirname(__file__); RAW_P=os.path.join(HERE,"..","perplexity_raw")
os.makedirs(os.path.join(HERE,"prompts_a6"),exist_ok=True)

# Mappa _KEY.md
KEY={"T01":("Perplexity","SearXNG"),"T03":("SearXNG","Perplexity"),"T04":("Perplexity","SearXNG"),
     "T06":("SearXNG","Perplexity"),"T07":("Perplexity","SearXNG")}
SX={
"T01":("OpenAI è stata fondata nel dicembre 2015 (10 dicembre 2015).",
       ["it.wikipedia.org/wiki/OpenAI","ai4business.it","agendadigitale.eu"]),
"T03":("Maggio 2026 OpenAI: GPT-5.5 Instant (default ChatGPT dal 5 mag, meno allucinazioni), modelli open-weight "
       "gpt-oss-120b/20b (Apache 2.0, HuggingFace), ChatGPT Ads Manager (dal 18 mag), nuove API vocali, rumor IPO "
       "(20 mag), SME AI Accelerator per PMI italiane.",
       ["openai.com/it-IT/news (ufficiale)","cosmonet.info","menteinformatica.it (5 mag 2026)"]),
"T04":("Ingredienti: spaghetti/tonnarelli, pecorino romano stagionato, pepe nero. Procedura GialloZafferano: acqua "
       "ridotta per più amido, tostatura del pepe, crema di pecorino con acqua di cottura, mantecatura fuori fuoco.",
       ["ricette.giallozafferano.it (ufficiale GZ)"]),
"T06":("Usa interface quando serve declaration merging, contratti di classe, estensione di librerie (extends più "
       "performante); usa type per union, intersezioni, tuple, conditional/generic types, alias di primitivi.",
       ["blog.logrocket.com","typescriptlang.org (playground ufficiale)"]),
"T07":("L'attuale CEO di Google (e Alphabet) nel 2026 è Sundar Pichai.",
       ["en.wikipedia.org/wiki/Sundar_Pichai","blog.google (ufficiale, 2026)","tg24.sky.it (mar 2026)"]),
}
QUESTION={"T01":"In che anno è stata fondata OpenAI?","T03":"Quali sono gli annunci e le novità di OpenAI di maggio 2026?",
"T04":"Ricetta originale della pasta cacio e pepe romana.","T06":"Differenze tra interfaces e types in TypeScript, quando usare quale.",
"T07":"Chi è l'attuale CEO di Google nel 2026?"}
FACTKEY={"T01":"OpenAI fondata nel dicembre 2015.","T03":"Maggio 2026: GPT-5.5 Instant default ChatGPT, modelli open-weight gpt-oss, ChatGPT advertising, API vocali, rumor IPO. Fonti recenti (mag 2026).",
"T04":"Cacio e pepe romana: pasta (spaghetti/tonnarelli), pecorino romano stagionato, pepe nero; NO panna/burro. Tecnica: crema di pecorino, tostatura pepe, mantecatura.",
"T06":"interface: declaration merging, contratti classe, extends performante. type: union/intersezioni/tuple/conditional/generic. Entrambi validi, scelta per caso d'uso.",
"T07":"CEO di Google/Alphabet nel 2026 = Sundar Pichai."}
# criteri per query (coerenti con i tipi)
CRIT={"T01":["Q1_corretto","Q3_fonte_autorevole"],"T03":["Q1_corretto","Q3_fonte_autorevole","Q4_attuale"],
"T04":["Q1_corretto","Q2_lingua_IT_adeguata","Q3_fonte_autorevole"],"T06":["Q1_corretto","Q3_fonte_autorevole"],
"T07":["Q1_corretto","Q3_fonte_autorevole","Q4_attuale"]}

def pplx(qid):
    d=json.load(open(os.path.join(RAW_P,qid+".json"))); return d["answer"][:900], d["citations"][:5]

for qid in KEY:
    a_sys,b_sys=KEY[qid]; sx=SX[qid]; p=pplx(qid)
    A=sx if a_sys=="SearXNG" else p; B=sx if b_sys=="SearXNG" else p
    crit=CRIT[qid]
    schema='{"A":{'+",".join(f'"{c}":true/false' for c in crit)+'},"B":{'+",".join(f'"{c}":true/false' for c in crit)+'}}'
    prompt=f"""Sei un giudice esperto e imparziale. NON cercare online: valuta SOLO i due testi rispetto alla FACT-KEY.
Regole: giudica i FATTI, NON premiare la risposta più lunga. Rispondi SOLO col JSON richiesto.

DOMANDA: "{QUESTION[qid]}"
FACT-KEY: {FACTKEY[qid]}

--- RISPOSTA A ---
{A[0]}
Fonti A: {A[1]}

--- RISPOSTA B ---
{B[0]}
Fonti B: {B[1]}

Criteri booleani (true=soddisfatto) per A e B:
{chr(10).join('- '+c for c in crit)}
  (Q3_fonte_autorevole=cita almeno una fonte ufficiale/primaria pertinente; social/video da soli=false.)
Output SOLO: {schema}"""
    open(os.path.join(HERE,"prompts_a6",qid+".txt"),"w").write(prompt)
    print(f"{qid}: A={a_sys} B={b_sys} crit={len(crit)}")
print("OK")
