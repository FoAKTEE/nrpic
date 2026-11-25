# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting, package NOT complete (stage/G2/OPEN.md section 1):
             FNQ and FL16 on the cards, note v3, fresh-context G2 verifier. Track criteria N and G
             met at the meshes and particle numbers run (C7, C8); C6 and C11 now PASS.
headline:    Decision 0040 item 3 done: no G2 horizon number rests on a failed search. No D run
             has `<fastflow> diagnostics`; by the source-fixed signature (NaN or bit-identical repeat)
             there is no failed search after 20 M in 13 summaries, the V-1L plateaus are found
             surfaces and N is unchanged (2.28e-4 M/8, 1.99e-4 M/16). Region shells outside the
             hole are particle noise (FNQ/FN4 = 3.4-4.4). FK's early removals (D4) all lie after
             235 M; before 219 M FK and ES-FL remove identically.
last-result: hz_check D-20261125-160142-b1c51b5 (figure D-20261125-160241-2b7ba3b);
             region_norms D-20261125-160355-bda7e38; d4_timing D-20261125-160450-9326390;
             rerun_g2.py test D-20261125-160651-29a730e (byte-identical). g2long entries 23-24.
failed:      batch 20: R1 as written (NaN Hmax of the empty horizon sphere at t = 0); T1's 1 per
             cent for FN4 (3.4 per cent before 219 M); run D-20261125-160123-f86d73c (parser).
             Earlier: P5 REFUTED (M/4 outside the regime, ruling 0039 item 4), P6, P11, P13, P12
             with the M/8 control, FF4 D3 early, FP4, FP-ext (ii), FE1, FE2, P2, XC2.
             Unexplained: why excision removes dust up to 0.36-0.66 M before the exact crossing late.
next:        1. Core's guard test on a card: ES-FL with `ah_exc_max_growth = 8` to 240 M, removals
                past 219.5 M (with diagnostics = true), when the cards free; post the outcome
             2. FNQ (Q1-Q3, XQ) and FL16 (L1-L5) as the queue runs them; close with nrpic-run finish
             3. Note v3, fresh-context G2 verifier (C17), then stage report for review
blockers:    none for processor work; FNQ (q0010) and FL16 (q0011) wait for the cards (held by
             another partition since the morning of 2026-11-25)
needs:       orch: b20-horizon-recheck-null-mesh-two-members (posted 2026-11-25; M/12 only on
             request). core: card check q0049 of core/restart-finder before using
             polish_iterations; older: lapse-leak-growth-data, newtonian-mode-edges,
             lapse-excision-criterion, particle-energy-and-crossing-record item 2,
             accretion-diagnostics item 3, spike-mass-refinement (outbox/)
offers:      g2long/tools: hz_check.py (failed finder searches without a status file),
             region_norms.py (shell norms from region spheres), d4_timing.py, close_by_hand.py,
             fk_compare.py, np_partial.py, probe_long.py, fp_analyse.py, xc_plane.py,
             slice_mosaic.py, judge_conv.py; stage/G2/rerun_g2.py (rerun of a stage package)
budget:      card-hours this session: 0. Closed earlier: FK 2.70, FF4 1.34, FE4 0.83, FN4 3.19.
             Processors this session: six analyses on one core each (seconds to a minute).
card jobs:   FNQ D-20261124-172725-2f426b6: q0010 submitted, chain at 353 M of 400, next job 5293
             pending (Resources). FL16 D-20261124-172745-72472ed: q0011 waiting (prio 1 eff.).
relaxed lapse: no G2 run uses it (decision 0025 item 3); G3 matter (stage/G2/OPEN.md section 2).
