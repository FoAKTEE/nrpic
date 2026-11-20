# junk_gauge: journal (F-hills, wave 3, round 1)

Helper package of F-hills: close S2g and judge E10 (nr_first), measure the junk radiation of
one member (S2g) and of the three-hole data (P1's spheres) for G1 T3, gauge recommendation.
Predictions are written before each measurement, outcomes after, failed ones included.
Labels [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-20 J0. Start of the session (14:15 PST)

State checked against the planner's reading [VERIFIED]:
- S2g, run F-20261119-143443-f11ebb9 (Slurm 4640): `S2g/athena.log` ends "Terminating on time
  limit", time = 90, cycle 2880, 1576 MeshBlocks at the end (1372 created, 196 deleted), exit 0
  at 2026-11-19T08:55:30-08:00, card memory peak 54025 MiB, 1877 s of cpu time on one card.
  Closed with `nrpic-run finish` at 14:22 PST: completed, 42 files checksummed (commit
  b02dc5c6, written by nrpic-run).
- S3 and S2: `scratch/F-hills/F-20261115-173601-2fae2dc/{S3,S2}`.
- P1, run F-20261119-150017-b45ec5f: waveforms `rpsi4_{real,imag}_00{40,48,70,90}.txt` end at
  t = 112.25 M (last row, all four spheres); the chain's last segment (seg 7, job 4684) ended
  with exit status 143 at 19:35 on 2026-11-19 (`chain/` log); another package resumes it.
  Header of the waveform files: column 1 time, then (l, m) for l = 2..8, m = -l..l
  (`athenak/src/z4c/z4c_wave_extr.cpp` lines 155-163).

## 2026-11-20 J1. Method for the junk of a single member, written before it is computed

Data: S2g only (S3 and S2 stopped at t = 22 m and 14 m, before any pulse reached 30 m, nr_first
E3). m = 1, P = 0.25 along +x, puncture at the origin, spheres R = 30, 40, 50 m, r psi4 modes
l = 2..8 every 0.25 m to t = 90 m. Domain +-256 m (outer boundary reflections cannot return
before t = 2 x 256 - 50 = 462); cells 1 m inside the level-3 cube [-64, 64]^3 m and 2 m in the
level-2 shell outside it (nr_first E11): the only interface the junk crosses before t = 90 is at
64 m, a refinement boundary, not an outer boundary.

Energy and momentum [BACKGROUND, Ruiz et al. arXiv:0707.4654, `gwaves.tex` lines 585-587 and
600-603]: dE/dt = (1/16 pi) oint |N|^2 dOmega, dP_i/dt = (1/16 pi) oint l_i |N|^2 dOmega, with
the news N(t, theta, phi) = int r psi4 dt = sum_lm N_lm(t) -2Y_lm. Energy from the mode sum;
momentum by quadrature on the sphere (N rebuilt from its modes with a port of AthenaK's own
-2Y_lm, `z4c_wave_extr.cpp` lines 45-59), so that no convention of the harmonics can enter; the
closed coupling formula of Ruiz et al. (lines 634-657) is computed beside it as a check of the
port (they agree only if AthenaK's harmonics have the convention of that paper).

Retarded time u = t - R*, R* = R_a + 2 M ln(R_a / 2M - 1), R_a = R (1 + M / 2R)^2 the areal
radius of the coordinate sphere and M = M_ADM = 1.038 (full solution, nr_first E3 reference)
[JUDGEMENT: the sphere radius is a coordinate radius of puncture coordinates, close to isotropic
far away].

Junk window: u in [-15, +30] m. Why: the data relax within a few m of the puncture, so an
outgoing pulse leaves r < 10 m by t = 10 and crosses R at u >= -15 m; the l = 2 quasinormal
mode of the hole (omega = 0.374/m, damping time 11.2 m: [BACKGROUND, Schwarzschild l = 2
fundamental mode], locator [TO VERIFY]) has lost 93 percent of its amplitude, 99.5 percent of its
energy, 30 m after it starts. The window ends at u = 30 because the record of the 50 m sphere
ends at u = 90 - R*(50) = 33.6 m. The gauge pulse of the 1+log lapse (speed about sqrt 2)
reaches R at u = R / sqrt 2 - R*, i.e. -14 (R = 30), -20 (40), -21 (50); psi4 changes under a
change of tetrad only at second order in the gauge perturbation times psi2, so it is left in
[JUDGEMENT].

Integration, two methods, both in the window:
- A (central): fixed-frequency integration [BACKGROUND, Reisswig and Pollney arXiv:1006.1632,
  `paper.tex` lines 914-928]: N~(omega) = -i psi4~(omega) / max(|omega|, omega_0) sign(omega),
  over the whole record t in [0, t_end] after a cosine taper of 4 m at both ends; omega_0 = 0.2/m
  (half the l = 2 quasinormal frequency; the hole's coordinate motion, x = 12-17 m in 90 m,
  and the near-zone part of an off-centre hole vary on 30 m and longer). Variants omega_0 = 0.1
  and 0.3 are reported as the systematic of the choice.
- B (time domain, as nr_first E10's `single_analysis.py`): a quadratic in t fitted to each mode
  outside the window is subtracted, the news integrated from the window's start.
Then E_junk = int over the window of dE/du; the same for P.

Junk against numerical noise: (i) the same pipeline gives a noise energy on the parts of the
record outside the window (before: u < -15 m, after: u > 30 m), scaled to the window's length
(45 m) as a rate; the junk is "measured" only where it exceeds ten times this; (ii) outgoing
radiation arrives at a fixed retarded time and has r psi4 independent of R, near-zone signal and
noise do not: the peak of |N|^2 must lie at the same u within 3 m at the three radii, and the
peak of |r psi4_20| must agree within 20 percent; (iii) the energy at the three radii is fitted
with E(R) = E_inf + a / R [JUDGEMENT: the first correction of a quantity measured at finite
radius].

Predictions [JUDGEMENT]:
1. E_junk/m (method A, omega_0 = 0.2) at each radius between 2e-5 and 2e-4 (core's scaling
   1.3e-2 (P/m)^4 m gives 5.1e-5 for P/m = 0.25: three_punctures JOURNAL line 295, "good to a
   factor two at best"); E10 item 3's wider band 1e-5 to 5e-4 is judged separately with E10's
   own script.
2. The three radii within 25 percent of each other (E10 item 3's criterion); |a| / R below 0.25
   E_inf at R = 30; E_inf inside the band of item 1.
3. Methods A and B within 25 percent at each radius; omega_0 = 0.1 and 0.3 within 25 percent of
   0.2.
4. The noise energy (rate outside the window times 45 m) below 0.1 E_junk at R = 30 and 40
   (R = 50 has 2.8 m of record after the window, so only the part before it).
5. Peak of |N|^2 at the same u within 3 m at the three radii; dominant modes (2,0) and (2,+-2)
   (the junk of a hole boosted along x is axisymmetric about x, which in harmonics about z is a
   mix of m = 0 and m = +-2 at l = 2).
6. Momentum: P_y, P_z below 1e-3 |P_x| (mirror symmetry y -> -y, z -> -z of the data);
   |P_x| < E_junk (|dP/dt| <= dE/dt holds pointwise for null radiation); the closed coupling
   formula equals the quadrature to 1e-6 if AthenaK's harmonics have Ruiz et al.'s convention.
Refuted (item by item) outside these ranges. A test of the pipeline on synthetic modes with a
known energy comes first (J2).

## 2026-11-20 E10 analyses run (registered; criteria of nr_first E10 unchanged)

Runs F-20261120-222403-b8dc28c (`s2g_compare.py` with S3, S2, S2g) and F-20261120-222415-137ada9
(`single_analysis.py` with S3, S2, S2g), both with --parent F-20261119-143443-f11ebb9. The
judgement is appended to `nr_first/JOURNAL.md` ("E10, outcome") after all figures are read.

## 2026-11-20 J2. Tests of the pipeline on synthetic modes (prediction)

`scripts/junk_lib.py` (FFI, time-domain integration, -2Y_lm port, sphere quadrature, coupling
formula), tested by `scripts/test_junk_lib.py` (no AthenaK data; what it builds is in its
docstring: a Gaussian-modulated pulse with omega = 0.4 in (2,0), (2,+-2), (3,0), a slow offset
of -6e-4 switched on after the pulse in (2,0), white noise 1e-6; window [30, 75]).
Predictions:
1. Orthonormality of the -2Y_lm port on the 40 x 80 grid: largest error below 1e-12.
2. Window energy: FFI with omega_0 = 0.2 within 5 percent of the exact value with the offset and
   noise, within 1 percent without them; omega_0 = 0.1 above it by more (the offset leaks more),
   omega_0 = 0.3 within 10 percent (it starts to cut the pulse, whose spectrum has width
   1/sigma = 0.17 about 0.4); the time-domain method within 10 percent.
3. Momentum: the quadrature's dE/dt equals the mode sum to 1e-12; |dP/dt| <= dE/dt everywhere;
   a real (2,0) + (3,0) pair gives dP_x = dP_y = 0 to round-off and dP_z != 0; quadrature and
   coupling formula: P_z equal to 1e-10 in any case; P_x, P_y equal to 1e-10 if AthenaK's
   harmonics have the convention of Ruiz et al., opposite in sign if they differ by (-1)^m
   (I expect equal [JUDGEMENT]: AthenaK cites arXiv:0709.0093, the NR data-format convention).
Refuted outside these.

## 2026-11-20 J2, outcome (run F-20261120-222655-4d3bbc2; `test_junk_lib.json`, figure `fig_test_junk_lib.png` read)

[VERIFIED, `test_junk_lib.json` of the run]
1. Orthonormality error 2.8e-14: met.
2. Window energy against the exact 2.80e-5: FFI omega_0 = 0.2 1.035 (met, within 5 percent);
   without offset and noise 0.981: FAILED (predicted within 1 percent; the pulse's spectrum,
   width 0.17 about 0.4, has 2 percent of its energy below omega_0 = 0.2, which FFI damps);
   omega_0 = 0.1 1.243 (met: the offset leaks more, and the figure shows a slope before the
   pulse); omega_0 = 0.3 0.948 (met, within 10 percent); time domain 1.130: FAILED (predicted
   within 10 percent; in the figure the excess is gathered after the pulse, where the offset
   that a quadratic outside the window cannot follow is integrated).
3. dE/dt of the quadrature equals the mode sum to 2.2e-15; largest |dP/dt| / (dE/dt) 0.14;
   the real (2,0) + (3,0) pair gives dP_x = dP_y = -5e-19 and dP_z = 7.519e-3 (coupling
   formula 7.519e-3); quadrature and coupling formula agree to 4e-14 in all three components
   (and differ by order one with the opposite sign): AthenaK's -2Y_lm have the convention of
   Ruiz et al. Met.
Consequence for J1 (no criterion changed): on a pulse with this spectrum the central method
(omega_0 = 0.2) has an error of order 2-4 percent and the time-domain method of order 10-15
percent where a slow offset follows the pulse; the spread of the omega_0 variants (-5 to +24
percent here) is the systematic of the choice, as planned.

## 2026-11-20 J3, outcome: junk of one member at finite radius (run F-20261120-222808-b65001c; `single_junk.json`, figures `fig_single_waves.png`, `fig_single_energy.png` read)

Numbers [VERIFIED, `single_junk.json` of the run; E in units of m, window u in [-15, 30]]:

| R | E FFI 0.1 | E FFI 0.2 | E FFI 0.3 | E time domain | noise (0.2) before / after | P_x (0.2) |
|---|---|---|---|---|---|---|
| 30 | 2.73e-4 | 1.25e-4 | 7.68e-5 | 2.88e-4 | 5.3e-5 / 5.9e-5 | 3.94e-5 |
| 40 | 1.15e-4 | 8.65e-5 | 5.92e-5 | 2.20e-4 | 1.5e-5 / 1.3e-5 | 1.37e-5 |
| 50 | 1.09e-4 | 8.52e-5 | 5.81e-5 | 2.18e-4 | 6.7e-6 / (none) | 1.24e-5 |

Fits E_inf + a/R over the three radii: FFI 0.2 E_inf = 1.7e-5 (a = 3.1e-3), 0.3 2.6e-5, 0.1
-1.7e-4, time domain 9.7e-5.
Against J1:
1. E_junk/m (FFI 0.2) between 2e-5 and 2e-4 at each radius: met (1.25e-4, 8.65e-5, 8.52e-5).
2. Three radii within 25 percent: FAILED (max/min 1.46; R = 30 is 46 percent above R = 50; 40
   and 50 agree within 1.5 percent). |a|/R below 0.25 E_inf at R = 30: FAILED (1.0e-4 against
   1.7e-5). E_inf in the band: FAILED (1.7e-5, below 2e-5).
3. Methods within 25 percent: FAILED. Time domain / FFI 0.2 = 2.3-2.6 at every radius; omega_0
   = 0.1 +33 and +28 percent at 40, 50 (+119 at 30); omega_0 = 0.3 -32 percent at 40 and 50.
4. Noise below 0.1 E_junk at R = 30 and 40: FAILED (0.42-0.47 at 30, 0.15-0.17 at 40); at
   R = 50 the part before the window is 0.078.
5. Arrival at fixed retarded time: met (peak of dE/du at u = 1.48, 1.37, 1.14 m); peak of
   |r psi4_20| 3.04e-3, 2.78e-3, 2.95e-3 (within 9 percent): met. Dominant modes: met; at R = 50
   (2,+-2) 0.705 and (2,0) 0.236 of the energy, l = 3 0.05, l >= 4 0.01. The ratio 3.0 of
   (2,+-2) to (2,0) is that of a pattern axisymmetric about x: |d^2_{20}(pi/2)|^2 = 3/8 per m =
   +-2 against |d^2_{00}(pi/2)|^2 = 1/4 [BACKGROUND, Wigner d-matrix].
6. Momentum: met. P_y / P_x and P_z / P_x at most 8.5e-4 (R = 50), 4.7e-4 (40), 8e-4 (30);
   largest |dP/du| / (dE/du) in the window 0.56-0.70; P_x > 0 (radiated along the boost: the hole
   recoils toward -x).
What the figures show: the pulse in r psi4 (u from -10 to +10 m) is the same at the three radii
(outgoing radiation); after u = 10 m every mode moves to a slowly varying offset that is larger
the smaller the sphere ((2,0) at u = 20: -1.3e-3, -0.9e-3, -0.8e-3 at 30, 40, 50; (2,2) rises to
1.5e-3 at R = 30). The "noise" rate outside the window falls as R^-4.4 (30 to 40) and R^-3.6 (40 to
50), as the square of a news that falls as 1/R^2: the near-zone field of the hole, which has moved
off the spheres' centre (x = 16 m at t = 90, nr_first E10), not numerical noise [JUDGEMENT]. It
enters the window energy through the slow content (omega_0 dependence) and through the cross term
with the pulse; the time-domain method's quadratic cannot follow an offset that switches on after
the pulse (as in J2, but here the offset is several times larger relative to the pulse).
Reading [JUDGEMENT]: the finite-radius numbers bound the junk only as 6e-5 to 1.3e-4 m (FFI 0.3 at
50 m to FFI 0.2 at 30 m, excluding the time domain). A better separation follows (J3b).

## 2026-11-20 J3b. Junk at infinity from the waveform extrapolated in 1/R before integration (prediction; added after J3, method not in J1)

Why: J3 shows a pulse that is independent of R and a slow offset that is not; r psi4 extrapolated
at fixed u as A(u) + B(u)/R removes a part of r psi4 that falls as 1/R [BACKGROUND: polynomial
extrapolation in 1/R at fixed retarded time is the usual finite-radius extrapolation of NR
waveforms; locator TO VERIFY]. What: each mode of S2g at R = 30, 40, 50 interpolated (cubic
spline) onto one u grid (step 0.25 m, the common u range [-36.5, 32.1] m), least-squares fit
A + B/R per u (order 2, A + B/R + C/R^2, as the variant), then the J1 pipeline on A (FFI with
omega_0 = 0.1, 0.2, 0.3, taper 4 m; time domain) in the same window u in [-15, 30].
Predictions [JUDGEMENT, written after seeing the finite-radius numbers of J3]:
1. A(u) of (2,0) and (2,2) after the pulse (u in [15, 30]) below 20 percent of the pulse's peak
   (the offset is mostly B/R).
2. The four methods within 25 percent of each other on A (the slow content that made them
   differ is removed); omega_0 = 0.1 and 0.3 within 15 percent of 0.2.
3. E_inf (FFI 0.2, order 1) between 6e-5 and 1.0e-4 m (the noise-corrected finite-radius values
   would be 7.2e-5, 7.2e-5, 7.9e-5 at 30, 40, 50, a post-hoc reading of J3); order 2 within 25
   percent of order 1.
4. P_x at infinity between 0.10 and 0.20 E_inf (J3 at 40 and 50: 0.15-0.16), P_y and P_z below
   1e-3 of P_x.
Refuted outside these; if 2 fails, the junk energy of a member is quoted as the range of J3.
