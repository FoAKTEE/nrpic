"""Deposition identity on a statically refined mesh in flat spacetime: residuals
|int E dV / sum m W - 1| and |int S_i dV / sum m u_i - 1| for every recorded cycle.

    python3 dep_smr.py [<label>=<rundir> ...] [--out NAME]

Defaults to the six variants under runs/dev/dep_smr. Exact zeros cannot be drawn on
a log axis: they are drawn as open markers on the floor 1e-17 (axis tick "0").
Marker sizes differ between runs (largest first) so that coincident points of
several runs stay visible as nested rings and dots.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import FIGS, H, parse_cli, read_nrpic_hst, run_path
from nrpic import figstyle as fs
from nrpic.io import read_nrp

DEFAULT = [f"{v}=runs/dev/dep_smr/{v}" for v in
           ("nocap", "cap1", "cap0", "cap1_filt2", "cpu_adapt", "cpu_adapt_min1_max2")]
runs, opts = parse_cli(sys.argv[1:], defaults=DEFAULT, options=("out",))
out = opts.get("out", "dep_smr")
FLOOR = 1e-17
EPS = np.finfo(float).eps / 2          # unit roundoff 1.1e-16
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"],
          "#7B3FA0", "#17A2B8"]

comps = [("int_e", "sum_mw", r"$|\int\!E\,dV/\sum mW-1|$"),
         ("int_sx", "sum_mux", r"$|\int\!S_x\,dV/\sum mu_x-1|$"),
         ("int_sy", "sum_muy", r"$|\int\!S_y\,dV/\sum mu_y-1|$"),
         ("int_sz", "sum_muz", r"$|\int\!S_z\,dV/\sum mu_z-1|$")]

fs.use_style()
fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharex=True)
fig.subplots_adjust(left=0.1, right=0.985, bottom=0.075, top=0.84, wspace=0.26,
                    hspace=0.06)
axes = axes.ravel()
scale = None
tmax = 0.0
for n, ((label, d), c) in enumerate(zip(runs, colors)):
    h = read_nrpic_hst(run_path(d, "dep.nrpic.hst"))
    t = h[:, H["time"]]
    tmax = max(tmax, t[-1])
    ms = [7.5, 6.0, 4.5, 3.0, 5.0, 3.5][n % 6]
    summary = [f"{label:22s} t_end={t[-1]:4.1f} N={len(t):3d}"]
    for ax, (ci, cs, _) in zip(axes, comps):
        r = np.abs(h[:, H[ci]] / h[:, H[cs]] - 1.0)
        z = r == 0.0
        ax.plot(t[~z], r[~z], ls="none", marker="o", ms=ms, color=c, mew=0.0,
                alpha=0.9, zorder=2 + n)
        ax.plot(t[z], np.full(z.sum(), FLOOR), ls="none", marker="o", ms=ms, mfc="none",
                mec=c, mew=1.0, zorder=2 + n)
        summary.append(f"{ci}: max {r.max():.2e} zeros {z.sum():2d}")
    axes[0].plot([], [], ls="none", marker="o", ms=5, color=c, label=label)
    print("  ".join(summary))
    if scale is None:
        # roundoff scale of the momentum sums: eps sum m|u_i| / |sum m u_i|, with the
        # particle momenta of the initial file (constant in flat spacetime)
        try:
            x, u, m, _ = read_nrp(run_path(d, "random.nrp"))
            scale = EPS * (m[:, None] * np.abs(u)).sum(0) / np.abs((m[:, None] * u).sum(0))
            print("roundoff scale of the momentum residuals:", scale)
        except OSError:
            scale = False

for i, (ax, (_, _, lab)) in enumerate(zip(axes, comps)):
    ax.set_yscale("log")
    ax.set_ylim(4e-18, 3e-11)
    ax.set_yticks([1e-17, 1e-16, 1e-15, 1e-14, 1e-13, 1e-12, 1e-11])
    ax.set_yticklabels(["0", r"$10^{-16}$", "", r"$10^{-14}$", "", r"$10^{-12}$", ""])
    fs.no_minor_labels(ax)
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.axhline(EPS, **fs.MASK_LINE)
    ax.text(tmax, EPS * 1.25, r"$\epsilon$", color="grey", ha="right", va="bottom")
    if i > 0 and scale is not False and scale is not None:
        s = scale[i - 1]
        ax.axhline(s, color="grey", lw=1.0, ls=":", alpha=0.7)
        ax.text(tmax, s * 1.25, r"$\epsilon\sum m|u_i|/|\sum m u_i|$", color="grey",
                ha="right", va="bottom", fontsize="small")
    ax.set_ylabel(lab)
    ax.set_xlim(-0.2, tmax + 0.2)
for ax in axes[2:]:
    ax.set_xlabel(r"$t\,[M]$", labelpad=-2)
axes[0].text(0.03, 0.95, "open markers at 0: exact zero\n" r"(drawn at the floor $10^{-17}$)",
             transform=axes[0].transAxes, va="top")
fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=3,
           bbox_to_anchor=(0.54, 1.0), title="GPU (cap = deposit_max_level, filt = nfilter)"
           " and CPU (adaptive cloud level) runs", title_fontsize="medium",
           columnspacing=1.5, handletextpad=0.3)
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
