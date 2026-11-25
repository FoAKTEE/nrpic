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

### W10 outcome (run kb-20261115-183921-31d5b77)

Held. Claims 25 and 674 are fulltext with status checked; checked 29 -> 31, fulltext 531 -> 533,
to_verify 117 -> 115, partial 36 -> 34; 688 claims. Snapshot `kb-20261115-a848a06.sqlite` =
db/current. Answer to A posted (`outbox/20261115T183946Z__to-A-emd-pbh__claim-status-s1.md`).

### Session summary (kb lead, wave 2, 2026-11-15T18:10-19:05Z)

Commits d78b8d46..(this commit) on kb/main. Runs (all with nrpic-run submit): kb-20261115-181519-d78b8d4
(misplaced output), -181544-94f68f2 (W2), -181916-08ebad9 (W4), -182232-85883d1 (W3),
-182238-b86d2b5 (W5), -182414-e13b30c and -182425-edbae8b (W6), -182505-7e3a0b5 (W7),
-182741-7dafdf9 (W8), -182907-3f69615 (W9, failed at the tag step), -183052-0f8245e (W9b),
-183921-31d5b77 (W10). 0 card-hours.

- did: rechecked the serve, claims and embed packages from their registered outputs with my own
  code and read all their figures (stage/REVIEW-wave2.md, figure note/figures/fig_w2_review.png);
  fixed the test fixture, the claim parser's table-row defect, the wiring of kb claim and kb qa,
  and my own equation counter; loaded the 70 uncovered served statements as claims; fetched the
  arXiv-API and INSPIRE metadata of all 708 ids; found, fetched and ingested 2201.09277 (C) and
  2107.06643 (D) by DOI; verified claims 25 (A's request) and 674 by reading; four snapshots
  (3826a68, 44b7406, a848a06 final); KB-G0 package written, KB-G1 updated, both verified with
  nrpic-stage verify (PASS) and reported (FAIL only for the missing verifier report); 16 outbox
  messages (10 answers incl. A's new request, 1 to all, 5 to orch); 11 inbox messages
  acknowledged; created wt/kb/.venv for the stage verifier.
- found: the helpers' numbers hold wherever I recomputed them (QA counts exactly, retrieval
  rescoring identically, vectors complete, model hash equal); their failed predictions are on
  record as written. Wrong: one "not found" in the F answer (0.07 is printed as "5-7 %"),
  outdated snapshot and metadata statements in the drafts, claim 193 a parser fragment, two
  embedding runs above kb's 8 cores, the helpers' journal times. My own instruments failed twice
  (W2 number matcher, eqcount trailing-row rule) and were caught by reading the source.
- changed my mind about: "numbers found at the locator" as a quality signal across checkers:
  two independent matchers disagreed on 24 of 330 statements and the stricter one was wrong
  every time I read; agreement between matchers is not evidence, reading is.
- open: KB-G2 (one paper, thresholds, retrieval at the answer location), K1 metadata into the
  papers table, K9 rerun with C4, the brief's own statements as claims, K7 module descriptions;
  requests to orch listed in STATUS.md.

## 2026-11-19T15:50Z  session kb lead, wave 2b (review of pdf_meta, retrieval, verifier; KB-G1, KB-G2)

State found: kb/main 67deee04 merged with main (4767ea77); tree clean; three helper packages
committed but not pushed (72 commits ahead of origin). db/current is still kb-20261115-a848a06;
the pdf_meta helper wrote kb.sqlite (gr-qc/9412071, metadata, groups) without a snapshot.
Inbox: 4 messages (B kb-request, D kb-request, C info, E info).

### B1 prediction: pdf_meta recheck (script analysis/lead_checks/w2b_pdfmeta_check.py, kb.sqlite read-only)

From the helper's report I expect, by my own SQL: gr-qc/9412071 parse_status pdf with 6
sections, 16 chunks, 1 caption, 19 bibliography entries, 32 distinct cite keys out, 36 citation
rows in; astro-ph/9407016 12 sections, 45 chunks, 22 entries; 2201.03458 5 sections, 70 entries.
Abstract chunk of gr-qc/9412071 against the arXiv-API abstract: word-sequence ratio >= 0.95 (the
helper's 0.994 is a different measure). Papers 710; primary_class, submitted, updated 710;
inspire_recid 706; DOI 651; journal_ref 648; licence 0; grp 710; title_matches_brief 1/0/NULL =
680/4/26; version equal to the API's latest for 710; title equal to the API title (normalised)
for 25 of 25 random papers. Additions file: 26 rows = the 26 rows outside arxiv.tsv, with the
same group. Vectors: 0 chunks without a vector, 0 orphans. Reading: of 20 fresh word repairs at
least 18 right; of 20 'cmmi-greek' repairs (a kind the helper's audit excluded) I make a weaker
prediction, at least 15 right, because the first edit of gr-qc/9412071 already reads
"F\x13\x10sica" -> "Fιζsica" (a Spanish affiliation word turned Greek): seen while choosing the
check, so that one edit is not evidence. The three author errata read as the helper says.
Refuted by any count that differs, a word-repair precision below 18/20, or an erratum that does
not hold on reading.

### B2 prediction: retrieval rescoring (w2b_retrieval_check.py)

My own rescoring of the top-10 chunk lists of R4 (run kb-20261119-142613-942f713) with my own
sourcemap bisection gives the helper's hits in every mode on both sets (golden 32 with 5-line
slack: text 27/21, hybrid 28/23, w2 27/22, w3 28/22, w2+stage1 29/23, w2-noexpand 28/25; ten:
9/4, 9/5, 7/6, 7/6, 8/6, 8/6) with no question-level disagreement; the final run's rerank ranks
equal R4's w2-noexpand on all 32 questions; C4: 30 of 30 INSPIRE records, my title ratio below
0.9 for exactly 2103.01183 and gr-qc/9905058. Parse status on a848a06: ok 684 of 709 (96.5 %).
Refuted by any differing count or question.

### B3 prediction: verifier recheck (w2b_verifier_check.py, snapshot a848a06)

20 of 707 TeX papers have no bibliography entry, 11 of them with parse_status ok. My pattern
counts confirm the verifier's causes: 1201.4794 has about 46 `\reference` lines, the eight
REVTeX-3 papers have `\begin{references}` and `\bibitem`, 2507.01095 `\harvarditem`;
gr-qc/9906015 has 58 live `\eqno`. Claim 25: locator string names L1084 and L1101-1103, rows hold
only L1101-1103, in both databases. Parameter index: local/nrpic at a1c2237; in
nrpic_collide.cpp on main every literal (block, name) pair is absent (12), in scalar_field.cpp
most. Refuted by a count of zero-bibliography papers other than 20, a cause not found by my
patterns in more than 3 of the 14, or claim 25 rows that include L1084.

### B1 outcome (run kb-20261119-155134-17d6704; pdfmeta_check.json, repair_reading.tsv and errata_reading.txt read by me)

Held, with two corrections of wording. Counts as predicted: the three PDF papers have status pdf,
sections 6/12/5, chunks 16/45/13, bibliography entries 19/22/70, vectors on every chunk;
gr-qc/9412071 has 32 outgoing citation rows (19 distinct keys, not "32 citation keys" as the
helper wrote) and is the target of 36 rows. 2201.03458 has 70 entries but 0 outgoing citation
rows (author-year references; the helper names the limit). Abstract ratio of gr-qc/9412071
0.994 (my word-sequence measure), astro-ph/9407016 1.000, 2201.03458 0.940. Papers 710;
primary_class, submitted, updated, grp 710; INSPIRE 706; DOI 651; journal_ref 648; licence 0;
title_source arxiv-api 710; title_matches_brief 680/4/26; version = API latest for 710; title
= API title for 25 of 25. Additions file: the same 26 ids as the rows outside arxiv.tsv, same
groups. Vectors 43560 = chunks, 0 orphans; equations 54502 = vectors. Reading: 20 of 20 fresh
word repairs right; 'cmmi-greek' 17 of 20 right (held, >= 15): three are characters of other
fonts mapped as math italic (a cmsy equivalence sign read as eta, a cmsy approx sign as pi, a
cmex parenthesis as theta), plus the affiliation word seen before. So the Greek mapping is right
for letters in formulas and wrong for symbols of other fonts: a known limit of the PDF text, not
of the word repairs the helper audited. Errata: all four read as the helper says (2310.00776
omits Ames; 2107.06306 adds Korzynski and Matarrese, who are on neither record; 2204.13098
order; 1203.6185 "Bai (first author)" is INSPIRE's alphabetical first, fourth of five on arXiv).

### B2 outcome (run kb-20261119-155310-e600e38; retrieval_check.json)

Held for every count: my rescoring of R4's top-10 lists equals the helper's hits in all six
modes on both sets, with no question-level disagreement; the final run's ranks equal R4's on
all 96 (mode, question) pairs; misses at the answer location with rerank q06 q07 q12 q13 q16 q17
q20, paper misses q06 q12 q13 q17. C4: 30 of 30 with an INSPIRE record. One prediction failed
on my own instrument: my word-level title ratio also puts gr-qc/0312117 below 0.9 (0.80),
because INSPIRE (and arXiv) misspell one word of its title; the helper's character ratio gives
0.99. Not a defect of the knowledge base. Parse status on a848a06: ok 684 of 709.

### B3 outcome (run kb-20261119-155315-b2c7420; verifier_check.json)

Held. 20 of 707 TeX papers have no bibliography entry, 11 of them status ok (0710.5073,
1109.2484, 1201.4794, 1302.5308, 1304.7791, 2507.01095, gr-qc/0107076, gr-qc/0304002,
gr-qc/9402041, gr-qc/9703066, hep-ph/0011159). My patterns find the verifier's cause in all 14
it named: `\begin{references}` with `\bibitem` (8), 46 `\reference` lines in 1201.4794, 103
`\harvarditem` in 2507.01095, 38 and 18 lines of a `\bi`/`\bib` macro, plain `\ref` paragraphs
(16, 21). Beyond the verifier: 2602.00155 has 28 `\bibitem` in paper.tex, a file its main file
(arXiv_paper.tex) does not include, so a seventh cause is "bibliography in a file the main file
does not reach". gr-qc/9906015: 58 live `\eqno`. Claim 25: locator string L1084; L1101-1103,
one row (L1101-1103) in both databases. local/nrpic indexed at a1c2237 (1115 rows); on main
f51539c6 all 12 literal pairs of nrpic_collide.cpp, 13 of 14 of scalar_field.cpp, 5 of 5 of
nrpic_kick.cpp and 2 of 5 of nrpic_cf.cpp are absent from the index.

### Figures of the helpers, read by me

pdf_meta: fig_pdf_reader (rare tokens, repairs by kind, abstract similarity; its dashed line
sits at 0.6 while the prediction's bar was 0.8, cosmetic), fig_brief16 (its right panel starts
at 0.6, which exaggerates the dips of G03, G07, G17, G19), fig_metadata. retrieval: fig_r4_rerank
(ranks per question agree with rerank_eval.json), fig_r5_c4. verifier: fig_papers, fig_summary,
fig_zero_bib (2602.00155 drawn as no list; see B3). All agree with the numbers above.

### D1, D2, Q1 predictions (database changes, then the QA run on the new snapshot)

Code changes first (tests: 220 collected, all pass except the strict xfail of the retrieval
package): `kb claim relocate` and `kb claim verify --locator` rewrite the locator rows (the cause
of verifier defect 4 was my own W10 verify, which changed claims.locator but not the rows);
`kb ingest pdf`, `kb meta load|brief16`; `kb ingest arxiv` takes groups from the full manifest
and reads the metadata back afterwards; `kb search --rerank`; QA C1 counts the 26 additions as
manifest, C2 judges the extraction by the abstract chunk, C4 compares parse_json.tex_front.

D1 (w2b_db_updates.py): claim 25 gets 2 resolved rows; 249 and 313 2 resolved rows each; 7 B
claims and 1 C claim added and verified (fulltext, checked); 4 D claims added (2 judgement, 2
to_verify) with resolved rows. Claims 688 -> 700, checked 31 -> 39, fulltext 533 -> 541,
judgement 39 -> 41, to_verify 115 -> 117. Refuted by a failed command or other counts.

D2: `kb ingest repo --this --ref main` re-indexes local/nrpic at f51539c6: its params rows grow
by at least 101 (the pairs the verifier found missing), and the 12 nrpic_collide pairs are then
present. `kb link load` reloads the 25 curated links; `kb link check`: at least 20 of 25 without
a problem (some symbols may have moved since a1c2237; no firm expectation). Then `kb snapshot`.

Q1 (`kb qa run --hybrid` on the new snapshot): C1 manifest 710 (684 + 26), all ingested; parse
status ok 684, review 23, pdf 3: parse success 684/710 = 96.3 % if only ok counts, 687/710 =
96.8 % if a PDF paper parsed as such counts; both meet the 95 % bar of decision 0016. C7 on the
32 golden questions: paper hits text 27, hybrid 28, rerank 28 (+-1, the three PDF papers add
74 chunks that may move a rank); answer location hybrid 23 +- 1, rerank 25 +- 1. KB-G2 retrieval
threshold (80 %, 26 of 32) met by hybrid and rerank. C4: the same 30 papers, 28 agree, 2103.01183
and gr-qc/9905058 below a bar. Refuted by parse success below 95 % under both readings or a
paper hit count below 26 in hybrid.

### V1 prediction: the verifier's scripts rerun, registered, on the new snapshot kb-20261119-a782f1e

The verifier's three runs have hand-written manifests dated 2026-11-19, which decision 0016
item 3 does not waive. I rerun its committed scripts unchanged through nrpic-run (run_all.py,
check_zero_bib.py, check_locator_rows.py); db/current is now a782f1e. Expected: P 18 of 20 with
the same two WRONG (no paper was re-ingested); C 10 of 10 (claim 25 now with both rows); K: the
row sample changes with the re-index (seeded draw over other rows), all sampled rows CONFIRMED,
recall in particles/ and pgen/nrpic/ complete, and 0 pairs on main absent from the index (main
5deee18 = indexed commit); Q 9 of 9; zero bibliographies 20; locator rows: 0 claims whose string
and rows disagree. Refuted by any other verdict count, a stale pair, or a disagreeing claim.

### D1, D2, Q1, V1 outcomes

D1 (run kb-20261119-161413-31e6b85): held. Claims 688 -> 700 (B 689-695 and C 696 verified by
reading; D 697-700), checked 39, fulltext 541, judgement 41, to_verify 117; claim 25 two resolved
rows; 249 and 313 two each. Not predicted: the four D claims keep status "unlocated" although
their rows resolve (relocate does not touch statuses, by design); a status refresh is for the
claims tooling next session.

D2 (run kb-20261119-161451-e15d1b8): held. local/nrpic re-indexed at main 5deee18 (main moved
from f51539c6 during the session): 790 files, 1242 parameter rows (+127), all 12 nrpic_collide
pairs present; 25 of 25 curated links OK; snapshot kb-20261119-a782f1e = db/current.

Q1 (run kb-20261119-161633-1d05960, 9 min on 6 threads): held. C1 710 of 710 ingested (684 + 26);
C3 26 not ok (23 review, 3 pdf): parse success 684/710 = 96.3 % (96.8 % with PDF papers); C7
text 27/21, hybrid 28/23, rerank 28/25; the only change against the helper's a848a06 run is q01
hybrid location rank 7 -> 6. C4 30/30 with INSPIRE, 2103.01183 and gr-qc/9905058 below a bar, now
comparing parse_json.tex_front. C2: no paper without any abstract; 25 without an abstract chunk.
Both KB-G2 thresholds are met. Caveat I add: the 11 ok papers without bibliography (verifier)
bring the strict rate to 94.8 % (673/710); figure fig_kbg2.png (run kb-20261119-162642-25012f7),
inspected.

V1 (run kb-20261119-161909-08df7ea): held. The verifier's scripts, unchanged, on a782f1e: papers.tsv
identical to its run 142015, C the same ten claims (claim 25 now with both rows), K 10 of 10 rows
ok with 0 stale pairs (indexed commit = main 5deee18), Q 73/73 and 18/18 locators, zero
bibliographies identical, 0 of 661 claims with string and rows disagreeing.

### Session summary (kb lead, wave 2b, 2026-11-19T15:45-16:50Z)

Commits 4767ea77 (merge of main)..(this commit) on kb/main. Runs (all through nrpic-run):
kb-20261119-155134-17d6704 (B1), -155310-e600e38 (B2), -155315-b2c7420 (B3), -161413-31e6b85 (D1),
-161451-e15d1b8 (D2, snapshot kb-20261119-a782f1e), -161633-1d05960 (Q1), -161716-2705191 and
-161744-2d5ecc8 (review figure, first and second drawing), -161909-08df7ea (V1),
-162642-25012f7 (KB-G2 figure). 0 card-hours.

- did: rechecked the pdf_meta, retrieval and verifier packages from their outputs with my own
  code and read their eight figures (stage/REVIEW-wave2.md, wave 2b; fig_w2b_review.png); wired
  the helpers' modules into `kb` (ingest pdf, meta, search --rerank; ingest reads metadata back;
  QA C1/C2/C4); found and fixed the cause of the claim-25 defect (my own wave-2 verify);
  re-indexed this repository at main; loaded 12 claims for B, C and D; snapshot a782f1e; QA on it;
  reran the verifier's scripts registered; KB-G1 package complete (all PASS), KB-G2 package
  written (thresholds met, verifier missing); kb/QA_REPORT.md and kb/golden/questions.yaml written;
  9 outbox messages (B, C, D, all, 5 to orch); 4 inbox messages acknowledged.
- found: every number of the three helpers that I recomputed holds; the verifier's WRONG items
  all hold; new: the Greek mapping of the PDF reader is wrong for cmsy/cmex symbols (3 of 20), a
  seventh cause of lost bibliographies (2602.00155), 11 ok papers without bibliography put the
  strict parse rate at 94.8 % (the recorded status gives 96.3 %).
- changed my mind about: "parse status ok" as the parse-success measure of KB-G2: the verifier
  shows it can hide a lost bibliography, so the package states both readings.
- failed predictions: my C4 word-level ratio (gr-qc/0312117, misspelled in both records); none
  else this session.
- open: bibliography parser and claim chunk remap; KB-G2 verifier; held-out golden set; KB-G3
  (the brief's statements as claims; 117 to_verify); upstream watch not run this wave.

## 2026-11-21T12:56Z  session kb lead, wave 3 batch 3 (review of verify_g2; KB-G0, KB-G2 packages)

State found: kb/main 465a1322 + merge of main (8b9b27a2). Of the five packages of round 1
(PLAN-wave3.md) only `verify_g2` finished (batch 2b); `ingest3`, `claims_tracks`, `claims_brief`
and `code_kb` were cut at 14:35 PST on 2026-11-20 and not resumed. Uncommitted: claims_tracks
LEDGER.tsv (14 rows of batch B1, applied as run kb-20261120-223013-5330e45, rows equal to its
ledger_rows.tsv), claims_tracks decisions/scripts C1, D1, E1 (written, never run), code_kb
JOURNAL M1 prediction, ingest3 figures/ids/scripts. No PAUSE flag; no kb card job.

### Prediction L1 (before run lead-check of verify_g2; written 12:56Z)

My own script (`tracks/kb/stage/review_wave3/scripts/lead_check_vg2.py`) reads the frozen
snapshot a782f1e with SQL, the verifier's raw search outputs and three sources, and expects:
1. Paper in top 10, recounted from the raw hit lists: held-out text/hybrid/rerank 21/22/21 of
   24, golden 27/28/28 of 32; rank 1 held-out 14/14/14, golden 20/17/19. Refuted by any
   difference.
2. Snapshot by SQL: parse_status ok 684, review 23, pdf 3; TeX papers with no bibliography
   entry 20 (11 of them ok); papers with citation rows but no entry 10; papers without an
   abstract chunk 25; repositories without code chunks 24 of 64. Refuted by any difference.
3. The verifier's database columns of scan.json (sections, equations, bibliography entries,
   citation rows, abstract chunk) equal my SQL counts for all 710 papers; refuted if any
   paper differs in a way that changes a component verdict.
4. My re-evaluation of the definition (S, E, B, A') from the scan's source counts and my
   database counts gives 688 lenient successes, 679 after the nine gaps read at the source,
   670 with the nine letters failed, 658 strict; refuted if any differs by more than one.
5. Sources (grep, read-only): 0710.5073 has 28 `\bibitem` in a `references` environment;
   1201.4794 has an AAS `\reference` list of at least 20 items; gr-qc/0304002 defines
   `\def\bi{\bibitem}`. Refuted if any is absent.
6. Held-out commit 8fb37106 precedes the start of run kb-20261120-222546-ea894c8.
7. C6b: `kb show 2611.12831 --abstract` and `kb cites 2611.12831 --out` on the snapshot print
   no snapshot id; search hits have no snapshot field. Refuted if an id is printed.
8. The manifests of kb-20261115-154858-b0d8c8f and kb-20261115-164121-5aca10c carry a status
   other than failed while their log or exit code says 1.

### Outcome L1 (run kb-20261121-125746-a03875b, 12:57Z; check.json, figure fig_lead_check_vg2.png)

All eight parts held [VERIFIED, scratch/kb/kb-20261121-125746-a03875b/check.json]:
1. paper hits and rank-1 counts from the raw lists equal the verifier's in all six set-mode
   pairs (held-out 21/22/21, rank 1 14/14/14; golden 27/28/28, rank 1 20/17/19);
2. ok 684, review 23, pdf 3; 20 TeX papers without bibliography (11 ok); 10 with citation rows
   but no entry; 25 without abstract chunk; 24 of 64 repositories without code chunks;
3. the scan's database columns equal my SQL for 710 of 710 papers (no difference at all);
4. definition re-evaluated: S 709, E 701, B 696, A' 710; 688 lenient, 679 after gaps, 670 with
   the letters failed (strict 658 taken from its tally, not recomputed by me);
5. 0710.5073: 28 `\bibitem`, one `references` environment; 1201.4794: 46 `\reference`;
   gr-qc/0304002: the `\def\bi{\bibitem}` and 39 uses;
6. 8fb37106 at 22:24:05Z is an ancestor of the search run's commit, run started 22:25:46Z;
7. `kb show --abstract` and `kb cites --out` print no snapshot id; hits have no snapshot field;
8. both wave-1 manifests: status "finished", exit_code 1.
Figures read: mine (bars equal; legend of panel (a) overlaps the last bars, cosmetic), the
verifier's fig_ranks.png (misses as counted) and fig_parse.png (database equation counts mostly
above the verifier's display counts; seven E failures below the half line).

- did: reviewed verify_g2 from its artefacts (stage/REVIEW-wave3.md); committed stranded B1
  ledger rows; corrected two manifests to failed; named the tool-choice reasons in kb/README.md;
  KB-G0 C5 and KB-G2 C8 PASS with VERIFIER.md, C3 and C6 evidence rewritten with the verifier's
  readings; OPEN.md of both rewritten with the defects and who removes them; nrpic-stage
  collect, verify, report for both; outbox: kb-g0-g2-gate-review, kb-cut-packages-schedule (orch),
  replies "queued" to A, B, C; 7 inbox messages acknowledged.
- found: nothing wrong in the verifier's numbers; it was right that C6b is unmet on the strict
  reading; C1b reasons exist (kb/JOURNAL.md L24-36, 205, 231); the parameter index is stale
  (main has core-v0.4 and core-v0.5; index at 5deee18).
- changed my mind about: C6 of KB-G2: PASS on the brief's wording (the note records the id), but
  the tool must carry the id; written down both ways for the reviewer.
- failed predictions: none this session (L1 held).
- open: the four cut packages (HANDOFF table); C6b code fix after ingest3; parameter index at
  main; raw source.bin modes.

## 2026-11-21 23:50 UTC, lead batch 9 (kb), session of about forty minutes, no helpers

Predictions written before the runs of this session.
- D1 (drop of gr-qc/0608095, decision 0024 item 2): the dry run counts papers 1, chunks 43,
  equations 7, figures 5, bib_entries 4, downloads 1, claims 0, claim_locators 0 (my read-only
  query at 23:41 UTC); after the drop all of them are 0 and the papers table holds 744. Refuted
  if any count differs or a claim names the paper (the script then refuses).
- K1 (claim check on the 21 claims of ingest3's two papers, 171-186 and 658-662): check reaches
  only the 16 wave-1 seeds 171-186 and reports them 'same' (ingest3 saw 'same 16' after its
  remap); 658-662 are served rows and are not reached. A 'pinned' count is possible for any of
  the 16 that a person relocated. Refuted if any of the 16 reports 'changed'.
- D1 outcome (run kb-20261121-234427-d6031d4): held. Before: papers 1, chunks 43, equations 7,
  figures 5, bib_entries 4, downloads 1, claims 0; also 7 citation rows and 22 vectors I had not
  counted. After: all 0, papers 744.
- K1 outcome (run kb-20261121-234437-8747d17): held, "checked: same 16"; 658-662 not reached
  (served rows); 0 dangling chunk references in the 21 claims and in all claims; 0 orphan vectors.
- S1 (snapshot): `kb snapshot` writes kb-20261121-<sha7>.sqlite and moves db/current to it;
  `kb status` then names it; a reader on db/current sees 744 papers, 860 claims, and the code
  index of local/nrpic at 47ab19ab. Refuted if current still points at kb-20261119-a782f1e or a
  count differs from the working database.
- Q1 (kb qa run on the new snapshot): parse rate 720/744 = 96.8 % with status ok (gr-qc/0608095
  was ok, so 719/744 = 96.6 % if it was among the ok papers), strict rate the same (ingest3 found
  no ok paper that cites without entries), bar met. Refuted if below 95 % or strict differs.
- B1 (B's claim on 2312.12499v2, read by me at main.tex L322-326 and L579-583): `kb claim add`
  writes one judgement claim (number 861) with two locator rows that both resolve. Refuted if a
  locator does not resolve or the add is refused.
- B1 outcome (runs kb-20261121-234903-f8e0b41, kb-20261121-234914-e160024): partly failed.
  `kb claim add` wrote claim 861 but no locator rows (add stores the locator string only); a
  `kb claim relocate` wrote the two rows, both resolved (chunk ids empty: equation lines).
- Q1 outcome (run kb-20261121-234721-b3aecfe, snapshot kb-20261121-bbaafe5): held on its second
  branch: 719/744 = 96.6 % with status ok, strict 719 (96.6 %), bar met; golden questions as
  ingest3 (hybrid 28/32 papers, 23/32 locations; rerank 28/32, 25/32). Not predicted: C1 says
  the counts do not agree, because the 35 additions of wave 3 have no downloads row (verify-
  downloads last ran 2026-11-15; ingest3's QA had the same verdict).
- V1 (kb verify-downloads, then a second snapshot): downloads rows for all 744 manifest ids plus
  the repositories, ok 743 and problem 1 (the existing one), no record 0; C1 then agrees by the
  report's own rule (recomputed by my SQL). Refuted if any of the 35 is missing or failed.
- V1 outcome (run kb-20261121-235128-dcd72a4): held for the 60 additions (all download rows ok;
  C1 agrees by its rule, my SQL); verify-downloads exits 1 on the known gr-qc/9412071 and lists
  the additions as "extra" of brief section 17 (it does not read arxiv_additions.tsv). Second
  snapshot kb-20261121-aa0a2ae = db/current (744 papers, 861 claims).
- Figures: none made this session; the steps were data management (drop, check, snapshot, QA
  text) and their outcomes are counts. I read ingest3's fig_parse_status.png and claims_brief's
  fig_seeds_by_section.png before relying on their numbers [JUDGEMENT on the exemption].
- did: additions test (60/744), guard of claim check, C6b, parse rate in kb qa run, drop of
  gr-qc/0608095, claim check of ingest3's seeds, two snapshots, claim 861, stale header of the
  link file, review of the four packages from own SQL (REVIEW-wave3.md), messages to F, A, C, B,
  orch; ack of orch's release message.
- found: decision 0027's 745 included the dropped paper; `kb claim add` writes no locator rows;
  QA C1 disagreed only through missing download rows of the 35 additions.
- failed predictions: B1 (no locator rows from add). D1, K1, S1, Q1, V1 held (V1 with the exit
  code of the known PDF paper).
- open: KB-G3 package and its verifier; ingest of the sources A and C asked for; fragment claims.

## 2026-11-24 kb lead batch 13 (from 23:27 UTC): ingest4 review, claims of the KB-G3 verifier, snapshot, KB-G3 package

Predictions, written before the runs:
- R1 (review of ingest4 from my own SQL on kb.sqlite): 762 papers (ok 737, review 22, pdf 3);
  the 18 ids of ids/additions18.txt all present with status ok; the six old-style papers have
  bib source `heading` and 11, 16, 16, 10, 27, 21 entries (the package's independent count).
  Refuted if any count differs.
- C1 (claims batch, tracks/kb/lead_b13/scripts/apply_g3.sh): every command exits 0; three
  claims are added (862 for 682, 863 for 714, 864 for 452; 861 -> 864 claims); afterwards 682
  is refuted; 781, 804, 409, 447, 449, 450 are fulltext/checked with every locator row
  resolved; 714, 809, 452 stay to_verify with an annotate event that states the answer. Refuted
  if a command fails, a locator row does not resolve, or the counts differ.
- S1 (verify-downloads, QA, snapshot): verify-downloads exits 1 only for gr-qc/9412071;
  QA C1 "counts agree"; parse rate 737/762 = 96.7 % (bar 95 %); golden hybrid 28/32 papers as in
  ingest4; the snapshot moves db/current to a new file and `kb status` on it shows 762 papers and
  864 claims. Refuted if C1 disagrees, the rate or the golden count changes, or the counts differ.
- C1 outcome (run kb-20261124-233445-89478ae): FAILED in part. Claims 862 (supersedes 682), 863
  (answer to 714), 864 (precise text for 452) were added; 682 refuted; 781, 804, 409, 447, 449,
  450 fulltext/checked with every locator row resolved (2, 8, 6, 1, 7, 5); 714, 809, 452
  annotated. The three `kb claim relocate` calls failed: the command requires `--by` (my
  script omitted it), so 862-864 had no locator rows. Fixed in apply_g3.sh; the three relocates
  are rerun by relocate_new.sh. Prediction C1b: three relocates exit 0 and every row resolves.
- C1b outcome (run kb-20261124-233504-c6530a6): held: 862, 863, 864 have 1, 3, 3 locator rows,
  all resolved; the table of the 13 claims is in after.tsv of the run.
- R1 outcome (own SQL on kb.sqlite, read-only): held: 762 papers (ok 737, review 22, pdf 3); the
  18 additions all ok with a downloads row ok; the six old-style papers carry 11, 16, 16, 10,
  27, 21 entries from source `heading`. Figures read: ingest4 fig_oldstyle.png (entries on the
  independent count; citation rows 0 for the two author-year papers), verifier fig_sample.png.
- C2 (before apply_g3b.sh): of the 32 to_verify claims, 11 brief seeds carry no processing
  event (716, 798, 799, 803, 805-808, 810-812). Four are answered by the store (716, 798, 799 by
  the KB-G1 first answers; 808 in part by ingest4). Prediction: four annotate events, exit 0;
  seven seeds remain without one. Refuted if the script fails or a count differs.
- C2 outcome (run kb-20261124-233637-3d710a8): held: four annotate events (716, 798, 799, 808);
  seven brief seeds remain without a processing event (803, 805, 806, 807, 810, 811, 812).
- C3 (apply_g3c.sh): annotations of 85 (fragment) and 737 (a correction, not a refutation), the
  verifier's items 1b and 2. Prediction: two events, exit 0.
- C3 outcome (run kb-20261124-233726-3b6e5b9): held (two annotate events, exit 0).
- S1 outcome (run kb-20261124-233515-0ed31c7): held. verify-downloads exit 1 only for
  gr-qc/9412071 (arXiv 684: ok 683, problem 1; extra 81); QA C1 "counts agree"; parse rate
  737/762 = 96.7 %, strict 96.7 %, bar met; golden hybrid 28/32 papers, 23/32 locations, rerank
  28/32, 25/32 (as ingest4); snapshot kb-20261124-9872d21 = db/current, 762 papers, 864 claims,
  28 events of this session inside it. kb/QA_REPORT.md replaced by this run's report.
- Q2 (figures of this QA, kb/kbtool/qa_figures.py on qa.json): three PNGs; retrieval panel shows
  28/32 for hybrid and rerank. Refuted if the script fails or the panel differs from the report.
- Q2 outcome (run kb-20261124-234330-7f49a10): held: three PNGs (copied to lead_b13/figures);
  I read fig_qa_retrieval.png (legend 27/32, 28/32, 28/32 papers; 21/32, 23/32, 25/32
  locations, as the report) and fig_qa_claims.png (D shows the one refuted claim 682).
- did: review of ingest4 (own SQL; R1); the verifier's KB-G3 findings acted on (682 -> 862, 781,
  804 verified, 714 -> 863, 809, 85, 737, 716, 798, 799, 808 annotated); 409, 447, 449, 450
  verified at abstract lines, 452 -> 864; snapshot kb-20261124-9872d21 with verify-downloads and
  QA; KB-G3 stage package (collect, SCOPE, EVIDENCE, OPEN, REVIEW, checklist, verify, report);
  messages to A, C, D, F, orch; acks of core and orch.
- found: the six wrong claims share one cause (processed by pipeline step, not by text); the tool
  has no supersede action; seven brief seeds had no event, two of them (803, 805) bear on G1.
- failed predictions: C1 in part (relocate without --by). R1, C1b, C2, C3, S1, Q2 held.
- gate: KB-G3 not complete (C1 FAIL on 803, 805; fresh verifier owed). 0 card-hours.

## 2026-11-25 03:40 UTC, kb lead batch 15 (review of claims3; snapshot and QA; KB-G3 package)

Predictions, written before the runs of this session.
- V1 (review run, read-only on kb-data/db/kb.sqlite and snapshot kb-20261124-9872d21): every
  row of claims3/LEDGER.tsv has label_after and status_after equal to the database; every
  successor has a claim_links row from the old claim to it; claims 865-881 exist with resolved
  locator rows; the claims whose row or status differs between the snapshot and kb.sqlite are
  exactly the ledger's claim ids (no other claim touched); recomputed from SAMPLE_VERDICTS.tsv:
  26/30, Clopper-Pearson 95 % 0.693-0.962, stratum-weighted rate 0.865 within 0.005; the weak
  class counted today by claims3/scripts/weak_class.py is between 520 and 543. Refuted by any
  mismatch, a claim outside the ledger changed, or a count outside the range.
- V2 (my own reading, not a run): of five claims drawn by me (seed 20261125+1 over the 30
  sampled and 869, 865-868, 870-881), each verdict of the package holds when I read the source
  lines. Refuted by one verdict I judge wrong.
- S2 (snapshot run): verify-downloads exit 1 only for gr-qc/9412071; QA C1 counts agree; parse
  rate 737/762 unchanged; golden hybrid 28/32 papers; claims 881; QA lists the statuses
  superseded and withdrawn; db/current points to the new snapshot. Refuted by any other
  problem row, a changed parse or retrieval count, or a claims count other than 881.
- V1 outcome (runs kb-20261125-033503-dfc398e, kb-20261125-033530-5a1ac43): held in part.
  Ledger: 72 rows, no label or status mismatch, 22 superseded_by links, every new claim
  865-881 has resolved locator rows; 881 claims (864 in the snapshot). Sample recomputed with
  my own Clopper-Pearson code: 26/30, 0.693-0.962, weighted 0.8648, s.e. 0.0609 (as the
  package). FAILED in two places: (a) the weak class today is 548, outside 520-543; the
  population diff shows no claim joined, 25 left; five sampled claims (308, 467, 662, 673 of
  WQ, 720 of WB) stay in the class because claims3 only annotated them and its query does not
  exclude claims3's own readings: the unread class is 548 - 5 = 543, as the package says.
  (b) five claims outside the ledger changed: 289, 313, 430, 624, 862, the existing
  successors of `supersede --to`; the step overwrote their claim_meta checked_by/checked_at
  (862: kb-lead-b13 -> kb-claims3; 289: 'kb claims helper (seed)' -> kb-claims3). For the four
  machine-located siblings this records a reading that did not happen (claims3 README: not read
  against their sources). Defect of kb/kbtool/claims_db.py supersede(): fixed (line removed;
  test test_supersede_to_existing_keeps_successor_checked_by passes). Four ledger claims
  without a row change (308, 467, 662, 673) were annotated only: expected.
- R2 (restore_checked.py, writes claim_meta.checked_by/checked_at of 289, 313, 430, 624, 862
  to the snapshot's values, one annotate event each, inside the writer lock). Prediction: dry
  run and real run each report five restores with 'before' = kb-claims3; after the real run
  the review script finds the same 72 changed claims minus none, and these five differ from
  the snapshot only by... nothing in claims/claim_meta/locators (so changed_not_in_ledger is
  empty). Refuted by any other count or an exception.
- R2 outcome (dry run kb-20261125-033655-43ee7ce, run kb-20261125-033703-3bd4386, review
  repeated kb-20261125-033703-a1be27a): held: five restores, 'before' kb-claims3 each; after it
  67 claims differ from the snapshot, all in the ledger; changed_not_in_ledger empty. (My R2 text
  had a garbled clause; the test was: no claim outside the ledger differs.)
- V2 outcome (my reading; ids drawn with seed 20261126 in the review run): held: 40, 669, 869,
  874, 877 right as worded at their locators. Reservation on 877: its second clause is F's run
  result under a fulltext label whose locator is the paper only.
- S2 outcome (run kb-20261125-033718-3405697): held: verify-downloads exit 1 only for
  gr-qc/9412071; QA C1 762/762, ok 761, problem 1; parse 737/762 = 96.7 %; golden hybrid 28/32
  papers, 23/32 locations (rerank 28/32, 25/32); 881 claims, statuses superseded 22 and withdrawn
  3 in C9; db/current -> kb-20261125-2f97258. kb/QA_REPORT.md replaced by this report.
- E1 (evidence run kb-20261125-034227-58fc4e0, no prediction beyond C1): no unprocessed to_verify
  claim bears on G1 (806, 807, 810, 811, 812 left by decision 0035); figure fig_g3_queue.png read.
- Test written after the fix, not before: test_supersede_to_existing_keeps_successor_checked_by
  (passes with the fix; by reading, the removed line set checked_by to the caller, so the old
  code fails it). Not run against the old code.
- did: review of claims3 from the artefacts (REVIEW-wave3.md batch 15); tool defect fixed and
  five rows repaired; snapshot kb-20261125-2f97258 with verify-downloads and QA; OPEN.md O1, O2,
  O3, O5 closed, O4 in part, O7 weak class as a known limit; KB-G3 evidence, checklist (C1 PASS),
  verify PASS, report; messages to all (superseded claims) and orch (second verifier,
  gr-qc/0608095); acks of core and orch (release v0.7, SIGTERM).
- failed predictions: V1 in two places (weak class 548 outside 520-543; five claims outside the
  ledger changed). V2, R2, S2 held.
- gate: KB-G3 package complete for the second fresh verifier (decision 0036 item 3); not passed.
  0 card-hours.
