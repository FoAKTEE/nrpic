# STATUS of B-emd-gw

gate:        G0 PASS (signed 2026-11-19, tag stage/B-emd-gw/G0-pass-20261119); G1 not met:
             criteria 1 and 2 met, 3 struck (0013), schematics and note v2 PASS; one item owed,
             C18 (ledger rows not yet recomputed by an independent verifier) (stage/G1/OPEN.md)
headline:    Both GW diagnostics recover an oblique flat wave and a tensor mode of the expanding
             matter-era box with the errors the code's stencils and integrator predict, read
             three times independently; the first source follows its second-order strain, and
             its departure falls as delta^2 (window to a = 34-42 at delta = 0.0025)
last-result: lead batch 2a: L1 the waves and verifier3 readings agree to 1 percent except X
             plus at N >= 48; L2 a third reading of X at N = 64 gives the waves value
             1.5384e-7 (run B-20261121-063617-6183015); L2b the difference is a definition
             (modulus vs part in phase with the exact mode; spatial quadrature 1.6e-8, run
             B-20261121-063835-826c461); truncation error 1.40e-7 (cross; x10 both);
             2312.12499 lines 324 and 581 differ by 3 in delta (reading); stage/REVIEW-wave3.md
next:        1. verifier4: independent recomputation of the remaining ledger rows (C18; no
                card time), then nrpic-stage report G1 and the request for the gate review
             2. close round 1: waves (F2, XS analysis; gauge module of gw_diag; README
                wordings), first_source (P12, P13, (1 + eps^2) test, 32^3 nulls), note v3
                (ledger rows 101, 118-119, 168)
             3. G2 legs: flrw_conv (J1 and P1 ran; J2, J3 to submit; analysis), shear (deck fix,
                smoke run, series); population: full-GR timing and periodic id_solve at L = 8
blockers:    none for G1 but the verifier package; N2 (embedded ellipsoid) waits for core's
             per-species history; population L = 16 data (test core-v0.4 id_solve on the torus)
needs:       orch: g1-verifier-for-c18, note-pdf-size; core: insitu-fourier-modes (+ correction),
             newtonian-species-history, newtonian-laplacian-order; kb:
             claim-2312-12499-delta-factor (tracks/B-emd-gw/outbox/20261121T0654*, 20261115T19*)
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio reads single and double
             precision bin output); first_source/fslib/gauge.py (second-order spatial-gauge
             piece G_tot, confirmed term by term and on exact pure-gauge data by verifier3);
             waves: exact references of a flat oblique wave and of the matter-era tensor mode,
             the code's RK4()4[2S] predictor and the whole linearized Z4c symbol model
             (waves/wlib); all on track/B-emd-gw
budget:      2.48 card-hours used of 40 (G1 1.69, G2 0.31, wave 1 0.48); this session 0;
             no card job queued or running
