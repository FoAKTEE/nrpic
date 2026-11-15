# Checklist: core G2

Collected by `harness/bin/nrpic-stage collect core G2` on 2026-11-15T14:56:21Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: FAIL
  - evidence: Rows 1 (geodesics) and 2 (dust collapse) PASS on the merged source 609a875 (runs core-20261115-065452-3629622, -065901-3629622); rows 3 (prolate/oblate) and 4 (cluster threshold) PARTIAL (verify/LADDER.md; OPEN.md items 2-3). New capabilities each pass their own tests (EVIDENCE.md).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: FAIL
  - evidence: Shown piecewise only: dust collapse in particle number at fixed mesh (LADDER.md row 2), expanding ball in mesh (JOURNAL-id.md), Newtonian collapse in mesh (JOURNAL-newton.md); no single three-way study (OPEN.md item 4).
- [x] **C3** Constraints behave
  - status: PASS
  - evidence: Dust collapse ||H|| equal to the earlier run (core-20261115-065901-3629622); homogeneous universe H-norm2 3.7e-10, |Theta| 1.1e-11 (core-20261115-065903-3629622); format-2 data: vacuum momentum residual sixth order (JOURNAL-id.md test 1); Bowen-York residual sixth order (JOURNAL-mp.md test 1a); scalar plane perturbation orders 5.2-6.0 (JOURNAL-scalar.md test 3). Sharp surfaces leave a non-converging constraint sheet (OPEN.md item 7).
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Self-gravitating dust collapse with Z4c on the merged card executable, horizon mass to 6.3e-4 (core-20261115-065901-3629622); cluster with collisions at Kn = 30 and 3 (core-20261115-140316-8742cdf, -142625-67f8c1d).

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report
  - status: FAIL
  - evidence: No REPORT.md: the write of tracks/core/stage/G2/REPORT.md was refused by this session's write guard for subagents; its content is in EVIDENCE.md, OPEN.md, this checklist, STAGE_REPORT.md (nrpic-stage report) and JOURNAL.md (lead entry of 2026-11-15T14:53Z).
- [ ] **C6** Reproducibility package
  - status: FAIL
  - evidence: Manifests of every run committed (tracks/core/runs/), scripts in tracks/core/verify/regress/ and tracks/core/analysis/; nrpic-stage verify (clean-export rerun) not run.

## Track-specific criteria of core for G2 (9.3 core: the shared NRPIC implementation (critical path))

- [ ] **C7** All of C3 passed, core-v0.1 released
  - status: FAIL
  - evidence: C3 rows 3 and 4 PARTIAL; core-v0.1 not tagged yet (proposal verify/RELEASE.md; core-v0.3 proposal CHANGELOG.md).

## Minimum figures at G2 (brief 13.4)

- [ ] **C8** Schematic: Verification ladder
  - status: FAIL
  - evidence: No schematic of the ladder yet.
- [ ] **C9** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: FAIL
  - evidence: Convergence figures exist per package (analysis/mp/figs/static_convergence.png, analysis/id/figs/t1_exterior.png, notes/scalar_figs/fig_wave_convergence.png, analysis/newton/field_point.png), not the three of 13.4 for the coupled module.
- [x] **C10** Data figure: Constraint norms against time
  - status: PASS
  - evidence: verify/figs/regress_os_core-20261115-065901-3629622.png (||H|| against t), verify/figs/regress_flrw_core-20261115-065903-3629622.png, analysis/id/figs/t2_constraints.png, notes/scalar_figs/fig_flrw_conformal.png.
- [ ] **C11** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: FAIL
  - evidence: No slice mosaic with zoom boxes in this package.

## Package (brief 13.3; judged by the session)

- [x] **C12** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: Figures of this wave use python/nrpic/figstyle.py (zoom style) and were drawn from registered runs; the ones the lead relied on were opened (EVIDENCE.md, column "looked at"); interfaces/figs/d1_*.png were not opened by the lead.
- [ ] **C13** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: FAIL
  - evidence: No track architecture schematic or gate timeline.
- [ ] **C14** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: FAIL
  - evidence: No working note under tracks/core/note/.
- [ ] **C15** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: FAIL
  - evidence: No VERIFIER_REPORT.md; the lead rechecked the packages from their artefacts (JOURNAL.md), which is not a fresh-context verifier.
- [x] **C16** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs and refuted predictions are in the journals (JOURNAL.md P5 first criterion; JOURNAL-id.md, -coll.md, -mp.md, -newton.md, -rng.md, -scalar.md) and their manifests are committed.
- [x] **C17** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of this session.
