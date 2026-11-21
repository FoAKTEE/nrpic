# Stage report: D-bh-dress G1

Date: 2026-11-21 · branch `track/D-bh-dress` at `0cb321d64787` · checklist
`tracks/D-bh-dress/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G1-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C7 OPEN, C16 OPEN
- verify ran on 9182d4d; files changed since: coord/DECISIONS/0020-size-batches-to-the-five-hour-window.md, harness/workflows/batch-2a.json, harness/workflows/batch-2b.json, harness/workflows/make_batch.py, tracks/D-bh-dress/HANDOFF.md, tracks/D-bh-dress/JOURNAL.md (run verify again)
- verify reported FAIL: clean, sync, runs, compare

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
| C1 | Baseline results obtainable without the NRPIC coupling | G1/STATUS.md rows D-pre-1..4 | PASS |
| C2 | The analysis pipeline validated on them | D-pre-2 (binning, invariants, crossing times; lead recheck D-20261115-193844-df4523c), D-pre-3 (masses; lead's own implementation D-20261115-193823-88f7f86), D-pre-4 (finder re-search); Einstein-Straus pipeline on AthenaK output of ES-1/V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b; analysis D-20261119-141839-8686bd7, -142929-bb375ff; lead Y1-Y6 D-20261119-151039-b2ce968) and of ES-1G (D-20261119-142633-6f72922; analysis D-20261120-221754-ae3dafe, -222424-230f936; lead Z1-Z2 D-20261121-063617-3f2036f: horizon, wall 1.68e-4, crossings, proper time reproduced to the printed digits); fresh verifier V1 reproduced the ES-1/V-1 numbers (stage/G1/VERIFIER.md). Vacuum-bubble floor at M/8 with the faces at +-384 M: 4.8e-5 over 100-200 M (V-1B D-20261120-222625-63abd72, lead Z3); that is G2 material | PASS |
| C3 | Interface proposals submitted | outbox/20261115T1510Z__to-core__*.md (8); core answered 6 (core/requests-adf outbox dfix-answers; scratch/core/exe/core_requests-adf/READY items 1-5) | PASS |
| C4 | Baseline data and figures | G0/EVIDENCE.md | PASS |
| C5 | Interface documents | D's specifications (outbox accretion-diagnostics, analytic-metric-excision, newtonian-mode-point-mass, tracer rule) are documented as options by core: core/requests-adf tracks/core/interfaces/REQUESTS_ADF.md and READY; D has no interface document of its own | PASS |
| C6 | Derivation and offline check of D-pre-1 | einstein_straus/DERIVATION.md; runs -042626-f3da881, -042704-f3da881, -043406-4df1e76 | PASS |
| C7 | The baselines of D-pre-2 and D-pre-3 | D-pre-2 MET: equatorial Kerr reference confirmed by the fresh verifier (V3: constant f 0.85/0.88 per cent, Hernquist a = 0 1.67 per cent, a = 0.8 peak 4.5 per cent below FdRW with the gap in FdRW's curve [JUDGEMENT]); AthenaK stationarity confirmed (V4); axis curve NOT CONFIRMED. D-pre-3: growth MET (M_ta within 0.3 per cent of the kernel shells at a/a_i = 2, 4, 8; dress within 1.1 per cent from a/a_i = 3, 0.5-3.3 per cent at 2: verifier V2, lead Z4 D-20261121-063617-3f2036f); profile about 25 per cent from the self-similar solution at a/a_i = 8, sensitive to r_ta; the criterion as written (r^-9/4) fails for an exact code: ruling d-pre-3-criterion open at orch since 2026-11-15, or the run to a/a_i = 30 (secondary_infall, design and references done, production run not started) | OPEN |
| C8 | The noise floor of D-pre-4 | puncture_drift; runs -121313/-121314-284ec4f, -130954-49ed46f; lead re-check -145546-5259f48 | PASS |
| C9 | Schematic: Updated architecture | note/figures/schem_architecture.png redrawn (run D-20261120-222429-026731f; P10 of note/JOURNAL.md): exists / provided by core / new for Track D, core's wave-2 capabilities (tracers on timelike orbits, removal record, flux spheres, analytic excision, Newtonian point mass, relaxed lapse, threaded build) and the run chain; looked at by the lead (../REVIEW-wave3.md section 6) | PASS |
| C10 | Schematic: Data-flow diagram | note/figures/schem_architecture.png is drawn as the data flow: initial data -> evolution in AthenaK -> analysis against references -> deliverables (run D-bh-dress-20261115-171627-18706fb) | PASS |
| C11 | Data figure: Baseline results | spike/figs/ref_*.png, kerr_ref_*.png, secondary_infall/figs/nm_*.png, puncture_drift/figs/drift_*.png, note/figures/fig_*.png | PASS |
| C12 | Data figure: Validation figures for the analysis pipeline | spike/figs/stationarity_*.png, kerr_main_*.png, slice_control.png; secondary_infall/figs/nm_field.png, nm_clumpstab.png; einstein_straus/figs/code_t0.png; puncture_drift/figs/drift_finder.png; lead: stage/review_wave2 figures (runs D-20261115-193819-df9f812 ... -193844-df4523c) | PASS |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, 2026-11-21), EVIDENCE.md, OPEN.md, CHECKLIST.md, VERIFIER.md (fresh verifier, 2026-11-21), REVIEW.md (-> ../REVIEW-wave2.md sections 1-3, 6, 8 and ../REVIEW-wave3.md), STATUS.md (the G1 criteria one by one); scoping text scope/SCOPE.md | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | all package figures from registered runs with figstyle/czstyle, one script each; looked at by their makers; lead looked at the key ones (REVIEW-wave2.md) | PASS |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py, schem_timeline.py (paperfig.py) | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | note v0 (main.pdf, 2026-11-15) passed check_manuscript.py --compile (0 undefined, 0 overfull); the v1 text and figures (commit c2e0571d; runs D-20261120-222413-4a67fa2 ... -223535-24f7f90) are committed but the PDF was not rebuilt and the checker not rerun on them (package note cut on 2026-11-20; P11-P12 open) | OPEN |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G1/VERIFIER.md (copy of verifier_g1/VERIFIER.md, helper verifier_g1, fresh context, verdicts committed in 102d696b before any review was read): V1-V6, 34 ledger rows agree, no row WRONG; WRONG as worded: dress at a/a_i = 2 (corrected in STATUS.md); NOT CONFIRMED: Hernquist axis curve, eight ledger rows; the track's action on each item: ../REVIEW-wave3.md section 2. Runs D-20261120-222209-871e07f, D-20261121-031031-e23da04, -031711-0d79cb3, -033209-9c0bd44, -034048-17427b0, -035106-0c619ee, -040417-8a3c402, -035114-8a3cb38, -040636-e8d5352, -040826-9d5051a (verify PASS) | PASS |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs kept: -121837-987643b, -122303-4e8e8af, -125449-60a62b8, -125724-464611f, -171733-633d422 (stopped); superseded: D-20261115-170326-dfb2a02, -193755-3a53b08, D-20261119-151012-b4afa8a, and the verifier's reference counts of D-20261121-034048-17427b0, -035106-0c619ee, -040417-8a3c402; refuted predictions in the journals (es_runs entries 1-3, 4-7, and entry 9: G2 failed, G6 refuted, J5, K1, K2 refuted; spike K1-K3; secondary_infall wave 2; note P4-P6; flux_tools entry 6b: momentum residual and growth-summary predictions; drift_controls A2 asphericity, pre-flight C1 at 3.1e-8 against 1e-8; the verifier's own V4 error, recorded) | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of batch 2a (2026-11-21) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T07:07:14Z, clean export of `9182d4dddadd`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 3 uncommitted paths: commit them first (tracks/D-bh-dress/drift_controls/tools/compare_runs.py, tracks/D-bh-dress/drift_controls/tools/count_blocks.py, tracks/D-bh-dress/drift_controls/tools/slice_profiles.py) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 9182d4dddadd (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G1-9182d4d-20261121T064019Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | WARN | note/main.pdf is older than the last change of its .tex files |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 10 figures, each with its script |
| min-figs | PASS | 2 schematics and 8 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 3 of 188 runs have problems; 3 waived |
| runs-waived | WARN | failures of the manifest check waived: 3 hand-written manifests of waves 1 and 2 listed in EVIDENCE.md (decision 0016 item 3) |
| run-notes | WARN | 100 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 10 of 10 scripts and commands ran cleanly in the export |
| compare | FAIL | 28 regenerated files compared with the committed ones; 1 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 20 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_es.* | note/scripts/fig_es.py | data | to be confirmed by the session |
| note/figures/fig_esrun.* | note/scripts/fig_esrun.py | data | to be confirmed by the session |
| note/figures/fig_floor.* | note/scripts/fig_floor.py | data | to be confirmed by the session |
| note/figures/fig_infall.* | note/scripts/fig_infall.py | data | to be confirmed by the session |
| note/figures/fig_kerr.* | note/scripts/fig_kerr.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_spike.* | note/scripts/fig_spike.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/D-bh-dress/stage/G1/VERIFIER.md` present; its first lines:

