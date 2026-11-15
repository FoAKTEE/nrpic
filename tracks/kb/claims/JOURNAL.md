# Journal of the claims helper (kb, wave 2: stages K8 and K9)

Predictions are written before the run they concern; outcomes after it, also when the
prediction failed. Labels: [VERIFIED] (checked against a file or a run named here),
[JUDGEMENT], [TO VERIFY].

## 2026-11-15 15:40 UTC: plan

Seed sources (read with `git show <branch>:<path>`, branch tips of 15:25 UTC):
A `scope/REFERENCES.md` (track/A-emd-pbh c7f4cfc), B `scope/REFERENCES.md` (767eb93),
C `scope/REFERENCES.md` and `stage/G0/REPORT.md` section 6 (904eb96), D
`scope/REFERENCES.md` (3276791), E has no REFERENCES.md: its errata request to kb
(`outbox/20261115T1410Z__to-kb__errata-s11-references.md`, 6330493), C's defect request
(`outbox/20261115T1320Z__to-kb__index-locators-typos.md`), F has no REFERENCES.md: its
novelty note `novelty/NOVELTY.md` (dd48b3e), core's
`tracks/core/interfaces/SECTION2_CORRECTIONS.md` on main (3da9086).

The notes use five locator styles (`(L264-268)`, bare `(879-882)`, `main.tex:103-118`,
`` (`:60-74`) ``, `` `TBH3.tex` lines 582-626 ``). Design [JUDGEMENT]: one claim per
locator group (text from the end of the previous locator to the end of this one); a
bracketed JUDGEMENT or TO VERIFY after a locator becomes a claim of its own; unlabelled
units take the default label the note's header states (B, C, F, core: "read at the
locator"), else `to_verify`. The knowledge base's own check, independent of the track:
the locator resolves in the store (paper, version, file, line within the file) and every
number the claim quotes (decimals, powers of ten, integers >= 10) occurs in the cited lines
+-3, as written or rounded to the quoted digits. Only a VERIFIED statement that passes
becomes `fulltext`; the others stay `to_verify` with the reason. Judgements never become
`fulltext`.

## P1 (prediction, before the dry run of `kb claim seed`)

Expected: 500-700 claims in all; at least 90 % of the paper locators resolve (the tracks
read the same store a few hours ago; misses would be parser errors or files in
subdirectories); of the VERIFIED claims at least 70 % reach `located` (the rest
`partial`: numbers paraphrased, e.g. "1e4" for "10^4", rounded values, numbers from the
track's own runs). Refuted if fewer than 90 % of locators resolve (the parser assigns
wrong papers or files) or fewer than 60 % of VERIFIED claims are located.

## P1 outcome (run kb-20261115-153712-595d313, kb.sqlite)

