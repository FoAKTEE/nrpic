# JOURNAL of the work package einstein_straus (D-pre-1, helper of D-bh-dress)

Units G = c = 1, black-hole mass M. Sign of the code: expansion has K < 0. Evidence
labels as in `CLAUDE.md`. Predictions are written before the script or run that tests
them; outcomes are appended below them and never edited away.

## 2026-11-15, entry 1: predictions for the symbolic derivation (sym/*.py), written before the scripts ran

Hypotheses under test are items 1 and 2 of `coord/notes/derivations_to_check.md`
(orchestrator, [JUDGEMENT]). My expectations, from my own derivation on paper:

S1. For the 3-metric dl^2 + R(l)^2 dOmega^2 and K^i_j = diag(KL, KT, KT), with matter at
    rest in the slice (S_i = 0), the Hamiltonian constraint reduces to
    (2/R^2)(1 - R'^2 - 2 R R'') + 4 KL KT + 2 KT^2 = 16 pi rho and the radial momentum
    constraint to dKT/dl = (KL - KT) R'/R. With m = (R/2)(1 - R'^2 + R^2 KT^2) the
    combination dm/dl - 4 pi R^2 rho R' is a linear combination of the two constraints
    (so m is constant in vacuum). Refuted if sympy leaves a nonzero remainder.
S2. Every slice t = T(R) of Schwarzschild (static coordinates) satisfies
    R'^2 = 1 - 2M/R + R^2 KT^2 identically in T, its KL equals d(R KT)/dR, and the lapse of
    the stationary slicing (alpha = -n.xi) equals R' = dR/dl.
