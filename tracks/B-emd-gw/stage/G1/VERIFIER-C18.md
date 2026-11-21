# VERIFIER-C18: fresh verifier of G1 item C18 of B-emd-gw (2026-11-21)

Independent recomputation, from the raw dumps of the registered runs, of the ledger rows of the
working note (`note/tables/ledger.tex`, line numbers below) that no earlier verifier recomputed,
and of the first_source round-3 results of batch 2b. Package: `stage/G1/verifier_c18/`
(scripts, results, figures, `JOURNAL.md` with predictions written before each step). Processors
only, no card time.

Labels: [VERIFIED] measured here in the run named; [JUDGEMENT] my inference; [BACKGROUND]
standard fact; [TO VERIFY] open.

## 1. How it was done, and the limits of independence

- Read first: CLAUDE.md, the charter to "Owners", decisions 0016 and 0021, the coverage lists of
  the earlier verifiers (stage/G0/VERIFIER.md section 1, stage/G1/VERIFIER.md head, verifier3
  sections 1 and 7), the C18 line of stage/G1/CHECKLIST.md, this owner's batch reports, the
  ledger and the note's definitions. Not read before section 3 was written: stage/REVIEW-*.md,
  stage/G1/REVIEW.md, STATUS, HANDOFF, the journals.
- Own code only (`verifier_c18/scripts/vlib.py`): readers of the mesh `bin` dumps (both
  precisions) and of the z4c part of restart files (layout from `restart.cpp`), TT projection
  in Fourier space, box-mode amplitudes by a direct sum over the cell centres, the junk solution
  g(tau) in closed form (spherical Bessel functions), the second-order spatial-gauge piece G_tot
  written from the note's Eq. (9), and a second-order noise prediction. Tested on analytic
  fields first (run B-20261121-130334-a86cff6: TT of a pure gradient 0; c_+ to 4e-12; g against
  DOP853 to 1.2e-11; exact pure-gauge metric: TT h - G_tot falls as the cube of the gauge
  amplitude; single vs double dumps and rst vs bin agree to float32 rounding).
- Limit: for the definitions of the ledger quantities (which mode, which a-range, cosine part
  or modulus, which dumps) I read `note/scripts/r2data.py` and the docstring and per-dump
  definitions of `first_source/fslib/modes.py`, and the docstrings of
  `first_source/scripts/eps2_test.py` and `p16_compare.py`. A definition that is wrong in the
  track's code is therefore shared [JUDGEMENT]; I checked each against the physics where
  possible (c_+/(s g) - 1 is 0.008 at a = 12 for eps = 1, i.e. the normalization of s, g and the
  polarization is right; a(tau) = (1 + tau/2)^2 equals <chi>^(-1/2) to 3e-5).
- Runs (all registered, package `stage/G1/verifier_c18`, processors):

