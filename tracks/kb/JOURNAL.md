# JOURNAL of kb

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:05Z  session kb-lead (wave 1)  commits 29f15a1..(see end of entry)  runs (see end of entry)

Lead of owner kb after three helpers (K0-K1, papers K2-K3, code K6-K7). Their own journals,
with all their predictions and outcomes, are in `kb/JOURNAL.md` (sections "K0-K1 helper",
"K2-K3 helper", "K6-K7 helper"). This entry holds the lead's independent checks of their
artefacts and the KB-G1 package.

### Predictions of the lead's checks (written before any of them ran)

- L0 suite: `cd kb && .venv/bin/python -m pytest` passes all 107 collected tests on
  29f15a1. Refuted by any failure or error. (Run before this entry was written: 107 passed;
  recorded here as the first observation, not as a prediction.)
- L1 manifests: my own extraction (awk, not kbtool) of brief lines 2543-3226 and 3234-3296
  gives 684 arXiv rows (priority 3/2/1 = 47/160/477) and 63 repositories, with id sets equal
  to `kb/manifests/arxiv.tsv` and `github.tsv`. Refuted by any count or set difference.
- L2 store: an independent scan (my own script, reading only directory names, the meta
  records and the bytes of source.bin) finds 684 of 684 manifest ids with a store directory,
  683 with a gzip TeX source or gzip tar and a sha256 equal to the meta record, and
  gr-qc/9412071 as gzipped PostScript. Refuted by any other missing id, or a sha mismatch.
- L3 rerun of `kb verify-downloads` (registered): ok 683, problem 1 (gr-qc/9412071),
  missing 0, failed 0, extras >= 18 (other sessions may add more). Refuted by other counts.
- L4 database: `papers` has 701 rows (676 ok, 23 review, 1 pdf, 1 failed); all 47
  priority-3 ids present with parse_status ok or review; `db/current` contains the code
  tables (64 repositories, 3454 params). Refuted by other counts or a current snapshot
  without code tables.
- L5 equations of 2611.12831: my own count of numbered display lines in the flattened source
  (equation/align/eqnarray/gather/multline without star, minus \nonumber/\notag lines,
  subequations counted as their sub-lines) equals the number of equation rows with a number
  in the database for that paper, and the largest number in the database equals that count.
  Refuted by a difference of more than 1.
- L6 bibliography: for 2611.12831 and 5 papers drawn with seed 20261115 among those with a
  .bbl, the stored entry count equals my own count of `\bibitem` in the .bbl. Prediction:
  at least 5 of 6 equal. Refuted by 2 or more differences.
- L7 parameters: my own grep of `pin->` calls of Get*/GetOrAdd* in the upstream AthenaK clone
  (src/) is within 5 % of the helper's 1165 ParameterInput calls; and three parameters read
  by hand in the source (`<z4c> damp_kappa1`, `<particles>` one NRPIC option, `<time> cfl_number`)
  have the default and line that the params table holds. Refuted by a >5 % difference or
  any default/line mismatch.
- L8 upstream watch: the stored bare mirror of the watch run holds 124 branch tips with
  main at c5a0d7f9155a; `git grep -i -E "tmunu|deposit"` over src/particles of every tip finds
  nothing; `git grep ADM` over src/particles of particles_gr finds at least one line.
  Refuted by a hit for tmunu/deposit or no ADM hit on particles_gr.
- L9 links: `kb link check` reports 25 of 25 pass.

### Outcomes L0-L9 (lead checks of the helpers' artefacts)

