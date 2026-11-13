# Reader reports on the second 1000-word version (2026-11-13)

Three first-year graduate students read `v1000_r2.md` cold: numerical relativity (NR),
plasma particle-in-cell (PIC), stellar dynamics (SD). Full reports:
`review_r2_NR.md`, `review_r2_PIC.md`, `review_r2_SD.md`. All three could state the
claims of the paper correctly in their own words. Points raised by at least two are
marked *.

## Where they got lost (the main text must not repeat these)
- * "constraint-damped moving-puncture evolution": no idea (PIC, SD). One plain clause:
  the standard way to evolve Einstein's equations through black hole formation on a
  fixed mesh.
- * The tetrad gauges: "analytic digits", "mesh digits", "the frame shifts its
  coefficient" (all three). Say first why it matters (without the choice the published
  numbers cannot be reproduced), then which choice reproduces which published test, and
  give the reader a recommendation. The Hermite clause can go to the method section.
- * "one representation level on a virtual grid", "local-cell clouds" (all three): needs
  the one-dimensional example or the figure.
- * "geometric Misner-Sharp mass" (PIC, SD): define in one clause (the mass inside a
  sphere computed from the geometry of the slice alone).
- * "published cell-volume mass rule", "discrete surface excess" (all three): say the
  rule (each lattice site carries the density times the cell volume) and why it is
  heavy (more lattice sites lie inside a sphere than its volume in cells).
- * "level-capped deposition" used before it is defined (PIC, SD).
- * "feel the slice mass" (NR, SD): say it plainly: the tracers orbit a black hole whose
  mass in the simulation is slightly larger than its initial mass, and their orbits
  show that.
- * "at the exact threshold", "collapsed lapse" (NR, SD): which threshold; what the
  lapse does inside a black hole.
- * "until a coordinate wave arrives" (PIC, SD): say that it is a feature of the
  coordinates, not of the matter.
- * "binding energy peaks at a binding-energy maximum" (all three): circular. Say along
  which parameter (the sequence from loosely to tightly bound clusters).
- * "expands earlier toward migration" (all three): earlier than what, migration to
  what.
- * "the quoted circular speed requires a host radius" (all three): whose quote, is it
  an error in the original.
- "relaxation" (NR, SD): the SD reader took it for two-body relaxation. Always
  "relaxation of the Hamiltonian constraint".
- "electric-like kicks around a magnetic-like rotation" (SD): compare with
  kick-drift-kick leapfrog; say what plays the electric and the magnetic field (PIC).
- "One agent, peers, a third" (NR, SD): the count of agents confuses; one example of a
  prediction that overturned an explanation would say more.
- "where particle updates cost little beside spacetime evolution" (NR): does not say
  why ten thousand particles matter. Say it: a run takes minutes on one graphics card.

## Where they got bored or skimmed
- * The list of [pending] results (all three): "made me stop trusting the list". One
  sentence for what is not finished.
- * The frame paragraph is long for "they did not say which frame" (NR, SD).
- * The definitions of lapse and shift in the second paragraph (NR: textbook; PIC: a
  stack of definitions).
- The deposition paragraph "reads like a changelog" (SD).
- The last paragraph repeats the fifth (SD).

## What they wanted more of
- * Numbers, one per finding (all three): how heavy the horizon, how large the bounce,
  how fast the oscillation grows, particles per cell.
- * The defect of the horizon finder: "every user of that code needs this" (NR).
- A direct answer to the opening question (NR): is the published text sufficient?
- Filter widening against ordinary gravitational softening (SD): the stellar-dynamics
  reader knows softening; say that the filter is a softening and the compensation
  removes its leading effect.
- What was hard "from text alone" (PIC).

## What each would open first
NR: dust collapse, lapse and horizon mass against the exact solution. PIC: the bounce
with and without the compensation pass. SD: the central lapse of the stable cluster,
to judge whether the growing oscillation is physical or a small-N effect.

## Consequences for the main text
1. Introduction: answer the reproducibility question in its last paragraph, with the
   three low-particle-number findings and the horizon-finder defect named, each with
   the place where its number is shown.
2. Each finding gets one figure the reader can open first: horizon mass against the
   slice mass (finder defect); lapse history for plain against compensated filter
   (bounce); horizon mass for capped against uncapped deposition; lattice surface
   excess; stable-cluster oscillation with its controls.
3. The numbers readers ask for go into the figures and one results table in the
   appendix; the prose points to them.
4. The agents: one paragraph in the assembly section with one worked example of a
   prediction that failed.
5. No list of unfinished runs in the main text: what is not finished is not in the
   paper.
