# Review r2: stellar-dynamics reader

**1. What I think the paper claims**
AI agents rebuilt Wu and Most's relativistic particle code from text alone, finding that the paper leaves the pusher's local-frame choice unstated and that AthenaK's horizon finder had a bug. With only 10^4 particles the rebuild reproduces spherical dust collapse and the stable/unstable split of relativistic clusters, once three small-N artifacts (surface mass error, filter-induced softening, coarse deposition near holes) are fixed. A growing core oscillation in stable clusters stays unexplained.

**2. Where I got lost**
- "constraint-damped moving-puncture evolution": no idea; one plain clause.
- "slice-normal observers": one sentence or picture.
- "electric-like kicks around an energy-preserving magnetic-like rotation": plasma jargon; compare to kick-drift-kick leapfrog.
- "symmetric gauge" vs "Cholesky gauge": which is right, and why care?
- "their analytic digits" / "their mesh digits": what are these?
- "the frame shifts its coefficient": lost.
- "one representation level on a virtual grid": needs an example.
- "feel the slice mass": vague.
- "collapsed lapse": define; which "exact threshold"?
- "geometric Misner-Sharp mass": undefined.
- "discrete surface excess": show the error once.
- "level-capped deposition": undefined.
- "Particle-independent tests": of a particle code?
- "until a coordinate wave arrives": what wave?
- "expands earlier toward migration": earlier than what?
- "the quoted circular speed requires a host radius": whose quote, which figure?

**3. Where I got bored or skimmed**
Paragraph 4 reads like a changelog (octree weights, ghost cells). Paragraph 3 is long for "they didn't say which frame." I skipped the "[pending]" run in paragraph 6. Paragraph 7 repeats paragraph 5.

**4. What I would cut / what I wanted more of**
Cut: agent division of labor ("peers... a third" broke my counting), Kerr digits, ghost cells, pending items, "binding energy peaks at a binding-energy maximum."
More: numbers (bounce size, dynamical times, particles per cell); filter widening versus ordinary softening; whether "relaxation" means two-body relaxation; one prediction that overturned a first explanation.

**5.** Yes; I would go first to the stable-cluster central-lapse plot to judge whether the growing oscillation is physical or small-N noise.
