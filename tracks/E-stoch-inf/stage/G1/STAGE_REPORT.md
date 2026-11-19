# Stage report: E-stoch-inf G1

Date: 2026-11-19 · branch `track/E-stoch-inf` at `a21869be9358` · checklist
`tracks/E-stoch-inf/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/E-stoch-inf/G1-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 7 checklist items not PASS or NA: C6 OPEN, C8 OPEN, C9 OPEN, C13 OPEN, C14 OPEN, C15 OPEN, C16 OPEN
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G1/REVIEW.md` | present |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | linear Mukhanov-Sasaki references of both cases (spec/ref/ms_reference.py; runs E-stoch-inf-20261115-122806-ef0d039, E-20261115-135532-3f958a1, verifier E-20261115-174606-3c67607, rerun identical E-20261119-150346-a513bc8); stochastic delta-N references (langevin/, runs E-stoch-inf-20261115-130137-176cdd6, -130139-176cdd6); the SR ladder itself needs no particle coupling (scalar field and Z4c only): STATUS.md, EVIDENCE.md 1 | PASS |
| C2 | The analysis pipeline validated on them | analysis/sfa.py synthetic tests T1-T5, 15/15 (E-20261115-171445-36152c4, rerun identical E-20261119-150346-a513bc8); estimators against the code's own history on a plane perturbation (E-20261115-171859-0b34449); ladder reader bitwise equal to core's and R^NR at t = 0 within 7.5e-10 (E-20261115-172935-ddfade0); extraction factor E6 (E-20261115-174214-74becdd); lead's independent extraction on L32p agreeing to three digits (E-20261119-150238-b81e33f) | PASS |
| C3 | Interface proposals submitted | noise/NOISE_SPEC.md, noise/RNG_REQUIREMENTS.md, codebase/DESIGN_REVIEW.md 9 and 11, spec/SPEC.md 10; outbox 20261115T1410Z to core (initial slice, diagnostics, card build, noise results), answered by core (message scalar2-ready; interface proposal tracks/core/interfaces/scalar_field_2.md on core/scalar-2); outbox of 2026-11-19 (release request, A4 proposal) | PASS |
| C4 | Baseline data and figures | ladder/results/final, floor, a6, a12 and ladder/fig/ (runs EVIDENCE.md 1); analysis/fig; stage/G1/fig/fig_lead_check.png | PASS |
| C5 | Interface documents | noise/NOISE_SPEC.md and RNG_REQUIREMENTS.md (track); coord/INTERFACES/ scalar field of core-v0.3; core's tracks/core/interfaces/scalar_field_2.md (branch core/scalar-2, written to SPEC 5.3 and 10; not yet released) | PASS |
| C6 | The power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge | spectrum MET (A2: 1.21e-4 at 256^3 for /n/ <= 32, E-20261115-172618-f948386; lead 8.76e-5 on L32p); freezing MET (A3: drift 1.4e-4 per e-fold against 2.5e-3, FLRW lattice excluded by 350); constraints converge in the sheet's sense (odd part order 4.2-5.9, H0 order 4, second-order part independent of N within 2.2 percent; E-20261115-194633-9e04ed8, E-20261119-142713-32c883a), but the owner's accepted A4 fails in its strict form in P1's set-up at every N (odd part up to 385-870 x even part from ln(N/8) e-folds) and A5's floor was defined after the data: ruling on A4'/A5' asked of orch (outbox 20261119). STATUS.md | OPEN |
| C7 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | applied: continue to G1 and G2; SCOPE 4 choices used (Courant 0.25, now justified by A6; level 0; thresholds A1-A7 as written, A4 failure kept on record); downgrade (SCOPE 4 item 5) not triggered: A3 passes, 0.503 card-hours per 256^3 SR realisation against 5 | PASS |
| C8 | Schematic: Updated architecture | not drawn: note/figures/schem_architecture.png shows the G0 state (836ac86); the initial slice, mode tables, constraint record, R^NR, per-mode and freezing analysis now exist (core/scalar-2, ladder/, analysis/) | OPEN |
| C9 | Schematic: Data-flow diagram | not drawn | OPEN |
| C10 | Data figure: Baseline results | ladder/fig/final/fig_spectrum.png, fig_a2_modes.png, fig_a3_freezing.png (looked at by the lead 2026-11-19; regenerated pixel-identically in run E-20261119-150842-ca70d37) | PASS |
| C11 | Data figure: Validation figures for the analysis pipeline | analysis/fig/fig_t2_extraction.png, fig_plane_constraint_ratios.png; stage/G1/fig/fig_lead_check.png (script stage/G1/scripts/lead_check.py, run E-20261119-150238-b81e33f); all looked at | PASS |
| C12 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md), STATUS.md (criteria table); scoping text spec/scope/SCOPE.md | PASS |
| C13 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | style: ladder and lead figures use a copy of harness/style/figstyle.py; every PNG looked at; but the ladder's six final figures come from one script (ladder/scripts/make_figures.py), not one script per figure, and no G1 note figure exists yet | OPEN |
| C14 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | the G0 schematics (note/scripts/schem_*.py, paperfig.py) exist; updated G1 versions not drawn (C8, C9) | OPEN |
| C15 | Working note written with /paper-writing; its manuscript checker passed with --compile | note/main.tex is the G0 note v0; G1 sections not written | OPEN |
| C16 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no fresh-context verifier of the G1 material (decision 0016 item 4); stage/G0/VERIFIER.md covered the plan; the lead's re-check (../REVIEW-wave2.md) is not a verifier | OPEN |
| C17 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept with manifests: E-20261115-172521-e098160, -170651-885fc6e (literal run directory), -171628-1737ebe (failed /M/ prediction), -171633-f574079 (final tail), E-20261119-145853-ef835c2 (lead's rerun, I/O bound); refuted predictions on record: ladder P5 and entry 6's attribution, analysis PS5 and T2a, verifier V6/V7/V2b items, owner A4 strict (ladder/JOURNAL.md, analysis/JOURNAL.md, stage/G0/JOURNAL.md, JOURNAL.md) | PASS |
| C18 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the lead on 2026-11-19 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:47:42Z, clean export of `a21869be9358`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of a21869be9358 (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G1-a21869b-20261119T154710Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: spec/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | PASS | 95 run manifests finished (30 hand-written, read as decision 0012 allows) |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 31 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
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

MISSING: the verifier subagent has not reported (`stage/G1/VERIFIER.md`, decision 0016).

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

G1 of E-stoch-inf is not met, and the package is not complete for the orchestrator's review under decision 0016 item 4. Met: the slow-roll power spectrum agrees with the analytic result (A2: 1.21e-4 for |n| <= 32 at 256^3 in P1's set-up, run E-20261115-172618-f948386) and super-horizon modes freeze by the criterion of arXiv:2606.14853 (A3: drift 1.4e-4 per e-fold against 2.5e-3); the constraints converge in the track sheet's sense (odd part at order 4.2-5.9, uniform residual H0 at order 4, second-order part independent of N); A1, A6 (order 3.93-4.08) and A7 pass. Not met: the owner's A4 as accepted in decision 0013 fails in its strict form in P1's set-up at every N (first-order spatial truncation of the shells with fewer than eight cells per wavelength), and A5 passes only with a floor defined after the data; A4' and A5' are proposed to the orchestrator (outbox 20261119T151727Z). Missing: a fresh-context verifier of the G1 material (request 20261119T151728Z), the updated architecture and data-flow schematics, and the G1 sections of the note. All slow-roll evidence comes from scouting runs with core's tested-branch executable core/scalar-2 (decision 0013); the release of that set-up is requested from core.

## Notes of the lead on this report (2026-11-19)

- `verify` ran with `--no-checksums` (PASS on d480131e and again on a21869be): the output checksums are
  not re-read (the disk was shared with two other leads' verifies; see `../G0/STAGE_REPORT.md`,
  notes); the reruns of `../REVIEW-wave2.md` reproduce the numbers from the registered outputs.
- A first G1 verify was started by mistake from the main checkout (the `cd` of the command
  applied only to a background subshell): it verified the tip of `track/E-stoch-inf` read-only
  as the orchestrator would, PASS on the same commit, and left its export under
  `scratch/orch/tmp/stage-verify/E-stoch-inf-G1-d480131-20261119T154146Z/` (not removed: it is
  another owner's scratch).
- The figures this gate relies on are not the note's (those are G0's) but the ladder's and the
  lead's: `ladder/fig/final/fig_a2_modes.png`, `fig_a3_freezing.png`, `fig_a4_paper.png`,
  `fig_spectrum.png`, `ladder/fig/floor/fig_floor.png`, `ladder/fig/a6/fig_a6.png`,
  `stage/G1/fig/fig_lead_check.png`, all looked at by the lead (EVIDENCE.md section 5). They are
  not yet note figures with one script each (checklist C13).
- Each criterion met or not: `STATUS.md`; what is missing: `OPEN.md`; the review of the helpers:
  `../REVIEW-wave2.md`.
