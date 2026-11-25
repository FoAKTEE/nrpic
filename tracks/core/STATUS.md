# STATUS of core

gate:        G2 NOT MET (tracks/core/stage/G2/: CHECKLIST 18 items, 13 PASS, 5 FAIL:
             C1 ladder rows 3, 4 partial; C2 three-way convergence; C6 reproducibility
             package (open level-3 chains); C7 = C1; C12 no REVIEW.md/SCOPE.md).
             Batch 17 (2026-11-25T11:47-12:30Z): round without AthenaK source change.
headline:    Release core-v0.7 is on main (tag 5f75e5b9); its release processor build is
             byte-identical to the candidate (75 of 75, core-20261125-115428-3670218). The
             queue marker no longer reaches any job of scripts/ (decision 0037 item 4;
             fake-Slurm tests PASS, control with the old scripts shows the leak). Row 4
             level 3, two of six runs: the 0.726875 member collapses at 338.25 M, and the
             0.73625 control, STABLE by the 300-M rule, collapses at 421.25 M (fates
             core-20261125-120724-246d2a5): the 300-M bracket (0.7175, 0.73625) stands as
             written but does not mark a stability threshold [JUDGEMENT, rest pending].
last-result: M1 (marker) held: core-20261125-120211-08f4fb9, -120145-665b6a0 (both
             registered by hand: the local launcher refuses fake-Slurm tests). R7 held.
             Provenance: E's seven ablation runs used athena_gpu 468109496c82... (source
             6ca93cba), verified on the copies in their run directories
             (tracks/core/EXE_PROVENANCE.md); answered E.
pending:     card runs in the shared queue (none waited for; all "waiting" at 12:10Z):
             q0039 core-v07-card   card check K7 of the merged card executable
             q0035 nl2-review-R5   card run of the reviewed level-2 build (its package)
             q0036 step-limit-card card smoke run of the step-limit build (its package)
             q0030-q0033           row 4 level 3: 0.726875 control, 0.73625 member
                                   continued, 0.755 pair continued (HANDOFF.md)
next:        1. when q0039 has run: judge it (RELEASE-v0.7.md, "Card checks pending");
                then the CLAUDE.md sentence to orch
             2. row 4 level 3 when q0030-q0033 have run: finish, row4_fate.py (HANDOFF)
             3. the Fable source session: tracks/core/NEXT_SOURCE.md items 1-3
blockers:    none
needs:       orch: RULES text on the marker once core/nrpic is merged, and whether
             fake-Slurm self-tests may be registered by the tool (outbox
             20261125T121047Z); older: 20261125T030800Z, 20261121T233031Z, 20261121T204332Z
offers:      scripts/tests/test_queue_marker.py; tracks/core/tools/hand_run.py;
             tracks/core/NEXT_SOURCE.md; EXE_PROVENANCE.md (rule: no executable is
             replaced in place)
budget:      G2 card-hours: used 15.76, reserved 4.03, left 20.21 of 40 (nrpic-run
             budget, 2026-11-25T12:15Z); this session used no card
