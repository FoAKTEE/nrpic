# Interface: Newtonian mode of the particle module

Owner: core (branch `core/newton`). For tracks A, B and D (decision 0010): a Newtonian
reference gravity for the same particles and clouds inside AthenaK, so that a relativistic
run and its Newtonian reference differ in the gravity only. `cosmo/newton/pm.py` (Python,
periodic uniform mesh, spectral Poisson solve) stays as an independent check.

Labels: [VERIFIED] read in the source of this tree or measured in a registered run
(locator given), [JUDGEMENT] a design choice of this note, [TO VERIFY] not checked.

## 1. Assessment of the existing gravity and multigrid modules

Source: `athenak/src/multigrid/` (7647 lines) and `athenak/src/gravity/` (638 lines) at
commit b7b431d; file and line given per statement.

| Question | Finding | Locator |
|---|---|---|
| What is solved | `lap phi = four_pi_G rho`, seven-point Laplacian, red-black Gauss-Seidel smoothing (`omega`, default 1.15), V cycles; iterative mode (start from the previous `phi`) or full multigrid (`full_multigrid = true`); stop by `threshold` on the L2 defect norm, by `threshold = 0` (until the defect stops falling) or by a fixed number `niteration` | `mg_gravity.hpp` 26-39; `mg_gravity.cpp` 39-65, 177-245; `multigrid_driver.cpp` 729-860 [VERIFIED] |
| Boundary conditions | Periodic faces follow the mesh; every other face is zero Dirichlet by default; `<gravity> mg_bc` = `zerofixed`, `zerograd` or `multipole`. `multipole`: the potential on the faces is the multipole expansion of the source about its centre of mass (`auto_mporigin`) to order 2 or 4 (`mporder`), recomputed at every solve | `multigrid_driver.cpp` 82-91, 1835-2195, 2213-2434; `mg_gravity.cpp` 66-120; `multigrid_tasks.cpp` 129-366 [VERIFIED] |
| Periodic domain | The mean of the source is removed when the mesh is periodic in all directions (`subtract_average`, default true), and the mean of the solution after the cycles | `mg_gravity.cpp` 51, 88-90; `multigrid_driver.cpp` 239-256, 754-757, 867-901 [VERIFIED] |
| Refined meshes | Supported: levels finer than the root grid of MeshBlocks are solved on per-cell "octets" (Athena++ style) held in host memory; flux-conserving prolongation at fine-coarse faces; arrays are rebuilt when adaptive refinement changes the mesh | `multigrid.hpp` 72-122, 499-510; `multigrid_driver.cpp` 181-236, 263-447; `mg_gravity.cpp` 356-434 [VERIFIED by reading; not run here] |
| Mesh restrictions | Three dimensions; MeshBlocks logically cubic with a power-of-two size; a warning (not an error) when the grid of root MeshBlocks does not coarsen to one cell | `multigrid.cpp` 52-57, 133-144, 109-130; `multigrid_driver.cpp` 60-65 [VERIFIED] |
| Cards | The MeshBlock levels and the root grid are Kokkos device kernels (`root_on_host` moves the root grid to the host); the octets of refined meshes and the sums of the multipole moments over MeshBlocks run on the host | `multigrid.hpp` 251-312, 621-647; `multigrid_driver.cpp` 132-164, 1851-1960, 2230-2307 [VERIFIED by reading]; card run: section 5 |
| MPI | Rank-packed boundary buffers exist; the NRPIC particle module itself is single-rank | `multigrid.hpp` 562-618; `nrpic.cpp` 60-64 [VERIFIED] |
| What it needs from the hydrodynamics module | Only the source: `MGGravityDriver::Solve` loads `u0(IDN)` of `<mhd>` or `<hydro>` and would dereference a null pointer without either; the driver calls it at every stage of the time integrator whenever a `<gravity>` block exists. The loader itself, `Multigrid::LoadSource(array, component, nghost, factor)`, takes any cell-centred array. The force on the gas is applied elsewhere (`srcterms.cpp` 215-232) and is not needed | `mg_gravity.cpp` 197-199; `driver.cpp` 571-574; `multigrid.cpp` 289-320 [VERIFIED] |
| Does it work in this tree | Yes on an isolated uniform mesh with the multipole boundary: hydro test `binary_gravity`, unmodified executable, N = 32 and 64: maximum relative potential error 1.76e-2 and 4.49e-3 (ratio 3.93, second order); the defect falls by a factor 3.8 to 4.8 per V cycle; 20 cycles at 64^3 take 0.53 s on one core | runs core-20261115-112129-b7b431d, core-20261115-112130-b7b431d [VERIFIED] |
| Ghost cells of the result | `RetrieveResult` copies at most `mg_nghost` (default 1) ghost layers into `pgrav->phi`; the cubic interpolation of the particle module needs two (four with `interp = bspline`) | `multigrid.cpp` 420-451 [VERIFIED] |

## 2. Choice of the Poisson solver

Reuse the multigrid module [JUDGEMENT, on the findings above]. It serves both domains the
tracks need (periodic with the mean removed; isolated with the multipole boundary), it is
already written for refined meshes and for cards, and a second, self-contained solver on
the root mesh would duplicate it and would have to be extended to refined meshes later.
What has to be added is small:

1. a source other than the gas density (`MGGravityDriver::SolveSource`), and a guard so
   that the per-stage call of the driver does nothing when there is no gas;
2. ghost cells of the potential to the depth the particle interpolation needs: exchange
   between MeshBlocks with the mesh boundary machinery already used for the sources,
   cubic extrapolation at faces that are not periodic;
3. a solve that does not depend on the history of earlier solves (the red-black colour
   offset of the driver alternates from cycle to cycle and is not stored in restart
   files), so that a restarted run repeats the original one.

The cost of the choice: second-order (seven-point) Laplacian instead of the spectral
operator of `cosmo/newton`; the two references therefore agree to truncation error, not
to rounding (section 5 measures the difference and attributes it).

## 3. Design of the mode (sections 4 and 5 are filled in as the work proceeds)

See section 4.
