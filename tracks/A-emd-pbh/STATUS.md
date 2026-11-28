# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21. G2 NOT PASSED on the independent review
             (coord/GATES.md; decision 0047). Conditions (a)-(d) for the second review; state in stage/G2/OPEN.md.
             No amplitude is compared with arXiv:2609.14218 before (c). Second review NOT yet to be asked for.
headline:    (d) NOT MET by the run made for it: S1L-F (q0090, A-20261128-012211-c9cedc1; reader
             A-20261128-073831-fce5805) finds S1L's horizon from t = 169.28 (m 5.83 -> 9.12 at t = 205), but the
             section-3 ratio outside it is 0.514 at detection (bound 0.1); the box violation sits in the matter.
             (a) the outer-face part of the ball's line ratio does NOT converge with the mesh, with or without
             core-v0.6's face set (FC, A-20261128-073120-9feebf2, reader A-20261128-080645-b3c9c7c: factor
             coarse/fine 0.70-0.92 stock, 0.64-0.87 with the set; the set lowers it ~100x). A whole-line ratio to an
             outflow face cannot fall with the mesh: a ruling is asked for. Retest RT2a queued on core-v0.9.
last-result: batch 40 (23:26-00:40 PST):
             - q0090 closed (jobs completed, 1.063 card-hours): F1 REFUTED (first find 169.3, before the window
               (178, 195]; 6 of 57 later searches at the iteration cap), F2 HELD (0.514 > 0.1), F3 REFUTED (history
               off S1L's by ~1e-3 from t = 50, S1L's own restart point).
             - FC: FC0 held (proxy = full meshes in the face band), FC1 held, FC2 REFUTED (no convergence with set).
             - RX (restart exactness of the box deck on processors, A-20261128-074500-daf8285): RX_RESULT
             - RT2a smoke (A-20261128-075804-b2908e4): v0.9 decks with the face set and region norms run.
cards:       shared queue, priority 2: q0089 a-s1l-quarter SUBMITTED (A-20261128-011607-3e2d530, chain at t = 133 of
             410, job 5633 pending); q0108 a-rt2a-A and q0109 a-rt2a-B WAITING (core-v0.9 card build, caps 0.5 and
             1.2 card-hours). 0 card-hours ran in this session; 1.063 closed (q0090).
processors:  8 registered runs this session (1 failed: RX first attempt, stopped by me on cost); at most 6 cores.
next:        1. Read q0108/q0109 (RT2a, predictions R1-R3, threshold_ball entry 20) and q0089 (A2Q) when they end.
             2. (d): the cause of the box violation - resolution pair of region ratios (P0L four vs P0L6 six levels).
             3. (a): with orch's ruling on what the bound covers, faces farther out or a coarser outer level for the
                face part; the top-hat matter part separately.
blockers:    G2 not passed; (a) face part does not converge by construction; (d) the box violation in the matter.
needs:       orch: a ruling on 0047 2(a) - is the bound read over the whole line to the outflow face, or over the
             matter/inside a radius, given FC; core: RX_CORE_NEED.
offers:      threshold_ball/scripts/face_conv.py (band norms, coarse/fine factors), decks nest*_L32_fr (face set +
             region norms); periodic_threshold/scripts/f_read.py (status, region at detection, history vs a
             reference with chain segments resolved), rx_run.sh/rx_compare.py (restart exactness).
budget:      card-hours batch 40: 0 ran, 1.7 newly capped in the queue (2.6 still capped for q0089).
