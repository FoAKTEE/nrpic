# Journal of the G1 verifier (package verifier2, wave 2b, 2026-11-19)

Fresh-context verifier for gate G1, checklist items C18 (recompute the note's ledger, the
Newtonian-mode results, the analytic-criteria checks and the expanding-ball comparison from
the registered raw outputs with my own code) and C11 (data-flow schematic). Read before
writing this entry: CLAUDE.md, CHARTER.md to "Owners", decisions 0010 and 0016, the brief
at S1 (335-365) and the track sheet (708-725), stage/G1/CHECKLIST.md (to know what C11 and
C18 ask), the note (note/main.tex and its tables), the READMEs of note/, criteria/, newton/,
runs_ball/, newton/SCAN.md section 7, and the paper sources at the locators the note cites.
Not read before the verdicts: REVIEW-wave2.md, STATUS.md, HANDOFF.md, the journals.

## Entry 1, 2026-11-19T14:10Z: predictions before any of my code runs

Method: one script per area under `verifier/`, sharing nothing with the track's code except
the raw files it reads (run outputs, the data-set table, the AthenaK histories and
trajectories, the paper sources). Every input file is checked against the `sha256sums.txt`
of its run where the run wrote one.

**P1 Threshold landscape (ledger block 1).** From MDPBH.tex:918 coded myself, hhat(0.2,0) =
0.4517 (refuted if the fourth digit differs). With delta_crit = (3/20)(12 pi)^(2/3) and the
mean measure deltabar = 12 mu/(5 e_E) (note eq. 2), the top-hat amplitude for a collapse at
t_end is mu_fd = (5 e_E/12) delta_crit (t_end/t_H)^(-2/3): 0.089, 0.048, 0.035, 0.019 for
t_end = 100, 250, 400, 1000 (refuted if any differs in the printed digits). The largest mu
of the ball from the Hubble condition R_b H_i = 0.9 and a start contrast <= 0.3: 0.069,
0.031, 0.017 (mean) and 0.0253, 0.0113, 0.0063 (central) for R_b = 2, 3, 4 r_m. Critical
dispersions sqrt(0.3) = 0.548 and 1.5 from 2507.18312:542 / 2211.13950:715 with sigma_v R
conserved. Slope of the read-off times: about -1.3 from a log-log fit over mu <= 0.15.
Median ratio of read-off to top-hat time for mu <= 0.15: I expect it NOT to be 0.86 if the
median was taken over all six points (the mu = 0.3 point has ratio near 1.5); refuted if my
median over the five points mu <= 0.15 is 0.86.

**P2 Criteria rows of the ledger.** Coded from the paper sources: R1 = (36/pi) e
E(m)/(1+3e)^2 = 1.084 at e = 0.2; R2 (2508.10070:593-598, sigma_h cancels) = 1.452; R3 =
(0.4 sigma_H)^(2/3) = 0.0252; R8 = e^(-0.4)(0.01/e)^(0.4) = 0.0712; R9 = (2.5 sigma_H)^(0.4)
= 0.229; R4 = 0.01 for a_end/a_H = 100. Particle threshold 12/5 x 0.045 = 0.108. Refuted
if any of these differs from the ledger in its printed digits. Ledger label of this row:
eight names for six values (I expect a label defect, not a value defect).

**P3 Check counts.** results.json of A-emd-pbh-20261115-130256-a7374a4 holds 37 checks, 33
passed, failing T1.2b, T2.2d, T2.4a, T2.4c (refuted otherwise). For the wave-2 runs
-161813-6c820fb and -163358-9b2d048 the README claims 40 checks with 3 failures (T2.6a-c)
and 17 with 0 failures; I expect the union (T2 from the later run) to give 0 failures.
Independent values: T4.1 a_max delta = (3/20)(6 pi)^(2/3) = 1.0624; T1.1 = 1.

**P4 Constraint orders.** The orders printed in the ledger (2.00; 4.00; 1.99; 3.90; 4.00;
4.00; -0.50; 3.98; 3.94) follow from the norms in convergence.json as log2 of successive
ratios at the finest pair (refuted if any differs by more than 0.01, or if the ledger's
order comes from a different pair than the one it says).

**P5 Exact solution of data set 2t, from the table alone.** Rebuilding R = psi^2 rbar,
1+2E = (dR/drbar)^2/psi^4, v = -KT R, m = R(v^2 - 2E)/2 from the .tab file of run
A-emd-pbh-20261115-130609-947c898 and solving the cycloid myself: M = 1.0096, rest mass
1.0159; core tau_ta = 16.894, R_max/R_i = 1.340; core crunch 44.454; core edge (R_i = 2.4)
trapped at 44.381; the first trapped sphere at tau = 44.349 just outside the core edge
(R_i near 2.7), m_AH/M near 0.08, areal radius 2 m_AH near 0.16. Refuted if a time differs
by more than 2e-3 or a mass by more than 1e-3 relative. Conformal-time coordinate times
from t = int a_i/a dtau along the core: 13.82, 49.51, 54.96 (refuted beyond 0.02). Exterior
K against -(3/2) sqrt(2M/R^3): agreement to 1e-12 or better away from the matter edge.

