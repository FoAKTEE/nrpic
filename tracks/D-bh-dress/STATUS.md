# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md). G2 in scouting: long card runs queued (g2long), not judged.
headline:    With dust filling the bubble (ES-F, M/8, 1+log, faces +-192 M) the horizon grows by
             0.25 M in 200 M and follows the exact LTB mass of the shell at the horizon to 0.25 per
             cent over shell proper times 0-250 M; the growth closes against the removed flux to
             1.5e-3 after the vacuum control's finder history is subtracted. This meets the G2
             matter criterion of the track sheet at one resolution and one boundary; the long runs
             of batch 5 repeat it to 500 M with the faces at +-768 M, with the null test beside it.
last-result: ES-F D-20261121-144631-aa7ce9b (0.81 card-h, one segment), analyses
             D-20261121-202137-7bc388e, -202142-ce0f509; judged in g2runs/JOURNAL.md entry 10 and
             stage/REVIEW-wave3.md section 11: every prediction of flux_tools entry 7 held except
             P3 (i) (one finder sample at t = 0.5 M) and P3 (ii-tau) (predicted to fail, holds).
             ES-F table extended to 1340 M for the +-768 M mesh: D-20261121-203042-82deeec.
next:        1. When the chains end (HANDOFF "Card runs"): finish each run, judge N, G and the
                predictions V1-V4, E1-E4, F1-F6, H1-H4 of g2long/JOURNAL.md entry 1 (analysis
                tools: g2runs/tools/compare_horizons.py, flux_tools/esf_analyse.py,
                g2runs/tools/esf_criteria.py with --control the V-1L finder file)
             2. Q16-256 (secondary_infall, processors): analyse against QR1-QR5 (JOURNAL 20:36Z)
             3. G2 package: stage/G2 collect with ES-F, the long runs, Q16-256; note v2
blockers:    none for the queued runs; core-v0.7 (lapse_leak mitigation, decision 0025 item 3)
             only for any lapse_leak run, none planned
needs:       core: lapse-leak-growth-data, newtonian-mode-edges, lapse-excision-criterion,
             particle-energy-and-crossing-record item 2, accretion-diagnostics item 3,
             spike-mass-refinement (outbox/); orch: none new (g1-complete-for-review answered by
             the gate review)
offers:      Einstein-Straus data and exact references (es_runs/make_data.py); ES-F data with the
             table to 1340 M (D-20261121-203042-82deeec); input builder for +-768 M meshes and an
             M/16 nest (g2long/tools/make_inputs.py); a held-job sequencer for chains
             (g2long/tools/sequencer.sh); vacuum control V-1B and lapse_leak pair ES-1GB/V-1GB
             (g2runs/inputs); Kerr spike reference (spike/kerr_lib.py); Newtonian-mode infall
             references (secondary_infall/nm_shells.py)
budget:      card-hours (nrpic-run budget before this session): G1 4.41 used; G2 3.20 used,
             26.80 left. This session registered five chains with caps 3.5 + 4.0 + 4.0 + 5.0 + 6.0
             = 22.5 card-hours toward G2 (expected ~14: R1 2.2, R2 2.5, R3 2.6, R4 ~3.0, R5
             ~3.5), announced here (decision 0014); 0 card-hours used yet. Processors: smoke runs
             1 core each (four, minutes); Q16-256 six threads for 1-2.5 h.
card jobs:   R1 V-1L Slurm 4830 and R2 ES-1L 4831 pending; R3 ES-FL 4833, R4 V-1L16 4834,
             R5 ES-1L16 4835 held, released by the sequencer in scratch/D-bh-dress/g2long_seq/.
