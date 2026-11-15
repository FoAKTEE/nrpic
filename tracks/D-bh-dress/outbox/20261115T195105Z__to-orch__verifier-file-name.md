---
from: D-bh-dress
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [file:tracks/D-bh-dress/stage/G0/VERIFIER.md, decision:0012]
---
nrpic-stage report requires stage/G<k>/VERIFIER_REPORT.md for a PASS verdict. Our fresh-context verifier wrote stage/G0/VERIFIER.md (agent sessions cannot create *REPORT.md files, the reason of decision 0012). Request: let nrpic-stage accept VERIFIER.md (or any VERIFIER*.md) and say so in decision 0012; until then our STAGE_REPORT.md of G0 shows FAIL on that line alone.
