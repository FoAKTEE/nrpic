# JOURNAL of the kb package K0-K1 (helper of owner kb)

Append-only, newest at the bottom. Predictions are written before a test runs, outcomes after,
failed predictions included. Evidence labels: [VERIFIED] read or computed here with a locator,
[BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 11:15 UTC  K0-K1 helper  (worktree wt/kb, branch kb/main)

### Starting state

- An earlier, interrupted attempt at this package had left uncommitted files under `kb/`
  (`kbtool/{__init__,__main__,brief,paths,lock,db,sniff}.py`, `schema.sql`, `manifests/`,
  `pyproject.toml`, `.venv/`), last written 03:08 local time; no process had the worktree as
  its working directory and no fetch was running (checked through /proc at 03:13). I read
  every file, kept them, and built on them [VERIFIED: files read in full].
- Re-extraction of the manifests from the brief reproduces `kb/manifests/arxiv.tsv` and
  `github.tsv` byte for byte (`cmp`, and `kb manifests --check`): 684 arXiv rows from brief
  lines 2543-3226 (47 priority 3, 160 priority 2, 477 priority 1; 21 groups G01-G21) and 63
  repositories from lines 3234-3296 (1 core, 6 dep, 38 ref, 18 tool) [VERIFIED: brief sha256
  9492261e..., `kb/manifests/SOURCE.json`].
- `kb/schema.sql` is the SQL block of brief 12.2 (lines 1277-1347) exactly, plus a two-line
  header comment (diff against `kbtool.brief.extract_schema`) [VERIFIED].

### K0 tool choice [JUDGEMENT]

- Core of `kbtool` (manifests, inventory, verify-downloads, schema, status, snapshot) uses the
  Python standard library only (argparse, sqlite3, tarfile, zlib, fcntl), so `kb/bin/kb` runs
  under the system `python3 -I` with nothing imported from the environment, and the safety
  checks have no third-party code in their path. typer/pydantic were not needed for this.
- SQLite of the system Python: 3.37.2, FTS5 available (the schema's virtual tables create).
- `kb/.venv` (uv venv, Python 3.10.12) holds the K0 extras for later stages: pytest,
  pylatexenc (K2 fallback converter), bibtexparser (K3), rapidfuzz (fuzzy title match, K1/K3),
  tenacity, pyyaml, numpy, matplotlib (figures). The embedding stack
  (sentence-transformers, sqlite-vec) waits for K4 because it pulls torch.
- No LaTeXML or pandoc on the machine is assumed; K2 decides.
- Schema change: migration 0002 adds tables `downloads` and `repo_downloads`, because
  `papers.title` is NOT NULL and titles come only with the metadata stage; K1 does not invent
  titles. Schema version after migration: 2.
- `git` is never run inside a downloaded repository (its config can name programs git runs);
  `kbtool.gitmeta` reads HEAD, loose refs and packed-refs as files.

### Predictions (written before the tests ran)

T1 manifests. The committed TSVs equal a fresh extraction; every row's brief line (first line
   + row index) contains the id and the group of that row; ids unique, all valid arXiv ids.
   Refuted by any mismatch.
T2 sniff and safe extraction (synthetic blobs). gzip-tar, gzip-tex, pdf, plain tex, html,
   empty and a gzip bomb are told apart from content alone, whatever the file name; the
   extractor refuses absolute paths, `..`, symlinks, hardlinks, devices and FIFOs, and stops at
   the single-file and total size limits. Refuted if any unsafe member lands on disk or any
   kind is misclassified.
T3 verify-downloads on a synthetic store laid out exactly as the fetch command writes it:
   ok / missing / failed / incomplete (directory without record) / extra (not in manifest)
   are classified as such; a changed byte in source.bin (sha mismatch), an HTML page stored as
   an e-print, a file planted in src/, a removed member, a symlink in src/, a `vX` version and
   a Content-Disposition naming another id are each reported as a problem; SHA256SUMS
   verifies with `sha256sum -c`. Refuted by any misclassification.
T4 verify-downloads on the real store (kb-data at about 11:15 UTC; other sessions may add
   entries meanwhile). Expected from a directory listing at 11:13 UTC: 24 manifest entries
   present (priority 3: 14, priority 2: 9, priority 1: 1), 3 extras (gr-qc/0404056,
   gr-qc/0606037, gr-qc/9703066), 660 missing, 0 failed; every present entry `ok`: sha256
   equal to the record, content kind consistent with the recorded kind (26 tar, 1 single
   gzip TeX), versions confirmed by Content-Disposition, extracted tree equal to the archive
   listing, no unsafe members. GitHub: all 63 missing (kb-data/raw/github does not exist).
   Refuted if any present entry is not `ok`, or the counts differ from a listing taken at the
   same time.
T5 database. `kb init` creates kb.sqlite with the 20 tables of brief 12.2 plus the 2 of
   migration 0002, schema_version rows 1 and 2; a second `kb init` changes nothing.
   Refuted by a missing table or a repeated migration.
T6 snapshot. `kb snapshot` writes kb-YYYYMMDD-<sha7>.sqlite whose sha256 begins with sha7,
   mode 0444, `current` points at it, and a reader opening `current` sees the same rows.
T7 writer lock. While one process holds locks/kb-writer.lock, a second writer times out with
   an error naming the holder; after release it gets the lock.

### Outcomes (after the tests ran)

- T1, T2, T3, T5, T6, T7 (synthetic, `kb/tests/`, `cd kb && .venv/bin/python -m pytest`):
  first run 50 passed, 2 failed. Both failures were mine and not the code under test's
  claims: (i) the INSERT into `downloads` had 21 placeholders for 20 columns (fixed; columns
  now named in the statement); (ii) the fixture recorded version "v1.retry1" where the fetch
  command records "v1" for a retry directory (fixture corrected to the fetch command's
  behaviour, `harness/bin/nrpic-fetch-arxiv` lines 124-133). Second run: 52 passed. All
  predictions T1-T3, T5-T7 hold [VERIFIED: commit 6bb2b7d and later, pytest output].
- T5 on the real data root: `kb init` created `kb-data/db/kb.sqlite`, schema_version rows
  (1, 2); a second `kb init` applied nothing [VERIFIED: 11:24 UTC, ingest_log rows init-db,
  migrate].
- T4, run `kb-20261115-112414-6bb2b7d` (manifest `tracks/kb/runs/.../manifest.json`):
  684 manifest rows: ok 24 (priority 3: 14, 2: 9, 1: 1), missing 660, failed 0, problem 0,
  incomplete 0; source kind tex for all 28 stored e-prints (27 gzip-tar, 1 gzip-tex); all 28
  versions confirmed by Content-Disposition; `sha256sum -c manifests/SHA256SUMS` passes for
  28 lines; GitHub 63 of 63 missing. Prediction held for every manifest entry. One part
  failed as worded: I predicted 3 extras and found 4. The fourth, gr-qc/0608095, was added by
  another session between my listing at 11:13 and the run (the run's own listings before and
  after the check both have 28 entries = 24 + 4), which is the case the inventory is built
  to tolerate [VERIFIED: `scratch/kb/kb-20261115-112414-6bb2b7d/raw_listing_*.txt`].
- Found in passing: 8 manifest ids have older copies under `refs/arxiv_*` outside the store
  (2611.12831, 1711.06681, 1908.05683, 1904.07841, 1905.08890, 2001.07968, 1101.3555,
  1111.2997); they are NOT counted as present, and the store gets its own copy through the
  fetch command [VERIFIED: report `kb/reports/verify-downloads.md`, "Problems and notes"].

### Prediction for the priority-3 download (before it starts)

D1 `kb fetch-missing --priority 3` hands the 33 missing priority-3 ids to one process of
   `harness/bin/nrpic-fetch-arxiv` (sequential, its lock, 3 s gaps). Expected: at least 30 of
   33 fetched with status ok, wall time under 15 min unless other sessions hold the lock; the
   next verify-downloads shows priority 3 at ok >= 44 of 47 and problem 0. Refuted if more
   than 3 fail, or an HTML or error page is stored as an e-print (verify would show
   "problem: not an e-print").

### Outcome of the priority-3 download (D1)

- Run `kb-20261115-112522-3ac74c2`: `kb fetch-missing --priority 3` replaced itself with
  `python3 -I harness/bin/nrpic-fetch-arxiv <33 ids>` (process 966412, its own session; the
  same pid before and after the exec, checked through /proc/966412/cmdline). It ran from
  11:25:23 to 11:28:09 UTC (166.7 s, about 5 s per paper); 33 of 33 ids printed a store path,
  stderr empty. The exit code was not observed (detached), recorded as null with that note.
- Run `kb-20261115-112823-3ac74c2` (verify-downloads afterwards): priority 3 ok 47 of 47,
  problem 0; manifest total ok 57, missing 627 (priority 2: 151, priority 1: 476); extras 4;
  61 stored e-prints, all source kind tex (56 gzip-tar, 5 gzip-tex), all versions confirmed
  by Content-Disposition; `sha256sum -c manifests/SHA256SUMS` exit 0; no refused archive
  members. Prediction D1 held (33 of 33 instead of at least 30; wall time 2.8 min, under 15)
  [VERIFIED: `scratch/kb/kb-20261115-112823-3ac74c2/{stdout.log,inventory.json,sha256sum_check.txt}`,
  figure `kb/reports/fig_inventory.png`, inspected].
- The largest e-print is 2605.04487 at 41252253 bytes, below the 256 MiB per-file limit.
- First snapshot `kb-data/db/kb-20261115-b715da3.sqlite` (read-only; `db/current` points at it):
  688 rows in `downloads` (684 manifest + 4 extras), 63 in `repo_downloads`; no papers yet.

### Open after K0-K1 (for the next helper)

- Priority 2 (151) and 1 (476) downloads: `kb/bin/kb fetch-missing --priority 2` as one
  detached registered run (see README), then priority 1; then `kb verify-downloads`.
- arXiv API and INSPIRE metadata, title/author cross-check with brief section 16: blocked on
  a sanctioned download path (README, Request 2).
- Repositories: none downloaded; which ones and how is Request 4 (decision 0010).
- `kb watch upstream` and the AthenaK branch-tip record: stub.

## 2026-11-15 12:45 UTC  K2-K3 helper (papers: download, TeX, bibliography)

### Starting state (12:42 UTC)

- No download process running (no process with nrpic-fetch-arxiv or fetch-missing in its
  command line, `ps -eo pid,args`). Store: 103 records in `kb-data/meta/arxiv`, all status ok;
  of the 684 manifest ids, priority 3: 47 of 47 present, priority 2: 21 of 160, priority 1:
  17 of 477 (other sessions added entries since K1) [VERIFIED: script over the records, 12:43].
- `kb fetch-missing --priority` now takes several priorities in the order given (one id list,
  one exec of the fetch command, so still one process). Dry run: 599 ids, priority 2 first.

### Prediction D2 (before the priority 2+1 download starts)

D2 One detached process (`kb fetch-missing --priority 3 2 1`, exec into
   `python3 -I harness/bin/nrpic-fetch-arxiv <599 ids>`) fetches the 139 missing priority-2
   ids and then the 460 missing priority-1 ids, sequentially. Expected at about 5 s per paper
   (K1: 166.7 s for 33) a wall time of 50 to 90 min unless other sessions hold the arXiv lock;
   at least 97 % of ids end with status ok; failures are a few ids withdrawn or without
   source (HTTP 403/404) or PDF-only. Refuted if more than 3 % fail, if two download
   processes of mine run at once, or if any stored record has a kind other than tar,
   single-file or pdf.

## 2026-11-15 13:10 UTC  K6-K7 helper (code: clones, code index, parameter index, paper-code links, upstream watch)

Scope: brief 12.7 under decision 0010 (repositories are cloned for reading and indexing
only; nothing in a clone is built, run or imported). Modules `kbtool/code_*.py`,
`kbtool/links_*.py`; subcommands `fetch-repos`, `ingest repo`, `code`, `link`, `watch upstream`.

### Starting state (13:05 UTC)

- `kb-data/raw/github/` and `kb-data/meta/github/` empty. No universal-ctags, tree-sitter
  or ripgrep on the machine; git 2.34.1 (Ubuntu package 1:2.34.1-1ubuntu1.17, with the
  distribution's security backports) [VERIFIED: `dpkg -l git`].
- The user's global git configuration has credential helpers for github.com. A clone that
  used it could send the user's token when a name does not resolve (GitHub answers 401 and
  git asks the helper). So every git call on downloads runs with GIT_CONFIG_GLOBAL=/dev/null,
  GIT_CONFIG_NOSYSTEM=1, no prompt, no askpass [JUDGEMENT; `kbtool/code_fetch.py`].
- `git ls-remote https://github.com/IAS-Astrophysics/athenak HEAD` at 13:02 UTC:
  c5a0d7f9155a70149931bf0be5a4ffb673f2532a, the commit the brief inspected (brief line 122).

### Prediction R1 (before the clone run)

R1 `kb fetch-repos` clones the 63 manifest rows sequentially (AthenaK first, with its
   remote branch list). Expected: at least 58 of 63 names resolve and clone; the ones that
   may not resolve are small personal or renamed repositories (for example
   gevolution-code/gevolution-2.0, caravangelo/inflation-easy, hayleyjm/mescaline-1.0);
   total checkout size 1-5 GB, wall time under 60 min; every clone's HEAD (read as a file)
   equals the sha of `git ls-remote` taken just before; AthenaK main is still c5a0d7f and the
   branch list has about 124 heads (brief line 130). Refuted if fewer than 58 clone, if any
   clone fails for a reason other than a name that does not resolve or a timeout, or if a
   HEAD differs from its ls-remote sha without a push in between.

### Outcome R1 (run kb-20261115-130232-ac33aa1)

- 63 of 63 manifest names resolved and cloned; none unresolved, none failed (stdout
  "summary: ok 63", stderr empty; exit code of the detached process not observed). Wall
  time 156.5 s. Checkouts 1.74 GB, object stores 0.63 GB (2.5 GB on disk with `du`). Every
  clone's HEAD read as a file equals the sha `git ls-remote` gave just before. Prediction R1
  held; my guess that some small repositories would not resolve was wrong (all exist).
  [VERIFIED: `kb-data/meta/github/*.json`, `scratch/kb/kb-20261115-130232-ac33aa1/stdout.log`]
- AthenaK upstream: main is c5a0d7f9155a (2026-09-11T15:50:16-04:00, "Cyclic zoom (#713)"),
  the commit the brief inspected; 124 remote heads at 13:02:32 UTC, the count of brief
  line 130 [VERIFIED: `kb-data/meta/github/IAS-Astrophysics__athenak.json`].
- Licence: the file-name rule of `kbtool/gitmeta.py` (exact names LICENSE, COPYING, ...)
  finds no licence file for 11 repositories and cannot classify 2 (ripgrep: dual
  MIT/Unlicense; LaTeXML: public-domain notice). The code index re-reads licences with a
  case-insensitive name rule (below) before any repository is treated as unlicensed.

### K2-K3 tool choices [JUDGEMENT] (helper of the papers modules)

- Plain-text converter: pylatexenc 2.11 (kb/.venv). LaTeXML is not on the machine and is not
  installed (no system-wide installs); `kb ingest arxiv` re-executes itself under
  kb/.venv/bin/python when the system python3 lacks pylatexenc. The converter is recorded per
  paper (papers.parse_json). Everything else (main file, flattening, comments, macros,
  structure, bibliography parsing) is standard library.
- pdflatex is installed; it is used ONLY on synthetic documents that the tests write, to read
  the true numbers from LaTeX's .aux (never on a download).
- Migration 0003 adds locators (char ranges of equations, figures, citations; flat_sha256 of
  the flattened text they refer to; figure/table kind; bibliography source).

### Predictions for the K2-K3 unit tests (before they run)

P1 test_tex_files: comment semantics (% eats the end of line, \% kept, \verb, comment
   environment, nested \iffalse..\fi), safe paths (.., absolute, symlink refused), flattening of
   \input{}, \input file, \include, \import with nested \input, source map file:line, cycle
   detection, main file from 00README.json / input graph / \documentstyle. Refuted by any
   failure that is the code's (not the test's) fault.
