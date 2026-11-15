# Interface: elliptic solver for initial data inside the code

Owner: core (branch `core/id-solver`, work package idsolve of wave 2). For tracks A, B, D
and F. Decision 0010, consequence 4: initial-data solves beyond spherical symmetry go
into the code. This document replaces the offline solver proposed in
`coord/notes/design_wave2_initial_data.md`, section 2 ("Where to implement").

Labels: [VERIFIED] read in the source of this tree (file and line) or measured in a
registered run (run id), [JUDGEMENT] a design choice, [TO VERIFY] not checked.
Units G = c = 1. Sections 1 to 5 were written before any source line of the solver;
sections 6 to 9 after the tests.

## 1. Scope of this wave

The scalar (Hamiltonian) constraint for the conformal factor on the mesh of the code,
with the matter density that the code itself deposits, on a uniform mesh with periodic
faces or with Robin faces:

    lap psi = -(1/8) psi^-7 Abar_ij Abar_ij + (1/12) psi^5 K^2 - 2 pi psi^5 E[psi].    (1)

Slice: gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Abar_ij + (1/3) psi^4 delta_ij K.
`E[psi]` is the energy density of the particle module on the mesh for the metric
psi^4 delta_ij: deposit of m W per coordinate volume with the cloud of the run and its
compensation, division by sqrt(gamma) = psi^6 of the cell, filter passes. For particles
at rest in the slice (u_i = 0, W = 1) and no filter, psi^5 E = psi^-1 Etilde with
Etilde = sum m S/dV independent of psi: the form of the work package.

Not in this wave (section 5): the vector equation for the correction of Abar_ij,
refined meshes, punctures.

## 2. What is held fixed and what is solved for

The problem generator sets a trial state as it does now (`nrpic_cf`: tables of format 1
and 2, Gaussians, spheroid; `nrpic_cosmo`: homogeneous or a field file). From the ADM
variables of that state the solver takes, per cell [JUDGEMENT]:

    psi_t   = (det gamma)^(1/12)                       trial conformal factor,
    K       = gamma^ij K_ij                            held fixed,
    Abar_ij = psi_t^2 (K_ij - (1/3) gamma_ij K)        held fixed,

and solves (1) for psi. Then K_ij = psi^-2 Abar_ij + (1/3) psi^4 delta_ij K with the
solved psi. This covers the three sources of K and Abar that the work package names:

- zero (format-1 components of `nrpic_cf`): K = 0, Abar = 0;
- a table of format 2: `nrpic_cf` sets K_ij = psi_t^4 [KT delta_ij + (KL - KT) n_i n_j]
  (`nrpic_cf.cpp` 286-296 [VERIFIED]), hence K = KL + 2 KT and
  Abar_ij = psi_t^6 (KL - KT)(n_i n_j - delta_ij/3);
- fields set by the problem generator (`nrpic_cosmo` with `id = file`, Bowen-York
  curvature of `nrpic_cf`): whatever is in `adm.vK_dd`.

The trial metric must be conformally flat (fatal error otherwise). Lapse and shift are
not touched: they stay as the problem generator set them (a lapse option that depends
on psi, `isotropic` or `precollapsed`, therefore refers to the trial psi) [JUDGEMENT].

Well-posedness [BACKGROUND, as in the design note, section 1]: with
sigma = d(right side)/d psi = (7/8) psi^-8 Abar^2 + (5/12) psi^4 K^2 + 2 pi psi^4 E >= 0
the linearised operator lap - sigma is negative definite, on the torus provided sigma
does not vanish identically (K = 0 and matter on the torus has no solution: the mean of
the right side of (1) cannot vanish).

## 3. Where it runs in the start-up sequence

[VERIFIED by reading: `driver.cpp` 460-475, `nrpic_io.cpp` 1233-1274, `nrpic.cpp` 1381-1416]

    Mesh construction      problem generator: trial ADM state, ADMToZ4c
    Driver::Initialize     1. ghost cells of the Z4c state
                           2. Particles::NrpicStartup(restart flag)
                                NrpicCreateParticles          (new run only)
                                NrpicSolveInitialData         (new; new run only, option)
                                NrpicInitializeSources        Z4cToADM, metric at the
                                                              particles, deposit, filter,
                                                              constraints
                                first diagnostics
                           3. scalar field, first time step

