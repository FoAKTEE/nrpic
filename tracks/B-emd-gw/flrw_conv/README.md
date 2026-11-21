# flrw_conv: G2 criterion (a) of Track B

Scale-factor error and linear growth rate of the particle FLRW run, converging in
particle number and mesh, in the production configuration (helper package of B-emd-gw,
wave 3). Criterion: `coord/CHARTER.md` section 9.5, first half ("the scale-factor error and
the linear growth rate of the particle FLRW run reach the sub-percent level and converge in
particle number and mesh"). Design, predictions (entries 1, 4, 7, 8, 10) and outcomes
(entries 7, 9, 10, 11): `JOURNAL.md`.

State (2026-11-21, batch 6): legs F and B run and judged at 16, 32 and 64 cells and 1, 8,
27 particles per cell; the optional Poisson-like start (P2) and a step test of the early
floor (P3, P4) run on processors. The 128^3 row of leg B (J3, chain) is still running and
was looked at provisionally to a = 190; see "Pending".

## Verdict on criterion (a)

**Met at 16-64 cells, with a stated floor in the first e-fold** [VERIFIED by the runs named
below]:

- Scale factor (leg F, homogeneous dust from a = 1 to 1000): largest relative error of any
  measure (lapse and chi extrema, proper volume, mean K) 3.8e-7 for lattices at rest and
  5.3e-5 with position noise of one percent of a cell. Lattices converge at fourth order in
  the step (32 -> 64 cells: factor 15.1); 8 and 27 per cell equal 1 per cell to 2.3e-12.
  The noise-induced part falls as N_c^-1/2 (extrema) and N_c^-1 (box averages) with the
  particles per cell and as h (extrema) with the mesh, as predicted. With Poisson-like
  noise (displacements up to half a cell, P2) the error stays at 4.7e-3 or below to a = 1000.
- Growth rate (leg B, test B of arXiv:1904.07841, Main.tex:413-415: a 1e-7 plane wave in a
  box of 1.35 initial Hubble radii, a = 1 to 1000): |f - f_ref| at most 8.4e-5 (16 cells),
  6.5e-6 (32), 4.9e-6 (64), for the density in the code's slicing against the relativistic
  dictionary f_ref = a/(a + 3/k^2) (Main.tex:673; it differs from the Einstein-de Sitter 1
  by 0.12 at a = 1) and for the gauge-invariant contrast delta_* (Main.tex:629, 633) against
  1. The plateau (a >= 3) converges at fourth order: 6.7e-5, 4.9e-6, 3.0e-7, and 2.6e-8 at
  128 cells (provisional, a <= 180). With particle number at 32 cells it falls from 4.9e-6
  (1 per cell) to 1.2e-6 and 1.5e-6 (8, 27 per cell), where the mesh part of 32 cells
  remains.
- Floor: in the first e-fold of expansion (a <= 2) a start error of the amplitude of about
  1.5e-6 to 2e-6 (|f_* - 1| about 5e-6 there) that does not change from 32 to 64 to 128
  cells. It is the step error of the start: the step limit 0.002 (the same at every mesh
  in the first e-fold) puts -1.9e-6 into the amplitude at 32 cells, converging at second
  order in the step (differences 1.47e-6 and 3.5e-7 for 0.002 -> 0.001 -> 0.0005, P3 and
  P4, entries 10 and 11), matching the -1.76e-6 floor at 128 cells. At the production step
  limit 0.01 it would be about 25 times larger, about 5e-5 [JUDGEMENT; not run].
- The potential estimator (a phi from chi) is the weakest: |f_phi - 1| up to 3.1e-3 (16),
  3.0e-4 (32), 1.7e-4 (64), set by an oscillation of period 2.34 in conformal time (speed
  L/P = 0.577 = 1/sqrt(3), that of the slicing d_t alpha = -(1/3) alpha^2 K
  [JUDGEMENT: a gauge wave]) whose amplitude falls with mesh and particle number.
  Sub-percent everywhere.

## Results

Leg F (analysis run B-20261121-220428-7367d5e, identical for the first eleven rows to
B-20261121-211951-b735833; columns: largest relative error over the run)

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
| f_n32_p1_a3 (P2) | B-20261121-212128-67b349a | 999 | 4.69e-03 | 4.26e-03 | 2.93e-03 | 2.13e-03 | 1.04e-03 / 3.20e-03 | 1.7e+00 |

Case names: f_n<cells>_p<particles per cell per direction>_a<noise: 0 none, 1 A1 = 4.2e-5,
2 A2 = 4.2e-4 = 0.01 h(32), 3 A3 = h(32)/2; uniform per component, seed 1>. With noise the
relative Hamiltonian constraint grows to order one: the noise contrast turns nonlinear at the
cell scale and the compensated cubic cloud then deposits negative cell densities (first at
a = 60 for 64 cells and 140 for 32 cells at A2, from the start at A3; entries 7, 9). The
scale factor is not affected beyond the numbers above.

Leg B (analysis run B-20261121-211956-b30627b; f errors against f_ref = a/(a + 3/k^2) for
delta and 1 for delta_* and the potential; plateau = median over 3 <= a <= 950; eps = the
decaying mode relative to the growing mode at a = 1, from ln(D_*/A a) = c0 + c1 ln a +
eps a^-5/2 on a <= 30)

| case | data run | largest abs(f_delta - f_ref) | plateau f_delta | plateau f_* | early f_* (a<=2) | f_phi largest | largest amplitude error | eps | Hr_max |
|---|---|---|---|---|---|---|---|---|---|
| b_n16_p1 | B-20261120-223006-24448ac | 8.36e-05 | 6.71e-05 | 6.70e-05 | 6.20e-05 | 3.06e-03 | 4.91e-04 | +3.3e-05 | 9.9e-10 |
| b_n32_p1 | B-20261120-222955-c8e16e3 | 6.48e-06 | 4.91e-06 | 4.91e-06 | 3.59e-06 | 2.97e-04 | 3.39e-05 | +4.5e-06 | 3.2e-09 |
| b_n32_p2 | B-20261120-222955-c8e16e3 | 5.33e-06 | 1.20e-06 | 1.20e-06 | 5.09e-06 | 2.10e-04 | 1.06e-05 | +1.4e-06 | 3.4e-09 |
| b_n32_p3 | B-20261120-222955-c8e16e3 | 5.45e-06 | 1.53e-06 | 1.54e-06 | 5.15e-06 | 2.09e-04 | 1.30e-05 | +1.3e-06 | 3.2e-09 |
| b_n64_p1 | B-20261121-202304-dc3020e | 4.86e-06 | 3.03e-07 | 3.02e-07 | 4.78e-06 | 1.69e-04 | 1.37e-06 | +2.5e-06 | 1.3e-08 |
| b_n128_p1 (provisional, a <= 190) | B-20261121-202335-3e6a898 | - | 2.96e-08 | 2.60e-08 | 4.85e-06 | - | 1.83e-06 | +2.8e-06 | - |

The provisional row is from run B-20261121-220441-06021c4 on the partial output of J3
(records to a = 189.5; plateau there over 3 <= a <= 180); the finished J3 replaces it.

Step test (leg B, 32 cells, 1 per cell, to a = 9; analysis run B-20261121-225745-773ffab):

| case | data run | step limit | eps (fit a <= 8.5) | c1 (f plateau) | largest difference of D_*/A a to the next larger step |
|---|---|---|---|---|---|
| b_n32_p1 (J1, card) | B-20261120-222955-c8e16e3 | 0.002 | +5.49e-6 | +5.59e-6 | - |
| s_n32_p1_dt2 (P3) | B-20261121-220450-e011c57 | 0.002 | +5.54e-6 | +5.58e-6 | 7.0e-8 to the card run |
| s_n32_p1_dt1 (P3) | B-20261121-220450-e011c57 | 0.001 | +3.87e-6 | +5.75e-6 | 1.47e-6 |
| s_n32_p1_dt05 (P4) | B-20261121-222813-560158b | 0.0005 | +3.42e-6 | +5.78e-6 | 3.53e-7 (ratio 4.2: second order) |

Figures (PNG and PDF in the analysis run directories; PNG copies in `figs/`):
`fig_f_lattice` (lattices), `fig_f_noise` (noise runs incl. P2, contrast, Hr), `fig_f_scaling`
(noise part against particles per cell and mesh, with the predicted laws),
`fig_f_constraints` (Hr maximum and mean, absolute momentum constraint, Theta);
`fig_b_growth` (f(a) and |f_* - 1|), `fig_b_error` (f and amplitude errors of the three
estimators), `fig_b_conv` (convergence in mesh and particle number), `fig_b_constraints`
(Hr, potential amplitude), `*_partial128` (with the provisional 128^3 row); `fig_step`
(step test). JSON copies in `results/`.

Failed predictions (entries 7, 9, 10): PF6 in part (alpha extrema 2.3e-5 above the
predicted 1e-5; the Hamiltonian constraint of the noise runs grows instead of being damped),
PB1 for the potential estimator, PB2 at 16 cells with the two-term fit, PB3 for the floor
(no floor at 1e-6 in the plateau; the early part has a floor of about 5e-6 in f), PB4 for
the amplitude (1 per cell differs from 8 and 27 by 4.5e-5), P2 "noise part of the alpha
extrema constant after a = 3" (it triples by a = 300), J3 "|e_D| at 128^3 at most a quarter
of 64^3's" (provisional: -1.76e-6 against -7.2e-7 at a = 100), P3 "the step is not the
cause of the early floor" (P4's prediction, second order in the step, held).

## Pending

- J3 = run B-20261121-202335-3e6a898, chain of `scripts/submit_chain.sh`: segment 1 (Slurm
  4825) ran 12:44-13:34 PST to t = 25.5 (a = 189); segment 2 is queued as Slurm 4849
  (pending at 14:33 PST). Leg B at 128^3, 1 per cell, to a = 1001; about 13,600 steps left at 0.31 s
  (1.2 card-hours). Predictions: entry 4 (as amended by entry 9: the amplitude error is set
  by the start, not the mesh, at 64 and 128 cells) and entry 8 (early part about 5e-6 in f).
  When it has ended: the chain or the lead's sequencer runs `nrpic-run finish`; then add
  `"b_n128_p1": "B-20261121-202335-3e6a898"` to `inputs/runs.json` and rerun
  `scripts/analyze_b.py` registered (the reader keeps the last segment of restarted records).

## Card time

J1 (Slurm 4746) 0.31 card-h, J2 (4824) 0.35 card-h, J3 segment 1 (4825) 0.83 card-h by
Slurm accounting; J3 needs about 1.2 more. The package reaches about 2.7 card-hours against
the 2.5 of its brief (J3 to a = 1001 was the lead's choice under decision 0025 item 4,
entry 4). No card job was submitted in batch 6. Processor runs P1-P4 at 4-6 threads.

## How to rerun

1. Initial data: `scripts/build_ic.sh` (runs B-20261120-222902-6b0be3c,
   B-20261120-222908-8aede2c, B-20261120-223448-7f7c034).
2. Simulations: card lists `inputs/batch_j1.list`, `batch_j2.list` (nrpic-run `--launcher
   batch`, executable `.work/build_gpu_v03/src/athena`), J3 deck `inputs/mode_prod_rst.athinput`
   (chain); processor lists `inputs/cpu_p1.list` to `cpu_p4.list` with `scripts/run_cpu.sh`
   (threaded executable `scratch/core/exe/core_build-openmp/athena_cpu`;
   `env THREADS=6 bash scripts/run_cpu.sh <list>` under nrpic-run).
3. Analysis (registered, one core), e.g.
   `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/B-emd-gw/flrw_conv
   --launcher local --cores 1 -- python3 tracks/B-emd-gw/flrw_conv/scripts/analyze_f.py
   tracks/B-emd-gw/flrw_conv/inputs/runs.json`; likewise `analyze_b.py` (`runs.json`) and
   `analyze_step.py` (`runs_step.json`).

## Runs of this package

| Run id | What | State |
|---|---|---|
| B-20261120-222902-6b0be3c | initial data, leg F all meshes, leg B 16/32 | completed |
| B-20261120-222908-8aede2c | initial data, leg B 64/128 | completed |
| B-20261120-223448-7f7c034 | initial data, Poisson-like start (A3) | completed |
| B-20261120-222955-c8e16e3 | J1 (card, Slurm 4746): F and B at 32^3 | completed |
| B-20261120-223006-24448ac | P1 (processors): F and B at 16^3 | completed |
| B-20261121-202304-dc3020e | J2 (card, Slurm 4824): F and B at 64^3 | completed |
| B-20261121-202335-3e6a898 | J3 (card chain, Slurm 4825, 4849): B at 128^3 | running |
| B-20261121-211524-e54164d, B-20261121-211626-e2a4df8 | analyses v1 of F and B | completed, superseded |
| B-20261121-211951-b735833, B-20261121-211956-b30627b | analyses v2 of F and B | completed |
| B-20261121-212128-67b349a | P2 (processors): Poisson-like start | completed |
| B-20261121-220428-7367d5e | analysis of F with P2 | completed |
| B-20261121-220441-06021c4 | analysis of B with the partial J3 (provisional) | completed |
| B-20261121-220450-e011c57 | P3 (processors): step test 0.002, 0.001 | completed |
| B-20261121-222718-311b50f | analysis of the step test (P3) | completed, superseded |
| B-20261121-222813-560158b | P4 (processors): step test 0.0005 | completed |
| B-20261121-225745-773ffab | analysis of the step test (P3, P4) | completed |

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | design, cost, predictions, outcomes |
| `inputs/flrw_prod.athinput` | leg F deck: homogeneous dust, production configuration, box 1.35085 |
| `inputs/mode_prod.athinput`, `mode_prod_rst.athinput` | leg B deck (step limit 0.002); the same with restart output for J3 |
| `inputs/runs.json` | case -> run directory of P1, J1, J2, P2 |
| `inputs/runs_j3_partial.json` | leg B cases with the partial 128^3 run |
| `inputs/runs_step.json` | cases of the step test |
| `inputs/batch_j1.list`, `batch_j2.list`, `batch_j3.list`, `cpu_p1.list` to `cpu_p4.list` | run lists |
| `scripts/build_ic.sh`, `scripts/ic_stats.py` | initial data and their deposited contrast |
| `scripts/run_cpu.sh`, `scripts/omp_places.py` | processor runs on core's threaded executable |
| `scripts/flrwlib.py` | readers, references a(t) and D(a), growth-rate estimators, decaying-mode fits, oscillation period |
| `scripts/analyze_f.py`, `analyze_b.py`, `analyze_step.py` | analyses and figures |
| `scripts/figstyle.py` | figure style (copy of `harness/style/figstyle.py`) |
| `figs/`, `results/` | PNG copies of the figures, JSON copies of the analyses |

## Requests

- To the lead: J3 is the only open row; when its chain has ended, rerun `analyze_b.py` with
  the 128^3 case (section "Pending") and record the outcome against entries 4, 8 and 9. The
  package passes its card cap by about 0.2 card-h if J3 completes (section "Card time").
- To the lead (optional, cards): the start error is best measured where the plateau is small:
  test B at 64^3 to a = 9 with step limits 0.002, 0.001, 0.0005 (three short card runs, about
  0.1 card-h together) would confirm at 64 cells the second-order start error found at 32
  cells (entry 11) and separate the early f floor from the plateau; test B at the production
  limit 0.01 would measure the start error the science runs carry (predicted about 5e-5 in
  the amplitude, entry 11).
- To core (no action needed for criterion (a)): the relative momentum constraint Mr of
  `.cstat.hst` is rounding over rounding on a homogeneous slice (it reads 1.41, about sqrt 2,
  for lattices at rest while |M| is 1e-11; run B-20261121-211951-b735833); a floor in its
  denominator, or a note in the format description, would avoid misreading it.
