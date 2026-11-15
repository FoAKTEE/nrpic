# JOURNAL of the baseline package (B-emd-gw, B-pre-4 under decision 0010)

Append-only. Predictions are written before the check runs, outcomes after, also when the
prediction fails. Times UTC. Units of the scripts: G = c = 1, horizon entry t_k = 1,
a(t) = (t/t_k)^(2/3), H_k = 2/3, Lagrangian radius R_L = c/H_k = 3/2, patch mass
M = c^3/(2 G H_k) = 3/4 (arXiv:2605.04487 `main_v3.tex` lines 996-1002 and 2149-2156;
arXiv:2403.15126 `pII_GW_Vir_C2_Arx.tex` lines 446-451 and 485).

Sources read for this package (kb-data, untrusted, read only):
- arXiv:2403.15126 v1 (Dalianis & Kouvaris), `pII_GW_Vir_C2_Arx.tex`, lines 150-1693;
- arXiv:2605.04487 v2 (Escriva, Harada, Kohri, Terada, Yoo), `main_v3.tex`, lines 140-3020.

## 2026-11-15T11:44Z  predictions (written before any script of this package ran)

Models. ZA: Zel'dovich axes R_i = a R_L (1 - a lambda_i), lambda = (alpha, beta, gamma)
(2605.04487 lines 2831-2838). Homogeneous-ellipsoid ordinary differential equations for
the semi-axes with the interior shape coefficients A_i (sum 2), started from the
Zel'dovich state at the first-axis turnaround t_turn = (2 alpha)^(-3/2) t_k
(2605.04487 lines 1036-1060):
- model A, "embedded": R_i'' = -(4 pi G/3) rho_b R_i - 2 pi G (rho_p - rho_b) A_i R_i
  (the overdensity rho_p - rho_b inside the current ellipsoid on top of the background;
  the standard isolated-ellipsoid model [BACKGROUND: Icke 1973, White & Silk 1979, not
  fetched]);
- model B, "literal 2605.04487": R_i'' = -(4 pi G/3) rho_b R_i - 2 pi G rho_p A_i R_i
  (its comoving equation with the full particle-particle force of all patch particles,
  lines 290-296, 484-490, 694-695; the background term then acts on top of the full
  patch mass);
- model C, "static, 2403.15126": R_i'' = -2 pi G rho_p A_i R_i (Hubble flow neglected
  after turnaround, lines 609-612).
The cold homogeneous ellipsoid with a linear velocity field is continued through
R_1 = 0 (the affine flow passes through the pancake and stays homogeneous).

