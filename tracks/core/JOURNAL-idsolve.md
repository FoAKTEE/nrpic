# Journal of core, work package "idsolve": elliptic solver for initial data in the code

Branch `core/id-solver`, worktree `wt/core-idsolve`. Units G = c = 1. Sign: expansion has
K < 0. Labels: [VERIFIED] read or measured here (with locator or run id), [BACKGROUND]
standard result not re-derived here, [JUDGEMENT] inference or design, [TO VERIFY] open.
Run ids are `core-<date>-<time>-<commit7>` (UTC); manifests in `tracks/core/runs/`,
outputs in `scratch/core/<run_id>/` of the main checkout.

## 2026-11-15, entry 1: what was read, facts of the code, design

Read: `CLAUDE.md`; `coord/CHARTER.md` to the end of "Owners"; brief lines 493-553,
688-706, 834-860; the rulings after wave 1 and decisions 0010 to 0015; core's
`HANDOFF.md`, `STATUS.md`, `stage/G2/OPEN.md` (core has no G0 or G1 package directory:
its gate is G2); `coord/notes/design_wave2_initial_data.md` sections 1 and 2;
`coord/INTERFACES/newtonian_mode.md`; `cosmo/ic/cosmo_id.py`; of the source:
`multigrid/multigrid.hpp`, `multigrid.cpp` 36-555, `multigrid_driver.cpp` 36-256,
556-937, 1700-2195, `multigrid_tasks.cpp` 100-380, `gravity/*`, `particles/nrpic.cpp`,
`nrpic_newton.cpp` 1-440, `nrpic_kick.cpp` 1-80, `nrpic_io.cpp` 1229-1317,
`particles.hpp`, `pgen/nrpic/nrpic_cf.cpp`, `nrpic_cosmo.cpp`, `z4c/z4c_adm.cpp`,
`utils/finite_diff.hpp` 1-110, `driver/driver.cpp` 440-500 and 759-775.

Facts the design rests on [VERIFIED, file and line of this worktree]:

- The multigrid module is a full approximation scheme (every level holds the solution:
  `Multigrid::RestrictPack` restricts the solution next to the defect and
  `CalculateFASRHS` adds the operator of the restricted solution, `multigrid.cpp`
  515-535, `multigrid.hpp` 293-312), with a seven-point Laplacian
  (`mg_gravity.hpp` 26-39) and red-black Gauss-Seidel.
- Its boundary conditions at faces that are not periodic are applied in three places:
  `MultigridDriver::PhysicalBoundary` (MeshBlock levels, `multigrid_tasks.cpp` 129-361),
  `MGRootBoundary` (root grid, device and host path, `multigrid_driver.cpp` 1835-2194),
  `ApplyPhysicalBoundariesOctet` (octets of refined meshes, 1724-1822). Kinds:
  zero value, zero gradient, multipole expansion of the source. There is no Robin kind.
- The coefficient arrays `coeff_`, `matrix_` of the module are declared and never
  allocated (`multigrid.cpp` 150-172; `ncoeff_` of `Multigrid` is not initialised,
  `ncoeff_ = 0` in the driver, `multigrid_driver.cpp` 49): a Helmholtz or nonlinear
  smoother is not available without work on every level type.
- `MGGravityDriver::SolveSource` (wave 1) solves lap phi = four_pi_G rho for any
  cell-centred array, resets the red-black colour offset, and with `threshold = 0`
  cycles until a defect norm or a stall (`mg_gravity.cpp` 178-262); the start value is
  `pgrav->phi`; the result comes back in the active cells of `pgrav->phi`.
- The constraint monitor: `Z4c::ADMConstraints` forms the Ricci scalar from first and
  second centred differences of `adm.g_dd` of order 2 (ng - 1) and
  H = R + K^2 - K_ij K^ij - 16 pi E with `tmunu.E` (`z4c_adm.cpp` 304-487). For
  gamma_ij = psi^4 delta_ij, H = -8 psi^-5 (lap psi - right side of the scalar
  equation) in the continuum [BACKGROUND].
- The deposit divides the deposited density per coordinate volume by sqrt(gamma) of
  the receiving cell and filters afterwards (`nrpic.cpp` 925-959, 1153-1176), so the
  source of the code is E = F[D/psi^6] and depends on psi.
