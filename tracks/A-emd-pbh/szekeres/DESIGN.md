# Szekeres dust without symmetry as a test of AthenaK: design

Helper of A-emd-pbh, wave 3a, 2026-11-19. Verification row of the brief, line 851
("Szekeres-type dust solutions | Nonlinear evolution without symmetry | Exact solution;
arXiv:1708.09143 | A, B"). Labels: [VERIFIED] (symbolic check, unit test or registered
run named), [BACKGROUND] (textbook or cited paper with locator), [JUDGEMENT],
[TO VERIFY]. Numbers come from the runs named; JOURNAL.md has the predictions made before
each run.

## 1. The solution

Quasi-spherical Szekeres dust (arXiv:1708.09143, `simsilun_rev.tex` lines 290-319),
signature (-,+,+,+), G = c = 1, Lambda = 0:

    ds^2 = -dt^2 + (R' - R Ecal'/Ecal)^2/(1 - k) dr^2 + R^2/Ecal^2 (dp^2 + dq^2),
    Ecal = ((p - P)^2 + (q - Q)^2)/(2S) + S/2,     Rdot^2 = 2M/R - k,
    8 pi rho = 2 (M' - 3M Ecal'/Ecal)/(R^2 (R' - R Ecal'/Ecal)),

with five free functions of r (M, k, S, P, Q) and the bang time, here simultaneous
(t_B = 0, pure growing mode). The dust is at rest in (r, p, q) and t is its proper time.
On the unit sphere of directions n (stereographic image of (p, q) about (P, Q) with scale
S), Ecal'/Ecal = b.n with b = -(P', Q', S')/S, so the whole dipole enters through one
scalar bn = b.n per element [VERIFIED, `sym/sym_szekeres.py` check E].

- Field equations, fluid scalars and Weyl tensor: all ten components of the Einstein
  equations, Theta, sigma^a_b = Sigma e^a_b, E^a_b = W e^a_b (e = diag(-2, 1, 1) in
  (r, p, q)), magnetic Weyl zero, with the paper's formulas and signs [VERIFIED, run
  A-20261119-152233-d31f783 (32 symbolic checks) and JOURNAL entry 2; the paper mixes sign
  conventions, see JOURNAL entry 1].
- Evolution of each element: R(t, r) = M^(1/3) t^(2/3) g(lambda), lambda = k t^(2/3)/M^(2/3)
  with one universal function g (`szekeres/universal.py`); R does not depend on the
  direction, the density does: rho = M/(4 pi R^3) (M'/M - 3 bn)/(R'/R - bn). Turnaround,
  crunch and R = 2M times are those of the LTB shell with the same M and k [VERIFIED to
  7e-15 against `expball`, run A-20261119-151501-9cff966]. The four silent-universe
  equations of the paper (lines 218-223) hold along every element [VERIFIED,
  `tests/test_szekeres.py::test_silent_universe_equations`, and run of section 5].
- Regularity: no shell crossing while R'/R > |b|, positive density while M'/(3M) > |b|.
- The LTB limit is b = 0 (S, P, Q constant).

Reference model (`scripts/common.py`): the LTB functions of expball data set 2 (H = 1/16,
smoothed top-hat, mean contrast 1 inside R1 = 2.4, Einstein-de Sitter from R2 = 6 on) and
the dipole b(r) = (eps/r) h(u) e(u), u = (r - 2.4)/3.6, h a C-infinity bump of height 1,
e(u) turning from z towards x while turning about z, eps = 0.1. A dipole is a coordinate
effect where M/r^3 and k/r^2 are constant [the density formula is then homogeneous], so
the dipole acts only in the transition shell 2.4 < r < 6 (it is supported there anyway);
the core r < 2.4 is a closed FLRW region and r >= 6 is exactly Einstein-de Sitter: a
Szekeres hole cut into Einstein-de Sitter, which tiles a periodic box. Margins before the
core crunch (tau = 44.454): (R'/R)/|b| >= 10.0, (M'/(3M))/|b| >= 3.94 [VERIFIED, run
A-20261119-151501-986153a]. The density at t_i ranges over 0.39 ... 2.0 of the background;
at tau = 30 up to 19.5, and the density along +b and -b of one shell differs by up to a
factor 0.60 (r = 4.6) [same run].

