#!/usr/bin/env python3
"""RT2a reader (threshold_ball JOURNAL entries 20 and 21; decision 0051 item 4).

For each member NAME=RUNDIR with a <base>.region.hst (core-v0.5 region norms: spheres s1 = 4.25, s2 = 13 and the
found horizon h0), the SCOPE section-3 ratio ||H|| / ||16 pi E|| over the whole exterior the run has (outside the
found horizon when the finder holds one at that row, else the whole box) and its split into parts whose squares add
up to the square of the total:
  inner   horizon (or 0) < r < 4.25  (the matter and what the mesh resolves: falls with the mesh, 0051 item 4)
  middle  4.25 < r < 13
  outer   r > 13 to the outer faces (falls with the distance of the faces and the face options)
All parts are normalised by the same ||16 pi E|| of the exterior. Volume norms: ||X||^2 = X2^2 V (X2 = rms over the
proper volume V of the region, as region.hst writes it).

Members NAME=RUNDIR:line also read the x-line tables (tab/ball.con.*.tab, tab/ball.tmunu.*.tab) with
ratio_split.split (edges 4.25, 13; xmax 32), for members without region norms (the v0.6 member A-d0.42).

    rt2a_read.py --out DIR [--t0 45.875] [--tmin 40] [--tmax 48.5] NAME=RUNDIR[:line] ...

Writes DIR/rt2a.json and DIR/fig_rt2a.{pdf,png}.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ratio_split as rs  # noqa: E402


def read_region(rd):
    f = sorted(glob.glob(os.path.join(rd, "*.region.hst")))
    if not f:
        return None
    rows = {}
    for line in open(f[0]):
        if line.startswith("#") or not line.strip():
            continue
        v = [float(x) for x in line.split()]
        rows[round(v[0], 9)] = v            # a repeated time (continued chain): the later row wins
    out = []
    for t in sorted(rows):
        v = rows[t]
        c = lambda k: v[k - 1]               # noqa: E731  (1-based columns of the header)
        rh = c(32)
        if rh > 0:
            Vx, Hx, Ex = c(38), c(39), c(40)
        else:
            Vx, Hx, Ex = c(3), c(7), c(8)
        nE2 = Ex * Ex * Vx
        tot2 = Hx * Hx * Vx
        out1 = c(17) ** 2 * c(16)            # outside 4.25
        out2 = c(28) ** 2 * c(27)            # outside 13
        inner2 = max(tot2 - out1, 0.0)
        mid2 = max(out1 - out2, 0.0)
        out.append(dict(t=t, cycle=int(c(2)), horizon_radius=rh, exterior="outside horizon" if rh > 0 else "whole box",
                        total=math.sqrt(tot2 / nE2), inner=math.sqrt(inner2 / nE2), middle=math.sqrt(mid2 / nE2),
                        outer=math.sqrt(out2 / nE2), whole_box=c(7) / c(8),
                        E_exterior_over_box=math.sqrt(nE2 / (c(8) ** 2 * c(3)))))
    return out


def read_found(rd):
    f = sorted(glob.glob(os.path.join(rd, "*.horizon_status_0.txt")))
    if not f:
        return []
    found = []
    for line in open(f[0]):
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        if p[2] == "1":
            found.append(dict(t=float(p[1]), mass=float(p[6]), radius=float(p[7])))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--t0", type=float, default=45.875)
    ap.add_argument("--tmin", type=float, default=40.0)
    ap.add_argument("--tmax", type=float, default=48.5)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rs.BANDS = [("x 0-4.25", 0.0, 4.25), ("x 4.25-13", 4.25, 13.0), ("x 13-face", 13.0, 1e9)]
    res = {}
    for m in a.members:
        name, d = m.split("=", 1)
        line = d.endswith(":line")
        d = d[:-5] if line else d
        r = dict(run=d, found=read_found(d))
        reg = read_region(d)
        if reg is not None:
            r["region"] = [x for x in reg if a.tmin - 1e-9 <= x["t"] <= a.tmax + 1e-9]
        r["line"] = [x for x in rs.split(d, 32.0) if a.tmin - 1e-9 <= x["t"] <= a.tmax + 1e-9]
        res[name] = r
        print("==", name, d)
        print("  finder finds:", len(r["found"]), " first", r["found"][0] if r["found"] else None)
        for x in r.get("region", []):
            if abs(x["t"] - a.t0) <= 0.51 or x["horizon_radius"] > 0:
                print("  region t=%7.3f %-15s r_h=%.3f total %.4f inner %.4f middle %.4f outer %.4f (box %.4f)"
                      % (x["t"], x["exterior"], x["horizon_radius"], x["total"], x["inner"], x["middle"],
                         x["outer"], x["whole_box"]))
        for x in r["line"]:
            if abs(x["t"] - a.t0) <= 0.26:
                print("  line   t=%7.3f total %.4f  " % (x["t"], x["total"])
                      + "  ".join("%s %.4g" % (b[0], x[b[0]]) for b in rs.BANDS))
    json.dump(dict(t0=a.t0, members=res), open(os.path.join(a.out, "rt2a.json"), "w"), indent=1)

    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.88, wspace=0.25)
    cols = dict(total="k", inner=fs.PAL["red"], middle=fs.PAL["green"], outer=fs.PAL["blue"])
    ls = ["-", "--", ":"]
    for k, (name, r) in enumerate(res.items()):
        if "region" in r:
            t = [x["t"] for x in r["region"]]
            for part in ("total", "inner", "middle", "outer"):
                ax[0].plot(t, [x[part] for x in r["region"]], color=cols[part], ls=ls[k % 3], lw=1.0,
                           marker="o", ms=2, label="%s %s" % (name, part))
            th = [x["t"] for x in r["region"] if x["horizon_radius"] > 0]
            ax[0].plot(th, [x["total"] for x in r["region"] if x["horizon_radius"] > 0], "s", mfc="none",
                       color="k", ms=6, label="%s: exterior of a found horizon" % name)
        t = [x["t"] for x in r["line"]]
        ax[1].plot(t, [x["x 0-4.25"] for x in r["line"]], color=fs.PAL["red"], ls=ls[k % 3], lw=1.0,
                   label="%s x<4.25" % name)
        ax[1].plot(t, [x["x 13-face"] for x in r["line"]], color=fs.PAL["blue"], ls=ls[k % 3], lw=1.0,
                   label="%s 13-32" % name)
    for x in ax:
        x.axhline(0.1, color="0.6", lw=0.8, ls="--")
        x.axvline(a.t0, color="0.6", lw=0.8, ls=":")
        x.set_yscale("log")
        x.set_xlabel(r"$t/M$")
    ax[0].set_title("region norms: exterior ratio and its parts", fontsize=8)
    ax[1].set_title(r"$x$ line: matter and outer-face parts", fontsize=8)
    ax[0].set_ylabel(r"$\|H\|/\|16\pi E\|$ (part)")
    ax[0].legend(fontsize=5, loc="upper left")
    ax[1].legend(fontsize=5.5, loc="lower right")
    fs.save(fig, os.path.join(a.out, "fig_rt2a"))


if __name__ == "__main__":
    main()