`NrpicSolveInitialData` (new file `athenak/src/particles/nrpic_idsolve.cpp`) is one
call between the creation of the particles and the existing initialisation. On exit the
Z4c state holds the solved data with its ghost cells exchanged as in step 1, and the
existing `NrpicInitializeSources` runs unchanged on it. A restart never solves: the
dump holds the solved state. Without the option nothing is called and nothing is added
to the parameter list of the run (the pattern of `NrpicKickInit`), so existing runs and
their restart files stay byte-identical.

## 4. How the deposited density and the solved psi stay consistent

1. The density in (1) is not a continuum density and not a copy of the deposit in
   another code: every evaluation of the residual calls the deposit and the filter of
   the module (`NrpicDepositSources`, `NrpicFilterSources`, `NrpicAddLambda`) with the
   current psi in the metric arrays, on the mesh of the run. Sampling noise, cloud
   shape, compensation, filter and (for moving particles) the Lorentz factors with the
   metric interpolated to the particles are therefore those of the evolution.
2. The state handed on is rebuilt from the solved psi alone (ADM variables on all cells,
   then `ADMToZ4c`), and the sources of the first step are deposited by the unchanged
   `NrpicInitializeSources` with that state: the same calls as inside the iteration.
3. Two residuals are offered (`id_residual`):
   - `code` (default): the residual is the Hamiltonian constraint as the code monitors
     it, `Z4c::ADMConstraints` (centred differences of order 2, 4, 6 for 2, 3, 4 ghost
     cells applied to gamma_ij; `z4c_adm.cpp` 252-528, `finite_diff.hpp` [VERIFIED]),
     F = -(psi^5/8) H. The iteration ends when the constraint monitor of the run is
     below the tolerance in every cell: what the evolution sees at t = 0 is zero.
   - `stencil`: F = lap_7 psi - right side of (1) with the seven-point Laplacian of the
     multigrid solver. The monitor of the run then shows the difference of the two
     discrete operators applied to psi (second order in the cell size for smooth psi).
   In both modes the linear solves use the seven-point operator; in mode `code` it is
   an approximate Jacobian (defect correction). Its error factor per iteration for a
   mesh mode of wavenumber k is 1 - lambda_code(k)/lambda_7(k): zero for long waves,
   -1/3 at the Nyquist wavenumber for the fourth-order stencil (16/3 against 4) and
   -0.51 for the sixth-order stencil (6.044 against 4) [JUDGEMENT, derived from the
   stencil symbols; to be seen in the iteration logs].
4. Ghost cells of psi during the solve: exchange between MeshBlocks and across periodic
   faces by the mesh boundary machinery (as for the potential of the Newtonian mode); at
   Robin faces psi - 1 is continued as 1/r (below). After the solve the Z4c ghost cells
   are filled by the same sequence as at start-up, so at an outflow face the outermost
   cells see the same boundary treatment as any other initial data.

## 5. Algorithm

**Outer iteration** (Newton with the seven-point Jacobian):

    repeat
      metric from psi; deposit and filter E; residual F (mode code or stencil)
      stop if max|F| <= id_tol * max over cells of (|2 pi psi^5 E| + |psi^5 K^2/12|
                                                    + |psi^-7 Abar^2/8|)
      sigma = (7/8) psi^-8 Abar^2 + (5/12) psi^4 K^2 + 2 pi psi^4 E
      solve (-lap_7 + sigma) d = F                       (inner iteration)
      psi <- psi + d   (halved until psi > 0 everywhere)

The matter term of sigma assumes Etilde independent of psi (exact for particles at rest
without filter; otherwise an approximation of the Jacobian that does not change the
solution).

