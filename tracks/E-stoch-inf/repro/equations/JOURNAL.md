# Journal of repro/equations (helper of E-stoch-inf, batch R1, 2026-11-22)

Package: the equations of arXiv:2401.08530 (P0, `Stochastic_Inflation.tex` v2) and
arXiv:2512.14649 (P1, `PRD_v2.tex` v2) checked with sympy and short numerical tests, and the
map of every source term to `athenak/src/scalar_field/`. Sources are read-only under
`kb-data/raw/arxiv/<id>/v2/src/`; nothing of them is copied here. Locators are `P0:<line>` and
`P1:<line>` in those files.

## Entry 1 (2026-11-22 18:05 PST): predictions, written before any script ran

Read: P0:80-410 (sections II, III), P0:413-890 (IV, V), P0:902-1079 (appendices A-D),
P1:96-520, P1:602-791; `spec/SPEC.md` sections 1-5 (earlier work of this track, not redone).
Hand derivations made while reading (to be confirmed or refuted by the scripts):

(a) Linear equations and gauge families (script `check_linear.py`).
- A1. Linearising the nonlinear ADM left-hand sides of P0:128-169 on the metric of P0:177-193
  (alpha_b = 1, plane wave) gives P0:248 (Hamiltonian) exactly; the momentum constraint comes
  out as -(2/3) d_i[Delta chi + kappa - (3/2) M^-2 phidot delta phi], not -2 d_i[...] as printed
  (P0:249, P1:610; P0:249 also carries a stray "+-"). Refuted if the prefactor is -2.
- A2. The linearised K equation equals P0:231 only after the Hamiltonian constraint is used
  (direct linearisation gives 6 H kappa - 4 Delta Phi where P0:231 has 2 H kappa and
  -2 M^-2 delta rho moves into the matter term); so "match exactly" (P0:174) holds up to a
  multiple of the linear Hamiltonian constraint. Refuted if the difference is not proportional
  to the linear Hamiltonian constraint.
- A3. The trace-free K equation of P0:137-139 (and P1:344-348, P0:655-657) is trace-free only
  with gamma_ij in place of delta_ij in the term (1/3) alpha^|k_|k delta_ij; with delta_ij
  literally its trace is (1/3)(1 - a^-2)... nonzero for a != 1 on a solution. Refuted if the
  literal form vanishes on the solutions.
- A4. Every gauge family of P0 section III (pure gravity/comoving, fixed curvature/flat,
  Newtonian, uniform N, generalised synchronous; arbitrary gauge functions) satisfies all five
  linear ADM equations identically once R obeys the MS equation P0:277. Expected misprints:
  Newtonian delta phi (P0:350) misses a factor H in -a^2(B*-Edot*) (dimension); the Psi line
  (P0:351-352) has a stray comma (the two lines are one sum). The uniform-N definition
  delta N = Phi + k^2 E / 3 (P0:371) has the opposite sign of what P0:365 gives
  (delta N = -Phi - k^2 E/3); harmless for delta N* = 0. Refuted if the printed Newtonian
  delta phi passes.
- A5. P0:286-289 = P1:164-167 follow from the comoving gauge; Phi_B = Psi_B on MS solutions.
- A6. P1:267 prints dV/dphi = (-3 + eps1 + eps2/2) H phidot^-1; P0:914 gives
  sqrt(2 eps1)(-3+eps1+eps2/2) M H^2 = (-3+eps1+eps2/2) H phidot. Expect P1:267 to be a
  misprint (phidot, not its inverse). P1:258 term a^2 H^-1 k^2 R> is not dimensionless;
  expect k^2/(a^2 H) or a different term after the check of P1:251-259.

(b) Coarse-grained equations (script `check_coarse.py`).
- B1. Inserting R -> W R (time derivatives after the product, P0:577) with Psi_B> of
  P0:613/P1:201 into the linearised LHS: the field, K and trace-free K equations leave
  residuals sqrt(2 eps1) M S_R, -eps1 S_R and a^2 eps1 (delta_ij/3 - k_i k_j/k^2) S_R
  (P0:669-671, P1:299, 371-372), in all five gauge families and independent of the gauge
  functions; both constraints leave zero. Refuted if any residual depends on a gauge function
  or a constraint residual is nonzero at first order.