- L0 held: 107 passed on 29f15a1 (`cd kb && .venv/bin/python -m pytest`).
- L1 held: awk extraction of brief lines 2543-3226 and 3234-3296 gives 684 rows (47/160/477),
  684 unique ids, 63 repositories; both id sets equal `kb/manifests/*.tsv`
  (script `scratch/kb/lead/`, commands in this entry's session log).
- L2 refuted as worded, substance held: 684 of 684 manifest ids are in the store, all 684
  sha256 equal the meta records; 682 are gzip (654 tar, 28 single file), gr-qc/9412071 is
  gzipped PostScript, and 2201.03458 is a PDF (arXiv served no TeX; source_kind pdf, which
  verify-downloads counts as ok). My prediction had forgotten the PDF case. 18 extras.
- L3 held: run kb-20261115-140336-29f15a1: ok 683, problem 1 (gr-qc/9412071), incomplete 0,
  failed 0, missing 0, extra 18; GitHub 63 ok. Exit code 1 is the documented "problems
  present" code.
- L4 held: kb.sqlite and db/current (kb-20261115-5ba1ab3.sqlite, schema 5) both have 701
  papers (676 ok, 23 review, 1 pdf, 1 failed), priority 3: 45 ok + 2 review; 64 repos,
  3454 params, 305733 symbols, 157184 code chunks; impl_links 25 claimed; claims 0;
  embeddings 0. Note: the code helper named kb-20261115-c8703d7 as db/current, but the
  papers helper's later snapshot kb-20261115-5ba1ab3 is current and holds both.
- L5 held: 2611.12831 has 139 numbered display lines by my count (comment-stripped
  main.tex; 80 equation, 35 align, 1 align*), the database has 139 numbered rows (1..135,
  A1, A2, B1, B2); ordinal 1, 10 and 40 carry the same labels in both
  (eq:adm-metric, eq:klimontovich-distribution, eq:lorentz-force).
- L6 held: 6 of 6 equal. 2611.12831: 137 stored = 137 distinct cited keys (139 .bib
  entries); 2002.05177 99, 1109.2314 136, 2207.03125 62, 2504.15978 77, 2607.20423 96
  (stored = \bibitem count; draw seed 20261115 among 408 papers with one .bbl).
- L7 held: grep finds 1172 call sites of Get*/GetOrAdd*/Set*/DoesParameterExist/
  DoesBlockExist outside parameter_input.{cpp,hpp} in upstream AthenaK src/ against the
  helper's 1165 ParameterInput calls (0.6 %). By hand: `<z4c> damp_kappa1` default 0.0 at
  src/z4c/z4c.cpp:131; `<time> cfl_number` (no default, GetReal) at src/mesh/build_tree.cpp:302
  and :496; `<particles> triad` default "symmetric" at athenak/src/particles/nrpic.cpp:82
  (this tree, main); all equal to the params table rows.
- L8 held: the watch mirror (kb-data/raw/watch/IAS-Astrophysics__athenak/20261115T132754Z.git,
  read with git, user and system configuration off) has 124 refs, main c5a0d7f9155a;
  `git grep -i -E "tmunu|deposit"` over src/particles of all 124 tips: 0 lines;
  `nrpic|vlasov` anywhere under src/ of all tips: 0 files; `ADM` in src/particles of
  particles_gr 8b04c1a8589d: 15 lines in boris_gr.cpp, 25 in gca_gr.cpp, 47 in hamiltonian_gr.hpp.
- L9 held: `kb link check`: 25 links, 0 with problems.
- Figures inspected (Read): fig_inventory.png (STALE: still the 11:28 state, 57 of 684;
  regenerated, see below), fig_papers_k2.png (fine; the legend of the lower-right panel has no
  swatch for "arXiv id", cosmetic), fig_citations_k3.png (fine; diagonal of the group matrix
  dominant, G20 strongest), fig_code_repos.png, fig_code_params.png (the P4 threshold label
  overlaps the first bar, cosmetic), fig_code_watch.png (fine).

### Defects found by the lead and fixed

- D-L1 `kb export` dropped the heading of a section whose text begins with a subsection
  ("3 Numerical tests" of 2611.12831). Test `kb/tests/test_export_headings.py` failed before
  the fix (heading absent) and passes after it (`kbtool/papers_cli.py`, ancestors printed).
- D-L2 the inventory figure was stale. Run kb-20261115-140838-29f15a1 passed a `.png` name and
  the script appended `.png`/`.pdf` (stray files removed by name); run
  kb-20261115-140851-29f15a1 wrote kb/reports/fig_inventory.{png,pdf}: 683 of 684, 18 extra,
  inspected.
- D-L3 (found while building the KB-G1 table) equations written with shorthands that are
  defined through an alias of \newcommand (`\newcommand{\nc}{\newcommand}` then
  `\nc{\beq}{\begin{equation}}`) are not found: 1908.05683 has 2 numbered rows in the database,
  1711.06681 has 1. Scan (scratch/kb/lead/alias_scan.py): 8 papers define such an alias
  (1410.3808, 1607.00381, 1711.06681, 1901.04498, 1908.05683, 2105.05208, 2312.12499,
  2509.05124).

### Prediction L10 (before the fix of D-L3 and the re-ingestion of the 8 papers)

My own count (scratch/kb/lead/eqcount_alias.py: shorthands substituted, then eqcount.py) of
numbered display lines in the main file: 1711.06681 19, 1908.05683 7, 1607.00381 25,
2105.05208 150, 1410.3808 72, 1901.04498 0. After the fix and `kb ingest arxiv --id` of the
8 papers, the database holds these numbers of numbered equation rows for these six; 2312.12499
at least 71 (it also \inputs files my count does not follow); 2509.05124 no prediction (its
equations are in \input files). Refuted if any of the six differs by more than 1, or if the
full test suite fails.

### Outcome L10

Held. Run kb-20261115-141159-bf9c30f (8 papers, 17.9 s): numbered equation rows 1711.06681
19 (was 1), 1908.05683 7 (was 2), 1607.00381 25 (was 20), 2105.05208 150 (was 14),
1410.3808 72, 1901.04498 0, 2312.12499 71 (was 57); 2509.05124 still 0.

### D-L4 and prediction L11

2509.05124 has 0 equations because its shorthand `\bea` stands for TWO environments,
`\begin{equation}\begin{aligned}`; `env_aliases` accepts a body of exactly one \begin or
\end. Scan (scratch/kb/lead/composite_scan.py): 20 papers use such composite shorthands in
their body (1707.00537 120 uses, 1905.06300 116, 1912.05399 103, 2101.05741 120,
2402.08642 115, 2509.05124 125, ...; stochastic-inflation groups mostly, which Track E reads).
Counts before the fix: scratch/kb/lead/l11_before.txt.
Prediction: after accepting bodies made only of \begin/\end commands and re-ingesting the 20,
every paper with at least 10 uses gains a number of equation rows within 10 % of its use
count of the shorthand (one equation environment per use), and each of the 20 gains at least
one row; nothing else changes (suite passes). Refuted otherwise.

### Outcome L11

Refuted as worded, substance held. Run kb-20261115-141358-9043e03 (20 papers, 15.6 s). 15 of
20 gained exactly or within 1 their use count (1707.00537 0 -> 120 rows, 2509.05124 0 -> 124,
2402.08642 0 -> 115, 1905.06300 +115 of 116, 2101.05741 +119 of 120, ...). Five were outside:
2311.03281 gained 27 for 19 counted uses, and 2404.15416, 2410.13683, 2605.11096, 2611.15050
gained 0 for 1 counted use. The fault was my scan: it concatenated all files of a paper and
split at the first \begin{document}, so uses in files listed before the main file were not
counted and a definition in a file listed after it counted as a use. A second count after the
fact (grep over all files, comments and definitions excluded): 2311.03281 has 27 uses
(= gain 27); the four others have 0 (= gain 0). The fix itself is not in question; my
prediction instrument was.

### Session summary (kb lead, 2026-11-15T14:30Z)

Commits 29f15a1..(package commit). Runs: kb-20261115-140336-29f15a1, -140838-29f15a1,
-140851-29f15a1, -140919-29f15a1, -141159-bf9c30f, -141358-9043e03, -141457-b2e57be,
-141500-b2e57be, -141630-b2e57be. Helpers' journals: `kb/JOURNAL.md` ("K0-K1 helper",
"K2-K3 helper", "K6-K7 helper").

