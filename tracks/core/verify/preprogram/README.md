# Pre-program run directories of ladder rows 2 to 4

Named here as **pre-program** (decision 0016 item 3 covers hand-written manifests of
waves 1 and 2; these directories are older still): they were made on 2026-11-13, before
the program's run registry and before release core-v0.1, by the campaign recorded in
`docs/TESTLOG.md` and `paper/`. They have no manifest under `tracks/core/runs/` and none
is written after the fact, because the command line, the source commit of the build and
the time of the run cannot be recovered beyond what the directories hold. What they hold
was inventoried by the registered run **core-20261121-231825-135474c** (`inventory.py`,
one core, batch 8): sha256 of every input, executable copy, log, history, horizon
summary, particle file and table, and the count and size of the bulk outputs
(`INVENTORY.md`, a copy of the run's output; `inventory.json` and `fig_inventory.png` in
`scratch/core/core-20261121-231825-135474c/`, looked at).

| Directory (`/data/haiyangw/nrpic/runs/`) | Ladder row | Numbers it carries (`verify/LADDER.md`) |
|---|---|---|
| `os/nocap_sc` | 2 | Oppenheimer-Snyder reference to 60 M: first horizon 16.39 M, M_AH/M, largest deviation 1.34e-3, removal by 19.74 M |
| `os/nocap_v4` | 2 | the same with the published lattice mass rule (1.18 per cent more mass) |
| `prolate/e09_v8` | 3 | prolate collapse at M/16 (horizon at 32.00 M, M_AH) |
| `st/yc0900_v4`, `st/yc0819_v4` | 4 | stable models: central-lapse ranges, particles kept |
| `st/yc0605_v5`, `st/yc0500_v5` | 4 | collapsing models: first horizon 191.0 M and 104.3 M, M_AH/M |
| `st/yc0283_v5` | 4 | expanding model: central lapse at 270 M |
| `st/migration_yc0500_v4`, `st/yc0756_unpert` | 4 | migration target; near-critical model to 800 M |

What the inventory establishes [VERIFIED, run core-20261121-231825-135474c]: every
directory holds its input file, the copy of the executable that ran (two builds: sha256
`eea699995025c974...` for `os/nocap_*`, `st/yc0900_v4`, `st/yc0819_v4` and the
migration chain; `bbb74535e4f77886...` for `prolate/e09_v8`, `st/yc0605_v5`,
`st/yc0500_v5`, `st/yc0283_v5` and the near-critical chain), its logs and both history
files; the horizon summary exists wherever a finder ran (absent for the two stable
models, the migration run and the near-critical run, whose ladder numbers come from the
history files). The fresh verifier recomputed the numbers of rows 2 and 4 from these
files (`stage/G2/VERIFIER.md` V2, V3).

What it does not establish: the source commit of the two builds and the exact command
lines; whether the files are unchanged since the runs (the inventory fixes their state
of 2026-11-21, so a later change is detectable, an earlier one is not). The ladder rows
on the merged and released executables rest on the registered regressions
(core-20261115-065452-3629622, -065901-3629622) and, for row 4 on M/8, on the six
registered chains of batch 5.
