# Journal of package a4res (E-stoch-inf, wave 3 round 1)

Pre-registered test of the resolution criterion for the strict A4 (the constraints second
order in the noise amplitude during the entry; SCOPE 4) against the reading A4' (SCOPE 4b;
outbox 20261119T151727Z__to-orch__a4-a5-rewording.md). Times in UTC.

## Entry 1, 2026-11-20 22:22Z: what was read, step 1 (stencil symbols) set up

Read: CLAUDE.md, coord/CHARTER.md to "Owners", decisions 0010 and 0016-0019, SCOPE 4 and
4b, the outbox proposal, `../ladder/README.md` and `../ladder/JOURNAL.md` entries 1, 6, 8,
9, 11, `../ladder/scripts/ladder_lib.py` and `ladder_analysis.py` (pair, judge),
core's `tracks/core/interfaces/scalar_field_3.md` section 4, `python/nrpic/sf_lattice.py`
and `tracks/core/analysis/scalar3/a1_twin.py` on `core/scalar-3` (18bae3c), the READY of
`scratch/core/exe/core_scalar-2/` (executables of a58e95b), `athenak/src/utils/
finite_diff.hpp` and the derivative calls of `z4c_calcrhs.cpp`, `z4c_adm.cpp`,
`scalar_field_rhs.cpp`.

What core claims (another owner, unmerged branch) [TO VERIFY by this package]:
C1 the first-order part of H, M_i at late entry is the defect mu = kap - q^2 of the
discrete contracted Bianchi identity, mu/k^2 = 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16 cells per
wavelength; C2 the largest ratio in time of first- to second-order part falls below 1 at
12.7 and below 0.1 at 18.7 cells per shortest source wavelength (scan at nmax2 = 64 with N
varied: twin odd part over the measured even part of core's 64^3 runs; values 692, 213,
77, 14.9, 4.0, 1.38, 0.25 at 4, 5, 6, 8, 10, 12, 16 cells); C3 strict A4 needs
nmax2 <= (N/12.7)^2; C4 (remark on SCOPE 4 A2) the ladder's stencil-k^2 reference (6.2e-3
against 1.2e-4 at 256^3) "may use the second-order stencil symbol", the code's sixth-order
symbol being 1.8 percent low at k dx = pi/2.

Facts read in the source [VERIFIED by reading]:
- Z4c and the scalar field use `Dx` (first difference), `Dxx` (second difference, the
  diagonal second derivatives) and `Dxy` (the product of two first differences, the mixed
  ones) of `finite_diff.hpp`; with `nghost = 4` (input) these are the sixth-order stencils.
- The mode file: `scalar_field_noise.cpp` at a58e95b (the commit of the executable),
  lines 401-431: a row whose |n|^2 is not a shell of the mode set (0 < |n|^2 <= nmax2) is
  skipped ("if (it == shell_of.end()) continue;"); a missing shell is fatal;
  `noise_mode_scale` multiplies R and dR/dtau of every shell (slice and sources). So the
  rows of `modes_n4096.txt` beyond noise_nmax2 are ignored, as coord/INTERFACES/
  scalar_field.md section 7.3 says ("extra rows ignored"). CONFIRMED.
- `ladder_lib.py:270-277` (`k2_stencil`, used by `reference_modes_stencil` for the A2
  'stencil-k^2' reference) is the sixth-order symbol per axis,
  -(-49/18 + 3 cos th - 0.3 cos 2th + (2/90) cos 3th)/h^2, not the second-order one.

