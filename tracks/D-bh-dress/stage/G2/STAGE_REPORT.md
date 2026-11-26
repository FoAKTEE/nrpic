# Stage report: D-bh-dress G2

Date: 2026-11-26 · branch `track/D-bh-dress` at `332692691262` · checklist
`tracks/D-bh-dress/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/D-bh-dress/G2-fail-20261126` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C17 OPEN
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | present |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | Ladder table stage/G2/LADDER.md (rows D owns: Einstein-Straus null test N at M/8 and M/16, converged-finder re-search FP; self-similar infall Q16/Q16-256; D's growth criterion G) and schematic D-20261124-175505-a1053fa. Null test N holds at M/8 (judge_long D-20261123-020550-f9a3482: 2.28e-4 against 2.51e-4) and M/16 (1.99e-4, D-20261124-131138-0b8ffc5); converged finder <= 7.3e-5 (fp_analyse D-20261124-172508-c847ee4). Growth criterion G holds at N/4, N, 4N (D-20261126-054616-a13a888, D-20261125-115647-fd2f3f7, D-20261125-122827-c5735f8) and at M/8, M/16 with own-mesh controls (D-20261123-020614-7ba5874, D-20261126-055158-30ae09c). On record as failed with its ruling: P5 (M/4 null test fails by a factor 20, judge_conv D-20261125-122227-3eb563a; decision 0039 item 4: M/4 outside the convergent regime, labelled so). every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e). All G2 runs slice with plain 1+log (decision 0025 item 3; OPEN.md section 2). The fresh G2 verifier is item C17. | PASS |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | Particle number, three members, read whole (g2long entries 26-27): N/4 FNQ D-20261124-172725-2f426b6, N FK D-20261123-022725-a553496, 4N FN4 D-20261124-134157-b17938b; /M_4N - M_N/ <= /M_N - M_N/4/ at all four named times, window-rms ratio 1.9-3.1 against 2 for N^-1/2 noise (conv3 D-20261126-055249-505b079, conv3.png looked at); removed m E_K of N/4 within 0.86 per cent of N (np_partial D-20261126-054636-93618ee). Mesh of the growth: M/8 ES-FL D-20261121-203150-15f2bad and M/16 FL16 D-20261124-172745-72472ed agree in Delta M from 20 M to 4.4e-4, 1.2e-4, 8.6e-5 at 100, 200, 300 (299) M (bound 3e-3; 3.6e-4 to 1.3e-5 with own controls); M/4 FF4 D-20261123-022727-1c17e73 drawn and labelled outside the convergent regime (decision 0039 item 4); two members in the regime, NO order claimed (L3 held as written only against the out-of-regime M/4). Mesh of the null test: M/8 and M/16 at the floor, two members and no order (decision 0041 item 4). Boundary: faces +-192/384/768 M (boundary_gauge D-20261124-131657-89cd963). Gauge: plain 1+log only; the relaxed lapse cannot serve (OPEN.md section 2) - stated as the gap of the gauge leg. every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e). | PASS |
| C3 | Constraints behave | Volume norms bounded in all long runs (D-20261123-021027-e3af9b8); exterior plane norms bounded to 500 M (XC1, D-20261124-134211-c6fce88). Particle noise of the deposit shown three ways: XN 4N/N = 0.43-0.49 (D-20261125-122849-43db157), XQ N/4 over N = 1.65-1.89 on A1/A2 at 100 and 200 M (D-20261126-054718-afa783e, looked at), region shells FNQ/FN4 = 3.2-5.2 from 20 to 400 M (region_norms D-20261126-054736-10c837a, looked at). Mesh: L5 M/16 over M/8 on A1 2.11 at 100 M, 1.08 at 200 M, 1.00 at 300 M (D-20261126-055159-6c40115, looked at). On record: XC2's expected fall failed (factor 1.05), R1's 'every column finite' failed on the NaN of the empty horizon sphere at t = 0 (g2long entries 12, 24). | PASS |
| C4 | A first minimal full-GR kinetic run | ES-F (D-20261121-144631-aa7ce9b) and ES-FL (D-20261121-203150-15f2bad, 850724 particles, 500 M): kinetic matter falling into an evolved puncture in full GR; analyses D-20261123-020606-fa0046c, -020614-7ba5874. | PASS |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | STAGE_REPORT.md (nrpic-stage report, batch 25), EVIDENCE.md, OPEN.md, this CHECKLIST, LADDER.md, REVIEW.md; working note v3 (note/main.pdf, section V and ledger part 11). What stays open is listed in OPEN.md: failures on record with their rulings and the fresh-context verifier (C17). | PASS |
| C6 | Reproducibility package | stage/G2/rerun_g2.py: every run id cited in CHECKLIST, EVIDENCE, LADDER, OPEN and STAGE_REPORT looked up in its manifest; 35 analyses rerun as new registered runs from the registered card outputs (5 that name no output directory of their own are listed and not rerun), 6 processor simulations with --include-sims, 14 card runs listed with input and card-hours for the queue only. Tested: rerun of xc_plane D-20261125-122849-43db157 as D-20261125-160651-29a730e gives a byte-identical xc_plane.json. | PASS |
| C7 | In the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor | Criterion N of g2long entry 1 (fixed before the runs): max /D_ES1L - D_V1L/ on 100-500 M = 2.28e-4 against 2.51e-4 = 2 F_V(500) (judge_long D-20261123-020550-f9a3482); M/16 1.99e-4 on 100-300 M (H3, D-20261124-131138-0b8ffc5). Since batch 11b the floor's cause is found: the production finder's stopping rule (FP2, FP3: converged-finder vacuum drift 1.8e-5 at M/8 over 100-500 M, 3.9e-6 at M/16); with the converged finder the bubble-minus-vacuum difference is at most 7.3e-5 (M/8, 100-500 M) and 5.5e-5 (M/16, 100-300 M), without a trend in time; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (FP5, FP-ext, FE; D-20261124-172508-c847ee4, D-20261124-175356-0f40f1a; fp_analyse.png and fe_analyse.png looked at). Reservation: at M/4 the criterion FAILS (FE4: 4.6e-3 at 300 M, P5 refuted, judge_conv D-20261125-122227-3eb563a, g2long entry 21): N holds at M/8 and M/16 only; M/4 is outside the convergent regime. Horizon searches rechecked (decision 0040 item 3; no D run has a status file, every one was made without `<fastflow> diagnostics`): by the source-fixed signature of a failed search (NaN or bit-identical repeat), none after 20 M in any of 13 summaries, the plateaus are found surfaces, no removal reads a failed line, N unchanged; four V-1L dumps also by core's status files (hz_check D-20261125-160142-b1c51b5, D-20261125-160241-2b7ba3b; g2long entry 24). | PASS |
| C8 | With matter filled in, the mass growth agrees with the integrated particle flux through the horizon | Criterion G of g2long entry 1 holds at every member: (iii) every 10 M bin within +-1 per cent (+-2 per cent for N/4) and D2 at every sample: ES-FL M/8 61 bins, max 0.620 per cent (D-20261123-020614-7ba5874); FL16 M/16 38 bins, 0.485 (D-20261126-055158-30ae09c, own control V-1L16); FK N 50 bins, 0.249 (D-20261125-115647-fd2f3f7); FN4 4N 0.239 (D-20261125-122827-c5735f8); FNQ N/4 0.290 (D-20261126-054616-a13a888); FF4 M/4 0.685 with its own control, outside the regime (D-20261125-121123-143a007). The (iii) step at tau_rem ~285 M is the end of horizon excision at 4 x initial_radius (FK, P9). On record: D3 fails at M/4 and at N/4 (8352 of 29984 removals after ~220 M, g2long entry 26); early removals before the exact crossing (FK, FN4, FNQ) [TO VERIFY], D4 has no bound. every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e). | PASS |
| C9 | Schematic: Verification ladder | Verification-ladder schematic schem_ladder.png, registered D-20261124-172838-3a30e48 and, redrawn after test FE, D-20261124-175505-a1053fa (paperfig style, g2long/tools/schem_ladder.py), both looked at by the lead on 2026-11-24; it will be redrawn as the queued runs end. | PASS |
| C10 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | Particle number and mesh of the growth: conv3.png (D-20261126-055249-505b079) and in the note fig_g2conv (note build D-20261126-055502-fbb1bec), looked at; mesh of the null test: judge_conv.png (D-20261125-122227-3eb563a) and fp_analyse.png panel (d) (D-20261124-172508-c847ee4); boundary/gauge: boundary_gauge.png (D-20261124-131657-89cd963). | PASS |
| C11 | Data figure: Constraint norms against time | constraints_long.png (D-20261123-021027-e3af9b8), xc_plane.png (D-20261124-134211-c6fce88, D-20261125-122849-43db157, D-20261126-054718-afa783e, D-20261126-055159-6c40115) and region_norms.png (D-20261126-054736-10c837a, FN4 and FNQ to 400 M), each looked at by the lead. | PASS |
| C12 | Data figure: At least one multi-scale slice mosaic with zoom boxes | Slice mosaic with zoom boxes D-20261124-134644-2389227 (g2long/tools/slice_mosaic.py), looked at by the lead of batch 11. | PASS |
| C13 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | CHECKLIST, EVIDENCE, OPEN, LADDER, STAGE_REPORT present; stage/G2/REVIEW.md points to the lead reviews in stage/REVIEW-wave3.md (sections 13-23); scope text scope/SCOPE.md; rerun plan stage/G2/rerun_plan.json (rerun_g2.py --json). | PASS |
| C14 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | Note v3 data figures drawn by one script each from registered run outputs (note/scripts/fig_*.py; new fig_g2conv.py), all regenerated by the registered build D-20261126-055502-fbb1bec (run_all 15 of 15); figure pages of the compiled note looked at by the lead (pages 11-14). The other G2 figures (judge_long, esf_criteria, xc_plane, region_norms, hz_check, conv3) are drawn with figstyle by their registered readers and were looked at. | PASS |
| C15 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png (on release core-v0.7: released capabilities as exists, the excision guard as provided by core on a tested branch) and schem_timeline.png (G2 package assembled), paperfig style, drawn by the registered build D-20261126-055502-fbb1bec and looked at by the lead. | PASS |
| C16 | Working note written with /paper-writing; its manuscript checker passed with --compile | Note v3 (note/main.tex, 24 pages): section V 'Verified capability' (null test to 500 M, growth at three particle numbers and two cell sizes, what stays open), ledger part 11 with every G2 number and its run id; compiled; check_manuscript.py --compile: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are run ids in the ledger (by design) and four contrastive phrasings kept where the contrast carries the content. | PASS |
| C17 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | No G2 verifier yet: to be sent by the orchestrator with the artefacts (decision 0016 item 4); the package is otherwise complete. | OPEN |
| C18 | Null results and failed runs are on record (manifests and JOURNAL) | Failed predictions on record in g2long/JOURNAL.md: entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2), entry 11 (P2), entry 12 (XC2 expected factor), entry 14 (FP4 refuted, FP-ext (ii) missed its bound); QR3/QR4 in secondary_infall/JOURNAL.md; cut chains closed as failed and resumed (entry 10). Batch 17-20: P5 refuted, P6, P11, P13 failed (entries 19-21); entry 24: R1 failed as written (NaN Hmax of the empty horizon sphere at t = 0), T1 failed for FN4 as an extension (3.4 per cent before 219 M); hz_check run D-20261125-160123-f86d73c failed (parser), on record. Batch 25: D3 fails at N/4 (FNQ, entry 26); conv3's first reading dropped the 300 M mesh time (D-20261126-055207-0137c53, reader changed after it and rerun, entry 27); np_partial's 'partial' label on a whole reading (entry 26). | PASS |
| C19 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of batch 25 (2026-11-25). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-26T06:01:46Z, clean export of `332692691262`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 332692691262 (HEAD) in /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/stage-verify/D-bh-dress-G2-3326926-20261126T060029Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 14 figures, each with its script |
| min-figs | PASS | 2 schematics and 12 data figures (brief 13.4 asks at least 1 and 5 at G2) |
| runs | PASS | 321 run manifests finished (106 hand-written, read as decision 0012 allows); failures of 1 runs waived by coord/WAIVERS.md (decision 0019) |
| runs-waived | WARN | failures of the manifest check waived: 1 runs named in main's coord/WAIVERS.md (decision 0019 item 6): D-20261121-165420-5d1c245: superseded: the check run of the G1 gate reviewer; an input under scratch changed after the run; its result stands in the gate review of G1 and no later claim rests on it (decision 0039 item 4) |
| run-notes | WARN | 99 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 14 of 14 scripts and commands ran cleanly in the export |
| compare | PASS | 40 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 28 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_es.* | note/scripts/fig_es.py | data | to be confirmed by the session |
| note/figures/fig_esf.* | note/scripts/fig_esf.py | data | to be confirmed by the session |
| note/figures/fig_esrun.* | note/scripts/fig_esrun.py | data | to be confirmed by the session |
| note/figures/fig_floor.* | note/scripts/fig_floor.py | data | to be confirmed by the session |
| note/figures/fig_g2conv.* | note/scripts/fig_g2conv.py | data | to be confirmed by the session |
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
- `D-20261125-160123-f86d73c`: failed (exit 1), g2long entry 23 test H (decision 0040 item 3): failed horizon searches by signature (bit-identical repeat or NaN; no run has a status file) in every G2 summary, criterion N with failed lines dropped, removals whose first sample is a failed line, FP/FP-ext probes found, bit match with core's status-file re-search of four V-1L dumps
- `D-bh-dress-20261115-121837-987643b`: failed (exit 1), Test 1 of D-pre-3: radiation-era turnaround of dark matter around a hole against the printed numbers of 2106.07480 (Table 1, eta_ta) and 1901.08528 (ratios 0.964, 0.999; radial-orbit factor 53 %)
- `D-bh-dress-20261115-122303-4e8e8af`: failed (exit -15), Test 2 of D-pre-3: Bertschinger-type self-similar collisionless infall onto a point-mass seed in Einstein-de Sitter by fixed-point iteration (inner slope, caustics, normalisation against the frozen-in estimate)
- `D-bh-dress-20261115-125449-60a62b8`: failed (exit 1), Analysis of tests 2 and 3 of D-pre-3 and the parameters of the AthenaK runs (closed-form checks, growth of turnaround, dress and hole mass, self-similarity at a/a_i=100, predicted profiles for eps 0.01 and 0.03, capture with angular momentum, cost from the scoping model)
- `D-bh-dress-20261115-125724-464611f`: failed (exit 1), P2a-d analysis of run A: stationarity, invariants, empty loss cone

