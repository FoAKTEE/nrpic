#!/usr/bin/env python3
"""SC0: self-tests of models.py (journal entry 1). Usage: selftest.py <outdir>"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models as mdl  # noqa: E402


def geodesic_conservation(out):
    """Pair force off (m1 = m2 = 0 in the pair term via alive2 = False): one member on the
    2404 Schwarzschild parabola with r_p = 8 M, from r0 = 25.85 M to 200 M."""
    rp, r0 = 8.0, 25.853
    xc, vc = mdl.cm_state("hrna", rp, r0)
    s0 = np.concatenate([xc, vc, xc + 100.0, vc])     # member 2 dead (frozen far away)
    E0, L0, _ = mdl.invariants("hrna", xc, vc)
    sol = solve_ivp(mdl.rhs_two, (0, 1500.0), s0, method="DOP853", rtol=1e-11, atol=1e-13,
                    args=("hrna", 1.0, 0.05, 0.05, True, False), dense_output=True)
    ts = np.linspace(0, 1500.0, 30001)
    Y = sol.sol(ts)
    Es, Ls, rs = [], [], []
    for k in range(ts.size):
        E, L, _ = mdl.invariants("hrna", Y[0:3, k], Y[3:6, k])
        Es.append(E)
        Ls.append(L)
        rs.append(float(np.linalg.norm(Y[0:3, k])))
    Es, Ls, rs = np.array(Es), np.array(Ls), np.array(rs)
    # pericentre by root of rdot on the dense output
    i = int(np.argmin(rs))
    from scipy.optimize import brentq

    def rdot(tt):
        y = sol.sol(tt)
        return float(y[0:3] @ y[3:6])
    tp = brentq(rdot, ts[i - 1], ts[i + 1], xtol=1e-12)
    rpn = float(np.linalg.norm(sol.sol(tp)[0:3]))
    Lexp = math.sqrt(2 * rp * rp / (rp - 2))
    res = dict(E0=E0, L0=L0, L_expected=Lexp, dE_rel=float(np.max(np.abs(Es - E0)) / E0),
               dL_rel=float(np.max(np.abs(Ls - L0)) / L0), rp_numeric=rpn,
               rp_error=abs(rpn - rp), nfev=int(sol.nfev))
    # azimuth swept: the Schwarzschild parabola sweeps more than 2 pi in total
    ph = np.unwrap(np.arctan2(Y[1], Y[0]))
    res["phi_swept_to_200M"] = float(ph[-1] - ph[0])
    return res, (ts, rs, Es, Ls)


def kepler_conservation():
    rp, r0 = 8.0, 25.853
    xc, vc = mdl.cm_state("newton", rp, r0)
    s0 = np.concatenate([xc, vc, xc + 100.0, vc])
    sol = solve_ivp(mdl.rhs_two, (0, 1500.0), s0, method="DOP853", rtol=1e-11, atol=1e-13,
                    args=("newton", 1.0, 0.05, 0.05, True, False), dense_output=True)
    ts = np.linspace(0, 1500.0, 30001)
    Y = sol.sol(ts)
    eps = 0.5 * np.sum(Y[3:6] ** 2, 0) - 1.0 / np.linalg.norm(Y[0:3], axis=0)
    L = Y[0] * Y[4] - Y[1] * Y[3]
    rmin = float(np.min(np.linalg.norm(Y[0:3], axis=0)))
    return dict(eps0=float(eps[0]), deps_abs=float(np.max(np.abs(eps - eps[0]))),
                dL_rel=float(np.max(np.abs(L - L[0])) / L[0]), rmin=rmin)


def full_conservation():
    s0 = mdl.initial_state("newton_full", 1.0, 0.05, 0.05, 3.0, 8.0, 0.7, 4 * 3.0 * 10 ** (1 / 3))
    m = np.array([1.0, 0.05, 0.05])
    sol = solve_ivp(mdl.rhs_full, (0, 1500.0), s0, method="DOP853", rtol=1e-11, atol=1e-13,
                    args=(m,), dense_output=True)
    ts = np.linspace(0, 1500.0, 15001)
    Y = sol.sol(ts)
    X = Y[:9].reshape(3, 3, -1)
    V = Y[9:].reshape(3, 3, -1)
    K = 0.5 * sum(m[i] * np.sum(V[i] ** 2, 0) for i in range(3))
    U = -sum(m[i] * m[j] / np.linalg.norm(X[i] - X[j], axis=0) for i in range(3) for j in range(i + 1, 3))
    E = K + U
    P = sum(m[i] * V[i] for i in range(3))
    Xb = sum(m[i] * X[i, :, 0] for i in range(3)) / m.sum()
    return dict(E0=float(E[0]), dE_rel=float(np.max(np.abs(E - E[0])) / abs(E[0])),
                P_max=float(np.max(np.abs(P))), barycentre0=Xb.tolist())


def main(out):
    os.makedirs(out, exist_ok=True)
    g, (ts, rs, Es, Ls) = geodesic_conservation(out)
    k = kepler_conservation()
    f = full_conservation()
    res = dict(geodesic=g, kepler=k, full=f)
    res["pass"] = dict(geodesic=g["dE_rel"] < 1e-9 and g["dL_rel"] < 1e-9 and g["rp_error"] < 1e-6,
                       kepler=k["deps_abs"] < 1e-10 and k["dL_rel"] < 1e-10,
                       full=f["dE_rel"] < 1e-9 and f["P_max"] < 1e-12)
    print(json.dumps(res, indent=1))
    json.dump(res, open(os.path.join(out, "selftest.json"), "w"), indent=1)
    sys.path.insert(0, "/data/haiyangw/nrpic/wt/F-hills/python")
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    axs[0].plot(ts, rs, color=fs.PAL["blue"])
    axs[0].axhline(8.0, **fs.MASK_LINE)
    axs[0].set_yscale("log")
    axs[0].set_xlabel(r"$t\,[M]$")
    axs[0].set_ylabel(r"$r\,[M]$")
    axs[0].set_title("HRNA, pair force off: 2404 parabola, $r_p = 8$", fontsize=9)
    axs[1].plot(ts, np.abs(Es / Es[0] - 1) + 1e-17, color=fs.PAL["blue"], label=r"$|E/E_0 - 1|$")
    axs[1].plot(ts, np.abs(Ls / Ls[0] - 1) + 1e-17, color=fs.PAL["red"], label=r"$|L/L_0 - 1|$")
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$t\,[M]$")
    axs[1].legend(frameon=False, fontsize=8)
    axs[1].set_title("conservation of the geodesic invariants", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_sc0_selftest"))


if __name__ == "__main__":
    main(sys.argv[1])