Step 1 (script `scripts/stencil_symbols.py`): parses the coefficients of Dx and Dxx for
NGHOST = 2, 3, 4 from the source, forms q h, kap h^2 and mu/k^2 at 4, 5, 6, 8, 10, 12, 16
cells, and evolves the ladder's linear reference with the continuum k^2 and with the
sixth-, fourth- and second-order k^2 for all 3363 wave-vector classes |n|^2 <= 1024 of
P256 to t = 8.5.
Expectation: C1 holds to the quoted digits (it is arithmetic on the coefficients, which
the ladder's entry 8 already read as 1/90, -3/20, 3/2, -49/18); for C4, the sub-horizon
phase error of the sixth-order k^2 accumulated over about 31 radians for |n| = 32,
k dx = pi/4 (0.5 x 3.8e-4 x 31 = 6e-3), reproduces the ladder's 6.25e-3, while the
second-order symbol (5 percent low in k^2 at pi/4) would give an O(1) difference: C4
refuted. Refuted if the sixth-order reference differs from the ladder's number by more
than 1 percent, or the second-order one matches it.
Disclosure: a development run of the script (not registered, `scratch/E-stoch-inf/tmp/
sym_test`, 22:20Z) already printed the numbers before this entry; the registered run
below is the one cited.

## Entry 2, 2026-11-21 13:08Z: outcome of step 1 (run E-20261120-222312-6ee4bc5)

A new session (batch 3) continues the package from the worktree: entry 1, the step-1
script and its registered run were committed; `a4lib.py`, `make_list.py`,
`twin_predict.py` were left uncommitted by the session cut on 2026-11-20 and are
committed now (the exact-time Twin of `twin_predict.py` is made optional, `--exact`: a
dev test of this session, `scratch/E-stoch-inf/tmp/a4res_dev`, not registered, showed
DOP853 at rtol 1e-11 needs about 30 s per 0.25 of time per set-up; the CodeTwin, which
steps like the code, takes 0.2-0.5 s).

Outcome (`run.log`, `symbols.json`, `fig_symbols.png` of the run, looked at):
- C1 CONFIRMED [VERIFIED, own arithmetic on the coefficients parsed from
  `finite_diff.hpp`]: mu/k^2 = 1.0988e-1, 3.5418e-2, 1.3172e-2, 2.5907e-3, 7.1049e-4,
  2.4380e-4, 4.4449e-5 at 4, 5, 6, 8, 10, 12, 16 cells per wavelength (one axis); core
  quotes 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16: equal to the quoted digits. At k dx = pi/2
  the second difference is 1.83 percent low in k^2 and the squared first difference 12.8
  percent low; the second-order second difference is 18.9 percent low (core: 1.8, 12.8,
  "about 19"). mu falls as (k dx)^6 (panel b: slope 6 above 8 cells).
- C4 REFUTED: the ladder's stencil-k^2 reference uses the sixth-order symbol
  (`ladder_lib.py:304-312`, `k2_stencil`). Evolving the ladder's reference with it for
  all 3363 classes |n|^2 <= 1024 of P256 to t = 8.5 gives a largest difference to the
  continuum reference of 6.255e-3 at n = (32, 0, 0); the ladder's judge recorded
  `max_rel_diff_references` = 6.2548e-3 (`ladder/results/final/P256_judge.json`). The
  fourth-order symbol would give 6.6e-2 and the second-order one 0.83. So the second-order
  symbol does not explain 6.2e-3; the sixth-order symbol does, as the sub-horizon phase
  error it accumulates from N* to crossing. The run follows the continuum reference
  (1.2e-4) because a mode enters the lattice through the window from the code's own
  continuum mode functions (ladder JOURNAL entry 6 [JUDGEMENT], SCOPE 4 A2 as amended);
  this package did not test that further.

## Entry 3, 2026-11-21 13:09Z: predictions for the card job (before it is submitted)

Set-ups (`scripts/a4lib.py`, list `inputs/card.list` from `scripts/make_list.py`): SR,
input `../ladder/inputs/sr_base.athinput`, one mode file `../ladder/inputs/
modes_n4096.txt` for all (its rows for |n|^2 <= 256 equal those of `modes_n256.txt`
bit for bit; those of `modes_n64.txt`, the ladder's L runs, differ by up to 2.7e-5 in
absolute value: checked in this session), seed 20261115, so every set-up shares one
family of phases. N64q16, N64q25, N64q36, N64q64 (N = 64, nmax2 = 16, 25, 36, 64: 16,
12.8, 10.7, 8 cells per shortest source wavelength) and N128q100, N128q64 (N = 128: 12.8
and 16 cells). Four members each, noise_mode_scale s = +1, -1, +1/2, -1/2 (suffixes p, m,
ph, mh). All: tlim = 4.5, dump_dt = 0.125 (37 dumps, the same times in all members of a
set-up), dump_constraints = true, dump_metric = false, Courant 0.25, executable
`scratch/core/exe/core_scalar-2/athena_gpu` (a58e95b). Rows of the mode file beyond
noise_nmax2 are skipped (entry 1, source read).

Analysis rules, fixed now (`scripts/a4_analysis.py`, written before the job ends):
- Pairs A = (p, m), B = (ph, mh); dumps matched by time and cycle (with equal tlim and
  dump_dt all 37 should match; a dropped dump is a finding). Odd part o = (f+ - f-)/2,
  even part e = (f+ + f-)/2 with its box mean removed, rms over the cells (M: rms of the
  vector), absolute units; O_A, E_A, O_B, E_B.
- Floor per dump, measured: the first-order part cancels in o_A - 2 o_B and the
  second-order part in e_A - 4 e_B (up to s^3 and s^4 terms, 1e-10 smaller), so
  f_o = rms(o_A - 2 o_B)/sqrt(5) and f_e = rms(e_A - 4 e_B)/sqrt(17) estimate the part
  that does not scale with s, if the floors of the two pairs are independent with equal
  rms [JUDGEMENT]; f = max(f_o, f_e).
- Entry window: dumps with t > 0 up to one e-fold after the top shell's window reaches
  W = 0.999 (twin background; t = 3.1-4.1).
- Strict A4 holds in a set-up iff, for H and for M: (i) O_A < E_A at every entry dump
  with max(O_A, E_A) > 3 f; (ii) E_A/E_B within 4.00 +- 0.05 at every entry dump with
  E_B > 10 f_e.
- A4' (SCOPE 4b): (a) = (ii), and E_A of N64q64 and N128q64 (both K = 8) agree within 5
  percent where above 3 f; (b) O_A/O_B within 2.00 +- 0.05 where O_B > 10 f_o, and the odd
  part converges between N64q64 and N128q64 at an order in [4, 6] (A5) where O_A(128) >
  3 f; (c) record <|H|/[H]> <= 1e-9 and <|M|/[M]> < 1e-3 at every cycle (`sr.sf.con.hst`,
  columns 3 and 6); (d) the sign-flip control is not part of this job: not tested here.
- Twin comparison: O_A against core's CodeTwin evolved at the run's own step times
  (`sr.sf.hst`), where O_A > 3 f_o.

Quantitative prediction (a), run E-20261121-130841-c406130 (twin of core/scalar-3 at
88544a5, identical to python/nrpic/ on main after the merge of core-v0.5; looked at
`fig_prediction.png`): the CodeTwin first-order parts per dump are in `prediction.json`.
Cross-check on the ladder's runs (another mode file, not an anchor): CodeTwin/measured
odd part of H = 1.000 +- 0.002 at every dump of L32 to t = 7.0, of L64 and Q64 from
t = 1.5 to 5.0, and 0.94-0.95 for L128 at t = 2.5-3.0 where its floor is a third of the
odd part; M likewise. Even part: model `a4lib.EvenModel` [JUDGEMENT] from the ladder's
measured L64 and Q64 pairs, uncertain by a factor 2. Predicted largest odd/even ratio
in time (H; M) and time of the maximum:

| set-up | cells | H | M | strict A4 predicted |
|---|---|---|---|---|
| N64q16 | 16.0 | 0.46 (t 1.89) | 0.17 (t 2.38) | holds |
| N64q25 | 12.8 | 0.99 (t 2.01) | 0.52 (t 2.63) | undecided (within the factor 2) |
| N64q36 | 10.7 | 2.8 (t 2.26) | 1.9 (t 2.77) | fails |
| N64q64 | 8.0 | 15.4 (t 2.50) | 13.8 (t 3.02) | fails |
| N128q100 | 12.8 | 0.92 (t 2.76) | 1.05 (t 3.25) | undecided |
| N128q64 | 16.0 | 0.27 (t 2.50) | 0.23 (t 3.01) | holds |

Log-log crossing of 1 in the N = 64 family: 12.8 cells (H), 11.7 (M); N = 128: 12.9 (M).
Core's scan (nmax2 = 64, N varied): 1.38 at 12, 0.25 at 16, crossing 12.7 [TO VERIFY].

Predictions (each refuted as stated):
- Q1 strict A4 holds at 16 cells (N64q16, N128q64) and fails at 10.7 and 8 cells
  (N64q36, N64q64). Refuted by any other verdict in these four.
- Q2 the largest ratio (max of H and M over the entry window) crosses 1 between 11 and
  14.5 cells, in the N = 64 family (log-log interpolation) and consistent with the
  N = 128 pair. Refuted if the crossing lies outside.
- Q3 the measured odd parts equal the CodeTwin within 10 percent wherever O_A > 3 f_o,
  every set-up, H and M. Refuted by any such dump outside [0.9, 1.1].
- Q4 halving: E_A/E_B = 4.00 +- 0.05 and O_A/O_B = 2.00 +- 0.05 at every qualifying dump.
  Refuted by a qualifying dump outside.
- Q5 the measured largest ratio lies within a factor 2 of the predicted one in each
  set-up (tests the even model). Refuted by a set-up outside.
- Q6 the even parts of N64q64 and N128q64 agree within 5 percent at every dump above
  3 f (the ladder's L64/L128 pairs: at most 3.5 percent in H, 4.7 percent in M to
  t = 4.5). Refuted by a deviation above 5 percent.
- Q7 the odd part converges between 8 and 16 cells at the twin's order (log2 of the
  twin's ratio, 5.9 at t = 2.6) within 0.3 where above 3 f. Refuted otherwise.
- Q8 record: <|H|/[H]> <= 1e-9 and <|M|/[M]> < 1e-3 at every cycle of every run.
Cost expected (READY of core_scalar-2): 64^3 runs seconds, 128^3 runs 1-3 min each; job
under 30 min of one card; dumps 21 MB (64^3) and 168 MB (128^3), about 62 GB in all.

## Entry 4, 2026-11-21 15:20Z: outcome of the card job and its analysis

Card run E-20261121-131000-b23055b (Slurm 4798, `core_scalar-2/athena_gpu`): queued
13:10Z, ran 15:05-15:16Z (11.2 min of one card, 0.19 card-hours); 24 runs, all exit 0;
64^3 runs 6-7 s each, 128^3 runs 70-73 s each; 37 dumps per run, 58 GB. Analysis run
E-20261121-151643-c2c0f5a (`a4_analysis.py` as committed at 94dfa93 before the job ran;
the rerun named below differs only in a figure margin), read the dumps sequentially from
the page cache right after the job, 62 s. All 37 dumps matched in every set-up (none
dropped). Figures looked at: `fig_ratio.png`, `fig_checks.png`, `fig_parts_H.png`.

| set-up | cells | largest odd/even H (t) | M (t) | E_A/E_B (n dumps) | O_A/O_B (n) | odd/twin | strict A4 |
|---|---|---|---|---|---|---|---|
| N64q16 | 16.0 | 0.455 (1.77) | 0.314 (2.26) | 3.980-3.999 (22) | none above 10 f_o | 1.004-1.056 | holds |
| N64q25 | 12.8 | 1.000 (2.01) | 0.795 (2.50) | 3.981-3.999 (37) | 1.993-1.997 (17) | 1.000-1.052 | holds (0.9997) |
| N64q36 | 10.7 | 2.81 (2.14) | 2.45 (2.77) | 3.981-4.000 (46) | 1.994-2.000 (36) | 1.000-1.049 | fails |
| N64q64 | 8.0 | 15.5 (2.50) | 13.8 (3.02) | 3.981-4.000 (57) | 1.997-2.000 (47) | 1.000-1.049 | fails |
| N128q100 | 12.8 | 0.939 (2.76) | 0.858 (3.25) | 3.984-3.999 (13) | none above 10 f_o | 1.002-1.057 | holds |
| N128q64 | 16.0 | 0.273 (2.50) | 0.240 (3.01) | 3.984-3.997 (9) | none above 10 f_o | 1.043-1.059 | holds |

(n counts H and M dumps together.) Against the predictions of entry 3:
- Q1 HELD: strict A4 holds at 16 cells (N64q16, N128q64) and fails at 10.7 and 8.
  At 12.8 cells it holds too, at N = 64 by 3e-4 (largest H ratio 0.9997), at N = 128
  with 0.939: 12.8 cells is the boundary itself.
- Q2 HELD: the largest ratio (max of H and M) crosses 1 at 12.80 cells in the N = 64
  family and at 12.66 in the N = 128 pair (H 12.80 and 12.66, M 12.33 and 12.46). Core's
  12.7 [C2] is confirmed. Core's scan point at 16 cells (0.25, K = 8) against 0.273
  measured at K = 8 (N128q64); at 8 cells 14.9 against 15.5 (N64q64). At equal cells the
  ratio depends on K a little: 0.455 at K = 4 against 0.273 at K = 8 (16 cells).
- Q3 HELD: measured odd part / CodeTwin within 1.000-1.059 wherever O_A > 3 f_o, all
  set-ups, H and M. The excess up to 6 percent sits where the floor is a third of the
  odd part (N128q64).
- Q4 HELD where testable: E_A/E_B 3.980-4.000 at every qualifying entry dump; O_A/O_B
  1.993-2.000 in N64q25, N64q36, N64q64. In N64q16, N128q100 and N128q64 no dump has
  O_B > 10 f_o (the odd part of the half pair peaks at 5.8, 8.2 and 1.9 floors): A4'(b)
  is untested there by the registered rule. The analysis script prints "A4' fails in b"
  for these three because it counts an empty set as a failure; that is a defect of the
  script's wording, not a measured failure (corrected in README, script unchanged so
  that the registered output stays reproducible).
