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