**Inner iteration**: conjugate gradients for the symmetric positive operator
A = -lap_7 + sigma, preconditioned by the Poisson solver that exists, M^-1 = (-lap_7)^-1:
one multigrid solve (`MGGravityDriver`, V cycles from a zero start to a relative defect
`id_mg_tol`) per iteration. M^-1 A = 1 + (-lap)^-1 sigma has its spectrum in
[1, 1 + mu_max], mu_max of order M/R for a ball of compactness M/R (3.65 M/R for a
homogeneous ball with K^2 = 24 pi rho [JUDGEMENT, lowest mode sin(kr)/r with kR = pi/2])
and 0.11 (H L)^2 on a torus of side L: a handful of iterations. The plain fixed-point
iteration psi <- psi + (-lap)^-1 F would diverge for mu_max > 1; conjugate gradients do
not. The Polak-Ribiere form of the update is used, which tolerates a preconditioner
that is only approximately the same linear operator in every application.
On a mesh periodic in all directions the Poisson solver removes the mean; the constant
mode is preconditioned by 1/<sigma> (M^-1 r = (-lap)^-1 (r - <r>) + <r>/<sigma>).

Why not a multigrid for (1) itself (full approximation scheme with a nonlinear
smoother) [JUDGEMENT]: the coefficient arrays of the multigrid module are never
allocated in this port (`multigrid.cpp` 150-172, `multigrid_driver.cpp` 49 [VERIFIED]),
so a variable-coefficient or nonlinear smoother needs changes on every level type
(MeshBlock levels, root grid, octets). The outer iteration around the unchanged Poisson
solver costs more V cycles but touches the multigrid module only at its boundary
condition, and the cost of an initial-data solve is paid once per run. The nonlinear
smoother is the step to take when refined meshes make the octet path necessary anyway.

**Robin faces** (`<gravity> mg_bc = robin`, new): psi - 1 and every correction fall off
as 1/r about a centre (x_o): in a ghost cell and in its mirror cell across the face
r u is the same, u_ghost = u_mirror r_mirror/r_ghost. This is d_n(r u) = 0 to second
order, and exact for a monopole about x_o whatever the face. It is linear and
homogeneous, so it applies unchanged to corrections and, the multigrid being a full
approximation scheme, on every level (MeshBlock levels and root grid; not on octets).

## 6. Interface

Source: `athenak/src/particles/nrpic_idsolve.cpp` (the solver, 682 lines) and
`athenak/src/multigrid/multigrid_robin.cpp` (Robin faces, 100 lines), commit 87e189e;
unchanged since [VERIFIED: `git diff 87e189e HEAD -- athenak/src` is empty at the
commit of this section].

**Options, `<particles>` block.** Nothing is read and nothing enters the parameter dump
of a restart file unless `id_solve` is present (`NrpicIdSolveInit`, the pattern of
`NrpicKickInit`).

| Option | Default | Meaning |
|---|---|---|
| `id_solve` | absent (off) | `true`: solve the Hamiltonian constraint for psi at the start of a new run (never after a restart) |
| `id_residual` | `code` | `code`: the residual is the constraint monitor of the code, F = -(psi^5/8) H (`Z4c::ADMConstraints`); `stencil`: the seven-point Laplacian |
| `id_psi_init` | `trial` | start value: `trial` (psi of the problem generator) or `one` |
| `id_tol` | 1e-10 | stop when max\|F\| <= id_tol times the largest sum of the absolute terms of the right side of (1) |
| `id_maxit` | 60 | outer (Newton) iterations; not converged is a fatal error |
| `id_lin_tol` | 1e-3 | conjugate gradients: residual over right side |
| `id_lin_maxit` | 50 | conjugate-gradient steps per linear solve |
| `id_mg_tol` | 1e-3 | defect over source at which a preconditioner (multigrid) solve ends |
| `id_dump` | `false` | write `<basename>.idsolve.bin` (fields, `docs/FORMATS.md`) |

**Options, `<gravity>` block** (required: it creates the multigrid Poisson solver).

| Option | Required value | Meaning |
|---|---|---|
| `four_pi_G` | any (1.0) | read by the module; the solver passes its own factor |
| `threshold` | `0.0` | the solver sets the defect at which V cycles end (fatal otherwise) |
| `mg_bc` | `robin` unless the mesh is periodic in all directions | new kind: psi - 1 and every correction fall off as 1/r about (`robin_x1`, `robin_x2`, `robin_x3`), default the origin; fatal on a refined mesh |

