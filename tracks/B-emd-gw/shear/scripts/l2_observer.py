#!/usr/bin/env python3
"""Where the L2 number of the shearing-dust test stops converging (risk R19): the observer's
metric history and the constraint means of the three series-3 runs (N_y = 32, 64, 128) between
the two arrivals, read from their rays.json (analyze_rays.py).

    python3 l2_observer.py <series 3 run dir> [<out dir>]     (default $NRPIC_RUN_DIR)

Writes l2_observer.json (per N_y: constraint means at t_B and t_A, their largest value before
t_A, the scale factor and h_xy at O at t_B and t_A, and the differences between meshes) and
fig_l2_observer (PDF, PNG).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

NYS = (32, 64, 128)


def main():
    d = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    R = {n: json.load(open(os.path.join(d, f"L2f_n{n}", "rays.json"))) for n in NYS}
    res = {}
    for n, r in R.items():
        cs, ob = r["cstat_series"], r["observer_series"]
        t, ot = np.array(cs["t"]), np.array(ob["t"])
        row = {"t_A": r["t_A"], "t_B": r["t_B"], "Delta": r["Delta"],
               "Delta_no_transport": r["Delta_no_transport"]}
        for key in ("Hr_mean", "Mr_mean"):
            y = np.array(cs[key])
            row[key + "_at_tB"] = float(np.interp(r["t_B"], t, y))
            row[key + "_at_tA"] = float(np.interp(r["t_A"], t, y))
            row[key + "_max_to_tA"] = float(y[t <= r["t_A"]].max())
        for key in ("aO", "hxy", "alpha"):
            y = np.array(ob[key])
            row[key + "_at_tB"] = float(np.interp(r["t_B"], ot, y))
            row[key + "_at_tA"] = float(np.interp(r["t_A"], ot, y))
        res[str(n)] = row
    for k in ("hxy_at_tA", "aO_at_tA", "Hr_mean_at_tA"):
        res["diff_" + k] = [res[str(b)][k] - res[str(a)][k] for a, b in ((32, 64), (64, 128))]
    with open(os.path.join(out, "l2_observer.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.93, wspace=0.42)
    for (n, r), col in zip(R.items(), fs.SERIES):
        cs, ob = r["cstat_series"], r["observer_series"]
        axs[0].semilogy(cs["t"], cs["Hr_mean"], color=col, lw=1.0, label=r"$N_y = %d$" % n)
        axs[0].semilogy(cs["t"], cs["Mr_mean"], color=col, lw=0.8, ls="--")
        axs[1].plot(ob["t"], ob["hxy"], color=col, lw=1.0)
        axs[2].plot(ob["t"], np.array(ob["aO"]), color=col, lw=1.0)
        for ax in axs:
            ax.axvline(r["t_B"], color=col, lw=0.5, ls=":")
            ax.axvline(r["t_A"], color=col, lw=0.5, ls=":")
    axs[0].set_xlabel(r"$t$")
    axs[0].set_ylabel(r"$\langle|H|\rangle_r$ (solid), $\langle|M|\rangle_r$ (dashed)")
    axs[0].legend(fontsize=6.5, loc="lower right")
    axs[1].set_xlabel(r"$t$")
    axs[1].set_ylabel(r"$\gamma_{xy}/a_O^2$ at O")
    axs[2].set_xlabel(r"$t$")
    axs[2].set_ylabel(r"$a_O = \det(\gamma)^{1/6}$ at O")
    fs.save(fig, os.path.join(out, "fig_l2_observer"))
    plt.close(fig)


if __name__ == "__main__":
    main()
