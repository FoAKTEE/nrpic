# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (open level-3 chains); C7 = C1; C12 no REVIEW.md/SCOPE.md).
             Batch 11 (analysis round, no AthenaK source change).
headline:    ladder row 4 on cells of M/8, level 2 judged by the rule written before the
             runs: collapse within 300 M is BRACKETED between y_c = 0.7175 (member and
             control collapse at 294 M) and 0.73625 (stays, D = +0.0014). P5, P6, P7, P9
             hold; P8 refuted just (the 0.73625 control drifts 0.043 inward, bound 0.04).
             But the surviving pairs drift inward steadily, member and control alike,
             and near the bracket the kick no longer matters: the bracket may be set by
             the 300-M window, not by a threshold. Level 3 (to 600 M) tests that.
last-result: fates of levels 1+2 core-20261124-130055-9fc9901 (six chains closed, 0.63
             card-hours each); T5 of branch core/noise-level2 PASS on the card (Track E,
             SMOKECHK E-20261123-090718-6203c87: card/processor 1.7e-13 means, 2.0e-11
             rms; level 2 / level 0 wall 1.156 SR, 1.136 USR); note rebuilt by
             core-20261124-133602-3e31713 (Fig. 5 levels 1+2 with the drift, 134
             ledger rows, 10 pages, checker clean).
pending:     row 4 level 3 (predictions P10-P15, journal 2026-11-24T13:05Z), six chains,
             11.82 card-hours asked, about 5.1 expected: 0.726875 member/control 0-600 M
             core-20261124-130310-597d9ca / -130340-31cf5e8 (jobs 5154 eligible, 5156
             held); 0.73625 pair continued 300-600 M -130347-7d6a10d / -130321-ed96d4d
             (5157 held, 5155 eligible); 0.755 pair continued -130406-09319a0 /
             -130356-d9d09bf (5159, 5158 held). Sequencer pid 3904230, log
             scratch/core/tmp/lead_b11/sequencer.log.
next:        1. when the chains end: finish each, row4_fate.py with the continuations
                joined (HANDOFF.md has the command), P10-P15, LADDER, note
             2. if the stable pairs collapse by 600 M: the drift (mesh, particle noise,
                deposit) is the open item of row 4; propose a window-free criterion
             3. core-v0.7: W31 step limit (in work this batch, core source slot), W24
                mitigation (core/gauge-2), W26 clump-table, W27 oblate, OPEN.md u; W30
blockers:    none
needs:       orch: interface corrections into coord/INTERFACES (outbox 20261121T233031Z);
             the nine waiver lines (outbox 20261121T204332Z); merge of core/nrpic
             (carries the cpu_run.sh footer fix)
offers:      tracks/core/note/ (row 4 on M/8 with levels 1+2 and the drift); outbox
             20261124T130733Z to A (W31 in work this batch) and 20261124T130734Z to kb
             (M18 verified by id_solver T1 in mode code: correction of core's answer)
budget:      G2 card-hours used 16.4 after this session's closures (40 to the gate,
             decisions 0026/0031); 11.82 asked for level 3; processors: three
             single-core analysis runs of minutes
