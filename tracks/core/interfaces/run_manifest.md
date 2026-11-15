# Interface: run manifest (proposal for `coord/INTERFACES/run_manifest.md`)

Status: PROPOSAL (core, 2026-11-15). Sources: the brief, section 11.6 (lines 1152-1188,
the example manifest); `CLAUDE.md` rule 4 (fields every session must record);
`harness/RULES.md` (plain-git protocol until `harness/bin/nrpic-run` exists). The
example at the end is the manifest of test D1 of this package. Field names follow the
brief's example; the fields the brief's example lacks but `CLAUDE.md` requires
(`command`, `cwd`, `kind`, cores and card-hours) are added.

## 1. Location and identity

- One file per run: `tracks/<ID>/runs/<run_id>/manifest.json`, JSON, UTF-8.
- `run_id = <owner>-<YYYYMMDD-HHMMSS>-<commit7>`: owner id as in `CLAUDE.md` (`core`,
  `A-emd-pbh`, ...; the brief's example uses the short form `A`), UTC time of
  registration, first seven hex digits of the commit the run is built from.
- Outputs under `scratch/<ID>/<run_id>/` with a `sha256sums.txt` of every file kept.

**Blocking issue [VERIFIED].** The ignore rule `runs/` (`.gitignore` line 12) matches
every directory named `runs`, so `tracks/<ID>/runs/<run_id>/manifest.json` cannot be
committed without `-f`, which `CLAUDE.md` forbids ("Nothing is committed that the ignore
list excludes"). Proposal: change the rule to `/runs/` (the untracked top-level
directory of the earlier project) so that `tracks/*/runs/` is tracked. Until then this
package keeps a copy of its manifest in `check/`.

## 2. Fields

| Field | Type | Required | Content |
|---|---|---|---|
| `run_id` | string | yes | as above |
| `track` | string | yes | owner id |
| `work_package` | string | no | package name of the wave plan |
| `gate` | string | yes | `G0` ... `G4` the run serves |
| `purpose` | string | yes | one sentence: what the run establishes |
| `kind` | string | yes | `scouting` or `production` (production only after the tag the run depends on exists, charter "What differs", item 1) |
| `preregistered_in` | string | yes for production | file and anchor of the written prediction |
| `git` | object | yes | `sha` (full or 7), `branch`, `dirty` (bool), `dirty_note` if dirty, `merge_base_main` (brief) |
| `code` | object | yes | `executable` (path), `executable_sha256`, `executable_built` (time; say if it predates source commits the run relies on), `core_tag` when one exists, `problem` (pgen name), `cmake_flags` when built for the run, `athenak_upstream_sha`, `kokkos_sha` (brief; may be null until recorded by core) |
| `env` | object | brief | `host`, `machine_file_sha256`, `uv_lock_sha256`, `container_digest`, `compiler`, `mpi`, `gpu` (brief's fields; `nrpic-env hash` will fill them) |
| `cwd` | string | yes | working directory of each command |
| `command` | list of strings | yes | every command, in order, exactly as run (including the initial-data generation and the analysis) |
| `inputs` | list of objects | yes | `file` (path relative to the repository or absolute), `sha256`; overrides on the command line as `overrides` (brief: `{"mesh/nx1": 256}`) |
| `resources` | object | yes | `nodes`, `gpus`, `cores`, `card_hours` (0 for processor runs), `walltime_s`, `particles` |
| `outputs` | object | yes | `dir` (`scratch/<ID>/<run_id>`), `sha256sums` (file name in that directory), `bytes`, `kept_in_git` (figures or summaries copied into the track) |
| `status` | string | yes | `registered`, `running`, `completed`, `failed`, `stopped` |
| `exit_code` | int | when ended | |
| `started`, `ended` | string | yes | ISO 8601 UTC |
| `parents` | list | yes | run ids this run restarts from or depends on |
| `notes` | string | no | outcome in one line, failed predictions included |

Rules carried from the brief (line 1158): the harness refuses a dirty worktree, writes
and commits the manifest before the start, fills checksums and status afterwards and
commits again, and refuses runs beyond the budget of the charter. By hand, the same
steps apply; a dirty worktree is allowed only for untracked files outside the source
tree, stated in `dirty_note`.

## 3. Example (test D1 of this package)

`tracks/core/runs/core-20261115-112600-b7b431d/manifest.json` (copy in
`check/manifest_core-20261115-112600-b7b431d.json`):

```json
{
  "run_id": "core-20261115-112600-b7b431d",
  "track": "core",
  "gate": "G1",
  "purpose": "Test D1: every output file of the NRPIC module, read back with readers written from diagnostics.md; restart compared with the uninterrupted run",
  "kind": "scouting",
  "preregistered_in": "tracks/core/interfaces/JOURNAL.md (entry 11:25)",
  "git": {"sha": "b7b431d", "branch": "core/nrpic", "dirty": true,
          "dirty_note": "only untracked files under tracks/core/"},
  "code": {"executable": "/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena",
           "executable_sha256": "91f2e2c2...547403",
           "executable_built": "2026-11-14T06:03:37-08:00", "problem": "nrpic_cosmo"},
  "cwd": ".../scratch/core/core-20261115-112600-b7b431d/run1",
  "command": ["python3 make_lattice.py --n 16 ...", "athena -i d1_formats.athinput", "..."],
  "inputs": [{"file": "tracks/core/interfaces/check/d1_formats.athinput", "sha256": "73f3c735..."}],
  "resources": {"nodes": 1, "gpus": 0, "cores": 1, "card_hours": 0.0,
                "walltime_s": {"run1": 3.38, "run2": 1.48}, "particles": 4096},
  "outputs": {"dir": "scratch/core/core-20261115-112600-b7b431d", "sha256sums": "sha256sums.txt",
              "bytes": 37420635},
  "status": "completed", "exit_code": 0,
  "started": "2026-11-15T11:22:20Z", "ended": "2026-11-15T11:23:40Z",
  "parents": []
}
```

## 4. Proposed rules (JUDGEMENT)

1. A number enters a note only with its `run_id` (or a knowledge-base locator); the
   manifest's `notes` holds the one-line outcome so that a reader can find failed runs.
2. The executable is identified by checksum and build time, since the shared
   executables of the main checkout can lag the source (`JOURNAL.md`, 11:21).
3. A restart chain is one manifest per segment with `parents` linking them, or one
   manifest with every segment's command listed; `scripts/submit_chain.sh` should write
   the first form.
