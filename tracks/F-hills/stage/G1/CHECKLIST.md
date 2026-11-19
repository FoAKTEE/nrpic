# Checklist: F-hills G1

Collected by `harness/bin/nrpic-stage collect F-hills G1` on 2026-11-19T15:11:36Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: Newtonian restricted and full three-body references (newton3; corrected energies of newton3_fix, F-20261115-175232-d399e83, -180351-b8eb386) and the geodesic (HRNA) reference (geodesic_binary), both reproduced against the literature (STATUS.md T1, T2); both run from the P1 start state (E6, F-20261115-174102-ffa764f); vacuum NR runs need no coupling: S3/S2 (F-20261115-173601-2fae2dc), smoke (F-20261115-174602-c6879fe)
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: NR readers nrread.py validated on a synthetic full-Newton trajectory in AthenaK formats with planted failed searches 10/10 (F-20261119-143627-1a84aa5), on core's run A (E3a, F-20261115-182100-613c9c6), passage analysis on synthetic files (E9, F-20261115-183737-49f0a7f); on the real S3/S2/smoke outputs reproduced from the raw files by the lead's own parser (V8, F-20261119-145434-82c05f2). Newtonian/HRNA pipelines against the literature (T1, T2)
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox/20261115T1507Z__to-core__* (input format, pairwise common-horizon trigger, energy diagnostics, two cards or larger blocks), answered in core's dfix-answers (pairwise common horizon done; corrections taken into multi_puncture.md); outbox/20261119T*__to-core__* (tracker files on restart, finder at 4 cells per radius, found flag, damping with three holes)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: newton3/figures (fig_skr_curves, fig_bkrs_and_h1, fig_general_pdis_energy, fig_finite_q, fig_energy_definition, fig_passages), geodesic_binary/figures (s1_sepfrac, s1_vinf), nr_first/figures/fig_baselines_p1.png; note figures fig_newton, fig_geodesic, fig_rp_scan, fig_passage; JSON in newton3/results, geodesic_binary/results, nr_first/results
- [x] **C5** Interface documents
  - status: PASS
  - evidence: multi-puncture input written by newton3/scripts/puncture_input.py per coord/INTERFACES/multi_puncture.md section 2 (F's corrections taken in by core, dfix-answers); reader and wrapper interfaces documented in nr_first/README.md (nrread.py, athena_keep_trackers.sh, tree_check.py)

## Track-specific criteria of F-hills for G1 (9.9 Track F: Hills mechanism (S12))

- [ ] **C6** F-pre-1 and F-pre-2 reproduce the curves of the literature
  - status: FAIL
  - evidence: F-pre-1 met (STATUS.md T1; independent check at seven points within 0.002/0.4 %, two retrograde points within 0.0063/1.2 %). F-pre-2 met for Schwarzschild (2404.16270: separation fraction within 0.0225, v_inf within 0.7 %), NOT for Kerr: 2402.02178's inclined-binary statement not reproduced (OPEN.md item 3)
- [ ] **C7** Constraint residuals and junk radiation of the three-puncture data are quantified
  - status: OPEN
  - evidence: constraints quantified (E2: t = 0 norm 4.7e-5 at m/8 is truncation; corrected data 4.9e-7 = 1/33 of uncorrected; order 7.6-8; F-20261115-173547-a02af7d, -181434-b9c8916; nr_first/figures/fig_c0_constraints.png; card smoke equal, F-20261115-174602-c6879fe). Junk radiation NOT measured: S3/S2 stopped at the slot limit before the pulse reached 30 m; pending P1's spheres (F-20261119-150017-b45ec5f) and S2g (F-20261119-143443-f11ebb9)
- [ ] **C8** One complete vacuum passage is done
  - status: OPEN
  - evidence: P1 at q = 4 (decision 0013) submitted 2026-11-19 as a chain, run F-20261119-150017-b45ec5f, Slurm 4650 (pending), 17-20 card-hours expected; smoke passed its run-health criteria (E7, V8d); predictions in JOURNAL.md (lead wave 2b) and STATUS.md here

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013)
  - status: PASS
  - evidence: followed: P1 and the convergence plan are at q = 4 (nr_first/inputs/p1_q4.athinput; STATUS.md); q = 10 waits for the mesh and for momenta from a GR parabola (V9a: the q = 10 input turns at 5.77 M in GR); the clump passage (object b) follows the first black-hole passage (core's wave-3a clump-table package)

## Minimum figures at G1 (brief 13.4)

- [ ] **C10** Schematic: Updated architecture
  - status: OPEN
  - evidence: not drawn: the G0 architecture schematic (note/figures/schem_architecture.png) predates core-v0.3 and the NR runs of waves 2 and 2b
- [ ] **C11** Schematic: Data-flow diagram
  - status: FAIL
  - evidence: no data-flow diagram exists yet (OPEN.md item 4)
- [x] **C12** Data figure: Baseline results
  - status: PASS
  - evidence: note/figures/fig_newton.png, fig_geodesic.png, fig_rp_scan.png, fig_passage.png (scripts note/scripts/fig_*.py, run F-20261115-180609-abc9f6e); nr_first/figures/fig_baselines_p1.png (F-20261115-174102-ffa764f); all looked at (note/JOURNAL.md; lead review)
- [x] **C13** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: nr_first/figures/fig_test_nrread_synthetic.png (reader test), fig_e10a_s3_s2_compare.png (comparison script on S3/S2), fig_e11_tree_check.png (tree model against restart trees), fig_e3_single_gauge.png (rerun F-20261119-145619-8246322), fig_e7_p1smoke.png; lead fig_review_nr.png (F-20261119-145434-82c05f2); all looked at by the lead (REVIEW-wave2.md). Drawn by the package scripts with python/nrpic/figstyle.py, not yet note figures

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (points to ../REVIEW-wave2.md and SCOPING.md section 10); the criterion-by-criterion text is STATUS.md beside them, the scoping text ../G0/SCOPING.md, both named in the report
- [ ] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: the G0 data figures of the note pass (zoom style, one script each, registered inputs, looked at); the G1 NR figures exist in nr_first/figures with their scripts and runs and were looked at, but are not yet note figures with scripts under note/scripts (OPEN.md item 4)
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS); their G1 updates are C10, C11
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: note v0 (11 pages, checker clean with --compile) covers G0 and the baselines; its G1 sections on the NR runs are not written
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no VERIFIER.md (no subagent tool in this session; the lead does not verify its own package); asked of orch (outbox 20261119T*). Second agent so far: ../G0/SECOND_CHECK.md (plan and baselines)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests and journal entries: F-20261115-173601-2fae2dc (S3/S2, slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a, F-20261119-143851-47595bd, F-20261115-174959-9e8a361 (stopped), F-20261115-174142-2a79515 (superseded), F-20261115-175542-b49d687; failed predictions on record: nr_first/JOURNAL.md (E1(b), E3 items 1, 2, 5, E4 rerun counts, E7 first-search masses), newton3/JOURNAL.md (Q1, Q3, Q4 bounds), stage/G0/JOURNAL.md (SC0d, SC2, SC6), JOURNAL.md (V4-V7 of wave 1)
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of wave 2b (2026-11-19); P1 announced in STATUS before submission
