# KB-G0: report of the independent verifier

Verifier: helper `verify_g2` of kb (wave 3; batch 2b, 2026-11-21), the same session that
verified KB-G2 (tracks/kb/stage/KB-G2/VERIFIER.md; method and independence rules there). Until
this file was committed I did not open tracks/kb/stage/** (other than writing the two
VERIFIER.md files), the lead's STATUS/HANDOFF/JOURNAL/RISKS/PLAN-wave3, kb/QA_REPORT.md or
kb/STATE.json. Evidence: run kb-20261121-080038-306bcdd (checks.json; script
tracks/kb/verify_g2/scripts/checks_c1_c5_c6.py), journal entries 7-8 of
tracks/kb/verify_g2/JOURNAL.md.

## Verdicts

| Criterion | Verdict | My numbers | Run |
|---|---|---|---|
| C1a tools chosen | **CONFIRMED** | kb/pyproject.toml declares pyyaml, pylatexenc, bibtexparser, rapidfuzz, tenacity, numpy, matplotlib, pytest; the environment kb/.venv is frozen in requirements-k0/k4/k6.lock (README.md:26); search uses SQLite FTS5 and sentence-transformers (bge-small-en-v1.5@5c38ec7), symbols tree-sitter | kb-20261121-080038-306bcdd |
| C1b reasons recorded | NOT CHECKED (in part seen) | reasons found for the embedding model and the fusion constant (kb/EMBEDDING.md, "Why this model", "k = 10 chosen on the K9 set ... kb-20261115-164430-5aca10c") and for tree-sitter over universal-ctags (pyproject.toml comment); the brief asks for the reasons in JOURNAL, which I may open only for C9, so the rest is not checked | same |
| C1c directories of brief 12.2 in place | **CONFIRMED** | kb-data: raw/arxiv, raw/github, meta/arxiv, meta/github, build/tex, build/code, db (kb.sqlite, current, snapshots), manifests (arxiv.tsv, github.tsv, SHA256SUMS), logs: all present. kb/: pyproject.toml, schema.sql, migrations/, kbtool/, golden/questions.yaml, curated/paper_code_links.tsv, curated/equation_tags.yaml, tests/, QA_REPORT.md, STATE.json present; two named files absent: `uv.lock` (replaced by requirements-k*.lock) and `curated/seed_claims.jsonl` | same |
| C2 read-only access by default | **CONFIRMED** | readers default to db/current (help text of search, show, eq, cites, code, frontier, export; kbtool/db.py `open_for_read`), open it `mode=ro`; dynamic test in a fake data root: the default read the snapshot, not kb.sqlite, and left its bytes unchanged; all 9 snapshot files 0444 | same |
| C3 snapshots at the end of the stages, ids recorded | **CONFIRMED** | 9 snapshots, each 0444 with sha256 starting with the 7 hex digits of its name; the wave-1/2 runs record their ids in their logs: kb-20261115-141500-b2e57be -> f2fcda5 ("for the KB-G1 package"), kb-20261115-164041-5aca10c -> 621430e, kb-20261115-183921-31d5b77 -> a848a06; KB-G2's kb-20261119-161451-e15d1b8 -> a782f1e; ingest_log of a782f1e holds 8 snapshot rows (b715da3 ... a848a06) | same |
| C6 failed runs on record | **CONFIRMED** (manifests) | 2 kb run manifests with status failed (kb-20261115-182907-3f69615, kb-20261119-143242-737909d); ingest_log: 2 ingest-arxiv failed, 63 review, 5 skipped rows. Journal part: addendum of the KB-G2 report | same |
| Package documents, currency of STATUS | NOT CHECKED | the lead's | |

## Defects

1. The layout of brief 12.2 names `kb/uv.lock` and `kb/curated/seed_claims.jsonl`; neither
   exists. The lock is replaced by three pip-style lock files (documented, README.md:26, 116);
   for the seed claims I found no replacement named in the files I may read (the working
   database held 700 claims right after the snapshot, status.json of
   kb-20261119-161451-e15d1b8). Minor.
2. "Raw files are read-only" (brief 12.1) holds by convention only: the 736
   raw/arxiv/*/*/source.bin files have mode 0664 (one Unix user for all sessions, so file modes
   could not separate owners anyway). Minor.
3. Reasons for most tool choices (pylatexenc over LaTeXML or pandoc, bibtexparser, rapidfuzz,
   FTS5 over the vector stores the brief lists) are not in kb/README.md or kb/EMBEDDING.md; if
   they are only in the lead's JOURNAL, a reader of the tool's own documentation does not find
   them.

## Not checked

- The reasons for the tool choices recorded in tracks/kb/JOURNAL.md (C1b), see above.
- Whether every snapshot was taken at the end of a stage rather than in between (four
  snapshots of 2026-11-15 between 13:56Z and 18:39Z are not tied to a stage by anything I read
  except the three named runs).
- The package documents and the currency of STATUS.

## Requests

To the kb lead: name in kb/README.md (one line each) why each K0 tool was chosen or rejected,
or point there to the JOURNAL entry; say what replaced `curated/seed_claims.jsonl`.

## Comparison with the package (written after the verdicts were committed in ef9d2d34)

Read: tracks/kb/stage/KB-G0/CHECKLIST.md (collected 2026-11-15T18:29:11Z). No verdict above was
changed.

Agree: the layout of brief 12.2 under kb-data; the frozen environments requirements-k0/k4/k6.lock;
the readers' default db/current and snapshot mode 0444; the snapshots and their runs
(f2fcda5 / kb-20261115-141500-b2e57be, 621430e / kb-20261115-164041-5aca10c, 3826a68 /
kb-20261115-182741-7dafdf9, 44b7406, a848a06 / kb-20261115-183921-31d5b77), all of which I found
with matching sha256 prefixes and mode 0444.

Differ:
- C1: the package points to kb/JOURNAL.md for the reasons of the tool choices; I did not open
  it for that (my task allowed the journal for C9 only), so C1b stays NOT CHECKED. The package
  does not mention the absent `uv.lock` and `curated/seed_claims.jsonl`.
- C6: the package names three failed wave-1 runs; two of them (kb-20261115-154858-b0d8c8f,
  kb-20261115-164121-5aca10c, exit code 1) are recorded with the status word "finished", which
  nrpic-run reads as completed, and the third (kb-20261115-181519-d78b8d4) as completed with
  exit 0 (its failure, a misplaced output, is in the journal only) (run
  kb-20261121-081226-a4025cf). My manifest scan therefore counted 2 failed runs, not 5. The
  verdict stands (failed runs are on record), with this defect of the record.
- C5 of the package (verifier) was FAIL for want of a verifier; this report is that verifier's.