P2 test_tex_numbering: for three synthetic documents (article, article with
   \numberwithin{equation}{section}, revtex4-2), every label's number computed by
   tex_structure equals the number pdflatex writes into the .aux (equations incl. align with
   \nonumber, subequations 4a/4b, gather, multline, eqnarray, \tag; sections incl. starred and
   appendix A, A.1, B; figures and tables). Expected risk: REVTeX appendix equation numbering
   (A1, A2, B1) and the subequations parent label. Refuted by any mismatch.

### Tool choice for the code index [JUDGEMENT]

- Symbols: tree-sitter 0.25.2 with tree-sitter-cpp 0.23.4 in `kb/.venv` (no universal-ctags
  on the machine, and a ctags build from the clone would mean building downloaded code).
  Kokkos/CUDA/AMReX attribute macros are blanked to the same length before parsing
  (KOKKOS_LAMBDA becomes "[=]"), so lines do not move. Python: standard-library `ast`
  (parsing only). Fortran: line patterns. Other languages: files and chunks, no symbols.
- Parameters: a standard-library parser (comments and string contents masked, arguments
  split at top-level commas), so `kb` keeps working without the venv; tree-sitter is used
  only as the independent second extractor of test P2.
- Chunks and full text only for roles core, ref and this repository; dep and tool
  repositories get files, symbols and parameters. Files over 5000 lines, files with a
  "generated" marker in the first five lines and directories named ker, kernels,
  generated, third_party, external, vendor get no chunks (generated kernels of gkeyll alone
  are about 2 million lines).
