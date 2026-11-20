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

## 2026-11-19, entry 5: a new session continues; tests B, C launched; predictions R0, P, W1 at 128 cells, K (card)

A new session took the package over at 15:31 UTC from commit 76add0c and the uncommitted
entry 4 (committed as 3d26b50). The submission loop of the previous session had stopped
(no process left, its log ends at 15:27 UTC). Read again: `CLAUDE.md`, `coord/CHARTER.md`
to "Owners", brief lines 493-553, 688-706, 834-860, decisions 0010, 0016, 0017, 0018,
`harness/RULES.md`, `interfaces/id_solver.md`, `JOURNAL-idsolve.md` (all), this journal,
`particles/nrpic_idsolve.cpp` (all), the two requests of Track A,
`pgen/nrpic/nrpic_bowen_york.hpp` 1-96, `python/nrpic/bowen_york.py` 1-232.

Launched (processor build of 76add0c, predictions of entries 2 and 3 unchanged): test B
at 32, 64 and 128 cells as run core-20261119-153416-3d26b50 (4 cores: the allotment of
owner core had 4 free), test C as run core-20261119-153510-d1eaa30 (1 core, what was
left). The 128-cell cases of B run on processors, not on a card.

**R0 regression against the release** (`regress_r0.py`): without `id_solve` the
executable of this branch writes the same bytes as the release executable core-v0.3
(`.work/build_cpu_v03/src/athena`) in the seven relativistic set-ups of
`regress_relativistic.py` (geo, boris, dep, east, os, jeans, binary: the binary has four
multigrid levels, so the octet boundary routine with its new Robin hook is passed with the
multipole kind) and the two Newtonian set-ups (isolated with multipole faces, periodic).
Refuted if any output file or result line of the log differs.

**P, punctures** (`test_p.py`; the singular part psi_s = 1 + sum m/2r in closed form, u
solved). References: for one Bowen-York puncture (m = 1, P = 0.5 along x) the multipole
solution `bowen_york.solve_axisym` (lmax 12): m_ADM = 1.145565, u at the puncture 0.028368,
and the mass that the moments within r = 16 give, m + 2 Q(16) with Q(R) = -R^2 u_0'(R):
1.119594; for a puncture (m = 1, at rest) in a Gaussian shell of particles at rest
(mass 0.5, radius 6, width 1) the radial solution of lap u = -2 pi Etilde/(psi_s + u)
computed in `test_p.py`: m_ADM = 1.448858, u(0) = 0.036309. Said plainly: two smoke runs at
32 cells were made before these predictions (`scratch/core/tmp/idsolve2/smoke_p/`, by
hand, not registered: the vacuum puncture in mode stencil and the shell in mode code with
radius 3), to check that a run without particles and the analysis work; what they showed
is quoted where a prediction uses it.
 P1 vacuum Bowen-York puncture, N = 32, 64, 128 (dx = 1, 0.5, 0.25):
  (a) mode stencil converges in at most 8 outer iterations; the largest error of u for
      1 < r < 12 is 3.0e-4 at N = 32 (smoke) and falls by at least 3 per halving; the
      error in the eight cells next to the puncture falls by at least 2.5 per halving (the
      source is of order r^3 at the puncture, u is only C^2 there);
  (b) M_psi of the record equals m + 2 Q(16) = 1.119594 to 2e-4 at every N (smoke:
      1.119678 at N = 32) and is NOT the ADM mass: the Bowen-York source falls as r^-4 and
      what lies beyond the sphere of the moments, 0.026 for P = 0.5 and r = 16, is missing;
  (c) mode code with id_puncture_radius 1: at N = 32 it does not converge or its error of
      u is more than 10 times that of mode stencil (the sixth-order monitor differentiates
      psi_s^4 at r = 1.7 dx); at N = 128 it converges and its error falls by at least 16
      between N = 64 and 128 (the truncation of the monitor at a fixed radius goes as
      dx^6), but stays above the stencil error;
  (d) mode code with radius 3: converges at N = 64 and 128 with an error of u within a
      factor 2 of mode stencil; the monitor outside the radius after the solve below 1e-9
      (more than 4 length units from the faces);
 P2 puncture in the shell, N = 32, 64, 128 (lattice h = dx/2):
  (a) mode stencil and mode code (radius 3) converge; the error of u for 3 < r < 12 falls
      by at least 3 per halving in both modes; at N = 128 the two modes agree with the
      reference to 1e-4 of u(0) or better;
  (b) M_psi of the record within 2e-4 of 1.448858 at N = 32 (smoke, mode code: 1.448946)
      and converging (factor 3 or more per halving);
  (c) mode code: the monitor outside radius 3 and away from the faces below 1e-10;
 P3 refined mesh: root 32^3 (dx = 1), static levels in |x_i| < 8 (dx = 0.5) and |x_i| < 4
     (dx = 0.25), lattice h = 0.125:
  (a) the shell in mode code (radius 3) and in mode stencil converge (BiCGStab); the error
      of u at the puncture (level 2) is at most 1.5 times that of p2_c3_n64 (the shell
      lies mostly on level 1, dx = 0.5); the monitor after the solve below 1e-8 on every
      level, away from the faces and outside radius 3;
  (b) the vacuum puncture in mode stencil: the largest error of u for 1 < r < 12 at most 2
      times that of p1_st_n64;
 P4 three punctures (m = 1, 0.6, 0.4 at (-3,0,0), (3,1,0), (0,-4,1); momenta (0,0.2,0),
     (0,-0.2,0.1), (0.1,0,-0.1); spin (0,0,0.2) on the first), mode stencil, N = 32, 64, 128:
  (a) at most 8 outer iterations; P_ADM of the record is the sum of the momenta,
      (0.1, 0, 0), and J_ADM the sum of spins and x_c times P_c, both to round-off;
  (b) u at each puncture converges: |u_128 - u_64| at most a third of |u_64 - u_32|;
  (c) the closed-form second-order corrections of `nrpic_cf` (comp_corr = approx with the
      background factor) agree with u at the punctures to 30 per cent (they omit the
      cross terms of the curvatures and orders above P^2);
 P5 the puncture of P1 in the shell of P2 moving with u_x = 0.1 (sum m u_x = 0.05), both
     parts in mode code (radius 3), N = 64: converges; P_ADM_x of the record = 0.55 to
     1e-6 relative (the momentum of the deposit plus that of the puncture); the vector part
     ends at id_vector_tol or by the stall rule with the monitor's max|M| at least 100
     times lower.
 Refuted (design) if P1 (a) or P2 (a) fails: then the split psi_s + u or the stencil near
 the puncture is wrong.

