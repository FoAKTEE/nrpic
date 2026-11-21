# Stage report: E-stoch-inf G1

Date: 2026-11-21 · branch `track/E-stoch-inf` at `5aa8bcd4767d` · checklist
`tracks/E-stoch-inf/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/E-stoch-inf/G1-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 6 checklist items not PASS or NA: C6 OPEN, C8 OPEN, C9 OPEN, C13 OPEN, C14 OPEN, C15 OPEN
- verify reported FAIL: clean, runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | present |
| `stage/G1/REVIEW.md` | present |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | linear Mukhanov-Sasaki references of both cases (spec/ref/ms_reference.py; runs E-stoch-inf-20261115-122806-ef0d039, E-20261115-135532-3f958a1, verifier E-20261115-174606-3c67607, rerun identical E-20261119-150346-a513bc8); stochastic delta-N references (langevin/, runs E-stoch-inf-20261115-130137-176cdd6, -130139-176cdd6); the SR ladder itself needs no particle coupling (scalar field and Z4c only): STATUS.md, EVIDENCE.md 1 | PASS |
| C2 | The analysis pipeline validated on them | analysis/sfa.py synthetic tests T1-T5, 15/15 (E-20261115-171445-36152c4, rerun identical E-20261119-150346-a513bc8); estimators against the code's own history on a plane perturbation (E-20261115-171859-0b34449); ladder reader bitwise equal to core's and R^NR at t = 0 within 7.5e-10 (E-20261115-172935-ddfade0); extraction factor E6 (E-20261115-174214-74becdd); lead's independent extraction on L32p agreeing to three digits (E-20261119-150238-b81e33f) | PASS |
| C3 | Interface proposals submitted | noise/NOISE_SPEC.md, noise/RNG_REQUIREMENTS.md, codebase/DESIGN_REVIEW.md 9 and 11, spec/SPEC.md 10; outbox 20261115T1410Z to core (initial slice, diagnostics, card build, noise results), answered by core (message scalar2-ready; interface proposal tracks/core/interfaces/scalar_field_2.md on core/scalar-2); outbox of 2026-11-19 (release request, A4 proposal) | PASS |
| C4 | Baseline data and figures | ladder/results/final, final2 (time-matched pairing), floor, a6, a6_64, l5, seed2, a12 and ladder/fig/ (runs EVIDENCE.md 1 and 7); analysis/fig; g1verify/fig (verifier); stage/G1/fig/fig_lead_check.png; stage/review3/fig (lead of batch 2a) | PASS |
| C5 | Interface documents | noise/NOISE_SPEC.md and RNG_REQUIREMENTS.md (track); coord/INTERFACES/ scalar field of core-v0.3; core's tracks/core/interfaces/scalar_field_2.md (branch core/scalar-2, written to SPEC 5.3 and 10; not yet released) | PASS |
| C6 | The power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge | spectrum MET and verified (A2: 1.21e-4 at 256^3 for /n/ <= 32, verifier the same; second seed 2.12e-4, 1.208e-4 over typical amplitudes); freezing MET and verified (A3: ratio within 2.4e-6 to 4.6e-6 of full MS, drift 1.4e-4 per e-fold, FLRW-lattice equation -0.052 per e-fold excluded); constraints converge in the sheet's sense, verified (odd part order 5.5-5.96, halving 2.000; even part halving 3.986-4.000, N-independent); but the owner's accepted A4 fails in its strict form in P1's set-up (odd/even up to 745-869 at N = 32-128, 25 at the last time-matched dump of N = 256) and A4' awaits orch's ruling (outbox 20261119T151727Z, repeated 2026-11-21 with the verifier's recommendation). STATUS.md, VERIFIER.md | OPEN |
| C7 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | applied: continue to G1 and G2; SCOPE 4 choices used (Courant 0.25, now justified by A6; level 0; thresholds A1-A7 as written, A4 failure kept on record); downgrade (SCOPE 4 item 5) not triggered: A3 passes, 0.503 card-hours per 256^3 SR realisation against 5 | PASS |
| C8 | Schematic: Updated architecture | package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/schem_architecture.py modified and not committed; no committed updated schematic yet | OPEN |
| C9 | Schematic: Data-flow diagram | package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/schem_dataflow.py written, not committed, figure not produced in a registered run | OPEN |
| C10 | Data figure: Baseline results | ladder/fig/final/fig_spectrum.png, fig_a2_modes.png, fig_a3_freezing.png; wave 3: ladder/fig/final2/fig_a4_paper.png, fig/a6_64/fig_a6.png, fig/l5/fig_l5.png, fig/seed2/fig_seed2.png; all looked at by the lead (2026-11-19, 2026-11-21) | PASS |
| C11 | Data figure: Validation figures for the analysis pipeline | analysis/fig/fig_t2_extraction.png, fig_plane_constraint_ratios.png; stage/G1/fig/fig_lead_check.png (script stage/G1/scripts/lead_check.py, run E-20261119-150238-b81e33f); all looked at | PASS |
| C12 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, VERIFIER.md, REVIEW.md (pointer to ../REVIEW-wave2.md and ../REVIEW-wave3.md), STATUS.md (criteria table); scoping text spec/scope/SCOPE.md | PASS |
| C13 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | style: ladder, verifier and lead figures use copies of harness/style/figstyle.py, every PNG looked at; the verifier has one script per figure (g1verify/scripts/fig_v1.py ... fig_v7.py); package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/fig_sr_{modes,freezing,constraints,order}.py written, not committed, not run as a registered run | OPEN |
| C14 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): G0 schematics exist; updated architecture, data-flow and timeline scripts modified/new and uncommitted | OPEN |
| C15 | Working note written with /paper-writing; its manuscript checker passed with --compile | package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/main.tex is the G0 note v0; G1 sections not written; no G1 ledger | OPEN |
| C16 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | VERIFIER.md (copy of g1verify/VERIFIER.md): fresh-context helper g1verify, own code from the raw dumps, verdicts V1-V7 committed (db88f631) before it read the track's numbers (c43e050c); runs EVIDENCE.md 6; the lead reran its analyses from the registered outputs (../REVIEW-wave3.md). Its 'every number of the Supplemental Material recomputed' part: no G1 ledger exists yet (note package unfinished), so the ledger recomputation is open with C15 | PASS |
| C17 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept with manifests: E-20261115-172521-e098160, -170651-885fc6e, -171628-1737ebe, -171633-f574079, E-20261119-145853-ef835c2; wave 3: E-20261121-030415-22d518b, -031936-16d6ae5, -034609-f573ddc, -063758-d643396 (lead); refuted predictions on record: ladder P5, entry 6, entries 16, 19-22 (eight in wave 3), g1verify entries 4-6, owner A4 strict (ladder/JOURNAL.md, g1verify/JOURNAL.md, JOURNAL.md); REVIEW-wave3.md section 1 lists them | PASS |
| C18 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten, JOURNAL.md appended and RISKS.md updated by the lead of batch 2a on 2026-11-21 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T06:57:09Z, clean export of `5aa8bcd4767d`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 17 uncommitted paths: commit them first (tracks/E-stoch-inf/note/scripts/common.py, tracks/E-stoch-inf/note/scripts/fig_background.py, tracks/E-stoch-inf/note/scripts/ledger.py, tracks/E-stoch-inf/note/scripts/run_all.py, tracks/E-stoch-inf/note/scripts/schem_architecture.py) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 5aa8bcd4767d (HEAD) in /data/haiyangw/nrpic/scratch/E-stoch-inf/tmp/stage-verify/E-stoch-inf-G1-5aa8bcd-20261121T065649Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: spec/scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 2 of 131 runs have problems |
| run-notes | WARN | 30 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 37 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 14 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_background.* | note/scripts/fig_background.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_deltan.* | note/scripts/fig_deltan.py | data | to be confirmed by the session |
| note/figures/fig_freezing.* | note/scripts/fig_freezing.py | data | to be confirmed by the session |
| note/figures/fig_noise.* | note/scripts/fig_noise.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/E-stoch-inf/stage/G1/VERIFIER.md` present; its first lines:

