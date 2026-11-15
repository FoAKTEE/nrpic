#!/usr/bin/env python3
"""V1: monoenergetic (Shapiro-Teukolsky) cluster sequence, written from scratch.

Independent of python/nrpic/st_cluster.py. Closures derived here from f = K delta(E - E0):
with W = E0 e^{-Phi} the local Lorentz factor and q^2 = W^2 - 1, d^3q = 4 pi q W dW, so
rho0 ~ q W^2, rho ~ q W^3, P ~ q^3 W / 3 (each times the same constant). With
y = e^{2(Phi - Phi_s)} and W = 1 at the surface, W = y^{-1/2}, q^2 = 1/y - 1, hence
P_c/rho_c = (1 - y_c)/3 and rho0_c/rho_c = y_c^{1/2}.

Areal-radius structure (G = c = 1, rho_c = 1):
  dm/dr = 4 pi r^2 rho, dm0/dr = 4 pi r^2 rho0 (1 - 2m/r)^{-1/2},
  d ln y/dr = 2 (m + 4 pi r^3 P) / (r (r - 2m)), stop at y = 1.
Output (directory argv[1]): v_mono.json, figs.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, os.path.join(ROOT, "python"))

RTOL, ATOL = 1e-12, 1e-14


def closures(lny, yc):
    """rho, rho0, P for rho_c = 1 as functions of ln y."""
    y = np.exp(lny)
    q2 = max(1.0 / y - 1.0, 0.0)
    q2c = 1.0 / yc - 1.0
    q, qc = np.sqrt(q2), np.sqrt(q2c)
    W, Wc = y ** -0.5, yc ** -0.5
    rho = (q * W ** 3) / (qc * Wc ** 3)
    rho0 = (q * W ** 2) / (qc * Wc ** 3)          # rho0_c/rho_c = 1/W_c
    P = (q ** 3 * W / 3.0) / (qc * Wc ** 3)
    return rho, rho0, P


def model(yc):
    def rhs(r, s):
        m, m0, lny = s
        rho, rho0, P = closures(lny, yc)
        g = 1.0 - 2.0 * m / r
        return [4 * np.pi * r * r * rho,
                4 * np.pi * r * r * rho0 / np.sqrt(g),
                2.0 * (m + 4 * np.pi * r ** 3 * P) / (r * r * g)]

    def surf(r, s):
        return s[2]
    surf.terminal, surf.direction = True, 1

    rho_c, rho0_c, P_c = closures(np.log(yc), yc)
    r0 = 1e-5
    m = 4 * np.pi / 3 * rho_c * r0 ** 3
    s0 = [m, 4 * np.pi / 3 * rho0_c * r0 ** 3,
          np.log(yc) + 4 * np.pi * (rho_c / 3 + P_c) * r0 ** 2]
    sol = solve_ivp(rhs, [r0, 1e3], s0, events=surf, rtol=RTOL, atol=ATOL,
                    method="DOP853", dense_output=False)
    R = sol.t_events[0][0]
    M, M0, _ = sol.y_events[0][0]
    zc = (yc * (1 - 2 * M / R)) ** -0.5 - 1
    # scale-free central quantities in ADM units (M = 1): rho0_c M^2, H_c/M
    H_c = np.sqrt(P_c / (4 * np.pi * rho_c ** 2))
    return dict(yc=yc, R_over_M=R / M, M0_over_M=M0 / M, Eb_over_M0=1 - M / M0, zc=zc,
                rho0c_M2=rho0_c * M * M, Hc_over_M=H_c / M,
                inv_rho0c_Hc=1.0 / (rho0_c * M * M * H_c / M),
                x_s=R / H_c, v_s=M / (H_c * P_c / rho_c))


def lane_emden(n):
    def rhs(x, s):
        th, dth = s
        return [dth, -max(th, 0.0) ** n - 2 * dth / x]

    def ev(x, s):
        return s[0]
    ev.terminal = True
    x0 = 1e-6
    sol = solve_ivp(rhs, [x0, 20], [1 - x0 ** 2 / 6, -x0 / 3], events=ev, rtol=1e-12,
                    atol=1e-14, method="DOP853")
    xi1 = sol.t_events[0][0]
    om = -xi1 ** 2 * sol.y_events[0][0][1]
    return xi1, om


WM = [(0.900, 0.125, 16.4282, 1.019453), (0.819, 0.236, 9.9642, 1.030106),
      (0.605, 0.592, 5.7502, 1.035171), (0.500, 0.817, 5.0758, 1.023830),
      (0.283, 1.504, 4.5846, 0.961732)]   # 2611.12831 main.tex:1024-1028


def main(out):
    os.makedirs(out, exist_ok=True)
    res = {}
    rows = []
    for yc, zc, RM, M0M in WM:
        g = model(yc)
        rows.append(dict(yc=yc, zc_paper=zc, zc=g["zc"], RM_paper=RM, RM=g["R_over_M"],
                         M0M_paper=M0M, M0M=g["M0_over_M"], Eb=g["Eb_over_M0"]))
    res["wu_most_rows"] = rows
    f = lambda y: -model(y)["Eb_over_M0"]
    o = minimize_scalar(f, bounds=(0.62, 0.74), method="bounded",
                        options=dict(xatol=1e-9))
    gmax = model(o.x)
    res["max"] = gmax
    yz = brentq(lambda y: model(y)["Eb_over_M0"], 0.33, 0.45, xtol=1e-10)
    res["zero_yc"] = yz
    for y in (0.756, 0.605):
        res[f"Eb_{y}"] = model(y)["Eb_over_M0"]
    # Newtonian limit: n = 1/2 polytrope
    xi1, om = lane_emden(0.5)
    lim = []
    for eps in (1e-2, 1e-3, 1e-4):
        g = model(1 - eps)
        lim.append(dict(one_minus_yc=eps, x_s=g["x_s"], v_s=g["v_s"]))
    res["newtonian"] = dict(xi1=xi1, omega=om, x_s_limit=np.sqrt(1.5) * xi1,
                            v_s_limit=1.5 ** 1.5 * om, approach=lim)
    # sequence for the figure
    ys = np.concatenate([np.linspace(0.97, 0.30, 135)])
    seq = [model(float(y)) for y in ys]
    res["sequence"] = [dict(yc=s["yc"], zc=s["zc"], Eb=s["Eb_over_M0"], RM=s["R_over_M"])
                       for s in seq]
    with open(os.path.join(out, "v_mono.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.95, wspace=0.3)
    z = np.array([s["zc"] for s in res["sequence"]])
    eb = np.array([s["Eb"] for s in res["sequence"]])
    ax = axs[0]
    ax.plot(z, eb, color=fs.PAL["red"], label="this check")
    for r in rows:
        ax.plot(r["zc_paper"], 1 - 1 / r["M0M_paper"], "o", mfc="none",
                color=fs.PAL["blue"], label="Wu-Most table" if r is rows[0] else None)
    ax.axvline(gmax["zc"], **fs.GUIDE, label=f"max at $y_c$={gmax['yc']:.5f}")
    ax.set_xlabel("$z_c$")
    ax.set_ylabel("$E_b/M_0$")
    ax.legend(loc="lower center")
    ax = axs[1]
    ax.plot([r["yc"] for r in rows], [abs(r["RM"] / r["RM_paper"] - 1) + 1e-12 for r in rows],
            "s-", color=fs.PAL["red"], label="$R/M$")
    ax.plot([r["yc"] for r in rows], [abs(r["M0M"] / r["M0M_paper"] - 1) + 1e-12 for r in rows],
            "o-", color=fs.PAL["yellow"], label="$M_0/M$")
    ax.plot([r["yc"] for r in rows], [abs(r["zc"] - r["zc_paper"]) + 1e-12 for r in rows],
            "^-", color=fs.PAL["green"], label="$z_c$ (absolute)")
    ax.axhline(5e-4, color="k", lw=1.0, ls=":")
    ax.text(0.62, 6e-4, "half a printed unit of $z_c$", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("$y_c$")
    ax.set_ylabel("|this / paper - 1|")
    ax.legend(loc="lower left", ncol=1)
    ax.set_ylim(1e-8, 3e-3)
    fs.save(fig, os.path.join(out, "fig_v1_mono"))
    print(json.dumps(dict(max=gmax, zero=yz, rows=rows, newton=res["newtonian"]),
                     indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NRPIC_RUN_DIR", "."))
