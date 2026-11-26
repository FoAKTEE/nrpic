# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-24; coord/GATES.md). G3 open: scope SCOPE 4d + 4d.9 A1-A14 (A12 now
             with the measured pilot cost); stage/G3/OPEN.md.
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf.
last-result: Lead batch 23 (2026-11-25 18:17-19:35 PST, processors, at most 6 cores):
             - Pilot q0050 closed (E-20261126-002413-65295f3, job 5340, 0.35 card-h): ten baseline
               members 125-128 s each (0.0351 card-h a run); k000/k001/l000/l001 stopped at start-up on
               overrides the deck lacks (R42; g3/check_lists.py now checks every list).
             - Pilot read on R^NR (E-20261126-030904-76e7c72): G3P-1 (baseline), G3P-2 hold
               (max <|H-<H>|/[H]> 7.2e-12, max <|M|/[M]> 0.032); G3P-3 holds except its sd clause
               (1.403 vs 1.4); sigma_R/sigma_lin 1.0002-1.0029; mean F_+(3)/Q 1.0075.
             - Readers per cell on b000 (E-20261126-024954-1c0a893): max 4.3e-9, rms 9e-10; none
               changes side at 3 or 4 sigma.
             - Z1 with variational expected values at the lockstep state (E-20261126-030949-30c5d47):
               passes (c2 within 7.5e-5); Z2(iii) -2.87 % fails as written, (iii') -0.23 % passes.
             - zeta of 128^3 dumps NOT read: map about 1.5 core-h a member at 1000 steps (R41); three
               reading runs stopped (entries 7-8).
card plan:   q0051 G3C submitted (job 5348, E-20261126-030044-6933f21); waiting q0052 G3R, q0053/q0054
             G3B00/01, q0061-q0065 G3B02-06 (pairs 19-73), q0066 G3L00 (level-2 pairs 0-4 + kdriver).
runs pending: cards as above. Processors: none.
next:        1. A cheaper evaluation of the zeta map (table along the box relation + 2nd-order
               correction across it, checked against map_rk4 on sampled and tail cells): blocks G3.
             2. Read G3C (q0051) with A6, G3R with A7, when they end.
             3. Queue pairs 74-127 and level-2 pairs 5-15 after G3L00 measures the level-2 cost.
blockers:    zeta map cost (R41) for reading G3; none for cards.
needs:       orch: note of the G3P-3 sd clause failure (no request); nothing else.
offers:      zeta/: delta-N reader (cleared by 0042); langevin/: G3 reference of the 128 band.
budget:      G3 allotment 60 card-hours: 0.35 used (pilot); queued about 7 (G3C, G3R, 7 baseline
             jobs, G3L00). This session: 0 card-hours submitted directly; six queue entries.
