# STATUS of C-sidm

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-27, decision 0048 item 1; coord/GATES.md). Working toward G3
             (80 card-hours). G2 package corrected after the gate review (batch 35); the stage
             check keeps one FAIL, 'runs', for heat_C1/heat_C2 (snapshots deleted by their
             reduction; reruns queued)
headline:    the collisionless threshold of the King b = 1 family lies in (0.324, 0.344), around
             the first maximum of the binding energy y_max = 0.334032 (arXiv:2009.08163
             paper.tex:952-958), same fates at N = 1e6 on M/8 and M/16, with shift_eta 2.0 and 1.0,
             and at N = 1e5. A bracket, not a converged location; lapse marker, no finder
last-result: batch 35 (JOURNAL 2026-11-28T01:59Z-02:20Z):
             - G3 scope written before any production run: scope/SCOPE_G3.md (first step: b = 0.1
               and monoenergetic brackets at N = 1e6, two meshes, finder, three seeds; then
               f_BH(Kn) with estimator, reference, criteria F1-F4, H1, K1-K4, B1, C1)
             - b = 0.1 particle files at N = 1e6 (C-20261128-020723-f3d27b8, -020724-5fb45c3,
               -020724-14139b1, -020724-3fb58bb; P1a.1-P1a.3 held)
             - smoke tests C-20261128-021146-0f3b8f2 (caught: finder never searches without
               start_time_0/stop_time_0) and -021714-46cc308 (fixed: status rows written)
             - reduction of the heat package writes into its own run dir, deletes nothing
in-flight:   queue q0092 heat_C1r (C-20261128-021624-9c11a74, job 5567), q0093 heat_C2r;
             q0096 G3A-C, q0097 G3A-56, q0098 G3A-52, q0099 G3A-60 (all priority 2)
budget:      G3 80 card-hours; reserved 0.6 (heat) + 16 (G3A, 4 each); used 0 at 02:20Z
next:        1. close and read q0092/q0093 (sacct COMPLETED first), reduce each into its own
                registered run, heat_series.py on the two reduction ids; judge HR.0-HR.5
             2. close and read q0096-q0099: nseries.py and the finder's status/summary files;
                judge G3A.1-G3A.7, F1-F3; queue 1b/1c/1c' with predictions first
             3. independent review of scope/SCOPE_G3.md (requested from orch); monoenergetic
                deck generator (2b)
risks:       RISKS.md 1-29; new 27 (finder defaults), 28 (b = 0.1 threshold may lie beyond
             0.60), 29 (b = 0.1 card cost)
open G2 owed: bracket-leg constraint histories in a package figure; two labels of
             schem_ladder.png still say "turning-point" (need a registered note run)
