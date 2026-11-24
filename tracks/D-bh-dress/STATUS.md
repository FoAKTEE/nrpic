# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting: track criteria N and G met at the meshes run
             (C7, C8); package not ready (stage/G2/STAGE_REPORT.md, OPEN.md): three-way
             convergence waits for six card runs, note text, G2 verifier, rerun script.
headline:    The vacuum "noise floor" of the null test (1.2e-4) is the horizon finder's
             stopping rule, not the slice (test FP, g2long entry 14): with a converged finder
             the vacuum horizon mass moves by at most 1.8e-5 at M/8 over 100-500 M and 3.9e-6 at
             M/16. The bubble differs from vacuum by at most 7.3e-5 (M/8) and 5.5e-5 (M/16), with
             no trend in time; its horizon mass dips by 4-6e-5 at 100 M at both meshes (test FE).
last-result: g2long entries 14-17: FP D-20261124-130935-fdca920, FP-ext -140606-286a302 judged by
             fp_analyse -172508-c847ee4; ladder schematic -172838-3a30e48; test FE
             -173137-f358715 judged by fe_analyse -175356-0f40f1a. FNQ -172725-2f426b6 and FL16
             -172745-72472ed registered and held.
failed:      FP4 (the converged-finder offset changes sign over M/4, M/8, M/16: no mesh order);
             FP-ext (ii) bound 5e-5 (7.3e-5, not refuted); FE1 and FE2 bounds (not refuted: the
             "step" was a dip at the reference time); earlier P2, XC2 factor.
next:        1. Read FE4 (P5 + tight re-search), FF4 (P12-P14), FK (P7-P11), FN4 (N1-N4, XN),
                FNQ (Q1-Q3, XQ), FL16 (L1-L5) as they end (HANDOFF table)
             2. Note v3 (long runs, FP/FE, XC, ladder, mosaic); rerun script (C6)
             3. Fresh-context G2 verifier; nrpic-stage verify G2 again without a timeout
blockers:    cards held by another user's priority jobs until about the morning of 2026-11-25
needs:       core: finder-stopping-rule (posted 2026-11-24), ah-excision-growth-guard; older:
             lapse-leak-growth-data, newtonian-mode-edges, lapse-excision-criterion,
             particle-energy-and-crossing-record item 2, accretion-diagnostics item 3,
             spike-mass-refinement (outbox/)
offers:      g2long/tools: probe_long.py (finder re-search of any restart dump), fp_analyse.py,
             fe_analyse.py, xc_plane.py (exterior constraint norms from z = 0 slices),
             slice_mosaic.py, boundary_gauge.py, judge_conv.py, schem_ladder.py;
             flux_tools/fluxio.drop_overlaps (removal records of preempted chain segments);
             ES-F data at 4N and N/4 (D-20261124-130942-29c5de2, -131050-ed0a535); the finding
             that mass_tol 1e-5 leaves the reported horizon mass ~6e-5 off (all tracks)
budget:      card-hours toward G2 (nrpic-run budget 09:32 PST, allotment raised by 0032): used
             17.45, reserved 18.68, left 3.86. This session's card use: 0 (cards held by priority
             jobs). Processors: FE 4 cores ~25 min, analyses 1 core, stage verify 1 core.
card jobs:   FF4 5152, FE4 5153 (pending, eligible); FK 5144, FN4 5170, FNQ 5174, FL16 5175
             (held; sequencer scratch/D-bh-dress/g2long_seq3/ releases them in that order).