- Start-up: `Driver::Initialize` fills the Z4c ghost cells, then calls
  `Particles::NrpicStartup`, which creates the particles and calls
  `NrpicInitializeSources` (`driver.cpp` 460-475; `nrpic_io.cpp` 1233-1238).
  `nw_driver` (the driver pointer the multigrid needs) is stored before that call.
- Options read with `GetOrAdd...` enter the parameter dump of restart files;
  `NrpicKickInit` shows the pattern that adds nothing unless a switch is present
  (`nrpic_kick.cpp` 51-56).

Design: `tracks/core/interfaces/id_solver.md`, sections 1 to 5 and 7, written before
the first source line (commit of this entry). In short: Newton iteration for psi with
the code's own deposit in every residual; linear solves by conjugate gradients
preconditioned with the existing multigrid Poisson solver; residual either the
constraint monitor of the code (default) or the seven-point stencil; Robin faces as a
new boundary kind of the multigrid module; one call in `NrpicStartup`.

## 2026-11-15, entry 2: predictions, written before the solver was compiled

Tests T1 to T5 below; each run is registered; figures under
`tracks/core/analysis/idsolve/figs/`. "Refuted if" names what would make me distrust
the implementation or the design.

**T0 regression.** With no `id_solve` in the input the new executable writes the same
bytes as the executable built from the unchanged source (same build script and
directory layout): cases geo, boris, dep, east, os, jeans, binary of
`tracks/core/tools/regress_relativistic.py` and the Newtonian mode (isolated and
periodic input of `problems/newton/`), because the only code reached without the option
is a guard in `NrpicStartup`, an empty option reader, and (multigrid) branches behind
`mg_bc = robin`. Refuted if any output file differs.

**T1 Gaussian, K = 0, against the format-1 construction.** `nrpic_cf` with one
`gaussian` component (conformal mass m = 1, width s = 2): psi_ex = 1 + (m/2)
erf(r/(sqrt 2 s))/r solves lap psi = -2 pi rhot with rhot the normalised Gaussian.
Particles at rest on a lattice of spacing dx/2 with masses rhot psi_ex h^3, so that
Etilde = rhot psi_ex and psi_ex solves (1). Start from psi = 1 (`id_psi_init = one`).
Box half-width 16, dx = 1, 0.5, 0.25, cloud in cell, no filter, Robin faces.
Predictions:
 (a) the outer iteration converges to `id_tol = 1e-10` in at most 8 iterations in mode
     `stencil` (quadratic at the end) and at most 40 in mode `code`, with factors
     between successive residuals near 1/3 (ng = 3) or 0.5 (ng = 4) at the end;
 (b) inner iteration: at most 8 conjugate-gradient steps per outer step
     (psi(0) - 1 = 0.2: mu_max of order 0.5);
 (c) mode `stencil`: psi - psi_ex at the centre = -(dx/s)^2/30 times (psi_ex(0) - 1)
     to leading order (cloud: -(dx/s)^2/12, seven-point Laplacian: +(dx/s)^2/20; both
     for the Gaussian, linear theory), i.e. relative errors -8.3e-3, -2.1e-3, -5.2e-4,
     falling by 4 per halving; the screening by the nonlinear term lowers this by a
     few per cent of itself;
 (d) mode `code` with four ghost cells (sixth-order monitor): only the cloud term
     remains, -(dx/s)^2/12: -2.1e-2, -5.2e-3, -1.3e-3; with `deposit_comp_c = 1/12` it
     drops to fourth order (below 2e-4 at dx = 0.5);
 (e) the Robin face adds no visible error (the exterior is a monopole about the
     origin): the error at the faces is below 1e-5 at dx = 0.5;
 (f) the constraint monitor: before the solve (psi = 1) max|H| = 16 pi E(0) =
     16 pi rhot(0) psi_ex(0) = 16 pi * 0.01985 * 1.1995 = 1.197; after, mode `code`:
     below 1e-9; after, mode `stencil`: of order (dx^2/12) |d^4 psi| * 8, falling by 4
     per halving.
 Refuted if: no convergence; an error that does not fall by about 4 per halving; a
 central error of the other sign or more than 30 per cent away from (c) and (d); an
 error at the faces above 1e-4.

