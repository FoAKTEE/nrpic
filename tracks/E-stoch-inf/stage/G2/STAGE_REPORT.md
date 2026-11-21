# Stage report: E-stoch-inf G2

Date: 2026-11-21 · branch `track/E-stoch-inf` at `acdcb8c15bfc` · checklist
`tracks/E-stoch-inf/stage/G2/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/E-stoch-inf/G2-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- 19 checklist items not PASS or NA: C1 OPEN, C2 OPEN, C3 OPEN, C4 OPEN, C5 OPEN, C6 OPEN, C7 OPEN, C8 OPEN, C10 OPEN, C11 OPEN, C12 OPEN, C13 OPEN
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G2/STAGE_REPORT.md` | present |
| `stage/G2/EVIDENCE.md` | present |
| `stage/G2/OPEN.md` | present |
| `stage/G2/CHECKLIST.md` | present |
| `stage/G2/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G2/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `spec/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G2 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The code paths used by the track pass their tests of §10 | SR (G1) and USR scouting pass their rows (ladder/, usr/); the release card build core-v0.6 is now being run on both (g2prod: P256v6 E-20261121-202935-31520bc, USR chains); judged when they have run. | OPEN |
| C2 | Three-way convergence in particle number, mesh spacing, and gauge or boundary | no particles before the hand-over (NA for particle number); mesh: U-R (256 vs 320 at fixed modes, SCOPE 4c), queued in g2prod; gauge: geodesic slicing only (RISKS R6) - to be stated at the package. | OPEN |
| C3 | Constraints behave | U-A4'(a) halving with the floor of SCOPE 4c at 256^3 (U256hp/hm queued), U-A4'(c) records on every release run, U-A4'(d) control (U256nc queued); scouting: group 1 even factors 3.987-4.001 (E-20261121-080134-a0cc3eb). | OPEN |
| C4 | A first minimal full-GR kinetic run | Track E has no kinetic matter before the field-to-particle hand-over (S11 subsequent work); proposed NA at G2 [JUDGEMENT], for orch to confirm. | OPEN |
| C5 | Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md) | — | OPEN |
| C6 | Reproducibility package | — | OPEN |
| C7 | The USR case is reproduced | criteria fixed in spec/scope/SCOPE.md 4c (commit 43dcc9cc) before production; release runs queued (g2prod/JOURNAL.md entry 1); scouting pair U256/U256m passes U-A2' at 1.09e-4 (E-20261121-101756-6bffd0c). | OPEN |
| C8 | Sensitivity to window-function parameters and resolution | window: U-W met by the scan (E-20261121-154733-0d1fbda; lead's rerun E-20261121-203008-f104a3e, stage/REVIEW-wave3.md Part C); resolution: U-R pending (U320ap/am in g2prod). | OPEN |
| C9 | Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013) | G0 decision: continue (coord/GATES.md 2026-11-20); G1 signed 2026-11-21; G2 within the scope of SCOPE section 4 and 4c. | PASS |
| C10 | Schematic: Verification ladder | — | OPEN |
| C11 | Data figure: Convergence figures (one each for particle number, mesh, gauge) | — | OPEN |
| C12 | Data figure: Constraint norms against time | — | OPEN |
| C13 | Data figure: At least one multi-scale slice mosaic with zoom boxes | — | OPEN |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | — | OPEN |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | — | OPEN |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | — | OPEN |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | — | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | — | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | — | OPEN |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | — | OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify E-stoch-inf G2`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_background.* | note/scripts/fig_background.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_deltan.* | note/scripts/fig_deltan.py | data | to be confirmed by the session |
| note/figures/fig_freezing.* | note/scripts/fig_freezing.py | data | to be confirmed by the session |
| note/figures/fig_noise.* | note/scripts/fig_noise.py | data | to be confirmed by the session |
| note/figures/fig_sr_constraints.* | note/scripts/fig_sr_constraints.py | data | to be confirmed by the session |
| note/figures/fig_sr_freezing.* | note/scripts/fig_sr_freezing.py | data | to be confirmed by the session |
| note/figures/fig_sr_modes.* | note/scripts/fig_sr_modes.py | data | to be confirmed by the session |
| note/figures/fig_sr_order.* | note/scripts/fig_sr_order.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G2/VERIFIER.md`, decision 0016).

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
(`stage/G1/VERIFIER.md`), the wave-3 ladder items and `stage/REVIEW-wave3.md`; updated by the lead of batch 3 on 2026-11-21 after the note and usr packages (`stage/REVIEW-wave3.md` Part B). Sources: `spec/scope/SCOPE.md` (sections 3, 4, 4b, 8),
`codebase/DESIGN_REVIEW.md`, `langevin/README.md`, `noise/NOISE_SPEC.md`, `ladder/README.md`.
Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The SR results of G1 were made with core's tested-branch executable `core/scalar-2` (a58e95b), the USR scouting card runs with `core_scalar-3` 5cc2821, not releases | low (both are in release core-v0.6) | medium | release processor build = scalar-2 word for word on L32p/L32m (run E-20261121-064707-77ec326); core's card check of core-v0.5 on the s3g and usr decks | P256 again on the release card build core-v0.6: run E-20261121-202935-31520bc (Slurm 4828, submitted 2026-11-21, prediction P256v6 of `g2prod/JOURNAL.md` entry 1); all G2 production runs of `g2prod` use the release core-v0.6 card build |
| R2 | A defect in core's stochastic hook that the tests cannot see | low | high | A6 at 32^3 and 64^3 (orders 3.82-4.10); L5 single kick (wave 3): H second order to 1e-6 in the halving factor, the kick's projector term equal to the one-step reference within 1.2 percent, remaining first-order M the fourth-order time error (A/B 15.5-19.5), no first-order stage-timing defect (runs E-20261121-034645-02a463e, -040015-436a615; lead LW5-LW6) | keep the sign-flip control in every set-up; "L5 never run" is closed |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping and tolerances open (SPEC 8) and print wrong formulas (SPEC 9) | certain | medium | SPEC 8, 9; kb claims 603-609 | per-mode acceptance needs no published tolerance; E6 (extraction factor 1/4) now tested by run E-20261115-174214-74becdd; the P2 initial-condition equation is "eq. (17)" in our older texts, but the source numbers it 23rd (SPEC 5.3 note) [TO VERIFY against the PDF] |
| R4 | The freezing criterion fails for a reason other than a defect | low | high (downgrade trigger) | A3 / U-A3 drift after N_k + 4 | SR passed on every rung (drift 1.4e-4 per e-fold against 2.5e-3); USR U-A3 passes at 64^3-256^3 (0.9923-1.0016 single run, 0.99992 odd part; runs E-20261121-084815-63462b8, -101756-6bffd0c) |
| R5 | Unit conversion G = 1 against Mpl = 100 | low (was medium) | high if wrong | A1 | A1 passes at 1e-11 on every rung (ladder; lead's check run E-20261119-150238-b81e33f) |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541); first-order truncation part at four cells per wavelength | happened as expected | medium | M/[M] record, odd part of M | reproduced: <abs M/[M]> 2.5e-2 at cN 6.6, 2.1e-3 at N_f (U256); late it is an s-independent floor over a magnitude proportional to the amplitude, not an error of the solution (usr entries 12, 15); strict A4 failed on record in SR, A4' adopted (decision 0021); for USR U-A4' proposed to orch (outbox 20261121T131021Z) |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 separate-universe Langevin overestimates the variance by 42-45 percent | window: low (scan done); gauge: medium | medium | scan L9 analysed (E-20261121-154733-0d1fbda; rerun by the lead E-20261121-203008-f104a3e): USR spectrum at N_f window-independent within numerical error (<= 1.9e-4 to k_max/2, <= 9.1e-3 to k_max); late constraint records depend on sigma (x0.14-x21.7, W6 refuted) | the window result is the G2 criterion U-W (SCOPE 4c); no further window run; compare NR with the sigma <= 0.01 reference only (A8); gauge: geodesic slicing only (R6) |
| R9 | Tail statistics need many realisations: 1e3 realisations at 256^3 cost about 500 (SR) to 620 (USR) card-hours | high for G3 | high for S11 item 2 | measured: 0.503 card-hours per SR realisation (E-20261115-172618-f948386), 0.617 per USR realisation with 21 dumps of 2.95 GB (U256, E-20261121-075255-8cf90e7; sacct 37:00; 1.30 s per step, 19.6 GB), about 0.58 without dumps | smaller boxes, importance sampling, or the downgrade path; scope of G3 decided at G2 (decision 0013) |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build slow (1.2e4-1.35e4 zone-cycles/s serial); cold dumps at 128^3-256^3 read through a memory map at a few MB/s when the disk is busy (lead's rerun E-20261119-145853-ef835c2 stopped) | certain | low | | N = 32 on processors; analyse large dumps right after the card job (page cache) or read them sequentially |
| R13 | Budget: 10 card-hours toward G2 (decision 0014 row E); G2 used 1.77 at 2026-11-21 12:23 PST; the g2prod ladder needs about 8.0 at actual cost, and nrpic-run counts a running chain at its ceiling (1.97 or 2.95) | certain | medium (the last three g2prod runs wait for closed runs or a larger allotment) | `harness/bin/nrpic-run budget`; sequencer log `scratch/E-stoch-inf/g2prod_seq/seq.log` | the sequencer retries refused submissions every 15 min; raise to 20 requested of orch (outbox 2026-11-21 batch 5), also for a 384^3 pair (about 6.5) |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` | happened, fixed | low | `nrpic-run budget` | statuses normalised; decision 0016 item 3 |
| R15 | USR ends at the border of diffusion domination (verifier weak point 3): classical drift per e-fold equals H/2pi at N* + 8.3 (ratio 0.98), Delta_R reaches 1 at 64 dk, one H/2pi kick moves the end of USR by about one e-fold; a delta-N end surface at N* + 10 sits just past the stationary inflection point | high for G2/G3 | high for the validity of linear-noise level-0 runs and of the delta-N reference | verifier V2b (run E-20261115-180056-d62ee5a: f_NL 0.011, response near-linear in the 256 box) | state the validity window at G2; do not enlarge the box or move the noise cut later without a level-1 comparison; place the delta-N end surface away from the inflection point |
| R16 | The double-precision rounding floor of the constraints grows as N^2.5 (6e-13 of <[H]> at 256^3 half an e-fold after N*) and limits what 256^3 shows during the first e-folds | certain | low (still 1e2 below P1's 1e-10) | odd part not scaling with s | the verifier measured three properties of rounding (does not scale with s; equal in odd and even parts; non-scaling parts in the ratio sqrt(17/5) of four independent noises) [VERIFIED, g1verify V5]; size and N^2.5 law [JUDGEMENT]; no run in another precision |
| R17 | Acceptance criteria reworded after the data (A4', A5', SCOPE 4b; for USR U-A2', U-A4') | happened | medium (credibility of the gate) | orchestrator's rulings | A4' adopted by decision 0021; for G2 the definitions (floor, clause on the maxima, U-R, U-S, U-W) are fixed in SCOPE 4c (commit 43dcc9cc) before any G2 production run, as decision 0023 item 1 asks; the strict forms stay failed on record |
| R18 | The absolute constraint levels are 40-100 times below P1's statements (proper ~1e-10, control ~1e-5, P1:538-541) while the ratio control/proper matches (verifier weak point 7) | open | medium (a definition mismatch would change the A4' magnitude clause (c)) | `stage/G1/VERIFIER.md` 7 | [TO VERIFY]: compare the definition of [H] and of the box statistic in P1 with core's record (`coord/INTERFACES/scalar_field_2.md`); no run needed |
| R19 | Packages cut by the usage limit leave uncommitted work and finished card jobs without analysis (wave 3: note and usr finished in batch 2b; a4res still has three untracked scripts; window's job ran, not analysed; usr entry 10 was first committed after the job it amends had run) | happened | medium (provenance of predictions; card time spent without result) | `git status`, `nrpic-run status` | the next session of each package commits its own files first; leads leave them alone; entry 10 rescued no verdict (`stage/REVIEW-wave3.md` B1) |
| R20 | Frontier items from the knowledge base (orch message 20261120T221329Z): hidden higher-derivative spikes of inflection potentials (2606.28005), UV sensitivity of mean-field backreaction to Bunch-Davies UV modes (2610.26669), non-Markovian noise (2602.11652, 2605.00476) | medium | medium for the USR acceptance discussion (G2) | `coord/FRONTIER.md` | check the test potential's derivatives and state the UV dependence in the G2 acceptance text; Markovian noise stays the reproduction's choice (P1) |
| R21 | The lockstep mode-function record integrates from N* with the run's step and carries RK4's phase error k^5 dt^4/600 into the injected top shells (2.55e-3 at k = 64 dk, 256^3) | certain in P1's set-up | low for U-A2 (k <= 32 dk: below 8e-5), medium for the top-shell spectrum (U-A5 6.7e-3) | usr entry 14.2 (L1: 0.973-1.023 of the law on 2934 shells) | request to core to sub-step the record (outbox 20261121T131020Z); until then quote top-shell numbers with this error |
| R22 | Late in the 256^3 USR pair the momentum parts are equal and flat at 1.6e-13-1.9e-13 absolute, seven times the 128^3 floor; cause not named | open | low (after USR, below the record's 2e-3) | usr entry 15 | the halving pair at 256^3 (U256hp/hm, s = +-1/2) is queued in `g2prod` (last but one; waits for the allotment) |
| R23 | Unattended card runs: the g2prod sequencer (setsid, pid in `scratch/E-stoch-inf/g2prod_seq/pid`) submits through nrpic-run, which refuses a dirty `g2prod/` and commits each manifest on track/E-stoch-inf; a session that edits `g2prod/` without committing blocks it; a chain preempted more often than its segment ceiling ends FAILED | medium | medium (card time idle, not lost) | `seq.log`, `state.tsv`, `scripts/submit_chain.sh --status <rundir>` | keep `g2prod/` committed; a FAILED chain resumes from its newest restart (HANDOFF); restart exactness checked on processors (R0, run E-20261121-202941-da16544) |
| R24 | 320^3 (and 384^3) never ran: memory and step time are scaled from 256^3 (U320 1.6 card-hours estimated) | medium | low (a chain can be stopped) | timing job E-20261121-202929-43dcc9c (Slurm 4827, 40 steps at 256, 320, 384) | read the timing before U320ap starts (third in the queue); stop the sequencer if 320^3 does not fit |

## Decision requested from the group

not ready: G2 production runs queued (g2prod); criteria fixed in SCOPE 4c
