# Journal of the szekeres package (helper of A-emd-pbh, wave 3a)

Predictions are written before the test runs; outcomes are appended below each, failed
predictions included. Labels: [VERIFIED] (symbolic check or registered run named),
[BACKGROUND] (textbook or cited paper, locator given), [JUDGEMENT], [TO VERIFY].

Reference: arXiv:1708.09143 (Bolejko, "Relativistic numerical cosmology with Silent
Universes"), source fetched with `nrpic-fetch-arxiv` to
`kb-data/raw/arxiv/1708.09143/v4/src/simsilun_rev.tex`; the quasi-spherical Szekeres
metric is its eq. (ds2) at lines 290-292, the function E(r,p,q) at line 296, the
evolution equation at line 301, the bang time at lines 307-310, the fluid scalars rho,
Theta, Sigma, W at lines 314-319, the shear and Weyl ansatz sigma_ab = Sigma e_ab,
E_ab = W e_ab at lines 212-215, the silent evolution equations at lines 218-223.

## Entry 1, 2026-11-19 14:35 UTC: conventions and predictions before any test

Conventions [JUDGEMENT]: signature (-,+,+,+), G = c = 1, Lambda kept in the symbolic
checks and set to 0 in the numerics (AthenaK runs of Track A have no Lambda). The paper
writes the metric with signature (+,-,-,-) but e_ab = h_ab - 3 z_a z_b, which is
traceless only when z_a z^a = +1: its conventions are mixed, so every sign is fixed here by
the symbolic computation, in mixed components (e^a_b = h^a_b - 3 z^a z_b with z_a z^a = +1,
eigenvalue -2 along z, +1 transverse). Radial label r = areal radius R on the initial
slice t = t_i (as `expball`); simultaneous bang time t_B = 0; the Szekeres dipole function
of the paper, E(r,p,q), is called `Ecal` here to avoid a clash with the LTB energy E.

Predictions (each refuted as stated):

- P1 (sym) The metric (ds2) with Rdot^2 = -k + 2M/R + Lambda R^2/3 satisfies
  G_ab + Lambda g_ab = 8 pi rho u_a u_b identically, u = d_t, with
  8 pi rho = 2 (M' - 3 M Ecal'/Ecal) / (R^2 (R' - R Ecal'/Ecal)) (paper eq. szrho, which is
  kappa rho). Refuted if the numerator of any component does not reduce to zero.
- P2 (sym) Theta = div u equals the paper's (sztht); sigma^a_b = Sigma e^a_b with the
  paper's Sigma (szshr); the electric Weyl tensor E^a_b = C^a_{cbd} u^c u^d = W e^a_b with
  the paper's W (szwey), same sign (Schwarzschild check: M' = 0, Ecal' = 0 gives
  E^r_r = -2M/R^3, the radial tidal stretching); the magnetic Weyl tensor vanishes
  (R_ijkt = 0 given the field equations). Refuted by any non-zero difference.
- P3 (sym) On the slice t = const (lapse 1, shift 0, K_ij = -(1/2) d_t gamma_ij, the
  sign of AthenaK, K = -Theta) the Hamiltonian and momentum constraints hold identically
  with S_i = 0; K^r_r = -(Rdot' - Rdot Ecal'/Ecal)/(R' - R Ecal'/Ecal),
  K^p_p = K^q_q = -Rdot/R.
- P4 (sym) The task text expects conformal flatness of the slice to fail in general. My
  prediction is the opposite [JUDGEMENT, from an argument written in DESIGN.md section 2]:
  the Cotton tensor of gamma_ij = (R' - R Ecal'/Ecal)^2/(1-k) dr^2 + R^2/Ecal^2 (dp^2+dq^2)
  vanishes identically for arbitrary R(r), k(r), S, P, Q(r); for k = 0 the slice is flat.
  Refuted if the Cotton tensor has a non-zero component.
- P5 (num) The evolution written with the universal function g(lambda),
  R = M^(1/3) t^(2/3) g(k t^(2/3)/M^(2/3)), reproduces `expball.exact.Shells.R` (written
  independently with the parametric cycloid and hypergeometric ages) to 1e-12 relative for
  every shell of data set 2 before its crunch; turnaround and crunch proper times to
  1e-12; k = -2E, Misner-Sharp m = M, K^r_r = KL, K^p_p = KT, rho at tau = 0 to 1e-12
  relative, in the limit of no dipole. Refuted by a larger difference anywhere.
