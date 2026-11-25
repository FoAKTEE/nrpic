# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 open
             (stage/G2: 7 of 20 items pass, 4 fail, 9 open); NOT met, not ready for a verifier
headline:    the collisionless control of the threshold model holds 600 M at N = 1e6 on M/8, where
             at N = 1e5 it collapsed at 534.8 M: the control collapse is particle-noise
             relaxation, so the threshold is read at N = 1e6 (bracket queued); the collisional
             collapse time converges with the mesh (206.64, 163.41, 158.42 M on M/4, M/8, M/16)
last-result: batch-17 analyses (JOURNAL 2026-11-25T12:21Z; figures read):
             - N-series C-20261125-122010-fb3cc08: N6c no collapse, alpha_c in [-0.0022,
               +0.0115]; H floor ratio 9.95 for N x 10; NS.1 holds, NS.2 FAILED
             - D2 + M/16 C-20261125-122020-031b67e: t_c(M/16) 158.42 M, rate ratio 1.0008;
               M16.1, M16.2 hold; budget 3.0e-16
             - earlier (batch 11): conductivity 1.020 +- 0.004; D2.2, A.3, A.4, N.3 failed
runs:        shared queue (HANDOFF.md table): q0046 N6b344, q0047 N6b324, q0048 D2eta1, q0018 N4c
             (priority 2); q0022, q0023, q0024 (5). Removed: q0019-q0021, q0025-q0027.
             A324s1c+ (C-20261123-032324-938ecbd) DONE at 600 M, not closed (tool refuses)
next:        1. read the bracket at N = 1e6 (q0046, q0047) against B17.5, B17.6: locates the
                threshold at one mesh and N and compares it with y_max = 0.334032 (C7, C9)
             2. close A324s1c+ by hand and rerun blockA_delta.py; read N4c and D2eta1 (C2)
             3. mesh and gauge legs of the bracket (card-hours asked), then figures, note, a
                G2 verifier
blockers:    preemption of the cards by another partition; card-hours for the convergence legs
             of the bracket (asked); nrpic-run finish refuses continued runs (asked)
needs:       orch: card-hours, dt_gauge ruling for series members, harness fix for continued
             runs (outbox 20261125T122226Z); a G2 verifier once the bracket is read
offers:      N-series reader longruns/scripts/nseries.py; N = 1e6 King samples of y0 0.324,
             0.334032, 0.344 with kicks (C-20261125-120426-f261c3e, C-20261124-130731-e1d24de,
             C-20261125-115759-77a6999); collision tests and references (collide/);
             conductivity reader; queue wrapper longruns/seq/qitem.sh
budget:      G2 allotment 60 card-hours: 29.62 used by closed manifests (nrpic-run budget after
             this session's closes: N6c 2.71, M16 1.19), 30.38 left; queued about 9.9 more
             (3 x 2.5 + 0.8 + 1.5 + continuations) [JUDGEMENT]
