# Checklist: E-stoch-inf G2

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G2` on 2026-11-23T02:32:53Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [x] **C1** The code paths used by the track pass their tests of §10
  - status: PASS
  - evidence: Release card build core-v0.6: SR P256v6 (E-20261121-202935-31520bc) records identical to the tested-branch G1 run, A2 1.2078e-4 (analysis E-20261123-015014-b4ecd4e); USR seed A identical per mode to the scouting pair, U-A0..U-A3 and U-A2' pass on all eight release USR runs (E-20261123-014858-8e72d4c, -021730-a421438, -020751-0baf597; judge E-20261123-024359-5dc3213). g2prod/JOURNAL.md entry 2.
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Particle number: NA (no particles before the hand-over). Mesh: U-R 256 vs 320 PASS (factor 2.10 on the odd-part maximum, shell power 1.2e-4, even/odd 1e-4; fig_g2_resolution.png of E-20261123-024359-5dc3213); the k <= 32 maximum sits on an s^2 common-mode part (entry 2.3). Gauge or boundary: periodic box (no boundary); geodesic slicing only, no gauge variant run - asked of orch (outbox 2026-11-23).
- [ ] **C3** Constraints behave
  - status: FAIL
  - evidence: U-A4'(a) as written: H within 4.00 +- 0.05 at all 9 judged dumps; M outside at one of 11 (3.925 at cN 6.52) - FAIL. U-A4'(c) PASS on the nine proper runs (H' <= 3.0e-12, M <= 0.025); U-A4'(d) control ratio 1.19e5 PASS (fig_g2_halving, fig_g2_records, fig_g2_control of E-20261123-024359-5dc3213). Third amplitude s = +-1/4 queued with predictions (g2prod entry 3).
- [x] **C4** A first minimal full-GR kinetic run
  - status: NA
  - evidence: Decision 0026 item 3: does not apply to Track E before the hand-over from field to particles.

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md present; the verification report needs the verifier (C18) and the note sections (C17).
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Every run registered with manifests and checksums; deck, queue, scripts committed (g2prod/); restart byte-exact (R0). A rerun recipe for a third party (README of g2prod with the analysis commands) not yet written.

## Track-specific criteria of E-stoch-inf for G2 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C7** The USR case is reproduced
  - status: FAIL
  - evidence: SCOPE 4c definition: U-A0, U-A1, U-A2', U-A3 for seeds A and B, U-R, U-W, U-A4'(c), U-S, U-A4'(d) PASS; U-A4'(a) FAILS at one dump of M (3.925, bar 3.95-4.05). As written the USR case is not reproduced in full; gate decision asked of orch. g2prod/JOURNAL.md 2.3.
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
  - evidence: Mesh: fig_g2_resolution.png (run E-20261123-024359-5dc3213) exists as an analysis figure; not yet a note figure with its own script under note/scripts; particle number NA; gauge none.
- [ ] **C12** Data figure: Constraint norms against time
  - status: OPEN
  - evidence: fig_g2_records.png (constraint records of every release run against time, E-20261123-024359-5dc3213) exists as an analysis figure; note figure pending.
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
  - evidence: G2 sections of the working note not written (this session wrote no note text, by its task).
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet; first next action (HANDOFF).
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and failed runs on record: g2prod entry 2 (T memory band, U320 band, U-A2' at s = 1/2, U-A4'(a) halving of M; failed analysis E-20261123-015650-493cff5; invalid pass E-20261123-014905-2bf3570).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md rewritten by the lead of batch 10a (2026-11-22).
