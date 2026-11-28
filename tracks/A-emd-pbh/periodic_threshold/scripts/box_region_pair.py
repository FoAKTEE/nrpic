#!/usr/bin/env python3
"""DR (periodic_threshold JOURNAL 2026-11-28 08:22 PST): the section-3 ratio of a box run, ||H|| / ||16 pi E|| over the
whole box, and its parts r < s2, s2 < r < s1, r > s1 (s1, s2 the spheres of the deck's region norms; P0L decks: 2.449
and 0.6), each normalised by the whole-box ||16 pi E||, so that the squares of the parts add up to the square of the
total. Only rows without a held horizon (radius_h0 = 0) are used. Repeated times of continued chains: later rows win.

    box_region_pair.py --out DIR [--times 50,100,130] NAME=REGION_HST [NAME=REGION_HST ...]

Writes DIR/box_region_pair.json and DIR/fig_box_region_pair.{pdf,png}.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def read(path):
    rows = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        v = [float(x) for x in line.split()]
        rows[round(v[0], 9)] = v
    out = []
    for t in sorted(rows):
        v = rows[t]
        c = lambda k: v[k - 1]  # noqa: E731
        if len(v) >= 32 and c(32) > 0:
            continue
        r1, r2 = c(10), c(21)
        if r2 > r1:
            raise SystemExit("expected s2 < s1")
        nE2 = c(8) ** 2 * c(3)
        tot2 = c(7) ** 2 * c(3)
        out1 = c(17) ** 2 * c(16)          # outside s1
        in2 = c(23) ** 2 * c(22)           # inside s2
        mid2 = max(tot2 - out1 - in2, 0.0)
        out.append(dict(t=t, total=math.sqrt(tot2 / nE2), inner=math.sqrt(in2 / nE2), middle=math.sqrt(mid2 / nE2),
                        outer=math.sqrt(out1 / nE2), s1=r1, s2=r2))
    return out


def at(rows, t):
    ts = np.array([r["t"] for r in rows])
    i = int(np.argmin(abs(ts - t)))
    return rows[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--times", default="50,100,130")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    times = [float(x) for x in a.times.split(",")]
    res, table = {}, {}
    for m in a.members:
        name, p = m.split("=", 1)
        res[name] = read(p)
        table[name] = [at(res[name], t) for t in times]
        for r in table[name]:
            print("%-6s t=%7.2f total %.4f  r<%.2f %.4f  middle %.4f  r>%.3f %.4f" %
                  (name, r["t"], r["total"], r["s2"], r["inner"], r["middle"], r["s1"], r["outer"]))
    names = list(res)
    if len(names) >= 2:
        for k, t in enumerate(times):
            a0, b0 = table[names[0]][k], table[names[1]][k]
            print("t=%g  %s/%s: total %.3f  inner %.3f  middle %.3f  outer %.3f" %
                  (t, names[0], names[1], a0["total"] / b0["total"], a0["inner"] / b0["inner"],
                   a0["middle"] / max(b0["middle"], 1e-300), a0["outer"] / b0["outer"]))
    json.dump(dict(times=times, at_times=table, series=res), open(os.path.join(a.out, "box_region_pair.json"), "w"),
              indent=1)

    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COL_WIDTH if hasattr(fs, "COL_WIDTH") else 3.4, 2.8))
    fig.subplots_adjust(left=0.17, right=0.98, bottom=0.16, top=0.9)
    cols = dict(total="k", inner=fs.PAL["red"], middle=fs.PAL["green"], outer=fs.PAL["blue"])
    ls = ["-", "--", ":"]
    for k, (name, rows) in enumerate(res.items()):
        t = [r["t"] for r in rows]
        for part in ("total", "inner", "middle", "outer"):
            ax.plot(t, [r[part] for r in rows], color=cols[part], ls=ls[k % 3], lw=0.9,
                    label="%s %s" % (name, part))
    for t in times:
        ax.axvline(t, color="0.7", lw=0.6, ls=":")
    ax.axhline(0.1, color="0.6", lw=0.8, ls="--")
    ax.set_yscale("log")
    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$\|H\|/\|16\pi E\|$ (whole box, parts)")
    ax.set_title("box: four against six levels, same particles", fontsize=8)
    ax.legend(fontsize=4.8, ncol=2, loc="lower right")
    fs.save(fig, os.path.join(a.out, "fig_box_region_pair"))


if __name__ == "__main__":
    main()
