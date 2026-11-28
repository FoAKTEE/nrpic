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

# Batch 4a (lead, 2026-11-21 15:45 UTC on), packages finished since batch 2b

Packages: `verify_g1` (VERIFIER.md, batch 2b), `note` v1 (batch 3), `drift` (batch 3, partial:
run (vi) running at the start of this session). Predictions L23-L28 were written and committed
before any check ran (`../JOURNAL.md` 2026-11-21T15:50Z, commit bf279bd3). Own code:
`review_wave3/rv_batch4a.py` (own readers of the histories and of the trajectory files from
`docs/FORMATS.md`; a coherent part of the energy change different from the package's) and
`review_wave3/rv_note_b4a.py`. Runs: C-20261121-155049-ecf8893 (L23, L26, L27),
C-20261121-155116-ba83d16 (rerun of the verifier's V5b), C-20261121-155220-5c0d480 (FAILED: a
JSON key of my script; on record), C-20261121-155226-8ea9e47 (L25). Figures looked at:
`rv_drift_b4a.png`, `v5_t9ks.png` (rerun), `note/figures/fig_heat.png`,
`note/figures/schem_architecture.png`.

## 9. verify_g1 (closed; VERIFIER.md, commits 00adbb95 blind verdicts, 8329cf06)

Order: the blind verdicts were committed and pushed before the claims were read (git log:
00adbb95 precedes 2ad1421* and 8329cf06), as decision 0016 item 4 asks.

Confirmed from the artefacts:
- Item 1 (L23 HOLDS): my own count from `box.coll.hst` of run C-20261115-165902-f9b1c8f gives
  385554 collisions for mb1, mb8 and mb64 and 385838 for seed8. REVIEW-wave2.md:49 attached the
  count to the wrong run; corrected there.
- Item 2 (L24 HOLDS): rerunning `verify_g1/v5_t9ks.py` from the registered T9 outputs gives a
  JSON identical to the verifier's (run C-20261121-155116-ba83d16): KS p = 1.72e-4 for the light
  class of seed 3 at the temperature of the initial energy; p >= 0.084 at that of the final
  energy, >= 0.089 at each class's own. Figure looked at: only that one point lies below 1e-3.
- The verifier's other verdicts agree with numbers the lead had recomputed earlier (T4 with 16
  snapshots: REVIEW-wave2.md:68-71; T7 rows: section 1 above; t_c and King onsets).

Not confirmed by me: V4 (own Einstein-Vlasov solver and pulsation code) was not rerun; its
headline numbers (0.6348, 0.5331, 0.32143, 0.334032) agree with the track's own independent
runs and with the lead's L15 (C-20261119-151502-cb831a8).

WRONG or NOT CONFIRMED items of VERIFIER.md and what the track does:
1. REVIEW-wave2.md:49 count of seed 8 (WRONG wording): corrected (commit 4051c352).
2. T9 KS clause without a named temperature (UNSUPPORTED as written): `collide/TESTS.md`
   section 2c names the temperature of the final energy, AFTER the data, and keeps the strict
   reading (initial energy) as FAILED on record (seed 3 light class, p = 1.7e-4; its cause is the
   energy drift of that seed, +4.8e-3 in theta). T9 is in the track's own list, not among the
   tests the brief names in C-pre-1, so C6 does not change. Named for the orchestrator's review
   (outbox gate status).
3. Number-mode bias sizes (DIFFER in size): `heat/README.md` and TESTS 2c now give both sets
   with their windows (+5, +11, +43 percent; verifier +4, +13, +79). Finding unchanged.
4. F21's onset 0.750 (trial function): labelled as a late trial-function bound in
   `scope/REFERENCES.md`; the note v1 already does so (checked: `note/main.tex` line 132 calls
   it the trial criterion, sufficient for instability, with the exact onset below it);
   `gravothermal/README.md` labels it "(F21 trial)" already.
5. T6(b), T4 definitions: named in TESTS 2c (T6(b) at the mean reservoir temperature 0.015,
   literal 0.994, 1.027; at the final 0.01336 1.051, 1.086; both pass; T4 on 16 snapshots).
