# Interface: initial-data solver, second pass (far field, moving matter, refined meshes, punctures, CMC slices)

Owner: core (branch `core/id-solver-2`, work package idsolve2 of wave 3a, started from
`core/id-solver`). For tracks A, B, D and F. The first pass (`id_solver.md`, options
`id_solve`, `id_vector`) stays valid; this document lists what the second pass adds and
changes. Journal with predictions and outcomes: `tracks/core/JOURNAL-idsolve2.md`.

Labels: [VERIFIED] read in the source of this branch (file and line) or measured in a
registered run (run id), [JUDGEMENT] a design choice or reading, [TO VERIFY] open.
Units G = c = 1; an expanding slice has K < 0.

## 1. What the second pass does

Same equations as the first pass (`id_solver.md` sections 1, 2, 10): on the slice
gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij + (1/3) psi^4 delta_ij K, with K held
fixed and Abar_ij = Abar_ij(trial) + (L W)_ij,

    lap psi = -(1/8) psi^-7 Abar_ij Abar_ij + (1/12) psi^5 K^2 - 2 pi psi^5 E[psi],     (1)
    lap W_i + (1/3) d_i d_j W_j = 8 pi Stilde_i + (2/3) psi^6 d_i K - d_j Abar_ij(trial), (2)

E and Stilde = psi^6 S_i deposited by the module itself in every evaluation. New:

1. **Far field at the faces** (option `id_far`, default `multipole`). The first pass
   filled ghost cells of psi - 1 and W_i by r u = const between a ghost cell and its
   mirror cell, which is exact for a monopole only; the far field of W depends on the
   direction already at order 1/r (Bowen-York, r W_i = -(7 P_i + n_i n.P)/4
   [BACKGROUND]), and the closure error of W at the faces was 0.9 per cent whatever the
   resolution (first pass, V2). Now the same 1/r fill acts on u - u_far, where u_far is
   the exterior multipole expansion (orders 0 to `id_far_lmax` = 4) of the right side of
   (1) (for psi) and of (2) (for W, through W_i = (7/8) V_i - (1/8)(d_i U + x_j d_i V_j),
   lap V_i = s_i, lap U = -x_j s_j) about the Robin centre, with raw moments of degree
   <= 4 summed over the cells inside the largest sphere about the centre that fits into
   the mesh (`id_far_radius` times that radius) [VERIFIED: `particles/nrpic_idfar.hpp`
   1-171; `nrpic_idsolve.cpp` 629-779]. The fill is affine in the field with the linear
   part of the plain fill, so inner iterations are unchanged; the moments lag one outer
   iteration. The record gets the far-field line M_psi, P_ADM, J_ADM (section 5).
2. **Moving matter in the scalar part.** psi^5 E = sum m W/(psi dV) with
   W^2 = 1 + psi^-4 u_i u_i: the Jacobian sigma of (1) gets + 4 pi psi S (S the trace of
   the deposited stress), exact for moving particles without filter
   (`nrpic_idsolve.cpp` 911-914, 949). For particles at rest S = 0 and nothing changes.
3. **Refined meshes** (static; adaptive meshes have the same level structure at t = 0).
   Ghost cells of psi, W and of every correction across levels by the restriction,
   exchange and prolongation that Z4c uses (`MeshBoundaryValuesCC` with the coarse
   array; plain 1/r fill on the coarse array at the faces) (`nrpic_idsolve.cpp` 574-607).
   With `id_residual = code` every evaluation writes the metric through the Z4c variables
   and their own exchange and back (871-878), so that the residual driven to zero is the
   constraint monitor of the run on its level structure, level boundaries included. The
   seven-point operator with prolongated ghost cells is not symmetric: BiCGStab with the
   multigrid solve as right preconditioner (`id_lin_solver`, default `bicgstab` on a
   refined mesh, `cg` otherwise; 1451-1487). The multigrid solver gets the Robin fill on
   its octets (`MultigridDriver::RobinBoundaryOctet`, `multigrid/multigrid_robin.cpp`
   95-151), so `mg_bc = robin` now works on a refined mesh. With the vector part in mode
   code, the cells within ng - 1 cells of a level boundary use the stencil form of (2)
   (their monitor differentiates K_ij across prolongated ghost cells and sees the
   difference of the truncation errors of L W on the two levels over the cell size,
   which no correction of W removes) (405-466). Dump per MeshBlock:
   `<basename>.idsolve.blk.bin`.
