# Stage report: E-stoch-inf G0

Date: 2026-11-19 · branch `track/E-stoch-inf` at `1d25517c3215` · checklist
`tracks/E-stoch-inf/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**PASS**. Tag: `stage/E-stoch-inf/G0-pass-20261119` (created and pushed by the orchestrator after review, decision 0003).

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/VERIFIER.md` (verifier's report) | present |
| `stage/G0/REVIEW.md` | present |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | spec/scope/SCOPE.md (owner's version 1): problem statement section 1, parameter ranges 2, exit criteria and the owner's decisions 4, test plan by row of brief 10 section 5; stage/G0/EVIDENCE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | statements of the key references read at file:line in kb-data/raw/arxiv sources (SCOPE.md section 3: P1, P2, BZ, FKTT, JM; lead re-read P1:536-541 on 2026-11-19); the errata are knowledge-base claims 603-609 of snapshot kb-20261115-44b7406 (judgement claims with the track's runs; 6 located, 603 partial; kb's locator check run kb-20261115-154906-f19880f, message 20261115T183741Z__to-E-stoch-inf__errata-s11-references); kb's numbering remark checked by the lead: the equation at P2:317-327 is the 23rd numbered environment, SPEC 5.3 corrected. The key statements themselves are not yet kb claims (as for C, D, F at their passed G0) | PASS |
| C3 | Risk list | RISKS.md (R1-R14); SCOPE.md section 7 | PASS |
| C4 | Compute estimate | SCOPE.md section 8 (codebase/figs/cost.json, run E-stoch-inf-20261115-123936-b2ec5c7, rerun identical in E-20261115-140116-87c1cc5; GPU throughput docs/TESTLOG.md:46; processor throughput runs E-stoch-inf-20261115-122727-a1c2237 and E-20261115-135218-bdf4710). Card overhead now measured by core (run core-20261115-143907-cea4c86: 65 percent instead of the assumed 15); recomputed with it, one 256^3 realisation costs 0.57-0.71 (SR) and 0.71-0.88 (USR) card-hours, an extrapolation from 128^3 (note Sec. V, Fig. 6, note/scripts/costmodel.py, run E-20261115-173904-3be0405); the conclusion of SCOPE.md 9 holds; measured since (wave 2): one SR realisation at 256^3 in P1's set-up 0.503 card-hours, 1.30 s per step, 19.6 GB (run E-20261115-172618-f948386); theta = 0.25 justified by A6 (runs E-20261119-142317-c851f27, -145230-ff0dff2); SCOPE.md 8 | PASS |
| C5 | Working note v0 | note/main.tex, note/main.pdf (REVTeX, 9 pages: problem and acceptance criteria, set-up and corrected initial slice, freezing and delta-N references, noise validation, cost and decision, open items; appendices parameters, errata, ledger); figures and tables from run E-20261115-173904-3be0405; predictions and outcomes note/JOURNAL.md N1-N3; claims check note/tables/claims.md (59 numbers of the lead's documents, 54 agree, 5 differ, listed in note/README.md) | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (Fig. 2 of the note; script note/scripts/schem_architecture.py, run E-20261115-173904-3be0405; PNG looked at) | PASS |
| C7 | Stage timeline | table in SCOPE.md section 10; schematic note/figures/schem_timeline.png (Fig. 7 of the note; run E-20261115-173904-3be0405) | PASS |
| C8 | Reproduction specification, code-base assessment and compute estimate are complete, and the group decides to continue, to shrink or to downgrade | specification (spec/SPEC.md), code-base assessment (codebase/DESIGN_REVIEW.md; decision 0010) and compute estimate (SCOPE.md 8, now with the measured 0.503 card-hours per SR 256^3 realisation, run E-20261115-172618-f948386) complete and checked (EVIDENCE.md 2; stage/REVIEW-wave2.md); the decision is taken: decision 0013 (continue to G1 and G2, scope of G3 at G2), accepted by the user with decision 0017 item 1 | PASS |
| C9 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | applied: the note's recommendation and timeline follow the ruling (continue to G1 and G2, scope of G3 decided at G2; note Sec. V, Fig. 7); the acceptance criteria of SCOPE.md section 4 are those of the note (Sec. II C). The group's decision itself is item C8 | PASS |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red), deliverables (plum); PNG looked at | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png: gates G0-G4 at the indicative times of SCOPE.md 10, requirements, needs between gates; PNG looked at | PASS |
| C12 | Data figure: None required | none required at G0 | NA |
| C13 | Data figure: Data from the literature may be redrawn | P1 Fig. 1 values redrawn against the reference: spec/fig/fig_background.png (run E-stoch-inf-20261115-123236-2e87364) | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; scoping text spec/scope/SCOPE.md (named in the report); no separate REVIEW.md: the lead's re-check of the helpers is EVIDENCE.md section 2 (for the lead to confirm); the lead's review of the wave-2/2b helpers: stage/REVIEW-wave2.md, pointed to by stage/G0/REVIEW.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | package figures (spec/fig, codebase/figs, langevin/fig, noise/fig) and the lead's (E-20261115-135532-3f958a1, E-20261115-140553-0b75e1e, E-20261115-140502-2957846) with python/nrpic/figstyle.py; the note's five data figures note/figures/fig_{background,freezing,deltan,noise,cost}.png with note/scripts/czstyle.py (unchanged copy), one script each, from checksum-verified outputs of registered runs (run E-20261115-173904-3be0405), every PNG looked at | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py and schem_timeline.py with note/scripts/paperfig.py (unchanged copy of harness/style/paperfig.py); both PNGs looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing guide and notation ../WRITING_GUIDE.md, ../NOTATION.md; check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are the run ids of the ledger appendix and the document names in the scripts, accepted by exception 1 of the guide; captions within five lines on the rendered pages (looked at). Reviewer subagents of the skill's step 4 not run | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | stage/G0/VERIFIER.md by a fresh-context verifier of wave 2 (name accepted by decision 0016 item 1): V1-V6, V8 CONFIRMED, V7 NOT CONFIRMED (cost, no card time; since measured, see REVIEW-wave2.md section 5); its computations rerun bit-identically by the lead (run E-20261119-150346-a513bc8); its run E-20261115-174600-81652ff closed; the note's ledger and claims are recomputed from the manifests by note/scripts/ledger.py, rerun by nrpic-stage verify (stage/G0/VERIFY) | PASS |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | EVIDENCE.md section 4; failed runs E-stoch-inf-20261115-125316-dafadc4, -131526-629fed8, E-20261115-135532-5ec2b09 (library-log leaf), E-20261115-140116-87c1cc5 (timing leaves), E-20261115-140502-2957846 (diagnostic syntax error) kept with manifests; refuted predictions in the package journals and the owner JOURNAL | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the lead on 2026-11-19 (wave 2b); RISKS.md updated | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:46:35Z, clean export of `1d25517c3215`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 1d25517c3215 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G0-1d25517-20261119T154605Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: spec/scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | PASS | 95 run manifests finished (30 hand-written, read as decision 0012 allows) |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 31 lines |
| rerun | PASS | 8 of 8 scripts and commands ran cleanly in the export |
| compare | PASS | 18 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_background.* | note/scripts/fig_background.py | data | yes (lead, 2026-11-19) |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | yes (lead, 2026-11-19) |
| note/figures/fig_deltan.* | note/scripts/fig_deltan.py | data | yes (lead, 2026-11-19) |
| note/figures/fig_freezing.* | note/scripts/fig_freezing.py | data | yes (lead, 2026-11-19) |
| note/figures/fig_noise.* | note/scripts/fig_noise.py | data | yes (lead, 2026-11-19) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes (lead, 2026-11-19) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes (lead, 2026-11-19) |

## Verifier report

`tracks/E-stoch-inf/stage/G0/VERIFIER.md` present; its first lines:

> # Independent verification of Track E's G0 and G1 material (wave 2)
> 
> Verifier: helper of E-stoch-inf, fresh reader, given the artefacts and not the conclusions.
> Date 2026-11-15. Worktree commit at start: 4c87b13 (after `git merge main`).
> 
> Read before the verdicts: the scoping text `../../spec/scope/SCOPE.md` (it names the claims),
> the derivation `../../spec/SPEC.md` sections 1-9, core's source of release core-v0.3
> (`athenak/src/scalar_field/*.cpp`, `pgen/nrpic/scalar_field_tests.cpp`, `z4c/z4c_newdt.cpp`,
> `z4c/z4c_tasks.cpp`, `utils/finite_diff.hpp`), the track's cost model
> `../../codebase/ref/cost.py` and its output, the run manifests, and the sources at the
> locators (P1 = 2512.14649 v2 `PRD_v2.tex`; P2 = 2502.06783 v3 `main_V2PRD.tex`; TH =
> 2610.32592 v1 `appendix.tex`; BZ = 2606.14853 v2 `Manuscript.tex`; P1's Fig. 1 PDFs).

## Null results and failed runs

- `E-20261115-135532-5ec2b09`: failed (exit 1), L-R noise: rerun of the E-pre-4 checks (twin, counts, self-test, dump adapter, reader on AthenaK output) and comparison with runs E-stoch-inf-20261115-125255-fcdcbdc, -132950-16a0168, -133731-2031735
- `E-20261115-140116-87c1cc5`: failed (exit 1), L-R codebase: rerun of the E-pre-2 checks D1-D4 and the cost model, comparison with run E-stoch-inf-20261115-123936-b2ec5c7
- `E-20261115-140502-2957846`: failed (exit 1), L-U2 and L-U3: per-mode diagnostic of the A1 difference (U6 Markov tanh, U1 frozen) and the three validations with each run's own input, on the outputs of run E-20261115-135523-a32c3a6
- `E-20261115-170651-885fc6e`: stopped (exit -15), Noise unit test, base case on processors (release core-v0.3): U2 (8 MeshBlocks, 64^3 x 300) as the reference of U9 (A14), then U4 = U2 restarted at cycle 150 (A12)
- `E-20261115-171628-1737ebe`: failed (exit 1), Constraint estimators of sfa.py on core's plane perturbation (N=16, 32) with the release processor executable: dump statistics against the code's history, convergence of |H|/[H] and |M|/[M]
- `E-20261115-171633-f574079`: failed (exit 1), ladder: mode files of the SR case (nmax2 = 256, 1024, 4096, kstart 100) with core's make_case.py of core/scalar-2 25daeed (extracted read-only by git archive)
- `E-20261115-172421-50ac4ce`: failed (exit 1), note v0: data figures (background, freezing, delta-N, noise validation, cost), the two schematics, the ledger and the check of the lead's numbers against the run outputs (predictions N1-N3 of note/JOURNAL.md)
- `E-20261115-172521-e098160`: stopped (exit -15), ladder: SR case at N = 32, nmax2 = 64 (L32 +-1 to t = 8.5; +-1/2 and negative control to t = 4.5) on core/scalar-2 a58e95b processor executable (A2, A3, A4, A5 bottom rung)
- `E-20261115-174515-4d30c15`: failed (exit 2), G0 verifier V6/V7: core's Mukhanov-Sasaki noise model with kicks and coupling (deck problems/scalar/noise_ms.athinput, N=32, nmax2=64) on the release processor executable: bit identity across three MeshBlock layouts and a restart, negative control (Pi sign) and continuum projector against the momentum constraint; processor timing of the synthesis vs MeshBlock size
- `E-20261119-145853-ef835c2`: failed (exit -15), Lead review LR1/LR2: rerun of the ladder's final analysis (analyse_all, verdicts, make_figures), floor analysis and A6 analysis at the current commit on the raw outputs of the ladder runs, for comparison with the committed ladder/results
- `E-stoch-inf-20261115-125316-dafadc4`: failed (exit 1), V2: quadratic inflation m = M_Pl, phi_in = phi_UV = sqrt42 (2206.11234 Fig. 2): Monte Carlo (direct and importance sampling) vs closed-form characteristic function, BDF2 survival solver, moment recursion; pole structure
- `E-stoch-inf-20261115-131526-629fed8`: failed (exit 1), T-N6 of noise/JOURNAL.md: calibration of the A3 decisions (KS of |w|^2 and arg w, fourth moment) on correct amplitudes, 2000 seeds of the base case; single-decision calibration and family-wise false-alarm rate per validation

## Open risks


Rewritten by the lead on 2026-11-15 at the G0 package; updated by the lead on 2026-11-19
(wave 2b) after the slow-roll ladder, the G0 verifier (`stage/G0/VERIFIER.md`) and the review
`stage/REVIEW-wave2.md`. Sources: `spec/scope/SCOPE.md` (sections 3, 4, 4b, 8),
`codebase/DESIGN_REVIEW.md`, `langevin/README.md`, `noise/NOISE_SPEC.md`, `ladder/README.md`.
Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The reproduction rests on core's tested-branch executable `core/scalar-2` (a58e95b: initial slice at N*, constraint record, double dumps with gt_ij), not on a release; every SR result of wave 2 is a scouting run | certain until the release | medium (G1 evidence is scouting; G2 needs released code) | `tracks/core/CHANGELOG.md`; core's release of scalar-2/scalar-3 | rerun the 256^3 SR case on the release when it exists (0.5 card-hours) and compare with run E-20261115-172618-f948386 |
| R2 | A defect in core's stochastic hook that the tests cannot see | low (was medium) | high | A6 passed (order 3.93-4.08, sources at the stage times; runs E-20261119-142317-c851f27, -145230-ff0dff2); negative controls 4e4-1.5e5 times the proper run; A2 per mode to 1.2e-4 at 256^3 | the single-kick test L5 on a resolved mesh is still not run; keep the sign-flip control in every set-up |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping and tolerances open (SPEC 8) and print wrong formulas (SPEC 9) | certain | medium | SPEC 8, 9; kb claims 603-609 | per-mode acceptance needs no published tolerance; E6 (extraction factor 1/4) now tested by run E-20261115-174214-74becdd; the P2 initial-condition equation is "eq. (17)" in our older texts, but the source numbers it 23rd (SPEC 5.3 note) [TO VERIFY against the PDF] |
| R4 | The freezing criterion fails for a reason other than a defect | low | high (downgrade trigger) | A3 drift after N_k + 4 | SR passed on every rung (drift 1.4e-4 per e-fold against 2.5e-3); USR not yet run |
| R5 | Unit conversion G = 1 against Mpl = 100 | low (was medium) | high if wrong | A1 | A1 passes at 1e-11 on every rung (ladder; lead's check run E-20261119-150238-b81e33f) |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541); first-order truncation part at four cells per wavelength | medium | medium | M/[M] record, odd part of M | A4 fails in its strict form in P1's set-up already in SR (first-order part from ln(N/8) e-folds); proposal A4' (SCOPE 4b) to orch; USR run by the wave-3a usr package |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 separate-universe Langevin overestimates the variance by 42-45 percent | medium | medium | sensitivity scan L9 (not run) | compare NR with the sigma <= 0.01 reference only (A8) |
| R9 | Tail statistics need many realisations: 1e3 realisations at 256^3 cost about 500 (SR) to 630 (USR) card-hours at the measured 0.50 card-hours per SR realisation | high for G3 | high for S11 item 2 | measured cost (run E-20261115-172618-f948386) | smaller boxes, importance sampling, or the downgrade path; scope of G3 decided at G2 (decision 0013) |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build slow (1.2e4-1.35e4 zone-cycles/s serial); cold dumps at 128^3-256^3 read through a memory map at a few MB/s when the disk is busy (lead's rerun E-20261119-145853-ef835c2 stopped) | certain | low | | N = 32 on processors; analyse large dumps right after the card job (page cache) or read them sequentially |
| R13 | Budget: 10 card-hours to the next gate; 1.43 used (`nrpic-run budget`) | low | medium | `harness/bin/nrpic-run budget` | Courant factor 0.25 is justified by A6; P2's 0.025 (6-15 card-hours per realisation, verifier V7) is not needed |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` | happened, fixed | low | `nrpic-run budget` | statuses normalised; decision 0016 item 3 |
| R15 | USR ends at the border of diffusion domination (verifier weak point 3): classical drift per e-fold equals H/2pi at N* + 8.3 (ratio 0.98), Delta_R reaches 1 at 64 dk, one H/2pi kick moves the end of USR by about one e-fold; a delta-N end surface at N* + 10 sits just past the stationary inflection point | high for G2/G3 | high for the validity of linear-noise level-0 runs and of the delta-N reference | verifier V2b (run E-20261115-180056-d62ee5a: f_NL 0.011, response near-linear in the 256 box) | state the validity window at G2; do not enlarge the box or move the noise cut later without a level-1 comparison; place the delta-N end surface away from the inflection point |
| R16 | The double-precision rounding floor of the constraints grows as N^2.5 (6e-13 of <[H]> at 256^3 half an e-fold after N*) and limits what 256^3 shows during the first e-folds | certain | low (still 1e2 below P1's 1e-10) | odd part not scaling with s | attribution to rounding is [JUDGEMENT]; no run in another precision tests it |
| R17 | Acceptance criteria reworded after the data (A4', A5', SCOPE 4b) | happened | medium (credibility of the gate) | orchestrator's ruling | the strict A4 failure stays on record; A4'/A5' are proposals, not in force |

## Decision requested from the group

G0 of E-stoch-inf: every checklist item is PASS or NA (collected 2026-11-19) and nrpic-stage verify passes on 1d25517c (without the output checksums, see the notes). The reproduction specification, the code-base assessment and the compute estimate are complete and were checked three times: by the wave-1 lead (EVIDENCE.md 2), by the fresh-context verifier of wave 2 (VERIFIER.md: V1-V6 and V8 confirmed, V7 not measurable then) and by the wave-2b lead's reruns (../REVIEW-wave2.md). The cost is now measured, 0.503 card-hours per slow-roll realisation at 256^3 (run E-20261115-172618-f948386) against the 5 card-hour downgrade threshold, and the Courant factor 0.25 is justified by A6. The decision of the feasibility gate is decision 0013 (continue to G1 and G2; scope of G3 at G2), accepted by decision 0017. The package is complete for the orchestrator's review under decision 0016 item 4 (verifier's report on the plan present). Flags for the reviewer: the key statements of the references are read at file:line but only the errata are knowledge-base claims (603-609); the timeline schematic still says the decision is pending.

## Scoping text and the products of this package (written by the note helper, wave 2)

The scoping text is `spec/scope/SCOPE.md` (owner's version 1), with the specification
`spec/SPEC.md`, the code-base assessment `codebase/DESIGN_REVIEW.md`, the noise contract
`noise/NOISE_SPEC.md` and the delta-N references `langevin/README.md`. The products that
OPEN.md items 2, 3 and 5 listed as missing now exist: the working note v0
(`note/main.tex`, `note/main.pdf`, 9 pages), its five data figures and the two schematics
(`note/figures/`), the ledger and the claims check (`note/tables/`), all from the registered
run E-20261115-173904-3be0405 (inputs checked against the checksums of their run manifests);
guide and notation `WRITING_GUIDE.md`, `NOTATION.md`; package README and journal
`note/README.md`, `note/JOURNAL.md` (predictions N1-N3 and outcomes; the failed run
E-20261115-172421-50ac4ce and the two superseded runs E-20261115-172442-78cf53e,
E-20261115-173135-858482f, E-20261115-173402-641b6e2 are on record there).

## Notes on the verification (lead of wave 2b, 2026-11-19)

- The verdict line above is the harness's reading of the checklist and of `verify`; the gate
  is passed only by the orchestrator's review (decisions 0016 item 4, 0017). The lead does not
  pass it.
- `verify` ran with `--no-checksums` on 1d25517c: all 16 checks PASS (`VERIFY_RESULTS.md`;
  `rerun` 8 of 8 including the ledger of `VERIFY`, `compare` 18 files). Two runs with the
  output checksums were stopped by the lead (the disk was shared with two other leads'
  verifies, 20 GB read in 11 minutes). Checked separately: `nrpic-run verify
  E-20261115-194633-9e04ed8` (the ladder's final analysis, 101 files PASS); the reruns of
  `../REVIEW-wave2.md` reproduce their numbers bit for bit from the registered outputs.
- An earlier verify on 30a84b6c failed `compare` on `note/tables/claims.*` only: the claims
  check reads SCOPE.md and SPEC.md, which the lead edited; the regenerated tables differ only in
  line locators (run E-20261119-154548-7885cdb, LN2 in the owner JOURNAL) and are committed.
- `run-notes` WARN: the 30 hand-written manifests of wave 1, named in `EVIDENCE.md`, read with
  defaults (decision 0016 item 3).
- The seven figures of the note were looked at by the lead on 2026-11-19 (table above); two
  small defects are left for the G1 sections: the right x-axis label of `fig_background.png`
  is cut at the edge, and `schem_timeline.png` still says the decision is pending.

## Disagreements between the lead's documents and the files (written by the note helper; state 2026-11-19)

All six are resolved: 1 and 2 (overhead and cost) by the measurement in SCOPE.md 8 and the
note under SPEC.md 11.2; 3 (USR eps1(N*) of the lead's integrator, 1.1e-4 relative) stays on
record in EVIDENCE.md and the verifier's report (irrelevant for the plan); 4 (dead pointer to
`stage/G0/REPORT.md`) removed from SPEC.md and RISKS.md; 5 (old state of the scalar field)
by the rewritten STATUS.md, HANDOFF.md, RISKS.md and the note at SCOPE.md 6; 6 (locator key)
renamed FKTT for arXiv:1308.4754 after reading the authors at the source.

The note helper's draft of the decision paragraph is superseded by the section "Decision
requested from the group" above.