> # Verifier report: Track D (D-bh-dress), gate G1, checklist item C17
> 
> Verifier: helper `verifier_g1` of D-bh-dress, wave 3, 2026-11-20 (fresh context; I produced
> none of the material). Package: `tracks/D-bh-dress/verifier_g1/` (scripts, `JOURNAL.md`
> with every prediction written before its run and every outcome, `README.md` with how to
> rerun). All my runs are processor analyses registered with `harness/bin/nrpic-run`, 0
> card-hours. Before these verdicts were committed I did not read `stage/**`, the track's
> `JOURNAL.md`, `STATUS.md`, `HANDOFF.md`, `RISKS.md`, `PLAN-wave3.md`, `analysis/lead_checks/`,
> or any package's `JOURNAL.md`. The note was read only at commit 78d470ca.
> 
> Verdicts: CONFIRMED = recomputed with my own code and an attempt to break it failed;
> NOT CONFIRMED = not checked (reason given); WRONG = with evidence. Qualified verdicts say

## Null results and failed runs

- `D-20261115-171733-633d422`: stopped (exit -15), G0/G1 verifier C4: own Newtonian radial-shell code, cold secondary infall onto a point seed in EdS with shell crossing, density slope inside r_ta against -9/4 (five variants: N, softening, step, a_f)
- `D-20261115-193755-3a53b08`: superseded (exit 0), lead review wave 2: es_check (independent re-check of helper claims, predictions W1-W4/W7-W9 in JOURNAL.md)
- `D-bh-dress-20261115-121837-987643b`: failed (exit 1), Test 1 of D-pre-3: radiation-era turnaround of dark matter around a hole against the printed numbers of 2106.07480 (Table 1, eta_ta) and 1901.08528 (ratios 0.964, 0.999; radial-orbit factor 53 %)
- `D-bh-dress-20261115-122303-4e8e8af`: failed (exit -15), Test 2 of D-pre-3: Bertschinger-type self-similar collisionless infall onto a point-mass seed in Einstein-de Sitter by fixed-point iteration (inner slope, caustics, normalisation against the frozen-in estimate)
- `D-bh-dress-20261115-125449-60a62b8`: failed (exit 1), Analysis of tests 2 and 3 of D-pre-3 and the parameters of the AthenaK runs (closed-form checks, growth of turnaround, dress and hole mass, self-similarity at a/a_i=100, predicted profiles for eps 0.01 and 0.03, capture with angular momentum, cost from the scoping model)
- `D-bh-dress-20261115-125724-464611f`: failed (exit 1), P2a-d analysis of run A: stationarity, invariants, empty loss cone

