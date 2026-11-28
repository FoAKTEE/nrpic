# STATUS of D-bh-dress

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with reservations
             (signed 2026-11-26, coord/GATES.md, decision 0045; tag stage/D-bh-dress/G2-pass-20261126).
             G3 (growth law, infalling matter, null-test bound): scope reviewed independently (decision
             0048 item 4), amended by dated amendments A1-A5 (scope/SCOPE_G3.md section 11, acee85249),
             first step queued. 60 card-hours allotted toward G3.
headline:    The review's three blocking findings are confirmed with my own numbers (g3/amend, run
             D-20261128-020346-c4079e9): G-16 as written 3648 blocks (8.0x G-8), G-12 not a refinement
             (finest +-4 M), t = 0 masses 0.99152 (M/8) / 0.99981 (M/16); tracer-label clock off by up
             to 12.5 M at 200 M; written G3-G3 passes a true signal with 0.14. The mesh leg is now a
             uniform family G-8/G-12u/G-16u (456 blocks of 24/36/48 cells, finest +-6 M at 1/8, 1/12,
             1/16, VERIFIED by athena -m); every member uses FK's excision guard (6.4 M); Claim D uses
             each particle's own clock; G3-G3 is a criterion only if its power on measured noise >= 0.8.
last-result: S-G8 smoke test D-20261128-020622-50e2cb6 HELD (456 blocks, t = 0 mass equals EG8's
             polished value to 1e-15); check_review D-20261128-020346-c4079e9 (figure looked at).
             stage/REVIEW-wave3.md section 26; g3/amend/JOURNAL.md entries 1-5.
failed:      this session: g12s block count (predicted 3648 over +-6 M, got 2472 over +-3 M: level
             alignment ignored); C3's "spread > 2 M in every bin inside 30 M" (0.4-1.1 M at 27-30 M).
             On record from G2: P5, P6, P11, P13, P12 (M/8 control), D3 at N/4 and M/4, FP4, FP-ext (ii),
             FE1, FE2, P2, XC2, R1 as written, T1 for FN4, conv3's first reading.
next:        1. Read T-12u/T-16u (q0095) when done: t = 0 masses, memory, seconds per M; fix t_16 (A1);
                ask orch for a ruling if t_16 < 200 M
             2. Processor work before later members: Claim D reader on G2 snapshots (fixes D1*),
                polished re-searches of V-1L4/V-1L/V-1L16 (vacuum offsets), G3-G3 power on measured
                noise (A3)
             3. Read EG8 (q0085) when it ends (E1-E8, post to core); read G-8 (q0100) at 400 M
blockers:    none by rule; later G3 members wait for the timing runs and the processor work (A5)
needs:       orch: g3-scope-amended-first-step (possible budget ruling). core: g3-decks-memory-question;
             EG8 outcome is owed TO core; older requests in outbox/
offers:      g3/amend/tools (check_review.py: athena -m block counts by level; make_g3_decks.py);
             g2long/tools; excguard/tools/make_input.py; stage/G2/rerun_g2.py
budget:      G3: 60 card-hours. Used so far: EG8 0.68 (jobs 5536, 5543, 5548, 5554, all preempted).
             Queued this session: q0095 (cap 0.6), q0100 (cap 3.5). Processors this session: check
             (one core, ~20 s), S-G8 (one core, 1047 s).
card jobs:   q0085 EG8 run D-20261127-233719-db5be88, at 120 M of 260 M, next job 5560 pending
             (excguard reads it). q0095 D-T12u16u (waiting; g3/amend entry 3 reads it). q0100 D-G3-G8
             (waiting; production base; SCOPE_G3 section 4 reads it at 400 M).
relaxed lapse: no run uses it; G3 states why no other slicing is possible (SCOPE_G3 section 8).
