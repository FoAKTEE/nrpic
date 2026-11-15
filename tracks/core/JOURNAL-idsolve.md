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