Without a gas the `<gravity>` block costs memory only: the per-stage solve of the
driver returns at once (`mg_gravity.cpp` 191-199 [VERIFIED by reading]). With a gas it
would add Newtonian self-gravity of the gas: do not combine `id_solve` with hydro or MHD.

**Requirements** (each a fatal error with a message): `metric = mesh`, a `<z4c>` block,
not `pusher = newton`, `deposit = true`, a uniform mesh, cubic cells, a single rank, a
conformally flat trial metric (relative deviation below 1e-10), no `<scalar_field>`
block, `threshold = 0`, Robin faces on a mesh that is not periodic, and on the torus K
or matter (otherwise the linearised operator has a zero mode).

**What the problem generator must provide**: a conformally flat trial state in the ADM
variables (any psi_t > 0; K_ij from which K and Abar_ij are taken and held fixed), the
particles (as now), lapse and shift. Tested generators: `nrpic_cf` (format-1 Gaussian,
format-2 table of the expanding ball), `nrpic_cosmo` (`id = flrw` with a particle file).
Not tested: `nrpic_cosmo id = file`, Bowen-York curvature of `nrpic_cf`.

**Outputs**: `<basename>.idsolve.txt` (one record per outer iteration, a summary line)
and with `id_dump = true` `<basename>.idsolve.bin`; formats in `docs/FORMATS.md`, readers
`tracks/core/analysis/idsolve/idlib.py`. One line on standard output.

**Lines of shared files touched** (all additions; line numbers of this branch):

| File | Lines | What |
|---|---|---|
| `athenak/src/CMakeLists.txt` | 103, 141 | the two new source files |
| `athenak/src/bvals/bvals.hpp` | 21 | `BoundaryFlag::mg_robin` appended at the end of the enum |
| `athenak/src/gravity/mg_gravity.cpp` | 77-89, 98, 226-241 | `mg_bc = robin` and its centre; `SolvePoisson` (SolveSource with another factor) |
| `athenak/src/gravity/mg_gravity.hpp` | 68-71 | declarations of `SolvePoisson`, `Threshold` |
| `athenak/src/multigrid/multigrid.hpp` | 397-401, 505-507, 689-779 | Robin methods and members; `MGRobinFill` (inline kernel) |
| `athenak/src/multigrid/multigrid_driver.cpp` | 2193-2194 | `if (robin_) RobinBoundaryRoot();` at the end of `MGRootBoundary` |
| `athenak/src/multigrid/multigrid_tasks.cpp` | 360-361 | `if (robin_) RobinBoundaryBlocks();` at the end of `PhysicalBoundary` |
| `athenak/src/particles/nrpic.cpp` | 276 | `NrpicIdSolveInit(pin);` at the end of `NrpicInit` |
| `athenak/src/particles/nrpic_io.cpp` | 1237 | `NrpicSolveInitialData();` after `NrpicCreateParticles()` in `NrpicStartup` |
| `athenak/src/particles/particles.cpp` | 122 | delete `pbval_ids` in the destructor |
| `athenak/src/particles/particles.hpp` | 152-166, 362-369 | `NrpicIdSolveOptions`; members and methods of the solver |
| `docs/FORMATS.md` | 142-150 | the two output files |

## 7. What refined meshes and punctures will need later

Stated before coding [JUDGEMENT]; nothing of this is implemented.

Refined meshes (static or adaptive):
1. The Robin fill for octets (`MultigridDriver::ApplyPhysicalBoundariesOctet`); until
   then `mg_bc = robin` stops with an error on a multilevel mesh.
2. The operator of the inner iteration at fine-coarse faces must be the multigrid's own
   (flux-matched) operator, or conjugate gradients lose the symmetry: take the defect
   from the multigrid object instead of the seven-point kernel of the solver. The inner
   products are already volume-weighted.
3. Ghost cells of psi across levels come from `MeshBoundaryValuesCC` (restriction,
   prolongation), as for the potential of the Newtonian mode, which was tried on one
   static level only (`coord/INTERFACES/newtonian_mode.md`, section 6).
