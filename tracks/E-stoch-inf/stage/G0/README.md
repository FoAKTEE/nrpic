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

Run ids: `VERIFIER.md`, section "Runs".

## Requests

Filled in at the end (see `VERIFIER.md`).
