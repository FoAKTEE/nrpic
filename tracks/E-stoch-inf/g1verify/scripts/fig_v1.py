"""Figure V1: box means of phi, Pi, K against my Friedmann/Klein-Gordon integration.

usage: fig_v1.py V123_RUN_DIR OUT_BASENAME
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

fs.use_style()
d = np.load(os.path.join(sys.argv[1], "v123_fig.npz"))
keys = sorted({k.split("_")[1] for k in d.files if k.startswith("v1_")})
show = [k for k in ("L32p", "L64p", "L128p", "L256p", "Q64p", "Q128p", "P256", "P256m", "NC128p") if k in keys]
cols = fs.series_colors(len(show))
fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.9, wspace=0.3)
for ax, nm in zip(axs, ("<phi>", "<Pi>", "<K>")):
    for k, c in zip(show, cols):
        t, rel = d[f"v1_{k}_{nm}"]
        ax.semilogy(t, np.maximum(rel, 1e-17), color=c, lw=1.0, label=k)
    ax.axhline(1e-4, **fs.GUIDE)
    ax.set_xlabel("code time t")
    ax.set_title(f"|{nm}/Friedmann - 1|")
    ax.set_ylim(1e-17, 1e-3)
axs[0].text(0.3, 1.5e-4, "A1 threshold", fontsize=8)
axs[0].legend(ncol=2, fontsize=7, loc="center right")
fs.save(fig, sys.argv[2])
