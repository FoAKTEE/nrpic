---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-11-29
refs: [arXiv:2512.14649, tracks/E-stoch-inf/codebase/DESIGN_REVIEW.md]
---
body: For the G1 criteria of Track E (constraints converge; per-mode spectrum; freezing)
the scalar-field runs need, independent of the particle module:
(1) the constraint ratios H/[H] and M/[M] with the absolute magnitudes [H], [M] of
2512.14649 PRD_v2.tex lines 735-745, as box statistics in the history file at a cadence
option; (2) double-precision dumps of phi, Pi and of the Z4c fields chi, gt_ij, Khat (or K),
At_ij, alpha (Track E extracts R^NR = Phi - <K>/(3 <alpha><Pi>) (phi - <phi>) itself, SPEC
7.1 P-c, and the per-mode amplitudes by its own FFT); (3) box means of phi, Pi, K, alpha in
the history (A1); (4) the interface document `tracks/core/interfaces/scalar_field.md`
(the ten items of DESIGN_REVIEW section 9: variables and signs, task order, Tmunu, potentials,
kick hook, noise keys and levels, initial data, output, dissipation and refinement, tests).
Smallest acceptable answer: (1) and (2) with option names, and a date for (4).