- B2. Negative controls: (i) flipping the sign of S_K (or of the S_R term in Psi_B>) makes the
  Hamiltonian residual nonzero at first order; (ii) setting Psi_B> = Phi_B> (P0:690) leaves
  gauge-dependent residuals and a constraint violation.
- B3. BSSN (P0:1022-1031, P1:685-691): with X_b = a^-2, S_A = a^-2 S_Kt, S_X = S_gt = S_Gt = 0;
  the BSSN K equation differs from the ADM one by the Hamiltonian constraint, so S_K^BSSN =
  S_K. Expected misprints in the printed BSSN system: "4 pi alpha (rho + S)" in a system with
  M^-2 (P1:654, P0:1001; should be M^-2 alpha (rho+S)/2), an extra alpha in
  alpha (R_ij - M^-2 alpha S_ij) (P1:655, P0:1002), and the momentum constraint
  D^j(gamma_ij K - K_ij) - M^-2 S_i (P1:667, P0:1014) has the geometric part with the sign of
  -(standard) so that with S_i = J_i it does not vanish.
- B4. Usual limit (P0 section IV E): Sigma = H(Sigma_pi + d_N Sigma_phi + (3-eps1) Sigma_phi)
  with the flat-gauge delta phi, delta pi equals sqrt(2 eps1) M S_R / H = S_Pi / H, i.e. the
  statement "Sigma = F^-1{S_Pi}" of P0:730 drops a 1/H that eq. (SImine) P0:708 keeps.
  The Friedmann line H^2 = V/(1 - pi^2/(6 M^2)) (P0:530, 710; P1:108) misses 1/(3 M^2).
  P0:718 (S_R in e-folds) holds exactly.

