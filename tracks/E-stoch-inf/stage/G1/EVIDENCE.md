# G1 evidence of E-stoch-inf: artefacts and run ids

Paths relative to `tracks/E-stoch-inf/`. Manifests: `runs/<run_id>/manifest.json`; outputs:
`/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/` (not committed). Criteria met or not:
`STATUS.md`. The lead's review: `../REVIEW-wave2.md`. Scoping text and thresholds:
`spec/scope/SCOPE.md` sections 4, 4b, 8. The G0 evidence (wave 1, with the hand-written
manifests of wave 1) is `../G0/EVIDENCE.md`.

## 1. Slow-roll ladder (helper package `ladder/`, waves 2 and 2b)

Executable: core's tested branch `core/scalar-2` a58e95b, `scratch/core/exe/core_scalar-2/`
(sha256 in each manifest; decision 0013, scouting). Predictions and outcomes:
`ladder/JOURNAL.md` entries 1-11; summary `ladder/README.md`.

| Run | What | Kind |
|---|---|---|
| E-20261115-172618-f948386 | job A, card: P256 (256^3, nmax2 = 4096, 8.10 e-folds), 0.503 card-hours | simulation |
| E-20261115-172629-312a82c | job B, card: P256m, L256p, 0.496 card-hours | simulation |
| E-20261115-172625-416fec0 | job C, card: L256m, L64, L128, Q64, Q128 with halving, NC64, NC128, 0.418 card-hours | simulation |
| E-20261115-172636-ce98836 | processors: L32p/m, L32ph/mh, NC32p/m | simulation |
| E-20261115-173719-e810503 | processors: L64p/m to t = 4.5 (hedge) | simulation |
| E-20261119-142317-c851f27 | processors: A6, N = 32 at Courant 0.25, 0.125, 0.0625, s = +-1 | simulation |
| E-20261115-171633-f574079 | mode files nmax2 = 256-4096 (manifest failed at a final `tail`; files checked by hand, entry 1) | preparation |
| E-20261115-172935-ddfade0 | self-test: reader against core's, R^NR at t = 0 | analysis |
| E-20261115-174008-7aee5ff | mode files against Track E's MS reference | analysis |
| E-20261115-174214-74becdd | extraction factor E6 (1/4) against alternatives | analysis |
| E-20261115-173540-b69c63f, -184737-92c4fa1, -191327-63c7397 | partial analyses (32; 32 and 64; job A) | analysis |
| E-20261115-194633-9e04ed8 | final analysis of all rungs: A1-A5, spectrum, negative control, cost (`ladder/results/final/`, `fig/final/`) | analysis |
| E-20261119-142625-82a7990 (superseded), -142713-32c883a | floor analysis (`ladder/results/floor/`, `fig/floor/`) | analysis |
| E-20261119-145115-7388a05 (superseded), -145230-ff0dff2 | A6 analysis (`ladder/results/a6/`, `fig/a6/`) | analysis |
| E-20261119-141654-c2a10d1 | A12 validations on processors and card (`ladder/results/a12/`) | analysis |
| E-20261115-172521-e098160 | stopped: literal `$NRPIC_RUN_DIR` (entry 2) | failed, on record |

## 2. Analysis of AthenaK output (helper package `analysis/`, wave 2)

| Run | What |
|---|---|
| E-20261115-171445-36152c4 | synthetic tests T1-T5 of `analysis/sfa.py` (15/15) |
| E-20261115-171628-1737ebe (failed prediction, on record), -171859-0b34449 | constraint estimators on core's plane perturbation against the code's history |
| E-20261115-172349-0bdb97d, -172347-a297a96, -175951-2e2387d | SR scouting from the homogeneous slice (release core-v0.3), N = 16 (with control), 32, half step |
| E-20261115-170645-3b21217 | noise unit test at the base size on a card (0.0153 card-hours) |
| E-20261115-170727-d15df12 | U2 and U4 on processors (closed in wave 2b) |
| E-20261115-180526-6b68c33 | U4 on a card (closed in wave 2b) |
| E-20261115-172423-5234cce, -180533-24a7781, -184748-9b010fa | validations: scaled U6, card base case, A14 |
| E-20261115-170651-885fc6e | stopped: literal `$NRPIC_RUN_DIR` (journal 17:08) |

## 3. The lead's checks (wave 2b; `../REVIEW-wave2.md`)

| Run | What |
|---|---|
| E-20261119-150238-b81e33f | own code on L32p/L64p/L128p: A1, A2, A3, H0, odd/even parts of H, order 32 -> 64 (`scripts/lead_check.py`, `fig/fig_lead_check.png`, `results/lead_check.json`) |
| E-20261119-150842-ca70d37 | partial rerun of the ladder's analyses, bit-identical |
| E-20261119-145853-ef835c2 | full rerun from the cold dumps, stopped (I/O bound), on record |
| E-20261119-150346-a513bc8 | analysis T1-T5 and verifier V1-V5, V8 reruns, identical |
| E-20261119-150541-3210cd6 | noise reference fixed (cancellation-free increment), U6 and frozen revalidated |

## 4. Baselines without the coupling and interfaces (wave 1, in `../G0/EVIDENCE.md`)

Linear MS references (`spec/ref/`, runs E-stoch-inf-20261115-122806-ef0d039 and later),
delta-N references (`langevin/`, runs E-stoch-inf-20261115-130137-176cdd6,
-130139-176cdd6, -130747-1b9bee4), noise validator and its self-test (`noise/`, runs
E-stoch-inf-20261115-132950-16a0168, -133731-2031735); interface documents
`noise/NOISE_SPEC.md`, `noise/RNG_REQUIREMENTS.md`, `codebase/DESIGN_REVIEW.md` 9, 11,
`spec/SPEC.md` 10; core's answer `tracks/core/interfaces/scalar_field_2.md` (core/scalar-2).

## 5. Figures relied on (each looked at by the lead on 2026-11-19)

`ladder/fig/final/fig_a2_modes.png`, `fig_a3_freezing.png`, `fig_a4_paper.png` (middle panel
shows the last-dump time-mismatch artefact at N = 4 for N = 64, 128; excluded from the
verdicts), `fig_spectrum.png`; `ladder/fig/floor/fig_floor.png`; `ladder/fig/a6/fig_a6.png`;
`analysis/fig/fig_t2_extraction.png`, `fig_plane_constraint_ratios.png`;
`stage/G1/fig/fig_lead_check.png`; the validator figure of run E-20261119-150541-3210cd6.
