# Journal of verifier2 (helper of B-emd-gw, wave 2b, 2026-11-19)

Independent verification for gate G1 of the wave-2 runs of Track B: the first-source scan
(crossed waves (1, eps, 0) in full GR) and the Newtonian-mode tests. Fresh reader: I did not
read `stage/REVIEW-wave2.md`, the owner's `STATUS.md`, `HANDOFF.md`, `JOURNAL.md` or the
package journals before my own numbers existed. I read the package READMEs
(`first_source/README.md`, `newton_tests/README.md`) for the set-up and the list of claims,
the run manifests, the inputs and `cosmo/ic/make_east.py`, and the AthenaK writer
`athenak/src/outputs/binary.cpp` for the dump format. Every script is mine
(`verifier2/scripts/`); none of the track's analysis code (`fslib`, `gw_diag`,
`analyze_*.py`) is imported or read.

## Predictions (written 2026-11-19 06:20 PST, before any of my analyses ran)

V1 Derivation. A symbolic second-order expansion of the Einstein equations (sympy, metric
a^2[-(1+2 Phi) d eta^2 + ((1-2 Phi) delta_ij + h_ij) dx^i dx^j], dust, Phi constant in
time, matter domination) gives for the + amplitude of the (k,k,0) mode, polarization
e+ = m m - z z with m = (1,-1,0)/sqrt 2:
  h'' + 2 calH h' + K^2 h = K^2 s,  K^2 = 2 k^2,  s = -(5/6) Phi_1 Phi_2,
for Phi = Phi_1 sin(kx) + Phi_2 sin(ky). Refuted if the coefficient is not -5/6 (I recall
the source TT[4 Phi d_i d_j Phi + (2/3) d_i Phi d_j Phi] from the literature but have not
derived it here before).

V2 Amplitude. With the set-up of make_east.py (Phi_1 = -(3/2) delta / k^2, delta = 0.01,
k = pi/2) s = -3.080e-5 eps. With h(eta_0) = 0 (conformally flat start) and h'(eta_0) = 0
(the first-order traceless extrinsic curvature vanishes for this dictionary, so its
second-order flat-TT part vanishes), g(eta) = 1 + A j1(K eta)/(K eta) + B y1(K eta)/(K eta)
with eta = t + 2. Prediction: the flat-TT + amplitude of the conformal metric at K1, read
by my own reader from the single-precision bin dumps of the 64^3 card runs, agrees with
s g within 1 % for 2 <= a <= 10 (eps = 0.1, 0.3, 1, zero shift), and c_+/eps agrees
among the three eps to 0.5 % there (the next correction at (1,1,0) is of fourth order).
Refuted by a larger difference; if h'(eta_0) is not zero in the data, the measured
TT part of tilde A at t = 0 says so and the reference is redone with it (stated).

V3 Null. eps = 0 (plane symmetric): the flat-TT part of tilde gamma at every wave vector
is zero up to the precision of the dump (single precision bin: ~1e-7 of the traceless
part; double rst if read: ~1e-15); gyy - gzz and gyz vanish at round-off. Refuted by a
TT amplitude growing with time above round-off.

V4 Resolutions. c_+(K1) from the 32^3 processor runs agrees with 64^3 to 1 % up to
a = 80 (before shell crossing at a ~ 100); refuted by > 1 %.

V5 Pancake. In 1D, before any sheet crossing, each sheet obeys exactly
s'' + calH s' = (3/2) calH^2 s (s = x - q_mass), so x(a) = q + A a + B a^(-3/2) from the
initial position and velocity of each particle. The Newtonian-mode runs (P1 east,
n = 16, 32, 64) follow this to the errors of the README table within 10 %, and the error
falls by about four per doubling. Refuted by a different error or order.

V6 Ellipsoid. My own homogeneous-ellipsoid ODE (Carlson R_D for the shape integrals)
from the json parameters gives the first x crossing at t_turn + 14.32 = 23.85 t_k
(README: 23.8524) to 1e-4; the code's crossing (minimum of I_xx in the history, my
interpolation) converges to it at about second order (README: +0.90, +0.18, +0.034 %).
Refuted by a disagreement above 1e-3 relative in the ODE value or a non-convergent code
crossing.

