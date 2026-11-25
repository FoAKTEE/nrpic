# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1 NOT met (stage/G1, batch 21): the
             complete vacuum passage (C8: A2 at 96.23 M of the >= 170 M needed) and the G1
             verifier (C18, asked when C8 is done)
headline:    The m/16 passage P1b (A + A2) has reached 96.23 M: the pair passed its own closest
             approach (2.11 M at 76.4 M) without merging and is now 13 M from the heavy hole and
             closing; nothing of its trajectory was lost to the tracker-file truncation.
last-result: - A2 PARTIAL (F-20261125-170453-1175d44, fig_b21_a2_state read): tracker copies of
               every segment join to 0-96.23 M without a gap, recomputed stretches agree to
               1e-12 M, horizon summaries/history/waveforms appended (S1-S3 met); A2-1 REFUTED on
               timing (2.110 M at 76.37 M against the window 63-75 M); centre of mass 13.06 M from
               M at 96.25 M, closing at 0.24 M per M (A2-2 open); masses flat (3e-5 per M), heavy
               hole within 6.9e-4, rms H <= 3.1e-5
             - passage reader F-20261125-170646-6dd4ae4: NR late against Newton; both members
               still bound to M and to each other at 96 M
             - horizon recheck, decision 0040 item 3 (F-20261125-170540-aa39bea,
               F-20261125-170632-5aa9786): no run of the track has the finder's status file; by
               the failure signature no failed search at m/12, m/16; P1's common horizon 48.81 M
               confirmed; drift wording corrected (m/8 0.9-1.7e-3 per M; R4); H2, H4 bands failed
             - B (F-20261121-203156-03efdd3) closed as stopped, 9.28 card-hours
decision:    continue A2 as it is (core-v0.5 card build + tracker-copy wrapper); no switch to the
             restart-finder executable (restart files belong to the build that wrote them; q0049
             unjudged), no rerun. Prediction: the cap stops it at 125-140 M, 10-14 card-hours
card jobs:   A2 P1b m/16  q0001, F-20261124-210400-902c650, Slurm 5294 PENDING (cards held
             until about 2026-11-26 06:46 PST), 96.23 -> 200 M, G1 ceiling 19.5 h (5.64 used),
             MAX_SEGMENTS 19 (13 used); read by stage/review_wave3/b21_a2_state.py, b11_passage.py
             B2 alone m/16 q0002 (waiting), 107.85 -> 140 M, G2 5 h; read by b11_cards.py
             C2 P1b m/12  q0003 (after B2), 20 -> 200 M, G2 24 h; read by b11_passage.py
             none of them can have <fastflow> diagnostics (R22)
next:        1. When A2 has passed the pair's pericentre with M (~100-125 M): rerun
                b21_a2_state.py and b11_passage.py (registered), judge A2-2; at the cap, continue
                A2 through one --cmd queue entry within 19.5 card-hours (orch's answer)
             2. A2 to the separation (>= 170 M), judge A2-3 to A2-5, then ask the fresh G1
                verifier with the material of stage/G1/OPEN.md item 2
             3. Note v3 with the passage; junk at P1b's spheres from A + A2 waveforms (T3)
blockers:    cards held by another partition (0041 item 6); preemptions (R20); queue cap of five
needs:       orch: A2's tail plan (outbox 20261125T171002Z a2-tail-plan); core: finder status
             file on a restart (outbox 20261125T171002Z finder-diagnostics-on-restart); earlier:
             HRNA pair-force spec, wave extraction beyond l = 8
offers:      nrread.py (tracker join across restarts, failed-search signature), b21_a2_state.py
             (coverage and overlap check of a chain's tracker copies), b21_horizon_recheck.py
             (horizon recheck without status files), chain wrappers athena_keep_trackers_bc.sh,
             athena_resume_bc.sh
budget:      G1: 30.19 used + 18.68 reserved (A2) of 60, 11.13 left; G2: 13.60 used, 46.40 left
             (nrpic-run budget, 09:25 PST). This session: 0 card-hours