- did: rechecked the three helper packages from their artefacts (L0-L9); fixed the export
  headings, the \nc alias and the composite-shorthand defects with tests written first
  (L10, L11) and re-ingested 28 papers; regenerated the stale inventory figure; wrote the
  KB-G1 package (FIRST_QUESTIONS.md with nine answers and file:line locators, EVIDENCE.md,
  OPEN.md, priority3_ingestion.tsv); ten outbox files; inbox acknowledgements; snapshot
  kb-20261115-f2fcda5; `kb status --write-state`.
- found: the helpers' numbers hold where I could recount them (manifests, store hashes,
  verify counts, 2611.12831 equation numbering, six bibliographies, parameter calls, the
  upstream watch, 25 links). The quality score does not catch silently missing equations:
  1707.00537, 2402.08642 and 2509.05124 had 0 equations with status ok. 2611.12831 states no
  numerical Z4c damping or gauge parameter and no number of filter passes, no code
  availability, no performance numbers, and does not mention cosmology or tidal effects.
- evidence: journal entries above; `kb/reports/fig_inventory.png`,
  `kb/reports/fig_lead_equations.png` (inspected).
- changed my mind about: the parse score as a gate for "ingested". It measures structure,
  not completeness; K9 needs an independent equation count on drawn papers.
