# G0 of F-hills: what the gate still lacks

State of 2026-11-19 (lead, wave 2b). The wave-1 items with their present state; closed items
stay listed with what closed them.

1. **Stage check.** Run: `CHECKLIST.md` (collect 2026-11-19), `VERIFY_RESULTS.md`
   (`nrpic-stage verify`), `STAGE_REPORT.md` (`nrpic-stage report`). OPEN only through item 2.
2. **Verifier's report (C18): OPEN.** No `VERIFIER.md`. A second agent checked the plan's
   load-bearing claims in wave 2 (`SECOND_CHECK.md`: novelty verdict holds; both baseline drivers
   have no defect; the q = 10 disagreement is physical capture, its size inflated in HRNA by the
   initial-binary convention and a spurious self-acceleration; the q = 10 start state turns at
   5.77 M in GR); the lead reproduced its last finding with own code (V9a). It did not recompute
   the note's ledger. Asked of orch: a fresh verifier, or a ruling that `SECOND_CHECK.md` serves
   as the verifier's report on the plan (decision 0016 item 4).
3. **Objects (0005): CLOSED** by decisions 0013 and 0017: (a) then (b) right after the first (a)
   passage, then (c).
4. **Allotment: CLOSED** by decisions 0014 (50 card-hours to G1) and 0016 item 7 (120 toward G2).
5. **Mass ratio of the scan lines: CLOSED** by decision 0013 (q = 4 for convergence and the first
   scan line; q = 10 when the mesh fits). Consequence: q = 4 at m/16 needs 2864 MeshBlocks
   (SCOPING section 9, corrected), above the 2700 slots of one card: two cards or 32^3 blocks
   (core, `dfix-answers`: larger blocks need no source change; benchmark not run).
6. **Capability: CLOSED.** Several moving black holes are in release core-v0.3 (CLAUDE.md); the
   track has run them (nr_first E1-E11; P1 submitted, run F-20261119-150017-b45ec5f).
7. **newton3 energies at finite q: CLOSED** by the Jacobi split (newton3_fix; runs
   F-20261115-174139-3340bf3, F-20261115-175232-d399e83; tests 15/15, lead V10 run
   F-20261119-145509-fb91531). Left: `three_punctures/scripts/newton_start.py` reads the old fields
   (its wave-1 outputs are records; not rerun).
8. **Unverified items carried**: Roche-lobe factor now located (Eggleton 1983 via 2002.10547
   `hills.tex:353-357`, kb answer `locators-wanted`; 0.379 for equal masses); the quadrupole
   energy of a parabolic flyby has no source in the knowledge base (kb: not found); SKR's
   retrograde criterion (H1) and D-uniform averages; 2402.02178 not reproduced (G1 T2); cause of
   HRNA's release-radius dependence (C2; the second check's self-acceleration is a candidate, test
   R3 open).
9. **Correction to the brief l. 275**: carried by `coord/BRIEF_ERRATA.md` (decision 0016 item 8)
   if orch took it; not checked again here.
10. **Object (b) inputs**: boosted equilibrium clumps are core's wave-3a package
    (`core/clump-table`); the clump model from Track C is still open.
11. **Corrections of wave-1 statements found in wave 2/2b** (`../REVIEW-wave2.md`): V4b covers
    seven, not nine, points; SCOPING section 9's q = 4 m/16 row (corrected); HRNA percentages
    are model outputs at release 4 r_t, not predictions; P1 is at q = 4.
