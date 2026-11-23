# Stage report: D-bh-dress G2

Date: 2026-11-23 · branch `track/D-bh-dress` at `98ce5b8d98c0` · checklist
`tracks/D-bh-dress/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G2-fail-20261123` (created and pushed by the orchestrator after review, decision 0003).

- 14 checklist items not PASS or NA: C1 OPEN, C2 OPEN, C3 OPEN, C5 OPEN, C6 OPEN, C9 OPEN, C10 OPEN, C11 OPEN, C12 OPEN, C13 OPEN, C14 OPEN, C15 OPEN
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | written by this command |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | The section-10 rows D owns (scope/SCOPE.md section 6) are not yet assembled into a G2 ladder table. Available: Einstein-Straus null test (N, entry 5), dust growth against the exact LTB solution (G, entry 5), Newtonian self-similar infall at two resolutions (Q16, Q16-256 D-20261123-020626-183c254), Kerr spike stationarity (G1). Missing: the table itself and the verifier. | OPEN |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Mesh spacing: vacuum and null test at M/8 (D-20261121-203124-a34cf1f, -203131-8ee2a49) and M/16 (D-20261121-203151-37e7b2d; -59c54fb running); the finder mass changes sign between them (H1 failed), so the third member M/4 is queued (entry 6: FV4, FE4). Boundary: faces +-192, +-384, +-768 M compared (V2, E1, F1 of entry 5). Gauge: lapse_leak pair of G1 (ES-1GB/V-1GB). Particle number: none yet for the dust run (ES-FL at one particle count). Growth law at one mesh (ES-FL M/8); ES-FL4 queued. | OPEN |
| C3 | Constraints behave | Volume norms bounded in all five runs (entry 8, D-20261123-021027-e3af9b8, constraints_long.png L), but they integrate the region inside the horizon beyond the chi cut; an exterior norm (region_*) is not in the inputs yet. | OPEN |
| C4 | A first minimal full-GR kinetic run | ES-F (D-20261121-144631-aa7ce9b) and ES-FL (D-20261121-203150-15f2bad, 850724 particles, 500 M): kinetic matter falling into an evolved puncture in full GR; analyses D-20261123-020606-fa0046c, -020614-7ba5874. | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md and OPEN.md written in this session; the package is not complete (C1-C3, C9-C12, C16, C17 open). | OPEN |
| C6 | Reproducibility package | Every run registered with manifests and inputs (g2long/inputs, tools); no consolidated rerun script for G2 yet. | OPEN |
| C7 | In the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor | Criterion N of g2long entry 1 (fixed before the runs): max /D_ES1L - D_V1L/ on 100-500 M = 2.28e-4 against the threshold 2.51e-4 = 2 F_V(500); never above the refutation level 3.76e-4 (judge_long D-20261123-020550-f9a3482, judge_long.png L). At M/16 to 225.6 M the difference follows the M/8 one (H3, partial). Reservation: the margin is 9 per cent, and the floor F_V itself is a resolution-independent step at 240-300 M whose cause is not known. | PASS |
| C8 | With matter filled in, the mass growth agrees with the integrated particle flux through the horizon | Criterion G of g2long entry 1: (iii) every 10 M bin of tau_rem <= 650 M within +-0.62 per cent of the exact LTB mass (61 bins), D2 at all 960 samples (esf_criteria D-20261123-020614-7ba5874, esf_criteria.png L; esf_bracket.png L). Reservations: one mesh spacing and one particle number; D1 closure +9.4e-3 at 500 M (predicted below 8e-3); the step at tau_rem ~ 285 M follows the end of horizon excision at 219 M (entry 5 F4; ES-FLK queued). | PASS |
| C9 | Schematic: Verification ladder | No verification-ladder schematic for G2 yet. | OPEN |
| C10 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | judge_long.png panel (a)-(c) is a two-resolution mesh figure; particle-number and gauge figures missing. | OPEN |
| C11 | Data figure: Constraint norms against time | constraints_long.png (D-20261123-021027-e3af9b8) shows the volume norms against time; exterior norms missing (C3). | OPEN |
| C12 | Data figure: At least one multi-scale slice mosaic with zoom boxes | No slice mosaic of the G2 runs yet. | OPEN |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | CHECKLIST, EVIDENCE, OPEN, STAGE_REPORT present; REVIEW.md not written for G2 (the lead review is stage/REVIEW-wave3.md section 13); scope text scope/SCOPE.md. | OPEN |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | G2 figures so far drawn with figstyle (judge_long, esf_criteria, esf_bracket, esf_growth, constraints_long), each PNG looked at by the lead; not yet in the note. | OPEN |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | The note schematics are those of G1 (note/figures/schem_*); no G2 update. | OPEN |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | Note v2 (note/, 22 pages, checker passed --compile per note/README.md) covers ES-F to 200 M; the long runs are not in it. | OPEN |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | No G2 verifier yet. | OPEN |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions of entry 1 on record in g2long/JOURNAL.md entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2) and of QR3/QR4 in secondary_infall/JOURNAL.md. | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of this session. | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify D-bh-dress G2`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_es.* | note/scripts/fig_es.py | data | to be confirmed by the session |
| note/figures/fig_esf.* | note/scripts/fig_esf.py | data | to be confirmed by the session |
| note/figures/fig_esrun.* | note/scripts/fig_esrun.py | data | to be confirmed by the session |
| note/figures/fig_floor.* | note/scripts/fig_floor.py | data | to be confirmed by the session |
| note/figures/fig_infall.* | note/scripts/fig_infall.py | data | to be confirmed by the session |
| note/figures/fig_kerr.* | note/scripts/fig_kerr.py | data | to be confirmed by the session |
| note/figures/fig_kerr_seeds.* | note/scripts/fig_kerr_seeds.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_q16.* | note/scripts/fig_q16.py | data | to be confirmed by the session |
| note/figures/fig_spike.* | note/scripts/fig_spike.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G2/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `D-20261115-171733-633d422`: stopped (exit -15), G0/G1 verifier C4: own Newtonian radial-shell code, cold secondary infall onto a point seed in EdS with shell crossing, density slope inside r_ta against -9/4 (five variants: N, softening, step, a_f)
- `D-20261115-193755-3a53b08`: superseded (exit 0), lead review wave 2: es_check (independent re-check of helper claims, predictions W1-W4/W7-W9 in JOURNAL.md)
- `D-20261121-075341-6310218`: failed (exit 1), D-pre-3 wave 3 production: Newtonian-mode secondary infall to a/a_i = 30 (nx 192, L 854, dx 8.896 M, edge 1.1, 5e5 dust, clump at a cell centre) on the threaded processor build, 6 threads bound; snapshots every 9.612 M, restart files every 600 M; prediction P in JOURNAL 07:55Z
- `D-20261121-125900-ea4c442`: failed (exit 1), ES-1GB: ES-1G (lapse_leak) with the outer faces at +-384 M; does the late horizon growth go away? predictions g2runs JOURNAL entry 1 (B1-B5)
- `D-20261121-154902-f2724c5`: failed (exit 1), lead batch 4a re-check Y1-Y2: ES-1GB/V-1GB horizons from raw finder summaries, Q16 growth against claims and matched shells, P192 lost particles (no helper code)
- `D-20261121-165420-5d1c245`: failed (exit 1), G1 gate reviewer's own check (predictions P1-P5 in stage/G1/GATE_REVIEW.md, commit 5d1c2455): D-pre-1 quadrature a, m_p; D-pre-4 drift 50->490 M; V-1B floor 100-200 M; Q16 particle count and M_ta at a/a_i = 15.96 by two estimators
- `D-bh-dress-20261115-121837-987643b`: failed (exit 1), Test 1 of D-pre-3: radiation-era turnaround of dark matter around a hole against the printed numbers of 2106.07480 (Table 1, eta_ta) and 1901.08528 (ratios 0.964, 0.999; radial-orbit factor 53 %)
- `D-bh-dress-20261115-122303-4e8e8af`: failed (exit -15), Test 2 of D-pre-3: Bertschinger-type self-similar collisionless infall onto a point-mass seed in Einstein-de Sitter by fixed-point iteration (inner slope, caustics, normalisation against the frozen-in estimate)
- `D-bh-dress-20261115-125449-60a62b8`: failed (exit 1), Analysis of tests 2 and 3 of D-pre-3 and the parameters of the AthenaK runs (closed-form checks, growth of turnaround, dress and hole mass, self-similarity at a/a_i=100, predicted profiles for eps 0.01 and 0.03, capture with angular momentum, cost from the scoping model)
- `D-bh-dress-20261115-125724-464611f`: failed (exit 1), P2a-d analysis of run A: stationarity, invariants, empty loss cone

## Open risks


Updated in the lead session of batch 10a (2026-11-22). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust and keeps its horizon mass under lapse_leak (late growth, decision 0025 item 3: mitigation in v0.7, cure later). 1+log leaves the dust off its exact curve (ES-1) but keeps the hole | certain for lapse_leak | the null test runs with 1+log only | core's cure after the usage reset | all G2 runs plain 1+log (g2long); lapse_leak runs wait for the cure |
| R3 Floor of the null test. Vacuum, 1+log, faces +-768 M: F_V(500) = 1.25e-4 at M/8 (V-1L), 1.34e-4 to 300 M at M/16 (V-1L16), set by a step of +1.2e-4 at 240-300 M that both resolutions show alike (not set at the horizon; cause unknown) | certain (measured) | N holds with a 9 per cent margin only; a floor quoted without its cause | M/4 member FV4 (entry 6 P3) | quote the matched control of each run; find the step's origin before G3 (a run that can fail: faces at +-1536 M, or another mesh layout) |
| R13 Late horizon drift. In vacuum with 1+log it was the outer boundary (V-1 -1.37e-4 after 165 M; gone at +-384 M, V-1B). Under lapse_leak it is not the boundary: ES-1GB (+-384 M) equals ES-1G (+-192 M) to 4.2e-9 up to 188 M; the batch-2a reading is withdrawn. ES-1's (-3.4e-4, 1+log, dust) is untested with far faces | low for vacuum 1+log; certain for lapse_leak (R2) | a gauge or boundary effect read as coupling or accretion | ES-1B | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); far faces protect the exterior mass (ES-1GB: Misner-Sharp mass 2.741 kept on R = 119-223 M) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 Boundary attribution of the D-pre-4 excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) | medium | floor windows limited | none planned | V-1B makes a boundary cause plausible [JUDGEMENT]; D-pre-4 is not the floor of the null test (R3) |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |
| R18 Long runs: the finder kept ES-FL's horizon to 500 M (radius 5.30 M); the queue and the sequencer worked (R1-R4 done, R5 at 225.6 M) | low now | runs late | horizon_summary gaps; `$S/g2long_seq/log` | sequencer restarted for the follow-ups (HANDOFF) |
| R19 Set-up data that do not cover a larger mesh (ES-F table to 345 M, exterior = zero, found by smoke S2) | was certain, fixed for ES-FL | constraint jump inside the domain | smoke runs before every new mesh; the table header line | data maker `--rbar_max`; HANDOFF trap 14 |
| R20 Horizon excision ends when the horizon's smallest radius passes 4 x initial_radius (nrpic.cpp:451-455): in ES-FL at 219 M; afterwards removal by the lapse rule, deeper and later, leaving steps in (iii), D3 and the closure | certain for growing holes | growth criteria biased by the removal time (+0.35 per cent in (iii)) | removal reasons in removed.bin | initial_radius_0 = 1.6 (ES-FLK, entry 6); core request ah-excision-growth-guard |
| R21 The z4c history norms skip chi < 0.0625 and measure the inside of the horizon (M/16 100x below M/8; ES-FL steps) | certain | 'constraints behave' not shown for the exterior | constraints_long.png | `<particles> region_*` outside the horizon in the next inputs |
| R22 The finder mass changes sign between M/8 (+9e-4) and M/16 (-2.5e-4): two members give no order | certain | no convergence statement for M_AH | FV4 P2 | three members (M/4 queued); if M/4 is outside the convergent regime, M/32 on +-3 M (~13 card-hours per run) |

Closed:
- R17 (ES-F's faces at +-192 M and executable): ES-F met every criterion except one early finder sample (g2runs entry 10); ES-FL repeats it at +-768 M.
- R15 (G1 waited on the ruling d-pre-3-criterion): decision 0021 item 2 ruled; C7 judged on that wording with Q16 (batch 4a).
- R1 (release card executable mis-pushes massless tracers): an input convention, m = 0 is a null particle
  (D-20261115-172821-f800e34; core dfix-answers); ES-1 tracers (m = 1e-30) follow the exact curve to 2.2e-3.
- R7 (format-2 reader only on core/id-extrinsic): in release core-v0.3; ES-1/V-1 ran on it.
- R8 (outflow boundary not transparent for the Painleve-Gullstrand exterior): measured, it is (V-1 against
  V-1B); handled by placing the faces at +-384 M (R13) until core's faces option is benchmarked.
- R12 (mixed time zones in run ids): nrun.py uses UTC since 5259f48; nrpic-run writes UTC.

## Decision requested from the group

None requested yet: the G2 package is incomplete (stage/G2/OPEN.md). Both track-specific criteria are met once at M/8 (C7, C8); the general G2 items (three-way convergence, exterior constraints, verifier) are open, and follow-up chains are queued (g2long entry 6).
