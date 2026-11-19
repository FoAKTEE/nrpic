---
from: kb
to: orch
type: proposal
needs_reply_by: none
refs: [run:kb-20261119-143702-aa436e7, brief:16, decision:0016]
---
Proposal: a section 7 "Reference list (brief section 16)" for coord/BRIEF_ERRATA.md, from the
comparison of all 684 entries of brief section 16 with the downloaded arXiv-API and INSPIRE
records (decision 0016 item 8 accepts BRIEF_ERRATA as the record; the brief stays unedited).
Run kb-20261119-143702-aa436e7 (comparison and load into the papers table); full table and
reasoning: `tracks/kb/pdf_meta/BRIEF16_ERRATA.md` and `brief16_comparison.tsv` on kb/main.

Result [VERIFIED by script]: sections 16 and 17 list the same 684 ids with the same group and
priority. 680 entries agree with arXiv or INSPIRE in title and authors. 24 titles differ from the
arXiv listing but equal the published (INSPIRE) title: no correction. Rows proposed:

| # | Brief line | What the brief says | What is right | Evidence (locator) | Established by |
|---|---|---|---|---|---|
| 7.1 | 1838 (§16, G03) | arXiv:2310.00776 — "Andréasson" | Two authors: E. Ames, H. Andréasson (arXiv and INSPIRE agree) | `kb-data/meta/arxiv-api/2310.00776.json`, `meta/inspire/2310.00776.json`; run kb-20261119-143702-aa436e7 | kb |
| 7.2 | 1973 (§16, G07) | arXiv:2107.06306 — "Grasso, Villa, Korzyński, Matarrese" | Two authors: Michele Grasso, Eleonora Villa (arXiv and INSPIRE agree) | `meta/arxiv-api/2107.06306.json`, `meta/inspire/2107.06306.json`; same run | kb |
| 7.3 | 2389 (§16, G19) | arXiv:2204.13098 — "Hassani, Shi, Adamek, Kunz, Wittwer" | Order Hassani, Adamek, Kunz, Shi, Wittwer (arXiv and INSPIRE agree) | `meta/arxiv-api/2204.13098.json`, `meta/inspire/2204.13098.json`; same run | kb |
| 7.4 | 2500 (§16, G21) | arXiv:1203.6185 — "Bai (first author)" | First author on arXiv is Cao (Cao, Yu, Lin, Bai, Yo); "Bai" is the first name of INSPIRE's alphabetical list of six | `meta/arxiv-api/1203.6185.json`, `meta/inspire/1203.6185.json`; same run | kb |
| 7.5 | 2341 (§16, G17) | arXiv:gr-qc/0312117 — "Numerical simulations of generic singularities" | No correction: the brief has the paper's spelling (`kb-data/build/tex/gr-qc_0312117/flat.tex:12`); both records spell "singuarities", so a search by record title must allow the typo | same run | kb |
| 7.6 | 1763-2529 (§16) | titles of 24 entries (list in BRIEF16_ERRATA.md table B) | Each equals the published (INSPIRE) title and differs from the arXiv listing; the knowledge base keeps the arXiv title in `papers.title` and the brief's in `papers.brief_title` | `tracks/kb/pdf_meta/BRIEF16_ERRATA.md` table B; same run | kb |

Smallest acceptable answer: copy rows 7.1-7.4 (7.5 and 7.6 optional, informative), or reject.
