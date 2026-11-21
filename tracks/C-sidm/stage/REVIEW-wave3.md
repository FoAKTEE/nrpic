# Review of wave 3 (round 1) of C-sidm

Lead session of batch 2b, 2026-11-21 (07:48-08:30 UTC), worktree merged with main at
core-v0.5. Packages of `PLAN-wave3.md` round 1 that ended since the wave-2b lead: `heat`
(closed), `decisive` (closed, job 5 pending at its close), `drift` and `models` (paused at the
usage flag of 2026-11-20 22:33 UTC), `note` (cut at 22:35 UTC with uncommitted work),
`verify_g1` (cut at 22:35 UTC; a helper of batch 2b works on it in this worktree now).

Method. Every check starts from the registered outputs, not from the helpers' conclusions.
Predictions L17-L22 were written before the runs (`../JOURNAL.md` 2026-11-21T07:51Z).
Own code in `review_wave3/`: `rv_clusters.py` (history reader, t_c, grid cosine fit; run
C-20261121-075336-49f92da) and `rv_heat_models.py` (T7 rows and extrapolations from the
per-seed values, figures of the models validation; run C-20261121-075535-b35b8fb). The two
card jobs that had finished unread were closed (`nrpic-run finish`) and analysed with the
packages' own scripts as their READMEs prescribe (C-20261121-075202-1a37fb9 decisive,
C-20261121-075359-26e3b31 drift). Every figure named below was looked at.

## 1. heat (closed; helper's verdict "C6 met")

Confirmed:
- T7 from the per-seed values (`heat/results/cardcpu_C-20261120-223203-b38a7d7.json`): my
  particle-number-weighted rows equal the package's to the last bit, and my weighted
  extrapolation in (k lambda)^2 gives kappa/kappa_1 = 1.024970 +- 0.002511 (theta 0.003),
  1.095709 +- 0.005144 (0.1), 0.991448 +- 0.003502 (1), equal to the package's (differences
  <= 3e-16). L21 HOLDS. Figure `rv_heat.png` (run C-20261121-075535-b35b8fb).
- Independent analysis by the verifier from the raw runs (verify_g1 V1b, V1c, runs
  C-20261120-223130-6742500, C-20261120-223133-2f98a0e): T7 at theta 0.003 1.019(4) with the
  eps = 0.2 nonlinearity removed (heat: 1.019 +- 0.004 on the processor seeds); T6(b)
  f = 1.027, 1.062 (heat: 1.029, 1.063). Agreement within the stated errors.
- Pass interval of T7 at theta 0.003, [0.99, 1.06]: met in every form (1.019-1.025;
  1.000-1.018 with the cell-size bias of T8 removed).
- The note's `fig_heat.png` (run C-20261120-223007-fe3f39c) shows the same rows and the
  isobaric reference through the step data.

Not confirmed (cannot be, with what exists):
- T8 rests on one card seed and one particle file for its seven variants; margin to the 2
  percent criterion 1.6 sd for dx.
- Whether the zero-cell-size conductivity at theta 0.003 lies 1-3 percent below the
  relativistic Chapman-Enskog value (1.0296, V1a): the weighted value is 1.7 se below it, the
  processor seeds 2.7 se; the rows do not follow the (k lambda)^2 form well (chi^2 6.6 for one
  degree of freedom; the k lambda = 0.2 row lies below the 0.1 row). V1a is itself unreviewed.
  [TO VERIFY] at G2 (cell-size and step series, about 0.3 card-hours).

Wrong: nothing. Cosmetic defects are on record in `heat/JOURNAL.md` (tick labels of
`T8_*_convergence.png`, pass band drawn on the theta 0.1 and 1 panels, clipped title).

What the track does: C6 is judged MET by the lead (stage/G1/CHECKLIST.md), with the T6-T8
wording of `../collide/TESTS.md` section 2b (accepted from the package's requests; no
criterion loosened). The G2 series for the CE deficit goes into the next plan.

## 2. decisive (closed; job 5 finished after the package)

Confirmed:
- Every collapse time t_c (first linear crossing of alpha_min = 0.3) of the 15 collisional
  runs recomputed by my own reader equals the package's to the last digit (L18 HOLDS); the
  cosine fits of the controls agree (CC1 399.25 M, A 0.01541; CC2 355.5 M, A 0.00859; D3
  282.25 M, A 0.00221; package: 399, 355, 282 M, 0.0022). Figure `rv_clusters.png`.
