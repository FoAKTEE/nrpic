# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package current (batch 28): C4, C6, C7, C9,
             C10, C12-C16, C19, C20 PASS; C8 NA (0013); C1 (shearing-dust L2) and C3 (constraints
             in the mesh) FAIL as written, rulings requested; C2, C11 wait for a running
             analysis; C5, C17 for its paragraph; C18 for a verifier. G2 not met.
headline:    The shifted (Gamma-driver) population box passes the finer mesh: 256^3 to a = 143
             with K_max < 0 (q0060, GM1). The late constraint level follows particles per cell,
             not spacing (Hr 128^3/256^3 only 1.11 at a = 141, GM4 refuted; 8 per cell lowers it
             1.6x, Mr 2.9x). The 0.028 box matches the 0.014 box at equal stage sigma1 a (S2, S3).
last-result: batch 28 (2026-11-26 13:20-): GM1 holds, GM4 refuted (B-20261126-212502-e9e4f4e);
             M2 counts hold, largest masses fail at a = 64-72 (1.35-1.37); M3 holds to a = 50,
             1.214 at a = 100, high-k part holds (4-23x with mesh) (B-20261126-212541-b647c59);
             Q1 high-k part refuted (0.98-1.01); S2, S3 hold at a' = 2a (B-20261126-212604-a508e94).
             C15 done: one script per G2 figure, pixel-identical (B-20261126-213450-f833a78).
             Note v3: section VI, abstract, summary, ledger rows; compiled, checker clean
             (B-20261126-213742-dcee645).
running:     processor analysis B-20261126-212212-c54d979 (GM2, GM3: 256^3 shifted strain and
             halos, equal masses, 5 cores, started 13:22 PST); close with `nrpic-run finish`
cards:       nothing queued or running for B (q0060 done: 3.75 card-h, predicted 3.5-5)
next:        1. close B-20261126-212212-c54d979; compare_legs.py --base <gauge leg
                B-20261125-115558-2ab4161/analysis_gr_gd.json> --halo-base
                <B-20261126-022407-87e8803/analysis_gr_gd.json> --leg m256gd:<json>; judge GM2,
                GM3; C2 and C11 then; the GM paragraph in note section VI, timeline schematic
             2. apply the orchestrator's rulings on C1 (L2) and C3 (outbox 20261126T213945Z)
             3. fresh verifier for C18 (requested), then nrpic-stage verify --full and report
needs:       orch: rulings C1/C3; a verifier for C18. core: parameters added at a restart
             (NEXT_SOURCE item 1); Fourier Newtonian solver with the threaded build.
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); analyze_gr.py --equal-mass;
             compare_legs.py --halo-base; findings for all: GR particle files carry the
             rest-mass weight (R25); zero shift fails in resolved periodic cores (R26); the
             constraint level after collapse follows particles per cell (R27)
budget:      card-hours toward G2: 11.61 used (q0060 3.75 this session); G1 1.69; allotment 40
             (0014); nothing submitted this session