## Outcomes (2026-11-19 06:25 PST, written before I read the track's review)

Readers. Unregistered smoke tests of `athio.py` (minutes): bin and rst dumps of the same
cycle (eps = 0.3, 64^3, cycle 82) agree to float32 rounding (|d gxx| 5.9e-8, |d Axy| 9e-13),
so the restart layout (header, lloc, data_size field, LayoutRight blocks with 4 ghosts) is
read correctly. The first scan run B-20261119-141201-1433762 wrote outside its run
directory and was stopped after 5 s (empty directory removed); resubmitted.

V1 CONFIRMED. Run B-20261119-140854-ec1f1c2 (sympy, `results/derive_s_output.txt`): the
background and first-order equations come out right (8 pi G rho a^2 = 3 calH^2,
v_i = -(2/(3 calH)) d_i Phi, no first-order traceless ij part), and the + equation at K1 is
H'' + (4/eta) H' + 2 k^2 H = -(5/3) k^2 Phi_1 Phi_2, i.e. s = -(5/6) Phi_1 Phi_2 exactly.
With Phi_1 = -(3/2)(0.01)/(pi/2)^2 = -6.0793e-3: s = -3.0798e-5 eps.

V2 CONFIRMED with one correction. Scan B-20261119-141219-b391580, comparison
B-20261119-142111-139aa84 (supersedes -141828-09cebfa; -141813-91cfe8e failed on an assert
of equal dump times between runs, which do differ). Measured potentials from alpha:
Phi_1 = -6.07942e-3 (eps 0.1) to -6.07964e-3 (eps 1), dictionary -6.07927e-3, so
s_measured/s_dictionary - 1 = 6e-5 to 1.2e-4. Measured h'(eta_0) from the TT part of tilde A
at t = 0: 0.002-0.004 s (changes the comparison by < 3e-6). Largest |c_+ - s g|/|s| over
2 <= a <= 10 (bin, 64^3): 0.246 % (eps 0.1), 0.244 % (0.3), 0.478 % (1); 32^3: 0.21, 0.21,
0.41 %; the largest value sits at a = 10. Later: a = 20: 1.15, 1.26, 2.34 %; a = 40: 5.7, 6.2,
11.4 %; c_+/s at 80 <= a <= 140: 1.32-2.07 (0.1), 1.35-2.20 (0.3), 1.82-2.53 (1). The
sin parts are < 3e-9 s and c_+(K2) = -c_+(K1) to 2e-8 s (symmetry), as expected.
The prediction "c_+/eps agrees among the three eps to 0.5 %" holds (0.21 % at a = 10), but
my reason was wrong in part: the (1,1,0) correction is fourth order, Phi1 Phi2 [alpha +
beta (Phi1^2 + Phi2^2)], hence of relative size R (1 + eps^2), not eps-independent. Test of
that form (run B-20261119-142015-da5ad0f, rst = double precision): r(0.1,0.3)/r(0.1,1) =
0.0806 (a = 6.3), 0.0808 (a = 9.0), 0.0810 (a = 20.3) against 0.0808 predicted. In single
precision (bin) the eps = 0.1 series is noisy at 1e-4 relative (bin against rst at the same
cycle: 3.2e-4 for eps 0.1, 1.5e-4 for 0.3, 4.1e-5 for 1), so r(0.1,0.3) from bin is noise
below a ~ 10.

V3 CONFIRMED. eps = 0, 64^3, all 218 bin and 23 rst dumps to a = 140: largest TT amplitude
of h at any wave vector 7.0e-17 (rst) / 9.8e-17 (bin), of tilde A 3.8e-17 (rst) / 2.3e-15
(bin); max |gyy - gzz| 3.2e-14, max |gyz| 2.4e-14 (rst; bin rounds gyy, gzz to the same
float). The rms traceless part grows from 1e-4 to 1.2e-2. [JUDGEMENT] The null follows from
the y <-> z symmetry of the aligned lattice and of the flat TT projection: it shows that the
code keeps that symmetry through shell crossing, not that particle noise is absent.

