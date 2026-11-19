# Stage report: C-sidm G1

Date: 2026-11-19 · branch `track/C-sidm` at `589237c86781` · checklist
`tracks/C-sidm/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/C-sidm/G1-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 7 checklist items not PASS or NA: C2 OPEN, C6 OPEN, C9 OPEN, C10 OPEN, C14 OPEN, C16 OPEN, C17 OPEN
- verify ran on 53b1391; files changed since: coord/DECISIONS/0018-usage-pause.md, harness/bin/nrpic-usage, tracks/C-sidm/stage/G0/VERIFY_RESULTS.json, tracks/C-sidm/stage/G0/VERIFY_RESULTS.md (run verify again)
- verify reported FAIL: clean, sync, runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | written by this command |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G1/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | F21 sequences and criteria (C-pre-3, run C-sidm-20261115-120722-38ab057); exact fluid onsets with five adiabatic indices, incl. the Juttner Gamma_1 anchor Z(0) = 0.5331 (runs C-20261115-165315-7b473b8, recheck C-20261115-193332-48771b4); 26 equilibrium particle models (wave 1: 13 at 1e4, run C-sidm-20261115-120610-b4592be; wave 2: 5 King + 8 F21 b = 0.1 at 1e4 and 1e5, runs C-20261115-170126-b4f74af, C-20261115-170742-84990ed) with offline checks (M1, M2 pass; M3 240/243, the three failures are the check's own h^2 error, run C-20261115-171723-17d46f0); K of the track Knudsen definition for all of them (run C-20261115-193751-d3872ff); wave 2b: the Juttner fluid onset along the King family (b = 1), y0 = 0.32143 against the collisionless E_b maximum 0.33403, tmb checked against the King JSON to 3e-10 (lead's run C-20261119-151502-cb831a8, L15) | PASS |
| C2 | The analysis pipeline validated on them | partly met. Box analysis: validated on synthetic snapshots (wave 1) and used on the box tests, recomputed independently by the lead (L8, run C-20261115-193332-48771b4). Cluster pipeline growth.py: collapse and crossing times recover 18 of 18 published numbers of the first paper (run C-20261115-170346-298a1ba, rerun identical in C-20261115-193332-48771b4); the growth-rate fit FAILED its synthetic-signal test G2 (bias +2-4 percent, coverage 0.58-0.90; cause found D1, run C-20261115-170713-cefe1c2) and G4; the fix is tested on synthetic signals only. Open: the fixed fit on runs (OPEN.md item 3) | OPEN |
| C3 | Interface proposals submitted | collide/SPEC.md and RNG_REQUIREMENTS.md (wave 1) adopted by core in coord/INTERFACES/collisions.md and rng.md; wave-2 requests answered by core on core/collisions-2 (message 20261115T191641Z: stream-2 table in rng.md 6.1, static_conformal metric, perturb_gamma option, coll_energy = particle) and checked by the track in wave 2b (box_tests R1-R6, runs C-20261119-141502-95f0200 ... C-20261119-145925-dbcfb9c; lead's recheck L13); SPEC.md 4.5 carries core's sub-step rule; Knudsen definition in SPEC.md section 1 | PASS |
| C4 | Baseline data and figures | box tests: box_tests/figs (14 PNGs of wave 2 and 9 of wave 2b: t0b_replay_c2off, t0b_replay_c2particle, compare_modes_c2, t2_rate_c2particle, t1_step_c2particle, paired_c2particle, t10_repro_c2particle, t12_c2, king_defect_c2) and results/ JSON named by run id; models: models/figs, results/; baseline: gravothermal/figs, note/figures/fig_sequences.png; card runs: threshold_scan/figs; lead's rv_box2b, rv_cc, rv_king_onset (wave-2b review run); every figure named in ../REVIEW-wave2.md was looked at by a lead | PASS |
| C5 | Interface documents | tracks/C-sidm/collide/SPEC.md, TESTS.md (section 2a added in wave 2), RNG_REQUIREMENTS.md; core's coord/INTERFACES/collisions.md and rng.md | PASS |
| C6 | All tests of C-pre-1 pass | NOT MET (T6-T8 missing). Run and passed on core-v0.3 (processors; card for T10b): T0 (wave 1), T0b (6/6), T1 (16 + 4 + 2 runs, incl. 1e4 steps), T2 (16/16), T3, T4, T5 (4/4 each), T9 (8 seeds), T10 (MeshBlocks 1/8/64, restarts; no MPI build), T10b (T2 statistics), T11 (a, b, c) - runs C-20261115-170155-13ff01f, -165500-c67e036, -170741-248af65, -170539-28432c3, -170814-8a54b43, -165902-f9b1c8f, -170447-cb3b230, -180525-94ddd22, -174651-0ad8612; recomputed by the lead (L8). Wave 2b, on core/collisions-2 with coll_energy = particle: T0b 6/6 (C-20261119-141711-7db7a6a), T1 and T2 16/16 with counts identical to the release in every step (C-20261119-141806-af19c1c), T10 (C-20261119-143041-f94e350), option absent byte-identical to the release (C-20261119-141502-95f0200), and T12 (G2 item) in the static homogeneous metric (C-20261119-143049-0cf699a, analysis C-20261119-145925-dbcfb9c); recomputed by the lead (L13, ../REVIEW-wave2.md section 6). Not run: T6, T7, T8 (heat conduction at the long and short mean-free-path ends, named in C-pre-1): in progress in package heat/ (wave-3a helper; processor runs and two card jobs C-20261119-150335-73fd40f, C-20261119-150347-e100007 pending on 2026-11-19); the MPI variant of T10 (no MPI build); T10b for T4; T3-T5, T9, T11 not repeated with coll_energy = particle | OPEN |
| C7 | The baseline is reproduced | F21 = arXiv:2108.11967 Tables 1 and 2 reproduced (run C-sidm-20261115-120722-38ab057; residuals as corrected in STATUS.md item 2); eps maximum Z(0) = 0.5404, exact onset 0.6348 confirmed by the verifier's independent solver (V2, V4, run C-20261115-170630-1037f6a); King y_max = 0.334032 against the printed 0.334 (V3) | PASS |
| C8 | Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013) | the ruling concerns the G2 wording and coord/BRIEF_ERRATA.md, not G1 | NA |
| C9 | Schematic: Updated architecture | the architecture schematic of wave 2 (note/figures/schem_architecture.png) predates the box tests, the F21 particle models and the Juttner onset; to be redrawn with their new state | OPEN |
| C10 | Schematic: Data-flow diagram | no data-flow diagram drawn yet (particle files and tables -> AthenaK -> histories, snapshots, dumps -> analysis) | OPEN |
| C11 | Data figure: Baseline results | note/figures/fig_sequences.png (F21 and King sequences, fluid onsets), models/figs/fig_fluid_onset.png, fig_models.png; looked at | PASS |
| C12 | Data figure: Validation figures for the analysis pipeline | box_tests/figs/t1t2_summary_cpu.png, relax_T345_*.png, t4_zoom_cpu.png, t0b_replay_cpu.png, and of wave 2b t0b_replay_c2particle.png, paired_c2particle.png, t12_c2.png, king_defect_c2.png; models/figs/fig_growth.png; lead's rv_box.png (run C-20261115-193332-48771b4) and rv_box2b.png (wave-2b review run); looked at | PASS |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md); STATUS.md (criteria by criterion); scoping text tracks/C-sidm/scope/SCOPE.md | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | the G1 data figures are the helper packages' figures (python/nrpic/figstyle.py, several figures per script: box_tests/scripts/figures.py, models/figures.py); one-script-per-figure versions in note/scripts/ for the G1 figures are not made yet | OPEN |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png drawn with paperfig.py (style copy verified); content update is C9 | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | working note v0 (G0) passed the checker with --compile; it does not yet contain the G1 results (box tests, models, Juttner anchor, card runs) | OPEN |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no fresh-context verifier of the G1 material yet (decision 0016 item 4 puts a verifier of the later material in G1): box tests of waves 2 and 2b, models, Juttner anchor, King onset. The leads' rechecks (../REVIEW-wave2.md, L8-L15) are not that check. Owner: the next wave (a verifier helper given the artefacts) | OPEN |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs on record: C-20261115-165742-2c645f8, -170221-b1a491c, -171137-9e3c807, -170231-4e68455 (wave 2); C-20261119-141614-e42b5ec (all six AthenaK runs exit 1, relative deck path; manifest says completed because the driver exited 0) and C-20261119-143049-0cf699a (T12 driver crashed on the figure after writing its JSON) (wave 2b); superseded analyses C-20261119-141836-2a00bed, -145801-111319f, -145850-49fd35b; failed predictions in box_tests/JOURNAL.md (T4 seed 2; wave 2b R3(iv) positions, R3(v') cost 1.68 > 1.5, R6(a) column 30), models/JOURNAL.md (G2, G4, G5, A1), threshold_scan/JOURNAL.md (P3.4, P3.7, P3.8, P3.10, P3.11, Test 4), JOURNAL.md | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | the wave-2 lead was cut off before rewriting them; rewritten (STATUS, HANDOFF, RISKS) and appended (JOURNAL, predictions and outcomes L12-L15) by the wave-2b lead session on 2026-11-19 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:44:10Z, clean export of `53b13916e214`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 2 uncommitted paths: commit them first (tracks/C-sidm/stage/G0/VERIFY_RESULTS.json, tracks/C-sidm/stage/G0/VERIFY_RESULTS.md) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 53b13916e214 (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G1-53b1391-20261119T154332Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 6 of 106 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_box_step.* | note/scripts/fig_box_step.py | data | to be confirmed by the session |
| note/figures/fig_collisions.* | note/scripts/fig_collisions.py | data | to be confirmed by the session |
| note/figures/fig_knudsen.* | note/scripts/fig_knudsen.py | data | to be confirmed by the session |
| note/figures/fig_sequences.* | note/scripts/fig_sequences.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G1/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `C-20261115-165742-2c645f8`: failed (exit 1), box_tests T10 of collide/TESTS.md: bit reproducibility over 1/8/64 MeshBlocks and restarts every 37 cycles, seed control; release CPU executable
- `C-20261115-170221-b1a491c`: failed (exit 1), Offline checks of the N = 10000 models of run C-20261115-170126-b4f74af (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261115-170231-4e68455`: failed (exit 1), Validation of the growth-rate and collapse-time pipeline (growth.py): synthetic signals and the first paper's cluster runs runs/st/* (read-only), published numbers of tab_outcomes.tex: predictions G1-G6 of tracks/C-sidm/models/JOURNAL.md
- `C-20261115-171137-9e3c807`: failed (exit 1), Offline checks of the N = 100000 models of run C-20261115-170742-84990ed (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261119-143049-0cf699a`: failed (exit 1), box_rerun R5: T12 collisions in the static homogeneous curved metric (alpha0 0.8, psi0 1.1; static_conformal) against the flat twin and the analytic rate, coll_energy = particle (and cell once), 1e6 particles, 200 steps
- `C-sidm-20261115-120801-38ab057`: failed (exit 1), C-pre-4 Tests 1-2: paper values (2009.08163 table, gr-qc/0601112 Tables 1,2,4), Newtonian limit, King turning point, and the offline checks of the 13 equilibria and their 10^4-particle files

## Open risks


State 2026-11-19 (lead, wave 2b). Numbers carry run ids or locators; see
`stage/G0/REPORT.md` and `stage/REVIEW-wave2.md` for the sources. L = likelihood, E = effect
(high, medium, low).

| Risk | L | E | Watch | Response |
|---|---|---|---|---|
| 1. Stiff collision term at small Kn: N needed grows as Kn^-3 (King threshold: N >= 1.7e3 Kn^-3 for dx <= lambda and 20 per cell); sub-steps ~ dt Gamma/0.1 | high | high | T8 convergence (heat package); max dx/lambda and min N per cell in `coll.hst` | scan stops at Kn_c = 0.3 unless N allows 0.1; the fluid end comes from the exact fluid onset with the Juttner Gamma_1 |
| 2. The collisionless threshold of core-halo families may not sit at the binding-energy maximum (2105.05556 `paper.tex:88-89, 599, 612`) | medium | high | growth rate against Z(0) over 0.4-1.0, both perturbation signs, 1000 M runs | eps_max (Z(0) = 0.5404 at b = 0.1) is a lower bound; G2 wording of decision 0013 |
| 3. The numerical equilibrium drifts more than the stability margin: collisionless King controls on the M/4 mesh move alpha_c by +0.018-0.033 within 200 M (run C-20261115-191420-8538aa4), larger than CC2's distance from the fluid onset (0.0055) and the CC1-CC2 separation (0.0148) (L15) | high (on this mesh) | high | controls of every scan; drift against mesh spacing (run D2) | D2 with one more refinement level and `coll_cell_factor = 2`; read collisional effects relative to a control of the same seed and mesh |
| 4. Physical Kn of relativistic SIDM cores is ~1e-19 (run C-sidm-20261115-115400-eb8b752) against Kn >= 0.3 in the code | certain | high | — | frame the result as the collisionless-to-fluid bridge; physical statements through the Kn -> 0 anchor (Juttner Gamma_1 onset: Z(0) = 0.5331 for F21 b = 0.1, y0 = 0.32143 for King) |
| 5. Card budget: G2 scan 26-28 card-hours (SCAN.md) plus D1-D3 (4-8) against 41.4 left of 45 to the next gate; heat jobs reserve 1.84 | medium | medium | `nrpic-run budget` | D1 first (smallest), scan blocks only after D1-D3 decide the mesh and defect questions |
| 6. Choice of initial model sways the answer: King b = 1 models near the threshold collapse with collisions after 2.5-15 collisions per particle (runs C-20261115-171058-c26cfad ...); F21 b = 0.1 untested in a run | medium | high | relative contraction against the control; distance of each model from both onsets | report every model with its distance from the collisionless and fluid onsets; D3 with a model clearly on the stable side |
| 7. Gravothermal contraction (leading hypothesis for the collisional collapses, JUDGEMENT) makes any King model collapse eventually, so "collapse within 300 M" is no threshold criterion | medium | high | contraction rate per collision against model and Kn | define the collisional threshold by the growth rate of the radial mode or by the time to collapse against the distance from the onset, not by collapse within a fixed time |
| 8. Particle noise and the intrinsic core oscillation near threshold (first paper `tab_outcomes.tex:120`) | high | medium | growth-rate fits over several periods; N = 1e4/1e5/1e6 | three-way convergence of the growth-rate zero, not of a collapse time; growth-rate fit fix still to validate (G1 OPEN item 3) |
| 9. Single seed and non-reproducible card runs: the seed scatter of a collapse time is unmeasured | certain (now) | medium | two seeds in D1 | every collisional comparison with at least two seeds |
| 10. Card executable of core/collisions-2 not shown equivalent to the processor one (CARD_TESTS.log FAIL lines, job 4484) | medium | medium | core's statement (outbox card-tests-collisions-2) | no new collisional card run with it before the statement; the heat card jobs count only after it |
| 11. Equal masses required for exact pairwise conservation and thermalisation (collide `SPEC.md` 4.4) | low | medium | `coll_weights = equal` fatal error | equal-mass sampling for every collisional run |
| 12. Reproducibility with the mesh metric only to rounding between MeshBlock divisions (core `rng.md` 5) | certain | low | T10 with the analytic metric | bitwise claims only for analytic-metric boxes |
| 13. Collapse leaves the static M/4 mesh unable to hold the black hole (non-finite state, exit 0) | certain (static mesh) | medium | constraint norm after collapse | refined mesh with collisions (request to core); excised fraction is a proxy until then |
| 14. Competition: Misner-Sharp group (2601.17117 `SIDM_MS.tex:514`), Gurian and May collisional Boltzmann SIDM (arXiv:2505.15903, fetched, not read) | medium | medium | kb watch | read 2505.15903 before G2; keep the claim to the fully relativistic kinetic 3D calculation |
| 15. One owner allotment of 16 cores shared by two workflows: the lead's analyses wait behind helpers' long runs (wave 2b) | high | low | `nrpic-run` refusals | request to orch (lead core share); run short analyses between helper runs |

## Decision requested from the group

No pass is requested for G1 of C-sidm: G1 is NOT MET because the heat-conduction tests T6-T8 of C-pre-1 have not finished (wave-3a heat helper, processor runs and two queued card jobs on 2026-11-19). Every other test of C-pre-1 passes on core-v0.3 and, with coll_energy = particle, on core/collisions-2, recomputed by the lead (REVIEW-wave2.md sections 1 and 6); the baseline is reproduced. Also open: the growth-rate fit validated on runs, the G1 schematics and data-flow diagram, the note's G1 sections and a verifier of the G1 material (OPEN.md). Record the state; the next lead resubmits when T6-T8 pass. Verify FAILs on 53b13916 are sync (one main commit merged afterwards) and runs (six live runs of the heat helper), not G1 products.
