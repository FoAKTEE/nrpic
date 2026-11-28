# C-sidm G2: what stays open after the gate

State at the end of the lead session of batch 35 (2026-11-28 UTC). **Gate G2 is signed, pass with
reservations** (coord/GATES.md, 2026-11-27; decision 0048 item 1; independent review
`GATE_REVIEW.md`, fresh verifier `VERIFIER.md`). Every checklist item is PASS. This file lists
what the gate leaves open and where each item now goes.

## The stage check's one failed item: two conductivity runs

`nrpic-stage verify --full` (VERIFY_RESULTS.md, 2026-11-27T10:40Z, 9199 outputs and 1184.70 GB
re-hashed) fails only on `runs`, for two card runs:

| Run | What is missing | Why |
|---|---|---|
| heat_C1 C-20261121-210524-36a658e | 120 intermediate snapshots `heat.part.00001-00015.bin` listed in its sha256sums.txt; 8 case directories gained case.json, reduced.npz, summary.json | the reduction runs C-20261124-130338-43b5ffa and -c4ac85e (`heat/scripts/run_mode.py reduce`) wrote into the card run directories and `heatlib.SnapReducer` deleted every snapshot but the first and last |
| heat_C2 C-20261122-183030-2f3a471 | 45 snapshots; 3 case directories changed | same |

Bearing: only the conductivity kappa/kappa_1 = 1.020 +- 0.004 (series C-20261124-131012-f920f45;
G1 reservation 1) and C6. Remedy under way (decision 0048 item 1): both runs again on the release
card build of core-v0.8, queue entries **q0092 (heat_C1r) and q0093 (heat_C2r)**, priority 2, with
predictions HR.0-HR.5 written first (JOURNAL 2026-11-28T01:59Z). The reduction now writes into its
own run directory and deletes nothing (`run_mode.py reduce --out`, commit of 2026-11-28). Reading
them: close each with `nrpic-run finish`, check sacct shows COMPLETED, reduce each into a registered
run of its own, then `longruns/scripts/heat_series.py` on the two reduction run ids. The two old
runs stay on record with their failed checksum item (no waiver requested).

## The verifier's requests (VERIFIER.md, README "Requests") and what was done

| | Request | Done in batch 35 |
|---|---|---|
| (a) | "BA.3 failed" is wrong | BA.3 held (it predicted that A.4 stays failed); corrected in CHECKLIST C1, C19 and here; A.4 is the failure on record |
| (b) | state the count test per member and window | CHECKLIST C8 now gives each member over (0, t_c]: D2f2s1 1.00080 (z +0.27), D2f2s2 0.99414 (-1.95), D2f1s1 0.99816 (-0.61), D2f4s1 0.98995 (-3.34), M16 0.99827 (-0.56), D2eta1 0.98847 (-3.83); four of six pass, two fall short by about one per cent (VERIFIER.md section 4) |
| (c) | stale risk that A334s3c ends at 0.25 M | RISKS.md 25 corrected: its rerun reaches 600 M, marker crossing 563.29 M (VERIFIER.md X.3) |
| (d) | the M/4 seed-2 collisional run is broken after its first excision | on record in CHECKLIST C19 (alpha_min -2.7e8, 335 non-finite rows; t_c read before) |
| (e) | the gauge leg changes the shift damping only | stated in the note (Sec. V B) and below |

Runs the verifier suggests to turn "consistent" into "shown" (a second N4c seed; N6c continued to
about 900 M against the predicted crossing near 830 M): not queued in this batch; they are listed
in scope/SCOPE_G3.md section 9 as optional, after the first step.

## Corrections of the gate review (GATE_REVIEW.md section 8)

- VERIFIER.md copied to stage/G2/ where the stage tool reads it (C14); C18 judged PASS.
- Full-pass VERIFY_RESULTS committed (987d33c03); the two heat runs named above.
- EVIDENCE.md rewritten to the final state; STAGE_REPORT.md regenerated.
- Note: the compared value is the first maximum of the binding energy of arXiv:2009.08163
  (paper.tex:952-958), whose authors reject the turning-point principle (paper.tex:969-972);
  "the location of the threshold is [converged]" replaced by what is shown; the control
  collapses are "a finite-particle-number effect"; the gauge leg varies the shift damping only.
- scope/SCOPE.md G2 clause amended with the date (decision 0048 item 1).
- Still owed: the constraint histories of the bracket legs in a package figure (they are in the
  reviewer's `scratch/C-sidm/C-20261127-232854-8859b86/fig_review_check.png`, right panel); the
  schematic `schem_ladder.png` still says "turning-point model" in two labels. Both need a
  registered note run; they go with the next note run.

## Reservations carried to G3 (coord/GATES.md) and where each is answered

| Reservation | Answered by (scope/SCOPE_G3.md) |
|---|---|
| monoenergetic and King b = 0.1 families not run | section 2, first step: brackets at N = 1e6 on two meshes, finder, three seeds near the threshold |
| gauge leg could hardly fail (shift damping only) | section 6: slicing leg (harmonic against 1+log) and domain leg (outer face 512 M against 1024 M), each able to fail |
| one seed per member | section 2 and 5: three seeds for every member next to a threshold |
| collapse time not converged (13.6 per cent between meshes) | section 6: three meshes for the science members; times quoted as envelopes, no order claimed from two |
| collapse is a lapse marker; no finder | section 3: a collapse is a found horizon (core-v0.8 finder, shear flow, polishing, diagnostics) |
| constraint floor is deposit noise and rises when the core is refined at fixed N | section 6: mesh legs at fixed particles per cell |
| only the pairwise budget closes; count test short by one per cent in two members | section 7: whole-system budget with the measured collisionless drift; count test per member with its window |
| conductivity runs not re-verifiable | q0092, q0093 above |
| control collapses shown only as a finite-N effect | section 9 (optional runs) |
