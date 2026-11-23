# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2: the
             production ladder on the release card build has run and is judged against SCOPE 4c;
             C3/C7 FAIL as written at one dump of M (below); package not complete (verifier, note
             sections, figures C10-C13, gauge leg of C2).
headline:    Release core-v0.6 repeats the G1 slow-roll run digit for digit; the USR case passes
             U-A0..U-A3, U-A2' (1.09e-4 per mode, seeds A and B), U-R, U-S, U-A4'(c), (d), and
             misses U-A4'(a) at one of 11 dumps of M (even halving 3.925 at cN 6.52, bar 3.95-4.05).
last-result: Lead batch 10a (2026-11-22 17:45-19:15 PST), g2prod/JOURNAL.md entry 2:
             - T: 1.374 / 2.522 / 4.300 s per step at 256/320/384^3 (held); peak 61077 MiB at 384^3
               (memory band missed low). P256v6 records identical to E-20261115-172618-f948386.
             - Seed A on the release identical per mode to the scouting pair; seed B U-A2' 1.087e-4,
               one-point rms 0.89411 (lattice 0.89366). U320: odd-part factor 2.10 (band 2.4-4.5
               missed; U-R (i) bar 2.0-4.5 met); shell power 320 vs 256 1.2e-4.
             - Halving s = 1/2: H 3.992-4.042 at 9 dumps; M one dump 3.925 -> U-A4'(a) FAIL.
             - Control: odd part of H 1.19e5 times the proper (bar 1e3).
             - Finding: a common factor of all modes, -4.1e-5 at s = 1, scaling as s^2 (4.16),
               appears after cN 5.5: third order in amplitude; which term is not named.
             Runs: analyses E-20261123-015014-b4ecd4e, -014858-8e72d4c, -021730-a421438,
             -020751-0baf597; judge E-20261123-024359-5dc3213; check E-20261123-024806-3c0e139.
             Analysis defects on record: E-20261123-015650-493cff5 (failed), E-20261123-014905-2bf3570
             (wrong realisation for seed B, per-mode numbers invalid).
card plan:   s = +-1/4 pair at 256^3 (U256qp/qm, about 0.62 card-hours each, ceiling 1.97) queued in
             the g2prod sequencer (pid in scratch/E-stoch-inf/g2prod_seq/pid, started 18:49 PST);
             it waits until fewer than two E card jobs are eligible (repro/scope holds two now).
runs pending: U256qp, U256qm (not yet submitted; sequencer). repro/scope's Slurm 4929, 4931 belong
             to package repro/scope (decision 0028), not to G2.
next:        1. G2 verifier (C18), fresh context, given the run directories and SCOPE 4c only.
             2. When U256qp/qm have run: analyse_g2.py --group g2q, judge Q-a..Q-c (entry 3).
             3. Note G2 sections and figures C10-C13 (coordinate with repro/note of decision 0028).
blockers:    orch: whether G2 can pass with the U-A4'(a) miss on record; the C2 gauge leg.
needs:       orch: rulings above (outbox 2026-11-23). core: lockstep sub-stepping (not blocking).
offers:      - g2prod/: release ladder, sequencer, analysis wrapper (analyse_g2.py, --seed, --last),
               SCOPE 4c judge (judge_g2.py). SR ladder: ladder/. USR: usr/. Window: window/.
             - Stochastic delta-N statistics: langevin/ (to A). Noise validator: noise/.
budget:      G1 2.15 (closed). G2 used 9.28 of 20 (g2prod 7.51 at measured cost), reserved 2.47
             (repro/scope). This session: 0 card-hours; processors at most 6 cores (analyses).
