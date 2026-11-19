"""Inputs of the predicted errors of the AthenaK test (DESIGN.md section 5).

1. Silent-universe check and linear response: along dust elements of the reference model
   (eps = 0.1), the four silent equations of arXiv:1708.09143 (lines 218-223, kappa = 8 pi,
   Lambda = 0) integrated from the exact initial values reproduce the exact evolution (a
   further check of the solution); then the response of K and rho to a relative error of
   1e-6 in the initial density or in the initial expansion (what a truncation or deposit
   error of the initial data does to one element if gradients are neglected).
2. Gradient scales in the coordinates of the code (the conformally flat coordinates of the
   initial slice, in which the dust stays at rest in geodesic slicing) on the three axes at
   tau = 0, 10, 20, 30, 40: max|K|/max|dK/dx| (K changes sign at turnaround, so a local
   ratio is meaningless) and min rho/|d rho/dx|.
3. Magnitudes the evolution must resolve: K/H and rho/rho_b in the core and on the shell.
Writes error_budget.json and fig_error_budget.

    python3 scripts/run_error_budget.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402

KAPPA = 8 * math.pi
TAUS = (0.0, 10.0, 20.0, 30.0, 40.0)


def silent_rhs(t, y):
    rho, Th, Sg, W = y
    return [-rho * Th,
            -Th * Th / 3 - KAPPA * rho / 2 - 6 * Sg * Sg,
            -2 * Th * Sg / 3 + Sg * Sg - W,
            -Th * W - KAPPA * rho * Sg / 2 - 3 * Sg * W]


def main():
    rdir = common.run_dir("error_budget")
    _, szk = common.models()
    t_i = szk.t_i
    tc = float(szk.crunch_time(np.array([1.0]))[0])
    tau_end = 40.0
    out = dict(run_id=common.run_id(), commit=common.git_commit(), tau_crunch_core=tc - t_i)
    elements = [(1.0, 0.0, "core"), (3.0, 1.0, "r=3,+b"), (3.0, -1.0, "r=3,-b"), (4.2, 1.0, "r=4.2,+b"),
                (4.2, -1.0, "r=4.2,-b"), (5.0, 1.0, "r=5,+b"), (5.4, -1.0, "r=5.4,-b"), (7.0, 0.0, "EdS")]
    tt = t_i + np.linspace(0, tau_end, 401)
    resp = {}
    for r0, sgn, name in elements:
        bb = float(np.linalg.norm(szk.dip.b(np.array([r0]))[0]))
        bn = sgn * bb
        ex = szk.fields(tt, np.full_like(tt, r0), np.full_like(tt, bn))
        y0 = [ex["rho"][0], ex["Theta"][0], ex["Sigma"][0], ex["W"][0]]
        sol = solve_ivp(silent_rhs, (tt[0], tt[-1]), y0, t_eval=tt, rtol=1e-12, atol=1e-30, method="DOP853")
        dev = float(np.max(np.abs(sol.y[1] - ex["Theta"]) / np.abs(ex["Theta"])))
        row = dict(r=r0, bn=bn, silent_vs_exact_Theta_rel_max=dev,
                   silent_vs_exact_rho_rel_max=float(np.max(np.abs(sol.y[0] - ex["rho"]) / ex["rho"])),
                   K_over_H_at_tau=[float(-np.interp(t_i + ta, tt, ex["Theta"]) / szk.H) for ta in TAUS],
                   rho_over_rhob_at_tau=[float(np.interp(t_i + ta, tt, ex["rho"]) / (szk.rho_b * (t_i / (t_i + ta)) ** 2))
                                         for ta in TAUS])
        for lab, idx in (("drho", 0), ("dTheta", 1)):
            yp = list(y0)
            yp[idx] *= 1 + 1e-6
            sp = solve_ivp(silent_rhs, (tt[0], tt[-1]), yp, t_eval=tt, rtol=1e-12, atol=1e-30, method="DOP853")
            aK = np.abs(sp.y[1] - sol.y[1]) / szk.H / 1e-6        # |dK| in units of H_i
            aKrel = np.abs(sp.y[1] - sol.y[1]) / np.abs(sol.y[1]) / 1e-6
            arho = np.abs(sp.y[0] - sol.y[0]) / sol.y[0] / 1e-6
            row[f"{lab}_dK_over_Hi_per_1e-6"] = [float(np.interp(t_i + ta, tt, aK)) for ta in TAUS]
            row[f"{lab}_amplification_K_relative"] = [float(np.interp(t_i + ta, tt, aKrel)) for ta in TAUS]
            row[f"{lab}_amplification_rho"] = [float(np.interp(t_i + ta, tt, arho)) for ta in TAUS]
            resp[name, lab] = (aK, arho)
        out[name] = row
        print(name, row, flush=True)
    # gradient scales in the code's coordinates (labels from the map of the initial slice)
    cm = ConformalMap(szk)
    s = np.linspace(-7.0, 7.0, 2801)
    scales = {}
    for ax in range(3):
        x = np.zeros((len(s), 3))
        x[:, ax] = s
        f0 = cm.fields(x)
        for ta in TAUS:
            f = szk.fields(t_i + ta, f0["r"], f0["bn"])
            for key in ("K", "rho"):
                v = f[key]
                g = np.gradient(v, s)
                if key == "K":      # K changes sign at turnaround: a global scale
                    lsc = np.max(np.abs(v)) / np.max(np.abs(g))
                else:               # rho > 0: the local scale
                    lsc = np.min(np.abs(v) / np.maximum(np.abs(g), 1e-300))
                scales[(ax, ta, key)] = float(lsc)
    out["gradient_scale_min"] = {f"axis{a}_tau{ta:g}_{key}": v for (a, ta, key), v in scales.items()}
    out["gradient_scale_min_all_axes"] = {f"tau{ta:g}_{key}": min(scales[a, ta, key] for a in range(3))
                                          for ta in TAUS for key in ("K", "rho")}
    common.dump(os.path.join(rdir, "error_budget.json"), out)
    print(out["gradient_scale_min_all_axes"])

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.91, wspace=0.28)
    cols = fs.series_colors(len(elements))
    for j, (r0, sgn, name) in enumerate(elements):
        aK, _ = resp[name, "drho"]
        axs[0].semilogy(tt - t_i, np.maximum(aK, 1e-3), color=cols[j], label=name)
        aK2, _ = resp[name, "dTheta"]
        axs[0].semilogy(tt - t_i, np.maximum(aK2, 1e-3), color=cols[j], ls="--")
    axs[0].set_xlabel(r"proper time $\tau$")
    axs[0].set_ylabel(r"$(|\delta K|/H_i)\,/\,10^{-6}$")
    axs[0].set_title(r"solid: $\delta\rho_i/\rho_i = 10^{-6}$; dashed: $\delta\Theta_i/\Theta_i = 10^{-6}$", fontsize=8)
    axs[0].legend(fontsize=6.5, ncol=2, loc="upper left")
    for key, col in (("K", fs.PAL["red"]), ("rho", fs.PAL["blue"])):
        axs[1].semilogy(TAUS, [out["gradient_scale_min_all_axes"][f"tau{ta:g}_{key}"] for ta in TAUS], "o-",
                        color=col, label={"K": r"$\max|K|/\max|\partial K|$",
                                          "rho": r"$\min\,\rho/|\partial\rho|$"}[key])
    axs[1].set_xlabel(r"proper time $\tau$")
    axs[1].set_ylabel("smallest gradient scale (code coordinates)")
    axs[1].legend(loc="lower left")
    common.save_fig(fig, "fig_error_budget", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
