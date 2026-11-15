Linear set: K_xx = 1e-6 sin(2 pi x), N = 64, t = 10. Largest departure of the mode amplitudes (a_s, K_s, h_s, b_c) from the linearized system, over the run, in units of kappa; largest |Theta|/kappa; for the four slicings with a local identity, its largest residual / kappa. Written by analysis/ana_gauge.py.

| case | run id | F (v_L^2) | eigenvalues / k | dev a_s | dev K_s | dev h_s | dev b_c | max Theta | identity |
|---|---|---|---|---|---|---|---|---|---|
| harmonic | B-emd-gw-20261115-113304-0ea0f74 | 1.0000 | +0.000+1.000i, +0.000-1.000i | 4.8e-08 | 1.2e-07 | 3.1e-08 | 4.1e-17 | 3.2e-06 | 3.3e-05 |
| onelog | B-emd-gw-20261115-113321-0ea0f74 | 2.0000 | +0.000+1.414i, +0.000-1.414i | 2.6e-07 | 1.2e-06 | 2.7e-07 | 2.3e-17 | 2.9e-06 | 6.0e-05 |
| conformal | B-emd-gw-20261115-113418-0ea0f74 | 0.3333 | +0.000+0.577i, +0.000-0.577i | 1.7e-08 | 2.7e-07 | 1.2e-07 | 5.0e-17 | 2.8e-06 | 1.3e-05 |
| volume | B-emd-gw-20261115-113517-0ea0f74 | 0.3333 | +0.000+0.577i, +0.000-0.577i | 1.2e-08 | 2.9e-07 | 9.1e-08 | 5.0e-17 | 2.9e-06 | 1.3e-05 |
| kdriver | B-emd-gw-20261115-113548-0ea0f74 | 1.3333 | +0.000+1.155i, +0.000-1.155i | 2.9e-07 | 1.6e-06 | 4.1e-07 | 5.0e-17 | 2.8e-06 | - |
| geodesic | B-emd-gw-20261115-113600-0ea0f74 | 0.0000 | 0 | 1.9e-22 | 1.2e-07 | 5.9e-07 | 6.7e-17 | 2.6e-06 | - |
| onelog_gd | B-emd-gw-20261115-113700-0ea0f74 | 2.0000 | -0.159+1.144i, -0.159-1.144i, +0.000+1.414i, +0.000-1.414i | 2.6e-07 | 1.1e-06 | 6.7e-07 | 3.1e-07 | 2.8e-06 | - |
| conf_gd | B-emd-gw-20261115-113816-0ea0f74 | 0.3333 | -0.000+0.577i, -0.000-0.577i, -0.080+0.997i, -0.080-0.997i | 1.4e-08 | 1.9e-07 | 5.9e-08 | 4.6e-08 | 2.7e-06 | - |
| harm_hs | B-emd-gw-20261115-113850-0ea0f74 | 1.0000 | +0.000+1.000i, +0.000-1.000i, +0.000+1.000i, +0.000-1.000i | 5.6e-08 | 8.1e-08 | 1.6e-08 | 4.8e-09 | 3.2e-06 | - |

Convergence of the Gamma-driver case (1+log, shift_Gamma 1, eta 2) to the linearized system:

| N | run id | dev a_s | dev K_s | dev h_s | dev b_c |
|---|---|---|---|---|---|
| 32 | B-emd-gw-20261115-113615-0ea0f74 | 4.7e-06 | 2.1e-05 | 1.2e-05 | 5.7e-06 |
| 64 | B-emd-gw-20261115-113700-0ea0f74 | 2.6e-07 | 1.1e-06 | 6.7e-07 | 3.1e-07 |
| 128 | B-emd-gw-20261115-113713-0ea0f74 | 1.2e-07 | 6.2e-07 | 2.9e-07 | 1.4e-07 |

Nonlinear set: K_xx = 1.5 sin(2 pi x), N = 128, t = 10.

| case | run id | first non-finite dump | alpha min | alpha max | max d_x alpha (at t) | max Theta | identity residual | max abs(alpha-1) at last finite dump |
|---|---|---|---|---|---|---|---|---|
| harmonic | B-emd-gw-20261115-113859-0ea0f74 | none (t = 10 reached) | 0.7877 | 1.2695 | 1.54 (9.75) | 1.1e-07 | 1.7e-08 | 4.0e-08 |
| onelog | B-emd-gw-20261115-113943-0ea0f74 | none (t = 10 reached) | 0.6910 | 1.3660 | 3.66 (9.00) | 9.7e-04 | 3.0e-05 | 1.6e-01 |
| conformal | B-emd-gw-20261115-114004-0ea0f74 | 2.7500 | 0.7936 | 1.1477 | 10.4 (2.56) | 4.3e+00 | 1.4e-01 | 2.1e-01 |
| volume | B-emd-gw-20261115-114122-0ea0f74 | 2.9375 | 0.7714 | 1.1477 | 13.3 (2.88) | 1.6e+01 | 2.0e-01 | 2.3e-01 |
| kdriver | B-emd-gw-20261115-114143-0ea0f74 | none (t = 10 reached) | 0.7312 | 1.3230 | 2.37 (9.81) | 5.4e-03 | - | 8.1e-02 |
| onelog_gd | B-emd-gw-20261115-114151-0ea0f74 | none (t = 10 reached) | 0.6909 | 1.3659 | 3.72 (9.00) | 2.7e-03 | - | 1.6e-01 |

Conformal-time lapse, kappa = 1.5, resolution dependence:

| N | run id | first non-finite dump | max d_x alpha at t = 1, 1.5, 2 |
|---|---|---|---|
| 64 | B-emd-gw-20261115-115139-42096b9 | 2.7812 | 0.746, 1.963, 3.312 |
| 128 | B-emd-gw-20261115-114004-0ea0f74 | 2.7500 | 0.751, 2.094, 5.446 |
| 256 | B-emd-gw-20261115-115140-42096b9 | none | 0.753, 2.167, 8.290 |
