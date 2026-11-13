# Tracers around an evolved Schwarzschild puncture against exact geodesics

**Setup.**
- Run `runs/puncture/single_v3`: Z4c, 1+log slicing with a Gamma-driver shift, M = 1 puncture from the isotropic time-symmetric slice with a precollapsed lapse, 0-250 M. Static mesh with dx = M/8, M/4, M/2 for max|x^i| < 4, 8, 16 (not M/2-M at r = 6-12). Six massless tracers, recorded every 0.125 M, with the metric reconstructed at the particle by Catmull-Rom interpolation.
- All comparisons use gauge-invariant quantities: proper time tau = integral of alpha/W dt, areal radius R from the tangential metric at the particle, and the azimuth in the orbital plane. The references are exact M = 1 Schwarzschild geodesics built from the initial data. Tag 4 has E = 0.948924118 and L = 3.290613291, and u_r(0) = 0, so it starts at its apocentre R0 = 13.020833.
- The six restart dumps (t = 0, 50, ..., 250) give metric-only checks: the Misner-Sharp mass m, an estimate of the R-reading error (Catmull-Rom against 4- and 6-point Lagrange interpolation of the same cells), and geodesics of the dump mass m(t) started from each tracer's own state at t = 50. To reproduce: `python3 analysis/diag/tracers_exact.py runs/puncture/single_v3 --out tracers_exact_single_v3`, which writes the figure `analysis/diag/figs/tracers_exact_single_v3.png`.

## Numbers

