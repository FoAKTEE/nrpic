# Story of the paper (step 1 of the writing procedure)

Second version, 2026-11-13 08:40, after the control runs of this morning. Items marked
[pending] wait for runs that are queued. Numbers quoted here are in `docs/TESTLOG.md`.

## The question

A particle-in-cell method for collisionless matter in a dynamical spacetime was published
recently, with results obtained at 10^6 to 10^7 particles on large machines. Two things
are open for anyone who wants to use it:

1. Is the published description enough to rebuild the method independently?
2. Which of its results survive with ten thousand particles, a number that fits on one
   graphics card in minutes, and what has to change for that?

## The answer in one picture

The particle-mesh cycle: the mesh hands the metric to the particles, the particles move
on geodesics, hand their stress-energy back, and the spacetime solver advances. Every
arrow of that cycle is tested in isolation and then all together. The rebuild is
quantitatively the same method. With few particles, three places need care, and each
was found by a run that could have shown otherwise.

## Turning points

1. **The pushers are reproducible to the last published digit, once a hidden choice is
   identified.** The implicit midpoint pusher is fixed completely by its definition, and
   the rebuilt version returns the published errors digit for digit. The spacetime Boris
   pusher works in an orthonormal frame, and the frame is free up to a rotation. Its
   truncation error depends on that choice. The published numbers for analytic input are
   reproduced by the symmetric square-root frame, those for mesh input by the Cholesky
   frame. The method paper does not state the choice.

2. **Test particles: every piece of the particle side holds on its own.** Clusters of
   test particles keep their invariants, phase-mix into a ring, are removed at the lapse
   threshold when exact geodesics say so, and the deposited sources integrate to the
   particle sums to rounding through 10^5 refinement-level crossings. Around a black
   hole that is itself evolved, tracers follow exact geodesics in gauge-independent
   quantities, and they feel the mass of the numerical black hole (slightly heavier
   than the initial one at the resolution used), which the slice's own mass confirms.

3. **An independent mass measure exposes a defect in the host code's horizon finder.**
   The finder read 2 to 6 percent low for a black hole of known mass, worse at higher
   resolution. Cause: it interpolates a derivative array whose ghost cells are never
   filled, so a horizon cut by mesh-block faces is evaluated wrongly. Taking the
   derivatives from the interpolant of the metric brings finder and slice mass together
   to a few parts in 10^4. Without the independent measure (Misner-Sharp mass of the
   slice) the low value would have passed as a property of the collapse.

4. **Low particle number, first place: the lattice start of the dust ball.** The
   published mass rule on lattice sites carries the lattice-count error of a sphere,
   negligible at a million particles and 1.2 percent at ten thousand. It shows up as a
   shell of excess mass and a horizon heavier than the spacetime. Putting the correction
   into the outermost lattice layer makes the horizon mass at formation equal to the
   total mass to 3 parts in 10^4.

5. **Low particle number, second place: the filter.** Few particles need several
   filter passes. Each plain binomial pass widens every cloud, and the widening softens
   the self-gravity: with four passes a stable cluster expands by 15 percent and comes
   back, identically for every sample; the excursion scales with the number of passes.
   A compensation pass (standard in plasma codes) cancels the widening and removes the
   excursion while keeping the smoothing. The same bias advances the expansion of the
   unstable model that the original uses as its migration test.

6. **Low particle number, third place, a negative result: coarser clouds.** Giving a
   particle a cloud on a coarser level than its cell (level-capped deposition) keeps the
   source smooth when the mesh is refined under diffuse matter, and it conserves
   exactly. It does not change the collapse of the centre, and near the forming black
   hole it makes things worse (constraint violation two to three times larger, horizon
   mass drifting by half a percent to one percent), even with one level of coarsening.
   The published rule, cloud at the finest local level, is the one to use there. Why
   even a little coarsening hurts is not determined.

7. **What does not depend on particle number is reproduced at full precision**: the
   equilibrium sequence of relativistic clusters and its binding-energy maximum, the
   analytic lapse bound of collapsing dust and the time at which the evolution leaves it,
   the time-symmetric initial data.

8. **What does depend on particle number is reproduced in kind.** Dust collapses to a
   black hole, all matter is removed, and the horizon mass equals the total mass to
   0.1 percent. A cluster on the stable branch stays bound and centred for 600 M; its
   central lapse oscillates at the radial period of its core with an amplitude that
   grows to two to three percent, which the original's figure can neither show nor
   exclude [cause not determined: not the sample, the particle number, the time step,
   the constraint damping or relaxation, or the cloud width]. The unperturbed model
   past the binding-energy maximum expands, as in the original, earlier [migration run
   pending]. Compact models with an inward kick collapse [pending]; the unbound model
   disperses [pending]. Prolate collapse [pending]. Two overdensities in a cluster
   [pending].

9. **Two quoted numbers of the original do not fit together.** The orbital speed quoted
   for the two overdensities is the circular speed only if the host cluster is less than
   half as large as the stated radius; the extent of the cluster in the published figure
   agrees with the smaller size. Which of the two numbers is the misprint, or whether
   the orbit was meant to be circular, cannot be decided from the text; the rebuild uses
   the reading that is self-consistent and says so.

10. **Who did the work, and how it was kept honest.** Language-model agents under human
    direction, from the text of the paper alone: one model for design, derivations and
    solver source, others for builds, runs, exact reference solutions and analysis, a
    third for the manuscript. On one morning five first explanations written by the lead
    agent were wrong (the stable cluster's motion as sampling noise, twice; the low
    horizon mass as early stopping of the finder; the horizon-mass drift as part of the
    collapse; a little cloud coarsening as harmless). Each was caught by a run designed
    so that the explanation could fail, with the expected outcome written down first.
    The paper reports results in that form: what was predicted, what was run, what came
    out, and "not determined" where no run isolates a cause.

## What the reader should leave with

- The method can be rebuilt from its description, and the rebuild is quantitatively the
  same method.
- One unstated choice matters for reproducing the published numbers: the tetrad gauge of
  the Boris pusher.
- At ten thousand particles two things must change (lattice masses at the surface,
  compensation of the filter) and one tempting change should not be made near black
  holes (coarser clouds).
- Horizon masses need an independent check; here it found a defect in the host code.
- Ten thousand particles on one graphics card are enough for the qualitative physics of
  the published tests, in minutes per run [as far as the pending runs confirm].
- Open: why the stable cluster's core oscillation grows; why coarser clouds disturb a
  forming black hole.

## Title candidates

- Rebuilding the numerical-relativity particle-in-cell method with language-model
  agents: What changes at ten thousand particles
- Numerical-relativity particle-in-cell method at low particle number: An independent
  reconstruction by language-model agents
