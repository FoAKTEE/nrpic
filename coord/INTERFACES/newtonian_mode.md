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
newton_mg_tol    = 0.0      # > 0: the Poisson solve may end when the defect norm is this
                            # fraction of the norm of four_pi_G (rho - <rho>); needs threshold = 0
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
Particles with zero (or negative) rest mass are tracers: they move in the potential and
carry no source (the field tests use them to sample the force).
The mode does not check that the mean density of the particles matches the scale factor
(for the matter era, `<rho> = 3 H^2/(8 pi G)` at `a = 1`); that is the caller's choice.
Complete inputs: `problems/newton/isolated.athinput`, `problems/newton/periodic.athinput`.

External gravity at the particles (work package dfix, test T4; read only if present):
`newton_pm_mass`, `newton_pm_x1..3`, `newton_pm_soft`, `newton_pm_soft_frame`
(`comoving` or `physical`): a fixed point mass with the potential
-G M/(r^2 + s^2)^(1/2), not deposited and not moved, nearest image in periodic
directions; `newton_bg_t0 > 0`: the acceleration -(2/9) x/(t0 + t)^2 of a matter-era
background (no expansion of the coordinates). The potential energy W of the history
counts the external potential in full. Details: `REQUESTS_ADF.md` section 2.4,
`athenak/src/particles/nrpic_external.hpp`. The accretion diagnostics (`diagnostics.md`
section 10a) work in this mode with E = 1 + p^2/(2 a^2) + Phi/a.
The Layzer-Irvine combination C of `<basename>.newton.hst` is conserved with
`newton_pm_soft_frame = comoving` (T4: drift 4.1e-5 and 1.0e-5 of a|W| at the steps 0.002
and 0.001, second order); with `physical` the potential depends on time explicitly
(s/a) and C is not a conservation check (5.6e-2 at both steps, runs
core-20261115-160805-5d1663f, core-20261115-162608-113493f, judged in
core-20261115-180144-83abe17); the orbits converge at second order in both frames.

### Output

`<basename>.newton.hst` (table above); `<basename>.nrpic.hst`, snapshots, trajectories
and restart files as in the relativistic mode (`docs/FORMATS.md`), with the potential in
the lapse columns.

### Lines of shared files touched (relative to `main` at b7b431d)

| File | Lines (new numbering) | Change |
|---|---|---|
| `athenak/src/particles/nrpic_newton.cpp` | new, 755 lines | the mode |
| `athenak/src/CMakeLists.txt` | 137 | new source file |
| `athenak/src/driver/driver.cpp` | 469 | stores the driver pointer before `NrpicStartup` (the multigrid solver runs task lists of the driver) |
| `athenak/src/gravity/mg_gravity.hpp` | 64-69, 83-85 | `SolveSource`, `last_defect`, `last_ncycle`; private `SolveDensity`, `until_stall_`, `stall_tol_` |
| `athenak/src/gravity/mg_gravity.cpp` | 178-217, 237, 259-301 | `Solve` returns when there is no gas and otherwise calls `SolveDensity` with the gas density (the former body, source passed as an argument); `SolveSource`; cycle control for `threshold = 0` in the particle path only |
| `athenak/src/particles/particles.hpp` | 25, 103-111, 261-293 | pusher `nrpic_newton`; six options; state and functions of the mode |
| `athenak/src/particles/particles.cpp` | 70-71, 121 | pusher name `newton`; destructor |
| `athenak/src/particles/nrpic.cpp` | 220-224, 273, 376, 705, 737-738, 1353-1357, 1380-1383 | mode flag, default of `deposit`, no `<adm>` needed; call of `NrpicNewtonInit`; branch in `NrpicPush`; `W = newton ? 1 : W_rel` in the deposit; branch in `NrpicDeposit` after the filter; branch in `NrpicInitializeSources` |
| `athenak/src/particles/nrpic_io.cpp` | 1129, 1225, 1249, 1287 | restart state write and read; Newtonian history at start and per cycle |
| `athenak/src/pgen/pgen.cpp` | 973-974 | `nrpic_newton` as a second name of the particles-only generator |

