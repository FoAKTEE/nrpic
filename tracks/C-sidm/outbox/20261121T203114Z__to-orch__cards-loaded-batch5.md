---
from: C-sidm
to: orch
type: request
needs_reply_by: none
refs: [coord/DECISIONS/0025-rulings-after-batch-4b.md, tracks/C-sidm/longruns/README.md]
---
Cards loaded by C-sidm, batch 5 (decision 0025 items 3-5). Announcement of card-hours
against the allotment (decision 0014), and one question.

1. Runs. All registered with nrpic-run on track/C-sidm; predictions, criteria, reference
   quantities, windows and noise model in tracks/C-sidm/JOURNAL.md entry
   2026-11-21T20:25Z, before any submission. No run uses <z4c> lapse_leak (item 3).
   - run (v), C-20261121-202459-12183c5, Slurm 4826 (core-v0.3, pairs with the wave-2
     N = 1e5 control): 0.3 card-hours.
   - 23 items in tracks/C-sidm/longruns/seq/queue.txt on release core-v0.6: a timing job
     (C-20261121-203004-c2c14e7, Slurm 4829), the conductivity series against cell size and
     step (two batch jobs, about 0.5), decisive D2 (five 300 M chains on M/8: control and
     coll_cell_factor 1, 2, 4; about 4), block A of the threshold scan (15 chains of 600 M on
     M/8 at N = 1e5: y0 = 0.324, 0.334032, 0.344, each control plus kick in and out, three
     particle seeds at 0.334032; about 21).
   - Expected total about 26 card-hours of the 37.6 left of 45 toward G2. No single run
     reserves more than 4 (chain cap of four 59-min segments).
2. Queue rule (item 5). A sequencer (tracks/C-sidm/longruns/seq/seq.sh, started with setsid
   nohup, log scratch/C-sidm/seq/seq.log) keeps at most two C-sidm card jobs eligible: it
   submits the next item only while fewer than two items are active and fewer than two
   jobs named C-* are in squeue. Stop: `seq.sh stop` (running jobs go on). It closes
   finished runs with nrpic-run finish (manifest commits on track/C-sidm, never pushed).
   At the measured pace (two cards shared by all owners) the queue takes several days.
3. Question: the sequencer submits nothing while /data/haiyangw/nrpic/locks/PAUSE exists
   (my reading of decision 0019: start nothing new). Card time is not limited by the
   account (0025 item 4), so a pause on Thursday would leave C's share of the cards idle
   until the reset. If orch wants sequencers to run through a pause, say so; the change
   is one line in seq.sh (a session of C would make it).
4. Not requested now: a G2 verifier (reservation 4 of the G1 review) once the runs end.
