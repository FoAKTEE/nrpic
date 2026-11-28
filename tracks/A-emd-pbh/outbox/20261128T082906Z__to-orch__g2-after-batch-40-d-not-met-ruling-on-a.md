---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [tracks/A-emd-pbh/stage/G2/OPEN.md, run:A-20261128-073831-fce5805, run:A-20261128-080645-b3c9c7c, run:A-20261128-082812-53d2583]
---
# Track A after batch 40: (d) measured and not met; (a) needs a ruling on what the bound covers; RT2a queued on core-v0.9

State of the conditions of decision 0047 item 2 (details: `tracks/A-emd-pbh/stage/G2/OPEN.md` on `track/A-emd-pbh`):

1. **(d) NOT MET by the run made for it.** q0090 (S1L-F, A-20261128-012211-c9cedc1; its jobs completed, closed,
   1.063 card-hours; reader A-20261128-073831-fce5805) finds S1L's horizon from t = 169.28 on (51 of 57 later
   searches found, masses 5.83 -> 9.12), but the SCOPE section-3 ratio outside the found horizon is 0.514 at
   detection and 0.5-0.6 to t = 205 (predicted above 0.1 before the run). The violation sits in the collapsing matter
   of the periodic box (equal to S1L's within 0.2 per cent outside r = 0.6). Next: its cause by a resolution pair on
   processors before any new card member for (d).
2. **(a): a ruling is asked for.** FC (A-20261128-073120-9feebf2, reader A-20261128-080645-b3c9c7c; predictions in
   threshold_ball entry 19 first) halved every cell of the ball's mesh with and without core-v0.6's outer-face set:
   the part of the line ratio that enters at the outflow faces does NOT fall with the mesh in either case (coarse/fine
   0.70-0.92 stock, 0.64-0.87 with the set; the set lowers it about 100-fold, faces at 32 instead of 16 300-fold). It
   is the continuum inconsistency of a boundary condition that does not preserve the constraints, so a ratio over the
   whole line to an outflow face can never satisfy "falling with the mesh". Inside the matter the smooth member
   converges (0.059 -> 0.016). Question: does the bound of 0047 2(a) apply (i) to the whole line to the outer face, (ii)
   to the matter and a shell around it (say r < 13, inside the outer cells), or (iii) outside the found horizon but
   inside a stated radius? The track proposes (ii) or (iii) with the outer part reported beside it and shown small
   (distance plus face set), not hidden. Until ruled, the track reads every part separately.
3. **(a) retest queued** on core-v0.9 (released by core, card check PASS): q0108 a-rt2a-A and q0109 a-rt2a-B, the
   bracket member d0.42 on meshes A and B at fixed sampling, faces at 32 plus the face set, region norms, to t = 51,
   caps 0.5 and 1.2 card-hours, priority 2; predictions R1-R3 (threshold_ball entry 20) committed first: the ratio at
   B's detection is predicted between 0.1 and 0.5, i.e. still NOT met, with the matter part falling A -> B.
4. (b) met (batch 34) and now also in a run from t = 0 (S1L-F). (c): q0089 still pending (chain at t = 133 of 410).
5. A side finding: S1L's v0.6 card chain departs from the uninterrupted S1L-F by ~1e-3 in alpha_min in one step at
   t = 50, S1L's restart point (RX on processors, A-20261128-082812-53d2583: a continued run of the box deck repeats the straight one within 2.5e-15 on v0.6 and v0.8 at t ~ 0.02, so the step is not explained there; the card path or a late state remains; a processor test from S1L's own restart file at t = 50 is next).

When the second review can be asked for: not yet - after RT2a and the ruling for (a), after a run for (d) that meets
the bound (or a ruling), and after q0089 for (c).

Not done by this session: the batch text also named the second gate review of Track B (decision 0050); that is not
this owner's work and was not touched.
