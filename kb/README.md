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
