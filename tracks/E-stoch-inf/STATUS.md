# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with reservations
             (2026-11-24; coord/GATES.md). G3 open, NOT ready for review: scope SCOPE 4d + 4d.9 A1-A14;
             stage/G3/OPEN.md (102 of 128 baseline pairs ran, 71 read; 0 of 16 level-2 pairs yet).
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf (G3 section V added).
last-result: Lead batch 34 (2026-11-27 15:21-16:50 PST, processors only, at most 6 cores):
             - Found: G3B06 (job 5419) and G3L00 (job 5420) were cut by preemption on 2026-11-26 (17 of
               22 and 0 members); the queue marks preempted batch jobs "done". Complete: pairs 0-70, p071.
             - All card runs closed; 143 boxes read with the cleared table map (8 readings, g3 entry 17):
               all healthy (max H' 7.2e-12, max M 0.032, spot check <= 6.7e-9); 0.0349 card-h a run.
             - Pair statistics on 71 pairs (E-20261128-000627-00ed437) against the 128-band reference
               (two direct 4e6 runs pooled, importance-sampled nu = 4):
               (T) AGREES on every item: skewness 0.019721 +- 0.000010 vs 0.01985 +- 0.00088; kurtosis
               0.0014 vs 0.0015; F_pm(3) -1.5/+1.35, F_pm(4) +1.1/+1.8, A(3) -2.1, A(4) -2.1 combined s.e.
               (V) FAILED as written: variance +0.28 +- 0.07 per cent (4.1 s.e.): NR 1.0013 of the lattice
               sum, reference 0.9985. Cause not named.
               Mirroring cuts the skewness error 40-fold; a_zeta = 6.65e-3 per pair, a_R = 3.0e-4.
             - Note: G3 section V, five figures (ladder, mosaic, one-point, tails, pairs), 17 ledger rows;
               checker clean, compiled, pages read (runs E-20261128-000901-9c289e9, -001644-500a097).
card plan:   batch 36 (g3 entry 19): after the queue audit (decision 0048 item 9) the missing members are
             entered again at priority 2, about 25 min a job: q0101-q0104 (G3B12-G3B15: baseline m077, pairs
             78-81, 105-114, 117-125), q0105 (G3L03: level-2 pairs 0-4 + k000/k001), q0106 (G3L04: lm005,
             level-2 pairs 6-10); q0088 (G3L02b: level-2 11-15 + baseline 126-127) auto-retried. When done:
             128 of 128 baseline pairs, 16 of 16 level-2 pairs. About 3 card-hours.
runs pending: q0088, q0101-q0106 (run ids: harness/bin/nrpic-queue show <qid>).
next:        1. As jobs end: finish, read each with read_pilot.py --save-fields, rerun pairs_g3.py --pairs
               0-127 (entry 17 lists the readings); level-2 pairs against level 0 (4d.7, reported).
             2. A4 on the saved fields; the sigma-paired reference (R39) to bound the coarse-graining and
               to test the variance difference.
             3. Fresh verifier on the full set; full checksum pass (nrpic-stage verify --full).
blockers:    cards held by another partition for long stretches (preemptions within seconds).
needs:       none (the queue correction of 0048 item 9 answers the earlier request).
offers:      g3/pairs_g3.py (pair statistics against the one-patch reference); g3/zeta_table.py.
budget:      G3 allotment 60 card-hours: about 8 used (pilot 0.35, G3C 0.26, G3R 0.35, baseline 143 runs
             5.0, G3B08b/09b 1.53, preempted fragments); about 3 queued (7 entries).
