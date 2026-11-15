---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [tracks/E-stoch-inf/spec/scope/SCOPE.md, tracks/E-stoch-inf/stage/G0/CHECKLIST.md, tracks/E-stoch-inf/stage/G0/EVIDENCE.md, tracks/E-stoch-inf/stage/G0/OPEN.md]
---
body: The G0 package of Track E (feasibility gate) is on `track/E-stoch-inf`. The track
sheet asks the group to decide to continue, shrink or downgrade. Recommendation (SCOPE.md
section 9): continue to G1 and G2 (reproduce the SR and USR cases of 2512.14649), and decide
the scope of G3 (tail statistics) at G2, when the cost of one realisation has been measured
on a card. Reasons: core's implementation on `core/scalar-field` 836ac86 follows the
specification and its noise generator passes the validation (bitwise across MeshBlock
layouts and restart); the estimate to G2 is about 1.5-2 card-hours of the 10 allotted, one
256^3 realisation 0.4-0.5 card-hours (ten times below the downgrade threshold of 5 that the
owner fixed); the downgrade path (delta-N statistics for Track A) already exists. Not done
for the gate: working note v0 (REVTeX), the two schematics, the verifier report
(`OPEN.md`). The owner also fixed the open choices of the specification (SCOPE 4: Courant
0.25, backreaction level 0, thresholds A1-A8, downgrade threshold) for the group to confirm.
Smallest acceptable answer: the group's decision, and whether the gate may pass with the
note and schematics following at G1.
