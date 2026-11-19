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

(Section filled after the runs: journal entries 4 to 8.)

## 6. Limits and what a track must know

(Section filled after the runs.)

## 7. Answers to the requests

(Section filled after the runs.)
