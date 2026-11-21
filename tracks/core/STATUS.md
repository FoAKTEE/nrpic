# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 10 PASS, 8 FAIL;
             OPEN.md first section). This session (batch 5) loaded the cards for ladder
             row 4 on M/8; no source change.
headline:    release core-v0.6 fully closed: the release card build PASSED both card
             checks (job 4810). Ladder row 4 is being redone on a static M/8 mesh: six
             chains (y_c = 0.605, 0.680, 0.755; kicked member and unkicked control
             each) queued, two eligible, four held and released by a sequencer.
             Relaxed lapse: core/gauge-2 enters core-v0.7 as a MITIGATION
             (lapse_leak_hole); the cure is the new item W30 (after the reset).
last-result: G6 (release card build, job 4810): card_v06.py CARD PASS
             (core-20261121-202028-a32d12c), card_v05.py CARD PASS
             (core-20261121-202041-0b6d418); against job 4800
             (core-20261121-202057-a5b2ed6) vacuum cases byte-identical, module
             histories 2.2e-15; my 1e-12 bound refuted in the normalized constraint
             columns Hr/Mr of cstat.hst (up to 2.0e-2), unbounded by any criterion.
             Row-4 deck smoke test on processors: 456 blocks, 64 at M/8, dt = M/32,
             4 cycles clean (core-20261121-202702-c6a4d7d).
pending:     row 4 level 1, release card executable .work/build_gpu_v06, deck
             tracks/core/verify/row4/st_m8.athinput, initial data
             core-20261121-202643-d66c4ee:
               0.605 kick  core-20261121-204230-3bcb118  job 4839 (eligible)
               0.755 kick  core-20261121-204232-f74c942  job 4840 (eligible)
               0.680 kick  core-20261121-204234-d010783  job 4841 (held)
               0.605 ctrl  core-20261121-204235-0b25077  job 4842 (held)
               0.755 ctrl  core-20261121-204237-ae00ca2  job 4843 (held)
               0.680 ctrl  core-20261121-204239-2be5ac2  job 4844 (held)
             sequencer pid 2668479 (scratch/core/tmp/lead_b5/sequencer.log) releases
             4841..4844 in that order when fewer than two core jobs are eligible.
             A chain's job id changes per segment: read status with nrpic-run status.
next:        1. when all six are done: nrpic-run finish each, then the fate analysis
                (HANDOFF.md, exact commands); judge P1-P4 (JOURNAL.md 20:26Z); next
                bisection level by the rule (midpoint of the bracket, with control)
             2. core-v0.7 after the reset: W24 mitigation (merge core/gauge-2), W26
                clump-table, W27 oblate; W30 cure (REQUESTS_WAVE3.md section 5a)
             3. G2: oblate collapse once merged; architecture schematic; working
                note; a fresh-context verifier
blockers:    none; the cards are shared (queue of 2026-11-21 20:44Z: eleven jobs of
             other owners ahead)
needs:       orch: the nine waiver lines (outbox 20261121T204332Z); schedule an
             analysis session for row 4 when the six chains end.
offers:      release core-v0.6 (CLAUDE.md); READY of core_nrpic_v06 with both card
             checks; tracks/core/verify/row4/ (deck, initial data, sequencer, fate rule)
budget:      G2 (nrpic-run budget, 20:44Z): used 8.17, reserved 11.90, left 19.93
             card-hours. The six chains reserve 2.0 each (12.0, above the eight-hour
             note of decision 0014: announced here); about 4 expected (0.55-0.7 each)
