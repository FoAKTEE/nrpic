# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-24; coord/GATES.md). G3 open: scope SCOPE 4d + 4d.9 A1-A14;
             stage/G3/OPEN.md (baseline not yet run: 246 of 256 runs wait in or outside the queue).
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf.
last-result: Lead batch 27 (2026-11-26 03:44-04:55 PST, processors only, at most 6 cores):
             - G3C (q0051, E-20261126-030044-6933f21) and G3R (q0052, E-20261126-041110-0a78c93)
               closed (completed; 15.8 and about 21 card-minutes).
             - G3-C (4d.4 + A6) PASSES as written (E-20261126-115943-32970f2): model test at all
               ten dumps of cN [2.0, 6.6]; every judged factor within 8.4e-4 of 4 (H 8/5, M 8/6
               dumps); the 4c two-amplitude estimator leaves the band late (3.55-5.27): the G2 miss
               of U-A4'(a) is the floor estimator's.
             - G3-R (4d.5 + A7) PASSES as written (E-20261126-120438-9d48377): factor of max D^L
               3.12, median per-mode ratio 2.63, sign 100 % of 8538 modes; T changes 5.6e-4.
             - Zeta table map (g3/zeta_table.py): about 20 s a 128^3 member instead of 1.5 core-h
               (R41 closed). TB-1 FAILED as written (5.4e-9 vs bar 1e-10; E-20261126-115112-43da266);
               diagnostic (E-20261126-115925-a2c6da5) refutes both predicted causes: round-off of the
               double-precision map, about 1e-9 per cell, worse at 16000 steps. Rule of entry 12 met
               (verifier 3.9e-9 at b000; spot checks <= 5.9e-9 on all ten members).
             - Pilot zeta (E-20261126-120434-5dda273): P5-5 holds on every clause (skew 0.0200;
               skew(zeta) + skew(R) 0.0204-0.0208; A(3) 0.082; F_+(4)/Q 1.195, F_-(4)/Q 0.751);
               P5-3 FAILED as written (3.2-4.1e-9 vs 1e-9; the same round-off).
card plan:   waiting at low priority, not moved since batch 23: q0053/q0054 G3B00/01 (28 runs),
             q0061-q0065 G3B02-06 (110 runs), q0066 G3L00 (level-2 pairs 0-4 + kdriver records).
             Not yet queued: pairs 74-127 (108 runs), level-2 pairs 5-15.
runs pending: cards as above. Processors: none.
next:        1. When baseline jobs end: close, read R^NR and zeta per member (read_pilot.py
               --map table --msteps 4000), then the pair statistics (A5) and (V), (T), A4.
             2. Queue pairs 74-127 (five lists through check_lists.py) when the queue moves; level-2
               pairs 5-15 after G3L00 measures the level-2 cost.
             3. sigma = 0.1 coarse-graining bound of A10 (R39); package items C5-C17, fresh verifier.
blockers:    card queue order only (G3 needs about 10.6 card-hours; requests_to_orch).
needs:       orch: priority for the G3 baseline entries; note of TB-1/P5-3 failures (no ruling needed).
offers:      g3/zeta_table.py (fast delta-N reader on a box); langevin/: G3 reference of the 128 band.
budget:      G3 allotment 60 card-hours: 0.96 used (pilot 0.35, G3C 0.26, G3R 0.35); queued about
             5.5 (G3B00-06, G3L00). This session: no card submission, no queue entry.
