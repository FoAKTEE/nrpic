---
from: D-bh-dress
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [run:D-20261124-134157-b17938b, run:D-20261124-130942-29c5de2, run:D-20261124-131050-ed0a535]
---
Track D asks for 12 more card-hours toward G2 (decision 0014: requests above eight card-hours are
announced; this one exceeds what is left).

State (nrpic-run budget, 2026-11-24 05:17 PST): G2 used 16.86, reserved 8.85 (three chains resumed
after the preemptions of 2026-11-23, counted at their ceilings; expected use about 2), left 4.29 of
the allotment of 30.

What the results call for (g2long JOURNAL entry 10, predictions committed in fdca9208 before any
of these runs): the scope's relaxation control at G2 ("capture rate and spike profile unchanged
between N and 4N", scope/SCOPE.md section 5) and the gate's three-way convergence in particle number
need ES-FLK at 4N and N/4 beside ES-FLK at N (FK, running); the growth comparison has two meshes and
needs ES-FL at M/16 as the third. Inputs, data runs and processor smoke tests are done.

| Run | Cap | Expected |
|---|---|---|
| FN4 ES-FLK4N (4N, 400 M) | 4.0 | 2.8 (registered now, within what is left) |
| FNQ ES-FLKQ (N/4, 400 M) | 3.0 | 1.9 (waits for allotment) |
| FL16 ES-FL16 (M/16, 300 M) | 5.0 | 3.5 (waits for allotment) |

Smallest acceptable answer: raise D's G2 allotment by 8 card-hours (FNQ and FL16 at their caps) or
say which of the two to drop. The sequencer keeps at most two D jobs eligible (decision 0025 item 5).
