# JOURNAL of the KB-G3 verifier (kb helper, batch 11, 2026-11-24)

## Entry 0 (2026-11-24 04:55 PST): set-up and what I read

- Merged main into kb/main (a9d5bdb2). No PAUSE flag. No card time (allotment 0).
- Read: CLAUDE.md; coord/CHARTER.md to "Owners" and its KB gate thresholds; brief L1218-1461;
  tracks/kb/HANDOFF.md; the READMEs of claims_tracks, claims_brief, ingest3, code_kb (what each
  claims); tracks/kb/stage/REVIEW-wave3.md from L105 (the batch-9 section). Disclosure: that
  section mixes the list of claims with the lead's "Confirmed" lines; I saw them. I take from
  it only the list of what is claimed, and every number below is recomputed by my own code.
- I read only the frozen snapshot `kb-data/db/kb-20261121-aa0a2ae.sqlite` (the target of
  `db/current` on 2026-11-24), opened read-only and immutable, never `kb.sqlite` (another kb
  helper may write it this batch). Sources are read as text from `kb-data/raw/arxiv/<id>/<v>/src`
  and from git objects of this repository; nothing there is executed.
- Population counts of the claims layer in the snapshot (exploration query, repeated inside
  the registered draw run): 861 claims. Strata used below:
  S1 fulltext+checked 225; S2 fulltext+located (machine) 464; S3 to_verify 38;
  S4 judgement or background 83. Not sampled: refuted 35 (item 2 takes all of them),
  abstract 16 (open brief seeds and two record-level defect claims).

## Entry 1 (2026-11-24 05:05 PST): design and predictions, written before any draw or check

### Item 1: stratified sample of 60 claims

Design. Allocation S1 18, S2 18, S3 12, S4 12; inside a stratum by owner track
(claim_meta.track: A-F, core, brief, kb) in proportion to the cell size with at least one
claim per present track (largest remainder); inside a cell a uniform draw without
replacement with Python's `random.Random(SEED)` over the sorted claim ids. SEED = 20261124,
committed in `SEED` before the draw script runs.

Verdict per claim, from my own reading of the source lines at each locator row:
- S1, S2 (fulltext): SUPPORTED (the lines say what the claim says, numbers equal or
  correctly rounded), NOT SUPPORTED (lines found, statement not there or different),
  LOCATOR WRONG (the statement is in the paper but not at the locator, or the locator does
  not resolve), NO STATEMENT (a fragment with nothing to support).
- S3 (to_verify), S4 (judgement/background): the same reading where a locator exists, and a
  processing verdict OK / NOT OK: does the recorded reason (claim_events evidence) hold?
  For to_verify: is it right that the store does not settle the statement? For judgement:
  is the annotation's evidence accurate where it points?
- Rate: "correct" = SUPPORTED for S1/S2, processing OK for S3/S4. Clopper-Pearson 95 %
  intervals per stratum and over the 60; a population estimate weighted by cell sizes.

Predictions (refuted as stated):
- P1a S1: 16-18 of 18 SUPPORTED. Refuted if fewer than 15.
- P1b S2: 14-17 of 18 SUPPORTED (machine located, nobody read them; claims_tracks' audit
  says 37/40 right, I expect a little worse because fragments count against). Refuted if
  fewer than 12 or if 18 of 18.
- P1c S3: 9-12 of 12 processing OK. Refuted if fewer than 8.
- P1d S4: 10-12 of 12 processing OK. Refuted if fewer than 9.
- P1e overall 50-58 of 60 correct; refuted outside 46-59.

### Item 2: refutations rederived

Set: the 11 refuted brief seeds (701-812) and the 24 refuted defect claims (813-860) with the
claims that supersede them. For each refuted seed I find the false part myself in the source.
- P2a: at least 9 of 11 refuted seeds CONFIRMED (a part of the statement is false at the
  source). I expect 1-2 where only one item of a long list is wrong, which I still count
  CONFIRMED but note as "refuted for one item". Refuted if 3 or more NOT CONFIRMED.