4. Mode `code` at level boundaries inherits the prolongation order of the Z4c ghost
   cells; a floor of the residual there is to be expected and measured.
5. The deposit needs nothing: level cap and adaptive cap are those of the module.

Punctures:
1. Split psi = psi_s + u with the singular part psi_s = 1 + sum m_c/(2 |x - x_c|) (plus
   the Bowen-York correction tables) known in closed form, and solve for the regular u:
   lap u = right side of (1) at psi_s + u. The problem generator has to hand over psi_s
   (now only the sum is in `adm.psi4`).
2. The residual for u must be the seven-point one (mode `stencil`) at least near the
   punctures: the constraint monitor is not usable there. psi^-7 Abar^2 is regular
   (r^7 against r^-6) and the matter term vanishes at a puncture.
3. With matter and punctures together the Robin centre is the centre of mass, not the
   origin (`<gravity> robin_x1` ...), or the multipole boundary of the solver is used.

Moving matter and the vector equation (next step of this package): with Stilde_i
deposited by the code, Abar_ij = Abar_ij(trial) + (L W)_ij,
lap W_i + (1/3) d_i d_j W_j = 8 pi Stilde_i + (2/3) psi^6 d_i K, through the
decomposition W_i = (7/8) V_i - (1/8)(d_i U + x_j d_i V_j) into four Poisson equations
(lap V_i = source_i, lap U = -x_j source_j) for the same solver, alternating with (1).

MPI: the particle module is single-rank (`nrpic.cpp` 60-64 [VERIFIED]); so is the solver.

## 8. Tests

Predictions and outcomes, failed predictions included: `tracks/core/JOURNAL-idsolve.md`
entries 2 to 8. Run ids per case: `tracks/core/analysis/idsolve/runs.json`; numbers:
`*_numbers.json` there; figures: `figs/`. Processor build of 87e189e unless stated.
All numbers below are [VERIFIED] in the runs named.

| Test | What it shows | Outcome |
|---|---|---|
| T0 regression | without `id_solve` existing results are unchanged | every output file byte-identical to the build of the unchanged source: seven relativistic cases (geodesics, Boris, deposit, East, Oppenheimer-Snyder on a refined mesh, Jeans, binary on four multigrid levels) and the Newtonian mode (isolated with multipole faces, periodic) (runs core-20261115-154817 to -155952, -160219 to -160227-87e189e; `regress_*_87e189e.json`) |
| T1 Gaussian, K = 0, against the format-1 psi of `nrpic_cf` | the solver solves what the design says, at the expected order | the same discrete system solved by a sparse direct Newton iteration in scipy agrees to 1.1e-13; error of psi - 1 at the centre -9.10e-3, -2.43e-3, -6.17e-4 (stencil) and -1.92e-2, -5.22e-3, -1.33e-3 (code, ng = 4) at dx = 1, 0.5, 0.25: second order, 0.82 to 0.91 of the prediction from the cloud and stencil moments; monitor after the solve 1.5e-11 to 2.6e-11 (code); Robin faces: error at the face centres 8.3e-5, 2.1e-5, 5.2e-6 (`figs/gauss_*`) |
| T2 expanding ball with its table curvature (exact psi = 1) | the solve accepts data that already solve the equation, up to discretisation | max\|psi - 1\| 2.33e-3, 5.19e-4, 1.20e-4 at dx = 2, 1, 0.5 (sharp surface), 4.2e-4, 1.10e-4, 2.8e-5 (smooth edge); max\|H\| 6e-3 before, 1.3e-12 to 2.1e-12 after (code); the sharp ball loses 3.1e-2, 4.6e-3, 6.3e-4 of its mass in the monopole at the faces (a failed prediction: the jump of the table curvature sampled at cell centres) (`figs/ball_*`) |
| T3 the same ball strained by (1.05, 1, 0.95) | Hamiltonian residual before and after the solve against resolution | before: max\|H\| 8.2e-3 to 1.2e-2, rms 4.2e-4, 3.3e-4, 3.2e-4 (a property of the data); after (code): max\|H\| 1.3e-12 to 2.2e-12 at dx = 2, 1, 0.5; quadrupole of the solved psi 4.15e-4, 4.21e-4, 4.20e-4 (resolved); the momentum constraint is not touched (rms 2.7e-3) (`figs/tri_slice`) |
| T4 plane wave on the torus against `cosmo/ic` | the same discrete system as the spectral reference with the seven-point symbol; the mean fixed by integrability | stencil mode against the seven-point reference: 7.8e-14, 5.7e-14 (one particle per cell), 2.3e-12, 4.6e-14 (eight); against the spectral symbol the fundamental of the difference is the predicted (k dx)^2/12 term to one per cent; code mode max\|H\| 7e-10 to 1.2e-9 (`figs/torus_psi`) |
| T5 card | the card build gives the solution of the processor build | Gaussian at 64 cells, one A100: same iteration counts (17 outer, 22 conjugate-gradient, 78 V cycles), psi equal to 1.1e-15; 5.7 s against 87 s on one core (run core-20261115-162952-46dcb31, `figs/card_vs_cpu`) |
| A, C restart | a restart never solves again and continues the solved state | held; the continuation differs from the uninterrupted run by the same 2e-10 in K_min with and without the solve (a property of the Z4c restart) |
| B, D, E evolution of the strained ball at 64 cells | does the evolution keep the advantage of the solved data? | not for the expanding ball at this resolution: after one step the mean \|H\| of the solved run is 2 times below the unsolved one, after eight steps within 10 per cent (sharp and smooth surface, with and without density-form sources) (`figs/evolution_tri`); test F (resolution, where the violation sits) in the journal, entry 9 |