The gas path of the gravity module is the former code with the source as an argument;
its output is unchanged (section 5.1).

## 5. Tests

Predictions were written before each run and outcomes after it, including the failed
ones: `tracks/core/JOURNAL-newton.md`. Run manifests: `tracks/core/runs/<run id>/`;
outputs: `scratch/core/<run id>/`; numbers and figures: `tracks/core/analysis/newton/`
(`*.json`, `*.png`); scripts: `problems/newton/` (README there), `tracks/core/tools/`.
Units G = 1. All numbers [VERIFIED] with the run ids given; processor build unless a
card is named.

### 5.1 Relativistic runs are unchanged (regression)

Five existing problems (Kerr geodesic with the midpoint and with the Boris pusher,
deposit on a statically refined flat mesh, periodic cosmology with Z4c at 16^3,
Oppenheimer-Snyder ball with Z4c on a refined mesh), executable built from `main`
(b7b431d) against the executable of this branch (c061b12):

- processor build: all 33 output files (histories, trajectories, snapshots, restart
  files) identical byte for byte. Runs core-20261115-121314-c061b12 to
  core-20261115-121803-dc623d1 (report `scratch/core/regress/report_cpu_c061b12.json`);
  the same result for the first version, 728637a, and for the final source, 38067a2
  (it differs from c061b12 by the line breaks of one string literal; runs
  core-20261115-123108-38067a2 to core-20261115-123544-38067a2).
- gas with self-gravity (the entry point of the multigrid module was split): the stock
  problems `jeans_wave` (20 steps) and `binary_gravity` (one step, four levels of
  refinement) give identical output files and identical result lines in the log (280
  and 48 lines); runs core-20261115-122504-dc623d1 to core-20261115-122609-dc623d1.
- card build (Slurm job 4405): the two cases without deposit are identical. The three
  with deposit do not reproduce themselves from run to run on a card (the baseline
  differs from its own repeat at rounding level: positions 1.8e-15 at the last snapshot
  of the cosmology case), so identity cannot be tested there; the difference between
  baseline and new is of the same size (2.2e-15). Runs core-20261115-122024-dc623d1 to
  core-20261115-122046-dc623d1.

### 5.2 Field of a point mass (isolated domain)

Unit mass, 2000 massless tracers, box [-2, 2]^3, cloud-in-cell, no filter; runs
core-20261115-115136-9d84282 (N = 32), -115145- (64), -115155- (128); figure
`field_point.png`.

| | N = 32 | N = 64 | N = 128 | order |
|---|---|---|---|---|
| rms relative force error, 846 tracers with r >= 0.5 | 1.61e-2 | 4.94e-3 | 1.33e-3 | 1.70, 1.89 |
| the same by distance: 8 to 16 cells | 5.9e-3 | 6.5e-3 | 6.2e-3 | follows (dx/r)^2 |
| beyond 16 cells | | 1.7e-3 | 1.3e-3 | |
| inside 2 cells | 0.57 | 0.37 | 0.23 | softened, anisotropic |
| potential at 8 probes, rms relative error | 3.9e-3 | 9.4e-4 | 6.5e-4 | one probe not monotonic |

A particle feels its own field: the force of the unit mass on itself is of order
0.5 m/dx^2 (components up to 0.36, 0.58, 0.47 m/dx^2 at the three resolutions),
reproduced to seven digits by an independent numpy model of "cloud-in-cell deposit,
seven-point solve, gradient of the Catmull-Rom interpolant". It is a property of the
scheme that the relativistic mode shares (deposit and gather kernels differ); it
vanishes at a cell centre and for a regular lattice.

### 5.3 Field of a homogeneous ball (isolated domain)

Mass 1, radius 1, 1 099 136 lattice particles, 2000 tracers; runs
core-20261115-115137-9d84282 (N = 32), -115146- (64), -115203- (128); figure
`field_ball.png`. Reference: the homogeneous ball that the lattice samples (radius
1.000324: the lattice has 0.097 per cent more points inside the unit sphere than its
volume; against the nominal radius the error has a floor of 3.4e-4).