**W1 at 128 cells** (`test_a.py --tests w1`, processors): far field: relative error of W_x
at the x-face centres 6e-5 (2.36e-4/4) within a factor 1.5, largest error over the
outermost layer below 1e-4; plain fill: 9e-3 at the face centres and above 1e-2 over the
layer, as at 32 and 64 cells.

**K card check** (card build of 76add0c, one A100, at most 0.5 card-hours reserved): the
vacuum puncture (mode stencil and mode code radius 3) at 128 cells, the moving Gaussian
with the far field at 128 cells and the solved Zel'dovich ball `zsol` at 128 cells with its
evolution to t = 2: the same outer iterations as the processor runs, psi (and W) equal to
1e-12 relative, the region means of |H| at t = 2 equal to 1e-6 relative (card runs with
deposition are not bit-reproducible). Refuted if an iteration count differs by more than
one or a field by more than 1e-9.

## 2026-11-19, entry 6: card job K queued; test G (Track A's CMC peak) predicted

Card job K: run core-20261119-154414-2506b80, Slurm job 4656 (batch launcher, card build
of 76add0c copied to `scratch/core/tmp/idsolve2/exe_76add0c/athena_gpu`, list
`scratch/core/tmp/idsolve2/card_k/card.list`, 0.6 card-hours reserved), waiting behind
about twenty jobs. Tests R0, P and W1 (128 cells) wait for room in the allotment of owner
core (loops `submit_wait.sh`, logs `scratch/core/tmp/idsolve2/submit_*.log`).

