#!/usr/bin/env python3
"""Figure of J4/J4b: P1's r psi4 against retarded time u = t - R* (M = 1.25) at the four spheres.
Top row: Re and Im of r psi4_22 per radius. Bottom row: |r psi4_lm| of the modes (2,+-2), (2,0),
(2,+-1), (3,+-3), (3,+-1) per radius (log scale). Shaded: the J4b window [-35, 6]; dashed: the ends
12 and 50 of J4's windows; dotted: the record cut of J4b (u = 14).
Reads P1's waveform files (read only) through junk_lib.load_modes.
Usage: fig_p1_waves.py <out | -> <P1 run dir> [--radii=40,48,70,90] [--M=1.25] [--umax=120]
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import junk_lib as jl  # noqa: E402


def main():
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    rd = sys.argv[2]
    radii, M, umax = (40, 48, 70, 90), 1.25, 120.0
    for a in sys.argv[3:]:
        if a.startswith("--radii="):
            radii = tuple(int(x) for x in a[8:].split(","))
        elif a.startswith("--M="):
            M = float(a[4:])
        elif a.startswith("--umax="):
            umax = float(a[7:])
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, len(radii), figsize=(fs.FULL_WIDTH, 4.6), sharex=True)
    groups = [("(2,+-2)", [(2, 2), (2, -2)], fs.PAL["blue"]), ("(2,0)", [(2, 0)], fs.PAL["red"]),
              ("(2,+-1)", [(2, 1), (2, -1)], fs.PAL["yellow"]),
              ("(3,+-3)", [(3, 3), (3, -3)], fs.PAL["green"]),
              ("(3,+-1)", [(3, 1), (3, -1)], fs.PAL["orange"])]
    for j, R in enumerate(radii):
        t, modes = jl.load_modes(rd, R)
        u = t - jl.tortoise(R, M)
        s = u <= umax
        ax[0, j].plot(u[s], modes[(2, 2)].real[s], color=fs.PAL["blue"], lw=0.9, label="Re")
        ax[0, j].plot(u[s], modes[(2, 2)].imag[s], color=fs.PAL["red"], lw=0.9, label="Im")
        for name, ks, col in groups:
            amp = np.sqrt(sum(np.abs(modes[k]) ** 2 for k in ks) / len(ks))
            ax[1, j].semilogy(u[s], np.maximum(amp[s], 1e-12), color=col, lw=0.9, label=name)
        ax[0, j].set_title(f"R = {R} M", fontsize=9)
        for a in ax[:, j]:
            a.axvspan(-35, 6, color="grey", alpha=0.15, lw=0)
            for x in (12, 50):
                a.axvline(x, color="k", lw=0.7, ls="--")
            a.axvline(14, color="k", lw=0.7, ls=":")
            a.set_xlim(max(u[0], -60), umax)
        ax[1, j].set_xlabel(r"$u = t - R_*$ [$M$]")
    ax[0, 0].set_ylabel(r"$r\psi_4^{22}$ [$M^{-1}$]")
    ax[1, 0].set_ylabel(r"$|r\psi_4^{lm}|$ (rms over $\pm m$)")
    ax[0, 0].legend(frameon=False, fontsize=7)
    ax[1, 0].legend(frameon=False, fontsize=6, loc="lower right")
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(out, "fig_p1_waves")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
