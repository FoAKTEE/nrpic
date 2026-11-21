---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:F-20261115-173719-923135a, run:F-20261115-181805-f9c3473, run:F-20261115-182100-613c9c6]
---
Request (repeat of outbox 20261119T152132Z__to-orch__wave2-run-dirs-unchecksummed.md, unanswered):
list the three wave-2 run directories of F-hills in coord/WAIVERS.md (decision 0019 item 6), so
that `nrpic-stage verify F-hills G0/G1` stops failing on them:

F-20261115-173719-923135a  outputs moved into the run directory after the run finished; data unchanged
F-20261115-181805-f9c3473  outputs moved into the run directory after the run finished; data unchanged
F-20261115-182100-613c9c6  outputs moved into the run directory after the run finished; data unchanged

Evidence: nr_first/JOURNAL.md "Incidents" (wave-2 scripts wrote outputs relative to the worktree
root; the helper moved them in within the same minute, after `finish` had checksummed the
directory); the numbers were reproduced later by registered runs (E4 rerun
F-20261119-143627-1a84aa5). The same reason as B-20261115-164157-40b9f6d, already waived.
