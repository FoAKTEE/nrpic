#!/usr/bin/env python3
"""T0 of JOURNAL.md: the spatial-gauge piece G on exact pure-gauge Minkowski data.

    python3 t0_gauge.py OUTDIR

gw_diag analytic.gauge_mode: Minkowski space in random coordinates x = X + xi(X) (and, with
the slicing on, t = T + f(X)), amplitude eps of the coordinate gradients. With the slicing
off, tilde gamma = det(J)^(-2/3) J^T J exactly, so Lambda h - G must fall as eps^3; with the
slicing on, Lambda[-d f d f] remains at eps^2. Writes OUTDIR/t0_gauge.json and the figure.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from gwdiag import tt, analytic  # noqa: E402
from gwdiag.grid import Grid  # noqa: E402
from fslib import gauge  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def rms(x):
    return float(np.sqrt(np.mean(np.einsum("ab...,ab...->...", x, x))))


out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
os.makedirs(out, exist_ok=True)
g = Grid((32, 32, 32), (4.0, 4.0, 4.0), (0.0, 0.0, 0.0))
eps = np.logspace(-4, -2, 9)
res = {"eps": eps.tolist(), "cases": {}}
for slicing in (False, True):
    for seed in (3, 11):
        rows = []
        for e in eps:
            gamma = analytic.gauge_mode(g, e, seed=seed, slicing=slicing)[0]
            ginv, d = tt.inv3(gamma)
            h = d ** (-1.0 / 3.0) * gamma - np.eye(3)[:, :, None, None, None]
            Lh = tt.tt_project(h, g)
            G = gauge.gauge_piece(h, g)
            Gn = gauge.gauge_piece(h, g, pad=False)
            rows.append([rms(Lh), rms(Lh - G), rms(Lh - Gn), rms(gauge.nonTT_traceless(h, g))])
        rows = np.array(rows)
        key = f"slicing={slicing},seed={seed}"
        sl = [float(np.polyfit(np.log(eps), np.log(rows[:, c]), 1)[0]) for c in range(4)]
        res["cases"][key] = {"rms_Lh": rows[:, 0].tolist(), "rms_Lh_minus_G": rows[:, 1].tolist(),
                             "rms_Lh_minus_G_nopad": rows[:, 2].tolist(), "rms_nonTT": rows[:, 3].tolist(),
                             "slopes": {"Lh": sl[0], "Lh_minus_G": sl[1], "Lh_minus_G_nopad": sl[2],
                                        "nonTT": sl[3]}}
with open(os.path.join(out, "t0_gauge.json"), "w") as f:
    json.dump(res, f, indent=1)

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2), sharey=True)
for j, slicing in enumerate((False, True)):
    c = res["cases"][f"slicing={slicing},seed=3"]
    ax[j].loglog(eps, c["rms_nonTT"], "s", color=fs.PAL["yellow"], ms=4, label="non-TT part of $h$")
    ax[j].loglog(eps, c["rms_Lh"], "o", color=fs.PAL["blue"], ms=4, label=r"$\Lambda h$")
    ax[j].loglog(eps, c["rms_Lh_minus_G"], "^", color=fs.PAL["red"], ms=4, label=r"$\Lambda h - G$")
    for p, y0 in ((2, c["rms_Lh"][-1]), (3, c["rms_Lh_minus_G"][-1])):
        ax[j].loglog(eps, y0 * (eps / eps[-1]) ** p, **fs.MASK_LINE)
    ax[j].set_xlabel(r"amplitude $\epsilon$ of the coordinate gradients")
    ax[j].set_title("spatial coordinates only" if not slicing else "spatial coordinates and slicing",
                    fontsize=10)
    s = c["slopes"]
    ax[j].text(0.03, 0.97, "slopes: %.2f, %.2f" % (s["Lh"], s["Lh_minus_G"]), transform=ax[j].transAxes,
               va="top", fontsize=8)
ax[0].set_ylabel("rms over the box")
ax[0].legend(loc="lower right")
fig.tight_layout()
fs.save(fig, os.path.join(out, "t0_gauge"))
print(json.dumps({k: v["slopes"] for k, v in res["cases"].items()}, indent=1))
