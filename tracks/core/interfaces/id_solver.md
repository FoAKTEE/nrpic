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

(Filled after the implementation: options, files, lines of shared files touched.)

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

(Filled after the runs: predictions and outcomes are in `tracks/core/JOURNAL-idsolve.md`.)

## 9. Not done, limits

(Filled at the end.)