**G, the phase-1 generator of Track A on the CMC slice with the code's solver**
(`test_g.py`; request `...183719Z__to-core__phase1-generator-cmc.md`). The data are those
of Track A's T4 (`t4_cmc_route.py` on `track/A-emd-pbh`, functions `ge_fields`, `run_case`,
copied with their source named): a curvature peak with mu, e = 0.2, eps_i = k/(aH) = 0.2
on a torus of side 20/k = 100 (H = 1), gradient-expansion psi_GE, K = -3H, Ahat_GE, E from
the Hamiltonian constraint of psi_GE and Shat from the momentum constraint (spectral
derivatives), one particle per cell at the cell centre carrying Ehat and Shat. The code
reads psi_GE, K and Ahat_GE (`nrpic_cosmo id = file`), starts from psi = 1 and solves with
K and Ahat held fixed. psi_GE solves the continuum constraint with this E exactly, so the
solved psi differs from it only by the discretisation of the code; measure: Track A's
c = max|dpsi - <dpsi>| / max|psi_GE - <psi_GE>|. Track A's Python solve diverged at mu = 0.5
(runs A-emd-pbh-20261115-160718-e04c0cc, -161134-f3949f8, quoted from their DESIGN.md 2.2).
Said plainly: one smoke run (mu = 0.5, 32 cells, by hand, `scratch/core/tmp/idsolve2/
smoke_g/`, not registered) was made to check the files: it converged after 8 outer
iterations with c = 1.6e-5, max|H| 1.2e-9 after, and 49 to 50 conjugate-gradient steps in
most Newton steps (the inner solve stops at id_lin_maxit = 50).
Cases: mu = 0.03, 0.3, 0.5, 0.7 at 64 cells, mu = 0.5 at 32 cells, mu = 0.5 at 64 cells
with the vector part (mode code). Predictions [JUDGEMENT]:
 (a) every case converges within 80 outer iterations, mu = 0.5 and 0.7 included;
 (b) c at 64 cells below 1e-4 for mu <= 0.5, and for mu = 0.5 at least 4 times below the
     value at 32 cells;
 (c) the monitor after the solve, max|H| below 1e-8 in every case; the mean offset of
     psi from psi_GE below 1e-6;
 (d) with the vector part: converges, c within 10 per cent of the scalar-only case, and
     the monitor's max|M| at least 10 times lower after the solve (or W frozen by the
     stall rule);
 (e) the inner solve is poorly preconditioned on a box of 100 Hubble lengths (the
     Poisson preconditioner against sigma/k_min^2 of order 1e3): for mu >= 0.3 at 64
     cells at least half of the Newton steps use all id_lin_maxit = 50 steps.
Refuted (machinery) if mu = 0.5 does not converge or c at 64 cells exceeds 1e-3.

## 2026-11-19, entry 7: outcomes of R0 and G

**R0 held** (run core-20261119-154842-de22625, 1 core, `regress_r0.json`, figure
`figs/regress_r0`, looked at: every bar identical, none differing). Without `id_solve`
the processor build of 76add0c writes the same bytes as the release executable
core-v0.3 in all nine set-ups: geo 2 files, boris 2, dep 1, east 12, os 16, jeans 5
(and the result lines of its log), binary 1, Newtonian isolated 11, periodic 9; both
executables exit 0 in every case.

**G, Track A's CMC peak with the code's solver** (run core-20261119-160329-ab0aa92,
2 cores, `test_g_numbers.json`, figure `figs/test_g_cmc`, looked at: the solved profiles
lie on psi_GE, the difference peaks at the centre at a few 1e-7 for mu >= 0.3 at 64 cells,
residual histories fall by about a decade per Newton step after the third):

