# Review r2: first-year PIC reader

## 1. What I think the paper claims
AI agents rebuilt Wu and Most's relativistic particle-in-cell code in AthenaK from their paper alone, finding it omits one choice (the Boris-like pusher's local frame) that changes results. At ten thousand particles instead of millions, three problems appear (extra surface mass, filters softening gravity, coarse deposition near black holes), each fixed, plus a horizon-finder bug. Spherical collapse and stable clusters work, but a growing oscillation in stable clusters is unexplained and non-spherical runs are pending.

## 2. Where I got lost
- "constraint-damped moving-puncture evolution": what does it do? "Like a Maxwell solver" helped little.
- "turning frame axes produce the rotation": which quantity plays E, which B?
- "symmetric gauge ... analytic digits" / "Cholesky gauge ... mesh digits": which did Wu and Most use, which do you recommend?
- "Hermite interpolation sets the error scale": lost.
- "one representation level on a virtual grid": how is the level chosen? A 1D sketch would fix it.
- "geometric Misner-Sharp mass": define it.
- "cell-volume mass rule carries a discrete surface excess": what rule, why extra mass?
- "level-capped deposition": define before use.
- "until a coordinate wave arrives": physical or gauge?
- "binding energy peaks at a binding-energy maximum": circular.
- "expands earlier toward migration": migration to what?
- "host radius below one-half the stated value": an error in the original?

## 3. Where I got bored or skimmed
Paragraph 2, second half: a stack of definitions. Paragraph 3 after the Boris sentence: digit-matching I could not follow. Paragraph 6: a run log with five "[pending]" tags.

## 4. Cut / wanted more
Cut: Kerr/Schwarzschild digits, the Hermite clause, the pending list (one sentence suffices).
More: one number per fix (how heavy the horizon, how big the bounce); what the agents did and what was hard "from text alone"; why ten thousand particles matters; which gauge to use.

## 5. Would I read it?
Yes, for the PIC parts; I would look first for the bounce figure with and without the compensation pass.
