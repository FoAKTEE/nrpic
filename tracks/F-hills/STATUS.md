# STATUS of F-hills

gate:        G0 package complete except the verifier's report (stage/G0; SECOND_CHECK.md is a second
             agent's check of the plan, not the harness verifier); G1 not met: F-pre-1 met, F-pre-2
             and the three-puncture data (constraints yes, junk no) partly, the passage P1 submitted
             2026-11-19 and running in the queue (stage/G1)
headline:    The first full-GR Hills passage (P1, q = 4, members at m/8) is submitted as a chain of
             17-20 card-hours; the single-puncture runs and the card smoke test give its rate, memory,
             gauge and horizon behaviour, and the two baselines disagree on which member it ejects.
announce:    P1 (decision 0014, above eight card-hours): run of `nr_first/inputs/p1_q4.athinput`,
             release core-v0.3 card build behind `nr_first/scripts/athena_keep_trackers.sh`, constant
             shift_eta = 2, `--gpu-hours 26` (21-25 segments of 50 min, 17-20 card-hours), one segment
             in the queue at a time; continues after the wave, the next session analyses it
last-result: - review of the wave-2/2b helpers from their raw outputs: S3/S2 stops, horizon rows, tracker
               speeds, smoke rate/memory/trackers all reproduced (F-20261119-145434-82c05f2); details
               stage/REVIEW-wave2.md
             - GR reading of the start states (F-20261119-145449-245e984): P1 centre-of-mass turning
               point 9.25 M in the hole frame (Newtonian 9.81 M); q = 10 input 5.77 M (second check
               confirmed), so a q = 10 passage needs momenta from a GR parabola
             - single punctures at m/8 (F-20261115-173601-2fae2dc, nr_first E3/E11): stopped at
               1632 > 1600 slots (wave-zone radius + 2:1 rule); with eta m = 0.25 the tracker settles
               at f = 0.76 in 4 m, with eta m = 2 still rising at 22 m; horizon mass drift 0.6-1.1e-4
               per m; junk energy not measured
             - P1 smoke (F-20261115-174602-c6879fe): 2057 MeshBlock-cycles/s, 69.2 GiB of 80 at 2700
               slots, trackers exact, member horizons good from t = 0.5 M
             - newton3 energies fixed (Jacobi split): ejection +1.3119 (q = 4) and +1.6127 (q = 10)
               units, equal to the lead's V5b; 15/15 tests (F-20261119-145509-fb91531)
             - corrected wave-1 claims: V4b covers 7 of 9 points; q = 4 m/16 tree 2514/2864/2568;
               HRNA capture percentages are model outputs, not predictions (second check)
next:        1. Analyse S2g (run F-20261119-143443-f11ebb9, Slurm 4640) with the commands of
                nr_first/README.md "Pending"; record E10's outcome.
             2. Follow P1 (run id in stage/G1/STATUS.md; `harness/bin/nrpic-run status <id>`,
                `scripts/submit_chain.sh --status <rundir>`); when it ends: finish, p1_analysis.py,
                the P1 prediction in JOURNAL.md (lead, wave 2b).
             3. G1 remainder: junk energy of the three-hole data from P1's spheres; Kerr row of F-pre-2
                (2402.02178); a verifier for G0 and G1; then the G2 plan (q = 4 at m/16 needs 2864
                slots: two cards or 32^3 blocks).
blockers:    no harness verifier for G0/G1 (orch); P1 waits in a full card queue; q = 4 at m/16 does
             not fit one card (core: two cards or larger blocks)
needs:       outbox 20261119T*: orch (verifier for G0 and G1, P1 announcement); core (tracker files
             truncated on restart; finder at 4 cells per radius; found flag in horizon summaries;
             mass-scaled damping with three holes)
offers:      readers of AthenaK trackers/horizons/waveforms with member energies against the
             barycentre (tracks/F-hills/nr_first/scripts/nrread.py); tracker-keeping chain wrapper
             (nr_first/scripts/athena_keep_trackers.sh); model of AthenaK's refinement tree
             (nr_first/scripts/tree_check.py); Newtonian three-body driver with multi-puncture input
             (newton3/scripts/puncture_input.py); HRNA reference (geodesic_binary/hrna.py)
budget:      card-hours used toward G1: 0.30 (S3, S2, smoke); reserved 0.98 (S2g) + 26 (P1 chain,
             expected 17-20); allotment 50 to G1 (0014), 120 toward G2 (0016)
