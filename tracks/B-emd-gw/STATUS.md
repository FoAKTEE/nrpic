# STATUS of B-emd-gw

gate:        G0 PASS (signed 2026-11-19, tag stage/B-emd-gw/G0-pass-20261119); G1 not met:
             criteria 1 and 2 met, 3 struck (0013), schematics and note v2 PASS; one item owed,
             C18 narrowed to ledger lines 34-36, 49-63, 70-71, 124, 199, 217 (stage/G1/OPEN.md)
headline:    Both GW diagnostics recover oblique flat waves (k = 2 pi (1,1,1) and (1,2,0)) and a
             tensor mode of the expanding matter-era box with the errors the code's stencils and
             integrator predict, read independently three times; the first source follows its
             second-order strain and converges in particle number and mesh before shell crossing
last-result: lead batch 4a: L4 F2 remeasured with verifier3's code equals the waves values to
             <= 2.9e-4 relative, orders to the third digit; L5 time part of the X error at
             N = 64 1.42992e-7 (run B-20261121-154933-a79da09); L6 first_source round-3
             analyses reproduce byte for byte (-155017-9aec47a); L7 verifier_c18's 116
             recomputed numbers reproduce (-155045-343bee1; 103 within 1 per cent); all four
             predictions held; stage/REVIEW-wave3.md section "Batch 4a"
next:        1. verifier_c18b: fresh verifier of the remaining ledger lines (or orch's ruling
                that the wave-1 pancake rows move to G2); then nrpic-stage report G1 and the
                gate request
             2. note v3: wordings of verifier3 and verifier_c18 (rows 101, 118-119, 125, 168,
                197, the (1 + eps^2) range), registered run_all, compile, pages
             3. G2 legs: flrw_conv (analyse J1, P1; submit J2, J3), shear (nprobe fix, smoke run,
                series), the Newtonian embedded ellipsoid with core-v0.6's group moments
blockers:    G1 waits for the verifier package or a ruling (requests to orch, 20261121T155410Z)
needs:       orch: c18-remaining-rows, next-batch-packages-of-b, note-pdf-size; core:
             insitu-fourier-modes (accepted, W18; no branch yet); kb: claim-2312-12499-delta-factor
             (waits for kb's claims package) (tracks/B-emd-gw/outbox/)
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio reads single and double
             precision; gauge: G_tot and tt_strain, commit 57232954); waves/wlib (exact flat
             oblique wave and matter-era tensor mode, RK4()4[2S] predictor, linearized Z4c
             symbol model); first_source tools (null prediction, eps^2 advance test, P16'
             comparison); all on track/B-emd-gw
budget:      2.51 card-hours used of 40 (G1 1.69, G2 0.34, wave 1 0.48); this session 0;
             no card job of B queued or running
