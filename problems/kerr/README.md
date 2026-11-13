# Kerr geodesic references (a = 0.9 M)

Reference trajectories for the single-particle Kerr tests of arXiv:2611.12831 (Sec. "Kerr
geodesics"), produced by the Python library in `python/nrpic/` (`kerr.py`, `geodesic.py`).
The library is independent of the C++ code.

## Regenerate

```
python3 problems/kerr/make_reference.py --workers 4      # ~18 min on 4 cores
python3 python/tests/test_kerr.py                         # or: python3 -m pytest python/tests/test_kerr.py
```

## Files

| file | content |
|---|---|
| `ref/initial_conditions.json` | everything per orbit: initial state in **all three** systems, invariants, turning points, periods, `t_end`, exact final state in all systems, event times, accuracy diagnostics |
| `ref/bl_equatorial_eccentric_bl.npz` | BL trajectory |
| `ref/bl_inclined_bl.npz` | BL trajectory |
| `ref/ks_passage_ks.npz` | spherical Kerr-Schild trajectory |
| `ref/ks_passage_cks.npz` | Cartesian Kerr-Schild trajectory |

npz arrays: `t` (N+1,), `x` (N+1, 3), `u` (N+1, 3) with `t_i = fl(i/100)` (dt_out = 0.01 M) from
0 to `t_end`; `x_end`, `u_end` = exact state at `t_end` (equal to the last row);
`x_end_free_dop853`, `u_end_free_dop853` = a single free-running DOP853 run (for comparison);
`t_anchor`, `x_anchor`, `u_anchor` = exact states every 10 M; scalars `t_end, a, M, E, Lz, Q`,
`system`.  Positions are `(r, theta, phi)` for `bl`/`ks` (phi continuous, not wrapped) and
`(x, y, z)` for `cks`; `u` is the covariant spatial four-velocity `u_i`.

## Python API (python/nrpic)

```python
from nrpic import kerr, geodesic          # with python/ on sys.path
m = kerr.adm(sys, x, a=0.9, M=1.0)       # sys in 'bl','ks','cks'; alpha, beta, gamma, gamma_inv,
                                          # dalpha[i], dbeta[i,j]=d_i beta^j, dgamma[i,j,k]=d_i gamma_jk
t2, x2, u2 = kerr.convert_state(t, x, u, src, dst, a, M)   # also kerr.convert_event(t, x, src, dst)
E, Lz, Q = kerr.invariants(sys, x, u, a, M)
kerr.orbit_periods(E, Lz, Q, a, M)        # turning points, T_r, T_th, frequencies (mpmath quadrature)
orb = kerr.MinoOrbit.from_state(sys, t0, x0, u0, a, M, dps=30)
t_s, x_s, u_s, lam = orb.state_at_time(t, sys)                # exact state (mpf)
tr = geodesic.integrate(sys, x0, u0, t_end, t0=0.0, dt_out=0.01, rtol=1e-13, atol=1e-13,
                        dense_output=False, turning_points=False)   # -> Trajectory (t, x, u, x_end, ...)
geodesic.invariant_history(sys, tr.x, tr.u, a, M, ref=None)  # E, Lz, Q and dE, dLz, dQ histories
```

To compare a BL run with a KS run, transform events, not equal-time slices:
`t_KS, x_KS, u_KS = kerr.convert_state(t_BL, x_BL, u_BL, 'bl', 'ks')`. Then evaluate the KS
trajectory at `t_KS`.

## Conventions

* M = 1, a = 0.9, signature (-,+,+,+). State `(x^i, u_i)` evolved in coordinate time with
  `dx^i/dt = alpha gamma^ij u_j / W - beta^i`,
  `du_i/dt = -W d_i alpha + u_j d_i beta^j - (alpha/2W) u_j u_k d_i gamma^jk`.
* `bl`: Boyer-Lindquist. `ks`: spherical KS, `l = dt + dr - a sin^2(theta) dphi`.
  `cks`: `x + i y = (r + i a) e^{i phi} sin(theta)`, `z = r cos(theta)`.
* `t_KS = t_BL + delta_t(r)`, `phi_KS = phi_BL + delta_phi(r)` with the integration constants
  fixed as
  `delta_t = 2M/(r+ - r-) [r+ ln((r - r+)/M) - r- ln((r - r-)/M)]`,
  `delta_phi = a/(r+ - r-) ln((r - r+)/(r - r-))`.
  Consequently `u_r^KS = u_r^BL + (2 M r E - a L_z)/Delta`; `u_t, u_theta, u_phi` are unchanged.
* `initial_state[sys].t0` is the time of the initial event in that system's clock (0 in the
  orbit's natural system).  A run started in another system at t = 0 must add `t0` (and compare
  in its own clock); the KS passage started in BL has `t0_BL = -delta_t(20)`.
