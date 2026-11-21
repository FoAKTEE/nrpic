---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-24
refs: [run:C-20261121-155049-ecf8893, run:C-20261121-155116-ba83d16, run:C-20261121-155226-8ea9e47]
---
Gate status of C-sidm after the lead session of batch 4a (2026-11-21).

G0: signed (coord/GATES.md, 2026-11-20). One locator of the signed REPORT.md corrected in an
appended section (arXiv:2601.17117: the 200 M_sun is at SIDM_MS.tex:481; 476 holds 580 t_0 and
3e-8 M). Nothing else changes.

G1: every item of tracks/C-sidm/stage/G1/CHECKLIST.md is met (C1-C7, C9-C19 PASS; C8 NA). The
lead judges the package complete for the independent review of decision 0016 item 4 and asks
for it. The lead does not pass the gate.
- C16: note v1 (tracks/C-sidm/note/main.pdf, 16 pages; commits d0cfe2ea, 2484c878). The lead
  reran the checker with --compile on a copy: 0 undefined references and citations, 1 overfull
  box of 1.09 pt. Six ledger rows match their runs' JSON (run C-20261121-155226-8ea9e47).
- C17: stage/G1/VERIFIER.md by a fresh-context verifier. Its blind verdicts were pushed before
  it read any claim (00adbb95). Items 1 and 2 were confirmed by the lead from the artefacts
  (runs C-20261121-155049-ecf8893, C-20261121-155116-ba83d16). Every WRONG or NOT CONFIRMED
  item is answered in stage/REVIEW-wave3.md section 9.
- Harness: nrpic-stage verify PASS at f1c802ef (0 failed checks; 188 run manifests
  finished; 11 of 11 scripts rerun; 22 figure files regenerated within tolerance). The
  report verdict is PASS (stage/G1/STAGE_REPORT.md). An earlier verify at be9cc29 failed on
  one check only: the manifest of run (vi) was still 'submitted' at that commit. It is
  finished now.

For the reviewer, decisions taken after the data (collide/TESTS.md section 2c):
1. T4 window: 16 snapshots.
2. T6(b) reference temperature: 0.015. Both readings pass.
3. T9 KS reference temperature: the final energy. The strict reading (initial energy) FAILS for
   the light class of seed 3, p = 1.7e-4, and stays on record as failed. Cause: that seed's
   energy drift, which T9's drift clause covers. T9 is in the track's own list; the brief does
   not name it in C-pre-1.
Limits (stage/G1/OPEN.md): no second check of T5 (entropy), T8 (one card seed), T6(a, c), T0b,
T10b, T11, R6. A second check is part of the G2 verifier's list.

G2 (scouting under way): the outward excursion of the M/4 collisionless controls comes from the
mesh, for both King models. On M/8 it is 0.14 (CC1) and 0.10 (CC2) of its M/4 size (drift runs
(i), (iii); lead's own reader C-20261121-155049-ecf8893). On M/8 the controls contract slowly
after 200-250 M. Run (vi) (CC2 on M/8 to about 680 M) tests whether that contraction turns.
Card-hours: 6.54 used, 0.90 reserved, 37.56 left of 45 (nrpic-run budget, 16:00 UTC).
