# STATUS of B-emd-gw

gate:        G0 package submitted 2026-11-15 (stage/G0/; working note, schematics and
             independent verifier still owed, stage/G0/OPEN.md); G1 not met (stage/G1/STATUS.md)
headline:    First GW source fixed (crossed waves (1, eps, 0), eps = 0 the plane-symmetric
             null); periodic Z4c and the GW diagnostics validated on AthenaK vacuum output;
             full-GR pancake runs through shell crossing; every wave-1 result reproduced bit
             for bit by the lead
last-result: lead re-check B-emd-gw-20261115-131016-03b1119 (clean export, all five
             packages identical; AthenaK re-executions byte-identical except restart padding);
             independent derivations B-emd-gw-20261115-131027-03b1119 (item 3, crossed-wave
             coefficient -(5/6) phi_x phi_y real amplitude, ZA energy, generator bug);
             pancake B-emd-gw-20261115-115217-69ab1db, -115902-a3207d7 (two per cell needed)
next:        1. Oblique linear wave and an expanding-box wave with both diagnostics once core
                fixes z4c_linear_wave (spec periodic_z4c/inputs/lw_3d.athinput)
             2. First-source scouting at 64^3: null (eps = 0) and eps scan at delta = 0.01,
                two per cell, rst dumps at d tau = 0.1, gw_diag on them (about 1 card-h)
             3. Working note v0 and the two G0 schematics; ask a fresh verifier for G0
blockers:    oblique wave: core (generator sign fix); Newtonian N-body baseline: core
             (Newtonian mode on main); noise-floor null: lattice-jitter option (core or B
             proposal branch)
needs:       core: z4c-linear-wave-polarization, newtonian-mode-for-track-b,
             gw-analysis-output, lattice-jitter-option, thin-periodic-boxes,
             initial-data-tt-part, weyl-output-timing, awa-generators;
             orch: track-b-criteria-under-0010, derivations-item3-amendment,
             cosmo-plan-particles-per-cell, harness-runs-and-venv;
             kb: track-b-sources; A-emd-pbh: matter-era-slicing
             (all in tracks/B-emd-gw/outbox/20261115T1340Z__*)
offers:      gw_diag (tracks/B-emd-gw/gw_diag/gwdiag: TT projection, rho_K, spectra,
             helicity, E/B/Psi_4, AthenaK rst/bin/NRFIELD readers; 14 tests);
             periodic_z4c record of lapse and shift options (tables/gauge.md) and AthenaK
             readers; exact Zel'dovich plane-wave reference (verify_cosmo/scripts/zeldovich.py);
             ZA/ellipsoid GW baseline with acceptance numbers for the Newtonian mode
             (baseline/BASELINE.md 4.2); all on track/B-emd-gw
budget:      0.48 GPU-hours used of 40 (decision 0006); processors only otherwise
