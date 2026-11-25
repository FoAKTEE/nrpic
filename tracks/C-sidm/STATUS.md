# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 open
             (stage/G2: 7 of 20 items pass, 4 fail, 9 open); NOT met, not ready for a verifier
headline:    at N = 1e5 on M/8 all three block A controls collapse (534.8, 549.3, 599.99 M) while
             the N = 1e6 control holds 600 M: particle-noise relaxation; the threshold is read at
             N = 1e6 (bracket q0046/q0047) with its mesh and gauge legs now queued (q0055-q0058,
             ruling 0039 item 3). No collapse time of the package rests on a horizon search
last-result: batch-20 analyses (JOURNAL 2026-11-25T16:14Z; figures read):
             - block A close-out C-20261125-160056-a5b7282: BA.1-BA.3 hold; A324s1c t_c 599.99 M;
               0.324 kin holds 600 M (Delta +0.085 over 500-600 M), 0.344 kin collapses 229.79 M
             - horizon recheck C-20261125-160207-05b6db1 (decision 0040 item 3): 24 simulations,
               none with the finder or its diagnostics; t_c recomputed from alpha_min = 0.3
             - batch 17: N6c holds 600 M at N = 1e6; collisional t_c 206.64, 163.41, 158.42 M on
               M/4, M/8, M/16
runs:        shared queue (HANDOFF.md table): q0046 N6b344, q0047 N6b324, q0048 D2eta1, q0018 N4c
             (pending, job 5297), q0055 A16b344, q0056 N6b344e1, q0057 A16b324, q0058 N6b324e1
             (priority 2); q0022, q0023, q0024 (priority 5). Nothing of C-sidm running.
next:        1. read the bracket at N = 1e6 (q0046, q0047) against B17.5, B17.6 (C7, C9 at one
                mesh)
             2. read the legs q0055-q0058 against B20.1-B20.3 (mesh and gauge of the bracket);
                read N4c (NS.3) and D2eta1 (B17.4)
             3. figures, note sections and a G2 verifier once the bracket and legs are read
blockers:    the cards are held by another partition (all five account jobs pending); the M/16
             cost is an estimate (6.5 card-hours each)
needs:       orch: budget file of nrpic-run to count 80 card-hours for C (ruling 0039 item 3);
             a G2 verifier once the bracket and the legs are read
offers:      readers longruns/scripts/{nseries,blockA_delta,d2_analysis,horizon_audit}.py;
             N = 1e6 King samples of y0 0.324, 0.334032, 0.344 with kicks
             (C-20261125-120426-f261c3e, C-20261124-130731-e1d24de, C-20261125-115759-77a6999);
             collision tests and references (collide/); queue wrapper longruns/seq/qitem.sh
budget:      G2 31.09 card-hours used by closed manifests (nrpic-run budget; it still shows the
             old allotment 60, ruling 0039 item 3 gives 80): about 49 left of 80; waiting in the
             queue about 7.5 (q0046-q0048, q0018, q0022-q0024) + 18.6 (q0055-q0058) [JUDGEMENT]
