# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 not met (stage/G2/OPEN.md, unchanged this
             session): C1 (shearing-dust L2) and C3 (constraints in the mesh) FAIL as written;
             decision 0046 item 2 requires two cheap runs before G2 (both started this session);
             C2, C11 wait for the GM analysis; C5, C17 for its paragraph; C18 for a verifier,
             sent when C1 and C3 have been read.
headline:    Before stream crossing the shearing dust keeps small constraint violations:
             beta = 0.125 at H L = 4 keeps relative constraint means of 1e-6 to 4e-4 up to the
             arrivals (L2: 0.12-0.4), and the first stream crossing comes at t = 9.25, after
             t_A = 4.12, at N_y = 64 (series 7, B-20261126-222544-f3a5176). Mesh leg running.
last-result: batch 29 (2026-11-26 14:18-): design of the amplitude without crossing
             (B-20261126-222532-5ab01ea; Zel'dovich estimate, too optimistic by 2-3 in the
             compression rate, recorded); series 7 N_y = 64: Delta = +0.0537. The first GM
             analysis (B-20261126-212212-c54d979) was killed with its session (SIGTERM, 42 min,
             no output), closed failed; rerun in the background.
running:     processor, background (close each with `harness/bin/nrpic-run finish <id>`):
             B-20261126-221911-a0531db GM2/GM3 analysis (4 workers, ~30 GB each);
             B-20261126-222544-f3a5176 shear series 7 (N_y = 64 done, 128, 256);
             B-20261126-222552-2e44186 64^3 initial data at 8 per cell (C3 step 1)
cards:       nothing queued for B; the C3 card member is queued after its initial data exist
             (HANDOFF has the line; priority 2, release v0.8 card build, about 0.1 card-h)
next:        1. close series 7, register series7_judge.py, judge N7a-c (shear/JOURNAL 14:25)
             2. close the 64^3 data, check modes and sigma1, queue the C3 member, judge C3a-b
             3. close the GM analysis, compare_legs.py, judge GM2 and GM3; C2, C11, the GM
                paragraph and ledger row in note section VI (C17)
needs:       orch: the fresh verifier for C18 after C1 and C3 are read (decision 0046).
             core: parameters added at a restart (NEXT_SOURCE item 1); Fourier Newtonian
             solver with the threaded build.
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); analyze_gr.py --equal-mass;
             compare_legs.py --halo-base; shear/scripts/crossing.py (stream crossing from
             snapshots of a lattice); findings: GR particle files carry the rest-mass weight
             (R25); zero shift fails in resolved periodic cores (R26); the constraint level
             after collapse follows particles per cell (R27)
budget:      card-hours toward G2: 11.61 used; G1 1.69; allotment 40 (0014); nothing
             submitted this session (the C3 member will cost about 0.1)
