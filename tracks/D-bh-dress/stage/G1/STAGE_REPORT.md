# Stage report: D-bh-dress G1

Date: 2026-11-19 · branch `track/D-bh-dress` at `b7777f441e37` · checklist
`tracks/D-bh-dress/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G1-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 3 checklist items not PASS or NA: C7 OPEN, C9 OPEN, C17 OPEN
- verify reported FAIL: runs
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
| C1 | Baseline results obtainable without the NRPIC coupling | G1/STATUS.md rows D-pre-1..4 | PASS |
| C2 | The analysis pipeline validated on them | D-pre-2 (binning, invariants, crossing times; lead recheck D-20261115-193844-df4523c), D-pre-3 (masses; lead's own implementation D-20261115-193823-88f7f86), D-pre-4 (finder re-search); Einstein-Straus pipeline on AthenaK output of ES-1/V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b): wall tracers on the exact curve to 2.2e-3 for tau <= 200 M, crossings of R = 2M to 6e-4 and 5.6e-3 M, horizon mass against the matched control (analysis D-20261119-141839-8686bd7, -142929-bb375ff); reproduced by the lead's independent code, Y1-Y6 held (D-20261119-151039-b2ce968; ../REVIEW-wave2.md section 6). The null-test floor in the ES set-up is not yet stated (late common drift after 165 M, cause open): that is G2 work | PASS |
| C3 | Interface proposals submitted | outbox/20261115T1510Z__to-core__*.md (8); core answered 6 (core/requests-adf outbox dfix-answers; scratch/core/exe/core_requests-adf/READY items 1-5) | PASS |
| C4 | Baseline data and figures | G0/EVIDENCE.md | PASS |
| C5 | Interface documents | D's specifications (outbox accretion-diagnostics, analytic-metric-excision, newtonian-mode-point-mass, tracer rule) are documented as options by core: core/requests-adf tracks/core/interfaces/REQUESTS_ADF.md and READY; D has no interface document of its own | PASS |
| C6 | Derivation and offline check of D-pre-1 | einstein_straus/DERIVATION.md; runs -042626-f3da881, -042704-f3da881, -043406-4df1e76 | PASS |
| C7 | The baselines of D-pre-2 and D-pre-3 | D-pre-2 met (Schwarzschild and Kerr reference, AthenaK stationarity a = 0 and 0.8; Hernquist Kerr 4 per cent below FdRW, TO VERIFY); D-pre-3: growth of the dress met in AthenaK's Newtonian mode (0.1-0.5 per cent against matched shells); the profile criterion as written (r^-9/4, slope -9/4 +- 0.05) fails for an exact code (verifier C4): restatement proposed to orch (outbox) | OPEN |
| C8 | The noise floor of D-pre-4 | puncture_drift; runs -121313/-121314-284ec4f, -130954-49ed46f; lead re-check -145546-5259f48 | PASS |
| C9 | Schematic: Updated architecture | note/figures/schem_architecture.png (wave 2) predates core's wave-2 executables (tracer rule, accretion diagnostics, analytic excision, Newtonian point mass on core/requests-adf; lapse_leak on core/gauge) and the ES-1/V-1/ES-1G chain: to be redrawn (not done in wave 2b) | OPEN |
| C10 | Schematic: Data-flow diagram | note/figures/schem_architecture.png is drawn as the data flow: initial data -> evolution in AthenaK -> analysis against references -> deliverables (run D-bh-dress-20261115-171627-18706fb) | PASS |
| C11 | Data figure: Baseline results | spike/figs/ref_*.png, kerr_ref_*.png, secondary_infall/figs/nm_*.png, puncture_drift/figs/drift_*.png, note/figures/fig_*.png | PASS |
| C12 | Data figure: Validation figures for the analysis pipeline | spike/figs/stationarity_*.png, kerr_main_*.png, slice_control.png; secondary_infall/figs/nm_field.png, nm_clumpstab.png; einstein_straus/figs/code_t0.png; puncture_drift/figs/drift_finder.png; lead: stage/review_wave2 figures (runs D-20261115-193819-df9f812 ... -193844-df4523c) | PASS |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, 2026-11-19), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (-> ../REVIEW-wave2.md sections 1-3, 6, 8), STATUS.md (the G1 criteria one by one); scoping text scope/SCOPE.md | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | all package figures from registered runs with figstyle/czstyle, one script each; looked at by their makers; lead looked at the key ones (REVIEW-wave2.md) | PASS |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py, schem_timeline.py (paperfig.py) | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | note/main.pdf; check_manuscript.py --compile: 0 undefined, 0 overfull; 2 of 16 checks with candidates only in the ledger appendix and registration scripts | PASS |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no fresh-context verifier of the G1 material yet (decision 0016 item 4: a verifier of later material belongs to G1); ../G0/VERIFIER.md covers the plan and the wave-1 baselines; the wave-2 baselines (Kerr spike, Newtonian mode) and the ES-1/V-1 outcome were rechecked by the leads with the helpers' reports in hand (../REVIEW-wave2.md), which does not count as fresh context; requested from orch (outbox 2026-11-19) | OPEN |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs kept: -121837-987643b, -122303-4e8e8af, -125449-60a62b8, -125724-464611f, -171733-633d422 (stopped); superseded: D-20261115-170326-dfb2a02, -193755-3a53b08, D-20261119-151012-b4afa8a; refuted predictions in the journals (es_runs entries 1-3; entries 4-7 of wave 2b: the 3e-5 drift, ES-1 within V-1's floor, the +1.5e-3 horizon level, the 1+log plateau model A2 and prediction 4, A3's lapse minimum, the boundary hypothesis E2 and its probe tests; spike K1-K3, secondary_infall wave 2, note P4-P6) | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of wave 2b (2026-11-19); the wave-2 lead was cut off before rewriting them | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:44:55Z, clean export of `b7777f441e37`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of b7777f441e37 (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G1-b7777f4-20261119T154350Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 1 of 153 runs have problems; 3 waived |
| runs-waived | WARN | 3 hand-written manifests of waves 1 and 2 listed in EVIDENCE.md: failures of the manifest check waived (decision 0016 item 3) |
| run-notes | WARN | 97 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 19 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_es.* | note/scripts/fig_es.py | data | to be confirmed by the session |
| note/figures/fig_floor.* | note/scripts/fig_floor.py | data | to be confirmed by the session |
| note/figures/fig_infall.* | note/scripts/fig_infall.py | data | to be confirmed by the session |
| note/figures/fig_spike.* | note/scripts/fig_spike.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G1/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `D-20261115-171733-633d422`: stopped (exit -15), G0/G1 verifier C4: own Newtonian radial-shell code, cold secondary infall onto a point seed in EdS with shell crossing, density slope inside r_ta against -9/4 (five variants: N, softening, step, a_f)
- `D-20261115-193755-3a53b08`: superseded (exit 0), lead review wave 2: es_check (independent re-check of helper claims, predictions W1-W4/W7-W9 in JOURNAL.md)
- `D-bh-dress-20261115-121837-987643b`: failed (exit 1), Test 1 of D-pre-3: radiation-era turnaround of dark matter around a hole against the printed numbers of 2106.07480 (Table 1, eta_ta) and 1901.08528 (ratios 0.964, 0.999; radial-orbit factor 53 %)
- `D-bh-dress-20261115-122303-4e8e8af`: failed (exit -15), Test 2 of D-pre-3: Bertschinger-type self-similar collisionless infall onto a point-mass seed in Einstein-de Sitter by fixed-point iteration (inner slope, caustics, normalisation against the frozen-in estimate)
- `D-bh-dress-20261115-125449-60a62b8`: failed (exit 1), Analysis of tests 2 and 3 of D-pre-3 and the parameters of the AthenaK runs (closed-form checks, growth of turnaround, dress and hole mass, self-similarity at a/a_i=100, predicted profiles for eps 0.01 and 0.03, capture with angular momentum, cost from the scoping model)
- `D-bh-dress-20261115-125724-464611f`: failed (exit 1), P2a-d analysis of run A: stationarity, invariants, empty loss cone

## Open risks


Updated in the lead session of wave 2b (2026-11-19). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust. Measured in ES-1 (1+log, D-20261115-172726-60ba4c2): K at the plateau tracer falls to 0.1-0.2 of -3H within 30-40 M and changes sign at 40-90 M, the lapse settles at 1.3-1.4 out to the boundary, the dust ages 280 M by t = 200 M; a lapse pulse from the dust moves the horizon mass by up to 3e-4 during t = 25-50 M | certain for 1+log; open for lapse_leak | the null test in expanding dust is not defined by 1+log; transients at the hole | ES-1G (D-20261119-142633-6f72922): G1-G3 of es_runs/JOURNAL.md entry 5 | core's lapse_leak (core_gauge); outbox lapse-for-expanding-dust and es-outcome-and-gauge-ready |
| R3 The floor of the null test in the ES set-up is not the D-pre-4 floor. V-1 on the ES mesh: 4.2e-5 over 100-165 M, 1.4e-4 over 100-200 M (D-20261119-151039-b2ce968), against 2.8e-5 for D-pre-4 | certain | a floor quoted too low | V-1 and its controls | floor stated only after R13 is explained, from t0 after the step at t ~ 30 M |
| R13 Common late drift of the horizon mass after t ~ 165 M in ES-1 and V-1 (to -3.4e-4 and -1.4e-4 at 200 M) and late axis/diagonal split of the tracer errors (from tau ~ 130 M); the boundary hypothesis failed its probe tests (D-20261119-143413-bce5e71, -143444-8a9949c) | certain (seen), cause unknown | the null-test window ends near 165 M at M/8; a slicing or finder effect would bias G2 | V-1 controls | V-1 with the boundary at 384 M, then V-1 at M/16 near the hole (lead's decision, after ES-1G) |
| R14 Lapse excision idle: the mesh minimum of the lapse rose above alpha_exc = 0.05 near t = 6 and 15 M in ES-1/V-1 | certain under 1+log | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8; check in ES-1G and ES-F |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) untested | medium | floor windows limited | boundary control | joins R13: the V-1 run with the boundary at 384 M |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools, wave 3a) is the first matter run into the hole |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R8 Outer boundary with K_ij ~ r^(-3/2) (Painleve-Gullstrand exterior): outflow is not transparent | medium | reflections reach the hole | R13 controls | boundary at 384 M; core request (lapse-for-expanding-dust, boundary part) |
| R9 Cost: G2 ladder priced about ten times too low beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (ES-1 0.769, V-1 0.672 card-hours for 200 M on 344 blocks); 25.4 of 30 card-hours left |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr) | medium | misleading wording | wording review | SCOPE.md 3.5-3.6 wording; second-agent review requested |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R15 G1 waits on others: a fresh-context verifier (0016 item 4) and orch's ruling on the D-pre-3 criterion | certain | G1 not reviewable | outbox g1-verifier-and-rulings | if the wording stays: Newtonian-mode run to a/a_i = 30-100 (two to four card-hours [JUDGEMENT]) |
| R16 Shared worktree: a wave-3a helper (flux_tools) commits in this worktree beside the lead; a wave-2b helper removed a directory through a shell-variable path | medium | index conflicts; rule breaks | git status before each commit | path-limited commits; rule repeated in HANDOFF traps |

Closed:
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.

## Decision requested from the group

None yet: G1 is NOT met and the package is not complete for review. Open: C7 (orch's ruling on the D-pre-3 criterion, proposal of 2026-11-15), C9 (architecture schematic), C17 (a fresh-context verifier of the G1 material, decision 0016 item 4; requested from orch in outbox 20261119T152700Z). The failed automated check 'runs' is the queued ES-1G run (status submitted).
