#!/usr/bin/env python3
"""Figure of J3: S2g's r psi4 (2,0) and (2,2) and the energy rate (FFI, omega_0 = 0.2) against
retarded time at R = 30, 40, 50 m. Reads single_junk.json and single_junk_curves.npz.
Usage: fig_single_waves.py <dir with the two files, and where the figure goes | -> [<tag> [<unit>]]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    d = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    tag = sys.argv[2] if len(sys.argv) > 2 else "single"
    unit = sys.argv[3] if len(sys.argv) > 3 else "m"
    res = json.load(open(os.path.join(d, f"{tag}_junk.json")))
    c = np.load(os.path.join(d, f"{tag}_junk_curves.npz"))
    xl = (min(c[f"R{r}_u"][0] for r in res["radii"]), max(c[f"R{r}_u"][-1] for r in res["radii"]))
    radii = [int(r) for r in res["radii"]]
    u0, u1 = res["window_u"]
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    cols = fs.series_colors(len(radii)) if len(radii) > 5 else fs.SERIES
    for R, col in zip(radii, cols):
        u = c[f"R{R}_u"]
        ax[0].plot(u, c[f"R{R}_rpsi4_20"].real, color=col, lw=1.1, label=f"R = {R} {unit}")
        ax[1].plot(u, c[f"R{R}_rpsi4_22"].real, color=col, lw=1.1)
        ax[1].plot(u, c[f"R{R}_rpsi4_2m2"].real, color=col, lw=0.8, ls=":")
        ax[2].semilogy(u, np.maximum(c[f"R{R}_dE_ffi0.2"], 1e-14), color=col, lw=1.1)
    for a in ax:
        a.axvspan(u0, u1, color="grey", alpha=0.12, lw=0)
        a.set_xlabel(f"$u = t - R_*$ [{unit}]")
        a.set_xlim(*xl)
    ax[0].set_ylabel(r"Re $r\psi_4^{20}$")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_ylabel(r"Re $r\psi_4^{22}$ (solid), $r\psi_4^{2,-2}$ (dotted)")
    ax[2].set_ylabel(f"$dE/du$ (FFI, $\\omega_0 = 0.2/{unit}$)")
    top = max(float(np.max(c[f"R{R}_dE_ffi0.2"])) for R in radii)
    ax[2].set_ylim(max(1e-14, 1e-5 * top), 3 * top)
    fig.tight_layout()
    for pth in fs.save(fig, os.path.join(d, "fig_single_waves" if tag == "single" else f"fig_{tag}_waves")):
        print("figure:", pth)


if __name__ == "__main__":
    main()
