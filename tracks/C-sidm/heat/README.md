# heat: heat conduction with the collision operator (tests T6-T8 of collide/TESTS.md)

Helper package of C-sidm, wave 3a (2026-11-19), closed in wave 3 (2026-11-20/21). The
heat-conduction tests T6 (temperature step between two reservoirs at the long and the short
mean-free-path end), T7 (conductivity from the isobaric mode) and T8 (convergence in time
step, pair probability and cell size) of `../collide/TESTS.md`, which nobody had run, with
core's executables of branch core/collisions-2
(`/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/`, commit f46f159;
`coll_energy = particle`, the corrected operator). Predictions and outcomes, failed ones
included: `JOURNAL.md`. No simulation code is written here (decision 0010): the package has
reference solutions, drivers, analysis and figures.

State (2026-11-21 03:10 UTC): CLOSED. Every run is finished and analysed; both card jobs are
reduced and closed; no run is pending. Verdicts: section "Verdict for G1 C6".

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
| `scripts/prep_card.sh` | particle files and `case.json` of the card cases, lists `inputs/card_*.list` |
| `scripts/check_pfiles.py` | first snapshot of every case against its particle file; regenerated against shared particle files (byte for byte) |
| `scripts/an_compare.py` | `cardcpu` (card seeds against processor seeds, N-weighted pooling), `eps` (eps 0.05 against 0.2), `t8` (changes between neighbouring dt, pmax, dx; cell-size fits), `seedpairs` (chi^2 of card z and of same-executable seed pairs) |
| `scripts/summary_c6.py` | post-hoc arithmetic for the verdict: T7 against the relativistic Chapman-Enskog value of `../verify_g1/` V1a, cell-size correction from card T8, eps 0.05 alone, S-pairs with the design noise |
| `results/` | JSON outputs copied from the run directories (run id in the name) |
| `figs/` | figures copied from the run directories (each looked at) |
| `JOURNAL.md` | predictions before each run, outcomes after |

## How to rerun

