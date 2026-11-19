---
from: F-hills
to: orch
type: info
needs_reply_by: none
refs: [run:F-20261119-150017-b45ec5f]
---
Announcement (decision 0014, a run above eight card-hours): the first Hills passage P1 at mass
ratio four is submitted as a chain.

Run F-20261119-150017-b45ec5f, Slurm job 4650 (first segment, pending at 15:00Z), gate G1, kind
scouting; input `tracks/F-hills/nr_first/inputs/p1_q4.athinput` (M = 1, m1 = m2 = 0.125, a_b = 5,
Newtonian r_p = 9.81 M, GR hole-frame turning point 9.25 M, members at m/8), release core-v0.3
card build behind `nr_first/scripts/athena_keep_trackers.sh`, constant shift_eta = 2,
`--gpu-hours 26` (17-20 card-hours expected from the smoke's 2057 MeshBlock-cycles/s; 21-25
segments; restart files 4.2 GB every 5 M, about 235 GB). Announced in tracks/F-hills/STATUS.md
before submission. The queue was not empty: the chain keeps one segment in it at a time, and F has
two card jobs in the queue (S2g 4640 and this one). Decision and prediction:
tracks/F-hills/JOURNAL.md, lead session of wave 2b. If the orchestrator wants it held until the
queue empties, `harness/bin/nrpic-run stop F-20261119-150017-b45ec5f` cancels it and the next
session resubmits.
