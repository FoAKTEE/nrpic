# Verifier report: the wave-2 runs of B-emd-gw for gate G1 (verifier2, 2026-11-19)

Independent verification (item C18 of `CHECKLIST.md`) of the first-source scan in full GR
(crossed waves (1, eps, 0), runs B-20261115-164059-d802e82, -165353-b592d43 on cards at 64^3,
-165525-f7c2004 on processors at 32^3) and of the Newtonian-mode tests (pancakes
B-20261115-165349-81a17bc, -163556-ad5637f, -165351-b38db6f, -163558-20244f2,
-163653-f6324ea; ellipsoid -163613-790095f, -163615-7bc8b30, -163617-085c093).

How it was done. I was a fresh reader: I did not read `stage/REVIEW-wave2.md`, the owner's
STATUS, HANDOFF or journals, or the package journals until my own numbers were written into
`JOURNAL.md` (commit 8519d1d1). I read the package READMEs for the set-up and the claims, the
manifests, the inputs, `cosmo/ic/make_east.py` and the AthenaK writers
(`athenak/src/outputs/binary.cpp`, `restart.cpp`). Everything else is my own code in
`verifier2/scripts/`: readers of the bin, restart, snapshot and trajectory files (`athio.py`;
bin and restart dumps of the same cycle agree to float32 rounding), a symbolic derivation of
the second-order source (`derive_s.py`), the flat-TT diagnostics (`scan.py`), the comparison
(`compare.py`, `linearity.py`) and the Newtonian references (`newton_checks.py`: exact 1D
sheets, homogeneous-ellipsoid ODE). None of the track's analysis code was imported or read.
Predictions were committed before the checks (commit ec1f1c21). Figures in `verifier2/figs/`,
all looked at.

Runs of this report (registered, processors, scouting, gate G1):

| Run | What |
|---|---|
| B-20261119-140854-ec1f1c2 | derivation of s (sympy) |
| B-20261119-141219-b391580 | TT diagnostics of every bin (218) and rst (23) dump of the 10 scan runs |
| B-20261119-142332-dd28d1d | comparison with s g, null, meshes, gauges, bin against rst (cited; supersedes -142111-139aa84 and -141828-09cebfa, same numbers; -141813-91cfe8e failed on an assert) |
| B-20261119-142015-da5ad0f | linearity in eps pair by pair, bin and rst |
| B-20261119-142135-e582e09 | pancakes against exact sheets, ellipsoid against the ODE |
| B-20261119-141201-1433762 | stopped after 5 s (wrote outside its run directory), resubmitted as -141219- |

## Verdicts, first source (claims of `first_source/README.md`, "State")

Notation: s = -(5/6) Phi_1 Phi_2, e+ = m m - z z with m = (1,-1,0)/sqrt 2,
h_ij = c_+ e+_ij cos(K1.x) at K1 = (k,k,0); g(eta) solves g'' + (4/eta) g' + 2k^2 (g - 1) = 0,
g(2) = g'(2) = 0, eta = t + 2.