- This repository (`local/nrpic`) is indexed from git objects at a ref (default `main`):
  athenak/src, python/nrpic, cosmo and problems (the brief's inputs/).

### Predictions P2-P4 (before the cross-check and the ingest runs)

P2 parameters. For upstream AthenaK, Athena++ and this tree, the index's parser and a
   second extractor on the tree-sitter syntax tree (`kb/scripts/code_crosscheck.py`) find
   the same set of (path, line, method, block, name) for every ParameterInput call.
   Smoke run on AthenaK: 1165 calls (730 GetOrAdd, 293 Get, 66 Set, 27 DoesParameterExist,
   49 DoesBlockExist), none unparsed. Refuted by any call found by one and not the other
   that is not a macro or preprocessor artefact I can point to.
P3 symbols. Every column-0 out-of-class definition `Type Class::Method(` in the .cpp files
   of upstream AthenaK and of this tree is a method symbol of the index (start line equal or
   up to two lines above). Expected at least 98 %. Refuted below 98 %.
P4 inputs against code. Of the parameter lines of the input files (upstream: 8670 lines in
   inputs/; this tree: problems/), at least 90 % name a parameter the code reads with the
   same literal block and name, or reads by that name under a block computed at run time
   (numbered output blocks). Refuted below 90 %.
### K2-K3 helper, continued: predictions written before the tests ran (labels K2-P1 and K2-P2
### are the P1 and P2 of the K2-K3 section above)

K2-P3 test_tex_text and test_bib_parse: macro expansion with optional arguments, \def with
   parameters, \DeclareMathOperator, bounded recursion; \be/\ee aliases found as equations;
   refs replaced by computed numbers; sentence splitter keeps "Eq.", "et al." and initials;
   chunks within 100..520 words, consecutive chunks overlap, no chunk boundary inside a display
   equation; arXiv ids (new with month/length check, old with archive list, versions dropped,
   bare numbers rejected), DOIs, REVTeX and biblatex .bbl, .bib (@string, #, parentheses,
   quoted values) equal to bibtexparser 2.1 on the fields compared; source preference .bbl >
   .bib (cited entries only) > inline thebibliography.
K2-P4 test_papers_ingest (synthetic store): two papers ingested; sections 1, 2, A; equations
   (1) eq:geo from method.tex line 2 through the source map and (A1) eq:app written with
   \be..\ee; char ranges index flat.tex whose sha256 is in papers; chunk kinds abstract, body,
   appendix, caption, footnote, comment; FTS hits; bibliography resolved by arXiv id (2) and by
   fuzzy title to the other corpus paper (1); in-corpus edges 2 of 4 distinct edges; re-ingest
   leaves counts unchanged; frontier lists the two absent ids; a download with a planted file
   is not ingested. Refuted by any failure due to the code.

### Outcomes of K2-P1 to K2-P4 (kb/tests, `cd kb && .venv/bin/python -m pytest`)

- K2-P1 held at the first run (9 tests).
- K2-P2 held for the code: for all three documents every label number computed by
  tex_structure equals the number in LaTeX's .aux (article: sections, equations 1-12 incl. 4a/4b,
  T, appendix A, A.1, B; numberwithin: 1.1 ...; revtex4-2: equations 1-9, A1, A2, B1, figures,
  tables). The first run failed for three reasons, all in the test: class-internal labels
  (FirstPage, LastPage, LastBibItem) were compared; REVTeX numbers tables in roman numerals
  (tab:one = "I"); I had expected multline to be (8), LaTeX says (7) and so does the code.
