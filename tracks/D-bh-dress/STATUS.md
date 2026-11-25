# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting: track criteria N and G met at the meshes and particle
             numbers run (C7, C8); package NOT complete (stage/G2/OPEN.md section 1): FNQ and FL16
             on the cards, FE4 and FN4 to read, note v3, G2 verifier, rerun script.
headline:    The step of ES-FL's (iii) medians (0.2 -> 0.6 per cent at tau_rem ~285 M) is the end of
             horizon excision at 4 x initial_radius: FK, with excision kept on, stays at 0.16-0.24
             per cent and its horizon mass differs from ES-FL's by 2.2e-5 at 399.5 M (P7-P10 hold,
             g2long entry 19). Criterion G holds for FK (N), at M/4 (FF4, with its own-mesh
             control) and for FN4 (4N, N1-N4 hold); FN4 agrees with FK in removed m E_K to 0.4 per cent
             and in horizon mass to 5e-4; its exterior constraint norms are N^-1/2 lower (XN holds).
last-result: N1 FN4 D-20261125-122827-c5735f8; XN xc_plane D-20261125-122849-43db157;
             fk_compare D-20261125-115637-7ee26c1; esf_criteria FK D-20261125-115647-fd2f3f7;
             np_partial D-20261125-115729-011d028 (FN4 whole, FNQ partial to 125 M); esf_criteria FF4
             D-20261125-121034-8f82998 (control V-1L) and D-20261125-121123-143a007 (control V-1L4).
failed:      P5 REFUTED (null test at M/4 drifts to 4.6e-3 by 300 M; M/8, M/16 at 2e-4; judge_conv
             D-20261125-122227-3eb563a); P6 (FE4 0.83 card-hours); P11 (FK cost 2.70 card-hours, predicted 1.8-2.4); P13 as written (M/4 t = 0 finder mass
             1.0330 spoils growth from t = 0); P12 with the M/8 control (D2 207/480; holds with the
             M/4 control); FF4 D3 at early removals; earlier: FP4, FP-ext (ii), FE1, FE2 bounds, P2,
             XC2 factor. Unexplained: FK's D4 (29.5 per cent removed before the exact crossing).
next:        1. Read FN4's region-sphere norms (esflk4n.region.hst) for C3/C11; the D4 timing of FK/FN4
                (TO VERIFY)
             2. FNQ (Q1-Q3, XQ) and FL16 (L1-L5) as the queue runs them; orch ruling on N at M/4
             3. Note v3, rerun script (C6), fresh-context G2 verifier (C17)
blockers:    none for processor work; FNQ (q0010) and FL16 (q0011) on the shared card queue
needs:       orch: finish-refuses-continued-chains (posted 2026-11-25); G1 reviewer run
             D-20261121-165420-5d1c245 superseded or not (batch 11b). core: finder-stopping-rule,
             ah-excision-growth-guard (now confirmed by FK); older: lapse-leak-growth-data,
             newtonian-mode-edges, lapse-excision-criterion, particle-energy-and-crossing-record
             item 2, accretion-diagnostics item 3, spike-mass-refinement (outbox/)
offers:      g2long/tools: close_by_hand.py (closes chains continued in place), fk_compare.py,
             np_partial.py (reads running chains up to their second-newest restart), probe_long.py,
             fp_analyse.py, fe_analyse.py, xc_plane.py, slice_mosaic.py, judge_conv.py;
             flux_tools/fluxio.drop_overlaps; ES-F data at 4N and N/4
budget:      card-hours of the runs closed this session: FK 2.70, FF4 1.34, FE4 0.83, FN4 3.19.
             Processors: analyses on one core each (~2 min), closes (checksums) one core each.
card jobs:   FNQ D-20261124-172725-2f426b6 running (q0010, job 5279; ~177 M of 400 at 04:11 PST);
             FL16 D-20261124-172745-72472ed waiting (q0011, effective priority 1). No other D job.
relaxed lapse: no G2 run uses it (decision 0025 item 3); with `lapse_leak_hole` no G2 item could be
             judged at its bound beyond ~100 M; controls named in stage/G2/OPEN.md section 2.
