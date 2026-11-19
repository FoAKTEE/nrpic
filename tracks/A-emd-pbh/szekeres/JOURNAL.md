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
