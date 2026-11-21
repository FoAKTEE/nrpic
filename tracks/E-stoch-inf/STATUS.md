# STATUS of E-stoch-inf

gate:        G0 PASS (signed 2026-11-20, coord/GATES.md). G1: all 18 checklist items PASS in the
             owner's judgement; package complete for the independent gate review (decision 0016
             item 4); NOT passed until reviewed and signed. G2 in progress (USR on the cards).
headline:    The slow-roll case of arXiv:2512.14649 passes A1-A3, A5-A7 and A4' (decision 0021) up
             to 256^3, verified independently; the ultra-slow-roll case runs to N_f at 256^3 on one
             card in 0.617 card-hours and follows linear theory per mode to 1.1e-4 (odd part), with
             a second-order part 2.5e-4 of the first and a one-point skewness of +0.0015.
last-result: - note (batch 2b): G1 products C8, C9, C13-C15: schematics, four G1 data figures with one
               script each, main.pdf v1 (16 pages, checker clean), G1 ledger of 45 rows (run
               E-20261121-080840-6112292).
             - usr (batch 2b): group 1 64^3/128^3 (E-20261120-222621-ba66218): U-A0..U-A3 pass;
               U256/U256m in P1's set-up (E-20261121-075255-8cf90e7, -085221-1f579fe): U-A0, U-A1,
               U-A3, U-A5, one-point pass, U-A2 on the odd part 1.09e-4; single-run U-A2 and U-A4
               FAILED as pre-registered; the lockstep record carries RK4 phase error k^5 dt^4/600.
             - Lead batch 3: every analysis of note and usr rerun (E-20261121-130021-0140e4e): all
               leaves and PNGs identical except 13 lockstep-reference leaves (at most 8.6e-4
               relative, BLAS thread count; no verdict changes); own code on the raw dumps
               (E-20261121-130236-e39e143) reproduces even/odd 2.533e-4, skewness, rms, max and the
               group-1 halving factors; ledger cross-check: 27 of 40 track rows agree with
               independent values, 13 track-only (stage/REVIEW-wave3.md B4).
next:        1. Independent G1 gate review (orch; outbox g1-package-complete).
             2. window: analyse job 4740 against W1-W8 (processors); P256 on the release card build
                .work/build_gpu_v05 (0.5 card-hours) for risk R1.
             3. After orch's ruling on U-A2'/U-A4': USR criteria into SCOPE, stage/G2 collect; USR runs
                on release core-v0.5; a4res analysis when job 4798 has run.
blockers:    G1: none of the owner's (gate review by orch). G2: ruling on U-A2'/U-A4' (orch); window
             analysis and a4res job 4798 (pending in the shared queue).
needs:       orch: g1-package-complete, usr-acceptance-after-data, schedule-window-r1-a4res (outbox
             2026-11-21 13:10Z-13:4xZ); earlier a4-ruling-with-verifier (answered by decision 0021).
             core: lockstep-record-substep (request, not blocking).
offers:      - SR ladder 32^3-256^3, two seeds, with verdicts: ladder/ (track/E-stoch-inf).
             - USR card runs 64^3-256^3 with mirrored and halved pairs, analysis and lockstep law: usr/.
             - Working note v1 with G1 sections and ledger: note/main.pdf.
             - Independent verifier tools (reader, Philox, MS, R^NR, odd/even split): g1verify/scripts/.
             - Lead's check code: stage/review3/scripts/ (reruns, own-code checks).
             - Reproduction spec with errata: spec/SPEC.md; MS references: spec/ref/.
             - Stochastic delta-N solvers and reference statistics: langevin/ (to A-emd-pbh).
             - Noise validator A0-A15: noise/ (to core, C-sidm).
budget:      G1 1.96 of 10 card-hours used; G2 1.39 (usr) + 0.38 (window job 4740) used, a4res job
             4798 pending (cap 0.5); this session 0 card-hours (processors only, at most 5 cores).
