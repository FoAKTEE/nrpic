# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21 (coord/GATES.md, tag stage/A-emd-pbh/G1-pass-20261121).
             G2 in progress: horizon formation of the spherical expanding ball against the exact solution.
headline:    The expanding ball forms its apparent horizon on every mesh of the convergence series (conv_ball: first-detection
             error 0.193, 0.068, 0.017 M at finest cells M/16, M/32, M/64; median horizon-mass error 7.4e-3, 2.1e-3, 2.1e-4;
             A-20261121-120257-a2eb839), independently checked (verify_bh: C1, C2 confirmed; first-detection mass +2e-2 is not a
             usable measure). Batch 5 put the first scan across a threshold of black-hole formation on the cards
             (threshold_ball: finite-duration threshold of the top-hat ball at t_end = 45 M, exact bracket delta_c in (0.40, 0.42]).
             The periodic box does not yet carry a relaxed-lapse run (job 4799 failed at t = 4.8 and 15.1).
last-result: periodic_threshold card job 1 (A-20261121-131600-02b5d41, Slurm 4799): both members stopped on the guard (exit 3),
               P0L at t = 4.815, S1L at t = 15.076; norm(H) jumps by ~1e4 at t = 2.506 in both (lead's reading
               A-20261121-203120-eaba95f). Predictions P3, P4, S1, S2 refuted. Request to core.
             threshold_ball design A-20261121-202520-3164672, data A-20261121-202812-cae4436 (exact tau_AH 15.39 ... 114.57 M for
               delta_c 1.0 ... 0.2), smoke tests A-20261121-203156-d094c56 (failed: decks lacked `diagnostics`) and
               A-20261121-203211-6d3ce73 (exit 0). Predictions T1-T6 in threshold_ball/JOURNAL.md entry 1.
             conv_ball (batch 2b) and verify_bh (batch 3) results reviewed for the decision (stage/REVIEW-wave3.md section 6).
cards:       running or queued (Slurm names A-*; sequencer keeps at most two):
               A-20261121-204149-c48bd33 (Slurm 4838) B-d0.42, chain to t = 51;  A-20261121-204250-0bf45c7 (Slurm 4845) B-d0.40 to 54
             waiting in threshold_ball/queue.txt (sequencer pid 2666191, scratch/A-emd-pbh/sequencer_threshold/):
               A-mesh batch (A-d0.42, A-d0.40), B-d0.45, B-d0.50, B-d1.00, B-d0.70, B-d0.35, B-d0.20, C-R1.25 (conv_ball leg,
               core_gauge), C-d0.42 (M/64, about 8 card-hours)
next:        1. As chains finish: nrpic-run finish <run id>; analyse with conv_ball's compare.py (threshold_ball needs its own
                analyse script: write it first, before the first member is read); judge T1-T6; figures.
             2. When core answers periodic-relaxed-lapse-blowup: a periodic deck that runs past t = 10, then P0L against the LTB
                reference and S1L; the AMR periodic run only after that.
             3. Before the G2 review: second agent on conv_ball's G2 reading (its JOURNAL entry 12) and on threshold_ball's
                outcomes; architecture schematic against core-v0.6; edge band reported separately in shell errors.
blockers:    periodic box: core's answer on the relaxed-lapse blow-up (request 20261121, periodic-relaxed-lapse-blowup);
             phase-1 periodic generator for mu >= 0.5 (core, deferred). Ball: none.
needs:       core: periodic-relaxed-lapse-blowup and bh1r-inte-deficit-two-levels (both posted this session); still open from earlier:
               refined-level K_ij dumps for the Szekeres test.
             kb: szekeres-conformal-flatness (acknowledged by kb, waits for its claims package).
offers:      expanding-ball data and exact LTB shells for any delta_c: threshold_ball/scripts/{design_scan,prep_scan}.py
             nested static mesh decks with finder diagnostics: threshold_ball/decks/
             card sequencer for an owner (two-job rule): threshold_ball/scripts/sequencer.sh
             convergence series of horizon formation: conv_ball/ (README, convergence.md of A-20261121-120257-a2eb839)
budget:      card-hours G2: 5.51 used, 3.93 reserved, 50.56 left of 60 at 12:44 PST (nrpic-run budget). This batch: the queue
               asks 32.7 card-hours (model 15: B members 0.25-0.8 each, C-R1.25 2.3, C-d0.42 8.2), above the 8-hour mark of
               decision 0014 in sum: announced here and to orch (outbox cards-loaded-threshold-scan). Processors this session:
               1-4 cores for about 8 minutes.
