#!/usr/bin/env python3
"""
Parsing giudizi 4 modelli + giudizio Claude → tabella 5-rater + Krippendorff alpha (nominale/binario).
Riproducibile. La metrica alpha è importata da metrics.py (VALIDATA in test_compute.py, 15/15 PASS) —
NON più reimplementata qui (best practice: niente metriche duplicate/hand-rolled non testate).
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import metrics  # noqa: E402

HERE=os.path.dirname(__file__)

MODELS=["GPT-5.4","Gemini 3.1 Pro","Kimi K2.6","Nemotron 3 Super"]
QIDS=["T11","N01","N02","N03","N04"]

# Giudizio di Claude (da blind_pplx/evaluation.md), mappato sui criteri usati nei prompt, per A/B.
# A/B secondo _KEY.md (T11:A=SX,B=P; N01:A=SX,B=P; N02:A=P,B=SX; N03:A=SX,B=P; N04:A=P,B=SX).
# Valori: Claude aveva dato 95%=95%, le ⚠️ erano N01-A(SX) fonte-uff-non-letta e N04 (SEO #1, ma poi letto docs).
CLAUDE={
 "T11":{"A":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":True,"Q5_citazioni_supportano_claim":True},
        "B":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":True,"Q5_citazioni_supportano_claim":True}},
 "N01":{"A":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":False,"Q5_citazioni_supportano_claim":True},
        "B":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":True,"Q5_citazioni_supportano_claim":True}},
 "N02":{"A":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":False},   # A=Perplexity (social-heavy)
        "B":{"Q1_corretto":True,"Q2_lingua_IT_adeguata":True,"Q3_fonte_autorevole":True}},    # B=SearXNG (GZ ufficiale)
 "N03":{"A":{"Q1_corretto":True,"Q3_fonte_autorevole":True,"Q4_attuale":True,"Q5_citazioni_supportano_claim":True},   # A=SearXNG
        "B":{"Q1_corretto":True,"Q3_fonte_autorevole":False,"Q4_attuale":False,"Q5_citazioni_supportano_claim":True}}, # B=Perplexity (datate)
 "N04":{"A":{"Q1_corretto":True,"Q2_lingua_adeguata":True,"Q3_fonte_autorevole":True,"Q5_citazioni_supportano_claim":True},  # A=Perplexity (docs)
        "B":{"Q1_corretto":True,"Q2_lingua_adeguata":True,"Q3_fonte_autorevole":True,"Q5_citazioni_supportano_claim":True}}, # B=SearXNG (poi docs)
}

def parse_judge(ans):
    """estrae il primo blocco JSON {A..B..} dalla risposta del modello."""
    m=re.search(r'\{.*"A".*"B".*\}', ans, re.DOTALL)
    if not m: return None
    txt=m.group(0)
    # taglia eventuale coda dopo l'ultima }
    depth=0;end=None
    for i,ch in enumerate(txt):
        if ch=='{':depth+=1
        elif ch=='}':
            depth-=1
            if depth==0:end=i+1;break
    try: return json.loads(txt[:end])
    except:
        try: return json.loads(txt[:end].replace("True","true").replace("False","false"))
        except: return None

# Raccogli tutti i rating: ratings[(qid,side,crit)] = {rater: bool}
ratings={}
parse_fail=[]
for qid in QIDS:
    d=json.load(open(os.path.join(HERE,"raw",qid+".json")))
    # Claude
    for side in ("A","B"):
        for crit,val in CLAUDE[qid][side].items():
            ratings.setdefault((qid,side,crit),{})["Claude"]=bool(val)
    # 4 modelli
    for r in d["individual_results"]:
        model=r["model"]; j=parse_judge(r.get("answer") or "")
        if j is None: parse_fail.append((qid,model)); continue
        for side in ("A","B"):
            for crit,val in j.get(side,{}).items():
                if (qid,side,crit) in ratings:  # solo criteri attesi
                    ratings[(qid,side,crit)][model]=bool(val)

# alpha importato da metrics.py (validato). Wrapper per compatibilità col resto dello script.
krippendorff_binary = metrics.krippendorff_alpha_nominal

# Raggruppa per criterio-base (toglie suffisso lingua diversi)
def base(crit):
    if crit.startswith("Q1"):return "Q1_corretto"
    if crit.startswith("Q2"):return "Q2_lingua"
    if crit.startswith("Q3"):return "Q3_fonte_autorevole"
    if crit.startswith("Q4"):return "Q4_attuale"
    if crit.startswith("Q5"):return "Q5_citation_precision"
    return crit

bycrit={}
for (qid,side,crit),d in ratings.items():
    units01={r:(1 if v else 0) for r,v in d.items()}
    bycrit.setdefault(base(crit),[]).append(units01)

print("=== Krippendorff alpha per criterio (5 rater: Claude+GPT+Gemini+Kimi+Nemotron) ===")
print(f"{'criterio':24} {'alpha':>7}  {'n_unita':>7}  {'%accordo_pieno':>14}")
for crit,units in sorted(bycrit.items()):
    a=krippendorff_binary(units)
    full=sum(1 for u in units if len(set(u.values()))==1)/len(units)
    print(f"{crit:24} {('%.3f'%a) if a is not None else '  n/a':>7}  {len(units):>7}  {full*100:>13.0f}%")

if parse_fail:
    print("\nPARSE FAIL:", parse_fail)
else:
    print("\nTutti i giudizi parsati correttamente (0 fail).")

# Conta i disaccordi specifici per ispezione
print("\n=== Unità con disaccordo (rater non unanimi) ===")
for (qid,side,crit),d in sorted(ratings.items()):
    if len(set(d.values()))>1:
        sys_label={"T11":("SX","P"),"N01":("SX","P"),"N02":("P","SX"),"N03":("SX","P"),"N04":("P","SX")}[qid][0 if side=="A" else 1]
        disn=[r for r,v in d.items() if v!=max(set(d.values()),key=list(d.values()).count)]
        print(f"{qid} {side}({sys_label}) {crit}: {d}  -> minoranza: {disn}")
