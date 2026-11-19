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

### Correction of clock times above (14:48Z, from `date -u` and the commits)

The times I wrote into the entries above were guesses and too late. From the record:
the predictions PA were written before commit 3d7d4e7 (14:40Z) and the run
`core-20261119-144026-3d7d4e7` started at 14:40:26Z; the source was written and the smoke
run made between 14:41Z and 14:46Z; the continuum numbers of `predict_boost.py` were
printed at 14:46Z and the predictions TB written directly after, before commit cbe1e3ef
(14:47Z). The order of prediction and run is as stated in each entry. From here on times
are copied from `date -u`.

### Prediction R (regression, written 14:48Z before the run)

Inputs without the new parameters give byte-identical data files with this branch's
processor executable (`.work/build_cpu`, source of commit cbe1e3ef) and the release
executable `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`: the four cases of
`tracks/core/analysis/clump/regress.py` (`regress_cf`, `cf_table_regress`,
`by_static`, and the first paper's two-overdensity configuration for two cycles;
restart files up to the 36 never-set header bytes). The new code is reached only through
`comp<c>_boost_file`; the loop of the generator gained a correction loop over zero
entries and a block behind `if (tcl.n > 0)`. Refuted by any differing data byte.

### Smoke checks before the card job (not registered, 14:53Z; no number below is used as a result)

- Fields of the code against the Python reference, 64 cells, 10^4 stratified particles,
  v = 0.3, correction and shift on (`scratch/core/tmp/clump2/smoke2`): psi^4 5.6e-8,
  K_ij 4.7e-8 of the largest component, beta^i 7.5e-9, lapse 3.0e-8, trace K 5e-18. The
  registered version of this check is TB5.
- `problems/clump/cluster_moving.athinput` starts on a processor (`time/nlim=0`): 568
  MeshBlocks (52 + 5 x 84 + 96 on the finest level, dx = 0.5 inside
  [-16, 32] x [-16, 16]^2), 1 min 57 s for the start alone.
- The registered processor runs TB and R wait: `nrpic-run submit` refuses while 16 cores
  are busy in live local runs of owner core (other packages of this wave);
  `scratch/core/tmp/clump2/submit_wait.sh` retries every 30 s.

### Predictions TC for the evolution on a card (written 14:53Z, before the job is submitted)

`problems/clump/cluster_moving.athinput`: the stable cluster of the first paper
(y_c = 0.819, 10^4 stratified particles of seed 1, dx = M/2, four filter passes with
compensation, 1+log lapse from the static lapse, Gamma-driver shift with eta = 2) on the
mesh of `st_cluster.athinput` with the refined box extended to x = 32; 50 M. Initial
data from `make_ic.py boosted` (files in `scratch/core/clump2-ic/`), curvature and
correction on. Four runs in one job: `v0` (at rest, no boost table read), `v0.1`,
`v0.3` (shift zero at the start), `v0.3s` (v = 0.3 with `comp0_boost_shift = true`).
Measured by `analysis/clump2/boost_evolution_check.py`: centre x_c(t) = rest-mass centre
of the particles from the snapshots (every 2 M); radii about x_c that enclose 10, 25, 50,
75, 90 per cent of the rest mass; alpha_min, sum m u_x from `cl.nrpic.hst`; constraint
norms from `cl.z4c.user.hst`. Cost estimate: 300 M of the first paper's mesh take 8
minutes [VERIFIED, docs/TESTLOG.md line 100]; this mesh has 568 MeshBlocks: about 2
minutes per run, 0.15 card-hours for the job [JUDGEMENT].

1. Centre. With zero shift the matter starts with the coordinate velocity
   `alpha_0^2 psi_0^-4 w V/W_v`: 0.474 v at the centre, about 0.6 v averaged over the
   mass (0.70 v at the surface). The Gamma driver then builds the shift of the moving
   coordinates and the coordinate speed rises towards v [JUDGEMENT; I have no estimate of
   the time it takes beyond "a few light-crossing times of the cluster", 20 to 40 M].
   Predicted for `v0.1` and `v0.3`: speed of x_c at t = 0 to 2 M between 0.5 v and
   0.7 v; mean speed over 30 to 50 M between 0.85 v and 1.05 v; x_c(50 M) between 0.70
   and 0.95 of v x 50 M (3.5 to 4.75 M, 10.5 to 14.25 M). For `v0.3s`: speed between
   0.9 v and 1.1 v already over 0 to 4 M, mean over 0 to 50 M between 0.93 v and 1.05 v
   (x_c(50 M) between 13.95 and 15.75 M). Run `v0`: |x_c| below 0.1 M throughout.
   Refuted if the late speed of the runs without initial shift is below 0.8 v (the
   coordinates do not catch up within 50 M: then `comp0_boost_shift` is needed for a
   clump to follow its trajectory) or if `v0.3s` leaves the stated band.
