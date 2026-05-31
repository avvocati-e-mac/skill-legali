#!/usr/bin/env python3
"""
Layer-retrieval eval: nDCG@10 + recall su pool stile TREC.
Riproducibile. Label di rilevanza 0-3 assegnate con regola ESPLICITA (vedi sotto),
non a gusto. Il pool è l'unione top-K dei due sistemi (TREC pooling).

Regola label (test oggettivo applicato a ciascun URL del pool, per la specifica query):
  3 = fonte PRIMARIA/UFFICIALE pertinente (sito ufficiale dell'oggetto, docs ufficiali,
      ente regolatore, enciclopedia di riferimento) E direttamente sul tema.
  2 = fonte SECONDARIA AUTOREVOLE pertinente (testata/ blog tecnico riconosciuto,
      sito ricette affermato, rivista giuridica/dottrina) sul tema.
  1 = pertinente ma DEBOLE come evidenza (forum, social, video, aggregatore, SEO-blog generico).
  0 = NON pertinente / irraggiungibile-vuoto.

Le label sono nel dict sotto, una per URL, con motivazione implicita nel tier.
nDCG (Järvelin & Kekäläinen 2002): DCG = Σ rel_i / log2(i+2) (rank 0-based → +2),
IDCG = DCG dell'ordinamento ideale del pool, nDCG = DCG/IDCG.
Le funzioni dcg/ndcg sono importate da metrics.py (validate in test_compute.py).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from metrics import dcg, ndcg  # noqa: E402

RAW = os.path.join(os.path.dirname(__file__), "perplexity_raw")

# Ranking SearXNG (ordine snippet usati nei raw, top-8) per query.
SEARXNG = {
 "T01": ["it.wikipedia.org/wiki/OpenAI","ai4business.it","agendadigitale.eu","openai.com/it-IT/our-structure","fastweb.it","ilpost.it","wired.it","repubblica.it"],
 "T03": ["cosmonet.info","cosimo.dev","openai.com/it-IT/news","ansa.it","finanza.repubblica.it","menteinformatica.it","smartphonology.it","dellanesta.it"],
 "T04": ["ricette.giallozafferano.it","blog.giallozafferano.it/dulcisinforno","casapappagallo.it","daniela1963.com","dececco.com","soniaperonaci.it","academia.tv","italiasquisita.net"],
 "T06": ["blog.logrocket.com","medium.com/leivadiazjulio","stackoverflow.com","convex.dev","totaltypescript.com","typescriptlang.org","dev.to/ebereplenty","joodi.medium.com"],
 "T07": ["en.wikipedia.org/wiki/Sundar_Pichai","blog.google","tg24.sky.it","linkedin.com/in/sundarpichai","repubblica.it","corriere.it","clay.com","fastweb.it"],
 "T11": ["garanteprivacy.it/faq/cookie","orizzontegiuridico.com","iubenda.com","blog.register.it","garanteprivacy.it/docweb/9677876","cookiebot.com","agendadigitale.eu","legalfordigital.it"],
 "N01": ["tesi.luiss.it","orizzontideldirittocommerciale.it","rivistadirittosocietario.com","diges.unicz.it","archiviofscpo.unict.it","brunoleoni.it","iris.unipa.it","thesis.unipd.it"],
 "N02": ["ricette.giallozafferano.it/Spaghetti-alla-Carbonara","blog.giallozafferano.it/dulcisinforno","blog.giallozafferano.it/incucinaconilsole","blog.giallozafferano.it/valeriaciccotti","blog.giallozafferano.it/cucinaconsimone","blog.giallozafferano.it/incucinacongiorgia"],
 "N03": ["benchlm.ai","ofox.ai","vellum.ai","artificialanalysis.ai","edenai.co","aipilotdaily.com","mindstudio.ai","cometapi.com"],
 "N04": ["dev.to/johalputt","docs.python.org/3/whatsnew/3.12","medium.com/the-pythonworld","andy-pearce.com","stackoverflow.com","miguelgrinberg.com","reddit.com","flyaps.com"],
}

# Label per URL (chiave = sottostringa identificativa). Applica la regola sopra.
LABEL = {
 # T01
 "wikipedia.org/wiki/OpenAI":3,"treccani.it":3,"openai.com/it-IT/our-structure":3,"ai4business":2,"agendadigitale":2,"fastweb":2,"ilpost":2,"wired.it":2,"repubblica":2,"librologica":1,"startupitalia":2,"ilpunto.beehiiv":1,"quotidiano.net":2,
 # T03 (news maggio 2026)
 "cosmonet.info":2,"cosimo.dev":2,"openai.com/it-IT/news":3,"ansa.it":2,"finanza.repubblica":2,"menteinformatica":2,"smartphonology":1,"dellanesta":1,"searchmarketingitalia":2,"vincenzodellolio":1,"blastingnews":1,"dreams.news":1,"tecnoandroid":2,"wikipedia.org/wiki/GPT-5.5":2,"ice.it":1,"brand-news":1,
 # T04 cacio e pepe
 "ricette.giallozafferano.it":3,"blog.giallozafferano.it/dulcisinforno":2,"casapappagallo":2,"daniela1963":2,"dececco":3,"soniaperonaci":2,"academia.tv":2,"italiasquisita":2,"tavolartegusto":2,"youtube.com":1,
 # T06 TS
 "logrocket":2,"leivadiazjulio":2,"stackoverflow":2,"convex.dev":2,"totaltypescript":2,"typescriptlang.org":3,"dev.to/ebereplenty":2,"joodi":1,"gibbok.github.io":2,"geraldhamilton":1,"manuelricci":1,"reddit.com":1,
 # T07 CEO Google
 "wikipedia.org/wiki/Sundar_Pichai":3,"blog.google":3,"about.google":3,"tg24.sky":2,"linkedin.com/in/sundarpichai":2,"repubblica":2,"corriere":2,"clay.com":1,"fastweb":2,"investing.com":2,"fanpage":2,"abcnews":2,
 # T11 cookie/GDPR
 "garanteprivacy.it/faq/cookie":3,"garanteprivacy.it/docweb/9677876":3,"garanteprivacy.it/home/docweb/-/docweb-display/docweb/9677876":3,"garanteprivacy.it/home/docweb/-/docweb-display/docweb/9679893":3,"orizzontegiuridico":2,"iubenda":2,"blog.register":1,"cookiebot":2,"agendadigitale":2,"legalfordigital":2,"privacylab":2,"gdprlab":1,
 # N01 dottrina
 "treccani.it/enciclopedia/abuso":3,"diritto.it/abuso":2,"tesi.luiss":2,"orizzontideldirittocommerciale":2,"rivistadirittosocietario":2,"diges.unicz":2,"archiviofscpo.unict":2,"brunoleoni":2,"iris.unipa":2,"thesis.unipd":1,"studiolegaleadamo":1,"giustiziacivile.com":2,"accademiaassociazionecivilisti":2,"macario":2,
 # N02 carbonara
 "ricette.giallozafferano.it/Spaghetti-alla-Carbonara":3,"blog.giallozafferano.it/dulcisinforno":2,"blog.giallozafferano.it/incucinaconilsole":2,"blog.giallozafferano.it/valeriaciccotti":2,"blog.giallozafferano.it/cucinaconsimone":2,"blog.giallozafferano.it/incucinacongiorgia":2,"youtube.com":1,"facebook.com":1,"tiktok.com":1,
 # N03 AI comparison
 "vellum.ai":2,"artificialanalysis.ai":3,"benchlm.ai":2,"ofox.ai":2,"edenai.co":2,"aipilotdaily":2,"mindstudio":2,"cometapi":1,"llmbase.ai":2,"braintrust.dev":2,"spectrumailab":1,"iweaver.ai":1,"reddit.com":1,
 # N04 python async
 "docs.python.org/3/whatsnew/3.12":3,"docs.python.org/3/library/asyncio":3,"docs.python.org/pt-br":2,"docs.python.org/it":3,"docs.python.org/3/library/asyncio-task":3,"dev.to/johalputt":1,"the-pythonworld":2,"andy-pearce":2,"stackoverflow":2,"miguelgrinberg":2,"reddit.com":1,"flyaps":1,"innovaformazione":1,"engineering.fb.com":2,
}

def lab(url):
    for k,v in LABEL.items():
        if k in url:
            return v
    return 0

def pplx_ranked(qid):
    d = json.load(open(os.path.join(RAW, qid+".json")))
    return [c for c in d["citations"]]

print(f"{'QID':5} {'nDCG_pplx':>10} {'nDCG_sx':>9} {'rel@3_pplx':>11} {'rel@3_sx':>9}")
rows=[]
for qid in ["T01","T03","T04","T06","T07","T11","N01","N02","N03","N04"]:
    p = pplx_ranked(qid)
    s = SEARXNG[qid]
    pool = list(dict.fromkeys(p + s))  # union, dedup
    pool_rels = [lab(u) for u in pool]
    pr = [lab(u) for u in p]
    sr = [lab(u) for u in s]
    np_ = ndcg(pr, pool_rels)
    ns_ = ndcg(sr, pool_rels)
    # rel@3 = quante fonti con label 3 (primarie/ufficiali) nei top-3
    p3 = sum(1 for r in pr[:3] if r==3)
    s3 = sum(1 for r in sr[:3] if r==3)
    rows.append((qid,np_,ns_,p3,s3))
    print(f"{qid:5} {np_:10.3f} {ns_:9.3f} {p3:11} {s3:9}")

import statistics
print("\nMEDIE:")
print(f"  nDCG pplx = {statistics.mean(r[1] for r in rows):.3f}")
print(f"  nDCG sx   = {statistics.mean(r[2] for r in rows):.3f}")
