#!/usr/bin/env python3
"""Figure of J3: S2g's junk energy, cumulative from the window's start against retarded time
(FFI omega_0 = 0.2 solid, time domain dashed) per radius, and the window energy against 1/R
with the fits E_inf + a/R for every method. Reads single_junk.json and single_junk_curves.npz.
Usage: fig_single_energy.py <dir | ->
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import junk_lib as jl  # noqa: E402


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    res = json.load(open(os.path.join(d, "single_junk.json")))
    c = np.load(os.path.join(d, "single_junk_curves.npz"))
    radii = [int(r) for r in res["radii"]]
    u0, u1 = res["window_u"]
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    for R, col in zip(radii, fs.SERIES):
        u = c[f"R{R}_u"]
        for key, ls in (("ffi0.2", "-"), ("td", "--")):
            E = jl.cumulative(u, c[f"R{R}_dE_{key}"])
            E = E - np.interp(u0, u, E)
            ax[0].plot(u, E, color=col, ls=ls, lw=1.1, label=f"R = {R} m" if key == "ffi0.2" else None)
    ax[0].axvspan(u0, u1, color="grey", alpha=0.12, lw=0)
    ax[0].set_xlim(-40, 55)
    ax[0].set_xlabel(r"$u = t - R_*\ [m]$")
    ax[0].set_ylabel(r"$E(u) - E(u_0)$ [$m$]; solid FFI 0.2, dashed time domain")
    ax[0].legend(frameon=False, fontsize=7, loc="upper left")
    x = 1.0 / np.array(radii, dtype=float)
    xx = np.linspace(0, x.max() * 1.05, 50)
    marks = {"ffi0.1": ("v", fs.PAL["blue"]), "ffi0.2": ("o", fs.PAL["green"]),
             "ffi0.3": ("^", fs.PAL["yellow"]), "td": ("s", fs.PAL["red"])}
    for key, (mk, col) in marks.items():
        E = [res["radii"][str(R)][key]["E"] for R in radii]
        f = res[f"extrap_{key}"]
        lab = ("FFI $\\omega_0$=" + key[3:]) if key.startswith("ffi") else "time domain"
        ax[1].plot(x, E, mk, color=col, ms=5, label=f"{lab}: $E_\\infty$ = {f['E_inf']:.2e}")
        ax[1].plot(xx, f["E_inf"] + f["a"] * xx, color=col, lw=0.9)
    ax[1].set_xlim(0, x.max() * 1.1)
    ax[1].set_ylim(0, None)
    ax[1].set_xlabel(r"$1/R\ [1/m]$")
    ax[1].set_ylabel(r"$E_{\rm junk}/m$ in the window")
    ax[1].legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_single_energy")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
