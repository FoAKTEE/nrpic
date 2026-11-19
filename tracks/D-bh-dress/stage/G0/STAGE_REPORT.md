# Stage report: D-bh-dress G0

Date: 2026-11-19 · branch `track/D-bh-dress` at `b7777f441e37` · checklist
`tracks/D-bh-dress/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G0-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- verify reported FAIL: runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/VERIFIER.md` (verifier's report) | present |
| `stage/G0/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |
| `stage/G0/REPORT.md` | written in wave 1, accepted as it is (decision 0012) |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | REPORT.md sections 1-4; scope/SCOPE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | scope/REFERENCES.md (18 sources, locators); REPORT.md section 5 (re-read by the lead) | PASS |
| C3 | Risk list | REPORT.md section 6; RISKS.md; scope/SCOPE.md section 8 | PASS |
| C4 | Compute estimate | REPORT.md section 7; runs D-bh-dress-20261115-120304-795eee9, -145950-23fa1c7 | PASS |
| C5 | Working note v0 | note/main.tex, note/main.pdf (REVTeX, 10 pages; figures and tables of run D-bh-dress-20261115-171627-18706fb); lead: clean compile and ledger rerun byte for byte, run D-20261115-193951-be7b41d; lapse sentence corrected (REVIEW-wave2 section 4) | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (note/scripts/schem_architecture.py, run D-bh-dress-20261115-171627-18706fb); looked at by the lead (note p. 2) | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (note/scripts/schem_timeline.py, run D-bh-dress-20261115-171627-18706fb); text in REPORT.md section 8 | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet has no G0-specific criterion | NA |
| C9 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png (exists / to be ported / new), run D-bh-dress-20261115-171627-18706fb | PASS |
| C10 | Schematic: Stage timeline | note/figures/schem_timeline.png, run D-bh-dress-20261115-171627-18706fb | PASS |
| C11 | Data figure: None required | none required | NA |
| C12 | Data figure: Data from the literature may be redrawn | optional | NA |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (-> ../REVIEW-wave2.md); scoping text scope/SCOPE.md; REPORT.md of wave 1 kept (decision 0012) | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | scope/figs/scoping_estimates.png (run D-bh-dress-20261115-120304-795eee9, figstyle); note/figures/fig_*.png (five, czstyle, one script each, run D-bh-dress-20261115-171627-18706fb); verifier figures stage/G0/figs/*.png; looked at (lead: fig pages 1-3 of the note, v2_drift, v4b_compare) | PASS |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py, schem_timeline.py with the vendored paperfig.py (unchanged copy of harness/style/) | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing guide and notation (WRITING_GUIDE.md, NOTATION.md); check_manuscript.py --compile after the lead's fix: 0 undefined references or citations, 0 overfull boxes; 2 of 16 checks have candidates, all in the ledger appendix (run ids) and the registration scripts, which the guide exempts | PASS |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G0/VERIFIER.md (fresh-context verifier of the plan, decision 0016 items 1 and 4: eight claims recomputed from the artefacts; runs D-20261115-170002-8cefc3e, -170224-924d1d9, -171508-94e8cb1, -171532-ba23a99, -171534-ff5b0e9, -171543-d966aba, -171545-d7e01a7, -171953-908afff, -171818-a5aefe8, -173149-7c6dd72); its WRONG (C8 cost) and NOT CONFIRMED (C4 criterion) items with what the track does: ../REVIEW-wave2.md sections 5 and 8; the note's numbers recomputed by note/tables/claims.md (36) and rerun byte for byte by the lead (D-20261115-193951-be7b41d) | PASS |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs kept (EVIDENCE.md); refuted predictions in JOURNAL.md, es_runs/JOURNAL.md, spike/JOURNAL.md, secondary_infall/JOURNAL.md, note/JOURNAL.md, stage/G0/JOURNAL.md; superseded runs D-20261115-170326-dfb2a02, -171733-633d422, -193755-3a53b08 | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of wave 2b (2026-11-19); the wave-2 lead was cut off before rewriting them | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:44:55Z, clean export of `b7777f441e37`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of b7777f441e37 (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G0-b7777f4-20261119T154350Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 1 of 153 runs have problems |
| run-notes | WARN | 97 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 8 of 8 scripts and commands ran cleanly in the export |
| compare | PASS | 23 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
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

`tracks/D-bh-dress/stage/G0/VERIFIER.md` present; its first lines:

> # Independent verification of the G0 and G1 material of Track D (wave 2)
> 
> Verifier: a helper of D-bh-dress that produced none of the material checked, working as a
> fresh reader. Read first: `scope/SCOPE.md` (the scoping text; it names the claims),
> `einstein_straus/DERIVATION.md`, the test scripts and inputs, and the raw outputs under
> `scratch/D-bh-dress/`. The track's summaries (STATUS, HANDOFF, JOURNALs, stage reports,
> `analysis/lead_checks/`) were read only after the verdicts below were written (section 3).
> Predictions and outcomes, including the failed ones: `JOURNAL.md` in this directory. Every
> number below carries a run id; my runs are listed in `README.md`. Labels as in the brief.
> 
> Verdicts: **CONFIRMED** (recomputed independently, rerun, and an attempt to break it did
> not), **NOT CONFIRMED** (what could not be checked and why), **WRONG** (with the evidence).

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

Review of G0 by the orchestrator (decision 0016 item 4). Every checklist item is PASS or NA; the verifier's report on the plan is VERIFIER.md (0016 item 1), its WRONG and NOT CONFIRMED items are answered in ../REVIEW-wave2.md sections 5 and 8. The only failed automated check is 'runs': ES-1G (D-20261119-142633-6f72922) is queued on the cards (status submitted), a G1/G2 run in flight, not G0 material. Output checksums: this verify ran with --no-checksums; nrpic-run verify passed for ES-1, V-1 and every wave-2b analysis run in this session (REVIEW-wave2.md section 9) and for 51 wave-2 runs in wave 2. The lead does not pass the gate.

## Lead's note on the verdict (wave 2b)

The generated verdict FAIL has one cause: `verify` fails the check `runs` because ES-1G
(D-20261119-142633-6f72922, a G1/G2 card run) is queued with status `submitted`. Every
checklist item is PASS or NA, the verifier's report on the plan is `VERIFIER.md`
(decision 0016 items 1 and 4), and the other checks of `verify` pass on commit b7777f44
(run with `--no-checksums`; output checksums: `nrpic-run verify` PASS for ES-1, V-1 and every
wave-2b run in this session, `../REVIEW-wave2.md` section 9). The package is complete for the
orchestrator's review; the lead does not pass the gate. The wave-2 helper drafts that stood
here ("Products of the note package", "Draft for Decision requested") were carried into
`CHECKLIST.md` in wave 2 and are removed.
