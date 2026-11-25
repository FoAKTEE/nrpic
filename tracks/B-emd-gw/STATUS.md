# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package current (batch 17): C4, C7, C10, C12,
             C13, C19, C20 PASS, C8 NA (0013), the rest OPEN (stage/G2/OPEN.md maps each to its
             queue entry). G2 not met.
headline:    The population's late-time high-k TT energy in full GR was the zero-shift
             coordinates: with a Gamma-driver shift it is 950 times smaller at a = 121 and the
             metric strain follows the particles' quasi-static near field (correlation >= 0.93) to
             a = 132; the 0.028 box's stop at a = 30.7 is the zero shift too (the shift passes it)
last-result: batch 17 (2026-11-25): gauge leg B-20261124-210431-6bf48af to a = 143 (analysis
             -115558-2ab4161, comparison -120818-1dfae55): GD1 holds (time part fails), GD2 counts
             hold, largest masses +10 to +16 per cent (fails), GD3 holds. X0-X3
             (B-20261124-210432-6c4d005, analysis B-20261125-115619-ad8b3f4): X0, X1 repeat the stop
             (9.0865, 9.0787), X2 passes to a = 36 (refuted), X3 not run (restart refused
             dt_lightspeed). Particle leg (8 per cell) cut at a = 94.8 by the chain cap: Mr_mean
             2-5 times lower, strain unchanged, high-k excess unchanged (Q1 part 2 fails), counts
             hold (analysis -115657-91b61ec, comparison -121830-9ecb59c). I3 holds (both solves).
running:     processors: nrpic-run finish of B-20261124-210431-6bf48af, -223926-33194d9,
             -210432-6c4d005, -172958-fc4a2cf, -172958-73b0662 (hashing 9-62 GB each; may be cut at
             session end: rerun `nrpic-run finish <id>` for any still 'submitted');
             stage verify G2 --no-checksums (scratch/B-emd-gw/tmp/stage_verify_g2_b17.log)
cards:       shared queue: q0007 pop_s014_gr256 (mesh leg, B-20261125-093500-242d3a3, Slurm 5283
             pending, segment 2 of 5, t = 4.5 after one segment); q0042 pop_s014_gr_p8_cont
             (P8C1-2, waiting); q0044 pop_s028_gd2 after q0042 (S1-S3, waiting); all priority 2
next:        1. Newtonian reference (runs done, exit 0): analyze.py on newton_s014/s028 and
                compare_newton.py against the GR runs, now in both gauges (N2-N4, R23)
             2. read q0042, q0044, q0007 when they end (P8C, Q1 at a = 141; S1-S3; M1-M4); decide a
                shifted-gauge run at a second mesh for the gauge leg of C2/C11
             3. G2 writing: note sections (C17), schematics (C16), one script per figure (C15),
                reproducibility list (C6); shear L2 amplitude without stream crossing (R19)
blockers:    card queue (another partition's priority); nothing else
needs:       core: parameters added at a restart (outbox 20261125T121932Z, new); Fourier
             Newtonian solver with the threaded build (20261124T173601Z). orch: stage verify with
             incremental checksums (20261124T134243Z). kb: claim 861 [TO VERIFY]
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); population/scripts/analyze_gr.py,
             compare_legs.py (legs of a GR box against a base), analyze_stop028.py; shear
             ppc_summary.py; finding for Tracks A and C: a zero-shift periodic box crunches in
             coordinates in halo cores; a Gamma-driver shift passes (R21)
budget:      card-hours toward G2: 4.28 used (earlier 3.42; batch 17 closed: gauge leg 0.185,
             X0-X3 0.05, particle leg 0.62); mesh leg running (about 0.84 in its first segment);
             queued ceilings 5 (q0007), 0.5 (q0042), 0.5 (q0044); G1 1.69; allotment 40 (0014)
