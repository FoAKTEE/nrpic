# JOURNAL of the note package (helper of D-bh-dress, wave 2)

Append-only. Predictions are written before the scripts that test them run; outcomes after.
The package makes the working note v0, its figures and schematics, the numerical ledger,
a check of the lead's documents against the run outputs, and `stage/G0/STAGE_REPORT.md`.
No simulation is run: every script reads outputs of runs registered in wave 1.

## 2026-11-15T16:58Z  predictions, written before any script of this package ran

Worktree at cbbdfe0 (main merged, up to date). Inputs: the run directories under
`/data/haiyangw/nrpic/scratch/D-bh-dress/` listed in `scripts/common.py`.

- P1 (claims check, `scripts/ledger.py`). Of the numbers that the lead's documents
  (`stage/G0/REPORT.md`, `stage/G1/STATUS.md`, `STATUS.md`, `HANDOFF.md`) state with a run
  id, I check about forty against the run outputs. Expected: all agree to the printed
  digits, with two exceptions I saw while reading the files: (a) "dress 0.625 M_ta" is
  attributed to run D-bh-dress-20261115-123813-97afeea, whose output prints the mass
  inside the outermost caustic, m(lambda_1) = 0.654; the 0.625 is `f_passed` = 0.6247 of
  the analysis run D-bh-dress-20261115-125613-248fdaf; (b) "order 5.8-5.9 in the curvature
  transition" holds for the box "mid transition" of run D-bh-dress-20261115-043406-4df1e76;
  over the whole region 4 < r < 30 M the same run gives 5.3 (H) and 4.7 (M). Refuted if
  more than three further numbers disagree, or if either (a) or (b) turns out to agree.
- P2 (`scripts/fig_floor.py`, my own code on the raw finder output of runs
  D-bh-dress-20261115-121313-284ec4f and -121314-284ec4f). The drift of a centred 20 M
  running mean from 50 to 490 M is +2.95e-4 (M/8) and +3.67e-5 (M/16), as the lead's
  re-check D-bh-dress-20261115-145546-5259f48. Refuted by a difference in the second digit.
- P3 (`scripts/fig_es.py`). The wall column of `es_reference.csv` (run
  D-bh-dress-20261115-043445-b782009) equals the marginally bound closed form
  R_w(tau) = (36^(3/2) + (3/2) sqrt(2) tau)^(2/3) M to 1e-10 relative, and the column "mass
  inside the wall" equals 1 to round-off. Refuted otherwise.
- P4 (`scripts/fig_es.py`). The tracers released at rest at R0 = 6 M and 10 M reach R = 2M
  at the proper times of the radial cycloid from rest, tau = sqrt(R0^3/2M) (eta + sin eta)/2
  with cos eta = 2(2M/R0) - 1 ... written as tau(R) = sqrt(R0^3/(2M)) [arccos(sqrt(R/R0)) +
  sqrt((R/R0)(1 - R/R0))]: 15.0 M and 34.6 M as `first_run_plan.json` says, and the csv
  crosses 2M within its 0.2 M sampling of these times. Refuted by a difference above 0.2 M.
- P5 (`scripts/fig_es.py`, density from the table). The Hamiltonian constraint evaluated
  on the table columns, 16 pi rho = -8 psi^-5 lap(psi) + 4 KL KT + 2 KT^2 with
  psi = 1 + u + m_p/(2 rbar), gives rho = 0 to 1e-9 rho_0 inside the bubble and in the
  exterior, and rho = rho_0 = 3.7182e-6 M^-2 on the plateau to 1e-4 relative (second-order
  differences of a smooth table at drbar = 0.02 M). Refuted by a nonzero density in the
  vacuum regions above 1e-6 rho_0 or a plateau off by more than 1e-3.
- P6 (all figure scripts). Every figure renders without a label cut at the figure edge
  (czstyle overflow check); the manuscript checker reports no hit outside the accepted
  ledger exception of the guide.

## 2026-11-15T17:15Z  outcomes of P1-P5 (run D-bh-dress-20261115-171128-38634d6, registered by hand)

