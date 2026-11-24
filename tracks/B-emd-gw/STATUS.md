# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121); G1 verify rerun formally on 2026-11-24: PASS.
             G2 package current (batch 11b): C4, C7, C10, C12, C13, C19, C20 PASS, C8 NA (0013),
             the rest OPEN (stage/G2/OPEN.md); its verify fails only on open runs. G2 not met.
headline:    The first population run in full GR (sigma1 = 0.014, 128^3, L = 8, to a = 143)
             has the Newtonian population's halo counts and masses at equal stage and the
             design's near-field TT strain to 9-13 per cent for 6 <= a <= 20; the shearing-dust
             L2 case does not converge in the mesh in this code
last-result: batch 11b (resumed lead, 2026-11-24 09:23-): shear series 6 (B-20261124-140856-911ded9,
             summary -172643-d1e88c7, figs/fig_ppc.png): L2 at 4 per cell along y -0.822, -0.831,
             -0.839 at N_y = 64, 128, 256 (differences 9.4e-3, 7.9e-3, order about 0.25, away
             from CosmoGRaPH's -0.8183); the prediction held only as written. Stage verify G1
             PASS, G2 FAIL only on four open runs (stage/G{1,2}/VERIFY_RESULTS.md, 14:57Z).
             Batch 11 (earlier today): population GR analysis -131918-e71996f (H1, H2, A1 to
             a = 30, Z hold; A1 fails from a = 36); the 0.028 run stops at a = 30.7 in a halo
             core; flrw_conv J4 closed; P10 holds; L2 particle limit at N_y = 64 about -0.820
running:     processors: Newtonian reference newton_s014 and newton_s028 at 128^3
             (B-20261124-172958-fc4a2cf, -73b0662; 33 s per step, end about 22:30 PST 2026-11-24;
             close by hand with nrpic-run finish, the sequencer is retired). Initial data of the
             particle and mesh legs finished (B-20261124-135029-3fe13f6, -135030-b54972f; outer
             change 8.3e-10 and 8.4e-10, H residual 2.1e-11 and 3.2e-11; I3 not yet judged).
cards:       shared queue only (decision 0033; batch 12, 13:05 PST): q0004 gauge leg (job 5208,
             B-20261124-210431-6bf48af), q0005 X0-X3 (job 5209, B-20261124-210432-6c4d005),
             q0006 particle leg after q0005, q0007 mesh leg after q0004; all priority 2 (G2).
             Cancelled while waiting at 12:00: 5169 (-133533-cb0bb7d), 5176 (-173547-11afdaf),
             closed as stopped; cards/sequencer.py retired (do not restart it)
next:        1. read the Newtonian reference (N1p, N2-N4: compare_newton.py against the GR run),
                the halo-by-halo GR-minus-Newton statement; X0-X3 when the cards return
             2. read the gauge, particle and mesh legs of the GR box (GD1-GD3, Q1-Q2, M1-M4):
                what the high-k TT excess after halo formation is (R22)
             3. shear: design and predict an amplitude between M2 and L2 without stream crossing
                before t_A at three meshes (R19); G2 products C11, C17, C18, C6
blockers:    card queue (another user's priority partition; cap of five jobs, 0033); nothing else
needs:       core: Fourier Newtonian solver tested with the threaded build (outbox
             20261124T173601Z, request); insitu-fourier-modes (W18, accepted, no branch; for the
             256^3 GW cadence). orch: stage verify with incremental checksums (outbox
             20261124T134243Z). kb: claim 861 used as [TO VERIFY]
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio; gauge G_tot);
             population/scripts/analyze_gr.py, fig_mosaic.py, compare_newton.py; flrw_conv
             analysis (analyze_step --set n128); shear ppc_summary.py (particle and mesh legs)
budget:      card-hours toward G2: 3.42 used (J2 0.35, J3 2.00, J4 0.45, pop_s014_gr 0.19,
             pop_s028_gr 0.10, earlier 0.33); in the shared queue 9.5 (ceilings: gauge leg 2,
             X0-X3 0.5, particle leg 2, mesh leg 5); G1 1.69; allotment 40 (0014). Processors:
             2 cores busy (two Newton runs)
