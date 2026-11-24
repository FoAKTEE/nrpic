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
             (B-20261124-172958-fc4a2cf, -73b0662; 33 s per step, about 13 h, end about 22:30
             PST), initial-data solves at 128^3 x 8 per cell and 256^3 (B-20261124-135029-3fe13f6,
             -135030-b54972f; outer 16 and 13 of up to 36 at 09:30). Cards (held by the priority
             partition until about the morning of 2026-11-25): X0-X3 restarts of the 0.028 run
             (Slurm 5169, B-20261124-133533-cb0bb7d), gauge leg pop_s014_gr_gd (Slurm 5176,
             B-20261124-173547-11afdaf). Sequencer pid 168802 alive: Newtonian analysis after the
             processor runs; particle and mesh legs (card chains) after their initial data
next:        1. read the Newtonian reference (N1p, N2-N4: compare_newton.py against the GR run),
                the halo-by-halo GR-minus-Newton statement; X0-X3 when the cards return
             2. read the gauge, particle and mesh legs of the GR box (GD1-GD3, Q1-Q2, M1-M4):
                what the high-k TT excess after halo formation is (R22)
             3. shear: design and predict an amplitude between M2 and L2 without stream crossing
                before t_A at three meshes (R19); G2 products C11, C17, C18, C6
blockers:    cards held by another user's priority jobs until about 2026-11-25 morning
             (decision 0032 item 2); nothing else
needs:       core: Fourier Newtonian solver tested with the threaded build (outbox
             20261124T173601Z, request); insitu-fourier-modes (W18, accepted, no branch; for the
             256^3 GW cadence). orch: stage verify with incremental checksums (outbox
             20261124T134243Z). kb: claim 861 used as [TO VERIFY]
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio; gauge G_tot);
             population/scripts/analyze_gr.py, fig_mosaic.py, compare_newton.py; flrw_conv
             analysis (analyze_step --set n128); shear ppc_summary.py (particle and mesh legs);
             cards/sequencer.py
budget:      card-hours toward G2: 3.42 used (J2 0.35, J3 2.00, J4 0.45, pop_s014_gr 0.19,
             pop_s028_gr 0.10, earlier 0.33); reserved 2.47 (5169 ceiling 0.5, 5176 ceiling 2;
             5167 cancelled before it ran); behind them by the sequencer 7 (ceilings 2 and 5);
             G1 1.69; allotment 40 (0014). Processors: 4 cores busy (two solves, two Newton runs)