| case | outer it. | c = max\|dpsi - <dpsi>\| / max\|psi_GE - <psi_GE>\| | max\|H\| before -> after | mean offset |
|---|---|---|---|---|
| mu = 0.03, 64^3 | 9 | 1.0e-7 | 0.56 -> 3.2e-10 | 0 |
| mu = 0.3, 64^3 | 10 | 3.6e-7 | 8.6 -> 1.5e-9 | 2e-12 |
| mu = 0.5, 32^3 | 8 | 1.6e-5 | 19.0 -> 1.2e-9 | -6.5e-10 |
| mu = 0.5, 64^3 | 10 | 5.2e-7 | 20.4 -> 3.1e-9 | -1.4e-11 |
| mu = 0.7, 64^3 | 11 | 6.3e-7 | 41.8 -> 2.2e-9 | -6.1e-11 |
| mu = 0.5, 64^3, vector part | 10 | 5.2e-7 | 20.4 -> 3.1e-9 | -1.4e-11 |

 (a) held: every case converged, mu = 0.5 and 0.7 included (Track A's Python solve
     diverged at 0.5), in 8 to 11 outer iterations.
 (b) held: c below 1e-4 at 64 cells for every mu (at most 6.3e-7); for mu = 0.5 it falls by
     31 from 32 to 64 cells (predicted at least 4).
 (c) held: max|H| after 3.2e-10 to 3.1e-9 (bound 1e-8); mean offsets at most 6.5e-10.
 (d) held: with the vector part c is the same to 1e-5 relative; the monitor's max|M|
     falls from 1.58e-7 to 1.66e-9 (factor 95), ending at id_vector_tol after 10
     iterations (the GE data satisfy the momentum constraint to the truncation of the
     monitor).
 (e) failed for mu = 0.3, held for 0.5 and 0.7: Newton steps that used all 50 inner steps:
     4 of 10 (mu = 0.3), 6 of 10 (0.5), 6 of 11 (0.7). The inner solve is poorly
     preconditioned on a box of 100 Hubble lengths, as predicted, but the Newton
     iteration converges regardless (each step still reduces the residual by about 10).
 Also seen: the proper density E of the code is uniform to 0.5 per cent on the CMC slice
 (max E over its mean 1.0047 to 1.0049 for mu >= 0.3), while Ehat = psi^6 E peaks at 4
 times its mean: the density contrast of the CMC slice is of order eps^2 zeta [JUDGEMENT,
 consistent with Track A's DESIGN.md 2.2].
 Consequence for request (5): the machinery of the code solves Track A's CMC data at
 64^3 to c of a few 1e-7 where their solver diverged; what the code does not provide is
 the generator of the trial fields (Track A's `ge_fields`, here copied into the test) and
 a field format with a non-conformally-flat metric.

## 2026-11-19, entry 8: outcome of C (refined meshes, torus, refined Zel'dovich ball); a fault of the analysis

Run core-20261119-153510-d1eaa30 (processor build of 76add0c, 15 cases, 1 core, 25 min),
analysed again by run core-20261119-161309-b04b4dd; `test_c_numbers.json`, figure
`figs/test_c_refined` (looked at: second-order profiles of the psi error with the refined
runs between the uniform ones, residual histories, the monitor per level).

**A fault of the analysis, found before any number of it was used.** The first analysis
inside the run read the six numbers per MeshBlock of the binary output as x1i, x2i, x3i,
dx1, dx2, dx3 (as the docstring of `athenak/vis/python/bin_convert.py` says); AthenaK
writes x1min, x1max, x2min, x2max, x3min, x3max (`outputs/binary.cpp` 139, 198-201
[VERIFIED]). The masks "4 length units from the faces" and the radial regions were
therefore wrong, and the monitor on level 0 of the Gaussian appeared as 1.9e-3 (the face
cells). The reader is fixed (commit 0540281, `test_c.py` `read_con`)
and the analysis repeated as its own registered run; all numbers below are from it.

**G** (Gaussian at rest, Robin faces):
 (a) held: mode code 20 (one level) and 22 (two levels) outer iterations, mode stencil 4.
 (b) held: the run's own monitor at t = 0 more than 4 units from the faces, max|H| per
     level: one level 2.4e-12 (root), 2.0e-11 (level 1); two levels 5.9e-13, 4.0e-12,
     1.9e-11; uniform 1.4e-11 (32^3), 1.1e-11 (64^3). The cells at the level boundaries
     are included: the solver's metric passes through the Z4c exchange of the run.
 (c) centre held, r = 6 failed: relative error of psi - 1 at r < 1: -5.01e-3 (one level)
     against -5.03e-3 (uniform dx = 0.5); two levels +3.0e-4 (smaller, as predicted). At
     r = 6 (root level, dx = 1) the refined runs have 5.4e-4 and 9.6e-4 against 1.67e-3 for
     the uniform dx = 1 run: not "within 30 per cent" but 2 to 3 times smaller. The error
     there is the far field of the error of the deposited monopole, which the finer centre
     makes smaller (as in the first pass, T1 (e)); my prediction took it as local.
 (d) failed: mode stencil on the refined mesh has -2.03e-3 at the centre against -5.01e-3
     in mode code (factor 2.5, predicted within 2), the same relation as on uniform meshes
     in the first pass (T1: -2.43e-3 against -5.22e-3); the stencil run leaves the monitor at
     1.4e-3 (level 1).
 (e) held: M_psi 1.000647 (one level) against 1.000651 (uniform 64^3).
**T** (torus, K = -3H):
 (a) held: t_uni 24 outer iterations, max|H| 1.15e-9.
 (b) held: t_smr (refined cube, nested lattice) 27 iterations, max|H| 2.6e-10 (root),
     1.15e-9 (level 1); without the solve 0.73 and 1.86.
 (c) failed on one count: t_smr_mov converges (27 iterations) and the mean removed from the
     vector residual is 1.4e-17, but the monitor's max|M| falls only from 9.8e-2 to 2.0e-2
     (predicted at least 100 times): W stalls (relative residual 1.3e-3) and max|M| sits at
     the level boundary (level 1: 2.0e-2, root 4.0e-3; mean 1.1e-3 and 2.8e-4). The smoke
     runs of entry 4 had shown it; this run confirms that the stencil form near the
     boundary (76add0c) does not remove it. Reading [JUDGEMENT]: K_ij = psi^-2 (Abar + L W)
     with L W from second-order central differences on each level; the monitor
     differentiates K_ij across prolongated ghost cells and sees the jump of the
     truncation error of L W between the levels over the fine cell size, a first-order
     error in M that no W removes. A fourth-order L W in mode code would lower it by about
     (k dx)^2; not done (section limits of the interface).
 (d) held: uniform torus with moving matter, A = 0.1, 0.5, 0.9: 24, 26, 33 outer
     iterations, psi >= 0.964; max|M| 0.095 -> 2.6e-4, 0.56 -> 5.0e-3, 1.32 -> 4.3e-2 (the
     vector part stalls at relative residuals 1.4e-3, 3.8e-3, 1.2e-2: the Nyquist content of
     the deposit, as in the first pass).
**Z** (Zel'dovich ball of B, root dx = 2, level 1 with dx = 1 in |x_i| < 16):
 (a) held: z_smr_sol converges in 43 iterations; at t = 0 interior and shell max|H|
     1.8e-13 and 1.6e-12 (root level away from the faces 6.9e-8).
 (b) held: means of |H| at t = 1 (interior 5.51e-5, shell 1.71e-4) and t = 2 (1.05e-4,
     1.85e-4) equal those of the uniform 64^3 run of B (zsol_n64: 5.52e-5, 1.71e-4;
     1.05e-4, 1.84e-4) to 1 per cent; at t = 1 the shell mean is below z_smr_off (4.01e-4).
 The vector part on this mesh stalls at max|M| 2.6e-4 (uniform 64^3: 2.6e-6), again at the
 level boundary (|x_i| = 16, in the curved exterior of the table); the interior mean of
 |M| is 9.8e-7 (uniform 8.9e-7).
Answer to Track A's request on refined levels [VERIFIED in these runs]: the solve runs on
the level structure of the run, and the run's own Hamiltonian monitor at t = 0 is at
1e-11 to 1e-9 on every level, level boundaries included (Track A measured 0.077 to 0.18
with data interpolated onto refined blocks).

## 2026-11-19, entry 9: outcome of W1 at 128 cells; P2

**W1 at 32, 64, 128 cells held** (run core-20261119-155750-c923762, 1 core; the 32- and
64-cell cases repeat run -145332-1ac049d to all digits printed; `test_a_numbers.json`,
figure `figs/test_a_far`, looked at: the far-field curves fall by 4 per halving in the
middle panel, the plain fill stays flat; the surface momentum converges at second order
for both fills). Far field at 128 cells: W_x at the x-face centres +5.9e-5 (prediction
6e-5 within 1.5), y-face centres 4.0e-5, largest error over the outermost layer 7.5e-5
(prediction below 1e-4); the factors 64 -> 128 are 3.98 and 3.99. Plain fill: -9.5e-3 at
the x-face centres and 2.25e-2 over the layer (does not fall). Central error -7.5e-4
(far) against -1.40e-3 (plain): at 128 cells the closure error of the plain fill is
half of the central error. P_ADM of the record 0.1141047395752 against sum m u_x =
0.11410473958 (round-off); surface integral at half-width 13.75: 1.25e-6 relative (5e-6 at
64, 2.0e-5 at 32 cells).

**P2, a puncture in a matter shell** (run core-20261119-161842-b92b298, 1 core;
`test_p_numbers_p2.json`, figure `figs/test_p_profiles_p2`, looked at: the solved u lies
on the radial reference at all three resolutions and (u - u_ref)/dx^2 is one curve, with
its maximum at the shell, r = 6 to 7):

| case | outer it. | u - u_ref at the puncture | max\|u - u_ref\|, 3 < r < 12 | M_psi (ref 1.448858) | monitor outside r_p |
|---|---|---|---|---|---|
| stencil, 32 / 64 / 128 | 4 / 3 / 3 | -1.4e-5 / -3.5e-6 / -8.8e-7 | 1.12e-4 / 2.9e-5 / 7.3e-6 | 1.448967 / .448885 / .448864 | 0.083 / 0.24 / 7.6e-3 |
| code, r_p = 3, 32 / 64 / 128 | 25 / 22 / 17 | +2.0e-4 / -6.1e-6 / -1.2e-6 | 2.9e-4 / 5.7e-5 / 1.4e-5 | 1.448946 / .448893 / .448866 | 4.4e-13 |

 (a) held for convergence and order: both modes converge; the error over 3 < r < 12 falls
     by 3.9 and 4.0 (stencil), 5.0 and 4.0 (code); at 128 cells the error at the puncture
     is 2.4e-5 (stencil) and 3.3e-5 (code) of u(0) = 0.0363, inside 1e-4; but the largest
     error over the shell region is 2.0e-4 and 3.9e-4 of u(0), not 1e-4: my bound "agree
     with the reference to 1e-4 of u(0)" fails for the maximum (the deposit's
     second-order error of the shell at r = 6).
 (b) held at 32 cells (8.8e-5, 1.09e-4 from the reference), converging at 4.0 and 4.1 per
     halving in mode stencil; in mode code the factors are 2.5 and 4.2, the first below my
     3 (failed for that step).
 (c) held: mode code leaves the monitor at 4.4e-13 outside radius 3 and away from the
     faces. Mode stencil leaves it at 0.08 to 0.24 next to the puncture (r of 1 to 2: the
     sixth-order monitor differentiating psi_s^4), which is the monitor's error on the
     singular part, not an error of the data (u converges at second order there).

## 2026-11-20, entry 10: wave 3, a new session closes the package; what was found; predictions P6, P7

The session of 2026-11-19 was cut off by the usage limit of the account after entry 9. A
new session took over on 2026-11-20 at 22:00 UTC (merge of main: decisions 0018, 0019,
the pre-commit hook, the pause flag). Read again: `CLAUDE.md`, `coord/CHARTER.md` to
"Owners", brief lines 493-553, 688-706, 834-860, decisions 0016 to 0019, `harness/RULES.md`,
this journal, `interfaces/id_solver2.md`, `test_p.py`, `analyze_k.py`, of
`nrpic_idsolve.cpp` lines 462-560, 812-960, 1040-1240.

State found [VERIFIED: `git status`, `nrpic-run status`, `sacct`]: source unchanged since
76add0c; every processor run of entry 5 had finished unattended (B at 32, 64, 128 cells
core-20261119-153416-3d26b50; P1 -165458-ecdaa7c; P3 and P4 -170050-f228951; P5
-170028-77f7173), their numbers and figures lay uncommitted in the analysis directory
(committed as a3c5a8f, each file equal to the copy in its run directory); the card job K
(core-20261119-154414-2506b80, Slurm job 4656) had run its four cases in 1 min 56 s
(0.032 card-hours) and was not closed (closed now with `nrpic-run finish`). Not done at
the cut-off: outcomes of B at 128 cells, P1, P3, P4, P5, K; the placeholders of the
interface; READY; publication. Outcomes: entry 11.

Two things the finished P runs show, which the tests below follow up (the numbers are
in entry 11): (i) the error of u of the vacuum Bowen-York puncture does not fall with
the cell size: it is 2.6e-4 to 2.9e-4 over 1 < r < 12 at 32, 64 and 128 cells, nearly
uniform in space (root mean square 2.6e-4 to 2.8e-4), in both residual modes; (ii) u at
the three punctures of P4 has not converged at dx = 0.25 (successive differences fall
by 0.63, 0.24, 0.48 instead of at most a third).

**P6, the face distance for a Bowen-York puncture** (`test_p.py --tests p6`; the vacuum
puncture of P1, m = 1, P = 0.5, mode stencil; mesh half-width 32 at dx = 1 and 0.5 (64
and 128 cells) and half-width 64 at dx = 1 (128 cells); the half-width 16 cases are those
of P1). Reading to be tested [JUDGEMENT]: the Bowen-York source of the scalar equation
falls as r^-4, lap u = -c/r^4 beyond the matter with c = (15/16) P^2 at leading order
(angle average of (1/8) Abar^2 with psi = 1), so u = Q_inf/r - c/(2 r^2), and the moments
within the sphere of radius R (the half-width) hold Q(R) = Q_inf - c/R. The remainder
u - u_far is then c/(R r) - c/(2 r^2) beyond R, which the 1/r fill does not represent:
d(r v)/dr = c/(2 r^2) where the fill assumes 0. The error is a solution of the
homogeneous equation, nearly a constant e0 with e0 = -(c/2) <1/r^2> over the faces,
about -0.64 c/(2 R^2) for a cube. With c from the reference (c/R = Q_inf - Q(16) =
0.01298, c = 0.208; leading order 0.234 less the factor psi^-7) that is -2.6e-4 for
R = 16, as seen. Predictions:
 (a) the mean of u - u_ref over 1 < r < 12 is negative and falls as R^-2: -6.5e-5 within
     20 per cent at half-width 32 for both cell sizes, and -1.6e-5 within a factor 1.5
     at half-width 64 (there the truncation error at dx = 1, about 1e-5, is of the same
     size);
 (b) M_psi of the record equals m + 2 Q(R) of the reference (`by_reference`, `m_inside`)
     to 1e-4 at half-width 32 and 64; its deficit against the ADM mass 1.145565 is
     0.0260 at R = 16 (measured in P1) and about 0.013 and 0.0065 at R = 32 and 64;
 (c) at most 6 outer iterations in every case.
 Refuted (the reading) if the mean error does not fall by 3 to 5 when the half-width
 doubles at fixed cell size.

**P7, the three punctures of P4 on refined meshes** (`test_p.py --tests p7`; root 32^3
with dx = 1, MeshBlocks of 8^3, static levels: |x_i| < 8 (dx = 0.5), |x_i| < 6 (0.25),
then cubes about each puncture of half-width 2 (0.125), 1 (0.0625) and 0.5 (0.03125);
cases `p7_l2` to `p7_l5` by the finest level; mode stencil, BiCGStab). Reading to be
tested [JUDGEMENT]: the source (1/8) psi^-7 Abar^2 of a puncture of bare mass m peaks at
r = 3 m/8 for its momentum (r^3/(r + m/2)^7) and at r = m/12 for its spin
(r/(r + m/2)^7): 0.15 to 0.375 for the three momenta and 0.083 for the spin of the first
puncture, not resolved by dx = 0.25. Predictions:
 (a) every case converges in at most 8 outer iterations; P_ADM and J_ADM of the record
     as in P4, (0.1, 0, 0) and (0.5, -0.2, -0.6), to round-off;
 (b) `p7_l2` agrees with the uniform 128-cell run of P4 at each puncture to 5 per cent
     of u (the same cell size at the punctures; the far field differs little);
 (c) the differences of u at each puncture between successive cases fall: |u_l4 - u_l3|
     at most 0.4 |u_l3 - u_l2| and |u_l5 - u_l4| at most 0.4 |u_l4 - u_l3| for the two
     punctures without spin; for the spinning one the second ratio holds (its source is
     resolved from dx = 0.0625 on);
 (d) u at the punctures on the finest mesh lies above the uniform 128-cell values
     (0.0164, 0.0121, 0.0109) and within 40 per cent of the closed-form second-order
     values of `nrpic_cf` (0.0157, 0.0100, 0.0078), which omit the cross terms of the
     curvatures of different punctures.
 Refuted (the reading) if the differences do not fall from `p7_l3` on.
