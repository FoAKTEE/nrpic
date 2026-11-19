# KB-G2 evidence (owner kb; lead, wave 2b, 2026-11-19)

Gate definition: brief 12.10 (line 1458): all papers and repositories ingested; the QA report
meets the parse success rate and retrieval hit rate written in CHARTER. Thresholds: charter,
"Gates of the knowledge base" (decision 0016 item 6): parse success >= 95 % of the ingested papers;
the right paper in the top ten for >= 80 % of the golden questions (answer location reported, not
gating). Database for every number: snapshot `kb-data/db/kb-20261119-a782f1e.sqlite` (db/current;
run kb-20261119-161451-e15d1b8). QA report: `kb/QA_REPORT.md` = QA_REPORT.md of run
kb-20261119-161633-1d05960. Figure: `tracks/kb/note/figures/fig_kbg2.png` (run
kb-20261119-162642-25012f7), inspected.

## Criteria and their state

| Criterion | State | Evidence |
|---|---|---|
| all papers ingested | met | 710 of 710 manifest ids (684 brief 17 + 26 additions, `kb/manifests/arxiv_additions.tsv`); QA C1 |
| all repositories ingested | met | 63 of 63 manifest repositories (wave 1) and this repository at main 5deee18 (wave 2b) |
| parse success >= 95 % | met on the recorded status; borderline under the strictest reading | ok 684/710 = 96.3 %; ok or pdf 687/710 = 96.8 %; minus the 11 ok papers without bibliography (KB-G1 verifier): 673/710 = 94.8 %, or 676/710 = 95.2 % counting PDF papers |
| paper in top ten >= 80 % of golden questions | met | hybrid 28/32 = 87.5 %, rerank 28/32 = 87.5 %, text 27/32 = 84.4 % |
| answer location (reported) | - | rerank 25/32 = 78.1 %, hybrid 23/32 = 71.9 %, text 21/32 = 65.6 % |

## Runs

| Run | Who | What | Result |
|---|---|---|---|
| kb-20261119-142651-7318d01 | pdf_meta | PDF reader ingest of gr-qc/9412071, astro-ph/9407016, 2201.03458 | status pdf for all three; 684/684 manifest ids in the base |
| kb-20261119-143251-eb99c45 | pdf_meta | vectors and citation edges of the PDF papers | 74 embedded, 14 orphans deleted, check clean |
| kb-20261119-143702-aa436e7 | pdf_meta | metadata into the papers table, brief section 16 | 710 papers with arXiv metadata; 680/684 section-16 entries agree |
| kb-20261119-142613-942f713 | retrieval | four re-ranking variants on 32 + 10 questions (a848a06) | w2-noexpand chosen: 28/25 on the 32 |
| kb-20261119-151500-2721f64 | retrieval | `kb qa run --hybrid` on a848a06 | text 27/21, hybrid 28/23, rerank 28/25 |
| kb-20261119-155134-17d6704 | lead | B1 recount of pdf_meta | held |
| kb-20261119-155310-e600e38 | lead | B2 rescoring of R4 and the final run with own code | identical in every mode and question |
| kb-20261119-161451-e15d1b8 | lead | re-index of this repository, links, snapshot kb-20261119-a782f1e | 1242 parameter rows, 25/25 links |
| kb-20261119-161633-1d05960 | lead | Q1: `kb qa run --hybrid` on kb-20261119-a782f1e | C1 710/710; C3 26 not ok; C7 as above; C4 30/30 with INSPIRE, 2 parse defects |
| kb-20261119-162642-25012f7 | lead | figure fig_kbg2 | inspected |

Every run of this package went through `nrpic-run submit` (no hand-written manifest).

## What the golden numbers rest on

The 32 golden questions (`kb/golden/questions.yaml`, identical to `tracks/kb/claims/golden_questions.yaml`)
were written in wave 2 from brief 12.9 and the first questions, before any retrieval result; a hit
is a chunk of the expected paper (paper level) or a chunk whose source lines overlap the expected
lines widened by 5 (answer location). The re-ranking was chosen on these 32 (in-sample); the ten
held-out questions share passages with five of them. A held-out set by someone who has not seen
the diagnosis is requested (outbox to orch, heldout-golden-questions).
