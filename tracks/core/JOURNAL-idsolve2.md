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

## 2026-11-19, entry 2: registration; predictions B (end-to-end: the Zel'dovich ball)

Registration: `nrpic-run submit` works in this worktree (venv made with `nrpic-env create
--no-kokkos`). The allotment of 16 cores at a time is counted per owner, and five other
packages of core were running (15 cores busy), so tests A went in with 2 cores and
without the 128-cell cases (run core-20261119-145332-1ac049d); the 128-cell cases go to a
card job. Each test script is one registered run that writes the particle files and
input files of its cases into its run directory, runs them, analyses them and copies
numbers and figures to `tracks/core/analysis/idsolve2/`. The executable of a run is a
copy of the build of the commit (`scratch/core/tmp/idsolve2/exe_<commit7>/`), so that a
later build cannot change it under a running test.

Smoke runs before the registered ones (`scratch/core/tmp/idsolve2/byhand-*`, by hand,
not registered, no number of them is used as a result) showed that the far-field fill
runs to convergence and led to two changes before the commit of the source (1ac049d):
the expansion is evaluated from precomputed coefficients of homogeneous polynomials with
an analytic gradient (the first version, a triple loop per evaluation and numerical
gradients, made the 32-cell solve 60 per cent slower), and the moments are always
accumulated to degree 4 so that the J_ADM line does not depend on `id_far_lmax`.

