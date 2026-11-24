# Checklist: D-bh-dress G2

Collected by `harness/bin/nrpic-stage collect D-bh-dress G2` on 2026-11-24T17:29:13Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: Ladder table stage/G2/LADDER.md (rows D owns: Einstein-Straus null test N at M/8 and M/16 with the converged-finder re-search FP; self-similar infall Q16/Q16-256; D's growth criterion G) and schematic D-20261124-172838-3a30e48. Open: the M/4 member of the null test (FE4, card) and the G2 verifier (C17).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Mesh: null test at M/8 and M/16 (D-20261121-203124-a34cf1f, -203131-8ee2a49, -203151-37e7b2d, -203151-59c54fb; converged-finder difference 4.5-7.3e-5 at M/8, 2.3-3.7e-5 at M/16, fp_analyse D-20261124-172508-c847ee4), M/4 FE4 queued (job 5153); growth at M/8 (ES-FL), M/4 FF4 at 456 M (job 5152), M/16 FL16 registered held (D-20261124-172745-72472ed). The horizon mass itself has no mesh order (P2, FP4 refuted). Particle number: N = FK (held, 225 M of 400), 4N = FN4 and N/4 = FNQ registered, held (D-20261124-134157-b17938b, -172725-2f426b6). Boundary: faces +-192/384/768 M, gauge: lapse_leak pair of G1 (boundary_gauge D-20261124-131657-89cd963).
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: Volume norms bounded in all long runs (D-20261123-021027-e3af9b8); exterior plane norms on annuli outside 1.2 r_AH bounded to 500 M in eight runs (XC1, xc_plane D-20261124-134211-c6fce88, looked at); with dust the exterior residual is ~100x the vacuum one and falls with more particles per cell. Region (sphere) norms come with FN4/FNQ/FL16 (predictions XN, XQ, L5).
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
  - evidence: Criterion N of g2long entry 1 (fixed before the runs): max |D_ES1L - D_V1L| on 100-500 M = 2.28e-4 against 2.51e-4 = 2 F_V(500) (judge_long D-20261123-020550-f9a3482); M/16 1.99e-4 on 100-300 M (H3, D-20261124-131138-0b8ffc5). Since batch 11b the floor's cause is found: the production finder's stopping rule (FP2, FP3: converged-finder vacuum drift 1.8e-5 at M/8 over 100-500 M, 3.9e-6 at M/16); with the converged finder the bubble-minus-vacuum difference is at most 7.3e-5 (M/8, 100-500 M) and 5.5e-5 (M/16, 100-300 M), without a trend in time; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (FP5, FP-ext, FE; D-20261124-172508-c847ee4, D-20261124-175356-0f40f1a; fp_analyse.png and fe_analyse.png looked at). Reservation: the M/4 member is pending.
- [x] **C8** With matter filled in, the mass growth agrees with the integrated particle flux through the horizon
  - status: PASS
  - evidence: Criterion G of g2long entry 1: (iii) every 10 M bin of tau_rem <= 650 M within +-0.62 per cent of the exact LTB mass (61 bins), D2 at all 960 samples (esf_criteria D-20261123-020614-7ba5874, esf_criteria.png L; esf_bracket.png L). Reservations: one mesh and one particle number so far (FF4, FL16, FK, FN4, FNQ queued); D1 closure +9.4e-3 at 500 M (predicted below 8e-3); the step at tau_rem ~ 285 M follows the end of horizon excision at 219 M (FK tests the workaround).

## Minimum figures at G2 (brief 13.4)

- [x] **C9** Schematic: Verification ladder
  - status: PASS
  - evidence: Verification-ladder schematic schem_ladder.png, registered D-20261124-172838-3a30e48 (paperfig style, g2long/tools/schem_ladder.py), looked at by the lead on 2026-11-24 09:28 PST; it will be redrawn as the queued runs end.
- [ ] **C10** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Mesh: judge_conv.png (D-20261124-131149-9f0166d, three vacuum meshes) and fp_analyse.png panel (d) (converged finder, three meshes); boundary/gauge: boundary_gauge.png (D-20261124-131657-89cd963). Particle-number figure waits for FK, FN4, FNQ.
- [ ] **C11** Data figure: Constraint norms against time
  - status: OPEN
  - evidence: constraints_long.png (volume norms, D-20261123-021027-e3af9b8) and xc_plane.png (exterior annuli, D-20261124-134211-c6fce88), both looked at; region-sphere norms against time wait for FN4/FNQ/FL16.
- [x] **C12** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: Slice mosaic with zoom boxes D-20261124-134644-2389227 (g2long/tools/slice_mosaic.py), looked at by the lead of batch 11.

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
  - evidence: Failed predictions on record in g2long/JOURNAL.md: entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2), entry 11 (P2), entry 12 (XC2 expected factor), entry 14 (FP4 refuted, FP-ext (ii) missed its bound); QR3/QR4 in secondary_infall/JOURNAL.md; cut chains closed as failed and resumed (entry 10).
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of this session.