| error in units of GM/R^2 | N = 32 | N = 64 | N = 128 | order |
|---|---|---|---|---|
| force, rms, away from the surface (\|r - R\| > 0.25) | 7.25e-4 | 1.83e-4 | 5.09e-5 | 1.99, 1.85 |
| force, rms, in the shell \|r - R\| < dx | 2.23e-2 | 1.22e-2 | 6.4e-3 | 0.87, 0.93 |
| force, largest over all tracers | 6.8e-2 | 3.6e-2 | 1.5e-2 | 0.94, 1.22 |
| potential at 9 probes, largest relative error | 6.43e-3 | 1.60e-3 | 3.94e-4 | 2.01, 2.02 |

Second order where the density is smooth, first order in the cell that holds the density
jump (the cloud smears it).

### 5.4 Cold collapse of a homogeneous ball from rest against the cycloid

One particle per cell on the lattice of the cell centres, to t = 1.0 (0.90 free-fall
times, where the ball has shrunk to 0.35 of its radius); runs
core-20261115-115448-fee90ca (N = 64, 500 steps) and core-20261115-120028-fee90ca
(N = 128, 1000 steps, card); figure `collapse.png`.

| | N = 64 | N = 128 | ratio |
|---|---|---|---|
| mean of r/r_0 against the cycloid, t = 1.0 | +1.1e-4 | +9.0e-5 | (inner and outer cancel) |
| particles with r_0 < 0.8, t = 1.0 | -4.5e-3 | -1.05e-3 | 4.3 |
| particles with r_0 > 0.9, t = 1.0 | +1.07e-2 | +2.5e-3 | 4.3 |
| energy K + W, largest relative change | 1.45e-3 | 3.9e-4 | 3.7 |
| I_xx against the exact second moment, t = 1.0 | 7.0e-3 | 1.9e-3 | 3.8 |
| d2I_xx/dt2, half free-fall time | -1.9e-3 | -5.2e-4 | 3.6 |
| d3I_xx/dt3 (difference quotient), rms over the run | 8.6e-2 | 4.0e-2 | 2.2 |
| d3I_xx/dt3 averaged over 0.1 free-fall times, half free-fall time | +7.8e-3 | +3.8e-4 | |

The third derivative carries the fluctuation of the mesh force as the edge of the ball
moves across cells (first order in dx); average it over the time scale of interest
before squaring it in the quadrupole formula. The columns are consistent: the centred
time difference of I reproduces dI to 4.0e-5 at dt = 0.002 and 1.0e-5 at dt = 0.001
(factor 3.9); that of dI reproduces d2I to 7.6e-4 and 2.7e-4 (factor 2.8; see 5.9); d3I
equals the difference quotient of d2I to rounding. Momentum and angular momentum stay at
rounding level. With the mesh sum W_mesh instead of the particle sum the energy drifts
by 1.6 per cent (N = 64): use column 6.

### 5.5 Moving, rotating ball: conservation laws (no exact solution)

N = 64, ball off centre with a uniform velocity and a rigid rotation, to t = 0.8; run
core-20261115-120641-6bef558; figure `spin_N64.png`. Centre of mass off uniform motion
by 1.8e-5 R; momentum changes by 2.5e-5 M sqrt(GM/R); angular momentum about the centre
of mass by 4.3e-5 of its size; energy by 1.4e-4. All six components of the second
moment: difference of I against dI below 4.9e-6, of dI against d2I below 2.1e-5.
The scheme does not conserve momentum exactly (deposit and gather kernels differ).

### 5.6 Plane wave in a periodic expanding box

Amplitude 0.25 at a = 1 at the fundamental wavenumber, one particle per cell, shell
crossing at a = 4, run to a = 6.25; runs core-20261115-115706-fee90ca (N = 32) and
core-20261115-115708-fee90ca (N = 64); figure `wave.png`. Relative rms difference of
the positions (in units of the rms displacement):