**P6 Measured cost.** Sum of "cpu time used" over the segments of runs/jeans/n1e4_v19:
19475 s = 5.41 card-hours; cycles from the logs 25600, so 0.761 s per cycle (refuted if
the cycle count in the logs is not 25600).

**P7 Newtonian mode (newton/).** From newton.newton.hst (second-moment tensor, centre of
mass) with semi-axes A_i = sqrt(5 lambda_i/M) and my own references (cycloid for the top
hat; isolated homogeneous ellipsoid A_i'' = -M A_i R_D(A_j^2, A_k^2, A_i^2) for the scan):
top hat at 128^3 with 2.7e5 particles: t_ta +7.2e-4, R_max +4.3e-4, t(R = 0.25 R_max)
+8.4e-4 (each within +-1.5e-4 of the claim, since my estimators of the extremum differ);
order about 2 in the mesh. Scan: first collapse along the predicted axis in every case,
t_1 within 2e-4 to 7e-4 for e = 0.05-0.3 and about 1.5e-3 for p = -e; my ellipsoid
reference times equal theirs (ball.json) to 1e-6. Hoop amplitudes h_1 delta_L near 0.3597,
0.5925, 0.8547, 0.9685, 0.9194, 0.8636 (to 1e-3). Energy error at the first collapse 1e-3
to 3e-2 (the README says so). Refuted if a time differs from the claim by more than 3e-4
absolute in relative error, or an axis is wrong.

**P8 Expanding ball (runs_ball/).** From ball.traj.bin and ball.trajmet.bin with my own
reader (areal radius r sqrt(gamma_perp), proper time int alpha/W dt) and P5's exact
cycloid per tracked particle: SR-1 dx = M/2 mean turnaround error near -0.022 M, core
max |R/R_ex - 1| at tau = 16.9 near 6.2e-3; dx = M 5.6e-2; dx = M/4 7.6e-4 and turnaround
-0.0125 M. SR-2: +0.043 M (M/2), +0.031 M (M/4), core max 7.5e-3 (M/2), 2.1e-2 (M).
Apparent order between M/2 and M/4 of 3-4.3. Refuted if my numbers differ by more than
20 per cent of the claim (estimator differences), or if the sign differs.

## Entry 2, 2026-11-19T14:40Z: outcomes (run A-20261119-142905-c813c01)

Development executions of the four scripts, unregistered, wrote only to
`scratch/A-emd-pbh/tmp/verifier2/dev_*` while I fixed my own bugs (listed below); the numbers
quoted here are those of the registered run A-20261119-142905-c813c01 (commit c813c01,
`verifier/run_all.py`, 4 cores, all four parts exit 0; 24 output files checksummed).

Bugs of mine found during development (none changes a verdict of the registered run): central
shells of the table with one-sided differences (fixed by the homogeneous-core scaling); noise
shells with E ~ 1e-13 counted as bound; the spindle's line singularity stopped my ellipsoid
integrator without an event (now recorded at the solver's stop, 7e-10 from the track's
reference); p = -0.0 counted as negative; card cases' ball.json lives in the prepare run
-153424; wrong background mass in my first top-hat check (0.5 H^2 a^2 instead of a^3).

**P1 outcome.** hhat(0.2,0) = 0.451747 [held]. mu_fd 0.08866, 0.04813, 0.03518, 0.01910
[held]. Ball limits 0.0688, 0.0306, 0.0172 and 0.02531, 0.01125, 0.00633 [held]. Critical
dispersions 0.5477, 1.5 [held]. Slope over mu <= 0.15: -1.3123 [held]. Median ratio over the
five points mu <= 0.15 is 0.8428; the printed 0.86 is the median over all six (0.8646):
prediction held, the ledger row is WRONG as labelled.

**P2 outcome.** R1..R4, R8, R9 at e = 0.2 equal the ledger and scan_summary.json to 2e-16
[held]; the ledger's label has eight names for six values [held: label defect].

**P3 outcome.** 37 checks, 33 passed, failing T1.2b, T2.2d, T2.4a, T2.4c in both wave-1 runs;
wave 2: 40 checks with T2.6a-c failed, then 17 of T2 with none failed; union 41 of 41 [held].
My own Ebar = 1.1816597, c = 0.0555549716 (rounds to 0.05555, the paper prints 0.05556);
1707.03595 prefactors 1.9213e-7 and 3.2484e-14 (3.2437e-14 with Ebar = 1.182): the track's
explanation of T1.2b and T2.2d is right.

**P4 outcome.** All nine orders reproduced to the printed digits from the norms of
convergence.json, each from the finest pair [held].