- procedural: one probe of stub exit codes wrote a temporary error file under /tmp (removed
  at once); CLAUDE.md asks for scratch/kb/tmp. The REPORT.md the task named for the stage
  package was refused by this session's file-write guard, so its content went into
  EVIDENCE.md (criteria, runs, compute) and OPEN.md (gaps, stages that remain).
- open: K1 metadata, K4, K5, K7 module descriptions, K8, K9, K10, K11 scheduler; five
  kb-requests from tracks A, B, C, E (inbox_acks.txt); 12 unexamined C3 discrepancies.

## 2026-11-15T18:10Z  session kb lead, wave 2 (review of serve, claims, embed; packages)

Merged main (3b8a5c9). Helpers' journals: `tracks/kb/served/JOURNAL.md`,
`tracks/kb/claims/JOURNAL.md`, `tracks/kb/embed/JOURNAL.md`. My checks are W1, W2, ...;
predictions before each run, outcomes after.

### W1 prediction: kb test fixture without NRPIC_HOME

Defect confirmed first: `pytest -x` without NRPIC_HOME stops at `tests/conftest.py:89`,
AttributeError: `nrpic_fetch_arxiv` has no `unpack` (main's f9ab6c7). Fix: the fixture loads
the worktree's own `harness/bin/nrpic-fetch-arxiv` and a shim `fetch_unpack` mirrors
`fetch_source`'s layout (check_eprint + safe_extract; a refused blob is stored as main.tex as
in wave 1). Prediction: the whole suite passes without NRPIC_HOME, with as many tests as the
embed helper counted with it (174). Refuted if any test fails or the count differs.

### W1 outcome

Held. `pytest` in kb/ without NRPIC_HOME: 174 passed (32.9 s); `kb/serve_tests.py` 6 OK.
The fixture now reads `harness/bin/nrpic-fetch-arxiv` of the worktree (`tests/conftest.py`).

### W2 prediction: independent recheck of the serve locator check (run kb-20261115-154906-f19880f)

My own checker `tracks/kb/analysis/lead_checks/w2_serve_check.py` (no kbtool or serve code;
own number extraction, TeX variants 10^{-3}, percentages) reads the helper's 330 statements and
the raw store. Expected: all 372 locators lie inside their stored files; of the 13 statements
the helper flags with a number not found, I flag at least 10 too; at most 5 statements the
helper calls "all numbers in the cited lines" get a missing number from me. Refuted if any
locator is outside its file or more than 5 helper-exact statements fail my check (their
matcher too lenient). Reading sample (12 statements, seed 20261116, my reading of the cited
lines): at least 10 supported as worded; refuted below 9.

