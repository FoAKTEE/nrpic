# G3 of Track E: what is open (batch 27, 2026-11-26 early morning)

G3 is not ready for review. Scope: spec/scope/SCOPE.md 4d with 4d.9 A1-A14 (A12 carries the measured pilot cost).
Definition of "G3 met": A13.

Done (each with its registered run; g3/JOURNAL.md entries 9 and 13; stage/REVIEW-wave3.md parts J and K):
- Reference proper (A1, A9, A10 except the sigma = 0.1 bound), zeta reader cleared (Z0, Z1 variational, Z2(i), Z2(iii');
  decision 0042 item 1).
- G3-C (4d.4 with A6): PASSES as written (E-20261126-115943-32970f2): every judged factor within 8.4e-4 of 4, model test
  at all ten dumps of the range, each factor and constraint judged at five or more dumps.
- G3-R (4d.5 with A7): PASSES as written (E-20261126-120438-9d48377): factor 3.12, median ratio 2.63, sign 100 per cent.
- Zeta at 128^3 is now cheap (R41 closed): the table map on 4000-step nodes (g3/zeta_table.py) under the rule of entry 12,
  about 20 s a member (E-20261126-115112-43da266, E-20261126-115925-a2c6da5, E-20261126-120434-5dda273). TB-1 and P5-3
  stay FAILED as written (bars below the round-off of the double-precision map, about 1e-9).
- Pilot (E-20261126-002413-65295f3): G3P-1, G3P-2 hold; G3P-3 holds except its sd clause (1.403 against 1.4); P5-5 holds.

Open:
1. Baseline: 246 of the 256 runs (128 mirrored pairs) are not yet run. Queued at low priority and not moved since batch
   23: q0053, q0054 (G3B00/01, 28 runs), q0061-q0065 (G3B02-06, 110 runs). Not yet queued: pairs 74-127 (108 runs, about
   five jobs). About 8.6 card-hours in all at 0.0351 card-h a run.
2. Level 2 (4d.7 with A11, reported): 16 mirrored pairs; G3L00 (q0066, pairs 0-4 plus the kdriver records of A8) waits;
   pairs 5-15 after G3L00 measures the level-2 cost. About 2.0 card-hours.
3. Reading of the baseline: R^NR and zeta per member (read_pilot.py --map table --msteps 4000; about 1.5 minutes a member on
   one core, 6 core-hours for 256), then the pair statistics of A5 and the comparison (V), (T), A4 of A2/A4.
4. sigma = 0.1 coarse-graining bound of A10 not reached (R39).
5. Reservations carried: geodesic slicing only (A8); U-A4'(a) of G2 stays FAILED as written (answered by G3-C, which passes).
6. Package items (C5, C6, C9-C17): result figures, ledger, schematic, working-note section, and a fresh verifier who
   recomputes the statistic, G3-C and G3-R from the dumps and repeats the table check against the long-double map on a
   second member.
