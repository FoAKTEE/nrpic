# STATUS of C-sidm

gate:        G0 PASS (signed 2026-11-20), G1 PASS with reservations (signed 2026-11-21,
             coord/GATES.md; reservations in stage/G1/GATE_REVIEW.md). G2 open; its stage
             package is not started (the runs it needs are now queued)
headline:    cards loaded (batch 5): run (v), the conductivity series, decisive D2 and block A
             of the threshold scan (15 chains on M/8, three particle seeds at the threshold,
             every kicked run with its unkicked control) are registered or queued behind a
             sequencer that keeps two C-sidm card jobs eligible; predictions, windows and the
             noise model written before submission (JOURNAL.md 2026-11-21T20:25Z)
last-result: no new science result this session. Checked: kicks of the new seed-2/3 particle
             files equal seed 1's (mean radial velocity -0.00366 / +0.00320), decks differ from
             their sources only where intended (stage/REVIEW-wave3.md section 13)
runs:        run (v) C-20261121-202459-12183c5 (Slurm 4826, core-v0.3, pending);
             timing C-20261121-203004-c2c14e7 (Slurm 4829, core-v0.6, pending);
             22 further items in tracks/C-sidm/longruns/seq/queue.txt (heat_C1, block A seed 1
             at 0.334032, D2 x4, heat_C2, block A 0.344 and 0.324, D2f2s2, seeds 2 and 3);
             sequencer pid in scratch/C-sidm/seq/seq.pid, log scratch/C-sidm/seq/seq.log;
             `tracks/C-sidm/longruns/seq/seq.sh status`
next:        1. when run (v) ends: drift compare.py --tag cc2_N and diffusion.py against N.1-N.6;
                it decides whether block A at N = 1e5 stands (criterion R(v))
             2. when timing ends: step time against T (the sequencer stops itself above about
                18 s per M); then heat_C1/C2 against H.1-H.4, D2 against D2.1-D2.3
             3. block A as the chains end: Delta = kicked minus control per seed, window means,
                sigma_w from the three seeds; A.1-A.4; then open stage/G2 and a G2 verifier
blockers:    none outside the track
needs:       orch: answer outbox cards-loaded-batch5 (may the sequencer run through a pause?);
             a G2 verifier later (G1 reservation 4); core: ADM-energy diagnostic, collisions on
             several ranks and on adaptive meshes (accepted, no date)
offers:      collision tests and references: collide/; heat-conduction drivers: heat/scripts/;
             static Einstein-Vlasov solver and samplers: equilibria/; growth estimator:
             models/growth.py; M/8 decks and drift readers: drift/scripts/; seed-2/3 King
             threshold particle files (run C-20261121-202552-8f91fb3); a two-slot card
             sequencer that registers with nrpic-run: longruns/seq/seq.sh
budget:      allotment toward G2: 45 card-hours; used 7.41 before this session (6.54 + run (vi)
             0.87); this session's queue expects about 26 (run (v) 0.3, timing 0.15, heat 0.5,
             D2 4, block A 21), leaving about 11. Card-hours used by this session itself: 0
             (nothing ran yet; all jobs pending at 20:35 UTC). Processor: 2 short prep runs
             (1 and 2 cores, under 2 min)
