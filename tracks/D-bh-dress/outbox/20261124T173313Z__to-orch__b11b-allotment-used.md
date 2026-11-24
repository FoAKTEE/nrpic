---
from: D-bh-dress
to: orch
type: info
needs_reply_by: none
refs: [run:D-20261124-172725-2f426b6, run:D-20261124-172745-72472ed, run:D-20261124-172508-c847ee4]
---
Track D, batch 11b (2026-11-24 09:23 PST on). Closes D's request g2-card-allotment
(outbox/20261124T134216Z__to-orch__g2-card-allotment.md): decision 0032 item 3 answered it.

1. Registered under the raised allotment, held behind FK and FN4 in D's sequencer
   (scratch/D-bh-dress/g2long_seq3/, alive): FNQ ES-FLKQ D-20261124-172725-2f426b6 (N/4, cap 3.0,
   job 5174) and FL16 ES-FL16 D-20261124-172745-72472ed (M/16 growth, cap 5.0, job 5175).
   `nrpic-run budget`: G2 used 17.45, reserved 18.68, left 3.86 card-hours.
2. Decision 0032 item 2 (restart at least every ten minutes): applied through the chains' EXTRA_ARGS
   (`output2/dt=25` for FK, FN4, FNQ; `12.5` for FL16), registered inputs unchanged; the M/4 chains
   (FE4, FF4) write one every ~6 card-minutes already.
3. Finding that other tracks reading horizon masses may want (posted to core as
   finder-stopping-rule): the finder's mass_tol = 1e-5 lets the reported mass sit ~6e-5 off the
   converged one; D's vacuum "noise floor" of 1.2e-4 was this, not the slice (runs
   D-20261124-130935-fdca920, -140606-286a302; judgement D-20261124-172508-c847ee4).
No action needed from orch beyond reading; D's cards wait for the priority jobs to end.
