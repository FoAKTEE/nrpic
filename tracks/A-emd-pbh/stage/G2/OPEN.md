# What G2 of A-emd-pbh still lacks (lead of batch 31, 2026-11-26 evening)

Gate G2 was NOT passed on the independent review (coord/GATES.md; decision 0047; GATE_REVIEW.md). Decision 0047
item 2 sets five conditions for the next review, each through a run that could have failed. Their state:

| condition (0047 item 2) | state after batch 31 | what remains | serves it |
|---|---|---|---|
| (a) cause of the constraint floor shown; section-3 ratio < 0.1 at detection in ball members at the bracket, falling with the mesh at fixed particles per cell; retest after core's deposit fixes, run to the horizon | OPEN. Batch 31: C3-F (entry 16, A-20261126-234222-dbf8624): no first-step jump, the early rise is the t = 0 momentum residual and converges; C3-G (entry 17, A-20261126-235005-d58354f): with the gauge frozen and particles at rest the floor stays (line ratio 0.21 at t = 1), so neither gauge dynamics nor motion across cells makes it | a member without level faces in the matter (frozen gauge, processors), prediction first; core's two deposit fixes at level faces (source session after 2026-11-27); then B-d0.42/B-d0.40 (or smoothed CIC twins) on two meshes to the horizon, prediction first | core, then cards |
| (b) finder finds the trapped surface on the restart files of the periodic chain and the triaxial run, no false acceptance | PARTLY MET on processors (FP, FPb: A-20261126-233542-fd9f9f0, A-20261126-234232-84f3e98): P0L6 t = 140 found with 4000 flow iterations (m 6.30, r 0.104; line 6.28 at 0.103); S1L t = 220 found from 0.16 in 1927 iterations (m 10.73, r 0.161) but not from 0.1, 0.2, 0.6 in 4000; nothing accepted where no round sphere is trapped (P0L6 t = 130) | the false acceptance of P0L6 at t = 118.1 is not retested (no restart file there); a deck rule that finds S1L's horizon from the deck's start radius; core's answer on the flow's convergence (outbox finder-slow-convergence-box) | core; then a deck change in G3 |
| (c) cause of the lag of the triaxial crossing named within the first-order class | OPEN | a run that could refute a named effect (gate review section 5 item 3) | processors or cards |
| (d) one triaxial phase-1 run to a found horizon with the bound met | OPEN (the horizon of S1L is found on its restart file at t = 220; the bound of section 3 is met nowhere) | follows from (a) and (b) | cards |
| (e) corrections of text and figures (review section 6, second verifier) | DONE in batch 31 (note main.tex V.A-V.D, VI, Summary; Fig. 7(a) ticks; Table V orders as ranges and the same-cell signal named; READMEs; CHECKLIST C9, C18, C21-C23; EVIDENCE header; this file); note run A-20261126-234358-f761d8d, compiled | | |

The track's own G2 criteria of SCOPE section 7 are in CHECKLIST C21-C23 (open): A1 and A3 with three-way
convergence (A3 fails), the horizon-mass error (passes with reservation), one triaxial run to horizon formation with
the bound (fails).

Failed criteria that stay failed on record: C3, A2, C1 (ii) horizon part of the card run; earlier T4, T5, T6, K, K2,
K3, F1, F2, G, AZ1 (both clauses: the 5 per cent clause and the first clause, periodic_threshold outcome AZ1), D2-D4,
A2X's bound, P17's lapse clause on N128/N256, P18 for N256 at tau 10 and at tau 40 (better than predicted), P21 at
tau 20, H's t = 0 clause. Batch 31: FP4 refuted for P0L6 (the finder works with more iterations), FP6 refuted (S1L's
first trapped round sphere is earlier than 190).

No threshold amplitude of this track is compared with arXiv:2609.14218 before condition (c) is closed (0047 item 3).
