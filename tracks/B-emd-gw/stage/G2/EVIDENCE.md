# Evidence: B-emd-gw G2 (state of batch 10a, 2026-11-22)

Runs this package rests on so far (manifests under `tracks/B-emd-gw/runs/<run id>/`; outputs
under `scratch/B-emd-gw/<run id>/`). Judgements in the package journals named per row.

## G2 criterion (a), FLRW particle run (`flrw_conv/`, JOURNAL entries 1-13)

| Run id | What | Kind |
|---|---|---|
| B-20261120-222902-6b0be3c | initial data, leg F (homogeneous dust, lattices and noise) | processors |
| B-20261120-222908-8aede2c | initial data, leg B 64/128 cells | processors |
| B-20261120-222955-c8e16e3 | J1: legs F and B at 32 cells, 1, 8, 27 per cell (card) | card |
| B-20261120-223006-24448ac | P1: legs F and B at 16 cells (processors) | processors |
| B-20261121-202304-dc3020e | J2: legs F and B at 64 cells (card) | card |
| B-20261121-202335-3e6a898 | J3: leg B at 128 cells to a = 1000 (card chain, 2.00 card-h) | card |
| B-20261121-212128-67b349a | P2: Poisson-like start | processors |
| B-20261121-220450-e011c57 | P3: step test 0.002, 0.001 at 32 cells | processors |
| B-20261121-222813-560158b | P4: step test 0.0005 at 32 cells | processors |
| B-20261121-220428-7367d5e | analysis, leg F | analysis |
| B-20261121-225745-773ffab | analysis, step test | analysis |
| B-20261123-015452-18d2956 | analysis, leg B with the 128-cell member (final) | analysis |

## Multi-code row (decision 0013): shearing dust (`shear/`, JOURNAL)

| Run id | What | Kind |
|---|---|---|
| B-20261120-223409-29c92ec | references and symbolic checks P1-P3 | analysis |
| B-20261121-202359-d12511c | smoke run S1, N_y = 32 | processors |
| B-20261121-202830-417af0c | series 1: 27 cases (closed as failed: S1_n64_lap1 guard stop) | processors |
| B-20261123-015919-dec4392 | summary of series 1, outcomes P4-P12 | analysis |

## Full GR against the Newtonian mode: population box (`population/`, JOURNAL)

| Run id | What | Kind |
|---|---|---|
| B-20261121-202946-ec4a156 | relativistic data sigma1 = 0.028 (outer change 3.25e-7, above the 1e-7 condition; not used) | processors |
| B-20261121-211707-d795743 | relativistic data sigma1 = 0.014 (converged) | processors |
| B-20261123-014847-f295ab4 | GR run sigma1 = 0.014 (chain, queued, Slurm 4921) | card |
| B-20261123-014850-7b7d986 | re-solve of the 0.028 data with 36 outer iterations (running) | processors |

Queued behind them in `cards/queue.json`: J4 = B-20261123-015905-7a30278 (128-cell step test,
Slurm 4922), then `pop_s028_gr`.

## Figures looked at in batch 10a

`flrw_conv/figs/fig_b_conv.png`, `fig_b_error.png`, `fig_b_constraints.png` (from
B-20261123-015452-18d2956); `shear/figs/fig_series.png` (from B-20261123-015919-dec4392).
