# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2: package complete for an independent review
             in the lead's judgement (batch 34; stage/G2/OPEN.md): 19 of 20 items PASS or NA,
             C18 (fresh verifier) OPEN and requested; C1 and C3 judged PASS under decision 0046
             item 2 with the failures on record; C2 PASS for the strain with the halo
             catalogue's mesh failure (GM3) on record, ruling requested. Not signed.
headline:    In the Gamma-driver gauge the band strain |k| <= 8 k_f of the population box is the
             same on 128^3 and 256^3 to 1.1 per cent up to a = 64 and 2.8 per cent up to a = 132
             (B-20261127-232236-7ab7aa2), and at a fixed eight particles per cell the late
             constraint means fall 1.6-2.3 times (H) and 1.7-2.2 times (M) when the spacing
             halves (64^3 against 128^3; B-20261127-232628-1361e3b), against 1.05-1.4 at one per
             cell.
last-result: batch 34 (2026-11-27 15:21-15:45 PST): C3 step 1 data checked (146 modes, same
             sigma1, H residual 1.2e-12; B-20261126-222552-2e44186); q0070 ran (0.038 card-h);
             C3b holds, C3a fails before a = 31 but is not refuted; GM2 band part holds, Omega
             part 0.85 (predicted 1.0-2.0) fails as written; GM3 fails in part (counts at
             a = 121, largest masses at a = 64 and 121); note v4 with Table VIII
             (B-20261127-232833-5891f77), checker and compile clean.
running:     nothing of B on cards or processors, apart from the detached checksum pass
             `nrpic-stage verify B-emd-gw G2 --full` (writes stage/G2/VERIFY_RESULTS.md and
             .json; started at the end of batch 34, see HANDOFF)
cards:       nothing queued (q0070 done, job 5524)
next:        1. the fresh verifier for C18 (orchestrator); answer its findings with
                registered runs
             2. read the --full verify result; commit VERIFY_RESULTS if it changed; regenerate
                STAGE_REPORT (nrpic-stage report)
             3. G3 scope: population runs at eight particles per cell in the Gamma-driver
                gauge; a 256^3 member at eight per cell if the GM3 ruling asks for it
needs:       orch: fresh verifier (C18); ruling on the halo catalogue at one particle per cell
             (outbox 2026-11-27T234330Z, two posts).
             core: parameters added at a restart (NEXT_SOURCE item 1).
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); analyze_gr.py --equal-mass;
             compare_legs.py --halo-base; judge_c3.py (constraint histories of a mesh pair);
             shear/scripts/crossing.py; findings: GR particle files carry the rest-mass weight
             (R25); zero shift fails in resolved periodic cores (R26); constraints converge
             with the mesh only at fixed particles per cell (R27); halo counts at one particle
             per cell are not mesh-converged (R29)
budget:      card-hours toward G2: 11.65 used (0.038 this session); G1 1.69; allotment 40 (0014)