| | N = 32 | N = 64 |
|---|---|---|
| against Zel'dovich, a = 2.25 / 3.52 | 5.6e-3 / 9.0e-3 | 2.1e-3 / 3.2e-3 |
| `cosmo/newton/pm.py` against Zel'dovich, a = 2.25 / 3.52 | 5.1e-3 / 8.3e-3 | 1.9e-3 / 2.8e-3 |
| against Zel'dovich with eight particles per cell (64^3 particles on the N = 32 mesh), a = 2.25 / 3.52 | 1.1e-3 / 1.4e-3 | |
| against `cosmo/newton/pm.py` (same particle file, mesh, cloud, step), a = 3.52 / 6.25 | 4.0e-3 / 6.1e-3 | 1.2e-3 / 2.0e-3 |
| against the scheme of the code in numpy, all 12 snapshots | <= 1.3e-15 | <= 6.5e-15 |
| Layzer-Irvine constant, before / after shell crossing, of max a\|W\| | 6.2e-4 / 4.9e-3 | 2.7e-4 / 1.5e-3 |

The error against Zel'dovich with one particle per cell falls only by 2.7 per doubling;
it is set by the particle lattice at the spacing of the mesh, not by the gravity solver:
with eight particles per cell on the same N = 32 mesh it is five times smaller (run
core-20261115-122313-dc623d1, which also agrees with the numpy scheme to 8.6e-16), and
`pm.py` behaves the same.
The difference from `pm.py` is the difference between the two discretisations (the
seven-point Laplacian and the gradient of the Catmull-Rom interpolant here, spectral
operators there) and falls with resolution (factor 3.3). The agreement with the numpy
re-implementation of the scheme to rounding, through shell crossing, is the statement
that the code does what section 3 says. With the options of the relativistic production
runs (triangular cloud, cloud compensation 1/8, two binomial passes and the
compensating pass; run core-20261115-121455-c061b12) the agreement with the numpy scheme
with the same options is 1.7e-15, the error against Zel'dovich at a = 2.25 is 1.5e-3 and
the Layzer-Irvine constant holds to 5.5e-5 before shell crossing.

### 5.7 Restart

Collapse (runs core-20261115-120109-fee90ca, continued core-20261115-120126-fee90ca) and
plane wave with expansion (core-20261115-120135-fee90ca, continued
core-20261115-120211-fee90ca): snapshots and both histories after the dump identical
byte for byte. Without the state file (core-20261115-120249-fee90ca) the continuation
differs at rounding level (7.8e-16 in position).

### 5.8 Card, cost, solver tolerance

Collapse at N = 128 (64 MeshBlocks of 32^3, 137 376 particles) on one A100: 0.65 s per
step with 13 V cycles (run core-20261115-120028-fee90ca, 0.18 card-hours); the
processor run of the same input (core-20261115-115450-fee90ca, one core of a loaded
machine) takes 3.2 s per step. Over the 1000 steps the two agree to 1.2e-13 in K and W
(largest relative difference of any record), to 2.7e-15 in the particle positions and
8.7e-15 in the momenta at t = 1.0; the number of V cycles differs at 5 of 1001 records
(`tracks/core/analysis/newton/card_vs_processor.json`). Not bitwise: the sums are
reduced in a different order.
With `threshold = 0` the solver runs to rounding: 13 to 19 V cycles per step. With
`newton_mg_tol = 1e-6` (collapse at N = 32, runs core-20261115-121044-c061b12 and
-121101-): 5.6 instead of 16.6 cycles, positions within 3.4e-9, energy error unchanged.
Step limit `newton_cfl = 0.2` (core-20261115-121108-c061b12): 19 steps instead of 200,
positions within 1.5e-4 of the radius.

### 5.9 Predictions that failed (kept on record; details in the journal)

- The first field test of the ball was void: with `threshold = 0` the stock rule of the
  multigrid driver ended the first solve after one V cycle (potential 13 per cent off).
  Fixed for the particle path (section 2, item 3 and section 4); the gas path keeps the
  stock rule, see section 6.
