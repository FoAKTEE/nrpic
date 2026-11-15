# kb/: the knowledge base tools (brief section 12), stages K0-K1

Data live in `/data/haiyangw/nrpic/kb-data/` (not in git; layout of brief 12.2). This
directory holds the code, the manifests extracted from the brief, the schema, tests and
reports. Predictions and outcomes are in `JOURNAL.md`.

## What is here

| Path | What |
|---|---|
| `bin/kb` | the `kb` command; runs under the system `python3 -I` from any directory (standard library only) |
| `kbtool/brief.py` | extraction of the manifests (brief section 17) and the schema (brief 12.2) by script, with line provenance |
| `kbtool/inventory.py` | `kb verify-downloads`: manifests against `kb-data/raw`, recomputed from the bytes |
| `kbtool/sniff.py` | file type from content (gzip-tar, gzip-tex, pdf, html, ...), bounded gunzip, safe extraction, tree scan |
| `kbtool/gitmeta.py` | commit and licence of a repository checkout read as files (git is never run inside a download) |
| `kbtool/db.py`, `lock.py`, `paths.py` | database creation, migrations, snapshots; the writer lock `locks/kb-writer.lock`; locations |
| `kbtool/cli.py` | subcommands: `init`, `manifests`, `status`, `verify-downloads`, `fetch-missing`, `snapshot`, `show` (download record only) are built; `search`, `code`, `frontier`, `watch upstream`, `ingest`, `resolve-bib`, `embed`, `eq`, `cites`, `link`, `claim`, `export`, `qa` are stubs that name their stage and exit 3 |
| `schema.sql` | the SQL block of brief 12.2 (lines 1277-1347), unchanged; schema version 1 |
| `migrations/0002_downloads.sql` | tables `downloads`, `repo_downloads` (K1 results; `papers` needs titles, which come with the metadata stage) |
| `manifests/arxiv.tsv`, `github.tsv`, `SOURCE.json` | 684 arXiv rows (`id group priority`), 63 repositories (`repo role owners description`), brief sha256 and line ranges: brief line of row i (0-based) = first_line + i |
| `reports/verify-downloads.md` | the latest inventory report (ids, kinds, sizes, hashes; no paper text) |
| `reports/fig_inventory.png` | figure of that inventory |
| `scripts/registered_run.py` | runs a command as a registered run (`tracks/kb/runs/<run_id>/manifest.json`, outputs in `scratch/kb/<run_id>/`) |
| `scripts/fig_inventory.py` | the inventory figure (project style `python/nrpic/figstyle.py`) |
| `tests/` | 52 tests (pytest); synthetic stores built with the fetch command's own `unpack` |
| `pyproject.toml`, `requirements-k0.lock` | the tool environment `kb/.venv` (uv venv, Python 3.10.12) and its frozen package list |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
# environment (once): uv venv kb/.venv && uv pip install --python kb/.venv/bin/python -e 'kb[k0]'
#   (UV_CACHE_DIR=/data/haiyangw/nrpic/scratch/kb/tmp/uvcache)
(cd kb && .venv/bin/python -m pytest)            # 52 tests; temporary files under scratch/kb/tmp/pytest
kb/bin/kb manifests --check                      # kb/manifests equal to the brief?
kb/bin/kb init                                   # K0: kb-data directories, kb.sqlite (idempotent)
kb/bin/kb verify-downloads --report kb/reports/verify-downloads.md
                                                 # K1: writes kb-data/manifests/{SHA256SUMS,inventory.json},
                                                 # table downloads, a log under kb-data/logs; exit 1 on problems