**T2 expanding ball with its table curvature.** `make_ball.py --Rb 10 --h dx/2`,
table of format 2, psi_t = 1; the exact data solve (1) with psi = 1. The solve starts
from the trial. Mesh half-width 32, dx = 1, 0.5, 0.25 (N = 64, 128, 256; the last one
only if time allows), cloud in cell, one filter pass as in `problems/ball`, and a
second series without filter.
 (a) Sharp surface: the residual before the solve sits in the surface cells (cloud
     and lattice against the jump of KL in the table) with max|H| of order
     16 pi rho = 1.2e-2 at every resolution and an L2 norm falling as sqrt(dx);
     after the solve (mode `code`) max|H| < 1e-9 in the interior;
 (b) the solved psi differs from 1 by the potential of that surface layer, which has
     no net mass to first order: max|psi - 1| of order 2 pi rho dx^2 times a number of
     order one (4e-4, 1e-4 at dx = 1, 0.5 if the number is one), falling by about 4 per
     halving (between 2 and 4 accepted: the surface is first order locally);
 (c) the smooth edge (`--edge 2`): clean second order of max|psi - 1|, smaller than (b);
 (d) the mass of the solved data stays that of the table: the Robin monopole
     2 r (psi - 1) at the faces is below 1e-3 M.
 Refuted if: psi - 1 does not fall with resolution; the solve moves psi by more than
 1e-2 anywhere; the residual after the solve is not at the tolerance.

**T3 the same ball with a small triaxial displacement.** Particle positions scaled by
(1 + e, 1, 1 - e) along x, y, z with e = 0.05 (traceless strain: the density is
unchanged to first order, the surface moves by up to 0.5 M); table curvature of the
sphere unchanged. dx = 1, 0.5 (0.25 if time allows).
 (a) before the solve the Hamiltonian residual is of order 16 pi rho = 1.2e-2 in a
     layer of thickness up to e Rb = 0.5 M at the surface; its L2 norm over the box
     does not fall with resolution once dx < 0.5 (it is a property of the data);
 (b) after the solve, mode `code`: max|H| at the tolerance at every resolution; mode
     `stencil`: max|H| set by the difference of the operators at the surface, falling
     slowly (first order or not at all in the maximum norm, the density jump is
     resolved by one cell), L2 norm falling at least as dx;
 (c) psi - 1 of the solved data is a quadrupole of size 2 pi rho e Rb^2 / 5 times a
     number of order one, about 1.5e-3 * 0.05 * 100 / 5 = 1.5e-3, the same at both
     resolutions to ten per cent;
 (d) the momentum constraint is not solved: its residual stays where the trial left
     it (reported, not judged).
 Refuted if (b) code mode does not reach the tolerance, or psi - 1 differs between
 the resolutions by more than 30 per cent.

**T4 plane wave on the torus against cosmo/ic.** `nrpic_cosmo` with `id = flrw`,
hubble H = 1, box L = 2 (H L = 2), N = 32 and 64 cells, particles at rest on the lattice
of the cell centres displaced along x by -(A/k) sin(k x), k = 2 pi/L, A = 0.1, equal
masses with mean density 3 H^2/(8 pi); cloud in cell, no filter. References computed
with `cosmo/ic/cosmo_id.py` from the same particle file: (i) its spectral solve,
(ii) the same iteration with the symbol of the seven-point Laplacian in place of k^2.
 (a) mode `stencil` against (ii): the two solve the same discrete system, agreement of
     psi to the tolerances (below 1e-9 in the maximum norm);
 (b) mode `stencil` against (i): difference of order (k dx)^2/12 of the perturbation
     of psi: dpsi = 2 pi rhobar delta/(k^2 + sigma), sigma = 12 pi rhobar = 4.5 H^2,
     amplitude 0.75 A/(9.87 + 4.5) = 5.2e-3; (k dx)^2/12 = 3.2e-3 (N = 32), 8.0e-4
     (N = 64): differences 1.2e-5 and 3e-6 (factor 4; within 30 per cent, the screening
     term changes the factor);
 (c) the mean of psi is fixed by the integrability condition and equals that of the
     references to 1e-9 (stencil against (ii));
 (d) conjugate gradients: mu = sigma/k^2 = 0.46 for the wave; at most 6 steps;
 (e) mode `code`: H of the monitor below 1e-9 after the solve; psi differs from (i)
     by less than in (b) (sixth-order operator).
 Refuted if (a) fails by more than 1e-7 or the mean differs.

**T5 card build.** The Gaussian case at dx = 0.5 on one A100 gives the same iteration
counts and psi to 1e-12 relative to the processor run (sums are reduced in another
order). At most 0.2 card-hours in all.

