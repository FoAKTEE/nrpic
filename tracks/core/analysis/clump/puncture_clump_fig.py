#!/usr/bin/env python3
"""Figure of test T7 (tracks/core/JOURNAL-clump.md): y component of the momentum
constraint in the plane z = dx/2 for the three cases of puncture_clump_check.py.

    puncture_clump_fig.py RUN_ID      -> figs/fig_clump_puncture.{pdf,png}
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "mp"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from mp_common import read_bin  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

top = os.path.join("/data/haiyangw/nrpic/scratch/core", sys.argv[1])
fs.use_style()
fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
cases = (("punc", 1.0, "puncture's curvature only"), ("all", 1.0, "clumps and puncture (both)"),
         ("all", 100.0, r"both, $\times 100$"))
vmax = None
for axx, (lab, fac, title) in zip(ax, cases):
    t, par, x, y, z, dx, var = read_bin(os.path.join(top, lab, "bin", "clump.con.00000.bin"))
    sel = np.abs(z - 0.0625) < 1e-6
    n = int(round(np.sqrt(sel.sum())))
    o = np.lexsort((x[sel], y[sel]))
    img = var["con_My"][sel][o].reshape(n, n) * fac
    if vmax is None:
        vmax = np.abs(img).max()
    im = axx.imshow(img, origin="lower", extent=(-8, 8, -8, 8), cmap="RdBu_r", vmin=-vmax,
                    vmax=vmax)
    axx.plot([0.0], [5.0], "k+", ms=8)
    axx.set_title(title, fontsize=9)
    axx.set_xlabel(r"$x/\sigma$")
ax[0].set_ylabel(r"$y/\sigma$")
cb = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.015, aspect=18)
cb.set_label(r"$\mathcal{M}_y$")
fs.save(fig, os.path.join(HERE, "figs", "fig_clump_puncture"))
