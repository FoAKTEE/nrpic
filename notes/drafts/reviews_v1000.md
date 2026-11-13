# Reader reports on the 1000-word version (step 4 of the writing procedure)

Three readers, each a first-year graduate student: numerical relativity (NR), plasma
particle-in-cell (PIC), stellar dynamics (SD). Points raised by at least two are marked *.

## Where they got lost
- * "push" and "deposit" used without a clause saying what they do (NR, SD).
- * The Boris step: say it is the plasma trick for a charge in electric and magnetic
  fields, the electric-like part changes the momentum and the magnetic-like part only
  rotates it; say what plays the role of the two fields (all three).
- * "triad derivatives enter the fields as frame-rotation forces while endpoint
  transformations rotate momentum into and out of the frame": lost (all three). An
  analogy would help: pushing with rotating polar unit vectors versus fixed Cartesian
  ones.
- * The tetrad finding: the conclusion cannot be extracted. Say plainly: the original
  paper never states which frame it used; its test with an analytic metric matches one
  frame and its test on a mesh matches the other. And resolve the apparent contradiction
  with "interpolation sets the error" (all three).
- * The wall of spacetime-solver names (constraint-damped conformal decomposition,
  moving-puncture gauge, logarithmic slicing, hyperbolic shift): treat it as the standard
  field solver, the equivalent of the Maxwell solver, in one clause (all three).
- * "the conservation identity": conservation of what, and what goes wrong at a
  refinement boundary without the single-level rule (all three).
- * "representation level", "virtual uniform lattice": need a sketch (NR, SD).
- * "the cycloid", "the lapse bound", "the surface gauge wave", "continuum benchmarks",
  "Kretschmann scalar", "time-symmetric initial slices": undefined (all three).
- * The parameter discrepancy: speed of what; is the text wrong and the figure right (all
  three).
- "normal observers", "covariant spatial momentum", triad versus tetrad: never explained
  (PIC).
- "lapse excision": what is removed and why (PIC, SD).
- Why at most ten thousand particles, if particles are cheap (SD).
- Who rebuilt the method is only said in the seventh paragraph; say it at the start
  (NR, PIC).

## Where they got bored
- * The list of steps of one cycle with no reason for any step.
- * The colon list of benchmarks, each stated as "it matched".
- * The credits roll of what each existing code supplies; the exponent seven-fourths is
  noise without a reason.
- * Five pending outcomes in a row; they undercut the closing claim.
- * The conclusion repeats the contributions.
- The textbook gloss of the 3+1 split (NR).

## Clearest sentences (all three chose the same)
1. Sampling noise scales as the inverse square root of macroparticles per cell.
2. Halving the cell edge divides the macroparticles per cell by eight per level.
3. The division of roles among the agents.
The paragraph on few particles and a fine mesh was the best one: readers recognized the
softening problem and "adaptive smoothing length".

## What they took away
All three: language-model agents rebuilt a general-relativistic particle code from the
paper alone and found what the paper left unspecified (the local frame of the pusher, the
cloud size on a refined mesh at low particle number) plus one wrong parameter. None could
say whether the black hole results hold, because they were marked pending.

## Figures they asked for
- Both tetrad gauges' errors over the published values.
- Central density of the dust collapse: uncapped, capped, analytic.
- Sketch of deposition at a coarse-fine boundary; conservation error versus time through
  regrids.
- Binding-energy curve with the stable, collapsing and dispersing runs marked.
- Apparent-horizon mass versus time against the total mass.
- The stated versus inferred cluster radius.
- One schematic of a time step.
- A timing breakdown (particle cost versus spacetime cost).
