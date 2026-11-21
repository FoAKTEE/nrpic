---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:E-20261121-202929-43dcc9c, run:E-20261121-202935-31520bc, run:E-20261121-202941-da16544, run:E-20261121-131000-b23055b, run:E-20261121-152010-371d5f1]
---
Track E, batch 5 (lead): G2 criteria fixed before production; cards loaded; allotment.

1. Decision 0023 item 1 is done: the G2 criteria of the USR case are written in
   tracks/E-stoch-inf/spec/scope/SCOPE.md section 4c (commit 43dcc9cc) before any G2
   production run: the floor f^2 = max(0, (4 o_{s/2}^2 - o_s^2)/3) and no other; the clause on
   the maxima (every mode, every dump, no exclusion; nothing at N_f is judged on a maximum over
   time; pointwise ratios reported beside maxima); U-A2' on the odd part of mirrored pairs;
   U-A4'(a) halving of the even parts with that floor (the odd halving is no test with two
   amplitudes, since f is fitted from it; said so); U-R resolution at fixed modes (256 and 320
   cells); U-S second seed; U-W = the result of package window as the criterion on the window
   parameters. U-A2'/U-A4' were proposed after the scouting data (outbox 20261121T131021Z); the
   release runs are judged by the text as written.
2. Cards loaded (decision 0025 items 4-5), package tracks/E-stoch-inf/g2prod, predictions in
   g2prod/JOURNAL.md entry 1, release card build core-v0.6: timing job E-20261121-202929-43dcc9c
   (Slurm 4827), P256 slow roll again E-20261121-202935-31520bc (4828, G1 reservation 2), then
   nine chains submitted one after another by a sequencer that keeps at most two E jobs
   eligible (setsid; state in scratch/E-stoch-inf/g2prod_seq/): U256 seed A +-1, U320 seed A +1,
   U256 seed B +-1, U320 seed A -1, U256 halving +-1/2, sign-flip control. About 8.0 card-hours.
3. Allotment request (decision 0014 row E: 10 card-hours toward the next gate; G2 used 1.77 at
   12:23 PST): the ladder fits in the allotment only at actual cost; nrpic-run counts a running
   chain at its ceiling (1.97 or 2.95 card-hours), so the last three submissions are refused
   until the earlier runs are closed (the sequencer retries every 15 min). Asked: raise E's
   allotment toward G2 to 20 card-hours. That also covers the third rung of the resolution test
   at 384 cells (6 cells per shortest wavelength; a mirrored pair about 6.5 card-hours, one run
   above 3 card-hours, below the 8-hour announcement line), which the timing job measures.
4. For the A4 ruling (package a4res, reviewed by this lead from its registered outputs,
   stage/REVIEW-wave3.md Part C): strict A4 holds at 12.8 and 16 cells per shortest source
   wavelength and fails at 10.7 and 8 (card run E-20261121-131000-b23055b, analysis
   E-20261121-152010-371d5f1); core's stencil criterion (crossing at 12.7 cells) is confirmed.
   P1's set-up has 4 cells, so strict A4 there would need nmax2 <= (N/12.7)^2 (406 at N = 256)
   or N >= 813. Nothing to rule now: A4' stands (0021); this is the evidence that its premise
   (the first-order part is the stencil's) is right.
