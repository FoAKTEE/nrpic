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

## 2026-11-15T11:40Z  outcomes of the three checks

Check 1, run `B-emd-gw-20261115-113102-bc5e082` (`results/check_item3.json`,
`results/check_item3_supplement_1B.txt`). All five predictions confirmed.
- 1A: the projection has the expected form; for diag(A, B, B) with T_xy, T_xz left free
  it is the zero matrix.
- 1B: a 90-degree rotation forces q_xy = q_xz = q_yz = 0 and q_zz = q_yy. For a symbolic
  angle sympy's solve returned no parametric solution list (a solver limitation, not a
  result); the supplementary line checks that diag(A, B, B) is invariant under a
  rotation by a symbolic angle: True. So invariance under rotations about x is
  equivalent to the form diag(A, B, B).
- 1C: divergence (dA/dx + 3 A dY/dx / Y, 0, 0); solution A = C1 / Y^3. One global TT
  mode per slice, none at nonzero wave number.
- 1D: identity holds; X/Y = 1 + eps (D psi' + (c1 - c2) zeta) to first order, whose
  integral over a period is L: the harmonic mode starts at second order.
- 1E: Ricci scalar of the slice 0; constraint numerator 2 (3 D da/dt + 2 a dD/dt) psi'
  da/dt, so dD/dt = -(3/2)(da/dt / a) D: only the decaying mode. The growing-mode pancake
  in GR needs an x-dependent transverse metric.
No figure: symbolic identities (the numerical counterpart is the figure of check 2).

Check 2, runs `B-emd-gw-20261115-113120-bc5e082` and, after a figure-label change,
`B-emd-gw-20261115-113148-4e5c33b` (case numbers identical; `results/crossed_waves_tt.json`,
`figs/crossed_waves_tt.png`, inspected: the points lie on the (5/12) phi_x phi_y line over
three decades; the plane wave sits at the floor because its TT part is exactly zero).
- 2A confirmed, more strongly than written: the TT part of the plane wave is exactly 0.0
  (the source has only an xx component and the projector removes it without rounding).
- 2B confirmed: only (+-k, +-k, 0) carry TT for (1, eps, 0); |h_+| = (5/12)|phi_x phi_y|
  to 3.3e-16 over eps = 1e-3 to 1. TT fraction of the traceless source 1.73 eps for
  eps up to 0.18, 0.5 from eps = 0.3 on.
- 2C confirmed: (1, 1, 0) gives h_+ = 1.540e-5 at delta = 0.01 on 4 modes, (1, 1, 1) on 12
  mixed modes, TT fraction 0.5 in both: cubic symmetry does not remove them. (1, 0.9, 1.1)
  gives h_+ = 1.386e-5 at (k, k, 0) (written: about 1.3e-5) and h_+ = 1.69e-5 at
  (k, 0, k), its largest mode (the JSON field max_TT_strain, 2.40e-5, is the Frobenius
  norm, sqrt(2) |h_+|). The identity TT[Phi dd Phi] = -TT[dPhi dPhi] holds to 4.5e-16.

Check 3, runs `B-emd-gw-20261115-113151-4e5c33b`, `B-emd-gw-20261115-113246-50c684b`,
`B-emd-gw-20261115-113632-2960145` (identical numbers; the reruns only changed figure
labels and a wrong log path in a comment: the 128-cell rate comes from
`runs/cosmo/east_d0.01_n128_tsc/athena.20261114-021442.log`, not from the run named
first). `results/regime_estimates.json`, `figs/regime_estimates.png` (inspected: the
envelope maxima follow the 1/a guide from a = 3 to 200; the three box lines are straight,
the two measured-infall squares lie on or just below the box-4 line).
- 3A confirmed: envelope times a between 1.0761 and 1.0831 for a = 10 to 100 (spread
  0.66 percent), log slope -0.997; at a = 60 the junk is 1.8 percent of the static value.
- 3B: for the box of four Hubble radii the ratio omega_vir/(c k_1) runs from 0.81 to 3.57
  for delta = 0.0025 to 0.05. The refutation bound I wrote (4 or 1/4) is not reached, but
  the "within a factor of two" I expected FAILS above delta = 0.015 (the ratio grows as
  delta^(1/2)); with the measured infall scale factors (58.07 and 13.44) it is 1.57 and
  3.27 for delta = 0.01 and 0.05. Above delta = 0.015 the radiation band lies at the
  harmonics |n| = 2 to 3 of the box rather than at the fundamental and mixed modes.
- 3C: card-time table. Not an independent test: the 64-cell estimate (1387 steps, 63 s
  for delta = 0.01 to a = 140) reproduces the run whose rate it uses (1404 cycles,
  63.8 s), by construction.

## 2026-11-15T11:50Z  run ids renamed to UTC
The six run ids were first written with the local clock (PST, 03:31 to 03:36);
`harness/bin/nrpic-run`, merged from main during the session, names runs by UTC. Renamed
(scratch directories and manifests): 033102 -> 113102, 033120 -> 113120, 033148 -> 113148,
033151 -> 113151, 033246 -> 113246, 033632 -> 113632. Manifests rewritten in the
fields the helper reads (schema, status completed, outputs with sha256sums.txt), the
old id kept in their notes. Numbers unchanged.
