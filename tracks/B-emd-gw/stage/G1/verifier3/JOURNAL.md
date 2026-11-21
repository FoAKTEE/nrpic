# Journal of stage/G1/verifier3 (independent verifier of G1 criterion 1 and of the spatial-gauge piece)

Helper of B-emd-gw, wave 3 round 1, started 2026-11-20 14:13 PST (`date`). Fresh context: I
did not produce the runs I check. Read so far (allowed list of the task): CLAUDE.md,
coord/CHARTER.md to "Owners", decision 0010, harness/RULES.md, docs/FORMATS.md, the set-up
files of waves/ (inputs/flat_oblique.athinput, expanding.athinput, card64.list,
card64_x10.list, scripts/make_expanding_ic.py, run_flat.sh, run_expanding.sh), the generator
`git show core/requests-b:athenak/src/pgen/tests/z4c_linear_wave.cpp` (the task named
`athenak/src/pgen/z4c_linear_wave.cpp`; the file lives in `pgen/tests/`), the binary writer
`git show core/requests-b:athenak/src/outputs/binary.cpp`, `athenak/src/pgen/nrpic/nrpic_cosmo.cpp`
lines 1-230, `athenak/src/z4c/z4c_adm.cpp` (ADM <-> Z4c), cosmo/README.md "Units and gauge",
gw_diag/README.md (definitions). Not read (forbidden until my V3 numbers are committed):
waves/README.md Results/Open, waves/JOURNAL.md, stage/** outside this directory, note/,
the owner's STATUS/HANDOFF/JOURNAL/PLAN, scratch/orch reports.

## Entry 1 (14:20): V1 predictions, before any check

Exact solutions I derive (by hand first; the script `scripts/v1_exact.py` checks them):

(F) Flat box [-1/2,1/2]^3, k = (1,1,1) cycles, K = 2 pi k, omega = |K| = 2 pi sqrt 3,
alpha = 1, beta = 0. Linear TT wave h_ij = A_+ e+_ij sin(P) + A_x ex_ij sin(P + phi_x),
P = K.x - omega t, gamma_ij = delta_ij + h_ij, K_ij = -(1/2) d_t h_ij, so
At_ij = chi (K_ij - gamma_ij K/3) = (omega/2)[A_+ e+ cos P + A_x ex cos(P+phi_x)] at first
order (chi = 1, K = 0 at first order). This is the generator's closed form with
pi |k| = omega/2. Linear ADM: d_t K_ij = R_ij = -(1/2) lap h_ij for TT h, so
d_t^2 h = lap h: exact for omega = |K|.
Predictions P1.1-P1.4:
- P1.1 the generator's (axx..azz) equal theta-hat theta-hat - phi-hat phi-hat and
  (bxx..bzz) equal theta-hat phi-hat + phi-hat theta-hat for khat = (1,1,1)/sqrt 3, with
  theta-hat, phi-hat the usual spherical unit vectors of khat (theta from +z, azimuth from
  +x); both transverse and traceless, e:e = 2, e+:ex = 0, to round-off (< 1e-15).
  Refuted if any of these fails by more than 1e-14 (then the cross polarization is not what
  the comment says, or not TT).
- P1.2 the closed form satisfies the linearized ADM equations (sympy residual identically 0);
  refuted by a non-zero residual (sign of At, factor pi|k|).
- P1.3 for this wave E_ij = (|K|^2/2) h_ij, B_ij = -(1/2) sym(eps_ikl d_k (d_t h)_lj)
  (coordinate components) and Psi_4 = -(E - iB)_ij mbar^i mbar^j with
  mbar = (theta-hat - i phi-hat)/sqrt 2 equals d_t^2 h_+ - i d_t^2 h_x for the wave moving
  along +khat and 0 for the reversed direction. Refuted if the sympy check of the 3+1
  formulas (E from R_ij + K K_ij - K_ik K^k_j, B from eps D K) linearized in A disagrees.

(X) Expanding box, side 4, k = (pi/2)(1,1,0), |K| = pi/sqrt 2 = 2.2214. Background:
lapse d_t alpha = -(1/3) alpha^2 K, zero shift, Einstein-de Sitter with H = 1 at a = 1:
alpha = a = (1 + t/2)^2, K = -3 a'/a^2 = -3 a^(-3/2) (prime = d/dt, t conformal time).
Perturbation gamma_ij = a^2 (delta_ij + h_ij), h TT, lapse unperturbed at first order.
Mode equation h'' + 2 (a'/a) h' + |K|^2 h = 0, a'/a = 2/(t+2). With tau = t + 2 the
solutions are j_1(|K| tau)/(|K| tau) and y_1(|K| tau)/(|K| tau). Initial slice of
make_expanding_ic.py: psi = 1, K = -3, alpha = 1, Ahat_ij = -(1/2) h'_ij(0) with
h'_ij(0) = eps_+ e+ cos(K.x) + eps_x ex cos(K.x + phi_x): from K_ij = -(1/2 alpha) d_t gamma_ij
at t = 0, a = 1, a'(0) = 1, K_ij = -(delta + h) - h'/2, so the traceless part is -h'/2 and
h(0) = 0. Hence h_+(x,t) = eps_+ T(t) cos(K.x), h_x = eps_x T(t) cos(K.x + phi_x) with
T = c1 j1(x)/x + c2 y1(x)/x, x = |K|(t+2), T(0) = 0, T'(0) = 1. The Z4c variables give
h = gt - delta (chi removes a^2) and h' = -2 a At (At = chi (K_ij - gamma K/3) = -h'/(2a)).
Weyl parts, coordinate components (my derivation): E_ij = (|K|^2/2) h_ij + (a'/(2a)) h'_ij
(= -(1/2)(h'' + (a'/a) h') by the mode equation), B_ij = -(1/2) sym(eps_ikl d_k h'_lj)
(independent of a: eps_i^kl = a^-1 [ikl], K_lj = -(a'/a^2) gamma_lj - (a/2) h'_lj).
Predictions P1.5-P1.7:
- P1.5 the closed form T(t) matches an independent numerical integration of the mode
  equation (solve_ivp, rtol 1e-12) to 1e-9 relative on t in [0, 10], and its ODE residual
  (finite differences of the closed form) is at the level of the difference error.
  Refuted otherwise.
- P1.6 a = (1+t/2)^2 and alpha = a solve the lapse condition and the Friedmann equation
  with rho_0 = 3/(8 pi) (sympy, identically).
- P1.7 the sympy linearization of E_ij and B_ij of the 3+1 formulas for the metric
  a^2(delta + eps T(t) e cos(K.x)) with K_ij = -(1/2a) d_t gamma_ij gives exactly the
  expressions above. Refuted by any non-zero residual (then my Weyl reference for X is
  wrong and V3-X must use the sympy expression instead).

## Entry 2 (14:30): V1 outcome (run B-20261120-222342-8cda367; failed first attempt B-20261120-222232-3d7d57e, a matrix-sum TypeError in my script)

All seven predictions hold [VERIFIED, results/v1.json, figs/v1_T.png]:
- P1.1: generator (axx..azz) = e+ and (bxx..bzz) = ex of the spherical basis to 2.2e-16 for
  k = (1,1,1), and for 200 random k to 8.3e-16; transverse and traceless to 4e-16; e:e = 2,
  e+:ex = 0. So the corrected generator uses exactly my basis (theta-hat, phi-hat).
- P1.2: At(generator) = K_ij(linear) and d_t K_ij = R_ij(linear), d_t^2 h = lap h: sympy 0.
- P1.3: background E, B = 0; first-order E = (w^2/2) h, B = -(1/2) sym(eps d hdot): sympy 0;
  Psi4(+n) = hdd_+ - i hdd_x exactly and Psi4(-n) = 0.
- P1.5: closed form T vs DOP853 to 1.9e-12 (T) and 8.7e-13 (T'); FD residual 5.3e-7 of
  k^2 max|T| = the O(1e-6) error of the h = 1e-3 central difference; sympy: j1(x)/x and
  y1(x)/x solve h_xx + (4/x) h_x + h = 0. c1 = -9.0975, c2 = 0.43808; T(10) = -5.0e-4
  (t = 10 is 0.015 after a zero at 9.985: the final dump sits next to a node, so errors at
  t = 10 must be measured relative to the envelope, not to |T(10)|). Zeros of T:
  1.46, 2.89, 4.315, 5.735, 7.15, 8.57, 9.985; extrema 0.27 (t ~ 0.6), then decaying
  roughly as 1/tau^2.
- P1.6: lapse condition and Friedmann equation with rho_0 = 3/(8 pi): sympy 0.
- P1.7: first-order E and B of the 3+1 formulas for a^2(delta + eps T e cos) equal my
  expressions (sympy 0 once a > 0 is declared); the ADM evolution equation with dust at rest
  is satisfied at order eps^0 (Friedmann acceleration) and at order eps^1 exactly when T
  obeys T'' + 2(a'/a)T' + k^2 T = 0 (sympy 0). So the mode equation of the input comment is
  the one the Einstein equations give in this gauge.

## Entry 3 (14:35): V2 predictions (scripts/diag.py, scripts/v2_tests.py), before the run

- P2.1 (reader, double, test F N16 t = 0, run B-20261119-142016-ee73a03): gt equals
  delta + h_exact to <= 2.3e-16 (rounding of 1 + h), At equals -hdot/2 to <= 1e-21,
  chi = alpha = 1 and Khat = Theta = Gam = beta = 0 exactly; header time 0, cycle 0, 22
  variables of 8 bytes, one block. The same data re-blocked into 8 shuffled blocks read back
  identically (0); a truncated file is refused. Refuted by any larger difference.
- P2.2 (reader, single precision, the 32^3 z4c_linear_wave along x of run
  B-emd-gw-20261115-112947-b7b431d, amp 1e-6): reader = float32(closed form) exactly or
  within one float ulp (1.2e-7 at 1); refuted by a larger difference (byte order, offsets).
- P2.3 (TT, non-cubic box 32x24x20, random TT waves + gauge + trace parts): Lambda(TT) = TT,
  Lambda(gauge + trace) = 0, Lambda^2 = Lambda, trace and divergence of Lambda T vanish, all
  to <= 1e-13 relative; mode coefficient of 0.7 cos(K.x + 0.4) gives 0.7 and 0.4 to 1e-15.
- P2.4 (Weyl, flat wave of test F on 16^3 and 32^3, spectral derivatives): E, B and the
  Psi4-inferred complex amplitudes agree with the linear exact values to a relative error
  of order the amplitude (~1e-6 at amp 1e-6, ~1e-5 at x10: the nonlinear terms);
  Psi4(-n) / (w^2 A) ~ 1e-6. With sixth-order differences instead: E error ~5e-5 at 16^3
  and ~1e-6 at 32^3 (order 6). Refuted if the spectral error does not scale with amplitude.
- P2.5 (Weyl and TT, EdS mode on 32^3 at t = 0, 0.6, 3, 9, eps x1 and x10): E_+, B_x of my
  code minus my exact linear expressions, relative, ~eps (1e-6 .. 1e-5) and x10 at x10;
  E_x, B_+ likewise; the TT route (h = Lambda(gt - delta), h' = Lambda(-2 a At)) recovers
  eps T and eps T' to O(eps^2).
- P2.6 (initial dumps of test X, N16 and N64): gamma = delta exactly, K equals the exact
  K_ij(t = 0) to round-off, alpha = 1, and Lambda(-2 At) has the mode coefficients
  2c_+ = 2e-6 (real) and |2c_x| = 1e-6 with phase 1.0: then make_expanding_ic.py's basis is
  mine. Refuted if the phase or sign differs (I would then compare in its basis).

## Entry 4 (14:50): V2 outcome (run B-20261120-222822-e26afae; an unregistered smoke run of the same commit gave identical numbers)

[VERIFIED, results/v2.json, figs/v2_weyl.png]
- P2.1 holds: header time 0, cycle 0, 22 variables of 8 bytes, one block; gt - (delta + h)
  1.7e-16, At + hdot/2 6.8e-21; chi = alpha = 1, Khat = Theta = Gam = beta = 0 exactly; the
  8-block shuffled re-blocking reads back identically (0); a file 8 bytes short is refused.
- P2.2 holds: the single-precision dump equals float32(closed form) to 1.2e-22 (values of
  size 1e-22 in gxy; elsewhere exact); its distance to the double closed form is 5.8e-8, the
  float32 rounding.
- P2.3 holds: Lambda(TT) = TT 2.1e-15, Lambda(gauge + trace) 2.8e-16, idempotent 2.5e-15,
  trace 4.3e-14 (absolute, fields of order a few), divergence 2.1e-15; mode coefficient
  exact.
- P2.4 holds for the scaling with amplitude in the field maximum of E (1.07e-6 at amp 1e-6,
  1.07e-5 at x10: the second-order terms); B and the Psi4-inferred mode amplitudes are
  better than predicted (1e-12 .. 7e-11): the mode projection at K removes the second-order
  terms (they live at 0 and 2K), so what is left is round-off. FD6: E 5.2e-5 (16^3),
  1.9e-6 (32^3, there floored by the 1e-6 second-order field-max error).
- P2.5 better than predicted for the same reason: mode-projected E, B and the TT route
  agree with my exact linear expressions to 1e-12 .. 5e-10 relative (round-off of a
  perturbation 1e-6 on an O(1..36) background), and the x10 case is not worse (third order
  is eps^2 ~ 4e-10 relative at most).
- P2.6 holds: the initial slices of X at N16 and N64 have gamma = delta and K = K_exact
  exactly, alpha = 1, Theta = Gam = 0, and Lambda(-2 At) has 2c_+ = 1.99999999995e-6 (real)
  and 2c_x = 1.0e-6 at phase 1.0000: make_expanding_ic.py's basis is mine, and the initial
  amplitudes are as the input comment says (eps_+ = 2e-6, eps_x = 1e-6, phi_x = 1).
Consequence for V3: with spectral derivatives the Weyl route is, at linear order, an
algebraic re-expression of the TT route (E is k^2 h/2 + calH h'/2 of the same numerical
h, B is k h'/2); a disagreement can only come from the backward/forward split (Psi_4 of F),
the background (calH) or nonlinear and round-off terms. I therefore also evaluate the Weyl
parts with sixth-order differences (what AthenaK's own Psi_4 would use at nghost 4), whose
own truncation then enters the comparison.

## Entry 5 (15:05): V3 predictions, before any measurement of the evolved dumps

Facts used (read from the code and logs, not from results): AthenaK's Kreiss-Oliger term at
nghost 4 is diss 2^-8 (-1) times the eighth difference over h (utils/finite_diff.hpp
Diss<4>, z4c.cpp line 168), damping rate per direction sigma sin^8(k_a h/2)/h; second
derivatives are sixth order; RK4 with dt = 0.25 h in F (log: 148 cycles to t = 2.3094 at
N16); in X dt = min(0.01 (1 + t/2), 0.25 h) (log of N48: dt = 0.01 at t = 0, 0.01283 at
t = 0.566), so N16 runs with the expansion limit throughout and N32 until t = 4.25. All
runs ended on the time limit with rc = 0 (athena.log), including X N48 whose manifest says
failed: its wrapper died at line 37 with "ena.log | tr '\n' ' '): command not found" after
AthenaK had finished (run.log), and all 41 dumps through t = 10 exist [VERIFIED];
[JUDGEMENT] the script file was edited while bash was still reading it.

Error measures: F: complex amplitude Z = 2i c(K) of h_+ and h_x, exact Z = A exp(-i w t)
(x: times exp(i phi_x)); X: Z = H + i H'/k with H = 2c(K) of h (x: times exp(-i phi_x)),
H' the same of h', exact eps (T + i T'/k). Amplitude error |Z|/|Z_ex| - 1, phase error
arg(Z/Z_ex) (positive = numerical lag), both at the last dump and as the maximum over the
dumps. Diagnostics: TT = Lambda(gt - delta) and Lambda(-2 alpha At); Weyl = Psi_4 along
khat (F: h_+ = -Re Psi4/w^2, h_x = Im Psi4/w^2) and, for X, h, h' inverted from E_+, E_x,
B_+, B_x (h' from B, h from E with calH = -alpha K/3 of the numerical background), each
with spectral and with sixth-order derivatives.

Predictions (numbers from the KO, dispersion and RK4 symbols, P3.x):
- P3.1 (F amplitude, TT): amplitude error negative (loss), -1.2e-4 (N16), -1e-6 (N32),
  ~-6e-8 (N48), ~-3e-8 (N64; there RK4 amplitude loss ~2.4e-8 exceeds KO 7.5e-9); order
  ~7 from 16 to 32, falling toward 5. Same for + and x to better than 1% of the error
  (the TT subspace is invariant under the scheme for k parallel to (1,1,1)).
- P3.2 (F phase, TT): lag 2.6e-4 rad (N16), 1.2e-5 (N32), 2.3e-6 (N48), 7e-7 (N64) at
  t = 4 periods; order between 4 (RK4) and 6 (space), tending to 4.
- P3.3 (F, TT vs Psi_4 spectral): differ by ~(w_num - w)/(2w) ~ 2e-6 at N16, order ~6,
  down to a floor <= 1e-9; with FD6 Weyl the difference is the FD6 truncation of the
  diagnostic, ~5e-5 at N16, order 6.
- P3.4 (X background): |a_num/a - 1| <= 1e-6 at t = 10 for all N [TO VERIFY: the source is
  extrapolated to mid-step, an O(dt^2) error independent of N].
- P3.5 (X amplitude, TT): loss 8e-5 (N16), 7e-7 (N32), 4e-8 (N48), 5e-9 (N64) at t = 10;
  order ~7. Phase lag ~9e-5 rad (N16), ~2e-6 (N32), then order 4-6.
- P3.6 (X, TT vs Weyl): spectral: agree to <= 1e-8 at all N (algebraic equivalence; only
  calH and round-off); FD6: differ by the FD6 truncation ~1e-5 at N16, order 6.
- P3.7 (X plus/cross): identical truncation errors; an asymmetry larger than 10% of the
  error can only come from round-off, which favours x here (ex lives in xz, yz with no
  background, e+ in xx, yy, zz, xy where gt = 1 + h). If the N64 errors are round-off
  limited, x10 reduces the relative errors ~10x and removes the asymmetry; if they are
  truncation limited, x1 and x10 agree to 10% and both polarizations agree to 10%. A
  difference between x1 and x10 that grows with amplitude would mean nonlinearity
  (third order is <= 4e-10 relative at x10, so that would refute my linear picture).
Refutation: errors off by more than a factor 3 from P3.1/P3.2/P3.5, or orders outside
[3, 8], or a TT-Psi4 (spectral) difference above 1e-6 at N >= 32.

## Entry 6 (2026-11-20 18:58 PST): restart after the five-hour cut of 14:35

Second session of this package (fresh context). State found: V1 and V2 complete and
committed (runs B-20261120-222342-8cda367, B-20261120-222822-e26afae), V3 predictions
(entry 5) and the V3 scripts committed (d104209e, 04feb69e); the V3 measurement was never
run: its submit was refused ("5 cores asked, 16 busy in live local runs of B-emd-gw",
scratch/B-emd-gw/tmp/verifier3/v3_submit.log). Nothing uncommitted in this directory. I
did not run `git merge main` (the package brief forbids merge in this shared worktree;
main is ahead only by harness/coord commits). I read the V3 scripts again before running
them; no change. Next: run v3_measure.py (registered, 5 cores), then v3_summary.py.

## Entry 7 (19:06 PST): V3 outcome (runs B-20261121-025826-80973e3 measurement, B-20261121-030121-58fe5dc summary)

Failed attempts on record: B-20261121-025612-ed4a875 (killed by my own 120 s shell timeout
around the foreground local launcher), B-20261121-030110-52ae004 (summary script sorted a
string key with the resolutions; fixed in commit 58fe5dc5). Numbers below are from
`results/v3_summary.json` (copy of the summary run's output); figures `figs/v3_*.png`,
all looked at.

Test F (flat, k = 2 pi (1,1,1), 4 periods, t = 2.3094) [VERIFIED, run B-20261121-030121-58fe5dc]:

| N | amp. error (TT, +) | phase lag (TT, +) | TT vs Psi4 spectral, max over t | TT vs Psi4 FD6, max |
|---|---|---|---|---|
| 16 | -1.41e-4 | 2.53e-4 | 3.19e-6 | 4.13e-5 |
| 32 | -1.72e-6 | 1.22e-5 | 5.08e-8 | 6.60e-7 |
| 48 | -1.57e-7 | 2.27e-6 | 4.44e-9 | 5.82e-8 |
| 64 | -3.09e-8 | 7.07e-7 | 1.02e-9 | 1.05e-8 |

- Orders, amplitude: 6.4 (16-32), 5.9 (32-48), 5.7 (48-64); phase: 4.4, 4.2, 4.05 (RK4 in
  time with dt = h/4 takes over). Cross: identical to 3 digits at N <= 48; at N = 64
  -3.17e-8 against -3.09e-8 (2.6 %, an absolute 4e-16: round-off of 1 + h).
- P3.1 holds within the factor 3 (N32 -1.7e-6 against -1e-6, N48 -1.6e-7 against -6e-8);
  "+ and x equal to 1 % of the error" fails at N = 64 only (2.6 %, round-off).
- P3.2 holds (2.53e-4 / 1.22e-5 / 2.27e-6 / 7.07e-7 against 2.6e-4 / 1.2e-5 / 2.3e-6 / 7e-7).
- P3.3 holds: the spectral Psi4 and TT differ by 3.2e-6 at N16 with order 6.0, 6.0, 5.2
  (floor ~4e-10 at N64); FD6 Weyl differs by its own truncation, 4.1e-5 at N16, order 6.0.
  The TT-Psi4 difference oscillates in time, zero at every half period (it equals my
  'backward fraction' to 3 digits). Interpretation [JUDGEMENT, tested in entry 8]: the data
  are the continuum wave, the discrete scheme's mode has w_sd = w (1 - theta^6/1120), so a
  backward discrete wave of relative size delta/2 is excited; TT measures both, Psi4 along
  +n only the forward one.
- nonTT_frac (non-TT part of gt - delta over the TT part) grows linearly in time to 1.44e-4
  at t = 2.31, the same at every N; the TT part outside +-K is <= 1.3e-9: the mode
  coefficients are not touched. Where it lives: entry 8.

Test X (EdS, k = (pi/2)(1,1,0), t = 0..10) [VERIFIED, same runs]:

| N | amp. error (TT, +) | phase lag (TT, +) | phase lag (TT, x) | TT vs Weyl spectral, max | TT vs Weyl FD6, max |
|---|---|---|---|---|---|
| 16 | -7.05e-5 | 8.30e-5 | 8.30e-5 | 1.91e-8 | 5.13e-5 |
| 32 | +1.32e-6 | 3.09e-6 | 3.06e-6 | 2.23e-8 | 8.20e-7 |
| 48 | +4.23e-7 | 6.48e-7 | 5.88e-7 | 2.41e-8 | 7.22e-8 |
| 64 | +1.38e-7 | 3.85e-7 | 2.76e-7 | 2.30e-8 | 1.66e-8 |
| 64, x10 | +1.40e-7 | 2.89e-7 | 2.79e-7 | 2.31e-8 | 1.68e-8 |

- Background: |a_num/a_ex - 1| <= 5.1e-8 (N16) .. 3.2e-8 (N64), alpha 7e-8, K 3.4e-8; chi
  uniform to 4e-15; Theta <= 3.6e-9. P3.4 (<= 1e-6) holds.
- P3.5 holds at N16 (-7.05e-5 against -8e-5; phase 8.3e-5 against 9e-5) and FAILS from
  N32 on: the amplitude error changes sign (a gain) and converges with order 2.8 (32-48)
  and 3.9 (48-64), not ~7: +1.3e-6 / +4.2e-7 / +1.4e-7 against -7e-7 / -4e-8 / -5e-9.
  The phase lag converges with order 4.8, 3.9, then 1.8 (N48-64, polarization +) or 2.6
  (x). The gain appears once the step is set by the grid (dt = h/4: from t = 1.1 at N64,
  2.1 at N48, 4.2 at N32, never at N16, read from the dump cycles) and is the same for
  both polarizations and both amplitudes [VERIFIED]; that it is a time-integration or
  matter-coupling error rather than a spatial one is my [JUDGEMENT], not tested here.
- P3.6: spectral Weyl and TT agree to 1.9e-8 .. 2.4e-8, independent of N and of the
  amplitude (x10: 2.31e-8): above my 1e-8 by a factor 2.4 (within the factor 3); FD6
  Weyl differs by its truncation, 5.1e-5 at N16 (my 1e-5 was 5x low), order 6.0.
- P3.7 (plus/cross, x1 against x10 at N64): amplitude errors equal for + and x and for x1
  and x10 (1.38e-7 / 1.40e-7 / 1.40e-7 / 1.40e-7): truncation. The phase lag of + at x1
  carries an extra 1.1e-7 rad (3.85e-7 against 2.76e-7 for x); at x10 the asymmetry is
  1.1e-8 rad, ten times smaller in the relative measure, i.e. a fixed absolute error in h
  of ~2e-13 in the components that carry e+ (diagonal and xy, where gt = 1 + h): round-off,
  as predicted, not nonlinearity (that would grow with amplitude). The imaginary
  (sin K.x) part of the + mode shows the same: 1.6e-8 at x1, 1.75e-9 at x10; x: 2.4e-13.
  Asymmetry grows with N (N16: 4e-9, N32 2.4e-8, N48 6e-8, N64 1.1e-7 rad) because the
  number of steps does and the truncation error falls.

## Entry 8 (19:10 PST): predictions for the V3 supplement (scripts/v3_extra.py), before the run

- P3.8 (F): |Z_TT - Z_Psi4,sp| / |Z_ex| = |delta sin(w t)| with delta = w_sd/w - 1 from the
  symbol of the sixth-order second derivative, |delta| = 3.20e-6, 5.09e-8, 4.48e-9, 7.98e-10
  at N = 16..64; the measured maximum within 10 % of |delta| at N <= 48 (N64: plus a
  round-off floor ~4e-10). Refuted if the ratio leaves [0.9, 1.1] at N <= 48.
- P3.9 (X): the TT-Weyl (spectral) difference has the size and the slow time dependence of
  the relative error of calH_num = -alpha K/3 (2-5e-8), at every N. Refuted if it is a
  factor > 3 away from the calH error or follows a different time dependence.
- P3.10 (F, last dump): the non-TT part of gt - delta sits mainly at k = 0 (a secular drift
  of the mean conformal metric, round-off or second order), not at +-K. Refuted if more
  than half of its power is at +-K (then a longitudinal first-order part exists).

## Entry 9 (19:14 PST): outcome of the V3 supplement (run B-20261121-030542-b2e3eff)

[VERIFIED, results/v3_extra.json, figs/v3_F_diag_diff.png, figs/v3_X_diag_diff.png]
- P3.8 holds: max_t |Z_TT - Z_Psi4,sp| / |Z_ex| over |delta_disp| = 0.999 (N16), 0.999 (N32),
  0.992 (N48), 1.28 (N64, where a round-off floor of 4.7e-10 adds); the curve follows
  |delta sin(w t)| with zeros at every half period, both polarizations. So the whole
  difference between the TT and the Psi4 diagnostic of test F is the backward discrete wave
  that the continuum initial data excite (relative size theta^6/1120, theta = 2 pi / N):
  3.2e-6, 5.1e-8, 4.5e-9, 8e-10.
- P3.9 holds: the X difference TT - Weyl (spectral) grows to 1.9-2.4e-8 at t = 10 with the
  zeros of the mode, and lies at 0.6-0.7 of |calH_num/calH - 1| (3.1-3.6e-8) at late times,
  the same at every N and at x10.
- P3.10 holds: 99.9997 % of the non-TT power of gt - delta at t = 2.31 is at k = 0, a
  uniform traceless shear with equal off-diagonal components 6.58e-11 and diagonal ~2e-13,
  i.e. proportional to TF(khat khat) for khat = (1,1,1)/sqrt 3, identical at N16 and N64.
  [JUDGEMENT] the second-order response of the mean metric to the momentum flux of the wave
  (A^2 w t ~ 2.5e-11); not tested (no F run at a second amplitude). It does not enter the
  mode coefficients at K.

## Entry 10 (19:25 PST): read waves/README.md 'Results' and 'Open' (after commits b2e3effe and 483924b9)

Only now read: tracks/B-emd-gw/waves/README.md lines 52-160 (Results, Open). Their measure
for both tests is the forward combination W = P + i P'/|k| at +k (for F my Z_TT used h
alone, which carries the backward discrete wave; for X my Z = H + i H'/k is theirs). To
classify the F claims on their own measure, scripts/v3_classify.py recomputes the forward
combination from my own per-dump numbers and adds my own symbol-plus-RK4 predictor of F.
Predictions before the run:
- C1: forward TT against spectral Psi4 (F) is at the round-off level, 1e-11 .. 1e-10, at
  every N (P3.8 says the whole difference was the backward wave).
- C2: my predictor (sixth-order symbol, KO sigma = 0.5 sum sin^8(theta/2)/h, RK4
  amplification, 148 / ... cycles) reproduces the measured forward amplitude and phase
  errors of F to within 3 % at every N (refuted if any ratio leaves [0.97, 1.03]; at N64
  the amplitude may be off by round-off, ~1e-9 absolute).
- C3: forward ratio Z_x / Z_+ equals 0.5 e^{i} to ~1e-9 in modulus and argument at every N.
