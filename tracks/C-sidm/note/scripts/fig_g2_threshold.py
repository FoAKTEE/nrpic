"""Figure (gate G2): the collisionless threshold of the King b = 1 family, one panel per leg of
the three-way convergence. Every curve is the smallest lapse on the mesh, alpha_min(t); a run
counts as collapsed when alpha_min falls below 0.3 (dashed line; the lapse marker: no run
carried a horizon finder). Crosses: the marker crossing, linear in time between records.

(a) particle number: the unkicked control of the turning-point model y0 = 0.334032 on M/8 at
    N = 1e4, 1e5, 1e6;
(b) mesh: the two bracket members y0 = 0.344 and 0.324, kicked inward, N = 1e6, on M/8 (solid)
    and M/16 (dashed);
(c) gauge: the same members on M/8 with shift damping eta = 2 (solid) and 1 (dotted).
Reads cc.nrpic.hst of the registered card runs common.RUNS["g2_*"], checked against the
checksums the runs recorded. Histories of runs continued in place: a later row replaces the
earlier ones from its time on (the rule of longruns/scripts/nseries.py).
"""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_g2_threshold"
MARK = 0.3


def hist(key):
    """Restart-aware reader: a row whose time is not after the last kept one truncates."""
    names, out = None, []
    with open(cm.run_file(key, "cc.nrpic.hst")) as f:
        for ln in f:
            if ln.startswith("#"):
                if names is None and "[1]=" in ln:
                    names = re.findall(r"\[\d+\]=(\S+)", ln)
                continue
            v = ln.split()
            if not v:
                continue
            r = [float(x) for x in v]
            while out and out[-1][0] >= r[0] - 1e-12:
                out.pop()
            out.append(r)
    a = np.array(out)
    return {n: a[:, i] for i, n in enumerate(names[:a.shape[1]])}


def crossing(t, y):
    i = np.flatnonzero(y < MARK)
    if not i.size:
        return None
    k = i[0]
    if k == 0:
        return float(t[0])
    return float(t[k - 1] + (MARK - y[k - 1]) * (t[k] - t[k - 1]) / (y[k] - y[k - 1]))


def draw(ax, key, color, ls, label, res):
    h = hist(key)
    t, am = h["time"], h["alpha_min"]
    ok = np.isfinite(am) & (h["np"] > 0)
    tc = crossing(t[ok], am[ok])
    ax.plot(t[ok], am[ok], ls, color=color, lw=1.2, label=label)
    if tc is not None:
        ax.plot([tc], [MARK], "x", color=color, ms=6, mew=1.4)
    res[key] = dict(run=cm.RUNS[key], t_c=tc, t_end=float(t[-1]), alpha_min0=float(am[0]),
                    alpha_min_min=float(np.nanmin(am[ok])))


def main():
    out = cm.out_dir("figures")
    cz.use_style()
    res = {}
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.55), sharey=True)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.17, top=0.9, wspace=0.07)
    red, blue = cz.PAL["red"], cz.PAL["blue"]
    ax = axs[0]
    for key, col, lab in (("g2_n4c", cz.PAL["orange"], r"$N=10^4$"),
                          ("g2_n5c", cz.PAL["green"], r"$N=10^5$"),
                          ("g2_n6c", blue, r"$N=10^6$")):
        draw(ax, key, col, "-", lab, res)
    ax.set_title(r"(a) control $y_0=0.334$, M/8", fontsize=8)
    ax = axs[1]
    draw(ax, "g2_b344", red, "-", r"$y_0=0.344$, M/8", res)
    draw(ax, "g2_b344m16", red, "--", r"$y_0=0.344$, M/16", res)
    draw(ax, "g2_b324", blue, "-", r"$y_0=0.324$, M/8", res)
    draw(ax, "g2_b324m16", blue, "--", r"$y_0=0.324$, M/16", res)
    ax.set_title(r"(b) kicked, $N=10^6$: mesh", fontsize=8)
    ax = axs[2]
    draw(ax, "g2_b344", red, "-", r"$y_0=0.344$, $\eta=2$", res)
    draw(ax, "g2_b344e1", red, ":", r"$y_0=0.344$, $\eta=1$", res)
    draw(ax, "g2_b324", blue, "-", r"$y_0=0.324$, $\eta=2$", res)
    draw(ax, "g2_b324e1", blue, ":", r"$y_0=0.324$, $\eta=1$", res)
    ax.set_title(r"(c) kicked, $N=10^6$, M/8: gauge", fontsize=8)
    for ax in axs:
        ax.axhline(MARK, **cz.GUIDE)
        ax.set_xlim(0, 610)
        ax.set_xticks([0, 200, 400] if ax is not axs[-1] else [0, 200, 400, 600])
        ax.set_ylim(0.0, 0.85)
        ax.set_xlabel(r"time $t/M$")
        ax.legend(frameon=False, loc="lower left", fontsize=6.5, handlelength=2.0)
    axs[0].set_ylabel(r"smallest lapse $\alpha_{\min}$")
    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    for k, v in res.items():
        print(f"{STEM}: {k}: {v}")


if __name__ == "__main__":
    main()
