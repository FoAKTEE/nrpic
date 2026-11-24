# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21; coord/GATES.md). G2 open:
             package stage/G2 opened 2026-11-24 (7 of 20 items pass, 4 fail, 9 open); not met
headline:    on the M/8 mesh at N = 1e5 the collisionless controls of the threshold model and of
             y0 = 0.344 collapse on their own (534.8, 549.3 M), so block A cannot bracket the
             threshold; the collisional collapse at Kn = 10 does not depend on the collision cell
             but moves 21 per cent between M/4 and M/8; conductivity settled (1.020 +- 0.004)
last-result: batch-11 analyses (JOURNAL 2026-11-24T13:12Z; figures read):
             - D2 C-20261124-130442-0819c88: t_c 164.0/163.4/166.0 M for collision cells M/8, M/4,
               M/2; rates within 2.1 per cent; budget 3e-16; D2.1, D2.3 hold, D2.2 FAILED
             - block A C-20261124-130634-3338d9b: A.3, A.4 FAILED (controls collapse); kin t_c
               294.5 (0.334032), 229.8 M (0.344); kout 449.0 M (0.334032)
             - heat C-20261124-131012-f920f45: H.1-H.4 hold; f0 1.0149 (k lambda 0.2), 1.0187 (0.1)
             - run (v) C-20261124-130021-5c9c207, -130222-6a4924d: D ratio 11.1 (1/N); N.3 FAILED;
               N.4, N.6 hold by the letter (phase confound on record)
             - T C-20261124-131129-e93be29: 8.29 s per M (holds)
             - lead recheck with an independent reader C-20261124-132113-52c2abe: all t_c agree
runs:        card plan (batch 12): sequencer retired; 12 runs in the shared queue (q0016-q0018 N6c,
             M16, N4c at priority 2; q0019-q0027 nine in-place continuations at 5; HANDOFF.md
             table); A324s1c+ (C-20261123-032324-938ecbd) runs in Slurm 5206 outside the queue
next:        1. N6c (control of y0 = 0.334032 at N = 1e6 on M/8): NS.1 relaxation against NS.2
                scheme decides the threshold scan (seeds at N = 1e6, or M/16 + gauge leg + core)
             2. M16 (D2 on M/16) against M16.1-M16.2: mesh convergence of the collisional t_c
             3. as the continued chains end: A.1/A.2 complete, control t_c scatter over seeds 1-3,
                kicked-minus-control collapse times (G1 reservation 2); then a G2 verifier
blockers:    preemption by another user's priority jobs (mitigated: restart every 10 M, resume
             items); card-hours (asked of orch)
needs:       orch: +15 card-hours toward G2 after N6c (outbox 20261124T133351Z); harness: a
             segment cap that does not count preempted segments (same outbox); core: drift rate of
             its row-4 controls and a SIGTERM restart (outbox 20261124T133352Z); a G2 verifier
             later (stage/G2/OPEN.md lists what it must cover)
offers:      collision tests and references: collide/; conductivity series and reader:
             longruns/scripts/heat_series.py; D2 and block A readers, independent t_c reader
             (longruns/scripts/); queue wrapper that resumes cut chains in place:
             longruns/seq/qitem.sh; N = 1e6 King threshold particle file (C-20261124-130731-e1d24de)
budget:      G2 allotment 60 card-hours (nrpic-run budget, 21:10Z, through decision 0032): 25.71
             used by closed manifests, plus the in-place continuations (counted when they close); expected
             about 17 more for the queue (9 continuations + A324s1c+, 6 follow-ups) [JUDGEMENT].
             Batch 12: no card time; A334s3o closed as stopped (orch stopped it at 12:00 PST)
