# Journal of the G0/G1 verifier of Track C (wave 2)

Helper package `tracks/C-sidm/stage/G0/` (files `JOURNAL.md`, `README.md`, `VERIFIER.md`,
`verifier/`). Fresh reader: the summaries of the lead and helpers (STATUS, HANDOFF, REVIEW,
the package journals, the stage report) are read only after VERIFIER.md is written.
Sources of the claims: `tracks/C-sidm/scope/SCOPE.md` (the scoping text),
`tracks/C-sidm/gravothermal/README.md`, `tracks/C-sidm/equilibria/{README,CONVERSION}.md`,
`tracks/C-sidm/collide/{README,SPEC}.md`.

## 2026-11-15, predictions (written before any of my code ran)

Eight claims on which the plan rests, chosen from SCOPE.md sections 1-8. For each: what I
expect my own independent computation to give, and what would refute the claim.

V1 Monoenergetic family (SCOPE 2, 3.1; G1 criterion (a) is built on it). Own integrator of
   the areal-radius structure equations with closures I derive from f = K delta(E - E0)
   (not `python/nrpic/st_cluster.py`). Expect: the five rows of 2611.12831 main.tex:1024-1028
   reproduced to their printed digits (z_c to 5e-4, R/M to 1e-4, M0/M to 1e-6); first maximum
   of E_b/M0 at y_c = 0.6796 +- 0.0002 with E_b/M0 = 0.03606, z_c = 0.4553, R/M = 6.552; first
   zero at y_c = 0.3905 +- 0.0003; Newtonian limit y_c -> 1 equals the n = 1/2 polytrope
   (x_s -> sqrt(3/2) xi_1, v_s -> (3/2)^{3/2} omega_1 of my own Lane-Emden solution).
   Refuted if y_c,max differs by more than 1e-3 or a table row by more than its rounding.

V2 Truncated Maxwell-Boltzmann (F21) family, b = 0.1 (SCOPE 3.2; gravothermal README 2).
   Own solver that integrates f(E) directly over the local momentum (not F21's I-integrals,
   not `tmb.py` or `king_sequence.py`). Expect: F21 Table 1 rows w0 = 0.6, 1.9, 3.2, 4.0515,
   4.5 (main.tex:492-503) reproduced to 2e-4 relative in M^, E^_rest, eps, Z(0), v(0)/c,
   <gamma>, gamma_cr (R^ to the 1e-3 grid); eps maximum at w0 = 3.165 +- 0.002,
   Z(0) = 0.5404 +- 0.0005, eps = 0.03518; root <gamma> = gamma_cr at w0 = 4.051 +- 0.002,
   Z(0) = 0.750 +- 0.001. Refuted otherwise.

V3 King model of 2009.08163 is the F21 family at b = 1 with y0 = -ln(1 - b w0) (SCOPE 3.2),
   and its threshold y_max = 0.33403 (equilibria README). Derivation by hand; numerically my
   b = 1 sequence against a second, separate integration of 2009.08163's own equation
   (paper.tex:663-672, variable y) with their ansatz. Expect y_max = 0.3340 +- 0.0002,
   y_zero = 0.7845 +- 0.0003 (paper 0.334, 0.784, paper.tex:953) by both routes. Refuted if
   the routes disagree or either misses the printed values by more than half a unit.

