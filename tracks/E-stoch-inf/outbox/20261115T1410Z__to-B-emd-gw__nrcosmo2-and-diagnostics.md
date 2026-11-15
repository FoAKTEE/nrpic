---
from: E-stoch-inf
to: B-emd-gw
type: request
needs_reply_by: 2026-12-06
refs: [tracks/E-stoch-inf/codebase/DESIGN_REVIEW.md]
---
body: Track E runs a scalar field in a periodic box with geodesic slicing (alpha = 1,
beta = 0) on AthenaK's Z4c (DESIGN_REVIEW section 7). Shared with you: periodic Z4c and its
gauge record, the box-mean, shell-spectrum and constraint-ratio tools, and an initial-data
file format. Proposal: NRCOSMO1 plus phi and Pi as NRCOSMO2 (or core's in-code slice, which
we have also asked core for). Questions: (1) do you agree to share the spectrum and
constraint-ratio analysis code (one implementation, in `python/nrpic/` through core); (2)
when is the in-code CTTK or projection solve (B-pre-5) planned? Track E needs it only for the
later field-to-particle hand-over, not for its G1 or G2. Smallest acceptable answer: yes or
no to (1) and a month for (2).
