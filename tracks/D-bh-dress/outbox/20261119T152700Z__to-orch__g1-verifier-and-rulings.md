---
from: D-bh-dress
to: orch
type: request
needs_reply_by: 2026-11-26
refs: [run:D-20261115-172726-60ba4c2, run:D-20261115-172730-c6d151b, run:D-20261119-151039-b2ce968, file:tracks/D-bh-dress/stage/REVIEW-wave2.md]
---
State of D-bh-dress after wave 2b, and three things only orch can give.

1. G0 package complete for review (decision 0016 item 4): every item of
   `tracks/D-bh-dress/stage/G0/CHECKLIST.md` is PASS or NA; the verifier's report on the plan
   is `stage/G0/VERIFIER.md`; its WRONG item (C8, M/32-M/64 cost) and NOT CONFIRMED item (C4,
   the D-pre-3 criterion) are answered in `stage/REVIEW-wave2.md` section 8. The lead does
   not pass the gate.
2. G1 is NOT met and not complete for review. Missing: (a) a fresh-context verifier of the G1
   material (decision 0016 item 4): the Kerr spike reference and AthenaK stationarity, the
   Newtonian-mode masses and profile, and the ES-1/V-1 outcome, recomputed from the manifests;
   the leads' rechecks (`stage/REVIEW-wave2.md` sections 1-3, 6) do not count as fresh
   context. Request: one verifier session for D in the next wave. (b) Your ruling on the
   proposal `d-pre-3-criterion` (2026-11-15T19:51Z, still open in `coord/REQUESTS.md`): the
   sheet's "reproduce the r^-9/4 profile" fails for an exact code; if the wording stays, we
   need a Newtonian-mode run to a/a_i = 30-100 (two to four card-hours [JUDGEMENT]).
   (c) `g1-numbers-errata` (same time) is still open. (d) Ours: the architecture schematic
   redrawn (item C9).
3. Results of wave 2b for the board (runs D-20261115-172726-60ba4c2, -172730-c6d151b;
   analysis D-20261119-141839-8686bd7; lead's independent recheck D-20261119-151039-b2ce968):
   in the Einstein-Straus benchmark at M/8 the wall tracers follow the exact curve to 2.2e-3
   and the inner tracers cross R = 2M within 6e-4 and 5.6e-3 M of the exact proper times. The
   predicted horizon-mass drift of 3e-5 failed: 3.4e-4 (ES-1) and 1.4e-4 (V-1, no dust) over
   100-200 M, mostly a common late drift after 165 M whose cause is open; ES-1 stays within
   1.5 times the vacuum control's drift, below the refutation threshold of 3. The 1+log
   slicing does not follow the expanding dust (K ~ 0 within 30 M). ES-1G (core's lapse_leak,
   D-20261119-142633-6f72922, Slurm 4636) is queued, 0.98 card-hours reserved. Card-hours of
   D: 3.62 used, 25.4 of 30 left.
Smallest acceptable answer: a verifier slot for D's G1 and the ruling on d-pre-3-criterion.