From the worktree root, with the worktree's `.venv`; every run registered with
`--package tracks/C-sidm/heat` (local runs with `--background` must be closed with
`harness/bin/nrpic-run finish <run_id>`; that is by design, not a failure):

    E=/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2
    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/heat"
    R=tracks/C-sidm/heat/scripts
    $S --cores 2 --purpose "S0"     -- python3 $R/smoke.py
    $S --cores 2 --purpose "design" -- python3 $R/design.py
    $S --cores 2 --purpose "T6b"    -- python3 $R/run_step.py --part b --seeds 1 2 --nproc 2
    $S --cores 4 --purpose "T6a"    -- python3 $R/run_step.py --part a --seeds 1 2 --nproc 4
    $S --cores 2 --purpose "T6c"    -- python3 $R/run_step.py --part c --seeds 1 --nproc 2
    $S --cores 6 --purpose "T7"     -- python3 $R/run_mode.py local --theta 0.003 --eps 0.2 \
        --kl 0.4 0.2 0.1 --seeds 1 2 3 4 --n 400000 --nproc 6 --tag T7_
    #   (same with --theta 0.1 / 1.0 --seeds 1 or 2; --kl 0.2 0.4 --seeds 11 12 13 14)
    $S --cores 2 --purpose "CL"     -- python3 $R/run_mode.py local --theta 0.003 --kl 100 \
        --eps 0.05 --seeds 1 --n 400000 --nproc 1 --tag CL_          # also theta 0.1, 1
    $S --cores 4 --purpose "T8 coarse" -- python3 $R/run_mode.py local --theta 0.003 --kl 0.2 \
        --eps 0.2 --seeds 1 --n 500000 --nproc 4 --tag T8p_ --nt-fixed 8 --ly-fixed 1.9634954084936207 \
        --variants '[{}, {"dt_frac": 0.2}, {"dt_frac": 0.05}, {"pmax": 0.2}, {"pmax": 0.05}, {"dx_frac": 0.5}, {"dx_frac": 0.125}]'
    $S --cores 2 --purpose "T8 T2b" -- python3 $R/t2nosub.py      # analysis: t2nosub.py --analyse-only DIR
    # card: particle files and lists, then the batch jobs
    $S --cores 2 --purpose "card prep" -- bash $R/prep_card.sh
    $S --launcher batch --list tracks/C-sidm/heat/inputs/card_A.list --gpu-hours 0.92 --wall 00:55:00 \
        --exe $E/athena_gpu --purpose "card A"                        # and card_B.list
    # analyses (one core each; run ids are resolved under scratch/C-sidm/; "-": the run directory)
    $S --cores 1 --purpose "T6a" -- python3 $R/an_step2.py a - <T6a run>
    $S --cores 1 --purpose "T6b" -- python3 $R/an_step2.py b - <T6b run>
    $S --cores 1 --purpose "T6c" -- python3 $R/an_step2.py c - <T6a run> <T6c run>
    $S --cores 1 --purpose "T7"  -- python3 $R/an_mode.py T7 - <run> [<run> ...]
    $S --cores 1 --purpose "CL"  -- python3 $R/an_mode.py CL - <CL run>
    $S --cores 1 --purpose "T8"  -- python3 $R/an_mode.py T8 - <run with T8* cases>
    # wave 3 closing runs (registered with --gate G1 instead of G2, and a --purpose each;
    # SC=/data/haiyangw/nrpic/scratch/C-sidm; run ids resolve under SC), in the order they ran:
    P=$SC/C-20261119-145725-d91858e
    $S --cores 4 --parent C-20261119-150335-73fd40f -- python3 $R/run_mode.py reduce $SC/C-20261119-150335-73fd40f --prep $P --nproc 4
    harness/bin/nrpic-run finish C-20261119-150335-73fd40f        # same two lines for job B, -150347-e100007
    $S --cores 1 -- python3 $R/check_pfiles.py - C-20261119-154032-e450dfc C-20261119-162015-d97abac \
        C-20261119-162353-7985a9a C-20261119-150335-73fd40f --pairs <regenerated>:<shared> ...   # exact: manifest of C-20261120-222547-e1c0353
    $S --cores 1 -- python3 $R/check_pfiles.py - C-20261119-150347-e100007 C-20261119-152752-0ffa031 \
        C-20261119-155433-a287f9c C-20261119-144545-c606492 C-20261119-155434-8563453
    $S --cores 1 -- python3 $R/an_mode.py T8 - C-20261119-154032-e450dfc C-20261119-162015-d97abac C-20261119-162353-7985a9a
    $S --cores 1 -- python3 $R/an_mode.py T8 - C-20261119-150335-73fd40f
    $S --cores 1 -- python3 $R/an_mode.py T7 - C-20261119-150335-73fd40f
    $S --cores 1 -- python3 $R/an_mode.py T7 - C-20261119-144545-c606492 C-20261119-155434-8563453 C-20261119-150347-e100007
    $S --cores 1 -- python3 $R/an_mode.py T7 - C-20261119-152752-0ffa031 C-20261119-155433-a287f9c C-20261119-150347-e100007
    $S --cores 1 -- python3 $R/an_compare.py cardcpu - C-20261120-223001-eb81eb7 C-20261120-222954-b1a06ed
    $S --cores 1 -- python3 $R/an_compare.py eps - C-20261120-222702-e2e02df T7_th0.003_e0.05 C-20261120-223001-eb81eb7 T7_th0.003_e0.2
    $S --cores 1 -- python3 $R/an_compare.py t8 - --noise C-20261120-223001-eb81eb7 T7_th0.003_e0.2 C-20261120-222624-cae43d6 C-20261120-222620-6ecac07
    $S --cores 1 -- python3 $R/an_compare.py seedpairs - C-20261120-223203-b38a7d7
    $S --cores 1 -- python3 $R/summary_c6.py -

## Results (core_collisions-2 `athena_cpu` on processors, `athena_gpu` on the card; `coll_energy = particle`)

f = kappa/kappa_1, kappa_1 = (75 sqrt(pi)/64) sqrt(theta)/sigma (first Chapman-Enskog
approximation, non-relativistic form), from the entropy-mode rate divided by that of the
nonlinear isobaric reference with the relativistic c_p (finite-amplitude bias removed).

