---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [file:tracks/E-stoch-inf/stage/G1/VERIFIER.md, file:tracks/E-stoch-inf/outbox/20261119T151727Z__to-orch__a4-a5-rewording.md, run:E-20261121-030657-c1afe38, run:E-20261121-031951-82984f8, run:E-20261121-063551-7957a3d, decision:0013]
---
Request of the owner of E-stoch-inf: rule on A4' (repeat of the proposal
`tracks/E-stoch-inf/outbox/20261119T151727Z__to-orch__a4-a5-rewording.md`, unanswered), now
with the fresh-context verifier's evidence. G1's track criterion "the constraints converge"
cannot be closed without this ruling.

What is new since 2026-11-19:
- The verifier of the G1 material (`tracks/E-stoch-inf/stage/G1/VERIFIER.md`, helper
  g1verify, own code from the raw dumps; runs E-20261121-030657-c1afe38, -031951-82984f8,
  -032413-0672bf9) confirms that the strict A4 fails at every N of P1's set-up for two
  measured reasons: a uniform time-integration residual (order s^0, order 4.1 in the step)
  and a first-order discretisation part (halving 1.9989-2.0000, order 5.5-5.9) that dominates
  once shells with fewer than about eight cells per wavelength enter; the second-order part
  halves by 3.986-4.000 and is resolution-independent (L128/L256 within 0.8 percent).
- Core explains the first-order part as the defect of the discrete contracted Bianchi
  identity of the Z4c stencils (`tracks/core/interfaces/scalar_field_3.md` section 4,
  message scalar3-closed): strict A4 would need nmax2 <= (N/12.7)^2.
- A4' clauses (a)-(c) pass with margin; (d) (negative control >= 1e3 x proper) passes on the
  maxima over the entry (1709-1874) and fails point by point at the end of the entry (89-179).
- The lead reran the verifier's analyses from its registered outputs (this session,
  `stage/REVIEW-wave3.md`).

Proposed ruling (the verifier's recommendation, which the lead adopts): A4' in, with
(i) clause (d) read on the maxima over the entry, (ii) the floor of (a), (b) defined as the
part that does not scale with the noise amplitude s, (iii) the "two finest resolutions"
clause of (a) applied in a set-up with the same modes at both resolutions (the L set-up),
and (iv) the strict A4 kept on record as failed for the measured reasons. Disclosure: A4'
was written after the data were seen (SCOPE 4b says so).

Smallest acceptable answer: "A4' adopted as proposed", "adopted with changes: ...", or
"A4 stays; G1's constraint criterion is failed in P1's set-up".
