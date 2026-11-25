#!/usr/bin/env python3
"""Ladder rows 2 and 3: horizon mass of the Oppenheimer-Snyder collapse and of the
prolate collapse.

Left: M_AH/M - 1 against time, the pre-program reference run to 60 M (lattice of 9328
particles) and the regression on the merged card build to 25 M; the band is the
paper's level of 1e-3. Right: M_AH/M of the prolate collapse at two resolutions, with
the paper's first-horizon time as a vertical line.

    fig_collapse.py OUTDIR   (writes OUTDIR/figures/fig_collapse.*, OUTDIR/numbers_collapse.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

T_AH_PAPER_PROLATE = 32.0   # main.tex line 971
DM_PAPER = 1e-3             # main.tex line 945


def at(t, m, t0):
    i = int(np.argmin(np.abs(t - t0)))
    return float(t[i]), float(m[i])


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent  # default: note/
    (out / "figures").mkdir(parents=True, exist_ok=True)
    fs = C.style()
    import matplotlib.pyplot as plt
    nums = {}
    d_sc, b = C.PRE["os_sc"]
    tsc, msc = C.horizon(d_sc / f"{b}.horizon_summary_0.txt")
    h = C.history(d_sc / f"{b}.nrpic.hst")
    src = "runs/os/nocap_sc (pre-program; inventory " + C.RUN["INVENTORY"] + ")"
    C.put(nums, "os.sc.t_first", float(tsc[0]), src, "V2")
    C.put(nums, "os.sc.m_first", float(msc[0]), src, "V2")
    C.put(nums, "os.sc.max_dev_to60", float(np.max(np.abs(msc[tsc <= 60.0] - 1.0))), src, "V2")
    for t0 in (20.0, 40.0, 60.0):
        tt, mm = at(tsc, msc, t0)
        C.put(nums, f"os.sc.m_at{int(t0)}", mm, src, "V2", note=f"search at {tt:.3f} M")
    i0 = int(np.argmax(h["np"] == 0)) if np.any(h["np"] == 0) else -1
    C.put(nums, "os.sc.n0", int(h["np"][0]), src, "V2")
    C.put(nums, "os.sc.t_all_removed", float(h["time"][i0]), src, "V2")
    C.put(nums, "os.sc.dev_above_1e-3_from", float(tsc[np.argmax(np.abs(msc - 1.0) > DM_PAPER)]),
          src, "V2", note="first search with |M_AH/M - 1| above 1e-3")
    above = np.abs(msc - 1.0) > DM_PAPER
    k = len(above) - int(np.argmin(above[::-1])) if not above.all() else 0
    C.put(nums, "os.sc.stays_above_1e-3_from", float(tsc[min(k, len(tsc) - 1)]), src, "V2",
          note="first search after which every search has |M_AH/M - 1| above 1e-3")

    d_o = C.SCRATCH / C.RUN["O"]
    to, mo = C.horizon(d_o / "os.horizon_summary_0.txt")
    C.put(nums, "os.O.t_first", float(to[0]), C.RUN["O"], "V2")
    C.put(nums, "os.O.m_first", float(mo[0]), C.RUN["O"], "V2")
    C.put(nums, "os.O.max_dev_to25", float(np.max(np.abs(mo[to <= 25.0] - 1.0))), C.RUN["O"], "V2")
    C.put(nums, "os.O.t_end", float(to[-1]), C.RUN["O"])

    d_p16, bp = C.PRE["prolate_m16"]
    tp16, mp16 = C.horizon(d_p16 / f"{bp}.horizon_summary_0.txt")
    d_p8 = C.SCRATCH / C.RUN["PROLATE_M8"] / "prolate_m8"
    tp8, mp8 = C.horizon(d_p8 / "prol.horizon_summary_0.txt")
    srcp = "runs/prolate/e09_v8 (pre-program; inventory " + C.RUN["INVENTORY"] + ")"
    for key, (t, m, s) in dict(m16=(tp16, mp16, srcp), m8=(tp8, mp8, C.RUN["PROLATE_M8"])).items():
        C.put(nums, f"prolate.{key}.t_first", float(t[0]), s)
        C.put(nums, f"prolate.{key}.m_first", float(m[0]), s)
        C.put(nums, f"prolate.{key}.m_max", float(m.max()), s)
        C.put(nums, f"prolate.{key}.t_last", float(t[-1]), s)
        C.put(nums, f"prolate.{key}.m_last", float(m[-1]), s)

    fig = plt.figure(figsize=(8.0, 3.3))
    ax = fig.add_axes([0.09, 0.16, 0.38, 0.78])
    bx = fig.add_axes([0.60, 0.16, 0.38, 0.78])
    fs.band(ax, [10, 62], [-DM_PAPER, -DM_PAPER], [DM_PAPER, DM_PAPER], fs.PAL["blue"], alpha=0.15)
    ax.plot(tsc, msc - 1.0, color=fs.PAL["blue"], lw=1.5, label=r"reference run, to $60\,M$")
    ax.plot(to, mo - 1.0, color=fs.PAL["red"], lw=1.5, ls="--", label=r"merged build, to $25\,M$")
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xlim(14, 61)
    ax.set_ylim(-2.5e-3, 1.5e-3)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$M_{\rm AH}/M - 1$")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, -3))
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    bx.plot(tp16, mp16, color=fs.PAL["blue"], lw=1.5, marker=".", ms=3, label=r"finest cells $M/16$")
    bx.plot(tp8, mp8, color=fs.PAL["red"], lw=1.5, marker=".", ms=3, label=r"finest cells $M/8$")
    bx.axvline(T_AH_PAPER_PROLATE, **fs.GUIDE)
    bx.axhline(1.0, color="k", lw=0.8)
    bx.set_xlabel(r"$t/M$")
    bx.set_ylabel(r"$M_{\rm AH}/M$")
    bx.set_ylim(0.90, 1.01)
    bx.set_xlim(31, 46)
    bx.legend(frameon=False, fontsize=8, loc="lower right")
    fs.save(fig, str(out / "figures" / "fig_collapse"))
    (out / "numbers_collapse.json").write_text(json.dumps(nums, indent=1))
    for k, v in nums.items():
        print(k, v["value"], v["note"])


if __name__ == "__main__":
    main()
