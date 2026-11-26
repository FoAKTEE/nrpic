# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (open level-3 chains); C7 = C1; C12 no REVIEW.md/SCOPE.md).
             Batch 23 (2026-11-26T02:17-03:30Z): round without AthenaK source change.
headline:    core/restart-finder merged into core/nrpic (b755cdcf, no conflict, source =
             01d4aeeb); release core-v0.8 prepared on processors, waits for card check q0049.
             Track A's PCS residual at static level faces is the documented deposit rule,
             reproduced to 1.1e-15 by an independent emulation; found on the way: a defect
             of deposit_fine_shape with CIC at level faces (NEXT_SOURCE item 0) and a
             compensation that is not conservative across levels (item 0b). Row 4 level 3:
             bracket (0.7175, 0.726875) by the 300-M rule; every model to 0.73625 collapses
             by 421 M.
last-result: deposit test core-20261126-022953-21b8455 (D1-D3 hold, D4 failed in both
             parts, D5 holds in substance); row-4 fates core-20261126-023040-b755cdc (P10,
             P11, P12, P15 hold); diagnostics after a restart core-20261126-023323-c8fad52
             (F1: command line refused, `-i add.athinput` works); R8 byte regression
             core-20261126-024438-1fa17dd and Q8 restart_test core-20261126-024518-e1e16dc
             (outcomes in JOURNAL.md, last entry).
pending:     card runs in the shared queue, none waited for (HANDOFF.md has the commands):
             q0049 core-rf-card    card check of core/restart-finder (release gate v0.8)
             q0039 core-v07-card   card check K7 of the merged card executable of v0.7
             q0035 nl2-review-R5   card run of the reviewed level-2 build (its package)
             q0036 step-limit-card card smoke run of the step-limit build (its package)
             q0032 (job 5346)      row 4: 0.755 control continued 300-600 M
             q0059                 row 4: 0.755 member continued, --after step-limit-card
                                   (was q0033; re-added behind the four checks)
next:        1. q0049: finish, card_check.py (JOURNAL-restart-finder.md entry 20), then the
                release core-v0.8 (tag, executables .work/build_*_v08, READY, CLAUDE.md row)
             2. q0039, q0035, q0036: judge (RELEASE-v0.7.md "Card checks pending")
             3. row 4: q0032, q0059 -> P13; then the note (section III D)
             4. Fable source session: NEXT_SOURCE.md items 0, 0b, 1
blockers:    none
needs:       orch: CLAUDE.md sentence on the two restart defects once core-v0.8 is out;
             older outbox items 20261125T121047Z, 20261125T030800Z
offers:      tracks/core/analysis/deposit_levels/dep_levels.py (deposit across level faces
             with a 1D emulation of the rule); analysis/restart_diag/diag_restart.py; the
             `-i add.athinput` way to add a parameter on a restart (answered A, B, D, F)
budget:      G2 card-hours: used 19.21, reserved 2.07, left 18.72 of 40 (nrpic-run budget,
             2026-11-26T02:48Z); this session used no card