- K2-P3: first run 5 failures. Code faults (fixed): pylatexenc turns ~ into U+00A0 (now a
  space); a biblatex \field{eprint}{<bare id>} was not read as an arXiv id; the .bib parser
  stopped at `journal = prd # " 100"` (a quoted string after #), losing later fields; symbols
  listed both \mathrm{d} and d. Test faults: I expected the space after a zero-argument macro
  to vanish (TeX drops it; the code keeps it on purpose).
- K2-P4: first run failures were the test's (it ran `kb init`, which copies SOURCE.json from
  the manifest directory; a short synthetic paper scores 'review', not 'ok') and one code
  fault: a stray space before the full stop in citation contexts ("[cit.] ."); and `kb
  frontier` read "in the manifest" from the downloads table, empty before a verify run (now from
  kb/manifests/arxiv.tsv).
- Existing tests of K0-K1 that hard-coded schema version 2 now use db.latest_version() and
  db.migrations(). Whole suite: 85 passed.

### Prediction K2-P5: ingestion of the 47 priority-3 papers (before the run)

`kb ingest arxiv --priority 3 --jobs 8` on the real store (all 47 verified ok by K1). Expected:
0 failed; at least 40 of 47 with parse_score >= 0.75 (status ok), the rest 'review' (short
letters, papers with few equations or unusual classes); a title from \title for at least 45
and an abstract for at least 44; more than 2000 equation rows in total; at least 60 % of the
bibliography entries carry an arXiv id; the fraction of distinct citation edges that stay
inside a 47-paper corpus is small, 2 to 15 %; wall time under 10 min. Refuted by any failed
paper whose cause is the code, or by counts outside these ranges.

