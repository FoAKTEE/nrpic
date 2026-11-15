# JOURNAL of tracks/C-sidm/models (wave 2 helper package "models")

Predictions are written before the registered run of each test; outcomes are appended
below them, also when a prediction fails. Labels: [VERIFIED] computed in a registered run
or read at a source with a locator; [BACKGROUND] standard, not re-derived; [JUDGEMENT];
[TO VERIFY]. Units G = c = 1; models in units of their ADM mass M unless stated.

## 2026-11-15, entry 1: predictions

### Disclosure: smoke check before these predictions

Before writing the predictions below I ran one unregistered smoke check of the
generalised solver `evstatic_b.py` (interactive, not kept): King b = 1 at y0 = 0.314,
0.334032, 0.354 gave E_b, R and Z_c bit-identical to `equilibria/evstatic.py`; the F21
family b = 0.1 at four w0 (2.973, 3.165, 3.587, 4.051) gave Z(0), eps, R/M and M0/M equal
to `gravothermal/tmb.py` to the ten printed digits; the first E_b maximum lay at
y0 = 0.380564 (eps = 0.0351789). Predictions M1 and M2 below are therefore not blind for
these points; the registered run repeats them on the full model set.

### M1. King regression (the generator chain is unchanged)

Prediction: the five King models (y0 = 0.314, 0.324, y_max = 0.334032, 0.344, 0.354)
built by `make_models.py` (equilibria's `make_equilibria.build` with `evstatic_b`,
b = 1.0) at N = 10^4, seed 1, stratified, give `.nrp` and `.tab` files byte-identical to
those of run C-sidm-20261115-120610-b4592be. Refuted by any differing byte.

### M2. F21 family b = 0.1 against the independent solver of the gravothermal package

Prediction: for every b = 0.1 model, Z(0), eps = E_b, R/M and M0/M of `evstatic_b`
(variable y = -ln(1 - b w), Gauss-Jacobi moments) agree with `tmb.solve` (variable w,
Gauss-Legendre) at w0 = (1 - e^{-y0})/b to 1e-8 relative; the first E_b maximum along y0
gives Z(0) = 0.5404 within 1e-6 of criteria.json (0.5404128568, run
C-sidm-20261115-120722-38ab057). Refuted by a larger difference.

### M3. Offline checks of the particle files at N = 10^4 and 10^5

Prediction: every enforced check of `equilibria/check_equilibria.check_model` passes for
the 5 King and 8 b = 0.1 models at both N: matching to Schwarzschild below 1e-12, TOV
residual below 1e-6, Hamiltonian-constraint residual of the table below 1e-6 away from
the edge, rest mass by the isotropic integral to 1e-8, file round trip, table monopole
M = 1 to 1e-12, stratified radial and polar ECDF within 1/N, equal-mass shell counts
exact, max E/E0 <= 1, shell moments within 4.5 standard errors (N = 2e4 resamples), KS
p-values > 1e-3, |sum m W/psi - M| < 1e-3. I expect |sum m W/psi - M| about 2e-4 at
10^4 (the King files of run -120610 have 2.2e-4) and smaller at 10^5 (not enforced).
Risk [JUDGEMENT]: the b = 0.1 models are core-halo (r_core about 2 M, R about 20 M), so
the table resolution (rbar_s/4000, about 5e-3 M) is fine, but the Hamiltonian-constraint
check near the steep core is the most likely failure.

### F1. Fluid onset with the Juttner adiabatic index (b = 0.1)

Prediction:
(a) Pipeline check: variant F21 (gamma = 1 + p/u) reproduces the gravothermal onset
    Z(0) = 0.6348 (w0 = 3.58710) to 1e-4 in Z(0) at N = 600 FEM nodes.
