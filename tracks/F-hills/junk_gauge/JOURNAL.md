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
