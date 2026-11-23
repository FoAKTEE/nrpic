# Checklist: B-emd-gw G2

Collected by `harness/bin/nrpic-stage collect B-emd-gw G2` on 2026-11-23T02:00:36Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: FLRW dust and linear growth rows of section 10 pass (flrw_conv, entry 12: runs B-20261120-222955-c8e16e3, -223006-24448ac, B-20261121-202304-dc3020e, -202335-3e6a898, analyses B-20261121-220428-7367d5e, B-20261123-015452-18d2956); GW diagnostics on analytic waves passed at G1 (signed). Open: the shearing-dust row (L2 without result, shear journal 2026-11-22 18:00) and the population box in full GR (queued).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Mesh 16-128 and particle number 1-27 per cell: flrw_conv (fig_b_conv, fig_f_scaling); step: P3/P4 (B-20261121-220450-e011c57, -222813-560158b). Gauge leg missing: the f = 1 lapse leg of the shear series stopped at the guard (B-20261121-202830-417af0c, S1_n64_lap1).
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: flrw_conv: largest Hr 3e-9 to 6e-8, mean-density error <= 4e-9 to a = 1000, but Hr grows with N (entry 12). shear: t = 0 momentum constraint fourth order; up to ray arrival below 1e-4 but rising with N_y at HL = 1/16, 1/128 (B-20261123-015919-dec4392). Cause of the rise not tested.
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Full-GR kinetic runs with particles coupled to Z4c in the periodic box: flrw_conv J3 B-20261121-202335-3e6a898 (128^3 to a = 1000), shear series B-20261121-202830-417af0c; the population box in full GR is queued (B-20261123-014847-f295ab4, Slurm 4921).

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md generated in batch 10a as a progress record; the verification report itself waits for C1-C3, C9.
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Manifests, decks and scripts exist per package (flrw_conv/README.md "How to rerun"); no package-level reproducibility list yet.

## Track-specific criteria of B-emd-gw for G2 (9.5 Track B: gravitational waves from EMD structure formation (S2))

- [x] **C7** The scale-factor error and the linear growth rate of the particle FLRW run reach the sub-percent level and converge in particle number and mesh
  - status: PASS
  - evidence: Met at 16-128 cells: flrw_conv/README.md "Verdict", JOURNAL entries 7, 9-12; runs above; figures fig_b_conv, fig_b_error, fig_f_lattice, fig_f_noise, fig_f_scaling (looked at).
- [x] **C8** Agreement with gevolution in the weak-field regime
  - status: NA
  - evidence: Replaced by C9 (decision 0013: gevolution is not run; the multi-code row is the shearing-dust comparison and full GR against the Newtonian mode).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [ ] **C9** Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013)
  - status: OPEN
  - evidence: Shearing dust (arXiv:2003.08014): S1-S4, M1, L1 judged (shear journal 2026-11-22 18:00; S within 1e-5 of linear, M1 and L1 inside the paper bounds, M2 sign against the prediction); L2, the case that separates the codes, has no number. Full GR against the Newtonian mode: GR population runs queued (pop_s014_gr Slurm 4921; pop_s028_gr behind a re-solve of its data B-20261123-014850-7b7d986).

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic yet.
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Mesh and particle number: flrw_conv/figs/fig_b_conv.png, fig_f_scaling.png; gauge: none.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: flrw_conv/figs/fig_b_constraints.png (largest Hr against a, 16-128 cells), fig_f_constraints.png; shear/figs/fig_series.png (means up to arrival).
- [ ] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: No slice mosaic; planned from the population box snapshots.

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: CHECKLIST, EVIDENCE, OPEN and STAGE_REPORT exist (batch 10a); REVIEW: stage/REVIEW-wave3.md section "Batch 10a".
- [ ] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: Figures from registered runs and looked at (flrw_conv, shear), but analyze_b.py and analyze_f.py draw several figures each; defects noted (legend over the 128 curve in fig_b_error, cut label in fig_series).
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: G2 schematics not drawn.
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: No G2 section in the working note yet.
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet.
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and runs on record: flrw_conv entries 7, 9-12 (PB3 floor, J3 quarter rule, P2, P3), shear journal (P4 Hamiltonian order, P7 S3, P8 M2 sign, P9 L2 and P10 without result, P12), population journal 2026-11-22 (0.028 data above tolerance), shear series manifest closed as failed.
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: Rewritten at the end of batch 10a.