## 2026-11-15, entry 3: amendments of the predictions, before any registered test run

The solver compiled at the first attempt (processor build). Three smoke runs in
`scratch/core/tmp/idsolve/` (not registered; no number of them is used as a result)
showed that it runs to convergence in both modes on Robin faces and on the torus. They
also showed two faults of entry 2, which I correct here before the registered runs.

1. **Arithmetic error in T1 (f), a failed prediction.** I wrote rhot(0) = 0.01985. The
   normalised Gaussian with m = 1, s = 2 has rhot(0) = m/(2 pi s^2)^(3/2) = 7.937e-3.
   The monitor before the solve (psi = 1) is therefore max|H| = 16 pi rhot psi_ex at the
   innermost cells, at most 16 pi * 7.937e-3 * 1.1995 = 0.4786 (the smoke run at
   dx = 1 printed 0.405; its innermost cell centres are at r = 0.87), not 1.197. The
   same slip made sigma(0) = 2 pi rhot/psi = 0.042, not 0.104: the screening of the
   error is about 5 per cent (k^2 about 3/s^2 = 0.75), not "a few per cent to ten".
2. **Lattice effect in T1 (c), (d), derived now [JUDGEMENT].** The particles sit on a
   lattice of spacing dx/2, at +-dx/4 and +-3dx/4 from a cell centre, with
   cloud-in-cell weights 3/4 and 1/4: the deposit has the second moment (3/16) dx^2
   per direction instead of the dx^2/6 of a continuum of particles, so the cloud term
   is -(3/32)(dx/s)^2, not -(dx/s)^2/12. Amended predictions for the relative error of
   psi - 1 at the centre (dx = 1, 0.5, 0.25), before screening:
   (c) mode `stencil`: (-3/32 + 1/20)(dx/s)^2 = -1.09e-2, -2.7e-3, -6.8e-4;
   (d) mode `code`, four ghost cells: -(3/32)(dx/s)^2 = -2.3e-2, -5.9e-3, -1.5e-3; with
       `deposit_comp_c = 1/12` the pass removes (1/12)(dx/s)^2 of it and -(dx/s)^2/96
       remains (-2.6e-3, -6.5e-4): still second order with this lattice;
       `deposit_comp_c = 3/32` would remove it to fourth order.
   The innermost cell centres are off the centre (r = 0.87 dx), where the error
   relative to psi - 1 is a few per cent smaller.
   (e) amended: the error at the faces is the far field of the error of the monopole,
   (psi - 1) times the relative change of the integral of Etilde/psi, a few 1e-3 of
   0.032 at dx = 1 (of order 1e-4), falling by 4 per halving; "below 1e-5 at dx = 0.5"
   was too tight. Refuted if it does not fall by about 4 per halving.
3. **T4, the lattice of the cell centres is a degenerate case.** With one particle per
   cell at the cell centres every particle sits at the kink of the cloud-in-cell
   weight; where the displacement changes sign (x = 0 and x = L/2) the deposited
   density jumps within one cell (seen in the smoke run). The comparison with
   `cosmo/ic` uses the same deposit and is not affected ((a), (c), (d) stand), but (b)
   and (e) assumed a smooth density. I keep the case as registered in entry 2 and add
   the lattice with eight particles per cell (`--ppc 2`), for which (b) and (e) are
   the predictions; for one particle per cell I expect the difference to the spectral
   reference to be several times larger than (b) near the two planes.
4. **T2, T3 resolutions.** Box half-width 32 as in `problems/ball`; resolutions
   dx = 2, 1, 0.5 (N = 32, 64, 128) instead of 1, 0.5, 0.25: N = 256 does not fit the
   processor runs of this session. The predictions of T2 (b) scale as dx^2 (1.5e-3,
   4e-4, 1e-4 times a number of order one).

## 2026-11-15, entry 4: outcomes of T0 to T4 (source of commit 87e189e, processor build)

Registration: `harness/bin/nrpic-run submit` and `status` stop with
`KeyError: 'outputs'` (`harness/bin/nrpic-run` line 163, `is_live`, reading the
hand-written manifests of wave 1 in `tracks/core/runs/`). All runs of this package are
therefore registered by hand with `tracks/core/tools/run_registered.py` (same fields).
Case names and run ids: `tracks/core/analysis/idsolve/runs.json`; numbers:
`gauss_numbers.json`, `ball_numbers.json`, `torus_numbers.json` there; figures:
`figs/`. I looked at every figure.

