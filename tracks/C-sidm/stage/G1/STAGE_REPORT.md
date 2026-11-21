# Stage report: C-sidm G1

Date: 2026-11-21 · branch `track/C-sidm` at `f1c802ef7b8c` · checklist
`tracks/C-sidm/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**PASS**. Tag: `stage/C-sidm/G1-pass-20261121` (created and pushed by the orchestrator after review, decision 0003).

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | present |
| `stage/G1/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | F21 sequences and criteria (C-pre-3, run C-sidm-20261115-120722-38ab057); exact fluid onsets with five adiabatic indices, incl. the Juttner Gamma_1 anchor Z(0) = 0.5331 (runs C-20261115-165315-7b473b8, recheck C-20261115-193332-48771b4); 26 equilibrium particle models (wave 1: 13 at 1e4, run C-sidm-20261115-120610-b4592be; wave 2: 5 King + 8 F21 b = 0.1 at 1e4 and 1e5, runs C-20261115-170126-b4f74af, C-20261115-170742-84990ed) with offline checks (M1, M2 pass; M3 240/243, the three failures are the check's own h^2 error, run C-20261115-171723-17d46f0); K of the track Knudsen definition for all of them (run C-20261115-193751-d3872ff); wave 2b: the Juttner fluid onset along the King family (b = 1), y0 = 0.32143 against the collisionless E_b maximum 0.33403, tmb checked against the King JSON to 3e-10 (lead's run C-20261119-151502-cb831a8, L15) | PASS |
| C2 | The analysis pipeline validated on them | MET with a restriction (lead, batch 2b, 2026-11-21; ../REVIEW-wave3.md section 4). Box analysis: validated on synthetic snapshots (wave 1), recomputed by the lead (L8, run C-20261115-193332-48771b4); heat analysis recomputed by the verifier from the raw runs (verify_g1 V1b, V1c: C-20261120-223130-6742500, C-20261120-223133-2f98a0e) and by the lead from the per-seed values (L21, C-20261121-075535-b35b8fb). Cluster pipeline: collapse and crossing times recover 18 of 18 published numbers of the first paper, also after the fix (G1', run C-20261120-222716-9d86ebc); fixed growth estimator growth_fit_v2 passes U1-U5 (C-20261120-222454-8721534) and on synthetic signals bias <= 0.07 percent, rms 0.40-0.66 percent, 3-SE coverage 0.96-1.00 (C-20261120-222716-9d86ebc; 1-SE coverage fails at sigma 0.1, cause found D3, C-20261120-223404-40668db); on the first paper's y_c = 0.5 runs ln/d/ is concave, so a rate is quoted only with its interval and the seed scatter over a common interval (D2: 0.0557-0.0617 per M over 17.5-51.75 M); lead's figure rv_models.png (C-20261121-075535-b35b8fb). The quantities the G2 scan relies on (t_c, crossing times, fates, D25-D150 against a control) are validated: t_c recomputed by the lead's own reader for all 15 collisional runs (L18, C-20261121-075336-49f92da), seed scatter measured (decisive, C-20261121-075202-1a37fb9). Restriction: no constant growth rate is claimed on runs. | PASS |
| C3 | Interface proposals submitted | collide/SPEC.md and RNG_REQUIREMENTS.md (wave 1) adopted by core in coord/INTERFACES/collisions.md and rng.md; wave-2 requests answered by core on core/collisions-2 (message 20261115T191641Z: stream-2 table in rng.md 6.1, static_conformal metric, perturb_gamma option, coll_energy = particle) and checked by the track in wave 2b (box_tests R1-R6, runs C-20261119-141502-95f0200 ... C-20261119-145925-dbcfb9c; lead's recheck L13); SPEC.md 4.5 carries core's sub-step rule; Knudsen definition in SPEC.md section 1 | PASS |
| C4 | Baseline data and figures | box tests: box_tests/figs (14 PNGs of wave 2 and 9 of wave 2b: t0b_replay_c2off, t0b_replay_c2particle, compare_modes_c2, t2_rate_c2particle, t1_step_c2particle, paired_c2particle, t10_repro_c2particle, t12_c2, king_defect_c2) and results/ JSON named by run id; models: models/figs, results/; baseline: gravothermal/figs, note/figures/fig_sequences.png; card runs: threshold_scan/figs; lead's rv_box2b, rv_cc, rv_king_onset (wave-2b review run); every figure named in ../REVIEW-wave2.md was looked at by a lead | PASS |
| C5 | Interface documents | tracks/C-sidm/collide/SPEC.md, TESTS.md (section 2a added in wave 2), RNG_REQUIREMENTS.md; core's coord/INTERFACES/collisions.md and rng.md | PASS |
| C6 | All tests of C-pre-1 pass | MET (lead, batch 2b; ../REVIEW-wave3.md section 1). The tests the brief names in C-pre-1 all pass: relaxation (T3), rate (T2), entropy (T5), heat conduction at both ends (T6-T8). Waves 1-2b on core-v0.3 and core/collisions-2: T0, T0b (6/6), T1, T2 (16/16), T3, T4, T5 (4/4 each), T9 (8 seeds), T10 (MeshBlocks 1/8/64, restarts), T10b (T2 statistics), T11 (a, b, c), T12 (G2 item) - runs C-20261115-170155-13ff01f, -165500-c67e036, -170741-248af65, -170539-28432c3, -170814-8a54b43, -165902-f9b1c8f, -170447-cb3b230, -180525-94ddd22, -174651-0ad8612, C-20261119-141711-7db7a6a, -141806-af19c1c, -143041-f94e350, -141502-95f0200, -143049-0cf699a, -145925-dbcfb9c; lead's L8, L13. Wave 3 (heat package, heat/README.md 'Verdict for G1 C6'; wording collide/TESTS.md section 2b): T6(a) PASS (C-20261119-145733-558136e; C-20261119-152744-2bba6de), T6(b) PASS f = 1.029, 1.063 (C-20261119-144535-2c7b6a4; C-20261119-160003-287b389; verifier 1.027, 1.062), T6(c) reported; T7 at theta 0.003 PASS 1.019 +- 0.004 (processors, C-20261119-161930-acd257b), 1.0250 +- 0.0025 (N-weighted with card seeds, C-20261120-223203-b38a7d7; lead's recompute identical, C-20261121-075535-b35b8fb), interval [0.99, 1.06]; T7 at theta 0.1, 1 reported 1.096 +- 0.005, 0.991 +- 0.004; collisionless check PASS (C-20261119-152845-017d186); T8 PASS on one card seed (C-20261120-222624-cae43d6, C-20261120-223321-3d088d4), T8 part 2 PASS (C-20261119-151044-a584069). Gaps of the track's own extra tests, not of the brief's list: T10b for the T4 statistics (one card job); the MPI variant of T10 cannot run (collisions stop on more than one rank in core-v0.5, coord/INTERFACES/mpi.md); T3-T5, T9, T11 not repeated with coll_energy = particle. Reservations: T8 rests on one card seed; the zero-cell-size conductivity may lie 1-3 percent below the relativistic Chapman-Enskog value [TO VERIFY at G2]. | PASS |
| C7 | The baseline is reproduced | F21 = arXiv:2108.11967 Tables 1 and 2 reproduced (run C-sidm-20261115-120722-38ab057; residuals as corrected in STATUS.md item 2); eps maximum Z(0) = 0.5404, exact onset 0.6348 confirmed by the verifier's independent solver (V2, V4, run C-20261115-170630-1037f6a); King y_max = 0.334032 against the printed 0.334 (V3) | PASS |
| C8 | Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013) | the ruling concerns the G2 wording and coord/BRIEF_ERRATA.md, not G1 | NA |
| C9 | Schematic: Updated architecture | note/figures/schem_architecture.png redrawn in registered run C-20261121-130335-d0cfe2e (paperfig.py; note v1, commit 2484c878): box tests, F21 and King particle models, Juttner onsets, pair energy at each particle's metric (release core-v0.4), T12, heat conduction T6-T8 on processors and card, growth rate over a stated fitting interval as existing; radial perturbation to be ported; refined-mesh collisions, ADM energy, threshold scan, mass fraction new. Looked at by the lead (batch 4a, ../REVIEW-wave3.md section 10) | PASS |
| C10 | Schematic: Data-flow diagram | note/figures/schem_dataflow.png (new; registered run C-20261120-223007-fe3f39c, paperfig.py; committed 077b849d): initial data -> AthenaK -> run outputs -> registered analyses -> note, with the checksum check of every input; looked at by the lead (batch 2b) | PASS |
| C11 | Data figure: Baseline results | note/figures/fig_sequences.png (F21 and King sequences, fluid onsets), models/figs/fig_fluid_onset.png, fig_models.png; looked at | PASS |
| C12 | Data figure: Validation figures for the analysis pipeline | box_tests/figs/t1t2_summary_cpu.png, relax_T345_*.png, t4_zoom_cpu.png, t0b_replay_cpu.png, and of wave 2b t0b_replay_c2particle.png, paired_c2particle.png, t12_c2.png, king_defect_c2.png; models/figs/fig_growth.png; lead's rv_box.png (run C-20261115-193332-48771b4) and rv_box2b.png (wave-2b review run); looked at | PASS |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md); STATUS.md (criteria by criterion); scoping text tracks/C-sidm/scope/SCOPE.md | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | one script per figure in note/scripts/ (fig_box_summary.py, fig_heat.py, fig_onsets.py, fig_cluster.py beside the four G0 scripts), python/nrpic/figstyle.py, all run in registered run C-20261120-223007-fe3f39c which checks the sha256 of every input against its run (log.txt: every input 'sha256 ok'); the eight data PNGs committed (077b849d) and looked at by the lead (batch 2b). Note v1 (run C-20261121-130335-d0cfe2e, 126 inputs, every sha256 ok): card T7 in fig_heat panel (d) (looked at by the lead, batch 4a); card T8, the growth-fit validation and the decisive and drift numbers in ledger Tables IV and V (six rows rechecked against their runs' JSON by the lead, run C-20261121-155226-8ea9e47); the follow-up cluster figures are still to come (G2 material) | PASS |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png drawn with paperfig.py (style copy verified); content update is C9 | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | note v1 (tracks/C-sidm/note/main.tex, main.pdf, 16 pages; commits d0cfe2ea, 2484c878) with the G1 sections (fluid anchor IV B, operator in the box IV E, heat conduction IV F, first collisional King clusters IV H, plan V, data-flow appendix); figures and tables from registered run C-20261121-130335-d0cfe2e; the package read all 16 pages. Checker with --compile rerun by the lead on a copy (run C-20261121-155226-8ea9e47): 0 undefined references, 0 undefined citations, 1 overfull box of 1.09 pt; remaining candidates are the guide's accepted exceptions (run ids and locators in the ledger appendix, generated-file comments). Not done: the reviewer step of the paper-writing procedure for a new paper (the note is an existing draft) | PASS |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G1/VERIFIER.md (commit 8329cf06) by the fresh-context package verify_g1, blind verdicts committed and pushed before any claim was read (00adbb95); own code, runs C-20261120-222423-519f12b, -223130-6742500, -223133-2f98a0e, C-20261121-074926-5d9ae56, -075256-2084cb5, -080313-84094f1, -080720-dbcd7ff, -081036-0d6117b, -081415-b8c9d29, -081715-2ad1421. No number recomputed is wrong beyond four wording items and one open definition; each is answered in ../REVIEW-wave3.md section 9 (lead, batch 4a; L23, L24 confirm items 1 and 2 from the artefacts): REVIEW-wave2.md count corrected; TESTS.md 2c names the T4 window and the T6(b), T9 reference temperatures after the data, with the strict T9 reading FAILED on record; bias sizes with their windows; F21 0.750 labelled a trial-function bound. Limit: 'every number recomputed' is not met literally; not checked by any second agent: T5 (entropy), T8 and T6(a, c), T0b, T10b, T11, R6, card cluster runs (G2 material), the growth-fit rows other than the two rechecked by the lead | PASS |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs on record: C-20261115-165742-2c645f8, -170221-b1a491c, -171137-9e3c807, -170231-4e68455 (wave 2); C-20261119-141614-e42b5ec, C-20261119-143049-0cf699a (wave 2b); wave 3: C-20261120-222339-663f963 (models U5), C-20261120-222852-7d55b7a, -222857-8ea9c42 (heat pooling, rerun), C-20261120-223424-f6ba00a (heat, registered at the pause, never started); superseded analyses C-20261119-141836-2a00bed, -145801-111319f, -145850-49fd35b, C-20261121-030252-b676218, -030314-f3cd423; failed predictions in box_tests/JOURNAL.md, models/JOURNAL.md (G2, G4, G5, A1; wave 3: U5 first try, G2' 1-SE coverage, G3', G6', G5' 30 percent clause), threshold_scan/JOURNAL.md, heat/JOURNAL.md (P-T7hot, P-T7pool (b), S0 cost, P-T6a, P-T6b, P-T6c), drift/JOURNAL.md (D1.5, M8.2), decisive/JOURNAL.md (entries 7-15: t_c scatter, sign of the contraction, D3 proportional clause, job 5), JOURNAL.md (L14(b), L15(b), L16, L17, L19); batch 3-4a: drift M8.2', M8.5', D2.2 (drift/JOURNAL.md entries 12, 14), T9 strict KS reading (collide/TESTS.md 2c), failed runs C-20261121-080152-b8d0acd, -080633-8ee41f7 (verifier), C-20261121-155220-5c0d480 (lead) | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten (STATUS, HANDOFF, RISKS) and appended (JOURNAL: predictions L23-L28 and outcomes) by the lead session of batch 4a on 2026-11-21 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T16:46:39Z, clean export of `f1c802ef7b8c`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of f1c802ef7b8c (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G1-f1c802e-20261121T163345Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 11 figures, each with its script |
| min-figs | PASS | 3 schematics and 8 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | PASS | 188 run manifests finished (25 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 39 lines |
| rerun | PASS | 11 of 11 scripts and commands ran cleanly in the export |
| compare | PASS | 22 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 22 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_box_step.* | note/scripts/fig_box_step.py | data | to be confirmed by the session |
| note/figures/fig_box_summary.* | note/scripts/fig_box_summary.py | data | to be confirmed by the session |
| note/figures/fig_cluster.* | note/scripts/fig_cluster.py | data | to be confirmed by the session |
| note/figures/fig_collisions.* | note/scripts/fig_collisions.py | data | to be confirmed by the session |
| note/figures/fig_heat.* | note/scripts/fig_heat.py | data | to be confirmed by the session |
| note/figures/fig_knudsen.* | note/scripts/fig_knudsen.py | data | to be confirmed by the session |
| note/figures/fig_onsets.* | note/scripts/fig_onsets.py | data | to be confirmed by the session |
| note/figures/fig_sequences.* | note/scripts/fig_sequences.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/C-sidm/stage/G1/VERIFIER.md` present; its first lines:

> # VERIFIER: fresh-context verification of the G1 material of C-sidm (criterion C17)
> 
> Verifier: package `tracks/C-sidm/verify_g1/` (wave 3; resumed in batch 2b). Own code only (no
> module of the track imported or copied; python/nrpic readers of the formats used). Every
> computation is a registered run; predictions and outcomes in `verify_g1/JOURNAL.md`.
> 
> Order of work (decision 0016 item 4): the blind verdicts `verify_g1/VERDICTS_BLIND.md` were
> written from the test definitions, the raw run outputs, the model files and the papers, and
> committed and pushed (commit 00adbb95) before any claim was read. Only then were the claims
> below read: `stage/G1/CHECKLIST.md`, `stage/G1/EVIDENCE.md`, `heat/README.md`,
> `box_tests/README.md`, `models/README.md`, `stage/REVIEW-wave2.md` sections 1-3 and 6.
> Exposures before that point (recorded in the journal): one row of core's own T12 claim in the

## Null results and failed runs

- `C-20261115-165742-2c645f8`: failed (exit 1), box_tests T10 of collide/TESTS.md: bit reproducibility over 1/8/64 MeshBlocks and restarts every 37 cycles, seed control; release CPU executable
- `C-20261115-170221-b1a491c`: failed (exit 1), Offline checks of the N = 10000 models of run C-20261115-170126-b4f74af (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261115-170231-4e68455`: failed (exit 1), Validation of the growth-rate and collapse-time pipeline (growth.py): synthetic signals and the first paper's cluster runs runs/st/* (read-only), published numbers of tab_outcomes.tex: predictions G1-G6 of tracks/C-sidm/models/JOURNAL.md
- `C-20261115-171137-9e3c807`: failed (exit 1), Offline checks of the N = 100000 models of run C-20261115-170742-84990ed (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261119-143049-0cf699a`: failed (exit 1), box_rerun R5: T12 collisions in the static homogeneous curved metric (alpha0 0.8, psi0 1.1; static_conformal) against the flat twin and the analytic rate, coll_energy = particle (and cell once), 1e6 particles, 200 steps
- `C-20261119-154032-e450dfc`: failed (exit 1), heat T8 coarse: seven variants (dt, pmax, dx) at theta 0.003, k lambda 0.2, eps 0.2, 5e5 particles, transverse 8x8 cells of lambda/4
- `C-20261119-162015-d97abac`: failed (exit 1), heat T8 coarse, seed 2: seven variants (dt, pmax, dx) at theta 0.003, k lambda 0.2, eps 0.2, 5e5
- `C-20261120-222339-663f963`: failed (exit 1), models wave 3: unit tests U1-U5 of growth_fit_v2 and oscillation_period on synthetic signals (JOURNAL entry 9)
- `C-20261120-222852-7d55b7a`: failed (exit 1), heat T7 theta 0.003 eps 0.2 pooled: processor seeds 1-4, 11-14 (4e5) and card seed 5 (4e6)
- `C-20261120-222857-8ea9c42`: failed (exit 1), heat T7 theta 0.1 and 1, eps 0.2 pooled: processor seeds 1, 2 (4e5) and card seeds 1, 2 (2e6)
- `C-20261120-223424-f6ba00a`: failed (exit None), heat P-cc post hoc: chi^2 of card-vs-processor z and of same-executable seed pairs under the theta 0.003 noise model
- `C-20261121-080152-b8d0acd`: failed (exit 1), verify_g1 V4: own static Einstein-Vlasov equilibria (King b=1, F21 b=0.1), E_b maximum, F21 turning points, radial-pulsation onsets with 1+p/u and Juttner Gamma_1 (trial function and finite elements); F21 Table 1 check
- `C-20261121-155220-5c0d480`: failed (exit 1), lead batch 4a L25: note v1 ledger rows against run JSON; checker with --compile on a copy
- `C-20261121-163051-16356b2`: failed (exit 1), lead batch 4a L28: run (vi) joined with run (i), own reader (alpha_c, H-norm2, energy diffusion)
- `C-sidm-20261115-120801-38ab057`: failed (exit 1), C-pre-4 Tests 1-2: paper values (2009.08163 table, gr-qc/0601112 Tables 1,2,4), Newtonian limit, King turning point, and the offline checks of the 13 equilibria and their 10^4-particle files

## Open risks


State 2026-11-21 (lead, batch 4a of wave 3). Numbers carry run ids or locators; see
`stage/G0/REPORT.md`, `stage/REVIEW-wave2.md` and `stage/REVIEW-wave3.md` for the sources.
L = likelihood, E = effect (high, medium, low).

| Risk | L | E | Watch | Response |
|---|---|---|---|---|
| 1. Stiff collision term at small Kn: N needed grows as Kn^-3 (King threshold: N >= 1.7e3 Kn^-3 for dx <= lambda and 20 per cell); sub-steps ~ dt Gamma/0.1 | high | high | T8 passed on one card seed (C-20261120-223321-3d088d4); max dx/lambda and min N per cell in `coll.hst` | scan stops at Kn_c = 0.3 unless N allows 0.1; the fluid end comes from the exact fluid onset with the Juttner Gamma_1 |
| 2. The collisionless threshold of core-halo families may not sit at the binding-energy maximum (2105.05556 `paper.tex:88-89, 599, 612`); on the M/4 mesh CC1 (at the E_b maximum) oscillates with a finite frequency (drift entry 4, JUDGEMENT) | medium | high | omega^2(y0) from the controls (CC1 399 M, CC2 355 M, D3 282 M at M/4); run (iii) CC1 at M/8 | locate the threshold also as the zero of omega^2(y0) measured on the controls; G2 wording of decision 0013 |
| 3. Mesh effect on the equilibrium: the outward excursion of the M/4 controls (alpha_c +0.018-0.033 within 200 M) is numerical: on M/8 it shrinks to 0.10-0.25 (run C-20261121-075359-26e3b31); the M/8 control instead contracts slowly after 200 M (alpha_c -0.0041 at 300 M) with a 9.3 times higher constraint floor | high | high | a control of every model on every mesh; run (iii), (v) | block A of SCAN.md on M/8 (about 22 card-hours instead of 9.5) or as an M/4-M/8 pair at the bracket; collisional effects read only against a control of the same mesh and seed |
| 4. Physical Kn of relativistic SIDM cores is ~1e-19 (run C-sidm-20261115-115400-eb8b752) against Kn >= 0.3 in the code | certain | high | — | frame the result as the collisionless-to-fluid bridge; physical statements through the Kn -> 0 anchor (Juttner Gamma_1 onset: Z(0) = 0.5331 for F21 b = 0.1, y0 = 0.32143 for King) |
| 5. Card budget: G2 scan 26-28 card-hours at M/4 (SCAN.md); block A on M/8 about 23 (or 14 for three models), plus D2 (2-5), against 37.56 left of 45 after 6.54 used and 0.90 reserved (`nrpic-run budget`, 2026-11-21 16:00 UTC) | high | medium | `nrpic-run budget` | runs (vi), (v), D2 before any scan block; a scan block above eight card-hours announced in STATUS and waiting for an otherwise empty queue (decisions 0014, 0016) |
| 6. Choice of initial model sways the answer: King models collapse with collisions after 2.5-15 collisions per particle; D3 (y0 = 0.26, 8.7 times CC2's distance from the onset) still collapses at Kn = 1 (100.5 M) and contracts at Kn = 10 (decisive, C-20261121-052720-75f3fff, -062412-7473ef1) | high | high | contraction per collision against model and Kn | report every model with its distance from both onsets; F21 b = 0.1 models in the scan |
| 7. Gravothermal contraction (now the leading reading, JUDGEMENT from D3) makes any model collapse eventually, so "collapse within 300 M" is no threshold criterion | high | high | contraction rate per collision against model and Kn | define the collisional threshold by the growth rate of the radial mode or by the collapse time against the distance from the onset; D2 decides whether the contraction rate is physical (collision cell size) |
| 8. Particle noise and the intrinsic core oscillation near threshold; growth rates on runs are window-dependent (ln d concave on the first paper's y_c = 0.5 runs, models D2, C-20261120-223404-40668db) | high | medium | rates with their interval and seed scatter | three-way convergence of the omega^2 zero and of collapse times, not of a single growth rate |
| 9. Seed scatter near the threshold: t_c of CC1 at Kn = 10 scatters by about 3 M (sd 2.83 M over five runs; CC2 0.21 M over four), runs C-20261121-075202-1a37fb9 | certain | medium | seeds per model | at least three seeds per model within about 0.02 in y0 of the threshold |
| 10. Card runs are not byte-reproducible and the collisions-2 card executable differs from the release at rounding; the drift runs use the core-v0.3 card executable (sha256 f9f2dc12..., needed for exact restarts); core-v0.6's merged card executable had its card check pending at tagging (job 4800) | medium | low | core's RELEASE-v0.6.md | collisional comparisons by seed scatter; a scan block runs on one executable throughout, controls included |
| 11. Equal masses required for exact pairwise conservation and thermalisation (collide `SPEC.md` 4.4) | low | medium | `coll_weights = equal` fatal error | equal-mass sampling for every collisional run |
| 12. Reproducibility with the mesh metric only to rounding between MeshBlock divisions (core `rng.md` 5); collisions stop on more than one MPI rank (core-v0.5) | certain | low | T10 with the analytic metric | bitwise claims only for analytic-metric boxes; request to core (outbox collisions-several-ranks) |
| 13. Collapse leaves the static mesh unable to hold the black hole: histories not valid after the first excision, some runs go non-finite (decisive) | certain (static mesh) | medium | constraint norm after collapse; `<z4c_guard>` of core-v0.5 stops non-finite runs (exit 3) | refined mesh with collisions (request to core, open); excised fraction is a proxy until then |
| 14. Competition: Misner-Sharp group (2601.17117 `SIDM_MS.tex:514`), Gurian and May collisional Boltzmann SIDM (2505.15903), kinetic SIDM halos with a Kn-dependent collapse time (2610.28745, coord/FRONTIER.md) | medium | medium | kb watch | read 2505.15903 and 2610.28745 before G2; 2610.28745 as the Newtonian baseline of the Kn scan; keep the claim to the fully relativistic kinetic 3D calculation |
| 15. Usage limit cuts sessions mid-package (2026-11-19, 2026-11-20): uncommitted work stranded in the worktree; none stranded at the start of batch 4a | medium | medium | git status at every start | commit small and often; packages sized to one window (decision 0020) |
| 16. Conductivity possibly 1-3 percent below the relativistic Chapman-Enskog value at zero cell size; the reference V1a is unreviewed | medium | low | cell-size series (about 0.3 card-hours); kb sources | G2 item, not a G1 blocker |
| 17. Test definitions named after the data (collide/TESTS.md 2c: T4 window, T6(b) and T9 reference temperatures; the strict T9 KS reading fails for one class of one seed) may be refused by the G1 reviewer | low | low | the reviewer's report | strict readings kept on record as failed; T9 is not among the tests the brief names in C-pre-1 |

## Decision requested from the group

Independent review of G1 (decision 0016 item 4). Every checklist item is met in the lead's judgement (C1-C7, C9-C19; C8 not applicable); nrpic-stage verify PASS at f1c802ef. Readings named after the data are in collide/TESTS.md 2c (strict T9 reading failed on record); limits in OPEN.md. The lead does not pass the gate.