| # | Claim | Verdict | My numbers (run) |
|---|---|---|---|
| F1 | s = -(5/6) phi_x phi_y = -3.08e-5 eps | CONFIRMED | derived from the Einstein equations at second order: + equation at K1 is H'' + (4/eta) H' + 2k^2 H = -(5/3) k^2 Phi_1 Phi_2, so s = -(5/6) Phi_1 Phi_2; first-order checks (Friedmann, v_i = -(2/(3 calH)) d_i Phi, no first-order traceless part) pass (-140854-). Phi_1 = -6.07927e-3 (dictionary), -6.0794e-3 to -6.0796e-3 measured from alpha: s = -3.0798e-5 eps, measured s within 1.2e-4 (-142332-) |
| F2 | c_+(k,k,0) follows s g including the junk oscillation, to 0.22 % (eps 0.1, 0.3) and 0.44 % (eps 1) for 2 <= a <= 10 | CONFIRMED | max \|c_+/(s g) - 1\| = 0.224, 0.222, 0.435 % (64^3), 0.195, 0.190, 0.379 % (32^3); as \|c_+ - s g\|/\|s\|: 0.246, 0.244, 0.478 %. The start has no second-order TT velocity: TT part of tilde A at t = 0 gives h'(eta_0) = 0.002-0.004 s, effect < 3e-6. c_+(K2) = -c_+(K1) to 2e-8 s; sine parts < 3e-9 s (-142332-) |
| F3 | linear in eps to 0.05 % | CONFIRMED for eps 0.1 against 0.3 only; NOT CONFIRMED for eps 1 | (0.1, 0.3): 0.050 % from bin, which is the single-precision floor of the eps = 0.1 series; 0.014 % at a = 9 from rst. (0.1, 1): 0.21 % at a = 10 (bin), 0.17 % at a = 9 (rst). The difference has the fourth-order form Phi1 Phi2 [alpha + beta (Phi1^2 + Phi2^2)]: r(0.1,0.3)/r(0.1,1) = 0.0806, 0.0808, 0.0810 at a = 6.3, 9.0, 20.3 against 0.0808 (rst, -142015-) |
| F4 | departures 1-2 % at a = 20, 6-11 % at a = 40 | CONFIRMED | \|c_+ - s g\|/\|s\| = 1.15, 1.26, 2.34 % (a = 20), 5.7, 6.2, 11.4 % (a = 40), eps 0.1, 0.3, 1 (-142332-) |
| F5 | growth to 1.6-2.5 times s after shell crossing (a ~ 80-140) | CONFIRMED in substance | c_+/s for 80 <= a <= 140: 1.32-2.07 (0.1), 1.35-2.20 (0.3), 1.82-2.55 (1; maxima 2.50 at a = 96.1, 2.55 at a = 123.3); Gamma driver 2.57 at a = 96.1. The lower end 1.6 is reached for eps <= 0.3 only from a ~ 100 (-142332-) |
| F6 | null (eps 0): TT amplitudes of h and tilde A at round-off (<= 2.8e-16) through shell crossing | CONFIRMED | largest TT amplitude at any wave vector over all dumps to a = 140: h 7.0e-17, tilde A 3.8e-17 (rst, 64^3); bin 9.8e-17, 2.3e-15; max \|gyy - gzz\| 3.2e-14, \|gyz\| 2.4e-14 (rst); rms traceless part 1e-4 to 1.2e-2 (-142332-) |
| F7 | 32^3 against 64^3: 0.5 % up to a = 80, 3 % at a = 100 (README, "Not done / open") | CONFIRMED at the sampled a and for eps 0.1, 0.3; NOT CONFIRMED as a bound for eps 1 | max over 2 <= a <= 80: 0.44 % (0.1), 0.45 % (0.3), 1.02 % (1, at a = 75.8; 0.47 % at a = 80), 1.6 % (Gamma driver, a = 79; 1.9 % at a = 80); <= 0.09 % for 2 <= a <= 50 in every case; a = 100: 0.24, 0.10, 3.2, 2.4 % (-142332-) |
| F8 | single- and double-precision c_+(K1) agree to 4e-5 (eps 1) and 3e-4 (eps 0.1) | CONFIRMED | 4.1e-5, 3.2e-4 (64^3, 22 common cycles); 1.5e-4 for eps 0.3 (-142332-) |
| F9 | second gauge, raw difference 0.4 % of s at a = 10, 11 % at a = 60 | CONFIRMED | (Gamma driver - zero shift)/\|s\| = -0.131, -0.360, -1.454, -4.82, -11.52 % at a = 5, 10, 20, 40, 60 (64^3); 32^3 -0.36, -11.2 % (-142332-) |
| F10 | P4 failed: other modes take up to 26 % of the TT power by a = 20 | CONFIRMED | box-mode share of the TT power of h at a = 20: 0.844, 0.834, 0.739 (eps 0.1, 0.3, 1) (-142332-) |

Not checked here: the gauge piece G_tot and its reduction of the two-gauge difference to
0.008 and 1.2 %; the magnetic Weyl agreement; rho_kin/rho_grad and rho_GW/rho_bar; the
late-rise analysis of the wave-1 dumps (P7-P10).

## Verdicts, Newtonian mode (claims of `newton_tests/README.md`)

| # | Claim | Verdict | My numbers (run B-20261119-142135-e582e09) |
|---|---|---|---|
| N1 | P1 east pancake, largest sheet error in units of (a-1) d/k at a = 2, 5, 10, 15: n = 16: 5.64e-3, 1.16e-2, 1.84e-2, 2.48e-2; n = 32: 1.39e-3, 2.99e-3, 4.42e-3, 5.76e-3; n = 64: 3.51e-4, 7.42e-4, 1.20e-3, 1.41e-3 | CONFIRMED | reference: each sheet exact before crossing, s(a) = A a + B a^(-3/2) from its own position and velocity at a = 1 (mass coordinate, mean displacement zero). n = 16: 5.72e-3, 1.16e-2, 1.79e-2, 2.43e-2; n = 32: 1.39e-3, 2.95e-3, 4.29e-3, 5.59e-3; n = 64: 3.52e-4, 7.36e-4, 1.21e-3, 1.37e-3 (within 3 %; second order, 4.1 and 3.9 per doubling at a = 2) |
| N2 | P1 first sheet crossing at a = 21.87, 21.34, 21.16 | CONFIRMED | 21.873, 21.338, 21.162 from the tracked line; the exact discrete sheets cross at 21.444, 21.109, 21.027, so the code crosses 2.0, 1.1, 0.6 % late |
| N3 | plane symmetry kept to 1.3e-15 L | NOT CONFIRMED as a number; round-off level CONFIRMED | largest spread of x within one sheet up to a = 16: 8.6e-16, 2.6e-15, 1.2e-14 (n = 16, 32, 64); 2.3e-14 at a = 36 (n = 64); y, z drift <= 7.8e-16. The README does not say which measure gives 1.3e-15 |
| N4 | P2 sin pancake, I_xx error 8.1e-3, 2.0e-3, 5.1e-4 (n = 16, 32, 64) | CONFIRMED in order and size | largest \|I_xx - I_xx^exact\| over 1.2 <= a <= 15 in units of the range of I_xx^exact: 8.85e-3, 2.23e-3, 5.57e-4 (factor 3.97, 4.0); my normalization may differ from the README's (values 9-11 % higher) |
| N5 | N1 ellipsoid: ODE first x crossing 23.8524 t_k; code 24.0659, 23.8955, 23.8604 (+0.90, +0.18, +0.034 %); Richardson 23.8513, order 2.3 | CONFIRMED | own ODE (Carlson R_D) from the json axes and rates (particle file consistent: mass 0.75, linear velocity field to 1e-16): 23.852370; code (first sign change of dI_xx/dt): 24.065902, 23.895492, 23.860390 (+0.895, +0.181, +0.0336 %); order 2.28, limit 23.85128 (-0.0046 %) |

