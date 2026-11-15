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

## 3. Design of the mode

Source: `athenak/src/particles/nrpic_newton.cpp` (new), with hooks listed in section 4.

**Equations.** The time coordinate `t` of the run is conformal time, the positions `x`
are comoving, and the momentum slots of the particle file hold `p = a dx/dt` per unit
rest mass:

    dx/dt = p/a,      dp/dt = -grad Phi,      lap Phi = four_pi_G (rho - <rho>),

with `rho` the rest-mass density per coordinate volume deposited by the particles and
`a(t)` a prescribed scale factor. The Newtonian potential is `Phi/a`. The mean `<rho>`
is removed on a mesh that is periodic in all directions, and only there. Without
expansion (default) `a = 1`, `t` is the Newtonian time and `p` the velocity. With
`newton_expansion = power`, `a = (1 + H t/n)^n` with the Hubble rate `H = newton_hubble`
at `t = 0` (where `a = 1`) and `n = newton_exponent` (2: matter era, the form of
`cosmo/newton/pm.py`; 1: radiation era). The equation of motion of `p` has no explicit
time dependence for any `a(t)`, so the scale factor enters only through the drift, whose
integral of `dt/a` over the step is taken in closed form. The same particle file serves
the relativistic run: in the weak-field, slow-motion limit of a run in conformal time
(`d_t alpha = -(1/3) alpha^2 K`, `gamma_ij = a^2 delta_ij`) the covariant `u_i` equals
`a dx/dt`.

**One cycle** (kick-drift-kick; task order of the relativistic mode):

| Task | Newtonian mode |
|---|---|
| `NrpicPush` -> `NrpicNewtonPush` | `p += (dt/2) g^n(x^n)`, `x += p int dt/a`, with `g = -grad Phi` |
| `NrpicExcise` (unchanged) | periodic wrap, removal of particles that left the mesh, MeshBlock ownership |
| `NrpicDeposit` | existing `NrpicDepositSources` with the Lorentz factor replaced by one (rest mass in the E slot of the source array, momentum density in S_i), existing `NrpicFilterSources` (binomial passes, compensation), existing cloud compensation |
| -> `NrpicNewtonFinishStep` | Poisson solve, ghost cells, `p += (dt/2) g^{n+1}(x^{n+1})`, particle sums, step limit |
| `NrpicDiagnostics` (unchanged) | histories, snapshots, trajectories, probes |

**Where the potential lives.** In the lapse slot of the metric array `met1`; the other
nine slots hold the flat metric. The deposit (which reads the metric at the particle)
and the interpolation `nrpic::MeshMetric` (Catmull-Rom, or the cubic spline through the
nodes with `interp = bspline`) then run unchanged, and the gradient of the interpolated
lapse is the gradient of the potential: the gather is the same code as in the
relativistic mode, not a copy. Consequence: every existing diagnostic that reports the
lapse reports `Phi` in this mode (history columns `alpha_probe`, `alpha_min`,
`alpha_max`, the probes); the proper-time columns are the time integral of `Phi` and
have no meaning.

**Poisson solve.** `MGGravityDriver::SolveSource(driver, array, component)` of the
gravity module (section 2). Ghost cells of the result: exchange between MeshBlocks and
across periodic faces with a `MeshBoundaryValuesCC` object for one variable (restriction
and prolongation across levels as for the sources), cubic extrapolation at faces that are
not periodic, one direction after the other so that edges and corners are filled. On a
periodic mesh the mean of the potential is set to zero.

**Diagnostics** (`<basename>.newton.hst`, one record every `hist_dcycle` cycles; all
sums over particles with their rest mass, tracers and null particles carry none). With
`v = p/a` and `acc = g/a - (da/dt / a) v`:

| Columns | Content |
|---|---|
| 1-4 | time, cycle, scale factor, total rest mass |
| 5 | kinetic energy `K = sum m v^2/2` |
| 6 | potential energy `W = sum m Phi(x)/(2a)`, potential interpolated to the particles as in the force |
| 7 | `W_mesh = int (rho - <rho>) Phi dV/(2a)`, mesh sum with the filtered density |
| 8, 9 | `C = a (K + W) + int K da` and the integral (trapezoidal rule over the steps). `C` is constant in time (Layzer-Irvine); without expansion it is the energy `K + W` |
| 10-12, 13-15, 16-18 | `sum m p`, `sum m x cross p` (about the origin), centre of mass |
| 19-24 | second moment `I_ij = sum m x_i x_j` (xx, xy, xz, yy, yz, zz) |
| 25-30 | `dI_ij/dt = sum m (x_i v_j + v_i x_j)` |
| 31-36 | `d2I_ij/dt2 = sum m (2 v_i v_j + x_i acc_j + acc_i x_j)`, with the acceleration that the kick applies |
| 37-42, 43 | `d3I_ij/dt3` as the difference quotient of columns 31-36 over the last step, and the mid-step time it belongs to |
| 44-47 | minimum and maximum of `Phi` on the mesh, largest `|p|`, largest `|g|` |
| 48, 50 | defect norm and number of V cycles of the last Poisson solve |
| 49 | the step just taken |

