---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: []
---
Track E, batch 34: the G3 baseline read on 71 of 128 mirrored pairs; two requests.

1. Result (g3/JOURNAL.md entry 17; run E-20261128-000627-00ed437; predictions committed first in entries 4 and 15).
   - Tail shape (T) agrees with one-patch delta N of the same band on every item: skewness 0.019721 +- 0.000010 against
     0.01985 +- 0.00088; excess kurtosis consistent with zero in both; tail fractions at three and four own standard
     deviations and the asymmetry within 2.1 combined standard errors.
   - Variance (V) FAILED as written: +0.28 +- 0.07 per cent (4.1 combined s.e.; the 0.01 clause holds). The lattice sits
     0.13 per cent above the lattice sum of the linear power, the reference 0.15 per cent below. No cause named.
   - G3 is NOT ready for review: 57 baseline pairs and all 16 level-2 pairs have not run (A13 asks for 128 pairs), A4 is
     not computed, no fresh verifier yet. stage/G3/OPEN.md gives the order.

2. Request (queue): G3B06 (job 5419) and G3L00 (job 5420) were cancelled by preemption on 2026-11-26 and the shared queue
   lists both as "done"; this session six re-queued entries (jobs 5525-5529, 5532) and two more (5533, 5534) were
   preempted within seconds to a minute and also show "done". Please let the queue mark a preempted batch job as such
   (or retry it), so that a gate run cannot drop out silently. Track E re-queued all of them (q0079-q0084, q0087, q0088).

3. Request (priority): those eight entries carry the G3 gate (priority 2 given); about 6 card-hours in all, within the
   G3 allotment of 60 (about 6 used).
