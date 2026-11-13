# Story of the paper (step 1 of the writing procedure)

Provisional until the remaining runs finish; items marked [pending] depend on them.

## The question

A particle-in-cell method for collisionless matter in a dynamical spacetime was published
recently, with results obtained at 10^6 to 10^7 particles on large machines. Two things
are open for anyone who wants to use it:

1. Is the published description enough to rebuild the method independently?
2. What does the method need to work with ten thousand particles, a number that fits on
   one graphics card in under an hour, and which of its results survive there?

## The answer in one picture

The particle-mesh cycle: the mesh hands the metric to the particles, the particles move
on geodesics, hand their stress-energy back, and the spacetime solver advances. Every
arrow of that cycle is tested in isolation and then all together, and at each arrow the
low-particle-number regime changes one specific thing.

## Turning points

1. **The pushers are reproducible to the last published digit, once a hidden choice is
   identified.** The implicit midpoint pusher is fixed completely by its definition, and
   the rebuilt version returns the published errors of energy and Carter constant digit
   for digit. The spacetime Boris pusher works in an orthonormal frame, and the frame is
   free up to a rotation. Its truncation error depends on that choice. The published
   numbers for analytic input follow from the symmetric square-root frame, those for
   mesh input from the Cholesky frame. The method paper does not say this; the
   reconstruction found it.

2. **Deposition conserves exactly, on any mesh.** The volume integrals of the deposited
   sources equal the particle sums to rounding error, across refinement boundaries and
   through regrids.

3. **With few particles the mesh outruns the matter.** Each refinement level divides the
   particles per cell by eight. Following the published rule (cloud size = finest local
   cell), the dust-collapse source breaks into isolated blobs as soon as cells are
   smaller than the particle spacing, and the central density falls to less than half of
   its true value. Capping the level on which a cloud is represented, with the cap
   following the local particle density, removes this while keeping exact conservation;
   with the cap off the rule is the published one.

4. **What does not depend on particle number is reproduced at full precision**: the
   equilibrium sequence of relativistic clusters and its binding-energy maximum, the
   analytic lapse bound of collapsing dust and the time at which the evolution leaves it,
   the time-symmetric initial data.

5. **What does depend on particle number is reproduced in kind.** Dust collapses to a
   black hole with all matter excised and a horizon mass near the total mass [pending:
   final number with the tight horizon tolerance]. A cluster on the stable branch
   breathes about its equilibrium; clusters past the binding-energy maximum collapse
   [pending]; the unbound model disperses [pending]. Prolate collapse passes its caustic
   and forms a horizon [pending]. Two overdensities in a cluster collapse, orbit and merge
   [pending].

6. **A wrong number in the original was found by rebuilding it.** The orbital speed
   quoted for the two overdensities is a circular orbit only if the host cluster is less
   than half as large as stated; the published figure agrees with the smaller size.

7. **Who did the work.** The reconstruction was carried out by language-model agents
   under human direction, from the text of the paper alone: one model for design,
   derivations and solver source, others for builds, runs, exact reference solutions and
   analysis, a third for the manuscript. The paper says what was checked by whom and how
   (independent exact solutions written without sight of the solver code).

## What the reader should leave with

- The method can be rebuilt from its description, and the rebuild is quantitatively the
  same method.
- Two unstated choices matter: the tetrad gauge of the Boris pusher and the size of the
  particle cloud relative to the mesh.
- Ten thousand particles on one graphics card are enough for the qualitative physics of
  every published test; the price is sampling noise, which the paper quantifies.
- Open physical questions stay open at this particle number: the fate of the most
  compact cluster, the growth of curvature at the caustic.

## Title candidates

- Rebuilding the numerical-relativity particle-in-cell method with language-model
  agents: Tetrad gauge, level-capped deposition, and collisionless collapse with ten
  thousand particles
- Numerical-relativity particle-in-cell method at low particle number: An independent
  reconstruction by language-model agents
