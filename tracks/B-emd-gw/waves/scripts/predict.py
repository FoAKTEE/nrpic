#!/usr/bin/env python3
"""Predictions of tests F and X from the Fourier symbol of the code's operators
(wlib/predict.py), written before the runs: amplitude and phase errors of the forward
combination W = P + i P'/|k| at the output times, at N = 16, 32, 64, and the error of the
order-6 Weyl evaluation relative to the spectral one (the symbol of gw_diag's stencils).

    python3 predict.py        (through nrpic-run; writes $NRPIC_RUN_DIR/predictions.json,
                               predictions.png, copies to ../results and ../figs)
"""
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import WT, PKG  # noqa: E402
from wlib import predict as pr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

NS = (16, 32, 64)
FLAT = dict(kvec=2 * np.pi * np.array([1.0, 1.0, 1.0]), L=(1.0, 1.0, 1.0),
            tlim=4.0 / np.sqrt(3.0), dt_out=1.0 / (8 * np.sqrt(3.0)))
EXP = dict(kvec=2 * np.pi / 4.0 * np.array([1.0, 1.0, 0.0]), L=(4.0, 4.0, 4.0),
           tlim=10.0, dt_out=0.25)

# FD stencils of gw_diag (weyl.py FD1, FD2 at order 6) = those of AthenaK with nghost 4
C1 = [(1, 3 / 4), (2, -3 / 20), (3, 1 / 60)]
C2 = (-49 / 18, [(1, 3 / 2), (2, -3 / 20), (3, 1 / 90)])


def weyl_fd_error(kvec, dx):
    """relative symbol errors of the order-6 first and second derivatives along the wave
    (first: sum_i k_i s1(theta_i) / |k|^2 - 1 weighted; second: Laplacian)."""
    kvec = np.asarray(kvec, float)
    th = kvec * dx
    s1 = np.array([2 * sum(c * np.sin(m * t) for m, c in C1) / dx for t in th])
    s2 = np.array([(C2[0] + 2 * sum(c * np.cos(m * t) for m, c in C2[1])) / dx ** 2 for t in th])
    kk = np.sum(kvec ** 2)
    e1 = np.sum(kvec * s1) / kk - 1.0
    e2 = -np.sum(s2) / kk - 1.0
    return e1, e2


def main():
    out = os.environ.get("NRPIC_RUN_DIR", os.path.join(WT, "..", "..", "scratch", "B-emd-gw", "tmp"))
    os.makedirs(out, exist_ok=True)
    res = {"flat": {}, "expanding": {}}
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.95, wspace=0.28, hspace=0.32)
    for col, (name, cfg, fun) in enumerate((("flat", FLAT, pr.predict_flat),
                                            ("expanding", EXP, pr.predict_flrw))):
        for i, N in enumerate(NS):
            p = fun(cfg["kvec"], cfg["L"], (N, N, N), cfg["tlim"], cfg["dt_out"])
            amp = np.abs(p["ratio"]) - 1
            ph = np.angle(p["ratio"])
            dx = cfg["L"][0] / N
            e1, e2 = weyl_fd_error(cfg["kvec"], dx)
            res[name][str(N)] = {
                "nsteps": p["nsteps"], "w_h/k-1": float(p["w_h/k-1"]), "ko_rate": float(p["ko_rate"]),
                "amp_end": float(amp[-1]), "phase_end": float(ph[-1]),
                "amp_maxabs": float(np.max(np.abs(amp))), "phase_maxabs": float(np.max(np.abs(ph))),
                "t_end": float(p["t"][-1]), "n_out": int(len(p["t"])),
                "weyl_fd6_rel_d1": float(e1), "weyl_fd6_rel_d2": float(e2)}
            c = fs.SERIES[i]
            axs[0, col].semilogy(p["t"], np.abs(amp) + 1e-18, color=c, label=f"N = {N}")
            axs[1, col].semilogy(p["t"], np.abs(ph) + 1e-18, color=c, label=f"N = {N}")
        for key in ("amp_end", "phase_end"):
            v = [res[name][str(N)][key] for N in NS]
            res[name]["order_" + key] = [float(np.log2(abs(v[i] / v[i + 1]))) for i in range(len(v) - 1)]
        axs[0, col].set_title("flat, k = 2π(1,1,1)" if name == "flat" else
                              "expanding, k = (π/2)(1,1,0)")
        axs[0, col].set_ylabel("|amplitude error| of W")
        axs[1, col].set_ylabel("|phase error| of W (rad)")
        axs[1, col].set_xlabel("t")
        axs[0, col].legend(loc="lower right", ncol=1)
    fig.savefig(os.path.join(out, "predictions.png"))
    fig.savefig(os.path.join(out, "predictions.pdf"))
    with open(os.path.join(out, "predictions.json"), "w") as f:
        json.dump(res, f, indent=1)
    shutil.copy(os.path.join(out, "predictions.json"), os.path.join(PKG, "results", "predictions.json"))
    shutil.copy(os.path.join(out, "predictions.png"), os.path.join(PKG, "figs", "predictions.png"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