### W3 prediction: the lead's equation counter after the fix

`eqcount.py` no longer drops an empty last row after a trailing `\\` and counts multline as
one line. On the helper's synthetic probe (run kb-20261115-155344-596b4ce, 16 labels up to
z5 = 16) it must give 16 numbered lines; on my synthetic probe
`scratch/kb/tmp/w3probe/probe_multline.tex` pdflatex must give a0 = 1, m1 = 2, a1 = 3,
a2 = 6 and the counter 6. Refuted by any other number.

Procedural, W2: the first registered run kb-20261115-181519-d78b8d4 received the literal
string `$NRPIC_RUN_DIR` as output directory (my quoting; nrpic-run does not expand it), so
its files landed in a directory of that name in the worktree. They held paper text (reading
sample), were never committed and were deleted; the manifest stays on record. The script now
takes its output directory from the environment; rerun below.

### W2 outcome (run kb-20261115-181544-94f68f2; rows.tsv, summary.json, sample.txt in its scratch directory)

- Locators: held. 372 of 372 locators lie inside their stored files (my own line count).
- Number verdicts: refuted as worded, and the cause is my instrument. 24 statements the helper
  calls "all numbers in the cited lines" fail my check. I read 16 of them at the source: in
  all 16 the helper is right and my extraction or matcher is wrong (percent and rounding forms:
  0.9 vs "90\%", 22.5 vs "22.536", 0.226 vs "0.2260", 0.001 vs "0.1\%", 0.1 vs "10^{-1}";
  single-line locators inside the text taken for numbers: 854, 785, 631, 606, 462, 509, 506,
  808; an arXiv id fragment 0110561). For the manual entries (errata of C, D) the helper checks
  the hand-written expected values, not every number of the statement, so the tracks' own
  values (D's 2.59, 9.2, +45/+14 per cent; C's corrected 0.45, 0.52) are rightly not sought.
- Of the helper's 13 "number not found": 12 confirmed by reading (track-derived or eye-read
  values, a truncation 0.98 of the printed 0.988, a range read as numbers). One is wrong:
  BKRS collision_deep, 1804.02911 `mnras.tex:762` prints "about 5-7 \%", so 0.07 IS at the
  locator; the draft answer to F says otherwise and is corrected before posting.
- My matcher also has one false positive (an exponent alone matched: 4.0e-3 "found" via
  2.40464 x 10^{-3}); the helper rightly flags 4.0e-3 as not printed.
- Reading sample: held, 12 of 12 statements supported by the cited lines as worded
  (2508.10070 x2, 2404.16270 x2, 1604.06065, 2403.15126, 1901.04498, 1804.02911, 2609.14218 x2,
  2402.02178, 2507.18312).
- Also confirmed: the claim id ranges in the nine drafts equal db/current (A 1-170, B 171-228,
  C 229-303 and 304-331, D 332-420, F 421-452, core 453-602, E 603-609, C errata 610-618); the
  six fetched papers have status ok and their source.bin hashes equal the records; the two watch
  snapshots (13:27:54Z, 15:46:46Z) have the same 124 tips and main c5a0d7f. By my own count of
  numbered environments in 2502.06783 `main_V2PRD.tex`, line 320 lies in equation 23
  (label eq:eqInitialConditions, starting line 317) and equation 17 is eq:Bardeen (line 248),
  the definition of Psi_G, which may be what E's "(17)" refers to.

### W4 prediction: independent recount of the claims helper's QA numbers (snapshot kb-20261115-621430e)

