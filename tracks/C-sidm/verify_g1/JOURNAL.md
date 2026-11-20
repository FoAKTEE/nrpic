# JOURNAL of verify_g1 (fresh-context verifier of C-sidm G1)

Labels: [VERIFIED] read at a source with locator or measured in a registered run of this
package; [BACKGROUND] standard result not re-derived; [JUDGEMENT] own reasoning;
[TO VERIFY] open.

## Entry 0 (2026-11-20 14:13 PST) Set-up and blind rules

Read: CLAUDE.md, coord/CHARTER.md (to Owners, 9.6, 10), decisions 0010, 0016, 0019,
harness/RULES.md (nrpic-run), collide/TESTS.md, collide/SPEC.md (definitions), the
interface text of `core/collisions-2` (sections 1-5, 11; not section 8, which is core's
own verification), docs/FORMATS.md, python/nrpic/collide.py (readers only). Not read
(blind phase): stage/**, PLAN-wave3.md, STATUS/HANDOFF/RISKS/JOURNAL of the track, any
package JOURNAL, Results sections of READMEs, the note, results/*.json, summary.json of
the run directories (written by the drivers; they may hold fitted values).

Inputs found for V1: the run directories hold for every case `case.json`, the deck
arguments in `athena.log`, the first and the last snapshot (`heat.part.00000.bin`,
`heat.part.000NN.bin`) and `reduced.npz` (Fourier sums of every snapshot, written by the
driver; the intermediate snapshots were deleted). I use `reduced.npz` for the time series
and check it against the two snapshots that remain (my own sums from the particles).
Deviation of the runs from TESTS.md T7 seen in `case.json`: eps = 0.2 (T7 says 0.05).

## Entry 1 (14:40) V1 predictions, before any computation

V1a Chapman-Enskog conductivity [own Monte Carlo of the collision brackets, ce_kappa.py].
Method: variational form of the first Chapman-Enskog equation, kappa = k_B <X, L^-1 X>/T
... (non-relativistic: X = (x - 5/2) c_z, x = m c^2/(2 k T); trial functions
Phi = sum_j a_j S_j(x) c_z with Sonine polynomials S_j = L_j^(3/2)); brackets
<Phi_i, L Phi_j> = (1/4) n^2 sigma_tot E[g Delta Phi_i Delta Phi_j] over Maxwellian pairs
with isotropic centre-of-momentum scattering (= hard spheres = the code's operator).
Prediction: the first approximation gives kappa_1 sigma_tot/(k_B sqrt(k_B T/m)) =
75 sqrt(pi)/64 = 2.0771 within 4 Monte Carlo standard errors (formula of Koda & Shapiro
arXiv:1101.3097 `sidm1.tex` lines 401-415: q = -(3/2) b (v/sigma) d v^2/dr with
b = 25 sqrt(pi)/32 [VERIFIED read], which is kappa = (3/2) b sqrt(T/m)/sigma_tot); orders
2-4 raise it by 2-3 percent (Chapman-Cowling value about 1.025 [BACKGROUND]). Refuted if the
first approximation differs from 2.0771 by more than 4 standard errors or the sequence does
not increase monotonically (the variational sequence must). Relativistic first
approximation (Eckart frame, X = v_z (E - h), h = m K3/K2, Moller flux) at theta = 0.003:
within 1.5 percent of the non-relativistic value; at theta -> 0 it must reproduce 2.0771.

V1b Isobaric mode (runs C-20261119-144545-c606492, C-20261119-155434-8563453).
Separation of sound and entropy mode: from the n-mode A_n = c1_M/sM and the pressure mode
A_p = c1_MK/sMK (p = (2/3) e_kin, non-relativistic; at theta = 0.003 the difference from
(1/3) sum M u^2/W is O(theta) of a quantity that is itself small), the entropy amplitude
A_s = A_n - (c_v/c_p) A_p is free of adiabatic sound (delta s = c_v dp/p - c_p dn/n = 0)
and equals A_n for the isobaric mode. Prediction: A_n shows an oscillation at
omega = c_s k (period 2 pi/(c_s k) = 444 at k lambda = 0.2) that A_s does not; A_s decays
exponentially. Expected kappa/kappa_1 at (k lambda)^2 -> 0: 1.02-1.05 (Sonine 1.025 times a
cell-size gain of order +1 percent at dx = lambda/4 [BACKGROUND, TO VERIFY]); at finite
k lambda the apparent kappa falls below (Burnett order (k lambda)^2). Nonlinearity at
eps = 0.2: quantified with my isobaric Lagrangian reference (heat_ref.py); I expect a
correction to the fitted rate of order eps^2, i.e. 1-4 percent. Refuted: kappa/kappa_1 outside
[0.99, 1.06] after the corrections I can compute; per-seed scatter larger than the
fit errors by more than a factor 2 (would mean an unmodelled noise source).
V1c Temperature step (run C-20261119-144535-2c7b6a4, lambda/L = 0.01, theta 0.02/0.01,
equal pressure). Prediction: with the nonlinear isobaric reference (kappa = f kappa_1(T),
c_p(theta)), the fitted f is 1.02-1.05 and agrees with V1b within the errors; the linear
form `step_diffusive` of the test definition, with chi at the final state, gives a value
biased by the factor-2 contrast (sign not predicted).
