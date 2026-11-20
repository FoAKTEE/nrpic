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

## 2026-11-20 J3b, outcome (run F-20261120-223018-a5c0838; `S2g_extrap.json`, `S2g_o2_extrap.json`, figures `fig_S2g_extrap.png`, `fig_S2g_o2_extrap.png` read)

[VERIFIED, the JSON files of the run; window u in [-15, 30], common u range [-36.5, 32.0]]
Extrapolated (order 1 / order 2): FFI 0.1 2.21e-4 / 1.20e-4; FFI 0.2 1.14e-4 / 8.77e-5; FFI 0.3
7.17e-5 / 5.90e-5; time domain 2.85e-4 / 2.72e-4. The finite radii on the same u grid (FFI 0.2):
9.83e-5 (30; J3 had 1.25e-4 on the full record, the difference is the shorter record's taper
and leakage), 8.71e-5 (40), 8.52e-5 (50).
1. A after the pulse below 20 percent of its peak: FAILED (order 1: 0.25, 0.23, 0.23 for (2,0),
   (2,2), (2,-2); order 2: 0.20, 0.19, 0.19).
2. Methods within 25 percent: FAILED (max/min 4.0 and 4.6); omega_0 = 0.1 and 0.3 within 15
   percent of 0.2: FAILED (+94 / -37 percent, order 1).
3. E_inf (FFI 0.2, order 1) in 6e-5 to 1.0e-4: FAILED (1.14e-4); order 2 within 25 percent of
   order 1: met (-23 percent).
4. P_x / E_inf in 0.10-0.20: FAILED for order 1 (0.22), met for order 2 (0.17); P_y, P_z below
   1e-3 P_x: met (at most 3.5e-4).
The figure shows why: the pulse itself is not the same at the three radii in its shape (its
positive lobe grows from 2.45e-3 to 2.95e-3 from R = 30 to 50 in (2,0), its negative lobe
shrinks), so A amplifies the difference (peak 3.77e-3) instead of only removing an offset; the
slow part after the pulse does not fall as 1/R alone. In the cumulative energies the time-domain
curve of A follows FFI 0.2 through the pulse (to u = 8 m, about 9e-5) and then grows without a
plateau, as an integrated offset does; FFI 0.1 takes most of its excess inside the pulse.
J3c (below) reads the energy up to the end of the pulse from the curves already computed.

## 2026-11-20 J3c. Energy up to the end of the pulse (a reading of the J3 and J3b curves; prediction)

`scripts/pulse_energy.py`: E from u = -15 to u_c = 8 and 10 m for every method, at each radius
and extrapolated. Prediction (written after seeing the cumulative curves, so it tests only what
the eye read): FFI 0.2 and time domain within 15 percent of each other up to u_c = 8 at R = 40,
50 and for A (order 1 and 2), all between 6e-5 and 1.0e-4; FFI 0.1 above them by more than 25
percent at R = 40, 50 (its excess is inside the pulse).

## 2026-11-20 J3c, outcome (run F-20261120-223121-c921d2d; `pulse_energy.json`)

E from u = -15 to u = 8 m [VERIFIED, `pulse_energy.json`]: R = 40: FFI 0.1 8.99e-5, 0.2 6.64e-5,
0.3 4.45e-5, time domain 2.00e-4; R = 50: 9.54e-5, 6.81e-5, 4.51e-5, 1.90e-4; extrapolated order
1: 1.91e-4, 9.43e-5, 5.67e-5, 9.01e-5; order 2: 9.12e-5, 6.28e-5, 4.21e-5, 7.73e-5. To u = 10 m
the values grow by 2-10 percent.
- FFI 0.2 and time domain within 15 percent: FAILED at R = 40, 50 (factor 3.0, 2.8), met for A
  of order 1 (4 percent), FAILED for order 2 (23 percent). So at finite radius the time-domain
  method is wrong already inside the pulse (its quadratic, fitted to the offset after the
  window, is far from the signal inside it); on the extrapolated waveform it agrees with FFI 0.2.
- All between 6e-5 and 1.0e-4: FAILED for the finite-radius time domain (1.9e-4, 2.0e-4); the
  others in range except FFI 0.3 (4.2e-5 to 5.7e-5) and extrapolated FFI 0.1 of order 1
  (1.9e-4).
- FFI 0.1 above FFI 0.2 by more than 25 percent at R = 40, 50: met (+35, +40 percent).

## 2026-11-20 Junk of one member: what is established

