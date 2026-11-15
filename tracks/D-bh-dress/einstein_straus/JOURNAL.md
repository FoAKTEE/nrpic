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
