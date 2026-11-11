"""E1 forward-in-time live test: fresh OpenPhish URLs on domains unseen in training, Layer A bypassed.
Clean side: fresh deep links from Tranco top sites. Paid LLM through the normal Layer D path."""
import gzip, json, random, sys, time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
sys.path.insert(0, "/app/src")
import pipeline
from evaluate_live import top_site_urls
from llm.llm_client import DEFAULT_MODEL, provider_of, spent_usd
from url_utils import registrable_domain, ensure_scheme

N_PH, N_CL, PER_DOMAIN, SEED = 200, 200, 2, 20261104
OUT = Path("/exp/out")
train = pd.read_csv("/app/dataset/urls/urls_labeled.csv", usecols=["url"]).url
known = {registrable_domain(u) for u in train}
with gzip.open("/app/data/blocklist/openphish.txt.gz", "rt", encoding="utf-8", errors="ignore") as f:
    feed = [ensure_scheme(l.strip()) for l in f if l.strip() and not l.startswith("#")]
rng = random.Random(SEED); rng.shuffle(feed)
per, seen_dom, ph = defaultdict(int), 0, []
for u in feed:
    d = registrable_domain(u)
    if d not in known:
        continue
    seen_dom += 1
    if per[d] < PER_DOMAIN:  # second half of E1: fresh feed URLs on domains seen in training
        per[d] += 1; ph.append(u)
cl = [u for u, _ in top_site_urls(N_CL, SEED)]
print("feed", len(feed), "known-domain", seen_dom, "phish", len(ph), "domains", len({registrable_domain(u) for u in ph}), "clean", len(cl), flush=True)

real_a = pipeline.check_blocklist
def no_a(url):  # bypass Layer A: every sampled URL is listed by construction
    r = dict(real_a(url)); r["flag"] = False; return r
pipeline.check_blocklist = no_a

def run(job):
    url, label = job; t0 = time.perf_counter()
    try:
        r = pipeline.analyze_url(url, llm_model=DEFAULT_MODEL)
    except Exception as e:
        return {"url": url, "label": label, "verdict": None, "decided_by": f"error:{type(e).__name__}", "c_label": None, "b_flag": None, "llm_unusable": None}
    L = r["layers"]; d = L.get("D_llm") or {}; c = L.get("C_classifier") or {}; b = L.get("B_typosquatting") or {}
    return {"url": url, "label": label, "verdict": r["verdict"], "decided_by": r["decided_by"],
            "b_flag": b.get("flag"), "c_label": c.get("label"), "c_score": c.get("score"),
            "llm_verdict": d.get("verdict"), "llm_unusable": d.get("timed_out"),
            "d_keys": sorted(k for k in d if k not in ("explanation", "reason"))[:20],
            "latency_s": round(time.perf_counter() - t0, 2)}

provider = provider_of(DEFAULT_MODEL); s0 = spent_usd(provider)
jobs = [(u, "phishing") for u in ph] + [(u, "clean") for u in cl]
with ThreadPoolExecutor(8) as pool:
    rows = list(pool.map(run, jobs))
out = {"time": datetime.now(timezone.utc).isoformat(), "model": DEFAULT_MODEL, "feed": len(feed),
       "feed_on_known_domains": seen_dom, "spend_usd": round(spent_usd(provider) - s0, 4), "details": rows}
(OUT/"e1b_live.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
for lb in ("phishing", "clean"):
    rs = [r for r in rows if r["label"] == lb]
    print(lb, len(rs), Counter(r["verdict"] for r in rs), Counter(r["decided_by"] for r in rs))
print("spend", out["spend_usd"])
