#!/usr/bin/env python3
"""Figure of J3b/J4: r psi4 (2,0) and (2,2) at each sphere and extrapolated (A of A + B/R)
against retarded time, and the cumulative window energy of the extrapolated waveform for every
method next to the finite radii (FFI 0.2). Reads <tag>_extrap.json and <tag>_extrap_curves.npz.
Usage: fig_extrap.py <dir | -> <tag> [<unit label, default m>]
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
    tag = sys.argv[2]
    unit = sys.argv[3] if len(sys.argv) > 3 else "m"
    res = json.load(open(os.path.join(d, f"{tag}_extrap.json")))
    c = np.load(os.path.join(d, f"{tag}_extrap_curves.npz"))
    radii = res["options"]["radii"]
    u0, u1 = res["options"]["window"]
    u = c["u"]
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    cols = fs.series_colors(len(radii)) if len(radii) > 4 else fs.SERIES
    for R, col in zip(radii, cols):
        ax[0].plot(u, c[f"R{R}_rpsi4_20"].real, color=col, lw=0.9, label=f"R = {R}")
        ax[1].plot(u, c[f"R{R}_rpsi4_22"].real, color=col, lw=0.9)
    ax[0].plot(u, c["A_rpsi4_20"].real, color="k", lw=1.4, label=r"$A$ ($R\to\infty$)")
    ax[1].plot(u, c["A_rpsi4_22"].real, color="k", lw=1.4)
    ax[0].set_ylabel(r"Re $r\psi_4^{20}$")
    ax[1].set_ylabel(r"Re $r\psi_4^{22}$")
    ax[0].legend(frameon=False, fontsize=7)
    styles = {"ffi0.1": ("-", fs.PAL["blue"]), "ffi0.2": ("-", "k"), "ffi0.3": ("-", fs.PAL["yellow"]),
              "td": ("--", fs.PAL["red"])}
    for key, (ls, col) in styles.items():
        if f"A_dE_{key}" not in c:
            continue
        E = jl.cumulative(u, c[f"A_dE_{key}"])
        E = E - np.interp(u0, u, E)
        lab = ("FFI $\\omega_0$=" + key[3:]) if key.startswith("ffi") else "time domain"
        ax[2].plot(u, E, ls=ls, color=col, lw=1.3 if key == "ffi0.2" else 1.0, label=f"$A$: {lab}")
    for R, col in zip(radii, cols):
        E = jl.cumulative(u, c[f"R{R}_dE_ffi0.2"])
        E = E - np.interp(u0, u, E)
        ax[2].plot(u, E, color=col, lw=0.7, ls=":")
    ax[2].set_ylabel(f"$E(u) - E(u_0)$ [{unit}] (dotted: each R, FFI 0.2)")
    ax[2].legend(frameon=False, fontsize=6, loc="upper left")
    for a in ax:
        a.axvspan(u0, u1, color="grey", alpha=0.12, lw=0)
        a.set_xlabel(f"$u = t - R_*$ [{unit}]")
        a.set_xlim(u[0], u[-1])
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, f"fig_{tag}_extrap")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
