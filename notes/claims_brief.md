# Claims brief for the title, abstract, introduction and conclusions

Status 2026-11-13 17:10. This is the list of what the paper claims, in the order of
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
4. (Withdrawn 17:10: an earlier item here, that black holes form only on meshes with
   six or more cells per horizon radius and that lapse-based removal aborts the
   collapse on coarser meshes, rested on a mass profile taken about the wrong centre.
   Do not write it.)

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

## Cluster with two overdensities: state (17:10)

- The overdensities collapse on time (smallest lapse 0.07 at 8.0 M with cells of
  M/128; the original's horizons are at 8.5 M).
- Black holes form with lapse-based removal, on both meshes tried. Measured with the
  Misner-Sharp mass about each tracker: 0.085 M at t = 10 M with cells of M/64 (the
  original: 0.088 M); 0.113 M at t = 12.3 M with cells of M/128.
- The apparent-horizon finder of the host code reports none of them (horizon radius
  three cells at M/64, ten cells at M/128). Why, and whether a setting cures it:
  PENDING.
- The M/64 run with the original's removal threshold failed at 11.9 M (cause not
  determined). The M/128 run with a lower threshold is running. Inspiral, merger and
  the common horizon: PENDING. Do not state an outcome.

## How the work was done (one paragraph in the introduction, one section)

- Language-model agents under human direction: one role wrote derivations and source,
  one ran and analysed, one wrote the text; exact reference solutions were written
  without access to the solver.
- Every explanation of an unexpected result was written down with a prediction before
  the run that could refute it. Eight first explanations were refuted this way or by
  an independent audit of the run files (cluster motion as sampling noise, twice; low
  horizon mass as early stopping of the finder; horizon-mass drift as part of the
  collapse; one level of cloud coarsening harmless; oscillation as a discretization
  error of the cell size; coarser-cloud disturbance as the lattice beat alone). One
  check of mine was itself wrong (a mass profile about the wrong centre) and was
  caught when two runs returned identical numbers; the statements built on it were
  withdrawn.
- Where no run isolates a cause the paper says "not determined".
