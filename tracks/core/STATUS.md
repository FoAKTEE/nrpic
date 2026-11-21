# STATUS of core

gate:        G2 NOT MET (package tracks/core/stage/G2/ brought to the state after
             core-v0.6 on 2026-11-21: CHECKLIST 18 items, 10 PASS, 8 FAIL; OPEN.md first
             section says what is missing; STAGE_REPORT.md from nrpic-stage report)
headline:    release core-v0.6 closed: the card check of the merged card executable
             PASSED (job 4800; prediction K6 held) and the release processor build of
             main is byte-identical with the candidate (75 of 75). The release card
             build waits in the queue (job 4810). Defect first for core-v0.7: the
             relaxed lapse (lapse_leak) grows a black hole's horizon mass in vacuum
             (decision 0022 item 3; Track D).
last-result: K6 judged in core-20261121-154700-2de4974 (Newtonian 1.6e-11 of
             processors, bound 1e-10; faces 1.9e-10, bound 1e-7; solver iterations
             equal) and core-20261121-154710-220c1b0 (K1-K6 of core-v0.5 held); R6:
             core-20261121-154737-dc1e4c1, 75/75 identical (figure
             core-20261121-155317-1ee04bf).
next:        1. job 4810 (run core-20261121-154654-d3ec487): finish, then card_v06.py,
                card_v05.py, card_pair.py (commands in RELEASE-v0.6.md, section
                "Release builds against the candidate"); judge against G6 (journal,
                entry of 15:46Z); write into RELEASE-v0.6.md and READY
             2. core-v0.7: W24 relaxed-lapse fix (test V-1GB to 5e-5), W26 clump-table
                (merge main, review, regress), W27 oblate (merge main, T1/T2 again,
                READY) (REQUESTS_WAVE3.md section 5)
             3. G2: ladder row 4 bisection on M/8 against a collisionless control;
                oblate collapse once merged; redraw the architecture schematic;
                working note; a fresh-context verifier
blockers:    none for the release; G2 rows 3-4 need card time (about 0.6 card-hours
             per M/8 cluster run to 300 M) and the oblate merge
needs:       orch: read the gate status (outbox of 2026-11-21, batch 4a); schedule a
             verifier and a note session for core when the ladder rows close.
             Track D: G2 null tests without lapse_leak until W24 is released.
offers:      release core-v0.6 (CLAUDE.md); scratch/core/exe/core_nrpic_v06/READY with
             the card check written in; release drivers tracks/core/analysis/release/
budget:      G2: 6.58 card-hours used by core, 0.40 reserved, 33.02 left (nrpic-run
             budget, 2026-11-21 15:55Z); job 4800 (asked in batch 3) used 46 s; this
             session asked 0.1 for job 4810
