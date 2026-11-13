"""Dust collapse: central lapse and density against the analytic solution, particle
bookkeeping, and apparent-horizon mass.

    python3 os_history.py <label>=<rundir> [<label>=<rundir> ...] [--out NAME]
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, H, read_horizon, read_nrpic_hst
from nrpic import figstyle as fs
from nrpic import oppenheimer_snyder as osn

args = [a for a in sys.argv[1:] if not a.startswith("--")]
out = "os_history"
if "--out" in sys.argv:
    out = sys.argv[sys.argv.index("--out") + 1]
    args = [a for a in args if a != out]
runs = [a.split("=", 1) for a in args]
# runs without output yet (queued, or not started) are reported and skipped
for label, d in list(runs):
    if not os.path.exists(os.path.join(d, "os.nrpic.hst")):
        print(f"{label}: no {os.path.join(d, 'os.nrpic.hst')} yet, skipped")
        runs.remove([label, d])

fs.use_style()
fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.4))
fig.subplots_adjust(left=0.08, right=0.985, bottom=0.085, top=0.985, wspace=0.24,
                    hspace=0.22)
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
E0 = osn.rho0()
tau_max = 0.0
for (label, d), c in zip(runs, colors):
    h = read_nrpic_hst(os.path.join(d, "os.nrpic.hst"))
    t, tau = h[:, H["time"]], h[:, H["tau_probe"]]
    has = h[:, H["np"]] > 0
    tau_max = max(tau_max, tau[-1])
    axes[0, 0].plot(tau, h[:, H["alpha_probe"]], color=c, label=label)
    axes[0, 1].plot(tau[has], h[has, H["e_probe"]] / E0, color=c, label=label)
    axes[1, 0].plot(t, h[:, H["sum_m"]], color=c, label=label)
    axes[1, 0].plot(t, h[:, H["m_excised"]], color=c, ls="--")
    ah = read_horizon(os.path.join(d, "os.horizon_summary_0.txt"))
    if len(ah):
        axes[1, 1].plot(ah[:, 0], ah[:, 1], color=c, label=label)

tt = np.linspace(0.0, min(tau_max, 0.995 * osn.collapse_time()), 600)
aLL = np.array([float(osn.staley_lower_bound(x)) for x in tt])
axes[0, 0].plot(tt, aLL, **fs.GUIDE, label="lapse bound", zorder=5)
axes[0, 1].plot(tt, np.array([float(osn.cycloid_rho(x)) for x in tt]) / E0, **fs.GUIDE,
                label="cycloid", zorder=5)
axes[0, 0].set_ylim(-0.05, 1.05)
axes[0, 0].set_xlabel(r"$\tau_c\,[M]$")
axes[0, 0].set_ylabel(r"$\alpha_c$")
axes[0, 0].legend(loc="lower left")
axes[0, 1].set_yscale("log")
axes[0, 1].set_xlabel(r"$\tau_c\,[M]$")
axes[0, 1].set_ylabel(r"$E_c/E_0$")
axes[0, 1].legend(loc="upper left")
axes[1, 0].plot([], [], color="k", label="particle rest mass")
axes[1, 0].plot([], [], color="k", ls="--", label="excised rest mass")
axes[1, 0].set_xlabel(r"$t\,[M]$")
axes[1, 0].set_ylabel(r"rest mass $[M]$")
axes[1, 0].legend(loc="center left")
axes[1, 1].axhline(1.0, **fs.GUIDE)
axes[1, 1].text(0.03, 0.93, "ADM mass", transform=axes[1, 1].transAxes)
axes[1, 1].set_xlabel(r"$t\,[M]$")
axes[1, 1].set_ylabel(r"$M_{\rm AH}\,[M]$")
axes[1, 1].set_ylim(0.95, 1.01)
axes[1, 1].legend(loc="lower right")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
