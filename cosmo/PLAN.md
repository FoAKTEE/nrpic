# Cosmological structure formation with the NRPIC code: plan

Started 2026-11-13. Request: use the NRPIC code for cosmological structure formation and
redo, in it, everything in three papers (small modifications allowed where needed):

1. East, Wojtak & Pretorius, "Einstein-Vlasov calculations of structure formation",
   arXiv:1908.05683 (most important). Method and observables are defined in its
   predecessor, East, Wojtak & Abel, arXiv:1711.06681.
2. Daverio, Dirian & Mitsou, arXiv:1904.07841 (time integration of a general-relativistic
   N-body code).
3. Barrera-Hinojosa & Li, arXiv:2001.07968 (initial conditions for a general-relativistic
   N-body code; its Part I is arXiv:1905.08890).

Sources are in `refs/arxiv_*/src/`. Reproduction specifications of papers 2 and 3 are in
`cosmo/notes/spec_*.md`. Progress is tracked in the working paper `cosmo/paper/main.pdf`
(its appendix "Progress ledger") and in `cosmo/TESTLOG.md` (every explanation with a
prediction written before the run that could refute it; later entries and corrections
override earlier ones).

Roles: Fable thinks, designs and writes the code; Opus agents do labor, audits and
independent reference implementations; nothing is asked of the user.

## Why this is cheap in a hyperbolic code (the design in one paragraph)

On a flat matter-dominated background gamma_ij = a^2 delta_ij and K = -3H. The lapse
condition d_t alpha = -(1/3) alpha^2 K (Bona-Masso with f = 1/3, available in the host
code as `lapse_oplog = 0`, `lapse_harmonic = 1/3`) gives alpha = a: the time coordinate
is conformal time, the coordinate speed of light is one at all times, and the time step
can stay fixed at a fraction of the comoving cell size. From a = 1 to a = 56 (collapse
of the 1 percent case of paper 1) the conformal time advances by 3.2 box lengths: about
800 steps at 64 cells per box length. The spatial coordinates are comoving, the mesh is
uniform and periodic, and no refinement is needed. Particle noise, the difficulty of the
first project, is absent at the start: a lattice of particles aligned with the mesh
deposits an exactly smooth density.

## What has to be built

Code (C++, in `athenak/`, all by Fable):
- B1. Periodic domains in the particle module: wrap positions after the push, wrap
  cloud cells in the deposit, probes.
- B2. Problem generator `nrpic_cosmo`: homogeneous background, analytic single modes,
  or fields read from a file on the mesh (conformal factor, K, traceless extrinsic
  curvature, lapse); particles from a file.
- B3. Proper time per particle (eighth real), so that every particle is a fiducial
  observer.
- B4. Null particles (zero rest mass) in both pushers, emitted at set times from set
  places, with trajectory output that carries what the redshift and the distance need.
- B5. Cosmological constant as a source term (papers 2 and 3).
- B6. Diagnostics: several probes; proper volume, mean K, extrema of lapse and density;
  constraint norms relative to their terms.

Python (`cosmo/`):
- P1. Initial data on the three-torus (`cosmo/ic/`): Zel'dovich lattice displacement
  with the relativistic dictionary, particle masses, and a spectral solve of the
  Hamiltonian and momentum constraints for the particles as deposited by the code.
- P2. Newtonian particle-mesh reference code (`cosmo/newton/`), same mesh, same cloud
  shape, plus the dictionary that turns its output into observer quantities.
- P3. Analysis: observer density contrast against proper time, crossing times, light
  rays (redshift, luminosity distance), power spectra.

## Milestones (each ends with figures inspected, log entries, working paper updated, push)

- C0. Infrastructure B1 to B3, B6. Test: homogeneous dust universe, a(t) and the
  density against the exact solution, constraint norms, convergence with the time step.
- C1. Linear regime: a single plane-wave mode and the three-mode data at very small
  amplitude against linear theory (growing mode, the relativistic density of the
  dictionary), with the constraint-solved data P1.
- C2. Paper 1, main results: the four amplitudes (0.25, 0.5, 1, 5 percent), general
  relativity against Newtonian gravity: density contrast seen by observers at the
  underdensity and at the overdensity; fall of fiducial observers through the
  overdensity and their crossing times; difference against infall velocity.