[VERIFIED numbers, runs F-20261120-222808-b65001c (J3), F-20261120-223018-a5c0838 (J3b),
F-20261120-223121-c921d2d (J3c), all on S2g, F-20261119-143443-f11ebb9; E in units of the
member's mass m, P/m = 0.25, cells m/8]
- The junk is a single outgoing pulse (u from -10 to +10 m) that arrives at fixed retarded time
  with the same r psi4 amplitude at 30, 40, 50 m (3.0e-3, 2.8e-3, 3.0e-3 in (2,0)); 94 percent
  of its energy is in (2,0) and (2,+-2) in the ratio of a pattern axisymmetric about the boost
  axis. It is followed by a slow near-zone signal of the moving hole that falls off with R.
- Energy through the end of the pulse: 4.5e-5 (FFI 0.3) to 9.5e-5 (FFI 0.1) at R = 40, 50 m;
  6.6e-5 and 6.8e-5 with the central FFI 0.2; extrapolated to infinity 4.2e-5 to 9.4e-5 for
  FFI 0.2-0.3 and the time domain (orders 1 and 2), 9.1e-5 and 1.9e-4 for FFI 0.1.
  Over the whole window (to u = 30) the same methods give 5.8e-5 to 1.15e-4 at R = 40, 50.
- Linear momentum along +x (the boost): 1.2e-5 to 2.5e-5 m (FFI 0.2), so a recoil of the hole of
  order 1e-5 c; P_y, P_z below 1e-3 of P_x.
Reading [JUDGEMENT]: E_junk/m = 7e-5, with a range 4e-5 to 2e-4 set by the separation from the
near-zone signal (the choice of omega_0 and of the window end), not by noise. This is 1.4 times
core's scaling 1.3e-2 (P/m)^4 = 5.1e-5 (three_punctures JOURNAL line 295) and inside E3/E10's
predicted 1e-5 to 5e-4. E10's own number (`single_analysis.py`: 3.7e-4, 2.8e-4, 2.4e-4 at 30,
40, 50) contains the integrated near-zone offset and is an upper bound only.

## 2026-11-20 J4a. Newtonian quadrupole reference for P1 (prediction)

