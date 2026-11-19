# Slow-roll ladder toward gate G1 (E-stoch-inf, helper package of waves 2 and 2b)

The slow-roll (SR, quadratic) case of arXiv:2512.14649 run in this repository's AthenaK with
core's published executables of branch `core/scalar-2` (a58e95b,
`scratch/core/exe/core_scalar-2/`), judged by the owner's thresholds A1-A6 (SCOPE 4,
restated in `JOURNAL.md` entry 1 before any run; A6 in entry 8): power spectrum against the
linear (Mukhanov-Sasaki) and slow-roll results, freezing of super-horizon modes by the
criterion of SPEC 7.3, convergence of the constraints, temporal order. Predictions and
outcomes: `JOURNAL.md` (entries 1-10).

## Results (each with its run; details and the failed predictions in `JOURNAL.md`)

| Threshold | Verdict | Numbers | Runs |
|---|---|---|---|
| A1 background | PASS | box means within 1.1e-12 (phi), 8.6e-12 (Pi), 2.0e-12 (K); e-folds 5.5e-6, 3.3e-7, 2.0e-8 at N = 32, 64, 128 (fourth order) | final analysis E-20261115-194633-9e04ed8 |
| A2 per mode, |n| <= k_max/2 | PASS | 8.8e-5 (L32) to 1.7e-6 (L256); paper set-up Q64 9.7e-5, Q128 9.9e-5, P256 1.21e-4 (threshold 0.02) | same |
| A3 freezing | PASS | 1051 modes per rung: power ratio within 4.6e-6, drift 1.4e-4 per e-fold = full MS within 1.8e-6 (threshold 2.5e-3; FLRW lattice -0.05) | same |
| Spectrum against linear and slow-roll results | PASS | shell ratios within 1.9e-4; Delta_lin/slow-roll formula 1.0104-1.0109 for |n| <= 7 | same |
| A4 constraints of second order during the entry | FAIL in the paper's set-up (k_max = N/4) at N = 32-256; PASS in the k_max/dk = 8 set-up from N = 128 | odd (first-order) part of H up to 385-870 times the even part from N = ln(N/8); magnitude <= 5.1e-11 (within 10 x P1's 1e-10); halving 2.00 (odd), 4.00 (even) | same; floor analysis E-20261119-142713-32c883a |
| A5 convergence before the floor | PASS with the floor made operational (JOURNAL entry 9) | odd part order 4.2-5.8 (H), 5.6-5.9 (M) on 32 -> 64 -> 128; floor independent of the amplitude, growing as N^2.5 | same |
| A6 temporal order | see `JOURNAL.md` entry 10 | | E-20261119-142317-c851f27 (runs), analysis in entry 10 |
| A7 restart (NOISE_SPEC A12) | PASS | U4 bit-identical to U2 on processors and on a card (whole dump files equal) | E-20261119-141654-c2a10d1 |
| Negative control | PASS | H 4e4-1.5e5 times the proper run, M/[M] 0.20-0.22 | final analysis |
| Cost | | 1.13-1.30 card-s per step at 256^3; 0.50 card-hours per 8-e-fold realisation | E-20261115-172618-f948386 |

Card time used by the package: 1.42 card-hours (jobs A, B, C) of the two allowed.

## Contents

