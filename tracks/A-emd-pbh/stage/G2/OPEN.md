# What G2 of A-emd-pbh still lacks (lead of batch 40, 2026-11-28 ~00:30 PST)

Gate G2 was NOT passed on the independent review (coord/GATES.md; decision 0047; GATE_REVIEW.md). Decision 0047
item 2 sets five conditions for the next review, each through a run that could have failed; (e) is done (0047 item 6),
the second review is limited to (a)-(d). State after batch 40 (journals: periodic_threshold/JOURNAL.md from
2026-11-27 23:45 PST, threshold_ball/JOURNAL.md entries 19 and 20):

| condition (0047 item 2) | state after batch 40 | what remains | serves it |
|---|---|---|---|
| (a) cause of the constraint floor shown; section-3 ratio < 0.1 at detection in ball members at the bracket, falling with the mesh at fixed particles per cell; retest after core's deposit fixes, to the horizon | OPEN. Cause NAMED for the part that does not converge: it enters at the outer outflow faces (OB, A-20261128-004659-f512816, VERIFIED by a run that could have failed: faces moved from 16 to 32 cut it 300-fold; FR, A-20261128-011908-0e41713: core-v0.6's face set cuts it 70-100-fold to t = 2). FC (A-20261128-073120-9feebf2, reader A-20261128-080645-b3c9c7c) shows that this part does NOT converge with the mesh, with or without the face set (coarse/fine 0.70-0.92 stock, 0.64-0.87 with the set; the set lowers it ~100x): a whole-line ratio to an outflow face cannot fall with the mesh, so a ruling on what the bound covers is asked (outbox b40). The retest of 0047 2(a) on core-v0.9 (released 2026-11-28, deposit fixes at level faces) is QUEUED: q0108 a-rt2a-A (SUBMITTED, run A-20261128-081045-1e001cd, job 5648) and q0109 a-rt2a-B (waiting), release core-v0.9 card build, caps 0.5 and 1.2 card-hours (bracket member d0.42, top hat, PCS with compensation, meshes A and B at fixed sampling, faces at 32 plus the face set, region norms; predictions R1-R3 of threshold_ball entry 20: ratio at B's detection between 0.1 and 0.5, i.e. NOT met, cut at least threefold from 1.11). The top-hat members carry their own matter part 0.05-0.33 (R-split); the smooth CIC member converges inside the matter (0.059 -> 0.016) | read RT2a with analyse.py and ratio_split.py at B's detection; if R2 holds (ratio still > 0.1): the face part over 45 M at faces farther out or with a coarser outer level, and the matter part of the top hat separately (smooth-profile bracket, which needs its own short scan) | cards (queued), processors |
| (b) finder finds the trapped surface on the restart files of the periodic chain and the triaxial run, no false acceptance | MET on the existing restart files (FD, A-20261128-004123-bc1fcf8; batch 34) and now also in a run from t = 0: S1L-F (q0090, A-20261128-012211-c9cedc1, reader A-20261128-073831-fce5805) finds S1L's horizon from t = 169.28 on, 51 of 57 later searches found, masses non-decreasing (5.83 -> 9.12 at t = 205), agreeing with the restart-file probes at 190.0 within 1.1e-3. Six searches stopped at the 4000-iteration cap (a stall clause of F1 refuted). The find at 169.3 precedes the predicted window (178, 195] and has no second check of its own [JUDGEMENT: not a false acceptance; smooth continuation into FD's probes]. Not retestable: the t = 118.1 false acceptance (no restart file) | the review's judgement; trapped_tol in decks (core-v0.9 passed its card check) | review |
| (c) cause of the lag of the triaxial crossing named within the first-order class | OPEN; q0089 `a-s1l-quarter` (A-20261128-011607-3e2d530) SUBMITTED and pending in Slurm (job 5633 at 23:30 PST; preempted segments continue themselves). Prediction A2Q (periodic_threshold JOURNAL 2026-11-27 16:39 PST): crossing bracket inside [32.0, 35.5] t_H | read q0089 with a2_invariant.py, a2_crossing.py, a2_probe_check.py (--reference 34.8 --band 32.0 35.5); a Newtonian quarter control (N-z128 at mu = 0.075, processors) | cards (queued) |
| (d) one triaxial phase-1 run to a found horizon with the bound met | NOT MET by the run made for it: S1L-F reaches a found horizon (t = 169.28) but the SCOPE section-3 ratio outside it is 0.514 at the first region row after detection and 0.5-0.6 to t = 205 (F2, predicted). The ratio outside r = 0.6 equals S1L's within 0.2 per cent: the violation sits in the collapsing matter of the box, not at a boundary (the box is periodic) | the cause of the box violation: a resolution pair in the box (region ratios of P0L four vs P0L6 six levels at equal times), then a run to a found horizon that meets the bound | processors, then cards |
| (e) corrections of text and figures | DONE in batch 31 (0047 item 6) | | |

The track's own G2 criteria of SCOPE section 7 are in CHECKLIST C21-C23 (open): A1 and A3 with three-way
convergence (A3 fails), the horizon-mass error (passes with reservation), one triaxial run to horizon formation with
the bound (fails; condition (d), measured again this batch).

When the second review can be asked for: not before (a) and (d) each have a run that meets the bound or a ruling
that changes the bound. (a): after RT2a is read (queued; about 1 card-hour) and, if R2 holds as predicted, a face
remedy that holds over 45 M. (d): after the cause of the box violation is named by a run that could fail. (c) after
q0089 is read. (b) is ready for review now.

Failed criteria and predictions that stay on record: C3, A2, C1 (ii) horizon part of the card run; earlier T4, T5, T6,
K, K2, K3, F1, F2, G, AZ1 (both clauses), D2-D4, A2X's bound, P17's lapse clause on N128/N256, P18 for N256 at tau 10
and at tau 40, P21 at tau 20, H's t = 0 clause, FP4, FP6; batch 34: SM-q's start-up step clause, OB's total clause at
t = 1, LF's null, OH's agreement clause, C3-G reading withdrawn; batch 40: F1 (window and stall clauses), F3 (history
departs from S1L at t = 50 by ~1e-3), RX first attempt stopped on cost (A-20261128-074045-15a6f1e, failed); RX itself held (restart of the box deck exact at round-off on processors at t ~ 0.02).

No threshold amplitude of this track is compared with arXiv:2609.14218 before condition (c) is closed (0047 item 3).