Cost: one processor core, build with assertions: 10, 87, 655 s for the Gaussian in mode
code at 32, 64, 128 cells (9.2e4 to 5.9e6 particles); 17 to 29 outer iterations in mode
code, 3 to 4 in mode stencil; at most 3 conjugate-gradient steps per linear solve in all
tests.

## 9. Not done, limits

1. **Hamiltonian constraint only.** K and Abar_ij are held fixed; the momentum
   constraint, psi^-10 d_j Abar_ij - (2/3) psi^-4 d_i K = 8 pi S^i [BACKGROUND], is not
   solved. Data whose trial violates it keep that violation, and the solve changes it
   where psi moves: a trial with psi_t = 1 and S_i = 0 that satisfies it is left with
   M_i = (2/3)(psi^-6 - 1) d_i K [derived]. For the strained ball (particles at rest,
   S_i = 0) the continuum trial satisfies the momentum constraint; what the monitor
   shows (T3: rms 2.7e-3 at the sharp surface) is the discretisation of the table
   curvature. The vector equation of section 7 is the next step [JUDGEMENT]. The
   evolution checks B, D, E show that for the expanding ball at 64 cells the evolution
   makes a violation of the size of the trial's within a few steps, with and without
   the solve.
2. **Uniform meshes, one rank, cubic cells.** Refined meshes and MPI: section 7.
3. **Robin faces** are exact for a monopole about the chosen centre; a dipole or
   quadrupole of the data falls off faster and is continued as 1/r, an error of order
   (dipole / r^2) at the faces (not measured separately). Off-centre matter: set
   `robin_x1..3` to the centre of mass.
4. **Mode stencil** leaves the monitor of the code at the difference of the two discrete
   operators; at a density jump that is resolved by one cell this does not fall with
   resolution (T2, T3: max\|H\| 2e-3), and for a deposit with structure at the cell scale
   it stays at 0.7 per cent of 16 pi rho on the torus (T4). Default and recommendation:
   mode `code`.
5. **Mode code** is a defect correction with the seven-point Jacobian: linear
   convergence with factor 0.5 (ng = 4), 0.32 (ng = 3), Newton-like for ng = 2. It is 2 to
   3 times slower than mode stencil.
6. **Matter Jacobian**: the term 2 pi psi^4 E of sigma treats Etilde as independent of
   psi; with a filter or moving particles (Lorentz factor through the interpolated
   metric) it is an approximation of the Jacobian, which changes the convergence rate,
   not the solution. A filter was run (T2 with one filter pass: converged); every test
   has particles at rest in the slice: moving particles were not tested.
