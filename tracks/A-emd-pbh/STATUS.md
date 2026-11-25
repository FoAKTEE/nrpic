# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md). G2 in progress: interim
             package stage/G2 (9 PASS, 10 OPEN, 1 FAIL: C3); NOT ready for review (stage/G2/OPEN.md).
headline:    At t = 0 the constraint floor of the top-hat members is the density jumps plus the PCS deposit at the
             refinement boundaries (smooth data with CIC: 6.4e-3 on M/16, 5.8e-4 on M/32), but the evolution rebuilds
             it (0.129 at t = 1 on M/16 with CIC): C3 stays FAILED. A2's lag is not in the Zel'dovich reference: the
             same positions under Newtonian gravity cross at 4.55 t_H (Zel'dovich 4.35), S1L at 6.35.
last-result: batch 20 (2026-11-25, processors only):
             - C3 smoothed-edge test (threshold_ball entry 13): `--edge-w` alone not admissible on data set 3
               (A-20261125-160221-b68396f); smooth members S1, S2 (A-20261125-160436-462452d). t = 0 ratio top hat /
               S1 / S2: 0.278 / 0.185 / 0.134 (M/16), 0.174 / 0.146 / 0.116 (M/32) (A-20261125-160849-8c01b54):
               smoothing alone fails (a refuted); S2's momentum norm falls 60-fold (c holds). Test D
               (A-20261125-161039-cb046d7): CIC 0.0064, PCS uncompensated 0.089: the remainder is the PCS deposit.
               F1 (A-20261125-161248-eecc672): S2 with CIC 6.4e-3 (M/16), 5.8e-4 (M/32). F2 REFUTED on M/16
               (A-20261125-165215-e3fe168): 0.129 at t = 1. C3 stays FAILED; the mesh leg S2c-B decides.
             - A2 control (periodic_threshold 2026-11-25 08:10 PST): second derivation of the reference (D = a,
               a_H = r_m^2 = 6, t/t_H = (a/6)^1.5, lambda_z = 0.063: 4.35 t_H). N-z (Newton, Zel'dovich velocities,
               A-20261125-160633-e38d321) crosses along z at 4.55 t_H (A-20261125-162905-d0ef1d7): AZ1 narrowly
               refuted (band [3.7, 4.5]); it follows Zel'dovich to 0.02, S1L leaves it from 1-2 t_H
               (A-20261125-162951-bb0fb26). N-f (the GR file under Newton) 0.43 t_H (A-20261125-165125-1640161):
               AZ2 direction holds, band refuted. The lag is in the GR evolution or its coordinates; not named.
cards:       none used this session. Shared queue: q0013 a-p0l6 (p2; chain A-20261125-044641-7d5bd16 at t = 138 of 140,
             Slurm 5296 pending; not ended, so the t = 118.1 find was not read); q0040, q0041 Szekeres (p2, waiting);
             q0015 S1L continuation (p5, waiting).
processors:  running detached: A-20261125-161154-62ce3dc (F: S2 with CIC, 3 cores, to ~11:30 PST),
             A-20261125-160633-594a474 (PCS twin S2-A, 2 cores, to ~09:00), A-20261125-160633-e38d321 (N-f, N-z128,
             1 core). Close each with `harness/bin/nrpic-run finish <id>`.
next:        1. C3: read the mesh leg S2c-B (M/32 to t = 1) against S2c-A at t <= 1; does the violation fall with the mesh?
             2. A2: N-z128 from the run above; then a control that separates a relativistic lag from a
                coordinate effect of the shift (gauge-invariant crossing measure, or a GR member with zero shift).
             3. Read q0013 (P0L6) and q0040/q0041 (Szekeres) when they end; stage verify --full when cores are free.
blockers:    C3 FAILS as written for every member run so far (PCS, and CIC on M/16 from t = 1); C1 needs Szekeres, P0L6 and
             an explanation of A2's lag.
needs:       orch: C3 result and follow-up (outbox 20261125T161356Z, and c3-f2-refuted: the 'if F2 holds' question withdrawn).
             core: is the PCS spike at a static refinement boundary a property or a defect (outbox 20261125T161355Z)?
offers:      conv_ball/scripts/prep_bh.py --profile smooth_tophat; threshold_ball/scripts/edge_compare.py (section-3
             line ratio and volume norms); periodic_threshold/scripts/a2_compare.py, a2_crossing.py --clock newton,
             inputs/a2_newton.athinput (Newtonian control of a GR particle file).
budget:      card-hours: none this session; processor: about 6 cores for 1 h in session plus the detached runs above.