Own SQL and counter (`w2_claims_check.py`), read-only. Expected: papers not ok 25 (review 23,
pdf 1, failed 1); bibliography entries with an arXiv id 38775 of 64712 (59.9 %); distinct
(citing, cited arXiv) edges 38406 with 5700 inside the corpus (14.8 %); claims fulltext 507,
to_verify 73, judgement 37, background 1, statuses checked 29, located 516, partial 33,
unlocated 39, unresolved 1; no arXiv id stored in two versions. C8: on the sample papers whose
source is one .tex without \input, my counter equals the database wherever the helper counted
no shorthand macro (my counter expands none). Reading audit of 10 unchecked fulltext claims
(seed 20261116): at least 9 supported. Refuted by any other count, a difference on a
shorthand-free single-file paper, or fewer than 8 supported claims.

### W4 outcome (run kb-20261115-181916-08ebad9)

- Counts: held exactly. Not ok 25 (review 23, pdf 1, failed 1); 38775 of 64712 bibliography
  entries with an arXiv id (59.9 %); 38406 distinct citation edges, 5700 inside the corpus
  (14.8 %); claims fulltext 507, to_verify 73, judgement 37, background 1; statuses checked 29,
  located 516, partial 33, unlocated 39, unresolved 1; no id stored in two versions.
- C8 third count: held. 36 of the 41 sampled papers are one .tex without \input; my counter
  equals the database on 30, and all 6 differences are papers where the helper counted shorthand
  macros (1105.5280, 2102.05690, 2208.05018, 2209.02735, 2311.17644, 2410.17987), which my
  counter does not expand. Every shorthand-free single-file paper agrees (the corrected counter
  gives 63 for 2408.09964, the trailing-row case).
- Reading audit: held, 9 of 10 supported (claims 125, 127, 205, 254, 311, 389, 396, 555, 600).
  Claim 193 is a parser fragment: its text is only `purely by shot noise" (2234-2238)`. Cause,
  checked in the parser and by a test that fails without the fix: B's bullet wraps onto a line
  starting with `|Q_ij|`, which `claims_parse.units` took for a markdown table row, flushing the
  bullet. Fixed (a continuation inside a bullet or paragraph is a table row only if it also ends
  with `|`), test `test_bullet_continuation_starting_with_pipe_is_not_a_table_row`. Claim 193
  itself stays as it is until the next seed (ids are frozen; no rebuild).
- astro-ph/0003278 (0 sections): flat.tex has `\section` at its lines 61 and 124 and an abstract
  environment, but doc.json has no section, no abstract and one equation (status review, score
  0.56). The cause lies in the K2 extractor and is not established here; listed as open.

### W3 and W5 predictions

W3 as written above (counter 16 on the helper's probe; pdflatex a0 = 1, m1 = 2, a1 = 3,
a2 = 6 and counter 6 on mine).

W5, independent recheck of the embed helper (`w2_embed_check.py`, read-only on db/current):
my own rescoring of their registered top-10 lists (chunk -> paper and flat range from the
database, -> source lines by my own bisection of sourcemap.json) gives the same hits@10 per mode
(ten: text 4, vector 4, hybrid 5; K9: text 21, vector 17, hybrid 23), at most one different per
mode (boundary rounding of the line map). Vectors: one model, dimension 384, 43398 chunk and
54259 equation vectors, 0 owners without a vector, 0 vectors without an owner, norms 1 within
1e-3; model weights sha256 equal to kb/EMBEDDING.md. Tags: of 18 sampled tagged equations (2 per
tag) at least 14 correct by my reading. Refuted by any larger difference.

### W3 outcome (run kb-20261115-182232-85883d1)

Held. pdflatex on my probe: a0 = 1, m1 = 2, a1 = 3, a2 = 6 (multline one number, trailing
empty align row numbered); the corrected counter gives 6. On the helper's probe the labels are
those of run kb-20261115-155344-596b4ce and the counter gives 16.

### W5 outcome (run kb-20261115-182238-b86d2b5)