- C3. Paper 1, light: luminosity distance against redshift between overdensity and
  underdensity, against the homogeneous solution and between the two gravities (B4).
- C4. Paper 1, numerical appendix: constraint convergence, dependence of crossing times
  and of the distance-redshift relation on resolution and particle number; the extreme
  case to the point where it stops.
- C5. Paper 2: every test in `cosmo/notes/spec_1904.07841.md`.
- C6. Paper 3: initial conditions with a power spectrum and every test in
  `cosmo/notes/spec_2001.07968.md` (B5).
- C7. Paper: the working paper becomes the manuscript (text through the writer under the
  paper-writing skill once the results are in).

Method tracks that run beside the milestones (from the assessment of the first project):
- T1. Constraint-compatible deposition. Measure how much of the constraint violation in
  C1 and C2 comes from matter sources that do not satisfy the discrete continuity
  equation; design a flux-form deposit of the momentum density whose divergence equals
  the change of the deposited density; test whether the momentum constraint improves.
- T2. Evolving the departure from a known solution (delta-f). Design for the stable
  cluster of the first project, where it tests what seeds the core oscillation; in the
  cosmological runs the homogeneous lattice plays the role of the known solution.

## State and revisions (2026-11-14 01:08)

Done: C0, C1; C3 machinery (rays in the code, both analyses, homogeneous test).
Running: C2 rerun with identical positions in the two calculations, with the cloud-shape
study (linear, quadratic, cubic); C5 tests A0, A (homogeneous universe, a = 1 to 1001,
with and without noise) and B (plane-wave linear mode).
What the first runs changed in the plan:
- Sources go to the spacetime solver as densities, converted at every stage (C0).
- The lattice sits on the cell corners; the relativistic data use the Newtonian
  positions and carry the rest of the density in the masses (C1, C2).
- T1 is staged. T1a: smoother clouds (B-splines of degree two and three, done in the
  code): the sampling error of a compressed lattice is c/2, 0.4 c^2, 0.4 c^3 for the
  three shapes, and the mismatch between the deposited fields and the finite
  differences of the solver, which drives the constraint violation, is the unresolved
  part of the cloud shape. T1b, only if T1a leaves a floor: a momentum density built
  from fluxes so that the discrete continuity equation holds; centred differences do
  not see the Nyquist mode, so this needs the filter and a non-local map.
- C4 gains the resolution study that the first runs call for: 64, 96, 128 cells, one
  and two particles per cell and direction, the three shapes; the filter without the
  compensation pass as a variant (the compensated filter leaves cells of negative
  energy density next to the collapsed region).
- New item E1 (beyond paper 1, which left it to future work): the extreme case through
  the formation of the black hole. Needs a lapse condition that keeps conformal time
  where the universe expands and avoids the singularity where it collapses, mesh
  refinement around the overdensity, and the horizon finder of the first project in a
  periodic box. To be designed after C2 to C4.
- C5: tests A0, A, B at the resolutions of paper 2 where affordable (8 particles per
  cell instead of 27; the 128-cell case of test B later); test C (random field from a
  power spectrum, 704 and 256 Mpc/h) needs a spectrum generator and long runs with
  restarts, after B.
- The Slurm limit is one hour per job and the two GPUs are shared with the last runs of
  the first project: short runs go through `scripts/gpu_batch.sh`; long cosmological
  runs need the restart path, which is untested for periodic particle runs.

## State and revisions (2026-11-14 04:26)

- C5 test C (random field): larger box done at 32, 64, 128 cells; smaller box done at
  64 cells, 128 cells running as restartable chains. C6 done (initial-condition tests
  of paper 3 without radiation; helper agent, reviewed).
- Three method elements came out of test C and are now options of the code:
  `deposit_comp_c` (compensation of the cloud on the deposited density, before the
  division by the volume element: the growth of waves ten cells long is right to
  half a percent over a thousandfold expansion), `dt_expansion` (step limited to a
  fraction of the expansion time: removes the uniform Hamiltonian-constraint offset
  that the integrator leaves in the first steps), and `damp_kappa1_over_alpha`
  (damping at a fixed rate per unit of conformal time). Restarts are exact with all
  three (format 05).
