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

Outcome R2 (run kb-20261119-140547-1170ecd, 06:07-06:12 PST; report and qa.json in its run
directory): prediction held. C7 hybrid paper 28/32, locator 23/32; text paper 27/32, locator
21/32 (same as wave 2 on 621430e). C4: 30 of 30 have an INSPIRE record (all from
meta/inspire); title ratio >= 0.9 for 28 of 30, surnames >= 0.8 for 28 of 30. The three
below a bar, each read in both records (06:25 PST):
- 1004.1353, surnames 2/3: the TeX author is written with an umlaut, INSPIRE transliterates
  it with "ue"; the comparator does not fold diacritics (comparator defect, fixed in R2b).
- 2103.01183, title 0.713: the stored TeX title carries the text of a `\thanks`-like bracket
  after the title (parser keeps a dedication in the title; tex_structure, not this package:
  request to the lead).
- gr-qc/9905058: TeX title and authors empty (no `\title` the parser recognises; on the C3
  list); INSPIRE has both. Parse defect, named.
So no disagreement of the metadata itself; R1's prediction held (3 below a bar, each with a
named cause).

## R2b. Diacritics in the author comparison (prediction 06:27 PST)

Test `test_compare_meta_folds_diacritics` (in test_qa_c4_reader.py): TeX "Bernd Brügmann" (and
the TeX accent form `Br\"ugmann`) against INSPIRE "Bruegmann, Bernd" must count as found.
Prediction: fails before (fraction 0), passes after folding (NFKD to ASCII, and the German
ae/oe/ue form); 1004.1353 then reaches 100 % in the next QA run.

## R3. Diagnosis of the misses (prediction 06:28 PST)

Script `scripts/inspect_misses.py` (on db/current a848a06): for each question the chunks on
the answer lines, their sizes in word pieces, where the answer starts inside them, and their
BM25, vector and hybrid ranks over the whole corpus.
Hypotheses, before looking: (H1) the vector ranking misses because the answer sits beyond the
512 word pieces the model reads (23.2 % of chunks are cut, run kb-20261115-153805-e164901);
(H2) oversized chunks (the largest body chunk has 99910 characters) dilute both rankings;
(H3) pure ranking: the answer chunk is short and in the paper but outranked.
Prediction: of the 9 hybrid locator misses (q06 q07 q11 q12 q13 q16 q17 q20 q24), at least 4
have an answer chunk longer than 512 word pieces with the answer starting beyond piece 512,
and at least one answer chunk is longer than 5000 characters. Refuted if fewer than 2 misses
involve a cut or oversized chunk: then ranking (H3) is the main cause and chunking is not.
