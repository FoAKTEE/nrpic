# stage/G0: verifier package (wave 2)

This directory holds the G0 stage package of Track C (CHECKLIST, EVIDENCE, OPEN, REPORT,
REVIEW: written by the lead in wave 1) and, from wave 2, the independent verifier's work:

| Path | What |
|---|---|
| `VERIFIER.md` | verdicts on eight claims of the plan (CONFIRMED / NOT CONFIRMED / WRONG), the three weakest points, comparison with the lead's review |
| `JOURNAL.md` | the verifier's predictions (written before any check ran) and outcomes |
| `verifier/v_mono.py` | V1: monoenergetic (Shapiro-Teukolsky) sequence from scratch, Newtonian limit |
| `verifier/kingsolve.py` | truncated Maxwell-Boltzmann (F21) / King steady states by direct momentum integration of f(E); profiles; local mean Moller speed |
| `verifier/v_king.py` | V2, V3, V5: F21 Table 1 rows and criteria, King b = 1 threshold, three Knudsen conventions, physical Kn |
| `verifier/v_pulsation.py` | V4: Rayleigh-Ritz (global basis) for F21's pulsation operator; Gamma = 2 polytrope limit |
| `verifier/v_rate.py` | V6: Monte Carlo of the mean Moller speed with an own Maxwell-Juttner sampler |
| `verifier/v_costs.py` | V7: unit costs from the first paper's AthenaK logs; particle number and sub-steps against Kn |
| `verifier/run_all.sh` | runs V1-V7 into `$NRPIC_RUN_DIR/{mono,king,puls,rate,costs}` |
| `verifier/rerun_track.sh` | reruns the track's own scripts and tests (scope scripts, test_tmb, collide pytest, equilibria knudsen) |
| `verifier/figs/` | PNG copies of the figures of run C-20261115-170630-1037f6a |

## How to rerun

From the worktree root (needs `.venv`: `harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/C-sidm/stage/G0 \
        --cores 1 --purpose "..." -- bash tracks/C-sidm/stage/G0/verifier/run_all.sh
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/C-sidm/stage/G0 \
        --cores 2 --purpose "..." -- bash tracks/C-sidm/stage/G0/verifier/rerun_track.sh

`run_all.sh` takes about 1 minute on one core; `rerun_track.sh` about 25 minutes (most of it
the equilibria `knudsen.py`). A single script: `python3 tracks/C-sidm/stage/G0/verifier/v_king.py <outdir>`
(v_costs.py also takes the v_king.json and v_mono.json paths). The cost check reads the
logs under `/data/haiyangw/nrpic/runs/st/` (main checkout, untracked).

Runs: C-20261115-170630-1037f6a (verifier suite), C-20261115-170716-e81ba08 (reruns).

## Requests

- **C-sidm lead**: (1) correct SCOPE.md section 1 (fluid window 0.540 < Z(0) < 0.635 for
  F21's gamma = 1 + p/u, not 0.75; the trial criterion is sufficient for instability only),
  section 3.4 (2105.05556:581 concerns small i; core-halo onsets, i = 100-250, are unrelated
  to the extrema, paper.tex:599) and section 4 (point to REPORT decision 2); (2) write the
  Knudsen definition of REPORT decision 2 into `collide/SPEC.md` and add K = 1/(rho0_c H_c)
  (H on rho0) to `equilibria/CONVERSION.md`, including the F21 b = 0.1 models (K = 142.6 at
  the eps maximum, 84.1 at the trial root, run C-20261115-170630-1037f6a); (3) state in
  `gravothermal/README.md` that the omega^2 values are in surface-observer time
  (tmb.py:389), or pass the full lapse; (4) note that the monoenergetic family has no
  stability theorem (f not decreasing in E).
- **orch**: none. `nrpic-run submit --package` worked for both runs. Minor: a shell driver
  as the command records only itself as an input; the Python files it calls are pinned by
  the commit only (pass `--input` for each if checksums are wanted).
- **core**: none from this package.