### Outcome of the first priority-3 run (kb-20261115-131730-b603113): wrong converter

- 47 of 47 parsed, 0 failed, 41 ok, 6 review, 7.6 s. But the header says "converter stdlib":
  the re-execution under kb/.venv never happened, because kb/.venv/bin/python is a symbolic
  link to /usr/bin/python3.10, and the check compared real paths of the interpreters. The
  plain text of that run is the crude standard-library conversion, and the fuzzy matcher was
  difflib. Fixed (compare sys.prefix with kb/.venv); one unregistered check run on 2611.12831
  confirmed "converter pylatexenc 2.11". The priority-3 ingestion is redone below; this run's
  rows are overwritten.

### Outcome K2-P5 (run kb-20261115-131809-f7f36ac, pylatexenc converter)

- 47 of 47 ingested in 30.8 s, 0 failed, 45 ok, 2 review (gr-qc/9906015: plain TeX with
  \centerline titles, no \section, score 0.40; 2009.08715: a habilitation thesis without
  \title, score 0.70). Abstracts 45 (>= 44, held). Equation rows 4099 (2097 labelled; > 2000,
  held). Bibliography entries 5192, 65.1 % with an arXiv id (>= 60 %, held), 83.9 % with an
  arXiv id or a DOI; distinct citation edges 3340, of which 111 = 3.3 % inside the corpus
  (2-15 %, held). Wall time held.
- FAILED as worded: titles for 43 of 47, not >= 45. Causes, one per paper: 2607.17929 had
  \renewcommand{\title}[2][]{...} in its preamble, and the first \title found was that
  definition (code fault; fixed: definitions of \title and \author are skipped, unit test
  added); gr-qc/9906015 (plain TeX), 2211.13950 (titlepage without \title), 2009.08715 (no
  \title) have no \title at all; their titles must come from the metadata (Request 2).
- Also added to the known-command list (quality score only): plain-TeX words such as \cal,
  \eqno, \cr, \kern, \vskip, which pylatexenc's database lacks and which are not macros of the
  paper.

### Prediction K2-P6: priority-3 re-ingestion with the title fix, and the independent checks

Re-ingestion: titles 44 of 47 (the three papers without \title stay empty), all other counts
as in K2-P5 within 2 %. Checks of kb/scripts/papers_checks.py:
C1 the main-file heuristics without the 00README hints pick the file 00README.json names for
   every paper that ships one (expect all agree).
C2 parse_bib equals bibtexparser 2.1 on every .bib file used: same key sets, same eprint and
   doi values (expect all equal; a difference in brace or quote stripping would refute).
C3 stored bibliography entries equal the count of \bibitem in the .bbl or flat text for every
   paper (expect all equal, perhaps one off where an item lacks a key).
C4 every \label inside a display environment of flat.tex is in some stored equation row
   (expect 100 %); no stored label absent from flat.tex.
C5 at most 1 % of the citation keys lack a bibliography entry.

### Outcome K2-P6 (re-ingestion kb-20261115-132028-f7f36ac; checks kb-20261115-132114-932c894)

- Re-ingestion: 45 ok, 2 review, 0 failed; titles 44 of 47 as predicted (held).
- C1 held: 14 of 14 papers with a 00README.json; the heuristics alone pick the same main file.
- C2 failed as worded, code fault: key sets equal for 7 of 7 .bib files, but 2 of 1070 eprint
  or doi values differed, both in 2601.17117/refs.bib, where an entry has lines
  `//eprint = "..."` (not BibTeX); my parser stopped at the first such line and lost the
  entry's later fields (its doi). Fixed (skip to the next comma at depth 0), test added.
- C3 held: 39 of 39 papers with a .bbl or thebibliography have as many stored entries as
  \bibitem in the text.
- C4 inconclusive as run: the checker's regex knew only literal \begin{equation} etc., so the
  labels of equations written with shorthands (\be..\ee, 7 papers) showed as "extra", and in
  2507.18312 the definition \newcommand{\be}{\begin{equation}} in the preamble opened a
  regex span that swallowed \label{sec:RV} ("missing"). Both are checker faults; the checker
  now reads the body only and writes the paper's environment shorthands out first. Rerun below.
- C5 held: 2 of 7710 citation keys lack an entry (1011.4920 "*martin-garcia:web", 2507.18312
  "Deluca", absent from that paper's .bbl).
- Found by reading the output (export of 2611.12831): pylatexenc 2.11 drops the argument of
  \texttt, \textsf, \textup, \textmd and \mbox, so "on top of the performance-portable
  \texttt{AthenaK} code" became "... performance-portable code"; and it raises on \href (the
  whole chunk then fell back to the stdlib converter). Fixed before the next ingestion; test
  added. Figures fig_papers_k2.png and fig_citations_k3.png of that run inspected: parse
  scores mostly above 0.95; body chunks mostly 200-400 words, a tail of shorter section ends;
  the citation matrix is dominated by the diagonal (G07, G14).

### Prediction K2-P7: full ingestion after the download, and checks C1-C5 on it