**B, the end-to-end test.** The expanding ball of Track A (`make_ball.py --Rb 10 --edge 2`,
M = 1, Hubble rate H = sqrt(2 M/Rb^3) = 0.0447, density 3 H^2/(8 pi) = 2.39e-4), with a
triaxial Zel'dovich displacement in its growing mode (`make_ic.py zeldovich`): Lagrangian
position q -> x_i = (1 + e_i) q_i with e = (0.05, 0, -0.05), and momentum u_i = H e_i q_i
relative to the normal observers (largest |u| 0.022). Now S_i is not zero: moving matter
together with the curvature of the table, the combination the first pass did not test.
Mesh half-width 32, N = 32, 64, 128 (dx = 2, 1, 0.5), no filter, density-form sources and
conformal-time lapse (the settings of tests E and F), evolution to t = 2 with field dumps
at t = 0, 1, 2. Four data sets per resolution: `sph` (sphere, solved), `zoff` (Zel'dovich,
not solved), `zsol` (Zel'dovich, scalar and vector part solved, both in mode code),
`zsca` (Zel'dovich, scalar part only). Norms over regions, never over the whole mesh
(test F): interior r < 7, shell 7 <= r < 13.5, exterior, face layer (4 length units).
Predictions [JUDGEMENT]:
 (a) before the solve (`zoff`, t = 0): max|H| about 1e-2 and a shell mean of |H| of 3e-4
     to 5e-4 at the two finer meshes (T3, F: a property of the data); interior mean of
     |M| about 5e-5 (8 pi rho H e r = 9e-5 at r = 7), the same within 30 per cent at the
     two finer meshes;
 (b) after (`zsol`, t = 0): max|H| in interior and shell below 1e-10 at every resolution;
     the interior mean of |M| at least 100 times below (a) (the vector part ends at its
     tolerance or by the stall rule);
 (c) `zsca`: H as in (b); the interior mean of |M| within 10 per cent of (a);
 (d) record: |P_ADM| below 1e-10 (the momenta are odd in q), M_ADM of `zsol` within 1e-3
     of that of `sph`;
 (e) evolution: in interior and shell the mean of |H| of `zsol` stays within a factor 1.5
     of `sph` at t = 1 and t = 2 at every resolution (the solved data keep the residual
     at the level of the spherical case);
 (f) at dx = 0.5 the shell mean of |H| of `zoff` at t = 2 is at least 3 times that of
     `zsol`;
 (g) the face layer has the same mean |H| at t = 2 in the four runs of one resolution to
     10 per cent (1.3e-4 in test F): whole-mesh norms cannot tell the data apart;
 (h) the interior mean of |M| at t = 1 of `zsol` is at least 2 times below that of `zsca`
     at dx = 0.5 (the residual of the data is now above truncation level, unlike V6).
Refuted: (b) if the solve does not converge at some resolution; (e) if `zsol` exceeds
`sph` by more than a factor 2 in interior or shell at dx = 0.5.

## 2026-11-19, entry 3: predictions C (refined meshes, torus with moving matter)

Source for C: the Robin fill on the octets of the multigrid solver
(`MultigridDriver::RobinBoundaryOctet`, `multigrid_robin.cpp`; one hook at the top of
`ApplyPhysicalBoundariesOctet`), the refusal of `mg_bc = robin` on refined meshes removed
(`mg_gravity.cpp`); in the solver the exchange across levels, the Z4c round trip of mode
code and BiCGStab were already in 1ac049d. Said plainly: one smoke run was made before
these predictions were written (`scratch/core/tmp/idsolve2/smoke/smr1`, the Gaussian of T1
with one static level, not registered): it converged in mode stencil after 4 and in mode
code after 20 outer iterations. The predictions below are for what that run did not show.
Script `test_c.py`; the monitor of the run is read from the run's own output of the
constraint variables (`<output> file_type = bin, variable = con`), per MeshBlock.

**G, Gaussian at rest (exact psi) on refined meshes, Robin faces.** Lattice h = 0.25.
Uniform dx = 1 (`g_uni32`) and 0.5 (`g_uni64`); root dx = 1 with one static level in
|x_i| < 4 (`g_smr1`, also in mode stencil: `g_smr1_st`) and a second level in |x_i| < 2
(`g_smr2`).
 (a) mode code converges within 30 outer iterations on the refined meshes, mode stencil
     within 6;
 (b) the run's own monitor at t = 0, more than 4 length units from the faces of the mesh:
     max|H| below 1e-9 on every level in mode code, the cells at the level boundaries
     included (the solver's metric passes through the Z4c exchange of the run);
 (c) relative error of psi - 1 at the centre (r < 1): `g_smr1` within 30 per cent of
     `g_uni64` (the truncation error of the deposit follows the local cell size), `g_smr2`
     not larger than `g_smr1`; at r = 6 (root level) the refined runs within 30 per cent
     of `g_uni32`;
 (d) `g_smr1_st` within a factor 2 of `g_smr1` at the centre;
 (e) M_psi of `g_smr1` within 1e-3 of `g_uni64`.
 Refuted if the monitor has a floor above 1e-7 at the level boundaries, or no convergence.

**T, plane wave on the torus (K = -3H, a slice of constant mean curvature).** H = 1,
L = 2, 32 root cells, eight lattice sites per root cell.
 (a) `t_uni` (uniform, A = 0.1): as T4, at most 30 outer iterations, max|H| below 2e-9;
 (b) `t_smr` (static level in the cube [0.5, 1.5]^3, lattice twice finer in that cube):
     converges within 40 outer iterations; the run's monitor has max|H| below 1e-8 on both
     levels; without the solve (`t_smr_off`) max|H| above 0.1;
 (c) `t_smr_mov` (momenta of the growing mode, u_x = H times the displacement, vector
     part in mode code): converges; max|M| at least 100 times below its value before; the
     mean of the vector residual removed on the torus below 1e-10 of its scale (total
     momentum zero);
 (d) uniform torus with moving matter at A = 0.1, 0.5, 0.9 (density contrast up to
     A/(1 - A) = 9): the Newton iteration converges within `id_maxit` = 60 at every
     amplitude, psi > 0. Refuted if A = 0.5 does not converge.

**Z, the Zel'dovich ball of test B with a refined centre** (root dx = 2, one static level
with dx = 1 in |x_i| < 16; lattice h = 0.5), evolution to t = 2 with the settings of B.
 (a) `z_smr_sol` converges; the run's monitor at t = 0 has max|H| below 1e-9 in interior
     and shell;
 (b) at t = 1 and t = 2 the interior and shell means of |H| of `z_smr_sol` are within a
     factor 2 of the uniform run `zsol_n64` of test B (the same cell size in the matter),
     and at t = 1 the shell mean is below that of `z_smr_off`.
 Refuted if the refined solved run has 5 times the |H| of the uniform one in the matter.

## 2026-11-19, entry 4: outcome of tests A at 32 and 64 cells; the queue

Run core-20261119-145332-1ac049d (processor build of 1ac049d, 13 cases, 2 cores, 12
minutes), numbers `analysis/idsolve2/test_a_numbers.json`, figure `figs/test_a_far.png`
(looked at: the plain fill's error of W_x rises to 1e-2 towards the faces along x, the
far-field curve stays below 6e-4 everywhere outside the matter; middle panel: second
order for the far field, flat for the plain fill; tick labels of the middle panel
overlap, to be redrawn with the 128-cell points).

**R1 held.** With `id_far = robin` and matter at rest the six output files of
gauss_code_n32 (record, dump, field dump, three histories) are byte-identical to those of
the published first-pass executable. For the moving Gaussian every file differs in some
byte, as predicted (the new term of sigma), with psi equal to 6.0e-15 and W to 5.1e-16
of its maximum, 17 outer iterations in both (prediction: 1e-9).

**W1 held at 32 and 64 cells** (128 cells pending, card job).

| | plain 1/r fill, N = 32 / 64 | far field, N = 32 / 64 |
|---|---|---|
| W_x at the x-face centres, relative error | -8.55e-3 / -9.28e-3 | +9.3e-4 / +2.36e-4 |
| W_x at the y-face centres | +2.11e-3 / +1.73e-3 | +6.4e-4 / +1.59e-4 |
| largest error of W over the outermost layer | 2.20e-2 / 2.22e-2 | 1.19e-3 / 2.98e-4 |
| mean over the outermost layer | 1.20e-2 / 1.24e-2 | 7.8e-4 / 1.97e-4 |
| W_x at the centre | -1.175e-2 / -3.60e-3 | -1.108e-2 / -2.94e-3 |

 (a), (b): the far field removes the closure error; what is left falls by 3.95 and 4.0
 per halving. (c): the central error changes by 6 and 18 per cent: the closure error of
 the plain fill, a solution of the homogeneous equation, reached the centre with 6.5e-4
 at 64 cells. (d): P_ADM of the record equals sum m u_x to 3e-13; the surface integral
 over cubes of half-width 9.5 to 13.75 differs from it by -5.6e-5 to -2.1e-5 (N = 32) and
 -1.4e-5 to -5.1e-6 (N = 64), second order, and by the same amounts with the plain fill
 (-5.2e-5 to -3.3e-5, -1.3e-5 to -8.3e-6), as predicted: the surface integral cannot
 see the closure error. At half-width 7.5 the integral misses 9e-4 and 3.7e-4 of the
 momentum: matter beyond the surface (3.75 sigma), not truncation. (e): residual ratio
 0.136 to 0.141 per outer iteration, 17 outer iterations.

**W2 held, except for one bound.** Off-centre Gaussian (centre (3, 2, 0)), 64 cells:
largest error of W over the outermost layer 5.6e-4 (lmax = 4), 0.116 (lmax = 0), 0.108
(plain fill); at the face centres 2.2e-4, 1.1e-4, 9.5e-5 against 5.7e-3 to 9.9e-3
(lmax = 0) and 4.9e-3 to 1.15e-2 (plain). J_ADM = (0, 7e-16, -0.2282094778), that is -2
times P_ADM = 0.1141047394. Failed bound: P_ADM differs from sum m u_x = 0.11410473958 by
1.4e-9 relative and J_z from -2 sum m u_x by 6e-10 and from -2 P_ADM... both above or at
my 1e-9: the lattice reaches r = 14 from its centre, 17.6 from the Robin centre, beyond
the sphere of the moments (16): 1.4e-9 of the momentum lies outside. The moments are
those of the sphere, as designed; my bound ignored the shift.

**C1 held.** u_x = 1 (P = 1.141, M_psi = 1.4286 and 1.4284 at 32 and 64 cells): 30 and
36 outer iterations; max|H| of the monitor away from the faces 2.1e-11 and 2.4e-11
(before 0.57 and 0.65); the vector part ends at `id_vector_tol` (9.9e-7) with max|M|
0.20 -> 3.3e-7 and 0.23 -> 1.4e-7; psi - 1 at the centre 0.24302 and 0.25143 (3.3 per
cent apart).

**Processors and cards.** After this run the allotment of owner core (16 cores at a
time, decision 0006) was full with the runs of other packages of core, and nine jobs
waited for the two cards (six of owner core). Tests B and C wait in a loop that
submits them when the allotment has room (`scratch/core/tmp/idsolve2/submit_wait.sh`);
no card job was added to the queue.

**Smoke runs between entries 3 and 4, and what they changed** (by hand in
`scratch/core/tmp/idsolve2/`, not registered; they led to a source change, so they are
reported). (1) The torus with a refined cube, matter at rest (`t_smr`): mode code
converges in 27 outer iterations, and the run's own constraint output shows max|H|
2.6e-10 (root level) and 1.15e-9 (refined level): the run sees what the solver solved.
(2) The same with moving matter and the vector part in mode code: the vector residual
stalled at 6e-2 of its scale and W was frozen after 12 iterations with max|M| 1.8e-2
(before 9.8e-2). Where it sits (bins by distance from the level boundary): with the
vector part in stencil form, converged to 5e-14, the monitor's |M| is 2.0e-2, 7.4e-3,
1.7e-3 in the first, second and third fine cell next to the level boundary and below
6.5e-4 further in (deep inside 2.0e-4, as on a uniform mesh of the fine cell size:
9e-5 to 2e-4); on the coarse side 4.0e-3 in the first cell. Reading [JUDGEMENT; the run
that could refute it is the registered t_smr_mov after the change]: the monitor of a
cell next to a level boundary differentiates K_ij across prolongated ghost cells and
sees the difference of the second-order truncation errors of L W on the two levels,
divided by the cell size; no correction of W removes it, and with the monitor as
residual those cells stall the iteration for the whole mesh. Change (76add0c): with
`id_vector_residual = code` on a refined mesh the residual is the stencil form in the
ng - 1 cells on either side of a level boundary. A smoke run of the changed code:
vector residual 1.3e-3 (uniform torus: 1.4e-3), max|M| still 2.0e-2 at the level
boundary. (3) Uniform torus, moving matter, A = 0.1, 32 cells, max|M| of the monitor
before 0.095: after, mode code 2.6e-4, stencil form 9.2e-4; with one filter pass
(`nfilter = 1`) mode code 2.0e-6, stencil form 3.9e-4. The filter removes the content at
the Nyquist wavenumber that the monitor's operator cannot balance.