| Path | What |
|---|---|
| `inputs/sr_base.athinput` | base input: SR case in code units (G = 1, time unit 1/H*, box 2 pi), initial slice at N* (`id = stochastic`), Mukhanov-Sasaki sources, geodesic slicing, Courant 0.25, dumps every 0.5 time units with phi, Pi, chi, gt_ij, K, At_ij, alpha, H, M_i, E |
| `inputs/sr_a6.athinput`, `inputs/a6proc.list` | A6: the base input with dumps every `dump_dcycle` cycles; six processor runs at Courant 0.25, 0.125, 0.0625, s = +-1, N = 32 |
| `inputs/modes_n{64,256,1024,4096}.txt` | mode files (R, dR/dtau at N* per shell); 64 = core's `problems/scalar/sr_stochastic_modes.txt`, the others from core's `make_case.py --kstart 100` (run E-20261115-171633-f574079) |
| `inputs/jobA.list`, `jobB.list`, `jobC.list` | card batches (P256; P256m + L256p; L256m + N = 64, 128 rungs, halving, negative controls) |
| `inputs/proc32.list`, `proc64.list` | processor runs (N = 32 rung; N = 64 hedge to t = 4.5) |
| `scripts/ladder_lib.py` | own NRSFDMP2 reader, mode coefficients on the hemisphere, R^NR extraction, linear reference (background + MS per shell, window), amplitudes from `../noise/ref/philox_ref.py` |
| `scripts/ladder_analysis.py` | `extract` (per dump R^NR, reference, constraint statistics; A1), `pair` (odd/even parts under s -> -s), `judge` (A2, A3, shell spectrum) |
| `scripts/analyse_all.py`, `scripts/verdicts.py` | the three on every ladder run found; A1-A5, negative control, cost -> `summary.json` |
| `scripts/floor_analysis.py` | floor of the odd parts (N^q from 128 -> 256), A5 before the floor, halving, first e-fold of odd > even against ln(N/8), even part with the floor in quadrature |
| `scripts/a6_analysis.py` | A6: differences between Courant factors at equal times, orders, D_n per Courant factor, constraint parts |
| `scripts/make_figures.py`, `scripts/figstyle.py` | figures (style copied from `harness/style/figstyle.py`) |
| `scripts/selftest.py`, `extraction_check.py`, `modefile_check.py` | reader against core's, R^NR at t = 0; the factor of the anisotropic term (SPEC 9 E6); mode files against Track E's MS reference |
| `scripts/run_list_cpu.sh` | runs a list on the processors inside a registered run |
| `results/final/`, `fig/final/` | JSON and figures of the final analysis of all rungs (E-20261115-194633-9e04ed8) |
| `results/floor/`, `fig/floor/` | floor analysis (E-20261119-142713-32c883a) |
| `results/a6/`, `fig/a6/` | A6 analysis |
| `results/a12/` | A12 validations (E-20261119-141654-c2a10d1) |
| `results/proc32*/`, `results/P256/`, `fig/proc32*/`, `fig/P256/` | earlier partial analyses (wave 2), kept for the record |

Definitions (R^NR, D_n, Q_n, N_k, odd/even parts): `JOURNAL.md` entry 1.

