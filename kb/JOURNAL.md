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
