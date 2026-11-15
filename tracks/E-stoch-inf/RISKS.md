# RISKS of E-stoch-inf

Rewritten by the lead on 2026-11-15 at the G0 package. Sources: `spec/scope/SCOPE.md`
section 3 (R1-R13 of the spec helper), `codebase/DESIGN_REVIEW.md`, `langevin/README.md`,
`noise/NOISE_SPEC.md`, and the lead's checks (`stage/G0/REPORT.md`). Labels as in the brief.

| Id | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| R1 | The reproduction waits for core: initial slice at N* (SPEC 5.3), constraint and R^NR diagnostics, a card build of `core/scalar-field` are not there yet (field, kicks and noise are, at 836ac86) | certain | high on the G1 date | `git log core/scalar-field`; outbox replies | requests in `outbox/`; the track supplies mode tables, references and the validators; nothing else waits |
| R2 | A defect in core's stochastic hook that the generator tests cannot see (kick signs, stage bookkeeping of the lockstep mode data) | medium | high | single-kick test L5 and temporal test L6 of DESIGN_REVIEW 8.1 | L5 with the sign flip as negative control (P1:541); L6 at three Courant factors |
| R3 | The papers leave the Courant factor, run lengths, Bunch-Davies form, noise stepping, binning and tolerances open (SPEC 8) and print wrong formulas (SPEC 9: delta Pi of the initial data, draw normalisation, extraction factors, 4 pi in the K equation) | certain | medium | SPEC 8, 9 | per-mode acceptance (A2, freezing) needs no published tolerance; errata checked by runs and by the lead's derivation (JOURNAL L-I) |
| R4 | The freezing criterion fails because of the level-0 backreaction or the window, not because of a defect | low | high (downgrade trigger) | per-mode drift after N_k + 4 against the full-MS reference | P1 reports level 2 vs 0 changes the spectrum by at most 1e-4 (P1:520); a failure is first checked at level 1 before the downgrade is invoked |
| R5 | Unit conversion G = 1 against Mpl = 100 of the papers | medium | high if wrong | A1 box means against the Friedmann reference | SPEC 2.5 mapping; core's FLRW test and A1 catch a wrong 8 pi |
| R6 | Geodesic slicing breaks down where perturbations collapse; USR outliers R ~ 10 (P1:534), an 11-sigma event under the band reference (`langevin/README.md`) | low for the test cases, high for science | medium | X contrast, outliers of R^NR | stop at the published N_f; a gauge study belongs to G2 |
| R7 | Momentum constraint ~ 1e-2 late in USR (P1:541) | medium | medium | M/[M] history | accept the published level at G2, resolution study |
| R8 | Window (s, sigma) and gauge dependence (brief 462); sigma = 1 at horizon crossing; separate-universe Langevin with sigma = 1 overestimates the variance by 42-45 percent (runs E-stoch-inf-20261115-130137/-130139-176cdd6) | medium | medium | sensitivity scan L9 | compare NR with the sigma <= 0.01 reference only (SPEC A8) |
| R9 | Tail statistics need many realisations: 1e3 realisations at 256^3 cost 400 to 5000 card-hours (0.4-5 each, SPEC 11.2) | high for G3 | high for S11 item 2 | cost per realisation measured at G1 | smaller boxes, importance sampling, or the downgrade path; Track A gets delta-N statistics now from `langevin/` |
| R10 | Competition with the group of the formalism (P1:587 announces the same science) | high | medium | arXiv listings of the authors | target what they leave open: tail statistics against delta-N, hand-over to EMD |
| R11 | The stochastic formalism itself is debated (brief 264) | medium | affects science, not the reproduction | literature | keep level 0 and level 1 as variants and state the dependence |
| R12 | Processor build too slow for N >= 64 tests (1.35e4 zone-cycles/s, run E-20261115-135218-bdf4710); the 64^3 x 300 unit-test base case costs 95 min per run | certain | low | | scaled tests on processors (N = 32); 64^3 and above on a card build |
| R13 | Budget: 10 card-hours to the next gate (decision 0006) | medium | medium | `harness/bin/nrpic-run budget` | Courant factor 0.25 (G0 decision); 0.025 only if L6 shows a dependence |
| R14 | Harness: hand-written run manifests broke `nrpic-run budget` (status "failed (exit 1)") | happened, fixed | low | `nrpic-run budget` | statuses normalised (commit after e303538); outbox note to orch |
