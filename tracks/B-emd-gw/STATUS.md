# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 not met (stage/G2/OPEN.md, unchanged this
             session): C1 (shearing-dust L2) and C3 (constraints in the mesh) FAIL as written;
             decision 0046 item 2 requires two cheap runs before G2: C1's ran and is judged
             (series 7), C3's member waits for its initial data (about 17:30 PST);
             C2, C11 wait for the GM analysis; C5, C17 for its paragraph; C18 for a verifier,
             sent when C1 and C3 have been read.
headline:    Without stream crossing the shearing-dust observable converges in the mesh: beta =
             0.125 at H L = 4, N_y = 64-256 at 4 per cell, Delta 0.053749, 0.053800, 0.053821
             (ratio 0.40, Richardson 0.05383, error 1.4e-5; streams cross only at t = 9, after
             t_A = 4.1), where L2 moved away with each refinement: L2's failure is attributed to
             stream crossing (B-20261126-222544-f3a5176, B-20261126-230056-294b265).
last-result: batch 29 (2026-11-26 14:18-15:05): series 7 N7a holds, N7b Delta part holds,
             constraint part fails (means 2.6e-6 Hr, 1.6e-4 Mr, falling only 1.0-1.4x per
             doubling), N7c holds (shear/JOURNAL 15:02). Design estimate of the crossing time too
             optimistic (B-20261126-222532-5ab01ea). The first GM analysis
             (B-20261126-212212-c54d979) was killed with its session (no output); rerun running.
running:     processor, background (close each with `harness/bin/nrpic-run finish <id>`):
             B-20261126-221911-a0531db GM2/GM3 analysis (4 workers, ~30 GB each);
             B-20261126-222552-2e44186 64^3 initial data at 8 per cell (C3 step 1, about 3 h,
             end near 17:30 PST)
cards:       nothing queued for B; the C3 card member is queued after its initial data exist
             (HANDOFF has the line; priority 2, release v0.8 card build, about 0.1 card-h)
next:        1. close the 64^3 data, check modes and sigma1, queue the C3 member (HANDOFF
                line, priority 2), judge C3a-b
             2. close the GM analysis, compare_legs.py, judge GM2 and GM3; C2, C11
             3. note section VI: paragraphs on GM2/GM3, series 7 (C1) and C3, ledger rows
                (C17); then the G2 stage package for the fresh verifier (0046)
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
