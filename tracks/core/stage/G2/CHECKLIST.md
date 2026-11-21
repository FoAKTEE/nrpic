# Checklist: core G2

Collected by `harness/bin/nrpic-stage collect core G2` on 2026-11-21T15:50:49Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: FAIL
  - evidence: State 2026-11-21 after core-v0.6 (OPEN.md, first section). Row 1 geodesics PASS (regression G core-20261115-065452-3629622, 104/104) and row 2 Oppenheimer-Snyder PASS (regression O core-20261115-065901-3629622, 13/13; M_AH/M - 1 = 3.5e-4 at formation, largest 1.3e-3 to 60 M) on the merged source of wave 1; every later release passes the byte regression of the twelve wave-1 set-ups against its predecessor (core-v0.4 core-20261120-221607-4985804, core-v0.5 core-20261121-063859-e410ee3, core-v0.6 core-20261121-130202-7cf7db8), among them the geodesic set-ups (geo, boris) and a short refined Oppenheimer-Snyder run (os, 3 steps) with identical data files (core-v0.4: differences only in unset restart-header bytes and parameter-dump lines, classes a and b), so rows 1 and 2 carry over to core-v0.6 [JUDGEMENT: the full ladder runs were not repeated on v0.4-v0.6]. Row 3 PARTIAL: prolate at M/16 and M/8 (card core-20261115-152845-5728b1d, comparison -162509-c691fb8): horizon 32.00/32.25 M as the paper's 32 M, largest M_AH 0.967/0.957; oblate has no released component (branch core/oblate, unmerged). Row 4 PARTIAL: fates of the five models as the paper; bisection at M/4 (cards -152842/-152843-5728b1d, -154726-37450f2, control -155617-06f844b; analyses -160501-ee15e0f, -170606-1c69507) gave no bracket by the rule fixed before the runs; Track C's M/8 controls (C-20261121-140057-92742cf) show that the M/4 mesh pushes clusters outward, so the bisection must be redone on M/8. verify/LADDER.md rows 3-4. New capabilities of v0.4-v0.6 pass their own tests (interface documents; RELEASE-v0.4/5/6.md).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: FAIL
  - evidence: verify/figs/convergence_three_way.png (run core-20261115-154736-f9f5edb; looked at 2026-11-21): ||H|| of the cluster y_c = 0.819 falls as N^-1/2 (10^2 to 10^4), the expanding ball converges at second order in dx (M to M/4), every gauge converges and the boundary effect at 24 M goes when the boundary moves to 48 M. Each direction is on a different set-up; no single coupled set-up is converged in all three, and the cluster's fate is not converged in the mesh (Track C drift, OPEN.md first section item 2). Package-level convergence since: faces (z4c_faces.md), solver (id_solver2.md: W at the faces against cell size), Newtonian mode (newtonian_mode.md section 7).
- [x] **C3** Constraints behave
  - status: PASS
  - evidence: Dust collapse ||H|| equal to the earlier run (core-20261115-065901-3629622); homogeneous universe: history columns H-norm2 3.7e-10 and Theta-norm2 1.1e-11 (core-20261115-065903-3629622), both volume integrals of the squared constraint, sum over cells of sqrt(gamma) dV H^2 and sqrt(gamma) dV Theta^2 (`athenak/src/outputs/history.cpp` lines 186, 229; the file header truncates the second label to `Theta-norm`); pointwise max|Theta| 2.27e-7 and max|H| 1.69e-6 (fresh verifier, run core-20261121-212248-a7972d1; label corrected after VERIFIER.md section 3 item 1); format-2 and Bowen-York residuals at sixth order (JOURNAL-id.md test 1, JOURNAL-mp.md test 1a); solved initial data: monitor 1e-11 to 1e-9 on every level at t = 0 (id_solver2.md test C), Bowen-York puncture max|H| 6.4e-12 after the solve on the merged card and processor executables (job 4800, core-20261121-154700-2de4974). Limits: sharp surfaces leave a non-converging constraint sheet (OPEN.md 2026-11-15 item 7); whole-mesh norms with stock outflow faces are set by the ghost cells (OPEN.md core-v0.6 item e).
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Self-gravitating dust collapse with Z4c on the merged card executable, horizon mass to 6.3e-4 (core-20261115-065901-3629622); cluster with collisions at Kn = 30 and 3 (core-20261115-140316-8742cdf, -142625-67f8c1d); prolate collapse and seven cluster runs of wave 2 on release core-v0.3 (C1).

## Main products of G2 (charter 9.2)

- [x] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: PASS
  - evidence: Verification report = this package (decision 0012): STAGE_REPORT.md (nrpic-stage report, 2026-11-21), EVIDENCE.md (run ids per release and per ladder row), OPEN.md (first section: whether G2 is met and what is missing; defects by release), with verify/LADDER.md (the ladder, row by row) and RELEASE-v0.4/5/6.md (regressions and card checks).
- [ ] **C6** Reproducibility package
  - status: FAIL
  - evidence: Manifests of every run committed (tracks/core/runs/, 1405 read by verify), drivers in tracks/core/analysis/release/, verify/ladder2/, verify/figscripts/; release records with the commands to repeat every check (RELEASE-v0.6.md). nrpic-stage verify of 2026-11-21 on the clean export of the tip (VERIFY_RESULTS.md; first on 9776100b, again after closing the stranded run): FAIL on two checks. (i) note: no tracks/core/note/main.tex. (ii) runs: 10 of 1405 runs have problems (11 in the first verify): 9 runs of 2026-11-20/21 name the executables of scratch/core/exe/core_cosmo-amr/, which were published again after the runs (sha256 differs; the outputs are not affected, the record of the input is), and 2 runs not closed: core-20261119-143517-ec2f4fc (gauge test E2, job 4641, both cases rc 0; closed with nrpic-run finish after the verify) and core-20261121-154654-d3ec487 (job 4810, pending). Output checksums were not re-verified in this run (--no-checksums): the full verify read run outputs for 13 minutes and was stopped by its process id at the runs of 2026-11-19 (log scratch/core/tmp/lead_b4a/verify.log). The ladder figures are not registered as fig_*.py scripts under note/scripts/, so verify regenerates no figure (min-figs WARN).

