# C-sidm G1: what the gate still lacks

State at the end of the lead session of batch 4a (2026-11-21). Verdict of the lead: every item
of the checklist is met (C1-C7, C9-C19 PASS; C8 not applicable to G1). The lead judges the
package complete for the independent review of decision 0016 item 4 and asks for it; the lead
does not pass the gate. Nothing below blocks that review in the lead's judgement; each item is
a stated limit for the reviewer.

1. Readings named after the data (`collide/TESTS.md` section 2c, from the verifier's
   `VERIFIER.md` section 2): the T4 fit window (16 snapshots), the T6(b) reference temperature
   (both readings pass) and the T9 KS reference temperature (final energy). The strict T9
   reading (initial energy) FAILS for the light class of seed 3 (p = 1.7e-4; cause: that seed's
   energy drift, +4.8e-3 in theta) and stays on record. T9 is in the track's own list, not among
   the tests the brief names in C-pre-1. For the reviewer to accept or refuse.
2. No second check of: T5 (entropy; needs an estimator with a bias study), T8 and T6(a, c),
   T0b, T10b, T11, R6; T8 rests on one card seed; T7 on the card was recomputed by the lead
   only from the per-seed values. These are the limits of C6 and C17.
3. Minor gaps of the track's own extra tests (not blocking): T10b for the T4 statistics (one
   short card job); the MPI variant of T10 (collisions stop on more than one rank, core accepted
   the port without a date); T3-T5, T9, T11 not repeated with `coll_energy = particle`.
4. Reservations carried to G2: the zero-cell-size conductivity at theta 0.003 may lie 1-3
   percent below the relativistic Chapman-Enskog value of V1a (itself checked by no second
   agent); growth rates on runs are defined only with their fitting interval; the note's v1
   ledger rows for card T7 at theta 0.1 and 1 and most growth-fit rows have no second check.
