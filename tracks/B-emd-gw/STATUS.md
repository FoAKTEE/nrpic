# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package current (batch 21): C4, C6, C7, C10,
             C12, C13, C16, C19, C20 PASS, C8 NA (0013), the rest OPEN (stage/G2/OPEN.md maps each
             to its queue entry or processor work). G2 not met.
headline:    Same particles, full GR against the Newtonian mode: halo counts agree in both gauges
             and the ten largest masses to 2.5-2.8 per cent (median, a = 121); the largest halo is
             lighter by 2-5 per cent with zero shift and heavier by 7-11 with the Gamma driver, so
             FoF masses depend on the spatial gauge (R23) and the shift does not bring them closer
last-result: batch 21 (2026-11-25): Newtonian analysis B-20261125-122434-060d53d closed;
             compare_newton.py against both gauges (B-20261125-165836-70b17b6, -165845-0621554):
             N2, N3 hold; N4 fails in both parts. Quasi-static part: analyze_gr.py deposits the
             GR particles' rest-mass weight (spread 2.8 per cent) as mass (B-20261125-170535-84c9ba5;
             with equal masses GR/Newton 1.01-0.94 at a = 2.3-36); the GR metric agrees with the
             Newtonian particles within 11 per cent at a = 4-36 in both gauges. Radiated part:
             0.29 against a factor 2 (B-20261125-172136-3e920ab), cause not tested. GN1 refuted.
             Note: G2 section, fig_pop_gauge, G2 schematics, ledger Table VIII
             (B-20261125-171148-563a6f0); stage/G2/REPRODUCE.md.
running:     nothing on processors
cards:       shared queue (cards held by another partition until about 2026-11-26, 0041 item 6):
             q0007 pop_s014_gr256 (mesh leg, B-20261125-093500-242d3a3, Slurm 5283 pending,
             segment 2 of 5); q0042 pop_s014_gr_p8_cont (P8C1-2, waiting); q0044 pop_s028_gd2
             after q0042 (S1-S3, waiting); all priority 2; nothing partial read
next:        1. analyze_gr.py without the rest-mass weight in hqs_particles (one flag), rerun on
                the zero-shift and gauge-leg runs, prediction first; redo A1-A3, GD3 particle parts
             2. read q0042, q0044, q0007 when they end (P8C, Q1; S1-S3; M1-M4); then C1-C3, C11
                in the note and a fresh G2 verifier (C18)
             3. C15: split analyze_b/analyze_f/analyze_gr/analyze figures into one script each;
                a proper-distance halo mass (gauge of FoF, R23); N4 radiated part at one cadence
needs:       core: parameters added at a restart (outbox 20261125T121932Z); Fourier Newtonian
             solver with the threaded build (20261124T173601Z). kb: claim 861 [TO VERIFY].
             orch: incremental checksums served (0039 item 5)
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); population/scripts/
             compare_newton.py, vel_check.py (same particles, one estimator), n4_band.py; finding
             for every track that deposits GR particle files with a Newtonian estimator: the
             file's masses carry the rest-mass weight W psi^6 (R25)
budget:      card-hours toward G2: 4.27 used (no card this session); mesh leg in the queue (about
             0.84 in its first segment); queued ceilings 5 (q0007), 0.5 (q0042), 0.5 (q0044);
             G1 1.69; allotment 40 (0014)
