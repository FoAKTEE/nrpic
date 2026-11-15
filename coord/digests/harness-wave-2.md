# Harness fixes of wave 2 (2026-11-15, 15:20-15:55Z)

Written by the harness helper of the orchestrator, from the main checkout. Commits on main:
`2267b92` (nrpic-run), `f8199f6` (nrpic-stage), `f9ab6c7` (nrpic-fetch-arxiv), `d33452b`
(pre-commit hook, doctor, machine file), `5c163b1` (nrpic-run --package), `8124fc5`
(harness/RULES.md). Usage: `harness/RULES.md`. Owners get it with `nrpic-ctx sync`; only
`nrpic-fetch-arxiv` is called from the main checkout and was live at once.

## What changed, against the owners' requests after wave 1

| Request (outbox) | Answer |
|---|---|
| A harness-manifests-and-ignore 2; C nrpic-run-manifest-schema; E harness-and-brief-notes 1 (KeyError 'outputs'/'dir', TypeError on lists) | fixed: one reader of both kinds of manifests (`H.manifest_view`); unreadable ones are reported and skipped; `nrpic-run lint [--all]` lists what was read with defaults; budget, status, submit read all manifests of the eight owners (879 at 15:55Z) without an error |
| E harness-and-brief-notes 2 (two run-id forms) | decision 0012 as written by nrpic-run: `<short owner>-<YYYYMMDD-HHMMSS UTC>-<commit7>`; the full form of wave 1 stays valid and is read (RULES.md) |
| E harness-and-brief-notes 3; decision 0012 (no REPORT.md) | nrpic-stage: package = STAGE_REPORT.md, EVIDENCE.md, OPEN.md, CHECKLIST.md (+ REVIEW.md, scoping text); REPORT.md never asked for |
| A harness-manifests-and-ignore (venv first) | a local `python ...` run without `.venv` is refused with `nrpic-env create --no-kokkos` |
| B harness-runs-and-venv 1-2, kb gitignore-runs, core anchor-runs-ignore-rule | already on main before this session (`/runs/`, `.venv/` in .gitignore); RULES.md's "known issue" retired |
| B harness-runs-and-venv 3 (stage verify without venv) | answered by the venv: `nrpic-env create --no-kokkos` once per worktree |
| kb metadata-path; decision 0015 | `nrpic-fetch-arxiv --meta [--service arxiv\|inspire\|both]`, `--inspire-query`; records in `kb-data/meta/arxiv-api/` and `kb-data/meta/inspire/` (not `meta/arxiv/<id>.api.xml` as asked: kb's inventory takes every file of meta/arxiv/ for an id) |
| kb fetch-arxiv-pdf-and-hardening 1-2; decision 0015 | `--pdf`; size limits; content check; flushed output; version also from the API record; `--check` |
| (found in wave 2) helpers sharing a worktree register card runs by hand because one helper's untracked files make submit refuse (A's runs A-emd-pbh-20261115-153843-7172b66, -153845-7172b66: "harness_refusal") | `nrpic-run submit --package DIR`: the package, the inputs and the shared code must be clean; other changes in tracks/<ID>/ are recorded in `manifest.git.outside_package` |

