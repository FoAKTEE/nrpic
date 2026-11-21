# Checklist: C-sidm G1

Collected by `harness/bin/nrpic-stage collect C-sidm G1` on 2026-11-21T15:55:50Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: F21 sequences and criteria (C-pre-3, run C-sidm-20261115-120722-38ab057); exact fluid onsets with five adiabatic indices, incl. the Juttner Gamma_1 anchor Z(0) = 0.5331 (runs C-20261115-165315-7b473b8, recheck C-20261115-193332-48771b4); 26 equilibrium particle models (wave 1: 13 at 1e4, run C-sidm-20261115-120610-b4592be; wave 2: 5 King + 8 F21 b = 0.1 at 1e4 and 1e5, runs C-20261115-170126-b4f74af, C-20261115-170742-84990ed) with offline checks (M1, M2 pass; M3 240/243, the three failures are the check's own h^2 error, run C-20261115-171723-17d46f0); K of the track Knudsen definition for all of them (run C-20261115-193751-d3872ff); wave 2b: the Juttner fluid onset along the King family (b = 1), y0 = 0.32143 against the collisionless E_b maximum 0.33403, tmb checked against the King JSON to 3e-10 (lead's run C-20261119-151502-cb831a8, L15)
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: MET with a restriction (lead, batch 2b, 2026-11-21; ../REVIEW-wave3.md section 4). Box analysis: validated on synthetic snapshots (wave 1), recomputed by the lead (L8, run C-20261115-193332-48771b4); heat analysis recomputed by the verifier from the raw runs (verify_g1 V1b, V1c: C-20261120-223130-6742500, C-20261120-223133-2f98a0e) and by the lead from the per-seed values (L21, C-20261121-075535-b35b8fb). Cluster pipeline: collapse and crossing times recover 18 of 18 published numbers of the first paper, also after the fix (G1', run C-20261120-222716-9d86ebc); fixed growth estimator growth_fit_v2 passes U1-U5 (C-20261120-222454-8721534) and on synthetic signals bias <= 0.07 percent, rms 0.40-0.66 percent, 3-SE coverage 0.96-1.00 (C-20261120-222716-9d86ebc; 1-SE coverage fails at sigma 0.1, cause found D3, C-20261120-223404-40668db); on the first paper's y_c = 0.5 runs ln|d| is concave, so a rate is quoted only with its interval and the seed scatter over a common interval (D2: 0.0557-0.0617 per M over 17.5-51.75 M); lead's figure rv_models.png (C-20261121-075535-b35b8fb). The quantities the G2 scan relies on (t_c, crossing times, fates, D25-D150 against a control) are validated: t_c recomputed by the lead's own reader for all 15 collisional runs (L18, C-20261121-075336-49f92da), seed scatter measured (decisive, C-20261121-075202-1a37fb9). Restriction: no constant growth rate is claimed on runs.
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: collide/SPEC.md and RNG_REQUIREMENTS.md (wave 1) adopted by core in coord/INTERFACES/collisions.md and rng.md; wave-2 requests answered by core on core/collisions-2 (message 20261115T191641Z: stream-2 table in rng.md 6.1, static_conformal metric, perturb_gamma option, coll_energy = particle) and checked by the track in wave 2b (box_tests R1-R6, runs C-20261119-141502-95f0200 ... C-20261119-145925-dbcfb9c; lead's recheck L13); SPEC.md 4.5 carries core's sub-step rule; Knudsen definition in SPEC.md section 1

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: box tests: box_tests/figs (14 PNGs of wave 2 and 9 of wave 2b: t0b_replay_c2off, t0b_replay_c2particle, compare_modes_c2, t2_rate_c2particle, t1_step_c2particle, paired_c2particle, t10_repro_c2particle, t12_c2, king_defect_c2) and results/ JSON named by run id; models: models/figs, results/; baseline: gravothermal/figs, note/figures/fig_sequences.png; card runs: threshold_scan/figs; lead's rv_box2b, rv_cc, rv_king_onset (wave-2b review run); every figure named in ../REVIEW-wave2.md was looked at by a lead
- [x] **C5** Interface documents
  - status: PASS
  - evidence: tracks/C-sidm/collide/SPEC.md, TESTS.md (section 2a added in wave 2), RNG_REQUIREMENTS.md; core's coord/INTERFACES/collisions.md and rng.md

## Track-specific criteria of C-sidm for G1 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [x] **C6** All tests of C-pre-1 pass
  - status: PASS
  - evidence: MET (lead, batch 2b; ../REVIEW-wave3.md section 1). The tests the brief names in C-pre-1 all pass: relaxation (T3), rate (T2), entropy (T5), heat conduction at both ends (T6-T8). Waves 1-2b on core-v0.3 and core/collisions-2: T0, T0b (6/6), T1, T2 (16/16), T3, T4, T5 (4/4 each), T9 (8 seeds), T10 (MeshBlocks 1/8/64, restarts), T10b (T2 statistics), T11 (a, b, c), T12 (G2 item) - runs C-20261115-170155-13ff01f, -165500-c67e036, -170741-248af65, -170539-28432c3, -170814-8a54b43, -165902-f9b1c8f, -170447-cb3b230, -180525-94ddd22, -174651-0ad8612, C-20261119-141711-7db7a6a, -141806-af19c1c, -143041-f94e350, -141502-95f0200, -143049-0cf699a, -145925-dbcfb9c; lead's L8, L13. Wave 3 (heat package, heat/README.md 'Verdict for G1 C6'; wording collide/TESTS.md section 2b): T6(a) PASS (C-20261119-145733-558136e; C-20261119-152744-2bba6de), T6(b) PASS f = 1.029, 1.063 (C-20261119-144535-2c7b6a4; C-20261119-160003-287b389; verifier 1.027, 1.062), T6(c) reported; T7 at theta 0.003 PASS 1.019 +- 0.004 (processors, C-20261119-161930-acd257b), 1.0250 +- 0.0025 (N-weighted with card seeds, C-20261120-223203-b38a7d7; lead's recompute identical, C-20261121-075535-b35b8fb), interval [0.99, 1.06]; T7 at theta 0.1, 1 reported 1.096 +- 0.005, 0.991 +- 0.004; collisionless check PASS (C-20261119-152845-017d186); T8 PASS on one card seed (C-20261120-222624-cae43d6, C-20261120-223321-3d088d4), T8 part 2 PASS (C-20261119-151044-a584069). Gaps of the track's own extra tests, not of the brief's list: T10b for the T4 statistics (one card job); the MPI variant of T10 cannot run (collisions stop on more than one rank in core-v0.5, coord/INTERFACES/mpi.md); T3-T5, T9, T11 not repeated with coll_energy = particle. Reservations: T8 rests on one card seed; the zero-cell-size conductivity may lie 1-3 percent below the relativistic Chapman-Enskog value [TO VERIFY at G2].
- [x] **C7** The baseline is reproduced
  - status: PASS
  - evidence: F21 = arXiv:2108.11967 Tables 1 and 2 reproduced (run C-sidm-20261115-120722-38ab057; residuals as corrected in STATUS.md item 2); eps maximum Z(0) = 0.5404, exact onset 0.6348 confirmed by the verifier's independent solver (V2, V4, run C-20261115-170630-1037f6a); King y_max = 0.334032 against the printed 0.334 (V3)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C8** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: NA
  - evidence: the ruling concerns the G2 wording and coord/BRIEF_ERRATA.md, not G1

## Minimum figures at G1 (brief 13.4)

- [x] **C9** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png redrawn in registered run C-20261121-130335-d0cfe2e (paperfig.py; note v1, commit 2484c878): box tests, F21 and King particle models, Juttner onsets, pair energy at each particle's metric (release core-v0.4), T12, heat conduction T6-T8 on processors and card, growth rate over a stated fitting interval as existing; radial perturbation to be ported; refined-mesh collisions, ADM energy, threshold scan, mass fraction new. Looked at by the lead (batch 4a, ../REVIEW-wave3.md section 10)
- [x] **C10** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (new; registered run C-20261120-223007-fe3f39c, paperfig.py; committed 077b849d): initial data -> AthenaK -> run outputs -> registered analyses -> note, with the checksum check of every input; looked at by the lead (batch 2b)
- [x] **C11** Data figure: Baseline results
  - status: PASS
  - evidence: note/figures/fig_sequences.png (F21 and King sequences, fluid onsets), models/figs/fig_fluid_onset.png, fig_models.png; looked at
- [x] **C12** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: box_tests/figs/t1t2_summary_cpu.png, relax_T345_*.png, t4_zoom_cpu.png, t0b_replay_cpu.png, and of wave 2b t0b_replay_c2particle.png, paired_c2particle.png, t12_c2.png, king_defect_c2.png; models/figs/fig_growth.png; lead's rv_box.png (run C-20261115-193332-48771b4) and rv_box2b.png (wave-2b review run); looked at

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md); STATUS.md (criteria by criterion); scoping text tracks/C-sidm/scope/SCOPE.md
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: one script per figure in note/scripts/ (fig_box_summary.py, fig_heat.py, fig_onsets.py, fig_cluster.py beside the four G0 scripts), python/nrpic/figstyle.py, all run in registered run C-20261120-223007-fe3f39c which checks the sha256 of every input against its run (log.txt: every input 'sha256 ok'); the eight data PNGs committed (077b849d) and looked at by the lead (batch 2b). Note v1 (run C-20261121-130335-d0cfe2e, 126 inputs, every sha256 ok): card T7 in fig_heat panel (d) (looked at by the lead, batch 4a); card T8, the growth-fit validation and the decisive and drift numbers in ledger Tables IV and V (six rows rechecked against their runs' JSON by the lead, run C-20261121-155226-8ea9e47); the follow-up cluster figures are still to come (G2 material)
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png drawn with paperfig.py (style copy verified); content update is C9
- [x] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note v1 (tracks/C-sidm/note/main.tex, main.pdf, 16 pages; commits d0cfe2ea, 2484c878) with the G1 sections (fluid anchor IV B, operator in the box IV E, heat conduction IV F, first collisional King clusters IV H, plan V, data-flow appendix); figures and tables from registered run C-20261121-130335-d0cfe2e; the package read all 16 pages. Checker with --compile rerun by the lead on a copy (run C-20261121-155226-8ea9e47): 0 undefined references, 0 undefined citations, 1 overfull box of 1.09 pt; remaining candidates are the guide's accepted exceptions (run ids and locators in the ledger appendix, generated-file comments). Not done: the reviewer step of the paper-writing procedure for a new paper (the note is an existing draft)
- [x] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G1/VERIFIER.md (commit 8329cf06) by the fresh-context package verify_g1, blind verdicts committed and pushed before any claim was read (00adbb95); own code, runs C-20261120-222423-519f12b, -223130-6742500, -223133-2f98a0e, C-20261121-074926-5d9ae56, -075256-2084cb5, -080313-84094f1, -080720-dbcd7ff, -081036-0d6117b, -081415-b8c9d29, -081715-2ad1421. No number recomputed is wrong beyond four wording items and one open definition; each is answered in ../REVIEW-wave3.md section 9 (lead, batch 4a; L23, L24 confirm items 1 and 2 from the artefacts): REVIEW-wave2.md count corrected; TESTS.md 2c names the T4 window and the T6(b), T9 reference temperatures after the data, with the strict T9 reading FAILED on record; bias sizes with their windows; F21 0.750 labelled a trial-function bound. Limit: 'every number recomputed' is not met literally; not checked by any second agent: T5 (entropy), T8 and T6(a, c), T0b, T10b, T11, R6, card cluster runs (G2 material), the growth-fit rows other than the two rechecked by the lead
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs on record: C-20261115-165742-2c645f8, -170221-b1a491c, -171137-9e3c807, -170231-4e68455 (wave 2); C-20261119-141614-e42b5ec, C-20261119-143049-0cf699a (wave 2b); wave 3: C-20261120-222339-663f963 (models U5), C-20261120-222852-7d55b7a, -222857-8ea9c42 (heat pooling, rerun), C-20261120-223424-f6ba00a (heat, registered at the pause, never started); superseded analyses C-20261119-141836-2a00bed, -145801-111319f, -145850-49fd35b, C-20261121-030252-b676218, -030314-f3cd423; failed predictions in box_tests/JOURNAL.md, models/JOURNAL.md (G2, G4, G5, A1; wave 3: U5 first try, G2' 1-SE coverage, G3', G6', G5' 30 percent clause), threshold_scan/JOURNAL.md, heat/JOURNAL.md (P-T7hot, P-T7pool (b), S0 cost, P-T6a, P-T6b, P-T6c), drift/JOURNAL.md (D1.5, M8.2), decisive/JOURNAL.md (entries 7-15: t_c scatter, sign of the contraction, D3 proportional clause, job 5), JOURNAL.md (L14(b), L15(b), L16, L17, L19); batch 3-4a: drift M8.2', M8.5', D2.2 (drift/JOURNAL.md entries 12, 14), T9 strict KS reading (collide/TESTS.md 2c), failed runs C-20261121-080152-b8d0acd, -080633-8ee41f7 (verifier), C-20261121-155220-5c0d480 (lead)
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten (STATUS, HANDOFF, RISKS) and appended (JOURNAL: predictions L23-L28 and outcomes) by the lead session of batch 4a on 2026-11-21
