"""Oscillation of a cluster about equilibrium: central lapse, its extrema, and the mean
Lorentz factor of the particles, for several runs.

    python3 cluster_osc.py <label>=<rundir> [...] [--out NAME] [--alpha0 0.80939]

Top: central lapse minus its equilibrium value. Middle: half the difference between
successive smoothed maxima and minima (amplitude) and their mean (drift), against the
time of the later extremum. Bottom: sum m W / sum m minus its initial value, a measure
of the kinetic energy that does not depend on a probe at the centre.
Printed: the extrema, and a straight-line fit of the amplitude against time.
"""
import glob
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

from common import FIGS, parse_cli, read_nrpic_hst, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], options=("out", "alpha0"))
out = opts.get("out", "cluster_osc")
alpha0 = float(opts.get("alpha0", 0.80939))
colors = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"],
          "#7B3FA0", "#17A2B8", "#8C564B"]

fs.use_style()
fig, ax = plt.subplots(3, 1, figsize=(fs.FULL_WIDTH, 8.0), sharex=True)
for (label, d), c in zip(runs, colors):
    files = sorted(glob.glob(os.path.join(run_path(d), "*.nrpic.hst")))
    h = read_nrpic_hst(files[0])
    t, a, w = h[:, 0], h[:, 12], h[:, 4] / h[:, 3]
    dt = np.median(np.diff(t))
    n = max(3, int(round(4.0 / dt)) | 1)            # 4 M boxcar
    s = np.convolve(a, np.ones(n) / n, mode="same")
    order = max(2, int(round(15.0 / dt)))           # extrema at least 15 M apart
    ext = sorted([(i, +1) for i in argrelextrema(s, np.greater, order=order)[0]] +
                 [(i, -1) for i in argrelextrema(s, np.less, order=order)[0]])
    ext = [(i, k) for i, k in ext if 8.0 < t[i] < t[-1] - 4.0]
    te, amp, mid = [], [], []
    for (i0, k0), (i1, k1) in zip(ext[:-1], ext[1:]):
        if k0 == k1:
            continue
        te.append(t[i1]); amp.append(0.5 * abs(s[i1] - s[i0])); mid.append(0.5 * (s[i1] + s[i0]) - alpha0)
    te, amp, mid = np.array(te), np.array(amp), np.array(mid)
    ax[0].plot(t, a - alpha0, color=c, label=label)
    ax[1].plot(te, amp, "o-", color=c, ms=4)
    ax[1].plot(te, mid, "s--", color=c, ms=3, lw=1.0)
    ax[2].plot(t, w - w[0], color=c)
    line = f"{label}: t_end {t[-1]:.0f}; extrema " + " ".join(
        f"{t[i]:.0f}:{s[i] - alpha0:+.4f}" for i, _ in ext)
    if len(te) >= 3:
        p = np.polyfit(te, amp, 1)
        line += f"\n   amplitude fit: {p[1]:.4f} + {p[0]:.2e} t; drift of the mean at the end {mid[-1]:+.4f}"
    line += f"\n   sum mW/sum m - initial: min {np.min(w - w[0]):+.5f}, max {np.max(w - w[0]):+.5f}, end {w[-1] - w[0]:+.5f}"
    print(line)
ax[0].axhline(0.0, **fs.REF_LINE) if hasattr(fs, "REF_LINE") else ax[0].axhline(0.0, color="0.5")
ax[0].set_ylabel(r"$\alpha_c - \alpha_{c,\rm eq}$")
ax[0].legend(frameon=False, ncol=2)
ax[1].set_ylabel("amplitude (circles), mean (squares)")
ax[1].axhline(0.0, color="0.8", lw=1.0)
ax[2].set_ylabel(r"$\sum mW/\sum m$ minus initial")
ax[2].set_xlabel(r"$t\,[M]$")
fig.subplots_adjust(left=0.12, right=0.98, top=0.98, bottom=0.07, hspace=0.06)
os.makedirs(FIGS, exist_ok=True)
for ext_ in ("pdf", "png"):
    fig.savefig(os.path.join(FIGS, f"{out}.{ext_}"), dpi=200)
print(os.path.join(FIGS, out + ".png"))