- P2b: of the defect pairs whose correction follows from the text (arithmetic, definitions,
  a value printed elsewhere in the paper) at least 90 % CONFIRMED; those that rest on
  reading a figure or on a recomputation I cannot repeat here are NOT CHECKED, expected
  5-9 of 24.

### Item 3: bibliography of ingest3's twenty papers

Ten cited keys per paper (all when fewer), drawn with SEED from the distinct keys of the
`\cite`-family commands that I find myself in the raw source; for each key I compare the
source entry (`\bibitem`, `.bbl`, `.bib`, `\reference`, ...) with the database row: entry
present, raw text the same reference, arXiv id or DOI equal to what the entry itself prints;
where the entry prints neither, the database target is judged against the entry's authors,
journal and year (title of the target when it is in the corpus); no outside lookup.
- P3a: 14 papers have entries, 6 have none (as ingest3 states). Refuted if different.
- P3b: entry present for at least 98 % of the drawn keys of the 14; raw text the same
  reference for at least 97 %.
- P3c: identifiers: where the entry prints an arXiv id or DOI, the database equals it in
  at least 95 %; where it prints neither, at most 2 wrong targets over the 14 papers.
- P3d: the six papers without entries do have reference lists in the source (old-style),
  so their 0 entries are a known gap, not "no references".

### Item 4: code index

Ten rows of `params` (repo of this repository) and ten links of
`kb/curated/paper_code_links.tsv`, both drawn with SEED; checked against `git show
<indexed commit>:<path>` and the paper source.
- P4a: 10 of 10 params rows have block and name read at the stated line (+-2 lines);
  9-10 of 10 have the right default (a default that is a variable or expression may be
  stored differently). Refuted if any block/name is wrong.
- P4b: 10 of 10 links name a symbol that exists in the file at the commit; for links with
  status verified the code does what the paper locator says in at least 8 of the verified
  ones drawn; claimed links are reported as such.

### Item 5: parse rate by my own definition

My definition (written before the scan): a paper is parsed when (i) it has TeX source;
(ii) its body chunks hold at least 1500 words or at least 50 % of the words of my own crude
flattening of the raw source; (iii) it has an abstract chunk of at least 20 words; (iv) the section rows are at least 70 % of my count of
`\section`/`\subsection` commands (when I count any); (v) the equation rows are at least
70 % of my count of display environments (when I count at least 3); (vi) when the source
cites, at least 80 % of my distinct cited keys have an entry. PDF-only papers count as not
parsed.
- P5: own rate between 93 % and 97 % of 744; refuted outside. Most failures from (iii)
  and (vi).

## Entry 2 (2026-11-24 05:40 PST): scripts written, smoke tests, one bug of my extractor fixed

- Scripts: `vcommon.py` (snapshot access, my own flattening of the raw TeX), `draw_sample.py`
  (item 1), `draw_bib.py` (item 3), `draw_code.py` (item 4), `parse_rate.py` (item 5),
  `show_claim.py` (terminal reader). Smoke tests wrote only to `scratch/kb/tmp/` (not
  registered, not used for any verdict).
- Bug found in the smoke test of `parse_rate.py`, in my own code: my cited-key extractor
  counted `\citeauthoryear{Authors}{year}` inside `\bibitem[...]` of MNRAS/AAS reference
  lists as citations (author strings such as "Bernuzzi and Hilditch" became "keys"), which
  made 36 papers fail criterion (vi) spuriously. Fix: keys are read only from the text
  before `\begin{thebibliography}` / `\begin{references}`, and `\citeauthoryear`,
  `\citename` are not citation commands. After the fix the 36 have 100 % of my keys with an
  entry. The definition of entry 1 is unchanged; the fix makes the extractor do what the
  definition says. Side effect noted: citations in an appendix placed after the reference
  list are not counted (rare).
- The smoke test showed my rate before that fix (91.1 %); the registered run below is the
  result. Criterion (iii) (no abstract chunk) failed for 25 papers in the smoke test,
  including 5 recorded "ok" (2109.01398, 2211.13659, 2501.13046, 2505.00286, gr-qc/0201056).