S3. The expansions of the outgoing and ingoing null normals of a sphere in the slice are
    theta_pm = (2/R)(pm R' - R KT); their product is -(4/R^2)(1 - 2m/R). Hence a sphere is
    anti-trapped iff R < 2m and KT < 0; with KT = -f sqrt(2M/R^3) and f >= 0 the slice has
    no anti-trapped sphere iff it stays at R >= 2M, i.e. iff f vanishes at the throat
    (throat at R = 2M, the bifurcation sphere).
S4. Where K_ij = 0 in vacuum, psi = a + b/rbar with 2ab = M and the throat at rbar = b/a,
    R = 2M. Because psi = 1 at large rbar and the slice is flat (psi = 1) wherever f = 1,
    integrating inwards gives a < 1 whenever f is not identically zero; so the puncture
    form is psi = 1 + u(rbar) + m_p/(2 rbar) with u(0) = a - 1 < 0 and bare mass
    m_p = M/a > M, NOT psi = 1 + M/(2 rbar) as item 2 writes. Refuted if a = 1 comes out.
S5. Lemaitre-Tolman-Bondi dust (comoving coordinates, E(r)): G^tau_r = 0 identically,
    d m/d tau = -(R^2 Rdot/2) G^r_r = -4 pi R^2 Rdot p_r = 0 for dust, so the mass inside
    any dust shell, in particular inside the comoving inner wall, is constant; the wall
    of a marginally bound bubble follows R_w(tau) = (R_w0^(3/2) + (3/2) sqrt(2M) tau)^(2/3).

## 2026-11-15, entry 2: predictions for the generator and the offline constraint check, written before the scripts ran

Model (`es_model.py`): M = 1; f(R) = 0 for R <= R0 = 4 M, smooth (C-infinity) step to
f = 1 at R1 = inner dust edge; dust density rising smoothly over [R_w - w_in, R_w + w_in]
with rho_0 chosen so that the dust beyond the edge is exactly Einstein-de Sitter
(m = 4 pi rho_0 R^3/3), and falling smoothly over [R_b - w_out, R_b + w_out].

N1. 1D residuals (radial, fourth-order differences of the exact fields sampled at
    spacing h): H and M_r fall as h^4 (measured order between 3.7 and 4.3 between
    h = 0.1, 0.05, 0.025 M in every region away from rbar = 0), down to a floor of order
    1e-13 of the term scale set by the quadrature of rbar(R).
N2. 3D residuals (Cartesian grid, metric psi^4 delta_ij and K_ij = psi^4 [KT delta_ij +
    (KL - KT) n_i n_j] evaluated as the code evaluates the table, Christoffel symbols and
    Ricci tensor by fourth-order differences of gamma_ij, no use of the conformal-flatness
    identity): fourth order in sub-boxes around the throat region, the curvature
    transition, the inner and the outer dust edge, between h = 1, 1/2, 1/4 M.
N3. Table interpolation (piecewise cubic of `nrpic_cf.cpp`, branch core/id-extrinsic) at
    drbar = 0.02 M: maximum relative error of u, KL, KT below 1e-7, so at the mesh
    spacings of a first run (dx >= M/32) the table adds less than the finite-difference
    error. Refuted if the 3D residual with table-evaluated fields differs from the one
    with exact fields by more than 10 per cent at h = 1/4 M.
N4. Throat at rbar = M/(2 a^2), apparent horizon area 16 pi M^2 on the slice; no
    anti-trapped sphere (theta_- < 0 everywhere on the outer sheet).

## 2026-11-15, entry 3: prediction for the start-time check inside AthenaK, written before the runs

Test (`code_t0_check.py`): the registered table of run D-bh-dress-20261115-042653-f3da881
plus the puncture of bare mass m_p, read by `nrpic_cf` of branch core/id-extrinsic (the
processor executable of `wt/core-id`, sha256 7d1292d0..., the build core registered at
commit 408df57), uniform mesh of half-width 48 M, dx = 1 and 1/2 M, nlim = 0; lattice
dust at the cell centres with hp = dx (CIC then deposits the exact density at the cell
centres); the code's own field dump of H, M_i, E at t = 0.

C1. Transition region (4 < r < 30): the code's max |H| and max |M| fall with resolution
    at order >= 3.5 between dx = 1 and 1/2 M, and at dx = 1 M they are within a factor
    of 10 of my offline 3D values at h = 1 M (box "mid transition": max |H| 1.5e-6,
    max |M| 5.9e-7); the code may be smaller if its stencils are of higher order.
C2. Inner dust edge (34 < r < 46): E equals rho at the cell centres to the float32
    precision of the dump (relative 1e-6); H and M fall at order >= 3.
C3. Puncture region (r < 3): no convergence claimed (the throat at rbar = 0.52 M is not
    resolved by dx = 1/2 M); recorded only.
Refuted by: a transition residual that does not fall, or exceeds 10 times the offline
value at the same spacing (that would point to a mismatch in how the code assembles
K_ij = psi^4 [...] with the puncture, a sign, or the mixed-component convention).

## 2026-11-15, entry 4: outcomes of entries 1-3

Symbolic (run D-bh-dress-20261115-042626-f3da881, 48 identities, all pass):
- S1 confirmed. The multipliers of the identity are dm/dl = 4 pi R^2 (rho R' - S_l R KT)
  + (R^2 R'/4) Ham - (R^3 KT/2) Mom (my first guess of the second multiplier, -R^2 KT/2,
  was wrong by a factor R; the script now checks -R^3 KT/2).
- S2 confirmed: Misner-Sharp relation and KL = d(R KT)/dR for every slice t = T(R);
  alpha = W and beta^R = alpha R KT for the stationary slicing; T'(R) of the f family.
- S3 confirmed; the expansion identities pass numerically at three points (sympy cannot
  remove the square-root branches symbolically) and the product rule with general m
  symbolically.
- S4 confirmed: a = 0.976592 < 1, so m_p = 1.023969 M, u(0) = -0.023408 (data-set run
  D-bh-dress-20261115-042653-f3da881). Item 2's psi = 1 + m/(2 rbar) is refuted for the code's
  normalization.
- S5 confirmed.

Offline check (run D-bh-dress-20261115-042704-f3da881):
- N1 partly as predicted, partly mis-specified. At the spacings I predicted
  (0.1, 0.05, 0.025 M) the 1D Hamiltonian residual of the transition is already at the
  round-off floor, so I changed to spacings per region (0.04 to 0.005 M inside rbar(R0),
  0.8 to 0.1 M beyond) before the registered run. Then: momentum residual fourth order
  (3.80/3.95/3.99 transition, 3.44/3.61/3.85 inner edge, 3.60/3.74/3.93 outer edge); the
  Hamiltonian residual is fourth order in the transition (3.92-3.98) and at round-off
  where psi is harmonic or 1. Not predicted: the radial fourth-order Laplacian
  D2 + (2/r) D1 is exact for psi = a + b/r (D2(r psi) = r D2 psi + 2 D1 psi for these
  stencils), so the 1D test is blind in the puncture region; the 3D test covers it.
- N2 confirmed: 3D orders 3.85-4.07 (finest pair) in all seven boxes, 3.49 for the
  inner-edge momentum residual at the coarsest pair (pre-asymptotic, C-infinity step).
- N3 confirmed: table error 1.0e-9 relative (KL), 6.5e-13 (u); table- and exact-field 3D
  residuals agree within 11 per cent (largest at h = 1/16 M, where the table error first
  shows), except where both are at round-off. Not predicted: the lapse column is
  interpolated to only 4.5e-6 next to rbar = 0 (alpha = psi^-2 ~ rbar^2/(a rbar + b)^2);
  harmless (gauge), and `lapse = precollapsed` gives the same lapse exactly.
- N4 confirmed: throat at rbar = 0.524256 M = M/(2 a^2); no anti-trapped sphere
  (figs/es_expansions.png, looked at).

Start-time check inside AthenaK (runs D-bh-dress-20261115-043002-d51c7f2,
D-bh-dress-20261115-043033-4df1e76, analysis D-bh-dress-20261115-043406-4df1e76):
- C1 confirmed in its refutation clause, and the code is far below my fourth-order values:
  in the box "mid transition" max |H| 8.4e-9 -> 1.4e-10, max |M| 2.4e-8 -> 4.4e-10 between
  dx = 1 and 1/2 M (order 5.9, 5.8; the code's derivative stencils are of higher order).
  Over the whole region 4 < r < 30 (which includes the steep start of the transition) the
  orders are 5.3 (H) and 4.7 (M). So nrpic_cf assembles K_ij = psi^4 [...] with the full
  psi (table + puncture) and the mixed components as the interface says.
- C2 confirmed: E - rho at most 1.1e-13 (relative 3e-8, float32); at the inner edge H
  order 4.9, M order 3.2 (max |M| 1.1e-5 -> 1.1e-6; offline at h = 1/2 M: 2.4e-6).
- C3 as expected: H of order 1 near the puncture at both spacings.
Figures looked at: figs/es_profiles, es_expansions, es_reference, es_particles,
check_1d, check_3d, code_t0.

Data set for the first run regenerated with plain-float header values as run
D-bh-dress-20261115-043445-b782009 (table and particle rows byte-identical to the checked
ones: sha256 of the table rows 815cc84f..., particle files equal by cmp).