(c) Noise amplitude of P0 appendix D (script `check_noise_amp.py`).
- C1. With the Heaviside window and the integration by parts of P0:1050, the variance per
  e-fold is |(R' + (3-eps1-eps2) R)(k_sigma)|^2 (d k_sigma^3/dN)/(6 pi^2): the first line of
  P0:1071 follows. In slow roll (sigma = 0.01..0.1) the numerical MS solution gives the
  printed 3 H /(2 pi sqrt(2 eps1) M) to O(sigma^2, eps).
- C2. In ultra-slow roll the printed value fails: on super-Hubble scales R' = 3 R(1 + O(x^2)),
  so R' + (3 - eps2) R = -x^2 R/(1 - i x) with x = sigma: the amplitude is suppressed by
  sigma^2 relative to the printed one. The step P0:1063 ("d_N R negligible") neglects the
  time dependence of eps1 ~ a^-6. Without the integration by parts (using R W'' as a
  distribution is ill defined), no finite white-noise amplitude exists. Refuted if the
  numerical USR amplitude agrees with 3 H/(2 pi sqrt(2 eps1) M) within 10 per cent at
  sigma = 0.1.

(d) Langevin pair of section V (script `check_langevin.py`).
- D1. dN/dN_b = sqrt(1 + (alpha^2-1)(1 - eps1/3)) (P0:806) follows exactly.
- D2. The drift of P0:825-826 follows exactly from the field equation P0:812.
- D3. The Ito term: with Z = phidot/alpha and the noise alpha S_Pi in dZ (P0:812), Ito's lemma
  gives (1/2) f_ZZ (dZ)^2 = alpha^5 <S_Pi^2>/phidot^2, not alpha^3 (P0:817). The printed
  alpha^3 is what one gets if the noise in dZ carries no alpha, but then the noise term is
  alpha^2 S, not alpha^3 S. A Monte Carlo of dZ = (phidot/Z) sigma dW at alpha_0 = 2 will
  show mean(d alpha)/dt = alpha^5 sigma^2/phidot^2 (not alpha^3 sigma^2/phidot^2, a factor 4
  smaller). Refuted if the Monte Carlo agrees with alpha^3.

(e) Map to the code: read `athenak/src/scalar_field/` (read only); expected conventions from
the header of `scalar_field_noise.cpp`: G = 1 units (eps1 = 4 pi Pi_b^2/H^2), Z4c variables
(Khat, At_ij with chi), proper time, kicks multiplied by alpha_b.

## Entry 2 (2026-11-22 18:30 PST): outcomes, run E-20261123-022009-a53e7ee

Registered run `E-20261123-022009-a53e7ee` (processors, 1 core, about 5 minutes; commit a53e7ee;
`scripts/run_all.sh`; outputs in `scratch/E-stoch-inf/E-20261123-022009-a53e7ee/`). Before it,
unregistered smoke runs into `scratch/E-stoch-inf/tmp/` found two bugs of my scripts (background
started at N = 0 although the mode needs N < 0; USR background lost phi' below the absolute
tolerance, fixed by integrating ln|phi'|) and one wrong expectation of a control (b2, below);
no number of a smoke run is quoted. Figures looked at: `fig/fig_checks_matrix.png`,
`fig/fig_noise_amp.png`, `fig/fig_langevin_ito.png`.

Prediction by prediction:
- A1 confirmed: momentum constraint prefactor -2/3 (`a1 momentum: linearised = (1/3) printed`).
- A2 confirmed: linearised K LHS = P0:231 - Ham_lin.
- A3 confirmed: with delta_ij the trace is Psi k^2 (1 - a^2)/a^2.
- A4 confirmed: five families pass; Newtonian delta phi as printed fails, with H it passes;
  delta N sign as predicted. The Psi line of P0:351-352 read as one sum passes.
- A5 confirmed (GI relations in every family, Phi_B = Psi_B on MS solutions).
- A6 confirmed: P1:267 misprint (phidot, not phidot^-1); P1:258 term is k^2/(a^2 H) R>
  (`b6`; the corrected form was found after the prediction by testing the dimensionally
  natural candidate, `scratch/E-stoch-inf/tmp/cg2.py`, then added to the registered script).
- Not predicted, found: P0:911 Hddot = 2 eps1 (1 - eps2/2) H^3 is wrong; Hddot =
  eps1 (2 eps1 + eps2) H^3 (`a0 Hddot`; ERRATA E7).
- B1 confirmed in all five families with arbitrary gauge functions; the printed linear K
  equation gives the same -eps1 S_R.
- B2 partly refuted: constraint violation at first order confirmed for both controls; my
  prediction that Psi_B> := Phi_B> leaves residuals that depend on the gauge functions failed
  (smoke run: the Newtonian residual contains no gauge function, and the registered run shows
  the Newtonian and synchronous residuals identical). What differs is the family: comoving,
  flat and uniform N never use Psi_B and give the printed sources. P0:690's "strong gauge
  dependence" is read in that sense in EQUATIONS.md.
- B5 (added before the registered run, after entry 1): with the printed sources dH/dt = dM/dt = 0
  on H = M = 0 in the gauge of the code; flipping S_Pi gives dH/dt = 4 S_R p^2/H, flipping S_K
  gives dH/dt = -4 S_R p^2/H and dM/dt != 0, flipping S_Kt gives dM/dt != 0 only.
- B3 confirmed (S_K^BSSN = S_K, S_A = a^-2 S_Kt, 4 pi misprint, momentum-constraint sign).
- B4 confirmed (Sigma = S_Pi/H, Friedmann line missing 1/(3 M^2)).
- C1 confirmed with a looser margin than I wrote: SR amplitude/printed = 1.043, 1.034, 1.027,
  1.025 at sigma = 0.02, 0.05, 0.1, 0.2 (the excess tracks |R|/|R_P0| = 1.044 ... 1.019, i.e.
  the change of H and eps1 between Hubble and sigma crossing, not O(sigma^2)).
- C2 confirmed: USR ratio = sigma^2/3 to four digits (1.3333e-4 at sigma = 0.02); dropping R'
  reproduces the printed value (1.0002 at sigma = 0.02).
- D1, D2 confirmed; D4 (added) linear drift (eps1 + eps2 - 3) = super-Hubble CPT.
- D3 confirmed: Monte Carlo drift 0.3075 +- 0.013 (4e5 paths, T = 0.01; 0.306 +- 0.018 at
  T = 0.005) against 0.32 (alpha^5) and 0.08 (alpha^3).
- (e) code map: all ten formula checks pass (`code_map/code_map.json`). Two labels of that
  file cite `noise.cpp:549/550` for w1, w2; the lines are 550/551 (EQUATIONS.md cites the
  right lines).

The matrix figure classifies 82 checks; all came out as expected at the time of the registered
run, but the expected-FAIL list of `make_figures.py` was written after the smoke runs, so the
figure is not a test of the predictions of entry 1: this entry is.
Open: none of my items; the review of these derivations on Fable (decision 0028 item 4) is for
the lead to decide.