kb/bin/kb status [--json] [--write-state]        # counts, schema version, snapshot id
kb/bin/kb fetch-missing --priority 3 [--dry-run] # hands the missing ids to harness/bin/nrpic-fetch-arxiv
kb/bin/kb snapshot                               # freeze kb.sqlite, move db/current
kb/.venv/bin/python kb/scripts/fig_inventory.py kb-data/manifests/inventory.json <out>
```

A registered run: `python3 -I kb/scripts/registered_run.py --purpose "..." -- <command>`
(`--detach` for background jobs; `--finish <run_id> --exit-code N` fills the wall time).

## Rules this code keeps

- Everything under `kb-data/raw` is bytes: never executed, compiled or imported; archives are
  listed with `tarfile` and checked member by member; no `git` inside a downloaded checkout.
- Every write to `kb-data` (database, manifests copy, SHA256SUMS, inventory, logs) is inside
  the flock `locks/kb-writer.lock`.
- arXiv downloads only through `harness/bin/nrpic-fetch-arxiv` (`kb fetch-missing` calls it,
  one process, sequential). Entries other sessions add are reported as "extra", never errors.
- Limits [JUDGEMENT]: 256 MiB per extracted file, 1 GiB per paper, 2 GiB decompressed gzip,
  20000 archive members.

## State and next steps (K1 still open)

- Store on 2026-11-15 11:28 UTC (run `kb-20261115-112823-3ac74c2`): priority 3 complete,
  47 of 47 ok; priority 2: 9 of 160; priority 1: 1 of 477; 4 extras added by other sessions;
  0 problems. The priority-3 download was run `kb-20261115-112522-3ac74c2` (process 966412,
  finished, log `scratch/kb/kb-20261115-112522-3ac74c2/stdout.log`).
- Next: `python3 -I kb/scripts/registered_run.py --detach --purpose "..." -- kb/bin/kb
  fetch-missing --priority 2 --ids-file '{run_dir}/ids.txt'`, then priority 1, one background
  job at a time, each followed by `kb verify-downloads`.
- Snapshot `kb-data/db/kb-20261115-b715da3.sqlite` is `db/current`.
- Not done in K1: metadata from the arXiv API and INSPIRE (titles, authors, abstract,
  categories, licence, record number, DOI) and the cross-check of title and authors with
  brief section 16 (`papers.title_matches_brief`); repositories (none downloaded); AthenaK
  branch tips for the upstream watch. See Requests.

## Code: K6-K7 (repositories, code index, parameter index, paper-code links, upstream watch)

Under decision 0010 the repositories are read and indexed only: nothing in a clone is
built, run or imported. Modules `kbtool/code_*.py`, `kbtool/links_*.py`; journal entries
"K6-K7 helper" in `JOURNAL.md` (predictions R1, P2-P6 and outcomes).

| Path | What |
|---|---|
| `kbtool/code_fetch.py` | `kb fetch-repos`: `git clone --depth 1` of each manifest repository into a new directory, moved into `kb-data/raw/github/<owner>__<repo>/` (files made read-only); record `kb-data/meta/github/<owner>__<repo>.json` (url, commit, dates, default branch, licence, size, command; AthenaK: all remote branch tips). git runs with the user's configuration off (no credential helper, no prompt, https only, no submodules, no LFS, symlinks as files, fsck) |
| `kbtool/code_symbols.py` | symbols: C/C++/CUDA with tree-sitter (Kokkos/CUDA attribute macros blanked to the same length), Python with `ast`, Fortran with line patterns |
| `kbtool/code_params.py` | every ParameterInput call (`Get*`, `GetOrAdd*`, `Set*`, `DoesParameterExist`, `DoesBlockExist`) with block, name, default, line; athinput parser; inputs-against-code comparison |
| `kbtool/code_index.py` | `kb ingest repo [--repo R ... \| --all] [--this [--ref main]]`: files, symbols, parameters, chunks into `kb-data/build/code/<key>/` and the tables repos, code_files, symbols, code_chunks, code_fts, params. `--this` indexes this repository (repo_id `local/nrpic`: athenak/src, python/nrpic, cosmo, problems) from git objects at a ref |
| `kbtool/code_query.py` | `kb code "SYMBOL or text" [--repo R\|this\|athenak] [--kind function\|class\|param\|file\|text]`: exact symbols, then parameters (`name`, `block/name`, `<block> name`), files, symbol prefixes, full text (BM25) |
| `kbtool/code_watch.py` | `kb watch upstream`: ls-remote diff of IAS-Astrophysics/athenak against the last snapshot, bare shallow clone of all branch tips, inspection of every branch (src/particles, src/z4c, pushers, coupling lines), snapshot `kb-data/meta/github/watch/...` and a report with a message for core |
| `kbtool/links_paper_code.py` | `kb link check\|load\|list\|add\|explicit`: curated links checked against the paper source and the index, loaded into impl_links; repository addresses found in the stored paper sources |
| `curated/paper_code_links.tsv` | 25 links from statements of the method of arXiv:2611.12831 (line ranges and labels of the stored v1 source) to functions of this repository, with parameters, evidence (core's interface documents on core/nrpic) and named tests; all `claimed` |
| `migrations/0004_code_indexes.sql` | indexes on the code tables (without them a re-ingest is quadratic in foreign-key checks) |
| `scripts/code_crosscheck.py` | test P2/P3: second, tree-sitter parameter extractor; column-0 method definitions against the symbol index |
| `scripts/code_report.py`, `scripts/fig_code_watch.py` | reports and figures below |
| `reports/code_index.md`, `code_params.md`, `code_params_*.tsv`, `code_links_check.txt`, `code_links_explicit.tsv`, `code_watch_upstream.md`, `fig_code_*.png` | results (no paper text, no code fragments of repositories without a licence) |
| `tests/test_code_*.py` | 20 tests: parameter parser, symbols, clone/ingest/query/watch/links end to end on a local file:// remote, licence rules, fair writer lock |

Rerun (all registered as runs with `scripts/registered_run.py`):

```bash
cd /data/haiyangw/nrpic/wt/kb
uv pip install --python kb/.venv/bin/python -e 'kb[k0,code]'      # tree-sitter (requirements-k6.lock)
(cd kb && .venv/bin/python -m pytest tests/test_code_*.py --basetemp=/data/haiyangw/nrpic/scratch/kb/tmp/pytest-code)
python3 -I kb/bin/kb fetch-repos [--repo owner/name] [--refresh]   # about 3 min for all 63
kb/.venv/bin/python -I kb/bin/kb ingest repo --all --this --ref main  # about 15 min; needs the venv (tree-sitter)
python3 -I kb/bin/kb link check > kb/reports/code_links_check.txt && python3 -I kb/bin/kb link load
python3 -I kb/bin/kb watch upstream --report kb/reports/code_watch_upstream.md   # weekly
kb/.venv/bin/python -I kb/scripts/code_report.py kb/reports
python3 -I kb/bin/kb snapshot                                      # readers use db/current
python3 -I kb/bin/kb code NrpicDepositSources ; python3 -I kb/bin/kb code "z4c/kappa1" --kind param
```

Results (2026-11-15; journal "K6-K7 helper"):

- 63 of 63 manifest repositories cloned (run `kb-20261115-130232-ac33aa1`, 156 s, 1.74 GB of
  checkouts); no name failed to resolve. Commits and licences: `reports/code_index.md`.
- Code index of 64 repositories (runs `kb-20261115-133232-3f7f25a` and
  `kb-20261115-134736-0e94ee2`): 68037 files, 305733 symbols, 157184 chunks, 3454
  parameter rows; snapshot `kb-20261115-c8703d7.sqlite` (`db/current`). Cross-checks P2/P3:
  two independent parameter extractors agree on all calls (AthenaK 1165, this tree 1259,
  Athena++ 999, Parthenon 384) and all column-0 method definitions are symbols.
- Parameter index: `reports/code_params.md` (the `<particles>` options of NRPIC with
  defaults and lines), full tables `reports/code_params_*.tsv`; input files against code:
  99.3 % (this tree) and 98.7 % (AthenaK) of the non-comment lines are read; `<z4c> nco` is
  set in inputs and read by no code.
- Paper-code links: 25 of 25 pass `kb link check` (`reports/code_links_check.txt`), all
  `claimed`; repository addresses in 121 stored paper sources: `reports/code_links_explicit.tsv`
  (none in 2611.12831).
- Upstream watch (run `kb-20261115-132754-bb3da03`, `reports/code_watch_upstream.md`,
  `fig_code_watch.png`): main still c5a0d7f; 124 branches, all inspected; no branch hands
  particle stress-energy to Z4c (no tmunu or deposit in any `src/particles`), no nrpic or
  vlasov anywhere; 7 branches read the metric in `src/particles` (particles_gr and six
  others), which corrects brief line 130 for particles_gr.

## Papers: K2-K3 (TeX structure, bibliography, citation graph)

Modules `kbtool/tex_*.py`, `kbtool/bib_*.py`, `kbtool/papers_*.py`; journal entries "K2-K3
helper" in `JOURNAL.md` (predictions D2, K2-P1 to K2-P8 and outcomes). Everything under
`kb-data/raw` is read as text from outside the tree; nothing in it is compiled or executed
(pdflatex runs only on synthetic documents the tests write, to read LaTeX's own numbers).

| Path | What |
|---|---|
| `kbtool/tex_files.py` | main file (00README.json/.XXX hints, `\documentclass`+`\begin{document}`, `\input` graph, .bbl name, size); flattening of `\input`, `\include`, `\subfile`, `\import`, `\subimport` inside the tree only (no `..`, absolute paths or links; depth, size and cycle limits) with a source map offset -> file, line, column; comments (`%`, `comment` environment, `\iffalse..\fi`) stripped with TeX semantics and kept separately |
| `kbtool/tex_macros.py` | `\newcommand`, `\renewcommand`, `\providecommand`, `\def` (undelimited parameters), `\DeclareMathOperator`; text-level expansion with optional arguments, bounded in depth and size; environment shorthands (`\be` -> `\begin{equation}`) |
| `kbtool/tex_structure.py` | title, authors, abstract; section tree (number, title, label, character range; appendix A, A.1); display equations (equation, align, gather, multline, eqnarray, flalign, alignat, `\[ \]`, `$$`), one row per numbered line group, numbers as LaTeX computes them (checked against pdflatex .aux for article, `\numberwithin`, revtex4-2); figures and tables (caption, label, files, number); footnotes; `\cite` with keys and offsets; label map |
| `kbtool/tex_text.py` | plain text (pylatexenc 2.11 with fixes for `\texttt`, `\textsf`, `\mbox`, `\href`; `\ref` -> computed numbers; stdlib fallback); sentences; chunks of 200-400 words with about 15 % overlap, never cut inside a display equation; equation normalisation (`tex_norm`) and symbols |
| `kbtool/bib_parse.py` | .bbl (natbib/REVTeX `\bibitem`, biblatex `\entry`), .bib (tolerant parser, standard library), inline thebibliography; arXiv ids (new form with month and length check, old form with the archive list), DOIs, eprint field; source preference |
| `kbtool/bib_resolve.py` | corpus resolution (written arXiv id, corpus DOI, fuzzy title ratio >= 0.93), citation edges and `in_corpus`, `kb frontier`, `kb cites`, group matrix and group check |
| `kbtool/papers_ingest.py` | `kb ingest arxiv`: parse (parallel) and write (serial, writer lock, one transaction per paper) into papers, sections, chunks(+fts), equations(+fts), figures, bib_entries, citations and `kb-data/build/tex/<id_>/{flat.tex, doc.json, sourcemap.json}`; quality score and `parse_status` ok / review / pdf / failed; only downloads that `check_paper` verifies |
| `kbtool/papers_cli.py` | `kb ingest arxiv [--id ID ... \| --priority N ... \| --all \| --new] [--extras] [--jobs 8]`, `kb resolve-bib`, `kb frontier [-n 50]`, `kb cites ID [--in\|--out] [--context]`, `kb export ID`, `kb show ID --abstract\|--section N\|--eq LABEL\|--fig N`, the paper counts of `kb status` |
| `migrations/0003_papers_k2.sql`, `0005_papers_fk_indexes.sql` | locators (character ranges into flat.tex and its sha256, figure/table kind, bibliography source, cite key and offset); indexes on the foreign-key child columns |
| `scripts/papers_checks.py` | independent checks C1-C6 (main file without hints vs 00README; .bib vs bibtexparser; entry counts vs `\bibitem`; labels in display environments; keys without entries; blind fuzzy matching vs written ids) and the figures `fig_papers_k2.png`, `fig_citations_k3.png` |
| `reports/papers_k2k3.md`, `reports/fig_papers_k2.png`, `reports/fig_citations_k3.png` | results of the final runs (counts and ids only, no paper text) |
| `tests/test_tex_*.py`, `test_bib_parse.py`, `test_papers_ingest.py` | 42 tests: comments, paths, flattening, main file, numbering against pdflatex, macros, text, chunks, identifiers, .bbl/.bib, ingestion end to end on a synthetic store |

Rerun (each registered with `scripts/registered_run.py`):

```bash
cd /data/haiyangw/nrpic/wt/kb
(cd kb && .venv/bin/python -m pytest tests/test_tex_*.py tests/test_bib_parse.py tests/test_papers_ingest.py)
python3 -I kb/bin/kb fetch-missing --priority 3 2 1        # one process, exec of nrpic-fetch-arxiv
python3 -I kb/bin/kb verify-downloads --report kb/reports/verify-downloads.md
python3 -I kb/bin/kb ingest arxiv --all --extras --jobs 8  # re-executes under kb/.venv; about 5-7 min
kb/.venv/bin/python -I kb/scripts/papers_checks.py <out_dir>
python3 -I kb/bin/kb snapshot ; python3 -I kb/bin/kb status
python3 -I kb/bin/kb show 2611.12831 --eq eq:vlasov ; python3 -I kb/bin/kb frontier -n 50
```

State on 2026-11-15 14:00 UTC (details and run ids in `reports/papers_k2k3.md`): manifest
683 of 684 downloaded and verified (gr-qc/9412071 is PostScript only), 0 failed downloads, 18
extras; 701 papers ingested (676 ok, 23 review, 1 PDF only, 1 failed: astro-ph/9407016 has no
TeX); 64248 bibliography entries, 60.1 % with an arXiv id; 14.8 % of the citation edges inside
the corpus. Snapshot `kb-data/db/kb-20261115-5ba1ab3.sqlite` is `db/current` (schema 5).

## Requests

1. **orch: ignore list.** The pattern `runs/` of the shared `.gitignore` also matches
   `tracks/<ID>/runs/`, so run manifests need `git add -f` (core and kb both did). Proposal:
   anchor it as `/runs/` or add `!tracks/*/runs/`.
2. **orch: metadata downloads.** K1 needs the arXiv API (title, authors, abstract,
   categories, version, licence) and INSPIRE (`eprint <id>`, checking `hits.total`) for every
   paper. The rule "every arXiv download through nrpic-fetch-arxiv" leaves no sanctioned path
   for the API. Proposal: a `--meta` mode of `nrpic-fetch-arxiv` (same lock, same 3 s gap,
   generic client name) that writes `kb-data/meta/arxiv/<id_>.api.xml` and
   `<id_>.inspire.json`, or permission for kb to do it under the same lock file.
3. **orch: hardening of nrpic-fetch-arxiv** (found while reading it; `kb verify-downloads`
   catches each case after the fact):
   (a) no size limits: `gzip.decompress` is unbounded and `extractall` has no per-file or
   total limit (brief 12.3 asks for limits);
   (b) an HTML or error page served with status 200 is stored as `src/main.tex` with
   status ok; a content check before recording ok would stop it;
   (c) `print` without `flush=True`, so a background log shows nothing until the end;
   (d) the version comes from the first `v<digits>` in Content-Disposition, with "vX" when
   absent; verify-downloads cross-checks the id part and flags "vX".
4. **orch: repositories under decision 0010.** Which of the 63 repositories of brief
   section 17 are cloned for indexing only (reading, never building or running), and with
   which command (a shallow clone at a pinned commit with hooks disabled, record in
   `kb-data/meta/github/`)? AthenaK upstream (`IAS-Astrophysics/athenak`) is the one the
   upstream watch needs.
5. **orch: legacy copies.** Eight manifest ids have older copies under `refs/arxiv_*`
   (2611.12831, 1711.06681, 1908.05683, 1904.07841, 1905.08890, 2001.07968, 1101.3555,
   1111.2997). Once the store holds them, `CLAUDE.md` could point readers at
   `kb-data/raw/arxiv/<id>/<v>/src` instead.
6. **orch: PostScript-only papers** (K2-K3). Two manifest ids have no TeX source: arXiv
   serves gr-qc/9412071 as a gzipped PostScript file, which `nrpic-fetch-arxiv` stores as
   `src/main.tex` with status ok (kb verify-downloads: "not an e-print"); astro-ph/9407016 is a
   tar of PostScript files only. Turning PostScript into text needs an interpreter
   (ghostscript), which would execute the downloaded program; brief 12.2 has `source.pdf` for
   this case. Proposal: a `--pdf` mode of the fetch command (same lock and gap) that stores
   `https://arxiv.org/pdf/<id>` as `source.pdf`; kb then extracts text with pdftotext as it
   does for 2201.03458.
7. **orch: metadata, again** (K2-K3). 36 ingested papers have no `\title` (custom title pages,
   plain TeX, theses; 18 of them are why 23 papers are on the review list) and 27 no abstract
   environment; the abstract-similarity part of the quality score and every INSPIRE look-up
   of bibliography entries without an identifier (17661 entries, 27.5 %) wait for Request 2.
8. **orch: grouping of brief section 16** (K3, brief 12.5 last item) [JUDGEMENT]: 53.2 % of
   the in-corpus citation edges stay inside one group (6.4 % expected at random), so the
   grouping agrees with the citation clusters overall. Five papers with at least 10 in-corpus
   out-edges cite no paper of their own group: 2211.08133 (G06; cites G07), 2505.01495 (G02;
   G06), 1807.11562 (G02; G07), 1905.07345 (G19; G08 93 %), 2304.13284 (G06; G13 100 %).
   Candidates for regrouping; the orchestrator decides.
9. **orch: frontier** (K3, brief 12.5): `kb frontier -n 50` (list in
   `reports/papers_k2k3.md`) is the weekly list of works cited most by the corpus but absent
   from it; 49 of the 50 are outside the manifest (the 50th is gr-qc/9412071, in the manifest
   but PostScript only, Request 6); additions are the orchestrator's decision.
10. **orch (brief line 130, section 2.2):** the K6 watch corrects one statement: on
   particles_gr (8b04c1a8589d) `src/particles` does refer to the ADM metric (`ADM[3][3]` in
   `gca_gr.cpp`, comments in `boris_gr.cpp`; relativistic pushers in a given spacetime). The
   conclusion stands: no branch hands particle stress-energy to Z4c
   (`reports/code_watch_upstream.md`). Request 4 is answered by this package: all 63
   repositories are cloned for reading only with `kb fetch-repos`; a weekly
   `kb watch upstream` needs a scheduler (orch's choice).
11. **core:** please review `curated/paper_code_links.tsv` (25 links from statements of the
   method of 2611.12831 to functions at main, derived from your interface documents) and
   name the test that upgrades each link from `claimed` to `verified` (`kb link add ...
   --status verified --evidence <run id>`). Inputs set `<z4c> nco` (problems/jeans/jeans.athinput
   line 127), which no code reads.
12. **kb (papers helper):** `kbtool/lock.py` now waits in the kernel (the old 0.5 s poll was
   starved by the paper ingest re-taking the lock paper after paper; test
   `tests/test_code_lockfair.py`); a running process keeps the old module until restarted.
   Migration numbers: 0004 is the code indexes; 0003 and 0005 are yours.
13. **orch:** `kb ingest repo` needs `kb/.venv` (tree-sitter); `kb code` and the rest run under
   the system `python3 -I`.
