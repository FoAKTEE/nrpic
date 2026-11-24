#!/usr/bin/env python3
"""Ladder row 4 on cells of M/8: kicked members against their unkicked controls.

Bisection levels 1 (batch 5) and 2 (batch 10a) under the rule of tracks/core/JOURNAL.md,
entry of 2026-11-21T20:26Z: y_c = 0.605, 0.680, 0.755 (level 1) and 0.69875, 0.7175,
0.73625 (level 2), each with a one-per-cent inward kick (solid) and without it (dashed),
static mesh with cells of M/8 inside |x| < 3.9 M, 10^4 particles, release core-v0.6 card
build, to 300 M. The central lapse is shown in units of the equilibrium value of each
model (initial data runs core-20261121-202643-d66c4ee and core-20261123-020409-4fae8fb).
Crosses mark the collapse time (first apparent horizon or central lapse below 0.3); the
grey band is the window 200-300 M of the rule. Panel (b): the two models without
collapse, with the means over 50-M windows (the inward drift).

A run continued from a restart file is written "<first run>+<continuation run>"; its
records are joined in time (for level 3, when it has run).

    fig_row4_m8.py OUTDIR   (writes OUTDIR/figures/fig_row4_m8.*, OUTDIR/numbers_row4m8.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

L1, L2 = "core-20261121-202643-d66c4ee", "core-20261123-020409-4fae8fb"
PAIRS = [  # y_c label, initial-data run, member run(s), control run(s)
    ("0.605", L1, "core-20261121-204230-3bcb118", "core-20261121-204235-0b25077"),
    ("0.680", L1, "core-20261121-204234-d010783", "core-20261121-204239-2be5ac2"),
    ("0.69875", L2, "core-20261123-020454-8fec6b2", "core-20261123-020456-884f550"),
    ("0.7175", L2, "core-20261123-020450-7e42037", "core-20261123-020452-e635a8e"),
    ("0.73625", L2, "core-20261123-020458-dfc38d7", "core-20261123-020500-9b192cd"),
    ("0.755", L1, "core-20261121-204232-f74c942", "core-20261121-204237-ae00ca2"),
]
T_RULE = 300.0


def joined(runs):
    """History of one run, or of a run and its continuations, joined in time."""
    t_all, a_all, ah = [], [], []
    for run in runs.split("+"):
        d = C.SCRATCH / run
        h = C.history(d / "st.nrpic.hst")
        t, a = np.asarray(h["time"]), np.asarray(h["alpha_probe"])
        if t_all:
            keep = t_all[-1] < t[0]
            t_all[-1], a_all[-1] = t_all[-1][keep], a_all[-1][keep]
        t_all.append(t)
        a_all.append(a)
        hf = d / "st.horizon_summary_0.txt"
        if hf.exists():
            th, mh = C.horizon(hf)
            if len(th):
                ah.append((float(th[0]), float(mh[-1])))
    t = np.concatenate(t_all)
    a = np.concatenate(a_all)
    return t, a, (min(ah) if ah else None)


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent  # default: note/
    (out / "figures").mkdir(parents=True, exist_ok=True)
    fs = C.style()
    import matplotlib.pyplot as plt
    models = {}
    for idata in (L1, L2):
        js = json.loads(C.checked(C.SCRATCH / idata / "models.json").read_text())
        for m in js["models"].values():
            models[round(float(m["yc"]), 6)] = (float(m["alpha_c"]), idata)
    nums = {}
    cmap = plt.get_cmap("plasma")
    cols = {p[0]: cmap(0.05 + 0.8 * i / (len(PAIRS) - 1)) for i, p in enumerate(PAIRS)}
    fig = plt.figure(figsize=(8.0, 3.3))
    ax = fig.add_axes([0.08, 0.16, 0.40, 0.78])
    bx = fig.add_axes([0.58, 0.16, 0.40, 0.78])
    tmax = T_RULE
    for yc, idata, mem, ctl in PAIRS:
        col = cols[yc]
        a_eq, src = models[round(float(yc), 6)]
        C.put(nums, f"m8.{yc}.alpha_eq", a_eq, src)
        means, collapsed, quiet = {}, False, []
        for run, ls, tag in ((mem, "-", "member"), (ctl, "--", "control")):
            t, a, ah = joined(run)
            tmax = max(tmax, float(t[-1]))
            an = a / a_eq
            lab = r"$y_c = " + yc + "$" if tag == "member" else None
            ax.plot(t, an, color=col, lw=1.0, ls=ls, label=lab)
            w = (t >= 200.0) & (t <= 300.0)
            means[tag] = float(a[w].mean())
            C.put(nums, f"m8.{yc}.{tag}.mean_alpha_200_300", means[tag], run)
            C.put(nums, f"m8.{yc}.{tag}.t_end", float(t[-1]), run)
            t_c = None
            if ah is not None:
                t_c = ah[0]
                C.put(nums, f"m8.{yc}.{tag}.t_first_ah", ah[0], run)
                C.put(nums, f"m8.{yc}.{tag}.m_ah_last", ah[1], run)
            below = t[a < 0.3]
            if len(below):
                C.put(nums, f"m8.{yc}.{tag}.t_alpha_below_0.3", float(below[0]), run)
                t_c = float(below[0]) if t_c is None else min(t_c, float(below[0]))
            if t_c is not None:
                C.put(nums, f"m8.{yc}.{tag}.t_c", t_c, run,
                      note="" if t_c <= T_RULE else "after the window of the rule")
                ia = int(np.argmin(np.abs(t - t_c)))
                ax.plot([t_c], [an[ia]], marker="x", color=col, ms=7, mew=1.8)
                if t_c <= T_RULE:
                    collapsed = True
            # 50-M window means of alpha_c / alpha_c^eq (the drift), all runs
            for w0 in np.arange(0.0, float(t[-1]) - 1e-9, 50.0):
                sel = (t >= w0) & (t < w0 + 50.0)
                if sel.any():
                    C.put(nums, f"m8.{yc}.{tag}.mean_norm_{int(w0)}_{int(w0) + 50}",
                          float(an[sel].mean()), run)
            quiet.append((t, an, ls))
        if not collapsed:   # panel (b): models where neither run collapses within the rule
            for t, an, ls in quiet:
                bx.plot(t, an, color=col, lw=0.8, ls=ls, alpha=0.6)
                ws = np.arange(0.0, float(t[-1]) - 1e-9, 50.0)
                wm = [float(an[(t >= w0) & (t < w0 + 50.0)].mean()) for w0 in ws]
                bx.hlines(wm, ws, ws + 50.0, color=col, lw=2.0, ls=ls)
        if not collapsed:   # D is defined by the rule only when neither run collapses
            C.put(nums, f"m8.{yc}.D", means["member"] - means["control"], f"{mem} - {ctl}")
    for axx in (ax, bx):
        axx.axvspan(200.0, 300.0, color="0.88", lw=0, zorder=0)
        axx.set_xlim(0, tmax)
        axx.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_c/\alpha_c^{\rm eq}$")
    ax.set_ylim(0.0, 1.3)
    ax.legend(frameon=False, fontsize=7, loc="lower left", ncol=2)
    ax.text(0.97, 0.97, "(a)", transform=ax.transAxes, ha="right", va="top")
    bx.set_ylim(0.84, 1.04)
    bx.text(0.03, 0.04, "models without collapse by 300 M; thick: 50-M means\nsolid: kicked member; dashed: control",
            transform=bx.transAxes, va="bottom", fontsize=7)
    bx.text(0.97, 0.97, "(b)", transform=bx.transAxes, ha="right", va="top")
    fs.save(fig, str(out / "figures" / "fig_row4_m8"))
    (out / "numbers_row4m8.json").write_text(json.dumps(nums, indent=1))
    for k, v in nums.items():
        print(k, v["value"], v["note"])


if __name__ == "__main__":
    main()
