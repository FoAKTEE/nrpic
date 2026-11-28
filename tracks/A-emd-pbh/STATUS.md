# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21. G2 NOT PASSED on the independent review
             (coord/GATES.md; decision 0047). Conditions (a)-(d) for the second review; state in stage/G2/OPEN.md.
             No amplitude is compared with arXiv:2609.14218 before (c).
headline:    (b) MET on the existing restart files: with `flow = shear` the finder finds S1L's horizon at t = 190.0,
             198.7, 220.0 (m 7.61, 8.34, 10.74) and P0L6's at t = 140 (m 6.3032) from every start, nothing at P0L6
             t = 130 (A-20261128-004123-bc1fcf8); only the t = 118.1 false acceptance is untestable (no restart file).
             (a) narrowed and partly NAMED: the part of the ball's section-3 line ratio that does not converge enters
             at the outflow outer faces (R-split A-20261128-004947-8fc6ba9; OB A-20261128-004659-f512816: faces moved
             to 32 cut it 300-fold on 0 < x < 16); inside the matter the smooth CIC member converges (0.059 -> 0.016).
             (c), (d) queued on cards (q0089, q0090), predictions A2Q and F1-F3 committed first.
last-result: batch 34 (16:32-17:35 PST):
             - D-q holds (quarter data, A-20261128-003940-60a3521); SM-F holds; SM-q's start-up step clause REFUTED
               (step falls with the amplitude), queued anyway with the reason on record.
             - FD holds on every tested clause (t = 180 clause untested: file mapping).
             - C3-G's batch-31 reading WITHDRAWN (frozen matter makes a violation by construction; entry 18).
             - OH UNDECIDED (A-20261128-005454-eb7b26b): the line reader is not accurate enough.
             - OB: 13-16 part and matter clauses hold; the total clause refuted at t = 1 (matter + edge = 0.091 on M/16).
             - LF REFUTED (A-20261128-005331-874ec88): a level face in the matter keeps the interior residual 2.4x
               higher at t = 2 (M/4). FR (A-20261128-011908-0e41713): core-v0.6's outer-face set cuts the outer
               part 70-100-fold to t = 2 (better than predicted; matter and edge parts unchanged).
             - S1L's region ratio outside r = 0.6 is 0.43 at t = 190 (periodic: violation in the collapsing matter).
cards:       shared queue, priority 2: q0089 a-s1l-quarter SUBMITTED 17:16 (run A-20261128-011607-3e2d530, job
             5545, cap 2.6 card-hours); q0090 a-s1l-finder WAITING (cap 1.6). 0 card-hours used by this session.
processors:  19 registered runs this session (2 failed: FR start, a figure colour), all closed; at most 6 cores.
next:        1. Read q0090 (F1-F3) and q0089 (A2Q) when they end (periodic_threshold JOURNAL, scripts named there).
             2. Ball: deposit-fix build with the v0.6 face set (FR) and faces at 32, S2c-A/B and LF to t = 2 on
                processors, prediction first; then smooth CIC bracket members on two meshes to the horizon (cards).
             3. Box violation (condition (d)): a resolution pair in the box (P0L four vs six levels' region ratios).
blockers:    G2 not passed; (a) the outer faces of the ball; (d) the box violation in the collapsing matter.
needs:       core: outer-face options for the expanding ball; card check q0086 of the faces-finder build.
             orch: the second review of (b) on the existing files; note that 0047 item 6's C3-G sentence is withdrawn.
offers:      threshold_ball/scripts/ratio_split.py (section-3 ratio by region), offline_h_line.py (spherical line
             reader); periodic_threshold/inputs/peak_leak_f.athinput (box deck with flow = shear);
             conv_ball/scripts/prep_bh.py --custom (lattices on any level list).
budget:      card-hours batch 34: 0 used, 4.2 capped in the queue. Processors: up to 6 cores, ~50 min.
