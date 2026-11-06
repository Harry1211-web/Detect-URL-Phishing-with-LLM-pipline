# TODO

Status of the work on the UI, the experiments and the paper. Nothing below is committed yet.

## Still to do

### Paper
- [ ] Rewrite the paper in the authors' own words. The ICCIES submission page prohibits AI-generated text and asks reviewers to check for it, and the current text was written by Claude. Ask the organizers what must be declared.
- [ ] Provide the corresponding author e-mail. `[corresponding author e-mail]` is still blank in all four paper files; re-export them once it is filled.
- [ ] Open the `.docx` files in Word and check them. They have only been rendered with LibreOffice.
- [ ] Check the headers of Tables VI and X in the two-column PDF by eye. They were checked by text only.
- [ ] Test `render_pdf.sh`. It has not been run yet, because the Docker image it needs must be rebuilt first.
- [ ] Optional: to use IEEE's real template, download `conference-template-a4.docx` into the project. The download was blocked for Claude, so the two-column version only follows IEEE-style specs.
- [ ] Optional: confirm whether the 9 validator errors in `styles.xml` of the Springer `.docx` come from the template. The original template was not validated.

### System
- [ ] Set these in `.env`, if not done yet:
  ```ini
  FE_ORIGINS=http://localhost:5173
  API_EXPOSE_LAYERS=0
  ```
- [ ] Decide what to commit, and on which branch. All of this work is uncommitted on `kha`.

## Done

### Project setup
- [x] Added the `lean-task` rule to `CLAUDE.md`.
- [x] Installed research skills in `.claude/skills/` (K-Dense, MIT): `scientific-writing`, `peer-review`, `scientific-critical-thinking`, `literature-review`, `citation-management`. No skill matched the requested names exactly, so these are the closest equivalents.
- [x] Removed the two image-generation scripts of `literature-review`, because they send data to OpenRouter.
- [x] Updated `.gitignore` (`node_modules/`, `UI/web/dist/`), `.dockerignore` (`UI/`) and `DIRECTORY_TREE.md`.

### UI
- [x] Reviewed `UI.md` before building and found the safety and run problems to fix, such as an unknown verdict showing as safe, and an error staying on a green background.
- [x] Built the web scanner in `UI/web/` (React, Vite, TypeScript, Tailwind).
- [x] Built the compact desktop window as a second page of `UI/web/`, opened by `start.cmd` / `start.sh`.
- [x] Wrote `RUNGUIDE.md` with the setup and run steps.

| Check | Result |
|---|---|
| Web tests and build | 24/24 passed, build succeeded |
| `test_bff.py`, `test_api.py` | 32/32 passed |
| BFF through Docker | All 7 scenarios correct |
| Web in headless Chrome with the real BFF | Clean URL, phishing URL, `@` trick, `javascript:`, false-report form, mobile and dark mode all correct |
| Display safety | No clickable links, no rendered malicious HTML |
| Layer D through the API | `httpbin.org` returned a `D_llm` verdict with a Vietnamese explanation in 8.7 s |

The LLM explanation was seen in the API response only, not on screen.

### Experiments
Scripts, results and figures are in `reports/paper_experiments/`. The scripts have not been rerun from that location; see `DIRECTORY_TREE.md` for how to run them.

- [x] **Reproduction:** missed URLs match the earlier reports: 12 on test, 43 on PhreshPhish, 15 on the Vietnamese set.
- [x] **Gate results (Layers B+C):** about 33 ms per URL. Miss rates are 0.03 % on test, 0.43 % on PhreshPhish and 0.56 % on the Vietnamese set, while clearing 44 to 58 % of clean URLs.
- [x] **Tranco dependence (main finding):** over 99 % of the clean URLs cleared are on Tranco-ranked domains, and so are 68 of the 70 misses. On the 67 Vietnamese phishing URLs on ranked domains, the gate misses 22.4 %.
- [x] **Live pipeline:** 0 of 207 fresh OpenPhish URLs were called safe with Layer A bypassed (95 % CI upper bound 1.8 %), against 9.3 % (28 of 300) on the old Vietnamese list. On clean URLs, 187 of 200 were called safe.
- [x] **LLM error:** it called 16.6 % of live Vietnamese phishing pages safe, but none of 149 pages from the same-day feed.
- [x] **Re-registration check:** this does not explain the gap (2 of 21 against 11 of 219, Fisher p = 0.32). The cause of the gap is still unknown.

The full pipeline does not reach the "no phishing marked clean" goal on the old Vietnamese list.

### Paper
- [x] Wrote the paper from measured results: 4 contributions, 10 tables, 2 figures, 20 references.
- [x] Filled in the placeholders with the user's answers: authors Lê Minh Kha, Nguyễn Đông Quân, Trương Đình Tú; Faculty of Information Technology, Ton Duc Thang University; code and data on reasonable request; no funding or competing interests.
- [x] Removed the hardware sentence and the note page for the lecturer.
- [x] Kept the `[n]` marks, because they are citations.
- [x] Moved the paper to Springer's official LNCS Word template, with macros removed.
- [x] Created a separate two-column version.
- [x] Kept the build scripts and the Springer template in `reports/paper_experiments/paper_build/`. A test rebuild from there gave the same text as both `.docx` files.

| File | Layout | Length |
|---|---|---|
| `ICCIES2027_Phishing_Detection_Paper.docx` / `.pdf` | Springer LNCS, single column; the one for ICCIES | 14 pages |
| `ICCIES2027_Phishing_Detection_Paper_TwoColumn.docx` / `.pdf` | IEEE-style, two columns, A4; references keep the LNCS wording | 7 pages |

Two limits apply to these files:
- The Springer `.docx` was saved again after a table XML fix, and its text is the same as the PDF.
- The two-column `.docx` passed the structure validator.
