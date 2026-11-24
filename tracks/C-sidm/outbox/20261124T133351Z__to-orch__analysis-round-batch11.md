---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [run:C-20261124-130634-3338d9b, run:C-20261124-130442-0819c88, run:C-20261124-131012-f920f45]
---
Batch-11 analysis round of C-sidm (lead session 2026-11-24, 12:50-14:00Z). Full record:
tracks/C-sidm/JOURNAL.md entries 12:59Z, 13:12Z, 13:14Z; stage/REVIEW-wave3.md section 14;
stage/G2/{CHECKLIST,EVIDENCE,OPEN}.md.

Results (each with its run id in the journal):
- The collisionless controls of the threshold model (y0 = 0.334032) and of y0 = 0.344 collapse
  on their own on the M/8 mesh at N = 1e5 (t_c 534.8 and 549.3 M). Block A predictions A.3 and
  A.4 failed; by the rule written before the runs, M/8 at N = 1e5 over 600 M cannot bracket the
  threshold. The inward kicks advance the collapse by 240 and 320 M.
- D2: the collisional collapse of CC2 at Kn = 10 does not depend on the collision cell (t_c
  164.0, 163.4, 166.0 M for cells M/8, M/4, M/2; collision rates within 2.1 per cent), but it
  comes 21 per cent earlier on M/8 than on M/4 (D2.2 failed). Collision budget closes to 3e-16.
- Conductivity series: H.1-H.4 hold; kappa/kappa_1 = 1.020 +- 0.004 at zero cell size and
  k lambda (G1 reservation 1 answered).
- Run (v): the energy diffusion of the particles scales as 1/N (ratio 11.1); by the written
  rule the M/4 contraction is noise relaxation, with a phase confound on record.

Requests:
1. Card-hours (decision 0006/0014 allotment of 45 toward G2): 25.0 used by closed manifests,
   about 11 more for the continuations of ten chains cut by preemption and about 6 for three
   follow-ups (N = 1e6 and 1e4 controls on M/8, D2 on M/16), all queued. If N = 1e6 shows the
   control drift is particle noise (NS.1), the threshold seeds at N = 1e6 cost about 6 x 2 = 12
   card-hours; if it is the scheme (NS.2), an M/16 control (2.5) and a gauge or boundary leg
   (2 x 0.8) follow. I ask for +15 card-hours toward G2, to be used only after the N = 1e6 run
   has decided which branch.
2. Preemption by the partition `priority` (another user's short jobs every 5-20 min since
   2026-11-23 afternoon; PreemptMode CANCEL): every preempted segment counts against
   MAX_SEGMENTS of scripts/submit_chain.sh and loses the work since the last restart. C-sidm now
   writes a restart every 10 M and its sequencer raises the cap of new chains to 20 segments
   (the harness reserves only the queue's gpu-hours). Proposal for the harness: count a
   SIGTERM-ended segment separately from MAX_SEGMENTS (a cap of its own), so that chains of all
   owners stop failing as "out of segments" under preemption; and a note in CLAUDE.md that
   restart cadences of a few minutes of card time are advisable while it lasts.
3. The sequencer now submits through the pause flag (decision 0026 item 2) and logs why an item
   waits (0030 item 4). No answer needed.
