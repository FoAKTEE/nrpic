# Blind verdicts of the G1 verifier of C-sidm (criterion C17)

Written before any claim of the track was read: not read were stage/**, PLAN-wave3.md, the
track's STATUS/HANDOFF/RISKS/JOURNAL, any package JOURNAL other than this one, the Results
sections of package READMEs, the note, results/*.json and the analysis outputs of the track's
runs. Read were: the test definitions (collide/TESTS.md, collide/SPEC.md definitions), the
interface texts, docs/FORMATS.md, the run manifests, the raw run outputs (decks, histories,
snapshots, case.json, reduced.npz), the model files (JSON fields including their `role`
labels, particle files) of two model runs, and the papers in kb-data. Exposures that could bias
me are listed in JOURNAL.md entries 7 (one row of core's own T12 claim in the interface text)
and 9, 12 (names and role labels of the track's model files, seen before or while I compared
with them; my thresholds had been computed before the role labels were read).
Method details, predictions and outcomes: JOURNAL.md entries 0-16. All code in this directory;
every computation a registered run (manifests under tracks/C-sidm/runs/<run_id>/).
Labels: [VERIFIED] measured in a registered run of this package or read at a locator;
[JUDGEMENT] own reasoning; [BACKGROUND] standard result not re-derived; [TO VERIFY] open.

## V1 Heat conduction at the short-mean-free-path end (C-pre-1)

| Quantity | My value | Test definition | Verdict |
|---|---|---|---|
| kappa_1 of hard spheres (first Chapman-Enskog approximation, non-relativistic), kappa_1 sigma_tot/(k_B sqrt(k_B T/m)) | 2.0810 +- 0.0014 (Monte Carlo collision brackets) against 75 sqrt(pi)/64 = 2.0771 | T7 uses kappa_1 = 2.077 sqrt(theta)/sigma | [VERIFIED] formula and value; run C-20261120-222423-519f12b |
| Sonine orders 2, 3, 4 relative to order 1 | 1.02235(30), 1.02460(23), 1.02491(23) | T7 "about 1.025" | [VERIFIED] |
| Relativistic (Eckart, Moller flux) at theta = 0.003 | 1.0077(13) (order 1), 1.0296(10) (order 4) times the non-relativistic kappa_1 | target of T7 at 0.003 | [VERIFIED] |
| T7 isobaric mode, kappa/kappa_1 extrapolated to (k lambda)^2 = 0 | 1.0090 +- 0.0038 (T7 estimator on the entropy amplitude; error from the seed scatter; 4, 8, 8 seeds at k lambda 0.1, 0.2, 0.4); 1.0194 +- 0.0038 with the eps = 0.2 nonlinearity removed by my nonlinear isobaric reference | [0.99, 1.06] | PASS (both readings) [VERIFIED] run C-20261120-223130-6742500 (first evaluation C-20261120-222754-14bd23d, same numbers) |
| T6(b) temperature step, lambda/L = 0.01 | chi/chi_1 = 1.051, 1.086 (seeds 1, 2; linear square-wave form of the definition, chi_1 at the final temperature), mean 1.068 +- 0.018; nonlinear isobaric reference f = 1.044 +- 0.017; sound removed 1.049 +- 0.017 | [0.95, 1.10] per seed | PASS [VERIFIED] run C-20261120-223133-2f98a0e |

Method: formula kappa = (3/2) b sqrt(T/m)/sigma_tot with b = 25 sqrt(pi)/32 from Koda &
Shapiro arXiv:1101.3097 `sidm1.tex` lines 401-415 [VERIFIED read], reproduced by my own
variational Chapman-Enskog brackets (`ce_kappa.py`). Sound and entropy mode separated by the
entropy amplitude A_s = A_n - (c_v/c_p) A_p (number-density mode minus the adiabatic part of the
pressure mode; delta s = 0 for adiabatic sound), which removes the oscillation at c_s k that the
density mode carries (the density-mode estimator gives 1.04, 1.13, 1.79 at k lambda 0.1, 0.2, 0.4).
reduced.npz equals my own Fourier sums of the remaining snapshots to the last bit.
Remarks: (i) the runs use eps = 0.2, T7 prescribes 0.05 (a deviation of the runs from the test
definition; corrected by my nonlinear reference, effect +1 percent); (ii) only theta = 0.003 of
T7 was checked (0.1 and 1 are "reported" in T7); (iii) the corrected value 1.019(4) lies 1.1
percent (2.7 sigma) below the converged relativistic Chapman-Enskog value 1.030 at theta =
0.003, unexplained, inside the pass interval [TO VERIFY]; (iv) T6(b) has two seeds only, so its
error is crude; the linear form of the definition is 2.4 percent above the nonlinear fit, the
bias of a linear form at a factor-2 contrast [JUDGEMENT].

## V2 Collision rate and conservation in the flat box (T1, T2)

Runs C-20261115-165500-c67e036 (release CPU) and C-20261119-141806-af19c1c (collisions-2 CPU,
coll_energy = particle), 16 collisional cases each (theta 1e-3, 0.1, 1, 10; plain and
sub-cycled; seeds 1, 2), two collisionless controls. My run: C-20261121-074926-5d9ae56.

| Quantity | My value | Criterion | Verdict |
|---|---|---|---|
| Own <v_Mol>(theta): two-dimensional quadrature in rapidities against 4 K3(2 zeta)/(zeta K2^2) | agree to <= 5e-14 at theta 1e-3 ... 10 | reference | [VERIFIED] |
| T2(a) z of sum n_coll against sum sum_P | \|z\| <= 2.10 (32 cases) | \|z\| <= 4 | PASS |
| T2(b) mean sum_P per step / ((1/2) N rho_0 sigma <v_Mol>(theta_s) dt) - 1 | \|rel\| <= 9.6e-5 (32 cases) | <= 0.5 percent | PASS |
| T2(b) 4-standard-error clause | z <= 2.92 with the step-to-step standard error; with my stricter batch-mean error z = +4.21 (theta 1e-3 plain s2) and -4.55 (theta 1 sub s2); tested pairs against the sample's own all-pairs mean: \|z\| <= 2.26 | 4 se; TESTS 2a: below 1e-4 compare with the sample's pair mean | PASS by the definition and by the 2a reading; the batch-error excess is the 1e-4 sample effect 2a names [JUDGEMENT] |
| T2(c) <W> start to end; KS of \|u\| at the end | sum M W identical (exactly rounded sums); KS p 0.095-0.985 | constant within 4 sigma; MJ | PASS |
| T1 per-step \|dE\|/sum_MW and max\|dP_i\|/sum_MW | <= 1.1e-7 and <= 3.6e-8 of the bound 1e-14 sqrt(n_coll + 1) | below the bound | PASS |
| T1 n_trunc; coll_energy = particle in flat space | 0; n_noroot = n_balance = 0, max_dlam = 0 | 0 | PASS |
| Release and collisions-2 executables | identical n_tested and n_coll in all 200 steps of all 16 cases, sum_P to 8.9e-16 | (consistency) | [VERIFIED] |
| Collisionless controls | end momenta bit-identical to the start | | [VERIFIED] |
| T1 drift over 1e4 steps | not testable on these 200-step runs (see V5) | < 1e-11 | see V5 |

## V3 Static homogeneous curved metric (T12)

Run C-20261119-143049-0cf699a (alpha0 = 0.8, psi0 = 1.1 from the deck; flat twins with box
psi0^2 and step alpha0 dt). My run: C-20261121-075256-2084cb5.
Expected [JUDGEMENT, own derivation]: collisions per coordinate time and coordinate volume =
alpha0 psi0^6 (= 1.417249) times the flat rate per unit time and volume at the same proper
density and temperature; per step (1/2) N rho_p sigma <v_Mol>(theta_s) alpha0 dt with rho_p =
sum M/(psi0^6 V_c), theta_s from <W> with W = sqrt(1 + u_i u_i/psi0^4).

| Quantity | My value | Criterion | Verdict |
|---|---|---|---|
| Sum n_coll (200 steps) against my expectation | z = -1.02, +0.27 (theta 0.1, seeds 1, 2), -0.67, -0.61 (theta 1), -1.02 (coll_energy = cell); mean sum_P within 9e-5 | within 4 sigma | PASS |
| Rate per coordinate time and volume, curved / flat twin | 28203.7/19900.3 = 1.417249 = alpha0 psi0^6 (identical counts) | alpha0 psi0^6 | PASS |
| Pair counting: sum_W of cycle 1 against my count from the snapshot (one straight push) | 2.5e-13 ... 4.1e-13 relative (9 cases) | (proper volume psi0^6 dV, proper time alpha0 dt) | [VERIFIED] |
| Twin identity | identical n_tested and n_coll in all 200 steps (4 pairs); end momenta u_i/psi0^2 within 2.5e-13, positions within 4.0e-13 | TESTS 2a sharp form | PASS |
| Conservation (T1 for covariant M u_i) | per-step defects <= 3.6e-7 of the bound; snapshot sums of M u_i constant to 6.2e-17 of sum M W; n_noroot = n_balance = 0; max_dlam 5e-14 | as T1 | PASS |
| `cell` against `particle` | identical counts, end momenta within 1.3e-14 | | [VERIFIED] |

## V4 Equilibrium thresholds with my own spherically symmetric Einstein-Vlasov solver

Own solver `v4_ev.py` (static Einstein-Vlasov, Schwarzschild coordinates, f = (exp((E0 -
E)/T_inf) - 1)_+, T_inf = b E0; b = 1 is the King model of arXiv:2009.08163 `paper.tex` line 635,
b = 0.1 the F21 family of arXiv:2108.11967 `main.tex` lines 113-144); radial pulsation from
Chandrasekhar's equation as printed in F21 (lines 202-204), in variational form, solved both with
F21's trial function xi = r e^Phi and exactly (finite elements, converged in J = 100/200/400).
Runs C-20261121-080313-84094f1 (thresholds; the earlier C-20261121-080152-b8d0acd failed at its
figure, same numbers) and C-20261121-080720-dbcd7ff (model files; C-20261121-080633-8ee41f7 had
a sign error in my sample check only).

| Quantity | My value | Reference | Verdict |
|---|---|---|---|
| Check of the solver: F21 Table 1 (b = 0.1), five rows | M, E_rest, eps, Z(0), rho(0), p(0), v(0), <gamma>, gamma_cr within 1.3e-4; R within 0.25 percent (their R grid of 1e-3) | F21 main.tex lines 490-503 | [VERIFIED] |
| (a) King: y0 at the maximum of E_b = (N - M)/N | 0.334032 (E_b,max = 0.0355886); first zero 0.784518 | 0.334, 0.784 (2009.08163 line 953) | agrees [VERIFIED] |
| k = 0.5 polytrope E_b maximum (extra) | 0.297661; zero 0.693022 | 0.298, 0.693 (line 954) | agrees |
| (b) King, onset of radial-pulsation instability with Juttner Gamma_1(T) = 1 + 1/c_v(T) | T = Tolman temperature b e^y: exact y0 = 0.039192 (Z(0) = 0.0558), trial function 0.039350; T = energy-matched temperature (<E>_MJ(T) = rho/n): exact y0 = 0.32143 (Z(0) = 0.4910), trial 0.34033 | none published | depends on the definition of the temperature: see below |
| (b') King with F21's gamma = 1 + p/u | exact y0 = 0.37206 (Z(0) = 0.5757), trial 0.39612: after the E_b maximum | | [VERIFIED] |
| (c) F21 b = 0.1 turning points | E max Z(0) = 0.08913, B max 0.29966, eps max 0.54041 (eps = 0.035179) | 0.087, 0.297, 0.548 at their w(0) grid points; eps_max 0.0352 (main.tex lines 280, 286) | agrees within their grid |
| (c) F21 adiabatic criterion with their gamma and trial function | Z(0) = 0.75001, w(0) = 4.0511, v(0) = 0.5662 | 0.750, 4.05, 0.566 (lines 274, 276) | agrees |
| (c) same gamma, exact fundamental mode | Z(0) = 0.63482 (w(0) = 3.5871) | | the trial-function onset of F21 is late by 0.115 in Z(0) [VERIFIED]; F21's statement that the result is insensitive to xi (line 220) does not hold for these centrally condensed models |
| (c) Juttner onset in Z(0) | Gamma_1 at the energy-matched temperature: exact Z(0) = 0.533057 (y0 = 0.3755336), trial 0.5947; at the Tolman temperature: exact 0.41253, trial 0.43567 | | see below |
| Track's model files (18 King and b = 0.1 files of both runs) | my equilibrium at the file's y0 reproduces E_b, C, Z(0), M, R/M, M0/M, n_c, rho_c, p_c to <= 6e-10; k = 0.5 files to 2e-5 (my quadrature at the square-root edge); particle samples of three threshold models: isotropic-radius distribution equals my enclosed rest mass to D = 1e-5 = 1/N | | [VERIFIED] |
| Model-file values of the thresholds | King "threshold (computed y_max)" y0 = 0.33403216 (mine 0.33403217); b = 0.1 "E_b maximum" Z(0) = 0.5404129 (mine 0.5404128); "fluid onset, F21 gamma" 0.6348166 (mine exact 0.6348174); "fluid onset, Juttner Gamma_1 at the energy-matched temperature" 0.5330561 (mine exact 0.5330565) | | agree to <= 1e-6 |

Judgement on the definition [JUDGEMENT]: the truncated distribution is not thermal, so "the
local temperature" has two readings. The Tolman temperature b e^y is a parameter of the
distribution function; at the King onset it is 1.38 m while the mean kinetic energy corresponds
to a Maxwell-Juttner gas of 0.10 m. A collision-dominated gas relaxes at fixed number and energy
density to Maxwell-Juttner at the energy-matched temperature, whose Gamma_1 is the adiabatic
index of the fluid the SIDM core becomes; that reading is the physically appropriate one, and
with it I reproduce the track's onset to 1e-6. With the Tolman reading the onsets move to Z(0) =
0.4125 (b = 0.1) and y0 = 0.0392 (King). The verdict on V4(c) is therefore: Z(0) = 0.5331 for the
exact mode with Gamma_1(T_em), which I regard as the right definition; the alternative reading
must not be quoted without naming the temperature.

## V5 Relaxation, reproducibility, long conservation, unequal masses (T1 long, T3, T4, T9, T10)

Runs analysed: C-20261119-143041-f94e350 (T10), C-20261115-170741-248af65 (T1 over 1e4 steps),
C-20261115-170539-28432c3 (T3, T4), C-20261115-170814-8a54b43 (T9). My runs:
C-20261121-081036-0d6117b and C-20261121-081415-b8c9d29.
Own exact initial rate for T4 [JUDGEMENT, own derivation, JOURNAL entry 14]: d(theta1 -
theta2)/dt = sigma X (n2/c_v(theta1) + n1/c_v(theta2)), X = <v_Mol (W_b - W_a)/2> over MJ1 x MJ2
by two-dimensional quadrature (checked by Monte Carlo of 4e6 pairs, |z| <= 1.3).

| Quantity | My value | Criterion | Verdict |
|---|---|---|---|
| T10 final snapshots, MeshBlocks 1, 8, 64 and restarts at cycles 0, 37, 74 | bit-identical (whole files byte for byte); restart histories identical record by record; seed 8 differs in every momentum; MeshBlock variants: same counts, sums in the history differ in the last bits (summation order) | bit-identical | PASS (MPI ranks not tested: no MPI in that executable) |
| T345: B run's snapshot at cycle 49 against A's last snapshot (same start) | bit-identical in 4 cases | (extra) | [VERIFIED] |
| T1 drift of sum M W over 1e4 steps (exactly rounded snapshot sums) | 0.0 in both seeds; momentum sums 2.4e-18; per-step defects <= 8.8e-7 of the bound; n_trunc = 0 | < 1e-11 | PASS |
| T4 initial slope / my exact rate - 1 (quadratic fit over 0.15 tau_rel) | -0.37 +- 0.49, -1.74 +- 0.60, +0.03 +- 0.39, +0.88 +- 0.27 percent (theta2 = 1e-3 s1, s2; 1 s1, s2) | <= 4 se + 1 percent and <= 5 percent | PASS (4/4) |
| tau_rel of the generator | equals (theta1 - theta2)/(my rate) to 0.1 percent | | [VERIFIED] |
| \|v_a - v_b\| instead of v_Mol | 1.265 x the rate at theta2 = 1, 1.0007 at 1e-3 | TESTS T4 states 1.27, 1.0008 | agrees |
| T3 at 15 tau_rel: KS of \|u\| against MJ(theta_eq); <u^2/W> = 3 theta_eq; populations at theta_eq | KS p 0.084, 0.77, 0.99, 0.92; \|z\| <= 0.007; \|z\| <= 0.78 | p > 1e-3; 4 sigma | PASS (4/4) |
| T5 entropy | not checked (needs an entropy estimator with its own bias study) | | not checked |
| T9 classes M and 4M at the same theta at the end | \|z\| <= 1.16 (8 seeds) | 4 sigma | PASS |
| T9 KS of each class | against MJ at the theta of the initial energy: light class p = 1.7e-4 in seed 3 (all else >= 0.049); against the theta of the final energy: p >= 0.084 everywhere; own theta: p >= 0.089 | p > 1e-3 ("Maxwell-Juttner") | PASS of the shape; FAIL in 1 of 16 if the reference theta is that of the initial energy: the nanbu energy drift of seed 3 (+1.48e-4) shifts theta by the amount seen [JUDGEMENT] |
| T9 drifts of sum M W and sum M u_i, mean over 8 seeds | energy +5.3e-5 +- 2.2e-5 of the total (z = 2.42; positive in 7 of 8 seeds); momentum z = 0.40, 2.19, 1.08 | zero within 4 se | PASS (energy at 2.4 se: watch) |
| T9 refusal with coll_weights = equal | stops with "unequal rest masses (smallest and largest ...)" | error naming the masses | PASS |

## Summary of the blind verdicts

- V1 PASS: T7 kappa/kappa_1 = 1.009(4) by the test estimator (1.019(4) with the eps = 0.2
  nonlinearity removed) in [0.99, 1.06]; T6(b) chi/chi_1 = 1.051, 1.086 (seeds) in [0.95, 1.10].
  Open: corrected value 2.7 sigma below the relativistic Chapman-Enskog 1.030; runs at eps = 0.2
  instead of 0.05; T7 at theta 0.1 and 1 not checked.
- V2 PASS: T2 rate within 9.6e-5 of my Moller integral, T1 per-step defects 1e-7 of the bound.
- V3 PASS: T12 rate = alpha0 psi0^6 x flat, twin identity exact, pair counting to 4e-13.
- V4: King E_b maximum y0 = 0.334032 (paper 0.334); F21 b = 0.1 eps maximum Z(0) = 0.5404; fluid
  onsets: F21's gamma with the exact mode Z(0) = 0.6348 (F21's own trial-function value 0.750 is
  reproduced but is late); Juttner Gamma_1 at the energy-matched temperature Z(0) = 0.5331 (King
  y0 = 0.3214), at the Tolman temperature 0.4125 (King 0.0392). The model files agree with my
  equilibria to 6e-10.
- V5 PASS except the T9 KS clause read with the initial-energy temperature (1 of 16 fails; passes
  with the final-energy temperature); T5 not checked.