## Open risks


Updated in the lead session of batch 20 (2026-11-25 08:20 PST). Closed risks are kept at the bottom.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R2 No lapse slices a puncture inside expanding dust and keeps its horizon mass under lapse_leak (late growth, decision 0025 item 3: mitigation in v0.7, cure later). 1+log leaves the dust off its exact curve (ES-1) but keeps the hole | certain for lapse_leak | the null test runs with 1+log only | core's cure after the usage reset | all G2 runs plain 1+log (g2long); `lapse_leak_hole` (core-v0.7) is a mitigation: no G2 item can be judged with it at its bound beyond ~100 M (stage/G2/OPEN.md section 2); at G3 only with the mitigated vacuum control beside it |
| R3 Floor of the null test. The production finder (mass_tol 1e-5, warm start) reports plateaus 1.3e-4 apart; this is its stopping rule (FP2, FP3 hold, g2long entry 14, D-20261124-172508-c847ee4): with mass_tol 1e-9 the vacuum mass moves by at most 1.8e-5 (M/8, 100-500 M) and 3.9e-6 (M/16). The floor of N as defined in entry 1 (production finder) stays 1.25e-4 | certain (measured) | N's margin (9 per cent) is the finder's; the converged-finder null difference is <= 7.3e-5 (M/8), <= 5.5e-5 (M/16), no trend; the bubble's mass dips by 4-6e-5 at 100 M at both meshes (FE, entry 17) | FE4 dumps (M/4): does the dip depend on the finest level? | quote both; G2 judged on the converged finder at the dumps; new null-test inputs set mass_tol_0 = 1e-8; core request finder-stopping-rule posted 2026-11-24 |
| R13 Late horizon drift. In vacuum with 1+log it was the outer boundary (V-1 -1.37e-4 after 165 M; gone at +-384 M, V-1B). Under lapse_leak it is not the boundary: ES-1GB (+-384 M) equals ES-1G (+-192 M) to 4.2e-9 up to 188 M; the batch-2a reading is withdrawn. ES-1's (-3.4e-4, 1+log, dust) is untested with far faces | low for vacuum 1+log; certain for lapse_leak (R2) | a gauge or boundary effect read as coupling or accretion | ES-1B | every 200 M run with the faces at +-384 M (400 MeshBlocks, 0.78 card-hours at M/8 in vacuum); far faces protect the exterior mass (ES-1GB: Misner-Sharp mass 2.741 kept on R = 119-223 M) |
| R14 Lapse excision idle: the mesh minimum of the lapse is above alpha_exc = 0.05 near t = 6 and 15 M (1+log) and from t = 108 M on under lapse_leak (0.069 at 200 M) | certain | matter near the hole kept only by ah_exc_factor | alpha_min (history column 16) in every matter run | keep ah_exc_factor = 0.8 with the finder on; request to core (outbox lapse-excision-criterion) |
| R4 D-pre-4's excursions (9.3e-5 at 220-255 M, 1.5e-4 at 300-340 M, same at M/8 and M/16) were attributed to the boundary; the same pattern with faces at +-768 M and its removal by the tight finder (FP) make the finder the likely cause [JUDGEMENT: D-pre-4's own dumps not re-searched] | medium | the G0/G1 wording of the floor | none | re-search D-pre-4 dumps with probe_long.py before the note cites the boundary reading again |
| R5 Particle resolution and noise next to the puncture (TESTLOG:1949-2053) | high for matter runs | spurious accretion or crash | n_excised, NaN in nrpic.hst column 3 | ah_exc_factor = 0.8, cloud level cap, N scan; ES-F (flux_tools) is the first matter run into the hole, pre-registered (entry 7) |
| R6 Numerical relaxation of a dress (TESTLOG:690-1022) | medium | spike flattened, loss cone refilled | capture rate N vs 4N | relaxation control at G2 |
| R9 Cost of the G2 ladder beyond M/16 (verifier C8: 3200, 4712, 7848 MeshBlocks); the faces at +-384 M add 16 per cent (400 against 344 blocks) | certain | budget | `-m` counts before submission | re-cost with measured rates (V-1B 0.778 card-hours for 200 M on 400 blocks); 29.22 card-hours left toward G2 |
| R10 Over-claiming the null result (2302.07878 `paper_couple_rev.tex:132` gives k = 0 to Kerr; orch brief check 2.87: 1903.01490 bounds |k| <= 5.0e-4) | medium | misleading wording | wording review | null test worded for ordinary black holes; design to reach |k| well below 5e-4 with the flux measured separately |
| R11 Defaults: finder `metric_drvts = stored` and `ah_exc_factor` off | certain | horizon mass 2-6 per cent low; matter kept at the puncture | every input | every Track D input sets both |
| R16 Shared worktree; sessions cut by usage limits leave runs unclosed and files uncommitted (2026-11-20: four runs, three tools, five figures) | certain | lost bookkeeping, index conflicts | git status and `nrpic-run status` at every session start | path-limited commits; close stale runs with `nrpic-run finish` after checking `.nrpic/result.json` |
| R18 Long runs: the finder kept ES-FL's horizon to 500 M (radius 5.30 M); the queue and the sequencer worked (R1-R4 done, R5 at 225.6 M) | low now | runs late | horizon_summary gaps; `$S/g2long_seq/log` | sequencer restarted for the follow-ups (HANDOFF) |
| R19 Set-up data that do not cover a larger mesh (ES-F table to 345 M, exterior = zero, found by smoke S2) | was certain, fixed for ES-FL | constraint jump inside the domain | smoke runs before every new mesh; the table header line | data maker `--rbar_max`; HANDOFF trap 14 |
| R20 Horizon excision ends when the horizon's smallest radius passes 4 x initial_radius (nrpic.cpp:451-455): in ES-FL at 219 M; afterwards removal by the lapse rule, deeper and later, leaving steps in (iii), D3 and the closure | certain for growing holes | growth criteria biased by the removal time (+0.35 per cent in (iii)) | removal reasons in removed.bin | CONFIRMED as the cause by FK (g2long entry 19: with excision kept on, the late (iii) medians stay at 0.16-0.24 per cent, ES-FL 0.6; P9). Inputs of growing holes set initial_radius_0 so that 4 x it exceeds the final r_min; core request ah-excision-growth-guard |
| R21 Exterior constraints: the z4c history norms skip chi < 0.0625; the z = 0 plane norms outside 1.2 r_AH (test XC) are bounded in every long run, but in the dust they sit near 1e-3 (A1) and fall on the coarser mesh (particle sampling noise of the deposit, [JUDGEMENT]) | certain | 'constraints behave' rests on a plane, not a volume; dust residual set by particle number | region norms in FN4 (prediction XN) | volume region norms in every new input (make_followups2.py) |
| R22 The horizon-mass offset has no mesh order: production finder -8e-3, +9.5e-4, -2.5e-4 (P2 refuted); converged finder (A32) -8.9e-3, +1.18e-3, -1.8e-5 over M/4, M/8, M/16 (FP4 refuted). The finder's angular truncation A16-A32 is a constant -1.8e-4 on every mesh | certain | no convergence statement for M_AH itself | three-mesh differences (null test, growth) | quote convergence only of differences; the A16 offset cancels in them |
| R25 `nrpic-run finish` refused chains continued in place (field `continuations`) | CLOSED for new closes: main accepts the field since 2026-11-25 14:15Z (orch message finish-continued-runs-checksum-cache) | - | close FNQ/FL16 with nrpic-run finish when their last job ends | close_by_hand.py kept as the fallback |
| R26 Coarse-mesh and restart artefacts in the growth readings: the M/4 finder's t = 0 mass is 1.0330 (M/8 0.9915), so growth from t = 0 fails P13; D3 fails at M/4 for early removals; FK removes 29.5 per cent of its dust before the exact horizon crossing (ES-FL 0.23 per cent), cause unknown | certain (measured) | a mesh order of the growth read from t = 0 is wrong; D4/D3 readings depend on the run | g2long entries 19, 20 | growth differences from 20 M (L3); each mesh with its own vacuum control; D4 of FK and ES-FL restricted to t_rem <= 219 M next session [TO VERIFY] |
| R27 Horizon searches read without a status file: every D run was made without `<fastflow> diagnostics`; the summary repeats the last accepted surface after a failed search (decision 0040 item 3) | certain for the existing runs | a failed search could pass for a plateau or a found mass | hz_check.py on every new summary (signature: NaN or bit-identical repeat); batch 20: none after 20 M in 13 summaries (D-20261125-160142-b1c51b5) | every new input sets `diagnostics = true`; with core-v0.8, `polish_iterations_0 = 100`, `mass_tol_0 = 1e-5` after core's card check q0049 |
| R28 Horizon excision with the guard off removes dust before the exact LTB crossing once the hole has grown (FK after 235 M: 62.6 per cent of removals, down to -0.36 M of proper time; FN4 from 170 M, -0.66 M; d4_timing D-20261125-160450-9326390) | certain (measured) | a dress or spike profile read from removal times near the horizon would be biased by ~0.5 M of proper time | D4 per bin in every growth run; core's guard test (ah_exc_max_growth = 8) when the cards free | no criterion depends on it now; cause not named [TO VERIFY] |
| R23 Card allotment: raised by 10 card-hours (decision 0032 item 3); FNQ and FL16 registered (caps 3.0, 5.0); 3.86 card-hours left toward G2 with six runs reserved | low now | none while the caps hold | nrpic-run budget | no further G2 card runs without an allotment request |
| R24 Preemptions (another user's priority jobs, 2026-11-23 and 11-24, held until about the morning of 2026-11-25) cut chains: each consumes a segment, AthenaK writes no restart on the signal, and a segment killed without its own restart rewrites the removal record after the resumption (FF4: 12582 duplicate records) | certain while the cards are shared | chains closed as FAILED; flux sums double-counted; card time lost back to the last restart | chain events.log; time going backwards in removed.bin | P11 failed on it (FK 2.70 card-hours against 1.8-2.4). Resume from the newest restart; MAX_SEGMENTS raised; new chains on core-v0.7 executables write a restart on SIGTERM (coord/INTERFACES/preempted_runs.md); restart every 25 M (FK, FN4, FNQ) and 12.5 M (FL16) through EXTRA_ARGS (decision 0032 item 2); fluxio.drop_overlaps in esf_analyse/esf_criteria |

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

Not ready for review (lead of batch 20): C1-C3, C5, C10, C13-C17 open; FNQ (q0010, 353 M of 400) and FL16 (q0011) wait for the cards; horizon recheck of decision 0040 item 3 done (no failed search after 20 M; no run has the diagnostics); C6 and C11 pass
