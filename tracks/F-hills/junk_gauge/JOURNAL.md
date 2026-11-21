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

## 2026-11-21 J0b. Restart in batch 2b (23:47 PST on the machine's clock)

Main merged (c442b569, release core-v0.5). Found committed: J0-J4a and the J4 prediction; not
done: E10's outcome, the J4 measurement, the gauge recommendation, README. P1's chain is at
segment 15 (Slurm 4773), waveforms to t = 253.25 M at all four spheres (last rows of
`rpsi4_real_00{40,48,70,90}.txt`). New since J4 was written [VERIFIED, `tracks/F-hills/p1/
JOURNAL.md` lines 173-183]: P1's binary MERGED at t = 48.8 M (common horizon from t = 48.81 M),
19.8 M from the grid origin; |x_1 - x_2| below 2 M at t = 39.2, 1 M at 44.1. E10's outcome is now
appended to `nr_first/JOURNAL.md` (items 1, 4, 5 met; 2 and 3 failed in one clause each).

## 2026-11-21 J4g. Where and when P1's sources radiate, from the trackers (prediction)

Why: J4's window [-35, 50] was cut against the Newtonian passage (J4a); P1's binary instead
spirals in and merges at t = 48.8 M, 19.8 M from the origin (J0b). Before any P1 waveform is
integrated I locate, from the trackers alone, the emission of that inspiral in retarded time.
`scripts/p1_geometry.py` (docstring: separation r12, centre of mass x_b of the binary, a
coordinate-track quadrupole luminosity L_trk as a proxy of the time profile [JUDGEMENT: not gauge
invariant], the circular formula at the tracked separation, and u_near(t_e) = t_e - |x_b(t_e)|,
the earliest retarded time at which anything emitted at t_e reaches any point of a sphere about
the origin).
Predictions [JUDGEMENT; r12 values below 2 M from p1 JOURNAL lines 174-175]: r12 = 4.95 at t = 0;
L_trk over t = 2-20 within a factor 3 of the circular formula there (1.3e-7, J4a), and above three
times that median from t = 25-35 M on, when r12 is 3.5-4.5 M and |x_b| 21-24 M, so u_near there
is 2-14 M; anything emitted after t = 35 M reaches the spheres at u >= 12 M or later. Refuted if
L_trk rises threefold before t = 20 or after t = 40.

## 2026-11-21 J4g, outcome (run F-20261121-075309-b6996ce; `p1_geometry.json`, figure `fig_p1_geometry.png` read)

[VERIFIED, `p1_geometry.json`] r12 = 4.952 M at t = 0, 4.29 at 20, 3.36 at 30, 1.84 at 40, 0.80 at
45; |x_b| = 25.40 (t = 0), 23.25 (20), 22.09 (30), 20.90 (40), 19.76 (48.8); heavy hole 6.35 ->
5.15 M from the origin. L_trk: median over t = 2-20 1.39e-6, ten times the circular formula there
(1.31e-7 at t = 0): FAILED (predicted within a factor 3); the figure shows why: L_trk is dominated
up to t = 12 by the trackers' start-up motion (values up to 10 at t = 0, the filter's edge and the
gauge transient), so that median is not the binary's emission. L_trk above 3x that median from
t = 23.55 (r12 = 4.0, |x_b| = 22.8, u_near = 0.7): r12 and |x_b| met, the time FAILED narrowly
(predicted 25-35) and u_near FAILED narrowly (predicted 2-14); not refuted (between 20 and 40).
Tenfold at t = 28.7 (u_near = 6.5); from t = 25 on L_trk follows the circular formula at the
tracked separation (figure), which is tenfold its t = 0 value at r12 = 3.1 (t of about 31).
Earliest retarded arrival of anything emitted after t_e: 13.5 (t_e = 35), 19.1 (40): met (>= 12).

## 2026-11-21 J4b. Junk window that keeps P1's inspiral out (prediction, before any P1 waveform is integrated)

