# Review of v1000_r2 (NR reader)

## 1. What I think the paper claims
Language-model agents rebuilt Wu and Most's relativistic particle-in-cell code in AthenaK from their paper alone, which mostly sufficed except for an unstated frame choice and one inconsistent radius. With ten thousand particles, dust collapse to a black hole and stable clusters come out right once three low-count artifacts are fixed: lattice surface mass excess, filter softening, and coarse deposition near horizons. They fixed a ghost-cell bug in AthenaK's horizon finder and cannot explain a growing central-lapse oscillation in stable clusters.

## 2. Where I got lost
- "where particle updates cost little beside spacetime evolution": why does this motivate 10^4?
- "One agent ... peers ... and a third": how many agents?
- "Every diagnosis was tested against a prediction": diagnosis of what? Give one example.
- "spacetime Boris pusher adapts the electromagnetic plasma update": what is Boris?
- "analytic digits" vs "mesh digits": digits of what? Which gauge did Wu and Most use?
- "while the frame shifts its coefficient": lost.
- "local-cell clouds", "virtual grid": need an example.
- "feel the slice mass": meaning?
- "at the exact threshold": which lapse value?
- "published cell-volume mass rule": define.
- "binding energy peaks at a binding-energy maximum": along what parameter?
- "relaxation": undefined.
- "expands earlier toward migration": earlier than what?
- "the quoted circular speed requires a host radius": whose quote, which figure?

## 3. Where I got bored or skimmed
Paragraph 2's lapse and shift definitions are textbook to me; "like a Maxwell solver" explains the familiar with the unfamiliar. Paragraph 3 spends a sixth of the text on a second-order frame ambiguity before saying why it matters. In paragraph 6, four "[pending]" tags made me stop trusting the list.

## 4. Cut / wanted more
Cut: lapse and shift definitions, the Hermite clause, the Schwarzschild aside, pending results.
More: numbers (horizon-mass bias, bounce size, oscillation growth rate); a direct answer to the opening reproducibility question; the horizon-finder bug, which every AthenaK user needs.

## 5. Would I read it?
Yes; first I would find the dust-collapse figure comparing lapse and horizon mass to the exact solution.
