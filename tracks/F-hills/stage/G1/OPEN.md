# G1 of F-hills: what the gate still lacks (2026-11-21, lead, batch 2a)

1. **A complete vacuum Hills passage (T4).** P1 (run F-20261119-150017-b45ec5f) will reach
   t = 280 M with segment 15 or 16 of its chain (segment 14, Slurm 4769, running at 22:24 PST
   2026-11-20), but its binary merged at t = 48.8 M, before the passage (p1 entry 4; lead run
   F-20261121-063449-4dcca98). Cause not established; the deciding test is the isolated binary
   at m/8 and m/16 (about 60 M; RISKS R15). Then a passage that keeps its binary.
2. **Junk radiation of the three-hole data (T3).** Single member measured (junk_gauge, not yet
   reviewed by the lead); three-hole junk from P1's spheres predicted (J4), not measured; P1's
   spheres also carry the merger signal after t = 48.8 M.
3. **F-pre-1: KHSR (1201.4794)** not reproduced (G0 verifier D8); one result planned (SCOPING 5).
4. **F-pre-2 for Kerr (T2).** Package `kerr` cut before any outcome (uncommitted predictions).
5. **Note.** The G1 revision of `note/main.tex` is written (paused package); registered rerun of
   `run_all.py`, compile, checker and page reading are not done; the lead's ledger corrections
   (verifier D7, D9, row 57) wait for that rerun.
6. **Verifier of the G1 material.** None yet; to be asked when items 1-5 are done.
7. **Gauge (E10).** S2g analysed by junk_gauge (runs F-20261120-222403-b8dc28c,
   -222415-137ada9) but E10's outcome is not recorded in `nr_first/JOURNAL.md`.
8. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end in `m_at`.
9. **For G2.** q = 4 at m/16 fits one card (3000 slots at 78785 MiB, g2mesh card run; its
   analysis by g2mesh pending); the G2 plan is about 100 card-hours (SCOPING 9) and is re-costed
   after item 1; a q = 10 passage needs momenta from a GR parabola (verifier D1).
