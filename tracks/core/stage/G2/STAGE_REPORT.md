# Stage report: core G2

Date: 2026-11-21 · branch `core/nrpic` at `26a519c13587` · checklist
`tracks/core/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/core/G2-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 5 checklist items not PASS or NA: C1 FAIL, C2 FAIL, C6 FAIL, C7 FAIL, C12 FAIL
- verify ran on 042f70b; files changed since: CLAUDE.md, coord/BOARD.md, coord/BRIEF_ERRATA.md, coord/DECISIONS/0023-rulings-after-batch-4a.md, coord/DECISIONS/0024-inbox-rulings.md, coord/DECISIONS/0025-rulings-after-batch-4b.md (run verify again)
- verify reported FAIL: note, runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | present |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | present |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | none found (SCOPE.md or SCOPING.md beside the report, or scope/SCOPE.md) |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | State 2026-11-21 after core-v0.6 (OPEN.md, first section). Row 1 geodesics PASS (regression G core-20261115-065452-3629622, 104/104) and row 2 Oppenheimer-Snyder PASS (regression O core-20261115-065901-3629622, 13/13; M_AH/M - 1 = 3.5e-4 at formation, largest 1.3e-3 to 60 M) on the merged source of wave 1; every later release passes the byte regression of the twelve wave-1 set-ups against its predecessor (core-v0.4 core-20261120-221607-4985804, core-v0.5 core-20261121-063859-e410ee3, core-v0.6 core-20261121-130202-7cf7db8), among them the geodesic set-ups (geo, boris) and a short refined Oppenheimer-Snyder run (os, 3 steps) with identical data files (core-v0.4: differences only in unset restart-header bytes and parameter-dump lines, classes a and b), so rows 1 and 2 carry over to core-v0.6 [JUDGEMENT: the full ladder runs were not repeated on v0.4-v0.6]. Row 3 PARTIAL: prolate at M/16 and M/8 (card core-20261115-152845-5728b1d, comparison -162509-c691fb8): horizon 32.00/32.25 M as the paper's 32 M, largest M_AH 0.967/0.957; oblate has no released component (branch core/oblate, unmerged). Row 4 PARTIAL: fates of the five models as the paper; bisection at M/4 (cards -152842/-152843-5728b1d, -154726-37450f2, control -155617-06f844b; analyses -160501-ee15e0f, -170606-1c69507) gave no bracket by the rule fixed before the runs; Track C's M/8 controls (C-20261121-140057-92742cf) show that the M/4 mesh pushes clusters outward, so the bisection must be redone on M/8. verify/LADDER.md rows 3-4. New capabilities of v0.4-v0.6 pass their own tests (interface documents; RELEASE-v0.4/5/6.md). | FAIL |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | verify/figs/convergence_three_way.png (run core-20261115-154736-f9f5edb; looked at 2026-11-21): //H// of the cluster y_c = 0.819 falls as N^-1/2 (10^2 to 10^4), the expanding ball converges at second order in dx (M to M/4), every gauge converges and the boundary effect at 24 M goes when the boundary moves to 48 M. Each direction is on a different set-up; no single coupled set-up is converged in all three, and the cluster's fate is not converged in the mesh (Track C drift, OPEN.md first section item 2). Package-level convergence since: faces (z4c_faces.md), solver (id_solver2.md: W at the faces against cell size), Newtonian mode (newtonian_mode.md section 7). | FAIL |
| C3 | Constraints behave | Dust collapse //H// equal to the earlier run (core-20261115-065901-3629622); homogeneous universe: history columns H-norm2 3.7e-10 and Theta-norm2 1.1e-11 (core-20261115-065903-3629622), both volume integrals of the squared constraint, sum over cells of sqrt(gamma) dV H^2 and sqrt(gamma) dV Theta^2 (`athenak/src/outputs/history.cpp` lines 186, 229; the file header truncates the second label to `Theta-norm`); pointwise max/Theta/ 2.27e-7 and max/H/ 1.69e-6 (fresh verifier, run core-20261121-212248-a7972d1; label corrected after VERIFIER.md section 3 item 1); format-2 and Bowen-York residuals at sixth order (JOURNAL-id.md test 1, JOURNAL-mp.md test 1a); solved initial data: monitor 1e-11 to 1e-9 on every level at t = 0 (id_solver2.md test C), Bowen-York puncture max/H/ 6.4e-12 after the solve on the merged card and processor executables (job 4800, core-20261121-154700-2de4974). Limits: sharp surfaces leave a non-converging constraint sheet (OPEN.md 2026-11-15 item 7); whole-mesh norms with stock outflow faces are set by the ghost cells (OPEN.md core-v0.6 item e). | PASS |
| C4 | A first minimal full-GR kinetic run | Self-gravitating dust collapse with Z4c on the merged card executable, horizon mass to 6.3e-4 (core-20261115-065901-3629622); cluster with collisions at Kn = 30 and 3 (core-20261115-140316-8742cdf, -142625-67f8c1d); prolate collapse and seven cluster runs of wave 2 on release core-v0.3 (C1). | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | Verification report = this package (decision 0012): STAGE_REPORT.md (nrpic-stage report, 2026-11-21), EVIDENCE.md (run ids per release and per ladder row), OPEN.md (first section: whether G2 is met and what is missing; defects by release), with verify/LADDER.md (the ladder, row by row) and RELEASE-v0.4/5/6.md (regressions and card checks). | PASS |
| C6 | Reproducibility package | Manifests of every run committed (tracks/core/runs/, 1405 read by verify), drivers in tracks/core/analysis/release/, verify/ladder2/, verify/figscripts/; release records with the commands to repeat every check (RELEASE-v0.6.md). nrpic-stage verify of 2026-11-21 on the clean export of the tip (VERIFY_RESULTS.md; first on 9776100b, again after closing the stranded run): FAIL on two checks. (i) note: no tracks/core/note/main.tex (written in batch 8, C15; the clean-export verify has not been rerun since). (ii) runs: 10 of 1405 runs have problems (11 in the first verify): 9 runs of 2026-11-20/21 name the executables of scratch/core/exe/core_cosmo-amr/, which were published again after the runs (sha256 differs; the outputs are not affected, the record of the input is), and 2 runs not closed: core-20261119-143517-ec2f4fc (gauge test E2, job 4641, both cases rc 0; closed with nrpic-run finish after the verify) and core-20261121-154654-d3ec487 (job 4810, pending). Output checksums were not re-verified in this run (--no-checksums): the full verify read run outputs for 13 minutes and was stopped by its process id at the runs of 2026-11-19 (log scratch/core/tmp/lead_b4a/verify.log). The ladder figures are not registered as fig_*.py scripts under note/scripts/, so verify regenerates no figure (min-figs WARN); since batch 8 note/scripts/fig_geodesic.py, fig_collapse.py, fig_clusters.py are (run core-20261121-232936-d979f1c). The run directories of ladder rows 2-4 made before the registry are named and inventoried by sha256 (verify/preprogram/README.md, run core-20261121-231825-135474c). | FAIL |
| C7 | All of C3 passed, core-v0.1 released | core-v0.1 (7daed19) and core-v0.2 to core-v0.6 are tagged (CHANGELOG.md, CLAUDE.md); C3 of the core sheet is not all passed: rows 3 and 4 PARTIAL (C1; OPEN.md first section items 1, 2). | FAIL |
| C8 | Schematic: Verification ladder | verify/figs/schem_ladder.png (script verify/figscripts/schem_ladder.py with ladder_status.json; run core-20261115-162615-ca0fd2b), looked at 2026-11-21: rows 1-2 PASS, 3-4 PARTIAL, oblate open, as today. Its state line says 2026-11-15; no verdict has changed since. | PASS |
| C9 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | verify/figs/convergence_three_way.png (script verify/figscripts/convergence3.py, run core-20261115-154736-f9f5edb), three panels: particle number, mesh, gauge and boundary; looked at 2026-11-21. The figure exists; what it does not show is criterion C2's. | PASS |
| C10 | Data figure: Constraint norms against time | verify/figs/regress_os_core-20261115-065901-3629622.png (//H// against t), verify/figs/regress_flrw_core-20261115-065903-3629622.png, analysis/id/figs/t2_constraints.png, notes/scalar_figs/fig_flrw_conformal.png. | PASS |
| C11 | Data figure: At least one multi-scale slice mosaic with zoom boxes | verify/figs/prolate_mosaic.png (run core-20261115-162509-c691fb8): energy density at y = 0, t = 27.75 M, four nested windows +-10, 4, 1.5, 0.6 M with zoom boxes, at M/16 and M/8; looked at 2026-11-21. | PASS |
| C12 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md, EVIDENCE.md, OPEN.md and this CHECKLIST.md are in tracks/core/stage/G2/. No REVIEW.md: the lead's reviews of the helper branches are in RELEASE-v0.4.md, RELEASE-v0.5.md, RELEASE-v0.6.md and the merge commit messages. No SCOPE.md or SCOPING.md: core's scope is its sheet in the brief (9.3) and the charter's 'What differs from the brief' item 1. | FAIL |
| C13 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Figures use python/nrpic/figstyle.py and are drawn from registered runs: release figures fig_regress_v04, fig_quick_v06, fig_card_v06 (core-20261121-154700-2de4974), fig_card_v05 (core-20261121-154710-220c1b0), ladder figures of verify/figs/; every one named in EVIDENCE.md was looked at (column 'looked at' there and in RELEASE-v0.x.md). Exceptions on record: interfaces/figs/d1_*.png were not opened by the lead. | PASS |
| C14 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png (script note/scripts/schem_architecture.py, paperfig.py copied from harness/style; run core-20261121-232936-d979f1c, batch 8), state 2026-11-21: base (v0.1, v0.2), released by v0.3, v0.4, v0.5-v0.6, and open for v0.7 (relaxed lapse away from a hole, step limit with the gauge speeds, exact restart of the refined mesh state, oblate data, clumps from tables, collisions on several ranks), with the gate timeline and the six release tags; looked at after two layout corrections (journal, batch 8, Q2 outcome). Figure 1 of the note. The old verify/figs/schem_architecture.png of 2026-11-15 is superseded. | PASS |
| C15 | Working note written with /paper-writing; its manuscript checker passed with --compile | tracks/core/note/main.tex, main.pdf (REVTeX 4.2, 8 pages, batch 8): the shared implementation and releases core-v0.3 to v0.6, the ladder row by row with what is partial (rows 3, 4), the known limits (relaxed lapse, decision 0025 item 3; step rule with a Gamma-driver, 0027 item 2; restart limit, 0027 item 3), the ledger appendix (103 rows: run id or locator for every number, 70 marked with the verifier claim that recomputed them). Guide and notation one level above: tracks/core/WRITING_GUIDE.md, NOTATION.md. Data figures fig_geodesic, fig_collapse, fig_clusters and the schematic by one registered run from raw outputs (core-20261121-232936-d979f1c; inputs checked by sha256 where a checksum was recorded), each looked at. Checker with --compile and the guide's --forbid list: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are the guide's accepted exceptions (run ids, paths and locators in the ledger appendix and scripts; y_c labels). All 8 pages read. Limit: step 4 of the story-first procedure (reviewer subagents) not run, no subagent tool in the session (note/README.md). | PASS |
| C16 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G2/VERIFIER.md (commit ba01d3f6) by the fresh-context helper verify/verifier_g2 (batch 6), predictions committed before any check (41766638), verdicts committed before it read core's conclusions (2a4336b5, 805da131, 7fff69fc, 5e40e8b9); own readers and references, no import of python/nrpic or core's analysis code; registered runs core-20261121-212008-6986d13, -212106-131e909, -212244-3f782d9, -212248-a7972d1, -212422-b616c6e, -212516-0f0a65b, -212611-5973536, -213713-952a0c4, -213807-4cc035d, -213946-cee79fa, -214108-0960a46, -214230-ad24f6b, -214547-7a21ed3, -215228-d1f36f4, one figure each. Fourteen claims: every met ladder row (1, 2, the met part of 4, C3, C4) and at least one claim of each release core-v0.3 to v0.6; twelve confirmed to their printed digits; one general statement wrong (restarts exact only for periodic set-ups and the particle state: OPEN.md, state after batch 8, item u); five text defects (section 3), each corrected in batch 8 (C3 above; interfaces/scalar_field.md test 1; interfaces/newtonian_mode.md 5.2; interfaces/id_solver.md T1; verify/LADDER.md row 2). Limit, as the verifier states: a sample of claims, not 'every number'; the working note's ledger (note/tables/ledger.tex, batch 8) was written after the report, and its rows say which numbers the verifier recomputed (column 'verifier') and which no second agent has checked. | PASS |
| C17 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs and refuted predictions are in the journals (JOURNAL.md: P5 first criterion of 2026-11-15, the driver faults of the v0.4-v0.6 releases, the faults listed per session; JOURNAL-*.md of every package; verify/JOURNAL.md: prediction '0.64 collapses' refuted) and their manifests are committed; the list of STAGE_REPORT.md. | PASS |
| C18 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md (entry of batch 8 with predictions Q1, Q2 and their outcomes) and HANDOFF.md rewritten at the end of session core-lead-8 (2026-11-21, batch 8); RISKS.md last rewritten in batch 4a. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T16:21:46Z, clean export of `042f70bcd92b`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 042f70bcd92b (HEAD) in /data/haiyangw/nrpic/scratch/core/tmp/stage-verify/core-G2-042f70b-20261121T161613Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | FAIL | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); no verifier's report yet (VERIFIER.md, decision 0016) |
| style | PASS | no figure scripts yet |
| fig-script | PASS | 0 figures, each with its script |
| min-figs | WARN | 0 schematics and 0 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | FAIL | 10 of 1405 runs have problems |
| run-notes | WARN | 1147 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 36 lines |
| rerun | PASS | 0 of 0 scripts and commands ran cleanly in the export (none registered) |
| compare | PASS | 0 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 0 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_clusters.* | note/scripts/fig_clusters.py | data | to be confirmed by the session |
| note/figures/fig_collapse.* | note/scripts/fig_collapse.py | data | to be confirmed by the session |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/core/stage/G2/VERIFIER.md` present; its first lines:

> # Verifier report: core, gate G2 (fresh context)
> 
> Verifier: helper `verify/verifier_g2` of owner core, batch 6, 2026-11-21 (21:14Z to
> 22:00Z), model Opus. I did not produce any of the results checked here. Before my
> verdicts were committed (commits 2a4336b5, 805da131, 7fff69fc, 5e40e8b9: the outcome
> entries of `tracks/core/verify/verifier_g2/JOURNAL.md`) I read only the claims (`EVIDENCE.md`,
> `CHECKLIST.md`, the first section of `OPEN.md`, `verify/LADDER.md`, the interface
> documents), the paper source for its digits, the source tree for file formats, and raw
> outputs; not core's STATUS, HANDOFF, REVIEW files or journal conclusions. Exceptions,
> both after a first independent measure disagreed with a claim: I read the measure (not
> the result) in `tracks/core/analysis/idsolve2/test_c.py` (mean over r < 1) and the
> column names of `athenak/src/outputs/history.cpp`. Package: `tracks/core/verify/verifier_g2/`

## Null results and failed runs

- `core-20261115-035638-c9aa6d2`: failed (recorded as None) (exit 1), evolution of the expanding ball against the exact solution: bound-ct-n160 (cells 160, half-width 20, gauge ct, start shift zero, q = 1, ball --Rb 5 --e0 0.16 --RE 10, extra none)
- `core-20261115-035639-c9aa6d2`: failed (recorded as None) (exit 1), evolution of the expanding ball against the exact solution: bound-ct-n080 (cells 80, half-width 20, gauge ct, start shift zero, q = 1, ball --Rb 5 --e0 0.16 --RE 10, extra none)
- `core-20261115-040408-1311b8e`: failed (recorded as None) (exit 1), evolution of the expanding ball against the exact solution: bound-ct-n320 (cells 320, half-width 20, gauge ct, start shift zero, q = 1, ball --Rb 5 --e0 0.16 --RE 10, extra none)
- `core-20261115-040410-1311b8e`: failed (recorded as None) (exit 1), evolution of the expanding ball against the exact solution: bound-mp-n160 (cells 160, half-width 20, gauge mp, start shift zero, q = 1, ball --Rb 5 --e0 0.16 --RE 10, extra none)
- `core-20261115-112103-b7b431d`: failed (recorded as None) (exit 1), unmodified multigrid, hydro binary_gravity test on an isolated uniform mesh (multipole boundary, order 4), N=32: does the solver of this tree work before any change
- `core-20261115-112104-b7b431d`: failed (recorded as None) (exit 1), unmodified multigrid, hydro binary_gravity test on an isolated uniform mesh (multipole boundary, order 4), N=64: does the solver of this tree work before any change
- `core-20261115-113512-a5197ba`: failed (exit 1), Regression R on a card: two punctures at rest with adaptive mesh, trackers, horizon finder and tracers (problems/puncture/tracers_headon.athinput), 24 cycles, executable built from main
- `core-20261115-113513-a5197ba`: failed (exit 1), Regression R on a card: same input, executable of this branch
- `core-20261115-113743-c89b6e3`: superseded (exit 0), Test
- `core-20261115-113744-c89b6e3`: superseded (exit 0), Test
- `core-20261115-113745-c89b6e3`: superseded (exit 0), Test
- `core-20261115-113841-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113842-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113844-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113845-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113846-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113847-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113848-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113849-c89b6e3`: failed (exit 1), Test 1a: P = 0.3, tabulated second-order correction (must agree with approx)
- `core-20261115-113850-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113851-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-113852-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113853-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113854-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-113855-c89b6e3`: failed (exit 1), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113856-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113857-c89b6e3`: failed (exit 1), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113858-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113859-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-113900-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-113901-c89b6e3`: failed (exit 1), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113902-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-113903-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-113904-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-113905-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-113906-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-113907-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-113908-c89b6e3`: failed (exit 1), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-113909-c89b6e3`: failed (exit 1), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-113910-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-113911-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-113912-c89b6e3`: failed (exit 1), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-113939-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113940-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113941-c89b6e3`: superseded (exit 0), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113942-c89b6e3`: superseded (exit 0), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113943-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113944-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113945-c89b6e3`: superseded (exit 0), Test 1a: truncation error of the Hamiltonian residual of a Brill-Lindquist puncture, no curvature
- `core-20261115-113946-c89b6e3`: superseded (exit 0), Test 1a (i): Bowen-York puncture P = 0.3, no correction
- `core-20261115-113947-c89b6e3`: superseded (exit 0), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113948-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-113949-c89b6e3`: superseded (exit 0), Test 1a (v): P = 0.3, tabulated full correction
- `core-20261115-113950-c89b6e3`: superseded (exit 0), Test 1a: P = 0.3, tabulated second-order correction (must agree with approx)
- `core-20261115-113951-c89b6e3`: superseded (exit 0), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113952-c89b6e3`: superseded (exit 0), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-113953-c89b6e3`: superseded (exit 0), Test 1a (iv): P = 0.3, closed-form correction
- `core-20261115-113957-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-114007-c89b6e3`: superseded (exit 0), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-114009-c89b6e3`: superseded (exit 0), Test 1a (ii),(iii): scaling with momentum, no correction
- `core-20261115-114011-c89b6e3`: superseded (exit 0), Test 1a (iv): scaling with momentum, closed-form correction
- `core-20261115-114012-c89b6e3`: superseded (exit 0), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-114014-c89b6e3`: superseded (exit 0), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-114015-c89b6e3`: superseded (exit 0), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-114017-c89b6e3`: superseded (exit 0), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-114018-c89b6e3`: superseded (exit 0), Test 1a (vi): momentum and spin not parallel, no correction
- `core-20261115-114019-c89b6e3`: superseded (exit 0), Test 1a (vi): spin 0.4 along z, closed-form correction
- `core-20261115-114020-c89b6e3`: superseded (exit 0), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-114021-c89b6e3`: superseded (exit 0), Test 1a (vi): spin 0.4 along z, no correction
- `core-20261115-114022-c89b6e3`: superseded (exit 0), Test 1a (vi): momentum and spin not parallel, closed-form correction with cross term
- `core-20261115-114023-c89b6e3`: superseded (exit 0), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-114026-c89b6e3`: superseded (exit 0), Test 1a (vii): two punctures with momenta and a spin, no correction
- `core-20261115-114030-c89b6e3`: superseded (exit 0), Test 1a (vii): two punctures, closed-form corrections
- `core-20261115-115339-7a60df2`: failed (exit 1), Test 1b: Bowen-York puncture m = 1, P = 0.3 along x, closed-form correction, finest cells 1/32, to t = 40
- `core-20261115-115342-7a60df2`: stopped (exit 143), Test 1b reference: stock generator z4c_boosted_puncture, rest mass 1.0112, velocity 0.2844, same mesh, to t = 40
- `core-20261115-115551-7a60df2`: stopped (recorded as 'cancelled') (exit 1), Diagnostic: why the number of MeshBlocks grows from 400 to 1184 in run core-20261115-115339-7a60df2; same input, 160 cycles, block limit 8192, lapse slices every 8 cycles
- `core-20261115-120038-70a5190`: stopped (recorded as 'cancelled') (exit 143), Test 1b (A): Bowen-York puncture m = 1, P = 0.3 along x, closed-form correction, finest cells 1/16, to t = 40
- `core-20261115-120040-70a5190`: stopped (recorded as 'cancelled') (exit 1), Test 1b (C): stock generator z4c_boosted_puncture, rest mass 1.0112, velocity 0.2844, same mesh as (A), to t = 40
- `core-20261115-120041-70a5190`: stopped (recorded as 'cancelled') (exit 1), Test 1b (B): Bowen-York puncture m = 1, P = 0.3, no correction, finest cells 1/16, to t = 40
- `core-20261115-120043-70a5190`: stopped (recorded as 'cancelled') (exit 1), Test 1b (E): Bowen-York puncture m = 1, P = 0.043 along x, S = 0.3 along z, closed-form correction (the heavy black hole of test 3 in its own units), to t = 40
- `core-20261115-120044-70a5190`: stopped (recorded as 'cancelled') (exit 1), Test 1b (D): Bowen-York puncture m = 1, P = 0.6, closed-form correction, finest cells 1/16, to t = 30
- `core-20261115-120534-5bdb22c`: failed (recorded as None) (exit 1), Accuracy of the arithmetic-geometric-mean logarithm of the normal draw against mpmath (200 bits) on 204000 values of s
- `core-20261115-124953-8e05112`: failed (recorded as None) (exit 1), Experiment (source not in the repository, patch tracks/core/notes/rng_gather_experiment.diff): mesh-metric kick demonstration D2 with a reconstruction that forms the cell coordinate from the position alone; expected to give bit-identical states for 8 and 64 MeshBlocks
- `core-20261115-132842-b33b7f3`: failed (recorded as None) (exit 1), P2 P3 P4: collision rate of a Maxwell-Juttner gas (1e6 particles, 32^3 cells, theta 0.01 to 10, with and without sub-cycling), conservation, null runs; processor
- `core-20261115-133146-5384d02`: failed (recorded as None) (exit 1), Scalar field test 1: Klein-Gordon plane wave of a test field on flat spacetime (dispersion relation, spatial orders for nghost 2, 3, 4, temporal order, dissipation, five potentials against the ordinary differential equation)
- `core-20261115-135349-1134b04`: failed (recorded as None) (exit 1), P10 collisions in a static homogeneous curved metric on the mesh (lapse 0.7, non-diagonal spatial metric): symmetric triad with midpoint pusher, Cholesky triad with Boris pusher, flat reference; 2e5 particles, 20 collision times; processor
- `core-20261115-135417-5a6953e`: failed (recorded as None) (exit 1), Regression on processors, final source of the scalar-field package: executable of the unmodified source (b28ecca) against 5a6953e, five existing set-ups, every output file compared byte by byte
- `core-20261115-135625-4b40aa5`: failed (recorded as None) (exit 1), driver check of run_cluster.py on the processor: stable cluster y_c = 0.819, two steps (t = 0.25 M), runs off, sigma0, kn30
- `core-20261115-141416-3f7ca07`: failed (recorded as None) (exit 1), Regression on processors, last source of the scalar-field package (3f7ca07, after the uniform shift in the test problem generator): executable of the unmodified source (b28ecca) against it, five existing set-ups
- `core-20261115-145323-5407341`: failed (recorded as None) (exit 1), lead integration: byte regression c1-c5 (rng package driver), baseline main source 74ed745 vs merged 609a875, processor
- `core-20261115-145448-3629622`: failed (recorded as None) (exit 1), lead integration: nrpic_cf byte regression (P2) and combined format-2 + Bowen-York curvature (P5), baseline 74ed745 vs merged 609a875, processor
- `core-20261115-145804-3629622`: failed (recorded as None) (exit 1), lead: analysis of the nine id card runs that finished after the id helper's session (T2c, T2d, T2e, T3): test2_evolution.py for prefixes t2 and t3
- `core-20261115-145939-3629622`: failed (recorded as None) (exit 1), lead integration: nrpic_cf checks P2 and P5 on the card executables (job 4430)
- `core-20261115-150002-3629622`: failed (recorded as None) (exit 1), lead integration P4: Newtonian point-mass field (T1 of problems/newton) N=32, 64 on the merged processor executable 609a875
- `core-20261115-150315-23eca56`: failed (recorded as None) (exit 1), lead integration P5: combined format-2 + Bowen-York curvature on the merged processor executable 609a875 (the first attempt inside core-20261115-145448-3629622 failed: command-line parameters missing from the input)
- `core-20261115-154604-63ad8eb`: failed (recorded as None) (exit -15), expanding ball with the old and the new lapse: bound-mp-n080 (cells 80, half-width 20, lapse mp, ball --Rb 5 --e0 0.16 --RE 10)
- `core-20261115-154606-63ad8eb`: failed (recorded as None) (exit -15), expanding ball with the old and the new lapse: bound-ct-n080 (cells 80, half-width 20, lapse ct, ball --Rb 5 --e0 0.16 --RE 10)
- `core-20261115-154622-e1a4d0c`: stopped (exit None), Test R of JOURNAL-clump (first attempt): old set-ups of nrpic_cf with the release processor executable and this branch's, every output byte compared
- `core-20261115-154650-cf9f921`: failed (exit 1), T2 output schedule across a restart: release core-v0.3 against the corrected Driver::Finalize (uninterrupted, cycle-limit stop, wall-clock stop)
- `core-20261115-154749-1b20b0f`: failed (exit 1), T1 initial slice at N*: twin, order of the constraints in the amplitude, odd part against the linear predictions (processors, zero steps)
- `core-20261115-155841-bc78aa8`: failed (exit 1), T6 existing behaviour: scalar-field inputs of wave 1 (flrw, plane, wave, refined mesh, power and Mukhanov-Sasaki sources, restart) with the processor executable of release core-v0.3 and the new one, every output file byte by byte
- `core-20261115-160354-b4430da`: failed (recorded as None) (exit -15), expanding ball with the old and the new lapse: leak1-n128 (cells 128, half-width 32, lapse leak1, ball --Rb 10)
- `core-20261115-160530-819d588`: failed (recorded as None) (exit 1), S: perturbing radial force in flat space (particle at rest, moving particle against an independent integration, null)
- `core-20261115-160549-a36abe3`: failed (exit 1), T6 existing behaviour (rerun with the corrected comparison of restart files): scalar-field inputs of wave 1 with the processor executable of release core-v0.3 and the new one, every output file byte by byte
- `core-20261115-160707-6537687`: failed (recorded as None) (exit 1), G1 G2: one collision step on frozen particles in the static conformal metric with a gradient, coll_energy = cell and = particle, 14 cases, 8e6 particles, against the pair model (references core-20261115-160136/160137/160139-819d588)
- `core-20261115-160746-19e3afe`: failed (exit 1), T4 external gravity of the Newtonian mode: Kepler orbits, softened circular orbits, background term, expanding periodic box; accretion diagnostics in that mode
- `core-20261115-160912-0656925`: failed (recorded as None) (exit 1), G4: equilibrium in the potential well with streaming and collisions, coll_energy = cell and = particle, two seeds, 1e6 particles, 600 steps, processor
- `core-20261115-161129-f905e98`: failed (exit 1), T6 byte regression of existing set-ups: release core-v0.3 against the changed source (7 relativistic and gravity cases, 3 Newtonian-mode cases, static mesh)
- `core-20261115-161513-e09c0b1`: stopped (exit None), T8 at N = 64: curvature perturbation R^NR from the dumps against W R alpha of the lockstep record, nmax2 = 64, to t = 3.2 (processors, one core)
- `core-20261115-161528-ff00411`: stopped (exit None), Card checks of work package dfix: T1 static tracer, T3 accretion, T4 Kepler, T5 pair horizon, memory at 2700 slots, 16^3 against 32^3 MeshBlocks on the three-puncture mesh, T1 acceptance (horizon_calib 250 M)
- `core-20261115-162714-abf9d27`: failed (recorded as None) (exit 1), G4 (processor version): equilibrium in the potential well with streaming and collisions, coll_energy = cell and = particle, two seeds, 1e5 particles, 400 steps
- `core-20261115-163855-7be94e4`: failed (exit 1), T5 U9: Track E's validation of U1-U8 on processors (run core-20261115-155122-eb68eaa) with the card run u9 of core-20261115-155404-24c88e3 as --card (test A14), reference as committed by Track E
- `core-20261115-171107-cdd7c88`: failed (recorded as None) (exit 1), G1 G2 on one A100: one collision step in the static conformal metric, cases psi_iso, well_tolman, well_shift, psi_iso_hot, both modes
- `core-20261115-171146-cdd7c88`: failed (recorded as None) (exit 1), G2e on one A100: replay of single collision steps by the Python twin, wave-1 cases and the cases of coll_energy
- `core-20261115-171154-cdd7c88`: failed (recorded as None) (exit 1), G4 on one A100: equilibrium in the potential well with streaming and collisions, both modes, two seeds
- `core-20261115-171207-cdd7c88`: failed (recorded as None) (exit 1), P11 with coll_energy on one A100: relativistic cluster y_c = 0.819 at Knudsen number 3, collision cells of 2 M, coll_energy = cell and = particle, 150 M
- `core-20261115-171830-cdd7c88`: failed (recorded as None) (exit 1), R on one A100: five existing set-ups, executable of core/collisions-2 (options absent) against the release executable core-v0.3
- `core-20261115-171836-cdd7c88`: failed (recorded as None) (exit 1), Rerun of wave 1 with the executable of core/collisions-2 (options absent) on one A100: P2 P3 P4 rate, conservation, null runs; outputs compared with core-20261115-135816-18d4555
- `core-20261115-172012-cdd7c88`: failed (recorded as None) (exit 1), Rerun of wave 1 with the executable of core/collisions-2 (options absent) on one A100: P5 P6 relaxation and entropy; outputs compared with core-20261115-135932-18d4555
- `core-20261115-172059-cdd7c88`: failed (recorded as None) (exit 1), Rerun of wave 1 with the executable of core/collisions-2 (options absent) on one A100: P7 MeshBlock divisions, restart, seed; outputs compared with core-20261115-140011-18d4555
- `core-20261115-172122-cdd7c88`: failed (recorded as None) (exit 1), Rerun of wave 1 with the executable of core/collisions-2 (options absent) on one A100: P8a time step; outputs compared with core-20261115-140021-18d4555
- `core-20261115-172223-cdd7c88`: failed (recorded as None) (exit 1), Rerun of wave 1 with the executable of core/collisions-2 (options absent) on one A100: P10 homogeneous curved metric; outputs compared with core-20261115-140259-8742cdf
- `core-20261115-175447-764390e`: stopped (exit -15), T12: Track E's A4 in its own form (record ratios <|H|/[H]>, <|M|/[M]> when the amplitude is halved) at N = 64 on processors (s = 1, -1, 1/2, -1/2, 0; nmax2 = 64; to t = 3.2) and at N = 32 from runs -155040-eb68eaa and -161040-760b515; T8 at N = 64 on the run s = 1
- `core-20261115-181243-a88c222`: failed (recorded as None) (exit 1), initial-data solver, test F: smooth triaxial ball with the settings of test E at 64 cells to t = 2 with field dumps, solve off
- `core-20261115-181244-a88c222`: failed (recorded as None) (exit 1), initial-data solver, test F: smooth triaxial ball with the settings of test E at 64 cells to t = 2 with field dumps, solve code
- `core-20261115-181246-a88c222`: failed (recorded as None) (exit 1), initial-data solver, test F: smooth triaxial ball with the settings of test E at 128 cells to t = 2 with field dumps, solve off
- `core-20261115-181247-a88c222`: failed (recorded as None) (exit 1), initial-data solver, test F: smooth triaxial ball with the settings of test E at 128 cells to t = 2 with field dumps, solve code
- `core-20261115-182037-e24d0d0`: failed (exit 1), G1 G2 regraded: code numbers of run core-20261115-160707-6537687 against the pair-model reference with the cell rate alpha_c/psi_c^6 (runs -181655, -181657, -181700, -181702); prediction JOURNAL-coll2.md 18:40 UTC
- `core-20261115-183107-ca15f8b`: failed (recorded as None) (exit 1), initial-data solver, test V0: torus_code_p1_n32 without id_vector, published executable
- `core-20261115-183109-ca15f8b`: failed (recorded as None) (exit 1), initial-data solver, test V0: torus_code_p1_n32 without id_vector, new executable
- `core-20261115-183458-b4430da`: failed (recorded as None) (exit -15), Einstein-Straus data of Track D, dust at cells of 4 M (coarse processor version of test ES), lapse relaxation T = 2 M, t = 10 M
- `core-20261115-184348-4ff75bd`: failed (recorded as None) (exit 1), initial-data solver, test V5: smooth ball (sphere), vector part with the monitor as residual, 64 cells
- `core-20261115-184637-4ff75bd`: failed (recorded as None) (exit 1), initial-data solver, test V5: smooth ball (strained), vector part with the monitor as residual, 64 cells
- `core-20261115-184925-71663b2`: failed (exit 2), T12 analysis repeat and T12b: record factors in narrower windows, mean of the second-order part of H, and the part of R^NR odd in s against W R alpha (N = 64), on the files of core-20261115-175842-7d54ff5 (no AthenaK run); figure fig_halving.png
- `core-20261115-185053-4ff75bd`: failed (recorded as None) (exit 1), initial-data solver, test V6: evolution of the smooth strained ball with the scalar and the vector solve (mode code), settings of test E
- `core-20261115-203207-b4430da`: failed (recorded as None) (exit 1), bound expanding ball through turnaround and collapse to a black hole, new lapse T = 0.5 M (test L3)
- `core-20261115-205317-6817f49`: stopped (exit None), G4 on one A100: equilibrium in the potential well with streaming and collisions, both modes, two seeds, theta_inf = 0.2
- `core-20261119-140406-8707fc4`: failed (exit 1), T8 analysis (P10): byte regression of the Z4c benchmark, oblique-wave amplitude scan N=64,128, z noise of the 256x256x16 box to t=4, circular wave card vs processor
- `core-20261119-141059-f3ccf56`: failed (exit 1), D of coll2-close: size of the byte differences between the card runs of the new executable (f46f159, options absent) and of the release executable core-v0.3 in the wave-1 collisional boxes (job 4484)
- `core-20261119-143246-812bebf`: failed (exit 1), omp: initial data of the thread tests (plane wave, collision box, 1e5-particle cluster, 64^3 cosmology box, Newtonian box of Track D's size)
- `core-20261119-143706-92efe0f`: stopped (exit -15), omp T0/T1a: serial build of this branch against release core-v0.3 (P0), and the OpenMP builds on one thread against it (P1), 13 set-ups
- `core-20261119-143745-78506dd`: failed (exit 1), faces a1: evolution with the present outflow faces at 16 against a reference with faces at 32 (ball, puncture, boosted puncture; extrapolation order 2 and 4; no dissipation)
- `core-20261119-144855-2a2ef23`: failed (exit 1), newton2 T1 analysis: Fourier solver against multigrid, numpy scheme and mixed radix
- `core-20261119-145554-6e2a253`: failed (recorded as None) (exit 1), mpi T1 (t1_kerr): test particles in a fixed metric on the mesh, 1, 2 and 4 ranks compared
- `core-20261119-145557-6e2a253`: failed (recorded as None) (exit 1), mpi T1 (t1_kerr_boris): test particles in a fixed metric on the mesh, 1, 2 and 4 ranks compared
- `core-20261119-145559-6e2a253`: failed (recorded as None) (exit 1), mpi T1 (t1p_box): test particles in a fixed metric on the mesh, 1, 2 and 4 ranks compared
- `core-20261119-150507-8224d72`: failed (exit 139), T10 of cosmo-amr: Track A's above-threshold case S1 (mu = 0.3) with adaptive refinement toward the peak, fine-shape deposit, light-speed step limit, guard, finder status, region norms; how far does it get
- `core-20261119-150818-615d921`: failed (exit 1), R a, b: ten scalar-field cases of wave 1 byte by byte against release core-v0.3; the three stochastic examples (20 steps, restart) against the published executable of core/scalar-2
- `core-20261119-150832-64460a8`: failed (exit 1), R c: relativistic and gravity set-ups (geo, boris, dep, east, os, jeans, binary) byte by byte against release core-v0.3
- `core-20261119-152217-73dccb9`: failed (exit -15), faces b1: ball with the non-wave radiative condition (orders 2 and 4, powers 3 and 2.5, Theta variant) to t=16
- `core-20261119-154816-ca46836`: failed (recorded as None) (exit 1), mpi T3 (t3_cluster_ext): self-gravitating cluster with Z4c on a uniform mesh, 1, 2 and 4 ranks against each other
- `core-20261119-154940-1c3e906`: failed (exit 1), omp P0: the serial build S of this branch (source with the deposit target of nrpic_threads.hpp, option absent) against the release core-v0.3 executable, all 13 regression cases, one thread each, four cases side by side; byte-for-byte comparison of every output file. Registered by hand: nrpic-run refused (16 cores of core busy in other sessions)
- `core-20261119-155057-57325bc`: failed (exit 1), omp P2-P5, P9-P11: the threaded build O3 at 4 and 16 threads (two runs each) against one thread of O3, all 13 regression cases; then the deposit cases with deposit_threads = private at 1, 4, 16 threads (two runs each); byte and number comparison of every output file. Registered by hand: nrpic-run refused (16 cores of core busy in other sessions)
- `core-20261119-155522-8480419`: stopped (exit 1), C2: card executable of the final source 5cc2821 on the gauge example with con_signed (32^3, 20 steps), to be compared with the processor executable by c2_compare.py; journal entry 11
- `core-20261119-155740-3c44b74`: failed (recorded as None) (exit 1), T11 of cosmo-amr: restarts on adaptive periodic meshes (moving tracker across the face, peak with the lapse ladder, uniform universe with the finder), restarted inside the loop and at the end of a run, with the executable of T1-T9 (old) and with the restart counters (new); hand-written manifest because nrpic-run refused (16 cores busy in live local runs of core)
- `core-20261119-155830-248f393`: failed (exit 1), omp P12: OpenMP build with Kokkos debug mode and View bounds checking at 4 threads, atomic and private deposit, cases dep, east, newton, coll, against one thread of O3 (reused from run core-20261119-155057-57325bc). Registered by hand: nrpic-run refused (16 cores of core busy in other sessions)
- `core-20261119-160404-beddeac`: stopped (exit 0), omp strong scaling, phase t4: O3 at four threads, the four scaling cases side by side, two repeats, places from omp_places.py. Registered by hand: nrpic-run refused (16 cores of core busy in other sessions)
- `core-20261119-161148-7f60657`: failed (recorded as None) (exit 1), mpi T4 (P4e): restarted runs of the cluster compared with each other (same dump read on different rank counts; dumps of 1, 2, 4 ranks)
- `core-20261119-162128-1cd17b2`: failed (exit 1), newton2 T4c: the embedded ellipsoid of T4b with the multigrid solver
- `core-20261119-162300-464fb38`: failed (recorded as None) (exit 1), mpi figures of T3 to T5 from their registered runs
- `core-20261119-162949-d87b113`: failed (recorded as None) (exit 1), T12 of cosmo-amr: the processor executable to be published (source 3c44b74) reruns the decks of T1 (22 cases), T2 (16 cases) and T9 (5 cases) and every output file is compared byte by byte with the tested executable (source 901d8b3); hand-written manifest because nrpic-run refused (16 cores busy in live local runs of core)
- `core-20261120-220849-cea5881`: failed (exit 1), byte regression of release candidate core-v0.4 (merge f9323185, processor build .work/build_cpu_v04rc) against release core-v0.3 on the twelve set-ups of wave 1
- `core-20261120-221728-59d6e64`: stopped (exit 1), newton2 second card job: T6c (balls on a lattice of the fine cell size on uniform 64^3, uniform 128^3 and 64^3 + one level, inside the fine region and across the level boundary) and T4d (embedded ellipsoid: kernels of T2 at 64^3, linear cloud at 96^3, 128^3 with both symbols and with the kernels of T2, 256^3)
- `core-20261120-221835-4870ae5`: failed (exit 1), newton2 card job 2a: T6c (balls on a lattice of the fine cell size on uniform 64^3, uniform 128^3 and 64^3 + one level, inside the fine region and across the level boundary) and T4d at 64^3 (kernels of T2) and 96^3 (linear cloud), Fourier solver
- `core-20261120-222724-75e323c`: failed (exit 1), quick tests of release candidate core-v0.4 on processors: READY example of each of the seven merged branches, merged executable against the branch executables
- `core-20261120-223022-2f5bbc0`: stopped (exit 1), card check Kb of idsolve2 (journal entry 13): card build of 4266c2d on one A100, the changed case p5_mov_n64 and w1_far_n128, against the processor runs
- `core-20261120-223248-8a370f3`: failed (exit 1), omp P15 (threads 1 and 2): cause of the thread dependence of the gas multigrid: Jeans deck with the diagnostic executable (mean of CalculateAverage summed plainly, in a fixed order, in a fixed order with compensation), two MeshBlock sizes
- `core-20261120-223428-587c09a`: failed (exit 1), omp P16 (two threads): restarts under threads: continued against uninterrupted run (east with Z4c, Newtonian mode) at one thread, two threads with private deposit copies, two threads atomic
- `core-20261121-025527-eb8e6b7`: failed (exit 3), T10c of cosmo-amr: T10b restarted at t = 10 with four finder surfaces that can flow (hmean_tol 1e30); first restart of an adaptive run on a card
- `core-20261121-030052-6acdca9`: failed (exit 1), omp P15 (threads 1, 2, 4, 6): cause of the thread dependence of the gas multigrid: Jeans deck with the diagnostic executable (mean of CalculateAverage summed plainly, in a fixed order, in a fixed order with compensation), two MeshBlock sizes
- `core-20261121-032250-db52a52`: failed (exit 1), analysis of T10c of cosmo-amr (run core-20261121-025527-eb8e6b7): the finder searches of the restart and the restart against the uninterrupted run core-20261120-220816-09f6f79
- `core-20261121-032510-c83f904`: failed (exit 1), T14b of cosmo-amr: card check of the card executable of source 1548d49 (build_gpu_b) on the decks of T2b (U, S, Sf, A, M, G) and T9b (ladder)
- `core-20261121-033223-e1d596b`: failed (exit 3), T14b and T10g of cosmo-amr with the card executable of source 1548d49 (build_gpu_b): card check on the decks of T2b (U, S, Sf, A, M, G) and T9b (ladder), then the scouting run of Track A's S1 again with the corrected fine-shape deposit and the four finder surfaces of T10c
- `core-20261121-065009-29b855c`: failed (exit 1), core-v0.5 candidate: quick tests on processors (one example per merged branch against the branch executable; threaded deposit with and without the fine shape at 1 and 4 threads; Kerr swarm and cluster on 1 and 2 ranks; stop of deposit_fine_shape on 2 ranks)
- `core-20261121-070623-077b056`: failed (exit 1), core-v0.5 candidate: byte regression of the threaded processor build at one thread against release core-v0.4, twelve set-ups
- `core-20261121-071842-f5a8b56`: failed (exit 1), core-v0.5 candidate, test R3: threaded build with the flags of the serial build (OMP_OPT=debug) at one thread against release core-v0.4, twelve set-ups: flags or back end as the cause of the rounding differences of athena_cpu_omp
- `core-20261121-080555-9730e2a`: failed (exit 1), test of scripts/submit_chain.sh (decision 0021 item 6): outside kills faked by a fake executable that kills its own pid; fake sbatch/squeue, no Slurm job; prediction JOURNAL.md 2026-11-21T08:00Z
- `core-20261121-081152-5fc1ea4`: failed (exit 1), newton2 T12: the example command lines of READY (periodic_fft with both symbols, embedded_ellipsoid, isolated_smr) with the published merged processor executable scratch/core/exe/core_newton-2/athena_cpu; fft example against T11b, refined-mesh example against the card run of T6c
- `core-20261121-082154-74071af`: failed (exit 1), faces analysis r2: byte comparison of the regression run core-20261121-080705-f6f9a0d (new executable without the options against the release core-v0.5)
- `core-20261121-082457-ab56e8f`: failed (exit 1), faces analysis r1: byte comparison of the regression run core-20261120-220733-ea71a73 (executable of cb50e22 without the options against the release core-v0.3), which the session of 2026-11-20 did not evaluate
- `core-20261121-083244-7bf063a`: failed (exit 1), faces analysis e1: example input against the package inputs, arrays exact and files byte for byte
- `core-20261121-133243-74c17ff`: failed (exit 1), Ro: threaded build of release candidate core-v0.6 at one thread against release core-v0.5, twelve set-ups (not a byte reference; reported)
- `core-20261121-133938-efeb8b4`: failed (exit 1), Ro judged: histories of the threaded build of core-v0.6 at one thread against release core-v0.5 (run core-20261121-133243-74c17ff)
- `core-20261121-134059-e3ab6f3`: failed (exit 1), faces card check k1 judged: card run core-20261121-083511-2cff9df (Slurm 4782) of the branch card executable against the processor runs r2 and m1

## Open risks


State 2026-11-21 15:57Z, after release core-v0.6 (session core-lead-6). Evidence for each
line: `stage/G2/OPEN.md` (first section items p to t; older items by release and number)
and the documents named. Lines marked "(2026-11-15)" were not rechecked in this session.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Relaxed lapse (`<z4c> lapse_leak`) acts in vacuum around a black hole: horizon shrinks in coordinates, mass grows by 1.3e-3 in 100-200 M (Track D V-1GB; OPEN p) | certain wherever it is used with a hole | biases the dress and growth measurements of Track D; any track that combines expanding matter with a hole | horizon mass of a vacuum control with the same gauge | null tests without the option (decision 0022); fix first in core-v0.7 (REQUESTS_WAVE3 W24): weight that vanishes around tracked punctures, optional matter gate; test V-1GB to 5e-5 |
| Ladder rows 3-4 stay PARTIAL (OPEN first section items 1, 2) | high | core's G2 and Track C's threshold criterion delayed | oblate merge; M/8 bisection cost | oblate in core-v0.7 (W27); row-4 bisection redone on M/8 against a collisionless control (Track C measured 8.2-8.3 s per M on M/8, about 2.3 card-hours per 1000 M run; core's monoenergetic models to 300 M about 0.6 card-hours each) |
| Mesh-made push of clusters on coarse meshes (Track C drift: M/4 moves King controls outward, 7-10 times less on M/8) | certain on M/4 | stabilises models; moves any fate bracket | collisionless control on the same mesh | no threshold work on M/4; read every fate against a control |
| Card queue shared with other users; jobs wait an hour or more | certain | release card checks lag the tags (core-v0.5 job 4772, core-v0.6 job 4800 ran after the tag) | squeue before submitting | tag on processor regressions; card check closes later and is written into RELEASE and READY |
| Branches drift from the releases (core/oblate does not hold core-v0.5; core/clump-table holds v0.5, not v0.6) | happened | merge conflicts, regressions against an old base | `git merge-base --is-ancestor` at each release | branches merge main before publishing READY (W26, W27) |
| Paper details filled in independently (deposit order, filter passes, refinement treatment; brief 9.3 main risk) (2026-11-15) | certain | results differ from the authors' at the 1e-3 level | ladder rows 3-4 | report our choices with each result; no tuning to the paper's numbers |
| Collision steps raise the energy at the particles' own metric (OPEN 2026-11-15 item 6) (2026-11-15) | certain for Track C science runs | spurious heating of a collisional core | `coll_budget` columns of `.coll.hst` | decide with Track C before G3 |
| Lapse front from a sharp matter surface; steepens without bound with resolution in the bound ball (OPEN 2026-11-15 item 7; verify/README wave 2 item 4) | high for Tracks A and D | non-convergent core shells after the front arrives | central lapse against a(tau) | smooth edges; gauge choice with Track A |
| Faces options reduce but do not remove reflection (OPEN core-v0.6 b-d) | certain | late-time errors in runs with near faces | region norms, a run with distant faces | distance of the faces stays the cure |
| Initial-data solver limits: vector part stalls at level boundaries; puncture floor set by the faces; one rank (OPEN core-v0.6 f-h; W28) | certain where used | constraint residual floors in solved data | the solver's record | use `id_residual = stencil`, distant faces; no release date |
| Card runs with deposit are not byte-reproducible | certain | a card byte regression cannot show identity | baseline twice against new | compare on processors; bounds written before a card check |
| Several ranks: the particle module runs on MPI since core-v0.5, but eleven options, collisions, `id_solve` and the Newtonian Fourier solver stop there or are untested (OPEN core-v0.5, core-v0.6 h, i, m) | certain | caps those capabilities at one card | the messages at start | port per request (W22 collisions) |
| Upstream publishes an official NRPIC implementation (brief 9.3) | unknown | duplicate effort; merge decision | kb watch (REQUESTS_WAVE3 W12: nothing yet) | decide with the group when it appears |

## Decision requested from the group

Keep core at G2 in progress (NOT MET: ladder rows 3 and 4 PARTIAL, no single three-way convergence study, no working note, no fresh-context verifier). Release core-v0.6 closed (card check PASS, release processor build byte-identical); first item of core-v0.7: the relaxed-lapse defect (decision 0022 item 3). Schedule a verifier session and a note session for core when ladder rows 3 and 4 close.
