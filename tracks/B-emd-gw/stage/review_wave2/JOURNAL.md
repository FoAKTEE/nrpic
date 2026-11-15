# JOURNAL of the lead's wave-2 review (B-emd-gw)

Predictions are written and committed before the review runs they concern; outcomes are
appended below, also where a prediction fails. Scripts: `scripts/`. Runs: manifests under
`tracks/B-emd-gw/runs/`, outputs under `scratch/B-emd-gw/<run id>/`. The review itself is
`../REVIEW-wave2.md`.

## 2026-11-15, before the review runs: what is recomputed and how

Independence. The helpers' conclusions were read (their reports), so this is a recheck of
the artefacts, not a blind one: the numbers are recomputed from the registered raw
outputs with code written here, sharing as little as possible with the helpers' code.

- first_source: own reader of AthenaK binary output (`scripts/athbin.py`, layout from
  `athenak/src/outputs/binary.cpp` lines 125-232, blocks placed by coordinates), the +
  amplitude at K1 = (k, k, 0) and K2 = (k, -k, 0) by direct summation of
  e+_ij h_ij cos(K.x) (e+ is TT at K, so no projector is needed), own integration of
  g'' + 2 Hc g' + |K|^2 (g - 1) = 0, own TT projector for the null. Taken from the helper:
  G_tot at K1 (the gauge-piece code of `first_source/fslib/gauge.py` is not rewritten;
  its exactness tests are the helper's T0 and `tests/test_gauge.py`), read from analysis
  runs B-20261115-180834-c77a132 and B-20261115-184650-2d155b6.
- the late rise (P7): gw_diag's restart reader (wave-1 code, reviewed then), own TT
  projector and band sums.
- newton_tests: own integration of linear growth with the H1 force factor; own reading of
  the history files for t_x, the quadrupole energy and the self-similar constants. Taken
  from the helper: the measured sheet errors of the pancakes (`pancake.json` of analysis
  run B-20261115-173904-a7297e3), because the trajectory file format is not reread here.

## Predictions R1-R9 (written before any review run)

R1 (first_source P2). My c_+(K1)/(s g) - 1 at 64^3 stays within 0.5 percent for
2 <= a <= 10 for eps = 0.1, 0.3 and 1, the K2 amplitude with the opposite sign to the
same level, and my c_+(K1) equals the helper's `h_K1_plus` to 1e-9 of |s| at every dump
(same file, different reader and arithmetic). Refuted by a larger deviation, by a deviation
that differs from the helper's (0.22, 0.22, 0.44 percent) by more than 0.05 percentage
points, or by any helper/lead mismatch above 1e-9 |s|.

R2 (P3). c_+/eps for eps = 0.3 and 0.1 agree to 0.1 percent for 2 <= a <= 10 (helper:
0.05 percent). Refuted above 0.1 percent.

R3 (null). The largest TT amplitude at any nonzero wave vector of the eps = 0 runs is
below 1e-15 at every tenth dump and at the last (64^3 and 32^3, single-precision dumps),
and the largest z-dependence of h below 1e-13. Refuted otherwise.

R4 (P6c). The raw difference of c_+(K1) between the zero-shift and Gamma-driver runs at
64^3 is 0.12, 0.36, 1.5, 4.9 and 11.5 percent of |s| at a = 5, 10, 20, 40, 60 to within
10 percent of each value; with the helper's G_tot the corrected differences are 0.002 to
1.2 percent of |s| at those a and the median corrected/raw ratio lies in 0.07-0.10 (helper:
0.084 at 64^3, 0.093 at 32^3). Refuted otherwise.

R5 (P8). c_+(K1) at 32^3 and 64^3 agree to 0.1 percent for 5 <= a <= 40 in all four
cases with eps > 0 and to 1 percent for 40 < a <= 80 in the zero-shift cases. Refuted
otherwise.

R6 (late growth). For eps = 1 at 64^3, max c_+/s is 2.5 +- 0.1 near a = 95 +- 10; c_+/s at
a = 20 and 40 is 1.0336 (1 + 0.023) and 1.014 (1 + 0.115) in the sense of the helper's
departures (+2.3 and +11.5 percent from s g). The K1 mode is quasi-static:
(dc/dtau)^2 / (|K|^2 c^2) below 0.1 for a >= 12 (my measure is one mode; the helper's
rho_kin/rho_grad <= 0.04 is over all modes). Refuted otherwise.

R6b (late rise, P7). On dumps 7 (a ~ 340) and 13 (a = 1001) of both wave-1 cosmology
runs: of the rise of the TT mean square, 0.93 +- 0.02 (quadratic cloud) and 0.97 +- 0.02
(cubic) lie at m = |k| L/2pi >= 20; the rms in m < 10 rises by 8 +- 2 and 10 +- 2 percent;
the cubic/quadratic ratio of the rms at m >= 20 at a = 1001 is 1.9 +- 0.1 and at m < 10
within 1.03 +- 0.02. My total rms of Lambda h equals the helper's (2.488e-9, 4.312e-9) to 1
percent if the conventions agree (both are sqrt of the mean over x of sum_ij (Lambda h)_ij^2
[JUDGEMENT]); if not, only the ratios are compared. Refuted otherwise.

R7 (newton_tests H1). My linear-growth prediction with F = [(kh/2)/sin(kh/2)]^2 agrees
with the helper's H1 column to 1 percent at the four values of a for n = 16, 32, 64, and
the measured/predicted ratio is within 2 percent of one at a = 2 and 5 for every n (the
helper's claim). Refuted otherwise.

R8 (N1). From the history files: t_x = 24.0659, 23.8955, 23.8604 (N = 32, 64, 128) to
1e-5 relative; E/M from the raw d3I = 3.22e-4, 4.01e-4, 4.44e-4 to 1 percent; Richardson
t_x = 23.851 +- 0.001; the step check (N = 64, step 0.01) gives t_x within 1e-6 of the
step-0.02 run. Refuted otherwise.

R9 (N3). E/(M (2 alpha)^(7/2)) from the raw d3I is the same for the four alpha at each N
to 1e-12 and equals 0.0621 (N = 32) and 0.0772 (N = 64) within 1 percent of the helper's
raw values 0.062059, 0.077205; t_x/t_turn the same to 1e-12. Refuted otherwise.

Note and verifier packages: no new runs. The note's four disagreements
(`note/tables/claims.md`) and the verifier's WRONG and NOT CONFIRMED items are checked by
reading the files they cite (outcomes in `../REVIEW-wave2.md`).

## R10 (written before the rerun of three verifier analyses)

`scripts/rv_verifier.sh` reruns the verifier's v2_crossed.py (C2), v3_junk.py (C3) and
v6_za_scaling.py (C8) on the current commit and compares their JSON leaf by leaf with the
registered outputs of runs B-20261115-165119-efd5ee7, -165123-9cb1745, -170518-c1b61a3.
Prediction: every numeric leaf agrees to 1e-12 relative (deterministic scripts, same
libraries). Refuted by a larger difference. Independent of the verifier's code: my own
g(tau) of R1 gives the junk envelope |g - 1| at a = 60 of 1.8 percent of the static value
(verifier 1.807 from the exact envelope) and (5/12)|phi_x phi_y| = 1.5399e-5 at eps = 1
(verifier, Fourier magnitude).

## Note package (no run): one sentence of the note corrected

The note (`note/main.tex` line 145) said "the resolved part at low wave numbers stays
frozen" about the late TT rise; the first-source helper corrected that reading in its own
journal (band sums, lines 195-205) and R6b rechecks it. The sentence now states the growth
below the twentieth harmonic; main.pdf recompiled (latexmk, 10 pages, no undefined
references).

## Outcomes (runs B-20261115-190007-e09a0d2 first_source, -190019-b5f5eb6 late rise, -190015-4dd3416 newton, -190323-2f8806a verifier, -190433-2d1d185 figures; figures `figs/rv_review_*.png`, looked at)

R1 CONFIRMED. max |c_+/(s g) - 1| for 2 <= a <= 10 at 64^3: 0.224, 0.222, 0.435 percent
(eps = 0.1, 0.3, 1; helper 0.22, 0.22, 0.44), K2 the same with the opposite sign; 32^3:
0.195, 0.190, 0.379. Lead and helper c_+(K1) agree to 8.6e-14 of |s| (64^3) and 6.4e-14
(32^3) at every dump. Not predicted: the Gamma-driver run departs from s g by 0.76 percent
in the same window (raw strain of another spatial gauge).
R2 CONFIRMED. c_+/eps, eps = 0.3 against 0.1: 0.050 percent (64^3), 0.066 (32^3).
R3 CONFIRMED. Largest TT amplitude of the null at every tenth dump: 1.9e-16 (64^3),
3.7e-16 (32^3); z-dependence of h 2.0e-14 and 1.4e-14; |c_+(K1)| <= 2e-16.
R4 CONFIRMED, one value off. Raw gauge difference 0.131, 0.360, 1.454, 4.82, 11.52 percent
of |s| at a = 5, 10, 20, 40, 60 (helper 0.12, 0.36, 1.5, 4.9, 11.5; a = 5 is 9 percent
higher, inside the 10 percent bound). Corrected 0.0053, 0.0076, 0.031, 0.29, 1.21 percent
(helper 0.002, 0.008, 0.03, 0.3, 1.2: a = 5 differs by 2.6, where the corrected difference
sits at the 1e-5 to 1e-4 noise of the figure and the dump chosen decides it). Median
corrected/raw 0.0840 (64^3) and 0.0928 (32^3) (helper 0.084, 0.093).
R5 PARTLY REFUTED. 5 <= a <= 40: largest |c_+(32^3)/c_+(64^3) - 1| 0.091, 0.065, 0.067,
0.065 percent (eps = 0.1, 0.3, 1, Gamma driver): below my 0.1 percent, but above the
helper's "<= 0.06 percent" for eps = 0.1. 40 < a <= 80: 0.42, 0.44 and 1.02 percent in the
zero-shift runs: eps = 1 exceeds my 1 percent bound (1.02). At a = 80 exactly: 0.42, 0.49,
0.47, 1.93 percent (helper 0.4-0.5 and 1.9); at a = 100: 0.24, 0.10, 3.2, 2.4 percent.
R6 PARTLY REFUTED. The largest c_+/s for eps = 1 is 2.547 at a = 123, not near a = 95:
c_+/s has two maxima, about 2.5 at a ~ 95 and 2.55 at a ~ 123 (the helper's "peaks at
a ~ 95, c_+/s = 2.5" names the first). Departures from s g at a = 20 and 40: 2.27 and
11.2 percent (helper 2.3, 11.5). Quasi-static: (dc/dtau)^2/(|K|^2 c^2) of K1 is 0.036 at
a = 4 and at most 0.013 for a >= 12 (helper, all modes: 0.04 and <= 0.01).
R6b CONFIRMED. Total rms of Lambda h at a = 1001: 2.4882e-9, 4.3116e-9 (helper 2.488e-9,
4.312e-9: same convention). Share of the rise at m >= 20: 0.926 and 0.972 (helper 93, 97
percent), at m >= 40: 0.551 and 0.726 (56, 73). rms at m < 10: +7.7 and +9.7 percent
(8, 10); cubic/quadratic at a = 1001: 1.944 at m >= 20, 1.030 at m < 10 (1.9, 3 percent).
Band 10-20 at a = 1001: 3.50e-10 and 4.21e-10 against the helper's 3.3e-10 and 3.9e-10
(6-8 percent: band-edge convention, not pursued).
R7 CONFIRMED. My H1 integration equals the helper's column to the printed digits at all
twelve points; measured/predicted at a = 2 and 5: 0.984, 0.982 (n = 16), 0.989, 1.019
(32), 1.000, 1.013 (64), all within 2 percent; at a = 10 and 15 it rises to 1.08-1.28
(nonlinear stage; H1 is linear).
R8 CONFIRMED. t_x = 24.065902, 23.895492, 23.860390; E/M (raw d3I, rectangle rule) =
3.2222e-4, 4.0085e-4, 4.4370e-4; Richardson t_x = 23.85128 (order 2.28), E/M = 4.950e-4
(order 0.88); step 0.01: t_x within 2.1e-7 relative, E within 2e-5. The energy is not in
its asymptotic range (distances from the extrapolated value 35, 19, 10 percent; figure),
so the +0.7 percent agreement of the extrapolation with the ODE is [JUDGEMENT] partly luck.
R9 CONFIRMED. E/(M (2 alpha)^(7/2)) = 0.0620684 (N = 32), 0.0772146 (N = 64), spread over
the four alpha 7.8e-15 and 3.4e-14; t_x/t_turn spread 2.7e-15 and 2.4e-15.
R10 CONFIRMED. v2_crossed, v3_junk and v6_za_scaling reproduce their registered JSON
exactly (407 numeric leaves, largest relative difference 0). Independent: (5/12)|phi_x phi_y|
= 1.5399e-5 at eps = 1 from my s; my g(tau) gives max |g - 1| = 1.93 percent over the
period centred on a = 60 (tau = 12.1 to 14.9, i.e. a = 50 to 70), consistent with the
verifier's exact envelope 1.807 percent at a = 60 and a 1/a decay.
