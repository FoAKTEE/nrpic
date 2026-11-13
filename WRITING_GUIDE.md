# Writing guide: NRPIC reconstruction paper

The per-paper layer of the paper-writing principles (Sec. 0). This file and `NOTATION.md`
sit one level above the manuscript directory `paper/` (7.1). Where this guide is more
specific than the principles, it governs this paper.

## Journal and tone (2.8)

- Target journal: Physical Review D (REVTeX 4.2, `aps,prd,twocolumn`).
- Where the methods go: the method is the body of the paper (it is a methods paper), so
  the algorithm lives in the main text. Scenario parameters go to an appendix table;
  every measured number goes to the Supplemental Material.
- Tone: letter-like concision, Physical Review style, American English, no hype.

## Readers (1.2)

| Community | Minimum background the paper supplies |
|---|---|
| Numerical relativists (fluid or vacuum) | what a particle-in-cell method is: macroparticles, shape functions, deposition, filtering, sampling noise |
| Plasma particle-in-cell practitioners | the 3+1 split, lapse and shift, what Z4c evolves, moving-puncture gauge, apparent horizons |
| Stellar-dynamics and kinetic-theory readers | why geodesic motion plus deposited stress-energy solves Einstein-Vlasov; what an equilibrium sequence and its binding-energy maximum mean |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | the steps of the argument | Introduction; Collisionless matter in a dynamical spacetime (the system); The particle-mesh method (the algorithm); Test particles (regime: no back-reaction); Self-gravitating matter (regime: full coupling); How the code was assembled; Conclusions |
| Subsection of the method | one stage of the particle-mesh cycle each | Geodesic pushers; Metric reconstruction; Stress-energy deposition; Spacetime evolution; Adaptive mesh; Numerical methods (last) |
| Subsection of each results section | the physical scenario | Fixed black hole; Evolving black holes / Dust collapse; Prolate collapse; Relativistic clusters; Collapse and merger inside a cluster |

Special cases entered as limits (2.2): Schwarzschild enters as the nonrotating limit of the
Kerr geodesic tests; the published deposition scheme enters as the limit of the
level-capped deposition with the cap removed; uniform and statically refined meshes enter
as limits of the adaptive mesh.

## Allowed numbers (4.1)

- Exact analytic factors and powers: 8 pi, 4 pi, 1/2, 1/3, psi^4, psi^6, chi^(-7/4),
  N^(-1/2), the factor eight in particles per cell per refinement level, binomial weights
  1/4, 1/2, 1/4.
- Structural integers: six phase-space variables, ten source components, eight receiving
  cells, four-point stencil, second-order accuracy, the two pushers, the two tetrad gauges.
- Labels: the equilibrium label y_c of each cluster model; (l, m) mode labels.
- Parameter values that define the figures: black hole spin a = 0.9 M, eccentricity
  e = 0.99, initial areal radius R_0 = 5 M, the particle numbers 10^2, 10^3, 10^4, the
  spheroid eccentricity 0.9.
- Everything else (errors, tolerances, step sizes, mesh spacings, times of horizon
  formation, masses, fit parameters) lives in figures, the appendix table, or the
  Supplemental Material.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole | any |
| Numerical methods | pipeline, solver, infrastructure (as a section title) | any |
| numerical-relativity particle-in-cell (NRPIC) method | NRPIC code, the reproduction | this paper |
| macroparticle | superparticle, marker | particle-in-cell |
| shape function; cloud-in-cell | kernel (for first order), CIC without definition | particle-in-cell |
| deposition | scatter, projection | particle-in-cell |
| pusher | integrator (for the particle update) | particle-in-cell |
| implicit midpoint pusher | midpoint scheme, IM | particle-in-cell |
| spacetime Boris pusher | DGREM-Boris, GR-Boris (which is a different scheme) | this paper |
| tetrad gauge; symmetric gauge; Cholesky gauge | triad choice, frame convention | this paper |
| moving-puncture gauge | puncture gauge, 1+log/Gamma-driver (without naming it once) | numerical relativity |
| apparent horizon | horizon (when the finder is meant) | numerical relativity |
| lapse excision | particle deletion, culling | numerical relativity |
| collisionless | dust (unless pressureless and cold is meant) | kinetic theory |
| Einstein-Vlasov system | Vlasov-Einstein, kinetic GR | kinetic theory |
| monoenergetic cluster | Shapiro-Teukolsky cluster (after first mention), ST model | relativistic stellar dynamics |
| binding-energy maximum | turning point (without saying of what) | relativistic stellar dynamics |
| level-capped deposition | capped CIC, fat particles | this paper |
| sampling noise | shot noise, particle noise (mixing terms) | particle-in-cell |
| relativistic cluster with two collapsing overdensities | Jeans run, the name of a problem generator | this paper |

## Project names (5.8)

The project's intermediate products, which the paper never names. Pass them to the checker
as `--forbid 'nrpic_cf|nrpic_geodesic|kernel_test|build_gpu|gpu_run|submit_chain|make_ic|athinput|Slurm|A100|anta'`.

- problem generator and script names (`nrpic_cf`, `nrpic_geodesic`, `kernel_test`,
  `make_ic.py`, `gpu_run.sh`, `submit_chain.sh`), input-file names, run directories;
- the standalone kernel driver and the Python prototypes;
- the cluster, its scheduler, and its hardware.

The paper names the codes of others (AthenaK, Kokkos, the published NRPIC implementation
of Wu and Most, WarpX, Entity, TRISTAN-MP) and its own code in its current version.

## Standing statements of fact (keep consistent everywhere)

- The work is an independent reconstruction of a published method from the text of the
  paper alone; no code of the original authors was used or seen.
- The reconstruction was carried out by large-language-model agents under human
  direction; say so in the title or abstract, the Introduction, the dedicated section,
  and the acknowledgments.
- All runs use at most 10^4 particles; the original uses 10^6 and above. Statements about
  noise-limited quantities are scoped to that.
- Quantities that do not depend on particle number are compared at the precision of the
  original (geodesic invariants, equilibrium sequences, conservation identities).

## Figures (Sec. 9)

Filled in as figures are produced; one script per figure in `paper/scripts/`.

| Figure | What the reader should see | Defining parameters (cited from the setup table) |
|---|---|---|
| cycle | the stages of one particle-mesh cycle and what each exchanges | none |
| Kerr orbits | bound orbits precess and stay on their tori | a = 0.9 M |
| passage | both pushers conserve the invariants through a near-capture passage; mesh interpolation sets the error | a = 0.9 M, e = 0.99 |
| deposition | a cloud crossing a refinement boundary keeps unit weight; the level cap keeps its size | none |
| dust collapse | lapse follows the analytic bound until the gauge wave arrives; density follows the cycloid | R_0 = 5 M |
| clusters | stable models hold, compact models collapse, the unbound model disperses | y_c labels |
| assembly hypergraph | which existing capabilities were combined into each component (last main-text figure) | none |
