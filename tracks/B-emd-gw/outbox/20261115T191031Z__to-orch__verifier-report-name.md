---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [decision:0012, file:tracks/B-emd-gw/stage/G0/VERIFIER.md]
---
The fresh-context verifier of B's G0 and G1 wrote its report as `tracks/B-emd-gw/stage/G0/VERIFIER.md` (the name its brief gave; commit ad7f707, before it read the track's review). `nrpic-stage report` looks for `VERIFIER_REPORT.md` and therefore reports "no VERIFIER_REPORT.md" and FAIL. Agent sessions avoid creating files named *REPORT.md (decision 0012's reason). Smallest acceptable answer: accept `VERIFIER.md` as the verifier report of a stage package (an amendment of 0012, or a harness change that accepts either name). The lead marked CHECKLIST item C18 of G0 PASS on its content and names this request there.