## Open risks


Updated in the lead session of batch 2a (2026-11-21). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust. 1+log leaves the dust (ES-1). core's lapse_leak (ES-1G, D-20261119-142633-6f72922) slices the dust on its exact curve (wall within 1.7e-4, dust lapse within 1.3e-2 of the model) but at the hole the horizon shrinks to 0.78 M (6.2 cells of M/8) and its mass grows by +7.0e-3 over 100-200 M | dust part retired by ES-1G; hole part open | the null test with matter has no gauge yet that holds both the dust and the hole | ES-1G with the faces at +-384 M; V-1G; M/16 nest | lapse_leak for G2 runs only with the faces at +-384 M, an M/16 nest and a matched V-1G control (es_runs README "Gauge for the null test"); question to core (outbox es1g-outcome-for-gauge-ready) |
| R3 Floor of the null test in the ES set-up. Now measured in vacuum: V-1B (faces at +-384 M, M/8, 1+log) within 4.8e-5 over 100-200 M (D-20261120-222625-63abd72); with dust and lapse_leak not measured | medium | a floor quoted for the wrong gauge or mesh | V-1G with the faces at +-384 M | quote the floor of the matched control of each G2 run, never one of another set-up |
| R13 Late horizon drift. V-1's (-1.37e-4 after 165 M) is the outer boundary at +-192 M: gone with the faces at +-384 M (V-1B, lead Z3). ES-1's (-3.4e-4) and ES-1G's (+7.0e-3, with the exterior mass lost from the faces inward, es_runs K1) are likely the same, not tested | low for vacuum, medium with dust | a boundary effect read as coupling or accretion | ES-1GB (ES-1G with faces at +-384 M) | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); core's faces option benchmarked on V-1 (outbox boundary-benchmark-v1b) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) | medium | floor windows limited | none planned | V-1B makes a boundary cause plausible [JUDGEMENT]; D-pre-4 is not the floor of the null test (R3) |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R15 G1 waits on orch's ruling `d-pre-3-criterion` (asked 2026-11-15, 11-19, 11-21) | certain | G1 not reviewable | coord/REQUESTS.md | if the wording stays: secondary_infall's run to a/a_i = 30 on processors (0.4-0.8 h); even then -9/4 is not reachable (profile resolved only to lambda ~ 0.06) |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |

Closed:
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R8 (outflow boundary not transparent for the Painleve-Gullstrand exterior): measured, it is (V-1 against
  V-1B); handled by placing the faces at +-384 M (R13) until core's faces option is benchmarked.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.

## Decision requested from the group

None yet: G1 is NOT met and the package is not complete for review. Open: C7 (orch's ruling on the D-pre-3 criterion, proposal of 2026-11-15, asked a third time on 2026-11-21; or the Newtonian-mode run to a/a_i = 30) and C16 (working note v1 committed but not compiled or checked). Closed since 2026-11-19: C9 (schematic redrawn, run D-20261120-222429-026731f) and C17 (fresh-context verifier, VERIFIER.md). The failed automated checks: 'clean' = three untracked tools of the unfinished package drift_controls; 'sync' = main moved during the 25-minute verify (merged right after, 0cb321d6); 'runs' = three wave-2 runs (D-20261115-170002-8cefc3e, -170326-dfb2a02, -193755-3a53b08) with outputs outside their sha256sums.txt (waiver requested); 'compare' = note/figures/fig_newton_numbers.json not refreshed after a change of fig_newton.py (note package, open).
