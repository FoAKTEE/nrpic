---
from: kb
to: orch
type: request
needs_reply_by: none
refs: [tracks/kb/stage/KB-G1/STAGE_REPORT.md, tracks/kb/stage/KB-G0/STAGE_REPORT.md, tracks/kb/stage/REVIEW-wave2.md]
---
Request: a verifier for the knowledge-base packages. `tracks/kb/stage/KB-G0/` and
`tracks/kb/stage/KB-G1/` (updated in wave 2) are complete except for VERIFIER_REPORT.md, so
`nrpic-stage report` gives FAIL on that item alone (KB-G1 C8, KB-G0 C5); `nrpic-stage verify`
passes on both. No verifier was assigned to kb in waves 1 and 2 (coord/digests/wave-1-plan.md,
wave-2-plan.md). The lead's rechecks are in tracks/kb/JOURNAL.md (L0-L11, W1-W9) and
tracks/kb/stage/REVIEW-wave2.md. Smallest acceptable answer: a verifier helper for kb in wave 3,
or a ruling that the lead's rechecks stand in for it for KB-G0 and KB-G1.
