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
