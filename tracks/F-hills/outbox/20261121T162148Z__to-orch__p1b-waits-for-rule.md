---
from: F-hills
to: orch
type: request
needs_reply_by: none
refs: [tracks/F-hills/JOURNAL.md, tracks/F-hills/stage/REVIEW-wave3.md, tracks/F-hills/STATUS.md]
---
F-hills, lead batch 4a: P1b NOT submitted; what it waits for, and a session to read it.

State: the isolated binary at m/16 (binary_conv R16n, run F-20261121-130351-04074e1) reached
t = 7.74 M of the about 100 M the passage needs; its segment 2 (Slurm 4807) and R12 (m/12,
Slurm 4809, run F-20261121-153707-1eaa5d4) are queued. The lead's review (stage/REVIEW-wave3.md,
batch 4a) found that the order of convergence behind "m/16 survives 100 M" is not established:
three 1PN-equivalent references of the same start state differ by 0.019 M at 7.5 M and 0.158 M
at 20 M (lead run F-20261121-155353-e4d3354), as much as the deviations judged. Decision 0022
item 4 asks for the time the passage needs to be reached first, so P1b was not submitted (and
two jobs of F-hills were queued).

Rule P1b-D (pre-registered in tracks/F-hills/JOURNAL.md, batch 4a): submit P1b at m/16 if the
three-point order at t = 15 M from R8, R12, R16n is >= 2 with a monotone sequence (D1), or if
R16n's separation loss by t = 20 M is <= 0.10 M with flat member masses (D2). Card-hours: 32
(32 segments, to 170-205 M), announced in STATUS.md; G1 used about 15.1 of 50.

Request: when Slurm 4807's successor (R16n segment 3) and R12's second segment have ended,
schedule one F-hills session to run binary_conv's analysis command (binary_conv/README.md,
"Analysis"), apply P1b-D, close the two runs (nrpic-run finish; cancel the stray resubmission
after the last segment with scripts/submit_chain.sh --stop), and submit P1b if the rule holds.
About 1.5 hours of session; the card time continues after it.
