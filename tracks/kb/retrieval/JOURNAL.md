# JOURNAL of the retrieval package (kb, wave 2b, 2026-11-19)

Package: fix the C4 reader of `kb qa run` (30 papers against INSPIRE), rerun the golden
questions (`kb qa run --hybrid`), then improve retrieval at the answer location and report
the rates against the KB-G2 thresholds of decision 0016 (paper in the top ten for at least
80 % of the golden questions gates; the answer location is reported, not gating).

Starting point [VERIFIED from the wave-2 report `scratch/orch/wave2_reports/kb.md`, kb:embed
and kb:lead]: on 32 golden questions, hybrid search found the right paper for 28 and the
answer location for 23 (run kb-20261115-164558-5aca10c, snapshot kb-20261115-621430e).
Evaluation database of this package: the read-only snapshot `kb-data/db/current` =
`kb-20261115-a848a06.sqlite` (other helpers may write `kb.sqlite` at the same time).

## R1. C4 reader (2026-11-19 06:10 PST)

Cause seen by reading the code: `qa_report._meta_record` looks for
`meta/arxiv/<key>.inspire.json` and `<key>.api.json`; the fetch command writes
`meta/inspire/<key>.json` (record under `record`, titles `record.titles[].title`, authors
`record.authors[].full_name`) and `meta/arxiv-api/<key>.json` (`title`, `authors`). 715 of 719
INSPIRE files have status ok, 4 not-found (counted on disk, 06:08 PST).

Test first: `kb/tests/test_qa_c4_reader.py` builds a synthetic store in the fetch command's
layout. Prediction: it FAILS on the current code (C4 reports blocked) and passes after the fix.

Prediction for the real sample (seed 20261115, 30 papers): after the fix at least 29 of 30
have a record (the 4 INSPIRE misses are 4 of 719, so a draw of one into the sample is
unlikely; the arXiv API record covers it if so); title ratio >= 0.9 for at least 27 of 30 and
surnames found >= 0.8 for at least 27 of 30 (TeX titles carry macros and line breaks, TeX
author lists collaboration names). Refuted if fewer than 25 have a record, or more than three
fall below either bar without a cause I can name by reading the two records.

Outcome R1 test (06:20 PST): the three tests of `kb/tests/test_qa_c4_reader.py` failed on the
old reader (blocked; KeyError 'differ') and pass after the fix; the whole suite passes, 176
tests (commit fdb7c90 says 179 by my miscount; history not rewritten).

## R2. Rerun of `kb qa run --hybrid` on db/current (prediction 06:22 PST)

Command: `kb/.venv/bin/python -I kb/kbtool/qa_cli.py qa run --hybrid --db kb-data/db/current`,
report and JSON into the run directory (kb/QA_REPORT.md is the lead's to replace).
Predictions: (a) C4 not blocked, numbers as predicted in R1; (b) C7 hybrid: paper 28 +- 1,
locator 23 +- 1 of 32 (snapshot a848a06 adds two papers to 621430e, so a rank may move); text:
paper 27 +- 1, locator 21 +- 1. Refuted if hybrid paper < 27 or locator < 22 (then the wave-2
numbers do not reproduce and I find out why before changing anything).
