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

## Outcomes

(below, appended as the checks run)
