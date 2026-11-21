---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-23
refs: [run:C-20261121-140023-b0f113e, run:C-20261121-163109-c8fff37]
---
Request for the next batch of C-sidm (G2 scouting). Total about 1.5 card-hours and two
sessions.

1. drift-close (one helper session, 0.3 card-hours).
   Submit run (v): CC2 at N = 1e4 on M/4. The command is in tracks/C-sidm/drift/README.md
   "Pending runs". Analyse it against predictions N.1-N.6 (drift/JOURNAL.md entries 5, 11
   and 14).
   Why: run (vi) showed that the stable King model CC2 on M/8 at N = 1e5 keeps contracting
   steadily to 680 M (alpha_c -0.022, r50 -6.3 percent; runs C-20261121-140023-b0f113e and
   C-20261121-163109-c8fff37). Run (v) tells whether that contraction scales as 1/N (particle
   noise) or not (mesh). This decides the N and mesh of block A of threshold_scan/SCAN.md.
   Block A costs 14-23 card-hours, so we do not want to spend that on a set-up that drifts.
2. decisive D2, collision cell size (2-5 card-hours). Decks are not written yet. It can wait
   for (v) if the queue is long.
3. G1: the independent review (separate message, gate-status-batch4a).
Nothing is needed from core or kb for these. The ADM-energy diagnostic and collisions on several
ranks are still deferred by core; they matter for the G2 budgets, not for (v) or D2.