A fault of my test runner, not of the code: two runs started in the same second get the
same run id and the second stops in `run_registered.py` (`os.makedirs`). The first
launch of T1 lost `gauss_code_n32` and `gauss_code_n32_comp` that way; the runner now
starts runs 1.2 s apart and the two cases were rerun (ids below). No run directory holds
two runs.

**T0 regression: prediction held.** Baseline: the executable built from the unchanged
source in the same build directory (`.work/base_cpu/athena`), new: 87e189e. Every
output file identical byte for byte: geo 2 files, boris 2, dep 1, east 12, os 16
(statically refined mesh with Z4c), jeans 5 (and its result lines of the log),
binary 1 (multigrid on four refinement levels) (runs core-20261115-154817 to
-155952-87e189e, report `regress_cpu_87e189e.json`); Newtonian mode: isolated ball
with the multipole boundary 11 files, periodic expanding wave 9 files (runs
core-20261115-160219 to -160227-87e189e, report `regress_newton_87e189e.json`).
Card build: not compared (see T5).

**T1 Gaussian, K = 0.** Runs gauss_*: stencil N = 32, 64, 128:
core-20261115-155048, -155050, -155053-87e189e; code: -160207, -155051, -155054.
- Independent reference: the same discrete system (cloud-in-cell density of the
  particle file, seven-point Laplacian, Robin closure) solved by a sparse direct
  Newton iteration in scipy (`idref.solve_isolated`) at N = 32: largest difference of
  psi 1.1e-13. The code solves what the design says.
- (a) held: mode stencil 4 outer iterations at every resolution (residual
  1, 3.6e-2, 8.6e-6, 3.1e-9, 1.3e-13 at N = 32); mode code 16 to 17, with factors
  0.49 between the last residuals for four ghost cells (0.51 predicted at the Nyquist
  wavenumber), 0.32 for three (1/3 predicted; run -155115), and 5 iterations of
  Newton type for two (run -155052).
- (b) held: 2 conjugate-gradient steps per linear solve in mode stencil, at most 3 in
  mode code; 32 to 41 V cycles (stencil), 78 to 101 (code) per solve of the problem.
- (c), amended form, held: relative error of psi - 1 at the innermost cells, mode
  stencil: -9.10e-3, -2.43e-3, -6.17e-4 (dx = 1, 0.5, 0.25; factors 3.75, 3.93)
  against -1.09e-2, -2.73e-3, -6.8e-4 before screening: 0.83, 0.89, 0.90 of the
  prediction.
- (d), amended form, held: mode code, four ghost cells: -1.92e-2, -5.22e-3, -1.33e-3
  (factors 3.68, 3.92) against -2.34e-2, -5.86e-3, -1.46e-3: 0.82, 0.89, 0.91. With
  `deposit_comp_c = 1/12`: -3.00e-3, -6.54e-4 against -2.60e-3, -6.51e-4. The profile
  of the error over radius, divided by (dx/s)^2, is the same curve at the three
  resolutions and follows -2 pi rhot s^2 (3/32) (figure `gauss_error`).
- Not predicted: with two ghost cells the error at the centre is -8.8e-4 at dx = 0.5,
  a third of that of mode stencil. The second-order monitor of the code is built from
  differences of psi^4 and is not the seven-point Laplacian of psi; I had assumed the
  two agree. They agree in the linearisation (hence the Newton-type convergence), not
  in their truncation error.
- (e), amended form, held: error at the face centres 8.3e-5, 2.1e-5, 5.2e-6 (factor
  4.0, 4.0); the monopole 2 r (psi - 1) at the faces is 1.00257, 1.00065, 1.00016.
  The original (e) ("below 1e-5 at dx = 0.5") failed: 2.1e-5.
- (f): before the solve max|H| = 0.405, 0.458, 0.473 (limit 0.4786; the 1.197 of
  entry 2 was my arithmetic error). After, mode code: 1.5e-11, 1.1e-11, 2.6e-11 in the
  solver and 1.4e-11, 1.1e-11, 2.0e-11 in the first field dump of the run away from
  the faces (the state the evolution starts from). After, mode stencil: 4.72e-3,
  1.42e-3, 3.72e-4 (factors 3.3, 3.8). Within four cells of an outflow face the monitor
  of the run reads up to 1.9e-3 in every mode: the ghost cells of the Z4c boundary
  condition, as for any initial data (figure `gauss_H`).