T1 (closed-form ZA spectrum). (1a) The prefactor of my derivation of dE/dln(omega) for
Q'''_ii proportional to t^(-1/3) on [t_k, t_col], with R_L = c/H_k and
G M = (3/4) c^3 t_k, equals 32/(135 pi) G M^2 omega / c times
S |E_1/3(i omega t_k) - alpha^-1 E_1/3(i omega t_col)|^2, the formula of 2605.04487
(lines 2896-2918), and the formula of 2403.15126 (lines 903 and 966-970 with its
1/(2 pi) Fourier convention, line 1259) reduces to the same. Symbolic ratio exactly 1.
(1b) A direct Fourier sum of the sampled Q'''_ZA(t) agrees with the closed form (mpmath
E_1/3) to 1e-3 relative for omega below a tenth of the sampling Nyquist frequency, for
the benchmarks (0.2, -0.02, -0.08) (2403.15126 line 990) and (0.11122237, 0.06683367,
0.02194397) (2605.04487 line 2275 and figure names). (1c) Parseval: the integral of
dE/d omega equals the closed-form energy E = (8/15) M c^2 S [(t_2/t_k)^(1/3) -
(t_1/t_k)^(1/3)] to 1e-3 (my derivation; for [t_k, t_col] this is (8/15) M c^2 S
(alpha^(-1/2) - 1)). (1d) The quadrupole formula of 2403.15126 lines 959-961: its
t^(8/3) term equals the one from its own axes (line 485); its t^2 term is larger by
1/alpha than the one from line 485 (hand derivation; irrelevant for Q''' because
d^3 t^2/dt^3 = 0). Refuted if any of (1a)-(1c) misses its tolerance, or if the t^2
terms agree.

T2 (ZA scalings, 2403.15126 lines 1007, 1031, 1074). At fixed ratios of the 2605.04487
benchmark and delta_L = alpha + beta + gamma from 1e-3 to 1e-2: local slopes
d ln E_tot / d ln delta_L = 3.5, d ln omega_peak / d ln delta_L = 1.5 and
d ln (dE/dln omega)_peak / d ln delta_L = 3.5, each within 0.05; departures grow towards
delta_L = 0.3 because the window starts at t_k (the -1 in alpha^(-1/2) - 1). Refuted if
any slope misses by more than 0.05 at delta_L <= 1e-2.

T3 (ellipsoid sanity). A_i from Carlson R_D sum to 2 within 1e-13 and agree with direct
quadrature within 1e-10 for random axes. Sphere (alpha = beta = gamma), models A and C:
collapse at t_c = (1 + 3 pi/(8 sqrt 2)) t_turn = 1.833041 t_turn within 1e-6 relative
(top hat from rest, mass M at R = a_turn R_L / 2), and Q_ij = 0 within 1e-12 M R_L^2.
Refuted otherwise.

T4 (quadrupole derivatives and energy of the ODE). The analytic Q''' of the ODE (jerk
from the force differentiated along the flow) agrees with a five-point stencil of Q(t)
on the dense output within 1e-5 relative to max|Q'''| away from the axis crossings. For
the 2605.04487 benchmark the energy radiated from t_turn to the first crossing in models
A and B exceeds the ZA energy over [t_turn, t_col] by a factor between 1 and 30. Refuted
if the stencil disagrees, or if the ratio is outside [1, 30].

T5 (crossing times against 2605.04487 lines 2277-2279: first-axis shell crossing at
t/t_k = 22.536, y-axis collapse at 29.097, for alpha ~ 0.111, beta ~ 0.0668,
gamma ~ 0.0219, sigma = 0.1, N = 3000, eps_com = 0.05). ZA: x at alpha^(-3/2) = 26.96,
y at beta^(-3/2) = 57.9. Prediction: every ODE model crosses the x axis earlier than ZA;
model B earlier than model A; the paper's 22.536 within 10 percent of model A or model B,
and its 29.097 within 15 percent of the y crossing of the same model. Refuted if neither
A nor B is within 10 percent for x. Side check against 2403.15126 line 680
(Delta t_col = t_col - t_max ~ 1.8 t_max, a time calibration of its N-body runs): model
C (the dynamics that paper states) gives Delta t_col / t_max between 0.5 and 0.9 for its
three benchmarks (0.2, -0.02, -0.08), (0.079, 0.045, 0.036), (0.059, 0, -0.054), well
below 1.8. Refuted if model C gives 1.5 or more.

T6 (exact self-similarity of the Newtonian problem). With the start at t_turn, the only
time scale is t_turn, so at fixed beta/alpha and gamma/alpha the energy radiated until
the first crossing is E = M c^2 (2 alpha)^(7/2) F(beta/alpha, gamma/alpha), the crossing
time is t_turn tau_x, and omega_peak = w / t_turn, in models A, B and C. Scan alpha =
0.01, 0.03, 0.1, 0.3: E (2 alpha)^(-7/2) / (M c^2) and t_x / t_turn constant within
1e-7 relative. Refuted if they vary beyond 1e-6 (a hidden scale or a units fault).

T7 (redshift to today, 2605.04487 lines 1963-2063 with constant g_* = g_*s = 106.75;
2403.15126 lines 1500-1509; 2605.04487 lines 2538-2582). For a fixed dimensionless
source: d ln f_0,peak / d ln M = -1/3, d ln f_0 / d ln T_rh = 1/3, d ln Omega_GW / d ln M
= 2/3, d ln Omega_GW / d ln T_rh = 4/3, exact to 1e-9 with constant g_*. The coefficient
of t_k / t_rh = C (M/M_sun) (T_rh/GeV)^2 at g_* = 106.75 is 21.03 within 0.5 percent
(2605.04487 line 2542) and 1/sqrt(C) = 0.218 (line 2553). Refuted otherwise.

T8 (box size for the code comparison). From the ODE (model A, 2605.04487 benchmark): the
comoving wavelength 2 pi c a(t_e) / omega_peak at the energy-weighted emission time
exceeds the side of the periodic box that holds one patch per smoothing volume,
V_k^(1/3) = (4 pi/3)^(1/3) R_L = 1.612 R_L (2605.04487 lines 2032-2036), and scales as
alpha^(-1/2). Refuted if it is shorter than that side.

## 2026-11-15T11:48Z  one more prediction (before any script ran)

T7b (the numbers of 2403.15126 through the conversion of 2605.04487). 2403.15126 states
for sigma = 0.1 a first peak of the averaged N-body spectrum at omega_e ~ H_k/10 with
<dE/dln omega> ~ 2e-5 in units G = c = H_k = 1 (lines 1487-1491; there M = 1/2 from
t_k = 4GM/3, line 450), emission completed by 3 <t_col> (line 1486), and today
f_peak ~ 4e-9 Hz (M/M_sun)^(-1/3) (T_rh/GeV)^(1/3), Omega_peak ~ 1e-6 sigma^(7/2)
(M/M_sun)^(2/3) (T_rh/GeV)^(4/3) (lines 1500-1509). Its <t_col> ~ 28 is ambiguous
(0.9 sigma^(-3/2) t_k = 28.5 t_k but written "28 H_k^-1", line 1481), so I take the
emission time t_e between 28 t_k and 3 x 42 t_k = 126 t_k. Prediction: the conversion
of T7 gives f_0 within a factor 3 of 4e-9 Hz and Omega_peak within a factor 10 of
1e-6 (0.1)^(7/2) = 3.2e-10 (at M = M_sun, T_rh = 1 GeV) for some t_e in that range.
Refuted if no t_e in the range comes within these factors.

## 2026-11-15T12:00Z  outcomes

Runs. Unregistered smoke runs under `scratch/B-emd-gw/tmp/smoke*` (development only, not
cited) found two faults of the check script, fixed before the registered runs: the
reference quadrature of T3 was inaccurate for elongated axes (relative error ~1 against
R_D; replaced by a quadrature in log u), and sympy's `coeff` needed `t**(8/3)`.
Registered: `B-emd-gw-20261115-115529-58c7f50` (all checks; two figure labels showed
Q'' for Q''', a legend covered curves, the ZA axes were drawn past their collapse, and the
T8 JSON key `box_side_one_patch_per_Vk_over_RL` held the side in units of c t_k, 2.418,
instead of 1.612) and `B-emd-gw-20261115-115752-840e994` (same code with those fixed;
every number identical except that key). Numbers below: the second run,
`results/baseline_results.json`; figures `figs/t*.png`, each inspected.

