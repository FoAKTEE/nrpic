# STATUS of F-hills

gate:        G0 package complete for an independent review (VERIFIER.md in; every WRONG item
             corrected or answered, stage/REVIEW-wave3.md; review asked of orch 2026-11-21);
             G1 not met (stage/G1/STATUS.md): P1's binary merged before the passage; KHSR, Kerr,
             three-hole junk, note compile and a G1 verifier open
headline:    The first full-GR Hills passage (P1, q = 4, members at m/8) did not test the Hills
             mechanism: its binary merged at t = 48.8 M, long before pericentre, which no reference
             model does; the members' resolution is the prime suspect.
last-result: - P1 merger confirmed by the lead's own parser (F-20261121-063449-4dcca98): separation
               < 0.1 M at t = 48.79 M, common horizon 0.2686 M at 48.81 M; remnant passes the heavy
               hole at 7.0 M (coordinate) at t = 155 M; p1 entry 4 (F-20261120-223252-ca18a81)
             - G0 verifier (verify_g0): 20 claims, ledger 57/57 (F-20261121-035817-0aca1c5, rerun
               F-20261121-063712-25981e0); WRONG items D1-D8 checked (F-20261121-063504-00f0743) and
               corrected in SCOPING ([amended: D<n>]), note text, RISKS
             - eih (1PN reference) reviewed: tests 9/9 identical (F-20261121-063520-abab33e); T5 and
               T4 reproduced by own integration to 1e-9 (F-20261121-063646-d826df4); first own
               attempt failed by method (F-20261121-063527-b4453db)
             - q = 4 at m/16 fits one card: 3000 slots ran at 78785 MiB (g2mesh F-20261120-222810-e408386)
             - junk of one member E/m = 7e-5 (4e-5 to 2e-4; junk_gauge, not yet reviewed)
next:        1. Isolated binary (the two members of P1, same gauge and data) at m/8 and m/16 for
                about 60 M: does m/8 alone merge it? (decides R15 and the whole G2 ladder)
             2. When P1's chain is DONE: nrpic-run finish F-20261119-150017-b45ec5f; p1 run_all.sh
                and p1_analysis.py to t = 280 M; junk_gauge J4; record E10's outcome
             3. Close the cut packages: note (rerun, compile, check, pages; lead's ledger list in
                note/JOURNAL.md), kerr (2402.02178), g2mesh (G2M-2 analysis); KHSR result (newton3);
                then a fresh G1 verifier
blockers:    P1 is not a Hills passage until the merger is understood (no blocker outside the track)
needs:       orch: G0 independent review; waivers for three wave-2 run directories; errata row 1.5
             rewording; chain rule for outside kills (outbox 20261121T*); core: tracker files on
             restart (reminder), Bowen-York momenta vs canonical 1PN momenta
offers:      readers of AthenaK trackers/horizons/waveforms (nr_first/scripts/nrread.py); tracker-keeping
             chain wrapper; MeshBlock tree model (g2mesh/scripts/tree3.py, exact against 22/23 restart
             trees); Newtonian three-body driver; HRNA reference; 1PN (EIH) three-body reference with
             trust ranges (eih/eih.py, T4); own raw-file parser (stage/review_wave3/review3.py)
budget:      card-hours used toward G1: about 11.5 (P1 10.72 to segment 14 by sacct, S2g 0.52, wave 2
             0.30); toward G2: 0.05 (g2mesh); P1 needs about 1.5 more to t = 280 M; allotment 50 to
             G1 (0014), 120 toward G2 (0016)
