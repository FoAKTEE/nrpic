---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [run:A-20261128-004659-f512816, run:A-20261128-011908-0e41713, run:A-20261128-005331-874ec88]
---
# Track A, batch 34, follow-up: condition (a) - the non-converging part of the ball's constraint ratio is named (outer faces)

Follows g2-conditions-after-batch-34. Three processor tests ended after it (threshold_ball JOURNAL entry 18, predictions
written before each run):
- OB (A-20261128-004659-f512816): moving the outflow faces from 16 to 32 cuts the outermost-cell part of the SCOPE
  section-3 line ratio 300-fold at t = 1-2, matter and edge parts unchanged: the part that does not converge with the
  mesh enters at the outer faces [VERIFIED by a run that could have failed].
- FR (A-20261128-011908-0e41713): core-v0.6's outer-face set at faces 16 cuts it 70-100-fold to t = 2.
- LF (A-20261128-005331-874ec88): a level face inside the matter keeps the interior residual 2.4x higher at t = 2
  (prediction refuted); core's deposit fixes at faces are the matching retest.
Condition (a) stays OPEN: the bound must still be met at detection (t ~ 45) in smooth CIC bracket members on two
meshes; the plan (face set + faces at 32 + deposit-fix build) is in stage/G2/OPEN.md. No card run for it is queued yet
(it waits for the processor retest with the deposit-fix build).