- T1 revised. The compensation is the constraint-compatible deposit for smooth flow:
  it removes the smoothing mismatch at its leading order. What limits the constraints
  afterwards is the sampling of a distorted lattice (rise from z of about 3 in the
  linear box, to the same level at 32 and 64 cells) and, after collapse, the noise of
  the collapsed regions, which the pass amplifies. Open: particles per cell against
  cloud order after collapse (runs queued: 27 per cell, cubic cloud with its
  compensation), and whether to switch the pass off where the flow has crossed.
- Lesson logged: box sizes go into the input in full precision, from the meta file of
  the initial data; six digits left a density offset of 4e-7 that looked like a
  property of the scheme for an hour.
- Still open from before: E1 (shift condition on refined blocks), the split of the
  relativistic delay between initial offset and evolution, C4 leftovers (two
  particles per cell and direction, filter without compensation).

## State and revisions (2026-11-14 06:30)

- T1 has grown into a consistent set, all options of the code, each with a measured
  effect: cubic cloud (`deposit_shape = pcs`), compensation of the cloud on the
  deposited density to fourth order (`deposit_comp_c = 1/6`, `deposit_comp_c2 = 7/15`),
  spline interpolation of the metric at the particles (`interp = bspline`), step limit
  (`dt_expansion = 0.01`), damping at a fixed rate (0.5). With them: waves of ten
  cells grow correctly to a thousandth over a hundredfold expansion; energy and
  momentum of the deposited matter are conserved on the mesh at fourth order
  (`cons_dcycle`); the constraints of a linear random field stay below 7e-7 and 7e-4
  to z = 0 at twenty cells per shortest wave.
- Rules learned: resolve the shortest wave of the initial data with twenty cells (the
  terms of second order sit at twice its wave number); the Catmull-Rom gradient error
  depends on where the lattice sits in the cells; one particle per cell is enough with
  the cubic cloud before collapse and not with the quadratic one.
- Diagnostics added: constraint fields in the dumps (`field_constraints`), conservation
  on the mesh, `cosmo/analysis/constraint_field.py`, `cosmo/analysis/lattice_error.py`.
- Running: production runs of test C in this configuration (larger box 64 and 128
  cells, smaller box 64 and 128 cells), and the 64-cell collapse run with the spline
  to see whether the interpolation biases the relativistic delay.
- Not solved: the noise after the matter streams cross (constraints rise, the
  compensation amplifies it). Candidates: T2, or withholding the pass by a criterion on
  stream crossing rather than on contrast.

## State and revisions (2026-11-14 10:31)

- The redo of the three papers is complete (C0 to C6); every run of the working paper
  is in the production configuration, and the working paper's ledger holds all numbers.
- Finished since 06:30: production runs of test C in both boxes at 64 and 128 cells
  (chains), test B and the four collapse amplitudes in the production configuration,
  the conservation test, the Newtonian random field at 32 and 64 cells.
- Newtonian against relativistic power of the random field: the nonlinear excess over
  linear theory is the same in both; the relativistic power is lower by 0.01 to 0.02
  percent at 64 cells (0.014 to 0.046 at 32); the part in the shortest shell was
  numerical; whether the remainder is relativistic is not determined (needs the
  Newtonian run at 128 cells with the particles of the relativistic one; days on one
  processor with the present reference code, not run).
- Open, none needed for the redo: noise after the matter streams cross (three remedies
  on the constraint subsystem failed; the clue is the connection constraint); E1
  (black-hole formation in an expanding box); T2 (not started); the split of the
  relativistic delay between initial data and evolution.

## State and revisions (2026-11-15 15:40 UTC)

