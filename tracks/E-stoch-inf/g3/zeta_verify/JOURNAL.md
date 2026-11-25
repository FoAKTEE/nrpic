# Journal of g3/zeta_verify (independent check of the zeta reader, decision 0041 item 1)

Helper of E-stoch-inf, batch 21 (2026-11-25). I did not write `zeta/zeta_reader.py` and do not
read it, nor the lead's journal entries on Z0-Z2, before my own numbers below exist. Sources
read: SCOPE.md 4d.1, 4d.3, 4d.9 (A1-A14); the deck `usr/inputs/usr_base.athinput`; the
potential in `athenak/src/scalar_field/scalar_field.hpp` lines 56-95; the dump format
`scalar_field_diag.cpp` (NRSFDMP2) and `scalar_field_io.cpp` lines 1-20; the definition of Pi
in `coord/INTERFACES/scalar_field.md` line 43; the R^NR formula `ladder/scripts/ladder_lib.py`
lines 175-187.

## Entry 1 (09:05 PST): predictions before any computation

Conventions I fix here (G = c = 1, code units of the deck): homogeneous Friedmann-Klein-Gordon
(FKG) in e-folds with state (phi, y = dphi/dN): H^2 = (8 pi/3) V/(1 - 4 pi y^2/3),
y' = -(3 - 4 pi y^2) y - V'/H^2. A cell's state (phi, Pi, K): y = -3 Pi/K (normal observers,
Pi = n^mu d_mu phi, local expansion -K/3). Delta N_bg(cell) = e-folds from the cell's state to
phi = phi_e, phi_e = phi of the homogeneous background at N* + 15 (started from the lockstep
background of the dump at N_f).

Numbers from the dump history that I looked at before writing this (zp4, usr.sf.00001.modes
header): at N_f = N* + 10.000, phi_b = -0.0558140583, Pi_b = 2.6950e-7, H = 0.95181,
eps1 = 1.0e-12, eps2 = -0.0276; box rms(dphi) = 4.77e-9, rms(dPi) = 6.31e-11 (s = 1/4).

P1 (closed form, exponential potential V = V0 exp(-lambda phi), exact attractor y = lambda/(8 pi)
in code units; off the attractor the FKG system separates in y). My integrator gives N(phi0, y0)
to phi_e within 1e-11 (absolute) of the closed form for y0 off the attractor by up to 50 per
cent; the variational first and second derivatives dN/dy0, d2N/dy0^2 within 1e-8 relative;
dN/dphi0 = -1/lambda' exactly and d2N/dphi0^2 = 0 (shift symmetry) to 1e-10 of
|dN/dphi0|/|phi0|. Refuted if any of these misses by ten times the bar.