4. **Punctures** (components `comp<c>_type = puncture` of `nrpic_cf`, read from
   `<problem>`: position, bare mass, momentum, spin; `nrpic_idsolve.cpp` 210-240):
   psi = psi_s + u with psi_s = 1 + sum m_c/(2 |x - x_c|) in closed form on every cell
   (517-539); the seven-point operator acts on u only (917-939); within
   `id_puncture_radius` bare masses of a puncture the residual is the stencil form
   whatever `id_residual` (the monitor differentiates psi^4 with psi ~ m/2r); the
   Bowen-York curvature of the punctures, divergence free, is subtracted from the trial
   curvature before its numerical divergence enters (2) (540-555); the far field is
   psi_s + u_far. A puncture on a cell centre is refused. The problem generator's own
   corrections (`comp<c>_corr = approx`, `table`) only change the start value.
5. **Slices of constant mean curvature on the torus** (Track A's phase-1 generator):
   nothing new in the source; the existing machinery (Newton steps with the Jacobian
   sigma, conjugate gradients preconditioned by the Poisson multigrid, the vector part on
   the torus with the mean of its residual removed, refined levels) is tested on Track
   A's gradient-expansion peak in section 7 (test G).

Default behaviour [VERIFIED by reading `NrpicIdSolveInit`, `nrpic_idsolve.cpp` 113-251]:
without `id_solve` nothing is read or called (test R0: byte-identical to release
core-v0.3). With `id_solve` on a mesh with no periodic face the far field is ON by
default (`id_far = robin` restores the first pass; test R1: byte-identical to the
first-pass executable for matter at rest). The new options are read only when present.

## 2. Options (`<particles>` block, all read only if present)

| Option | Default | Meaning |
|---|---|---|
| `id_far` | `multipole` | `multipole`: 1/r fill of u - u_far at faces that are not periodic (every face must be a Robin face); `robin`: the plain 1/r fill of the first pass |
| `id_far_lmax` | 4 | highest multipole order of u_far (0 to 4); the moments are always accumulated to degree 4 |
| `id_far_radius` | 1.0 | the moments are summed over the sphere of this fraction of the distance from the Robin centre to the nearest face |
| `id_lin_solver` | `bicgstab` on a refined mesh, `cg` otherwise | linear solver of the Newton step |
| `id_punctures` | `true` | `false`: ignore the puncture components of `nrpic_cf` (psi_s = 1) |
| `id_puncture_radius` | 1.0 | in bare masses: within it the residual is the stencil form whatever `id_residual` |

`<gravity> mg_bc = robin` with `robin_x1..3` (the centre of the 1/r fall-off and of the
multipole expansion) is now accepted on refined meshes. Every option of the first pass
(`id_solver.md` section 6) keeps its meaning.

**Requirements** (fatal error otherwise): those of the first pass, except that a refined
mesh (static) is now allowed; the far field needs the Robin centre inside the mesh; no
puncture on a cell centre; at most 8 punctures.

## 3. Outputs

`<basename>.idsolve.txt`: a second header line (`# second pass: ...`) and, with the far
field, a last line `# far field: M_psi = ..., P_ADM = (...), J_ADM = (...)`; on a refined
mesh with `id_dump = true` the block dump `<basename>.idsolve.blk.bin` instead of
`.idsolve.bin` and `.idvector.bin`. Formats: `docs/FORMATS.md`, section "Initial-data
solver"; readers `tracks/core/analysis/idsolve2/lib2.py` (`summary`, `far_line`,
`read_blk`, `blk_coords`).

