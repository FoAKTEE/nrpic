#!/usr/bin/env python3
"""Homogeneous lapse models of the ES dust plateau for ES-1G (es_runs, Track D).

    es1g_model.py [--out DIR] [--T 2.0] [--t_end 200]

The plateau of the ES data is marginally bound dust (Einstein-de Sitter), H(tau) =
H0/(1 + 1.5 H0 tau), H0 = es_model.EinsteinStrausBH(**GEOM).H. With zero shift and the
dust at rest with respect to the normal observers (homogeneous slices), K = -3H(tau) and
d tau/dt = alpha. Two slicings:
  1+log       d_t alpha = -2 alpha K                                   (ES-1, ES-1 entry A2)
  lapse_leak  d_t alpha = -2 alpha K - (alpha/T) max(ln(alpha/alpha0), 0)  (core/gauge READY,
              option 1; alpha0 = 1), whose quasi-stationary value is alpha = exp(6 T H).
Start: alpha = 1, tau = 0 at t = 0 (the precollapsed lapse is 1 in the dust: probe at
x = 46 M of ES-1, run D-20261115-172726-60ba4c2, alpha_probe = 1.0 at t = 0).
Writes DIR/es1g_model.json and DIR/figs/es1g_model.png,pdf. DIR defaults to $NRPIC_RUN_DIR.
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "D-bh-dress", "einstein_straus"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, PKG)
import es_model as em  # noqa: E402
from make_data import GEOM  # noqa: E402

TIMES = (5, 10, 25, 50, 100, 150, 200)


def integrate(H0, T, t_end, n=400001):
    """RK4 in coordinate time for y = (alpha, tau); T = None is plain 1+log."""
    def rhs(y):
        al, tau = y
        H = H0 / (1.0 + 1.5 * H0 * tau)
        d = 6.0 * al * H
        if T is not None:
            d -= (al / T) * max(math.log(al), 0.0)
        return np.array([d, al])
    t = np.linspace(0.0, t_end, n)
    dt = t[1] - t[0]
    Y = np.zeros((n, 2))
    Y[0] = (1.0, 0.0)
    for i in range(n - 1):
        y = Y[i]
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        Y[i + 1] = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return t, Y[:, 0], Y[:, 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--T", type=float, default=2.0)
    ap.add_argument("--t_end", type=float, default=200.0)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    H0 = em.EinsteinStrausBH(**GEOM).H
    res = {"H0": H0, "T": a.T, "models": {}}
    curves = {}
    for name, T in (("1+log", None), ("lapse_leak", a.T)):
        t, al, tau = integrate(H0, T, a.t_end)
        H = H0 / (1.0 + 1.5 * H0 * tau)
        curves[name] = (t, al, tau, H)
        res["models"][name] = {
            f"t={T_:g}": dict(alpha=float(np.interp(T_, t, al)), tau=float(np.interp(T_, t, tau)),
                              K=float(-3.0 * np.interp(T_, t, H)),
                              exp6TH=(float(math.exp(6.0 * a.T * np.interp(T_, t, H))) if T is not None else None))
            for T_ in TIMES}
        res["models"][name]["alpha_max"] = float(al.max())
        res["models"][name]["t_alpha_max"] = float(t[np.argmax(al)])
    # proper time at which the exact references are reached (es_model: wall and group crossing)
    with open(os.path.join(a.out, "es1g_model.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.96, wspace=0.28)
    col = {"1+log": fs.PAL["red"], "lapse_leak": fs.PAL["blue"]}
    for name, (t, al, tau, H) in curves.items():
        lab = name if name == "1+log" else f"lapse_leak, $T={a.T:g}M$"
        axs[0].plot(t, al, color=col[name], label=lab)
        axs[1].plot(t, tau, color=col[name], label=lab)
        if name == "lapse_leak":
            axs[0].plot(t, np.exp(6.0 * a.T * H), **dict(fs.GUIDE, label=r"$e^{6TH}$"))
    axs[0].set_yscale("log")
    axs[0].set_xlabel(r"coordinate time $t/M$")
    axs[0].set_ylabel(r"plateau lapse $\alpha$")
    axs[0].legend(loc="upper left")
    axs[1].plot([0, a.t_end], [0, a.t_end], **fs.MASK_LINE)
    axs[1].set_xlabel(r"coordinate time $t/M$")
    axs[1].set_ylabel(r"dust proper time $\tau/M$")
    axs[1].set_yscale("log")
    axs[1].set_xscale("log")
    fs.save(fig, os.path.join(a.out, "figs", "es1g_model"))
    plt.close(fig)


if __name__ == "__main__":
    main()
