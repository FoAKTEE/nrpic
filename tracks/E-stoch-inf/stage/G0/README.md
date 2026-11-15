# stage/G0: independent verification of Track E's G0 and G1 material (wave 2 helper)

Owner E-stoch-inf; written by the G0 verifier helper. Verdicts: `VERIFIER.md`. Predictions
and outcomes: `JOURNAL.md`. This helper writes only `JOURNAL.md`, `README.md`,
`VERIFIER.md`, `scripts/`, `fig/`, `results/` here and its own run manifests under
`../../runs/`; the other files of this directory (CHECKLIST, EVIDENCE, OPEN) are the lead's.

## Contents

| Path | What |
|---|---|
| `scripts/common.py` | background of both cases in cosmic time (own integrator) |
| `scripts/v1_background.py` | V1 derived background numbers |
| `scripts/v2_freezing.py` | V2 full vs deformed Mukhanov-Sasaki modes, freezing, A3 numbers |
| `scripts/v3_initial_data.py` | V3 linearised constraints of the initial data (sympy) |
| `scripts/v4_draw_norm.py` | V4 normalisation of the random draw |
| `scripts/v5_kicks.py` | V5 core's sources, window derivatives, kicks vs constraints (sympy) |
| `scripts/v6_athenak.sh`, `v6_modefile.py`, `v6_compare.py` | V6 reproducibility of core's MS model with kicks (layouts, restart, negative control), V7 processor timing |
| `scripts/v2b_usr_nonlinear.py` | V2b delta-N f_NL, N(kick), drift vs diffusion, mode-coupling proxy for A3-USR |
| `scripts/v7_cost_arithmetic.py` | V7 card-hours per realisation (track's inputs; calibrated with core's card run) |
| `scripts/v8_deltaN_reference.py` | V8 lattice-sum factor and sigma = 1 excess |
| `scripts/rerun_track.sh`, `cmp_tree.py` | rerun of the track's spec/ref tests T1-T4, comparison with the original outputs |
| `scripts/run_python_checks.sh` | runs V1-V5, V8 |
| `fig/`, `results/` | figures and JSON copied from the registered runs |

## Rerun

From the worktree root (`.venv` from `harness/bin/nrpic-env create --no-kokkos`):

    bash tracks/E-stoch-inf/stage/G0/scripts/run_python_checks.sh <outdir>      # V1-V5, V8, ~5 min
    bash tracks/E-stoch-inf/stage/G0/scripts/rerun_track.sh <outdir>            # track's T1-T4, ~4 min
    bash tracks/E-stoch-inf/stage/G0/scripts/v6_athenak.sh \
         /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena <outdir>             # V6, V7, ~10 min, 6 cores

V2b and V7 are single commands; their exact command lines are in the run manifests
(`../../runs/E-20261115-180056-d62ee5a/`, `-180348-d799c68/`, `-180445-e72dad6/`).
Run ids: `VERIFIER.md`, section "Runs".

## Requests

To the owner (lead):

1. Link or rename `VERIFIER.md` for the stage check: CHECKLIST C18 and `nrpic-stage` look for
   `VERIFIER_REPORT.md` (the package brief asked for `VERIFIER.md`).
2. State in SCOPE 8 / 9 that the margin to the downgrade threshold holds at theta = 0.25 only:
   calibrated with core-20261115-143907-cea4c86, theta = 0.025 costs 6.0-15.1 card-hours per
   256^3 realisation (run E-20261115-180445-e72dad6), i.e. L6 (A6) decides the downgrade
   question and should run first; add the 4-5 percent longer cosmic time N* to N_f to the
   step counts.
3. Add a risk for the end of the USR run at the drift/diffusion border (ratio 0.98 at N*+8.3)
   and the stationary inflection point near the delta-N end surface (VERIFIER.md weak point 3).

To core:

4. The first card run of the MS model should time one 256^3 step with the sources for two
   MeshBlock sizes (64^3, 128^3): the synthesis cost per step grows 5.4 times from 128^3 to
   32^3 MeshBlocks (operation count of `scalar_field_noise.cpp:596-652`).
5. A run of the MS model with physical mode functions through to R^NR (A2) is the missing
   test; V6 shows reproducibility and the first-order constraint preservation of the kicks on
   the release, not the amplitude.

To orch (harness):

6. `nrpic-run submit --launcher local -- bash script.sh '$NRPIC_RUN_DIR'` passes the
   variable unexpanded and the script then writes a directory literally named
   `$NRPIC_RUN_DIR` into the worktree root (run E-20261115-174515-4d30c15; removed by hand).
   Either expand it in the wrapper or refuse an argument that contains it literally; the
   `bash -c '... "$NRPIC_RUN_DIR"'` form works.
