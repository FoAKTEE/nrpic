# Gate review: C-sidm G1 (independent reviewer, decision 0019 item 3)

Reviewer: a fresh session that produced none of this work (batch 4b, 2026-11-21, 16:49 to
about 17:15 UTC). No tag `stage/C-sidm/G1-pass-*` existed at the start (`git tag -l`; only
`stage/C-sidm/G0-pass-20261120`). Criteria read: `coord/CHARTER.md` 9.2 and sheet 9.6 (G1:
"all tests of C-pre-1 pass; the baseline is reproduced"), brief lines 674-686, decisions
0013, 0016 (and 0019-0023: no further ruling on Track C's G1). Package read:
`STAGE_REPORT.md`, `CHECKLIST.md`, `EVIDENCE.md`, `OPEN.md`, `VERIFIER.md`, `REVIEW.md`,
`../REVIEW-wave3.md` section 1, `../../collide/TESTS.md` sections 2-2c, `../../heat/README.md`
verdict, `../../heat/JOURNAL.md` P-T8, `../../box_tests/README.md` results,
`../../gravothermal/README.md`, `../../equilibria/README.md` checks, the note `main.tex`
sections IV-VI and its ledger.

The draft of this file with the predictions of the reviewer's own checks R1 and R2 was
committed before each ran (commits a2e557be, 01f1503b). Their code is the reviewer's own,
`scratch/C-sidm/tmp/gate_review_G1/t5_kl_check.py` and `t6a_check.py` (untracked; each is an
input of its run with its sha256 in the manifest); only the snapshot reader
`python/nrpic/collide.read_snapshot` and the figure style are the repository's.

## Verdict per criterion

| # | Criterion | Verdict | Evidence the reviewer opened |
|---|---|---|---|
| C1 | Baseline results without the NRPIC coupling | PASS | Run C-sidm-20261115-120722-38ab057: all 8 output checksums verify; `summary.md` gives F21 Table 1 (56 rows) median relative differences 4e-7 to 6e-4 per column and maxima 2.6e-6 to 2.5e-3 (R, printed on a 1e-3 grid), except the C and p0 columns, whose outliers are the printed typos of main.tex:491, :493, :516 already in `coord/BRIEF_ERRATA.md` (row "arXiv:2108.11967"); Table 2 (14 rows) maxima <= 2.1e-3. Equilibria checks of run C-sidm-20261115-121626-e99907d read in `equilibria/README.md` "Checks" (2009.08163 thresholds, gr-qc/0601112 tables 27 of 29 rows, Lane-Emden limit, per-model constraint residuals), run output not reopened. Figure `note/figures/fig_sequences.png` looked at: solver curve through the printed points, onsets marked. |
| C2 | Analysis pipeline validated on them | PASS WITH RESERVATION | Box analysis: my own estimators reproduce the package's numbers where I recomputed them (R1: the track's T5 gap s_MJ - s_mix = 0.045142 for theta_2 = 1e-3 seed 1 equals my quadrature value 0.045142; R2: my slab sums of the T6(a) snapshots equal the package's `reduced.npz` rows exactly, 0.0 relative, all four cases). Verifier V1b, V1c, V2, V5 and the lead's L8, L13, L21 recompute the rest of the box and heat analyses. Cluster pipeline (18/18 published numbers, growth_fit_v2 U1-U5) read in EVIDENCE and VERIFIER only, not reopened. Reservation: growth rates on the cluster runs are window-dependent (G3', G6' failed; 1-SE coverage fails at sigma 0.1, run C-20261120-223404-40668db); the restriction "no constant growth rate" is binding at G2. |
| C3 | Interface proposals submitted | PASS | `coord/INTERFACES/collisions.md` lines 7-9 (client Track C; follows `collide/SPEC.md` at 4c76ca8; section 10 lists the differences); `coord/INTERFACES/rng.md` lines 199-207 (stream 2 requested by Track C, table 6.1); decision 0011 ACCEPTED. |
| C4 | Baseline data and figures | PASS | Looked at `box_tests/figs/relax_T345_th1.0_s1.png` (temperatures, entropy, end-state histogram on MJ), `note/figures/fig_box_summary.png`, `fig_heat.png`, `fig_sequences.png`; result JSON of runs C-20261115-170539-28432c3, C-20261120-223321-3d088d4 opened. |
| C5 | Interface documents | PASS | `collide/SPEC.md`, `TESTS.md`, `RNG_REQUIREMENTS.md` present; adopted as in C3. |
| C6 | All tests of C-pre-1 pass | PASS WITH RESERVATION | Each test the brief names in C-pre-1 now has an independent check: relaxation to Maxwell-Juttner (T3; my R1.3: chi-square of the end state against MJ(theta_eq), p = 0.26, 0.41, 0.57, 0.47), collision rate (T2; verifier V2), monotonic entropy increase (T5; my R1, below), heat conduction at the long end (T6(a); my R2, below) and at the short end (T6(b), T7; verifier V1b, V1c). T8 from run C-20261120-223321-3d088d4 `t8.json` opened: card seed (4e6) finest changes dt -0.52, pmax -0.006, dx -1.04 percent (z -0.85, -0.01, -1.70 against sd 0.61 percent), PASS; the processor sets (5e5, two seeds) exceed 2 percent in four of six finest changes at 1.0-2.5 sd, which `heat/JOURNAL.md` (P-T8c) predicted and records: that set cannot judge the criterion. Reservations below (1)-(4). |
| C7 | The baseline is reproduced | PASS | Two rows of `table1_compare.csv` checked against the paper source (`kb-data/raw/arxiv/2108.11967/v2/src/main.tex:490`, `:503`): the transcribed values are the printed ones (E = 2.72074e-2, 1.27271e-2), the solver's within 1.6e-6 and 1.1e-4. Verifier V4 (run C-20261121-080313-84094f1, own finite-element solver): Table 1 b = 0.1 rows to <= 1.3e-4, eps maximum Z(0) = 0.540413, exact onset 0.634817, King y_max 0.334032. The onset criterion of G26 (2601.17117) is F21's (`SIDM_MS.tex:476`, quoted in `stage/G0/REPORT.md`), so reproducing F21 covers both named papers up to the threshold. |
| C8 | Ruling 0013 | NA | Concerns the G2 wording; agree. |
| C9 | Schematic: updated architecture | PASS | `note/figures/schem_architecture.png` looked at: exists/to-be-ported/new legend; box tests, heat T6-T8, pair energy at the particle metric marked as existing; refined-mesh collisions, ADM energy, threshold scan new. |
| C10 | Schematic: data flow | PASS | `schem_dataflow.png` looked at: initial data, AthenaK, run outputs, analysis, note, checksum loop. |
| C11 | Data figure: baseline results | PASS | `fig_sequences.png` looked at. |
| C12 | Data figure: pipeline validation | PASS | `relax_T345_th1.0_s1.png`, `fig_box_summary.png` looked at (rate within 2e-4 of the Moller rate at all temperatures; per-step energy change 1e-22 to 1e-18 against the bound 1e-11; curved-metric rate equal to the flat twin). |
| C13 | Package documents | PASS | All present (verify `package` check). Cosmetic: the "Looked at" column of the figure table in `STAGE_REPORT.md` still reads "to be confirmed by the session" (template text), and its verdict line names the tag as if it existed. |
| C14 | Data figures from registered runs, one script each | PASS | My two reruns of `nrpic-stage verify` (below): 11 of 11 scripts ran in a clean export, all 22 committed figure files regenerated, 0 differ beyond tolerance. |
| C15 | Schematics with the paper style | PASS | `schem_timeline.png` looked at; style copies match `harness/style/SHA256SUMS` (verify `style`). |
| C16 | Working note, checker with --compile | PASS | Run C-20261121-155226-8ea9e47 `checker.txt`: 0 undefined references, 0 undefined citations, 1 overfull box (1.09 pt); verify `note-pdf` PASS. The note body states no measured number outside the ledger: I listed every number in sections I-IV B (formulas, model labels b = 0.1 and 1, test temperatures, the design range of sigma/m) and the ledger tables: 79 of 79 data rows carry a run id or a source locator; literature numbers carry locators in the appendix paragraph. |
| C17 | Fresh-context verifier | PASS WITH RESERVATION | `VERIFIER.md` read; blind verdicts committed first (00adbb95). "Every number recomputed" is not met literally. My R1 and R2 close T5 and T6(a); still without a second agent: T8 (card), T6(c), the measured T7 values at theta 0.1 and 1 (the lead recomputed them from per-seed values only), T0b, T10b, T11, R6, most growth-fit rows. |
| C18 | Null results and failed runs on record | PASS | Verify `runs` PASS (188 manifests); failed runs listed in `STAGE_REPORT.md`; failed predictions recorded in every package journal (e.g. `JOURNAL.md` L17, L19; `heat/JOURNAL.md` P-T8c; `collide/TESTS.md` 2c strict T9 reading). My own failed prediction R2.2 is below. |
| C19 | STATUS, JOURNAL, HANDOFF current | PASS | `STATUS.md` 39 lines; `HANDOFF.md` written by the lead of batch 4a, 2026-11-21. |

## Reviewer's own check R1: T5 (entropy), run C-20261121-165320-a2e557b

Own estimator: D(t) = s_MJ(theta_eq) - s(t) = KL(f || MJ(theta_eq)) of the |u| marginal,
100 bins of equal MJ(theta_eq) probability, Miller-Madow corrected; theta_eq from the mean W
at t = 0; reference by quadrature of the two-temperature mixture at the sample temperatures.
All 85 snapshots of each of the four boxes of run C-20261115-170539-28432c3.

| Box | D_ref (binned / continuous) | D(0), z | largest increase (combined se) | chi-square p at 15 tau_rel | max relative change of mean W |
|---|---|---|---|---|---|
| theta_2 = 1e-3, seed 1 | 0.04198 / 0.04514 | 0.04205, +0.22 | 1.59 | 0.26 | 8.9e-16 |
| theta_2 = 1e-3, seed 2 | 0.04136 / 0.04448 | 0.04143, +0.25 | 1.66 | 0.41 | 1.1e-15 |
| theta_2 = 1, seed 1 | 0.11693 / 0.12282 | 0.11702, +0.18 | 1.69 | 0.57 | 1.0e-15 |
| theta_2 = 1, seed 2 | 0.11561 / 0.12145 | 0.11541, -0.38 | 1.47 | 0.47 | 8.9e-16 |

Predictions R1.1-R1.4 all HELD. Figure `scratch/C-sidm/C-20261121-165320-a2e557b/t5_kl_check.png`
looked at: D falls monotonically from the reference to the noise floor (4 null standard
deviations, 2.8e-5) by about 6 tau_rel at both temperatures and then scatters about zero.
T5 is confirmed independently of the track's estimator.

## Reviewer's own check R2: T6(a) (long mean free path), run C-20261121-165856-01f1503

| Case | own vs package sums | max deviation from same sample (noise units; M, MW, MK) | rms against ensemble curve (M, MW, MK) | initial slope / ensemble |
|---|---|---|---|---|
| lambda/L = 1000, seed 1 | identical | 0.19, 0.19, 0.23 | 1.22, 1.21, 1.43 | 1.006 |
| lambda/L = 1000, seed 2 | identical | 0.25, 0.25, 0.31 | 0.95, 0.96, 1.08 | 0.998 |
| lambda/L = 100, seed 1 | identical | 0.45, 0.46, 0.54 | 1.20, 1.20, 1.37 | 1.007 |
| lambda/L = 100, seed 2 | identical | 1.17, 1.20, 1.53 | 1.00, 1.00, 1.10 | 0.998 |

- R2.1 HELD (0.0 relative difference at the first and last snapshot of all four cases).
- R2.2 FAILED as worded: at lambda/L = 1000 seed 2 the M (W - 1) sum deviates from the
  same-sample curve by 0.31 noise units (prediction < 0.3), and at lambda/L = 100 seed 2 by
  1.17-1.53 (prediction < 1.0). My bound was set too tight; the deviation from the same sample
  grows from lambda/L = 1000 to 100 by factors 2.4 (seed 1) and 4.7 (seed 2), of the order of
  sqrt(10) expected if it is the stochastic scatter of the collided particles, as the heat
  package found ([JUDGEMENT]; not tested by a run that could have refuted it). It does not
  bear on the T6(a) criterion, which compares with the ensemble curve.
- R2.3 HELD: rms 0.95-1.43 noise units (< 1.5) at lambda/L = 1000; the package reported
  1.20/1.20/1.11 and 0.86/0.87/1.04. With my per-particle variance the M (W - 1) sum of seed 1
  comes to 1.43, close to the bound: the pass does not survive a 5 percent smaller noise model.
- R2.4 HELD: initial slopes 1.006 and 0.998 of the ensemble slope (package: 1.001, 0.978).

Figure `scratch/C-sidm/C-20261121-165856-01f1503/t6a_check.png` looked at: the hot-half mass
rises from 1 to 1.5 of its initial value by t = 0.8 L/<|v|> on the collisionless curve; the
deviations from the ensemble curve follow the initial sample (the two lambda/L of one seed
share their particle file and track each other), within about 2.5 noise units.

## Re-verification (`nrpic-stage verify C-sidm G1`)

1. At 59f352d9 (16:50-17:00 UTC): every check PASS (clean, export, size, note, package,
   note-pdf, style, fig-script, min-figs, runs 188 finished, status, rerun 11 of 11, compare
   22 files, regenerate 22) except `sync` FAIL: main received commits (efd77b39 and the core
   release record) while the check ran. They touch no file of this track, `harness/`,
   `python/` or `coord/WAIVERS.md`. `run-notes` WARN: 25 hand-written manifests of waves 1-2
   (decision 0016 item 3). Output kept at
   `scratch/C-sidm/tmp/gate_review_G1/VERIFY_RESULTS_59f352d.md`.
2. After merging main again, at 96f35eb0 (16:56-17:06 UTC): **PASS**, 0 failed checks; sync
   PASS; runs PASS (189 manifests, my run R1 included); rerun 11 of 11; compare and
   regenerate 22 of 22; `run-notes` WARN as above. Output kept at
   `scratch/C-sidm/tmp/gate_review_G1/VERIFY_RESULTS_96f35eb.md`.

The committed `VERIFY_RESULTS.md` of the package (at f1c802ef, the lead's) is left as it is.

## Overall recommendation

PASS WITH RESERVATIONS. Both track-specific criteria of G1 are met with evidence that a second
agent has now checked for every test the brief names in C-pre-1: rate (verifier), relaxation
and entropy (this review, R1), heat conduction at the short end (verifier) and the long end
(this review, R2); the baseline (F21 sequence and onsets, King thresholds) is reproduced by two
independent solvers. The package is complete, re-verifies on a clean export, keeps every
number of the note behind a run id or a locator, and keeps its failed predictions and runs.

## Reservations to carry to G2

1. Conductivity at the percent level: T8 rests on one card seed (margin 1.6 sd for dx), the
   conductivity grows with the collision cell (form open), and the zero-cell-size value at
   theta = 0.003 may lie 1-3 percent below the relativistic Chapman-Enskog value of V1a, which
   no second agent has checked [TO VERIFY]. Run the cell-size and step series (about 0.3
   card-hours) and have V1a checked before any G2 statement relies on kappa below 3 percent.
2. Growth rates: on the cluster runs a rate exists only with its fitting interval; the G2
   threshold must come from collapse times, the zero of omega^2 on the controls, or the
   contraction against a control of the same mesh and seed, with at least three seeds near
   the threshold (RISKS 8, 9).
3. Definitions named after the data (`collide/TESTS.md` 2c: T4 window, T6(b) and T9 reference
   temperatures) are accepted for G1 only because the brief's tests do not hinge on them; the
   strict T9 reading failed and stays on record. Every G2 test names its reference quantities,
   windows and noise model before the run.
4. Not second-checked: T8 (card), T6(c), the T7 card measurements at theta 0.1 and 1, T0b,
   T10b, T11, R6 (King defect), most growth-fit rows, all card cluster runs. A G2 verifier
   covers those G2 uses (T8, R6, the cluster runs and their controls).
5. The T6(a) pass is close to its bound under an exact per-particle noise model (rms 1.43 for
   M (W - 1), seed 1); state the noise model with the criterion when T6(a) is quoted again.
6. Capability gaps for G2 sit with core: collisions on refined meshes, collisions on several
   MPI ranks (they stop in core-v0.5), an ADM-energy diagnostic; the M/4 mesh does not hold
   the equilibrium within the stability margin (RISKS 3).
7. Cosmetic: fill the "Looked at" column of the figure table of `STAGE_REPORT.md`.
