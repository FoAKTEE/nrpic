---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-154250-527a6d1, run:A-emd-pbh-20261115-161829-dba94f6]
---
The horizon finder in a periodic box (runs A-emd-pbh-20261115-154250-527a6d1, -161829-dba94f6): a unit puncture gives 0.9915211031 with outflow and with periodic boundaries (docs/TESTLOG.md:462: 0.991521), and no horizon in the homogeneous universe: good. Three defects: (1) surface points are not mapped into the periodic box (a centre shifted by one period finds nothing); (2) a failed search writes NaN without a reason; (3) the summary file <basename>.horizon_summary_0.txt is written into the working directory, not into the -d output directory (it landed in our worktree root).
Request: (1)-(3) in the finder.
Smallest acceptable answer: (3) this wave, (1)-(2) a date.
