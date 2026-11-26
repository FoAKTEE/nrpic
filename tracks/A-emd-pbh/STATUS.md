# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 package assembled in
             batch 28 (stage/G2): every run ruled for in 0043 item 1 has ended and is judged; what remains open is
             the failures on record with their rulings (C3, A2, horizon part of C1 (ii)) and the fresh verifier of the
             whole gate (C18). Szekeres P24 judged (entry 14); its tau 30/40 rows are not yet in the note's Table V.
headline:    A2H holds: at half amplitude the triaxial peak first crosses in (13.85, 14.36] t_H, inside the band of
             a lag first order in the amplitude (A-20261126-213147-f274b2e). The C3 floor is not particle sampling
             (x8 particles: same floor, A-20261126-212340-4ea9fb2); its cause is unexplained.
last-result: batch 28 (13:19-14:30 PST; processors only):
             - q0068 S1L-h (A-20261126-125306-0653547, 1.18 card-h): A2H HOLDS; no horizon; alpha_min 0.92 at crossing.
             - q0067 Szekeres N256 to tau 40 (A-20261125-231808-0784bc9): finite (P17 completion holds); lapse drifts
               3.6e-12 by round-off (P17's lapse clause refuted on N128, N256). Readers: orders 2.3-5.2 at tau 10-20,
               P19, P20 hold; P18 refuted for N256 (better); P21 refuted at tau 20 (szekeres entry 13).
             - C3 particle leg (A-20261126-024922-97a2f14): H holds for t = 1-2, t = 0 clause refuted (x9.6).
             - Note v2: Sec. "Verification of the code paths", Figs. ladder/convergence/mosaic, Table V; runs
               A-20261126-213903-08eaf25, A-20261126-214059-b32377a; compiled, checker clean (dictionary hints only).
             - stage/G2: CHECKLIST 17 PASS, 2 FAIL (C1, C3), 1 OPEN (C18); RERUN.md, VERIFY, OPEN.md; verify + report.
cards:       none submitted this session; ended entries used 1.18 (q0068) and 0.76 (q0067 segment 2) card-hours.
             Shared queue: nothing of A waiting.
processors:  nothing running. Readers A-20261126-212138-49b9a2d, A-20261126-212141-7eeb046 closed: P24 holds at tau 40
             (0.041), refuted at tau 30 (0.00365, better than [0.004, 0.04]); P20 holds to tau 30 (szekeres entry 14).
next:        1. Fresh verifier of the whole G2 gate (C18), asked of orch (outbox g2-package-batch-28).
             2. Note pass: Table V rows of szekeres entry 14 (tau 30/40), registered run_all, compile, checker.
             3. After core's deposit fixes (source session after 2026-11-27): C3 retest S2c-A/S2c-B, prediction first.
blockers:    C3 FAILED (cause unexplained); C1 (ii) finder fails on P0L6 (core request open); A2 FAILED as written.
needs:       orch: verifier for G2; ruling that G2 is judged with C3, A2, C1 (ii)-horizon as failures on record.
             core: the two deposit fixes at level faces; the finder (finder-false-accept-and-stall-p0l6).
offers:      note/scripts/fig_slice_mosaic.py (plane reader of NRFIELD2 dumps), ledger_g2.py; a2 scripts with
             --band/--reference/--label; threshold_ball/scripts/edge_compare.py (any extra member drawn).
budget:      card-hours batch 28: 0 submitted. Processors: up to 5 cores, ~70 min.
