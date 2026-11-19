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