I have not looked at P1's waveforms or figures; I know of them only the E_rad to t = 112.25 that
p1 recorded (2.6e-4, 9.9e-5, 5.4e-5, 7.1e-6 M at 40, 48, 70, 90; p1 JOURNAL line 237: the whole
record, merger included). J4 is run as written (whole record, windows [-35, 50] and [-35, 12])
beside J4b; J4's prediction items stand and are judged as written.
Retarded time u = t - R* (M = 1.25), as J4.
Window: u in [-35, 6] M at all four radii (complete at all: the record reaches u = 153 at 90 M).
Start -35: the members' junk, emitted at t < 5 M about 25 M from the origin, reaches the near side
of a sphere at u >= -28 (J4 item 4). End 6: the tracked emission of the inspiral is tenfold its
early value from t = 28.7 M, which reaches the nearest point of a sphere at u = 6.5 (J4g); the
merger (t = 48.8, |x_b| = 19.8) at u >= 29. Before u = 6 the window holds the binary's slow
inspiral from t_e up to about 31 on the near side: my estimate of that part, int w(t_e) L(t_e)
dt_e with w the share of the sphere reached by u = 6 (isotropic emission) and L the circular
formula at the tracked separation, is about 5e-6 M before FFI and about 1e-6 M after it (2 Omega
= 0.09-0.2/M below omega_0 = 0.2) [JUDGEMENT, arithmetic]. The far-side tail of the members' junk
(u up to about +30 there) is cut off: it is the price of keeping the inspiral out.
Integration: FFI (omega_0 = 0.2/M central; 0.1, 0.3) on the record cut at u <= 14 (cosine taper
4 M at both ends, so the end taper lies on [10, 14], after the window), so that the inspiral and
the merger cannot enter the window through the FFI kernel (its spread is about 1/omega_0 = 5 M
with slowly decaying side lobes); the time-domain method beside it (not predicted: its quadratic
is fitted outside the window on a record that holds the inspiral).
Junk against noise and near zone: (a) the share of the window's energy spectrum above
omega = 1/M (`hf_frac`); (b) E(R) across the four radii, straight lines E_inf + a/R through all four
and through 70 and 90 M only.
Predictions [JUDGEMENT]:
1. The members' junk does not reach the spheres: hf_frac below 0.01 at 70 and 90 M (their junk
   has omega of about 3/M, wavelength 2 M = one cell at the spheres, and a source 25 M off the
   centre needs l of about omega d = 75 > 8 in the extraction).
2. E (FFI 0.2) at 70 and 90 M between 1e-7 and 1e-5 M, within a factor 2 of each other; at 40 M
   more than three times that at 90 M (near zone of the members, 15 M from the 40 M sphere).
3. E_inf (FFI 0.2) from 70 and 90 M between -1e-6 and 1e-5 M; the four-radius line gives an
   E_inf within 1e-5 M of it. Refuted outside.
4. FFI 0.1 and 0.3 within a factor 2 of FFI 0.2 at 70 and 90 M.
5. Momentum: |P_z| below 1e-3 |P| at every radius (z -> -z symmetry of the data); |P| < E.
6. P1 prediction item 4 (junk between 1e-6 and 1e-4 M through the 40-90 M spheres by t = 150 M):
   judged on E_inf of item 3; I expect it below 1e-5 M and cannot say whether above 1e-6 M; if it
   is below 1e-6 M, item 4 fails on the low side for what the spheres can see, and the members'
   own junk (1.0e-5 to 5.2e-5 M scaled from S2g, J4 item 2) stays unmeasured at P1's resolution.

## 2026-11-21 J4c. What the J4b window holds, by l and by frequency (prediction, after seeing J4b's totals and l shares)