- The ball test had a floor of 3.4e-4 against the nominal radius: my reference was
  wrong (lattice ball), not the code.
- Collapse: I predicted that the mean radius lags the cycloid; the inner particles run
  ahead and only the outer shell lags.
- The difference quotient d3I is not accurate to ten per cent at one particle per cell
  on an aligned lattice (8.6 per cent rms at N = 64, 4.0 at N = 128); averaged over a
  tenth of the free-fall time it is (0.8 and 0.04 per cent).
- The centred difference of dI against d2I falls with the step by 2.8 (Catmull-Rom) and
  3.4 (cubic spline, runs core-20261115-121242/-121244-c061b12), not by 4: the force
  along a trajectory is not smooth in time. The kinks of the Catmull-Rom gradient
  account for part of it; the rest is not explained (candidate, untested: the kinks of
  the cloud-in-cell weights).
- Plane wave against Zel'dovich: the error falls by 2.7 per doubling with one particle
  per cell, not by 4. Cause established by a run that could have refuted it
  (core-20261115-122313-dc623d1): the particle lattice at the spacing of the mesh; with
  eight particles per cell on the N = 32 mesh the error at a = 2.25 falls from 5.6e-3
  to 1.1e-3. `cosmo/newton/pm.py` behaves the same.
- I assumed card runs reproduce themselves byte for byte; with deposit they do not.

## 6. Not done, limits, open points

**Refined meshes: a trial only.** On a mesh with one static level (point mass, run
core-20261115-121732-dc623d1) the solver converges, the force inside the fine region
equals that of the uniform fine mesh (all digits of the table of the journal), the
coarse region lies between the two uniform meshes, and within two coarse cells of the
level boundary the force error is one per cent rms and up to nine per cent on single
tracers. Not done: any run in which particles cross a level boundary; conservation on a
refined mesh; the level options of the deposit in this mode; adaptive refinement (the
re-initialisation after a mesh change is written, `NrpicNewtonInitialize`, and has never
run). [TO VERIFY] before any use on refined meshes.

**Cards.** Verified on one A100 for the isolated collapse on a uniform mesh only. Not
run on a card: the periodic and expanding case, restart, refined meshes (the octets of
the multigrid solver run on the host). Card time used by this work package: 0.19
card-hours (Slurm jobs 4382 and 4405).

**MPI.** Single rank, the restriction of the particle module (`nrpic.cpp` 60-64).

**Scale factor.** Power law only. No table, no cosmological constant, and no check that
the mean density of the particles matches the scale factor.

**Second moment.** About the origin of the coordinates; positions are wrapped on a
periodic mesh; the third derivative is a one-step difference quotient (section 5.4).
For gravitational waves from a periodic box the transverse-traceless stress in Fourier
space is the right quantity and is not provided here.

**Properties of the scheme that the tracks should know** (shared with the relativistic
mode, not faults of this mode): a particle feels its own field (0.5 m/dx^2); momentum
is not conserved exactly (2.5e-5 in the test of 5.5); the force is of first order in dx
in a cell that holds a density jump; with one particle per cell the discreteness error
of a cold lattice falls only at order 1.5.

**Solver.** Seven-point Laplacian, second order. Convergence factor about four per V
cycle (measured), 13 to 19 cycles per step to rounding; `newton_mg_tol = 1e-6` cuts it
to a third. The stock `threshold = 0` rule of the gas path can end a solve after the
first cycle (`multigrid_driver.cpp` 790-829; seen here with a zero starting potential
and the multipole boundary): not changed, because that would change gas runs; a point
for whoever uses self-gravitating gas.

**Isolated domain.** Ghost cells at the faces by cubic extrapolation; the multipole
expansion (order 4 about the centre of mass) was tested with the matter within 1.5 of
the centre of a box of half-width 2; matter close to a face was not tested. Particles
that leave the box are removed and counted (existing code).

**Not tested at production size.** Largest run: 128^3 cells, 1.1e6 particles (field
test), 1.4e5 particles (collapse).
