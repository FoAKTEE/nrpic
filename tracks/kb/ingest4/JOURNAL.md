# Journal of package ingest4 (kb helper, wave 3 batch 11)

Package brief: batch-11 task "ingest4" (sources the tracks asked for and the store does not hold;
the six old-style reference lists that ingest3 left; QA with the parse rate against the bar;
answers to the requesting tracks). Session start 2026-11-24 12:51 UTC (04:51 PST). No PAUSE flag.
kb/main at a9d5bdb2 (main bc180c26 merged, "Already up to date"), tree clean, no stranded files of
an earlier ingest4 (the directory did not exist). Card time of this package: 0.

## Entry 1 (2026-11-24 13:05 UTC): what the requests and the store say before any run

Requests (read from the senders' branches):
- A (track/A-emd-pbh, outbox 20261121T080816Z): (1) a source that the t = const slices of the
  quasi-spherical Szekeres dust solution are conformally flat; (2) how the apparent horizon of a
  Szekeres model relates to R = 2M (Krasinski and Bolejko 2012). kb's answer of batch 9
  (tracks/kb/outbox/20261121T235027Z__to-A-emd-pbh__refutation-742-and-szekeres.md) gave
  1612.08222v3 L162 (Cotton-York tensor zero) and 2605.30145v1 L535 (R = 2M) and left the
  Krasinski-Bolejko paper and a conformal-flatness source to this package.
- C (track/C-sidm, outbox 20261121T081156Z, reply by 2026-11-28): (1) hard-sphere conductivity
  beyond the first Chapman-Enskog approximation, relativistic or not; (2) DSMC cell-size and step
  errors of transport coefficients (Alexander-Garcia-Alder 1998, Garcia-Wagner 2000,
  Hadjiconstantinou 2000).
- F and D: the thirteen ids of tracks/kb/claims_tracks/README.md "orch (manifest)". The store
  already holds 2605.22525 (ok, G21, added by ingest3's frontier step), so 12 are missing:
  F 2609.20338, 2608.22735, 2608.16986, 2610.27775, 2212.10891, 1303.1540, 2602.06961,
  2610.20594; D 2307.02474, 2307.10708, 2306.08199, 1904.03781. Claims 409 (D), 447, 449, 450,
  452 (F) wait for them; claims 413 (Einstein-Straus 1945) and 416 (ApJS 58, 39, 1985) cite
  originals that predate arXiv.

The six old-style papers (all status review): the parse score is below 0.75 because title,
abstract and sections score 0 (parse_json.quality.components); the quality score has no
bibliography component. Reference formats, read in kb-data/build/tex/<key>/flat.tex (data, not
run):
- astro-ph/0306304: `\begin{center}References\end{center}` then `\begin{enumerate}` with `\item`;
  numeric citations `[1]` in the text.
- astro-ph/9306009: `\centerline{\bf References}`, `\def\i#1{\par\hang\indent\llap{[#1]\quad}...}`,
  entries `\i\Guth ...` with `\def\Guth{1}`; citations `\r{\Guth,\Olive}`.
- astro-ph/9510056: `\begref{References}` then `\ref` paragraphs (A&A macros, author-year text).
- astro-ph/9607124: `{\Large \noindent \bf References}` then `\noindent[1] ...` paragraphs.
- gr-qc/9604001: `{\bf References}` then `[1] ...` separated by `\next`.
- gr-qc/9906015: `\centerline{\rmm References}` then `\ref` paragraphs (author-year).

## Predictions (written before run 1)

- P1 (identification of the 12 ids): the arXiv API returns a record for each of the 12 and each
  title fits the subject the claim gives it; at least 11 of 12 come as TeX (one may be PDF only).
  Refuted if an id has no record or a title does not fit.
- P2 (Track A): INSPIRE finds the Krasinski-Bolejko paper on apparent horizons in quasi-spherical
  Szekeres models with an arXiv id (probability 0.85 [JUDGEMENT]). A paper on arXiv stating in
  words that the t = const slices are conformally flat is found by INSPIRE title/abstract or
  full-text queries with probability 0.5; the classical statement (Berger, Eardley and Olson 1977)
  predates arXiv and would be recorded, not fetched. Refuted if the queries return no such paper
  (then the answer says "not found" with the queries).
- P3 (Track C, DSMC): at least two of the three named DSMC papers have no arXiv e-print (INSPIRE
  may hold no record at all, being a high-energy index); an arXiv paper on the cell-size or
  step error of DSMC transport coefficients is found through INSPIRE with probability 0.3.
- P4 (Track C, conductivity): an arXiv paper giving the relativistic heat conductivity of a gas
  of hard spheres (constant cross section) at more than one moment order is found (probability
  0.8); a non-relativistic Sonine-series table on arXiv with probability 0.4.
- P5 (ingest of the additions): every fetched TeX addition parses with status ok except at most
  one review; the recorded parse rate stays at or above 96.5 % (now 719 of 744 = 96.64 %).
- P6 (old-style lists): entries for all six papers, each count equal to an independent count of
  the entry markers in the source (my own grep in run R-count, made before the parser runs);
  citation rows for the four numeric papers (0306304, 9306009, 9607124, 9604001), none for the
  two author-year papers (9510056, 9906015). The parse status of the six stays review (score has
  no bibliography term) unless headings or titles are also recovered.
- P7 (no regression): a dry run over all other TeX papers changes no paper's entries or citation
  rows: the new rule fires only where no recognised list exists (at most 3 others change, and only
  by gaining entries).
- P8 (QA): golden questions with the hybrid mode stay at 28 of 32 (paper) within one; the
  recorded parse rate is reported against the 95 % bar and passes it.

## Entry 2 (2026-11-24 13:35 UTC): identification, fetch, reading (P1-P4 outcomes)

Runs: kb-20261124-125553-f0a7a10 (metadata of the 12: INSPIRE ok for 12, arXiv API failed with
HTTP 503 after the tool's back-off; recorded in meta.txt, retried in the next run),
kb-20261124-130108-5d1c671 (17 INSPIRE queries, 43 hits), kb-20261124-130410-9673ce1 (7 more
queries, 7 hits), kb-20261124-130450-5e22375 (sources and metadata of 18 ids: all 18 sources and
both records ok), kb-20261124-131019-d622860 (meta_table.tsv), kb-20261124-130510-20ce0df
(R-count of the six old-style lists).

- P1 HELD: arXiv records for 12 of 12, each title fits the claim's subject (meta_table.tsv; e.g.
  1904.03781 is Croker et al. 2019 "Implications of symmetry and pressure in Friedmann cosmology II",
  the "Croker-Weiner 2019" of claim 409); all 12 come as TeX (one .tex file each, 2212.10891 two).
- P2 HELD (both parts). Krasinski and Bolejko 2012 is arXiv:1202.5970 (PRD 85, 124016), hit A-kb1.
  Conformal flatness stated in words: 1908.02697v3 RB_SzekeresGeometry2.tex L65 ("Its constant-t
  hypersurfaces are conformally flat", citing Berger, Eardley and Olson, PRD 16, 3086 (1977), L1588)
  and 1611.09781v2 main.tex L71-72 (Cotton-York tensor of the t = const hypersurfaces vanishes,
  "which implies their conformal flatness", citing Krasinski's 1997 book). Berger-Eardley-Olson
  1977 has an INSPIRE record without e-print (hit A-cf2 rank 5): predates arXiv, recorded, not
  fetched.
- P3 HELD as stated (none of the three named DSMC papers has an arXiv e-print that INSPIRE knows;
  Hadjiconstantinou gives 0 hits, Alexander-Garcia gives only their 1995 PRL "A consistent
  Boltzmann algorithm", no e-print). The probable outcome (no arXiv paper with the cell-size form)
  also came true: Weinberg 2014 (1304.3941, hit C-ds1 and C-ds6) states only the tuning rule
  (cell of order the mean free path, L553-569) and an effective mean free path max{l/2, lambda}
  with numerical diffusion for l >> lambda (L836-848), not the dependence on dx/lambda.
- P4 HELD for the relativistic part: 1202.4551v1 main.tex L1424-1452 (Table diff_massless3,
  particle-diffusion coefficient of a classical gas with constant cross section, ultrarelativistic:
  3/(16 sigma), 21/(128 sigma), 0.1605/sigma, 0.1596/sigma at 14, 23, 32, 41 moments) and
  1301.1190v1 HeatCondRelSys.tex L614-667, L758-760 (heat conductivity of the massless hard-sphere
  gas: 2/sigma_22 at 14 moments, 2.5536/sigma_22 resummed, 2.44/sigma_22 Chapman-Enskog of de Groot,
  2.59 +- 0.07 from BAMPS). The non-relativistic Sonine table was not found (INSPIRE indexes no
  kinetic-theory journals of that kind; predicted 0.4).

## Prediction P9 (before the dev copy reaches the worktree)

The dev parser (scratch/kb/ingest4/dev) gives, on the six papers: 11, 16, 16, 10, 27, 21 entries
(equal to R-count kb-20261124-130510-20ce0df, which counts 27 for gr-qc/9604001 whose list has no
[18]); citations by number for 0306304, 9306009, 9607124, 9604001 and none for 9510056, 9906015;
every cited number has an entry. The kb suite (all tests plus the 9 new ones) passes; refuted by
any failure.

## Entry 3 (2026-11-24 13:55 UTC): dry run over every paper; tests (P5, P6 part, P7, P9 outcomes)

Runs: kb-20261124-132834-12dc42b (whole kb suite on commit 33bbd4e2: exit 0, one expected xfail),
kb-20261124-132848-81e6285 (baseline state `before/`, dry-run parse of all 762 manifest papers
`dry/`, comparison with the database rows `compare/`).

- P9 HELD: entries 11, 16, 16, 10, 27, 21 for 0306304, 9306009, 9510056, 9607124, 9604001,
  9906015, each equal to R-count (kb-20261124-130510-20ce0df); cited keys 11, 16, 0, 10, 27, 0, each
  with an entry (the four numeric papers cite every entry of their list; the two author-year papers
  have no citation by number). The suite passes.
- P7 HELD: of the 744 papers in the database, 9 differ in the dry run: the six (entries 0 -> n,
  chunks down by 0 to 2 because the list is no longer body text) and the three PDF-only papers
  (2201.03458, astro-ph/9407016, gr-qc/9412071), which `kb ingest arxiv` does not handle (the same
  artefact of the comparison that ingest3 recorded); no TeX paper outside the six changes.
- P5 HELD in the dry run: the 18 additions parse with status ok (scores 0.85 to 1.0; every one has
  entries; 1611.09781 has no numbered sections but scores 0.849).
- P6 (status part) HELD: the six stay review (scores unchanged; the quality score has no
  bibliography term).

## Prediction P10 (before the ingest that writes the database)

`kb ingest arxiv` of the 18 additions and the six old-style papers with `--remap-claims`, then
`kb eq --apply-tags`, `kb embed`, `kb embed --check --work`: 762 papers, ok 737, review 22, pdf 3
(recorded rate 737/762 = 96.7 %); the six get 101 entries in all and citation rows only for the four
numeric papers, every row with a bib_id and a chunk; claim 778 (two locator rows on
astro-ph/0306304) is remapped and `kb claim check --id 778` reports it unchanged; 0 dangling chunk
references; the vector check 0 missing, 0 stale, 0 orphaned. Refuted by any of these failing.

## Entry 4 (2026-11-24 14:20 UTC): the database ingest (P10 outcome), figures

Run kb-20261124-135341-e65f142 (ingest of the 18 and re-ingest of the six with --remap-claims,
equation tags, vectors, vector check, claim check of 778, state `after/`); figures
kb-20261124-141600-4556f93 (first version: stacked status bars with overlapping labels and a legend
without its "ok" patch, redrawn) and kb-20261124-141642-9110c13 (final; both PNGs looked at; copies
in figures/).

- P10 HELD except one part. 762 papers: ok 737, review 22, pdf 3; recorded rate 96.72 % (strict the
  same; ok or pdf 97.11 %), up from 96.64 % on 744. The six: 101 entries (11, 16, 16, 10, 27, 21),
  citation rows 13, 20, 0, 13, 41, 0, every row with an entry; chunks 15, 34, 44, 15, 64, 37
  (before 17, 35, 44, 16, 66, 38). The 18: all ok, all with entries and citation rows. Vectors:
  1100 chunks and 1403 equations embedded, 216 and 315 orphans deleted; check 0 missing, 0 stale,
  0 orphaned for both. 0 dangling chunk references among the 1044 claim locator rows; zero-entry
  TeX papers 0 (6 before).
- FAILED part: `kb claim check --id 778` printed an empty "checked:" list, so the command did not
  check the claim at all (it is a brief seed whose rows were written by relocate; the HANDOFF trap
  "pinned" applies, and served/brief rows are not reached by that command). Checked instead from the
  rows: the two locator rows of 778 on astro-ph/0306304 (main.tex L328-329 and L31) kept their flat
  ranges 11614-11715 and 472-544 (flat.tex byte-identical, remap report), and their new chunk ids
  191527 and 191522 belong to astro-ph/0306304 and cover those ranges (read-only query of
  kb.sqlite after the run; the flat text there is the neutrino f_nu sentence and the free-streaming
  sentence of the abstract).

## Entry 5 (2026-11-24 14:18 UTC): paused

The PAUSE flag appeared (five-hour window at 80 per cent, locks/PAUSE) at 14:17 UTC. Started nothing
new after it. Where I stopped: the QA run kb-20261124-141551-a75bc11 (`kb qa run --hybrid`, 4 cores,
registered at 14:15 UTC) was still running; it is a processor run and may end by itself. Not read,
not finished: prediction P8 (golden questions 28 of 32 within one; parse rate reported against the
bar and passing) is open. The rate itself is known from the state after the ingest (96.72 %,
kb-20261124-135341-e65f142). Answers to A, C, D, F and the note to orch are posted (commit 2f386306).
To resume: `harness/bin/nrpic-run finish kb-20261124-141551-a75bc11`, read its QA_REPORT.md, write
the P8 outcome here and in README.md.

## Entry 6 (2026-11-24 17:25 UTC): resumed; P8 outcome; prediction P11

Resumed after the pause. The QA run kb-20261124-141551-a75bc11 had ended by itself (exit 0 at
14:23:38 UTC, run.log); closed with `nrpic-run finish` now and its QA_REPORT.md read.

- P8 HELD. Golden questions (32): hybrid paper 28/32 (87.5 %), locator 23/32; rerank 28/32 and
  25/32; text 27/32 and 21/32: the same as the final QA of ingest3 (kb-20261121-222222-28b1c1b).
  Parse rate 737 of 762 with status ok, 96.7 %, strict 96.7 %, reported against the 95 % bar:
  met. Equations exact 40 of 41 (C8). Bibliography 68970 entries (heading: 101, 1 with an id),
  111311 citation rows, 14968 in the corpus (ingest3: 67865, 109730, 14810).
- NOT FORESEEN: C1 says "counts do NOT agree". All 762 manifest ids are ingested; the
  disagreement is that the 18 additions of this package have no row in the `downloads` table
  ("no record 18"; their ids are the "missing or failed downloads" list). nrpic-fetch-arxiv
  writes kb-data/raw but not the database; `kb verify-downloads` records the rows and was not run
  after the fetch. The final QA of ingest3 had the same verdict with "no record 35"; the 35 have
  rows now, so a later verify-downloads recorded them.

## Prediction P11 (before `kb verify-downloads` and a second QA run)

`kb verify-downloads --report <run dir>` (takes kb-writer.lock itself) exits 1 for the known
gr-qc/9412071 (PDF only) and nothing else of brief 17; the 18 are listed as extra and get
download rows. Then `kb qa run --hybrid`: C1 downloads by status ok 761, problem 1, no record 0;
missing list empty; verdict "counts agree"; everything else in the report the same as in
kb-20261124-141551-a75bc11 (C3 25 not ok, C7 28/32 hybrid, C8 40/41, C5 counts). Refuted by any
download row of the 18 with a status other than ok, by a remaining "no record", or by any other
section changing.

## Entry 7 (2026-11-24 17:31 UTC): P11 outcome; prediction P12

Run kb-20261124-172443-40d2ae1 (`kb verify-downloads`, then `kb qa run --hybrid`; 4 cores, 7 min).

- P11 HELD. verify-downloads: brief 17 ok 683, problem 1 (gr-qc/9412071, "not an e-print"),
  exit 1 as known; extra 81 (the 78 additions and three more ids on disk that are in neither
  list; not examined here). QA: C1 downloads ok 761, problem 1; missing none; "Verdict: counts
  agree". `diff` of the two QA_REPORT.md files: only the time stamp, the C1 lines and the run
  time differ (C2 to C10 identical).

## Prediction P12 (before the QA figures)

`kb/kbtool/qa_figures.py` on that qa.json draws fig_qa_retrieval (hybrid paper rank within 10
for 28 of 32 questions, q12, q13, q11 and q24 the misses), fig_qa_eqcount (all points on the
line of equality but 1502.02011 at -2) and fig_qa_claims (861 claims, nine owners). Refuted by
a figure that shows other counts.
