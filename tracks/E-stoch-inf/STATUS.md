# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-24; coord/GATES.md). G3: scope SCOPE 4d with amendments 4d.9
             A1-A14 (A14 batch 20: sampler shift profile, Z2(iii')); no card run of G3 yet; the
             zeta reader exists and passes Z0, Z2(i), Z2(iii') but FAILS Z1 along Pi alone and
             Z2(iii) as written (ruling asked); stage/G3/OPEN.md.
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf.
last-result: Lead batch 20 (2026-11-25 07:54-09:05 PST, processors only, at most 6 cores):
             - zeta reader zeta/zeta_reader.py (E-20261125-161456-8d3f43c, 32^3 pairs): TO VERIFY of
               4d.3 settled (deck = HiggsInflection mapped to code units to 1e-14; landmarks within
               1.3e-9 in N); Z0 3.0e-5; a_zeta 6.763e-3 at s = 1/4 and 1/2 (ratio 0.999996);
               Z2(iii) -2.89 % (FAIL, predicted), Z2(iii') -0.25 % (pass); Z1 passes along phi and
               the box relation (5e-5), FAILS along Pi alone (0.142; the independent integrator's
               floor by the diagnostics, cause not named; rerun stopped, E-20261125-161757-fb0eb95).
             - A4 preview vs the 8-band reference (E-20261125-160705-5f75bb4): box variance 1.031
               (scatter 3.1 %), zeta skewness 0.0027 vs 0.0026 +- 0.0020: the box carries the
               one-patch non-Gaussianity through the map; its field is Gaussian.
             - sigma = 0.1 lattice reference (E-20261125-160722-a6d1f26): variance gate FAILED
               (1.00245 +- 0.00050); skewness 0.0182 +- 0.0014 vs 0.0199 +- 0.0012: A10's bound
               not reached (R39).
             - Importance sampler (A9 with A14 (a)): E-20261125-160658-855db8c, see
               g3/amend/JOURNAL.md entry 10 (side +: c0 3.95, rel. s.e. of F_+(4) 0.11 %).
             - Defects fixed: NaN of the biased sampler where the noise vanishes; constant shift
               of A9 unusable (mean weight 0.01); variance gate required s0.01_lattice.
card plan:   q0050 G3P, q0051 G3C, q0052 G3R (priority 2), q0053 G3B00, q0054 G3B01 (priority 5,
             after G3P): all waiting, cards held by another partition (R37). Nothing new queued:
             the remaining baseline waits for the pilot's cost (A12).
runs pending: q0050-q0054 (cards). Processors: none after this session (the tilt run is closed
             in this session if it ends; otherwise `nrpic-run finish E-20261125-160658-855db8c`).
next:        1. Ruling on Z1 along Pi and Z2(iii) (outbox); then the 128^3 cost of the map (R41).
             2. Read q0050 (pilot) when it ends: cost per run into A12, A8 record, reader on k/b.
             3. Coarse-graining bound (R39): paired-noise runs at sigma = 0.01, 0.05, 0.1.
blockers:    none for processors; cards held (R37).
needs:       orch: ruling on the reader tests and on A14 (outbox batch 20).
             core: a field-dependent lapse, for later (outbox 2026-11-25), not for G3.
offers:      langevin/: G3 reference of the 128 band (direct 4e6, tilted nu = 4, sigma = 0.1);
             zeta/: delta-N reader for scalar-field dumps (code units, any potential of the deck).
budget:      G3 allotment 60 card-hours: 0 used; queued at most about 4. This session: 0 card-hours.
