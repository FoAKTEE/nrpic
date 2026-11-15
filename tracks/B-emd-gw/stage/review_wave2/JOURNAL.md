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
