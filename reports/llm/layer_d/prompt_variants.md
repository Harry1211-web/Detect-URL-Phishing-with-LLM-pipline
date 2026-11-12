# Layer D prompt variants (summary of the removed per-run JSON files)

Runs of `src/llm/layer_d_eval.py` on the Layer D dev set (351 phishing, 300 clean pages) unless
marked "test" (1,004 phishing, 1,000 clean). "Phish safe" = phishing pages called safe (the miss
that matters); "Clean phish" = clean pages called phishing. Production prompt: `v7_nonce`
(file kept: `eval_dev_v7_nonce.json`). Vietnamese-explanation runs keep their own files (`eval_dev_explain_vi_*.json`, read by the notebook).

| Variant | Model | Change vs compact prompt | Phish safe | Phish suspicious | Clean phish | Clean suspicious | p50 latency | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| v5_compact | gpt-6-luna | compact decision rules, 2,500 chars | 58 | 88 | 6 | 3 | 1.98 s | 0.078 |
| v5_compact_1500 | gpt-6-luna | page text cut to 1,500 chars | 59 | 91 | 8 | 2 | 1.93 s | 0.071 |
| v5_fewshot3 | gpt-6-luna | + 3 worked examples | 48 | 50 | 5 | 2 | 1.91 s | 0.099 |
| v6_screenshot | gpt-6-luna | + page screenshot | 59 | 83 | 6 | 1 | 3.00 s | 0.088 |
| v7_nonce (production) | gpt-6-luna | page text between random nonce markers | 55 | 92 | 4 | 2 | 2.51 s | 0.082 |
| pilot20_haiku_think_off (20 pages) | claude-haiku-5-5 | thinking off | 2 / 10 | 1 / 10 | 0 / 10 | 0 / 10 | 0.96 s | 0.002 |
| pilot20_haiku_think_default (20 pages) | claude-haiku-5-5 | thinking default | 0 / 10 | 3 / 10 | 0 / 10 | 0 / 10 | 1.76 s | 0.004 |
| final_compact (test) | gpt-6-luna | v5_compact on the test set | 74 | 246 | 32 | 17 | 1.89 s | 0.251 |

Reading: shorter text or a screenshot did not lower phishing-called-safe;
few-shot examples lowered it (48 vs 55) but at a higher cost per page.