**M_psi is the mass of the monopole of psi inside the sphere of the moments**,
psi -> 1 + M_psi/2r: the bare masses of the punctures minus (1/2 pi) times the integral of
the right side of (1) over that sphere. It is the ADM mass only when the source inside the
sphere is all the source: for Bowen-York curvature (falling as r^-4) the part outside is
missing (section 7, P1), and for a table of format 2 the Painleve-Gullstrand exterior
curvature contributes K^2 terms. P_ADM = (1/8 pi) times the integral of the right side of
(2) plus the momenta of the punctures; J_ADM from its antisymmetric first moment plus the
spins and x_c times P_c of the punctures.

## 4. Lines of shared files touched (all of `core/id-solver` and `core/id-solver-2` against main)

New files: `athenak/src/particles/nrpic_idsolve.cpp`, `nrpic_idfar.hpp`,
`athenak/src/multigrid/multigrid_robin.cpp`. Lines of shared files (this branch):

| File | Lines | What |
|---|---|---|
| `athenak/src/CMakeLists.txt` | 103, 141 | the two new source files |
| `athenak/src/bvals/bvals.hpp` | 21 | `BoundaryFlag::mg_robin` appended to the enum |
| `athenak/src/gravity/mg_gravity.cpp` | 77-92, 221-241 | `mg_bc = robin` and its centre (the refusal on refined meshes of the first pass is removed); `SolvePoisson` |
| `athenak/src/gravity/mg_gravity.hpp` | 68-71 | `SolvePoisson`, `Threshold` |
| `athenak/src/multigrid/multigrid.hpp` | 397-402, 506-508, 691-779 | Robin methods (with `RobinBoundaryOctet`, new) and members; `MGRobinFill` |
| `athenak/src/multigrid/multigrid_driver.cpp` | 1726 (new), 2194-2195 | `if (robin_) { RobinBoundaryOctet(oct, fcbuf); return; }` at the top of `ApplyPhysicalBoundariesOctet`; `if (robin_) RobinBoundaryRoot();` |
| `athenak/src/multigrid/multigrid_tasks.cpp` | 360-361 | `if (robin_) RobinBoundaryBlocks();` |
| `athenak/src/particles/nrpic.cpp` | 276 | `NrpicIdSolveInit(pin);` |
| `athenak/src/particles/nrpic_io.cpp` | 1237 | `NrpicSolveInitialData();` |
| `athenak/src/particles/particles.cpp` | 122 | delete `pbval_ids` |
| `athenak/src/particles/particles.hpp` | 153-176, 375-380 | `NrpicIdSolveOptions` (second-pass members 169-175, new); `ids_coarse`, `ids_punc` (new), methods |
| `docs/FORMATS.md` | 142-154 | output files (second-pass rows new) |

## 5. Tests

Predictions and outcomes, failed predictions included: `tracks/core/JOURNAL-idsolve2.md`
entries 1 to 9. Scripts, numbers, figures: `tracks/core/analysis/idsolve2/` (`test_*.py`,
`*_numbers.json`, `figs/`). Processor build of 76add0c (the published source) unless
stated. All numbers [VERIFIED] in the runs named.

