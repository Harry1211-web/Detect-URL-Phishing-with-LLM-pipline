"""E2 stale-label check: current RDAP registration date of the live-run VN phishing domains vs the listing date."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd
sys.path.insert(0, "/app/src")
from url_classifier import host_features as hf
from url_utils import registrable_domain
d = json.load(open("/app/reports_live/vi_vi_final_gpt.json", encoding="utf-8"))
rows = [r for r in d["details"] if r["label"] == "phishing"]
vi = pd.read_csv("/app/data/test_sets/vi/phishing.csv").set_index("url")
def one(r):
    dom = registrable_domain(r["url"])
    try:
        raw = hf._rdap(dom)
    except Exception as e:
        raw = {"error": type(e).__name__}
    time.sleep(0.3)
    m = vi.loc[r["url"]] if r["url"] in vi.index else None
    return {"url": r["url"], "domain": dom, "verdict": r["verdict"], "decided_by": r["decided_by"],
            "llm_unusable": r.get("llm_unusable"), "rdap": raw,
            "listed_by": None if m is None else str(m["listed_by"]), "registered_csv": None if m is None else str(m["registered"])}
with ThreadPoolExecutor(6) as p:
    out = list(p.map(one, rows))
Path("/exp/out/e2_rdap.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print(len(out), json.dumps(out[0], default=str)[:500])
