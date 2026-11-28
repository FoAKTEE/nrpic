# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19; G1 PASSED with reservations 2026-11-21. G2 NOT PASSED on the independent review
             (coord/GATES.md; decision 0047). Conditions (a)-(d) for the second review; state in stage/G2/OPEN.md:
             (a) NOT met, (b) met, (c) PARTLY (ruling asked), (d) NOT met. Second review NOT yet to be asked for.
headline:    (c) the lag of the triaxial crossing is first order in the curvature perturbation: the quarter-amplitude
             member crosses in (34.77, 35.28] t_H, inside the predicted band (A2Q holds; q0089, A-20261128-011607-3e2d530);
             c = ln(lag_a)/zeta ~ 1.5 over a factor 4 in amplitude, the gradient-expansion factor (c = 2) refuted; the
             mechanism within the class is not separated. (a) on mesh A of the retest (core-v0.9, faces at 32 + face
             set): exterior ratio 0.907 at the first held horizon (t = 46.0), because 95 per cent of E is inside it;
             the face set cuts the outer-face part 6-7x over 45 M. Mesh A stops at the guard at t = 48.14 (known blow-up,
             reproduced on processors in 9 cycles).
last-result: batch 41 (07:58-08:40 PST):
             - A2Q: readers A-20261128-160444-e6c646e, -160447-c41d66a, -160446-6c171f3 (figures looked at).
             - RT2a-A (q0108, A-20261128-081045-1e001cd) FAILED at the guard t = 48.140625, MeshBlock 31 (level 4) at
               (-0.4375, -0.4375, -1.4375), inside the matter; GA (A-20261128-160727-0d75d4e) reproduces it exactly
               from the t = 48.0 restart file. Reader rt2a_read.py (A-20261128-160831-6fd1da1): RA1 held, RA2 refuted at
               t = 45.75 (1.59 > 1.5), RA3 held (0.907 > 0.1).
             - DR (A-20261128-161728-cabd2c5): the box violation of (d) does not fall with two more levels at the same
               particles (P0L/P0L6 0.94 at t = 100, 1.75 at t = 130): not mainly mesh truncation at the peak.
cards:       shared queue, priority 2: q0109 a-rt2a-B WAITING (mesh B of RT2a, core-v0.9 card build, cap 1.2 card-hours;
             five jobs of other owners in Slurm). q0089 done (2.2517 card-hours), q0108 marked done (0.0908; guard stop
             after its reading time). Nothing newly queued.
processors:  5 registered runs this session (4 analyses, 1 four-thread reproducer of 48 s); at most 4 cores at once.
next:        1. Read q0109 (B-F) with rt2a_read.py (add B-F=<run dir>) and analyse.py; judge R1-R3 of threshold_ball
                entry 20 and (a) per 0051 item 4; then the domain leg (faces at 64 with the set) for the outer part.
             2. (d): the sampling leg at fixed mesh (P0L's deck with 8x the particles), prediction first.
             3. (c): after orch's ruling, either nothing or a run separating the data's zeta-delta relation from the
                dynamics; the Newtonian quarter control N-z128 at mu = 0.075 (processors, ~2 h) in either case.
blockers:    G2 not passed; (a) inner part 0.89 on mesh A and outer part normalised by a small exterior E; (d) the box
             violation in the matter, not mesh-limited.
needs:       orch: ruling on what "named within the class" asks for (c) (outbox b41-condition-c-ruling-and-a-on-mesh-a);
             core: info only (outbox b41-mesh-a-guard-stop-reproducer-v09).
offers:      threshold_ball/scripts/rt2a_read.py (exterior ratio split from region.hst), ga_repro.sh (9-cycle guard
             reproducer); periodic_threshold/scripts/box_region_pair.py (box ratio parts, two members).
budget:      card-hours batch 41: 0 ran in this session, 2.343 closed (q0089 2.2517, q0108 0.0908); 1.2 capped (q0109).