> # Independent verification of Track E's G1 material (slow-roll ladder 32^3-256^3)
> 
> Verifier: helper g1verify of E-stoch-inf (decision 0016 item 4; item C16 of the G1
> checklist), a fresh reader given the artefacts and not the conclusions. Two sessions:
> 2026-11-20 14:21-14:35 PST (cut by the five-hour limit) and 2026-11-20 18:55 PST onwards
> (2026-11-21 UTC). Worktree commit at start: bc5e277 (session 1), 36824dc (session 2, after
> `git merge main`).
> 
> Read before the verdicts: `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and section 9.8 (the
> G1 criterion); decisions 0010, 0013 (Track E), 0016-0020; `spec/scope/SCOPE.md` section 4
> item 4 (definitions and thresholds A1-A8; the amendment note under A2 quotes two ladder
> numbers, 6.2e-3 and 1.2e-4 at 256^3, which I could not avoid seeing) and section 4b (A4',

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
- `E-20261121-030415-22d518b`: failed (exit 1), g1verify V7 (A7, cost): bit-identity of the noise unit-test dumps (U1/U2/U3 MeshBlock layouts on the card, U2 vs U4 restart on processors and card) on the files themselves, sha256 against the runs; card vs processor for information; cost of one 256^3 realisation from the manifests (JOURNAL entry 3, P-V7)
- `E-20261121-031936-16d6ae5`: failed (exit 1), g1verify V4/V5 analysis from my constraint pass E-20261121-030657-c1afe38: odd/even parts of H, M over <[H]>, <[M]>, dominance, halving factors above the floor, negative controls, record maxima and halving factors, strict A4 and A4' tests, spatial order L32-L256, floor against N (JOURNAL entry 3, P-V4, P-V5)
- `E-20261121-034609-f573ddc`: failed (exit 1), ladder item (c): L5 single-kick analysis of the eleven card runs K1p ... N1m of E-20261121-025643-02526ff (parts in s cell by cell, kick reference, verdicts PL1-PL3 of JOURNAL 14)
- `E-20261121-063758-d643396`: failed (exit 1), lead review wave 3 (batch 2a), checks LW1-LW6 with the lead's own code on the raw dumps: seed 2 of P256 (A1-A3), P256 odd/even of H time-matched and index-paired, record maxima, A6 at 64^3, L5 second order and first-order M, L5 step test at 32^3; predictions in JOURNAL entry 2026-11-21T06:35Z
- `E-stoch-inf-20261115-125316-dafadc4`: failed (exit 1), V2: quadratic inflation m = M_Pl, phi_in = phi_UV = sqrt42 (2206.11234 Fig. 2): Monte Carlo (direct and importance sampling) vs closed-form characteristic function, BDF2 survival solver, moment recursion; pole structure
- `E-stoch-inf-20261115-131526-629fed8`: failed (exit 1), T-N6 of noise/JOURNAL.md: calibration of the A3 decisions (KS of |w|^2 and arg w, fourth moment) on correct amplitudes, 2000 seeds of the base case; single-decision calibration and family-wise false-alarm rate per validation

## Open risks


Rewritten by the lead on 2026-11-15 at the G0 package; updated by the lead on 2026-11-19
(wave 2b) after the slow-roll ladder, the G0 verifier (`stage/G0/VERIFIER.md`) and the review
`stage/REVIEW-wave2.md`; updated by the lead of batch 2a on 2026-11-21 after the G1 verifier
(`stage/G1/VERIFIER.md`), the wave-3 ladder items and `stage/REVIEW-wave3.md`. Sources: `spec/scope/SCOPE.md` (sections 3, 4, 4b, 8),
`codebase/DESIGN_REVIEW.md`, `langevin/README.md`, `noise/NOISE_SPEC.md`, `ladder/README.md`.
Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The SR results of G1 were made with core's tested-branch executable `core/scalar-2` (a58e95b), not a release | low (scalar-2 is in release core-v0.4 since 2026-11-21) | medium | release processor build = scalar-2 word for word on L32p/L32m, all dumps and records (lead, run E-20261121-064707-77ec326) | rerun P256 on the release card build (0.5 card-hours) against E-20261115-172618-f948386; until then the card results are tied to the branch executable |
| R2 | A defect in core's stochastic hook that the tests cannot see | low | high | A6 at 32^3 and 64^3 (orders 3.82-4.10); L5 single kick (wave 3): H second order to 1e-6 in the halving factor, the kick's projector term equal to the one-step reference within 1.2 percent, remaining first-order M the fourth-order time error (A/B 15.5-19.5), no first-order stage-timing defect (runs E-20261121-034645-02a463e, -040015-436a615; lead LW5-LW6) | keep the sign-flip control in every set-up; "L5 never run" is closed |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping and tolerances open (SPEC 8) and print wrong formulas (SPEC 9) | certain | medium | SPEC 8, 9; kb claims 603-609 | per-mode acceptance needs no published tolerance; E6 (extraction factor 1/4) now tested by run E-20261115-174214-74becdd; the P2 initial-condition equation is "eq. (17)" in our older texts, but the source numbers it 23rd (SPEC 5.3 note) [TO VERIFY against the PDF] |
| R4 | The freezing criterion fails for a reason other than a defect | low | high (downgrade trigger) | A3 drift after N_k + 4 | SR passed on every rung (drift 1.4e-4 per e-fold against 2.5e-3); USR not yet run |
| R5 | Unit conversion G = 1 against Mpl = 100 | low (was medium) | high if wrong | A1 | A1 passes at 1e-11 on every rung (ladder; lead's check run E-20261119-150238-b81e33f) |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541); first-order truncation part at four cells per wavelength | medium | medium | M/[M] record, odd part of M | A4 fails in its strict form in P1's set-up already in SR (first-order part from ln(N/8) e-folds); proposal A4' (SCOPE 4b) to orch; USR run by the wave-3a usr package |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 separate-universe Langevin overestimates the variance by 42-45 percent | medium | medium | sensitivity scan L9: package `window` ran its linear reference (E-20261120-222802-bffb812: prediction at N_f window-independent to 1.6e-14) and its card job (4740, E-20261120-222424-0eb754b), not yet analysed | compare NR with the sigma <= 0.01 reference only (A8) |
| R9 | Tail statistics need many realisations: 1e3 realisations at 256^3 cost about 500 (SR) to 630 (USR) card-hours at the measured 0.50 card-hours per SR realisation | high for G3 | high for S11 item 2 | measured cost (run E-20261115-172618-f948386) | smaller boxes, importance sampling, or the downgrade path; scope of G3 decided at G2 (decision 0013) |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build slow (1.2e4-1.35e4 zone-cycles/s serial); cold dumps at 128^3-256^3 read through a memory map at a few MB/s when the disk is busy (lead's rerun E-20261119-145853-ef835c2 stopped) | certain | low | | N = 32 on processors; analyse large dumps right after the card job (page cache) or read them sequentially |
| R13 | Budget: 10 card-hours to the next gate; G1 used 1.96 (`nrpic-run budget`); the cut packages' two card jobs (4740 window, 4742 usr) ran 0.38 + 0.16 card-hours with manifests still "submitted" (0.90 reserved for G2) | low | medium | `harness/bin/nrpic-run budget` | close those two manifests with `nrpic-run finish` in their packages; Courant 0.25 justified by A6 |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` | happened, fixed | low | `nrpic-run budget` | statuses normalised; decision 0016 item 3 |
| R15 | USR ends at the border of diffusion domination (verifier weak point 3): classical drift per e-fold equals H/2pi at N* + 8.3 (ratio 0.98), Delta_R reaches 1 at 64 dk, one H/2pi kick moves the end of USR by about one e-fold; a delta-N end surface at N* + 10 sits just past the stationary inflection point | high for G2/G3 | high for the validity of linear-noise level-0 runs and of the delta-N reference | verifier V2b (run E-20261115-180056-d62ee5a: f_NL 0.011, response near-linear in the 256 box) | state the validity window at G2; do not enlarge the box or move the noise cut later without a level-1 comparison; place the delta-N end surface away from the inflection point |
| R16 | The double-precision rounding floor of the constraints grows as N^2.5 (6e-13 of <[H]> at 256^3 half an e-fold after N*) and limits what 256^3 shows during the first e-folds | certain | low (still 1e2 below P1's 1e-10) | odd part not scaling with s | the verifier measured three properties of rounding (does not scale with s; equal in odd and even parts; non-scaling parts in the ratio sqrt(17/5) of four independent noises) [VERIFIED, g1verify V5]; size and N^2.5 law [JUDGEMENT]; no run in another precision |
| R17 | Acceptance criteria reworded after the data (A4', A5', SCOPE 4b) | happened | medium (credibility of the gate) | orchestrator's ruling | the strict A4 failure stays on record; the fresh-context verifier recommends A4' with (d) on maxima and the floor named as the non-scaling part (`stage/G1/VERIFIER.md`); request repeated to orch 2026-11-21 |
| R18 | The absolute constraint levels are 40-100 times below P1's statements (proper ~1e-10, control ~1e-5, P1:538-541) while the ratio control/proper matches (verifier weak point 7) | open | medium (a definition mismatch would change the A4' magnitude clause (c)) | `stage/G1/VERIFIER.md` 7 | [TO VERIFY]: compare the definition of [H] and of the box statistic in P1 with core's record (`coord/INTERFACES/scalar_field_2.md`); no run needed |
| R19 | Packages cut by the usage limit leave uncommitted work and finished card jobs without analysis (wave 3: note, a4res, usr, window; usr's pre-registration addendum, entry 10 of `usr/JOURNAL.md`, written 22:35Z before job 4742 started at 22:36:46Z, is still uncommitted) | happened | medium (provenance of predictions; card time spent without result) | `git status`, `nrpic-run status` | the next session of each package commits its own files first, then analyses the finished jobs; leads leave them alone (batch 2a) |
| R20 | Frontier items from the knowledge base (orch message 20261120T221329Z): hidden higher-derivative spikes of inflection potentials (2606.28005), UV sensitivity of mean-field backreaction to Bunch-Davies UV modes (2610.26669), non-Markovian noise (2602.11652, 2605.00476) | medium | medium for the USR acceptance discussion (G2) | `coord/FRONTIER.md` | check the test potential's derivatives and state the UV dependence in the G2 acceptance text; Markovian noise stays the reproduction's choice (P1) |

## Decision requested from the group

G1 of E-stoch-inf is not met, and the package is not complete for the independent gate review of decision 0016 item 4. Met and confirmed by the fresh-context verifier (VERIFIER.md, V1-V7) and by the lead's reruns: the slow-roll power spectrum agrees with the analytic result (A2 1.21e-4 for |n| <= 32 at 256^3 in P1's set-up; a second realisation 2.12e-4), super-horizon modes freeze by the criterion of arXiv:2606.14853 (A3 ratio within 5e-6 of the full MS, drift 1.4e-4 per e-fold), the constraints converge in the track sheet's sense (odd part order 5.5-5.96, halving 2.000; second-order part halving 3.99-4.00 and N-independent); A1, A6 (also at 64^3), A7 (also on the G1 executable), and the single-kick test L5 pass. Not met: the owner's A4 as accepted in decision 0013 fails in its strict form in P1's set-up for two measured reasons; the ruling on A4' is asked of the orchestrator (outbox 20261121T064752Z, with the verifier's recommendation). Missing products: the updated architecture and data-flow schematics, one script per data figure and the G1 sections of the note (package note, cut on 2026-11-20). The SR set-up is in release core-v0.4 since 2026-11-21 and the release processor build reproduces the scouting runs word for word at 32^3 (run E-20261121-064707-77ec326). Asked: the A4' ruling; after the note package, an independent gate review.

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

## Notes of the lead of batch 2a on this report (2026-11-21)

- `verify --no-checksums` on 5aa8bcd4 (after merging main): FAIL on two checks, both caused by
  the wave-3 packages that the usage limit cut on 2026-11-20 and that are not G1 material:
  `clean` (17 uncommitted files of `note/`, `a4res/`, `usr/`, left alone by this lead as the
  batch instructions ask; `HANDOFF.md` lists them) and `runs` (the two G2 card jobs of `usr`
  and `window`, E-20261120-222621-ba66218 and E-20261120-222424-0eb754b, finished on the card
  but their manifests still read "submitted"; their packages close them). Every G1 check
  passes: export, size, package, note-pdf, style, fig-script, min-figs, status, rerun (7 of 7),
  compare (14 of 14), regenerate.
- Output checksums of the G1 analysis runs were checked where the lead reran from them
  (`nrpic-run verify` PASS on the verifier's passes E-20261120-223154-d42de1a,
  E-20261121-025750-d1b6139, -030657-c1afe38, -031049-27cdc06); the full checksum pass of
  verify reads about 150 GB and was not run.
- The verifier's report is in this directory (`VERIFIER.md`); its nine numerical disagreements
  and eleven weak points, with what the track does about each, are in `../REVIEW-wave3.md`
  section 2. `STATUS.md` carries the corrected numbers (P256 odd/even 25 time-matched, not 385;
  A1 maxima 2.0e-12, 8.6e-12, 3.6e-12; control separation 89-179 at its minimum).
- The figures relied on in wave 3 are listed in `EVIDENCE.md` section 9; all looked at.
