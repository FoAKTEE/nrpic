# G0 of F-hills: what the gate still lacks

State of 2026-11-21 (lead, batch 2a). Closed items stay listed with what closed them.

1. **Stage check.** `CHECKLIST.md` (collect 2026-11-21: 20 items, all judged), `VERIFY_RESULTS.md`
   (`nrpic-stage verify`), `STAGE_REPORT.md` (`nrpic-stage report`). The harness verdict fails only
   on items outside the plan (item 6).
2. **Verifier's report (C18): CLOSED** by `VERIFIER.md` (fresh verifier, batch 1 of 2026-11-20):
   20 claims; ledger tables 1-2 recomputed 57 of 57 (run F-20261121-035817-0aca1c5, rerun by the
   lead F-20261121-063712-25981e0). Every WRONG or PARTLY item (D1-D10) is answered in
   `../REVIEW-wave3.md` and corrected in `SCOPING.md` ([amended: D<n>]), `note/main.tex`, the risk
   list, or listed for the note's ledger rerun (D9, row 57; `note/JOURNAL.md`, lead entry).
3. **Objects (0005): CLOSED** by decisions 0013 and 0017.
4. **Allotment: CLOSED** by decisions 0014 (50 card-hours to G1) and 0016 item 7 (120 toward G2).
   The G2 plan is corrected to about 100 card-hours (SCOPING 9, verifier D3).
5. **Mass ratio of the scan lines: CLOSED** by decision 0013. q = 4 at m/16 (largest tree 2864)
   fits one card: 3000 slots ran at 78785 MiB of 81920 (g2mesh run F-20261120-222810-e408386;
   verifier D5).
6. **Harness FAILs that are not about the plan**: (a) three wave-2 run directories with outputs
   moved in after the runs (waiver asked of orch on 2026-11-19 and again 2026-11-21, for
   `coord/WAIVERS.md`); (b) P1's chain (run F-20261119-150017-b45ec5f) is still running; (c) the
   worktree holds the uncommitted files of two packages cut on 2026-11-20 (`kerr/`,
   `g2mesh/scripts/card_analysis.py`), left alone as instructed.
7. **newton3 energies at finite q: CLOSED** (Jacobi split; lead V10).
8. **Unverified items carried**: the quadrupole energy of a parabolic flyby has no source in the
   knowledge base; SKR's retrograde criterion (H1) and D-uniform averages; 2402.02178 not
   reproduced (G1 T2, package kerr in progress); KHSR (1201.4794) not reproduced (verifier D8;
   planned at G1, SCOPING 5).
9. **Correction to the brief l. 275**: errata row 1.5 to be reworded (verifier D6, N3; outbox to
   orch 2026-11-21).
10. **Object (b) inputs**: C-sidm's King and polytrope models are available (answer of 2026-11-19);
    core's boosted table clumps are in progress (`core/clump-table`).
11. **Corrections of earlier statements**: wave 2/2b in `../REVIEW-wave2.md`; wave 3 (the
    verifier's D1-D10) in `../REVIEW-wave3.md`.

Judgement [JUDGEMENT]: the G0 package is complete for an independent review (decision 0016
item 4). The lead does not pass the gate.
