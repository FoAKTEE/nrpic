"""Verifier of B-emd-gw, claim C3: junk TT of conformally flat data in the matter era.

    python3 v3_junk.py OUTDIR

Mode K = sqrt(2) k, k = 2 pi / 4 (box of four initial Hubble radii, H = 1 at a = 1).
Conformal time tau with a = tau^2/4 (a = 1 at tau = 2, Hc = 2/tau). Equation (weak field,
arXiv:1604.06065 eq. (ij), static source of Einstein-de Sitter):
    h'' + (4/tau) h' + K^2 (h - h_s) = 0,  h(2) = h'(2) = 0,
whose exact solution is h_s + c1 j1(x)/x + c2 y1(x)/x, x = K tau (spherical Bessel
functions; checked here against a numerical integration). The envelope of the
oscillating part is sqrt(c1^2 + c2^2) |h1(x)| / x = sqrt(c1^2 + c2^2) sqrt(1 + 1/x^2)/x^2
and x^2 = 4 K^2 a, so envelope * a -> sqrt(c1^2 + c2^2)/(4 K^2).

Writes OUTDIR/v3_junk.json and OUTDIR/v3_junk.png.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn, spherical_yn

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "..", "python"))
from nrpic import figstyle as fs  # noqa: E402


def u(fun, x, deriv=False):
    """j1(x)/x or y1(x)/x and their x-derivatives."""
    f = fun(1, x)
    if not deriv:
        return f/x
    return fun(1, x, derivative=True)/x - f/x**2


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    K = np.sqrt(2.0)*2*np.pi/4.0
    hs = 1.0
    tau0 = 2.0
    x0 = K*tau0
    M = np.array([[u(spherical_jn, x0), u(spherical_yn, x0)],
                  [u(spherical_jn, x0, True), u(spherical_yn, x0, True)]])
    c1, c2 = np.linalg.solve(M, [-hs, 0.0])
    a = np.logspace(0, np.log10(200.0), 400001)
    tau = 2*np.sqrt(a)
    x = K*tau
    osc = c1*u(spherical_jn, x) + c2*u(spherical_yn, x)
    env_exact = np.hypot(c1, c2)*np.sqrt(1 + 1/x**2)/x**2
    # numerical integration (independent of the Bessel algebra)
    sol = solve_ivp(lambda t, y: [y[1], -4/t*y[1] - K*K*(y[0] - hs)], (tau0, tau[-1]),
                    [0.0, 0.0], t_eval=tau, rtol=1e-11, atol=1e-14, method="DOP853")
    num_dev = float(np.abs(sol.y[0] - hs - osc).max())
    # local maxima of |h - h_s| (as the scope measured it)
    dev = np.abs(osc)
    i = np.where((dev[1:-1] > dev[:-2]) & (dev[1:-1] > dev[2:]))[0] + 1
    ap, ep = a[i], dev[i]
    sel = (ap > 10) & (ap < 100)
    prod = ep[sel]*ap[sel]
    slope = float(np.polyfit(np.log(ap[sel]), np.log(ep[sel]), 1)[0])
    sel_e = (a > 10) & (a < 100)
    prod_e = env_exact[sel_e]*a[sel_e]
    res = {"K": K, "x0": x0, "c1": c1, "c2": c2,
           "max_abs_numerical_minus_bessel": num_dev,
           "maxima_slope_10_100": slope,
           "maxima_envelope_times_a_spread": float(prod.max()/prod.min() - 1),
           "exact_envelope_times_a_spread_10_100": float(prod_e.max()/prod_e.min() - 1),
           "exact_envelope_at_a60_over_hs": float(np.interp(60.0, a, env_exact)),
           "maxima_envelope_at_a60_over_hs": float(np.interp(60.0, ap, ep)),
           "asymptotic_envelope_times_a": float(np.hypot(c1, c2)/(4*K*K)),
           "one_over_a_at_60": 1/60.0}
    with open(os.path.join(out, "v3_junk.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH*1.3, 3.2))
    ax = fig.add_axes([0.16, 0.15, 0.80, 0.78])
    ax.loglog(a, dev, color=fs.PAL["red"], lw=0.6, label=r"$|h-h_s|/h_s$ (Bessel solution)")
    ax.loglog(a[::4000], np.abs(sol.y[0][::4000] - hs), "o", ms=2.5, color=fs.PAL["blue"],
              label="numerical integration")
    ax.loglog(a, env_exact, **fs.GUIDE, label=r"$\sqrt{c_1^2+c_2^2}\,|h^{(1)}_1(x)|/x$")
    ax.axvline(60, **fs.MASK_LINE)
    ax.set_xlabel(r"scale factor $a$")
    ax.set_ylabel(r"oscillating TT part / static part")
    ax.set_xlim(1, 200)
    ax.set_ylim(1e-3, 2)
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, "v3_junk"))


if __name__ == "__main__":
    main()
