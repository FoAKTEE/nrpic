# STATUS of B-emd-gw

gate:        G0 package resubmitted 2026-11-15 (stage/G0/; every checklist item PASS or NA
             in the lead's judgement, harness verdict FAIL on the verifier file name and
             wave-1 manifests, requests to orch); G1 not met (stage/G1/, six items open)
headline:    The first GW source runs in full GR through shell crossing: the (k,k,0) strain
             follows the second-order value with its junk oscillation to 0.2-0.4 percent for
             2 <= a <= 10, the plane-symmetric null holds at rounding, a second spatial gauge
             agrees after the computed gauge piece; the Newtonian mode reproduces the 7/2 law
             and the ellipsoid crossing time; all rechecked by the lead from the raw outputs
last-result: lead recheck B-20261115-190007-e09a0d2 (first_source, own reader: c_+ equal
             to the helper's to 9e-14 of s), -190019-b5f5eb6 (late rise: 93-97 percent at
             |k|L/2pi >= 20, not gauge), -190015-4dd3416 (newton: H1 to 2 percent at a <= 5,
             t_x Richardson 23.8513), -190323-2f8806a (verifier scripts reproduce bit for bit);
             card scan B-20261115-164059-d802e82, -165353-b592d43; review stage/REVIEW-wave2.md
next:        1. Oblique and expanding-box linear waves with both diagnostics (G1 criterion 1)
                with core/requests-b's generator fix (scouting exe, decision 0013)
             2. Jittered-lattice null and particle-number convergence of the first source
                (1, 8, 27 per cell; 128^3), delta = 0.0025 to widen the window (~1 card-h)
             3. G1 schematics, note Sec. IV-V with the scan and the Newtonian tests,
                gauge_piece_total into gw_diag; an independent verifier of the wave-2 runs
blockers:    oblique wave and jitter: core/requests-b not on main (core/orch); N2 (embedded
             ellipsoid): per-species history (core); reviewer agents for the note (orch)
needs:       orch: verifier-report-name, stage-verify-runs-check, reviewer-agents-for-the-note;
             core: newtonian-species-history, newtonian-laplacian-order, OpenMP build and
             release of core/requests-b (reply-requests-answered); kb:
             track-b-key-reference-claims (all in tracks/B-emd-gw/outbox/20261115T19*)
offers:      gw_diag (TT, rho_K, spectra, helicity, E/B/Psi_4, readers; 14 tests);
             first_source/fslib/gauge.py (second-order spatial-gauge piece of the flat TT
             projection, G_tot with the homogeneous-anisotropy cross terms; 6 tests);
             a passing Gamma-driver shift in an expanding box with particles (run
             B-20261115-165353-b592d43); exact Zel'dovich plane-wave reference; the (kh)^2/12
             force error of the Newtonian mode (newton_tests H1); all on track/B-emd-gw
budget:      0.99 GPU-hours used of 40 (0.51 at G1 in wave 2, 0.48 in wave 1)