P2 (closed form, Hamilton-Jacobi potential with H(phi) given, attractor y = -H'/(4 pi H)):
N(phi0) on the attractor within 1e-10 of the quadrature of 4 pi H/H'; its first and second
derivatives along the attractor within 1e-7 relative.

P3 (Z0 on the pairs): O_zeta = -O_R per cell; rms(O_zeta + O_R)/rms(O_R) below 1e-3 at both
amplitudes (I expect about 1e-4 to 3e-3 from the second-order part of the momentum and from
chi; refuted as "Z0 holds" if above 1e-3). Linear coefficient of O_zeta on O_R: -1.000 within
1e-3.

P4 (the map at N_f along the box's relation): the box's (dphi, dPi) lie on the background
trajectory (adiabatic): dPi/dphi = (dPi_b/dN)/(dphi_b/dN) = H (dln Pi_b/dN) ~ 0.013, from the
rms ratio 6.31e-11/4.77e-9 = 0.0132. Along the trajectory N is exactly linear in the time shift,
so the quadratic coefficient of the map along the box's relation in terms of zeta_1 = N_phi dphi
is a_map = (1/2) dln y/dN at N_f = -eps2/4 ~ 0.007 (range 0.004-0.010). a_zeta on the lattice
= a_map - a_R (A14(b)); a_zeta at s = 1/4 and 1/2 agree within 2 per cent.

P5 (the map along the momentum alone, at fixed phi and K): N_Pi = -1/(3 Pi_b) (1 + O(eps2)),
i.e. the decaying mode moves the field by dy/3; N_Pi dPi is about 0.5 per cent of N_phi dphi at
the box's spread. The second-order change of N along Pi alone at eps = rms(dPi) is about 5e-11
in N, comparable to the resolution of N at the end surface in double precision (the field moves
2.8e-7 per e-fold near phi_e, and phi ~ 0.056 is resolved to 7e-18, so N is quantised at about
2.5e-11). Prediction: the 0.142 discrepancy of the second coefficient along the momentum is a
numerical-precision artefact of a finite-difference second coefficient taken where the
second-order change of N is near the round-off of the end-surface crossing (an ill-conditioned
test, not a property of the map): the exact second derivative (variational equations) and
finite differences in extended precision agree with each other within 1 per cent, and float64
finite differences at eps, 2 eps scatter by ten per cent or more. The map is analytic in Pi
(Pi_b + dPi stays positive: |dPi|/Pi_b ~ 2e-4). Refuted if extended-precision finite
differences and the variational coefficient disagree by more than 1 per cent, or if float64
finite differences at the box's eps are stable to 1 per cent.

P6 (consequence for the one-point statistics): the box's states lie on the relation up to a
residual dPi_perp whose rms is below 1 per cent of rms(dPi); an error of 14 per cent in the
coefficient of the momentum alone then moves zeta by less than 1e-6 sigma per cell and F(3),
F(4) by less than 1e-5 relative. Refuted if the computed shift of F(3) or F(4) exceeds 1e-3
relative.

## Entry 2 (09:20 PST): outcome of P1, P2; a development pass; prediction P7

Run E-20261125-170519-fa5ad33 (`scripts/test_closed.py`, figure `fig_closed_form.png` looked at:
fourth-order convergence in the step for the exponential case, a floor of 1e-14 for the
Hamilton-Jacobi case at N = 27.6).
- P1 HELD: at h = 1e-3, |N - N_exact| <= 8.2e-16 for y0/y_a - 1 in [-0.5, 0.5] (bar 1e-11);
  N_y within 1.1e-14, N_yy within 3.4e-12 relative of the 40-digit reference (bar 1e-8);
  N_phi = -1/y_a to 2.2e-16; N_phiphi, N_phiy below 8.2e-13 (absolute, against N_yy ~ 1-4).
- P2 HELD: N = 27.611138361785630 against 27.611138361785620 (1.0e-14); first and second
  derivatives along the attractor within 6e-19 and 3e-17 relative (bars 1e-10, 1e-7).

A development pass of `scripts/analyse_pairs.py` on the pairs (output in scratch tmp, not a
result; the registered run below repeats it bit for bit, processors being deterministic) showed
that the second finite-difference coefficient along the momentum alone at eps = the box's
spread is off by 907 per cent in float64 and by 1.2 per cent even in long double, while the
variational coefficient is step-converged to 6e-13; the error moved to +0.29 per cent when the
step changed from 1e-3 to 7.3e-4 and barely moved when the end surface was shifted within a
step. My P5 named the end-surface quantisation (2.5e-11 in float64) as the floor; that
mechanism is too small. New prediction before the registered run:

P7 (round-off floor of N): the floor is the accumulated rounding of the absolute field over the
~5000 steps, about sqrt(5000) x ulp(phi ~ 0.056) x |N_phi| (|N_phi| = 3.5e6): 1.5e-12 in
long double, 1.5e-9 in float64. Measured as the rms of N(e) minus a cubic over 41 points within
+-3 spreads: long double 3e-13 to 3e-12, float64 3e-10 to 3e-9, both directions, changing
erratically (not smoothly) with the step. Refuted if the long-double floor is below 1e-13 or
the float64 floor below 1e-10, or if the floor scales smoothly with the step (then it is
truncation, not rounding). The second-order change of N along the momentum alone at one spread
is 4.2e-11 (from N_PiPi): a float64 integration of the absolute field cannot resolve it.
