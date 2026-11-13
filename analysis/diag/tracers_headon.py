"""Test particles around a head-on collision of two black holes on the x axis.

    python3 tracers_headon.py <rundir> [--base bbh] [--out NAME]

The spacetime is axisymmetric about the collision axis in any gauge that keeps the
symmetry, so L_x = y u_z - z u_y of every particle is conserved exactly; it is the one
exact invariant of this test. Panels: trajectories projected on the plane normal to the
axis and on the (x, rho) half-plane with the puncture tracks; L_x(t)/L_x(0) - 1; mass of
the common apparent horizon against the total mass.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, parse_cli, read_traj_tagged, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("base", "out"))
label, d = runs[0]
base = opts.get("base", "bbh")
out = opts.get("out", "tracers_headon")
d = run_path(d)
tr = read_traj_tagged(os.path.join(d, base + ".traj.bin"))
co = [np.loadtxt(os.path.join(d, f"{base}.co_{k}.txt")) for k in (0, 1)]
ah = np.loadtxt(os.path.join(d, base + ".horizon_summary_0.txt"))
ah = ah[np.isfinite(ah[:, 2])]
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"], "#7B3FA0", "#17A2B8"]

fs.use_style()
fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
for (tag, q), c in zip(sorted(tr.items()), colors):
    t, x, y, z, ux, uy, uz = q[:, 0], q[:, 2], q[:, 3], q[:, 4], q[:, 5], q[:, 6], q[:, 7]
    rho = np.hypot(y, z)
    Lx = y * uz - z * uy
    ax[0, 0].plot(y, z, color=c, lw=1.0)
    ax[0, 0].plot(y[0], z[0], "o", mfc="none", color=c, ms=5)
    ax[0, 1].plot(x, rho, color=c, lw=1.0, label=f"{int(tag)}")
    ax[0, 1].plot(x[0], rho[0], "o", mfc="none", color=c, ms=5)
    line = f"tag {int(tag)}: t = {t[0]:.2f} .. {t[-1]:.2f} ({len(t)} records), rho {rho[0]:.3f} -> {rho[-1]:.3f}, x {x[0]:+.3f} -> {x[-1]:+.3f}"
    if abs(Lx[0]) > 1e-12:
        dl = Lx / Lx[0] - 1.0
        ax[1, 0].plot(t, dl * 1e4, color=c, lw=1.0)
        i = int(np.argmax(np.abs(dl)))
        line += f"; L_x(0) = {Lx[0]:.6f}, max|dL_x/L_x| = {np.abs(dl).max():.2e} at t = {t[i]:.1f} (rho = {rho[i]:.2f})"
        for T in (40.0, 60.0, 100.0):
            k = t <= T
            if k.any():
                line += f", up to t = {T:.0f}: {np.abs(dl[k]).max():.1e}"
    else:
        line += f"; L_x(0) = 0, max|L_x| = {np.abs(Lx).max():.2e}"
    print(line)
for c_ in co:
    ax[0, 1].plot(c_[:, 2], np.hypot(c_[:, 3], c_[:, 4]), color="k", lw=2.0)
ax[0, 0].set_xlabel(r"$y\,[M]$"); ax[0, 0].set_ylabel(r"$z\,[M]$"); ax[0, 0].set_aspect("equal")
ax[0, 1].set_xlabel(r"$x\,[M]$ (collision axis)"); ax[0, 1].set_ylabel(r"$\rho=(y^2+z^2)^{1/2}\,[M]$")
ax[0, 1].legend(frameon=False, ncol=3, title="tag; black: punctures", loc="upper right")
ax[1, 0].axhline(0.0, color="0.8", lw=1.0)
ax[1, 0].set_xlabel(r"$t\,[M]$"); ax[1, 0].set_ylabel(r"$L_x/L_x(0)-1\ [10^{-4}]$")
if len(ah):
    ax[1, 0].axvline(ah[0, 1], color="0.6", lw=1.0, ls=":")
    ax[1, 1].plot(ah[:, 1], ah[:, 2], color=fs.PAL["red"], label="common apparent horizon")
    print(f"common horizon: first at t = {ah[0, 1]:.2f} (mass {ah[0, 2]:.5f}); "
          + ", ".join(f"t = {T:.0f}: {ah[np.argmin(np.abs(ah[:, 1] - T)), 2]:.5f}" for T in (55, 60, 80, 100, 120, 140, 159) if T <= ah[-1, 1] + 1)
          + f"; rms expansion at the end {ah[-1, 8]:.1e}")
ax[1, 1].axhline(1.0, color=fs.PAL["blue"], lw=1.5, ls="--", label="total mass")
ax[1, 1].set_ylim(0.985, 1.006)
ax[1, 1].set_xlabel(r"$t\,[M]$"); ax[1, 1].set_ylabel(r"horizon mass $[M]$")
ax[1, 1].legend(frameon=False, loc="lower right")
fig.subplots_adjust(left=0.09, right=0.98, top=0.98, bottom=0.08, hspace=0.24, wspace=0.26)
os.makedirs(FIGS, exist_ok=True)
for e in ("pdf", "png"):
    fig.savefig(os.path.join(FIGS, f"{out}.{e}"), dpi=200)
print(os.path.join(FIGS, out + ".png"))
