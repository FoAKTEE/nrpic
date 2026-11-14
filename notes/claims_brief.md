# Claims brief for the title, abstract, introduction and conclusions

Status 2026-11-13 16:15. This is the list of what the paper claims, in the order of
importance, each with the place where the paper shows it. The abstract, the last
paragraphs of the introduction and the conclusions state these and nothing beyond them.
Source of every statement: `docs/TESTLOG.md` (later entries and "Correction" entries
override earlier ones) and `notes/results_brief_selfgravity.md`. Items marked PENDING
must not be written as results.

## The two questions

Q1. Does the published description of the numerical-relativity particle-in-cell method
suffice to rebuild it, without the original code?
Q2. Which of its results hold at ten thousand macroparticles on one graphics card, and
what has to change for that?

## Answers

A1. Yes, with one unstated choice and two places where the text is incomplete.
- The tetrad gauge of the spacetime Boris pusher is not stated. The symmetric gauge
  reproduces the published digits of the invariant errors on the analytic metric; the
  Cholesky gauge reproduces the published digits on the mesh. (Sec. test particles.)
- For the cluster with two overdensities, the stated orbital speed is the circular
  speed only for a host cluster less than half as large as the stated radius; the
  published figure agrees with the smaller size. (Appendix on sampling.)
- For the perturbed near-critical cluster, the text gives the size of the density
  perturbation and neither its sign nor its form. (Sec. clusters.)
- Every single-particle and test-particle benchmark of the original is reproduced
  (invariant errors to the published digits; second-order convergence in the time
  step; third order in the cell size with cubic Hermite reconstruction; conservation
  identities of the deposition to rounding error).

A2. What holds at ten thousand macroparticles.
- Dust collapse: lapse bound and cycloid; horizon mass equal to the total mass to one
  part in a thousand at formation, as in the original at millions of particles.
- Relativistic cluster sequence: the two models on the stable branch hold; the two
  bound models past the binding-energy maximum collapse to black holes whose mass ends
  at the total mass; the unbound model disperses. Fates as in the original.
- Migration of the unperturbed unstable model: same sequence of states and the same
  first two maxima and minima of the central lapse as the original, to the end of the
  original's run.
- Near-critical model: unperturbed, it shows the oscillation (period, largest swing,
  decay, slow fall of the lapse) that the original shows for its perturbed model.
- Prolate collapse: passes through the caustic stage and forms an apparent horizon at
  the time shown in the original.
- With 10^3 particles the stable cluster holds for a few periods and then drifts; with
  10^2 it does not hold.

A2. What has to change at this particle number (each found by a control run).
1. Lattice masses of the dust ball: the published cell-volume rule overcounts the mass
   at the surface by about one percent; rescaling the outermost layer restores the
   horizon mass.
2. Source filter: several plain binomial passes widen every cloud and soften gravity
   (a stable cluster expands by about fifteen percent in radius and returns); a compensation
   pass removes this and keeps the smoothing.
3. Random samples and refinement: with a random sample the curvature-based refinement
   follows the sampling noise. Four passes with compensation, a limit on the depth, or
   coarser clouds keep it bounded. Coarser clouds cost a few tenths of a percent of
   horizon mass near a forming black hole (more on a lattice, where the regular
   particle lattice beats against the cloud lattice), so collapse results use the
   published rule.
4. Removal of particles: a black hole forms only where the mesh has about six or more
   cells per horizon radius; on a coarser mesh the lapse falls below the removal
   threshold before a horizon exists, the removal takes the collapsing core away and
   no black hole forms. Where horizons formed in this work they preceded the first
   removal. [Established at M/64 for the cluster with two overdensities; whether M/128
   suffices is PENDING.]

A third result that concerns the host code.
- The apparent-horizon finder of the host code, as distributed, interpolated a
  derivative array whose ghost cells are not filled; masses came out two to six
  percent low, worse on finer meshes. Found by comparing with the Misner-Sharp mass of
  the slice; removed by differentiating the metric interpolant.

## Documented differences from the original (causes not determined unless stated)

- Collapse times of the two compact kicked clusters are later here (horizons at 104
  and 191 M against 73 and 109 M).
- Migration: every extremum after the first maximum comes earlier here (full cycles of
  250 to 290 M against 290 to 310 M) and the later swings are smaller.
- Near-critical model: a homologous ten-percent change of the density gives collapse
  (compression) or an oscillation about a higher lapse (expansion); the original's
  curve is matched by the unperturbed model, 150 M later.
- Central lapse after collapse settles lower here than in the original (not looked
  into).

## Limitations found here (not differences from published numbers)

- Prolate collapse: the horizon mass peaks three percent below the total mass and is
  five percent below and falling at the end of the run; the missing mass is field
  content outside the black hole; a spherical control shows that random sampling alone
  costs only a few tenths of a percent. The original states no horizon mass for this
  test. A run with halved cells does not fit on one card.
- Stable clusters: the central lapse oscillates at the core period with a swing that
  grows and then saturates at a few percent; controls exclude random seed, sampler,
  particle number between 10^3 and 10^4, time step, constraint damping and relaxation,
  cloud width and cell size as the cause of the growth. What sets the small offset
  from which it starts is not determined.
- Cluster with two overdensities: PENDING (see below).

## Cluster with two overdensities: state

- The overdensities collapse on time (cores collapsed at 9.2 to 9.4 M; the original's
  horizons are at 8.5 M).
- With cells of M/64 at the overdensities (the original: M/256) no apparent horizon
  forms: three cells per horizon radius. Lapse-based removal then takes the cores away
  and the collapse is aborted (shown with the Misner-Sharp mass: no trapped surface).
- Runs with cells of M/128 are in progress: PENDING. Do not state an outcome.

## How the work was done (one paragraph in the introduction, one section)

- Language-model agents under human direction: one role wrote derivations and source,
  one ran and analysed, one wrote the text; exact reference solutions were written
  without access to the solver.
- Every explanation of an unexpected result was written down with a prediction before
  the run that could refute it. Eight first explanations were refuted this way or by
  an independent audit of the run files (cluster motion as sampling noise, twice; low
  horizon mass as early stopping of the finder; horizon-mass drift as part of the
  collapse; one level of cloud coarsening harmless; oscillation as a discretization
  error of the cell size; coarser-cloud disturbance as the lattice beat alone; black
  holes of the overdensities formed but under-resolved).
- Where no run isolates a cause the paper says "not determined".