| Test | What it shows | Outcome |
|---|---|---|
| R0 | without `id_solve` nothing changes | all 59 output files of nine set-ups (geodesics with both pushers, deposit on a refined mesh, East's cosmology, Oppenheimer-Snyder on a refined mesh, Jeans, a binary on four multigrid levels, the Newtonian mode isolated and periodic) byte-identical to release core-v0.3 (run core-20261119-154842-de22625, `regress_r0.json`) |
| R1 | `id_far = robin` is the first pass | for matter at rest every output byte-identical to the first-pass executable; moving matter: psi to 6e-15, W to 5e-16 (the new term of sigma) (run core-20261119-145332-1ac049d) |
| W1 | far field of a moving Gaussian (faces at 8 sigma) against the semi-analytic continuum W | relative error of W_x at the x-face centres: plain fill -8.6e-3, -9.3e-3; far field +9.3e-4, +2.4e-4 at 32, 64 cells (falls by 3.9 per halving); largest error over the outermost layer 2.2e-2 (plain) against 1.2e-3, 3.0e-4 (far); P_ADM of the record equals sum m u_x to 3e-13; the surface integral of (L W)_xj converges at second order to it with either fill (core-20261119-145332-1ac049d; 128 cells: @W128@) |
| W2 | off-centre moving Gaussian | largest error over the outer layer 5.6e-4 (lmax 4), 0.116 (lmax 0), 0.108 (plain fill); J_ADM = -2 P_ADM to 6e-10 (the 1.4e-9 of the momentum outside the sphere of the moments) |
| C1 | coupled solve with fast particles (u_x = 1, W = 1.4) | 30 and 36 outer iterations at 32 and 64 cells; max\|H\| of the monitor 0.57 -> 2.1e-11; max\|M\| 0.20 -> 3.3e-7 |
| B | end-to-end: expanding ball (M = 1, Rb = 10, edge 2) with a triaxial Zel'dovich displacement and its momenta; solve and evolution to t = 2 | @B@ |
| C | refined meshes (static), torus | Gaussian on one and two static levels: mode code 20 and 22 outer iterations; the run's own monitor at t = 0 at 2.4e-12 to 2.0e-11 on every level, level boundaries included; central error equal to the uniform run of the finest cell size (-5.01e-3 against -5.03e-3); torus with a refined cube and a nested lattice: max\|H\| 2.6e-10 and 1.15e-9 on the two levels (0.73 and 1.86 without the solve); torus with moving matter at density contrast up to 9: converges (24 to 33 iterations); the refined Zel'dovich ball evolves like the uniform run of the same cell size to 1 per cent in the matter. Failed: the vector part on a refined mesh stalls at the level boundary (max\|M\| 9.8e-2 -> 2.0e-2 on the refined torus) (runs core-20261119-153510-d1eaa30, analysis -161309-b04b4dd) |
| G | Track A's CMC peak (gradient-expansion data on K = -3H, eps_i = 0.2, e = 0.2, torus of 100 Hubble lengths) solved by the code from psi = 1 | converges for mu = 0.03, 0.3, 0.5, 0.7 in 8 to 11 outer iterations (Track A's Python solve diverged at 0.5); solved psi equals psi_GE to c = 1.0e-7, 3.6e-7, 5.2e-7, 6.3e-7 of the perturbation at 64^3 (1.6e-5 at 32^3 for mu = 0.5); monitor after 3e-10 to 3e-9; with the vector part the same psi and max\|M\| 1.6e-7 -> 1.7e-9 (run core-20261119-160329-ab0aa92) |
| P | punctures | @P@ |
| K | card build on one A100 | @K@ |

## 6. Limits and what a track must know

**Before use** (in addition to `id_solver.md` section 9, which stays valid):

- **Judge data in the matter region, never over the whole mesh.** The outflow faces of
  Z4c dominate whole-mesh norms of |H| and |M| within a few steps whatever the data
  (first pass, test F; here B (g): the face layer has the same mean |H| at t = 2 in all
  four data sets of one resolution). Use region norms (interior, shell; the script
  `test_b.py`, `region_stats`, shows how) or the solver's record.
- **M_psi of the far-field line is not the ADM mass** of Bowen-York data (their r^-4
  source outside the sphere of the moments is missing; P1) nor of a table of format 2
  (its Painleve-Gullstrand exterior carries the mass in K). P_ADM and J_ADM of the line
  are exact sums of the deposit and the punctures inside that sphere.
- **Vector part on refined meshes**: with `id_vector_residual = code` the monitor of
  the momentum constraint stalls at the level boundaries (C: refined torus max|M| 2.0e-2
  after the solve against 2.6e-4 on the uniform mesh; refined ball 2.6e-4 against
  2.6e-6), because L W is formed with second-order differences on each level and the
  monitor differentiates K_ij across prolongated ghost cells. Away from the boundaries
  the vector part solves as on a uniform mesh (interior mean of |M| the same), and the
  evolution of the refined Zel'dovich ball matches the uniform run to 1 per cent (C, Z).
  The scalar part is not affected.
