"""T4: the HRNA force in the 3+1 (x^i, u_i) form used by the NRPIC pushers, against hrna.py.

Covariant equation (2404 article.tex:223-235, with the attractive sign of Eq. CoordtEqs):
    dU_mu/dtau = 1/2 d_mu g_ab U^a U^b + a_mu,   a_mu = A_mu + U_mu U^b A_b,
    A_i = -(1/m) d_i Phi (the Newtonian pair acceleration), A_0 = 0.
In coordinate time (dt/dtau = W/alpha):
    dx^i/dt = alpha gamma^ij u_j / W - beta^i
    du_i/dt = [geodesic part of python/nrpic/geodesic.py] + (alpha/W) (A_i + u_i U^j A_j),
    U^j = gamma^jk u_k - W beta^j / alpha.
Integrated with scipy DOP853 using python/nrpic/kerr.py (Cartesian Kerr-Schild), compared with
hrna.py (Eq. CoordtEqs in (x, xdot), own metric) at the same coordinate times.

Run: <venv>/bin/python -I tests/t4_force_31.py <outdir>
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import hrna  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import geodesic, kerr  # noqa: E402


def u_from_v(x, v, a):
    g, gi, dg = np.zeros((4, 4)), np.zeros((4, 4)), np.zeros((3, 4, 4))
    hrna.metric(hrna.COORDS_CKS, x, 1.0, a, g, gi, dg)
    xd = np.array([1.0, *v])
    gam = 1 / math.sqrt(-(xd @ g @ xd))
    return gam * (g[1:, :] @ xd)


def make_rhs(a, m1, m2):
    geo = geodesic.make_rhs("cks", a, 1.0)

    def f(t, y):
        x1, u1, x2, u2 = y[0:3], y[3:6], y[6:9], y[9:12]
        d = x1 - x2
        r12 = np.linalg.norm(d)
        A = (-m2 * d / r12 ** 3, m1 * d / r12 ** 3)
        out = np.empty(12)
        for k, (x, u) in enumerate(((x1, u1), (x2, u2))):
            g6 = geo(t, np.concatenate([x, u]))
            m = kerr.adm("cks", x, a, 1.0)
            U = m.gamma_inv @ u
            W = math.sqrt(1 + u @ U)
            Uc = U - W * m.beta / m.alpha
            Ak = A[k]
            out[6 * k:6 * k + 3] = g6[:3]
            out[6 * k + 3:6 * k + 6] = g6[3:] + m.alpha / W * (Ak + u * (Uc @ Ak))
        return out
    return f


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    res = {}
    curves = {}
    for spin in (0.0, 0.9):
        kw = dict(law="hrna", coords="cks", spin=spin, beta=5.0, phase=1.41, sense=1, r0_rt=5.0,
                  rf_rt=5.0, record=200000)
        o = hrna.run_encounter(**kw)
        t, Y = o["rec_t"], o["rec_y"]
        m1 = m2 = 0.5e-6
        y0 = np.concatenate([Y[0, 0:3], u_from_v(Y[0, 0:3], Y[0, 3:6], spin),
                             Y[0, 6:9], u_from_v(Y[0, 6:9], Y[0, 9:12], spin)])
        sol = solve_ivp(make_rhs(spin, m1, m2), (t[0], t[-1]), y0, method="DOP853", t_eval=t,
                        rtol=1e-12, atol=1e-14)
        Z = sol.y.T
        dx1 = np.linalg.norm(Z[:, 0:3] - Y[:, 0:3], axis=1)
        drel = np.linalg.norm((Z[:, 0:3] - Z[:, 6:9]) - (Y[:, 0:3] - Y[:, 6:9]), axis=1)
        sep = np.linalg.norm(Y[:, 0:3] - Y[:, 6:9], axis=1)
        res[f"a{spin}"] = dict(n=len(t), t_span=float(t[-1]), max_dx1=float(dx1.max()),
                               max_drel_over_a0=float((drel / 1.013).max()),
                               separated=o["separated"], sep_end=float(sep[-1]), nfev_31=int(sol.nfev))
        curves[spin] = (t - o["t_peri"], drel / 1.013, dx1)
    with open(os.path.join(outdir, "t4_force_31.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.9))
    ax = fig.add_axes([0.19, 0.16, 0.77, 0.8])
    for spin, c in ((0.0, fs.PAL["red"]), (0.9, fs.PAL["blue"])):
        tt, dr, dx = curves[spin]
        ax.semilogy(tt, dr + 1e-18, color=c, label=f"relative orbit, $a={spin}$")
        ax.semilogy(tt, dx + 1e-18, color=c, ls="--", lw=1.0, label=f"member 1 position, $a={spin}$")
    ax.set_xlabel(r"$t-t_p\ [GM/c^3]$")
    ax.set_ylabel(r"3+1 form vs CoordtEqs $[a_0$ or $r_g]$")
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(outdir, "t4_force_31"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
