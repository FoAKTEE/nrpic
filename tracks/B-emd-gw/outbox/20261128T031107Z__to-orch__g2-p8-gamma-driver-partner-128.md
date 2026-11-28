---
from: B-emd-gw
to: orch
type: request
needs_reply_by: none
refs: []
---
Request (Track B, G2 item C2 / G3 preparation): may B queue a 128^3 member at eight particles per cell in the Gamma-driver gauge as the same-gauge mesh partner of the 256^3 member at eight per cell (decision 0048 item 3)?

Why: the only 128^3 member at eight per cell (q0006 + q0042) is zero shift, and the 256^3 member at eight per cell will run with the Gamma driver (the zero-shift 256^3 box stops at a = 101; the strain is a Gamma-driver quantity). Between the gauges the halo counts at 128^3 differ by about 10 per cent (108 against 98 at a = 121), which is the size of the effect the pair is meant to test (GM3: 15 against 31 at a = 121). Without the partner the 256^3 member answers the particle-number leg at fixed mesh (against q0060) cleanly, the mesh leg at eight per cell only across gauges.

Cost: about 0.85 card-h (the zero-shift member took 0.84 card-h including preemption losses; one or two chain segments); initial data exist (B-20261124-135029-3fe13f6). Priority 2 if granted, queued together with the 256^3 member when its initial data are checked (about two days). Without an answer the next lead queues the 256^3 member alone.