## Track-specific criteria of core for G2 (9.3 core: the shared NRPIC implementation (critical path))

- [ ] **C7** All of C3 passed, core-v0.1 released
  - status: FAIL
  - evidence: core-v0.1 (7daed19) and core-v0.2 to core-v0.6 are tagged (CHANGELOG.md, CLAUDE.md); C3 of the core sheet is not all passed: rows 3 and 4 PARTIAL (C1; OPEN.md first section items 1, 2).

## Minimum figures at G2 (brief 13.4)

- [x] **C8** Schematic: Verification ladder
  - status: PASS
  - evidence: verify/figs/schem_ladder.png (script verify/figscripts/schem_ladder.py with ladder_status.json; run core-20261115-162615-ca0fd2b), looked at 2026-11-21: rows 1-2 PASS, 3-4 PARTIAL, oblate open, as today. Its state line says 2026-11-15; no verdict has changed since.
- [x] **C9** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: PASS
  - evidence: verify/figs/convergence_three_way.png (script verify/figscripts/convergence3.py, run core-20261115-154736-f9f5edb), three panels: particle number, mesh, gauge and boundary; looked at 2026-11-21. The figure exists; what it does not show is criterion C2's.
- [x] **C10** Data figure: Constraint norms against time
  - status: PASS
  - evidence: verify/figs/regress_os_core-20261115-065901-3629622.png (||H|| against t), verify/figs/regress_flrw_core-20261115-065903-3629622.png, analysis/id/figs/t2_constraints.png, notes/scalar_figs/fig_flrw_conformal.png.
- [x] **C11** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: verify/figs/prolate_mosaic.png (run core-20261115-162509-c691fb8): energy density at y = 0, t = 27.75 M, four nested windows +-10, 4, 1.5, 0.6 M with zoom boxes, at M/16 and M/8; looked at 2026-11-21.

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C12** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: FAIL
  - evidence: STAGE_REPORT.md, EVIDENCE.md, OPEN.md and this CHECKLIST.md are in tracks/core/stage/G2/. No REVIEW.md: the lead's reviews of the helper branches are in RELEASE-v0.4.md, RELEASE-v0.5.md, RELEASE-v0.6.md and the merge commit messages. No SCOPE.md or SCOPING.md: core's scope is its sheet in the brief (9.3) and the charter's 'What differs from the brief' item 1.
- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: Figures use python/nrpic/figstyle.py and are drawn from registered runs: release figures fig_regress_v04, fig_quick_v06, fig_card_v06 (core-20261121-154700-2de4974), fig_card_v05 (core-20261121-154710-220c1b0), ladder figures of verify/figs/; every one named in EVIDENCE.md was looked at (column 'looked at' there and in RELEASE-v0.x.md). Exceptions on record: interfaces/figs/d1_*.png were not opened by the lead.
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: FAIL
  - evidence: verify/figs/schem_architecture.png (script verify/figscripts/schem_architecture.py, paperfig.py; run core-20261115-154738-f9f5edb) has the architecture and the gate timeline, but its state is 2026-11-15: it shows the lapse relaxation, the mass-scaled shift damping, the initial slice at N*, the elliptic solver and the oblate data as 'to be built', and stops at core-v0.3; looked at 2026-11-21. To be redrawn for core-v0.6.
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: FAIL
  - evidence: No working note under tracks/core/note/.
- [x] **C16** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G2/VERIFIER.md (commit ba01d3f6) by the fresh-context helper verify/verifier_g2 (batch 6), predictions committed before any check (41766638), verdicts committed before it read core's conclusions (2a4336b5, 805da131, 7fff69fc, 5e40e8b9); own readers and references, no import of python/nrpic or core's analysis code; registered runs core-20261121-212008-6986d13, -212106-131e909, -212244-3f782d9, -212248-a7972d1, -212422-b616c6e, -212516-0f0a65b, -212611-5973536, -213713-952a0c4, -213807-4cc035d, -213946-cee79fa, -214108-0960a46, -214230-ad24f6b, -214547-7a21ed3, -215228-d1f36f4, one figure each. Fourteen claims: every met ladder row (1, 2, the met part of 4, C3, C4) and at least one claim of each release core-v0.3 to v0.6; twelve confirmed to their printed digits; one general statement wrong (restarts exact only for periodic set-ups and the particle state: OPEN.md, state after batch 8, item u); five text defects (section 3), each corrected in batch 8 (C3 above; interfaces/scalar_field.md test 1; interfaces/newtonian_mode.md 5.2; interfaces/id_solver.md T1; verify/LADDER.md row 2). Limit, as the verifier states: a sample of claims, not 'every number'; the working note's ledger (note/tables/ledger.tex, batch 8) was written after the report, and its rows say which numbers the verifier recomputed (column 'verifier') and which no second agent has checked.
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs and refuted predictions are in the journals (JOURNAL.md: P5 first criterion of 2026-11-15, the driver faults of the v0.4-v0.6 releases, the faults listed per session; JOURNAL-*.md of every package; verify/JOURNAL.md: prediction '0.64 collapses' refuted) and their manifests are committed; the list of STAGE_REPORT.md.
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of session core-lead-6 (2026-11-21, batch 4a).
