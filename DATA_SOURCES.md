# Data sources & licenses

The MIT license in `LICENSE` covers the **code and documentation** of this repository only. The
URL lists, labels and page data come from the third parties below and stay under **their own
terms**; MIT does not relicense them. Check the upstream terms before any reuse, especially
commercial use or redistribution. Terms were last checked on 2026-10-30.

| Source | Used for | In this repository | Terms (upstream) |
|---|---|---|---|
| [PhiUSIIL Phishing URL dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) (UCI) | Training URLs, phishing + clean | URLs in `dataset/urls/` (`source = phiusiil`) | **CC BY 4.0**: attribution required (citation below) |
| [PhreshPhish](https://huggingface.co/datasets/phreshphish/phreshphish) (Hugging Face) | External test set, Layer D evaluation, DOM model | URLs + metadata in `dataset/external/`; HTML pages are downloaded, not stored | **CC BY 4.0**; the dataset card asks that it be used only for anti-phishing research |
| [Phishing.Database](https://github.com/Phishing-Database/Phishing.Database) | Training URLs (phishing), Layer A feed | URLs in `dataset/urls/` (`source = phishing_database`); feed downloaded | **MIT** (© Mitchell Krog, Nissar Chababy and contributors) |
| [PhishTank](https://phishtank.org/) (Cisco Talos) | Training URLs (phishing), Layer A feed | URLs in `dataset/urls/` (`source = phishtank`); feed downloaded | Free for commercial and non-commercial use per its [FAQ](https://phishtank.org/faq.php); governed by the PhishTank / Cisco terms of use linked on the site |
| [OpenPhish](https://openphish.com/) community feed | Training URLs (phishing), Layer A feed | URLs in `dataset/urls/` (`source = openphish`, 267 rows); feed downloaded | [Terms of use](https://openphish.com/terms.html): personal and research use only; commercial use and **redistribution need OpenPhish's written permission** |
| [Tranco](https://tranco-list.eu/) top-1M list | Clean training URLs (crawl of ranked sites), Layer C rank feature, `.vn` clean test set | Crawled URLs in `dataset/urls/` (`source = tranco_crawl`) and `data/test_sets/vi/` (`tranco_vn`); the list itself is downloaded | No explicit license; the list aggregates providers with their own terms (e.g. Majestic CC BY 3.0, CrUX CC BY-SA 4.0, Cloudflare Radar CC BY-NC 4.0). Cite the paper below |
| [Chống Lừa Đảo](https://chongluadao.vn/) blacklist, via the [ChongLuaDao-Phishing-Blocklist](https://github.com/elliotwutingfeng/ChongLuaDao-Phishing-Blocklist) mirror | Vietnamese test set (phishing) | URLs in `data/test_sets/vi/` (`source = chongluadao`) | No published data license found; the mirror's code is BSD-3-Clause, the URLs are compiled by the Chống Lừa Đảo project. Not affiliated with or endorsed by it |

Brand lists in `dataset/brands/` are compiled by this project from public sources (see
`dataset/brands/README.md`); brand names and trademarks belong to their owners.

## Notes

- **Redistribution.** The labelled URL files in `dataset/` and `data/test_sets/` contain URLs from
  the sources above. They are shared for academic research on phishing detection. Remove the
  `openphish` rows before any use outside research unless you have OpenPhish's permission.
- **Live phishing URLs.** Many URLs in these files are, or were, malicious. Do not open them
  outside an isolated environment.
- **Not stored here.** Feed snapshots (`data/blocklist/*.gz`), the Tranco list and PhreshPhish
  HTML pages are downloaded by the scripts and listed in `.gitignore`.

## Citations

- A. Prasad and S. Chandra, "PhiUSIIL: A diverse security profile empowered phishing URL detection
  framework based on similarity index and incremental learning," *Computers & Security*, vol. 136,
  2024. doi: [10.1016/j.cose.2023.103545](https://doi.org/10.1016/j.cose.2023.103545)
- T. Dalton et al., "PhreshPhish: A Real-World, High-Quality, Large-Scale Phishing Website Dataset
  and Benchmark," arXiv:[2507.10854](https://arxiv.org/abs/2507.10854), 2025.
- V. Le Pochat, T. Van Goethem, S. Tajalizadehkhoob, M. Korczyński and W. Joosen, "Tranco: A
  Research-Oriented Top Sites Ranking Hardened Against Manipulation," in *Proc. NDSS*, 2019.
  doi: [10.14722/ndss.2019.23386](https://doi.org/10.14722/ndss.2019.23386)
