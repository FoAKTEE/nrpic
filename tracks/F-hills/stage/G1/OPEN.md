# G1 of F-hills: what the gate still lacks (2026-11-25, lead, batch 21)

G1 is NOT met. Item by item, with what the fresh verifier of the gate (C18) will need.

1. **A complete vacuum Hills passage (T4, CHECKLIST C8).** P1 (m/8) merged its binary at 48.8 M.
   P1b at m/16: A (F-20261121-203144-b2cf16b, 0-61.8 M) + A2 (F-20261124-210400-902c650, queue
   q0001, chain still going; next segment Slurm 5294 pending while the cards are held) reach
   96.23 M (batch 21, PARTIAL, F-20261125-170453-1175d44): the pair passed its own closest
   approach (2.11 M at 76.4 M) unmerged; the centre of mass is 13.06 M from M and closing; both
   members are still bound to M and to each other (F-20261125-170646-6dd4ae4). Missing: the
   passage's pericentre (A2-2) and the separation (A2-3, at least 170 M). Projection (JOURNAL
   batch 21): the chain's segment cap stops it at 125-140 M; a continuation through a `--cmd`
   queue entry within A2's 19.5 card-hours (5.64 used) reaches the separation if preemptions
   stay moderate (request to orch: outbox a2-tail-plan). Nothing of the trajectory is lost to the
   tracker-file truncation: the wrapper keeps every segment's copy and the join is exact (S1-S3).
2. **Verifier of the G1 material (C18).** None yet. To be asked when item 1 is done. Material:
   note v2 ledger tables; KHSR K3 (khsr_note scan F-20261121-212757-77cdc15); P1 to 280 M
   (`khsr_note/results/p1_280.json`); junk_gauge, eih, binary_conv, kerr; the batch-11 card
   analysis (F-20261124-130009-33bef4d, F-20261124-132934-375a163); the passage A + A2 (run
   directories above; readers `nr_first/scripts/nrread.py`, `stage/review_wave3/b11_cards.py`,
   `b11_passage.py`, `b21_a2_state.py`); the horizon recheck (`b21_horizon_recheck.py`, runs
   F-20261125-170540-aa39bea, -170632-5aa9786). What the verifier needs to know: (a) no run of
   this track has `<fastflow> diagnostics` (no horizon_status file): every horizon number is
   "made without the diagnostics" and the recheck uses the failure signature (decision 0041
   item 4 accepted that route for Track D); (b) tracker files are truncated at each restart in
   the executables used (core-v0.3/v0.5 card builds); the segments' copies are in
   `<rundir>/trk_keep/<UTC stamp>/`, oldest first, and the live file is the newest segment;
   (c) horizon summaries, histories and waveforms are appended and repeat times after a restart
   (keep the last row per time); (d) column 1 of the horizon summary is the integrator stage,
   not the cycle; (e) the m_AH sawtooth band (up to 4e-3, accepted searches, fig_b21_horizon_recheck
   panel b) is not removed by any filter: read slopes, not single rows; (f) the energies are
   coordinate quantities (R6).
3. **Note v3.** The passage section (A2), the junk at P1b's spheres (T3 reservation), the
   duplicated legend of fig_elliptic, floats after Sec. VI, the reviewer step of the
   paper-writing procedure. v2 (24 pages) compiles.
4. **Reservations on T3 (C7).** The three-hole junk is measured with P1's m/8 binary; most of the
   window's energy is a steady emission of unidentified source; extraction stops at l = 8. To be
   remeasured at P1b's spheres (A2's waveforms: 137 samples per sphere from 62 to 96 M so far,
   batch 21 S3; A's waveforms 0-61.8 M).
5. **Wording to correct (batch 21, H2, H4).** RISKS R4 and the G1 texts: m/8 member drift
   "0.9-1.7e-3 per M" (R8 10-21 M gives 0.92e-3), not 1.0-1.7e-3; C's members 1.22e-4 and
   1.71e-4 per M. P1's heavy hole: within 0.7 percent of its median after 1 M (the first three
   searches, t <= 0.125 M, read 0.984). Every such number: "made without the diagnostics".
6. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end in `m_at`; binary_conv's README labels fractional mass drifts "per M" and its
   "Results" row for 20 M at m/16 is out of date; geodesic_binary S4 (Kerr, chart 'cks') carries
   the slicing pump (rerun in 'bks').
7. **For G2 (not G1).** C2 (m/12 from 20.0 M; q0003, waits after B2) and B2 (q0002, the pair
   alone to its next apocentre); g2mesh G2M-2/3; the gauge leg; C's member drift above A4's
   bound. Every new run that uses the horizon finder sets `<fastflow> diagnostics = true`
   (decision 0041 item 5). A2, B2 and C2 continue from restart files and CANNOT get it by a
   command-line override: `diagnostics` is read with DoesParameterExist (z4c/fastflow.cpp line 285)
   and so never enters a restart file, and a command-line parameter absent from the restart's block
   is fatal (parameter_input.cpp lines 397-403). Do NOT add `fastflow/diagnostics=true` to a
   chain's EXTRA_ARGS: the next segment would exit at start-up. Request to core: outbox
   finder-diagnostics-on-restart. Until then their horizon numbers carry "made without the diagnostics".