- **Punctures**: @PUNC@
- **Large tori**: on a box of many Hubble lengths (G: L H = 100) the Poisson
  preconditioner of the Newton step is poor (sigma/k_min^2 of order 1e3); the inner
  solve uses all `id_lin_maxit` = 50 steps in about half of the Newton steps, and the
  Newton iteration still converges in about 10 steps (G).
- **Cost** (processor, one core): moving Gaussian at 64 cells with the far field about
  as the first pass; Zel'dovich ball at 64 cells with both parts in mode code 400 s
  (44 outer iterations), at 128 cells @COST128@; CMC peak at 64^3 115 to 150 s on two
  cores.

**Not done or not tested**:
1. MPI (single rank, as the particle module); adaptive refinement beyond the level
   structure at t = 0 (the solve runs once, on the mesh as it is at the start).
2. A fourth-order L W for the vector part on refined meshes (would lower the stall at
   level boundaries by about (k dx)^2); a far field for meshes with some periodic and
   some open faces (the plain fill is used there).
3. Trial metrics that are not conformally flat (fatal error); a field format with a
   conformal metric (Track A's request 5, second half).
4. Lapse and shift stay those of the problem generator (a lapse that depends on psi
   refers to the trial psi).
5. Puncture combinations not run: punctures with a table of format 2, with `nrpic_cosmo`;
   spinning punctures with matter.
6. Card executable: @CARD@

## 7. Answers to the requests

**Track A, `20261115T183720Z__to-core__refined-level-constraint-solve.md`** ("whether the
id-solver handles static refinement, and a date for the nested lattice"): yes, from this
branch. The solve runs on the level structure of the run (static refinement), with the
deposit of the module on every level, and in mode code the residual driven to zero is
the run's own Hamiltonian monitor after the Z4c exchange across levels: at t = 0 the
monitor is at 1e-11 to 1e-9 on every level, level boundaries included (test C: Gaussian
on one and two levels, torus with a refined cube; Track A measured 0.077 to 0.18 with data
interpolated onto refined blocks). Nested lattice: `problems/idsolve/make_ic.py wave
--nest x0 x1` writes a lattice twice finer inside a cube (used in C, `t_smr`); the same
in `cosmo/ic/make_field.py` is not done here (not in this package's paths). The momentum
part on refined meshes has the limit of section 6.

**Track A, `20261115T183719Z__to-core__phase1-generator-cmc.md`** ("whether core/id-solver
will take this, and a date"): the machinery is in place and tested on Track A's own data
(test G): with K = -3H held fixed, the trial psi_GE, Ahat_GE from a field file
(`nrpic_cosmo id = file`, format NRCOSMO1) and particles carrying E and J, the code's
Newton iteration (variable-coefficient Jacobian sigma, conjugate gradients with the
multigrid preconditioner) converges from psi = 1 for mu = 0.03 to 0.7 at the paper's
start eps_i = 0.2 and returns psi_GE to c = 1e-7 to 6e-7 at 64^3; the vector part removes
the remaining momentum residual (max|M| 1.6e-7 -> 1.7e-9). Acceptance (a) of DESIGN.md 2.3
is met at 64^3 for mu = 0.03 and 0.5 (c far below O(eps^4) = 1.6e-3); (b) the monitor at
t = 0 is at 3e-9 or below. Not provided by core: the generator of the gradient-expansion
fields and particles (Track A's `ge_fields`; `tracks/core/analysis/idsolve2/test_g.py`
shows a complete use, with one particle per cell at the cell centres), a field format
with a non-conformally-flat metric, and acceptance (c) (an evolution: Track A's).

**Track F (three punctures) and Track D (dressed punctures)**: punctures of `nrpic_cf`
enter the solve as psi_s + u (section 1, item 4); P1 to P5 show what is verified.
@PANSWER@
