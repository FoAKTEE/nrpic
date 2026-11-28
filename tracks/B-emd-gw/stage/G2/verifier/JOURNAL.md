# Journal of the fresh verifier of gate G2, Track B (batch 35, 2026-11-27)

Fresh context (decision 0016 item 4, 0046 item 2, 0048 item 3; checklist C18). Claims taken
from: the end of `stage/G2/OPEN.md` ("what to recompute first"; the file is 49 lines and I
read it whole, so its top paragraph, which carries the lead's states, was read too: noted
here as a limit of the freshness), `stage/G2/REPRODUCE.md`, note section VI and Tables VII
and VIII of `note/tables/ledger.tex`, Table V (waves), `scope/SCOPE.md` sections 4-7, the
track sheet (charter 9.5). Not read before VERIFIER.md is written: the outcome entries of the
journals, `stage/REVIEW-wave3.md`, the verdict column of `stage/G2/CHECKLIST.md` (item texts
only, extracted with a filter), `STAGE_REPORT.md`, `VERIFY_RESULTS.md`.

Definitions taken from the lead's scripts (only what a quantity IS, so that my number is the
same quantity; no code of theirs is imported or run): band rms of `compare_legs.py`
(`band_rms2`: sum over integer shells n = 1..8 of spec[n]/n^2, spec = per-shell
k^2-weighted TT power, shells nk = rint(|k|/k_f)); halos of `analyze.py` (friends-of-friends,
b = 0.2 of the mean spacing, at least NMIN particles; common limit 100 m_N with
m_N = rho_c L^3/64^3); a = (1 + t/2)^2; particle snapshot format of `docs/FORMATS.md`;
mesh dump format of `athenak/src/outputs/binary.cpp`.

## Entry 1 (18:05 PST): predictions, written before any recomputation

Readers first (V0): my mesh-dump reader, particle reader, TT projector and FoF are tested on
analytic cases before any claim is touched. Prediction V0: the TT projector returns a random
TT field to rounding (< 1e-12 relative) and removes a pure-gauge field d_i xi_j + d_j xi_i to
rounding; FoF recovers the membership of synthetic, well-separated Plummer clumps exactly.
Refuted if any of these fails.

