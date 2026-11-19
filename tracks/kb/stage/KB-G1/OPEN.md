# KB-G1: what is still open (owner kb; wave 1, updated by the wave-2 lead 2026-11-15)

The four criteria of KB-G1 are met (`EVIDENCE.md`, `CHECKLIST.md`). The package criterion
"verifier report" is not: no verifier was assigned to kb. KB-G2 is not met (below), so this
package stays KB-G1 with what remains.

## KB-G2 (brief 12.10, line 1458): state of each criterion

| Criterion | State | Numbers |
|---|---|---|
| all papers ingested | not met | 683 of 684 manifest ids ingested; gr-qc/9412071 is a gzipped PostScript e-print. Its PDF is stored since wave 2 (`raw/arxiv/gr-qc_9412071/v2/source.pdf`, `meta/arxiv-pdf/`), but `kb ingest` reads only `src/`; a reader for `source.pdf` is needed (astro-ph/9407016 is ingested as `failed` and also has a stored PDF now). 26 extras stored and ingested |
| all repositories ingested | met | 63 of 63 manifest repositories and this tree (wave 1) |
| parse success rate written in CHARTER | not assessable | CHARTER states no rate (`coord/REQUESTS.md`: kb-g2-thresholds open). Against kb's proposal (95 %): 684 of 709 papers ok = 96.5 % (25 not ok: 23 review, 1 pdf, 1 failed; W4 recount, run kb-20261115-181916-08ebad9, before the two W9 papers) |
| retrieval hit rate written in CHARTER | not assessable; below kb's proposal at the locator level | 32 golden questions, top 10, hybrid with all vectors: answer location 23 of 32 (72 %), right paper 28 of 32 (88 %) (run kb-20261115-164558-5aca10c, rescored by the lead, W5). Against the proposed 80 %: met for the paper, not for the location. The K9 report's own hybrid numbers predate the full embedding and are stale |

## Inside K1

- The arXiv-API and INSPIRE records are on disk since wave 2 (708 and 704 of 708; run
  kb-20261115-182505-7e3a0b5), but nothing reads them yet: `papers.title_matches_brief` is empty,
  the comparison with brief section 16 is not done, titles and abstracts missing from 36/27
  papers are not filled, and 17661 bibliography entries without an identifier still wait for
  INSPIRE look-ups. Next session: a reader of `meta/arxiv-api/<key>.json` and
  `meta/inspire/<key>.json` in the inventory, then the comparison.
- Four ids have no INSPIRE record: 1609.03053, 1612.06734, 1709.00267, 2409.16053.

## K9 quality report

- C4 (30 papers against INSPIRE): the sample is fixed (seed 20261115, `tracks/kb/claims/QA_REPORT.md`)
  and the records exist now, but `kb/kbtool/qa_report.py` reads `meta/arxiv/<id_>.inspire.json`,
  not the fetch command's `meta/inspire/<key>.json`. Change the reader, rerun `kb qa run --hybrid`,
  and write `kb/QA_REPORT.md` and `kb/golden/questions.yaml` (brief 12.2 paths; copies now under
  `tracks/kb/claims/`).
- Retrieval quality: four of the ten FIRST_QUESTIONS-based questions are missed by every mode; the
  embed helper names finer chunks, titles in the embedded text and a reranker as remedies, none
  tried (choose on one question set, check on the other).

## Known defects (found and not fixed)

- Claim 193 is a fragment (parser defect fixed in wave 2; the claim is replaced at the next seed).
- astro-ph/0003278: flat.tex has `\section` commands and an abstract environment, the database has
  no section, no abstract and one equation (status review). Cause in the K2 extractor not found.
- Equation tags: two false positives seen in the lead's sample (a total-Hamiltonian functional as
  hamiltonian_constraint, a noise correlator as langevin); rules version 3 not re-sampled.
- Code chunks (157184) have no vectors; `kb search --kind code` is full-text only.
- `kb ingest arxiv` does not run `kb eq --apply-tags` and `kb embed`; after every ingest they are
  run by hand, then `kb embed --check --work` and `kb snapshot` (done in W9b).
- Extras carry no group: F asks for G21 on seven papers; ingest takes the group from the manifest
  only, so a curated group list for extras is needed.
- From wave 1: C3, 12 thebibliography papers with an entry count different from their \bibitem
  count, unexamined; 23 papers on the review list; 49 body and 8 appendix chunks above 420 words;
  symbols only for C/C++/CUDA, Python, Fortran; the 25 paper-code links are `claimed`.

## Claims queue (K8, and KB-G3)

- 688 claims (snapshot kb-20261115-a848a06). Of the 618 seeded: 30 checked by a
  person, 39 unlocated, 33 partial, 1 unresolved (claim 25 verified in W10). The 70 served statements
  were added with the K8 rules (24 fulltext, 44 to_verify, 2 judgement; claim 674 verified in W10). The labelled statements of the brief itself (brief 12.8, first item) are not
  seeded. KB-G3 needs every statement bearing on the six tracks' G1 processed.

## Open sub-points of the first answers (wave 1, unchanged)

- Q1, Q3: the number of filter passes and every numerical Z4c damping and gauge value are not in
  2611.12831; only the authors can supply them (decision 0002, a group step).
- Q2: how the momentum constraint is handled for the two moving clumps of Sec. 4 of 2611.12831.
  [TO VERIFY]

## Stages that remain (brief 12.3-12.10)

| Stage | Missing |
|---|---|
| K1 (rest) | read the metadata into the papers table; compare with brief section 16 |
| K7 (rest) | module descriptions of src/z4c, src/particles, src/pgen, src/mesh, src/bvals; order of physics calls in the task list |
| K8 | the brief's own statements as seeds; work through unlocated, to_verify and partial claims |
| K9 | C4 reader and rerun; hybrid numbers with all vectors; `kb/QA_REPORT.md` |
| K10 | optional MCP wrapper |
| K11 | a scheduler for the weekly watch (orch); `kb ingest` to call tags and embed |
