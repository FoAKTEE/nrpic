# geodesic_binary: relativistic baseline F-pre-2 (HRNA, arXiv:2404.16270)

Work package F-pre-2 of track F-hills. Status: in progress (this file is rewritten at the end of
the package).

## Driver interface (shared with the Newtonian baseline `tracks/F-hills/newton3`)

Written first so that both drivers use the same names. Units: G = c = 1, the black-hole mass
M = 1, so lengths and times are in r_g = GM/c^2 and GM/c^3, velocities in c.

One encounter is described by these parameters (Python keyword names):

| name | meaning | paper value (2404.16270) |
|---|---|---|
| `law` | `"newton"` (point mass M plus Newtonian pair force), `"hrna"` (exact Schwarzschild/Kerr acceleration plus Newtonian pair force) | both |
| `coords` | coordinates of the HRNA equations: `"sch"` (Schwarzschild, Cartesian form), `"cks"` (Cartesian Kerr-Schild) | `"sch"` |
| `spin` | a/M of the black hole (only with `coords="cks"`) | 0 |
| `mb` | total binary mass m1 + m2, in M | 1e-6 |
| `q12` | m2/m1 | 1 |
| `a0` | initial binary separation (circular binary), in r_g | 1.013 |
| `beta` | penetration factor r_t/r_p, r_t = (M/mb)^(1/3) a0 | 0.1 to 10 |
| `rp` | pericentre distance of the CM orbit, in r_g (alternative to `beta`) | r_t/beta |
| `phase` | initial binary phase (true anomaly), radians from the x axis | [0, pi] |
| `sense` | +1 prograde, -1 retrograde binary rotation relative to the CM orbit | both |
| `r0_rt` | initial CM distance in units of r_t | 50 |
| `rf_rt` | the run stops when the CM distance exceeds this, in units of r_t | 150 |
| `rtol` | relative tolerance of the integrator | not stated |

Every run returns a dictionary with these keys (same meaning in both drivers):

| key | meaning |
|---|---|
| `separated` | True if the binary energy `Eb_end` > 0 at the end |
| `Eb_end`, `eb_end`, `ab_end` | Newtonian specific binary energy, eccentricity, semi-major axis (if bound) at the end |
| `eps1`, `eps2` | specific orbital energy of each member relative to the black hole (relativistic: E - 1 with E = -u_t) |
| `L1`, `L2` | specific angular momentum (z component) of each member |
| `eps_cm` | specific energy of a virtual test particle at the CM (flat-space average) |
| `vinf` | sqrt(2 max(eps1, eps2)), the paper's ejection speed |
| `t_peri` | coordinate time of the CM pericentre |
| `t_s`, `rcm_ts` | time (relative to `t_peri`, in units of T0 = 2 pi sqrt(a0^3/mb)) at which the separation last exceeds 2 a0, and the CM radius then |
| `a_min` | minimum separation during the run, in units of a0 |
| `alpha_max` | maximum of a/R, R = (r/r_g)^(3/2) r_g (paper Eq. 9 consistency parameter) |
| `plunged` | 0 none, 1 or 2: that member crossed r < 2.5 r_g moving inwards (counted as captured by the hole) |

## Requests

(filled at the end of the package)
