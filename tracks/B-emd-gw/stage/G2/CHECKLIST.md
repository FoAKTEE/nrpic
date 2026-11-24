# Checklist: B-emd-gw G2

Collected by `harness/bin/nrpic-stage collect B-emd-gw G2` on 2026-11-24T13:37:48Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: FLRW dust and linear growth rows pass (flrw_conv entries 7-12; J4 B-20261123-015905-7a30278 with analysis B-20261124-125457-79ce723 confirms the amplitude floor at 128 cells is the start step); GW diagnostics on analytic waves passed at G1 (signed). Shearing dust: S1-S4, M1, L1 judged (B-20261123-015919-dec4392), P10 holds (f = 1 against f = 1/3: -8.7e-5, B-20261124-131336-bc61eee); L2: with narrow fans (series 3, B-20261124-134209-4584052; summary B-20261124-134720-c753aff) Delta = -0.828, -0.830, -0.835 at N_y = 32-128, near CosmoGRaPH (-0.8183) and far from gevolution and GRAMSES, not converging; S3 has a floor of 2-3e-5 (N_y = 256). Population in full GR: sigma1 = 0.014 to a = 143 (B-20261123-014847-f295ab4) matches the Newtonian population at equal stage and the design's near field for 6 <= a <= 20 (analysis B-20261124-131918-e71996f, figures B-20261124-133150-e9ef701); sigma1 = 0.028 stops at a = 30.7 in the densest core (B-20261123-035002-bcc82bd; restarts X0-X3 queued, B-20261124-133533-cb0bb7d). Open: a converged L2 number, the 0.028 stop.
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Mesh 16-128 and particle number 1-27 per cell: flrw_conv (fig_b_conv, fig_f_scaling); step at 32 cells (P3/P4, B-20261121-220450-e011c57, -222813-560158b) and at 128 cells (J4, figs/fig_step128.png). Gauge: one slicing point at one mesh (shear S1 at N_y = 64, f = 1 against f = 1/3: -8.7e-5 relative, inside the 1e-4 bar; B-20261124-131336-bc61eee); the f = 1 run stops at t = 0.578, after the rays arrive. No convergent gauge leg; population has no mesh or particle-number leg yet.
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: flrw_conv: largest Hr 3e-9 to 6e-8, mean-density error <= 4e-9 to a = 1000, Hr grows about as N^2 (cause untested). shear: t = 0 momentum constraint fourth order; means below 1e-4 to ray arrival but rising with N_y at HL = 1/16, 1/128. Population (sigma1 = 0.014): Hr_mean 1.6e-4 at a = 29 and 2.85e-2 at a = 141, Mr_mean 0.20 at a = 141, both growing monotonically after the halos form (figs/pop_gr_constraints.png; B-20261124-131918-e71996f). Not shown to behave at late times or fine meshes.
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Full-GR kinetic runs with particles coupled to Z4c in the periodic box: flrw_conv J3 B-20261121-202335-3e6a898 (128^3 to a = 1000), shear series B-20261121-202830-417af0c, the population box pop_s014_gr B-20261123-014847-f295ab4 (128^3, L = 8, 2.1e6 particles, to a = 143, 0.19 card-h).

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
  - evidence: Shearing dust (arXiv:2003.08014): S1-S4, M1, L1 judged (S within 1e-5 of linear, M1 and L1 inside the paper's bounds, M2 sign against the prediction); P10 holds; L2, the case that separates the codes: Delta = -0.828, -0.830, -0.835 at N_y = 32, 64, 128 (series 3, B-20261124-134209-4584052, figure shear/figs/fig_series2.png), 0.010-0.017 below CosmoGRaPH's -0.8183 and 0.15-0.2 below gevolution (-0.619) and GRAMSES (-0.68), but not converging in N_y (shear journal 2026-11-24 06:50). Full GR against the Newtonian mode: the GR box at sigma1 = 0.014 has the halo counts and masses of the Newtonian fidL8 box at equal stage (H1: counts inside 2 sqrt(N) + 2 at a = 49-121, largest mass within -7 to +13 per cent, the five largest matched within 0.07) and the design's near-field strain to 9-13 per cent for 6 <= a <= 20 (A1), population/JOURNAL.md 2026-11-24 05:58. The same-particle Newtonian reference at 128^3 is queued (B-20261124-131438-5d7e049, predictions N1-N4).

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic yet.
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Mesh and particle number: flrw_conv/figs/fig_b_conv.png, fig_f_scaling.png; step: flrw_conv/figs/fig_step128.png; gauge: a single slicing point (shear rays.png of B-20261124-131336-bc61eee); no gauge convergence figure.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: flrw_conv/figs/fig_b_constraints.png (largest Hr against a, 16-128 cells), fig_f_constraints.png; shear/figs/fig_series.png (means up to arrival).
- [x] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: population/figs/pop_gr_mosaic.png (run B-20261124-133709-85c4be7): the GR box at a = 132, particle density over the box with zooms L/4 and L/16 around the largest halo (zoom boxes drawn), and the lapse, K and flat TT strain on the same plane; looked at. Defect: the colour range of the K panel saturates in the halo core.

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
  - evidence: Failed predictions and runs on record: flrw_conv entries 7, 9-12 (PB3 floor, J3 quarter rule, P2, P3); shear journal (P4 Hamiltonian order, P7 S3, P8 M2 sign, P12; L2 cause found 2026-11-24); population journal 2026-11-22 (0.028 data above tolerance) and 2026-11-24 (G1 cost below the range; G1 for 0.028: guard stop at a = 30.7, run B-20261123-035002-bcc82bd closed as failed; A1 fails from a = 36; A2 in part; A3 for the strain rms); failed analysis runs B-20261124-130512-d39dae4 and -131918-e71996f (figure step) on record.
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: Rewritten at the end of batch 11 (2026-11-24).
