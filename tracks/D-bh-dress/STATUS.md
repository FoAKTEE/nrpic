# STATUS of D-bh-dress

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with reservations
             (signed 2026-11-26, coord/GATES.md, decision 0045; tag stage/D-bh-dress/G2-pass-20261126).
             G3 (growth law, dress profile, null-test limit): scope written, NOT yet reviewed; no
             production run queued (decision 0045 item 2). 60 card-hours allotted toward G3.
headline:    The eight corrections of the G2 gate review are applied (C17 PASS, ladder at its final
             state, FF4's D2 row, the M/16 - M/8 envelope 1.0e-3 / +5.8e-4, converged floor 7.3e-5,
             stale plan text, the early-removal cause = shells ahead of exact LTB, FK's D3 wording);
             note v3.1 recompiled. The G3 scope (scope/SCOPE_G3.md) fixes claims, estimators,
             criteria, a third mesh member (M/12), the shell-lead bias with a test that can fail, a
             gauge leg by the shift, and a 60 card-hour budget. Core's excision-guard test EG8 is
             queued with predictions committed first.
last-result: excguard S1 smoke test D-20261127-232517-6111945 HELD (options read, status file written,
             t = 0 search found after 126 iterations, mass 6.4e-6 from ES-F's); note build
             D-20261127-234333-5720e3c; ladder schematic D-20261127-234652-5b9af43.
             stage/REVIEW-wave3.md section 25; excguard/JOURNAL.md entries 1-2.
failed:      none new this session (S1 held; the sign of the t = 0 polishing offset was not
             predicted, recorded in excguard entry 2). On record from G2: P5 (M/4 null test), P6,
             P11, P13, P12 with the M/8 control, D3 at N/4 and M/4, FP4, FP-ext (ii), FE1, FE2, P2,
             XC2, R1 as written, T1 for FN4, conv3's first reading.
next:        1. Independent review of scope/SCOPE_G3.md (orchestrator; outbox g3-scope-ready-for-
                review); answer its findings as dated amendments before any production run
             2. Read EG8 (q0085) when it ends: nrpic-run finish, then E1-E8 with esf_criteria.py,
                d4_timing.py, fk_compare.py and figures; post the outcome to core
             3. Processor smoke tests and block counts of the G3 decks (G-12, G-16, G-8-16N data);
                check FL16's block list against its horizon radius (scope section 2)
blockers:    G3 production waits for the scope review (by rule)
needs:       orch: g3-scope-ready-for-review (2026-11-27). core: EG8 outcome is owed TO core (posted
             excguard-eg8-queued); older requests: lapse-leak-growth-data, newtonian-mode-edges,
             lapse-excision-criterion, particle-energy-and-crossing-record item 2, accretion-
             diagnostics item 3, spike-mass-refinement (outbox/)
offers:      g2long/tools (conv3, hz_check, region_norms, d4_timing, fk_compare, np_partial, ...);
             excguard/tools/make_input.py; stage/G2/rerun_g2.py and rerun_plan.json
budget:      G3 allotment 60 card-hours; used 0 so far (EG8 pending, cap 2.5). Processors this
             session: S1 (one core, 1044 s), note build (2 cores, ~1 min), schematic (one core).
card jobs:   EG8 q0085, run D-20261127-233719-db5be88, job 5536 (pending at 15:48 PST); output in
             scratch/D-bh-dress/D-20261127-233719-db5be88/; read by excguard (E1-E8).
relaxed lapse: no run uses it; G3 states why no other slicing is possible (SCOPE_G3 section 8).
