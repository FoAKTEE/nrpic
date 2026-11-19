# JOURNAL of core, work package clump2 (equilibrium clumps with a bulk momentum)

Branch `core/clump-table` (from `core/clump-curvature`), worktree `wt/core-clump2`.
Append-only, newest at the bottom. Predictions are written before a test runs, outcomes
after. Labels: [VERIFIED] read from a source with a locator or measured in a registered
run, [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Units G = c = 1. Times from `date -u`.

## 2026-11-19  session clump2-1 (from 14:22Z)

### Read

- `CLAUDE.md`, charter to "Owners", brief lines 493-553, 688-706, 834-860, decisions
  0010, 0016, 0017, `harness/RULES.md`, `scripts/README.md`.
- `tracks/core/interfaces/moving_clumps.md` and `tracks/core/JOURNAL-clump.md` (first
  pass: Gaussian clumps; open items 1, 2, 5, 6 of its section 8 are this package).
- Track F's request `track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-core__moving-clump-initial-data.md`
  (two equilibrium clumps of 0.05 M, compactness 0.05 to 0.1, with bulk momenta, beside
  a heavy puncture; acceptance: an isolated moving clump keeps its profile for 200 M).
- `core/id-solver:tracks/core/interfaces/id_solver.md` (scalar and vector solve on a
  uniform mesh, one rank, Robin faces; refined meshes and punctures not done, section 7).
- Source: `athenak/src/pgen/nrpic/nrpic_cf.cpp`, `nrpic_clump_curvature.hpp`,
  `nrpic_bowen_york.hpp` (multipole correction tables of punctures, `BYCorrection`),
  `python/nrpic/st_cluster.py` (`STModel`, `_shell_integral`), `sampling.py`
  (`sample_st`), `clumps.py`, `smeared_bowen_york.py`, `bowen_york.py` (`write_table`),
  `problems/ic/make_ic.py`, `problems/st/st_cluster.athinput`, `docs/TESTLOG.md` lines
  72-140 (the stable cluster of the first paper: y_c = 0.819, 10^4 stratified particles,
  dx = M/2, four filter passes; 300 M take 8 minutes on a card with 16^3 MeshBlocks).
- Model numbers, `STModel(0.819).summary()` [VERIFIED, python/nrpic/st_cluster.py]:
  R = 9.9642 M, rbar_s = 8.9362 M, alpha_c = 0.80908, psi_c = 1.10420, E_0 = alpha_s =
  0.89403, M_0 = 1.030106 M.

### Derivation [JUDGEMENT until the checks PA below have run]

**The object.** A static, spherical, isotropic equilibrium: `ds^2 = -alpha_0^2 dt^2 +
psi_0^4 delta_ij dx^i dx^j`, energy density rho, pressure P (static observers), every
particle with conserved energy `E = -u_t = alpha_0 W`. Boosted to first order in V it is
the same spacetime on another slice: `t~ = t + T(x)`, `T -> V.x` at infinity.

**Slice.** In the coordinates (t~, x) the metric is `-alpha_0^2 (dt~ - d_i T dx^i)^2 +
psi_0^4 dx^2`: the spatial metric is psi_0^4 delta_ij up to O(V^2), the shift is
`beta^i = alpha_0^2 psi_0^-4 d_i T`, and `K_ij = (1/(2 alpha_0)) (D_i beta_j + D_j beta_i)`,
`K = psi_0^-6 alpha_0^-1 d_i (psi_0^2 alpha_0^2 d_i T)`. So the slice is maximal (the
`K = 0` the generator assumes) if and only if

    d_i (A d_i T) = 0,   A = (alpha_0 psi_0)^2,   T = (V.n) F(r),
    (r^2 A F')' = 2 A F,   F ~ r at the centre,   F/r -> 1 at infinity.

`T = V.x` (F = r, the plain Lorentz boost of the isotropic coordinates) is not maximal:
`K = V.grad(alpha_0^2 psi_0^2)/(alpha_0 psi_0^6)`, first order in V and in the potential.
Outside the matter `A = (1 - m/r)^2`, m = M/2, and the two solutions are closed forms,
`F_1 = r + m + m^2/r` (the areal radius minus M/2) and `F_2 = 1/(r (r - m))` (checked by
hand: `(r - m)^2 F_1' = (r - m)^3 (r + m)/r^2`, derivative `2 (r - m)^2 (r^2 + m r +
m^2)/r^3 = 2 A F_1`). So `F = F_1 + kappa F_2` outside, with kappa from the match at the
surface.

**Matter on the slice.** The static frame has `u_i = alpha_0 d_i T` relative to the
slice (from `u = -alpha_0 dt = -alpha_0 dt~ + alpha_0 d_i T dx^i`), so with
`w_i = d_i T = V_i w_a + n_i (V.n) w_b`, `w_a = F/r`, `w_b = F' - F/r`:

    Stilde_i = psi_0^6 S_i = psi_0^6 (rho + P) alpha_0 w_i      (first order).

It contains the pressure, the lapse and the slice function; it is not proportional to the
conformal source `rho psi_0^5` that item 1 of section 8 of `moving_clumps.md` proposed
(`Q = -2 r^2 u'/M`): that proposal is withdrawn.

**Curvature for any polar l = 1 momentum density.** For `Stilde_i = V_i s_a(r) +
n_i (V.n) s_b(r)` the traceless `Abar_ij = a (V_i n_j + V_j n_i) + b delta_ij V.n +
c n_i n_j V.n`, `b = -(2a + c)/3`, has the divergence `V_i [a' + (7a - c)/(3r)] +
n_i V.n [a'/3 - a/(3r) + 2c'/3 + 7c/(3r)]`. With `a = A2 + A4`, `c = A2 - 5 A4` the
system decouples (eigenvalues -2 and -4): `(r^2 A2)' = 2 pi r^2 (3 s_a + s_b)`,
`(r^4 A4)' = 2 pi r^4 (s_a - s_b)`. Hence the two lines of the Gaussian case hold
unchanged,

    Abar_ij = 3 Q/(2 r^2) [V_i n_j + V_j n_i - (delta_ij - n_i n_j) V.n]
            + I4/(2 r^4)  [V_i n_j + V_j n_i + (delta_ij - 5 n_i n_j) V.n],
    Q(r)  = 4 pi int_0^r (s_a + s_b/3) r'^2 dr',
    I4(r) = 4 pi int_0^r (s_a - s_b) r'^4 dr',

with these generalised moments (for `s_b = 0` they are those of `moving_clumps.md`). The
total momentum is `P_i = Q(inf) V_i`. The code needs a table of Q and I4 only.

**Particles** (rule `boost` of the generator). Sample the static cluster (x, q, m_0; q the
orthonormal velocity, `u^s_i = psi_0^2 q_i`), then
- momentum: `u~_i = u^s_i + E w_i(x)`, `E = alpha_0 W` (the covariant components in the
  coordinates of the new slice, `u~_i = u_i - u_t d_i T`: exact),
- mass: `m~ = m_0 (1 + w.xdot)`, `xdot^i = alpha_0 q^i/(psi_0^2 W)` the coordinate
  velocity: the weight with which a world line crosses the new slice (relativity of
  simultaneity; the Jacobian of `u -> u + E(x,u) w` at fixed x is `1 + w.dE/du`).
For any isotropic static distribution the momentum density of these particles is
`psi_0^6 (rho + P) alpha_0 w_i` exactly (terms odd in q vanish; the rule is linear in w),
so the curvature above solves the momentum constraint in the continuum for whatever w is
used. Without the weights the pressure term is missing (`rho` instead of `rho + P`).

**Speed.** The parameter of the generator is the speed v of the clump; the linear rule is
applied with `V = W_v v` (so that a cold clump moves exactly at v) and the momentum is
`P = Q(inf) W_v v`. Expected (check PA2): `Q(inf) = M`, the ADM mass of the static
cluster, because the data are a slice of the boosted static spacetime to first order,
whose ADM momentum is M V. With `F = r` it would be `int psi^6 (rho + P) alpha d^3x`,
which is not M (the Tolman mass has `rho + 3P`).

**Hamiltonian constraint at second order.** With the rule above, `W~ = (1 + psi^-4
|u~|^2)^(1/2)` and `psi = psi_0 + dpsi`, averaging over the directions of q
(`wbar = (alpha_0/psi_0^2) w`):

    D~ = sum m~ W~ delta = psi_0^6 [rho + (rho + P) wbar^2/2 - 6 P dpsi/psi_0] + O(V^4),

so `lap psi = -2 pi D~/psi - psi^-7 Abar^2/8` gives, linear in dpsi,

    lap dpsi - 2 pi psi_0^4 (rho + 6P) dpsi
        = -pi psi_0^5 (rho + P) wbar^2 - psi_0^-7 Abar_ij Abar_ij/8.

The right side has l = 0 and l = 2 about V (`wbar^2` and `Abar^2` are `f(r) + g(r) mu^2`),
so `dpsi = V^2 [y_0(r) + y_2(r) P_2(mu)]` from two radial equations: the "spherical radial
solve per clump" of the task. The table format of the puncture corrections (`mp1`,
multipoles about an axis) carries it; the code adds it to psi. The particles are not
changed by the correction (their rule uses psi_0 and alpha_0 only). Not included: the
Lorentz contraction of the profile and the part of the metric that is not conformally
flat (both O(V^2), no constraint violation), terms O(V^4), and cross terms with other
bodies.

Why not the elliptic solver of `core/id-solver` here [JUDGEMENT]: it works on a uniform
mesh on one rank with Robin faces; the clump runs need refined meshes and, for Track F, a
puncture. For an isolated clump the radial solve is exact to the stated order and costs
nothing in the code. What the mesh solver would add, once it has refined meshes and
punctures (its section 7): the cross terms `Abar_c : Abar_j` of several bodies, the tidal
variation of the other bodies' psi across a clump, and the sampling noise of the actual
particles.

**Shift.** With zero shift the coordinate velocity of the matter is `alpha_0^2 psi_0^-4 w`:
0.44 w at the centre of the y_c = 0.819 cluster (alpha_c^2/psi_c^4 = 0.6546/1.4866), V
far away. In coordinates that move with the clump the shift is
`beta^i = -(V^i - alpha_0^2 psi_0^-4 w^i)`, which vanishes far away as 3m V/r. Option
`comp<c>_boost_shift = true` sets it (per clump, from its own alpha_0, psi_0 and F).

**Several bodies.** Near clump c the others add a nearly constant `Lambda_c - 1` to psi.
`psi = Lambda psi^(Lambda^2 x)` is the isolated solution in the coordinates
`x^ = Lambda^2 x`: positions shrink by Lambda^2, `u(r) = Lambda u^(Lambda^2 r)`,
covariant momenta `u~_i = Lambda^2 u^_i`, `P = Lambda^2 P^`, `Q(r) = Q^(Lambda^2 r)`,
`I4(r) = I4^(Lambda^2 r)/Lambda^4`, rest masses unchanged. The generator applies this
scaling, and multiplies each particle mass by the factor that makes its `m W/psi` equal to
the isolated one with the actual psi of all bodies (so the Hamiltonian constraint keeps
only the cross terms of the curvatures).

### Design [JUDGEMENT]

1. New header `athenak/src/pgen/nrpic/nrpic_clump_table.hpp` (namespace
   `nrpic_tclump`): reader of the "boost table" (`# format = bst1`, columns `r Q I4 ba bb`
   on the uniform grid of the radial tables; header keys `pmass` (momentum per unit
   coordinate velocity), `ext_m`, `ext_kappa` for the closed forms beyond the last row),
   curvature, shift, and the correction of psi through `nrpic_by::BYReadTable` and
   `BYCorrection` (table `mp1`).
2. Options on a component of type `table` (format 1): `comp<c>_boost_file`,
   `comp<c>_p1..3`, `comp<c>_corr = table` with `comp<c>_corr_file`
   (`comp<c>_corr_axis1..3` as for punctures; default the momentum), `comp<c>_boost_shift`.
   Read only when `comp<c>_boost_file` exists.
3. Hooks: `nrpic_cf.cpp` (include, reader call, correction in the sum of psi, curvature
   block, shift) and one line of `BYRead` in `nrpic_bowen_york.hpp` (a table component
   with a boost file is not a puncture).
4. Python: `python/nrpic/boosted_cluster.py` (`BoostedST`: F, moments, shift, correction,
   particle rule, table writers, scaling by Lambda), `problems/ic/make_ic.py boosted`.

### Predictions PA for the checks without simulation (written 14:50Z, before the module runs)

Model y_c = 0.819, M = 1. Script `tracks/core/analysis/clump2/check_boost.py`.

- PA1 (slice function). The interior solution matches the exterior closed forms with a
  kappa that is constant: `F - F_1 - kappa F_2` evaluated from an ODE integration
  continued to 4 rbar_s is below 1e-8. `w_a(0) = F'(0)` is above 1 (the lapse is lowest at
  the centre, so `A` grows outward and the gradient of T concentrates inside; I expect
  1.05 to 1.3). Refuted if the residual is above 1e-6.
- PA2 (momentum). `Q(inf)/M = 1` to 1e-7 with the maximal F; with `F = r` it is not 1 (I
  expect a few per cent below or above; the sign I do not predict). Refuted if
  `|Q(inf)/M - 1| > 1e-5`: then `Stilde_i = psi^6 (rho + P) alpha d_i T` or the slice
  equation is wrong.
- PA3 (Einstein equations). `Abar_ij` from the moments equals `psi_0^6 (Lbar beta)_ij/
  (2 alpha_0)` with `beta^i = alpha_0^2 psi_0^-4 d_i T`, built by finite differences of
  the model functions and of F, at points inside and outside the matter: relative
  difference below 1e-5 of the largest component (limited by the differencing).
  This compares the momentum constraint solved with the matter source against the
  geometry of the static solution: it can fail through the sign of w, the factor
  `rho + P`, the lapse factor, or the moments. Refuted above 1e-3.
- PA4 (divergence). `d_j Abar_ij = 8 pi Stilde_i` by sixth-order differences at points
  inside: below 1e-6 of the largest source.
- PA5 (particles). For a stratified sample of 10^5 particles, `sum m~ u~_i` over
  `Q(inf) V` is 1 within 3 sigma of its sampling error, and the radial profile of
  `sum m~ u~_x` in 20 shells follows `Q(r)` within the sampling error; without the weights
  the total is low by `int P`-fraction (I expect 3 to 8 per cent).
- PA6 (second order). The mass the correction adds, `2 x monopole`, is `M V^2/2` times a
  factor 1 + O(M/R): I expect 0.9 to 1.3. The direction-averaged `D~` of the rule,
  computed exactly for the monoenergetic model by quadrature, differs from the
  second-order form by less than 2 V^2 times the second-order term at V = 0.1 and 0.31.
  The residual of the radial equations (finite differences of the written table) is below
  1e-4 of the largest source away from the surface.

### Outcome of PA (run `core-20261119-144026-3d7d4e7`, 14:40Z; `analysis/clump2/check_boost.json`, `figs/fig_boost_reference.png`)

The first execution of the module was this registered run. Its outputs went to a
directory literally named `$NRPIC_RUN_DIR` in the worktree (I quoted the variable on the
command line; the launcher does not expand it); I moved them into the run directory
after the run had been closed, so its `sha256sums.txt` lists `run.log` only. The scripts
now read `NRPIC_RUN_DIR` from the environment.

- PA1 HELD. Continuing the interior solution through the vacuum with the ODE agrees with
  `F_1 + kappa F_2` to 3.2e-13 out to 4 rbar_s; kappa = -5.98881. `w_a(0) = 1.07692`,
  `w_a(rbar_s) = 1.05019`. With zero shift the matter at the centre starts with the
  coordinate velocity `alpha_c^2 psi_c^-4 w_a(0) V = 0.4742 V`.
- PA2 HELD. `Q(inf)/M - 1 = -9.4e-15` with the maximal slice; the plain boost `F = r`
  gives `Q(inf)/M = 0.94729` (5.3 per cent low). So the momentum of the data is M V to
  round-off: the source `psi^6 (rho + P) alpha grad T`, the slice equation and the
  exterior match are consistent with the ADM momentum of the boosted spacetime.
- PA3 HELD. Curvature from the moments against `psi^6 (Lbar beta)/(2 alpha)`: 4.2e-11
  inside, 1.1e-11 outside, of the largest component 9.88e-3 (V = 0.3); `alpha K` of the
  slice 1.3e-13. For the plain boost `max |alpha K| = 2.6e-3`: not maximal, as derived.
- PA4 HELD. Divergence against `8 pi Stilde_i`: 6.0e-11 of the largest source.
- PA5 HELD for the rule, FAILED in one number. 10^5 stratified particles:
  `sum m~ u~_x/(Q(inf) V) = 1.00004 +- 0.0022`; enclosed momentum in 20 shells within
  1.9e-3 P of `Q(r) P`. Without the weights the total is 0.97206: 2.8 per cent low, just
  outside the 3 to 8 per cent I wrote (the pressure share of `rho + P` in this model).
- PA6 HELD. Added mass `2 x monopole = 0.98379 M V^2/2`; `y_0(0) = 0.03568`; the exact
  direction average of `m~ W~` differs from the second-order form by 1.7e-3 (V = 0.1) and
  1.6e-2 (V = 0.31) of the second-order term; residual of the radial equations on the
  written table 3.9e-7 (l = 0), 5.5e-8 (l = 2) of the largest source; tails of the table
  0.963 and 1.679 (l = 0 is not yet the pure monopole at 6 rbar_s: the r^-2 particular
  part). The quadrupole `y_2` is below 2 per cent of `y_0` everywhere (figure).
- For v = 0.3 (`V = W v = 0.31449`): `P = 0.31449`, `M_ADM = 1.04865` with the
  correction, against `W_v M = 1.04828` for an exact boost: 3.7e-4 M apart.

After PA the boost table was changed to hold `Q/r^3` and `I4/r^5` (finite at the centre,
so that the cubic interpolation of the code needs no special case near r = 0); below
0.02 rbar_s a quadratic through the central value continues the quadrature. Checked by
hand at r = 0.1: 3.83916e-3 both ways, 2.303456e-3 against 2.303456e-3.

### Source written (15:00Z to 15:20Z), smoke runs (not registered, no number used)

`athenak/src/pgen/nrpic/nrpic_clump_table.hpp`, hooks in `nrpic_cf.cpp` and `BYRead`;
`problems/ic/make_ic.py boosted`; `problems/tests/clump_table_static.athinput`. The
processor and card executables build. One smoke run at 64 cells with 10^4 stratified
particles (v = 0.3, correction and shift on): the log prints "curvature of 1 moving table
component(s), 1 correction(s) of psi, comoving shift on"; psi^4 of the dump equals the
Python reference to 5.6e-8 (single precision of the dump). No other number is taken
from it.

### Predictions TB for the data at t = 0 on the mesh (written 15:25Z, before the runs)

Cluster y_c = 0.819, M = 1, at the origin of the box [-16, 16]^3 (`nghost = 4`, linear
cloud, four filter passes with compensation: the setting of the first paper's cluster
runs), 32, 64, 128 cells (dx = 1, 0.5, 0.25), processors. Particles: the quiet sample
(lattice of spacing 0.25 with weights `rho_0 psi_0^6 h^3`, six momenta per site: no
sampling noise and exact first and second moments at every site), 1.15e6 particles;
v = 0.1 and 0.3 (`V = W v = 0.10050, 0.31449`), and the static sample on the same sites.
Cases per v and resolution: `none` (K_ij = 0), `curv` (curvature of the boost table with
`comp0_p = sum m u`), `corr` (curvature and correction of psi). Norms as the history file
defines them, restricted to r < 14 ("interior"; the layer at the outflow faces of
`JOURNAL-clump.md` T1 is left out), computed from the dumps by
`analysis/clump2/boost_static_check.py`. Continuum numbers from
`analysis/clump2/predict_boost.py` (quadrature of the reference; printed at 15:22Z):
v = 0.1: M-norm 0.036089, Mx-norm 0.042326, second-order H-norm 3.1460e-3 (matter part
2.777e-3, curvature part 5.24e-4); v = 0.3: M-norm 0.112924, Mx-norm 0.132441,
second-order H-norm 0.030803 (0.027188, 5.132e-3); norm of the matter term 16 pi E:
0.90873.

- TB1 (momentum constraint, `none`). Interior M-norm equals the continuum value within 3
  per cent at 64 and 128 cells (the filter lowers it at 32 cells, as in T1 of the first
  pass: within 10 per cent there). Ratio v = 0.3 over v = 0.1: 3.129 within 1 per cent.
- TB2 (momentum constraint, `curv`). The residual is what the cloud and the filter do to
  the profile, plus the surface, where the density ends as (rbar_s - r)^(1/2): ratio to
  `none` between 0.03 and 0.12 at dx = 1, 0.008 and 0.05 at dx = 0.5, 0.002 and 0.02 at
  dx = 0.25, falling by a factor 1.5 to 6 per halving [JUDGEMENT: smoothing width about
  0.75 dx against a density scale of about 3 M gives (w/L)^2 = 0.06, 0.016, 0.004; the
  edge adds a first-order term]. The ratio is the same at v = 0.1 and 0.3 within 5 per
  cent (linear). The curvature term alone, `M_x(curv) - M_x(none)`, has the Mx-norm of
  the continuum within 1 per cent at 128 cells (it does not pass through the deposit).
  Refuted if the ratio does not fall with resolution or is above 0.3 anywhere.
- TB3 (Hamiltonian, second order). With `D_H(case) = H(case) - H(static)` cell by cell:
  the interior norm of `D_H(curv)` equals the continuum second-order norm (3.146e-3,
  0.030803) within 5 per cent at 64 and 128 cells; ratio v = 0.3 over 0.1: 9.79 within 3
  per cent. With the correction, `|D_H(corr)|/|D_H(curv)|` is below 0.15, 0.08, 0.05 at
  dx = 1, 0.5, 0.25 for v = 0.3 (fourth order 1.6e-2, and the smoothing of the
  second-order matter source by the deposit, which the correction does not know of) and
  not larger at v = 0.1; the projection `<D_H(corr), D_H(curv)>/<D_H(curv), D_H(curv)>`
  is within 0.05 of zero (a correction of the wrong sign gives 2, none gives 1).
  Refuted if the ratio is above 0.3 or the projection outside +-0.1.
- TB4 (whole-box history norms, the numbers a user sees). At 64 cells, v = 0.3: H-norm
  of `corr` within 2 per cent of the static cluster's H-norm (the deposit error of the
  matter, the same in both), H-norm of `curv` above it; M-norm of `curv` and `corr`
  equal within 1 per cent. I do not predict the static H-norm itself.
- TB5 (fields). In the case `corr` at 64 cells with `comp0_boost_shift = true`: psi^4,
  K_ij and beta^i of the dumps equal the Python reference at every cell centre to 2e-6
  of the largest value (single precision of the dumps, cubic interpolation of the
  tables); K = 0 to the same accuracy.
- TB6 (the sample of the evolution: 10^4 stratified equal-mass particles, v = 0.3, 64
  cells). The momentum-constraint norm is sampling noise: the curvature lowers M-norm2
  by the smooth part only, `M-norm2(none) - M-norm2(curv) = 0.112924^2 = 0.01275` within
  30 per cent, and the projection of `M_x` on the smooth field `-8 pi psi^-6 Stilde_x`
  goes from 1.0 +- 0.1 to 0.0 +- 0.1. The H-norm does not change by more than 2 per
  cent between `none`, `curv` and `corr` (noise dominates; the second-order norm 0.031 is
  small against it).
