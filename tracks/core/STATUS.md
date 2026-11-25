# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (open level-3 chains); C7 = C1; C12 no REVIEW.md/SCOPE.md).
             Batch 14 (2026-11-25T02:12-03:12Z): release candidate core-v0.7.
headline:    RELEASE CANDIDATE core-v0.7 at source commit 5f75e5b9, REGRESSION PASS
             (tracks/core/RELEASE-v0.7.md). Four branches merged on top of core-v0.6, one
             merge commit each, no conflict: core/noise-level2 (level 2 of the stochastic
             backreaction, R on the mesh), core/step-limit (<z4c> dt_gauge; restart
             outputs on SIGTERM; chain script), core/gauge-2 (<z4c> lapse_leak_hole, a
             MITIGATION), core/clump-table (table clusters with momentum). core/oblate
             left out. Executables published: scratch/core/exe/core_nrpic_v07/.
last-result: byte regression against core-v0.6, twelve set-ups, new options absent: 75 of
             75 items identical (core-20261125-023046-30aba6c; MPI build
             core-20261125-023646-eca713c); no file differs because of the changes that
             act without an option. Quick tests PASS (core-20261125-023641-7a1c47d: 65 of
             65 files identical with the branch executables, SIGTERM S1 and S2, chain
             script, two combinations). Threaded build not a byte reference (32 of 75,
             rounding level; core-20261125-030151-8c0c306). clump-table's card check M2
             judged: held (core-20261125-021225-382dbc7).
pending:     card runs in the shared queue (none waited for):
             q0039 core-v07-card   card check K7 of the merged card executable (22
                                   cases, 0.3 card-hours); commands that judge it in
                                   RELEASE-v0.7.md, section "Card checks pending"
             q0035 nl2-review-R5   card run of the reviewed level-2 build (its package)
             q0036 step-limit-card card smoke run of the step-limit build (its package)
             q0029-q0033           row 4 level 3 (HANDOFF.md; q0028 done, not finished)
next:        1. when q0039 has run: finish it, card_v07.py, card_v06.py, card_v05.py;
                write the result into RELEASE-v0.7.md, READY and OPEN.md item i
             2. row 4 level 3: finish the chains, row4_fate.py (HANDOFF.md)
             3. after the tag: release builds against the candidate (regress_v04.py)
blockers:    none
needs:       orch (release clerk): merge core/nrpic, tag core-v0.7, release builds,
             interface documents, announcement (outbox 20261125T030800Z); older: outbox
             20261121T233031Z (interface corrections), 20261121T204332Z (waiver lines)
offers:      scratch/core/exe/core_nrpic_v07/ with READY (an example input per new
             option); tracks/core/CHANGELOG.md section core-v0.7; OPEN.md section
             core-v0.7 (restart defects a, b; mitigation status c; level 2 limits d)
budget:      G2 card-hours: used 15.76, reserved 2.07, left 22.17 of 40 (nrpic-run
             budget, 2026-11-25T03:07Z); this session used no card; q0039 asks 0.3
