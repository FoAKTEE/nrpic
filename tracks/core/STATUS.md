# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package; C7 = C1; C12 no REVIEW.md/SCOPE.md). Unchanged this session.
             Batch 40 (2026-11-28T07:26-07:55Z): round without AthenaK source change.
headline:    RELEASE core-v0.9 FINAL: source ad54460e, REGRESSION PASS (75 of 75 against
             core-v0.8), CARD CHECK PASS. q0094's job 5601 COMPLETED (sacct; 24 s, 0.0067
             card-hours); run core-20261128-052151-e5a2d55 closed; judged by the
             registered card_check.py, run core-20261128-072820-d5fa2ca (figure looked
             at): K1 planar deposit lines card = processors to 2.0e-15 (cic, cic_fs 0.0),
             line sum 32.0; K2 the three compensated cases conserve to 9.9e-16 at 12
             records (the printed digit); K3 six S1L finder members found, masses to
             1e-15; K4 a continued run takes fastflow/diagnostics=true on the command line.
             Executables published: scratch/core/exe/core_nrpic_v09/ (athena_cpu = R9
             build b7a48e9a, athena_cpu_mpi = M9 build a44b7c85, athena_cpu_omp 2e31b69e,
             athena_gpu 20172cae = the card-checked build; COMMIT, SHA256SUMS, READY).
             RELEASE-v0.9.md in the form of v0.8 (with a section for the clerk); changelog
             section core-v0.9 complete (options table, three changes without an option
             and the runs they change, start/stop times, not done incl. level faces
             between ranks, cost of the compensated deposit, Track A's false acceptance).
             Interface texts ready to copy: level_faces.md, restart_parameters.md,
             finder_box.md (new section 0: decks without puncture_setup must name
             start_time_<n> and stop_time_<n>; the defaults never search), finder_stop.md
             (two paragraphs). Outbox: A, D, F (executable, what changes in their decks,
             read from their branches: 17 of A's nested-ball decks change; none of D's or
             F's); orch (clerk request, CLAUDE.md row); C (start/stop answered).
last-result: card run core-20261128-052151-e5a2d55; analysis core-20261128-072820-d5fa2ca
             (CARD CHECK PASS). Earlier evidence of the release: R9 -020122-3a1a3dd, T9
             -021251-d4575ac, Q9 -020910-9292e5d, M9 -022409-4720043.
pending:     nothing in the shared queue for core. q0028 is listed by `nrpic-queue audit`
             as done but NOT COMPLETED (old row-4 chain, handled in batch 17); q0086 is
             superseded by q0094.
next:        1. clerk: merge core/nrpic, tag core-v0.9 on ad54460e, release builds
                (RELEASE-v0.9.md, "For the release clerk"; outbox 20261128T074500Z)
             2. row 4: the note (section III D of note/main.tex, fig_row4_m8.py) with the
                fourth reading; P14 (joins) still uncomputed
             3. G2 package items C2, C6, C12; NEXT_SOURCE.md for the next Fable session
                (level faces between ranks; cost of the compensated deposit on a card)
blockers:    none
needs:       orch/clerk: the merge and tag of core-v0.9; the CLAUDE.md row (outbox)
offers:      release executables scratch/core/exe/core_nrpic_v09/ (all four builds);
             rerun_compare.py (byte comparison of two run trees); card_check.py of
             faces_finder for a release card build (0.01 card-hours)
budget:      G2 card-hours: used 20.72, reserved 0.10, left 19.18 of 40 (nrpic-run budget,
             07:50Z); this session: no card run queued (q0094 used 0.0067); processors: one
             analysis on 1 core (seconds)
