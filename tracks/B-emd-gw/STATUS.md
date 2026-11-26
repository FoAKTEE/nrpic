# STATUS of B-emd-gw

gate:        G0 PASS (2026-11-19), G1 PASS with reservations (2026-11-21, tag
             stage/B-emd-gw/G1-pass-20261121). G2 package current (batch 23): C4, C6, C7, C10,
             C12, C13, C16, C19, C20 PASS, C8 NA (0013), the rest OPEN (stage/G2/OPEN.md: each
             item with the queue entry or running analysis that serves it). G2 not met.
headline:    The zero shift fails at the finer mesh: the 0.014 box at 256^3 stops at a = 102 after
             K_max turns positive at a = 80 (q0007, B-20261125-093500-242d3a3); the shifted gauge
             carries the 0.028 box to a = 141 (q0044). With equal GR particle masses the Gamma
             driver is the gauge closer to Newton (median |dM| 3.8 against 5.7 per cent, a = 81-132)
last-result: batch 23 (2026-11-25 18:17-19:15): M1 refuted, M4 fails where reachable (Hr 128^3
             over 256^3 1.11-1.36); P8C1, P8C2 hold (continuation repeats to 4e-12); Q1 constraint
             part holds (Mr 2.93 times smaller with 8 per cell at a = 141); S1 holds (Hr_mean
             1.1e-2 at the end); N2e, GN1e hold with equal masses (B-20261126-024936-1ee0a16,
             -024941-647553b): the rest-mass weight (R25) made GR halos 5 per cent heavier and
             had reversed GN1 in batch 21. analyze_gr.py --equal-mass, header dump times, run
             union. Note section VI and ledger updated (B-20261126-025137-7686b91).
running:     processors (registered, read next session after `nrpic-run finish`):
             B-20261126-022356-52c2460 (256^3 strain and halos, M2-M3, 3 cores),
             B-20261126-022403-82f6e69 (0.028 shifted box, S2-S3 input, 2 cores),
             B-20261126-022838-27fab1b (8 per cell joined, Q1 high-k, 1 core)
cards:       q0060 pop_s014_gr256_gd waiting (256^3 Gamma driver, priority 2, ceiling 6 card-h,
             GM1-GM4 in population/JOURNAL 2026-11-25 18:50); nothing else queued
next:        1. close the three analyses; judge M2, M3, Q1 high-k, S2, S3 (judge_s028gd.py,
                compare_legs.py), figures looked at
             2. read q0060 when it ends (GM1-GM4); then C2, C3, C11 and the G2 abstract/summary
             3. C15 split of the multi-figure scripts; strain parts of A1-A3, GD3 with equal
                masses; then a fresh G2 verifier (C18)
needs:       core: parameters added at a restart (outbox 20261125T121932Z); Fourier Newtonian
             solver with the threaded build (20261124T173601Z). kb: claim 861 [TO VERIFY].
offers:      gw_diag (TT, rho_K, spectra, E/B/Psi_4; gauge G_tot); population/scripts/
             analyze_gr.py --equal-mass; finding for every track that reads GR particle files
             with a Newtonian estimator: the masses carry the rest-mass weight W psi^6 (R25),
             which moves halo masses by about 5 per cent
budget:      card-hours toward G2: 7.86 used (this session closed 3.58: q0007 3.23, q0042 0.22,
             q0044 0.13; none submitted to run); q0060 ceiling 6; G1 1.69; allotment 40 (0014)
