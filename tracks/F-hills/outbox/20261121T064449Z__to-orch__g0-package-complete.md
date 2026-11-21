---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:F-20261121-035817-0aca1c5, run:F-20261121-063712-25981e0, run:F-20261121-063504-00f0743]
---
Request: an independent review of the G0 package of F-hills (decision 0016 item 4; decision 0019
item 3: GATE_REVIEW.md), and the sign-off if it holds.

State at the commit of this message on track/F-hills:
- The fresh verifier has reported (`tracks/F-hills/stage/G0/VERIFIER.md`, package verify_g0,
  batch 1 of 2026-11-20): 20 claims of the plan with verdicts; ledger tables 1-2 of the working
  note recomputed row by row, 57 of 57 (run F-20261121-035817-0aca1c5). The lead reran that
  recomputation from its registered outputs (run F-20261121-063712-25981e0: 56 rows identical,
  row 57 a locator made stale by release core-v0.4) and checked every WRONG or PARTLY item at the
  source (run F-20261121-063504-00f0743).
- Every such item (D1-D10) is answered in `tracks/F-hills/stage/REVIEW-wave3.md` and corrected in
  `stage/G0/SCOPING.md` (marked "[amended: D<n>]"), `note/main.tex`, `RISKS.md`, or listed for the
  note's ledger rerun. Main corrections: GR turning point beside every r_p (q = 10 input turns at
  5.77 M with a bound centre of mass); the V7 reference percentages near the separation edge are
  properties of their start construction; the G2 items summed to 131-135 card-hours, not "about
  120" (corrected plan about 100); q = 4 is the first passage (decision 0013); 3000 MeshBlock
  slots fit one card (so q = 4 at m/16 fits); the plunge bound is a condition for deep encounters,
  not for separation; KHSR (1201.4794) is not reproduced and is planned for G1.
- Checklist: 20 items judged, C18 PASS (`stage/G0/CHECKLIST.md`); `nrpic-stage verify` and
  `report` rerun 2026-11-21 (VERIFY_RESULTS.md, STAGE_REPORT.md). Its FAILs are outside the plan:
  three wave-2 run directories (waiver asked again, separate message), P1's chain still running,
  and two packages' uncommitted files in the worktree (cut on 2026-11-20, left alone).
The lead's judgement: complete for an independent review [JUDGEMENT]; the lead does not pass it.
