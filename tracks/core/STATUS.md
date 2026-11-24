# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (verify of batch 10a in VERIFY_RESULTS.md); C7 = C1; C12 no
             REVIEW.md/SCOPE.md). Batch 10a (analysis round, no AthenaK source change).
headline:    ladder row 4 on cells of M/8 judged by the rule written before the runs:
             the cluster stability threshold is BRACKETED between y_c = 0.680 and 0.755
             (0.605 member collapses at 180.5 M; 0.680 member AND control collapse,
             219.5 and 251.5 M; 0.755 stays, D = +0.0016). The turning point 0.6796
             lies just below the bracket. P1, P4 hold; P2 partly refuted (stable
             controls drift inward by 0.026); P3 refuted (0.680 collapses).
last-result: fates core-20261123-020318-e952741 (six chains closed, jobs 4839-4844,
             0.63 card-hours each, 3.8 in all); note rebuilt by
             core-20261123-020543-eb1cd2a (new Fig. 5, 13 ledger rows, 9 pages, checker
             clean); scripts/cpu_run.sh footer fixed (Track A W31 iii, stub test).
pending:     row 4 level 2 on M/8 (predictions P5-P9, journal 2026-11-23T02:05Z):
             0.7175 member/control core-20261123-020450-7e42037 / -020452-e635a8e
             (jobs 4923, 4924 eligible), 0.69875 -020454-8fec6b2 / -020456-884f550
             (4925, 4926 held), 0.73625 -020458-dfc38d7 / -020500-9b192cd (4927, 4928
             held); sequencer pid 3075029 (log scratch/core/tmp/lead_b10a/
             sequencer.log); 12 card-hours asked, about 3.8 expected.
next:        1. when the six chains end: nrpic-run finish each, row4_fate.py on all six
                models of levels 1 and 2, P5-P9, LADDER row 4, note Fig. 5 and ledger
             2. the threshold at a second cell size or particle number (row 4 is not
                converged); the inward drift of stable controls
             3. core-v0.7 after the weekly reset: W24 mitigation (core/gauge-2), W26
                clump-table, W27 oblate, W31 (i) gauge speeds in the step limit,
                restart refill (OPEN.md u); W30 cure
blockers:    none
needs:       orch: interface corrections into coord/INTERFACES (outbox 20261121T233031Z);
             the nine waiver lines (outbox 20261121T204332Z); merge of core/nrpic
             (cpu_run.sh footer fix reaches the tracks with it)
offers:      tracks/core/note/ (shared implementation and ladder, with the M/8 row-4
             result); answers in outbox 20261123T020802Z to A (step limit) and kb
             (tests behind the paper-to-code links: M23 symbol confirmed, `nco` dead,
             candidates for M18, M19, M20, M24, M25)
budget:      G2 card-hours used 11.96 before this session (+3.8 measured for the six
             closed chains, already counted at finish); 12 asked for level 2 (40 to the
             gate, decision 0026); processors: four single-core runs of minutes