| quantity | value | limited by |
|---|---|---|
| **Metric (dumps)** | | |
| Misner-Sharp m - 1, median over 2.5 < R < 16 | t = 0: -1e-7; 50: +1.47e-3; 100: +1.79e-3; 150: +1.78e-3; 200: +1.80e-3; 250: +1.75e-3 | Evolved metric. At t = 150 and 250 it is constant from R = 1.6 to 16 within 1.5e-4, so this is a Schwarzschild exterior of mass about 1.0018 rather than a local error. It forms between t = 0 and 50, where there is no dump, so where and when it forms is not determined. |
| m - 1 at R = 2 vs apparent-horizon mass - 1 | t = 50-250: m +1.6e-3 to +1.8e-3; M_AH -2.3e-2 to -2.8e-2 (t = 0: m -5e-6, M_AH +3.6e-3) | Horizon finder (FastFlow), not the slice. |
| **R reading and proper time** | | |
| R(0)/R_exact(0) - 1 | tag 0: -5.7e-7; tags 1, 3: -2.1e-6; tags 2, 5: -6.7e-7; tag 4: -2.7e-7 | Interpolation of the initial metric. It equals the Lagrange-Catmull-Rom estimate at t = 0. |
| R-reading estimate at r >= 2 (all dumps, all tags) | <= 2.1e-6 | Interpolation. |
| Jump of R where the particle changes level | <= 7.7e-6 (third difference, about 1e-7 elsewhere) | Interpolation (the source cells change). |
| R-reading estimate at r < 0.5 (last records of tags 4 and 5) | 1e-2 to 4e-2 | Puncture fewer than 4 cells away (dx = M/8). |
| tau, trapezoid - Simpson | <= 1.3e-5 (tags 0-3), 6e-5 (tag 4), 9e-5 (tag 5) | Record spacing; negligible. |
| **Tag 5, radial infall (cycloid)** | | |
| max \|R/R_ex - 1\|, R_ex > 2.2 | 7.2e-4 (at R = 2.20, tau = 39.0, R_num smaller); +3.4e-4 at tau = 30, sign change at tau about 37 | Worldline error, not reading: it grows smoothly, does not jump at the two level changes, and the reading error there is <= 4e-5. Tracer or metric: not determined. The whole fall (t <= 48) lies before the first dump with m != 1. |
| max \|R/R_ex - 1\| down to removal | 8.6e-2 (R = 1.28, r = 0.22, tau = 39.84). At removal (t = 54.125, tau = 39.862): R = 1.357 vs 1.384 | Reading next to the puncture (estimate 1e-2 to 4e-2). R_num rises in 6 of the last records, which an infaller cannot do. |
| **Tag 4, plunge** | | |
| max \|R/R_ex - 1\|, R_ex > 2.2 | 1.14e-1 (tau = 93.8, R_num smaller). Earlier: <= 1.4e-4 to tau = 40, 1.1e-3 at tau = 60, 5.6e-3 at tau = 80 | After t = 50, the evolved mass. From the tracer's state at t = 50 the deviation is 7.0e-2 against M = 1 but 3.0e-3 against m(t). The rest, and everything before t = 50, is not determined. |
| max \|R/R_ex - 1\| down to removal | 3.0e-1 | Reading next to the puncture plus the mass offset. |
| phi(R) - phi_ex(R), R_ex > 2.2 | max 3.2e-2 rad (-3.1e-2 at R = 2.2) | Evolved mass. From t = 50 it is 2.5e-2 rad against M = 1 and 1.1e-3 rad against m(t). |
| phi(tau) - phi_ex(tau) at R_ex = 2.2 | +0.19 rad | Same as above. The tracer reaches R = 2.2 0.28 M earlier in tau. |
| \|L/L0 - 1\| | 1.0e-4 for R > 2.2; 5.9e-3 at removal | Not determined. The large value is next to the puncture. |
| **Circular orbits** (window t = 150-250) | tag 0 / 1 / 2 / 3 (R0 = 7.04167 / 9.03125 / 11.025 / 9.03125, tag 3 inclined 40 deg) | |
| R/R0 - 1, minimum over the run | -2.46e-2 / -1.13e-2 / -8.65e-3 / -1.08e-2 | Evolved mass (next two rows). |
| R/R0 - 1, mean in the window | -2.14e-2 / -9.4e-3 / -8.0e-3 / -8.5e-3 | Evolved mass. |
| From t = 50: max \|R/R_geo - 1\|, M = 1 / m(t) | 2.6e-2 / 8.4e-4; 1.2e-2 / 1.2e-3; 8.3e-3 / 6.9e-4; 1.1e-2 / 3.1e-4 | The m(t) remainder is not determined: m is known only every 50 M, and at t = 200 it varies by 3e-3 over the shell 6 < R < 12. |
| M_eff - m_dump at the particle, t = 150 | +5e-5 / 0 / -5e-5 / +5e-5 (up to 3e-4, 6e-4, 9e-4 at t = 50, 100, 200) | The dumps at t = 50, 100, 200 are not quiet. M_eff is a 20 M Savitzky-Golay average; the dump is a single instant. |
| Omega_t / Omega_Kepler(R0) - 1 | +3.59e-2 / +1.67e-2 / +1.46e-2 / +1.50e-2 | The radius offset. The Killing-time caveat is small: see the next three rows. |
| dalpha/dt, dR/dt at the particle (window fit) | +1.9e-5, +7.6e-4 / +8.4e-6, +6.0e-4 / +1.6e-7, +2.7e-5 / +9.4e-6, +6.8e-4 | dR/dt is the radial oscillation of the orbit, not the gauge. |
| c_K - 1 = ((alpha^2 - beta^2)/(1 - 2M/R))^1/2 - 1, window mean | -1.9e-4 / -1.2e-4 / -8.7e-5 / -1.3e-4 (+1e-4 to +2e-4 with m in place of M = 1) | Gauge: normalisation of d/dt against the Killing vector. |
| d_t R at fixed x at the particle, dump t = 250 | -1.1e-3 / -1.3e-3 / -1.4e-3 / -1.3e-3 | Gauge: the coordinates still drift inward. |
| Omega_tau / exact(R0) - 1 | +4.56e-2 / +1.98e-2 / +1.66e-2 / +1.78e-2 | The radius offset. L0/R^2 with the measured R gives the same values to 1e-8 / 2e-5 / 7e-5 / 1e-5. |
| \|L/L0 - 1\| max; plane tilt (tag 3) | 1.1e-4 / 2.4e-4 / 3.9e-4 / 2.3e-4; 0.004 deg | Not determined. |

## Reading

- The circular orbits do not keep R0 because the evolved spacetime around them has mass m = 1.0018, not 1. With the conserved L, each tracer starts at the apocentre of an orbit around the shifted circular radius and oscillates radially with an amplitude about equal to the shift. The effective mass that makes each tracer's radial acceleration geodesic matches the dump mass to 5e-5 at the quiet dump (t = 150). From t = 50 on, the geodesics of m(t) reproduce R to <= 1.2e-3, against <= 2.6e-2 for M = 1. So after the transient, the tracers follow geodesics of the numerical metric, and the R and frequency errors measure that metric, not the pusher.
- Before t = 50 the two cannot be separated: no dump exists between t = 0 and 50, and the tracers' M_eff overshoots to +2.3e-3 to +3.5e-3 at t of about 30-35. This covers all of tag 5 outside the horizon.
- Inside R of about 1.8 M (r < 1, a few cells of size M/8 from the puncture), reading R dominates.
