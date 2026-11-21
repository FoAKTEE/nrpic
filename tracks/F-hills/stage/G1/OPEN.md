# G1 of F-hills: what the gate still lacks (2026-11-21, lead, batch 5)

1. **A complete vacuum Hills passage (T4, CHECKLIST C8).** P1 (run F-20261119-150017-b45ec5f)
   ended at t = 280 M, but its binary merged at t = 48.8 M before the passage; the cause is the
   m/8 member resolution (binary_conv; decision 0022 item 4). Rule P1b-D held in batch 5 (clause
   D1; analysis F-20261121-202021-3c4321e): P1b at m/16 runs as chain F-20261121-203144-b2cf16b
   (31 segments, tlim 200; days of queue). Open risk R19: the converged isolated binary shrinks
   (0.196 M by 20 M); the R16n extension F-20261121-203156-03efdd3 (to 120 M) decides whether the
   pair survives to the pericentre. Second resolution of the passage: F-20261121-203247-961801d
   (m/12, held until the extension ends; released by `binary_conv/scripts/seq_release.sh`).
2. **F-pre-1: KHSR (1201.4794)** not reproduced (G0 verifier D8); one result planned with
   newton3 (`e_orb`, processor minutes; SCOPING 5). (C6)
3. **Note (C15, C17).** The G1 revision of `note/main.tex` is written (paused package);
   registered rerun of `run_all.py`, compile, checker and page reading not done; the lead's
   ledger corrections (verifier D7, D9, row 57) wait for that rerun; the Kerr row, P1's merger
   and its cause, and the junk numbers of batch 4a are not in the note.
4. **Verifier of the G1 material (C18).** None yet; to be asked when items 1-3 are done.
5. **Reservations on T3 (C7).** The three-hole junk is measured with P1's m/8 binary, which
   spirals in numerically; most of the window's energy is a steady emission whose source is
   not identified; extraction stops at l = 8. To be remeasured at P1b's spheres.
6. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end in `m_at`; binary_conv's README and BC-3 label fractional mass drifts "per M";
   geodesic_binary S4 (Kerr, chart 'cks') carries the slicing pump (rerun in 'bks').
7. **For G2.** q = 4 at m/16 fits one card (3000 slots at 78785 MiB; g2mesh's analysis
   pending); the G2 resolution ladder must start at m/16 (m/8 merges the binary), which raises
   its cost; the G2 plan is re-costed after P1b; the gauge leg (mass-scaled profile of
   junk_gauge) moves to G2.
