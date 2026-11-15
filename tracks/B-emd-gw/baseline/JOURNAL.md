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