- Q5 HELD: measured/predicted largest ratio 0.98-1.02 (H), 0.82-1.90 (M).
- Q6 FAILED at one dump: E_A(N64q64)/E_A(N128q64) = 0.891 (H), 0.952 (M) at t = 0.147,
  the first dump after t = 0; every later dump within 0.968-1.031 (H) and 0.968-1.019 (M).
  Candidate cause, not yet named as the cause: the log-linear interpolation of the 128^3
  even part from its dumps at t = 0.135 and 0.258 onto t = 0.147 while E falls fast after
  the initial slice. Post-hoc test (`scripts/post_checks.py`, prediction fixed now): with
  a three-point quadratic interpolation in t, and at t = 0 where both runs dump at the
  same time, the ratio lies within 1 +- 0.05. Refuted (interpolation not the cause) if
  either lies outside.
- Q7 HELD: odd order between 8 and 16 cells 5.80-5.84 where O_A(128) > 3 f, twin
  5.89-5.90 (within 0.1). A5 band [4, 6]: held.
- Q8 HELD: <|H|/[H]> at most 2.6e-12 and <|M|/[M]> at most 1.5e-5 over all cycles of all
  24 runs (limits 1e-9 and 1e-3), so A4'(c) holds everywhere.
Measured floor f_o at t = 0.13: 4.1e-13 (64^3) and 2.2e-12 (128^3) in absolute rms of H;
the ladder's floor model predicted 4.1e-13 and 2.3e-12 (entry 3 run, `prediction.json`).
A4' (SCOPE 4b, as ruled in decision 0021): (a) holds in all six set-ups; (b) holds in the
three where testable; (c) holds; (d) not part of this job.

