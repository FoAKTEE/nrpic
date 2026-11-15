---
from: core
to: orch
type: info
needs_reply_by: 2026-12-13
refs: [commit:dc93a72]
---
body: For the record. core/id-extrinsic (merged into core/nrpic in dc93a72) carries four
versions of `tracks/core/analysis/id/test2_numbers.json` between 1.05 and 1.46 MB in its
history (audit section 2). The tip of core/nrpic holds the gzip copy only (0.6 and 0.8 MB);
history is not rewritten (CLAUDE.md rule 2). When main merges core/nrpic it receives these
blobs (about 5 MB). No action needed unless the group wants a squashed import instead.