Note by the orchestrator from Track B's verification of `cosmo/` (program wave 1); the
entries above stay as written.
- The rule of 06:30 "one particle per cell is enough with the cubic cloud before collapse"
  fails where the lattice is stretched. Track B ran the plane-wave pancake
  (`cosmo/ic/make_east.py --ratios 1,0,0`, d = 0.05, exact Zel'dovich crossing at a = 21)
  in the production configuration, box of one initial Hubble radius, at 32, 64, 96 cells
  with one particle per cell and at 64 cells with two per cell and direction, to a = 42.
  With one particle per cell the mean relative Hamiltonian and momentum violations reach
  1.6e-4 and 0.13 at a = 10, 1.3e-3 and 0.21 at a = 15, before the crossing; they sit in the
  void and do not depend on the mesh, because the cubic cloud under-samples the stretched
  lattice there (the deposit differs from the continuum density by 0.21 in the void at
  a = 15). Two particles per cell and direction lower them to 3.2e-5 and 4.2e-5 (H) and
  1.0e-2 and 6.3e-3 (M), the void violation 115-fold at a = 15. After the crossing, with one
  per cell the energy density turns negative in void cells (E_min = -2.9e-7 against a mean
  of 7.6e-6 at a = 25); with two per cell it stays positive. The Newtonian reference on the
  same particles converges only at first order in the cell size with one per cell; two per
  cell remove that part.
- Evidence: runs B-emd-gw-20261115-115217-69ab1db and -115902-a3207d7 (cards, 0.48
  card-hours together), Newtonian -115239-69ab1db and -122451-01801f6, analysis
  -123852-ea4475c (`results/pancake.json`); `tracks/B-emd-gw/verify_cosmo/VERIFY.md`
  section 6, items 1, 3 and 6, figures `figs/pancake_constraints.png`, `figs/pancake_ppc.png`
  (branch `track/B-emd-gw`); proposal
  `tracks/B-emd-gw/outbox/20261115T1340Z__to-orch__cosmo-plan-particles-per-cell.md`.
- Rule from now on, in Track B's wording: one particle per cell is enough with the cubic
  cloud before collapse while the lattice is not stretched by more than about 2; for
  pancakes and voids use two per cell and direction. The factor 2 is the bound Track B
  proposes; the runs above measured the d = 0.05 plane wave only.
  The baseline of "Decisions" below (one lattice particle per cell) is affected for runs
  that form voids or pancakes.

## T2, design notes (not started)

Where it applies. A cold lattice has no smooth distribution function to subtract: its
error is the lattice sampling error of T1a, and the undisplaced lattice already deposits
exactly. T2 is for warm systems with a known stationary solution, i.e. the equilibrium
clusters of the first project, whose noise (the growing oscillation of the stable
cluster, the scatter of the collapse times) is sampling noise of the whole distribution.
Form. The distribution function is constant along particle paths, so a particle that
starts with the value f_p carries the weight w_p(t) = 1 - f0(z_p(t)) / f_p, where f0 is
the reference evaluated at the particle's current phase-space point. No weight equation
has to be integrated. The source is the stress-energy of f0 plus the weighted particle
sums; its noise scales with the size of the departure.
The difficulty in general relativity. f0 must be a function on the phase space of the
evolved coordinates, and its stress-energy must be taken in the evolved metric. For a
static cluster f0 = F(E) with E the conserved energy of the static metric; once the
gauge moves, E is no longer a known function of the evolved variables. Options, in
order of cost: (a) keep the reference in a gauge that the evolution can hold (static
slicing of the cluster with frozen lapse and zero shift while the departure is small);
(b) define f0 through the evolved metric itself, f0 = F(-p_t / alpha-like invariant),
which is not a solution and then needs the weight equation with a source term; (c)
tabulate the moments of f0 as functions of the local metric components.
First test, when started: the stable cluster of the first project at 1e4 particles in
the static gauge, option (a): the oscillation amplitude and its growth against the
full-distribution run.

## Decisions

- Particle numbers: the limit of 10^4 belonged to the first project. Here the mesh has
  64^3 cells at least, and the baseline uses one lattice particle per cell (64^3 =
  2.6e5), with 32^3 and 128^3 particles for the dependence on particle number.
- Initial data differ from paper 1 in one stated way: paper 1 keeps the density fixed
  and solves for the conformal factor and the shift (conformal thin sandwich); here the
  particles are fixed and the conformal factor and a vector potential of the traceless
  extrinsic curvature are solved for (the density scales with the conformal factor as
  the particles require, which also makes the Hamiltonian constraint uniquely solvable
  on the torus). Both satisfy the constraints and agree to linear order.
- Gauge differs from papers 1 and 2 (generalized harmonic; their own); comparisons use
  observer quantities, as paper 1 does.
- Newtonian reference: particle-mesh at the mesh of the relativistic run, so that the
  two differ in the gravity only (paper 1 used a tree code at higher force resolution
  and found the saturated densities sensitive to exactly that).

## Units

G = c = 1. Paper 1: initial Hubble rate H_0 = 1 at a = 1, box length L = 4 (four Hubble
radii), wave number k = pi/2, background density rho_0 = 3/(8 pi).
