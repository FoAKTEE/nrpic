# Journal of the KB-G2 / KB-G0 verifier (wave 3, round 1, package verify_g2)

Independent verifier: given artefacts and criteria, not conclusions. Until the verdicts
are committed I do not open tracks/kb/stage/**, the lead's STATUS/HANDOFF/JOURNAL/RISKS/
PLAN-wave3, kb/QA_REPORT.md, kb/STATE.json, tracks/kb/{retrieval,pdf_meta,claims}/**, the
outbox of kb or scratch/orch. Database: only the frozen snapshot
`kb-data/db/kb-20261119-a782f1e.sqlite`, opened with `mode=ro&immutable=1`.

## Entry 0 (2026-11-20 22:17 UTC): start

- Worktree clean, branch kb/main at 8b24b590 (main already merged by another helper);
  no earlier state of this package (`git log -- tracks/kb/verify_g2` empty).
- Read: CLAUDE.md, CHARTER to "Gates of the knowledge base", RULES nrpic-run section,
  brief 1218-1461, decisions 0015, 0016, 0019, kb/README.md (commands).
- Snapshot first look (python sqlite, read-only): 710 papers; parse_status ok 684, review 23,
  pdf 3; priority 1/2/3 = 478/185/47; 21 groups G01-G21. [VERIFIED, query in entry 1 run]

## Entry 1: draw of the held-out set (step 1)

Plan: `scripts/draw_heldout.py --seed 20261120`, 24 papers; one slot per group (21) plus 3
slots to groups drawn proportional to size; priority quotas 4 x p3, 7 x p2, 13 x p1. I have
not opened kb/golden/questions.yaml, so the held-out papers may overlap with golden papers;
that is recorded, not avoided.

Prediction (D1): the draw is feasible within a few hundred shuffles and gives 24 distinct
papers covering all 21 groups; one or two of them have parse_status review or pdf (expected
24 x 26/710 = 0.9). Refuted if a group is missing or the assignment is infeasible.

Outcome (D1, run kb-20261120-222100-50182fe, 22:21 UTC): confirmed. 21 assignment
attempts; 24 distinct papers, all 21 groups (G07, G09, G13 twice); priorities 4/7/13;
parse_status ok 23, review 1 (2009.08715), no pdf paper. The ad-hoc preview before the
registered run gave the identical draw (diff of draw.json picks empty). [VERIFIED]

## Entry 2 (22:24 UTC): held-out questions written (step 1)

For each drawn paper I read the stored source (raw/arxiv/<id_>/<v>/src, read-only, with
Read/grep only) and wrote one question in my own words whose answer is a specific
passage away from the abstract (a number, a definition, a method statement or the
provenance of a result). Locators are file:line ranges of the source file. File:
`heldout.yaml` (24 questions; kinds: 9 number, 11 method, 2 definition, 1 provenance,
plus 1 number/method mix). Overlap with the golden set unknown (golden file still
unopened). Validated: YAML loads, 24 distinct papers, every locator file exists and the
line ranges lie inside it. Commit of heldout.yaml: see entry 3 (made before any search).

## Entry 3 (22:25 UTC; times of entries 2 and 3 corrected from `date -u`): commit of the held-out set; predictions for retrieval (step 2)

- heldout.yaml committed as **8fb37106** (pushed to origin/kb/main) before any `kb search`
  was run by me and before kb/golden/questions.yaml was opened. Correction of entry 2:
  the kinds are 10 number, 11 method, 2 definition, 1 provenance (24).
- Scoring definitions (fixed now, before the runs): paper hit = expected paper_id among the
  10 hits. Location: my own map from source lines to flat.tex characters (each expected
  line, comment-stripped, located verbatim in flat.tex; ambiguous matches resolved by
  nearness to the unique ones); the expected range is [first anchor, last anchor + line
  length). Location hit (strict) = a hit of the right paper whose [char_start, char_end)
  overlaps the expected range; location hit (slack) = overlap with the range widened by
  200 characters on each side (about two to three source lines). Rank = first rank that
  hits.

Prediction (R1, held-out set, 24 questions; my own words, not tuned):
| mode | paper hit in top 10 | location hit (slack) |
|---|---|---|
| text-only (BM25) | 70 % (17/24), range 55-85 % | 35 %, range 20-55 % |
| hybrid | 80 % (19/24), range 65-92 % | 40 %, range 25-60 % |
| rerank | 83 % (20/24), range 70-95 % | 55 %, range 35-75 % |
Reasoning [JUDGEMENT]: most questions carry a few domain terms (oscillon, Hernquist,
Gauss-Bonnet, tetrahedra, lapse) that BM25 can use; vectors help the paraphrased ones;
the answer passages sit in the body, so the location rate is well below the paper rate.
Refuted if: hybrid paper hit < 60 % or > 96 %; rerank location hit < 30 %; or rerank worse
than hybrid on paper hits by more than 2 questions.

Prediction (R2, golden set, read after the held-out runs): the golden set was written by
the package (decision 0016 asks >= 80 %); I expect hybrid paper hit >= 85 % on it and the
held-out rate 5 to 15 points below the golden rate (a sign of tuning on the golden set if
the gap exceeds 20 points). Refuted if golden hybrid paper hit < 80 % (then C4 fails as
stated) or if the held-out rate is above the golden rate by more than 10 points.

Prediction (R3, side effects): `kb search --db <snapshot>` opens the snapshot read-only
and writes nothing into kb-data (mtimes of db/ and logs/ unchanged by my runs). Refuted by
any new or changed file there attributable to my runs.

## Entry 4 (22:29 UTC): parse scan, definition and prediction (step 4)

Own scan `scripts/parse_scan.py` (definition of "parsed successfully" in its docstring:
S sections, E display equations >= half of my count, B bibliography >= half of my count of
the source bibliography when the paper cites, A abstract chunk with >= 50 % recall of the
metadata words). Debugged on the first 40 papers (ad hoc, not reported): the first form of
B compared with distinct cited keys and counted the `\citeauthoryear` inside inlined .bbl
text as citations; changed to compare with the source bibliography and to drop cites inside
`thebibliography`. My map of source lines to flat.tex (locmap.py) agrees with the tool's
sourcemap.json on all 24 held-out ranges (start offsets identical, ends within 3 chars),
and all 24 flat.tex files match papers.flat_sha256 of the snapshot.

Prediction (P1): under the recorded parse_status, ok = 684/710 = 96.3 % (from the query of
entry 0), ok or pdf = 687/710 = 96.8 %. Under my definition: 90-96 % (bibliography
failures of single papers seen in the trial: 0710.5073 with 28 \bibitem and no entry,
1005.4054 with 79 \bibitem and 17 entries); I expect B to be the weakest component and the
rate to fall below the 95 % bar with probability about one half. Refuted if my rate is
above 98 % or below 85 %.

Outcome of the first scan run kb-20261120-222948-fcdd5e7 (22:29 UTC): **superseded**, kept on
record. It gave 644/710 = 90.7 % under my definition, but reading its failure list showed two
defects of MY scan, not of the database: (1) for papers with a .bib file it compared with
all entries of the .bib (uncited ones too), e.g. 2606.02712 1732 .bib entries vs 138 cited;
(2) it did not know biblatex `\addbibresource` (2607.21308, 2610.23218 counted as "cites
but no bibliography"). Fixed: the expected count is the .bbl named like the main file (else
the largest .bbl), else the cited keys found in the .bib files (all under `\nocite{*}`),
else `\bibitem` in flat.tex; `.bib` files are found by basename. Added a lenient variant
A' (an abstract in papers.abstract counts). Ad-hoc rerun after the fix: 662/710 (93.2 %),
lenient 688/710 (96.9 %); the registered rerun follows (entry 5).

## Entry 5 (2026-11-21 07:49 UTC): restart after the usage-limit cut; outcomes of the runs left behind

The session of 2026-11-20 was cut at 22:35 UTC. This session continues from the worktree
(merged main at b0e1fafb). State found: the held-out search run kb-20261120-222546-ea894c8 had
ended by itself (exit 0 at 22:39:40 UTC, 72 calls, all rc=0) but was not finished; closed now
with `nrpic-run finish` (commit a2a10899). The registered parse-scan rerun
kb-20261120-223309-14e4cb6 and the 15-paper draw kb-20261120-223339-b842a8a (seed 20261121)
were complete and finished.

Outcome of P1 (registered rerun kb-20261120-223309-14e4cb6, scan.json): recorded status ok
684/710 = 96.3 %, ok or pdf 687/710 = 96.8 %; my definition (S, E, B, A) 662/710 = 93.2 %;
lenient (A' = abstract chunk or papers.abstract) 688/710 = 96.9 %. Components over all 710:
S 709, E 701, B 696, A 680. The prediction (90-96 %, refuted above 98 or below 85) is
**confirmed**; "B the weakest component" is **refuted**: A (abstract chunk with >= 50 % word
recall of the metadata abstract) is the weakest (30 failures; 21 of the 23 review papers fail
A). Whether these A failures are failures of the knowledge base or of my test is the subject
of the 15-paper source check (entry 7). [VERIFIED, run kb-20261120-223309-14e4cb6]

Golden file opened now (after the held-out set was committed at 8fb37106 and its search had
run): kb/golden/questions.yaml version 1, 32 questions, one expected paper each, answer
locations as question-level `file` and `lines` = [[a, b], ...]. My scorer's loader did not know
this form; I added it (score_search.py, load_golden) without changing the scoring rules of
entry 3. All 32 expected papers are in the snapshot (ad-hoc check of the loader).

## Entry 6 (2026-11-21 07:52 UTC): held-out retrieval scored; prediction for the source check

Outcome of R1 (score run kb-20261121-075156-b84a189 on the raw outputs of
kb-20261120-222546-ea894c8; 24 held-out questions, all 24 answer ranges mapped, my map and
the tool's sourcemap agree on every start offset, ends within 3 characters):
| mode | paper hit top 10 | loc strict | loc slack 200 | paper rank 1 |
|---|---|---|---|---|
| text-only | 21/24 = 87.5 % | 12/24 = 50.0 % | 13/24 = 54.2 % | 14 |
| hybrid | 22/24 = 91.7 % | 15/24 = 62.5 % | 15/24 = 62.5 % | 14 |
| rerank | 21/24 = 87.5 % | 13/24 = 54.2 % | 14/24 = 58.3 % | 14 |
The stated refutation bars of R1 are not met (hybrid 91.7 % is inside 60-96 %; rerank location
58 % > 30 %; rerank is one question below hybrid, not more than two), so R1 stands, but the
point estimates were too low: text-only paper hits 87.5 % lie above my range 55-85 % and the
hybrid location rate 62.5 % above 25-60 %. BM25 alone does better on my paraphrased questions
than I expected. Missed in every mode: H20 (1204.2019). Missed in some: H03 (only hybrid
finds it), H17 (text misses), H22 (rerank misses), H24 (hybrid misses). [VERIFIED, runs above]

Prediction (P2, the 15-paper source check of draw kb-20261120-223339-b842a8a, seed 20261121):
reading each source I will agree with my scan's S, E, B, A verdicts in at least 14 of 15
papers, and every failure verdict will turn out to be a real gap of the database (a
bibliography or an abstract present in the source and absent from the database), not an
artefact of my regular expressions. Refuted if two or more verdicts are wrong, or if any of
the failure verdicts (A for astro-ph/0306304, 2009.08715, 2403.15126, 2509.01320,
gr-qc/9906015; B for 2403.15126 and 0710.5073) is a scan artefact.

## Entry 7 (2026-11-21 07:57 UTC): outcome of the source check P2; predictions for C1, C5, C6, KB-G0

Outcome of P2 (draw kb-20261120-223339-b842a8a; I read each source with grep/sed, read-only):
- 9 of the 10 papers with status ok: the overall verdict (success) is right. Spot checks against
  the source: section commands equal my count in all 10 (e.g. 2610.08045 23, 2107.12735 33);
  .bbl rows equal the database's bibliography (2110.11249 58 = 58, 1701.00303 83 = 83,
  1303.2899 31 = 31, 1706.09309 63 = 63, 2104.12293 8 = 8); 2610.08045 has only a .bib
  (`\bibliography{biblio}`): 84 cited keys = 84 entries in the database.
- 0710.5073 (ok): the B failure is real. The bibliography is a `references` environment
  (REVTeX 3) with 28 `\bibitem` at backreaction2prdrv.tex:587-705; the database has 0 entries but
  51 citation rows.
- 2403.15126 (review): B and A failures real. 116 entries made by a custom `\sortbibitem` macro
  inside `thebibliography` (pII_GW_Vir_C2_Arx.tex:117-129, 1719 ff.); database 0 entries,
  122 citation rows. The abstract is a bold heading (line 171) with the environment commented
  out (line 185). My count of the source bibliography (1, the `\bibitem` inside the macro
  definition) is an undercount; the verdict is unaffected (database 0).
- 2009.08715 (review): A failure real (abstract as `{\bf Abstract}` at HDR.tex:223).
- 2509.01320 (review): A failure real (SciPost `\section*{Abstract}` at
  notes_cosmo_beyond_FLRW.tex:108); the text is in the database as a section, not as an
  abstract chunk.
- astro-ph/0306304 (review) and gr-qc/9906015 (review): A failure real (abstract unmarked:
  `\footnotesize` block at main.tex:34-50; plain TeX "Summary:" at main.tex:90). BUT my S and B
  verdicts are wrong for both: the papers have numbered sections written as bold or font
  headings (`{\bf I. Introduction}` main.tex:56; `{\rma 3.1. ...}` main.tex:599) and a reference
  list without `\cite` (`\item` list after "References" at main.tex:696; 21 `\ref` lines after
  main.tex:1250), none of which is in the database (0 sections, 0 bibliography entries). My scan
  passes S when there is no sectioning command and B when there is no `\cite`, which is too
  lenient for such papers.
P2 is **refuted** on its first bar (component verdicts wrong in 2 of 15 papers, 4 component
verdicts), **confirmed** on its second (every failure verdict is a real gap of the database).
Consequence: my rate 662/710 is an upper bound in this respect; the papers where S or B pass
only because the source has no sectioning command or no `\cite` are counted in the figure run
(step 7), which tells how large the bound's slack can be. [VERIFIED, sources at the locators]

Predictions (P3), checks script `scripts/checks_c1_c5_c6.py`:
- C1: all 684 + 26 = 710 manifest ids are in the snapshot, no extra paper, group and priority
  agree; all 63 + 1 repositories are present, each with a 40-hex commit and >= 1 file; the
  684 rows of arxiv.tsv are each found in the brief line SOURCE.json names. Refuted by any
  missing id or repository, or a repository without commit or files.
- C5: every snapshot file has mode 0444; the readers' default is db/current (static: the
  `open_for_read` function; dynamic: in a fake data root, `kb search` without --db finds the
  word that is only in the snapshot and not the word added to kb.sqlite afterwards, and the
  snapshot's bytes are unchanged by the reads). Refuted by a writable snapshot or a default
  that reads kb.sqlite.
- C6: sha256 of kb-20261119-a782f1e.sqlite starts with a782f1e; the earlier snapshots named in
  the wave-1/2 runs exist with matching sha prefixes; the snapshot's own ingest_log does NOT
  hold its own snapshot row (it is written into kb.sqlite after the copy, kbtool/db.py:192-195)
  but holds the rows of the earlier snapshots. "Locators carry it": I expect the answer of
  `kb search` to name the database file (text footer, JSON info.database) but no per-hit
  snapshot field; I will judge that as partly met. Refuted (for the sha part) by any prefix
  mismatch.
- KB-G0 C1: the directories of brief 12.2 exist; the reasons for the tools are NOT expected in
  kb/README.md (the brief asks for them in JOURNAL, which I may not open), so that part will
  likely stay NOT CHECKED.

## Entry 8 (2026-11-21 08:01 UTC): outcome of P3 (run kb-20261121-080038-306bcdd, checks.json)

- C1 **confirmed**: 684 + 26 = 710 expected ids, 710 papers in the snapshot, none missing, none
  extra, no duplicate id, group and priority equal to the manifests for all 710; every paper
  has chunks, a raw source.bin (or source.pdf) and, for the 707 TeX papers, a flat.tex. The 684
  rows of arxiv.tsv and the 63 of github.tsv are each found (by code, not read by me) in the
  brief line SOURCE.json names, and the brief's sha256 equals SOURCE.json's. Repositories: 64
  expected (63 + local/nrpic), 64 present, each with a 40-hex commit and files (smallest 46).
  Observations: 24 of the 64 repositories have a file inventory but no code chunks (no
  full-text code index; 19 of them have symbols, 5 have none); raw/arxiv holds 736 directories,
  26 of them not in the snapshot (fetched after it, presumably by this wave's ingest helper;
  not checked).
- C5 **confirmed**: all 9 snapshot files have mode 0444 (kb.sqlite 0644, the writer's); the
  readers' --help says "default db/current, else kb.sqlite" for search, show, eq, cites, code,
  frontier, export; `open_for_read` (kbtool/db.py:155-161) returns db/current when it exists, and
  readers open it with `mode=ro` (db.py:36-38). Dynamic: in a fake data root `kb snapshot` wrote
  kb-20261121-8832bb1.sqlite with mode 0444 and a matching sha prefix; `kb search` without --db
  found the word that is only in the snapshot (1 hit) and not the word added to kb.sqlite
  afterwards (0 hits; 1 hit with --db kb.sqlite); the snapshot's bytes were unchanged by the
  reads.
- C6: sha part **confirmed**: sha256 of every snapshot starts with the 7 hex digits of its
  name (all 9, among them a782f1e, and f2fcda5, 621430e, a848a06 named by the wave-1/2 runs);
  the snapshot's ingest_log holds 8 snapshot rows (b715da3 ... a848a06, 2026-11-15) and, as
  predicted, not its own; its last row is 2026-11-19T16:16:02Z, inside the run that took it
  (kb-20261119-161451-e15d1b8, 16:14:51-16:16:18Z): the snapshot was the last step after the
  re-index. Locators: the text answer of `kb search`, `kb eq` and `kb code` ends with
  "database .../kb-20261119-a782f1e.sqlite", the JSON of `kb search` has it in info.database;
  no hit carries it, and `kb show` and `kb cites` do not print it at all. Partly met, as
  predicted.
- KB-G0 C1: of the brief 12.2 layout all kb-data directories and files exist; in kb/ two
  named files are absent: `uv.lock` (the environment is frozen as requirements-k0/k4/k6.lock,
  README.md:26) and `curated/seed_claims.jsonl`. Reasons for tools: kb/EMBEDDING.md gives them
  for the embedding model and the fusion constant, pyproject.toml for tree-sitter over
  universal-ctags; for the rest (pylatexenc, bibtexparser, rapidfuzz, tenacity, sqlite FTS5)
  nothing in the files I may read. The 736 source.bin files are writable by their owner
  (0664), i.e. "read-only" raw files are a convention, not a file mode.
- Failed runs on record (manifests): 2 with status failed (kb-20261115-182907-3f69615,
  kb-20261119-143242-737909d); ingest_log of the snapshot records 2 ingest-arxiv failures,
  63 review and 5 skipped rows.

## Entry 9 (2026-11-21 08:03 UTC): the leniency of S and B, counted (step 4c)

`scripts/lenient_check.py` looks, in flat.tex of the 32 papers that pass only because they
have no sectioning command (23, S) or no `\cite` (9, B), for headings written another way and
for reference lists without `\cite`. No prediction was written before its first (ad-hoc,
debugging) run, whose output I saw; the registered run below repeats it and is recorded as an
unpredicted count, not as a test. Reading the flagged sources (grep, read-only):
- genuine section gap: hep-ph/9809574 (`{\bf I. Introduction}` ... `{\bf V. Discussion}`,
  flat.tex:85-437; database 0 sections);
- genuine bibliography gaps: 1201.4794 (AAS `references` environment with `\reference{}`
  author-year entries, flat.tex:1022 ff.; database 0 entries), gr-qc/0304002 (`\def\bi{\bibitem}`
  at flat.tex:22, `thebibliography` at 2983-3189; database 0), astro-ph/9607124 ("References"
  at flat.tex:421, numbered `\noindent[1]` list; database 0; not flagged by the heuristic);
- letters with run-in headings ("Introduction.--", `{\it Introduction}`, `\paragraph*`):
  1306.1562, 1408.2741, 1511.05124, 2006.01172, 2104.12293, 2105.11880, 2302.00655,
  2311.17644, 2504.15978. [JUDGEMENT] A letter has no numbered sections, so a missing section
  row is not a parse failure there; the run-in labels are lost, which costs little.
Corrected rates under my definition: lenient (A') 688 - 4 = 684/710 = 96.3 %; counting the
nine letters as failures too, 675/710 = 95.07 %; strict (A) 662 - 4 = 658/710 = 92.7 %.

## Entry 10 (2026-11-21 08:06 UTC): golden retrieval scored; outcomes of R2 and R3

Golden search run kb-20261121-074940-08426cc (96 calls, all rc=0, 07:49:41-08:05:44 UTC),
scored by kb-20261121-080557-06d44ba (37 answer ranges of 32 questions, all mapped; my map and
the tool's sourcemap agree on every start except q05, 15 characters apart):
| mode | paper hit top 10 | loc strict | loc slack 200 | paper rank 1 |
|---|---|---|---|---|
| text-only | 27/32 = 84.4 % | 20/32 = 62.5 % | 21/32 = 65.6 % | 20 |
| hybrid | 28/32 = 87.5 % | 23/32 = 71.9 % | 23/32 = 71.9 % | 17 |
| rerank | 28/32 = 87.5 % | 25/32 = 78.1 % | 25/32 = 78.1 % | 19 |
Missed: q12 (2609.14218) in every mode; q11 (2609.14218) and q24 (astro-ph/0110561) in text and
hybrid; q13 (2512.14649) in hybrid and rerank; q17 (2507.18312) in text and rerank; q06
(rerank) and q07 (text) once each.

Outcome R2: golden hybrid 87.5 % >= 85 % (confirmed); "held-out 5 to 15 points below golden"
**refuted**: the held-out set scores at or above the golden set (text 87.5 vs 84.4, hybrid
91.7 vs 87.5, rerank 87.5 vs 87.5). The stated refutation bars (golden hybrid < 80 %, held-out
above golden by more than 10 points) are not reached. No sign of retrieval tuned to the golden
set. The C4 bar (>= 80 % of golden questions with the right paper in the top ten) is met in
all three modes on the frozen snapshot, and also on my held-out set. [VERIFIED, runs above]

Outcome R3 (ad-hoc listing, scratch/kb/verify_g2/db_mtimes_{before,after}_golden.txt): the
listing of kb-data/db (sizes, modes, mtimes, among them kb.sqlite-wal) and of kb-data/logs is
identical before and after the golden search: confirmed for that run.

## Entry 11 (2026-11-21 08:07 UTC): the package's QA report read; prediction for the final tally

After entry 10 was committed (c2ccdc3d) I read the QA output of the named run
kb-20261119-161633-1d05960 (QA_REPORT.md, its sections C1, C2, C3 and C7; an output directory
the task lets me read). Its retrieval numbers are those I recomputed (entry 10). Its parse
section lists 26 papers not ok (pdf 3, review 23) and states no rate against the 95 % bar.

Prediction (T1) for `scripts/tally.py` on the registered scan and leniency outputs, gaps
hep-ph/9809574, 1201.4794, gr-qc/0304002, astro-ph/9607124 and the nine letters of entry 9:
mine (lenient, corrected) 684/710, with letters failed 675/710, strict corrected 658/710;
`kb show --abstract` on papers without an abstract chunk prints the metadata abstract (recall
of its words >= 0.9). Refuted by other counts (then entry 9 is wrong) or by an empty or
different abstract (then A' is not served and my definition falls back to strict A).

## Entry 12 (2026-11-21 08:08 UTC): outcome of T1; the leniency check had a hole

Tally run kb-20261121-080749-3dfab11: the counts are as predicted (684, 675, 658 of 710) and
`kb show --abstract` prints the metadata abstract for the 8 papers without an abstract chunk
I tried (recall of its words 1.0 in all 8), so A' is served. But its list of review papers
that pass my lenient definition contains astro-ph/0306304 and gr-qc/9906015, the two papers
whose S and B gaps I had read at the source (entry 7). Cause (my error): lenient_check.py
examined only the strict successes, not the lenient ones. T1 is therefore **refuted** in
substance: entry 9's count of genuine gaps was incomplete. Fixed: lenient_check.py now also
examines lenient successes. Ad-hoc rerun (debugging, registered rerun follows) flags five
review papers, all plain TeX or old styles with numbered headings and reference lists that
the database lacks (0 sections, 0 bibliography entries): astro-ph/0306304, astro-ph/9306009
(`{\bf I. INTRODUCTION}` ... `VI. CONCLUSIONS`), astro-ph/9510056 (A&A macros `\titlea`,
`\titleb` at flat.tex:1897-2260, `\begref{References}` with `\ref` entries at 2511 ff.),
gr-qc/9604001 (`{\bf 1. Introduction}`), gr-qc/9906015. All five are genuine gaps.
Corrected rates under my definition (S, E, B, A'): 684 - 5 = 679/710 = 95.6 % with the nine
letters counted as parsed, 670/710 = 94.4 % if they are not; strict A: 658/710 = 92.7 %.
Prediction (T2) for the registered reruns: lenient_check finds exactly these five more (17
flagged in all); tally with the nine gaps gives 679, 670 and 658.

## Entry 13 (2026-11-21 08:08 UTC): outcome of T2

Leniency rerun kb-20261121-080834-6c50215: 17 flagged (12 + the 5 review papers), as
predicted. Tally rerun kb-20261121-080843-98907be with the nine genuine gaps: status ok
684/710 = 96.3 %; mine (S, E, B, A', gaps corrected) 679/710 = 95.6 %; letters counted as
failures 670/710 = 94.4 %; strict A 658/710 = 92.7 %. Cross-tab of status against mine: ok and
pass 663, ok and fail 21 (13 bibliography, among them 1201.4794 and gr-qc/0304002; 7 equations;
1 sections, hep-ph/9809574), review and pass 13, review and fail 10, pdf and pass 3. Sensitivity: one paper of
mine has fewer than half of its sectioning commands as sections (2209.06775). T2 **confirmed**.
The bar (674.5 papers) is passed under my definition by 4.5 papers; my verdict on C3 rests on
the [JUDGEMENT] that a letter with run-in headings has no sections to lose.
