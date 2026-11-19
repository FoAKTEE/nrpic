# heat: heat conduction with the collision operator (tests T6-T8 of collide/TESTS.md)

Helper package of C-sidm, wave 3a (2026-11-19). The heat-conduction tests T6 (temperature
step between two reservoirs at the long and the short mean-free-path end), T7
(conductivity from the isobaric mode) and T8 (convergence in time step, pair probability
and cell size) of `../collide/TESTS.md`, which nobody had run, with core's executables of
branch core/collisions-2 (`/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/`,
commit f46f159; `coll_energy = particle`, the corrected operator). Predictions and
outcomes, failed ones included: `JOURNAL.md`. No simulation code is written here
(decision 0010): the package has reference solutions, drivers, analysis and figures.

State: see "Results" (filled as runs finish) and "Pending runs".

## Contents

| Path | What |
|---|---|
| `inputs/heat.athinput` | periodic Minkowski box at x0 = 10 (flat Kerr-Schild functor), `nrpic_geodesic`, collision options of collisions.md on core/collisions-2; the drivers set mesh, step, sigma, seed, snapshots on the command line |
| `inputs/card_*.list` | card runs (batch launcher), written by `run_mode.py prep` |
| `scripts/heatlib.py` | paths, particle files (`../collide/analysis/make_box.py`), running the executable, reducing snapshots to slab sums or Fourier sums while a run goes on |
| `scripts/isobaric.py` | reference: nonlinear isobaric heat conduction in 1D (Lagrangian, kappa = f kappa_1(T), relativistic c_p, uniform pressure from the box volume); self-test |
| `scripts/design.py` | design numbers and predictions (windows, amplitude bias, fit error by Monte Carlo, cost) |
| `scripts/smoke.py` | S0: the deck runs; cost per particle and collision time; `particle` vs `cell` |
| `scripts/run_step.py` | T6 runs (parts a, b, c) on processors |
| `scripts/run_mode.py` | T7/T8 mode runs: `local` (processors), `prep` + list (card), `reduce` (card output) |
| `scripts/t2nosub.py` | T8 part 2: T2(b) at max P = 0.5 with and without sub-cycling |
| `scripts/an_step2.py` | T6 analysis (a: collisionless curve, slopes; b: f and literal statistic; c: transition) |
| `scripts/an_mode.py` | T7/T8 analysis (entropy-mode fit, f against the nonlinear reference, extrapolation in (k lambda)^2; collisionless check) |
| `results/` | JSON outputs copied from the run directories (run id in the name) |
| `figs/` | figures copied from the run directories (each looked at) |
| `JOURNAL.md` | predictions before each run, outcomes after |

## How to rerun

From the worktree root, with the worktree's `.venv`; every run registered with
`--package tracks/C-sidm/heat`:

    E=/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2
    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/heat"
    $S --cores 2 --purpose "S0"     -- python3 tracks/C-sidm/heat/scripts/smoke.py
    $S --cores 2 --purpose "design" -- python3 tracks/C-sidm/heat/scripts/design.py
    $S --cores 2 --purpose "T6b"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part b --seeds 1 2 --nproc 2
    $S --cores 6 --purpose "T7"     -- python3 tracks/C-sidm/heat/scripts/run_mode.py local \
        --theta 0.003 --eps 0.2 --kl 0.4 0.2 0.1 --seeds 1 2 3 4 --n 400000 --nproc 6 --tag T7_
    $S --cores 4 --purpose "T6a"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part a --seeds 1 2 --nproc 4
    $S --cores 3 --purpose "T6c"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part c --seeds 1 --nproc 3
    $S --cores 2 --purpose "T8 T2b" -- python3 tracks/C-sidm/heat/scripts/t2nosub.py
    # analysis (one core each); run ids are resolved under scratch/C-sidm/
    $S --cores 1 --purpose "T7 analysis" -- python3 tracks/C-sidm/heat/scripts/an_mode.py T7 - <run_id> [<run_id> ...]   ("-": the run directory)

## Results (processors, core_collisions-2 `athena_cpu`, `coll_energy = particle`)