V4 Exact fluid onset with F21's gamma = 1 + p/u: omega_0^2 = 0 at Z(0) = 0.6348 for b = 0.1
   (gravothermal README 3; SCOPE 1 uses the fluid limit as the Kn -> 0 anchor). Own
   Rayleigh-Ritz with a global polynomial basis (not the package's piecewise-linear FEM).
   Expect the zero at Z(0) = 0.635 +- 0.003, omega_0^2 < 0 at the trial root w0 = 4.0515.
   Limit check first: Gamma = 2, K = 100 polytrope, omega_0^2 = 0 at the mass maximum
   (rho_c = 3.18e-3) within 1 percent in rho_c. Refuted if Z(0) differs by more than 0.005.

V5 Knudsen number and the conversion to sigma/m (SCOPE 4; equilibria CONVERSION.md).
   Expect 1/(rho0_c H_c) = 166 (King b = 0.1 eps max), 199 (King b = 1 max), 270
   (monoenergetic max) within 1 percent in ADM units; the unit G^2 M_sun/c^4 = 1.097e-23
   cm^2/g; Kn_c = 4.5e-20 to 1.8e-19 for 5 cm^2/g at 200 M_sun. Also: CONVERSION.md's
   Kn sigma~ = 129.8 at the King b = 1 threshold with its own definition (Moller mean free
   path over H built on rho0). I expect the two packages' definitions of "Kn_c = 1" to differ
   by a factor of about 1.5 (my estimate from <v>/<v_Mol> ~ 0.77 and rho/rho0 ~ 1.16): if so,
   the claim "the Knudsen number is defined" is NOT CONFIRMED for the plan as a whole.

V6 Collision-rate reference <v_Mol>(theta) = 4 K3(2 zeta)/(zeta K2(zeta)^2) (collide SPEC 2).
   Own Monte Carlo over pairs from my own Maxwell-Juttner sampler (rejection, not `mj.py`).
   Expect agreement within 3 standard errors at theta = 0.01, 0.1, 1, 10; limits
   sqrt(16 theta/pi) and 1. Rerun of the package's pytest suite: 62 pass.

V7 Stiffness and cost numbers (SCOPE 7.1, 8). Expect: the "k = 32 partners within one mean
   free path" rule of 1101.3097 sidm1.tex:667-697 read at the source; from my rho0_c, H_c:
   N = 600-1600 macroparticles at Kn_c = 1, scaling Kn^-3; the five unit costs (s per M)
   recomputed from the AthenaK logs within 2 percent; the G3 total 156 card-hours follows
   from the stated assumptions. Refuted if the source does not state the rule or a cost is
   off by more than 5 percent.

V8 Source locators the threshold choice rests on (SCOPE 1, 3.3, 3.4, 6, 7): at least ten read
   at the source (2105.05556, 2009.08163, 2602.17487, 2108.11967, 2601.17117, gr-qc/0601112,
   astro-ph/0110561). Expect all to say what is quoted. Refuted for each misquote.

Reruns: the package scripts that support V1-V3, V5 (scope/scripts), the tests of
`gravothermal/test_tmb.py` and `collide/REFERENCES/tests`.

## 2026-11-15, outcomes

Development runs of the scripts were made in `scratch/C-sidm/tmp/verifier/` (not registered);
the registered run C-20261115-170630-1037f6a (commit 1037f6a) reproduces them. Reruns of the
track's scripts: run C-20261115-170716-e81ba08.

- V1 held. y_c,max = 0.6796102, z_c = 0.455290, E_b/M0 = 0.0360576, R/M = 6.55243; zero at
  0.3904461; Wu-Most rows within R/M 1e-5, M0/M 5e-7, z_c 4.3e-4; Newtonian limit approached
  linearly in 1 - y_c. Rerun of the scope script: 0.6796101.
- V2 held, with one overshoot of my tolerance: B^ at w0 = 4.5 differs by 2.4e-4 (> 2e-4);
  M^ and E^rest differ by 1.1e-4 there, so B^ = E^rest - M^ carries both; F21's fixed-step
  RK4 is the stated cause in the gravothermal package, my solver runs at rtol 1e-11. All
  criteria to the printed digits (eps max Z(0) = 0.54041, trial root Z(0) = 0.75001).
- V3 held: y_max = 0.334032, y_zero = 0.784518. The "second route" turned out to be the same
  ODE (y = ln W_c), so the numerical check is against the printed values only.
- V4 held: polytrope limit zero at rho_c = 3.1824222e-3 vs mass maximum 3.1824221e-3; onset
  b = 0.1 Z(0) = 0.63482, b = 0.5 0.57904; gamma = 5/3 0.77927. Unexpected: my omega_0^2 at
  w0 = 4.0515 is -3.315 against the package's -3.59; the factor 1.084 = 1/(1 - 2C) traced to
  the lapse normalisation in tmb.py:389 (surface lapse 1). Not an onset change.
- V4b (not predicted; fell out of V4): SCOPE.md section 1's fluid window ends at 0.635, not 0.75.
- V5 held as predicted, including the split: SCOPE's convention gives 1.530 times
  CONVERSION's sigma~ for "Kn_c = 1" (198.64 vs 129.82, King b = 1), 1.532 for King b = 0.1.
  After reading REPORT.md: the lead fixed a fourth convention (K = 168.9), not yet propagated.
- V6 held: pulls within 1.75 standard errors at seven temperatures; 62 reference tests pass;
  test_tmb 14 PASS.
- V7 held for N (597-1586 at Kn_c = 1) and costs (within 0.2 percent). Sub-steps: mine 1.6-3.4
  at Kn_c = 0.1 against the scope's 2-7; cause found in knudsen_costs.py (non-relativistic t_r,
  no lapse): conservative, so the claim holds as an upper estimate.
- V8: 35 locators read; one mis-described (2105.05556:581), the rest as quoted.
