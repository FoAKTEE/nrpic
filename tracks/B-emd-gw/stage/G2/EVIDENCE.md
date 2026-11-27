# Evidence: B-emd-gw G2 (state of batch 11, 2026-11-24)

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
| B-20261123-015905-7a30278 | J4: step test of leg B at 128 cells (limits 0.002, 0.001, 0.01) | card |
| B-20261124-125457-79ce723 | analysis of J4 (`analyze_step.py --set n128`): J4a-c hold | analysis |

## Multi-code row (decision 0013): shearing dust (`shear/`, JOURNAL)

| Run id | What | Kind |
|---|---|---|
| B-20261120-223409-29c92ec | references and symbolic checks P1-P3 | analysis |
| B-20261121-202359-d12511c | smoke run S1, N_y = 32 | processors |
| B-20261121-202830-417af0c | series 1: 27 cases (closed as failed: S1_n64_lap1 guard stop) | processors |
| B-20261123-015919-dec4392 | summary of series 1, outcomes P4-P12 | analysis |
| B-20261124-131336-bc61eee | P10: rays of the f = 1 run of series 1 (copied), against f = 1/3: -8.7e-5 | analysis |
| B-20261124-133702-4a06a52 | series 2: L2 with tlim = 10 at N_y = 32, 64, 128 (fan too coarse: no reliable number); S3 at N_y = 256 | processors |
| B-20261124-134209-4584052 | series 3: L2 with narrow fans at N_y = 32, 64, 128 | processors |
| B-20261124-134720-c753aff | summary of series 2 and 3 (`series2_summary.py`), figure fig_series2 | analysis |

## Full GR against the Newtonian mode: population box (`population/`, JOURNAL)

| Run id | What | Kind |
|---|---|---|
| B-20261121-202946-ec4a156 | relativistic data sigma1 = 0.028 (outer change 3.25e-7, above the 1e-7 condition; not used) | processors |
| B-20261121-211707-d795743 | relativistic data sigma1 = 0.014 (converged) | processors |
| B-20261123-014847-f295ab4 | GR run sigma1 = 0.014 to a = 143 (Slurm 4921, 0.19 card-h) | card |
| B-20261123-014850-7b7d986 | re-solve of the 0.028 data with 36 outer iterations (9.1e-10 at outer 33) | processors |
| B-20261123-035002-bcc82bd | GR run sigma1 = 0.028: guard stop at a = 30.7 in the densest core (closed as failed) | card |
| B-20261124-130512-d39dae4 | analysis of both GR runs, failed on the guard-stop dump | analysis |
| B-20261124-131918-e71996f | analysis of both GR runs (JSON complete; figure step failed) | analysis |
| B-20261124-133150-e9ef701 | figures and summary of that analysis: A1-A3, H1-H2, Z | analysis |
| B-20261124-133709-85c4be7 | slice mosaic with zoom boxes of the GR box at a = 132 (C13) | analysis |
| B-20261124-131438-5d7e049 | Newtonian reference at 128^3 with the GR runs' own particles, sigma1 = 0.014, 0.028 (Slurm 5167, queued) | card |
| B-20261124-133533-cb0bb7d | four restarts of the 0.028 run from t = 8 (X0-X3; Slurm 5169, queued) | card |


## Batches 23 and 28: legs of the population box (`population/JOURNAL.md` 2026-11-25 18:22-18:51, 2026-11-26 13:22-13:27)