7. **Lapse and shift** are those of the problem generator: a lapse option that depends
   on psi (`isotropic`, `precollapsed`) refers to the trial psi, not the solved one.
8. **Not tested**: `nrpic_cosmo id = file`, the Bowen-York curvature of `nrpic_cf`, a
   cosmological constant (`lambda` enters sigma), the adaptive deposit.
9. **Mass of a sharp-surfaced ball** at coarse resolution changes by the solve (3 per
   cent at five cells per radius, T2 (d)); a smooth edge of two cells removes most of it.
10. A `<gravity>` block in a run with a gas adds Newtonian self-gravity of the gas; the
    solver is meant for particle runs without gas.

## 10. The vector equation (option `id_vector`), design before coding

Written before any source line of this part [JUDGEMENT unless labelled].

**Equation.** With Abar_ij = Abar_ij(trial) + (L W)_ij,
(L W)_ij = d_i W_j + d_j W_i - (2/3) delta_ij d_k W_k, the momentum constraint
psi^-10 d_j Abar_ij - (2/3) psi^-4 d_i K = 8 pi S^i [BACKGROUND] becomes, multiplied by
psi^10 (S^i = psi^-4 S_i, and psi^6 S_i = Stilde_i is the deposit of m u_i per
coordinate volume, independent of psi for fixed u_i),

    lap W_i + (1/3) d_i d_j W_j = 8 pi Stilde_i + (2/3) psi^6 d_i K - d_j Abar_ij(trial).   (2)

The code's monitor gives psi^6 M_i = left side minus right side of (2) with its own
differences.

**Why not mode `code` for (2).** The monitor differentiates the stored K_ij once; with
K_ij = psi^-2 (L W)_ij formed by central first differences the composite operator is a
product of two central first differences, whose symbol vanishes at the Nyquist
wavenumber of every direction (sin(k dx) = 0). A deposited source has content there
(cloud and lattice), which that operator cannot reach: a residual of the monitor cannot
be driven to the tolerance in general. (2) is therefore solved in stencil form, with the
compact operator
    (Delta_L W)_i = lap_7 W_i + (1/3) [ (W_i(+e_i) - 2 W_i + W_i(-e_i))/dx^2
                    + sum_{j != i} (4-point mixed difference of W_j)/(4 dx^2) ],
whose symbol is not singular, and the right side with central differences of K and
Abar(trial). (L W)_ij is formed with central first differences. With
`id_residual = code` the scalar equation keeps its mode; the monitor M is reported, not
driven to zero.

**Iteration.** One outer iteration of the existing solver evaluates both residuals with
one deposit; the scalar correction is computed as before (Abar^2 now includes L W); the
vector correction is one preconditioned Richardson step
    W <- W - P^-1 F,   P^-1 F = lap_7^-1 F - (1/4) lap_7^-1 grad lap_7^-1 div F,
which inverts the continuum vector Laplacian exactly (div W = (3/4) lap^-1 div F) and
costs four multigrid solves. Fourier analysis of the compact operator on a periodic
mesh gives eigenvalues of P^-1 Delta_L between 1 and 4/3: an error factor of at most
1/3 per iteration. Convergence: both relative residuals below `id_tol`; the scale of (2)
is the largest sum over its terms of their absolute values.

**Faces.** W, div F and every correction use the Robin fill (1/r about the centre): the
far field of an isolated momentum (Bowen-York, W_i = -(7 P_i + n_i n.P)/(4 r)
[BACKGROUND]) has r W_i depending on the direction only. On the torus (2) is solvable
only when the mean of its right side vanishes (total momentum zero); the mean is
removed from F before the test and reported in the record.

**Interface.** `<particles> id_vector = true` (read only if present; requires
`id_solve`); outputs: extra columns in `<basename>.idsolve.txt` (max and rms of F of (2),
max of the monitor's |M|) and with `id_dump` a file `<basename>.idvector.bin` (W_i,
right side of (2), F of (2), the monitor's M_i after and before the solve). Without the
option the solver runs exactly as before.