## How to rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create
--no-kokkos`):

    X=/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2
    I=tracks/E-stoch-inf/ladder/inputs
    # processors (32^3, 3-6 s per step on one core, depending on the load)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher local --cores 6 --background --input $X/athena_cpu \
      --input $I/proc32.list --purpose "..." -- \
      bash tracks/E-stoch-inf/ladder/scripts/run_list_cpu.sh $X/athena_cpu $I/proc32.list
    # (A6: the same with $I/a6proc.list)
    # cards (one Slurm job per list)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher batch --exe $X/athena_gpu --list $I/jobA.list --wall 00:45:00 \
      --purpose "..."
    # analysis of any set of run directories (registered)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher local --cores 8 --purpose "..." -- bash -c \
      'cd tracks/E-stoch-inf/ladder/scripts && export OMP_NUM_THREADS=8 && \
       python3 analyse_all.py --runs RUNDIR... --out "$NRPIC_RUN_DIR/res" && \
       python3 verdicts.py --res "$NRPIC_RUN_DIR/res" --rundirs RUNDIR... \
         --out "$NRPIC_RUN_DIR/summary.json" && \
       python3 make_figures.py --res "$NRPIC_RUN_DIR/res" --out "$NRPIC_RUN_DIR/fig"'
    # floor analysis and A6 on the outputs above
    ... bash -c 'cd tracks/E-stoch-inf/ladder/scripts && python3 floor_analysis.py \
         --res RES_DIR --out "$NRPIC_RUN_DIR"'
    ... bash -c 'cd tracks/E-stoch-inf/ladder/scripts && python3 a6_analysis.py \
         --run A6_RUNDIR --out "$NRPIC_RUN_DIR"'

Traps: nrpic-run runs its command without a shell; write `$NRPIC_RUN_DIR` only inside
`bash -c '...'` (run E-20261115-172521-e098160 wrote into a directory named
`$NRPIC_RUN_DIR`). A run with `tlim` ends with a dump after a shortened step at exactly
`tlim`; a partner with a larger `tlim` dumps at the same cycle at a later time, so mirrored
or halved pairs must share `tlim` (or dump by cycle, as `sr_a6.athinput` does).

Disk: a 256^3 dump with the metric and the constraints is 2.95 GB; job A wrote 18 of them
(53 GB), job B 10 + 10 (13 + 30 GB), job C about 40 GB.

## Requests

To the lead (owner of `spec/` and `spec/scope/SCOPE.md`); proposals, not adopted here:

1. A4, reworded (the strict form fails in the paper's set-up for a reason of the method,
   JOURNAL entries 2, 6, 9, 10; core's T12 found the same at 32 and 64):
   "A4: split H and M_i into the parts odd and even in the amplitude s with a mirrored
   pair (s = +-1), and halve s once. (a) The even part with its box mean removed scales by
   4.00 +- 0.05 when s is halved and agrees between the two finest resolutions within 5
   percent where it lies above the rounding floor (the second-order violation does not
   depend on the resolution, P1's plateau; measured: 2.2 percent between 64 and 128). (b) The odd part (first order in s) is truncation: it
   converges at the order of A5, and it may exceed the even part while shells with fewer
   than eight cells per wavelength enter (from N = ln(N_cells/8) e-folds after N* in the
   paper's set-up k_max = N_cells/4). (c) The record <|H|/[H]> stays within a factor 10 of
   P1's 1e-10 (P1:538-539) and <|M|/[M]> below 1e-3. (d) The negative control with the
   sign of the Pi kick flipped has an odd part at least 1e3 times that of the proper run.
   The record ratios themselves are no order test: they contain the uniform residual H0 of
   the time integration, which does not depend on s, and [M] is first order in s."
2. A5, made operational: "before the floor" = where the finer odd part exceeds three times
   the rounding floor, the floor being the part that does not scale with s (halving factor
   1) and grows with N (here N^2.5, 6e-13 of <[H]> at N = 256 half an e-fold after N*).
3. A2: the reference for this scheme is the continuum mode function, not the one with
   the stencil's k^2 (entry 6: the stencil reference fits worse, 6.2e-3 against 1.2e-4 at
   256^3, because a mode enters the lattice through the window from the code's continuum
   mode functions).
4. SPEC 9 E6 (factor 1/4 of the anisotropic term of R^NR) can be relabelled
   [VERIFIED by run] (entry 4, run E-20261115-174214-74becdd).
5. The analysis package's pending predictions P5 and P5' (A12) are now tested and hold
   (entry 7, run E-20261119-141654-c2a10d1); its runs E-20261115-170727-d15df12 and
   E-20261115-180526-6b68c33 are closed.

To core (information for package scalar3, item "first-order truncation at late mode
entry"): the first-order part enters exactly with the shells of fewer than eight cells per
wavelength (first dump with odd > even at N = 1.51, 1.99, 2.96, 3.44 against ln(N/8) =
1.39, 2.08, 2.77, 3.47 for N = 32-256); entry 10 says whether it is spatial or temporal.

Not done: the USR case (G2), a second seed, a halving pair at 256^3, A6 at 64^3 on a card
(L6 asks 64^3; run here at 32^3 on processors), sensitivity L9.