- P6 (num) With no dipole the conformal map of this package gives the isotropic radius
  and psi of `expball.model.Ball.rbar_of_R` to 1e-10.
- P7 (num) With a dipole of amplitude eps = 0.1 (data set 2's LTB functions plus a
  rotating dipole supported in the transition shell), the Cartesian fields psi, K_ij, rho
  built through the conformal map satisfy the finite-difference Hamiltonian and momentum
  constraints with residuals that converge at the order of the stencil (2 and 4) in every
  norm, since the data are C-infinity (refuted: order below p - 0.3 at the finest pair).
- P8 (num) The difference between the Szekeres slice and the LTB slice with the same M, k
  (what a format-2 table can hold) is first order in eps: max|psi_Sz - psi_LTB|,
  max|rho_Sz - rho_LTB|/rho_b and max|K_Sz - K_LTB|/H have log-log slope 1.00 +- 0.05 in
  eps for eps <= 0.05. So a spherical table represents the Szekeres slice only at zeroth
  order in the dipole.
- P9 (num) For eps = 0.1 neither shell crossing (R'/R <= |b|) nor negative density
  (M'/(3M) <= |b|) occurs on any shell before the crunch of the core (tau = 44.45, data
  set 2) [to be computed; if it fails, eps is lowered and the failure stays on record].

## Entry 2, 2026-11-19 15:18 UTC: outcomes of P1-P9

- P1 HELD [VERIFIED, `sym/sym_szekeres.py --fast`, all ten components of
  G_ab + Lambda g_ab - 8 pi rho u_a u_b vanish at three exact rational points each, with
  Lambda kept; the registered repeat is run A-20261119-1528xx below]. The fully symbolic
  mode (`--only C` without `--fast`) did not finish within 50 minutes for the constraints
  and was not used; the random-point test is exact arithmetic (Schwartz-Zippel).
- P2 HELD: Theta, sigma^a_b = Sigma e^a_b, E^a_b = W e^a_b with the paper's formulas and
  signs, e = diag(-2, 1, 1); R_ijkt = 0 on shell (H_ab = 0); Schwarzschild limit W = M/R^3.
  The paper writes (+,-,-,-) and e_ab = h_ab - 3 z_a z_b; the mixed components used here
  are unambiguous.
- P3 HELD: Hamiltonian and momentum constraints, K^r_r, K^p_p, K = -Theta. A negative
  control (density doubled) is non-zero, as it must be.
- P4 HELD, against the expectation of the task text: the Cotton tensor of the comoving
  slice vanishes for arbitrary R(r), k(r), S, P, Q(r) (exact rational points), and also
  exactly for explicit polynomial functions (S = 1 + r/3 + r^2/5, P = r^2/7 + r/2,
  Q = r^3/11 - r/4, k = r^2/9, R = r + r^3/13, at (r, p, q) = (1/3, 2/5, -1/7): all nine
  independent components are 0 in rational arithmetic; probe script in
  scratch/A-emd-pbh/tmp/sym/, not registered). The k = 0 slice is flat (3-Ricci = 0); for
  k != 0 the slice is not flat. A first run reported four non-zero Cotton components: a
  random point had hit a zero of a denominator (exact evaluation gives zoo there); the
  check now skips singular points and the failure is on record here. The explicit
  conformal map (confmap.py) is a constructive proof: its identities hold symbolically
  (check E) and its pull-back equals the Szekeres metric to 1e-8 at 25 random points
  (finite differences, test_confmap_pullback_is_conformally_flat).
- P5 HELD with one bound exceeded: run A-20261119-151501-9cff966. Initial slice: M exact,
  k to 1.7e-16, rho 4.0e-16, KL 3.4e-15, KT 3.4e-15 (relative). R(tau) of 400 shells on
  400 times: 2.2e-14 up to 0.9 of the core crunch, 2.17e-12 at tau = 44.41, 0.1 per cent
  before the crunch of the core (R/r = 0.04) - the predicted 1e-12 is exceeded there, by
  the conditioning near the crunch; turnaround, crunch and R = 2M times 6.6e-15, 5.1e-15,
  5.1e-15. Figure `figures/fig_ltb_limit.png` (inspected).
- P6 HELD: isotropic radius of the map against `expball` 5.1e-12 (largest near r -> 0),
  psi 1.5e-12, rho 1.9e-12 rho_b, KL 1.2e-12 H at 20000 points (same run).
- P8 HELD: run A-20261119-151501-3e344a4. Fits over eps <= 0.05 give slopes 0.9996
  (psi), 1.004 (rho), 1.006 (K), 1.007 (KL - KT), 0.9995 (displacement of the centre of
  the r = 1 sphere); coefficients max|dpsi| = 0.0044 eps, max|drho|/rho_b = 1.84 eps,
  max|dK|/H = 1.43 eps, max|d(KL - KT)|/H = 1.11 eps, centre shift 1.93 eps (length units,
  ball radius 6). For eps = 0.1 the spherical table misses 0.19 rho_b of density and
  0.15 H of K, but only 4.4e-4 of psi. Figure `figures/fig_dipole_order.png` (inspected).
- P9 HELD: run A-20261119-151501-986153a. min over r and over tau up to 0.995 of the core
  crunch of (R'/R)/|b| = 10.0 (at tau = 0, where it is 1/eps by construction; it grows
  later), (M'/(3M))/|b| = 3.94. Figures `fig_slice_maps.png`, `fig_evolution.png`
  (inspected; the slice-map layout left an empty right margin and no z label: fixed in the
  script and rerun below).
- A defect found and fixed while testing (no registered run used the defective code):
  the safeguarded Newton loops (inverse map, cycloid angle, inverse of l) could leave a
  converged point at a bisection midpoint when the loop ended for all points at once; a
  slab of the mesh run then put one cell at the wrong shell (r = 0.0015 instead of 3.98).
  Converged points are now frozen, and a collapsed bracket counts as converged; serial
  and parallel mesh residuals agree to the last digit and batch and single-point
  evaluations agree exactly.

## Entry 3, 2026-11-19 15:19 UTC: predictions for the first AthenaK execution

Run: scripts/run_code_geodesic.py, processor executable of core-v0.3
(.work/build_cpu_v03/src/athena), periodic box [-8, 8]^3 at N = 32 and 64 cells per side,
nrpic_cosmo id = file with the field file of szekeres/codeid.py, one particle per cell at
rest with m = rho psi^6 h^3, CIC deposit, geodesic slicing (every lapse and shift driver
off), Z4c with nghost = 4, diss = 0.5, damp_kappa1 = 0.5, RK4 at CFL 0.25, to tau = 40
(the core crunches at 44.45). Predictions:

- P10 The field file is read and at tau = 0 the dumped energy density E equals the exact
  rho at every cell to the float32 precision of the dump (1e-6 relative): the CIC weight of
  a particle at a cell centre is 1 in that cell. chi = psi^-4 to 1e-6. Refuted by a
  larger difference anywhere.
- P11 alpha stays 1 to round-off (alpha_dev_max < 1e-12) and the run reaches tau = 40
  without failure at both resolutions.
- P12 The errors of K (= Khat + 2 Theta_Z4c), of E and of chi against the exact values at
  the same cells converge: the maximum relative error over the shell region falls by at
  least 4 from N = 32 to N = 64 at every dump time (second order or better; the stencils
  are sixth order, the cloud and the Kreiss-Oliger term are lower) [JUDGEMENT]. Absolute
  scale at N = 64: below 1e-2 relative for K at tau = 10 [JUDGEMENT, from the initial
  Hamiltonian residual of order 1e-3 of 16 pi rho_b at h = 0.25 (run
  A-20261119-151452-46f171e) and an amplification of order 10 to tau = 40].
- P13 The constraint monitor at tau = 0: rms H/(16 pi rho_b) over the shell region below
  1e-2 at N = 32 and smaller by at least 4 at N = 64.

## Entry 4, 2026-11-19 15:36 UTC: what the first AthenaK run shows while it runs; predictions for a second, short run

Run A-20261119-152010-94a9461, from its constraint statistics (`N32/szk.cstat.hst`) before
its own analysis finishes:

- N = 64 was stopped by me (kill of its process id) after start-up: on the loaded
  processors one cycle of 64^3 takes tens of seconds, so 640 cycles to tau = 40 would take
  hours. Its tau = 0 dump exists and is analysed by the run.
- N = 32 (h = 0.5): the whole-box maximum of |H| jumps from 9.6e-4 at tau = 0 (0.04 of
  16 pi rho_b, the size of the order-4 finite-difference residual of the data at this h,
  run A-20261119-152252-2ae031e: Linf 0.054) to 1.3e-2 at tau = 1 and 3.4e-2 at tau = 10;
  the mean |H| rises from 3.5e-5 to 1.4e-3; K leaves the exact range after tau = 20 and the
  run turns to NaN between tau = 24 and 28. P11 FAILED at N = 32 (and was not tested at
  N = 64). The data are under-resolved at h = 0.5: the initial momentum residual at this h
  is 34 per cent of 16 pi rho_b at its maximum (same mesh run), the smallest density scale
  is 0.55 (run A-20261119-152232-3d29cc1). Cause not established: resolution, the
  dissipation term (diss = 0.5 at h = 0.5), or geodesic slicing (no gauge damping) are
  candidates; none has been tested in a run where it could have failed.

Predictions for run 2 (scripts/run_code_geodesic.py --N 32 64 --tlim 2, dumps at
tau = 0.5, 1, 2, with a variant diss = 0):

- P14 If the early growth of |H| is a truncation effect of the under-resolved shell, the
  maximum and rms of H/(16 pi rho_b) over the shell at tau = 1 and 2 fall by at least 4
  from N = 32 to N = 64, with and without dissipation. If the dissipation drives it, the
  variant diss = 0 has a growth at least 3 times smaller at both N. Refuted (both
  hypotheses) if neither happens.
- P15 The relative error of K against the exact -Theta in the shell at tau = 2 falls by at
  least 4 from N = 32 to N = 64.

## Entry 5, 2026-11-19 15:39 UTC: outcomes of P10-P13 (run A-20261119-152010-94a9461)

Analysis of the run itself (`code_geodesic.json`, `figures/fig_code_geodesic.png`,
`fig_code_geodesic_profiles.png`, inspected):

- P10 HELD at N = 32 and 64: at tau = 0 the code's K equals the exact -Theta to 5e-16
  (the field file is read as written), E equals rho to 9e-9 (core) and 6e-8 (shell),
  chi = psi^-4 to 3e-8: the float32 precision of the dump. One particle per cell centre
  with the CIC deposit gives the exact density, as designed.
- P11 PARTLY: alpha stays 1 to 1.1e-13 (tau = 10) and 2.3e-13 (tau = 20); but the run at
  N = 32 does not reach tau = 40: K leaves the exact solution (relative error 0.15 in the
  shell and 0.17 in the core at tau = 10, 0.85 in the core at tau = 20) and the fields are
  NaN at tau = 30. N = 64 was stopped after start-up (entry 4). FAILED as stated.
- P12 NOT TESTED (no N = 64 evolution). At N = 32 the errors at tau = 10 are 15 per cent
  in K, 6.5 per cent in E and 4.4 per cent in chi (maximum over the shell): far above the
  "1e-2 at N = 64" scale predicted, which belongs to N = 64 and remains open.
- P13 HELD: the code's monitor at tau = 0, rms of H/(16 pi rho_b) over the shell, is
  9.8e-3 at N = 32 and 8.6e-4 at N = 64 (factor 11.4); over the core 9.7e-4 and 6.6e-5.
  The momentum monitor over the shell 1.5e-2 and 2.6e-3. These are the code's sixth-order
  operator on gamma_ij; the order-4 residual of this package at h = 0.47 and 0.23 was
  1.2e-2 and 1.4e-3 (shell, L2, run A-20261119-152252-2ae031e): the same size.
- The constraint grows fast after the start: rms H/(16 pi rho) over the shell 1.18 at
  tau = 10 and 6.3 at tau = 20 at N = 32 (normalised by the background density at that
  time). Cause: open (entry 4, run 2 below tests resolution and dissipation).