| Test | Verdict | Run ids (run; analysis) | Key numbers | Figure |
|---|---|---|---|---|
| S0 smoke, cost | function ok; cost prediction failed | C-20261119-143228-31ba665 | n_trunc = n_noroot = n_balance = 0; `particle` = `cell` to 1.7e-16 in u; 2.1e-6 s per particle and step, 1.2e-6 s per tested pair (7 x the planning value; machine load ~100) | - |
| design | done | C-20261119-144117-37b2328 | T6(b) reference literal statistic 0.967 (f = 1), window [0.741, 50.88]; amplitude bias of the mode fit -1.0 percent at eps 0.2, -0.06 at 0.05; fit error by Monte Carlo | `figs/design_references.png` |
| T6(a) lambda/L = 1000 | PASS (2 seeds) | C-20261119-145733-558136e; C-20261119-152744-2bba6de | rms deviation from the exact collisionless curve 1.20/1.20/1.11 and 0.86/0.87/1.04 noise units (< 1.5); initial slopes of rest mass and energy 1.001/1.001 and 0.978/0.977 of -2 (Phi(1) - Phi(2)) (sd 1.2 percent) | `figs/T6a_step_long.png` |
| T6(a) lambda/L = 100 | reported | same | collisional deviation from the free streaming of the same sample 3.1-3.3 x that at 1000 = sqrt of the collided-fraction ratio (7.6/0.8 percent): stochastic scatter, not a drift proportional to t/t_coll (prediction's mechanism failed) | same |
| T6(b) lambda/L = 0.01 | PASS (2 seeds), precision a few percent | C-20261119-144535-2c7b6a4; C-20261119-160003-287b389 | f = 1.029, 1.063 (kappa = f kappa_1(T) in the nonlinear isobaric reference); literal chi_fit/chi(kappa_1, 0.015) = 0.994, 1.027 (reference itself 0.967); residuals show an early kinetic lag and sound-wave ringing (period L/c_s) that the isobaric reference lacks | `figs/T6b_step_short.png` |
| T6(c) lambda/L = 10, 1, 0.1 | reported | C-20261119-151104-b930d71; C-20261119-154057-471b5ec | collisionless curve down to lambda/L = 1; at 0.1 slower mixing and acoustic ringing (period ~1.1 L/<v>_2); not the diffusive curve predicted | `figs/T6c_transition.png` |
| T7 theta = 0.003 | PASS | C-20261119-144545-c606492; C-20261119-155257-754a43b | eps 0.2, 4 seeds x 4e5: f = 1.0232 +- 0.0039 (k lambda 0.1), 1.0170 +- 0.0049 (0.2), 1.034 +- 0.017 (0.4); extrapolated kappa/kappa_1 = 1.021 +- 0.004 in [0.99, 1.06]; Balberg et al. (0.72) excluded; the number mode alone gives 1.05, 1.11, 1.43 (sound waves) | `figs/T7_th0.003_e0.2_cpu.png` |
| T7 collisionless (k lambda = 100) | PASS | C-20261119-150358-3805fd5; C-20261119-152845-017d186 | max z 3.0, 3.1, 2.9 against the ensemble (< 4); against the free streaming of the same sample rms 0.27, 0.14, 0.05 noise units at theta 0.003, 0.1, 1 | `figs/T7_collisionless.png` |
| T8 part 2: T2(b) at max P 0.56 | PASS, no deficit | C-20261119-150358-66295f7; C-20261119-151044-a584069 | without sub-cycling 1.000025 +- 0.000041, with 0.999992 +- 0.000026 of the analytic rate; n_trunc 0 | `figs/T8_t2_nosub.png` |
| T7 theta = 0.1, 1 | (processors running) | | | |
| T8 coarse (5e5 per variant) | (processors running) | | | |

Card jobs (pending in the Slurm queue at the end of the session): see "Pending runs".

Findings for the track:
1. The conductivity of the operator is the Chapman-Enskog hard-sphere value: kappa =
   1.021 +- 0.004 kappa_1 at theta = 0.003 (expected ~1.025 from higher Sonine terms
   [BACKGROUND]). The conduction coefficient b = 25 sqrt(pi)/32 (Koda & Shapiro; arXiv:
   2601.17117) is right and Balberg et al.'s 25 pi/(32 sqrt 6) is not, for this operator
   (SPEC.md 7.3's open question) [VERIFIED by run]. arXiv:2505.15903 (Gurian & May,
   `kb-data/raw/arxiv/2505.15903/v2/src/sidm.tex` lines 94 and 163) also uses
   b = 25 sqrt(pi)/32 and reports that its kinetic code reproduces the Chapman-Enskog
   conductivity to 2 percent [VERIFIED that the text says so].
2. TESTS.md T7 as written (fit of the number-density mode) is biased by sound waves that
   the initial transient launches (+5, +11, +43 percent at k lambda 0.1, 0.2, 0.4); the
   entropy combination A_S = (A_K - A_N)(<W> - 1)/theta - A_N removes them.
3. The statistical precision of a mode measurement is set by the equilibrium entropy
   fluctuations (var A_S = 2 c_p/N): ~5 percent per run of 1e6 particles at eps = 0.05;
   eps = 0.2 with the nonlinear reference (bias -1 percent) is 16 times cheaper.
4. T6(b) with a contrast of 2 is nonlinear (the isobaric reference scores 0.967 on the
   literal statistic) and rings acoustically at lambda/L = 0.01; it checks kappa to a
   few percent, T7 to half a percent.
5. Without sub-cycling the collision rate is still exact (no deficit) as long as no pair
   exceeds P = 1.
6. Cost on processors under load: 2.1e-5 s per particle per collision time (1.2e-6 s per
   tested pair, 17 tested pairs per particle per t_coll at dt = 0.1 t_coll).

## Pending runs

(filled at the end of the session)

## Requests

(filled at the end of the session)
