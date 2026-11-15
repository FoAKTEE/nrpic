# JOURNAL of the scope package (B-emd-gw, G0)

Append-only. Predictions are written before the check runs, outcomes after, also when the
prediction fails. Times UTC.

## 2026-11-15T11:29Z  predictions for the three checks of this package

Check 1, `scripts/check_item3.py` (symbolic, sympy). Item 3 of
`coord/notes/derivations_to_check.md` claims that an exactly plane-symmetric collapse has
no transverse-traceless (TT) part. Written before the run:
- (1A) The flat-space TT projector for a wave vector along x annihilates a symmetric
  tensor exactly when T_yy = T_zz and T_yz = 0; the remainder otherwise is
  ((T_yy - T_zz)/2)(e_y e_y - e_z e_z) + T_yz (e_y e_z + e_z e_y). Refuted if any
  component of the projection of diag(A, B, B) is not identically zero.
- (1B) Invariance under rotations about the x axis forces Q_xy = Q_xz = Q_yz = 0 and
  Q_yy = Q_zz for a symmetric tensor. Refuted if a 90-degree rotation alone leaves a free
  off-diagonal component other than Q_yz (expected: 90 degrees forces Q_xy = Q_xz = 0,
  Q_yy = Q_zz, Q_yz -> -Q_yz, so Q_yz = 0).
- (1C) For the plane-symmetric 3-metric diag(X^2, Y^2, Y^2)(t, x), the covariant
  divergence of the mixed tensor diag(A, -A/2, -A/2)(x) is dA/dx + 3 A d(ln Y)/dx, so the
  TT tensors with the symmetry form one family A = c / Y^3 (one global mode on the torus,
  no mode at nonzero wave number). Refuted if the divergence has another form.
- (1D) With zero shift and unit lapse, the L2 projection of the traceless extrinsic
  curvature onto that mode is proportional to -d/dt of the integral of X/Y over x. In
  the linear regime this integral is constant, so the mode starts at second order.
  Refuted if the integrand identity (X/Y)(K^x_x - K^y_y) = -d/dt (X/Y) fails.
- (1E) Side check on the reference solution of the pancake test: with transverse metric
  a(t)^2 (no dependence on x), X = a (1 + D(t) psi'(x)), dust at rest, rho = rho0 /
  (1 + D psi'), the Hamiltonian constraint on the flat slice forces dD/dt = -(3/2) H D:
  only the decaying mode. So the growing-mode pancake in general relativity needs a
  transverse metric that depends on x (a comoving curvature perturbation), and "the
  Zel'dovich solution is exact in plane symmetry" holds as stated only for the Newtonian
  theory. Refuted if the constraint is satisfied by D proportional to a.

Check 2, `scripts/crossed_waves_tt.py` (numpy, Fourier grid 32^3, box 4, H0 = 1). The
quasi-static second-order TT strain of the matter-era potential Phi = sum_i phi_i
sin(k x_i), phi_i = -(3/2)(H/k)^2 d_i, from the weak-field equation of arXiv:1604.06065
(its eq. ij, source line 294-298) with growing-mode velocities: h^TT = (20/3)
TT[d_i Phi d_j Phi] / |k|^2. Written before the run:
- (2A) Plane wave, ratios (1, 0, 0): largest |h^TT| at most 1e-15 of the largest |h| of
  the untruncated source (rounding).
- (2B) Ratios (1, eps, 0): the only nonzero TT modes are at (+-k, +-k, 0); their
  amplitude is (5/12) |phi_x phi_y| (Fourier coefficient of the "plus" polarization in
  the basis (1,-1,0)/sqrt2, (0,0,1)), linear in eps to 1e-10.
- (2C) Equal amplitudes (1, 1, 0) and (1, 1, 1) give nonzero TT modes at the mixed wave
  vectors (cubic symmetry does not remove them); for (1, 0.9, 1.1) at delta = 0.01 the
  static TT strain at (k, k, 0) is about 1.3e-5.
Refuted if the plane wave gives a TT part above rounding, if other wave vectors appear for
(1, eps, 0), or if the amplitude law differs from (5/12) phi_x phi_y by more than 1e-10.

Check 3, `scripts/regime_estimates.py` (ODE and arithmetic). Written before the run:
- (3A) Junk TT radiation of conformally flat initial data: the TT mode starts at zero
  while its quasi-static value is h_s; integrating h'' + 2 Hc h' + G^2 h = G^2 h_s in
  conformal time (a = (1 + t/2)^2) from h = h' = 0, the oscillating part |h - h_s|
  decays as 1/a once the mode is inside the horizon: envelope times a constant to 10
  percent for a between 10 and 100 at G = sqrt(2) pi/2 (the (k, k, 0) mode of the box of
  four Hubble radii). Refuted if the envelope falls as a^-1/2 or slower.
- (3B) For the box of four initial Hubble radii, the virial GW frequency at the collapse
  epoch (omega = 2 sqrt(Delta/2) Hc, Delta = 18 pi^2) is within a factor of two of the
  lowest box wave numbers for amplitudes 0.0025 to 0.05: the box modes sample the
  radiation band rather than only the near field. Refuted if the ratio is above 4 or
  below 1/4 over that range. (Estimate only; not a test of the code.)