- Cost on one processor core (build with assertions): 3.7, 29, 253 s (stencil) and 10,
  87, 655 s (code) at N = 32, 64, 128 with 9.2e4, 7.4e5, 5.9e6 particles.

**T2 expanding ball with its table.** Runs ball_*; sharp surface, mode code, no
filter: core-20261115-160245, -160250, -160259-87e189e (dx = 2, 1, 0.5).
- (a) held: before the solve max|H| = 6.3e-3, 5.8e-3, 6.0e-3 (16 pi rho = 1.2e-2),
  rms 4.0e-4, 2.7e-4, 1.9e-4 (factor 1.5, 1.4, as sqrt(dx)); after, mode code:
  max|H| 1.3e-12, 1.4e-12, 2.1e-12 in the solver and in the field dump away from the
  faces. Mode stencil leaves max|H| = 2.0e-3 at every resolution (the density jump in
  one cell), rms 1.4e-4, 9.1e-5, 6.6e-5.
- (b) held: max|psi - 1| = 2.33e-3, 5.19e-4, 1.20e-4 (factors 4.5, 4.3), that is 0.39,
  0.35, 0.32 times 2 pi rho dx^2. With one filter pass (as `problems/ball`): 3.27e-3,
  7.5e-4, 1.78e-4.
- (c) held: smooth edge 4.2e-4, 1.10e-4, 2.8e-5 (factors 3.84, 3.96); (psi - 1)/dx^2
  is one curve at the three resolutions (figure `ball_psi`).
- (d) failed at the two coarser meshes: the monopole 2 r (psi - 1) at the faces is
  -3.1e-2, -4.6e-3, -6.3e-4 M (dx = 2, 1, 0.5; factors 6.6, 7.3), predicted below
  1e-3 M. The solve lowers the mass of the data by 3 per cent when the ball is five
  cells in radius. With the smooth edge it is +2.1e-3, +4.5e-4, +1.1e-4 M (factors
  4.7, 4.1): fifteen times smaller at dx = 2. These runs could have shown the same
  monopole and did not, so the sharp surface (the jump of KL of the table sampled at
  cell centres against the ragged lattice surface) is the cause of the larger one.
- 28 to 29 outer iterations (code), 3 (stencil); at most 3 conjugate-gradient steps.

**T3 the ball with a triaxial strain of 0.05.** Runs tri_*: code -160408, -160419,
-160448; stencil -160415, -160421, -160511; without the solve -160418, -160440, -160538.
- (a) held: before the solve max|H| = 8.2e-3, 1.01e-2, 1.22e-2; rms over the mesh
  4.16e-4, 3.28e-4, 3.24e-4: flat between dx = 1 and 0.5.
- (b): after the solve, mode code: max|H| 1.3e-12, 1.4e-12, 2.2e-12, rms 1.5e-13,
  7.1e-14, 8.1e-14 at dx = 2, 1, 0.5 (held). Mode stencil: max|H| 2.5e-3, 2.7e-3,
  2.6e-3 (not falling, as predicted), rms 1.38e-4, 9.9e-5, 8.3e-5: factors 1.4 and
  1.2 per halving, not the factor 2 I predicted for the rms (failed).
- (c): the quadrupole of the solved psi, half the difference of psi - 1 on the x and
  z axes at r = 15, is 4.15e-4, 4.21e-4, 4.20e-4 at the three resolutions (the same to
  1.5 per cent); the largest |psi - 1| is 3.3e-3, 1.79e-3, 1.46e-3 (1.5e-3 predicted
  for the quadrupole part; the two finer meshes differ by 22 per cent because the
  monopole error of the sharp surface of T2 is added at the coarser one). Sign: psi
  is raised along the stretched axis and lowered along the compressed one (figure
  `tri_slice`).
- (d) as stated: the momentum constraint is not solved; its rms over the mesh is
  2.66e-3, 2.69e-3, 3.57e-3 without and 2.67e-3, 2.69e-3, 3.57e-3 with the solve, and
  its maximum (2.1e-2, 4.7e-2, 9.8e-2) grows as 1/dx at the sharp surface, a property
  of the trial data known from wave 1.
