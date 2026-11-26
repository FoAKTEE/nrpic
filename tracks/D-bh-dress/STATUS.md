# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 package ASSEMBLED for its fresh-context verifier and the gate
             review (batch 25): every CHECKLIST item PASS except C17 (verifier); OPEN.md lists only
             failures on record with their rulings. Not passed: the gate is the orchestrator's.
headline:    The last two G2 runs held every prediction: FNQ (N/4) and FL16 (M/16). The growth
             against the flux holds at N/4, N, 4N and M/8, M/16 (bins within 0.29-0.62 per cent);
             the horizon mass converges in particle number with N^-1/2 noise; M/8 and M/16 agree
             in the growth to <= 4.4e-4 (M/4 outside the regime, no order claimed). Every horizon
             number made without the finder diagnostics, rechecked by the failure signature.
last-result: FNQ D-20261124-172725-2f426b6 and FL16 D-20261124-172745-72472ed closed; readings
             D-20261126-054616-a13a888 (Q1), -054636-93618ee (Q2), -054718-afa783e (XQ),
             -054736-10c837a (R3), -055158-30ae09c (L2), -055159-6c40115 (L5), -055208-4e0fd0e
             (signature), -055249-505b079 (conv3, C2); note v3 build D-20261126-055502-fbb1bec.
             g2long/JOURNAL.md entries 25-27; stage/REVIEW-wave3.md sections 23-24.
failed:      batch 25: D3 at N/4 after ~220 M (8352 of 29984 removals; not predicted, no bound
             in G); conv3's first reading D-20261126-055207-0137c53 dropped 300 M (reader fixed,
             labelled post hoc). Earlier: P5 (M/4 null test; ruling 0039 item 4), P6, P11, P13, P12
             with the M/8 control, FF4 D3 early, FP4, FP-ext (ii), FE1, FE2, P2, XC2, R1 as
             written, T1 for FN4. Unexplained: excision removes dust up to 0.67 M of proper time
             before the exact crossing late on (FK, FN4, FNQ) [TO VERIFY].
next:        1. Orchestrator: fresh-context G2 verifier, then the gate review (outbox
                g2-package-ready-for-verifier); answer the verifier's findings
             2. Full-checksum stage verify (--full) before the review
             3. G3 design: core's excision guard test (ah_exc_max_growth = 8, diagnostics =
                true) after core judges q0049; growth law and spike scan with predictions first
blockers:    none for D; the verifier is the orchestrator's to send
needs:       orch: g2-package-ready-for-verifier (2026-11-26), b20-horizon-recheck-null-mesh-
             two-members (answered by ruling 0041 item 4). core: card check q0049 of
             core/restart-finder before using polish_iterations / the excision guard; older:
             lapse-leak-growth-data, newtonian-mode-edges, lapse-excision-criterion,
             particle-energy-and-crossing-record item 2, accretion-diagnostics item 3,
             spike-mass-refinement (outbox/)
offers:      g2long/tools: conv3.py (three-way convergence of the growth), hz_check.py, region_
             norms.py, d4_timing.py, close_by_hand.py, fk_compare.py, np_partial.py, probe_long.py,
             fp_analyse.py, xc_plane.py, slice_mosaic.py, judge_conv.py; stage/G2/rerun_g2.py and
             rerun_plan.json (51 analyses, 14 card runs, 6 processor simulations)
budget:      card-hours this session: 0 submitted; closed this session FNQ 1.90, FL16 3.66 (ran
             2026-11-25). Closed earlier: FK 2.70, FF4 1.34, FE4 0.83, FN4 3.19.
             Processors: ten readings on one core each (seconds to a minute), one note build (2).
card jobs:   none queued or running (q0008-q0011 done).
relaxed lapse: no G2 run uses it (decision 0025 item 3); G3 matter (stage/G2/OPEN.md section 2).