`harness/bin/nrpic-run submit --package tracks/D-bh-dress/note` refused: an untracked
`es.horizon_summary_0.txt` (another helper's AthenaK output) sits in the worktree root.
The run was registered with `scripts/handreg.py` (manifest with the refusal, inputs with
sha256, `sha256sums.txt`). All eight scripts ran cleanly; figures and tables copied into
`figures/` and `tables/`. Every figure was looked at (PNG read): fig_es, fig_constraints,
fig_floor, fig_spike, fig_infall, schem_architecture, schem_timeline.

- P1 holds. 36 statements checked (`tables/claims.md`), 31 agree to the printed digits.
  (a) confirmed: "dress 0.625 M_ta" is `f_passed` = 0.6247 of run -125613-248fdaf; run
  -123813-97afeea prints m(lambda_1) = 0.654 (locator to be corrected). (b) confirmed: orders
  5.88 (H) and 5.76 (M) in the box "mid transition"; 5.29 and 4.69 over 4 < r < 30 M.
  Three further remarks, none a plain disagreement: the 0.02 per cent against the published
  SFW figure holds for the peak (1.5e-5 in height, 1.5e-4 in position), the whole curve
  deviates by up to 2.6e-3; the arrival times 15.0 and 34.6 M of the tracers are the first
  samples of the 0.2 M reference grid after the crossing, the exact values are 14.83 and
  34.44 M; the cost of the vacuum control (about 1.2 card-hours) is a judgement with no row
  in the cost table. Also: REPORT.md:101 cites the simulation run for |dE/E|, |dL/L|, whose
  values sit in the analysis run -125739-a18d74d.
- P2 holds: +2.952888e-4 (M/8) and +3.674327e-5 (M/16), equal to the lead's values to all
  digits. Not an independent method: like the lead, the 20 M mean is taken at its last
  finite point (489.5 and 489.75 M) for "490 M".
- P3 holds: wall against the closed form 6.7e-16 relative; mass inside the wall exactly 1.
- P4 partly refuted. As written (fall from rest) it holds for the 6 M group (closed form
  14.83 M, first sample below 2M at 15.0 M) and fails for the 10 M group (33.70 M against
  34.6 M, 0.9 M off). With each group's own energy from `es.json` (E = -0.09997 at 10 M, an
  outgoing start because K^theta_theta < 0 in the transition) the infall law gives 34.44 M
  and 244.74 M (20 M group), both within the 0.2 M sampling of the reference. The tracers
  start with the expansion of the slice, not at rest; my prediction ignored that.
- P5 refuted in the bubble at the stated threshold, holds elsewhere. Largest |rho| inside
  0.95 x 36 M is 2.2e-5 rho_0 (at R = 31.3 M), above 1e-6. On every second and fourth table
  row it is 8.9e-5 and 3.6e-4 rho_0: a factor 4.0 per doubling, the second-order truncation
  of my own differencing of u, not a property of the data (the offline check of the run
  -042704-f3da881 uses fourth-order differences). Plateau: rho/rho_0 - 1 at most 1.7e-7;
  exterior 3.3e-9 rho_0; -K/H = 1 on the plateau.

## 2026-11-15T17:25Z  final run, P6, note compiled, stage report