[VERIFIED, run kb-20261115-153712-595d313 stdout.log and `kb claim stats`] 622 claims seeded
from 9 notes (70 papers): 677 of 679 paper locators resolve (99.7 %); of the 547 statements
the tracks marked as read at the source (364 explicit, 183 by the note's header) 512 became
`fulltext` (93.6 %); statuses located 550, partial 31, unlocated 39, unresolved 2; labels
fulltext 512, to_verify 72, judgement 37, background 1. Prediction held on all three counts.
Caveat [JUDGEMENT]: 388 of the 550 located claims quote no checkable number, so for them
"located" means only that the locator resolves; whether the passage supports the statement
is what P2 measures. Two dry runs before (not registered, scratch/kb/tmp/claims_dev/) fixed
parser defects: prefix locators "L1340: ...", "lines N" after a file-qualified locator,
repository files and brief lines taken for paper lines, outbox front matter.

## P2 (prediction, before the manual audit)

Sample: 30 `fulltext` claims drawn with random.Random(20261115) from the 512, plus all 31
`partial`. I read the cited lines (+-3) in the store myself and judge whether the passage
supports the statement as worded (track paraphrase allowed; a statement split from its
locator by the parser counts as a failure). Expected: at least 27 of 30 supported (90 %).
Refuted if fewer than 24 (80 %): then "located" is too weak to give `fulltext` and the rule
must change. For the partial ones I expect most missing numbers to be the tracks' own
values (corrected numbers, own runs, rounding of a range), not wrong locators.

## P2 outcome (audit of the first seed, kb-20261115-153712-595d313)

[VERIFIED, my reading of the cited lines in kb-data/raw, claim ids of that seed] 29 of 30
sampled `fulltext` claims are supported by the cited passage as worded (prediction >= 27
held). The one failure (id 108, "criterion L315-331)") was a parser split: two locators
inside one parenthesis, "(abstract L78-79; criterion L315-331)", became two claims, the
second without its statement. Fixed (grouping of locators inside one parenthesis, test
`test_two_locators_in_one_parenthesis_stay_one_claim`); a second defect found while fixing
it (several ranges of one locator, "lines 185, 269-277, 400", split into empty claims) was
fixed and tested too. Remarks on the 29 [JUDGEMENT]: 3 are supported but terse fragments
("initial lapse L460", "maximal slicing (L432)", "Summary and features: lines 62-103");
2 carry the track's own one-line verdict or a repository remark appended after the
locator (ids 436, 596 of the final seed); none was wrong. New rule from the audit: a
statement whose cited lines are all TeX comments is not `fulltext` (status partial, note
"cited lines are TeX comments"); 2 claims of the final seed fall under it.
Partial claims (33 in the final seed): reading the missing numbers, they are the tracks'
own values (corrected table entries of the errata, e.g. 0.45/0.52 for printed 0.045/0.052;
"8e-5" between two solvers; "in our variables" of F), numbers of the Brief column of
core's table that the evidence column cites elsewhere, three line ranges of B's
"Abstract: 68-80" style read as numbers, and the 2 comment cases. None points at a wrong
paper or file [JUDGEMENT, from the `missing` lists in the seed table].
Final seed: run kb-20261115-154020-7b80ccc (618 claims, 70 papers, 677/679 locators
resolve; located 545, partial 33, unlocated 39, unresolved 1; fulltext 507, to_verify 73,
judgement 37, background 1). The 29 audited claims were then marked checked by a person
(run kb-20261115-154041-7b80ccc; `kb claim verify`, checked_by "kb claims helper (manual
read, audit P2)"). From here on the claim ids are not rebuilt (`--rebuild` refuses).

## Incident (found 15:45 UTC): my --rebuild removed another helper's claims

[VERIFIED, ingest_log of kb.sqlite] The serve helper loaded 330 claims (origin `served:*`,
claims table only, no side tables) at 15:37:51 (run kb-20261115-153751-e164901). My two
`--rebuild` seeds (15:39:43, run kb-20261115-153942-e70f45d; 15:40:23, run
kb-20261115-154020-7b80ccc) emptied the whole claims table and so deleted those 330 rows;
`SELECT count(*) FROM claims WHERE origin LIKE 'served:%'` is now 0. The guard I wrote
checked only snapshots and people's labels, not other writers. Their module calls that
load superseded (its `sync-k8` removes the served rows and re-adds the uncovered ones
through the K8 side tables, seed_key `served:<key>`), but any claim id taken from that run
no longer exists. Fixed: rebuild, re-check and stale-marking touch only rows of the K8
seed (`claims_db.OWN_SEED`: seed_key not `served:*`, not `manual-*`); test
`test_rebuild_and_stale_leave_other_writers_rows`. Request to the lead: have the serve
package re-run its `sync-k8` and not reply to the tracks with ids of run
kb-20261115-153751-e164901.

## P3-P5 (predictions, before the first `kb qa run`)

P3, independent equation count (C8; 2611.12831 plus 40 papers drawn with
random.Random(20261115 + 1) from the ingested TeX papers; `qa_eqcount.py`, a stack scanner
written apart from kbtool's extractor and from the lead's checkers; the raw main file for
single-file papers, else flat.tex): at least 75 % of the papers agree exactly on the number
of numbered display lines, at least 90 % within 2 % or 2 lines. Refuted if fewer than 70 %
agree exactly; then I read at least three mismatches at the source and say which side
is wrong before naming a cause.

P4, retrieval (C7, 32 golden questions, top 10 chunks): BM25 alone finds the expected
paper for at least 26 of 32 (80 %) and the expected lines (+-5) for at least 16 (50 %).
Refuted if fewer than 22 papers (70 %). Hybrid mode with vectors for only about a quarter
of the chunks (10496 stored now): paper hits not more than one below BM25.

P5, integrity (C1-C6, C10): manifest ids not ingested = {gr-qc/9412071} only (PostScript;
astro-ph/9407016 is ingested as failed); papers not ok = 25 (23 review, 1 pdf, 1 failed)
or a few more if the served ingest added extras; bibliography with an arXiv id 60 +- 1 %
and in-corpus edges 15 +- 1 % (the K3 numbers of kb/README.md); every reference of CHARTER
section 10 ingested. Refuted by any other id in the not-ingested list or a rate outside
those bands.

## P3-P5 outcomes (first QA run kb-20261115-155007-11f0fde; the run before it,
## kb-20261115-154858-b0d8c8f, failed in the retrieval step: IndexError in
## embed_search.Locator.lines on the empty source map of 2201.03458; guarded in qa_report)

P3 held as worded: 39 of 41 papers agree exactly, 40 within 2 % or 2 lines (totals 2283
independent, 2295 database). Both mismatches were read at the source and both are defects
of MY counter, not of the extractor [VERIFIED]:
- 1706.09896 (0 against 10): "$\sim 1 - 3$$\Gpc^{-3}...$" is two inline maths side by
  side; the counter took the `$$` for a display and swallowed the paper. Fixed (the first
  `$` decides; escaped `\$` skipped), test `test_adjacent_inline_maths_are_not_a_display`.
- 2408.09964 (61 against 63): two align blocks end in `\nonumber \\` before `\end{align}`.
  pdflatex on a synthetic file (run kb-20261115-155344-596b4ce, labels in its stdout.log)
  numbers the empty last row after a trailing `\\` in align, gather and eqnarray alike, so
  the database's 63 (contiguous 1-15, A1-A21, B1-B27) is right and the counter's rule "drop
  an empty last row" was wrong. Fixed and tested. The same rule is written in the lead's
  checker `tracks/kb/analysis/lead_checks/eqcount.py` ("a trailing \\ before \end is
  dropped for ams environments"): refuted by this run for align and gather (Request).
So on this sample the extractor's numbered-line counts have no error found; the
independent counter had two.

P4 held for BM25: expected paper in the top 10 for 27 of 32 (84 %), expected lines (+-5)
for 21 of 32 (66 %), mean reciprocal rank 0.71. Missed papers: q07 (machines of
2611.12831), q11 and q12 (2609.14218, slicing and eigenvalues: mathematics-heavy), q17
(2507.18312), q24 (astro-ph/0110561). The hybrid sub-prediction is refuted: hybrid found
22 of 32 papers (69 %) and 15 locators, five fewer than BM25, with vectors for 21760 of
43398 chunks at run time [JUDGEMENT: fusing a vector ranking that covers half the chunks
pushes BM25's correct hits down; to re-test when all chunks are embedded].

P5: held for C1 (not ingested: gr-qc/9412071 only), C3 (25 not ok: 23 review, 1 pdf,
1 failed), C10 (27 of 27 suite references ingested), bibliography with an arXiv id 59.9 %.
Refuted as worded for the in-corpus fraction: 11.9 %, outside 15 +- 1 %. Cause, checked
with a query in which it could have failed: I counted citation rows (one per `\cite`
occurrence, 104726), K3 counted distinct (citing, cited arXiv id) edges; with K3's
definition the base gives 5700 of 38406 = 14.8 %, inside the band. The report now gives both.
New finding of C2: 37 papers with status ok have no section row; read for 7 of them
(1505.04756, 2504.15978, 0710.5073, 1207.1286, 2311.17644, 2312.03860, gr-qc/0511048):
none has a `\section` command (letters). The rerun separates "no sectioning command"
from "command present, nothing extracted".

## P6 (prediction, before the QA rerun with the corrected counter)

All 41 sampled papers agree exactly (the two fixes touch only the cases found); C2 finds
no paper whose flat.tex has a sectioning command but no extracted section. Refuted by any
mismatch or any such paper.
