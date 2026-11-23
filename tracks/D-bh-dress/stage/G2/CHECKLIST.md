# Checklist: D-bh-dress G2

Collected by `harness/bin/nrpic-stage collect D-bh-dress G2` on 2026-11-23T02:09:59Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: The section-10 rows D owns (scope/SCOPE.md section 6) are not yet assembled into a G2 ladder table. Available: Einstein-Straus null test (N, entry 5), dust growth against the exact LTB solution (G, entry 5), Newtonian self-similar infall at two resolutions (Q16, Q16-256 D-20261123-020626-183c254), Kerr spike stationarity (G1). Missing: the table itself and the verifier.
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Mesh spacing: vacuum and null test at M/8 (D-20261121-203124-a34cf1f, -203131-8ee2a49) and M/16 (D-20261121-203151-37e7b2d; -59c54fb running); the finder mass changes sign between them (H1 failed), so the third member M/4 is queued (entry 6: FV4, FE4). Boundary: faces +-192, +-384, +-768 M compared (V2, E1, F1 of entry 5). Gauge: lapse_leak pair of G1 (ES-1GB/V-1GB). Particle number: none yet for the dust run (ES-FL at one particle count). Growth law at one mesh (ES-FL M/8); ES-FL4 queued.
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: Volume norms bounded in all five runs (entry 8, D-20261123-021027-e3af9b8, constraints_long.png L), but they integrate the region inside the horizon beyond the chi cut; an exterior norm (region_*) is not in the inputs yet.
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: ES-F (D-20261121-144631-aa7ce9b) and ES-FL (D-20261121-203150-15f2bad, 850724 particles, 500 M): kinetic matter falling into an evolved puncture in full GR; analyses D-20261123-020606-fa0046c, -020614-7ba5874.

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md and OPEN.md written in this session; the package is not complete (C1-C3, C9-C12, C16, C17 open).
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Every run registered with manifests and inputs (g2long/inputs, tools); no consolidated rerun script for G2 yet.

## Track-specific criteria of D-bh-dress for G2 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [x] **C7** In the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor
  - status: PASS
  - evidence: Criterion N of g2long entry 1 (fixed before the runs): max |D_ES1L - D_V1L| on 100-500 M = 2.28e-4 against the threshold 2.51e-4 = 2 F_V(500); never above the refutation level 3.76e-4 (judge_long D-20261123-020550-f9a3482, judge_long.png L). At M/16 to 225.6 M the difference follows the M/8 one (H3, partial). Reservation: the margin is 9 per cent, and the floor F_V itself is a resolution-independent step at 240-300 M whose cause is not known.
- [x] **C8** With matter filled in, the mass growth agrees with the integrated particle flux through the horizon
  - status: PASS
  - evidence: Criterion G of g2long entry 1: (iii) every 10 M bin of tau_rem <= 650 M within +-0.62 per cent of the exact LTB mass (61 bins), D2 at all 960 samples (esf_criteria D-20261123-020614-7ba5874, esf_criteria.png L; esf_bracket.png L). Reservations: one mesh spacing and one particle number; D1 closure +9.4e-3 at 500 M (predicted below 8e-3); the step at tau_rem ~ 285 M follows the end of horizon excision at 219 M (entry 5 F4; ES-FLK queued).

## Minimum figures at G2 (brief 13.4)

- [ ] **C9** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic for G2 yet.
- [ ] **C10** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: judge_long.png panel (a)-(c) is a two-resolution mesh figure; particle-number and gauge figures missing.
- [ ] **C11** Data figure: Constraint norms against time
  - status: OPEN
  - evidence: constraints_long.png (D-20261123-021027-e3af9b8) shows the volume norms against time; exterior norms missing (C3).
- [ ] **C12** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: No slice mosaic of the G2 runs yet.

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: CHECKLIST, EVIDENCE, OPEN, STAGE_REPORT present; REVIEW.md not written for G2 (the lead review is stage/REVIEW-wave3.md section 13); scope text scope/SCOPE.md.
- [ ] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: G2 figures so far drawn with figstyle (judge_long, esf_criteria, esf_bracket, esf_growth, constraints_long), each PNG looked at by the lead; not yet in the note.
- [ ] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: The note schematics are those of G1 (note/figures/schem_*); no G2 update.
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: Note v2 (note/, 22 pages, checker passed --compile per note/README.md) covers ES-F to 200 M; the long runs are not in it.
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet.
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions of entry 1 on record in g2long/JOURNAL.md entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2) and of QR3/QR4 in secondary_infall/JOURNAL.md.
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of this session.