- Final registered run D-bh-dress-20261115-171627-18706fb (by hand, same refusal):
  8 of 8 scripts clean; the seven PNGs are byte-identical to those of -171128-38634d6 (the
  changes between the two runs touch only the ledger layout, the explicit frameon=False, and
  the deck values, now read from the M/16 input the run's manifest records). Outputs copied
  to `figures/` and `tables/`.
- P6 holds for the figures (no label cut at the edge, czstyle check, all eight scripts). The
  manuscript checker (`--compile`, forbid list of `../WRITING_GUIDE.md`) is clean on 14 of 16
  checks; the hits of 5.5 (run ids) are in the ledger appendix and of 5.8 in `ledger.py`,
  `run_all.py`, `handreg.py` (exception 1 of the guide) and one data key `pass_e0.1_s0.5_a100`
  of a registered output that matches the hardware pattern `A100`. So P6 as written (no hit
  outside the exception) is refuted only by that data key.
- `main.pdf`: 10 pages, latexmk without undefined references or overfull boxes; every page
  read. Figures are numbered in the order of first citation.
- `stage/G0/STAGE_REPORT.md` written by `harness/bin/nrpic-stage report D-bh-dress G0`
  (verdict FAIL: CHECKLIST items OPEN, no verify, no verifier report), then sections of my own
  appended: proposed statuses for C5-C7, C9, C10, C13-C15 with evidence, the five remarks of
  the claims check, a draft for the decision paragraph. `nrpic-stage verify` not run (it
  writes into the stage directory, outside this package's paths).

## 2026-11-20T22:18Z  wave 3, round 1: working note v1 (helper `note`), predictions

Worktree at 0f6b3be5 (main merged, up to date; git status clean, no stranded files of this
package). Package brief: `../PLAN-wave3.md`, row `note`. This round adds to the note the
wave-2 baselines (Kerr spike and its AthenaK stationarity; the Newtonian-mode infall), the
first full-relativity runs (the bubble run and its vacuum control) and the redrawn
architecture schematic (G1 item C9). Results that other helpers produce in parallel this
round (the lapse_leak run, the matter run, the late-drift controls, the late Newtonian-mode
run, the G1 verifier) are named only as pending work, with no numbers. No simulation is run:
three new figure scripts read registered outputs, each registered with `nrpic-run submit
--package tracks/D-bh-dress/note`. Predictions, written before any new script ran:

- P7 (`scripts/fig_kerr.py`; reference D-bh-dress-20261115-171615-8adbbdd, stationarity
  analysis -174954-786ddcc). The script reads the numbers it prints from the run files, so
  it must reproduce `spike/README.md` items 5 and 6 to the printed digits: constant-f
  equatorial peaks 0.9271e8 GeV/cm^3 at 7.31 Gm (a = 0.5) and 1.0604e8 at 6.61 Gm (a = 0.8),
  largest deviation from FdRW fig_rho_a 0.88 % and 0.95 %; Hernquist a = 0.8 peak 3.922e18
  at 5.06 Gm against FdRW 4.083e18 (ours 4 % below); stationarity chi^2 median 43.8 for
  47 dof, late/early ratios 0.998, 1.003, 0.999, 1.000, 1.000 in the five ranges. Refuted
  by any difference in the printed digits (then README or my reading is wrong).
- P8 (`scripts/fig_newton.py`; runs D-20261115-171503-4262f03, -171505-62940f4,
  -171507-d1058a9, analysis -190541-e27453d). From `nm_growth.txt` and `nm_analysis.json`:
  M_ta at a/a_i = 4 is 2.5966 (N128c and N64c) and 4.8159 at a/a_i = 8 (N128Lc); dress
  0.7975, 0.7966 at 4 and 2.1537 at 8; the largest M_ta deviation from the kernel-matched
  shells after a/a_i = 1.5 is 0.10, 0.12 and 0.31 %; dress/M_ta 0.307 (a/a_i = 4) and 0.447
  (8) against the self-similar 0.625. Refuted by a difference in the fourth digit of a mass
  or the second digit of a deviation.
- P9 (`scripts/fig_esrun.py`; my own reading of the raw outputs of D-20261115-172726-60ba4c2
  and -172730-c6d151b through the readers of `es_runs/analyse.py`, data run
  D-20261115-170213-d2c2131). It reproduces es_runs JOURNAL entry 4 and 6 to three digits:
  horizon drift from t0 = 100 M, max |.| over 100-200 M 3.40e-4 (ES) and 1.37e-4 (V);
  over 100-165 M within [-5.0e-5, +9.3e-5] and [-4.2e-5, +2.1e-5]; level M_AH(100 M) - M
  +9.55e-4 and +9.37e-4; largest |drift(ES) - drift(V)| 2.04e-4 = 1.49 V's floor; wall
  tracers max |R/R_exact - 1| for tau <= 200 M 2.20e-3 and 1.59e-3; crossings of R = 2M at
  tau = 14.826 and 34.437 M (exact 14.827, 34.442); the 20 M group of ES at tau = 244.09-244.51
  M; lapse at the probe x = 46 M 1.292, 1.662, 1.636 at t = 10, 25, 50 M against the
  homogeneous 1+log model 1.377, 2.096, 3.577 (`plateau_lapse_model`). Refuted by a
  difference in the third digit (then either my reader or the journal is wrong).
- P10 (schematics). `schem_architecture.py` and `schem_timeline.py` redrawn render with no
  text running out of its block (checked by eye on the PNGs, and by a bounding-box test
  in the scripts that reports any label wider than its block).
- P11 (ledger). Every old row of `tables/ledger.tex` is reproduced unchanged by the rerun
  (the inputs are the same registered files); the new rows equal the numbers of P7-P9.
- P12 (checker). `check_manuscript.py --compile` with the guide's forbid list: 0 undefined
  references or citations, 0 overfull boxes; hits only in the ledger appendix and the
  registration scripts (exception 1 of the guide).

## 2026-11-20T22:26Z  outcomes of P7-P10 (five registered runs, `nrpic-run submit --package tracks/D-bh-dress/note`)

Runs (each closed by nrpic-run with exit 0; outputs copied to `figures/`; every PNG looked
at, byte-identical to the preview I corrected by eye before registering):
D-20261120-222413-4a67fa2 (`fig_kerr.py`), D-20261120-222422-983f3f6 (`fig_newton.py`),
D-20261120-222424-d7cd958 (`fig_esrun.py`), D-20261120-222429-026731f
(`schem_architecture.py`), D-20261120-222430-452c907 (`schem_timeline.py`). Every input
file passed its run's sha256 record (stdout of each run).

- P7 holds. Constant-f equator peaks 0.9271e8 at 7.31 Gm (a = 0.5) and 1.0604e8 at 6.61 Gm
  (a = 0.8), largest deviation from FdRW fig_rho_a 8.84e-3 and 9.54e-3; Hernquist a = 0.8
  peak 3.922e18 at 5.06 Gm against 4.083e18 (ratio 0.961); chi^2 median 43.8 for 47 dof;
  late/early 0.998, 1.003, 0.999, 1.000, 1.000. The unit factor of the Hernquist curves
  is recomputed from `spike/kerr_lib.py` (KerrHernquist.Af); the peak on the 44-point grid
  times it is 3.918e18 against the refined 3.922e18 of the reference, so the factor is the
  one the reference used. Seen in the figure: our a = 0.8 Hernquist peak lies visibly below
  the published markers (the open 4 per cent, TO VERIFY in `spike/README.md`).
- P8 holds. M_ta 2.5966 / 2.5966 at a/a_i = 4 (dx = 1.06, 2.125 M) and 4.8159 at 8; dress
  0.7975 / 0.7966 and 2.1537; largest M_ta deviation from the kernel shells after a/a_i = 1.5
  1.04e-3, 1.20e-3, 3.07e-3; dress/M_ta 0.307 and 0.447. The analysis run read exactly the
  three run directories that `common.py` names (checked by the script). Seen in the figure:
  the dress deviations are a few per cent at a/a_i < 2, where the dress is small, and the
  measured profile at a/a_i = 8 follows the self-similar curve only outside lambda ~ 0.06.
- P9 holds to three digits throughout. Level +9.547e-4 / +9.374e-4; max |drift| from 100 M
  3.400e-4 / 1.368e-4; 100-165 M [-4.96e-5, +9.35e-5] / [-4.21e-5, +2.11e-5]; largest
  |drift difference| 2.037e-4 = 1.49 times the control's; wall 2.196e-3 / 1.594e-3 for
  tau <= 200 M; crossings 14.8262-14.8264 and 34.4366-34.4370 M (exact 14.8269, 34.4423);
  20 M group of the bubble run 244.09-244.51 M (exact 244.74), not reached by the control;
  probe lapse 1.292, 1.662, 1.636 against 1.377, 2.096, 3.577. Seen in the figure: the
  axis and diagonal wall tracers part from tau ~ 130 M on (panel c), the bubble run's
  horizon mass oscillates more than the control's between 100 and 165 M (panel b), and
  K at the plateau tracer turns positive between t = 50 and 130 M (panel f).
- P10 holds after one correction by eye: the first architecture render had the word "hole"
  without "black" in one block (paper-writing 5.6) and a third of the canvas empty below
  the legend; both changed before registration. Width check: 34 labels, none wider than its
  block. The timeline's "now" marker was moved from midway between G1 and G2 to just after
  G1, because G1 still has two open items.