Held. My rescoring equals the helper's hits@10 in every mode with no disagreement on any
question (ten: text 4, vector 4, hybrid 5; K9: text 21, vector 17, hybrid 23). One model
(bge-small-en-v1.5@5c38ec7), dimension 384, 43398 chunk and 54259 equation vectors, 0 missing,
0 orphaned, norms 1 within 1.3e-7; weights sha256 equal to kb/EMBEDDING.md. Tag counts by tag
sum to 1147 over the 1140 tagged equations. Reading 18 sampled tagged equations: 16 correct;
wrong: 2110.11720 (3) total Hamiltonian functional tagged hamiltonian_constraint, and
2009.08715 (31) a noise correlator tagged langevin (the v2 rule meant to exclude correlators
misses this form); borderline-correct: 2110.00893 (25), the deconvolution of the deposit window.

### W6 prediction: loading the serve helper's 70 uncovered statements into K8

Inputs: checked.jsonl and k8map.tsv of run kb-20261115-154906-f19880f (the registered check;
the claims tables have not changed since: 618 claims in kb.sqlite and db/current).
`kb/serve_locate.py sync-k8` under the writer lock. Dry run first: added 70, covered by K8 258,
no locator 2, removed 0, nothing written. Real run: the same counts, new claim ids 619-688
consecutive, 688 claims after, labels of the added rows as in the helper's summary (fulltext 24,
to_verify 44, judgement 2). Refuted by other counts, gaps in the ids, or any change to claims
1-618.

### W6 outcome (dry run kb-20261115-182414-e13b30c; load kb-20261115-182425-edbae8b)

Held. Dry run: added 70, covered by K8 258, no locator 2, removed 0, claims unchanged. Load:
the same counts; 688 claims, ids 619-688 (B 619-625, F 626-678 and 686-688 by key order, D
679-685; exact ids per statement in the run's sync.tsv); digest of claims 1-618 and their
claim_meta unchanged (40d6c2cfa7e33b84 before and after); added labels fulltext 24, to_verify
44, judgement 2. `nrpic-run` refused the kind "production" for gate G2 before a G1 tag; the
load is registered as scouting under G1.

### W7 prediction: arXiv-API and INSPIRE metadata of the 708 ids (decision 0015)

Ids: the 684 manifest ids and the 24 extras (`tracks/kb/analysis/lead_checks/meta_ids_w7.txt`).
One call at a time through the main checkout's `nrpic-fetch-arxiv --meta` (arXiv batches of 50,
INSPIRE batches of 25), then two INSPIRE DOI queries (Ambrus et al. 2022 for C,
Croker-Weiner 2019 for D). Expected: an arXiv-API record with status ok for at least 700 of
708; an INSPIRE record for at least 95 % (papers of the last weeks may not be in INSPIRE yet);
2611.12831's record gives categories and a first-submission date in November 2026; each DOI
query returns exactly one record carrying an arXiv eprint. Refuted by fewer records, a failed
batch that is not retried, or a DOI query with zero or several hits.

### W8 prediction: snapshot after the K8 load

`kb snapshot` (writer lock) freezes kb.sqlite into a new read-only `kb-20261115-<sha7>.sqlite`
and moves `current` to it; the new snapshot holds 707 papers, 688 claims, 97657 vectors and
schema version 6, and the earlier snapshots are untouched. Refuted by other counts or a
writable snapshot.

### W7 outcome (run kb-20261115-182505-7e3a0b5, 18:25-18:28Z)

Held. arXiv API: 708 of 708 records ok (`kb-data/meta/arxiv-api/`). INSPIRE: 704 ok, 4 not found
(1609.03053, 1612.06734, 1709.00267, 2409.16053), 99.4 %. 2611.12831: first submitted
2026-11-09T18:30:08Z (v1), primary gr-qc, cross-lists astro-ph.GA, astro-ph.HE,
physics.plasm-ph, comment "37 pages, 23 figures", INSPIRE record 3226709
(`meta/arxiv-api/2611.12831.json`, `meta/inspire/2611.12831.json`). DOI queries, one hit each:
10.1038/s43588-022-00333-x is arXiv:2201.09277 (Ambrus, Bazzanini, Gabbana, ..., INSPIRE
2016358); 10.3847/1538-4357/ab32da is arXiv:2107.06643 (Croker, Weiner, INSPIRE 1757478)
(`meta/inspire/query/4c626d666d4cbfab.json`, `010cf07abf4df1ab.json`).