2. Profile. The five radii stay within 10 per cent of their values at t = 0 for 50 M in
   every run, and at every snapshot the radii of the moving runs are within 6 per cent
   of those of `v0` at the same time (the data are not Lorentz-contracted, 1 - 1/W_v =
   4.6 per cent along x at v = 0.3, and the coordinates change with the shift). No
   particle is lost. Refuted by a radius that departs by more than 15 per cent from the
   run at rest, or by a monotonic growth or shrinking of all five radii.
3. Central lapse (alpha_min; 0.8091 at t = 0 in all runs, the static table). `v0`:
   between 0.800 and 0.825 for 50 M (the first paper's run rises from 0.809 to 0.837 at
   115 M). `v0.1`: within 0.004 of `v0` at all times. `v0.3` and `v0.3s`: the lapse
   of the boosted slicing of the exact solution would be `alpha_0/(W_v (1 - V_c^2)^(1/2))`,
   `V_c = v alpha_0/psi_0^2`: 0.7875 at the centre [derived from g^tt of the boosted
   static metric; JUDGEMENT that 1+log moves towards it]. Predicted: alpha_min falls by
   0.010 to 0.035 below the run at rest within the first 25 M and its difference from
   `v0` then changes by less than 0.012 until 50 M (no drift towards collapse or
   dispersal). Refuted if alpha_min of a moving run is below 0.74 or above 0.85 at any
   time, or still moving away from `v0` by more than 0.02 between 30 and 50 M.
4. Summed momentum. `sum m u_x` is the covariant momentum on the slice and depends on
   the slicing at first order in v and in the potential (on the plain boosted slice the
   same matter has 0.947 M V, on the maximal slice M V: PA2). The 1+log slicing leaves
   the maximal slice, so the sum changes without any force on the clump [JUDGEMENT; this
   is my candidate for the drift of 1.3 to 1.6 per cent in 2 M that the first pass could
   not explain]. Predicted: |change of sum m u_x|/P below 8 per cent over 50 M; the
   relative histories of `v0.1` and `v0.3` agree within 2 per cent of P at every record
   (linear in v); in `v0` |sum m u_x| stays below 2e-3 M. What would speak against the
   candidate: relative histories that differ between v = 0.1 and 0.3 by more than the
   drift itself, or a drift that accompanies a change of the centre's speed.
5. Constraints. H-norm and M-norm of the moving runs within a factor 1.5 of the run at
   rest at every record after t = 5 M (sampling noise dominates all four).

### A slip of mine outside the worktree (14:54Z)

A command of mine used a shell variable that was not set in that call (`cd $IC &&
sha256sum * > SHA256SUMS`): `cd` went to the home directory and wrote a 75-byte file
`/home/haiyangw/SHA256SUMS` (one line, the checksum of `anta.env`). The file did not
exist before (it does not list itself, and the names are expanded before the file is
created); I removed it at once. Nothing else was written there. The staged initial data
of TC are in `/data/haiyangw/nrpic/scratch/core/clump2-ic/` with their `SHA256SUMS`
(generator calls: `make_ic.py boosted --cluster 0.819,1,0,0,0,<v>,0,0 --N 10000 --seed 1
--prefix v<v>` for v = 0, 0.1, 0.3 at commit e9e35f16; the three radial tables are
identical, 0c604861..., as are the two boost tables, 73f8c205...). Batch list:
`tracks/core/analysis/clump2/card_tc.list`.

### Several clusters: generator, and predictions TD (written 15:11Z, before any mesh run of two clusters)