Items the verifier could not check (T5 entropy, card T7/T8, T6(a, c), T0b, T10b, T11, R6, the
MPI variant of T10, the growth pipeline, card cluster runs): T5 and the card T7/T8 are the gaps
that matter for C6. T7 on the card was recomputed exactly by the lead (section 1); T5 and T8
have no second check. They go to the G1 reviewer as stated limits, and T5 into the next
verifier's list.

## 10. note v1 (closed; commits d0cfe2ea, 2484c878)

Confirmed (L25 HOLDS, run C-20261121-155226-8ea9e47): the checker of `note/README.md` with
--compile on a copy of the note: 0 undefined references, 0 undefined citations, one overfull
box of 1.09 pt, 16 pages; the remaining candidates are run ids and locators in the ledger
appendix and two generated-file comments, the guide's accepted exceptions. Six ledger rows
equal the JSON of their runs to the printed digits (t_c 184.02, 185.29, 178.86 and sd 3.40 of
C-20261121-075202-1a37fb9; card T8 changes -0.0052, -0.0001, -0.0104 of C-20261120-223321-3d088d4;
drift ratios 0.22, 0.25, 0.10 of C-20261121-075359-26e3b31; growth-fit bias +6.9e-4 and -6.1e-4
of C-20261120-222716-9d86ebc). `fig_heat.png` panel (d) and the redrawn architecture schematic
show what the package says (looked at). Sec. IV H agrees with sections 2-3 above (drift mostly
numerical; y0 = 0.26 collapses at Kn = 1; threshold and collapsed mass left open).

Not confirmed: I did not read all 16 pages myself (the package did; the checker's compile and
the two figures I looked at are my evidence). The v1 ledger rows that no second agent has
recomputed: the growth-fit rows other than the two above (card T7 at theta 0.1 and 1 was
recomputed in section 1, run C-20261121-075535-b35b8fb).

Wrong: nothing in the note. The package's README item 5 (G0 locator) was half right: line 476
of 2601.17117 does hold 580 t_0 and 3e-8 M; the 200 M_sun is at 481. Corrected by an
appended section of `G0/REPORT.md` (the three numbers of its items 1-3 had been corrected in
wave 2, commit d3872ff5; `G1/STATUS.md` item 2 also carries the corrected bounds already).

What the track does: C16 MET (note v1 with G1 sections, checker passed with --compile); C9 and
C14 updated with the new run. The next note version adds the follow-up cluster figures (decisive,
drift (iii), (vi)) with their own script.

## 11. drift, batch 3 (partial: run (vi) was running; run (v) not submitted)

Confirmed (own reader, run C-20261121-155049-ecf8893; L26 HOLDS, L27 HOLDS):
- Run (iii) CC1 on M/8: largest centred 20 M mean of alpha_c - alpha_c(0) 0.00455 at 195.75 M
  (M/4: 0.03295 at 205.25 M), ratio 0.138; +-5 M mean at 300 M -0.00202; H-norm2 over 100-300 M
  7.86e-3 (M/4 8.53e-4); alpha_min >= 0.659; np = 1e5 and sum_m unchanged. CC2 ratio 0.099. All
  as the package reports (entry 12). The outward excursion of the M/4 controls is a mesh effect
  for both models [VERIFIED, one seed, one N].
- D2 with my own reader and my own coherent part (800 equal-count cells in E_K(0) and the
  conserved angular momentum |x x u|(0), times the sign of x.u): D over 25-300 M is 0.97-1.01
  times the package's in all four controls (1.06-1.09 over 25-75 M); D(M/8)/D(M/4) = 1.67 (CC1),
  1.54 (CC2). The diffusion is a linear random walk (figure: dots on the package's dashed
  curves), and the package's 200 cells (empty cells and cells of 2320 particles) do not leave
  coherent motion in its 'incoherent' part. D2.2 FAILED as the package says: the energy
  diffusion grows by 1.6, not by the factor 9 of the constraint floor.