V1 (waves; my exact solutions: the forward combination W = h + i h'/|k| of the t = 0 dump
carried by e^{-i|k|t} for the flat wave F; for the standing mode X of the matter era the
combination of j1(x)/x and y1(x)/x, x = k (t + 2), fitted to h = 0 and h' of the t = 0 dump).
Claims (ledger Table V): F amplitude error -1.41e-4, -1.72e-6, -3.1e-8 and phase error
2.53e-4, 1.22e-5, 7.07e-7 at N = 16, 32, 64, t = 4/sqrt 3; X cross polarization amplitude
-7.05e-5, 1.32e-6, 1.4e-7 and phase 8.3e-5, 3.06e-6, 2.76e-7 at N = 16, 32, 64, t = 10.
Prediction: I reproduce |error| to within 5 per cent at N = 16 and 32 and within 15 per cent
at N = 64 (my exact solution starts from the dump, theirs from the closed form; my TT
projection is spectral). The sign of the phase may differ by convention (stated, not counted).
Refuted if a magnitude differs by more than these bounds.

V2 (population, GM2): band rms |k| <= 8 k_f of the TT metric strain, 256^3 over 128^3, Gamma
driver. Claim: within 1.1 per cent to a = 64 and 2.8 per cent to a = 132 (corrected strain).
Prediction: (a) from the two analysis files with my own band sum I get the same largest
deviations to two digits; (b) my raw recomputation from the dumps (own reader, own TT) at
t = 4, 8, 14, 21 gives the files' raw band rms to 1e-3 relative on each mesh; (c) the gauge
piece in the shifted gauge is below 1 per cent of the band rms, so raw and corrected ratios
agree to 0.3 per cent; (d) the 128^3 dumps lie 0.0082 later in t than the 256^3 dumps; a
time interpolation of the 128^3 raw band rms to the 256^3 times changes the ratio by less
than 0.5 per cent. Refuted if (a) differs in the second digit, (b) by more than 1e-3, (c) or
(d) exceed their bounds.

V3 (population, high-k): TT measure above 16 k_f, zero shift over Gamma driver, 128^3,
a = 121: claim 946. Prediction: my raw recomputation from the two dumps gives the same ratio
within 10 per cent (raw against corrected differ in the zero-shift run by the gauge piece,
whose size the file records; I report both). Refuted if my raw ratio is below 500 or above 2000.

V4 (halos, equal masses): claim at a = 121, counts of FoF halos with at least 100 particles
108 (zero shift), 98 (Gamma driver), 106 (Newtonian mode); 256^3 against 128^3 Gamma driver:
counts above the common limit below the 128^3 counts at every epoch (0.484 to 1), largest
mass ratio 0.987 to 1.32, 1.32 and 1.13 at a = 64, 121. Prediction: my FoF on the same
snapshots gives counts within +-2 of each claimed count and the largest masses within
0.5 per cent (a different union order cannot change FoF groups; only the snapshot time and
the mass convention can). Refuted if a count differs by more than 2 or a largest mass by more
than 1 per cent. If 256^3 FoF does not fit in memory or time, it is stated as not checked.

V5 (constraints, C3): claims: 64^3 over 128^3 at eight particles per cell, zero shift,
Hr_mean 1.32 to 2.34 over 25 <= a <= 141, at least 1.64 for a >= 49; Mr_mean 1.71 to 2.16
for a >= 49; one particle per cell 128^3 over 256^3 Hr_mean 1.05 to 1.37 (Table VIII) or
1.11 to 1.36 (Table VII, both gauges); particle leg at a = 141 (128^3, 1 over 8 per cell):
Mr 2.93, Hr 1.58; continuation repeats the cut run to 4.2e-12. Prediction: my own
interpolation (log-linear in t onto a common grid; the lead's method is unknown to me) gives
each extreme within 3 per cent, the continuation difference below 1e-11. Refuted if an
extreme differs by more than 5 per cent, or the 8-per-cell pair falls below 1.2 for
a >= 49 in my reading.

V6 (stop at 256^3, zero shift): claims: largest K turns positive at a = 79.9, last record
before the non-finite stop a = 101, largest K there 0.0224. Prediction: from pop.cstat.hst
and the guard file I get these to three digits. Refuted otherwise.

V7 (shearing dust, series 7, beta = 0.125, HL = 4): claims Delta = 0.053749, 0.053800,
0.053821 at N_y = 64, 128, 256; ratio of differences 0.401 (order 1.3); finest minus
Richardson -1.38e-5; t_A = 4.12; no stream crossing before t_A, smallest neighbour spacing
0.699 of the lattice spacing; first crossing at t = 9.25, 9.25, 9. Also my own evaluation of
the closed-form cos(theta_lin) (SPEC section 4) against the files' cos_lin. Prediction: Delta
and Richardson reproduce from the rays.json values to all printed digits (arithmetic); my
crossing check from the particle snapshots finds no crossing up to t_A on all three meshes,
a smallest spacing within 0.02 of 0.699, and a first crossing snapshot within one snapshot
interval (0.25) of the claim; my closed form gives cos_lin to 1e-8 relative. Refuted if a
crossing appears before t_A, or cos_lin differs by more than 1e-6.
V7b (L2 as run, beta = 0.5, HL = 4, 4 per cell): Delta at N_y = 64, 128, 256 moves away from
CosmoGRaPH's -0.8183 with each refinement (claim). Prediction: |Delta + 0.8183| grows
monotonically with N_y; and the streams of L2 cross before t_A (the note says so), which my
crossing check must find. Refuted if the distance shrinks, or no crossing before t_A.

V8 (what G2 can claim): judged after V1-V7 against the scope text and decisions 0013, 0046,
0048, written into VERIFIER.md before reading the lead's verdicts.

## Entry 2 (18:25 PST): prediction for one more check, before it runs

V7c (series 7 constraint floor, Table VIII rows 278): claims, mean relative Hamiltonian
constraint over 1 <= t <= t_A at N_y = 64, 128, 256: 3.62e-6, 2.73e-6, 2.55e-6; momentum
2.33e-4, 1.66e-4, 1.64e-4 (OPEN: Mr 1.6e-4 not falling between 128 and 256). Prediction: a
time average of the cstat columns Hr_mean and Mr_mean (trapezoid in t, my choice; the lead's
averaging is unknown to me) gives these to two digits; refuted if any differs by more than
5 per cent. If they reproduce, the 128-to-256 step lowers Mr by less than 2 per cent.

## Entry 3 (18:30 PST): outcomes, prediction by prediction

V0 (B-20261128-021054-577fc9d): PASS on every test. Failed as written in an unregistered dry
run before it (scratch/B-emd-gw/tmp/v0dry): the projector's round trip through a real field
failed at 1.6 relative because the Nyquist planes of a real field cannot carry a
direction-dependent projection with Hermitian symmetry; every measure of mine excludes the
Nyquist planes since (as the lead's measures do), and the test zeroes them in its inputs.
Recorded as a failed prediction of the dry run, corrected before any claim was touched.

V1 (B-20261128-021125-515c0cc): holds, better than predicted. F amplitude -1.4092e-4,
-1.7174e-6, -1.5742e-7, -3.1218e-8; phase 2.5310e-4, 1.2176e-5, 2.2728e-6, 7.0694e-7 (N = 16,
32, 48, 64): every claimed digit reproduced. X cross amplitude -7.0481e-5, 1.3169e-6,
4.2498e-7, 1.3989e-7; phase 8.3039e-5, 3.0650e-6, 5.8797e-7, 2.7624e-7: every claimed digit.
X plus polarization against cross: amplitude +2.6 and +10.0 per cent, phase +10.2 and +39.1
per cent at N = 48, 64 (claim: 0.0263, 0.0997, 0.102, 0.391 against the prediction, which
equals the cross error): reproduced. Sign convention of the phase the same as the claims'.

V2 (files part in all three attempts; raw part in B-20261128-021923-351e31f; attempts
B-20261128-021349-a57f21e and B-20261128-021412-072e411 FAILED on bugs of mine, an int32
overflow in the reader and an exact-time match, both after the files part had printed):
(a) holds: largest |256^3/128^3 - 1| of the corrected band 0.010897 (a <= 64) and 0.027699
(a <= 132.25) against claimed 0.0109, 0.0277. (b) holds, far inside the bound: my raw rms and
band from the dumps equal the files' to 1e-15 relative at all 14 dumps read. (c) holds: the
gauge piece is 0.03 to 1.07 per cent of the rms in the shifted gauge, raw and corrected
band ratios agree within 0.02 per cent. (d) holds: the 128^3 dumps lie 0.0082 later in t;
interpolating them to the 256^3 times moves the deviation to 0.0115 (a <= 64) and 0.0271
(a <= 132.25). Extra: with an exact per-mode band (no n^-2 shell weighting) the ratio at
a = 64 is 1.0119 and at a = 132.25 0.9983 (files form 1.0023): the 1.1 per cent is
reproduced within 0.1 percentage point; the a = 121 maximum was not recomputed in the exact
form.

V3 (B-20261128-021923-351e31f, B-20261128-022328-1a9d681): the claimed 946 is reproduced
from the files' corrected spectra (945.56 at a = 121.1). My raw recomputation with all
modes off the Nyquist planes gives 1700, the files' raw 1864: prediction "within 10 per
cent" FAILED as written for the raw form, cause found in a run that could have failed: the
files' spectrum stops at shell 64 (n/2), so the cube's corner modes (|n| > 64.5) drop out;
with that cut my raw ratio is 1864.09, equal to the files' to 1e-15. In the Gamma-driver
run 9.0 per cent of the measure above 16 k_f lies in the corners, in the zero-shift run
0.17 per cent. The "about 950 times" depends on that cut by about 10 per cent; no
conclusion changes (ratio 1700 to 1864 raw).

V4 (B-20261128-021413-6b4d7a1): holds. Counts of >= 100 particles at a = 121: 108 (zero
shift), 98 (Gamma driver), 106 (Newtonian mode): exact. Median |M_GR/M_N - 1| of the ten
largest: 0.0264 (zero shift, claim 0.0264), 0.0124 (Gamma driver, claim 0.0123: last digit).
Largest halo at a = 121: 0.909 (zero shift) and 1.029 (Gamma driver) of the Newtonian one,
inside the claimed ranges. 256^3 against 128^3 (Gamma driver): counts above the common limit
8/11 = 0.727 and 15/31 = 0.484 at a = 64, 121; largest mass ratio 1.3235 and 1.1279 (claims
0.484, 1.32, 1.13): exact; my 256^3 catalogues equal the lead's file (242, 8, 1.038 and 431,
15, 1.905). |15 - 31| = 16 exceeds 2 sqrt(31) + 2 = 13.1: outside the counting band at a = 121.

V5 (B-20261128-021335-a7a2a49, -021515-a6306af, -022330-6e6076d): holds for the 8-per-cell
pair: Hr 64/128 1.324 to 2.340 over 25 <= a <= 141, at least 1.638 for a >= 36 and a >= 49;
Mr 1.715 to 2.159 for a >= 49 (claims 1.32, 2.34, 1.64; 1.71, 2.16). Pairing sensitivity
(interpolation either way, nearest records): extremes within 0.1 for Hr, the minimum for
a >= 49 1.62 to 1.64. One-per-cell pairs: Gamma driver 1.105 to 1.36 with nearest records
(claim 1.11, 1.36: exact), 1.106 to 1.38 interpolated; zero shift 1.047 to 1.405 over
25 <= a <= 100 (claim Table VIII 1.05, 1.37; the note's "1.05 to 1.4"), 1.13 to 1.40 over
36 <= a <= 100 (claim Table VII 1.11, 1.36): the zero-shift maximum is 1.39 to 1.41 in all
three of my pairings, 2 to 3 per cent above both claimed maxima; the minimum of Table VII
(1.11) I do not find in that window (1.13 to 1.17). Not reproduced to the claimed digits;
no conclusion changes. Particle leg at the last records (a = 140.74 in both runs): Hr 1.575,
Mr 2.932 (claims 1.58, 2.93); continuation against the cut run 4.23e-12 (claim 4.23e-12).
Wording: the note says the 8-per-cell momentum ratio is 1.7 to 2.2 "from a ~ 36 on"; from
a = 36 it reaches down to 1.45, from a = 49 it is 1.71 to 2.16 (Table VIII says a >= 49).

V6 (same runs): holds. First record with K_max > 0 at a = 79.88 (linear zero crossing
79.36); last finite record a = 101.25, K_max 0.02244 there (claims 79.9, 101, 0.0224); guard
stop at t = 18.21. K_max does not stay positive after a = 79.9 (it returns below zero in
some records before the stop). Gamma driver after t = 9: largest K -0.000844 (256^3),
-0.00141 (128^3); last a of the 256^3 run 142.5 (claims -0.000844, -0.00141, 143).

V7 (B-20261128-021337-d0c2105): holds. Delta 0.0537486, 0.0538000, 0.0538206; Delta =
cos/cos_lin - 1 from the stored cos to all digits; d2/d1 = 0.4007, order 1.32, Richardson
0.0538344, finest minus Richardson -1.379e-5 (claims 0.401, -1.38e-5). My closed form gives
cos_lin = 0.1259217103254327 (b = beta (HL)^2 = 2) equal to the files' to all digits
(second quadrature 4e-14). Crossing: smallest spacing up to t_A 0.6992, 0.6993, 0.6993 of the
lattice spacing; first crossing in the snapshots at t = 9.25, 9.25, 9.00 (claims 0.699,
9.25, 9.25, 9): no stream crosses before the rays arrive (t_A = 4.118). V7b holds for the
Delta series: L2 at four per cell, N_y = 64, 128, 256: -0.82180, -0.83123, -0.83915, distance
to -0.8183 0.0035, 0.0129, 0.0208, growing; differences ratio 0.84 (no convergence). The
crossing part of V7b is NOT CHECKABLE: the L2 runs wrote only the t = 0 particle snapshot.
V7c (B-20261128-022420-5d1f804): holds: plain record means 3.62e-6, 2.73e-6, 2.55e-6 (Hr),
2.33e-4, 1.66e-4, 1.64e-4 (Mr) equal the claims; Mr falls 1.5 per cent from 128 to 256.

Side result: the lead's detached --full stage verify (PID 2643528) ended at 18:21 PST:
PASS, 0 failed checks, 13883 output files hashed again (1166.91 GB read); it left
stage/G2/VERIFY_RESULTS.{md,json} modified in the worktree (the lead's files; not touched).