| Test | Verdict | Run ids (run; analysis) | Key numbers | Figure |
|---|---|---|---|---|
| S0 smoke, cost | function ok; cost prediction failed | C-20261119-143228-31ba665 | n_trunc = n_noroot = n_balance = 0; `particle` = `cell` to 1.7e-16 in u; 2.1e-6 s per particle and step, 1.2e-6 s per tested pair (7 x the planning value; machine load ~100) | - |
| design | done | C-20261119-144117-37b2328 | T6(b) reference literal statistic 0.967 (f = 1), window [0.741, 50.88]; amplitude bias of the mode fit -1.0 percent at eps 0.2, -0.06 at 0.05; fit error by Monte Carlo | `figs/design_references.png` |
| T6(a) lambda/L = 1000 | PASS (2 seeds) | C-20261119-145733-558136e; C-20261119-152744-2bba6de | rms deviation from the exact collisionless curve 1.20/1.20/1.11 and 0.86/0.87/1.04 noise units (< 1.5); initial slopes of rest mass and energy 1.001/1.001 and 0.978/0.977 of -2 (Phi(1) - Phi(2)) (sd 1.2 percent) | `figs/T6a_step_long.png` |
| T6(a) lambda/L = 100 | reported | same | collisional deviation from the free streaming of the same sample 3.1-3.3 x that at 1000 = sqrt of the collided-fraction ratio (7.6/0.8 percent): stochastic scatter, not a drift proportional to t/t_coll (prediction's mechanism failed) | same |
| T6(b) lambda/L = 0.01 | PASS (2 seeds), precision ~2.5 percent per seed | C-20261119-144535-2c7b6a4; C-20261119-160003-287b389, C-20261119-162440-296dad0 (late window) | f = 1.029, 1.063 (kappa = f kappa_1(T) in the nonlinear isobaric reference; late window 1.036, 1.066); literal chi_fit/chi(kappa_1, 0.015) = 0.994, 1.027 (reference itself 0.967); mean f 1.046 +- 0.017, consistent with T7 at 1.6 sd; residuals show an early kinetic lag and sound-wave ringing (period L/c_s) that the isobaric reference lacks | `figs/T6b_step_short.png` |
| T6(c) lambda/L = 10, 1, 0.1 | reported | C-20261119-151104-b930d71; C-20261119-154057-471b5ec | collisionless curve down to lambda/L = 1; at 0.1 slower mixing and acoustic ringing (period ~1.1 L/<v>_2); not the diffusive curve predicted | `figs/T6c_transition.png` |
| T7 theta = 0.003 | PASS | C-20261119-144545-c606492, C-20261119-155434-8563453; C-20261119-161930-acd257b | eps 0.2, 4e5 per run: f = 1.0232 +- 0.0039 (k lambda 0.1, 4 seeds), 1.0174 +- 0.0047 (0.2, 8 seeds), 1.041 +- 0.011 (0.4, 8 seeds); extrapolated kappa/kappa_1 = 1.019 +- 0.004 in [0.99, 1.06]; Balberg et al. (0.72) excluded; the number mode alone gives 1.05, 1.11, 1.45 (sound waves) | `figs/T7_th0.003_e0.2_cpu.png` |
| T7 collisionless (k lambda = 100) | PASS | C-20261119-150358-3805fd5; C-20261119-152845-017d186 | max z 3.0, 3.1, 2.9 against the ensemble (< 4); against the free streaming of the same sample rms 0.27, 0.14, 0.05 noise units at theta 0.003, 0.1, 1 | `figs/T7_collisionless.png` |
| T8 part 2: T2(b) at max P 0.56 | PASS, no deficit | C-20261119-150358-66295f7; C-20261119-151044-a584069 | without sub-cycling 1.000025 +- 0.000041, with 0.999992 +- 0.000026 of the analytic rate; n_trunc 0 | `figs/T8_t2_nosub.png` |
| T7 theta = 0.003, all seeds (8 processor at 4e5, card seed 5 at 4e6) | PASS | C-20261119-144545-c606492, C-20261119-155434-8563453, C-20261119-150347-e100007; C-20261120-223001-eb81eb7 (unweighted), C-20261120-223203-b38a7d7 (weights proportional to N) | f0 = 1.0208 +- 0.0034 (unweighted), 1.0250 +- 0.0025 (N-weighted; chi^2 6.6 for 1 dof, se x 2.6 if scaled); in [0.99, 1.06] | `figs/T7_th0.003_e0.2_pooled.png`, `figs/cardcpu_th0.003.png` |
| T7 theta = 0.003 at eps = 0.05 (card, 4e6, seeds 1, 2, k lambda 0.2, 0.4) | consistent with eps 0.2 | C-20261119-150335-73fd40f; C-20261120-222702-e2e02df, C-20261120-223208-4ca3110, C-20261121-030328-e3ffc6d | f = 1.0011 (k lambda 0.2), 1.0565 (0.4); against eps 0.2: -2.05 percent (z -1.62), +1.27 percent (z +0.45); alone, two-point extrapolation 0.983 +- 0.019 (expected se), 0.4 se below 0.99 | `figs/T7_th0.003_e0.05_card.png`, `figs/T7_eps0.05_vs_0.2.png` |
| T7 theta = 0.1 (2 processor seeds at 4e5, 2 card seeds at 2e6) | reported; agrees with relativistic CE (post hoc) | C-20261119-152752-0ffa031, C-20261119-155433-a287f9c, C-20261119-150347-e100007; C-20261120-222954-b1a06ed, C-20261120-223203-b38a7d7, C-20261121-030328-e3ffc6d | f0 = 1.0957 +- 0.0051 (N-weighted; unweighted 1.1013 +- 0.0052); relativistic CE order 4 of verify_g1 V1a (C-20261120-222423-519f12b): 1.0988 +- 0.0015, difference -0.28 percent (z -0.58); f_N > f_S in every seed | `figs/T7_th0.1_e0.2_pooled.png`, `figs/cardcpu_th0.1.png`, `figs/summary_c6.png` |
| T7 theta = 1 (same seeds) | reported; agrees with relativistic CE (post hoc) | same | f0 = 0.9914 +- 0.0035 (N-weighted; unweighted 0.9854 +- 0.0046); CE order 4: 0.9933 +- 0.0010, difference -0.19 percent (z -0.51); CE first order 0.9407 excluded (14 se) | `figs/T7_th1_e0.2_pooled.png`, `figs/cardcpu_th1.png`, `figs/summary_c6.png` |
| T8 card (one seed, 4e6, one particle file for 7 variants) | PASS | C-20261119-150335-73fd40f; C-20261120-222624-cae43d6, C-20261120-223321-3d088d4 | f at dt 0.05/0.1/0.2: 1.0169/1.0222/1.0203; pmax 0.05/0.1/0.2: 1.0221/1.0222/1.0274; dx lambda/8, /4, /2: 1.0116/1.0222/1.0403; changes between the two finest values -0.52, -0.006, -1.04 percent (< 2; expected sd of a change 0.61); n_trunc 0 | `figs/T8_changes.png`, `figs/T8_card_convergence.png` |
| T8 trend in dx (card) | reported | same | kappa rises with dx: quadratic c = 0.115 +- 0.025 per (dx/lambda)^2 (chi^2 0.76) or linear 0.076 +- 0.016 (chi^2 0.04); bias at the T7 cell size 0.245 lambda: +0.69 +- 0.15 or +1.87 +- 0.39 percent | `figs/T8_changes.png` |
| T8 processors (seeds 1, 2 x 5e5) | P-T8c held; too noisy for the 2 percent criterion | C-20261119-154032-e450dfc, C-20261119-162015-d97abac, C-20261119-162353-7985a9a; C-20261120-222620-6ecac07 | largest change between neighbours 4.27 percent (< 5); expected sd of a change 1.73 percent; same dx trend as the card | `figs/T8_changes.png`, `figs/T8_cpu_convergence.png` |
| Particle files (P-pf) | PASS | C-20261120-222547-e1c0353, C-20261120-222846-029c453 | regenerated T8 particle files byte-identical to the shared ones; first snapshot of all 72 started cases bit-identical to its particle file | - |
| Card against processor (P-cc, S-pairs) | PASS at theta 0.003; no card bias seen at 0.1, 1 | C-20261120-223203-b38a7d7, C-20261121-025837-8b5b9ee, C-20261121-030328-e3ffc6d | theta 0.003: z = +1.79, +1.19, +0.27; all three temperatures: mean z_ref of the 15 card seeds -0.29 +- 0.26 (no common offset); excess chi^2 at k lambda 0.1 in card and processor pairs alike (noise model from 4 seeds; with the design noise chi^2 8.7 for 12 pairs) | `figs/cardcpu_th*.png`, `figs/seedpairs.png` |

Card time of the package: jobs A and B, 0.2425 + 0.2739 = 0.516 card-hours of allocation
(1.84 reserved). Disk: the reductions freed 47.5 GB (job A) and 38.9 GB (job B); the two run
directories now hold 6.45 and 5.31 GB.

Findings for the track:
1. The conductivity of the operator is the Chapman-Enskog hard-sphere value: kappa =
   1.019 +- 0.004 kappa_1 at theta = 0.003 (expected ~1.025 from higher Sonine terms
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
7. (Wave 3) The operator reproduces the relativistic Chapman-Enskog conductivity of
   isotropic hard spheres at theta = 0.1 and 1 to 0.3 percent, including the Sonine
   correction (+5.6 percent at theta = 1 between orders 1 and 4), against the reference that
   the owner's verifier computed (`../verify_g1/`, run C-20261120-222423-519f12b; post-hoc
   comparison, run C-20261121-030328-e3ffc6d) [VERIFIED by runs; the reference is
   unreviewed]. At theta = 0.003 the measured value at dx = lambda/4 lies 0.5-1.0 percent
   below that reference (1.0296), and finding 8 pushes the zero-cell-size value 1.2-2.9
   percent below it [TO VERIFY].
8. (Wave 3) The conductivity rises with the cell size: +1.0 percent from lambda/8 to
   lambda/4 and +1.8 percent from lambda/4 to lambda/2 at k lambda 0.2 (card, one seed;
   both processor seeds show the same rise). The T7 runs at dx = 0.245 lambda carry
   +0.7 (quadratic form) to +1.9 percent (linear form) from it; one seed cannot fix the
   form. The time-step dependence (0.05-0.2 t_coll) is below 0.6 percent and not resolved.

## Verdict for G1 C6 (heat conduction, T6-T8)

Judged against `../collide/TESTS.md` as written (sections 2 and 2a) and against the readings
declared in `JOURNAL.md` before the runs (D1-D4 of 2026-11-19 14:50), with the wording this
package proposes under "Requests". This is the helper's verdict; the lead decides C6.

| Test | As written | With the proposed wording | Evidence (runs; analyses) |
|---|---|---|---|
| T6(a) lambda/L = 1000 | PASS | PASS | C-20261119-145733-558136e; C-20261119-152744-2bba6de: rms 1.20/1.20/1.11 and 0.86/0.87/1.04 noise units (< 1.5); initial slopes 1.001/1.001 and 0.978/0.977 of -2 (Phi(1) - Phi(2)) (within 5 percent) |
| T6(a) lambda/L = 100 | REPORTED (the "proportional to t/t_coll" description does not fit: the deviation scales as the square root of the collided fraction) | REPORTED | same runs; JOURNAL 2026-11-19 15:31 |
| T6(b) lambda/L = 0.01 | PASS (literal chi_fit/chi(kappa_1) = 0.994, 1.027 in [0.95, 1.10]) | PASS (f = 1.029, 1.063 against the nonlinear reference; mean 1.046 +- 0.017) | C-20261119-144535-2c7b6a4; C-20261119-160003-287b389, C-20261119-162440-296dad0; the verifier's own analysis C-20261120-223133-2f98a0e gives f = 1.027, 1.062 |
| T6(c) lambda/L = 10, 1, 0.1 | REPORTED (no criterion) | REPORTED | C-20261119-151104-b930d71; C-20261119-154057-471b5ec |
| T7 theta = 0.003 | PASS: kappa/kappa_1 = 1.019 +- 0.004 (processor seeds), 1.021 +- 0.003 (all seeds), 1.025 +- 0.003 (N-weighted), in [0.99, 1.06]; with the cell-size bias of T8 removed 1.000-1.018, still inside; Balberg et al. (0.72) excluded. TESTS.md names both the number mode and the W - 1 weighted mode; the verdict uses their entropy combination at eps = 0.2 (reading D3). The literal eps = 0.05 set alone (two k lambda, two seeds) gives 0.983 +- 0.019, consistent with the interval | PASS | C-20261119-144545-c606492, C-20261119-155434-8563453, C-20261119-150347-e100007, C-20261119-150335-73fd40f; C-20261119-161930-acd257b, C-20261120-223001-eb81eb7, C-20261120-223203-b38a7d7, C-20261120-222702-e2e02df, C-20261120-223208-4ca3110, C-20261121-030328-e3ffc6d |
| T7 theta = 0.1, 1 | REPORTED: 1.096 +- 0.005 and 0.991 +- 0.004 (N-weighted, k lambda -> 0) | REPORTED, and in agreement with the relativistic CE value of verify_g1 V1a (1.099, 0.993) at -0.6 and -0.5 se (post hoc) | C-20261119-152752-0ffa031, C-20261119-155433-a287f9c, C-20261119-150347-e100007; C-20261120-222954-b1a06ed, C-20261120-223203-b38a7d7, C-20261121-030328-e3ffc6d |
| T7 collisionless check (k lambda = 100) | PASS (max z 3.0, 3.1, 2.9 < 4) | PASS | C-20261119-150358-3805fd5; C-20261119-152845-017d186 |
| T8 dt, pmax, dx | PASS: changes between the two finest values -0.52, -0.006, -1.04 percent (< 2) on one card seed of 4e6; trends reported (finding 8) | PASS | C-20261119-150335-73fd40f; C-20261120-222624-cae43d6, C-20261120-223321-3d088d4; processor cross-check C-20261120-222620-6ecac07 |
| T8 part 2: T2(b) at max P 0.56 without sub-cycling | PASS; "the deficit is reported": there is none (1.000025 +- 0.000041 of the analytic rate) | PASS | C-20261119-150358-66295f7; C-20261119-151044-a584069 |

So T6 PASS, T7 PASS at theta = 0.003 (REPORTED at 0.1 and 1, as TESTS.md asks), T8 PASS:
the T6-T8 part of C6, which the G1 stage report listed as the missing part, is met. Limits
the lead should weigh: T8 rests on one card seed with one particle file for its seven
variants (margin to 2 percent: 1.6 sd for dx); T6(b) checks kappa to a few percent only;
the comparison with V1a is post hoc and V1a is unreviewed.

### The collisions-2 card executable for these tests

Core's reading (`scratch/core/exe/core_collisions-2/READY`, section "Card", and
`CARD_TESTS.log`, note of 2026-11-20; `git show core/collisions-2:tracks/core/JOURNAL-coll2.md`,
entries "2026-11-19 14:30 UTC", part D, and "2026-11-20 22:05 UTC", R150): with the options
absent the card executable f46f159 is not byte-identical to the release card executable in
collisional runs, but tests and accepts the same pairs in every step, with momenta within
2.1e-14 of max(1, |u|) (run core-20261119-141059-f3ccf56), and over 1200 steps of the Z4c
cluster it collides the same pairs as the release with the lapse within 7.8e-15 (analysis
core-20261120-220420-63419ab); core calls it usable for runs [JUDGEMENT of core: the card
compiler builds the changed collision kernel differently]. READY lists heat conduction
(T6-T8) as not tested by core. This package's checks on the card, which core did not do:
(1) every one of the 26 card cases started from the intended particle file (first snapshot
bit-identical, runs C-20261120-222547-e1c0353, -222846-029c453); (2) the card seed at
theta = 0.003 lies within 1.8, 1.2, 0.3 standard errors of eight processor seeds at
k lambda 0.1, 0.2, 0.4 (C-20261120-223203-b38a7d7); (3) the 15 card seeds of the three
temperatures show no common offset from the processor seeds (mean z -0.29 +- 0.26); the
excess scatter at k lambda 0.1 appears in processor seed pairs as well
(C-20261121-025837-8b5b9ee); (4) eps 0.05 on the card agrees with eps 0.2 (z -1.6, +0.5);
(5) T8 on the card meets its criterion with n_trunc = 0. Within the 0.3-1 percent
resolution of these statistics the card executable gives the same conductivity as the
processor executable; nothing here makes it suspect for heat conduction. This does not sign
for core: the byte-level difference core describes lies far below what these tests resolve.

