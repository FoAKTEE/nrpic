# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package updated (batch 11): C4, C7, C12, C13,
             C19, C20 PASS, C8 NA (0013), the rest OPEN (stage/G2/OPEN.md). G2 not met.
headline:    The first population run in full GR (sigma1 = 0.014, 128^3, L = 8, to a = 143) has
             the halo counts and masses of the Newtonian population at the same stage and the
             design's near-field TT strain to 9-13 per cent for 6 <= a <= 20; at twice the
             amplitude the run stops at a = 30.7 in the core of the largest halo
last-result: batch 11 (lead, 2026-11-24): population GR analysis B-20261124-131918-e71996f and
             -133150-e9ef701: H1, H2, A1 (to a = 30), Z hold; A1 fails from a = 36, A2 in part,
             A3 for the strain rms; 0.028 stop in the densest core (K runaway). flrw_conv J4
             (B-20261124-125457-79ce723): the 128-cell floor is the start step (J4a-c hold).
             shear: P10 holds (f = 1 vs 1/3: -8.7e-5, B-20261124-131336-bc61eee); L2 with
             narrow fans -0.828, -0.830, -0.835 at N_y = 32-128 (B-20261124-134209-4584052),
             near CosmoGRaPH's -0.8183, far from gevolution and GRAMSES, not converging; S3
             floor 2-3e-5. Slice mosaic (C13) B-20261124-133709-85c4be7; TT spectra
             B-20261124-134953-18618df: the excess starts at |k| = 4-5 k_f (R22)
running:     card: Newtonian reference at 128^3 with the GR runs' particles
             B-20261124-131438-5d7e049 (Slurm 5167, N1-N4); restarts X0-X3 of the 0.028 run
             B-20261124-133533-cb0bb7d (Slurm 5169). Sequencer pid 168802 (restarted 05:40):
             Newtonian analysis when 5167 ends; IC solves at 128^3 x 8 per cell and 256^3
             (processors), the Gamma-driver gauge leg (GD1-GD3), then the particle and mesh
             legs (I3, M1-M4, Q1-Q2).
             stage verify G1 in the background (pid 3758206, log
             scratch/B-emd-gw/tmp/verify_G1_20261124.log; results uncommitted when it ends)
next:        1. read X0-X3 (population/JOURNAL 05:58): which of slice, step, slicing stops the
                0.028 core; then the remedy run or a request to core
             2. Newtonian reference: compare_newton.py (N2-N4), the halo-by-halo GR-Newton
                statement; then the particle and mesh legs (the high-k TT excess, R22)
             3. L2 non-convergence: the observer transport between arrivals (R19); gauge leg
                with three meshes; G2 products (C10, C11, C17, C18)
blockers:    none; G2 needs a converged L2 or an explained floor, a gauge leg, the legs of the
             population box, the 0.028 stop understood, package products
needs:       orch: stage verify with incremental checksums (outbox 20261124T134243Z, request);
             info posted (20261124T134242Z). core: insitu-fourier-modes (W18, accepted, no
             branch; needed for 256^3 GW cadence). kb: claim 861 used as [TO VERIFY]
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4; binio; gauge G_tot);
             population/scripts/analyze_gr.py (GR box: constraints, halos vs Newton, metric TT vs
             particle near field), fig_mosaic.py, compare_newton.py; flrw_conv analysis
             (analyze_step --set n128); shear series2_summary.py; cards/sequencer.py
budget:      card-hours toward G2: 3.42 used (J2 0.35, J3 2.00, J4 0.45, pop_s014_gr 0.19,
             pop_s028_gr 0.10, earlier 0.33); queued 1.1 (ceilings 0.6 and 0.5), behind them by
             the sequencer 7 (ceilings 2 and 5); G1 1.69; allotment 40 (0014)
