# G1 of F-hills: what the gate still lacks (2026-11-24, lead, batch 11)

1. **A complete vacuum Hills passage (T4, CHECKLIST C8).** P1 (m/8) merged its binary at 48.8 M.
   P1b at m/16 (run A, F-20261121-203144-b2cf16b) reached t = 61.8 M with its members unmerged
   (s = 2.74 M) and was cut by preemption; the isolated m/16 pair (R16n + B) does not merge
   before 107.85 M (turns at 3.12 M at 73.9 M; analysis F-20261124-130009-33bef4d), so the
   passage can be tested. Continuation A2 (from 61.80 M, restart files every 1 M, 19.5 card-hours
   of G1) is registered and on the cards behind the sequencer `binary_conv/scripts/seq_b11.sh`;
   predictions A2-1 to A2-5 in JOURNAL.md, batch 11. G1 needs A2 to the separation of the binary
   (at least about 170 M). If A2's 19.5 card-hours end before that, the allotment request to orch
   (outbox 20261124T135319Z) decides how the tail runs.
2. **Verifier of the G1 material (C18).** None yet. To be asked when item 1 is done, with: note
   v2 ledger tables, KHSR K3 (khsr_note scan F-20261121-212757-77cdc15), P1 to 280 M
   (`khsr_note/results/p1_280.json`), junk_gauge, eih, binary_conv, kerr, and the batch-11 card
   analysis (F-20261124-130009-33bef4d, F-20261124-132934-375a163).
3. **Note v3.** The passage section (A2, C2), the junk at P1b's spheres (T3 reservation), the
   duplicated legend of fig_elliptic, floats after Sec. VI, the reviewer step of the
   paper-writing procedure. v2 (24 pages) compiles and its checker is clean except accepted
   items (lead's rebuild, batch 11).
4. **Reservations on T3 (C7).** The three-hole junk is measured with P1's m/8 binary; most of the
   window's energy is a steady emission of unidentified source; extraction stops at l = 8. To be
   remeasured at P1b's spheres (A2's waveforms).
5. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end in `m_at`; binary_conv's README labels fractional mass drifts "per M" and its
   "Results" row for 20 M at m/16 is out of date; geodesic_binary S4 (Kerr, chart 'cks') carries
   the slicing pump (rerun in 'bks'); the horizon finder's sawtooth band in m_AH (up to 4e-3,
   fig_b11_health) is not filtered by nrread.
6. **For G2 (not G1).** The second resolution of the passage C2 (m/12, from 20.0 M; G2 24
   card-hours, held until B2 ends); B2 (the isolated pair to its next apocentre: decay per orbit
   against Peters); g2mesh G2M-2/3 (card batch analysis; `scripts/card_analysis.py` committed
   as work in progress); the gauge leg (mass-scaled profile of junk_gauge); the member masses of
   C drift 1.2-1.7e-4 per M (above A4's bound).