## Pending runs

None. Both card jobs are reduced and closed (A: reduction C-20261120-221630-fd17a2d, B:
C-20261120-222329-3a77ad6; every case has reduced.npz, case.json, summary.json and its first
and last snapshot); no case was lost or left unreduced. The T8 cases lost on the processors
in wave 3a were rerun in C-20261119-162353-7985a9a. Run C-20261120-223424-f6ba00a was
registered at the pause of 2026-11-20 22:34 and never started; it was rerun as
C-20261121-025837-8b5b9ee.

## Requests

To the lead of C-sidm (TESTS.md is the lead's; nothing here loosens a criterion):
- T7: fit the entropy combination A_S, not the number mode A_N (sound waves bias A_N by
  +5 to +43 percent, finding 2); allow eps = 0.2 with the nonlinear-reference correction
  (finding 3; eps 0.05 on the card agrees with it, P-eps); the pass interval [0.99, 1.06]
  is met in every form (1.019-1.025; 1.000-1.018 with the cell-size bias removed).
- T7 at theta 0.1 and 1: the "no reference" note can now cite the relativistic
  Chapman-Enskog values of `../verify_g1/` V1a (run C-20261120-222423-519f12b; 1.099 and
  0.993 kappa_1); measured 1.096 +- 0.005 and 0.991 +- 0.004. Whether to turn them into
  pass criteria is the lead's call (V1a is unreviewed; see the kb request).
- T6(b): state the nonlinear reference (the literal statistic of a perfect kappa_1 code is
  0.967, i.e. the interval [0.95, 1.10] means kappa/kappa_1 in [0.982, 1.138]), the
  one-dimensional box (transverse lambda x lambda), and that the test checks kappa to a
  few percent only (sound ringing, early kinetic lag; a compressible reference would be
  needed for more).
- T6(a): replace "consistent with a deviation proportional to t/t_coll" by the observed
  scaling with the square root of the collided fraction (stochastic scatter), or ask for
  many seeds if a systematic part is wanted.
- T6(c): at lambda/L = 0.1 the step rings acoustically; no diffusive curve applies there.
- T8: the "deficit without sub-cycling" is zero while no pair exceeds P = 1 (finding 5).
  The criterion was met on one card seed; the dx trend (finding 8) is real but its form is
  not fixed.
- Open, for G2 [TO VERIFY]: whether the zero-cell-size conductivity at theta 0.003 is 1-3
  percent below the relativistic CE value (finding 7). It would take a cell-size series at
  k lambda 0.1 and 0.2 (dx = lambda/8, /4, /2, plus dt = 0.05 t_coll at lambda/8) with two
  card seeds of 4e6 each: about 12 cases, roughly 0.3 card-hours by the 873 s that job A
  took for 11 cases of this size [JUDGEMENT]. Not submitted (card cap of this package: 0).
- Card time used by the package: 0.516 card-hours of allocation (jobs A and B; 1.84
  reserved at submission). No job pending.

To core:
- Optional, for long box runs: an in-situ particle reduction (sums of M w cos(j k x),
  M w sin(j k x) for w in {1, W - 1, W, u_x}, j = 1..3, every n cycles) would replace 72 B
  per particle per snapshot; the card runs of this package wrote about 98 GB of snapshots to
  keep about 30 numbers per snapshot.
- For information: on the processors under load the operator cost 1.2e-6 s per tested
  pair (`coll_energy = particle`; `cell` 20 percent cheaper), 3.5 times the wave-2 figure.
- For information: the collisions-2 card executable reproduces the processor conductivity
  within the resolution of T7/T8 (section "The collisions-2 card executable"); heat
  conduction can be moved from "not tested" in READY to "tested by Track C" if core agrees.
- `docs/FORMATS.md` line 123 omits the trailing 8 N bytes of proper times that
  `athenak/src/particles/nrpic_io.cpp` lines 942-944 write after the species of a snapshot
  (snapshot size 32 + 72 N bytes; JOURNAL 2026-11-20 22:26).

To kb:
- The hard-sphere conductivity beyond the first Chapman-Enskog approximation (Chapman &
  Cowling; 1 + 1/44 at second order [BACKGROUND]) and the relativistic one (Cercignani &
  Kremer) are still not in the corpus; they would check V1a (whose theta = 1e-4 and
  non-relativistic order-4 values differ by 2.1 se, 1.0233 against 1.0267).
- DSMC discretisation errors of transport coefficients in cell size and time step
  (Alexander, Garcia & Alder 1998; Garcia & Wagner 2000; Hadjiconstantinou 2000
  [BACKGROUND, not re-read]) for the form of the dx trend of finding 8.
