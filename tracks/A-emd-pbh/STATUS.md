# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md, tag stage/A-emd-pbh/G1-pass-20261121).
             G2 in progress: horizon formation of the spherical expanding ball against the exact solution.
headline:    The expanding ball forms its apparent horizon on every mesh of the convergence series (conv_ball: first-detection
             error 0.193, 0.068, 0.017 M at finest cells M/16, M/32, M/64; median horizon-mass error 7.4e-3, 2.1e-3, 2.1e-4;
             A-20261121-120257-a2eb839), independently checked (verify_bh). The first threshold scan (threshold_ball) is on the
             cards. The periodic box's failure (job 4799) has its cause: the Gamma-driver shift is unstable above dt/dx = 0.685
             (periodic_diag, decision 0027); the deck now runs cfl_number 0.5 and its second card job is queued.
last-result: periodic_diag (batch 6): Test B A-20261121-212800-d7f31a4 (threshold 0.685), uniform G0-G6
               A-20261121-212941-9e68be1 / A-20261121-220510-6c46032 (cfl 0.5, 0.6 stable), card deck with zero shift R2
               A-20261121-212853-4a52dea (no jump), Test A A-20261121-222539-c4e42fe; second finding: lapse_leak x dt > ~2.5 is
               unstable (U8/U9 A-20261121-223054-ae9af0c).
             batch 7: request posted to core (outbox periodic-gamma-driver-step); deck peak_leak.athinput at cfl 0.5;
               predictions Q1-Q3 in periodic_threshold/JOURNAL.md (2026-11-21 23:15Z); P0L and S1L queued.
cards:       queued or running (Slurm names A-*; the sequencer keeps at most two):
               A-20261121-204149-c48bd33 (Slurm 4838) B-d0.42, chain to t = 51;  A-20261121-204250-0bf45c7 (Slurm 4845) B-d0.40 to 54
               (both PENDING at 15:15 PST)
             waiting in threshold_ball/queue.txt (sequencer pid 2666191, scratch/A-emd-pbh/sequencer_threshold/):
               lines 5-11 A-mesh batch, B-d0.45, B-d0.50, B-d1.00, B-d0.70, B-d0.35, B-d0.20; 12 C-R1.25 (conv_ball leg);
               13 C-d0.42 (M/64); 14 periodic P0L (cfl 0.5, to t = 140); 15 periodic S1L (cfl 0.5, to t = 220)
next:        1. As chains finish: nrpic-run finish <run id>; threshold_ball needs analyse.py (write it before the first member is
                read); judge T1-T6 with figures.
             2. Periodic job 2 (lines 14-15): judge Q1-Q3 first (remedy on the refined mesh), then P1-P4 against the LTB reference
                and S1-S3; tell core the outcome (its gauge-speed step limit). HANDOFF has the commands.
             3. Before the G2 review: second agent on conv_ball's G2 reading and on threshold_ball's outcomes; architecture
                schematic against core-v0.6.
blockers:    none for the ball. Periodic box: none in the source (cfl 0.5 is the remedy, untested on the refined mesh until
             job 2); phase-1 periodic generator for mu >= 0.5 (core, deferred).
needs:       core: periodic-gamma-driver-step (posted 2026-11-21 23:15Z: gauge-speed step limit, lapse_leak stiffness limit,
               cpu_run.sh footer; no reply needed before job 2); bh1r-inte-deficit-two-levels; refined-level K_ij dumps (Szekeres).
             kb: szekeres-conformal-flatness (acknowledged, waits for its claims package).
offers:      expanding-ball data and exact LTB shells for any delta_c: threshold_ball/scripts/{design_scan,prep_scan}.py
             card sequencer for an owner (two-job rule): threshold_ball/scripts/sequencer.sh
             von Neumann analysis of the Z4c gauge with the code's stencils: periodic_diag/scripts/vonneumann.py
             convergence series of horizon formation: conv_ball/ (README, convergence.md of A-20261121-120257-a2eb839)
budget:      card-hours G2: 5.51 used, 3.93 reserved, 50.56 left of 60 (nrpic-run budget, 15:15 PST). Queue asks 37.6 card-hours
               in all (model 16.8): the scan 32.7 (model 15) and periodic job 2 4.9 (P0L 2.0 = 2 segments, S1L 3.0 = 3
               segments; model 1.8: about 14,300 and 22,000 steps at 0.173 s per step of job 4799). Announced here; the
               scan's part was announced to orch in outbox cards-loaded-threshold-scan. Batch 7 used 0 card-hours, no processors.