| Run | What |
|---|---|
| B-20261121-130334-a86cff6 | T0: tests of the own tools |
| B-20261121-130454-bbbf320 | P1: initial-data files (rows 198, 199), card-hours (216) |
| B-20261121-130345-622e9e4 | M1a: per-dump diagnostics of the second-round runs (jit0p3, jit0p1, d0025_e1, d0025_e0p3, e1_rep; 1205 dumps) |
| B-20261121-130410-0ff2a75 | M1b: the same with G_tot, wave-2 scan (64^3 eps0, 0.1, 0.3, 1, 1_gd; 32^3 eps1, 1_gd; bin and rst) |
| B-20261121-131318-6a9bad1 | M1c: box modes of the round-3 runs (64^3 1 and 27 per cell, 128^3, 32^3 companions) |
| B-20261121-131930-79b125f | M1d: the run without the wave (P16') |
| B-20261121-131827-5d48168 | A1: rows 197, 200, 204, 205, 207-215, 116-123 (101 as a control), figures |
| B-20261121-131447-6f56217 | P2: own noise prediction, rows 201-203, 206 |
| B-20261121-132010-bf007b5 | A2: round 3 (P12, P13, (1 + eps^2), P16') |
| B-20261121-132053-5191d8e | P3: row 125 (slicing of the three-wave runs) |

Figures (all looked at): `verifier_c18/figs/a1_rows.png` (departures, collapse in a delta, nulls,
two gauges), `a1_floor_gauge.png` (rerun floor, G_tot/c_+), `p2_null_pred.png`, `a2_round3.png`,
`p3_slicing.png`.

## 2. Verdicts, ledger rows (line numbers of `note/tables/ledger.tex`)

### Second round of the first source (Table VI, lines 197-217)

| Line | Ledger | Mine | Verdict |
|---|---|---|---|
| 197 rerun floor, double | 9.5e-13; 4.71e-13 | 9.53e-13; 4.31e-13 (direct sum), 9.47e-13; 4.79e-13 (FFT route) | CONFIRMED [VERIFIED]: the run repeats to ~1e-12; the second digit is at the rounding of the diagnostic itself and not meaningful |
| 198 two IC tools without jitter | 0; 2097152 | files byte-identical; 2097152 | CONFIRMED [VERIFIED] |
| 199 jittered-data residuals | 7.63e-4, 2.83e-4, 3.12e-17; 3.70e-11 | the same numbers in the tool's id.json | NOT RECOMPUTED (transcription checked only) |
| 200 largest TT mode after the first dump | 1.27e-7, 5.98e-7, 4.41e-8, 2.04e-7, 2.77e-16 | identical to the printed digits | CONFIRMED [VERIFIED] |
| 201 measured/predicted at (k,k,0), 3 <= a <= 20 | 0.927, 1.04, 1.33; 0.942, 1.03, 1.27 | own growing-mode prediction: 0.950, 1.08, 1.37; 0.948, 1.04, 1.27 | CONFIRMED in substance [VERIFIED]: an independent prediction agrees within 5 per cent (the track also carries the decaying parts of the noise; I do not) |
| 202 the same at (k,-k,0) | 0.741, 0.943, 1; 0.728, 0.951, 1.01 | 0.746, 0.944, 1.01; 0.731, 0.953, 1.02 | CONFIRMED in substance [VERIFIED] |
| 203 largest phase difference | 0.364, 0.184; 0.0812, 0.0629 | 0.361, 0.182; 0.076, 0.060 | CONFIRMED in substance [VERIFIED] |
| 204 jitter 0.3 over 0.1, 1.5 <= a <= 20 | 2.12, 2.56, 2.65 | 2.12, 2.56, 2.65 | CONFIRMED [VERIFIED] (my prediction of the ratio from the initial data alone: 2.47) |
| 205 null (0.3) over eps = 0.1 signal | 0.0148, 0.0251, 0.0314 | 0.0148, 0.0251, 0.0314 | CONFIRMED [VERIFIED] |
| 206 rms TT over second-order estimate | 12, 14.7 | 12.0, 14.8 (own static all-mode estimate) | CONFIRMED in substance [VERIFIED] |
| 207 TT power share at |k|L/2pi >= 16 | 0.984, 0.949, 0.61, 0.985, 0.952, 6.18e-12, 5.59e-5 | 0.984, 0.949, 0.610, 0.985, 0.952, 6.18e-12, 5.59e-5 | CONFIRMED [VERIFIED] (shells by rint of |m|) |
| 208 kinetic over gradient, a = 140 | 0.0115, 0.00925 | 0.0115, 0.00925 | CONFIRMED [VERIFIED] |
| 209 window 0.5 per cent | 10.3, 12.6, 33.7, 41.7 | 10.3, 12.6, 33.7, 41.7 | CONFIRMED [VERIFIED] |
| 210 window 1 per cent | 13, 17.7, 46.3, 63.3 | 13.0, 17.7, 46.3, 63.3 | CONFIRMED [VERIFIED] |
| 211 R, eps = 1 | 17.9, 16.8, 17.2, 19.1 | 17.9, 16.8, 17.2, 19.1 | CONFIRMED [VERIFIED] |
| 212 R, eps = 0.3 | 50.4, 16.8, 19.4, 18.3 | 50.4, 16.8, 19.4, 18.3 | CONFIRMED [VERIFIED] |
| 213 collapse in a delta | 1.06, 1.47, 1.07, 1.31 | 1.06, 1.47, 1.07, 1.31 | CONFIRMED [VERIFIED] |
| 214 departure at a = 140 | 0.0939, 0.0505, 1.23, 1.15 | 0.0939, 0.0505, 1.23, 1.15 | CONFIRMED [VERIFIED] |
| 215 largest departure, 2 <= a <= 10 | 3.17e-4, 3.49e-4, 9.56e-4, 2.66e-3, 4.35e-3, 2.22e-3 | the same | CONFIRMED [VERIFIED] |
| 216 card-hours of the round | 0.481 | 0.4806 in the batch manifest (1730 s) | CONFIRMED as recorded |
| 217 second reading (30 numbers, 1.96e-12) | | | NOT RECOMPUTED (bookkeeping of the note's own second reading; this report replaces it with an independent one) |

### Spatial gauge (Table IV, lines 115-125)

| Line | Ledger | Mine | Verdict |
|---|---|---|---|
| 116 |G_tot/c_+|, a <= 20, eps = 0.1, 0.3 (1) | 0.0055, 0.00596 (0.0112) | 0.00550, 0.00596 (0.0112) | CONFIRMED [VERIFIED] (own G_tot from the note's Eq. (9)) |
| 117 the same at a = 40 | 0.0163, 0.0185 (0.0397) | 0.0163, 0.0185 (0.0397) linear in a; nearest dump 0.0162, 0.0183, 0.0393 | CONFIRMED [VERIFIED] |
| 118-119 (verifier3 covered; control) | 0.00121 ... 0.115; 1.95e-5 ... 0.012 | identical | CONFIRMED |
| 120 median corrected/projected; share | 0.084, 0.0928; 0.89 | 0.0840, 0.0928; 0.894 | CONFIRMED [VERIFIED] |
| 121 quadratic piece alone | 5.24, 5.32 | 5.24, 5.32 | CONFIRMED [VERIFIED] |
| 122 departure from s g, projected/corrected, a = 10, 20 | 0.00444, 0.00687, 0.0231, 0.0345 | 0.00444, 0.00687, 0.0231, 0.0345 | CONFIRMED [VERIFIED] |
| 123 rms non-TT, zero over driven shift, a >= 10 | 16.2, 52.2 | 16.2, 52.2 | CONFIRMED [VERIFIED] |
| 124 magnetic Weyl and flat TT gauge differences | 0.00121, 0.0139 | | NOT RECOMPUTED (no own magnetic-Weyl code in this package) |
| 125 slicing of the three-wave runs | -0.999, 5.48e-5, 0.0408 | -0.9992, 5.48e-5, 0.0408 | CONFIRMED in digits [VERIFIED]; wording: the smallest ratio 5.48e-5 is the initial slice (tau = 0, a = 1 + 6.5e-9, admitted by "1 < a" only through rounding); over the evolved dumps (a = 12-121) the ratio spans 3.8e-3 to 0.0408 |

Controls outside my list: line 101 (kinetic over gradient for a >= 12: 0.00857, 0.00821) is
reproduced only over the double-precision restart dumps (22 per run); over all 217
single-precision dumps the largest for eps = 1 is 0.00882 (a = 13.0) [VERIFIED]. Line 100 (box-mode
share 0.963, 0.929, 0.843, 0.737) CONFIRMED.

## 3. Verdicts, first_source round 3 (batch-2b report, finished after the earlier verifiers)

| Claim | Report | Mine (A2, B-20261121-132010-bf007b5) | Verdict |
|---|---|---|---|
| P12, 2 <= a <= 40: 1 and 8 per cell against 27 | 7.8e-5, 7.4e-5 | 7.76e-5, 7.44e-5 | CONFIRMED [VERIFIED] |
| P12, 80 <= a <= 140: 8 vs 27; 1 vs 27 | 3.4e-5; 2.5e-4 | 3.35e-5; 2.51e-4 | CONFIRMED [VERIFIED] |
| P12(c) rerun floor (single precision) | 1.4e-10 | 1.35e-10 (2 <= a <= 40) | CONFIRMED [VERIFIED] |
| P13, a <= 40: 128^3 vs 64^3 (8 and 1 per cell) | 1.6e-4, 1.8e-4 | 1.62e-4, 1.86e-4 | CONFIRMED [VERIFIED] (the second rounds to 1.9e-4 here; the times of the 128^3 dumps differ by up to 0.011 and the interpolation decides the last digit) |
| P13, rms after crossing: 128 (1 ppc) vs 64 (8 ppc); 64 vs 32 | 1.30e-2; 3.39e-2 | 1.38e-2 (a = 80-140; 1.64e-2 for a = 101-140); 3.39e-2 | CONFIRMED in substance [VERIFIED]: the ordering and the observed order of about 1.3-1.4 hold; the first number is 6 per cent higher here (range and interpolation not fixed by the report) |
| (1 + eps^2), a = 30-60: R; Q at 32^3; Q at 64^3 | 17.1-19.1; 1.007-1.036; 1.006-1.023 | 17.1-19.1; 1.007-1.036; 1.006-1.023 | CONFIRMED [VERIFIED] |
| (1 + eps^2) fails at a = 20: Q at 32^3, 64^3; R(eps = 0.3, 32^3) | 1.16, 1.10; 21.5 | 1.16, 1.10; 21.5 | CONFIRMED [VERIFIED] |
| P16': D at tau = 0.1, a = 2.3 (64^3); at a = 12 | 0.994, 0.856; 0.27 | 0.994, 0.856; 0.275 | CONFIRMED [VERIFIED] |

Not checked from round 3: the per-shell TT/non-TT fractions and the box-mode moduli of P16'(iv),
(v); the 32^3 run without the wave; P11 and P14 at 32^3 beyond the (1 + eps^2) numbers.

## 4. Comparison with the track's own review

(Written after sections 1-3 and the journal entries 0-5 were committed; see below.)

## 5. What was not checked

- Line 124 (magnetic Weyl part across the two gauges): no own magnetic-Weyl code.
- Line 199 (constraint residuals of the jittered initial data): read from id.json, not
  recomputed; the cause of the momentum residual is the track's open item.
- Lines 201-203, 206: checked against my own prediction (growing part only), not against a
  re-implementation of the track's prediction with its decaying parts.
- Line 217 and the wave-1 rows outside the G0 claims (lines 26-27, 34-36, 49-63, 70-71): not
  recomputed in this package (the raw pancake and homogeneous-run dumps were not read).
- Population, flrw_conv, shear and waves round-1 results (F2, XS): no number of them is in the
  note's ledger yet; not checked.

## 6. Requests

- To the lead (note v3): line 125, say that the smallest rms ratio is the initial slice, or give
  the evolved range 3.8e-3 to 0.0408 (a = 12-121); line 101, say that the maximum is over the
  double-precision dumps (over all dumps it is 0.00882 for eps = 1); line 197, quote the floor
  as "~1e-12" (its second digit depends on the summation of the diagnostic).
- To the lead: C18 can be judged on this report for every line except 124, 199 (residuals
  recomputed), 217 and the wave-1 rows listed in section 5.
