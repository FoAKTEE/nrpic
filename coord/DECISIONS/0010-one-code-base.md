# 0010 One code base: everything is built on top of this repository's AthenaK

Status: ACCEPTED (user instruction of 2026-11-15: "we already build the full NRPIC code in
our athenak, we should build everything on top of athenak") · orchestrator

Decision. Every simulation capability of the program is built in the AthenaK of this
repository (`athenak/src/`): spacetime, particles and their coupling (exist), collisions,
scalar fields and stochastic sources, a Newtonian reference gravity for the same particles
and clouds, several moving black holes, and the initial data the code starts from (problem
generators, fed as now by the repository's own tools under `problems/ic/` and
`python/nrpic/`). No outside simulation code is adopted, built or run (no GRChombo,
GRTeclyn, gevolution, REBOUND as a substitute for a capability), and no standalone
simulation code is written where the capability belongs in AthenaK.

What stays outside `athenak/src/`: exact and semi-analytic reference solutions (ordinary
differential equations, closed forms, the analytic criteria of the literature), the
analysis of AthenaK output, figures, notes, the knowledge base and the harness.

Consequences.
1. The "pre-core" packages of the brief that were standalone prototypes become source work
   in AthenaK, written by core (Fable) in this wave: the relativistic Monte Carlo collision
   operator (Track C), the scalar field with stochastic sources (Track E), the Newtonian
   reference gravity (tracks A, B, D), next to the three items already planned (initial
   data with extrinsic curvature, random numbers, several black holes). The track's helper
   for such a package writes the specification, the reference solutions and the tests, and
   checks the implementation independently.
2. Decision 0004 is settled: Track E builds on this AthenaK.
3. Newtonian precursor scans and baselines run in AthenaK's Newtonian mode once it exists;
   until then a track uses semi-analytic references and low-resolution full-relativity
   scouting runs, which the existing code can already do.
4. Initial-data solves beyond spherical symmetry go into the code (elliptic solver on the
   mesh) rather than into an offline solver: `coord/notes/design_wave2_initial_data.md`,
   section 2, is revised accordingly in wave 2.