Also: allotments are read from 0006 as amended by 0014 (C 45, F 50; the sentence "To the
next gate: ..."), and a request above eight card-hours is noted; one submit lock per owner;
`nrpic-env create` in the main checkout (venv only, Kokkos untouched; the main checkout's
`.venv` exists now); `nrpic-env check` skips wt/ and the data roots; the machine file's
default executables are the core-v0.3 builds; `harness/hooks/pre-commit` (brief 13.1)
written and tested, not installed.

## Live checks (read-only unless stated)

- `nrpic-run -C wt/<ID> budget` for all eight owners: no error; card-hours read from the
  hand-written manifests match decision 0014: core 3.36 (no gate recorded), B 0.48 (no gate),
  D 2.18 (G1).
- `nrpic-run lint --all` (manifests on the owners' branches, 15:55Z; core and A are still adding):

| Owner | Runs | By nrpic-run | Hand-written | Run-id forms |
|---|---|---|---|---|
| core | 469 | 0 | 469 | short |
| kb | 59 | 0 | 59 | short |
| A-emd-pbh | 75 | 13 | 62 | 13 short, 62 full |
| B-emd-gw | 78 | 8 | 70 | full |
| C-sidm | 25 | 10 | 15 | full |
| D-bh-dress | 56 | 0 | 56 | full |
| E-stoch-inf | 39 | 9 | 30 | 9 short, 30 full |
| F-hills | 78 | 0 | 78 | full |

  Status words read with defaults: core done 72, finished 11, cancelled 6, none 302; kb
  finished 59; B done 48; C done 5; D none 14; A "failed (exit 1)" 2. None unreadable. The
  wave-2 manifests of core and A are still written by hand (see Open).
- `nrpic-stage -C wt/kb collect kb KB-G1 --stdout`: the four KB-G1 criteria of brief 12.10
  (inventory report, priority-3 papers ingested, code and parameter index of AthenaK, answers
  to the first questions) and the snapshot rule; the same four as kb's own
  `stage/KB-G1/EVIDENCE.md`. Nothing written.
- nrpic-run's Slurm parsing against the real queue: `squeue -h -j <id> -o %T` RUNNING/PENDING,
  `sacct -n -X -P -o ElapsedRaw` 1291 s for job 4432, none for an unknown job.
- Real network, four requests in all, through the live command into the live store: arXiv API
  (2201.03458, gr-qc/9412071: one request), INSPIRE (the same two: one request, 108 and 5
  references), PDFs of the two entries without TeX (gr-qc/9412071 v2, astro-ph/9407016 v1, now
  `source.pdf` beside their e-prints; pdftotext reads the title).

## nrpic-doctor --all after the fixes (15:52Z)

```
owner        wt      build   venv    env     scratch guard   main    kb      gpu     ctx     git     stop
orch         PASS    PASS    PASS    PASS    SKIP    SKIP    SKIP    MISSING PASS    PASS    MISSING PASS
core         PASS    PASS    PASS    PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
kb           PASS    PASS    MISSING PASS    PASS    PASS    PASS    PASS    PASS    PASS    MISSING PASS
A-emd-pbh    PASS    PASS    PASS    PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
B-emd-gw     PASS    PASS    MISSING PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
C-sidm       PASS    PASS    MISSING PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
D-bh-dress   PASS    PASS    MISSING PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
E-stoch-inf  PASS    PASS    PASS    PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
F-hills      PASS    PASS    MISSING PASS    PASS    PASS    PASS    MISSING PASS    PASS    MISSING PASS
```

Against the bootstrap of wave 1: env, scratch, guard, main and stop, MISSING then for want of
the hooks and the machine file, now PASS everywhere. Still MISSING, none for a defect of the
harness: venv of kb, B, C, D, F (each owner runs `harness/bin/nrpic-env create --no-kokkos`
once); kb in every worktree but kb's (main has not merged kb/main; the row already checks that
`kb-data/db/current` refuses a write); git (the pre-commit hook is not installed; decision 0008).

## Self-tests (scratch repositories under scratch/harness/, never the live branches)

| Test | Checks |
|---|---|
| test_nrpic_run.py | 55/55 (new: venv refusal, hand-written manifests of every wave-1 shape, lint, finish/stop refusal, verify of a hand-written run, 0014 amendment, 8 card-hour note, --package) |
| test_nrpic_stage.py | 37/37 (new: hand-written manifest in the package, package documents, kept sections and decision, kb collect KB-G1 --stdout and KB-G2, unknown kb gate) |
| test_fetch_arxiv.py | 29/29 against a loopback server; no request leaves the machine |
| test_precommit.py | 13/13 |
| test_nrpic_env.py, test_style.py, test_hooks.py, test_claude_config.py | 15/15, 10/10, 99/99, 51/51 (unchanged) |

## Open

- No card run had gone through `nrpic-run` batch or chain by 15:55Z: the cards were held by
  core's verification jobs, with A's hand-registered batch jobs queued behind. Job-id parsing
  and wall time were checked against the real squeue and sacct, not yet on a finished card run
  of the command; the first ones should be read with `nrpic-run status <run_id>` after
  `finish`.
- `nrpic-ctx audit` does not yet report non-standard status words (E's proposal); `nrpic-run
  lint --all` does.
- Installing the pre-commit hook (`git config core.hooksPath <main>/harness/hooks`) and the
  Claude Code configuration: decision 0008, the user's.