Not checked here: the quadrupole energies of N1, the self-similarity N3, the H1 growth law,
the Layzer-Irvine column, the step check.

No claim was found WRONG.

## Comparison with the track's review (`stage/REVIEW-wave2.md`, read after my numbers)

1. Every first-source number of the review that I recomputed agrees to the printed digits:
   0.224, 0.222, 0.435 % and 0.195, 0.190, 0.379 % (F2); the raw two-gauge differences
   0.131-11.52 % (F9); the 1.02 % at 32^3 against 64^3 for eps 1 between a = 40 and 80 (F7);
   the two maxima of c_+/s for eps 1 (2.50 near a = 96, 2.55 at a = 123); the N1 crossing
   times to six decimals and the Richardson value 23.85128 (order 2.28). Two independent
   readers and two independently derived references give the same result.
2. Linearity. The review accepts "0.050 / 0.05 percent" (P3). That number is the pair
   eps = 0.1 against 0.3 in single precision, at the noise floor of the eps = 0.1 bin series
   (bin against rst 3.2e-4). In double precision the pair differs by 0.014 % at a = 9, and
   eps = 1 departs from eps = 0.1 by 0.17-0.21 % there. The three runs fit the fourth-order
   form R(a) (1 + eps^2) with the ratio 0.0808 to three digits; written as
   D + R (1 + eps^2), the departure from s g at a = 10 is R = -0.23 % and D = -0.01 % of
   \|s\| [JUDGEMENT on the decomposition; arithmetic on the values of -142332-]. This puts a
   number on the review's judgement (item 3 of "Wrong or imprecise") that the departure after
   a ~ 10 is beyond second order and grows with eps: almost all of it is the fourth-order
   term, not junk or gauge.
3. Pancake sheet errors. The review did not reread them ("not reread"); this report does,
   against an exact reference of its own, and confirms the README table within 3 %. New: the
   exact discrete sheets cross at a = 21.44, 21.11, 21.03, so the code's crossing is late by
   2.0, 1.1, 0.6 % (n = 16, 32, 64).
4. Resolution. The review states 0.4-0.5 % at a = 80 for zero shift and corrects the
   helper's bound to 1.02 % for eps 1 at 40 < a <= 80. I agree, and add that the Gamma-driver
   run differs between the meshes by 1.6 % at a = 79 and 1.9 % at a = 80. Both meshes carry
   eight particles per cell (262 144 and 2 097 152 particles): mesh and particle number change
   together, so this is not a convergence study (the README says so).
5. Null. The review's 1.9e-16 and the helper's 2.8e-16 are a different normalization of the
   same round-off; mine is 7e-17 (h) and 3.8e-17 (tilde A) in double precision. [JUDGEMENT]
   For eps = 0 the set-up (aligned lattice, (1, 0, 0)) is symmetric under y <-> z and the flat
   TT part at wave vectors along x is (h_yy - h_zz)/2 and h_yz; the null therefore tests that
   the code keeps that symmetry through shell crossing, not the noise floor of the GW
   extraction. The jittered-lattice null of `OPEN.md` is the test of the noise floor.
6. The review relies on the lead's own g(tau). Mine is derived independently and uses
   h'(eta_0) = 0; the measured TT part of tilde A at t = 0 (0.2-0.4 % of s in h') confirms that
   choice and that the reference needs no fitted parameter.

## Weak points of this verification

- The time series are from the single-precision bin dumps; double precision exists only
  every unit of time (rst). The eps = 0.1 series carries 1e-4 relative noise in bin.
- The reference assumes that the code's zero-shift gauge coincides with Poisson gauge to
  second order for the flat TT strain at K1; the raw two-gauge difference (0.36 % of s at
  a = 10) and the derivation support it, but I did not compute the gauge pieces.
- I checked the claims of the two READMEs that the task names; the G_tot correction, the
  energies and the late-rise analysis are not covered.
