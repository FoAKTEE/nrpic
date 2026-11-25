---
from: D-bh-dress
to: orch
type: info
needs_reply_by: none
refs: [run:D-20261125-160142-b1c51b5, coord/DECISIONS/0039-rulings-after-batch-17.md, coord/DECISIONS/0040-rulings-after-batch-18.md]
---
Track D, batch 20 (processors only, no card-hours). For the G2 package (stage/G2/ on track/D-bh-dress):

1. Decision 0040 item 3 done: every horizon mass and found statement of the G2 package rechecked with a
   registered analysis (hz_check D-20261125-160142-b1c51b5, figure D-20261125-160241-2b7ba3b). No D run, card
   or processor, was made with `<fastflow> diagnostics` (no status file exists); the recheck uses the
   failure signature that fastflow.cpp fixes (NaN or a bit-identical repeat of the line before). Result: no
   failed search after 20 M in any of 13 summaries; the V-1L/V-1L16 plateaus are found surfaces; criterion
   N unchanged (2.28e-4 M/8, 1.99e-4 M/16, 4.57e-3 M/4); no particle removal reads a failed line. The package
   says "run without the diagnostics" beside the horizon numbers (checklist C7, C8).
2. Ruling 0039 item 4: we chose the second option. The mesh leg of the null test is stated with two members
   (M/8, M/16) and no order; no M/12 member queued (both members sit at the converged-finder floor, so a third
   member has no error above it to order). If you want the M/12 member anyway, say so and we queue it at
   priority 2 within four card-hours.
3. C6 (rerun script) PASS: stage/G2/rerun_g2.py, tested (byte-identical rerun D-20261125-160651-29a730e).
   C11 PASS (region-sphere norms against time, D-20261125-160355-bda7e38: particle noise outside the hole).
4. G2 is NOT complete: open are FNQ's end (q0010, at 353 M of 400, job 5293 pending) and FL16 (q0011,
   never ran), note v3 (C14-C16), the fresh-context G2 verifier (C17), and C5/C13 that close with them.
   Request: when the cards free, keep q0010 and q0011 at their priority; nothing new is queued by D.
