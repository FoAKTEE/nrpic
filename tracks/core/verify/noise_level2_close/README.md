# verify/noise_level2_close: open steps of the level-2 review closed

Package of batch R3 (2026-11-24), owner core, branch `core/noise-level2` (worktree
`wt/core-s2`). No source change. The review itself is in
`tracks/core/interfaces/noise_level2.md` (section 12) and
`tracks/core/JOURNAL-noise-level2.md` (entries 6 to 15); this session added entries 16
(predictions) and 17 (outcomes). `JOURNAL.md` here is the short record of the package.

## What was done (run ids are directories of `scratch/core/`)

| Step | Result | Run |
|---|---|---|
| (1) R1f closed and judged: final source 64f150ec against 6ca93cba, fifteen processor tests | 366 of 366 files identical | core-20261124-143147-2ff64b9 (runs), core-20261124-211517-b90ce89 (comparison) |
| R6 threaded build, old against new, level 2, 64^3, three threads | 22 of 22 files identical | core-20261124-211548-60896c5 |
| Figures of the review looked at; `fig_pi_range.png` redrawn | numbers unchanged; one correction to entry 10 (R4 rms of n.d R 6.6e-12 at most) | core-20261124-142629-8516adb, core-20261124-211620-c6e5735 |
| (2) Reviewed executables published | `scratch/core/exe/core_noise-level2/` = 64f150ec; old set in `scratch/core/exe/core_noise-level2_6ca93cba/` | sha256sum -c passes in both |
| (3) Card job R5 | queued, not run: shared queue q0035, priority 2, at most 0.33 card-hours | reading command: journal entry 17 |
| (4) Interface text, journal, outbox | section 12 verdict: v0.7 fit once R5 passes; messages to E-stoch-inf and orch | `tracks/core/outbox/20261124T2120*` |

## How to rerun

From `wt/core-s2`:
- R1f comparison: `python3 tracks/core/analysis/noise_level2/bytecmp.py --a
  scratch/core/core-20261124-130250-0a4a7cb --b scratch/core/core-20261124-143147-2ff64b9
  --out <dir>` (paths under /data/haiyangw/nrpic/).
- R6: `python3 tracks/core/analysis/noise_level2/omp_identity.py --old
  /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2_6ca93cba/athena_cpu_omp --new
  /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_cpu_omp --out <dir>`
  (six cores).
- R5 once q0035 has run: journal entry 17 has the two commands.
Register every rerun with `harness/bin/nrpic-run submit`.

## Not done

- R5 has not run (queue). Until it passes, the reviewed card executable is untested on a
  card and the release condition of section 12 is open.
- The inflection case with `noise_background_eq = evolved`; level 2 with a shift or a
  lapse that varies in space (both untested, as before).
- Two cosmetic legend overlaps (fig_t1t3 (b), fig_readings (c)) left as they are.

## Requests

- E-stoch-inf: confirm that every run of yours that used the executables of 6ca93cba is in
  the list of `scratch/core/exe/core_noise-level2_6ca93cba/READY` (nine manifests found;
  the task spoke of fifteen runs); point any deck or wrapper that has not yet started
  and must keep 6ca93cba at that directory.
- orch: keep q0035 at priority 2 (release v0.7 waits for it); at the merge carry the six
  `<scalar_field>` options of `tracks/core/interfaces/noise_level2.md` into the changelog
  and `coord/INTERFACES/`.