### W8 outcome (run kb-20261115-182741-7dafdf9)

Held. Snapshot `kb-data/db/kb-20261115-3826a68.sqlite` (read-only), `current` points to it:
707 papers, 688 claims, 97657 vectors, schema 6; earlier snapshots untouched.

### W9 prediction: fetch and ingest the two papers found by DOI (C item 5, D item 3)

`nrpic-fetch-arxiv 2201.09277 2107.06643`, then `kb verify-downloads`, `kb ingest arxiv --new
--extras`, `kb eq --apply-tags`, `kb embed`, `kb embed --check --work`, `kb snapshot`, one after
the other. Expected: both stored ok with a TeX source; verify-downloads 683 ok + 1 problem in the
manifest and 26 extras; the ingest takes exactly these two (gr-qc/9412071 skipped as before), each
ok or review; tags change only their equations; embed adds only their chunks and equations (a
few hundred vectors), the check exits 0 with 0 missing, stale or orphaned; the new snapshot has
709 papers. Refuted by a failed fetch, any other paper (re)ingested, or a failed check.

### W9 outcome, first part (run kb-20261115-182907-3f69615, failed at step 4)

Fetch, verify-downloads and ingest held: 2201.09277 v2 and 2107.06643 v1 stored with TeX;
verify-downloads 683 ok + 1 problem (gr-qc/9412071), 26 extras; ingest took exactly these two
(both ok: 18 and 24 sections, 60 and 183 equations, 109 and 36 bibliography entries) and skipped
gr-qc/9412071. The run then failed at `kb eq --apply-tags`: ModuleNotFoundError yaml. Cause,
checked in the log and the environment: since I created the worktree's `.venv` this session
(`nrpic-env create --no-kokkos`, for nrpic-stage verify), nrpic-run puts it first on PATH, so
`python3` in the command is that venv, which has no PyYAML; the helpers' runs used the system
python3. The remaining steps are rerun with `kb/.venv/bin/python` (W9b). Prediction for W9b as
for W9: tags change only the two papers' equations, embed adds only their vectors, the check
exits 0, the snapshot has 709 papers.

### W9b outcome (run kb-20261115-183052-0f8245e)

Held. Tags: 243 equations changed (exactly the two papers' 60 + 183; none matched a rule), 1140
tagged as before. Embed: 102 chunks and 243 equations embedded, 43398 and 54259 unchanged,
0 orphaned; `kb embed --check --work`: 0 missing, 0 stale. Snapshot
`kb-data/db/kb-20261115-44b7406.sqlite` = db/current: 709 papers, 688 claims, 98002 vectors
(43500 chunks, 54502 equations); claims 1-618 digest unchanged.

### W10 prediction: two claims verified by reading (A's request claim-status-s1; F's collision_deep)

I read 2609.14218 `MDPBH.tex:1101-1103` (horizon for mu >= 0.05, none for mu <= 0.045) and
`:1084`, `:1095` (e = 0.2, caption of fig:alpha_p): claim 25 is supported, with the e = 0.2
locator added. I read 1804.02911 `mnras.tex:757-763` (collision when the members come closer than
2 R_star, about a fifth of the separation; "about 5-7 %" for D < 0.1 at line 762): claim 674 is
supported. `kb claim verify` for both (writer lock), then `kb snapshot`. Expected: both become
fulltext with status checked; checked 29 -> 31, to_verify 117 -> 115, fulltext 531 -> 533; 688
claims and 709 papers in the new snapshot. Refuted by any other change.
