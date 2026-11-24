#!/usr/bin/env python3
"""Ladder row 4: central lapse of the relativistic star clusters.

Left: the five models of the paper's sequence (one-per-cent inward kick, 10^4
particles, adaptive mesh; pre-program runs), with a cross at the first apparent horizon
of the two that collapse. Right: the wave-2 bisection between the turning point and the
collapsing model, on a mesh capped at cells of M/4 (release core-v0.3), with the
turning point y_c* marked on the axis of central lapse.

    fig_clusters.py OUTDIR   (writes OUTDIR/figures/fig_clusters.*, OUTDIR/numbers_clusters.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

Y_STAR = 0.6796   # turning point, run core-20261115-152805-47d8f25 (verify/LADDER.md row 4)
PAPER_T_AH = {"yc0605": 109.0, "yc0500": 73.0}   # main.tex line 1138


def main():
    out = Path(sys.argv[1])
    (out / "figures").mkdir(parents=True, exist_ok=True)
    fs = C.style()
    import matplotlib.pyplot as plt
    nums = {}
    models = [("yc0900", "0.900", fs.PAL["blue"]), ("yc0819", "0.819", fs.PAL["green"]),
              ("yc0605", "0.605", fs.PAL["red"]), ("yc0500", "0.500", fs.PAL["orange"]),
              ("yc0283", "0.283", fs.PAL["yellow"])]
    fig = plt.figure(figsize=(8.0, 3.3))
    ax = fig.add_axes([0.08, 0.16, 0.40, 0.78])
    bx = fig.add_axes([0.58, 0.16, 0.40, 0.78])
    for key, lab, col in models:
        d, b = C.PRE[key]
        src = f"runs/{d.parent.name}/{d.name} (pre-program; inventory {C.RUN['INVENTORY']})"
        h = C.history(d / f"{b}.nrpic.hst")
        t, a = h["time"], h["alpha_probe"]
        sel = t <= 300.0
        ax.plot(t[sel], a[sel], color=col, lw=1.2, label=r"$y_c = " + lab + "$")
        C.put(nums, f"cl.{key}.alpha_min", float(a[sel].min()), src, "V3")
        C.put(nums, f"cl.{key}.alpha_max", float(a[sel].max()), src, "V3")
        C.put(nums, f"cl.{key}.t_end", float(t[-1]), src, "V3")
        C.put(nums, f"cl.{key}.np_start", int(h["np"][0]), src, "V3")
        C.put(nums, f"cl.{key}.np_end", int(h["np"][-1]), src, "V3")
        hf = d / f"{b}.horizon_summary_0.txt"
        if hf.exists():
            th, mh = C.horizon(hf)
            if len(th):
                C.put(nums, f"cl.{key}.t_first_ah", float(th[0]), src, "V3")
                C.put(nums, f"cl.{key}.m_ah_end", float(mh[-1]), src, "V3")
                ia = int(np.argmin(np.abs(t - th[0])))
                ax.plot([th[0]], [a[ia]], marker="x", color=col, ms=8, mew=2)
        if key == "yc0283":
            i = int(np.argmin(np.abs(t - 270.0)))
            C.put(nums, "cl.yc0283.alpha_at270", float(a[i]), src, "V3",
                  note=f"record at {t[i]:.2f} M")
    ax.set_xlim(0, 300)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"central lapse $\alpha_c$")
    ax.legend(frameon=False, fontsize=8, ncol=1, loc="center right", bbox_to_anchor=(1.0, 0.45))

    members = [("BIS_B", "st_yc0p720", "0.72"), ("BIS_A", "st_yc0p700", "0.70"),
               ("BIS_C", "st_yc0p690", "0.69"), ("BIS_C", "st_yc0p670", "0.67"),
               ("BIS_A", "st_yc0p660", "0.66"), ("BIS_B", "st_yc0p640", "0.64"),
               ("BIS_CTRL", "st_yc0p605", "0.605")]
    cols = fs.series_colors(len(members))
    for (run, sub, lab), col in zip(members, cols):
        d = C.SCRATCH / C.RUN[run] / sub
        h = C.history(d / "st.nrpic.hst")
        t, a = h["time"], h["alpha_probe"]
        bx.plot(t, a, color=col, lw=1.0, label=r"$" + lab + "$")
        hi = 250.0 if run == "BIS_CTRL" else 300.0
        w = (t >= 200.0) & (t <= hi)
        C.put(nums, f"bis.{lab}.mean_alpha_200_{int(hi)}", float(a[w].mean()), C.RUN[run],
              "V3" if lab == "0.72" else "")
        C.put(nums, f"bis.{lab}.alpha_start", float(a[0]), C.RUN[run])
        C.put(nums, f"bis.{lab}.t_end", float(t[-1]), C.RUN[run])
    bx.set_xlim(0, 300)
    bx.set_ylim(0.55, 0.93)
    bx.set_xlabel(r"$t/M$")
    bx.set_ylabel(r"central lapse $\alpha_c$")
    bx.legend(frameon=False, fontsize=7.5, ncol=4, loc="upper left", title=r"$y_c$",
              title_fontsize=8)
    fs.save(fig, str(out / "figures" / "fig_clusters"))
    (out / "numbers_clusters.json").write_text(json.dumps(nums, indent=1))
    for k, v in nums.items():
        print(k, v["value"], v["note"])


if __name__ == "__main__":
    main()
