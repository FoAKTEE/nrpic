# What G2 of A-emd-pbh still lacks (lead of batch 41, 2026-11-28 ~08:30 PST)

Gate G2 was NOT passed on the independent review (coord/GATES.md; decision 0047; GATE_REVIEW.md). Decision 0047
item 2 sets the conditions for the next review, each through a run that could have failed; (e) is done (0047 item
6), the second review is limited to (a)-(d). Decision 0051 item 4 (2026-11-28) rules on (a): the bound of 0.1 is read
as written, over the whole exterior the run has, at detection; the part inside must fall with the mesh at fixed
sampling, the part at the outer faces with the distance of the faces and the face options. Journals:
threshold_ball/JOURNAL.md entries 19-21, periodic_threshold/JOURNAL.md from "2026-11-27 23:45 PST".

## State of the conditions

| condition (0047 item 2) | state after batch 41 | met? | what it still needs |
|---|---|---|---|
| (a) cause of the constraint floor shown; section-3 ratio < 0.1 at detection in ball members at the bracket, falling with the mesh at fixed particles per cell; retest after core's deposit fixes, to the horizon | Cause NAMED for the part that does not converge with the mesh: it enters at the outer outflow faces (OB A-20261128-004659-f512816, FR A-20261128-011908-0e41713, FC A-20261128-073120-9feebf2). Retest RT2a on release core-v0.9 (faces at 32 + core-v0.6 face set + region norms, bracket member d0.42): mesh A done (q0108, A-20261128-081045-1e001cd; reader A-20261128-160831-6fd1da1). The face set cuts the outer-face part 6-7x over 45 M on mesh A (RA1). At the first region row that holds a found horizon (t = 46.0) the ratio over the exterior is 0.907 (inner 0.890, middle 0.085, outer 0.150): 95 per cent of ||16 pi E|| lies inside the horizon, so the exterior ratio divides by the E of the few particles outside. Mesh A has no persistent detection (5 finds) and stops at the guard at 48.14 (deterministic: GA, below). Mesh B (q0109) waits in the shared queue. | NOT MET | q0109 (B-F) read with rt2a_read.py and analyse.py at its detection: the inner part must fall from 0.89 toward 0.1 (a factor ~9: B then C at second order); the outer part (0.0071 of the whole-box E at faces 32 + set) must fall below ~0.0047 of it: a domain leg with faces at 64 (or a coarser outer level), prediction first |
| (b) finder finds the trapped surface on the restart files of the periodic chain and the triaxial run, no false acceptance | Found on the existing restart files (FD, A-20261128-004123-bc1fcf8) and in a run from t = 0 (S1L-F, A-20261128-012211-c9cedc1: from t = 169.28, 51 of 57 later searches, masses non-decreasing, agreeing with the restart-file probes at 190.0 within 1.1e-3). The t = 118.1 false acceptance has no restart file (not retestable). | MET (on what can be tested) | the review's judgement |
| (c) cause of the lag of the triaxial crossing named within the class the half-amplitude run narrowed (first order in the amplitude) | A2Q (q0089, A-20261128-011607-3e2d530; readers A-20261128-160444-e6c646e, -160447-c41d66a, -160446-6c171f3) HOLDS: S1L-q crosses first along z at the centre in (34.77, 35.28] t_H, inside the predicted [32.0, 35.5]; no horizon; lapse 0.964. The lag is first order in the amplitude over a factor 4 (c = ln lag_a / zeta_max: 1.06-1.57, 1.45, 1.45-1.78 at zeta 0.296, 0.148, 0.074); an amplitude-independent delay is excluded (<= 0.03 in ln a); the gradient-expansion factor e^(-2 zeta) (c = 2) is REFUTED; the data's psi^4 factor (c ~ 1.15) is disfavoured (no refutation was written for it). Not separated, as written before the run: the nonlinear zeta-delta relation of the data from a relativistic (aH/k)^2 correction of the same order, or from a numerical error first order in zeta. | PARTLY: the class is confirmed and its coefficient measured; the cause WITHIN the class is not named | a run that separates the data's relation from the dynamics (written next session, prediction first); the Newtonian quarter control N-z128 at mu = 0.075 (processors, ~2 h) to replace the scaled Newtonian premise by a measurement; or a ruling that the measured first-order coefficient is what "named within the class" asks |
| (d) one triaxial phase-1 run to a found horizon with the bound met | S1L-F reaches a found horizon (t = 169.28) but the section-3 ratio outside it is 0.514 at detection and 0.5-0.6 to t = 205 (F2). The box is periodic: no outer faces; the ratio outside r = 0.6 equals S1L's within 0.2 per cent. | NOT MET | the cause of the box violation by a run that could fail (region ratios of P0L four levels against P0L6 six levels at equal times, processors, existing files), then a member that meets the bound |
| (e) corrections of text and figures | done in batch 31 (0047 item 6) | MET | |

GA (A-20261128-160727-0d75d4e): the RT2a-A guard stop repeats on the v0.9 threaded processor build from the t = 48.0
restart file at t = 48.140625, cycle 3081, MeshBlock 31 (level 4) at (-0.4375, -0.4375, -1.4375), 317832 non-finite
values, as on the card: inside the collapsing matter, not at the faces; the same cell as the v0.6 stop at 47.92.
A 9-cycle processor reproducer for core (`threshold_ball/scripts/ga_repro.sh`). It does not block (a): the reading
time 45.875 lies before it, and mesh A is the coarse member.

The track's own G2 criteria of SCOPE section 7 are in CHECKLIST C21-C23 (open): A1 and A3 with three-way
convergence (A3 fails), the horizon-mass error (passes with reservation), one triaxial run to horizon formation with
the bound (fails; condition (d)).

## When the second review can be asked for

Not yet. (a) needs B-F read (q0109) and, if its inner part is still above 0.1 as expected on two meshes, mesh C or
a ruling; its outer part needs the domain leg. (d) needs the cause of the box violation and a member that meets the
bound. (c) needs a discriminating run or a ruling. (b) is ready. The orchestrator gets one line when (a), (c) and
(d) each have their run.

Failed criteria and predictions that stay on record: C3, A2, C1 (ii) horizon part of the card run; earlier T4, T5, T6,
K, K2, K3, F1, F2, G, AZ1 (both clauses), D2-D4, A2X's bound, P17's lapse clause on N128/N256, P18 for N256 at tau 10
and at tau 40, P21 at tau 20, H's t = 0 clause, FP4, FP6; batch 34: SM-q's start-up step clause, OB's total clause at
t = 1, LF's null, OH's agreement clause, C3-G reading withdrawn; batch 40: F1 (window and stall clauses), F3, RX first
attempt; batch 41: RA2 at t = 45.75 (interior part 1.59x lower on v0.9 than on v0.6, bound 1.5); run q0108 FAILED at
the guard (t = 48.14, mesh A, reproduced).

No threshold amplitude of this track is compared with arXiv:2609.14218 before condition (c) is closed (0047 item 3).
