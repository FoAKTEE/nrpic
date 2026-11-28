# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package; C7 = C1; C12 no REVIEW.md/SCOPE.md). Unchanged this session.
             Batch 35 (2026-11-28T01:55-02:30Z): round without AthenaK source change.
headline:    candidate core-v0.9 merged and checked on processors: origin/core/faces-finder
             merged into core/nrpic at 8139c969 (source = ad54460e, git diff empty).
             R9 byte regression against core-v0.8 PASS 75 of 75; T9 the branch's six
             tests with the merged build: 416 files, none differs (45 differ only by the
             run directory's name stored in decks and restart files), same verdicts; Q9
             restart test ALL OK. RELEASE-v0.9.md written NOT RELEASED: the card check
             q0086 was PREEMPTED after 5 s (job 5544; the queue said done), queued again
             as q0094 (priority 2). Changelog section core-v0.9 written (three changes
             without an option and the runs they change; four finder options; not done:
             level faces between ranks, cost of the compensated deposit).
             Release builds of core-v0.8: .work/build_cpu_v08 = core_nrpic_v08/athena_cpu
             on 75 of 75 items (V8); the card build not compared by a run (RELEASE-v0.8.md).
             Answers: A (outer-face options of core-v0.6 for the expanding ball; the run
             that decides 0048 item 5), F (found flag: column 10 is the integral of H,
             hmean_tol 100 is an abort test; v0.5 restarts under v0.8 untested). Finder
             requests of A answered by the source session (said so). finder_stop.md gains
             the paragraph "Found does not mean a vanishing expansion".
last-result: R9 core-20261128-020122-3a1a3dd (figure -020936-0826227); T9
             -021251-d4575ac (first pass -021119-fb199ef failed on script summaries);
             Q9 -020910-9292e5d; V8 -020855-e27868f (figure -021505-7852e7f); merged-build
             tests -020214-a173064 (dep, failed by its split check as on the branch),
             -020250-1981d90, -020255-72e53c6, -020317-73134bb, -020447-28dbb9f,
             -020922-7d1da68; q0086's run core-20261128-002929-335815e closed as stopped.
pending:     q0094 (core-ff-card2, waiting): card check of core-v0.9 (K1-K4 of
             JOURNAL-faces-finder.md entry 5); judge with card_check.py (RELEASE-v0.9.md).
             (Row 4: q0059's run core-20261126-110234-a72e07c closed this session; fates
             core-20261128-021941-61b61a1: 0.755 member no collapse by 600 M, P13 holds
             for both runs, bracket (0.7175, 0.726875) unchanged; LADDER fourth reading.)
next:        1. q0094 when COMPLETED (sacct): finish, card_check.py, then RELEASE-v0.9.md
                final in the form of RELEASE-v0.8.md, executables in
                scratch/core/exe/core_nrpic_v09/ (MPI build to make), outbox to orch
             2. row 4: the note (section III D of note/main.tex, fig_row4_m8.py) with the
                fourth reading; P14 (joins) still uncomputed
             3. G2 package items C2, C6, C12; NEXT_SOURCE.md for the next Fable session
blockers:    none
needs:       orch: nothing new until q0094 has passed; then the clerk (merge, tag on
             ad54460e, release builds, interface texts level_faces, restart_parameters,
             finder_box; finder_stop updated)
offers:      candidate core-v0.9 executables for scouting: scratch/core/exe/core_faces-finder/
             (card build untested); rerun_compare.py (byte comparison of two run trees)
budget:      G2 card-hours: used 20.06, reserved 2.07, left 17.87 of 40 (nrpic-run budget,
             02:16Z); this session queued q0094 (0.2 asked); processors: one serial build
             (6 jobs, 180 s), two regressions on 3 cores (about 5 min each), tests on 1 core
