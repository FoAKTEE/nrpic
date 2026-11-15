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
