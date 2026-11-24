# Checklist: E-stoch-inf G2

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G2` on 2026-11-24T23:36:39Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [x] **C1** The code paths used by the track pass their tests of §10
  - status: PASS
  - evidence: Release card build core-v0.6: SR P256v6 (E-20261121-202935-31520bc) records identical to the tested-branch G1 run, A2 1.2078e-4 (analysis E-20261123-015014-b4ecd4e); USR seed A identical per mode to the scouting pair, U-A0..U-A3 and U-A2' pass on all eight release USR runs (E-20261123-014858-8e72d4c, -021730-a421438, -020751-0baf597; judge E-20261123-024359-5dc3213). g2prod/JOURNAL.md entry 2.
- [x] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: PASS
  - evidence: Ruling 0030 item 2: a gauge variant is not required of Track E at G2 (the reproduced paper runs geodesic slicing only); C2 stands on mesh convergence in the periodic box, another gauge is a G3 item. Mesh: U-R 256 vs 320 PASS (factor 2.10 on the odd-part maximum, shell power 1.2e-4; fig_g2_resolution.png of E-20261123-024359-5dc3213); SR spectral convergence 32-256 (repro/figs Fig. 7, pass E-20261124-213029-e937f69; floor at the lowest shells, test FL128h/FL256h queued q0037/q0038, floor/JOURNAL.md entry 1). Particle number: NA (no particles before the hand-over).
- [ ] **C3** Constraints behave
  - status: FAIL
  - evidence: U-A4'(a) as written: H within 4.00 +- 0.05 at all 9 judged dumps; M outside at one of 11 (3.925 at cN 6.52) - FAIL, on record without rewording (ruling 0030 item 2). U-A4'(c) PASS on the nine proper runs (H' <= 3.0e-12, M <= 0.025); U-A4'(d) control ratio 1.19e5 PASS (E-20261123-024359-5dc3213). Third amplitude s = +-1/4 ran (U256qp E-20261123-230004-861aea7, U256qm E-20261123-230507-a6246b1); its reading against Q-a..Q-c (g2prod entry 3): analysis E-20261124-233223-51b52c0 (see g2prod/JOURNAL.md entry 4).
- [x] **C4** A first minimal full-GR kinetic run
  - status: NA
  - evidence: Decision 0026 item 3: does not apply to Track E before the hand-over from field to particles.

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md present. Verification of the reproduction: repro/verify/VERIFIER.md (fresh verifier, two passes). Missing for G2: a verifier of the g2prod SCOPE 4c numbers (C18) and the reading of the quarter pair.
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Every run registered with manifests and checksums; decks, queues, scripts committed (g2prod/, repro/*); restart byte-exact (R0); continued runs join their originals bit for bit (repro/continue entries 12-13, E-20261124-212343-7e9c4b2, E-20261124-225720-444aecc). Rerun recipes: repro/figs/README.md, repro/verify/README.md, HANDOFF (analyse_g2.py commands); g2prod/README.md (22 lines) still lacks the analysis commands of entry 2.

## Track-specific criteria of E-stoch-inf for G2 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C7** The USR case is reproduced
  - status: FAIL
  - evidence: SCOPE 4c definition: U-A0, U-A1, U-A2', U-A3 for seeds A and B, U-R, U-W, U-A4'(c), U-S, U-A4'(d) PASS; U-A4'(a) FAILS at one dump of M (3.925, bar 3.95-4.05), kept on record by ruling 0030 item 2 (no rewording; the package goes to independent review after the quarter pair is read). The reproduction of arXiv:2512.14649 (repro/note, Table IV) reproduces the USR figures in part: spectra agree, one-point widths 3.5-4 times narrower than the published ones (cause open).
- [x] **C8** Sensitivity to window-function parameters and resolution
  - status: PASS
  - evidence: Window: U-W met by the scan (E-20261121-154733-0d1fbda, rerun E-20261121-203008-f104a3e). Resolution: U-R PASS (E-20261123-020751-0baf597 with E-20261123-014858-8e72d4c, judge E-20261123-024359-5dc3213).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [x] **C9** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: G0 decision: continue (coord/GATES.md 2026-11-20); G1 signed 2026-11-21; G2 within the scope of SCOPE section 4 and 4c.

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: Not drawn yet.
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Mesh: note figure fig_specconv (repro/note/manuscript, script under repro/note/manuscript/scripts; SR spectral convergence 32-256) and the analysis figure fig_g2_resolution.png (USR 256 vs 320, E-20261123-024359-5dc3213); particle number NA; gauge NA by ruling 0030. Not yet a figure of the USR resolution pair in a note.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: Note figure fig_constraints (repro/note/manuscript: constraint records against e-folds, both scenarios, rungs 32-256, from registered runs; ledger with verifier verdicts) and fig_g2_records.png (every release USR run, E-20261123-024359-5dc3213).
- [ ] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: Not drawn yet.

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: CHECKLIST, EVIDENCE, OPEN, STAGE_REPORT present; scoping text spec/scope/SCOPE.md (section 4c for G2); REVIEW: stage/REVIEW-wave3.md Part D (analysis record; no helper package).
- [ ] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: Analysis figures from registered outputs, all looked at (g2prod entry 2); note figures with one script each pending.
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: G1 schematics exist (note/); G2 update not drawn.
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: Working note of the reproduction: repro/note/manuscript/main.pdf (26 pages, REVTeX, /paper-writing, guide and notation one level above; checker with the forbid list run, accepted hits only: repro/note/JOURNAL.md). It carries the SR/USR reproduction, not the SCOPE 4c judgement of g2prod (U-A* criteria, halving, quarter pair): those G2 sections are not written.
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: repro/verify/VERIFIER.md: fresh verifier of the reproduction (two passes, 133 ledger rows with verdicts; repro/note README). No fresh verifier of the g2prod SCOPE 4c numbers (U-A0..U-A4', U-R, U-S) yet.
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and failed runs on record: g2prod entry 2 (T memory band, U320 band, U-A2' at s = 1/2, U-A4'(a) halving of M; failed analysis E-20261123-015650-493cff5; invalid pass E-20261123-014905-2bf3570).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md rewritten by the lead of batch 13 (2026-11-24).
