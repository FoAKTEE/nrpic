"""Constraint norms and number of MeshBlocks against time for coupled particle + Z4c
runs (dust collapse by default, any basename with --base).

    python3 os_constraints.py <label>=<rundir> [...] [--base os] [--out NAME]

Plotted norms are the square roots of the AthenaK history columns H-norm2 and
M-norm2, i.e. (int H^2 sqrt(gamma) d^3x)^(1/2) and (int M_i M^i sqrt(gamma) d^3x)^(1/2)
over the cells with chi above the Z4c excision threshold (not divided by the volume).
Exact zeros (||M|| = 0 at t = 0 for time-symmetric data) are not drawn.
A dotted vertical line in the run's colour marks its first apparent horizon.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, H, parse_cli, read_athena_hst, read_horizon, read_nrpic_hst, \
    run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("base", "out"))
base = opts.get("base", "os")
out = opts.get("out", "os_constraints")
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]

fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.8))
hs, gap, b = 1.36, 0.05, 0.45
axes = [fs.inch_axes(fig, 0.78, b + (2 - i) * (hs + gap), 7.1, hs) for i in range(3)]
tmax = 0.0
for (label, d), c in zip(runs, colors):
    z = read_athena_hst(run_path(d, f"{base}.z4c.user.hst"))
    hp = run_path(d, f"{base}.nrpic.hst")
    if not z and not os.path.exists(hp):
        print(f"{label}: no history files in {d} yet, skipped")
        continue
    if z:
        t = z["time"]
        Hn, Mn = np.sqrt(z["H-norm2"]), np.sqrt(z["M-norm2"])
        # exact zeros (M at t = 0 for time-symmetric data) are left out of the log axis
        axes[0].plot(t[Hn > 0], Hn[Hn > 0], color=c, label=label)
        axes[1].plot(t[Mn > 0], Mn[Mn > 0], color=c, label=label)
        tmax = max(tmax, t[-1])
        print(f"{label}: z4c history t = {t[0]:.2f} .. {t[-1]:.2f} ({len(t)} rows); "
              f"||H|| at t=0 {Hn[0]:.3e}, max {Hn.max():.3e} at t = {t[np.argmax(Hn)]:.2f}"
              f", final {Hn[-1]:.3e}; ||M|| max {Mn.max():.3e} at t = "
              f"{t[np.argmax(Mn)]:.2f}, final {Mn[-1]:.3e}")
    else:
        print(f"{label}: no {base}.z4c.user.hst")
    if os.path.exists(hp):
        h = read_nrpic_hst(hp)
        axes[2].plot(h[:, H["time"]], h[:, H["nmb"]], color=c, label=label,
                     drawstyle="steps-post")
        tmax = max(tmax, h[-1, H["time"]])
        nmb = h[:, H["nmb"]]
        ch = np.nonzero(np.diff(nmb))[0]
        print(f"   MeshBlocks {nmb[0]:.0f} -> {nmb[-1]:.0f}; changes at t = "
              + ", ".join(f"{h[i + 1, 0]:.2f} ({nmb[i]:.0f}->{nmb[i + 1]:.0f})" for i in ch))
    ah = read_horizon(run_path(d, f"{base}.horizon_summary_0.txt"))
    if len(ah):
        for ax in axes:
            ax.axvline(ah[0, 0], color=c, lw=1.0, ls=":")
        print(f"   first apparent horizon at t = {ah[0, 0]:.3f}")

for ax in axes[:2]:
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
for ax in axes:
    ax.set_xlim(0, tmax)
    ax.yaxis.set_label_coords(-0.075, 0.5)
axes[0].set_ylabel(r"$\|H\|$")
axes[1].set_ylabel(r"$\|M\|$")
axes[2].set_ylabel(r"MeshBlocks")
axes[2].set_xlabel(r"$t\,[M]$", labelpad=-2)
axes[0].legend(loc="lower right", ncol=3)
axes[2].legend(handles=[matplotlib.lines.Line2D([], [], color="k", lw=1.0, ls=":",
                                                 label="first apparent horizon")],
               loc="upper left")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