## Entry 5, 2026-11-21 15:25Z: post-hoc check of Q6, final run, close

Run E-20261121-152010-371d5f1: `a4_analysis.py` again (fig_checks margin only; every
number of `a4res.json` equal to E-20261121-151643-c2c0f5a apart from wall times, checked),
then `post_checks.py` (`results/post.json`, `fig/fig_post.png`, looked at).
- Q6 post hoc, prediction of entry 4 REFUTED: at t = 0, where both runs dump at the same
  time, E_A(N64q64)/E_A(N128q64) = 0.99993 (H) and 1.00000 (M); but the three-point
  quadratic interpolation still gives 0.917 (H) and 0.961 (M) at t = 0.147 (log-linear:
  0.891, 0.952). The even part falls by a factor 2.7 from t = 0 to 0.135 and is not
  monotonic over the next dumps (H at 128^3: 3.42e-11, 1.25e-11, 0.97e-11, 1.41e-11 at
  t = 0, 0.135, 0.258, 0.380), so the dump spacing of 0.125 does not resolve it and no
  interpolation settles the point. Cause not named. A run that would settle it: N64q64
  and N128q64 (p, m) with dump_dt a multiple of the 64^3 step (both runs then dump at
  the same times), about 3 card-minutes; not submitted (the package's question does not
  depend on it: the strict-A4 verdicts use no comparison across resolutions).
- A4'(b) post hoc at O_B > 5 f_o: O_A/O_B = 1.973-1.979 (N64q16, H, 5 dumps),
  1.972-1.991 (N128q100, H and M, 21 dumps), inside 2.00 +- 0.05; N128q64 has no such
  dump (its half-pair odd part peaks at 1.9-2.0 floors), N64q16 M none (3.7 floors).

Card time of the package: 0.19 card-hours (cap 0.5). Pending runs: none.
