# G1 evidence of E-stoch-inf: artefacts and run ids

Paths relative to `tracks/E-stoch-inf/`. Manifests: `runs/<run_id>/manifest.json`; outputs:
`/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/` (not committed). Criteria met or not:
`STATUS.md`. The leads' reviews: `../REVIEW-wave2.md` (waves 2, 2b), `../REVIEW-wave3.md`
(wave 3, batch 2a). The fresh-context verifier: `VERIFIER.md` (section 6 below). Scoping text and thresholds:
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

## 5. Figures relied on (each looked at by the lead on 2026-11-19; wave-3 figures in section 9)

`ladder/fig/final/fig_a2_modes.png`, `fig_a3_freezing.png`, `fig_a4_paper.png` (middle panel
shows the last-dump time-mismatch artefact at N = 4 for N = 64, 128; excluded from the
verdicts), `fig_spectrum.png`; `ladder/fig/floor/fig_floor.png`; `ladder/fig/a6/fig_a6.png`;
`analysis/fig/fig_t2_extraction.png`, `fig_plane_constraint_ratios.png`;
`stage/G1/fig/fig_lead_check.png`; the validator figure of run E-20261119-150541-3210cd6.

## 6. Wave 3: the verifier of the G1 material (helper package `g1verify/`)

Own code (reader, Philox, background, Mukhanov-Sasaki, R^NR, odd/even split) from the raw
dumps; predictions and outcomes `g1verify/JOURNAL.md`; report `VERIFIER.md` (copy of
`g1verify/VERIFIER.md`); all on processors.

| Run | What |
|---|---|
| E-20261120-222844-dbca87f | C0: tools against core's reader, numpy's Philox, core's alpha twin, the deck, the mode files |
| E-20261120-223154-d42de1a, E-20261121-025750-d1b6139 | R^NR per mode and box means from every dump (P256, L256p; L32p-L128p, Q64p, Q128p, L64p_proc), sha256 of each dump |
| E-20261121-030207-fb6f090 | V1 (A1), V2 (A2, spectrum), V3 (A3) |
| E-20261121-030657-c1afe38, -031951-82984f8, -032413-0672bf9 | V4/V5: odd/even parts, halving, controls, strict A4 and A4', orders, floor; figures |
| E-20261121-030522-c6907b6 (and the superseded -030412-42dd156) | V6 (A6) |
| E-20261121-030520-5a23d64, -031049-27cdc06, -031251-c48670d | V7 (A7): noise unit test; the G1 executable on 8 MeshBlocks and from a restart |
| E-20261121-030415-22d518b, -031936-16d6ae5 | failed (the verifier's script bugs), on record, rerun |

## 7. Wave 3: ladder items (a)-(d) (helper package `ladder/`, JOURNAL entries 12-22)

| Run | What | Kind |
|---|---|---|
| E-20261120-223038-684821a, E-20261121-025932-7a21f34 | (a) time-matched pairing: `ladder/results/final2/`, `fig/final2/` | analysis |
| E-20261121-025643-02526ff | (b)+(c) card job 4757: A6 at 64^3 in P1's set-up (six runs), L5 single kick (eleven runs), 0.028 card-hours | simulation |
| E-20261121-034414-bfd0285 | (b) A6 at 64^3: `ladder/results/a6_64/`, `fig/a6_64/` | analysis |
| E-20261121-031110-041cdf7, -034950-06f01f9 | (c) L5 on processors at 64^3; step/mesh test at 32^3 | simulation |
| E-20261121-034645-02a463e, -035509-790b1dc, -040015-436a615 | (c) L5 analyses (card, processors and comparison, step/mesh): `ladder/results/l5/`, `fig/l5/` | analysis |
| E-20261121-034609-f573ddc | (c) first L5 analysis, failed (log fit at t = 0), on record | failed |
| E-20261121-032828-fe18c5f | (d) card job 4762: P256 with seed 20261120, 0.501 card-hours | simulation |
| E-20261121-045105-f797ebb, -045236-755a956 | (d) analysis and outlier check: `ladder/results/seed2/`, `fig/seed2/` | analysis |
| E-20261120-222812-b352d5f | L5 smoke test on processors (input check) | scouting |

## 8. Wave 3: the lead's checks (batch 2a; `../REVIEW-wave3.md`)

| Run | What |
|---|---|
| E-20261121-063551-7957a3d | LR: every final analysis step of g1verify and ladder rerun unchanged from its registered inputs; JSON leaves compared with the registered outputs and the committed copies (`../review3/results/`) |
| E-20261121-063816-64ac0dc | LW1-LW6: the lead's own code on the raw dumps (seed 2, P256 odd/even, records, A6 at 64^3, L5, step test); `../review3/fig/fig_lead3.png` |
| E-20261121-063758-d643396 | first attempt of LW1-LW6, failed (recursion in the lead's parameter reader), on record |
| E-20261121-064707-77ec326 | LR1: L32p, L32m with the release core-v0.4 processor build against core/scalar-2 (E-20261115-172636-ce98836): 0 of 18.9 million words differ, records identical (`../review3/fig/fig_r1.png`) |

## 9. Figures relied on in wave 3 (each looked at by the lead of batch 2a)

`VERIFIER.md`'s `g1verify/fig/fig_v1.png` ... `fig_v7.png`; `ladder/fig/final2/fig_a4_paper.png`,
`fig_halving_fix.png`; `ladder/fig/a6_64/fig_a6.png`; `ladder/fig/l5/fig_l5.png`,
`fig_l5_scaling.png`; `ladder/fig/seed2/fig_seed2.png`; the lead's `../review3/fig/fig_rerun.png`,
`fig_lead3.png`, `fig_r1.png`.
