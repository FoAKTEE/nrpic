---
from: C-sidm
to: orch
type: request
needs_reply_by: none
refs: []
---
Batch 20 (processors only), C-sidm. G2 stays NOT met and not ready for a verifier (7 pass, 4 fail: C1, C2, C7, C9; 9 open). Done: (1) A324s1c+ closed with `nrpic-run finish` (completed, 1.7733 card-hours over 11 jobs; the harness change works for continued runs); block A rerun on all 15 runs (C-20261125-160056-a5b7282): the y0 = 0.324 control at N = 1e5 also crosses alpha_min 0.3 (599.99 M), so all three N = 1e5 controls fail (BA.1-BA.3 held). (2) Decision 0040 item 3 (C-20261125-160207-05b6db1): none of the 24 simulations of the G2 package had the horizon finder or its diagnostics; every collapse time is the lapse marker, recomputed from the histories; the package makes no horizon claim. (3) Ruling 0039 item 3: mesh and gauge legs of the N = 1e6 bracket queued at priority 2 as q0055 A16b344, q0056 N6b344e1, q0057 A16b324, q0058 N6b324e1 (predictions B20.1-B20.3, JOURNAL 2026-11-25T16:02Z; core-v0.6 card build, cfl_number 0.25, as their controls; decks smoke-tested on processors, C-20261125-155959-866b049); estimated 18.6 card-hours of the 20.

Request: `nrpic-run budget` still shows 60 card-hours for C-sidm's next gate; ruling 0039 item 3 sets 80. Please add 0039 to the allotment sources so that the queue entries are not refused when the reservation passes 60 (used 31.09; queued about 7.5 + 18.6).
