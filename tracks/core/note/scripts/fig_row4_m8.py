#!/usr/bin/env python3
"""Ladder row 4 on cells of M/8: kicked members against their unkicked controls.

Bisection level 1 of batch 5 (rule and predictions: tracks/core/JOURNAL.md, entry of
2026-11-21T20:26Z): y_c = 0.605, 0.680, 0.755, each with a one-per-cent inward kick
(solid) and without it (dashed), static mesh with cells of M/8 inside |x| < 3.9 M,
10^4 particles, release core-v0.6 card build. Crosses mark the first apparent horizon;
the grey band is the window 200-300 M of the rule; the dotted line of each colour is the
equilibrium central lapse of the model (run core-20261121-202643-d66c4ee).

    fig_row4_m8.py OUTDIR   (writes OUTDIR/figures/fig_row4_m8.*, OUTDIR/numbers_row4m8.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

IDATA = "core-20261121-202643-d66c4ee"
PAIRS = [  # y_c, member run, control run
    ("0.605", "core-20261121-204230-3bcb118", "core-20261121-204235-0b25077"),
    ("0.680", "core-20261121-204234-d010783", "core-20261121-204239-2be5ac2"),
    ("0.755", "core-20261121-204232-f74c942", "core-20261121-204237-ae00ca2"),
]


def main():
    out = Path(sys.argv[1])
    (out / "figures").mkdir(parents=True, exist_ok=True)
    fs = C.style()
    import matplotlib.pyplot as plt
    models = json.loads(C.checked(C.SCRATCH / IDATA / "models.json").read_text())
    nums = {}
    cols = {"0.605": fs.PAL["red"], "0.680": fs.PAL["orange"], "0.755": fs.PAL["blue"]}
    fig = plt.figure(figsize=(8.0, 3.3))
    ax = fig.add_axes([0.08, 0.16, 0.40, 0.78])
    bx = fig.add_axes([0.58, 0.16, 0.40, 0.78])
    for yc, mem, ctl in PAIRS:
        col = cols[yc]
        a_eq = None
        for m in models["models"].values():
            if abs(float(m["yc"]) - float(yc)) < 1e-6:
                a_eq = float(m["alpha_c"])
        if a_eq is not None:
            C.put(nums, f"m8.{yc}.alpha_eq", a_eq, IDATA)
            for axx in (ax, bx):
                axx.axhline(a_eq, color=col, lw=0.6, ls=":")
        means, collapsed = {}, False
        for run, ls, tag in ((mem, "-", "member"), (ctl, "--", "control")):
            d = C.SCRATCH / run
            h = C.history(d / "st.nrpic.hst")
            t, a = h["time"], h["alpha_probe"]
            lab = r"$y_c = " + yc + "$" if tag == "member" else None
            ax.plot(t, a, color=col, lw=1.1, ls=ls, label=lab)
            w = (t >= 200.0) & (t <= 300.0)
            means[tag] = float(a[w].mean())
            C.put(nums, f"m8.{yc}.{tag}.mean_alpha_200_300", means[tag], run)
            C.put(nums, f"m8.{yc}.{tag}.alpha_min", float(a.min()), run)
            C.put(nums, f"m8.{yc}.{tag}.t_end", float(t[-1]), run)
            hf = d / "st.horizon_summary_0.txt"
            th = np.array([])
            if hf.exists():
                th, mh = C.horizon(hf)
            below = t[a < 0.3]
            t_c = None
            if len(th):
                t_c = float(th[0])
                C.put(nums, f"m8.{yc}.{tag}.t_first_ah", t_c, run)
                C.put(nums, f"m8.{yc}.{tag}.m_ah_last", float(mh[-1]), run)
            if len(below):
                C.put(nums, f"m8.{yc}.{tag}.t_alpha_below_0.3", float(below[0]), run)
                t_c = float(below[0]) if t_c is None else min(t_c, float(below[0]))
            if t_c is not None and t_c <= 300.0:
                collapsed = True
                C.put(nums, f"m8.{yc}.{tag}.t_c", t_c, run)
                ia = int(np.argmin(np.abs(t - t_c)))
                ax.plot([t_c], [a[ia]], marker="x", color=col, ms=8, mew=2)
            if t_c is None:
                bx.plot(t, a, color=col, lw=1.0, ls=ls)
        if not collapsed:   # D is defined by the rule only when neither run collapses
            C.put(nums, f"m8.{yc}.D", means["member"] - means["control"], f"{mem} - {ctl}")
    for axx in (ax, bx):
        axx.axvspan(200.0, 300.0, color="0.85", lw=0, zorder=0)
        axx.set_xlim(0, 300)
        axx.set_xlabel(r"$t/M$")
        axx.set_ylabel(r"central lapse $\alpha_c$")
    ax.set_ylim(0.0, 1.0)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    bx.set_ylim(0.60, 0.85)
    bx.text(0.03, 0.95, "runs without collapse\nsolid: kicked member; dashed: control",
            transform=bx.transAxes, va="top", fontsize=8)
    fs.save(fig, str(out / "figures" / "fig_row4_m8"))
    (out / "numbers_row4m8.json").write_text(json.dumps(nums, indent=1))
    for k, v in nums.items():
        print(k, v["value"], v["note"])


if __name__ == "__main__":
    main()