`scripts/newton_quad.py`: the three bodies of `nr_first/inputs/p1_q4.athinput` (bare masses
1, 0.125, 0.125, velocities P/m) as Newtonian point masses (scipy DOP853, rtol 1e-11) to t = 280,
and the quadrupole luminosity from the exact jerk [BACKGROUND formula]. It is the time profile of
the physical emission (binary and passage) at the source; it says nothing about junk.
Predictions: relative energy drift of the integration below 1e-8; L for t < 20 within 30 percent
of the circular-binary formula (32/5) mu^2 a^4 Omega^6 (e_b = 0.033, `nr_first/results/
baselines_p1.json`), which I estimate at 1.25e-7 for a_b = 5.11, m_b = 0.25 [arithmetic]; the
pericentre of the binary's centre of mass at t = 104.35 (the Newton track of E6,
`baselines_p1.json` "t_cm_pericentre") within 0.5; L above twice the binary's value from about
t = 60-85 on (the passage's own quadrupole grows as the c.o.m. orbit closes in) [JUDGEMENT].
Run F-20261120-223314-b1b64fa FAILED (exit 1): the input reader split the file at the first
"<problem>", which is in the header comment, and found no `ncomp`. Fixed (block header on a line
of its own); rerun below, prediction unchanged.

## 2026-11-20 J4a, outcome (run F-20261120-223333-9fbe615; `newton_quad.json`, figure `fig_newton_quad.png` read)

[VERIFIED, `newton_quad.json`] Energy drift 5.6e-10: met. c.o.m. pericentre at t = 104.25
(r = 9.76): met (E6: 104.35). L for t < 20: median 2.31e-7 against the circular formula 1.31e-7
(computed in the run; my estimate 1.25e-7): FAILED (predicted within 30 percent; the figure shows
L varying by a factor 2.5 over t = 0-60 with the binary's radial period: r12 = 4.95 at t = 0
against a_b = 5.11, and the heavy hole's tide). L above twice its early value from t = 72, ten
times from t = 82: met (60-85). Cumulative quadrupole energy 8.5e-6 by t = 40, 1.07e-5 by 60,
2.1e-5 by 80, 1.8e-4 by 100, 5.5e-4 by 120, 9.7e-4 by 200 (the passage).

## 2026-11-20 J4. Junk of the three-hole data at P1's spheres (prediction, before any P1 waveform is integrated)

Data: P1, run F-20261119-150017-b45ec5f, `waveforms/rpsi4_{real,imag}_00{40,48,70,90}.txt`, read
only, to t = 112.25 M at the time of writing (J0); restarted segments repeat rows, the reader
keeps the last row of each time (`nr_first/scripts/nrread.py`). Geometry (input
`nr_first/inputs/p1_q4.athinput`): heavy hole at 6.35 M from the origin, members at 23.2 and
27.7 M (J4a: largest 27.67); cells 2 M within 48 M of the origin, 4 M to 100 M, root 8 M; outer
boundary 256 M. Retarded time with M = 1.25 (sum of the bare masses) [JUDGEMENT].

1. P1 prediction item 4 (lead, `tracks/F-hills/JOURNAL.md` lines 318-320): junk between 1e-6 and
   1e-4 M, passing the 40-90 M spheres by t = 150 M.
2. My scaling from J3 [JUDGEMENT]: E_junk = m E/m(P/m) with E/m = 7e-5 at P/m = 0.25 (range 4e-5
   to 2e-4) and core's power law (P/m)^4 (three_punctures JOURNAL line 295), the members
   (m = 0.125, P/m = 0.234 and 0.268 from the input's momenta) and the heavy hole (P/M = 0.056) at
   the same cells per mass (m/8, M/8): 0.125 x 7e-5 x (0.767 + 1.32) = 1.8e-5 M for the two
   members (range 1.0e-5 to 5.2e-5) and 1.8e-7 M for the heavy hole; the junk of the
   superposition itself (tides, the binary's missing radiation field) is not in this estimate.
   But the members' junk has omega of about 0.4/m_h = 3/M (wavelength 2 M), which the wave zone of
   P1 (cells 2 M and 4 M) cannot carry (nr_first E3, "Consequence for P1"): I predict that less
   than 10 percent of it, below 2e-6 M, reaches the 40 M sphere.
3. What the spheres will show instead [JUDGEMENT]: (a) the binary's own radiation at
   omega = 2 Omega_b = 0.089/M with luminosity 1-2.5e-7 (J4a), physical, not junk, 1-2e-5 M over
   the window below in the raw news, of which FFI with omega_0 = 0.2 keeps about
   (0.089/0.2)^2 = 0.2; (b) the near-zone field of the members, which pass 12-20 M from the 40 M
   sphere: large at 40 and 48, steeply smaller at 70 and 90; (c) a heavy-hole response at its
   quasinormal frequency 0.37/M, small.
4. Window: u in [-35, 50] M. Start: the members are up to 27.7 M from the origin, so their pulse
   (leaving at t < 5 M) reaches the near side of a sphere at u >= -28 - 5 (tortoise offsets of a
   few M). End: the Newtonian passage luminosity exceeds twice the binary's at t = 72 and ten
   times at t = 82 (J4a); its sources are within about 15 M of the origin then, so its first
   arrival is at u >= 72 - 15 = 57; I cut at u = 50, 7 M before, and check that dE/du does not
   rise by more than a factor 2 from u = 30 to 50 (refuted otherwise: then the burst is inside).
   The record at t <= 112.25 ends at u = 64 (40 M), 56 (48), 33 (70), 12 (90): the window is
   complete at 40 and 48 only. A second measurement on the window [-35, 12], complete at all
   four radii, gives E against 1/R.
5. Integration: FFI with omega_0 = 0.2/M central (half the heavy hole's l = 2 quasinormal
   frequency; the same rule as S2g in units of the heavy hole), 0.1 and 0.3 as variants, taper
   4 M; the time-domain method beside it.
6. Predictions to refute: (i) E (FFI 0.2, window [-35, 50]) at 40 M between 1e-7 and 2e-5 M and
   at 48 M below it (near-zone part falling); (ii) on [-35, 12] E falls from 40 to 90 by more than
   a factor 3 (refuted if E(90) > E(40)/3: then the signal is radiation, not near zone); (iii) no
   pulse at fixed retarded time common to 40, 48 and 70 M with more than 2e-6 M (refuted by one);
   (iv) dominant modes (2,+-2) (the orbits lie in the xy plane); (v) P_z below 1e-3 |P| (the data
   are symmetric under z -> -z); (vi) the extrapolated E_inf on [-35, 12] below 2e-6 M. If (i)-(iii)
   hold, the junk of the three-hole data is bounded above by E_inf and the scaled estimate
   (1.8e-5 M at most for what the members radiate on their own cells), and P1's prediction item 4
   is met only as an upper bound.