T1 CONFIRMED. (1a) symbolic ratios mine/2605 = 1 and 2403/2605 = 1. (1b) Fourier sum vs
closed form: max relative difference 6.66e-5 (2403 benchmark) and 6.65e-5 (2605
benchmark) for omega t_k <= 100 (omega/Nyquist <= 6.4e-3); the 2605 formula equals mine to
3e-15. (1c) Parseval 1.0e-4 and 2.1e-4; E[t_k, t_col] = 9.009e-4 and 1.171e-4 M c^2.
(1d) t^(8/3) terms equal; the t^2 term of 2403.15126 lines 959-961 is 1/alpha times the
one from its own axes (line 485): a slip in a term that does not radiate in EdS
(d^3 t^2/dt^3 = 0). Figure `t1_za_spectrum.png`: dots on the line over five decades; the
relative difference grows as omega^2 (trapezoid sum), below 1e-4 at omega t_k = 100.

T2 CONFIRMED. Local slopes for delta_L <= 1e-2 within 0.034 (E_tot), 0.0065 (peak
amplitude) and 0.0013 (omega_peak) of 3.5, 3.5, 1.5. They drift at larger delta_L: E_tot
slope 3.30 at delta_L ~ 0.14 and 2.83 at 0.57; omega_peak slope 1.54 and 1.86. At the
2605 benchmark (delta_L = 0.2): E_tot = 1.17e-4 M c^2, omega_peak t_k = 0.088, peak
dE/dln omega = 4.9e-5 M c^2. Figure `t2_za_scaling.png` (the grey band is the tested
range).

