"""E4 (post hoc): does the Layer C score separate phishing from clean inside each Tranco stratum,
and where do ranked-domain misses sit (shared platforms vs other ranked domains)?
No network, no LLM. Runs in the phishing-api image (/app, /exp) or locally:
    python e4_strata.py [repo root] [scores dir]
Scores are cached as scores_<set>.csv (same columns as e03_offline.py); result -> results/e4.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/exp/out")
RESULTS = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(ROOT / "src"))
from typosquatting.typosquatting import check_typosquatting_deep
from typosquatting.paas_domains import is_untrusted_hosting, is_user_content_host
from url_classifier import predict, host_features as hf
from url_utils import registrable_domain, host_of
import os
import typosquatting.typosquatting as ts

# Layer C reads the Tranco list pinned with the model; TRANCO=<csv> also sets Layer B's list
if os.environ.get("TRANCO"):
    hf.RANK_PATH = ts.TRANCO_PATH = Path(os.environ["TRANCO"])

CLEAR_RATES = (0.10, 0.25, 0.50)  # share of a stratum's clean URLs cleared at the matched threshold


def sets() -> dict:
    df = pd.read_csv(ROOT / "dataset/urls/urls_labeled.csv")
    vp = pd.read_csv(ROOT / "data/test_sets/vi/phishing.csv")[["url"]].assign(label="phishing")
    vc = pd.read_csv(ROOT / "data/test_sets/vi/clean.csv")[["url"]].assign(label="clean")
    return {"test": df[df.split == "test"][["url", "label"]],
            "phreshphish": pd.read_csv(ROOT / "dataset/external/phreshphish_urls.csv")[["url", "label"]],
            "vn": pd.concat([vp, vc])}


def scored(name: str, d: pd.DataFrame) -> pd.DataFrame:
    """B flag, Layer C score / production threshold and Tranco rank, cached on disk."""
    path = OUT / f"scores_{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    d = d.reset_index(drop=True).copy(); urls = d.url.tolist()
    d["B"] = [check_typosquatting_deep(u)["flag"] is True for u in urls]
    parts = [predict.score_urls(urls[i:i + 4096], host_mode="cache") for i in range(0, len(urls), 4096)]
    d["score"] = np.concatenate([p[0] for p in parts]); d["thr"] = np.concatenate([p[1] for p in parts])
    rank = hf._tranco_rank()
    d["rank"] = [rank.get(registrable_domain(u)) for u in urls]
    OUT.mkdir(parents=True, exist_ok=True); d.to_csv(path, index=False)
    return d


def separation(d: pd.DataFrame) -> dict:
    """AUCs and miss rate when the threshold is set to clear a fixed share of the stratum's clean URLs."""
    y = (d.label == "phishing").to_numpy(); s = d.score.to_numpy()
    out = {"n_ph": int(y.sum()), "n_cl": int((~y).sum())}
    if y.all() or not y.any():
        return out
    out["roc_auc"] = round(float(roc_auc_score(y, s)), 4)
    out["pr_auc"] = round(float(average_precision_score(y, s)), 4)
    clean = np.sort(s[~y])
    for r in CLEAR_RATES:
        t = clean[int(np.ceil(r * len(clean))) - 1]  # clears >= r of the clean URLs (score <= t)
        out[f"miss_at_clear_{int(r * 100)}"] = [int((s[y] <= t).sum()), round(100 * float((s[y] <= t).mean()), 3)]
    return out


def gate(d: pd.DataFrame) -> dict:
    """Production B+C gate (no verified-domain shortcut): misses and clean cleared."""
    ph = d.label == "phishing"; cleared = ~d.B & (d.score < d.thr)
    return {"n_ph": int(ph.sum()), "missed": int((cleared & ph).sum()),
            "n_cl": int((~ph).sum()), "cleared": int((cleared & ~ph).sum())}


def platform(url: str) -> bool:
    """Free hosting, site builder, shortener, abused platform or user-content host."""
    return is_untrusted_hosting(registrable_domain(url)) or is_user_content_host(host_of(url))


res = {"uses_network": bool(predict.uses_network())}
for name, d in sets().items():
    d = scored(name, d)
    ranked = d["rank"].notna()
    plat = ranked & d.url.map(platform)
    res[name] = {"gate_all": gate(d),
                 "separation": {"ranked": separation(d[ranked]), "unranked": separation(d[~ranked])},
                 "ranked_split": {"shared_platform": gate(d[plat]), "other_ranked": gate(d[ranked & ~plat])}}
    print(name, json.dumps(res[name]), flush=True)
RESULTS.mkdir(exist_ok=True)
(RESULTS / "e4.json").write_text(json.dumps(res, indent=1))
