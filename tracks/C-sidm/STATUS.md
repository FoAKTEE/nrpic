# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 open
             (stage/G2: 7 of 20 items pass, none fails as written, 13 open); NOT met, not ready
             for a verifier: the mesh and gauge legs of the bracket are unread
headline:    the collisionless threshold of the King b = 1 family is bracketed on M/8 at
             N = 1e6: y0 0.344 kicked in collapses at 252.31 M, 0.324 kicked in holds 600 M
             within +-0.015, so (0.324, 0.344) contains y_max = 0.334032; same fates at N = 1e5;
             the unstable side repeats with shift_eta 1.0 (252.41 M). Lapse markers, no finder
last-result: batch-27 analyses (JOURNAL 2026-11-26T12:10Z-12:34Z; figures read):
             - NS.3 held: N = 1e4 control collapses at 295.78 M (C-20261126-120656-f5c62bb);
               controls on M/8: 295.78 / 534.81 M / none at N = 1e4 / 1e5 / 1e6
             - B17.5, B17.6 held (C-20261126-121836-c7a76c1); B20.3 first half held
               (C-20261126-123219-f734997)
             - B17.4 held: collisional t_c 164.01 M with shift_eta 1.0 vs 163.41 M
               (C-20261126-114801-ea62ac3); D2.3 seed part FAILED: 2.24 M vs 2 M bar
               (C-20261126-121702-b6b1eda); run D2eta1 FAILED on record (guard stop 190.4 M)
             - note: G2 section (Sec. V) and ledger table VI written, compiled, checked
runs:        q0055 A16b344 ENDED (C-20261126-043714-8ea1c35, 600 M, collapsed; `nrpic-run
             finish` running at the end of the session, log scratch/C-sidm/tmp/
             finish_a16b344.log); q0057 A16b324 (job 5382 pending); q0058 N6b324e1 waiting.
             Nothing else of C-sidm queued
next:        1. close A16b344 if the finish did not end; read it with nseries.py beside N6b344
                (B20.2), then q0057 (B20.1) and q0058 (B20.3 second half) when they end
             2. G2 figures by one script each (convergence in N, mesh, gauge; ladder schematic;
                slice mosaic) via the note's run_all; then the fresh G2 verifier (0041 item 3)
             3. G3 design: collapsed mass fraction against Kn with the finder's diagnostics on
blockers:    none besides the queue (cards shared)
needs:       orch: q0057, q0058 at priority 2; a fresh G2 verifier after they are read
offers:      readers longruns/scripts/{nseries,d2_analysis,blockA_delta,horizon_audit}.py
             (nseries now with --control, --band, --title); N = 1e6 King samples of y0 0.324,
             0.334032, 0.344; collision tests and references (collide/)
budget:      G2: 41.78 card-hours used by closed manifests, 11.80 reserved, 26.42 left of 80
             (nrpic-run budget, 12:35Z; before A16b344 was closed)
