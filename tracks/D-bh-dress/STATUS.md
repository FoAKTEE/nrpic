# STATUS of D-bh-dress

gate:        G0 PASS (signed 2026-11-20). G1: every item PASS in the lead's judgement (batch 4a,
             2026-11-21); package complete for the orchestrator's independent review (decision 0016
             item 4), not passed (stage/G1/STATUS.md, CHECKLIST.md, OPEN.md). G2 in scouting.
headline:    D-pre-3 is met as decision 0021 item 2 words it: AthenaK's Newtonian mode follows matched
             shells within 0.8 per cent to a/a_i = 16 and its profile lies within 16 per cent of the
             self-similar solution there (Q16; lead checks against two self-similar solutions).
             For G2, the relaxed lapse (lapse_leak) makes the horizon mass grow late even in vacuum
             (+1.3e-3 by 200 M), and with dust (+4.2e-3 by 188 M) not because of the outer faces:
             ES-1GB with the faces at +-384 M grows exactly as ES-1G. Decision 0022 item 3: the null
             test runs with 1+log (vacuum floor 4.8e-5 over 100-200 M, V-1B) or core-v0.7's fix.
last-result: Q16 D-20261121-085652-7e189a2 (secondary_infall); ES-1GB D-20261121-125900-ea4c442 to
             188 M, V-1GB D-20261121-125909-06f856e (g2runs); note v1 main.pdf, 18 pages, checker
             0/0/0 (D-20261121-130510-7e14c5f); lead checks Y1-Y5 held (D-20261121-154912-27e91c6,
             -155215-0611c24; stage/REVIEW-wave3.md section 9); Y1(d) failed by 0.5 per cent
             (null test 1.005e-4 up to 90 M against "below 1e-4"); Y3's guessed cause was wrong
next:        1. When Slurm 4806 (ES-F, running since 16:14Z) finishes: g2runs/tools/finish_g2.sh esf;
                judge P1-P7, (i)-(iii), D1-D4 as pre-registered (flux_tools JOURNAL entry 7). ES-1GB
                ended at 188 M (chain capped at one segment; closed, D-20261121-125900-ea4c442)
             2. Card, after those: ES-1B (ES-1 with 1+log and the faces at +-384 M) against V-1B, the
                null test without lapse_leak (decision 0022); then the M/16 nest of the pair
             3. drift_controls: judge Pb1-Pb5 with its three untracked tools, README; note v2 with
                ES-1G, ES-1GB/V-1GB, Q16, ES-F and run ids; kb's journal data into references.bib
blockers:    core-v0.7 (lapse_leak late growth, decision 0022 item 3) for any lapse_leak run; none for
             G1 (orch's gate review)
needs:       orch: G1 gate review (outbox g1-complete-for-review), close d-pre-3-criterion in
             coord/REQUESTS.md; core: lapse-leak-growth-data (this session), newtonian-mode-edges,
             lapse-excision-criterion, particle-energy-and-crossing-record item 2,
             accretion-diagnostics item 3, spike-mass-refinement (outbox/)
offers:      Einstein-Straus data and exact references (es_runs/make_data.py); vacuum-bubble boundary
             benchmark V-1 (+-192 M) against V-1B (+-384 M); lapse_leak regression pair ES-1GB/V-1GB
             (g2runs/inputs); ES-F data (flux_tools/esf_data.py, D-20261119-145022-2208a19); Kerr
             spike reference (spike/kerr_lib.py); Newtonian-mode infall references with the measured
             mesh kernel at a vertex and at a cell centre (secondary_infall/nm_shells.py)
budget:      card-hours (nrpic-run budget, 2026-11-21 16:40Z): G1 4.41 used; G2 2.39 used (ES-1GB
             closed: 0.83), 1.97 reserved (ES-F), 25.64 left. This lead session used 0 card-hours
             and one core. One D job: Slurm 4806 (ES-F), running.