T3 CONFIRMED. |sum A_i - 2| <= 8.9e-16, R_D vs quadrature <= 8.1e-16 over 200 random axes
(1e-3 to 10). Sphere: models A and C reach R = 1e-4 R(t_turn) at 1.8330402 t_turn, the
cycloid at the same radius agrees to 2.1e-15, and the analytic collapse 1.8330406 t_turn
is 1.9e-7 away (the remaining infall from R = 1e-4 R_0); Q <= 4e-16 M R_L^2. Model B (no
prediction): 1.8086 t_turn, 1.3 percent earlier, the background force acting on top of the
full mass. Figure `t3_sphere_and_shape.png`.

T4 PARTLY REFUTED. Stencil: as implemented (points closer than 3h = 6e-3 t_turn to a
crossing excluded) the maximum difference is 4.4e-3 of max|Q'''|: the 1e-5 I predicted
FAILED. The same run measured where the difference sits: farther than 0.2 t_turn from
every crossing it is 4.9e-7 (h = 2e-3 t_turn) and 3.5e-8 (h = 5e-4 t_turn), before the
first crossing 2.3e-7 and 2.7e-8, i.e. it falls as h^2 (truncation of the stencil); within
0.2 t_turn of a crossing it is 6.8e-4 and 3.5e-4 (band 10h to 0.2 t_turn) and 4.6e-3 and
6.0e-4 (band 3h to 10h), also falling with h. So the analytic Q''' and the stencil agree
where the stencil is accurate; near a crossing Q''' changes on a time scale shorter than
my exclusion window (the thin axis enters the force through |R_1|/R_2), and the stencil
needs h much smaller there. Name of cause: stencil truncation, supported by the h
dependence measured in this run, which could have failed. Energies CONFIRMED: radiated from
t_turn to the first x crossing, E/(M c^2) = 5.03e-4 (A), 6.15e-4 (B), 4.91e-4 (C), against
5.15e-5 for ZA on [t_turn, t_col]: ratios 9.78 (A), 11.95 (B), inside [1, 30]. Up to the
first y crossing (formal continuation of the affine flow): 6.3e-3 (A), 7.8e-3 (B),
4.5e-3 (C). Already at t_turn, where R and R' equal the ZA state, P_GW of the ellipsoid is
about three times the ZA value, because the ZA acceleration is not the ellipsoid's own
gravity. Figure `t4_t5_axes_quadrupole_power.png` (bottom: stencil dots on the model A line
away from the cusps; P has a cusp at every crossing, where R_i'' changes sign).

T5 CONFIRMED (main prediction); side check REFUTED. 2605 benchmark, t_turn = 9.532 t_k:
first x crossing ZA 26.96, A 24.25, B 22.77, C 23.85; first y crossing ZA 57.88, A 31.40,
B 29.12, C 32.04. Against the paper's 22.536 and 29.097: A +7.6 and +7.9 percent, B +1.05
and +0.09 percent, C +5.8 and +10.1 percent. With the snapshot-name parameters (0.1114,
0.0667, 0.0219): B 22.73 and 29.13. All models cross before ZA; B before A. Side check:
model C gives Delta t_col / t_max = 2.37, 1.38, 2.62 for the three benchmarks of
2403.15126 (written: 0.5 to 0.9): REFUTED. My estimate took the free fall of the short axis
alone; the other axes are still expanding at the x turnaround (ZA velocity
R_L adot (1 - lambda_i/alpha) > 0) and dilute the patch. The 1.8 of 2403.15126 line 680 lies
inside the model C range and equals the ZA value 2 sqrt 2 - 1 = 1.83; I find no evidence
for a large mis-calibration of its time axis, only a configuration-dependent offset of
-25 to +45 percent [TO VERIFY whether that paper rescales per configuration].
Reading [JUDGEMENT]: model B is the literal content of 2605.04487 (comoving equation with
the background term, lines 290-296, plus the particle-particle force of all patch
particles, lines 484-490, and nothing else outside the patch, line 695), and it matches the
two quoted times to 1 percent; the physically embedded model A is 8 percent later. The
patch carries the full mass of its Lagrangian sphere (lines 1000-1002), so in model B the
background density is counted inside the patch in addition to the patch matter. Counter-
evidence I cannot resolve: the snapshot times of the sigma = 0.01 case of the same shape
(file names, lines 2654-2659, not described as events), divided by its t_turn = 301.4,
are 2.475 and 3.205, between B (2.389, 3.055) and A (2.544, 3.294); Newtonian self-
similarity (T6) makes these ratios independent of sigma if they mark the same events.

T6 CONFIRMED. Over alpha = 0.01 to 0.3 at fixed beta/alpha, gamma/alpha: relative spread
of F = E/[M c^2 (2 alpha)^(7/2)] 2.6e-13 (A), 1.5e-13 (B), 4.8e-14 (C); of t_x/t_turn
5e-16. F = 0.09689 (A), 0.11848 (B), 0.09465 (C); t_x/t_turn = 2.5444 (A), 2.3892 (B),
2.5024 (C). The ZA energy on [t_k, t_col] is not self-similar (F from 0.0305 to 0.0153),
because its window starts at t_k. Figure `t6_self_similarity.png`.

T7 CONFIRMED. Slopes -1/3, 1/3, 2/3, 4/3 with largest local deviation 2.2e-15; t_k/t_rh
coefficient 21.027 (paper 21.03, -1.6e-4); 1/sqrt(C) = 0.2181 (paper 0.218). Figure
`t7_redshift_scalings.png`.
T7b: f_0 CONFIRMED, Omega REFUTED. f_0/(4e-9 Hz) = 2.22, 2.91, 4.61, 6.04 for t_e = 28,
42, 84, 126 t_k (within 3 for t_e <= 42 t_k); h^2 Omega/(3.16e-10) = 144, 188, 299, 392,
far outside the factor 10 (and Omega = h^2 Omega/h^2 makes it larger by about 2). Cause
not identified [TO VERIFY]: the unit of the quoted <dE/dln omega> ~ 2e-5, the
normalisation of the Doroshkevich average over its restricted domain, or the prefactor
of 2403.15126 line 1501. Note: at M = M_sun, T_rh = 1 GeV the patch enters after
reheating (t_k/t_rh = 21), so the prefactor is a formal coefficient of the power law; the
scalings themselves are exact.

T8 CONFIRMED. Comoving wavelength 2 pi c / (a(t_e) omega_peak) at the energy-weighted
emission time, 2605 benchmark: 3.555 R_L (A), 3.329 R_L (B), against the box side
V_k^(1/3) = 1.612 R_L: ratios 2.21 and 2.06. Fitted slope against alpha -0.4999 (A),
-0.5001 (B). omega_peak t_turn = 1.470 (A), 1.631 (B); t_e/t_turn = 2.216 (A), 2.093 (B).
The prediction text wrote the wavelength as 2 pi c a(t_e)/omega_peak, a slip: the comoving
wavelength divides by a. The script computes the correct quantity, which decides; the
slipped formula would give 208 R_L and confirm trivially. Figure `t8_box_and_spectra.png`:
the box fundamental (dotted) lies above the spectral peak in frequency.