J4b ran (run F-20261121-075600-4480a13; outcome written below after J4c): the window [-35, 6]
holds 2.5-2.8e-6 M at all four radii with 67-70 percent of it in l >= 4 (`P1b_junk.json`,
"share"). So it is outgoing radiation from an off-centre source, and the extraction's l <= 8
may cut part of it. `scripts/p1_lspec.py` gives E_l (l = 2..8) and the band shares of the
window's spectrum (|omega| < 0.2, 0.2-0.5, 0.5-1, > 1 per M; all modes and l = 2 alone).
Predictions [JUDGEMENT; a source about 23-25 M off the centre radiating at omega needs l up to
about omega d]:
1. E_l does not fall by more than a factor 3 from l = 4 to l = 8 at 70 and 90 M (so l > 8
   carries energy the extraction misses; the window's energy is a lower bound).
2. Band shares at 90 M (all modes): 0.2-0.5 the largest, above 0.4; above 1/M below 0.02
   (J4b: 0.015); below 0.2 less than 0.3.
3. At 40 M the band above 1/M has a larger share than at 90 M (2 M cells within 48 M carry
   higher frequencies than the 4 M cells beyond).
Refuted outside these.

## 2026-11-21 J4, outcome as written (run F-20261121-075600-4480a13; `P1w50_junk.json`, `P1w12_junk.json`; figures `fig_p1_waves.png`, `fig_p1_energy.png`, `fig_p1_extrap.png` read)

P1's waveforms read to t = 253.25 M (all four windows complete at all radii). Whole record,
FFI omega_0 = 0.2 central [VERIFIED, the JSON files of the run]:
| R | E [-35, 50] | E [-35, 12] | (2,+-2) share [-35, 50] | l >= 4 share [-35, 50] |
|---|---|---|---|---|
| 40 | 7.41e-5 | 4.31e-6 | 0.019 | 0.84 |
| 48 | 7.44e-5 | 4.04e-6 | 0.018 | 0.84 |
| 70 | 6.93e-5 | 3.82e-6 | 0.022 | 0.84 |
| 90 | 6.35e-5 | 3.91e-6 | 0.028 | 0.82 |
Lines E_inf + a/R through the four radii: [-35, 50] 5.7e-5, [-35, 12] 3.5e-6 (FFI 0.2).
Window check of item 4: dE/du at u = 50 is 0.44-0.82 of its value at u = 30 (no rise), so the
check as written passes; but the figures show the merger burst inside the window: dE/du peaks at
u = 24.9 (40, 48 M) and 27.8-28.0 (70, 90 M) at 4.3e-6 to 9.3e-6, the arrival J4g puts at u >= 19
for the last M before the merger. The check was built for a passage burst at u >= 57 and does not
catch an earlier one.
1-6 of item 6:
(i) E at 40 M on [-35, 50] between 1e-7 and 2e-5: FAILED (7.4e-5, the merger's burst); at 48 M
    below 40 M: FAILED (equal within 0.4 percent).
(ii) on [-35, 12] E(90) < E(40)/3: REFUTED (3.9e-6 against 4.3e-6): the window holds radiation,
    not the near zone I expected.
(iii) no pulse common to 40, 48, 70 M above 2e-6 M: REFUTED: 3.8-4.3e-6 M arrives at the same
    retarded time at all four radii on [-35, 12], and 6-7e-5 M on [-35, 50].
(iv) dominant modes (2,+-2): FAILED; l >= 4 carries 0.82-0.84 of [-35, 50] and 0.54-0.60 of
    [-35, 12]; (2,+-2) 0.02-0.03 and 0.07-0.15.
(v) P_z below 1e-3 |P|: met on [-35, 50] (1.8e-4 to 8e-4); on [-35, 12] FAILED at 40, 70, 90 M
    (up to 3.4e-2 at 40 M, where |P| is small).
(vi) E_inf on [-35, 12] below 2e-6: FAILED (3.5e-6).
Item 2's "less than 10 percent of the members' junk, below 2e-6 M, reaches 40 M": FAILED as
stated (4.3e-6 on [-35, 12], 2.8e-6 on J4b's window, at 40 M), with what that energy is open (J4b,
J4c). Item 3 (a) (binary's radiation 2-4e-6 M after FFI over the window): not separable here.
So J4's premises were wrong twice: P1 has no passage burst at u >= 57 but a merger burst from
u of about 19 on, and what precedes it at the spheres is radiation of an off-centre source in
high l, not a near-zone field.

## 2026-11-21 J4b, outcome (run F-20261121-075600-4480a13; `P1b_junk.json`, `p1_extrap.json`; same figures)

Window [-35, 6] M, record cut at u = 14 M [VERIFIED, `P1b_junk.json`, `p1_extrap.json`]:
| R | FFI 0.1 | FFI 0.2 | FFI 0.3 | time domain | hf_frac | P (FFI 0.2) | l >= 4 share |
|---|---|---|---|---|---|---|---|
| 40 | 4.21e-6 | 2.84e-6 | 2.24e-6 | 1.9e-4 | 0.28 | (-4.2e-7, -1.37e-6, -3.2e-8) | 0.70 |
| 48 | 3.67e-6 | 2.62e-6 | 2.04e-6 | 4.6e-5 | 0.20 | (-2.9e-7, -1.15e-6, -6e-10) | 0.69 |
| 70 | 3.66e-6 | 2.46e-6 | 1.81e-6 | 4.5e-5 | 0.050 | (-1.6e-7, -8.8e-7, 1.7e-9) | 0.67 |
| 90 | 3.72e-6 | 2.52e-6 | 1.87e-6 | 6.0e-5 | 0.015 | (-1.1e-7, -8.2e-7, 1.7e-9) | 0.67 |
E_inf (FFI 0.2): 2.19e-6 (line through the four radii), 2.75e-6 (through 70 and 90); FFI 0.1
3.3e-6 / 3.9e-6, FFI 0.3 1.5e-6 / 2.1e-6. Noise outside the window (rate before u = -35 times
41 M): 6e-8 to 8e-7, 2-30 percent of E (largest at 40 M). The cumulative energy (figure) rises
within 3 M of u = -35 at every radius, then grows steadily to u = 6; the record before u = -35 is
quiet at 70 and 90 M (r psi4 1e-6 to 1e-5) and rises there by one to two decades.
1. hf_frac below 0.01 at 70 and 90 M: FAILED (0.050, 0.015); the share falls outward (0.28 at
   40, 0.20 at 48 M), so frequencies above 1/M are carried by the 2 M cells and lost in the 4 M
   cells beyond 48 M [JUDGEMENT].
2. E at 70 and 90 M in 1e-7 to 1e-5 and within a factor 2: met (2.46e-6, 2.52e-6). E(40) more
   than 3 E(90): FAILED (1.13): no near zone; the window's energy arrives at fixed retarded time
   with the same size at 40-90 M, so it is outgoing radiation.
3. E_inf (70-90) in -1e-6 to 1e-5: met (2.75e-6); four-radius E_inf within 1e-5 of it: met
   (2.19e-6).
4. FFI 0.1, 0.3 within a factor 2 of 0.2 at 70, 90 M: met (1.49 / 1.47 and 0.74 / 0.74).
5. |P_z| below 1e-3 |P|: met at 48 M only (5e-4); FAILED at 40 (2.2e-2), 70 (1.9e-3), 90 M
   (2.1e-3). |P| < E: met (|P|/E = 0.51, 0.45, 0.36, 0.33). P points from the origin toward the
   binary ((-0.14, -0.99) at 90 M; the binary is at (-0.38, -0.92) of 25 M) and shrinks outward
   as an off-centre source seen at finite R should [JUDGEMENT]; the line in 1/R gives P_y,inf
   -3.3e-7 (four radii) or -6.0e-7 (70, 90): the junk's momentum at infinity is not determined
   better than "below 1e-6 M".
6. P1 prediction item 4 (junk 1e-6 to 1e-4 M through the 40-90 M spheres by t = 150 M): MET,
   with E_inf 2.2-2.8e-6 M (FFI 0.2; 1.5-3.9e-6 over the FFI variants), arriving by t = 106 M at
   90 M. What the number holds (J4c): radiation in l = 2..8 with E_l flat in l, so l > 8 would add
   more (a lower bound in l), and it includes the binary's slow inspiral before t of about 31 M,
   my estimate 1e-6 M after FFI (an upper bound for the junk alone). The time domain does not
   work here (1e-4 level; its quadratic is fitted to a record holding the inspiral).

## 2026-11-21 J4c, outcome (run F-20261121-075803-8e1955b; `p1_lspec.json`, figure `fig_p1_lspec.png` read)

[VERIFIED, `p1_lspec.json`] E_l over l = 2..8 in J4b's window, R = 90 M: 4.7, 3.6, 3.1, 3.1, 3.3,
3.7, 3.8 e-7; R = 70 M: 4.5, 3.7, 2.7, 3.1, 3.1, 3.6, 3.9 e-7; at 40 and 48 M the same shape
(4.9 to 3.3 to 4.4 e-7). Band shares (all modes, |omega| < 0.2 / 0.2-0.5 / 0.5-1 / > 1): 90 M
0.30 / 0.54 / 0.15 / 0.015; 70 M 0.27 / 0.59 / 0.10 / 0.050; 40 M 0.22 / 0.42 / 0.08 / 0.28;
l = 2 alone 0.59-0.72 below 0.2/M at every radius.
1. E_l not falling by more than 3 from l = 4 to 8 at 70, 90 M: met (it rises, 1.4 and 1.2 times).
2. At 90 M: 0.2-0.5 the largest and above 0.4: met (0.54); above 1/M below 0.02: met (0.015);
   below 0.2 under 0.3: FAILED by 0.001 (0.301).
3. Above 1/M larger at 40 than at 90 M: met (0.28 against 0.015).
Reading [JUDGEMENT]: the junk window holds radiation of a source about 25 M off the centre at
0.2-0.5/M spread evenly over l = 2..8 and beyond; the l = 2 part is mostly below 0.2/M, where the
binary's own emission lies (2 Omega = 0.09-0.16/M for r12 = 4.95-3.4 M). The extraction up to
l = 8 does not converge in l for this source; the energy that passes the spheres is at least
the measured 2.5e-6 M and, if E_l stays flat to l of about omega d = 5-12, up to about twice it.

## 2026-11-21 Junk of the three-hole data: what is established (for G1 T3)

[VERIFIED numbers from runs F-20261121-075600-4480a13 (J4, J4b), F-20261121-075803-8e1955b (J4c),
F-20261121-075309-b6996ce (J4g), all read-only on P1, F-20261119-150017-b45ec5f]
- In the retarded-time window [-35, 6] M, which ends before P1's inspiral emission (tenfold its
  early level from t = 28.7 M) can reach any point of a sphere, the spheres at 40, 48, 70 and 90 M
  receive 2.8, 2.6, 2.5, 2.5 e-6 M (FFI 0.2): the same at fixed retarded time, so outgoing
  radiation; E_inf = 2.2-2.8e-6 M (1.5-3.9e-6 with the FFI variants). Momentum below 1.4e-6 M at
  every radius, pointing toward the binary and falling outward (off-centre source at finite R).
- It is spread evenly over l = 2..8 (67-70 percent in l >= 4) at 0.2-0.5/M: an off-centre source
  that the l <= 8 extraction resolves only in part (the number is a lower bound in l, up to about
  twice larger). It also contains the binary's slow inspiral of the first 30 M (about 1e-6 M by
  my estimate): the junk alone is between about 1.5e-6 and 5e-6 M [JUDGEMENT].
- The members' junk at its own frequency (about 3/M) is not carried by the wave zone: the share
  above 1/M falls from 0.28 at 40 M (2 M cells) to 0.015 at 90 M (4 M cells). The single-member
  measurement (S2g, J3c: E/m = 7e-5, range 4e-5 to 2e-4) scaled to P1's members gives 1.8e-5 M
  (1.0e-5 to 5.2e-5) radiated near the members [JUDGEMENT, scaling of J4 item 2], several times
  what the spheres see; it is lost in the wave zone of P1's grid, not measured there.
- So the junk of P1's data lies between about 1.5e-6 M (seen at the spheres) and 5e-5 M (the
  members' scaled junk at its upper end); against the binary's Newtonian binding energy
  m1 m2 / 2a = 1.6e-3 M that is at most about 3 percent [arithmetic].

## 2026-11-21 G. Gauge recommendation for the passages after P1 (written into README)

[JUDGEMENT, from E3, E10 and P1] Use core's mass-scaled shift damping (shift_eta = 2/M, profile on,
M_ref = M, width 4) for the next passage, after a 400-cycle three-hole card smoke and with a
profile arm in the lead's isolated-binary test; full text, reasons and what is untested in
README "Gauge recommendation". One reading added for it [VERIFIED, column meanradius of
`single.horizon_summary_0.txt` of S3, S2 (run F-20261115-173601-2fae2dc) and S2g (run
F-20261119-143443-f11ebb9)]: S2g's coordinate horizon has mean radius 1.06 m (t = 10), 1.03 (14),
0.99 (20), 1.01 (40, 89.5), between S3's 1.16-1.18 and S2's 0.92-0.89 m: the profile gives the
member S3's horizon mass but not S3's coordinate size (my first README draft said it did; corrected
before commit).

## 2026-11-21 State at the end of the package (batch 2b)

Done: S2g finished; E10 judged (nr_first JOURNAL); single-member junk (J1-J3c); three-hole junk
(J4g, J4, J4b, J4c); gauge recommendation; README with the G1 T3 text. Failed predictions on
record: J2 (2 of its bounds), J3 (4 of 6), J3b (3 of 4), J3c (2 of 3), J4a (1), J4g (3 clauses,
narrowly), J4 (all six items of item 6 but (v) on the main window), J4b (items 1, 2 second clause,
5), J4c (one clause by 0.001). Not done: a second-agent review of J3-J4c; nothing is pending on the
cards. P1's chain (segment 15, Slurm 4773) keeps appending; J4b does not depend on it.
