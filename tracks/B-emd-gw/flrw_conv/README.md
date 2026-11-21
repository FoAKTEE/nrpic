# flrw_conv: G2 criterion (a) of Track B

Scale-factor error and linear growth rate of the particle FLRW run, converging in
particle number and mesh, in the production configuration (helper package of B-emd-gw,
wave 3). Criterion: `coord/CHARTER.md` section 9.5, first half ("the scale-factor error and
the linear growth rate of the particle FLRW run reach the sub-percent level and converge in
particle number and mesh"). Design, predictions (entries 1, 4, 7, 8) and outcomes:
`JOURNAL.md`.

State (2026-11-21, batch 6): legs F and B run and judged at 16, 32 and 64 cells and 1, 8,
27 particles per cell. The 128^3 row of leg B (J3, chain, Slurm 4825) is still running;
see "Pending".

## Verdict on criterion (a)

**Met at 16-64 cells, with one stated floor** [VERIFIED by the runs named below]:

- Scale factor (leg F, homogeneous dust from a = 1 to 1000): largest relative error of any
  measure (lapse and chi extrema, proper volume, mean K) 3.8e-7 for lattices at rest and
  5.3e-5 with position noise. Lattices converge at fourth order in the step (32 -> 64 cells:
  factor 15.1); 8 and 27 per cell equal 1 per cell to 2.3e-12. The noise-induced part falls
  as N_c^-1/2 (extrema) and N_c^-1 (box averages) with the particles per cell, and as h
  (extrema) with the mesh, as predicted.
- Growth rate (leg B, test B of arXiv:1904.07841, 1e-7 plane wave, a = 1 to 1000):
  |f - f_ref| at most 8.4e-5 (16 cells), 6.5e-6 (32), 4.9e-6 (64) for the density in the
  code's slicing (f_ref = a/(a + 3/k^2), the relativistic dictionary at the box scale) and
  for the gauge-invariant contrast delta_* (f = 1). The plateau (a >= 3) converges at fourth
  order: 6.7e-5, 4.9e-6, 3.0e-7. With particle number at 32 cells it falls from 4.9e-6
  (1 per cell) to 1.2e-6 and 1.5e-6 (8, 27 per cell), the mesh part at 32 cells.
- Floor: for a <= 2 the f error is about 5e-6 at 32 and 64 cells (and in a development
  look at the partial 128^3 run): a decaying mode of relative amplitude eps = 1.3e-6 to
  4.5e-6 that does not converge with the mesh. Its cause is open; the step test P3 (entry 8)
  addresses one candidate (section "Step test").
- The potential estimator (a phi from chi) is the weakest: |f_phi - 1| up to 3.1e-3 (16),
  3.0e-4 (32), 1.7e-4 (64), set by an oscillation of period 2.34 in conformal time
  (speed L/P = 0.577 = 1/sqrt(3), that of the slicing [JUDGEMENT: a gauge wave]) whose
  amplitude falls with mesh and particle number. Still sub-percent everywhere.

## Results

Leg F (analysis run B-20261121-211951-b735833; columns: largest relative error over the run)

| case | data run | a end | alpha extrema | chi extrema | volume | mean K | alpha noise part a=3 / a=300 | Hr_max end |
|---|---|---|---|---|---|---|---|---|
| f_n16_p1_a0 | B-20261120-223006-24448ac | 999 | 3.81e-07 | 2.77e-07 | 2.77e-07 | 1.95e-07 | - | 1.8e-07 |
| f_n32_p1_a0 | B-20261120-222955-c8e16e3 | 999 | 1.86e-07 | 1.35e-07 | 1.35e-07 | 9.61e-08 | - | 8.4e-08 |
| f_n32_p2_a0 | B-20261120-222955-c8e16e3 | 999 | 1.86e-07 | 1.35e-07 | 1.35e-07 | 9.61e-08 | - | 8.4e-08 |
| f_n32_p3_a0 | B-20261120-222955-c8e16e3 | 999 | 1.86e-07 | 1.35e-07 | 1.35e-07 | 9.61e-08 | - | 8.5e-08 |
| f_n64_p1_a0 | B-20261121-202304-dc3020e | 1000 | 1.23e-08 | 8.94e-09 | 8.94e-09 | 6.30e-09 | - | 1.6e-08 |
| f_n16_p1_a2 | B-20261120-223006-24448ac | 999 | 5.30e-05 | 4.74e-05 | 1.07e-06 | 9.50e-07 | 4.12e-05 / 2.23e-05 | 2.2e-01 |
| f_n32_p1_a1 | B-20261120-222955-c8e16e3 | 999 | 3.18e-06 | 2.51e-06 | 1.18e-07 | 8.28e-08 | 2.24e-06 / 1.59e-06 | 2.7e-02 |
| f_n32_p1_a2 | B-20261120-222955-c8e16e3 | 999 | 3.19e-05 | 2.94e-05 | 1.52e-06 | 1.22e-06 | 2.24e-05 / 1.82e-05 | 6.6e-01 |
| f_n32_p2_a2 | B-20261120-222955-c8e16e3 | 999 | 1.04e-05 | 8.48e-06 | 2.65e-08 | 3.35e-08 | 7.18e-06 / 4.94e-06 | 1.7e-01 |
| f_n32_p3_a2 | B-20261120-222955-c8e16e3 | 999 | 6.17e-06 | 4.45e-06 | 8.70e-08 | 5.78e-08 | 3.57e-06 / 2.78e-06 | 7.7e-02 |
| f_n64_p1_a2 | B-20261121-202304-dc3020e | 1000 | 1.70e-05 | 1.43e-05 | 1.91e-06 | 1.44e-06 | 1.06e-05 / 1.07e-05 | 1.3e+00 |

Case names: f_n<cells>_p<particles per cell per direction>_a<noise: 0 none, 1 A1 = 4.2e-5,
2 A2 = 4.2e-4 = 0.01 h(32), uniform per component, seed 1>. With noise the relative
Hamiltonian constraint grows to order one at a = 1000: the noise contrast turns nonlinear at
the cell scale and the compensated cubic cloud then deposits negative cell densities (first
at a = 60 for 64 cells, 140 for 32 cells at A2; entry 7). The scale factor is not affected.

Leg B (analysis run B-20261121-211956-b30627b; f errors against f_ref = a/(a + 3/k^2) for
delta and 1 for delta_* and the potential; plateau = median over 3 <= a <= 950)

| case | data run | largest abs(f_delta - f_ref) | plateau f_delta | plateau f_* | early f_* (a<=2) | f_phi largest | largest amplitude error | eps (log fit) | Hr_max |
|---|---|---|---|---|---|---|---|---|---|
| b_n16_p1 | B-20261120-223006-24448ac | 8.36e-05 | 6.71e-05 | 6.70e-05 | 6.20e-05 | 3.06e-03 | 4.91e-04 | +3.3e-05 | 9.9e-10 |
| b_n32_p1 | B-20261120-222955-c8e16e3 | 6.48e-06 | 4.91e-06 | 4.91e-06 | 3.59e-06 | 2.97e-04 | 3.39e-05 | +4.5e-06 | 3.2e-09 |
| b_n32_p2 | B-20261120-222955-c8e16e3 | 5.33e-06 | 1.20e-06 | 1.20e-06 | 5.09e-06 | 2.10e-04 | 1.06e-05 | +1.4e-06 | 3.4e-09 |
| b_n32_p3 | B-20261120-222955-c8e16e3 | 5.45e-06 | 1.53e-06 | 1.54e-06 | 5.15e-06 | 2.09e-04 | 1.30e-05 | +1.3e-06 | 3.2e-09 |
| b_n64_p1 | B-20261121-202304-dc3020e | 4.86e-06 | 3.03e-07 | 3.02e-07 | 4.78e-06 | 1.69e-04 | 1.37e-06 | +2.5e-06 | 1.3e-08 |

Figures (PNG and PDF in the analysis run directories; copies in `figs/`):
`fig_f_lattice` (lattices), `fig_f_noise` (noise runs, contrast, Hr), `fig_f_scaling` (noise
part against particles per cell and mesh, with the predicted laws), `fig_f_constraints`
(Hr maximum and mean, absolute momentum constraint, Theta); `fig_b_growth` (f(a) and
|f_* - 1|), `fig_b_error` (f and amplitude errors of the three estimators), `fig_b_conv`
(convergence in mesh and particle number), `fig_b_constraints` (Hr, potential amplitude).

Failed predictions (entry 7): PF6 in part (alpha extrema 2.3e-5 above the predicted 1e-5;
the Hamiltonian constraint of the noise runs grows instead of being damped), PB1 for the
potential estimator, PB2 at 16 cells (two-term fit; the three-term fit gives 3.3e-5),
PB3 for the floor (no floor at 1e-6 in the plateau; the early part has a floor of about
5e-6), PB4 for the amplitude (1 per cell differs from 8 and 27 by 4.5e-5).

## Pending

- J3 = run B-20261121-202335-3e6a898, chain of `scripts/submit_chain.sh`, Slurm job 4825
  (segment 1 running since 12:44 PST; at t = 21, a = 132, at 13:30). Leg B at 128^3, 1 per
  cell, to a = 1001; about 23,200 steps at 0.31 s, 2.0 card-hours with two or three
  segments. Prediction (entry 4): plateau error at most a quarter of 64^3's (3.0e-7); the
  early part stays at about 5e-6 (entry 8). When it has ended: `nrpic-run finish` is done by
  the chain or the sequencer; then add `"b_n128_p1": "B-20261121-202335-3e6a898"` to
  `inputs/runs.json` and rerun `scripts/analyze_b.py` registered.

## Card time

J1 (Slurm 4746) 0.31 card-h, J2 (4824) 0.35 card-h by Slurm accounting; J3 0.75 card-h at
13:30 and about 2.0 card-h when complete, so the package reaches about 2.7 card-hours
against the 2.5 of its brief (J3 to a = 1001 was the lead's choice under decision 0025
item 4, entry 4). Processor runs: P1, P2, P3 (6 threads at most).

## How to rerun

1. Initial data: `scripts/build_ic.sh` (runs B-20261120-222902-6b0be3c,
   B-20261120-222908-8aede2c, B-20261120-223448-7f7c034).
2. Simulations: card lists `inputs/batch_j1.list`, `batch_j2.list` (nrpic-run `--launcher
   batch`, executable `.work/build_gpu_v03/src/athena`), J3 deck `inputs/mode_prod_rst.athinput`
   (chain); processor lists `inputs/cpu_p1.list`, `cpu_p2.list`, `cpu_p3.list` with
   `scripts/run_cpu.sh` (threaded executable `scratch/core/exe/core_build-openmp/athena_cpu`).
3. Analysis (registered, one core):
   `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/B-emd-gw/flrw_conv
   --launcher local --cores 1 -- python3 tracks/B-emd-gw/flrw_conv/scripts/analyze_f.py
   tracks/B-emd-gw/flrw_conv/inputs/runs.json` (and `analyze_b.py`; `analyze_step.py` with
   `inputs/runs_step.json`).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | design, cost, predictions, outcomes |
| `inputs/flrw_prod.athinput` | leg F deck: homogeneous dust, production configuration, box 1.35085 |
| `inputs/mode_prod.athinput`, `mode_prod_rst.athinput` | leg B deck (step limit 0.002); the same with restart output for J3 |
| `inputs/runs.json` | case -> run directory of P1, J1, J2 |
| `inputs/runs_j3_partial.json` | the same with the partial 128^3 run (development check only) |
| `inputs/batch_j1.list`, `batch_j2.list`, `batch_j3.list`, `cpu_p1.list`, `cpu_p2.list`, `cpu_p3.list` | run lists |
| `scripts/build_ic.sh`, `scripts/ic_stats.py` | initial data and their deposited contrast |
| `scripts/run_cpu.sh`, `scripts/omp_places.py` | processor runs on core's threaded executable |
| `scripts/flrwlib.py` | readers, references a(t) and D(a), growth-rate estimators, decaying-mode fits, oscillation period |
| `scripts/analyze_f.py`, `analyze_b.py`, `analyze_step.py` | analyses and figures |
| `scripts/figstyle.py` | figure style (copy of `harness/style/figstyle.py`) |
| `figs/` | copies of the figures (PNG) |
| `results/` | copies of the analysis JSON |

## Requests

- To the lead: J3 is the only open row; when its chain has ended, rerun `analyze_b.py` with
  the 128^3 case (above) and record the outcome against entries 4 and 8. The package passes
  its card cap by about 0.2 card-h if J3 completes (section "Card time").
- To core (no action needed for criterion (a)): the relative momentum constraint Mr of
  `.cstat.hst` is rounding over rounding on a homogeneous slice (it reads 1.41, about sqrt 2, for
  lattices at rest while |M| is 1e-11; run B-20261121-211951-b735833); a floor in its denominator, or a note in the format
  description, would avoid misreading it.
