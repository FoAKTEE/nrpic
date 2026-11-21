#!/usr/bin/env python3
"""Figure of J4/J4b: cumulative radiated energy of P1 from u = -35 M against retarded time, per
sphere. Left: J4b (record cut at u = 14, FFI omega_0 = 0.2 solid, 0.1 dashed, 0.3 dotted).
Middle: J4 as written (whole record, FFI 0.2). Right: dE/du (FFI 0.2) of J4b and J4 at the four
radii. Shaded: the J4b window [-35, 6]; dashed lines: 12 and 50 (J4's window ends).
Reads <tagB>_junk_curves.npz and <tagA>_junk_curves.npz from the run directory.
Usage: fig_p1_energy.py <dir | -> [--tagB=P1b] [--tagA=P1w50] [--radii=40,48,70,90]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import junk_lib as jl  # noqa: E402


def cum_from(u, dE, u0):
    E = jl.cumulative(u, dE)
    return E - np.interp(u0, u, E)


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    tagB, tagA, radii = "P1b", "P1w50", (40, 48, 70, 90)
    for a in sys.argv[2:]:
        if a.startswith("--tagB="):
            tagB = a[7:]
        elif a.startswith("--tagA="):
            tagA = a[7:]
        elif a.startswith("--radii="):
            radii = tuple(int(x) for x in a[8:].split(","))
    cB = np.load(os.path.join(d, f"{tagB}_junk_curves.npz"))
    cA = np.load(os.path.join(d, f"{tagA}_junk_curves.npz"))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    cols = fs.SERIES
    for i, R in enumerate(radii):
        col = cols[i % len(cols)]
        u = cB[f"R{R}_u"]
        s = u >= -35
        for key, ls in (("ffi0.2", "-"), ("ffi0.1", "--"), ("ffi0.3", ":")):
            E = cum_from(u, cB[f"R{R}_dE_{key}"], -35)
            ax[0].semilogy(u[s], np.maximum(E[s], 1e-12), color=col, lw=1.0, ls=ls,
                           label=f"R = {R}" if key == "ffi0.2" else None)
        uA = cA[f"R{R}_u"]
        sA = (uA >= -35) & (uA <= 120)
        EA = cum_from(uA, cA[f"R{R}_dE_ffi0.2"], -35)
        ax[1].semilogy(uA[sA], np.maximum(EA[sA], 1e-12), color=col, lw=1.0, label=f"R = {R}")
        ax[2].semilogy(u[s], np.maximum(cB[f"R{R}_dE_ffi0.2"][s], 1e-14), color=col, lw=1.0)
        ax[2].semilogy(uA[sA], np.maximum(cA[f"R{R}_dE_ffi0.2"][sA], 1e-14), color=col, lw=0.6,
                       alpha=0.5)
    ax[0].set_title("J4b: record cut at u = 14", fontsize=9)
    ax[1].set_title("J4: whole record", fontsize=9)
    ax[2].set_title("dE/du (thin: whole record)", fontsize=9)
    ax[0].set_ylabel(r"$E(u) = \int_{-35}^{u} \dot E\,du$ [$M$]")
    ax[2].set_ylabel(r"$dE/du$")
    for a in ax:
        a.axvspan(-35, 6, color="grey", alpha=0.15, lw=0)
        for x in (12, 50):
            a.axvline(x, color="k", lw=0.7, ls="--")
        a.set_xlabel(r"$u$ [$M$]")
    ax[0].set_xlim(-40, 16)
    ax[1].set_xlim(-40, 120)
    ax[2].set_xlim(-40, 120)
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_p1_energy")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
