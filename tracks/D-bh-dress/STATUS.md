# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting: track criteria N and G met (C7, C8); package
             FAIL as expected (stage/G2/STAGE_REPORT.md): particle number, third mesh of the
             growth, note text and the G2 verifier missing.
headline:    PAUSED at 06:18 PST (pause flag). The vacuum "floor" of the null test (1.25e-4)
             looks like the finder's, not the slice's (FP run log; registered judgement
             pending): re-searched with mass_tol 1e-9 the vacuum horizon mass moves by
             at most 1.8e-5 (M/8) and 4e-6 (M/16) from 100 to 450 M, where the production
             finder (mass_tol 1e-5) jumps between plateaus 1.3e-4 apart. With the converged
             finder the bubble-vacuum difference is at most 6.5e-5 at M/8 and 2.3e-5 at M/16
             (200-300 M). The null test holds at M/16 too (H3: 1.99e-4 against 2.28e-4).
last-result: g2long/JOURNAL.md entries 11-13 (13: paused, FP and FP-ext running, not judged):
             FP D-20261124-130935-fdca920, FP-ext -140606-286a302, judge_long -131138-0b8ffc5, judge_conv -131149-9f0166d,
             XC -134211-c6fce88, boundary_gauge -131657-89cd963, slice mosaic -134644-2389227.
failed:      P2 (M/4 offset -8e-3, no mesh order of the production-finder offset); XC2 expected
             factor (1.05, not 1.3-3); FP-ext (ii) bound 5e-5 likely fails (6.5e-5 at 250 M in the
             FP log; judgement pending).
next:        0. Close FP and FP-ext (nrpic-run finish), run fp_analyse.py (entry 13)
             1. Read FE4 (P5), FF4 (P12-P14), FK (P7-P11) when they end (jobs 5153, 5152, 5144);
                then FN4 (N1-N4, XN; job 5170 held)
             2. Register FNQ and FL16 when card allotment allows (orch request posted)
             3. G2 package: note v3 with the long runs, FP and XC; a fresh-context G2 verifier;
                nrpic-stage verify without timeout
blockers:    card allotment: 4.29 card-hours left toward G2 before FN4 (cap 4.0)
needs:       orch: g2-card-allotment (outbox 2026-11-24). core: finder-stopping-rule (draft in scratch, post after FP);
             ah-excision-growth-guard; older: lapse-leak-growth-data, newtonian-mode-edges,
             lapse-excision-criterion, particle-energy-and-crossing-record item 2,
             accretion-diagnostics item 3, spike-mass-refinement (outbox/)
offers:      g2long/tools: probe_long.py (finder re-search of any restart dump), fp_analyse.py,
             xc_plane.py (exterior constraint norms from z = 0 slices), slice_mosaic.py,
             boundary_gauge.py, judge_conv.py; flux_tools/fluxio.drop_overlaps (removal record of
             preempted chain segments); ES-F data at 4N and N/4 (D-20261124-130942-29c5de2,
             -131050-ed0a535)
budget:      card-hours toward G2 (nrpic-run budget 05:17 PST): used 16.86, reserved 8.85, left
             4.29; FN4 registered with cap 4.0 (expected 2.8). This session's card use: 0.16
             (two preempted segments, jobs 5142/5143). MAX_SEGMENTS of the resumed chains raised
             (FF4, FE4 10; FK 12; FN4 7) because preemptions consume segments; the card time stays
             what the segments run. Processors: FP 4 cores ~70 min, FP-ext 2 cores, smoke tests
             and analyses 1 core each.
card jobs:   FF4 5152, FE4 5153 (pending, eligible); FK 5144, FN4 5170 (held; sequencer
             scratch/D-bh-dress/g2long_seq3/ releases them in that order).