* `theta0 = pi/2` means the double `fl(pi/2) = pi/2 - 6.1e-17`, so the Cartesian `z0` of the KS
  passage is `20 cos(fl(pi/2)) = 1.22e-15` and the equatorial orbit has `Q = 3.7e-32`.
  Setting `z0 = 0` instead changes nothing at the 1e-10 level.

## Method and accuracy

* **Exact solution.** `nrpic.kerr.MinoOrbit` writes the geodesic in Mino time using only the
  first integrals E, L_z, Q, with singularity-free phases `r = p/(1 + e cos chi_r)` and
  `cos(theta) = sqrt(z_-) cos(chi_theta)`. It evaluates t(lambda), phi(lambda), r and theta by
  mpmath quadrature at 30 digits, and inverts t(lambda) by Newton iteration. This solution does
  not use the 3+1 equations, and raising the precision to 40 digits leaves the result unchanged
  to 25 digits.
* **Stored trajectory.** DOP853 on the 3+1 equations (analytic metric derivatives), with
  rtol = atol = 2.5e-14 and max step 0.1 M. The integration restarts from the exact state every
  10 M, and the samples come from the dense output. The step cap makes the dense output as
  accurate as the steps.
* **Turning points and periods** come from quadrature: the roots of R(r) and Theta(theta),
  `T_r = Gamma Lambda_r` and `T_theta = Gamma Lambda_theta`, where Gamma is the Mino-time
  average of dt/dlambda. For the equatorial orbit, T_r is exactly the time between successive
  pericenters. For the inclined orbit, that interval oscillates about T_r by about ±0.02 M.
  The JSON also lists event-detected turning times (dr/dt = 0 on the dense output) and the
  exact pericenter times.

### Orbits

| orbit | invariants (E, L_z, Q) | radial range | e, p | T_r (T_theta) | t_end |
|---|---|---|---|---|---|
| `bl_equatorial_eccentric` | 0.9460319622242687, 3.144275, 0 (3.7e-32) | 6.0000 – 11.6056 | 0.3184, 7.9104 | 227.40141353754 (–) | 4550 = 20.009 T_r |
| `bl_inclined` | 0.94313371908962, 2.9, 1.9411209797170 | 8.0000 – 8.5171, theta in [1.1246, 2.0170] | 0.0313, 8.2505 | 213.57767708314 (163.55156437450) | 3850 = 18.026 T_r |
| `ks_passage` | 0.9973800000000002, 2.4328, 1.974 | r_p = 1.8983272737, r_a = 378.2017 | 0.990011, 3.777693 | 16812.95 (5373.50) | 230 (KS time) |

The KS passage reaches pericenter at t_KS = 98.94834713589 (t_BL = 101.86211008), with theta
in [1.0472, 2.0944]. At t = 230 it is outbound at r = 23.48. The BL orbits both start at
pericenter (r0 = 6 and r0 = 8, u_r = 0). To give the C++ side a common step grid, t_end for the
BL orbits is N·T_r rounded up to a multiple of 10 M.

### Accuracy

The table gives max |error| over all components of `x` and `u`, against the exact
(quadrature) solution.

| file | stored samples (20 random exact checks) | segment end (every 10 M) | free-running DOP853 at t_end (rtol 1e-12 / 1e-13 / 2.5e-14) | max invariant error along stored samples |
|---|---|---|---|---|
| `bl_equatorial_eccentric_bl` | 5.7e-14 | 2.3e-13 (phi ~ 170) | 4.4e-9 / 7.1e-10 / 1.2e-10 | dE/E 4.7e-16, Q (abs) 4e-31 |
| `bl_inclined_bl` | 8.5e-14 | 2.0e-13 | 1.4e-11 / 7.1e-12 / 1.4e-12 | dE/E 4.7e-16, dQ/Q 1.2e-14 |
| `ks_passage_ks` | 1.1e-14 | 1.8e-14 | 1.4e-11 / 1.4e-11 / 3.2e-12 | dE/E 1.1e-15, dQ/Q 6.1e-15 |
| `ks_passage_cks` | 7.1e-15 | 1.2e-14 | 2.1e-7 / 1.8e-8 / 4.1e-9 | dE/E 2.7e-15, dL/L 3.7e-15, dQ/Q 1.1e-14 |

The `final_state` (npz `x_end`, `u_end`) is the exact solution rounded to double. Its accuracy
was cross-checked at 30 and 40 digits. The full per-orbit diagnostics are in
`initial_conditions.json` under `orbits.<name>.accuracy`.

The KS passage is near the separatrix: r3 = 1.850 lies just below r_p = 1.898. At t = 230,
the final state responds to a relative energy error with dr ≈ -2.3e4 dE/E and
dphi ≈ +3.0e4 dE/E, and to a relative Q error with dphi ≈ -1.7e3 dQ/Q. A pusher with
dE/E ~ 1e-8 therefore shows final phase errors of about 3e-4 from the energy error alone.
For the same reason, a single free-running double-precision run in Cartesian KS is accurate
only to about 4e-9 at t = 230, which is why the stored trajectory is restarted from the exact
state.