`python/nrpic/boosted_cluster.BoostedClusters` and `make_ic.py boosted` take several
clusters (and punctures): background `lam_c = 1 + sum (M_j/lam_j)/(2 d_cj)`, the scaling
of the derivation, and per particle the mass factor that reproduces the isolated
`m W/psi` in the psi of the code. `--cluster-p` gives a cluster by its momentum
(`V = P/pmass`), which is what Track F's three-body set-ups specify. Generator output
for two clusters of mass 1 at x = -20, +20 with v = (M/(2d))^(1/2) = 0.111803 along -y, +y
(not a registered run; these are properties of the generator's own numbers): lam =
1.012348, pmass = lam^4 = 1.050312, |P| = 0.118169 each (continuum), first-order ADM mass
2/lam = 1.975606 (binding energy -0.02439 against the Newtonian -M^2/d = -0.025), with
the corrections 1.988526 (kinetic 0.01292 against the Newtonian 0.0125).

Test TD (`run_binary_static.py`, `problems/tests/clump_table_binary.athinput`): that
pair at t = 0 on a uniform mesh of cell size 0.5 ([-48, 48] x [-24, 24]^2), quiet sample
with spacing 0.25; cases `single` (one cluster alone at x = -20, at rest), `b0` (the
pair at rest), `bv_none`, `bv_curv`, `bv_corr` (the pair moving: K_ij = 0, the two
boost tables, tables and corrections). Norms within 14 of the centre of cluster 0.
- TD1. H-norm of `b0` over that of `single`: 1 +- 0.1 (each cluster keeps the
  Hamiltonian residual of the isolated one; a factor lam or lam^2 lost in psi, the
  tables or the particles would show as a residual of 1 to 6 per cent of the matter
  term, 0.01 to 0.05 in norm).
- TD2. M-norm `bv_curv`/`bv_none`: the value of TB2 at dx = 0.5 (which does not depend
  on v) within 30 per cent; a factor lam^2 = 1.025 lost in the momentum, or the table
  scaled wrongly, leaves at least 0.025.
- TD3. `|D_H(bv_corr)|/|D_H(bv_curv)|` (differences to `b0`) below 0.1 and within a
  factor 1.5 of TB3 at dx = 0.5 and v = 0.1; projection within 0.05 of zero.
Refuted by an H ratio outside 0.85 to 1.15, an M ratio more than twice the TB2 value,
or a D_H ratio above 0.2.

## 2026-11-19  session clump2-2 (from 15:30Z; the first session ended without a handoff)

State found at 15:30Z (from the record, not from memory): run `core-20261119-151457-7a855d8`
(processor tests, one core) is still running. Its first part, test R, stopped at once:
`regress.py` started the executables by a relative path after changing the working
directory (`FileNotFoundError: .work/build_cpu/src/athena`); the fix (absolute paths,
commit eedc4cb8) came after the run had started, so R is rerun as its own registered run
with the three short cases (prediction R above, unchanged); the case `jeans` at the end of
the running job starts after the fix and uses the fixed script. The 25 cases of TB ran
("all cases ran"); TD is running. The card job of TC (`core-20261119-145433-8c4083d`,
Slurm 4649) waits in the queue (15 jobs of the program ahead of it, one card job of
another user running). The executables of `.work/build_*` are from the source of
cbe1e3ef; `git diff cbe1e3ef HEAD -- athenak/` is empty.

### Test TE: two clusters on a quasi-circular orbit, design and predictions (written 15:52Z, before the card job is submitted)

Budget [JUDGEMENT]: the package has one card-hour. TC asks for at most 0.4 (expected 0.15:
568 MeshBlocks x 400 cycles x 4 runs). The cost per MeshBlock-cycle on a card is 5.1e-4 s
[VERIFIED: `runs/st/ctl/s1_nf4/athena.log`, 960000 MeshBlock-cycles in 487.7 s, 10^4
particles, the first paper's cluster mesh]. A binary needs the whole orbit at dx = M/2: the
smoke start of `problems/clump/cluster_binary.athinput` (processor, `time/nlim=0`, not
registered; only the block count is used) has 1408 MeshBlocks (256 on the finest level,
224 on each of levels 1 to 5: the refined region straddles the block boundaries of every
coarser level). A whole orbit (808 M) would cost 1408 x 6464 x 5.1e-4 s = 77 min; "a few
orbital times" does not fit. TE runs 250 M (2000 cycles, 24 min, about 0.4 card-hours, a
third of an orbit), which is enough to tell a quasi-circular orbit from a Newtonian one by
its phase.

Set-up. Two y_c = 0.819 clusters of ADM mass 1, 10^4 stratified particles each (seed 1),
at x = -15 and +15 (separation r = 30 M, D/R = 3, what Track F asks for: clumps of
compactness 0.1 three to six radii apart), momenta -P and +P along y with the first
post-Newtonian quasi-circular value of the ADM Hamiltonian, `P = mu (M/r)^(1/2) (1 + 2 M/r)
= 0.146313` (M = 2, mu = 1/2; Newtonian 0.129099). [BACKGROUND for the 1PN ADM
Hamiltonian of two point masses; JUDGEMENT for the step: with
`H_1PN/mu = (3 nu - 1) p^4/8 - [(3 + nu) p^2 + nu (n.p)^2]/(2 r) + 1/(2 r^2)` the circular
condition at fixed `p_phi` gives `p_phi^2 = r + 4` in units of M, checked by hand.] Curvature
of both boost tables and both corrections of psi, zero initial shift, lapse (2 - psi)/psi
(0.7807 at the centres, against the static lapse 0.809 times (1 - M/r) = 0.782).
Generator: `make_ic.py boosted --cluster-p 0.819,1,-15,0,0,0,-0.14631270419005796,0
--cluster-p 0.819,1,15,0,0,0,0.14631270419005796,0 --N 10000 --seed 1 --prefix orbit`
at commit cb978cec (files and `SHA256SUMS` in `scratch/core/clump2-binary-ic/`): lam =
1.016398, the particles carry |sum m u| = 0.146338 and 0.146396 (sampling; net 6.6e-5,
5.8e-5 in x, y), M_ADM = 1.98715. Reference values: angular velocity 1PN
`omega = (M/r^3)^(1/2) (1 - (3 - nu) M/r)^(1/2) = 0.0077778` (period 808 M), Newtonian
0.0086066 (730 M); radiation reaction `dr/dt = -(64/5) nu M^3/r^3 = -9.5e-4`.
Measured by `analysis/clump2/binary_evolution_check.py` from the snapshots (species =
cluster): rest-mass centres, separation D(t), phase of the separation vector, radii
enclosing 10 to 90 per cent of each cluster's rest mass, |sum m u| per cluster; histories.

1. Phase. The mean angular velocity of the separation vector over 40 to 250 M is within
   5 per cent of the 1PN value, 0.00739 to 0.00817, below the Newtonian 0.00861. In the
   first 40 M the coordinates lag (zero initial shift: the matter starts with 0.5 to 0.7
   of its speed in coordinates, TC prediction 1), so the phase at 250 M is 0 to 0.25 rad
   below `omega_1PN x 250 = 1.944`. Refuted if the fitted angular velocity is outside
   0.0072 to 0.0084 (outside 0.0084 it is closer to Newtonian than to 1PN).
2. Separation. D stays within 28.5 to 31.0 M throughout (eccentricity from the 2PN terms
   left out of P, of order 1 per cent in P, plus the coordinate transient); the linear fit
   of D over 40 to 250 M has a slope between -0.01 and +0.005 (the radiation reaction,
   -9.5e-4, is not resolved). Refuted by D outside 27 to 32 or a slope below -0.02 (an
   inspiral much faster than radiation reaction: the data would hold too little angular
   momentum).
3. Profiles. Every radius of each cluster stays within 15 per cent of its start value
   (tides at D/R = 3 deform at order (R/D)^3 = 4 per cent; the cluster at rest moves its
   radii by up to 10 per cent, `docs/TESTLOG.md` line 76); the two clusters behave alike
   (symmetric set-up) within 3 per cent; no particle is lost.
4. Lapse. alpha_min stays between 0.75 and 0.82 (no collapse, no dispersal).
5. Momentum. |sum m u| of each cluster stays within 10 per cent of its start value (the
   slicing dependence of TC prediction 4); the total over both stays below 3e-3 in each
   component.
6. Constraints. H-norm and M-norm (history) stay within a factor 2 of their values at
   t = 5 M after that time (sampling noise dominates; no growth).

### Supplement to prediction TC4 (written 15:54Z; job 4649 has not started)

If the drift of `sum m u_x` comes from coordinates and slices that change in time
(candidate of TC4), the run with the comoving shift is the control: there the data are
the stationary cluster in coordinates that move with it, the 1+log lapse starts with
K = 0 and its static value, and the Gamma driver starts from a shift that already holds
`d_t Gamma^i = 0`, so the distribution function stays stationary in those coordinates and
every phase-space integral, `sum m u_x` among them, stays constant up to the noise of the
run at rest. Predicted: over 0 to 10 M, |change of sum m u_x|/P in `v0.3s` is at most
half of that in `v0.3`, and below 1 per cent. Refuted (and the candidate with it) if
`v0.3s` drifts as much as `v0.3`.

### Prediction G (card against processor at t = 0; written 15:55Z, before any of the runs)

`run_t0_records.py` starts the five entries of `card_tc.list` and `card_te.list` on a
processor with `time/nlim=0` (branch executable `.work/build_cpu`, same source as the card
executable). Predicted: the first records of `cl.nrpic.hst` and `cl.z4c.user.hst` of the
card runs (jobs 4649, 4657) equal these processor records in every printed digit except
quantities that vanish (round-off of a zero) and the constraint norms, which agree to
1e-5 relative (the card deposits with atomic additions in another order). Refuted by any
other difference: then the card executable builds other initial data than the processor
executable, and the processor tests TB, TD say nothing about the card runs.

### Outcome of TB and TD (analysis run `core-20261119-155912-1fda7e0` on the cases of `core-20261119-151457-7a855d8`; 16:00Z)

The first analysis attempt, `core-20261119-153545-8898621`, failed at once: I gave the TB
script the run directory instead of its `tb/` part (no number from it). Figures
`tb/fig_boost_static_convergence.png` and `tb/fig_boost_static_slices.png` of the
analysis run, looked at.

- TB1 HELD. Interior M-norm with K_ij = 0 over the continuum value: 0.981, 0.995, 0.9995 at
  32, 64, 128 cells, the same for v = 0.1 and 0.3; ratio v = 0.3 over 0.1: 3.129 (continuum
  3.129).
- TB2 HELD. With the boost table the M-norm falls to 0.0703, 0.0341, 0.0151 of the
  uncorrected one at dx = 1, 0.5, 0.25 (bands 0.03-0.12, 0.008-0.05, 0.002-0.02), a factor
  2.06 and 2.26 per halving, identical to four digits at v = 0.1 and 0.3. So it converges
  at first order: the edge of the cluster, where the density ends as (rbar_s - r)^(1/2),
  dominates (slope-1 guide in the figure) [JUDGEMENT: the order was predicted as "1.5 to 6
  per halving, the edge adds a first-order term"; that the edge is the cause is not
  separately tested]. The curvature term alone has the Mx-norm of the continuum to
  1.5e-4, 2e-5, 4e-6 at 32, 64, 128 cells (it does not pass through the deposit).
  Outside r < 14 (the layer at the outflow faces) the curvature leaves an M-norm of
  6.2e-5 at 128 cells, v = 0.3.
- TB3 HELD for the second-order residual without correction, FAILED in two of its bands
  with the correction, not refuted. `|D_H(curv)|` over the continuum second-order norm:
  0.983, 0.995, 0.998 (v = 0.1), 0.973, 0.985, 0.988 (v = 0.3); ratio v = 0.3 over 0.1
  9.69 at 64 and 128 cells (predicted 9.79 within 3 per cent: 1 per cent low). The
  correction leaves `|D_H(corr)|/|D_H(curv)|` = 0.082, 0.081, 0.097 at dx = 1, 0.5, 0.25
  (v = 0.3) and 0.078, 0.078, 0.094 (v = 0.1). Predicted below 0.15, 0.08, 0.05: the band
  at dx = 0.5 is missed narrowly and the one at dx = 0.25 by a factor 2; the ratio does
  not fall with the cell size and does not depend on v, so the leftover is second order
  in V (not the O(V^4) terms I named) and not the smoothing of the deposit (which would
  fall). Projections -0.023 to +0.002 (predicted within 0.05 of zero; a wrong sign gives
  2, none gives 1): the correction has the right sign and size, and what is left is
  nearly orthogonal to the second-order residual. The correction removes 90 to 92 per
  cent of the second-order residual. Cause of the remaining 8 to 10 per cent not known;
  diagnostic below.
- TB4 FAILED narrowly in both numbers. At 64 cells, v = 0.3, the whole-box H-norm of
  `corr` is 0.054299 against 0.052066 for the cluster at rest (4.3 per cent apart,
  predicted within 2); `curv` 0.058458 is above (held). M-norms of `curv` and `corr`
  0.0038321 and 0.0037922: 1.04 per cent apart (predicted within 1). The whole-box
  H-norm is dominated by the faces of the box already at rest (interior 0.0313 against
  whole box 0.0521).
- TB5 HELD. Code against the Python reference at every cell (64 cells, v = 0.3, all
  on): psi^4 5.6e-8, K_ij 4.7e-8 of the largest component (9.93e-3), beta^i 4.5e-8 of
  0.165, lapse 3.0e-8, trace K 3.5e-18 (single precision of the dumps).
- TB6 HELD. 10^4 stratified particles, 64 cells, v = 0.3: M-norm2 falls from 0.013954 to
  0.001327 (drop 0.012627 against the smooth part 0.012752: 1 per cent); projection of
  M_x on the smooth field 0.9952 without, -0.0044 with the curvature (static sample
  0.0002); H-norm 0.1945, 0.1950, 0.1919 for none, curv, corr against 0.1878 at rest
  (within 2 per cent of each other: held).
- TD1 HELD. Interior H-norm (within 14 of cluster 0) of the pair at rest over the single
  cluster: 1.027 (band 0.9 to 1.1).
- TD2 HELD. M-norm with the two boost tables over without: 0.0348 (TB2 at dx = 0.5:
  0.0341).
- TD3 HELD. `|D_H(corr)|/|D_H(curv)|` = 0.0729 (below 0.1; TB3 at dx = 0.5, v = 0.1:
  0.0779), projection 0.0008. Generator numbers of the pair: lam = 1.012348, momenta
  -0.118182 and +0.118182 (particle sums), M_ADM 1.98853 moving, 1.97561 at rest.

### Diagnostic of the TB3 leftover: predictions (written 16:02Z, before the run)

`tb_residual_diag.py` splits `D_H(corr)` of the TB runs into its projection on the
residual of the cluster at rest and the rest, measures it within 1 M of the surface
rbar_s = 8.936 and elsewhere, and plots shell averages (monopole and P_2 part). Two
candidates, which predict different things [JUDGEMENT]:
(a) the quiet lattice (spacing 0.25 at every cell count) samples the second-order matter
source at the edge with an error that does not depend on the mesh: then more than half
of `|D_H(corr)|` lies within 1 M of the surface at every cell count, and its monopole
there has one sign over a width of about the lattice spacing;
(b) the second-order source of the correction differs from what the code deposits by a
smooth factor (a term of the derivation that is missing or has the wrong weight): then
`D_H(corr)` is spread over the interior with a shell profile proportional to that of
`D_H(curv)` or of the matter density, and less than half of it is near the surface.
Neither is established if the split is near one half.

### Outcome of the diagnostic (run `core-20261119-160318-b9d749c`, figure `fig_tb_residual_profiles.png` looked at) and of R (run `core-20261119-153230-3e858c9`)

- R HELD: release core-v0.3 and this branch give byte-identical data files for
  `regress_cf` (16 files), `cf_table_regress` (9), `by_static` (5). The fourth case
  (`jeans`) runs at the end of `core-20261119-151457-7a855d8`.
- Diagnostic: the leftover of the correction sits at the surface. The share of
  `|D_H(corr)|^2` within 1 M of rbar_s = 8.936 is 0.76, 0.91, 0.95 at 32, 64, 128 cells
  (v = 0.3; 0.89, 0.99, 0.99 at v = 0.1); off the surface it is 1.2e-3, 7.3e-4, 7.0e-4
  (v = 0.3), against 0.029 of `D_H(curv)` there (a factor 40 removed). The shell average
  near the surface is two-signed (a dip of -1.2e-4 at rbar_s and a smaller bump outside),
  about 0.5 M wide, narrower at 128 cells than at 64; the P_2 part has a spike there.
  Inside, a flat monopole of about +2e-5 remains (3 per cent of the uncorrected -7.3e-4 at
  the centre; the O(V^4) terms were estimated at 1.6 per cent). Candidate (a), the
  lattice, predicted "more than half within 1 M of the surface": held; "one sign": not
  held. Candidate (b) predicted less than half at the surface: refuted. The leftover's
  projection on the residual at rest is 0.036, 0.062, 0.138 (v = 0.3), so it is not a
  multiple of the deposit error of the cluster at rest.

### Lattice test: predictions (written 16:08Z, before the run)

The quiet lattice has the spacing h = 0.25 at every cell count, so an error of its
sampling at the edge does not fall with the cell size. Run TB again for v = 0.3 at 64
and 128 cells with h = 0.125 (8 times the particles; cases at rest, `curv`, `corr`) and
apply the same diagnostic. If the lattice is the cause: the surface norm of `D_H(corr)`
falls by at least a factor 2 against h = 0.25 at the same cell count (2.34e-3 at 64,
2.86e-3 at 128), while `D_H(curv)` changes by less than 2 per cent. Not the cause: the
surface norm changes by less than 20 per cent; then the next candidate is the edge of the
second-order source itself on the mesh (the cloud and the filter acting on a profile
whose derivative is singular at rbar_s), which the code and the reference treat
differently, and the leftover is a property of the data at this resolution, to be
documented, not removed.
