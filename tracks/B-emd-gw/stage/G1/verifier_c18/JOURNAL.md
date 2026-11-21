# JOURNAL of stage/G1/verifier_c18 (fresh verifier for G1 item C18 of B-emd-gw)

Labels: [VERIFIED] measured or derived here in the run named; [JUDGEMENT] my inference;
[BACKGROUND] standard fact; [TO VERIFY] open.

## Entry 0 (2026-11-21 04:58 PST): what I read, scope, what I will not read

Read: CLAUDE.md, coord/CHARTER.md to "Owners", decisions 0016 and 0021, the coverage lists of
the earlier verifiers (stage/G0/VERIFIER.md section 1; stage/G1/VERIFIER.md head; verifier3
sections 1 and 7), the C18 line of stage/G1/CHECKLIST.md (it names what is not yet recomputed),
the batch reports of this owner (scratch/orch/wave3_reports/B-emd-gw.md), the note's ledger
(note/tables/ledger.tex) and the note's text of Secs. II B, III B, V (definitions).

For the definitions of the ledger quantities (which mode, which range, which normalization) I
read note/scripts/r2data.py and the docstring and per-dump definitions of
first_source/fslib/modes.py (lines 1-160). I did not read the numbers in any JSON of the track,
nor the track's reviews (stage/REVIEW-*.md), STATUS, HANDOFF or the journals. Every number
below comes from my own code in scripts/, reading the raw dumps (bin, double-precision bin,
rst) under scratch/B-emd-gw/<run>/ directly. This is a limit of independence: a definition that
is wrong in the track's code would be shared; where I can I check each definition against the
physics (normalization of c_+ against the static strain s, a(tau) against the mean of chi).

Not yet recomputed independently (from CHECKLIST C18 and the batch-2a lead report):
(i) the second-round table, ledger lines 197-217; (ii) gauge rows 120-125 and eps = 0.1, 0.3 of
rows 116-117; (iii) wave-1 rows outside the G0 claims; plus (iv) the results of first_source
round 3 (batch 2b, finished since).

Plan, in order of priority (a few hours, no card time): (i), (ii), (iv), then a sample of (iii).

## Entry 1 (05:00 PST): predictions, written before any of my code touched a dump

Tools (test T0, analytic fields, run to be registered):
- T0a: my reader returns the header time and assembles 2x2x2 MeshBlocks of 32^3 into 64^3
  arrays; the double and single dumps of the same time agree to float32 rounding (< 1e-6
  relative on chi, < 1e-7 absolute on gt_ij - delta_ij). Refuted by any larger difference or a
  block misplacement (a jump at the block faces of an analytic test field).
- T0b: on an analytic field h_ij = A e+_ij cos(K.x) + B ex_ij sin(K.x) + a pure gradient
  d_i xi_j + d_j xi_i, my TT projection and mode extraction return c_+ = A, the gradient part
  vanishes to 1e-14 relative. Refuted by anything above 1e-12.
- T0c: my junk solution g(tau) from the closed form (spherical Bessel j1, y1 over x) and from
  a DOP853 integration agree to 1e-9; g -> 1 with an envelope ~ 1/a.
