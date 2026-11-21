# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 in
             production: criteria fixed in spec/scope/SCOPE.md 4c before any G2 production run
             (decision 0023 item 1); stage/G2/CHECKLIST.md collected, items open.
headline:    SR case of arXiv:2512.14649 reproduced to 1.2e-4 per mode at 256^3 (G1). USR case on
             scouting builds: odd part per mode 1.09e-4 at 256^3, spectrum at N_f window-independent
             within numerical error (<= 1.9e-4 to k_max/2). Release production ladder now queued.
last-result: - Lead batch 5 (2026-11-21 12:19-12:50 PST): reviewed `window` and `a4res` from their
               registered outputs (stage/REVIEW-wave3.md Part C; reruns E-20261121-203008-f104a3e,
               E-20261121-203016-7209255); SCOPE 4c (floor f^2 = (4 o_{s/2}^2 - o_s^2)/3, clause on
               the maxima, U-A2', U-A4', U-R, U-S, U-W); package g2prod with predictions (entry 1),
               timing and P256 jobs, sequencer for nine USR chains; restart of the deck byte-exact
               (R0, E-20261121-202941-da16544). Reruns identical to the committed results; own-code
               check of a4res holds (E-20261121-203540-a9b5d10). Nothing found wrong.
             - window (batch 4a): L9 scan analysed; W6 refuted (late USR constraint records depend on
               sigma by up to x21.7). a4res (batch 3): strict A4 holds at >= 12.8 cells per shortest
               wavelength, fails at 10.7 and 8; Q6 failed at one dump (cause not found).
card plan:   (announced before submission, decision 0014; allotment toward G2 10 card-hours, used 1.77
             at 12:23 PST) release card build core-v0.6, package g2prod:
             | T timing 4827 | 0.15 | P256v6 4828 | 0.5 | U256 a+-, b+-, h+-1/2 | 6 x 0.65 |
             | U320 a+, a- | 2 x 1.6 (estimate, measured by T) | U256nc control | 0.25 |
             total about 8.0 card-hours; no single run above 8. The last three need either the
             earlier runs closed at actual cost or the allotment raised (asked: 20).
runs pending: E-20261121-202929-43dcc9c (Slurm 4827, timing), E-20261121-202935-31520bc (Slurm
             4828, P256v6); queue of the sequencer (scratch/E-stoch-inf/g2prod_seq/state.tsv):
             U256ap, U256am, U320ap, U256bp, U256bm, U320am, U256hp, U256hm, U256nc.
next:        1. Read T (step time, memory at 320^3/384^3) before U320ap starts; judge P256v6 against
                E-20261115-172618-f948386 (prediction P256v6).
             2. When U256ap/am have run: U-A0..U-A3, U-A2' and the release-vs-scouting comparison;
                then U-R, U-S, U-A4'(a) as the chains finish (g2prod entry 2, figures).
             3. Stage G2: fill CHECKLIST C1-C20 (C4 "first full-GR kinetic run": NA for E before the
                hand-over, to be confirmed by orch), working note G2 sections, a fresh verifier.
blockers:    allotment for the last three g2prod runs (orch); the shared card queue.
needs:       orch: allotment toward G2 raised to 20 card-hours (also for a 384^3 pair, third rung
             of U-R); acknowledgement that SCOPE 4c answers decision 0023 item 1.
             core: lockstep record sub-stepping (request 2026-11-21 13:10Z, not blocking).
offers:      - SR ladder 32^3-256^3 with verdicts: ladder/. USR card runs and analysis: usr/.
             - Window scan L9 and its sensitivity table: window/. Strict-A4 resolution law: a4res/.
             - G2 criteria text: spec/scope/SCOPE.md 4c. Sequencer for unattended chains:
               g2prod/scripts/sequencer.sh (reusable by other owners: edit WT, Q, labels).
             - Stochastic delta-N reference statistics: langevin/ (to A-emd-pbh). Noise validator:
               noise/ (to core, C-sidm). Working note v1: note/main.pdf.
budget:      G1 2.15 used (closed). G2 1.77 used + g2prod about 8.0 planned (reservations 0.42 +
             0.97 now). This session: 0 card-hours used so far (jobs queued); processors at most
             5 cores (two reruns of 2, restart check of 1).
