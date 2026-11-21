# Checklist: E-stoch-inf G2

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G2` on 2026-11-21T20:31:07Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: SR (G1) and USR scouting pass their rows (ladder/, usr/); the release card build core-v0.6 is now being run on both (g2prod: P256v6 E-20261121-202935-31520bc, USR chains); judged when they have run.
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: no particles before the hand-over (NA for particle number); mesh: U-R (256 vs 320 at fixed modes, SCOPE 4c), queued in g2prod; gauge: geodesic slicing only (RISKS R6) - to be stated at the package.
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: U-A4'(a) halving with the floor of SCOPE 4c at 256^3 (U256hp/hm queued), U-A4'(c) records on every release run, U-A4'(d) control (U256nc queued); scouting: group 1 even factors 3.987-4.001 (E-20261121-080134-a0cc3eb).
- [ ] **C4** A first minimal full-GR kinetic run
  - status: OPEN
  - evidence: Track E has no kinetic matter before the field-to-particle hand-over (S11 subsequent work); proposed NA at G2 [JUDGEMENT], for orch to confirm.

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: 
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: 

## Track-specific criteria of E-stoch-inf for G2 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C7** The USR case is reproduced
  - status: OPEN
  - evidence: criteria fixed in spec/scope/SCOPE.md 4c (commit 43dcc9cc) before production; release runs queued (g2prod/JOURNAL.md entry 1); scouting pair U256/U256m passes U-A2' at 1.09e-4 (E-20261121-101756-6bffd0c).
- [ ] **C8** Sensitivity to window-function parameters and resolution
  - status: OPEN
  - evidence: window: U-W met by the scan (E-20261121-154733-0d1fbda; lead's rerun E-20261121-203008-f104a3e, stage/REVIEW-wave3.md Part C); resolution: U-R pending (U320ap/am in g2prod).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [ ] **C9** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: G0 decision: continue (coord/GATES.md 2026-11-20); G1 signed 2026-11-21; G2 within the scope of SCOPE section 4 and 4c.

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: 
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: 
- [ ] **C12** Data figure: Constraint norms against time
  - status: OPEN
  - evidence: 
- [ ] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: 

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: 
- [ ] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: 
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: 
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: 
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: 
- [ ] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: 
- [ ] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: 