V4 CONFIRMED for eps 0.1 and 0.3, NOT for eps 1 over the whole interval. |c32 - c64|/|c64|:
<= 0.09 % for 2 <= a <= 50 in every case; max over 2 <= a <= 80: 0.44 % (0.1), 0.45 % (0.3),
1.02 % (eps 1, at a = 75.8; 0.47 % at a = 80 itself), 1.6 % (Gamma driver, a = 79; 1.9 % at
80); at a = 100: 0.24, 0.10, 3.2, 2.4 %. Note: the two meshes carry 8 and 8 particles per
cell, i.e. 2.1M and 262k particles; this is not a convergence study.

Gauge (raw, no correction): (c_+ Gamma driver - c_+ zero shift)/|s| = -0.36 % at a = 10,
-11.5 % at a = 60 (64^3); 32^3: -0.36 %, -11.2 %. The corrected difference (G_tot of the
track) is not recomputed here.

Box-mode fraction of the TT power of h (64^3): at a = 20 0.844 (0.1), 0.834 (0.3), 0.739 (1),
so up to 26 % of the TT power is in other modes by a = 20.

V5 CONFIRMED. Run B-20261119-142135-e582e09. Exact sheets (growing plus decaying mode per
sheet, mass coordinate, mean displacement zero; total momentum 1e-20). Largest error of the
tracked line in units of (a - 1) d/k at a = 2, 5, 10, 15: n = 16: 5.72e-3, 1.16e-2, 1.79e-2,
2.43e-2; n = 32: 1.39e-3, 2.95e-3, 4.29e-3, 5.59e-3; n = 64: 3.52e-4, 7.36e-4, 1.21e-3,
1.37e-3; ratio per doubling 4.1 and 3.9 at a = 2 (second order). First crossing of
neighbouring tracked particles: code 21.873, 21.338, 21.162; exact discrete sheets 21.444,
21.109, 21.027 (the code crosses 2.0, 1.1, 0.6 % late). Plane symmetry: largest spread of x
within one sheet 8.6e-16, 2.6e-15, 1.2e-14 (n = 16, 32, 64) up to a = 16 and 1.6e-15,
6.9e-15, 2.3e-14 at a = 36; drift of y and z <= 7.8e-16. Sin pancake: largest
|I_xx - I_xx^exact| over 1.2 <= a <= 15, in units of the range of I_xx^exact there:
8.85e-3, 2.23e-3, 5.57e-4 (n = 16, 32, 64): second order.

V6 CONFIRMED. My ODE (Carlson R_D, json axes and rates; particle file consistent: mass
0.75, linear velocity field to 1e-16, lattice axes within 0.3 % at N = 32 and 0.01 % at
N = 128): first x crossing at t_turn + 14.320748 = 23.852370 t_k. Code (first sign change
of dI_xx, linear interpolation): 24.065902, 23.895492, 23.860390 t_k at N = 32, 64, 128;
relative errors +0.895, +0.181, +0.0336 %; order 2.28; Richardson limit 23.85128
(-0.0046 %). The ODE started from the lattice moments instead gives 23.9162, 23.8604,
23.8518 (the lattice start explains part of the N = 32 error, not the N = 128 one).

## After reading the track's review (2026-11-19 06:35 PST)

Comparison run B-20261119-142332-dd28d1d adds max |c_+/(s g) - 1| (the review's measure):
0.224, 0.222, 0.435 % (64^3), 0.195, 0.190, 0.379 % (32^3), identical to the review's
numbers; my earlier 0.246/0.478 % are |c_+ - s g|/|s| and differ by g(a = 10) = 1.10.
Maxima of c_+/s for eps 1: 2.496 at a = 96.1 and 2.547 at a = 123.3, as in the review.
The review's "linearity 0.050 %" is the pair (0.1, 0.3) in bin (mine 0.0497 %), i.e. the
single-precision floor. No claim WRONG; F3 (eps 1), F7 (bound for eps 1 and the Gamma
driver) and N3 (number) NOT CONFIRMED as worded. Report: `VERIFIER.md`.