(b) Gamma_1 = 1 + 1/c_v of a Juttner gas falls twice as fast with temperature as the
    perfect-gas 1 + p/u (series: 5/3 - (5/3) theta against 5/3 - (5/6) theta
    [BACKGROUND]); at the centre theta_T = b/(1 - b w0) is about 0.15, so Gamma_1 is about
    1.45-1.50 against F21's gamma(0) = 1.607 at the eps maximum (criteria.json). At the
    eps maximum F21's gamma_cr = 1.568 (criteria.json), above this Gamma_1, so by the
    trial-function criterion the Juttner fluid is already unstable there. I therefore
    predict the J_T onset at Z(0) between 0.30 and 0.5404, i.e. BELOW the collisionless
    E_b maximum (the opposite order from the F21-gamma onset, 0.6348). Refuted if
    Z(0)_J_T >= 0.5404 or < 0.30.
(c) Ordering: Z(0)(J_T) <= Z(0)(J_E), Z(0)(J_p) < Z(0)(J_pu) < Z(0)(F21): the truncated
    distribution is colder than its temperature parameter (theta_E, theta_p < theta_T), so
    Gamma_1 is higher with theta_E or theta_p. Refuted by another order.
(d) Resolution: N = 600 and 1200 roots agree to 1e-3 in Z(0).

### G1-G6. Growth-rate and collapse-time pipeline on the first paper's runs

Runs: `/data/haiyangw/nrpic/runs/st/` (main checkout, read-only). Published numbers:
`paper/sections/tables/tab_outcomes.tex`, tables `tab:outcomes_clusters` and
`tab:outcomes_migration`.

G1. Recovery of the published numbers to their printed digits: first apparent horizon
    t/M 191.0 (y_c = 0.605, `yc0605_v5`), 104.3 (0.500, `yc0500_v5`), 147.2 (0.756
    compressed, `reconf_yc0756_hc`); M_AH/M at the end 1.0000, 1.0001, 0.9970;
    macroparticles left 6, 3, 0; alpha_c at the end 0.051, 0.016; alpha_c(0) = 0.749
    (compressed); first upward crossing of alpha_c = 0.8 at 59 (plain filter) and 88, 86,
    91 (compensated samples 1-3, `dir_yc0500_*`); half-swing growth of the stable
    y_c = 0.819 model 1.3e-5 per M (`ctl/s1_nf4c`, sample 1) and 1.7e-5 (`osc/dx2b`, half
    the cell spacing; the row lists sample 1 first, `make_tables.py` loops over
    s1_nf4c then dx2b). Refuted by any value that differs at the printed precision.
G2. Synthetic signals d(t) = A e^{sigma t} + oscillation + white noise, sigma = 0.02,
    0.05, 0.1 per M, window spanning 2.3 e-folds: the smoothed log-linear fit recovers
    sigma within 3 percent on average over 50 noise realisations, and |fit - truth| < 3 SE
    in at least 90 percent of them. Refuted otherwise.
G3. The three compensated unperturbed y_c = 0.5 samples (same model, other noise) give
    growth rates of alpha_c within 15 percent of their mean. The plain-filter run crosses
    0.8 earlier (59 against 86-91) mainly because it starts with a larger amplitude (its
    deposit is 3e-3 low in E, tab:outcomes_clusters), not because it grows faster:
    sigma_plain within 25 percent of the compensated mean and the extrapolated amplitude
    at t = 0 larger by more than a factor 2. Refuted otherwise.
G4. In the same runs the growth rate of the radius enclosing 10 percent of the rest mass
    agrees with that of alpha_c within 20 percent (one linear mode).
G5. Kicked collapsing runs: sigma(y_c = 0.605) < sigma(y_c = 0.500) (0.605 is closer to
    the threshold y_c = 0.67961, run C-sidm-20261115-115344-eb8b752); the kicked y_c = 0.5
    rate within 30 percent of the unperturbed y_c = 0.5 rate (same mode, opposite sign;
    adaptive against static mesh) [JUDGEMENT]; the lapse collapse time t(alpha_c = 0.2)
    precedes the first apparent horizon by 0 to 6 M in all three collapsing runs.
G6. Fit settings (smoothing 5-20 M, amplitude window (0.003, 0.03) to (0.01, 0.1)) change
    the growth rates of G3 by less than 20 percent.