**P5 outcome.** From the table alone: M = 1.00959, rest mass 1.01590, tau_ta 16.8938,
R_max/R_i 1.33980, first trapped sphere 44.3493 at R_i = 2.7418 with m = 0.08051 (2m =
0.1610), core edge trapped 44.3815, crunch 44.4542, m at the crunch 0.09602; conformal-time
coordinate times 13.823, 49.506, 54.964 [all held]. Two findings I had not predicted: (a) the
masses are in code units (nominal mass 1), not in units of the total M = 1.0096 the labels
name (m/M_total = 0.0797, 0.0951); (b) the shells of the surface taper (6.5 <= R < 9.43) do
not share the bang time (10.667 to 13.588), contrary to the note's "a common bang time for
every shell". The geodesic step bound is reached at tau = 42.36 (all shells; 42.38 core
only) against the claimed 42.30: the track's speed R_i/R omits 1/psi^2 [held within 0.1].

**P6 outcome.** 19475 s over 13 segments = 5.4099 card-hours, final cycle 25600, 0.7608 s
per cycle [held]. (My side number 0.778 s per cycle in the run output divides by the 25031
cycles between the first and last cycle lines of each segment; the log prints every 100 cycles,
so that count is short at each segment end and the side number has no meaning.)

**P7 outcome.** Top hat 128^3: +7.18e-4, +4.19e-4, +8.19e-4, +2.66e-4 against +7.16e-4,
+4.31e-4, +8.39e-4, +2.59e-4 [held, within my estimator spread]; doubling factors 4.0-6.1
[held]; 2.1e6 vs 2.7e5 particles 1.2e-5. Energy 9.5e-5 is reproduced only with the track's
normalisation |W_0| and interval up to t(R = 0.25 R_max); relative to |E_0| it is 2.2e-4.
Scan: axis right in 14 of 14; t_1 +1.6e-4 to +6.3e-4 with my +-3-record vertex (the e = 0.05
point 1.3e-4 below the claim's 2.9e-4); spindle +1.49e-3; my ellipsoid equals ball.json's to
3e-9. Prediction "within 3e-4 absolute" held. Axes and hoop ratio: 1.2e-3 and 6.1e-4 when
evaluated at the reference t_1 as the track does; 1.5e-3 and 8.6e-4 (opposite sign) at the
measured t_1. Hoop amplitudes 0.3597 ... 0.8636 reproduced exactly with the track's
estimator, to 6e-4 with mine [held]. Energy 1.1e-3 to 9.3e-3 and 3.0e-2 with |W_0| [held].

**P8 outcome.** SR-1: -0.0224 M (M/2), -0.0126 M (M/4), core max |eps| 5.57e-2 (M),
6.22e-3 (M/2), 7.61e-4 (M/4) [held]. SR-2: 2.08e-2, 7.51e-3, 3.56e-4 [held]; turnaround
+0.0434 (M/2) and +0.0307 (M/4) [held] but ONLY with a three-point vertex: with fit windows of
+-2, 3, 5 records the M/4 value falls to +0.0245, +0.0156, +0.0088 and the M/2 median is
-0.12 to -0.005, while SR-1 does not depend on the window. Not predicted: the SR-2 turnaround
error is not a robust number. Apparent orders 3.03 (SR-1) and 4.40 (SR-2) [held]; the M/4
runs use a box of half the size, so this is not a pure mesh refinement. Breakdown of SR-1:
first non-positive metric determinant at t = 32.875 (M/2) and 30.25 (M) [held]. Central
lapse of SR-2 at the core turnaround 1.862 (M/2), 1.812 (M) against the exact 1.340 [held].

Figures looked at (stage/G1/figs/): fig_v_ledger (h-hat against the read-offs, collapse times,
tau_AH(R_i) with the first trapped sphere, coordinate speed of light), fig_v_criteria,
fig_v_newton, fig_v_newton_scan, fig_v_ball; note/figures/schem_dataflow.png. Paper figures
hcont.pdf and alpha.pdf of 2609.14218 rendered into scratch (not committed) and looked at:
the read-off values of the track (h-hat at p = 0; collapse times 24, 46, 74, 106, 144, 199
t_H) are consistent with them at reading accuracy.

## Entry 3, 2026-11-19T14:55Z: comparison with the track's review; package closed

After committing VERIFIER.md sections 1-3 (commit 37240f3) I read `../REVIEW-wave2.md`,
`REVIEW.md`, `OPEN.md`, `STATUS.md`, `CHECKLIST.md` and runs_ball/JOURNAL.md entry 6.
Differences, in VERIFIER.md section 4: (1) the SR-2 turnaround "R2 FAILS" rests on a
three-point vertex that the lead's independent check also used; with wider windows it is
undecided; (2) STATUS T3 / CHECKLIST C8 "14 scan points within 2.2e-4 to 6.3e-4" is wrong as
written; (3) the note's ledger had no check before: findings 1-4, 7 are new; (4) the
criteria state in STATUS T2 and the note is the wave-1 one; (5) three versions of the SR-1
breakdown time, each a different criterion; (6) items the lead left unconfirmed that I
confirm (card points, crossing energy, t_2); (7) items the lead checked and I did not
(periodic box, L4, LTB, cost, horizon statements). No prediction of entry 1 changed.
C11 schematic: run A-20261119-143347-37240f3, looked at. Card-hours used: 0.