When the download run kb-20261115-124340-9048b83 has finished: `kb verify-downloads` shows the
manifest complete except for a few failures; then `kb ingest arxiv --all --jobs 8` (priority
order 3, 2, 1). Expected: at most 3 % of the manifest papers fail to parse (failures from
PDF-only or exotic sources); at least 85 % 'ok'; wall time under 15 min; arXiv-id rate of the
bibliography entries 55-75 %; fraction of distinct citation edges inside the corpus rises to
10-30 % (the corpus is the field's core literature). Checks: C1 all agree; C2 all equal;
C3 at least 97 % of papers agree; C4 at least 99 % of the labels inside display environments
are stored; C5 at most 1 % of keys without entry. Refuted by any number outside these ranges.

### Outcome P2, P3 (runs kb-20261115-130931-c0e0ec8, -131150-, -131158-, -131207-7350d70)

- P2 held: the masked-text parser and the tree-sitter extractor agree on every
  ParameterInput call: upstream AthenaK 1165 of 1165 (338 C/C++ files), this tree at main
  1259 of 1259 (347), Athena++ 999 of 999 (371), Parthenon 384 of 384 (374); none found by
  only one of them [VERIFIED: `scratch/kb/<run>/crosscheck_*.json`].
- P3 held: column-0 method definitions found by the line pattern and present as method
  symbols of the index: upstream AthenaK 886 of 886, this tree 924 of 924, Athena++ 1563 of
  1563, Parthenon 508 of 508.
- Limits of the two tests: both extractors see `#if 0` blocks and both use the same
  macro blanking and string unescaping; a call hidden behind a macro of the code itself
  would be missed by both.

### Scouting ingest (run kb-20261115-131627-7350d70) and two fixes found with the unit tests

- 64 repositories indexed (63 clones + local/nrpic) in about 10 min (gkeyll alone 232 s);
  database 379 MB: 68037 files, 305733 symbols, 157178 chunks (177 MB of text), 3489
  parameter rows. Kokkos contributed 35 "parameter" rows that are calls of another
  interface (no literal block anywhere); the params table now takes rows only from a
  repository that defines the ParameterInput class (AthenaK, Athena++, Parthenon, this
  tree). The unit test `test_cpp_symbols` (first run: 1 failure) showed that tree-sitter
  ends a `#define` node at column 0 of the next line (end line one too late) and that a
  blanked KOKKOS_INLINE_FUNCTION line cut the doc comment off; both fixed in
  `code_symbols.py`, test passes. The production ingest below is run with the fixes.

### Prediction P5 (before the first `kb watch upstream`)

P5 The bare shallow clone of all 124 branch tips of IAS-Astrophysics/athenak and the
   inspection of every branch show: (a) no branch whose `src/particles` mentions tmunu or
   deposit (no matter handed to the spacetime); (b) at least one branch (particles_gr with
   its relativistic pushers in a given spacetime) whose `src/particles` mentions z4c or adm
   (reading the metric), which brief line 130 says it does not; (c) no nrpic or vlasov
   anywhere under `src/`; (d) no branch name containing pic, vlasov, nrpic or deposit;
   (e) main still c5a0d7f. Refuted if (a) or (c) fails: then the coupling would be public.

### Outcome D2 (download of priority 2 then 1, run kb-20261115-124340-9048b83)

- One process for the whole list: pid 1935449 was `kb fetch-missing --priority 3 2 1` and then,
  after exec, `python3 -I harness/bin/nrpic-fetch-arxiv <599 ids>` (checked with ps at 12:44
  UTC); no second download process of mine ran. 12:43:44 to 13:27:06 UTC (43.4 min, 4.3 s per
  paper). 599 of 599 ids printed a store path; stderr empty. Exit code not observable (detached).
- Verify run kb-20261115-132730-a51e26e: 684 manifest rows: ok 683, problem 1, failed 0,
  missing 0; 18 extras added by other sessions. The problem is gr-qc/9412071: arXiv serves
  only a gzipped PostScript file for it (Content-Disposition "...v2.ps.gz"); the fetch command
  stored it as src/main.tex with status ok (README Request 3b of K1). Prediction D2 held
  (0 % failed, kinds tar/single-file only); the one PostScript file is the kind of failure
  D2 named ("PDF-only or without source").

### Outcome K2-P7: full ingestion (run kb-20261115-132806-013c452) and checks (kb-20261115-133637-3f7f25a)

- 702 store entries handled in 249.5 s with 8 parser processes (held: < 15 min). Rows in
  papers: 701 (683 manifest + 18 extras). Manifest papers (684): ok 658 (96.2 %, held >= 85 %),
  review 23, pdf 1 (2201.03458, PDF only: pdftotext text, no equations), failed 1
  (astro-ph/9407016: only PostScript files, eqf.ps and figures, no TeX), not ingested 1
  (gr-qc/9412071, PostScript stored as main.tex; download status "problem"). Failures 2 of
  684 = 0.3 % (held: <= 3 %). Of the 23 'review' papers, 18 have neither \title nor an
  abstract environment (custom title pages: SciPost, titlepage, book classes, plain TeX), so
  their score stops near 0.70; their titles must come from the metadata.
- Totals: sections 13186, chunks 71069 (body 29712, appendix 2219, caption 6584, footnote 3914,
  abstract 674, comment 27966), equations 52345 (25555 labelled), figures and tables 6655.
- Bibliography: 64248 entries (source: .bbl 400 papers, .bib 49, thebibliography 230); with an
  arXiv id 60.1 % (held: 55-75 %), arXiv id or DOI 72.5 %, no identifier 17661 entries;
  resolved through a corpus title 293. Citations 103808; distinct edges 38268, inside the corpus
  5653 = 14.8 % (held: 10-30 %).
- C1 held: 115 of 115. C3 held: 621 of 634 (97.9 %); all 13 differences are thebibliography
  papers; the one examined (1005.4054, 17 stored vs 79 counted) is a checker over-count: 62
  \bibitem lines stand after \end{document}, which LaTeX never reads. C4 held: 25654 labels in
  display environments, labels missing from the rows in 8 papers (at most 2 each in the
  listing, < 0.1 %). C5 held: 910 of 103808 keys (0.88 %) without an entry.
- C2 FAILED as worded ("all equal"): key sets equal in 50 of 52 .bib files, eprint/doi values
  differ in 8 of 17101 comparisons (3 files). Examined causes: duplicate keys in 2604.27429 and
  2512.13673 (BibTeX and kb keep the first definition; the checker's dictionary kept the last,
  bibtexparser the first), an entry with an empty key in 2310.00042 (bibtexparser keeps it, kb
  skips it), an entry bibtexparser rejects in 2606.02712 (Zhang_2024, parsed by kb). No
  field-extraction fault of kb found in these; not every one of the 8 was examined.
- C6 (added after K2-P7 was written, so no prediction was recorded): blind fuzzy matching on
  1697 entries whose written arXiv id points into the corpus: 1482 matched at ratio >= 0.93,
  all 1482 to the written id (precision 1.0), recall 0.873.
- Grouping check (brief 12.5, last item): of 5653 in-corpus edges between manifest papers,
  53.2 % stay inside one group of brief section 16, against 6.4 % expected if the cited group
  were drawn at random from the group sizes. Of 208 papers with at least 10 in-corpus
  out-edges, 5 cite no paper of their own group: 2211.08133 (G06, mostly G07), 2505.01495
  (G02, G06), 1807.11562 (G02, G07), 1905.07345 (G19, G08 93 %), 2304.13284 (G06, G13 100 %)
  [JUDGEMENT: candidates for regrouping, for the orchestrator].
- Frontier (kb frontier): every manifest paper is now in the corpus, so the top 50 are all
  outside the manifest; the most cited is 1807.06209 (81 corpus papers).
- Figures of the check run inspected: parse scores concentrated above 0.95 with a small
  group near 0.80 (no abstract environment or few sections) and the review group near 0.70;
  body chunks mostly 200-400 words, with fewer than 30 chunks above 420 (one long sentence unit
  that cannot be split outside math); the group matrix is diagonal-dominated.

### Correction to the K2-P7 entry above, and a numbering fault found by C4

- Two sentences above are wrong as written: chunks above 420 words are 49 body and 8 appendix
  chunks (query on kb.sqlite), not "fewer than 30"; and C4 lists 16 missing labels in 8
  papers, up to 5 in one paper (2402.10190), not "at most 2 each" (the check output truncates
  each list at 5). 16 of 25654 = 0.06 %, so C4 still holds.
- The 16 examined one by one: 12 lie outside \begin{document}..\end{document} (dead text after
  \end{document}: checker artifact); 1 is a figure label that the checker's regex swept into
  a display span (2309.02946: artifact); 3 are real (1611.03437 eq:Adot, 0710.5073 w2, and one
  more of the same kind): a \label on an empty last line after `\\` in eqnarray, which the
  code dropped. pdflatex on a synthetic file (scratch/kb/tmp/eqna/t.aux) shows that LaTeX
  numbers such empty lines, in eqnarray AND in amsmath align (a trailing `\\` costs one
  number): K2-P2 had not covered this case. Fixed: every line of a multi-line environment
  takes a number unless \nonumber/\notag; an empty unlabelled line takes its number but gives
  no row. The synthetic numbering test now includes these cases and agrees with LaTeX's .aux
  in all three classes (105 tests pass).

### Prediction K2-P8: re-ingestion of the whole store with the numbering fix

Counts as in K2-P7 within 1 % (papers by status identical; equation rows change by less than
1 %); C4: of the 16 missing labels only the 13 checker artifacts remain; C1, C3, C5, C6 as
before. Refuted by any change of the per-status paper counts or by a real missing label.

### Outcome P5 (run kb-20261115-132754-bb3da03; snapshot kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261115T132754Z.json)

- 124 branches, none new, removed or moved since the clone record of 13:02:32 UTC; main
  c5a0d7f9155a (2026-09-11). Bare shallow clone of all tips: 2.9 s, 17 MB; inspection of the
  124 branches with git plumbing 4 min (wall time of the run 245.6 s).
- (a) held: no branch has a line with tmunu or deposit under `src/particles`. (b) held:
  7 branches read the metric in `src/particles` (z4c/adm lines): particles_gr and
  temp/static-monopole (pushers boris, only_gr, full_gr, gca_gr; e.g. `ADM[3][3]` in
  `gca_gr.cpp`), and circumbinary_radiation, circumbinary_stable, flash-beam,
  port-radsrc-rr-tweaks-to-dyn-radiation, project/m1_vs_boltzmann (a null_geodesic pusher
  that requires an `<adm>` block). This corrects brief line 130 for particles_gr, which says
  its particle module has no reference to adm (the brief's search was presumably case
  sensitive; the hits are `ADM` in code and comments) [VERIFIED: watch snapshot, report
  `kb/reports/code_watch_upstream.md`]. (c) held: nrpic or vlasov nowhere under `src/` on any
  branch; `src/z4c` mentions particles on no branch. (d) held: no branch name with pic,
  vlasov, nrpic or deposit. (e) held.
- Answer to the package question: on 2026-11-15 13:28 UTC the particle-spacetime coupling of
  arXiv:2611.12831 (particles handing their stress-energy to Z4c) is not public in
  IAS-Astrophysics/athenak on any of its 124 branches. The brief's two unread branches
  (id_solve_porting 1319500b2037, project/collapse_relaxation 8f19675f6ac1) are now read:
  stock particle module, no coupling. Modules that mention tmunu on main: dyn_grmhd, mesh,
  outputs, tasklist, z4c.

### The first production ingest stopped, and why (run kb-20261115-132750-bb3da03)

- The re-ingest replaces a repository's rows. With `PRAGMA foreign_keys = ON` and no index
  on `symbols.file_id`, `code_chunks.file_id`, `params.file_id`, every deleted
  `code_files` row scans those tables (300k + 157k rows) for references: AthenaK did not
  finish in 3 min 46 s where the first ingest (nothing to delete) took 6 s. I stopped it by
  its process id; the transaction rolled back. Migration `0004_code_indexes.sql` adds the
  indexes (schema version 4); the ingest was restarted as run kb-20261115-133232-3f7f25a.

### Prediction P6 (before `kb link check` on the production index)

P6 All 25 curated links of `kb/curated/paper_code_links.tsv` pass `kb link check`: each line
   range exists in the stored source of 2611.12831 v1, each equation label lies in its
   range, each symbol is in the index of local/nrpic at the stated path, and each of the
   parameters named is read by the code with that block and name. Refuted by any link
   with a problem that is not a typing error of mine in the table.

### Re-ingestion run kb-20261115-134029-56dbd1c stopped (exit -15): slow deletes

- 161 of 702 papers in 10 min, against 702 in 250 s for the first ingestion into empty tables.
  Suspected cause [TO VERIFY by the next run]: re-ingesting deletes a paper's old rows, and
  with foreign keys on, SQLite checks every deleted parent row (bib entry, chunk, section)
  against the child tables (citations.bib_id, citations.chunk_id, chunks.section_id,
  equations.section_id), which have no index, so each check is a full scan. I stopped the run
  (kill of the numeric pids of the main process and its 8 workers); every paper is written in
  its own transaction, so the database stays consistent (161 papers re-ingested with the fix,
  the rest from run kb-20261115-132806-013c452). Migration 0005 adds the five indexes.
  Prediction: with them, the full re-ingestion returns to under 6 min. If it does not, the
  cause is elsewhere.

### Writer-lock starvation (run kb-20261115-133232-3f7f25a stopped) and its fix

- The second production attempt wrote 8 repositories, then waited more than 5 min for
  `locks/kb-writer.lock` (process in `do_select`, CPU time constant) while the paper ingest
  (pid 2747510) held it paper after paper. `kbtool/lock.py` polled with LOCK_NB every 0.5 s
  and missed the short gaps between two holds; at 600 s it would have raised LockTimeout and
  ended the ingest. I stopped it by its process id.
- Test written to fail on the old lock: a holder that keeps the lock 100 ms, releases it for
  2 ms and re-takes it. Old lock (`git show 3f7f25a:kb/kbtool/lock.py`): timeout after 4.02 s
  in 3 of 3 trials. New lock (waits in the kernel with flock LOCK_EX, SIGALRM for the timeout
  in the main thread, polling elsewhere): obtained in under 2 s in 4 of 4 runs
  (`tests/test_code_lockfair.py`). A first version of the test with no gap at all failed
  for the new lock once in a full-suite run: flock gives no hand-off, so a holder that
  re-takes the lock within microseconds can still win every race [VERIFIED; limit stated in
  the test]. The papers helper's running process still has the old module loaded; its next
  start picks up the new one.
- Remaining 55 repositories and local/nrpic: run kb-20261115-134736-0e94ee2 (fair lock).

### Outcome P6 (run kb-20261115-135323-534eb86)

- P6 held: 25 of 25 curated links pass `kb link check` (line ranges, labels in range,
  symbols at the stated paths, 22 named parameters read with that block and name) against
  the production index; loaded into impl_links (25 rows, status claimed). Output
  `kb/reports/code_links_check.txt`. The check is able to fail: the unit test's bad row
  (wrong lines, label, symbol, parameter) gives 4 problems.
- Explicit links: 339 repository addresses in the stored sources of 121 papers, 23 distinct
  manifest repositories among them (`kb/reports/code_links_explicit.tsv`). The source of
  2611.12831 itself contains no repository address (no code-availability link); AthenaK's
  address occurs in 2409.10383, 2409.10384 and 2409.16053.

### Outcome P4 (run kb-20261115-135337-45ab9d0): refuted for this tree

- Upstream AthenaK: 8670 input lines, literal 6356, computed block 1871, other block 9,
  unmatched 434: 94.9 % (held). Athena++: 4886 lines, 92.8 % (held). This tree (29 input
  files under problems/): 2549 lines, literal 1816, computed block 351, unmatched 382:
  85.0 %, below the 90 % of the prediction: refuted as stated.
- Reading the unmatched list: most are names the code builds at run time
  (`<particles> p0_x1` ... read as `pre + "x1"`, `<z4c> co_0_type` read as
  `"co_" + nstr + "_type"`, fastflow `center_x_0`, probes `probe1_x1`), which my comparison
  only allowed for computed blocks, not computed names; and the `<comment>` block (27 lines),
  which AthenaK keeps as documentation (`athenak/src/parameter_input.cpp` line 106).
  Hypothesis, not yet a cause: the code reads nearly all of these.

### Prediction P4' (before the rerun with computed-name patterns)

P4' With a computed name matched against the literals of its expression (status `pattern`,
   weaker evidence) and the `<comment>` block counted apart, at least 97 % of the
   non-comment input lines of this tree and of upstream AthenaK are read; what stays
   unmatched is a list of genuinely unread or misspelled options and of names built from a
   plain variable (no literal to match). Refuted if more than 3 % of the non-comment lines of
   either stay unmatched.