- T0d: my G_tot (written from the note's Eq. (gaugepiece)) on an exact pure-gauge metric
  delta + (J^T J - delta) traceless with J = 1 + D of a small periodic xi: TT h - G_tot falls
  as the cube of the gauge amplitude (TT h alone as the square). Refuted if the slope of
  TT h - G_tot is below 2.7.

Second-round table (i), from the raw dumps of runs B-20261119-142833-19edd82 (cards, 64^3,
8 per cell), B-20261115-164059-d802e82 and -165353-b592d43 (wave-2 scan), with the ledger's
definitions:
- P1 (rows 204, 205, 209-215, 200 max_TT): each printed number reproduced to its printed
  digits (relative difference <= 0.5 per cent, or the last printed digit) [prediction].
  Refuted: any number off by more than 1 per cent; then I find which reading is wrong.
- P2 (row 197): the rerun of eps = 1 against the first run, double precision: largest relative
  difference of c_+ of order 1e-12 (within a factor 3 of the ledger's 9.5e-13 and 4.7e-13).
  Refuted: above 1e-10 (that would mean the runs differ beyond rounding).
- P3 (row 198): the two initial-data tools without jitter give identical files (difference
  exactly 0 on positions, velocities, masses and fields; 2097152 particles). Refuted by any
  nonzero difference.
- P4 (row 207): the share of TT power at |k|L/2pi >= 16 is above 0.9 for the jittered runs
  at a = 2.3 and 12 and below 1e-4 for the eps = 0.1 signal at a = 12; ledger digits
  reproduced to 1 per cent.
- P5 (row 208): kinetic over gradient energy of the TT part at a = 140 is << 1 (quasi-static),
  ledger digits to 2 per cent.
- P6 (rows 211-213): physics check independent of the ledger: the departure ratio
  delta = 0.01 over 0.0025 at fixed a is close to 16 (between 12 and 22) for a = 30-60.
- Rows 199 (constraint residuals of the initial data), 201-203 and 206 (the noise prediction)
  need the initial-data residual computation and the second-order noise prediction; I attempt
  them only if time is left, and say so if not.

Gauge rows (ii), runs B-20261115-164059-d802e82 (64^3 zero shift eps = 0.1, 0.3),
-165353-b592d43 (eps = 1 both gauges), -165525-f7c2004 (32^3, all cases):
- P7 (rows 116, 117, eps = 0.1 and 0.3; also eps = 1 as a control against verifier3): my
  |G_tot/c_+| reproduces the ledger to 3 per cent. Refuted above 5 per cent.
- P8 (rows 120-123): medians and ratios to 5 per cent.
- Row 124 (magnetic Weyl) and 125 (slicing of the earlier three-wave runs): attempted only if
  time is left.

Round 3 (iv), batch-2b report of first_source: P12 (1, 8, 27 per cell differ by at most
7.8e-5, 7.4e-5 for 2 <= a <= 40), P13 (128^3 vs 64^3 at most 1.6e-4 and 1.8e-4 for a <= 40;
rms after crossing 1.30e-2 vs 3.39e-2), (1 + eps^2) test Q = 1.006-1.036 at a = 30-60:
- P9: each reproduced to 3 per cent from the raw dumps. Refuted above 5 per cent.

## Entry 2 (05:10 PST): tool tests T0 (run B-20261121-130334-a86cff6), P1, and more predictions

T0 outcomes against entry 1:
- T0a CONFIRMED: double vs single bin of the same time (jit0p3, four pairs): chi relative
  <= 6.0e-8, gxx absolute 6.0e-8 (float32 rounding of 1 + h), gxy 1.5e-11; rst vs bin of the
  wave-2 eps1 run (three pairs, same times to all digits): chi 3.9e-8 to 5.9e-8, gxy <= 5.8e-11.
  The restart layout of the wave-2 executable has RegionIndcs of 19 int and a data-size word
  per MeshBlock (my first parse assumed 22 int and a total: corrected before any use).
  a from the mean of chi equals a(tau) = (1 + tau/2)^2 to 3e-5 relative.
- T0b CONFIRMED in substance, my bound REFUTED for one route: the FFT route returns c_+ = A
  to 3e-16 and the TT projection of a pure gradient is 0; the direct-sum route returns c_+ to
  3.9e-12 relative (absolute 1.2e-17), above my bound of 1e-12 (summation rounding of the
  phase factors; irrelevant at the signal level of 1e-5 to 1e-7).
- T0c CONFIRMED: closed form against DOP853, largest difference 1.2e-11; envelope times a is
  1.1-1.24 over tau = 5-17.
- T0d CONFIRMED: pure gauge without TT part: TT h slope 2.000, TT h - Gq slope 3.000; with a TT
  wave of the same order: TT h - TT[h_T] slope 2.000, minus G_tot slope 3.000.

P1 (run B-20261121-130454-bbbf320): row 198 CONFIRMED (the two tools' files are byte-identical;
2097152 particles, every difference 0). Row 199: the four numbers are those recorded by the
tool in id.json (7.63e-4, 2.83e-4, 3.12e-17; 3.70e-11): read, not recomputed. The jitter is
along y, z only, bounded by A h (max 0.29999974 h), uniform (rms A/sqrt3). Row 216: the batch
manifest records 0.4806 card-h (walltime 1730 s): CONFIRMED as recorded.

Predictions for round 3 (P9, refined before the M1c measurement; definitions from the batch-2b
report and the docstrings of first_source/scripts/eps2_test.py and p16_compare.py):
- P9a P12: max |c(1 ppc)/c(27 ppc) - 1| and |c(8)/c(27) - 1| for 2 <= a <= 40 reproduce 7.8e-5
  and 7.4e-5 to 20 per cent (the times of two runs differ by up to a step; I carry the reference
  by a cubic spline in tau, the track may do otherwise). Refuted above a factor 1.5.
- P9b P13: 128^3 vs 64^3 for a <= 40 at most 1.6e-4 and 1.8e-4; rms after crossing 1.30e-2
  (128,1 vs 64,8) and 3.39e-2 (64 vs 32): to 20 per cent.
- P9c (1 + eps^2): Q(delta = 0.0025) within 1.00-1.04 for a = 30-60 on both meshes, R = 17-19.
- P9d P16': D (TT power at |m| >= 16, no wave over wave) at tau = 0.1 and a = 2.3 near 0.99 and
  0.86 at 64^3, and near 0.27 at a = 12; to 3 per cent (the shell edge 15.5 or 16 may matter).

## Entry 3 (05:16 PST): prediction for my own noise prediction (rows 201-203, 206), before running it

P2 (scripts/p2_null_pred.py): static second-order strain h(K) = (20/(3K^2)) TT[dPhi dPhi](K)
from the initial potential (psi^4 = 1 - 2 Phi), wave = unjittered data, noise = difference,
growing part 3/5 of the noise, response g(tau) for every term (the track also carries the
decaying parts; I do not). Predictions: (a) the code recovers -(5/6) phi_x phi_y on analytic
crossed waves to 1e-10 relative; (b) |measured|/|predicted| at K1 and K2 for 3 <= a <= 20 has a
median in 0.85-1.2 for both jitters, extremes within 0.6-1.5 (the ledger's ranges are
0.93-1.33 and 0.73-1.01), phases within 0.4 rad; (c) rms TT of all modes over my static
all-mode estimate, 3 <= a <= 20, in 10-17 for jitter 0.3 (ledger 12-14.7). Refuted: a median
outside 0.7-1.4 or a phase error above 1 rad.

## Entry 4 (05:24 PST): prediction for row 125, before running P3

P3 (scripts/p3_slicing.py) on the 2 x 14 restart dumps of runs/cosmo/dav_c256_n128_t and
_pcs4bt: the largest correlation of d ln alpha with d ln gamma^(1/6) over 1 < a <= 121 is
<= -0.99 (ledger -0.999), and the rms ratio spans about 5e-5 to 0.04 (ledger 5.48e-5, 0.0408),
both reproduced to 5 per cent if my a (mean of chi) selects the same dumps. Refuted: a
correlation above -0.99 or a ratio off by more than 20 per cent.

## Entry 5 (05:30 PST): outcomes of M1a-d, A1, A2, P2, P3 (written before reading any review)

Runs: M1a B-20261121-130345-622e9e4, M1b B-20261121-130410-0ff2a75, M1c B-20261121-131318-6a9bad1,
M1d B-20261121-131930-79b125f (own per-dump tables, 0 errors); A1 B-20261121-131827-5d48168;
A2 B-20261121-132010-bf007b5; P2 B-20261121-131447-6f56217; P3 B-20261121-132053-5191d8e.
Figures looked at: figs/a1_rows.png, a1_floor_gauge.png, a2_round3.png, p2_null_pred.png,
p3_slicing.png.

- P1 (rows 200, 204, 205, 209-215, 207, 208) CONFIRMED: every printed digit reproduced.
- P2 (row 197) CONFIRMED: 9.53e-13 and 4.31e-13 (direct sum), 9.47e-13 and 4.79e-13 (FFT route);
  ledger 9.5e-13, 4.71e-13. The second digit is not meaningful: the diagnostic's own summation
  rounding is of the same size (T0b). Single-precision pairs: 2.4e-10 (float32 floor).
- P3 (row 198) CONFIRMED (entry 2). P4 (row 207) CONFIRMED (shells by rint(|m|); floor or 15.5
  edges change the third digit only). P5 (row 208) CONFIRMED: 0.0115, 0.00925.
- P6 CONFIRMED: R = 16.8-19.1 for a = 30-60, both ratios.
- P7 (rows 116-117) CONFIRMED to the printed digits with linear interpolation in a at a = 40
  (nearest dump: 0.0162, 0.0183, 0.0393). P8 (rows 120-123) CONFIRMED, after one fix of my own
  pairing: my first pairing by rounded times found only 38 of 217 pairs at 32^3 and gave
  0.0168 and 1.88 for the 32^3 medians (wrong); pairing by nearest time (|dt| < 1e-5; the
  32^3 runs agree to 5e-7) gives 0.0928 and 5.32, as the ledger.
- Control row 101 (verifier3 covered it): 0.00857 and 0.00821 are reproduced only over the
  double-precision (rst) dumps; over all 217 single-precision dumps the largest for eps = 1 is
  0.00882 (a = 13.0). The caption does not say which dumps.
- Rows 201-203, 206 (own growing-mode prediction, P2): medians 1.08 and 1.04 (K1), 0.944 and
  0.953 (K2) for jitter 0.3 and 0.1; extremes 0.73-1.37; phases <= 0.36 rad; rms ratio
  12.0-14.8 (jitter 0.3). Prediction (b), (c) of entry 3 CONFIRMED; (a) CONFIRMED (the code
  returns -(5/6) phi_x phi_y to 2e-16). The ledger's numbers differ from mine by <= 5 per cent
  in the ratios and <= 7 per cent in the phases, the size of the decaying-mode parts I left out.
- Row 125 (P3) CONFIRMED in digits (-0.999, 5.48e-5, 0.0408) but the smallest ratio 5.48e-5 is
  the initial slice (tau = 0, a = 1 + 6.5e-9, which "1 < a" admits by rounding); over the
  evolved dumps (a = 12-121) the ratio spans 3.8e-3 to 0.0408.
- Round 3 (P9): P12 CONFIRMED (7.76e-5, 7.44e-5; 3.35e-5 and 2.51e-4 after crossing; bin floor
  1.35e-10). P13: <= 40: 1.62e-4 and 1.86e-4 (report 1.6e-4, 1.8e-4); rms for a = 80-140:
  1.38e-2 (report 1.30e-2, 6 per cent higher; 1.64e-2 for a = 101-140) and 3.39e-2 (exact).
  (1 + eps^2): R 17.1-19.1 and Q 1.007-1.036 at 32^3, Q 1.006-1.023 at 64^3, a = 30-60; a = 20:
  Q 1.16 and 1.10, R(eps = 0.3, 32^3) 21.5: all CONFIRMED. P16': D = 0.994, 0.856 (tau = 0.1,
  a = 2.3), 0.275 (a = 12): CONFIRMED.

## Entry 6 (05:40 PST): comparison with the track's review, close

Read after commit 499bd581: stage/G1/REVIEW.md, stage/REVIEW-wave3.md, gauge lines of
stage/REVIEW-wave2.md. The review left lines 120-125, eps = 0.1/0.3 of 116-117, the second
round and round 3 unchecked (deferred to "the G2 verifier"); no number here contradicts it.
Line 101: same finding as verifier3 (0.0088 over all dumps), still owed in ledger.tex. New
here: the wording of line 125 (initial slice), the second digit of line 197, and independent
evidence for G_tot (exact pure-gauge test plus lines 116-123). Section 4 of VERIFIER-C18.md.
Not done: line 124, the residuals of line 199, line 217, wave-1 lines outside the G0 claims.
