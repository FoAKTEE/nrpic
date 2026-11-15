---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-20
refs: [run:D-bh-dress-20261115-121314-284ec4f, athenak/src/outputs/restart.cpp]
---
Minor. When a chained run stops at the wall-clock limit, the extra restart file it writes
goes through the ordinary writer, which advances the output's `last_time` by dt
(athenak/src/outputs/restart.cpp:193-201), so the next scheduled dump is skipped: in
Track D's M/16 run D-bh-dress-20261115-121314-284ec4f the dump at t = 300 M was never
written. Request: write the final restart without advancing `last_time`. Acceptance: a
two-segment chain writes every scheduled dump.
