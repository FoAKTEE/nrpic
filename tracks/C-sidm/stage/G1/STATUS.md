# C-sidm G1: status of each criterion

State at the end of the lead session of 2026-11-15 (branch `track/C-sidm`). Criteria: the
track sheet (charter 9.6: "G1: all tests of C-pre-1 pass; the baseline is reproduced") and
the common G1 evidence of charter 9.2 ("baseline results obtainable without the NRPIC
coupling; the analysis pipeline validated on them; interface proposals submitted").
Decision 0010 turns C-pre-1 and C-pre-2 into specifications, references and tests by the
track and an implementation by core. Run ids are under `tracks/C-sidm/runs/`; the review
runs of the lead are C-sidm-20261115-131130-3077a99 (cross-checks X1-X5) and
C-sidm-20261115-131135-3077a99 (reruns of every package); see `../G0/REVIEW.md`.

**Verdict: G1 NOT MET.** The baseline and the specifications are done and independently
checked; core committed the operator at the end of this session (3436846, untested by core),
and its kernels pass the track's T0; the box tests T0b-T12 have not run.

## 1. Track-specific criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | All tests of C-pre-1 pass (collision operator) | NOT MET: T0 passed, the rest waits for core | What the track specified: `collide/SPEC.md` (algorithm, options, outputs, curved-spacetime frame), `collide/TESTS.md` (T0-T12, pass criteria fixed before any run), `collide/REFERENCES/` (62 tests pass, rerun in -131135; closed-form rate checked by an independent 3D quadrature to 5e-7, X1), 209 kernel test vectors, box analysis tested on synthetic data and on the collisionless AthenaK run T6-0 (run C-sidm-20261115-121302-313d399, reproduced byte for byte at its commit, run -132327-eab8e41). What core implemented: commit 3436846 on `core/collisions` (13:19Z): `tracks/core/interfaces/collisions.md` (design, adopts SPEC eq. P, the Moller speed, keys K1-K3 on stream 2, equal-mass fatal error, sub-cycling, before/after dump), kernels `athenak/src/particles/nrpic_collide.hpp`, task `nrpic_collide.cpp`, predictions P0-P11 in `tracks/core/JOURNAL-coll.md`; its message says the processor build compiles and nothing is tested yet. Differences from SPEC listed in its section 10: global cell index with face correction; default triad `symmetric` (Boris gauge) instead of Cholesky; per-step history; global equal-mass check; an extra velocity-dependent cross-section model. Check against the track's references: T0 on the committed kernels (CollGammaRelM1, CollMoller, CollScatter compiled standalone at -O0, -O2, -O3 -march=native with contraction) PASSES on all 208 equal-mass vectors: largest error 3.2e-16 of max(1, |u|) (criterion 1e-13), pair four-momentum conserved to 1.32 eps (criterion 4 eps) (run C-sidm-20261115-132624-13a77db, `fig_t0_kernel.png` looked at); core's own driver, committed minutes later (1a050f3, run core-20261115-132556-a7dc8ab), reports 3.3e-16 and 1.4 eps, so two independent drivers agree. T0b-T12 need an executable of `core/collisions` that has passed core's own checks: not run. |
| 2 | The baseline is reproduced (C-pre-3) | MET | F21 = arXiv:2108.11967: Table 1, 56 rows: Z(0), rho0, p0, v0, <gamma>, gamma_cr within 2.1e-5, E and E_rest within 1.11e-4, B within 2.4e-4 and eps within 1.3e-4 (both at `main.tex:503`, w0 = 4.5), eps_c(0) within 1.3e-4 (`:498`), R (printed on a 1e-3 grid) and C (computed by F21 from that R) within 2.5e-3, apart from three printed typos (`main.tex:491, 493, 516`) [corrected in wave 2 from "all within 1.1e-4 except R": note helper's claims check and lead recheck, run C-20261115-193332-48771b4]; Table 2, 14 roots, w0 within 1.1e-4 (run C-sidm-20261115-120722-38ab057, `gravothermal/figs/fig_table_residuals.png`, looked at). Criteria: eps maximum Z(0) = 0.5404 (b = 0.1), adiabatic-index root w0 = 4.05115 (F21 4.0515). An independent second solver (scope) agrees to 2e-8 in eps and 2e-9 in Z(0), and both match four F21 rows transcribed by the lead (X2, `fig_review_tmb.png`, looked at). Beyond F21: exact radial-pulsation onset Z(0) = 0.6348 (b = 0.1) to 0.5790 (b = 0.5) with gamma = 1 + p/u, the finite-element solver checked on Gamma = 2 polytropes (zero at the mass maximum to 3e-8, run -121524-5cebcf5, reproduced in -131135) and by a sign change between w0 = 3.58 and 3.595 at two resolutions (X5, `fig_review_onset.png`, looked at). 2601.17117 prints no sequence of its own; its time scales are recorded with locators (run -121412-d463e1a). |

## 2. Common G1 evidence (charter 9.2)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 3 | Baseline results without the NRPIC coupling | MET | Item 2; equilibria of C-pre-4: 13 near-threshold models (King, k = 1/2 polytrope, L0 = 0.1 shell), 1e4 equal-mass particles each, every offline check passes (243 pass flags, rerun in -131135); 2009.08163 thresholds reproduced (King y_max 0.33403 against 0.334, `paper.tex:953`), gr-qc/0601112 tables 27 of 29 rows within rounding (run -121626-e99907d); three independent solvers agree on the King sequence to 3e-8 (X3). Monoenergetic threshold y_c = 0.67961 between the first paper's bracket (run -115344-eb8b752). |
| 4 | Analysis pipeline validated on them | PARTLY MET | Box analysis (`collide/analysis/an_box.py`, `an_step.py`): synthetic snapshots (3 tests pass) and the collisionless AthenaK step run T6-0 (positions exact to 1.8e-12 L; bit-identical on rerun). AthenaK reads the new King table and particle file (run -125308-54870b9). Missing: the growth-rate extraction for the threshold runs, to be validated on the first paper's monoenergetic outputs (`../G0/OPEN.md` item 8). |
| 5 | Interface proposals submitted | MET (core's answer pending) | Collision operator: `collide/SPEC.md` (read by core at 4c76ca8, adopted in its draft); random numbers (C-pre-2): `collide/RNG_REQUIREMENTS.md` (keys K1-K3, tag rules), against core's `tracks/core/interfaces/rng.md` (branch `core/rng`, stream 2 reserved for collisions); outbox files of this session to core: collision operator, stream-2 table, perturbation recipe, static curved metric option. |

## 3. Work packages behind the criteria

| Package | State |
|---|---|
| C-pre-1 collision operator | specified, references and tests done; implementation by core in progress (uncommitted) |
| C-pre-2 random numbers | requirements done; core's interface exists; the stream-2 table is in core's draft collision interface, not yet in `rng.md` |
| C-pre-3 spherical baseline | done (item 2) |
| C-pre-4 initial data and Kn conversion | done for King b = 1, polytrope, shell; F21 b = 0.1 particle models missing; Kn definition fixed by the lead (`../G0/REPORT.md` section 2): sigma~ = K/Kn, K = 168.9 for the King threshold model |

## 4. First cluster runs with collisions, for wave 2

Preconditions: core's operator (committed in 3436846) past core's own predictions P0-P11; T1,
T2 and T10 of `collide/TESTS.md` passed on processors; T0b run with `triad = cholesky`
(or the replay taught the symmetric triad). Then, with the processor or card executable of
`core/collisions`, registered as scouting, predictions in `JOURNAL.md` first:

| Run | Model (file of run C-sidm-20261115-120610-b4592be, regenerated at N = 1e5) | Kn_c (sigma~) | Purpose |
|---|---|---|---|
| CC1-inf, CC1-10, CC1-1 | King b = 1 threshold, y0 = 0.334032 (`king_y0p33403`) | infinity (0), 10 (16.9), 1 (168.9) | conservation budgets in curved spacetime against the collisionless control (G2 criterion); collision counts against the local Moller rate; evaporation above E0; alpha_c(t) |
| CC2-inf, CC2-10, CC2-1 | King b = 1 stable side, y0 = 0.314 (`king_y0p31400`) | the same | the same on a model that is stable without collisions |

Set-up of all six: `nrpic_cf` with the model's table and particles (as
`problems/st/st_cluster.athinput`), static mesh with dx = M/4 over the cluster, outer
boundary 512 M, equal masses, `coll_cell_factor = 1`, `coll_pmax = 0.1`, sub-cycling
`measured`, 300 M, no perturbation, `<job> rng_seed` 1. At the centre of `king_y0p33403`
(psi_c = 1.2026, model JSON of run -120610) a mesh cell of M/4 is 0.36 M proper and holds
about 19 macroparticles at N = 1e5 (central spacing 0.293 M at N = 1e4, `knudsen.json`),
so dx = lambda/4 at Kn_c = 1 (lambda = H_c = 1.436 M) [JUDGEMENT from these numbers];
`coll_cell_factor = 2` (about 150 per cell, lambda/2) is the variant for the cell-size
check.
Cost about 2-4 card-hours in total (`../G0/REPORT.md` section 8). The F21 b = 0.1 models
follow once their particle files exist.
