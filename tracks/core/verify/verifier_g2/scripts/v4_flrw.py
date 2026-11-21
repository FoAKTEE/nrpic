#!/usr/bin/env python3
"""V4: homogeneous dust universe (C3 constraints), against my own Einstein-de Sitter solution.

Gauge of the run: conformal-time lapse d_t alpha = -(1/3) alpha^2 K with alpha(0) = 1,
K(0) = -3 H_0 = -3 (read from the first record), gamma_ij = a^2 delta_ij. Then
d_t a = alpha a H, alpha = a, H = H_0 a^(-3/2), so da/dt = H_0 a^(1/2) and
a(t) = (1 + H_0 t / 2)^2; K = -3 H_0 a^(-3/2); E = 3 H_0^2 / (8 pi) a^(-3);
proper volume V_0 a^3; chi = a^(-2). Columns read by name from the header lines.

usage: v4_flrw.py RUNDIR OUTDIR
"""
import json
import os
import re
import sys

import numpy as np


def read_named(path, pat=r"\[\d+\]=(\S+)"):
    names = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") and "[1]=" in line:
                names = [m.group(1) for m in re.finditer(pat, line)]
                break
    d = np.loadtxt(path, comments="#", ndmin=2)
    return {n: d[:, i] for i, n in enumerate(names)}


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    h = read_named(os.path.join(rd, "flrw.nrpic.hst"))
    c = read_named(os.path.join(rd, "flrw.cstat.hst"))
    u = read_named(os.path.join(rd, "flrw.z4c.user.hst"))
    K0 = c["K_min"][0]
    H0 = -K0 / 3.0
    t = h["time"]
    a = (1 + H0 * t / 2) ** 2
    rel = lambda x, y: np.abs(x / y - 1)
    res = {"H0": float(H0), "E0_expected": 3 * H0 ** 2 / (8 * np.pi), "E0_read": float(c["E_max"][0]),
           "t_last": float(t[-1]), "a_last": float(a[-1]),
           "max_rel_err_lapse": float(rel(h["alpha_probe"], a).max()),
           "max_rel_err_mean_K": float(rel(h["mean_K"], -3 * H0 * a ** -1.5).max()),
           "max_rel_err_proper_volume": float(rel(h["proper_volume"], h["proper_volume"][0] * a ** 3).max()),
           "np_min": int(h["np"].min()), "np_max": int(h["np"].max()),
           "max_identity": float((np.abs(h["int_E"] / h["sum_mW"] - 1)).max()),
           "max_density_spread": float((h["E_max"] / h["E_min"] - 1).max())}
    tc = c["time"]
    ac = (1 + H0 * tc / 2) ** 2
    res["max_rel_err_E_cstat"] = float(rel(c["E_max"], 3 * H0 ** 2 / (8 * np.pi) * ac ** -3).max())
    res["max_rel_err_chi_cstat"] = float(rel(c["chi_max"], ac ** -2).max())
    res["max_H_norm2_userhst"] = float(u["H-norm2"].max())
    res["max_Theta_norm_userhst"] = float(np.abs(u["Theta-norm"]).max())
    res["max_Theta_max_cstat"] = float(np.abs(c["Theta_max"]).max())
    res["max_H_max_cstat"] = float(np.abs(c["H_max"]).max())
    with open(os.path.join(outdir, "v4_flrw.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax = axs[0]
    ax.semilogy(t, np.maximum(rel(h["alpha_probe"], a), 1e-17), color=fs.PAL["blue"], lw=1, label=r"$\alpha$ vs $a$")
    ax.semilogy(t, np.maximum(rel(h["mean_K"], -3 * H0 * a ** -1.5), 1e-17), color=fs.PAL["red"], lw=1, label=r"$\langle K\rangle$")
    ax.semilogy(t, np.maximum(rel(h["proper_volume"], h["proper_volume"][0] * a ** 3), 1e-17), color=fs.PAL["green"], lw=1, label="proper volume")
    ax.set_xlabel(r"$t$ (conformal, $H_0=1$)")
    ax.set_ylabel("relative difference to EdS (own)")
    ax.legend(fontsize=7)
    ax = axs[1]
    ax.semilogy(u["time"], np.maximum(u["H-norm2"], 1e-30), color=fs.PAL["blue"], lw=1, label="H-norm2 (user hst)")
    ax.semilogy(u["time"], np.maximum(np.abs(u["Theta-norm"]), 1e-30), color=fs.PAL["red"], lw=1, label=r"$\Theta$-norm (user hst)")
    ax.semilogy(tc, np.maximum(np.abs(c["H_max"]), 1e-30), color=fs.PAL["green"], lw=1, label="H_max (cstat)")
    ax.set_xlabel(r"$t$")
    ax.set_ylabel("constraint")
    ax.legend(fontsize=7)
    fig.suptitle("V4: homogeneous dust universe against Einstein-de Sitter, run core-20261115-065903-3629622", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v4_flrw"))


if __name__ == "__main__":
    main()