| Run | What it establishes | Kind |
|---|---|---|
| B-20261125-093500-242d3a3 | 256^3 zero shift (q0007): guard stop at a = 102 after K_max > 0 from a = 80 (M1 refuted), closed failed | card |
| B-20261125-221742-5100a22 | particle leg continued to a = 143 (q0042; P8C1, P8C2 hold) | card |
| B-20261126-011415-449c8ce | 0.028 box with the Gamma driver from t = 8 to a = 143 (q0044; S1 holds) | card |
| B-20261126-105021-6343c13 | 256^3 Gamma driver (q0060) to a = 143, no guard stop (GM1 holds) | card |
| B-20261126-022356-52c2460 | equal-mass analysis of the 256^3 zero-shift leg to a = 100 | analysis |
| B-20261126-022403-82f6e69 | equal-mass analysis of the shifted 0.028 box | analysis |
| B-20261126-022407-87e8803 | equal-mass halo catalogues of base and gauge leg | analysis |
| B-20261126-022838-27fab1b | equal-mass analysis of the joined 8-per-cell leg | analysis |
| B-20261126-024849-87e72b7 | histories of six legs: M1, M4, P8C2, Q1 (constraints), S1 | analysis |
| B-20261126-024936-1ee0a16 | GR (zero shift) against Newton with equal masses: N2e, GN1e | analysis |
| B-20261126-024941-647553b | GR (Gamma driver) against Newton with equal masses: N2e, GN1e | analysis |
| B-20261126-025137-7686b91 | note figures and ledger of batch 23 | analysis |
| B-20261126-212502-e9e4f4e | histories of seven legs: GM1 holds, GM4 refuted | analysis |
| B-20261126-212541-b647c59 | M2 (counts hold, early masses fail), M3 (mixed), Q1 high-k part refuted | analysis |
| B-20261126-212604-a508e94 | S2, S3 hold at the same stage | analysis |
| B-20261126-212212-c54d979 | equal-mass analysis of the 256^3 Gamma-driver box (GM2, GM3); killed with its session, closed failed; rerun as B-20261126-221911-a0531db | analysis |
| B-20261126-221911-a0531db | equal-mass analysis of the 256^3 Gamma-driver box (rerun, background) | analysis |
| B-20261126-222544-f3a5176 | shear series 7 (C1, 0046 2a): beta = 0.125, N_y = 64, 128, 256, release v0.8 processor build | simulation |
| B-20261126-230056-294b265 | series 7 judged: N7a holds, N7b Delta part holds, constraint part fails, N7c holds | analysis |
| B-20261126-222552-2e44186 | 64^3 relativistic initial data at eight per cell (C3 step 1): same 146 modes and sigma1 as the 128^3 data | initial data |
| B-20261127-232236-7ab7aa2 | GM2 (band strain holds, Omega part fails as written), GM3 (fails in part) | analysis |
| B-20261127-232258-37c6773 | q0070: 64^3 member at eight per cell to a = 143, 0.038 card-h | simulation (card) |
| B-20261127-232604-21d85fb | C3 judged (first drawing: cut labels) | analysis |
| B-20261127-232628-1361e3b | C3 judged, figure redrawn: C3b holds, C3a fails before a = 31, not refuted | analysis |
| B-20261127-232833-5891f77 | note v4: figures, schematics, ledger with Table VIII | analysis |

Figures looked at in batch 34: `pop_legs.png` (B-20261127-232236-7ab7aa2), `c3_mesh_pair.png`
(B-20261127-232604-21d85fb and -232628-1361e3b), `series7.png` (B-20261126-230056-294b265), note pages
1, 15, 26.

Figures looked at in batch 28: `pop_leg_histories.png` (B-20261126-212502-e9e4f4e), `pop_legs.png`
(B-20261126-212541-b647c59), `pop_s028gd.png` (B-20261126-212604-a508e94; overlapping tick labels).

## Figures looked at in batch 11

`flrw_conv/figs/fig_step128.png`; `population/figs/pop_gr_constraints.png`, `pop_gr_halos.png`,
`pop_gr_gw.png`, `pop_gr_stop.png`, `pop_gr_mosaic.png`; the rays figure of B-20261124-131336-bc61eee; `shear/figs/fig_series2.png`.

## Figures looked at in batch 10a

`flrw_conv/figs/fig_b_conv.png`, `fig_b_error.png`, `fig_b_constraints.png` (from
B-20261123-015452-18d2956); `shear/figs/fig_series.png` (from B-20261123-015919-dec4392).
