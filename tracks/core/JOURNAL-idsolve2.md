# Journal of core, work package "idsolve2": the initial-data solver, second pass

Branch `core/id-solver-2` (from `core/id-solver`, a7a32cd source), worktree
`wt/core-idsolve2`. Units G = c = 1; expansion has K < 0. Labels: [VERIFIED] read or
measured here (locator or run id), [BACKGROUND] standard result not re-derived here,
[JUDGEMENT] inference or design, [TO VERIFY] open. Runs are registered with
`harness/bin/nrpic-run submit` (run ids `core-<UTC date>-<time>-<commit7>`, manifests in
`tracks/core/runs/`, outputs in `scratch/core/<run_id>/`). First pass: `JOURNAL-idsolve.md`,
`interfaces/id_solver.md`. Wave 3a, 2026-11-19.

## 2026-11-19, entry 1: what was read; design of the second pass; predictions A

Read: `CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; brief lines 493-553,
688-706, 834-860; decisions 0010, 0016, 0017; `interfaces/id_solver.md` and
`JOURNAL-idsolve.md` in full (with the failed predictions); the requests
`track/A-emd-pbh:tracks/A-emd-pbh/outbox/20261115T183720Z__to-core__refined-level-constraint-solve.md`,
`...183719Z__to-core__phase1-generator-cmc.md`,
`track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-core__moving-clump-initial-data.md`;
of the source: `particles/nrpic_idsolve.cpp` (all), `multigrid/multigrid_robin.cpp`,
`multigrid.hpp` 380-813, `multigrid_driver.cpp` 1700-1830 and 2201-2370,
`gravity/mg_gravity.cpp` 55-300, `particles/nrpic_newton.cpp` 186-372,
`pgen/nrpic/nrpic_cf.cpp` 395-648, `nrpic_bowen_york.hpp`, `nrpic_puncture_setup.hpp` 1-80,
`z4c/z4c_tasks.cpp` (boundary tasks), `bvals/bvals.hpp` 215-237.

Facts found while reading [VERIFIED, file and line of this worktree]:

- Meshes of AthenaK have no covered cells: every active cell of every MeshBlock is a
  leaf; a fine-coarse face is handled by a coarse array per block (restriction) and by
  prolongation into the fine ghost cells. Z4c does this with its own high-order scheme
  (`RestrictCC(u0, coarse_u0, true)`, `ProlongateCC(u0, coarse_u0, true)`,
  `z4c_tasks.cpp` 268-296); `MeshBoundaryValuesCC` takes the same flag in its constructor.
- The multigrid Poisson solver runs on refined meshes (octets between root grid and
  MeshBlocks); its octet boundary routine knows zero value and zero gradient only
  (`multigrid_driver.cpp` 1724-1822); `mg_bc = robin` stops on a refined mesh
  (`mg_gravity.cpp` 79-84).
- The puncture components of `nrpic_cf` live in `<problem>` as `comp<c>_type = puncture`,
  `_mass`, `_x1..3`, `_p1..3`, `_s1..3` (`nrpic_bowen_york.hpp` 324-360), and the
  Bowen-York curvature is added in closed form (`BYAddCurvature`, 97-117).
- A defect of the multigrid module outside this package, found while checking my own
  expansion against it [VERIFIED by transcribing the formulas into numpy,
  `tracks/core/analysis/idsolve2/check_multipole_upstream.py`]: the l = 3, m = 0 term
  of the multipole boundary (`mg_bc = multipole`, `mporder = 4`, the default) uses
  z (z^2 - 3 r^2), which is not harmonic (its Laplacian is -24 z); the solid harmonic is
  z (5 z^2 - 3 r^2) (`multigrid_driver.cpp` 2282 for the moment, `multigrid.hpp` 800 for
  the evaluation). For 20 random point sources within the unit cube the expansion as
  coded is off by 8.4e-4, 1.1e-4, 1.3e-5 of the potential at r = 8, 16, 32 (it falls as
  r^-3, the order of the wrong term), against 4.8e-6, 1.5e-7, 4.6e-9 with the corrected
  term. It affects the Newtonian mode on isolated domains for sources without mirror
  symmetry in z about the expansion centre. Not changed here (it would change existing
  results of another package); reported to core's lead.

### Design [JUDGEMENT unless labelled]

**(1) Far field at the faces (option `id_far`, default `multipole`).** The first pass
filled the ghost cells of psi - 1 and of W_i by r u = const between a ghost cell and its
mirror cell. That is exact for a monopole only, and the far field of W depends on the
direction already at order 1/r. Now the same fill acts on the remainder u - u_far, where
u_far is the exterior multipole expansion (orders 0 to `id_far_lmax` = 4) of the right
side of the equation about the Robin centre, with moments summed over the cells inside
the sphere that fits into the mesh (`id_far_radius`, a fraction of the distance to the
nearest face, default 1):

    psi_far = psi_s - (1/4 pi) sum_l M_l[rhs of (1)](n) / r^(l+1),
    W_far,i = (7/8) V_i - (1/8)(d_i U + x_j d_i V_j),   lap V_i = s_i,  lap U = -x_j s_j,

with s_i the right side of the vector equation (2) and V_i, U expanded in the same way
(for s_i = 8 pi P_i delta this is the Bowen-York field -(7 P_i + n_i n.P)/(4 r); the
decomposition was checked by hand: lap W_i = s_i - (1/4) d_i d_j V_j and
d_j W_j = (3/4) d_j V_j). The expansion (`particles/nrpic_idfar.hpp`) uses raw monomial
moments of degree <= 4 and Legendre polynomials; checked against direct summation in numpy
(`check_multipole_upstream.py`: error 4.8e-6, 1.5e-7, 4.6e-9 at r = 8, 16, 32 source
sizes for lmax = 4, falling as r^-5). The fill is affine in the field with the same
linear part as before, so the inner iterations (which see corrections with the plain
fill) are unchanged and the fixed point moves to the solution with the right far field;
the moments are those of the previous evaluation (they lag one outer iteration).
The record gets a line with M_ADM = -M_0[rhs]/(2 pi) (+ bare masses), P_ADM,i =
M_0[s_i]/(8 pi) (+ puncture momenta) and J_ADM from the antisymmetric first moment.

**(2) Coupled solve.** The alternation of the first pass stays (one deposit per outer
iteration serves both residuals). New: the matter term of sigma is exact for moving
particles without filter: psi^5 E = sum m W/(psi dV) with W^2 = 1 + psi^-4 u_i u_i gives
d/dpsi = -(psi^4)(E + 2 S), S the trace of the deposited stress; sigma gets + 4 pi psi^4 S.
For particles at rest S = 0 exactly and nothing changes.

**(3) Refined meshes.** (a) Ghost cells of psi, W and the corrections across levels with
the Z4c scheme (restriction, exchange, prolongation); the coarse array gets the plain 1/r
fill at mesh faces. (b) With `id_residual = code` every evaluation writes the metric
through the Z4c variables and their own exchange, then back, so that the monitor the
solver drives to zero is the one the run evaluates at t = 0 on its level structure (the
ghost cells at the faces of the mesh keep the solver's fill). (c) The seven-point operator
with prolongated ghost cells is not symmetric: BiCGStab with the multigrid solve as right
preconditioner replaces conjugate gradients (`id_lin_solver`, default `bicgstab` on a
refined mesh, `cg` otherwise). (d) Robin fill on the octets of the multigrid solver, so
that `mg_bc = robin` works on a refined mesh. (e) A dump per MeshBlock
(`<basename>.idsolve.blk.bin`).

**(4) Punctures.** psi = psi_s + u, psi_s = 1 + sum m_c/(2|x - x_c|) in closed form from
the puncture components of `nrpic_cf`; the seven-point operator acts on u; within
`id_puncture_radius` (default 1) bare masses of a puncture the residual is the stencil
form whatever `id_residual` (the monitor differentiates the singular metric: its
truncation error applied to m/2r at distance R is of order (dx/R)^6 m/R^3, which a fixed
physical radius lets fall as dx^6); the far field is psi_s + u_far; the Bowen-York
curvature of the punctures is subtracted in closed form before the trial curvature is
differentiated in (2) (it is divergence free); P and S of the punctures enter the ADM
line.

**(5)** Track A's CMC generator on the torus: the same solver with K = -3H and moving
particles (vector part on the torus); to be answered after the tests.

Default behaviour: with `id_solve` the far field is on by default (the plain fill has a
known error); `id_far = robin` recovers the first pass. Without `id_solve` nothing is
read or called, as before.

### Predictions A (written before the first run of the new executable)

**R1 first pass recovered.** With `id_far = robin` and particles at rest the new
executable writes the bytes of the published first-pass executable (a7a32cd,
`scratch/core/exe/core_id-solver/athena_cpu`) for gauss_code_n32 of T1 (record, dumps,
histories): the far field is off, wk has one more component, sigma gets + 0. For the
moving Gaussian (gboost, V1) psi and W agree to 1e-9 relative but not in every bit (the
new term of sigma). Refuted if a byte differs in the first case.

**W1 moving Gaussian (V2 again), far field against plain fill.** m = 1, sigma = 2, half
width 16, u_x = 0.1, N = 32, 64, 128, scalar mode code, vector stencil form, against the
semi-analytic continuum W of `run_vector.py`.
 (a) Plain fill: relative error of W_x at the face centres 8.6e-3 and 9.3e-3 at N = 32,
     64 (V2) and about the same at 128. Far field: below 2e-3 at N = 32 and falling by at
     least 3 per halving (what is left is the truncation error of the solution, of order
     (dx/L)^2).
 (b) Largest relative error of |W| over the outermost active layer of cells: plain fill
     above 1e-2 at every N; far field below 4e-3 at N = 32, falling by at least 3 per
     halving.
 (c) Central error unchanged by the far field to 20 per cent (-1.18e-2, -3.6e-3 at
     dx = 1, 0.5).
 (d) P_ADM of the record equals sum m u_x of the particle file to 1e-9 relative (the
     cloud conserves the sum; all matter is inside r < 16). The momentum from a surface
     integral of (L W)_xj over cubes of half-width 8 to 14 through cell centres equals it
     to 2 per cent at N = 32 and converges at second order (factor above 3 per halving) for
     both fills: the closure error is a solution of the homogeneous equation and carries
     no flux, so this integral cannot tell the fills apart; (a) and (b) can.
 (e) The vector residual falls by 0.13 to 0.14 per outer iteration as in V1 (the linear
     part of the fill is unchanged); at most 20 outer iterations.
 Refuted if the face error with the far field does not fall with resolution, or exceeds
 half of the plain-fill error at N = 64.

**W2 off-centre moving Gaussian** (centre (3, 2, 0), Robin centre at the origin, N = 64,
u_x = 0.1): J_ADM of the record = (0, 0, -2 P) to 1e-9 relative (first moment of the
deposit); face error of W against the translated continuum solution: lmax = 4 below
3e-3; lmax = 0 at least 3 times larger; plain fill at least 1e-2. Refuted if lmax = 4 is
not the best of the three.

**C1 coupled solve with fast particles** (the Gaussian with u_x = 1, Lorentz factor about
1.4; N = 32, 64; scalar and vector part in mode code): converges within 40 outer
iterations; max|H| of the monitor below 1e-9 away from the faces; the vector part ends at
`id_vector_tol` or by the stall rule with max|M| at least 1e3 times below its value
before; psi(0) - 1 changes by less than 5 per cent between N = 32 and 64 (second order).
Refuted if it does not converge or psi goes non-positive.