- D1 for CC2: the energy defect of the release operator does not move the collapse
  (particle minus cell +0.18 M against a seed scatter of 0.2-0.4 M).
- D3 (y0 = 0.26, 8.7 times CC2's distance from the Juttner onset) collapses at Kn = 1 at
  100.46 M and contracts without collapse at Kn = 10 in 300 M: the collapse is not set by the
  distance from the relativistic onset [VERIFIED from the histories; the reading is
  JUDGEMENT].

New (job 5, run C-20261121-062408-49fa14a; analysis C-20261121-075202-1a37fb9):
- CC1 at Kn = 10, cell seeds 2 and 3 collapse at 185.29 and 178.86 M (seed 1: 184.02 M).
  The cell-mode sd is 3.40 M, the particle-mode sd 0.65 M (two seeds), all five 2.83 M.
- Decision rule of decisive entry 10: difference particle minus cell 2.66 M, sigma 2.02 M,
  ratio 1.32: a mode effect is not shown and not excluded at the 1 M level.
- FAILED predictions: decisive entry 10 ("cell seeds within 1.5 M of each other and of
  184.02 M"), the lead's L17 (s3 outside [182.5, 186.5] M). Both recorded
  (`decisive/JOURNAL.md` entry 15).

Not confirmed: the package's reading that one seed is enough for t_c "away from the
threshold" holds for CC2 (sd 0.21 M over four runs) but not for the threshold model CC1
(about 3 M); D2 (collision cell size) did not run (no cap left).

Wrong: the package's statement "one seed is enough for t_c away from the threshold" is
right as worded, but the summary in its report ("seed scatter of t_c: 0.17 M for CC2, 0.92 M
for CC1") understates CC1's scatter by a factor three now that three cell seeds exist.
Corrected in `decisive/JOURNAL.md` entry 15 and in STATUS.

What the track does: at least three seeds per model within about 0.02 in y0 of the
threshold in the G2 scan; D2 gets its own allotment (2-5 card-hours) in the next plan.

## 3. drift (paused; run (i) finished unread)

Confirmed (D1, runs C-20261120-222211-aa1be86, -223139-2526c6d; my fits above):
- The outward excursion of the M/4 controls is a large radial oscillation started at a
  turning point (periods 399 and 355 M; areal radius of the 50 percent shell up by 9 and 5
  percent); the fluid fundamental periods of the King family with the F21 index (358, 305,
  260 M at y0 = 0.334, 0.314, 0.26) are of the same size. The failed D1.5 (period of order the
  dynamical time) stays on record.

New (run (i) cc2_kninf_M8, C-20261120-222533-ce50a86; analysis C-20261121-075359-26e3b31):
- On the M/8 mesh the excursion of CC2's control shrinks to R = 0.22 (cosine amplitude),
  0.25 (sine with trend), 0.10 (largest 20 M mean) of M/4: the M/4 excursion is numerical,
  of second order or faster in the cell size [VERIFIED, one model, one seed].
- At M/8 the control has no cosine form; after about 200 M it contracts slowly (alpha_c
  -0.0041, areal r50 -1.5 percent at 300 M; mean W +0.002), with a 9.3 times higher
  constraint floor (H-norm2 7.9e-3 against 8.6e-4) [VERIFIED]. Cause open [JUDGEMENT: the real
  slow mode, or relaxation by deposit noise].
- Predictions of drift entry 2: M8.1, M8.3, M8.4 HOLD; M8.2 FAILED (no comparable period;
  half period about 215 M). Entry 6 (d3_kninf) HOLDS: P = 282 M in [260, 380] and below 355 M,
  A = 0.0022 below 0.0086. My L19 (R in [0.4, 1.0]) FAILED: the mesh effect is larger than I
  expected. L20 HOLDS.

Not confirmed: whether the M/4 mesh moves the collisionless onset above y0 = 0.334 (drift
entry 4; needs run (iii), CC1 at M/8); the source of the M/8 contraction (needs run (v) at
N = 1e4 and a second seed).

Wrong: the drift package's preliminary reading that the excursion "is the fundamental radial
pulsation" of the model is not supported at M/8: the excursion is mostly the mesh. The period
match with the fluid mode at M/4 is a coincidence of scale or a mesh-shifted mode
[JUDGEMENT]. Recorded in `drift/JOURNAL.md` entry 8 and `drift/README.md`.

What the track does: block A of `threshold_scan/SCAN.md` runs on M/8 (or as an M/4-M/8 pair
at the bracket), about 22 card-hours instead of 9.5 (drift's estimate); run (iii) first, then
(v); runs (ii) and (iv) (M/4 continuations) are dropped from the plan. Every collisional
reading stays relative to a control of the same mesh and seed. RISKS item 3 rewritten.

## 4. models (paused at the flag)

Confirmed:
- v2 estimator on synthetic signals (npz of C-20261120-222716-9d86ebc): medians 0.019995,
  0.049949, 0.100036 against true 0.02, 0.05, 0.1 (bias below 0.04 percent); the 'first'
  reference biased high (medians +7.5, +6.1, +1.6 percent; the package's means +5.1, +5.2,
  +2.2 percent), which is diagnosis D1. L22 HOLDS. Figure `rv_models.png` (left).
- On the three compensated y_c = 0.5 runs ln|d_s| of alpha_c is concave from the start: the
  local slope falls from 0.07-0.08 to below 0.01 per M by 100 M (`rv_models.png`, middle and
  right), so a single exponential rate is not defined on these runs; over the common interval
  17.5-51.75 M the rates are 0.0557, 0.0584, 0.0617 per M (diag_v2 `common`), as the package
  says (D2).

Not done by the package (recorded, not redone): the King-run reading (step 5), the README
section and the "for G1 C2" statement; its figures (now drawn by the lead from its npz files,
which closes the figure rule for runs C-20261120-222716-9d86ebc and -223404-40668db).

Wrong: nothing found.

What the track does (lead decision on the package's request): a growth rate on runs is
quoted only with its fitting interval and the seed scatter over a common interval (D2(b));
the window-start rule is not changed after the fact. The quantities the G2 scan relies on
are times (t_c, crossing times), fates and contraction measures against a control
(D25-D150), all validated: 18 of 18 published times recovered (G1'), the D-measures with a
measured seed scatter (decisive). C2 is judged MET with that restriction.

## 5. note (cut at 22:35 UTC; not continued in this batch)

What exists: registered run C-20261120-223007-fe3f39c (all figure, schematic and ledger
scripts; inputs checksummed; 66 ledger rows, 23 claims, 3 differ as at G0). Its figures and
the two schematics, byte-identical in the worktree, were looked at by the lead and committed
(077b849d): `fig_box_summary`, `fig_heat`, `fig_onsets`, `fig_cluster`, the redrawn
architecture and the new data-flow schematic. Left uncommitted for the note session:
`main.tex` (G1 sections partly written), `references.bib`, `scripts/{common,ledger,
schem_timeline}.py`, `tables/ledger.tex`, `tables/runinfo.tex`, `schem_timeline.*` (edited
after the run). Remaining: N3 outcome in `note/JOURNAL.md`, G1 sections finished, a second
registered run_all, compile, checker with --compile, pages read, commit. The architecture
schematic marks "growth-rate fit, checked on runs" as to be ported and heat conduction "on
processors": both to be updated by the note session (C2 decided here; T7/T8 ran on the card).

## 6. verify_g1 (in progress in this batch)

Interim, from its committed journal: V1a (relativistic CE brackets), V1b (T7), V1c (T6(b)),
V2 (T1, T2: rate within 9.6e-5 of its own Moller integral, run C-20261121-074926-5d9ae56), V3
(T12: rate alpha0 psi0^6 times flat, twin identity, run C-20261121-075256-2084cb5) confirm
the claims they cover. No WRONG or NOT CONFIRMED item yet; `stage/G1/VERIFIER.md` does not
exist. The next lead answers each of its items.

## 7. Card time and pending runs

Card time of round 1 (sacct): heat 0.52, decisive 2.92 (five jobs), drift 0.69; total 4.13
card-hours. No card job of the owner queued or running at 08:00 UTC; this session submitted
none.
