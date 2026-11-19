# Checklist: C-sidm G1

Collected by `harness/bin/nrpic-stage collect C-sidm G1` on 2026-11-15T19:39:53Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: F21 sequences and criteria (C-pre-3, run C-sidm-20261115-120722-38ab057); exact fluid onsets with five adiabatic indices, incl. the Juttner Gamma_1 anchor Z(0) = 0.5331 (runs C-20261115-165315-7b473b8, recheck C-20261115-193332-48771b4); 26 equilibrium particle models (wave 1: 13 at 1e4, run C-sidm-20261115-120610-b4592be; wave 2: 5 King + 8 F21 b = 0.1 at 1e4 and 1e5, runs C-20261115-170126-b4f74af, C-20261115-170742-84990ed) with offline checks (M1, M2 pass; M3 240/243, the three failures are the check's own h^2 error, run C-20261115-171723-17d46f0); K of the track Knudsen definition for all of them (run C-20261115-193751-d3872ff)
- [ ] **C2** The analysis pipeline validated on them
  - status: OPEN
  - evidence: partly met. Box analysis: validated on synthetic snapshots (wave 1) and used on the box tests, recomputed independently by the lead (L8, run C-20261115-193332-48771b4). Cluster pipeline growth.py: collapse and crossing times recover 18 of 18 published numbers of the first paper (run C-20261115-170346-298a1ba, rerun identical in C-20261115-193332-48771b4); the growth-rate fit FAILED its synthetic-signal test G2 (bias +2-4 percent, coverage 0.58-0.90; cause found D1, run C-20261115-170713-cefe1c2) and G4; the fix is tested on synthetic signals only. Open: the fixed fit on runs (OPEN.md item 3)
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: collide/SPEC.md and RNG_REQUIREMENTS.md (wave 1) adopted by core in coord/INTERFACES/collisions.md and rng.md; wave-2 requests answered by core (message 20261115T191641Z: stream-2 table in rng.md 6.1, static curved metric, perturbation option, energy correction coll_energy = particle); SPEC.md 4.5 now carries core's sub-step rule; Knudsen definition in SPEC.md section 1

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: box tests: box_tests/figs (14 PNGs) and results/ JSON of 18 runs; models: models/figs, results/; baseline: gravothermal/figs, note/figures/fig_sequences.png; card runs: threshold_scan/figs; every figure named in ../REVIEW-wave2.md was looked at by the lead
- [x] **C5** Interface documents
  - status: PASS
  - evidence: tracks/C-sidm/collide/SPEC.md, TESTS.md (section 2a added in wave 2), RNG_REQUIREMENTS.md; core's coord/INTERFACES/collisions.md and rng.md

## Track-specific criteria of C-sidm for G1 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [ ] **C6** All tests of C-pre-1 pass
  - status: OPEN
  - evidence: NOT MET. Run and passed on core-v0.3 (processors; card for T10b): T0 (wave 1), T0b (6/6), T1 (16 + 4 + 2 runs, incl. 1e4 steps), T2 (16/16), T3, T4, T5 (4/4 each), T9 (8 seeds), T10 (MeshBlocks 1/8/64, restarts; no MPI build), T10b (T2 statistics), T11 (a, b, c) - runs C-20261115-170155-13ff01f, -165500-c67e036, -170741-248af65, -170539-28432c3, -170814-8a54b43, -165902-f9b1c8f, -170447-cb3b230, -180525-94ddd22, -174651-0ad8612; recomputed independently by the lead (L8). Not run: T6, T7, T8 (heat conduction at the long and short mean-free-path ends, named in C-pre-1; card runs), the MPI variant of T10, T10b for T4. T12 belongs to G2 (TESTS.md)
- [x] **C7** The baseline is reproduced
  - status: PASS
  - evidence: F21 = arXiv:2108.11967 Tables 1 and 2 reproduced (run C-sidm-20261115-120722-38ab057; residuals as corrected in STATUS.md item 2); eps maximum Z(0) = 0.5404, exact onset 0.6348 confirmed by the verifier's independent solver (V2, V4, run C-20261115-170630-1037f6a); King y_max = 0.334032 against the printed 0.334 (V3)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C8** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: NA
  - evidence: the ruling concerns the G2 wording and coord/BRIEF_ERRATA.md, not G1

## Minimum figures at G1 (brief 13.4)

- [ ] **C9** Schematic: Updated architecture
  - status: OPEN
  - evidence: the architecture schematic of wave 2 (note/figures/schem_architecture.png) predates the box tests, the F21 particle models and the Juttner onset; to be redrawn with their new state
- [ ] **C10** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: no data-flow diagram drawn yet (particle files and tables -> AthenaK -> histories, snapshots, dumps -> analysis)
- [x] **C11** Data figure: Baseline results
  - status: PASS
  - evidence: note/figures/fig_sequences.png (F21 and King sequences, fluid onsets), models/figs/fig_fluid_onset.png, fig_models.png; looked at
- [x] **C12** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: box_tests/figs/t1t2_summary_cpu.png, relax_T345_*.png, t4_zoom_cpu.png, t0b_replay_cpu.png; models/figs/fig_growth.png; lead's rv_box.png (run C-20261115-193332-48771b4); looked at

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md); STATUS.md (criteria by criterion); scoping text tracks/C-sidm/scope/SCOPE.md
- [ ] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: the G1 data figures are the helper packages' figures (python/nrpic/figstyle.py, several figures per script: box_tests/scripts/figures.py, models/figures.py); one-script-per-figure versions in note/scripts/ for the G1 figures are not made yet
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png drawn with paperfig.py (style copy verified); content update is C9
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: working note v0 (G0) passed the checker with --compile; it does not yet contain the G1 results (box tests, models, Juttner anchor, card runs)
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no fresh-context verifier of the G1 material (box tests, models); the lead's recheck (../REVIEW-wave2.md, L8-L12) is not that check
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs on record: C-20261115-165742-2c645f8, -170221-b1a491c, -171137-9e3c807, -170231-4e68455; failed predictions in box_tests/JOURNAL.md, models/JOURNAL.md, threshold_scan/JOURNAL.md, JOURNAL.md
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of the wave-2 lead session
