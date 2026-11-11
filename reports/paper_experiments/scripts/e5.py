import sys, pandas as pd, numpy as np
sys.path.insert(0,"/app/src")
import pipeline
from pipeline import trusted_official_domain as t
for n in ("test","phreshphish","vn"):
    d=pd.read_csv(f"/exp/out/scores_{n}.csv"); ph=d.label=="phishing"
    off=d.url.map(lambda u: bool(t(u)))
    cf=(~d.B & (d.score<d.thr)); both=cf|(off&~d.A)
    print(n,"official",int(off.sum()),"cleared_nosc",int((cf&~ph).sum()),"cleared_sc",int((both&~ph).sum()),round(100*(both&~ph).sum()/(~ph).sum(),2),"miss_sc",int((both&ph).sum()),"miss_sc_noA",int(((cf|off)&ph).sum()))
