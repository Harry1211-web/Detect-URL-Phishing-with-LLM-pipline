"""E0 reproduction of B+C and E3 Tranco stratification, plus a threshold sweep. No network, no LLM."""
import json, os, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/app/src")
from blocklist.lookup import check_blocklist
from typosquatting.typosquatting import check_typosquatting_deep
from url_classifier import predict, host_features as hf
from url_utils import registrable_domain

ROOT = Path("/app"); OUT = Path("/exp/out")

def sets():
    df = pd.read_csv(ROOT/"dataset/urls/urls_labeled.csv")
    te = df[df.split == "test"][["url", "label"]]
    ph = pd.read_csv(ROOT/"dataset/external/phreshphish_urls.csv")[["url", "label"]]
    vp = pd.read_csv(ROOT/"data/test_sets/vi/phishing.csv")[["url"]].assign(label="phishing")
    vc = pd.read_csv(ROOT/"data/test_sets/vi/clean.csv")[["url"]].assign(label="clean")
    return {"test": te, "phreshphish": ph, "vn": pd.concat([vp, vc])}

def score(d):
    d = d.reset_index(drop=True).copy(); urls = d.url.tolist()
    d["B"] = [check_typosquatting_deep(u)["flag"] is True for u in urls]
    d["A"] = [check_blocklist(u)["flag"] is True for u in urls]
    parts = [predict.score_urls(urls[i:i+4096], host_mode="cache") for i in range(0, len(urls), 4096)]
    d["score"] = np.concatenate([p[0] for p in parts]); d["thr"] = np.concatenate([p[1] for p in parts])
    rank = hf._tranco_rank()
    d["rank"] = [rank.get(registrable_domain(u)) for u in urls]
    return d

def rate(d):
    ph = d.label == "phishing"; c = d.score >= d.thr; clean_final = ~d.B & ~c
    return {"n_ph": int(ph.sum()), "n_cl": int((~ph).sum()),
            "miss_BC": int((clean_final & ph).sum()), "cleared_BC": int((clean_final & ~ph).sum()),
            "miss_ABC": int((clean_final & ~d.A & ph).sum()),
            "cleared_ABC": int((clean_final & ~d.A & ~ph).sum())}

res = {"uses_network": bool(predict.uses_network())}
for name, d in sets().items():
    d = score(d); d.to_csv(OUT/f"scores_{name}.csv", index=False)
    r = {"all": rate(d)}
    rk = d["rank"]
    for k, m in {"ranked": rk.notna(), "unranked": rk.isna(), "top100k": rk <= 100000,
                 "rank_100k_1m": (rk > 100000)}.items():
        r[k] = rate(d[m])
    sweep = {}
    for t in (0.5, 0.75, 1.0, 1.5, 2.0):  # multiplier on the production threshold, capped at 1
        c = d.score >= np.minimum(d.thr * t, 1.0); cf = ~d.B & ~c; p = d.label == "phishing"
        sweep[str(t)] = [int((cf & p).sum()), int((cf & ~p).sum())]
    r["threshold_multiplier_sweep_miss_cleared"] = sweep
    r["thr_unique"] = sorted(set(np.round(d.thr, 6).tolist()))[:6]
    res[name] = r; print(name, json.dumps(r["all"]), flush=True)
(OUT/"e03.json").write_text(json.dumps(res, indent=1))