## 2. The slice orthogonal to the dust

The dust is irrotational and geodesic, so its orthogonal slices are t = const of the
metric above, with lapse 1 and shift 0 (synchronous comoving gauge):

    gamma = (R' - R bn)^2/(1 - k) dr^2 + R^2/Ecal^2 (dp^2 + dq^2),
    K^r_r = KL = -(Rdot' - Rdot bn)/(R' - R bn),   K^p_p = K^q_q = KT = -Rdot/R,
    K = -Theta,  S_i = 0 (the dust is at rest in the slice), E = rho.

The radial eigenvalue KL depends on the direction, the transverse one KT does not: on
each shell K^i_j has one eigenvalue that is the same in every direction [VERIFIED,
sym check C].

**Conformal flatness holds.** The task text expected it to fail in general. It does not:
the Cotton tensor of gamma vanishes for arbitrary R(r), k(r), S(r), P(r), Q(r) [VERIFIED,
sym check D at exact rational points, and exactly for explicit polynomial functions,
JOURNAL entry 2], and for k = 0 the slice is flat (3-Ricci zero). Whether this is stated
in the Szekeres literature was not looked up [TO VERIFY through kb]. The reason, and the
construction used here (`szekeres/confmap.py`): write Ecal as a vector X = (a, b, c, d)
on the hyperboloid b^2 + c^2 - 4ad = -1. The "flat Szekeres" metric
(rho' - rho Ecalt'/Ecalt)^2 dr^2 + rho^2/Ecalt^2 (dp^2 + dq^2) is flat for any functions
rho(r), Ecalt(r) (it is the slice of the M = 0, k = 0 member, which is Minkowski space),
and gamma = Phi^2 times it with Phi = R Ecalt/(rho Ecal) provided

    u = (ln rho)' = s (-(R'/R) eta(Xt, X) + eta(Xt, X')),   Xt' = u Xt - s ((R'/R) X - X'),

s = (1 - k)^(-1/2), eta the Minkowski product of the hyperboloid; the ODE keeps Xt on the
hyperboloid [VERIFIED, sym check E]. The flat metric is embedded in R^3 by non-concentric
spheres, x = rho(r) O(r) ntilde + C(r) with O' = -O [omega~]x, C' = -rho O b~ [VERIFIED,
sym check E; the pull-back of the numerical map reproduces the Szekeres metric to 1e-8,
unit test]. So:

- In conformally flat Cartesian coordinates gamma_ij = psi^4 delta_ij with psi = Phi^(1/2)
  exactly, and K_ij = psi^4 [KT delta_ij + (KL - KT) N_i N_j]: the algebraic form of a
  table of format 2, but with N the unit normal of non-concentric spheres (the dust shells,
  radius rho(r), centre C(r)), and psi and KL depending on the direction.
- The difference from the LTB slice with the same M and k (which a format-2 table can
  hold) is first order in the dipole: slopes 1.00 +- 0.01 in eps for psi, rho, K, KL - KT
  and the displacement of the shells' centres; max|dpsi| = 0.0044 eps,
  max|drho| = 1.84 eps rho_b, max|dK| = 1.43 eps H, centre shift 1.93 eps (ball radius 6)
  [VERIFIED, run A-20261119-151501-3e344a4, `figures/fig_dipole_order.png`]. psi barely
  moves; the density and the curvature carry the dipole.

**Answer to "can the code's conformally flat initial data represent it".** The code's
initial data are conformally flat (`nrpic_cf`, `nrpic_cosmo`, the solver of core/id-solver
requires a conformally flat trial metric, `tracks/core/interfaces/id_solver.md` line 52 on
that branch). The Szekeres slice is representable exactly in the continuum: psi, K and
Ahat_ij on the mesh in the coordinates of section 2, and particles at rest. A table of
format 2 (one centre, psi(rbar), KL(rbar), KT(rbar)) holds it only at zeroth order in the
dipole: it misses O(eps) of the density and of K (19 per cent of rho_b and 0.15 H at
eps = 0.1). Representation on the mesh is exact up to the discretisation: the
finite-difference Hamiltonian and momentum residuals of the sampled fields converge at the
order of the stencil (section 5, run A-20261119-152252-2ae031e).

## 3. Initial-data path for the code

**Recommended: `nrpic_cosmo` with `<problem> id = file`** (exists in release core-v0.3;
`athenak/src/pgen/nrpic/nrpic_cosmo.cpp` lines 7-19 and 108-200 [VERIFIED by reading]).
The file holds psi, K, alpha, Ahat_ij at the cell centres of the root mesh with
K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K, which is the exact form above with
K = KL + 2 KT and Ahat_ij = psi^6 (KL - KT)(N_i N_j - delta_ij/3). The box is periodic:
the Szekeres hole (label radius 6, conformal radius 6 because Phi = 1 outside) sits at
the centre of [-8, 8]^3, Einstein-de Sitter fills the rest, which is an exact solution
of the periodic problem (Swiss cheese) [JUDGEMENT: no boundary error at all].
`szekeres/codeid.py` writes the file (NRCOSMO1) and the particles: one particle per cell
at the cell centre, at rest (u_i = 0), m = rho psi^6 h^3. With the cloud-in-cell deposit
the code's energy density is then rho at every cell centre without sampling noise or
cloud smoothing (checked in the first run, section 6). With a cloud of higher order the
deposit smooths by (h^2/8) d^2 per direction (TSC) [JUDGEMENT from the weights].

Not the format-2 table: it cannot hold the slice (section 2). An isolated hole in vacuum
(as `expball`) would need a Cartesian field reader in `nrpic_cf` (a request, not needed
for the test) and outflow faces that are not exact.

**The initial-data solver of core (branch core/id-solver; second pass core/id-solver-2)**
can be put on top of the recommended path, as a test of the solver rather than as the
way to make the data: with `id_solve = true` it holds K and Ahat_ij of the file fixed and
re-solves the Hamiltonian constraint for psi with the code's own deposit; with
`id_vector = true, id_vector_residual = code` it adds L W to Ahat for the momentum
constraint (id_solver.md lines 175-188 on that branch). Because the exact data already
satisfy both constraints in the continuum, the prediction is that the solve changes psi
only by the difference between the continuum and the code's discrete operator: of the
size of the finite-difference residual of section 4 divided by the Laplacian's scale,
order 1e-6 at h = 0.125 [JUDGEMENT: psi correction ~ (psi^5/8) |H| l^2 with |H| ~ 1e-4
(16 pi rho_b) and l ~ 1]. Two cautions from the interface: `nrpic_cosmo id = file` is
listed there as not tested (line 212), and on the torus the mean of the right side of the
vector equation must vanish (the hole has zero momentum, so it does). Starting the solver
from the LTB slice instead (K and Ahat of the spherical table) cannot reach the Szekeres
data: the solver never changes K or the transverse-traceless part of Ahat, so the O(eps)
part of K stays missing (section 2) [JUDGEMENT from the design of the solver].

## 4. Gauge and what is compared

**Primary test: geodesic slicing (alpha = 1, beta = 0 for all time).** Every lapse and
shift driver off: `lapse_oplog = lapse_harmonic = lapse_volume = 0`, `lapse_advect = 0`,
`shift_Gamma = shift_eta = shift_advect = 0` (`athenak/src/z4c/z4c.cpp` 139-157,
`z4c_calcrhs.cpp` 688-735 [VERIFIED by reading]; `lapse_kdriver`, `shift_alpha2Gamma`,
`shift_H` default to 0). Then the dust stays at rest in the code's coordinates (the
geodesic equation with alpha = 1, beta = 0, u_i = 0 has du_i/dt = 0 [BACKGROUND]), the
slices are the slices of the exact solution and the code's coordinates are the comoving
coordinates of the initial map: the exact solution is known at every cell and time, and
the comparison is pointwise. Geodesic slicing ends at the core crunch, tau = 44.454; the
test stops at tau = 40.

Compared at each cell of the dumps (`<particles> field_time*`, `field_constraints = true`
writes E, chi, H, M_i, Khat, Theta_Z4c, alpha; `athenak/src/particles/nrpic_io.cpp`
lines 513-590 [VERIFIED by reading]):

| quantity | exact value at the cell (label r, direction bn from the initial map) |
|---|---|
| K = Khat + 2 Theta_Z4c | -Theta(t, r, bn) |
| E (deposit over sqrt(gamma)) | rho(t, r, bn) |
| chi = (det gamma)^(-1/3) | psi^-4 (rho(t)/rho(t_i))^(2/3) (mass per coordinate cell is constant) |
| H, M_i | 0 (by region: core r < 2.4, shell, outside r > 6) |
| alpha | 1 |

Invariant content: K and E here are the expansion and the rest-frame density of the dust,
both invariants of the dust congruence; chi tracks the volume of each element. A
statement that is special to Szekeres and absent in LTB: on each shell the transverse
eigenvalue KT of K^i_j is the same in every direction while KL and rho are not (needs the
full K_ij in the dump: a request, section 7).

**Secondary test: the production gauge of Track A** (1+log or the conformal-time lapse,
Gamma-driver shift). The code's slices are no longer orthogonal to the dust; compared
are quantities along the particles: the proper time of each particle and the rest-frame
density at the particle (interpolated E with the Lorentz factor removed) against
rho(tau, r, bn) of its label, and the time and place where the core reaches a given
density. Requires the proper time per particle in the trajectory output [TO VERIFY that
it exists; else a request].

## 5. Predicted errors

Inputs (registered runs; numbers relative to 16 pi rho_b = 6 H^2 at t_i):

- Initial-data truncation, L2 over [-7.5, 7.5]^3 (all cells), eps = 0.1, h = 0.47, 0.23,
  0.12, 0.059: Hamiltonian 6.1e-3, 7.2e-4, 6.0e-5, 4.2e-6 with the order-4 stencil
  (orders 3.09, 3.57, 3.84), momentum 4.9e-2, 9.7e-3, 1.1e-3, 9.2e-5 (2.33, 3.10, 3.61);
  maxima 7 to 13 times larger, all in the transition shell (`fig_residual_maps.png`)
  [VERIFIED, run A-20261119-152252-2ae031e]. The LTB limit has the same numbers to 2 per
  cent: the asymptotic regime starts only at h ~ 0.1 because of the profile, not of the
  dipole. The code's own monitor at t = 0 agrees in size (section 6).
- Linear response along elements (silent equations, gradients neglected): a relative
  error 1e-6 of the initial density of an element gives |dK| = 1.1e-6, 2.5e-6, 7.5e-6,
  8.2e-5 H_i at tau = 10, 20, 30, 40 in the core (3.7e-5 at tau = 40 for the inner shell,
  r = 3) and below 5e-7 H_i in the expanding part of the shell and in Einstein-de Sitter;
  an error 1e-6 of the initial expansion grows to 9.5e-5 H_i in the core by tau = 40
  [VERIFIED, run A-20261119-152232-3d29cc1, `fig_error_budget.png`]. So errors are
  amplified about a hundredfold in the collapsing core by tau = 40 and not at all outside.
- Gradient scales in code coordinates: the smallest density scale rho/|grad rho| is 0.55
  at t_i, 0.44, 0.38, 0.30, 0.17 at tau = 10 ... 40; K's global scale falls from 3.0 to
  0.46 (same run). A stencil of order p therefore needs h well below 0.17 by tau = 40;
  the error at fixed h grows like (0.55/0.17)^p, a factor 10 (p = 2) to 100 (p = 4).

Predictions for the code [JUDGEMENT unless a number is quoted from a run]:

1. At tau = 0, E = rho to the float precision of the dump and chi = psi^-4 to 1e-6
   (no deposit error with one particle per cell centre and CIC).
2. alpha = 1 to round-off; particles do not move (u_i = 0 is an exact solution of the
   code's pusher when alpha = 1 and beta = 0) [TO VERIFY in the run].
3. Errors of K, E, chi in the shell converge at second order or better in h (sixth-order
   stencils, Kreiss-Oliger dissipation of the same order, RK4), grow with tau by the
   amplification of the element dynamics (up to 100 in the core by tau = 40) and the
   shrinking gradient scales, and are largest at the edge of the core near tau = 40.
   Resolution needed for per-cent errors at tau = 40 [JUDGEMENT from the two inputs
   above]: h <= 0.06 (256^3 on [-8, 8]^3); 128^3 suffices to tau ~ 20.
4. Cost: 128^3 to tau = 40 is about 1300 RK4 steps on 2.1e6 cells and particles; 256^3
   about 16 times that. On the processors the particle module of core-v0.3 is slow: 32^3
   in one run took 3.2 s a cycle on the loaded machine, and 64^3 in 16^3 MeshBlocks more
   than 100 s a cycle (cost grows with MeshBlocks times particles) [VERIFIED, run
   A-20261119-152010-94a9461]. The convergence series belongs on a card: a few card
   minutes at 128^3 [JUDGEMENT, not measured here].

## 6. First execution (processors, release core-v0.3)

Two registered runs with the recommended path (field file, one particle per cell, CIC,
geodesic slicing, nghost = 4, RK4, CFL 0.25); JOURNAL entries 3 to 6 hold the predictions
and outcomes.

- Run A-20261119-152010-94a9461 (N = 32 to tau = 40; N = 64 stopped after start-up): at
  tau = 0 the code holds the data exactly (K to 5e-16, E to 6e-8 and chi to 3e-8, the
  float32 precision of the dumps) and its constraint monitor over the shell is 9.8e-3
  (N = 32) and 8.6e-4 (N = 64) of 16 pi rho_b, the size of the finite-difference residual
  of section 5. alpha stays 1 to 2e-13. At N = 32 the evolution departs (K off by 15 per
  cent at tau = 10) and turns to NaN between tau = 24 and 28 (`fig_code_geodesic_run1_tau40`).
- Run A-20261119-153832-7097718 (N = 32 and 64 to tau = 2, with and without dissipation):
  every error falls with resolution, by about 3 per halving (order about 1.7 at h = 0.5,
  0.25): K in the shell 3.9e-2 -> 1.3e-2, in the core 2.2e-2 -> 2.4e-3, E and chi
  1.1e-2 -> 3.6e-3 and 7.6e-3 -> 2.4e-3, rms H over the shell 0.30 -> 0.095 of 16 pi rho.
  Dissipation reduces the error. `fig_code_geodesic.png`, `fig_code_geodesic_profiles.png`.

What this establishes: the initial-data path works as designed (no new code needed), the
code converges towards the Szekeres solution at the resolutions that fit on processors,
and the departures at 32^3 and 64^3 are those of an under-resolved transition shell
(smallest density scale 0.55 = 1.1 h at N = 32). What it does not establish: the order of
convergence in the asymptotic range, the behaviour to tau = 40, the convergence in the
particle number (one particle per cell only), other gauges. These need the card series
of section 7.

## 7. Requests and open points

- core: (1) dump the full K_ij and gamma_ij in the field dumps (or as an AthenaK output
  variable list), so that the eigenvalue test (KT uniform on a shell, KL not) can be made;
  (2) say whether the trajectory output carries the particle's proper time (secondary
  test, section 4); (3) the first test of `id_solve` with `nrpic_cosmo id = file` could be
  this hole: field file and particles from `szekeres/codeid.py`, prediction in section 3.
- lead of A-emd-pbh: the card convergence series 64^3, 128^3, 256^3 (under one card-hour
  in total, section 5) after the processor runs of section 6; choose whether eps = 0.1 or a
  larger dipole is the production reference (eps = 0.2 still has margins of 5 and about
  2 [JUDGEMENT from the scaling of the margins with 1/eps]).
- Track B (co-owner of the row): the same files serve B's periodic set-up; the hole can be
  scaled to any H R2 (the model is defined by H, the profile and eps).
