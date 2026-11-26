# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (open level-3 chains); C7 = C1; C12 no REVIEW.md/SCOPE.md).
             Batch 27 (2026-11-26T11:44-13:00Z): round without AthenaK source change.
headline:    release core-v0.8 made final: card check q0049 PASS (K1, K2, K4, K5 held; K3
             held for the polished and tight finder rules, card = processors within
             3.3e-16, and FAILED for the rule 1e-5 without polishing, which differs between
             card and processors up to 8.8e-6 and in two accepts of sixteen). Executables
             published in scratch/core/exe/core_nrpic_v08/ (serial, MPI, threaded, card;
             MPI smoke test M1, M2 held). Waits for the clerk (merge, tag on 01d4aeeb,
             release builds, CLAUDE.md row: outbox 20261126T115635Z).
             core-v0.7 card checks: K7 CARD PASS (three analyses); step-limit card run P4a,
             P4c held, P4b held in its test; level-2 review R5: see last-result.
             Row 4: bracket (0.7175, 0.726875) unchanged; 0.755 control does not collapse
             by 600 M but drifts (P13 holds for the control).
last-result: card check core-20261126-114747-a6f2385 (of card run -070946-7971fde; first
             pass -114526-2b1f001 failed on the reader); MPI smoke -115451-893a30e;
             K7: -115658-8af7dd7, -115708-140bafa, -115725-9a8d381; step limit
             -121103-1070457; row 4 -121143-aaae1b7; R5 -115933-9fb0e47 (see JOURNAL.md,
             last entry, for its outcome).
pending:     q0059 (job 5378, pending in Slurm): row 4, 0.755 member continued 300-600 M
             (member half of P13). No other entry of core in the queue.
next:        1. clerk: merge core/nrpic, tag core-v0.8 on 01d4aeeb, builds, CLAUDE.md rows
                of v0.7 (card checks judged) and v0.8 (words in the outbox)
             2. q0059 when it has run: finish, row4_fate.py (HANDOFF), member half of P13
             3. Fable source session: NEXT_SOURCE.md items 0, 0b, 1
             4. G2 package items: C2, C6, C12 (HANDOFF "What G2 still lacks")
blockers:    none
needs:       orch: merge and tag core-v0.8; CLAUDE.md rows (outbox 20261126T115635Z and the
             v0.7 row words of this session); older outbox 20261125T121047Z, 20261125T030800Z
offers:      core_nrpic_v08 (finder polishing: 0.33 s per search on a card; excision guard
             factor; restart outputs equal on one rank); card_check.py, mpi_smoke_v08.py
budget:      G2 card-hours: used 20.06, reserved 2.07, left 17.87 of 40 (nrpic-run budget,
             2026-11-26T12:13Z); this session submitted no card run; processors: one MPI
             build (4 jobs, 2.5 min), analyses on 1-2 cores