- Seen in the figure, not predicted: the strained lattice (spacing h (1 + e)) beats
  against the mesh, and the deposited density carries a moire of period h/e = 5 cells
  of a few per cent; the solve absorbs it into psi.

**T4 plane wave on the torus against cosmo/ic.** Runs torus_*: stencil, one particle
per cell, N = 32, 64: core-20261115-155120, -155203; eight per cell: -155135, -155219;
code: -155123, -155211, -155142, -155220.
- (a) held: mode stencil against `cosmo_id.solve` with the seven-point symbol: largest
  difference of psi 7.8e-14, 5.7e-14 (one particle per cell), 2.3e-12, 4.6e-14 (eight);
  the deposited E agrees to 6e-14, 5e-14, 1.7e-12, 4e-14.
- (b) failed in the maximum norm, held for the wave: against the spectral reference
  the largest difference is 2.28e-5, 5.9e-6 (one per cell) and 1.95e-5, 5.2e-6 (eight)
  against 1.2e-5, 3e-6 predicted. A Fourier split of the difference of the two
  references along x, which could have shown a fundamental of 2e-5, gives a
  fundamental of 1.143e-5 and 2.87e-6 (the prediction to one per cent) and a remainder
  of up to 1.2e-5 (one per cell) or 9.6e-6 (eight) at N = 32: the cloud-in-cell
  density of a displaced lattice has structure at the scale of the cells, where the
  two symbols differ most. Eight particles per cell reduce it only by a fifth.
- (c) held: the mean of psi equals that of the seven-point reference to 1.6e-14,
  6.7e-15, 1.9e-12, 3.4e-15; it is 1 - 6.38e-5.
- (d) held: 3 conjugate-gradient steps per linear solve.
- (e): mode code leaves max|H| = 8.2e-10, 9.4e-10, 1.15e-9, 7.3e-10 (before: 0.89,
  0.90, 0.73, 0.80); I predicted "below 1e-9" and one case is 15 per cent above. The
  tolerance is on F = psi^5 H/8 relative to the largest term (about 1.6 here), so the
  bound on H is 8 * 1e-10 * 1.6 = 1.3e-9: my prediction did not convert it. The
  difference to the spectral reference is 9.7e-7, 2.4e-7 (one per cell), 1.45e-6,
  3.2e-7 (eight), below (b) as predicted. 23 to 24 outer iterations, factor 0.48-0.50.
- Not predicted, and the reason for the default `id_residual = code`: after a solve in
  mode stencil the monitor of the run reads max|H| = 3.7e-2, 3.6e-2 (one per cell) and
  4.7e-2, 4.3e-2 (eight) at N = 32, 64: 0.7 per cent of 16 pi rho and not falling
  with resolution, because the density has structure at the scale of the cells at
  every resolution.
- Amplitude of psi: 5.17e-3 to 5.21e-3 (linear theory 5.22e-3).

## 2026-11-15, entry 5: prediction for the evolution and restart check (before the runs)

(The commit message of entry 4 says "five failed predictions"; the count in the entry
is six: T1 (f) value, T1 (e) original bound, T2 (d), T3 (b) rms, T4 (b) maximum norm,
T4 (e) bound.)

`check_evolution.py`, source 87e189e, processor build.
A. Gaussian at 32 cells, solved in mode code, 8 cycles, restart dump at cycle 4, then
   a run from the dump. Predictions: the run from the dump prints no solve and writes no
   `idsolve.txt` (the call sits in the branch of a new run); its constraint records at
   cycles 5 to 8 equal those of the uninterrupted run to rounding (relative 1e-10 or
   better in the extrema of chi, K, E; a Z4c restart is not bitwise). During the 8
   cycles the mean of |H| over the mesh stays below 1e-4 (it starts at the tolerance
   in the interior; the boundary layer of the outflow faces and the time integration
   raise it). Refuted if the solver runs after the restart, if the histories differ by
   more than 1e-8 relative, or if a value is not finite.
B. Triaxial ball at 64 cells, 8 cycles, without the solve and with it. Predictions: both
   run to the end with finite values; at the first record the mean of |H| is the trial
   value without the solve and at least 1e3 times smaller with it; after 8 cycles
   (t = 2) the run with the solve still has the smaller mean |H| (by at least a factor
   3: the momentum constraint is violated equally in both and feeds H during the
   evolution). Refuted if the run with the solve has the larger H at the end, or fails.