- Predictions of the package: M8.1', M8.2'', M8.3', M8.4', D2.1, D2.3, D2.4 HOLD; M8.2', M8.5',
  D2.2 FAILED (entries 12, 14). I agree with each verdict from my numbers.

Not confirmed: the reading that the slow contraction on M/8 is either noise relaxation or a slow
evolution of the model in this code (entry 14) - that needs (vi) and (v). The Richardson
estimate of entry 12 is arithmetic on two meshes, not a convergence test [JUDGEMENT].

Wrong: nothing. Cosmetic: the title of my own panel (c) is clipped at the right.

What the track does: block A of `../threshold_scan/SCAN.md` will not run on M/4 (decided in
batch 2b; now for both models). Whether it runs on M/8 at N = 1e5 waits for (vi) (does the
contraction of a stable model turn?) and (v) (does it scale with 1/N?). Run (v) (0.3
card-hours, within the package's cap) is NOT submitted by this lead, whose task names no card
time; it is the first item of the next batch (section 12).

## 12. Run (vi), ended in this session (drift entry 16)

Slurm 4804 ran 15:38-16:30 UTC (0.87 card-hours) and continued run (i) from 300 to 680 M.
The lead closed it and analysed it twice: own reader C-20261121-163109-c8fff37 and the
package's compare.py C-20261121-163135-57f9296. Both give the same numbers. Figures looked
at: `rv_drift_vi.png`, `fig_cc2_M8A.png`.
- The continuation is exact: alpha_c joins within 8.7e-6, np and sum_m unchanged, the
  constraint floor is unchanged (7.87e-3).
- The contraction of the stable CC2 on M/8 does not turn. alpha_c - alpha_c(0) is -0.0043,
  -0.0118, -0.0151 and -0.0186 at 300, 400, 500 and 600 M, and -0.0216 over 640-680 M. r50 is
  -6.3 percent at 680 M. The slope is steady after 400 M, about -0.0035 per 100 M. There is no
  runaway and no collapse (alpha_min >= 0.652).
- Predictions VI.1, VI.3 and VI.4 hold. VI.2 (bounded) FAILED. The lead's L28 FAILED on its
  interval; its "no turn, no collapse" part held.

What the track does [JUDGEMENT]:
- A collisionless equilibrium should be stationary, so this drift is numerical until shown
  otherwise.
- Block A of SCAN.md does not start on M/8 at N = 1e5 until the source is known. First comes
  run (v) (N = 1e4 on M/4, 0.3 card-hours, predictions N.1-N.6), which tests the 1/N scaling.
- If the drift scales as 1/N, block A runs at N = 1e6 near the threshold. If it does not,
  the next leg is a finer mesh (an M/16 control).
- In either case every fate is read against a control of the same mesh, seed, N and length.


## 13. Batch 5 (2026-11-21, lead session "cards first"): what changed and what this lead checked

No helper package of C-sidm finished after the lead review of batch 4a (sections 9-12): the
only commits on `track/C-sidm` between that review and this session are the independent G1
gate review (`stage/G1/GATE_REVIEW.md`, commit 4b0297a9, runs C-20261121-165320-a2e557b and
C-20261121-165856-01f1503), which orch signed as PASS with reservations (coord/GATES.md,
decision 0025 item 1). Nothing stranded: `git status` was clean at the start. Packages still
open: drift (run (v) now submitted), models (step 5 paused since 2026-11-20), threshold_scan
(block A now queued, blocks B-D not), decisive (D2 now queued).

This session reviewed only what the decisions on the long runs needed:
- [VERIFIED] The kicks of the new particle files (run C-20261121-202552-8f91fb3, seeds 2 and 3
  of y0 = 0.334032) match those of seed 1 (run C-20261115-174556-3544e2c): mean radial
  velocity kin -0.003660 (seed 2), -0.003548 (seed 3) against -0.003657 (seed 1); kout
  +0.003202, +0.003316 against +0.003206; net momentum below 1e-17 in every file. The
  binding energy printed by the sampler (Eb = 0.035589, Z_c = 0.51191) is the model's.
- [VERIFIED] The new decks differ from the decks they derive from only where intended (diff
  read): `D2_cc2_kninf` equals the drift deck `cc2_kninf_M8` of runs (i)/(vi) except header
  and name; `D2_cc2_kn10_f<f>_s<s>` adds to it the collision block of `decisive/inputs/
  cc2_kn10_part_s<s>` with `coll_cell_factor` f; `A8_*` equal the M/8 control with tlim 600
  and the particle file and table of their model and seed.
- [BACKGROUND] For D2.1 (rate independent of the collision cell): core's own cluster test at
  Kn = 3 with cells of 2, 1 and 0.5 M gave 5037, 5219 and 5269 expected collisions
  (`coord/INTERFACES/collisions.md` line 342): a 4.6 percent rise for an eightfold smaller
  cell. Static refinement with collisions is supported (same file, lines 80-86); adaptive
  refinement during a run is not exercised (line 419), so no run of this batch uses it.

How the batch-5 runs answer the reservations of the G1 review (GATE_REVIEW.md, "Reservations
to carry to G2"):
| Reservation | What is queued | Remains |
|---|---|---|
| 1 conductivity at the percent level | heat_C1 (k lambda 0.2, two new seeds, three dx and dt 0.05) and heat_C2 (k lambda 0.1, three dx) on core-v0.6; H.1-H.4 | V1a (relativistic Chapman-Enskog reference) still needs a second agent |
| 2 threshold from collapse times or contraction against a control, three seeds | block A: every kicked run has the unkicked control of the same model, seed, mesh, N and executable; three particle seeds at y0 = 0.334032 | if run (v) shows 1/N contraction, the threshold seeds again at N = 1e6 |
| 3 definitions named before the run | reference quantities, windows (100 M), noise model (sigma_w) and refutations in JOURNAL.md 2026-11-21T20:25Z before submission | — |
| 4 card tests without a second check | — | a G2 verifier for T8, R6, the cluster runs and their controls once the runs end |
| 6 M/4 mesh unfit | all new cluster runs on M/8 | M/8 also contracts (drift run (vi)); its cause is what run (v) and the controls of block A measure |

## 14. Batch 11 (2026-11-24, analysis round after the card runs): what the lead checked

No helper package ran for C-sidm between batch 5 and this session: every commit on
`track/C-sidm` since 1274fb36 is a manifest commit of the sequencer (`C(run): register|finish`).
`git status` was clean; nothing stranded. The runs read here are the batch-5 queue (predictions
JOURNAL.md 2026-11-21T20:25Z); the analysis scripts are this session's own, so the second check
asked of the lead is a reader that shares no code with them (run C-20261124-132113-52c2abe,
`longruns/scripts/xcheck_b11.py`, figure read) plus the figures of every analysis.

| Item | Runs (analysis) | Recheck | Verdict of the lead |
|---|---|---|---|
| Cause of the ten FAILED chains | chain event logs; `sacct -a` | every log ends "STATUS FAILED (MAX_SEGMENTS=4 reached)" (D2f2s2: 2) after 4-8 SIGTERMs; jobs of another user in partition `priority` start at each SIGTERM time (e.g. 5162 at 05:09:12, our two segments cancelled at 05:09:11) | [VERIFIED] preemption, not physics; continued in place from the newest restart (JOURNAL 12:59Z) |
| Restart cadence of the continuation | C-20261123-032324-938ecbd, -20261124-120250-9e6a3ba | `output2` block of the new restart files: dt = 10, last_time = 10 and 110 | [VERIFIED] the command-line override acts on a restart |
| R(v), drift run (v) | C-20261124-130021-5c9c207, -130222-6a4924d | N.1 9.95, N.2 3.22, N.5 11.07 read from the JSON; N.4/N.6 recomputed from `diffusion.json` (mean_dE difference -0.00182, -0.00438, -0.00507 at 250, 275, 300 M) | N.1, N.2, N.4, N.5, N.6 hold by their letter, N.3 failed; N.4/N.6 carry a phase confound (JOURNAL 13:12Z) |
| T | C-20261124-131129-e93be29 (first attempt C-20261124-131113-b196c0e divided by t = 0: my bug, rerun) | log values read by hand: cpu 165.89 s for 20 M | [VERIFIED] 8.29 s per M |
| H.1-H.4 | C-20261124-131012-f920f45 (first attempt -130951-36beb5c failed, my bug) | per-case f_S printed; f0 arithmetic by hand | [VERIFIED] all four hold; H.4 by 1.85 sigma |
| D2 | C-20261124-130442-0819c88 (first attempt -130433-e84cb43 failed, my bug); xcheck | t_c at the record 164.25, 163.5, 166.0 M against interpolated 164.01, 163.41, 165.97 | [VERIFIED] D2.1, D2.3 hold, D2.2 failed; budget dH to 3.2e-16 of sum MH |
| Block A | C-20261124-130506-2ddce1f, -130634-3338d9b; xcheck | t_c at the record 535.0, 294.5, 449.0, 549.5, 230.0 M against 534.81, 294.47, 448.96, 549.26, 229.79; alpha_c changes at 400 M identical | [VERIFIED] two controls collapse; A.3, A.4 failed |

Found while checking, not yet explained [TO VERIFY]: the count test of the collision rate
before t_c, z = (n_coll - sum P)/sqrt(sum P), is -0.61 and +0.20 for f = 1 and 2 but -3.39 for
f = 4 (`d2.json`, count_z_before_tc), with n_noroot 509, 957, 1969 and n_balance 1.4, 2.0, 2.6
per cent of the collisions. Whether the n_balance events must be added back (decisive README
line 178) and whether the f = 4 deficit is the largest cells' pair sampling is a G2 verifier
item; it does not touch D2.1 (rates from n_coll within 2.1 per cent).

Defects of the noise model of block A (written before the runs) found here: the ripple and the
seed standard deviation are taken over windows that contain a collapse, so sigma_w is the size
of the collapse (0.07). The reader now takes the ripple before a time given on the command
line (`--ripple-tmax`, post hoc, labelled); partial windows (a run cut inside a window) still
enter the seed standard deviation, which inflates it; to be fixed before the seeds 2 and 3
are read (HANDOFF).

Later in the same session: `blockA_delta.py` drops a window that a run covers only in part
(complete windows only enter the seed standard deviation); not rerun on the interim data.

## 15. Batch 17 (2026-11-25, two queue runs ended): what the lead checked

No helper package ran for C-sidm since batch 12; `git status` was clean after the merge of
main (release core-v0.7). The runs read are the shared-queue entries q0016 N6c and q0017 M16
(predictions JOURNAL 2026-11-24T13:14Z), closed with `nrpic-run finish` before any analysis.
The N-series reader is new (`longruns/scripts/nseries.py`); it was first run on the closed
N = 1e5 control, where it reproduced the alpha_c changes of the batch-11 journal (+0.0024,
+0.0044, -0.0024, -0.0188, -0.093 at 100-500 M) before it read N6c.

| Item | Runs (analysis) | Recheck | Verdict of the lead |
|---|---|---|---|
| N6c, NS.1/NS.2 | C-20261124-221122-928c9eb (C-20261125-122010-fb3cc08) | reader reproduces the N = 1e5 numbers of batch 11; fig_nseries.png read: no collapse, alpha_c pulsation within [-0.0022, +0.0115], H floor 10x lower | [VERIFIED] NS.1 holds, NS.2 fails; relaxation reading |
| M16, M16.1/M16.2 | C-20261125-044843-2d048b6 (C-20261125-122020-031b67e) | d2_analysis.py unchanged; the M/8 runs reproduce their batch-11 values (t_c 164.01, 163.41, 165.97 M; rates 8.8512e-3, 8.8572e-3, 8.675e-3); fig_d2.png read | [VERIFIED] both hold; t_c 158.42 M |
| A324s1c+ | C-20261123-032324-938ecbd | chain DONE at 600 M; `nrpic-run finish` refuses (manifest with `continuations` read as hand-written) | not closed, not judged; to close by hand |

Not done, and why: the independent reader `xcheck_b11.py` was not rerun on N6c and M16 (time);
the M/16 t_c and the N6c no-collapse are read by one reader each. A G2 verifier is not sent: the
package has four failing and nine open items.

Decision of the lead: the six continuations of kicked N = 1e5 runs are removed from the queue
(they read a bracket that A.4 declared unfit, and NS.1 now explains why); the bracket is run at
N = 1e6 instead (q0046, q0047), and the gauge leg starts on D2 (q0048). The decks stay on the
core-v0.6 card build of their series without `dt_gauge` (cfl_number 0.25 below 0.47), a
deliberate departure from the instruction that new decks carry `dt_gauge = 0.9`: a control
and its kicked runs must share an executable and a step rule.

## 16. Batch 20 (2026-11-25, processors only): what the lead checked

No helper package ran for C-sidm since batch 17; `git status` was clean after the merge of main.
No queue run of C-sidm ended (N4c q0018 is pending as job 5297; it is not read). Three things
were checked from artefacts, each with a registered analysis and its figure read:

| Item | Runs (analysis) | Recheck | Verdict of the lead |
|---|---|---|---|
| A324s1c+ close-out | C-20261123-032324-938ecbd closed by `nrpic-run finish` (completed, 1.7733 card-hours, 11 jobs; 230 files hashed) | blockA_delta.py on all 15 block A runs (C-20261125-160056-a5b7282); the seed-1 numbers of batch 11 are reproduced (t_c 534.81, 549.26, 294.47, 448.96, 229.79 M); fig_blockA.png read | [VERIFIED] BA.1-BA.3 hold: the 0.324 control crosses 0.3 at 599.99 M; A.4 failed with all three controls |
| Horizon claims (decision 0040 item 3) | 24 simulations of stage/G2 and block A (C-20261125-160207-05b6db1) | own reader: deck blocks, horizon files, t_c from alpha_min recomputed; fig_horizon_audit.png read | [VERIFIED] no run had the finder or its diagnostics; no horizon claim in the package; every t_c is the lapse marker |
| A334s3c (q0023) state | C-20261124-082221-7f03a8e | chain events.log: four segments restarted from rst/cc.00000.rst written at t = 0; history ends at 0.25 M | HANDOFF of batch 17 was wrong ("from about 28 M"): q0023 reruns it from t = 0 (corrected here) |

Not rechecked here: 206.64 M (M/4, mean of the decisive part runs of wave 2) and 163.41 M (D2 f2,
abbreviated id in the checklist; checked only in an unregistered dev run, 163.407 M). Neither
rests on a horizon (no deck of decisive/ or longruns/ has a <fastflow> block).

Decision of the lead: the mesh and gauge legs of the N = 1e6 bracket granted by ruling 0039 item 3
are queued as four entries (predictions B20.1-B20.3, JOURNAL 2026-11-25T16:02Z) on the
executable and step rule of their controls, without the horizon finder (as the controls; the
legs judge fate and lapse t_c, not horizon times). The gauge variant is shift_eta 1.0, the
variant of D2eta1, so the track's gauge leg is one change for both series; a slicing change was
not chosen because the collapse marker is the lapse itself.

## 17. Batch 27 (2026-11-26, eight queue runs ended): what the lead checked

No helper package ran for C-sidm since batch 20; `git status` was clean after the merge of main.
Eight card runs had ended. Each was closed with `nrpic-run finish` before any analysis (checksums
of 50-80 GB each), then read with a registered analysis whose figure was looked at; every number
is judged against the prediction written before the run (JOURNAL entries named).

| Item | Runs (closed) | Analysis, figure read | Verdict of the lead |
|---|---|---|---|
| N4c, NS.3 (2026-11-24T13:14Z) | C-20261125-132112-edf3fbc (1.2892 card-h) | nseries.py C-20261126-120656-f5c62bb | [VERIFIED] relaxation branch holds: t_c 295.78 M < 300 M; floors scale as 1/N (ratios 9.78, 9.95) |
| N6b344, B17.5 (2026-11-25T12:01Z) | C-20261125-224959-d1d4494 (1.7747) | nseries.py C-20261126-121836-c7a76c1 | [VERIFIED] holds: t_c 252.31 M in [200, 400] |
| N6b324, B17.6 | C-20261126-020831-fabf2d7 (2.6283) | same | [VERIFIED] holds: no collapse, 20 M means in [-0.0119, +0.0150] |
| D2eta1, B17.4 (2026-11-25T11:56Z) | C-20261126-034500-4b34b1c (0.4453, FAILED: guard stop 190.4 M) | d2_analysis.py C-20261126-114801-ea62ac3, -121702-b6b1eda | [VERIFIED] holds: t_c 164.01 vs 163.41 M; rate ratio 0.992. The first figure drew m16 and eta1 alike (fixed in the script, redrawn) |
| D2f2s2+, D2.3 seed part (2026-11-21T20:25Z) | C-20261124-035054-c06503f (0.7228) | d2_analysis.py C-20261126-121702-b6b1eda | [VERIFIED] FAILED: 165.65 vs 163.41 M, 2.24 M against 2 M |
| N6b344e1, B20.3 first half (2026-11-25T16:02Z) | C-20261126-050124-00e10ae (1.7831) | nseries.py C-20261126-123219-f734997 | [VERIFIED] holds: t_c 252.41 vs 252.31 M; central lapse differs by <= 3.1e-4 before collapse |
| A334s3c+, A334s2c+ (priority 5) | C-20261124-082221-7f03a8e (1.6789), C-20261124-053105-2fcc8af (2.0081) | not read in this session | closed only; their seed scatter is not needed for the bracket |

Reader changes made before the analyses and committed first: nseries.py `--title`, `--control`,
`--band` and the 20 M band (ea62ac39); d2_analysis.py colours and line styles of m16 and eta1.

Decision of the lead: items C7 and C9 are located at one mesh and one N (bracket (0.324, 0.344)
around y_max = 0.334032 at N = 1e6 on M/8, fates repeated at N = 1e5, unstable side repeated with
shift_eta 1.0). C1, C2, C7, C9 move from FAIL to OPEN: what was failed (the N = 1e5 controls)
stays on record and no longer decides the items; they wait for q0055 (ended during the session),
q0057 and q0058. The G2 package is therefore not handed to a verifier yet (ruling 0041 item 3:
the verifier follows the legs). The G2 section of the note is written for what is settled.

Added at 12:43Z: q0055 A16b344 (C-20261126-043714-8ea1c35, 3.9744 card-hours) ended during the
session, was closed and read with nseries.py (C-20261126-124143-b485eac, figure read): on M/16 the
kicked 0.344 model collapses at 217.97 M against 252.31 M on M/8 (B20.2 held, shift -13.6 per
cent, bar 20). [VERIFIED] The unstable side of the bracket now repeats on two meshes, two gauges
and two N; the stable side waits for q0057 and q0058.

## 18. Batch 32 (2026-11-27, the last two G2 runs ended): what the lead checked

No helper package ran for C-sidm since batch 27; `git status` was clean after the merge of main.
The two card runs left for G2 had ended (600 M each). Each was closed with `nrpic-run finish`
before any analysis, read with a registered analysis whose figure was looked at, and judged
against the prediction of JOURNAL 2026-11-25T16:02Z.

| Item | Runs (closed) | Analysis, figure read | Verdict of the lead |
|---|---|---|---|
| A16b324, B20.1 | C-20261126-121449-1d37e77 (6.3844 card-h, 16 jobs, nine attempts cut by SIGTERM) | nseries.py C-20261127-084538-8e98060 | [VERIFIED] holds: no lapse-marker crossing by 600 M (alpha_min >= 0.651); 20 M block means of alpha_c - alpha_c(0) in [-0.0171, +0.0107], inside +-0.03 |
| N6b324e1, B20.3 second half | C-20261126-130519-1a79a66 (2.6175 card-h) | nseries.py C-20261127-084417-79c0e4d | [VERIFIED] holds: no crossing (alpha_min >= 0.656); largest 20 M difference from shift_eta 2.0 1.4e-5, bar 0.01 |
| C7, C9 | eleven threshold runs (RERUN.md) | the five bracket analyses; fig_g2_threshold (note run C-20261127-084828-b6ca5ce) | [VERIFIED] the fates of y0 0.344 (collapse) and 0.324 (holds) repeat on M/8, M/16, shift_eta 2.0, 1.0 at N = 1e6 and on M/8 at N = 1e5; [JUDGEMENT] the location converges, the collapse time of the unstable member does not (-13.6 per cent M/8 to M/16) |
| Note figures N5 | run C-20261127-084828-b6ca5ce (after a layout draft C-20261127-084609-36b1ecb, same numbers) | every new PNG read; others byte-equal to C-20261121-130335-d0cfe2e | N5.1 held (crossings equal nseries.py to all digits), N5.2 held (central cell of 0.344 at 220 M 27 times that of 0.324; the window-mean ratio is 3.5), N5.3 held for figures and ledger (runinfo.tex differs by construction, the run id) |

What could not be confirmed in this session: nothing beyond the fresh verifier's items (OPEN.md).
Small defects fixed: tick labels of adjacent panels collided and the smallest mosaic window was
shot-noise dominated at 96 cells (now 32); both fixed before the registered run that the note uses.

## 19. Batch 35 (2026-11-28 UTC, after the gate was signed): what the lead checked

Packages finished since batch 32: the fresh G2 verifier (batch 33, `stage/G2/verifier/`) and the
independent gate review (batch 34, `stage/G2/GATE_REVIEW.md`). G2 is signed, pass with
reservations (coord/GATES.md 2026-11-27; decision 0048 item 1).

Checked from the artefacts, not from the conclusions:
- The literature locator (kb-data/raw/arxiv/2009.08163/v1/src/paper.tex:948-972, 1056-1066):
  Table "First binding energy maximizer and zero", King y_max = 0.334; "According to the so-called
  turning point principle ... we find that this is not true"; the binding energy maximum
  hypothesis holds. [VERIFIED, read by me] The note's "turning point" was the wrong name for the
  right number; corrected (commit 3dbfa5d1f).
- The deleted conductivity snapshots: heat_C2 case `..._dx0.25` holds heat.part.00000 and 00016
  only, while its sha256sums.txt lists 51 heat.part files (3 cases x 17); the case directory holds
  case.json, reduced.npz, summary.json that the card run did not write; heatlib.SnapReducer
  removes every snapshot but the first and last (`os.remove`). [VERIFIED] The reduction now
  writes into its own run directory and deletes nothing (run_mode.py reduce --out); both runs
  queued again on core-v0.8 (q0092, q0093; predictions HR.0-HR.5).
- The reviewer's figure `scratch/C-sidm/C-20261127-232854-8859b86/fig_review_check.png`, looked
  at: the two unstable members cross 0.3 near 218 M (M/16) and 252 M (M/8), the eta1 member on
  the M/8 curve; the stable members' 20 M block means stay inside +-0.03 and turn back after the
  kick (A324s1i at N = 1e5 dips to about -0.025 near 600 M, still inside); the integrated H^2 of
  the M/16 member is about six times the M/8 members' and flat from 50 to 600 M. This matches
  R1-R3 as stated.
- The verifier's count-test table (VERIFIER.md section 4) is copied per member into CHECKLIST C8;
  I did not rerun its reader (collrate.py, run C-20261127-090913-97ee992).

Not confirmed by me: the verifier's own equilibrium solver value 0.3340322 and its per-run
crossings (I rely on the reviewer, who reproduced them with a third reader). Not wrong: nothing
found. What the track does with each WRONG or NOT CONFIRMED item of the verifier and reviewer:
`stage/G2/OPEN.md` (requests a-e applied; reservations mapped to scope/SCOPE_G3.md sections).