The trace-free quadrupole and the quadrupole-formula luminosity follow from columns
19 to 43: `python/nrpic/newton.py`, `quadrupole`, `quadrupole_luminosity`. On a periodic
mesh the positions are wrapped and the second moment is of limited meaning.

**Restart.** Next to `<name>.rst.prt` the mode writes `<name>.rst.prt.nwt`: the sums of
the last synchronised state, the Layzer-Irvine integral, the third derivative, and the
potential (it is the starting guess of the next solve). With it a continued run repeats
the uninterrupted one byte for byte; without it (a dump of another mode) the potential is
solved for again and the continuation agrees to rounding.

## 4. Interface

### Input

```
<particles>
pusher           = newton   # switches the mode on (midpoint, boris: relativistic)
newton_expansion = none     # none | power: a = (1 + newton_hubble t/newton_exponent)^newton_exponent
newton_hubble    = 0.0      # Hubble rate at t = 0, where a = 1
newton_exponent  = 2.0      # 2: matter era, 1: radiation era
newton_cfl       = 0.0      # > 0: step <= c dx a/max|p| and <= sqrt(2 c dx a/max|g|)
dt               = ...      # upper limit of the step (required unless newton_cfl > 0)
<gravity>
four_pi_G        = 12.566370614359172   # G = 1
threshold        = 0.0      # 0: V cycles until two in succession lower the defect by
                            # less than ten per cent; > 0: absolute L2 defect norm
mg_bc            = multipole  # isolated domain (omit on a periodic mesh)
mporder          = 4
<problem>
pgen_name        = nrpic_newton   # nothing is set on the mesh
```

Used unchanged from the relativistic mode: `particle_file` (or the inline list),
`deposit_shape`, `nfilter`, `filter_compensate`, `filter_comp_c`, `deposit_comp_c`,
`deposit_comp_c2`, `deposit_comp_limit`, the level options of the deposit, `interp`,
`hist_dcycle`, `snap_dt`, `traj_*`, the probes. Not allowed together with the mode:
`<z4c>`, `<adm>`, `<hydro>`, `<mhd>` (fatal error with a message). Requirements of the
multigrid solver: three dimensions, cubic MeshBlocks with a power-of-two size.
The mode does not check that the mean density of the particles matches the scale factor
(for the matter era, `<rho> = 3 H^2/(8 pi G)` at `a = 1`); that is the caller's choice.
Complete inputs: `problems/newton/isolated.athinput`, `problems/newton/periodic.athinput`.

### Output

`<basename>.newton.hst` (table above); `<basename>.nrpic.hst`, snapshots, trajectories
and restart files as in the relativistic mode (`docs/FORMATS.md`), with the potential in
the lapse columns.

### Lines of shared files touched (relative to `main` at b7b431d)

| File | Lines (new numbering) | Change |
|---|---|---|
| `athenak/src/CMakeLists.txt` | 137 | new source file |
| `athenak/src/driver/driver.cpp` | 469 | stores the driver pointer before `NrpicStartup` (the multigrid solver runs task lists of the driver) |
| `athenak/src/gravity/mg_gravity.hpp` | 64-67, 81-82 | `SolveSource`, `last_defect`, `last_ncycle`; private `SolveDensity`, `until_stall_` |
| `athenak/src/gravity/mg_gravity.cpp` | 178-215, 235, 257-298 | `Solve` returns when there is no gas and otherwise calls `SolveDensity` with the gas density (the former body, source passed as an argument); `SolveSource`; cycle control for `threshold = 0` in the particle path only |
| `athenak/src/particles/particles.hpp` | 25, 103-109, 259-291 | pusher `nrpic_newton`; five options; state and functions of the mode |
| `athenak/src/particles/particles.cpp` | 70-71, 121 | pusher name `newton`; destructor |
| `athenak/src/particles/nrpic.cpp` | 220-224, 273, 376, 705, 737-738, 1353-1357, 1380-1383 | mode flag, default of `deposit`, no `<adm>` needed; call of `NrpicNewtonInit`; branch in `NrpicPush`; `W = newton ? 1 : W_rel` in the deposit; branch in `NrpicDeposit` after the filter; branch in `NrpicInitializeSources` |
| `athenak/src/particles/nrpic_io.cpp` | 1129, 1225, 1249, 1287 | restart state write and read; Newtonian history at start and per cycle |
| `athenak/src/pgen/pgen.cpp` | 973-974 | `nrpic_newton` as a second name of the particles-only generator |

The gas path of the gravity module is the former code with the source as an argument;
it was not run here (no hydro regression), see section 6.
