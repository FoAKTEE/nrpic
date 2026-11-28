#!/usr/bin/env python3
"""FC reader (threshold_ball JOURNAL entry 19): absolute ||H|| per band of the line x > 0 (weight x^2 dx, as
ratio_split.py), the E norm and the section-3 ratio, for members NAME=RUNDIR, and the factors between named pairs.

  face_conv.py --out DIR --pair N4:N8 --pair N4F:N8F --same N4F:FR --same N8:S2cB  NAME=RUNDIR ...
RUNDIR holds tab/ball.con.*.tab and tab/ball.tmunu.*.tab. Writes DIR/face_conv.json and fig_face_conv.{png,pdf}.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BANDS = [("x<4.5", 0.0, 4.5), ("4.5-6.5", 4.5, 6.5), ("6.5-13", 6.5, 13.0), ("13-16", 13.0, 16.0)]


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def member(rd):
    out = {}
    for f in sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab"))):
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        _, m = read_tab(g)
        x = c["x1v"]
        o = np.argsort(x)
        x, H, E = x[o], c["con_H"][o], 16.0 * math.pi * m["tmunu_E"][o]
        s = (x > 0) & (x < 16.0)
        x, H, E = x[s], H[s], E[s]
        w = x * x * np.gradient(x)
        nE = math.sqrt(np.sum(w * E * E))
        rec = dict(t=t, nE=nE, H_total=math.sqrt(np.sum(w * H * H)))
        for name, lo, hi in BANDS:
            q = (x >= lo) & (x < hi)
            rec["H_" + name] = math.sqrt(np.sum(w[q] * H[q] ** 2))
            rec["ratio_" + name] = rec["H_" + name] / nE
        out[round(t, 6)] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("members", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pair", action="append", default=[], help="COARSE:FINE, factor of ||H|| in 13-16")
    ap.add_argument("--same", action="append", default=[], help="X:Y, ratio of ||H|| in 13-16 (proxy check)")
    ap.add_argument("--tmax", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mem = {}
    for m in a.members:
        name, d = m.split("=", 1)
        mem[name] = {t: r for t, r in member(d).items() if t <= a.tmax + 1e-9}
        for t, r in sorted(mem[name].items()):
            print("%-6s t=%.2f nE %.4e  " % (name, t, r["nE"])
                  + "  ".join("H[%s] %.3e" % (b[0], r["H_" + b[0]]) for b in BANDS)
                  + "  ratio13-16 %.5f" % r["ratio_13-16"])
    res = dict(members=mem, pairs={}, same={})
    for kind, lst in (("pairs", a.pair), ("same", a.same)):
        for p in lst:
            x, y = p.split(":")
            ts = sorted(set(mem[x]) & set(mem[y]))
            res[kind][p] = [dict(t=t, factor=mem[x][t]["H_13-16"] / mem[y][t]["H_13-16"]
                                 if mem[y][t]["H_13-16"] > 0 else None) for t in ts]
            print(kind, p, " ".join("t=%.2f %.3f" % (q["t"], q["factor"]) for q in res[kind][p] if q["factor"]))
    json.dump(res, open(os.path.join(a.out, "face_conv.json"), "w"), indent=1)

    sys.path.insert(0, os.path.join(HERE, "..", "..", "note", "scripts"))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.3))
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["yellow"], "0.4", "0.7"]
    for k, (name, rs) in enumerate(mem.items()):
        ts = sorted(t for t in rs if t > 0)
        ls = "--" if name.endswith("F") or name == "FR" else "-"
        ax[0].semilogy(ts, [rs[t]["H_13-16"] for t in ts], ls, marker="o", ms=3, color=cols[k % len(cols)], label=name)
    ax[0].set_xlabel("t"); ax[0].set_ylabel(r"$\|H\|$ on $13<x<16$ (weight $x^2dx$)"); ax[0].legend(fontsize=7)
    for k, (p, rs) in enumerate(list(res["pairs"].items()) + list(res["same"].items())):
        q = [r for r in rs if r["factor"] and r["t"] > 0]
        ax[1].plot([r["t"] for r in q], [r["factor"] for r in q], marker="o", ms=3, color=cols[k % len(cols)],
                   label=p + (" (coarse/fine)" if p in res["pairs"] else " (proxy)"))
    for y in (1.0, 2.0, 4.0):
        ax[1].axhline(y, color="0.6", lw=0.6)
    ax[1].set_yscale("log"); ax[1].set_xlabel("t"); ax[1].set_ylabel("factor of $\\|H\\|$ on 13-16")
    ax[1].legend(fontsize=7)
    for k, s in enumerate("ab"):
        ax[k].set_title("(%s)" % s, loc="left", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_face_conv"))


if __name__ == "__main__":
    main()
