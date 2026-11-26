#!/usr/bin/env python3
"""Fresh verifier of gate G2 (Track A), item V4 (checklist C3): ||H|| / ||16 pi E|| on the x line through the ball
(weights x^2 dx, x > 0; SCOPE section 3 bound 0.1), from the AthenaK line outputs (tab/<base>.con.NNNNN.tab, column
con_H; tab/<base>.tmunu.NNNNN.tab, column tmunu_E), with a reader of my own.

    python -I c3_verify.py --out DIR --member NAME=DIR ...

dx of each cell: half the distance between its neighbours on the line (exact inside a level). test_weights() first.
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
import figstyle as fs  # noqa: E402


def read_tab(path):
    with open(path) as f:
        l1 = f.readline()
        l2 = f.readline()
    t = float(l1.split("time=")[1].split()[0])
    names = l2.lstrip("#").split()
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def widths(x):
    o = np.argsort(x)
    xs = x[o]
    w = np.empty_like(xs)
    w[1:-1] = 0.5 * (xs[2:] - xs[:-2])
    w[0] = xs[1] - xs[0]
    w[-1] = xs[-1] - xs[-2]
    out = np.empty_like(w)
    out[o] = w
    return out


def ratio(x, H, E):
    m = x > 0
    w = widths(x)[m] * x[m] ** 2
    return math.sqrt(np.sum(H[m] ** 2 * w)) / math.sqrt(np.sum((16 * math.pi * E[m]) ** 2 * w))


def test_weights():
    # a nested line: cells 0.5 wide out to 8, 0.25 to 4, 0.125 to 2 (both signs)
    xs = []
    for lo, hi, h in ((4, 8, 0.5), (2, 4, 0.25), (0, 2, 0.125)):
        c = np.arange(lo + h / 2, hi, h)
        xs += list(c) + list(-c)
    x = np.array(xs)
    w = widths(x)
    m = x > 0
    I = float(np.sum(w[m] * x[m] ** 2))           # integral of x^2 on [0, 8] = 170.667
    E = np.exp(-x ** 2 / 8)
    r = ratio(x, 0.1 * 16 * math.pi * E, E)
    return dict(int_x2=I, exact=512 / 3, ratio=r, passed=bool(abs(I / (512 / 3) - 1) < 2e-3 and abs(r - 0.1) < 1e-12))


def member(d):
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "tab", "*.con.*.tab"))):
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        t2, e = read_tab(g)
        assert abs(t - t2) < 1e-9
        x = c["x1v"]
        assert np.allclose(x, e["x1v"])
        rows.append(dict(t=t, ratio=ratio(x, c["con_H"], e["tmunu_E"]), ncell=int((x > 0).sum()),
                         hmin=float(np.min(widths(x)))))
    return rows


def at(rows, t):
    for r in rows:
        if abs(r["t"] - t) < 1e-6:
            return r["ratio"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(test=test_weights(), members={})
    print("weights test", res["test"], flush=True)
    for spec in a.member:
        nm, d = spec.split("=", 1)
        res["members"][nm] = dict(dir=d, rows=member(d))
        rr = res["members"][nm]["rows"]
        print(nm, [(round(r["t"], 3), round(r["ratio"], 6)) for r in rr[:9]], flush=True)
    T = (0.0, 0.25, 0.5, 0.75, 1.0, 2.0)
    table = {nm: {f"{t:g}": at(m["rows"], t) for t in T} for nm, m in res["members"].items()}
    res["table"] = table
    pairs = [("tophat A (card)", "tophat B (card)"), ("S2c-A", "S2c-B"), ("S2c-A0", "S2c-B0"), ("S1-A0", "S1-B0"),
             ("S2-A", "S2-B")]
    orders = {}
    for p, q in pairs:
        if p in table and q in table:
            o = {}
            for t in T:
                u, v = table[p][f"{t:g}"], table[q][f"{t:g}"]
                o[f"{t:g}"] = math.log2(u / v) if u and v else None
            orders[f"{p} -> {q}"] = o
    res["orders_A_to_B"] = orders
    if "S2c-A8" in table and "S2c-A" in table:
        res["A8_over_A"] = {f"{t:g}": (table["S2c-A8"][f"{t:g}"] / table["S2c-A"][f"{t:g}"]
                                       if table["S2c-A8"][f"{t:g}"] and table["S2c-A"][f"{t:g}"] else None) for t in T}
    # figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.COLUMN_WIDTH * 1.4, 3.0))
    ax = fs.inch_axes(fig, 0.65, 0.45, 4.8, 2.4)
    sty = {"tophat A (K4-ref)": (fs.PAL["blue"], "o", "-"), "tophat A (card)": (fs.PAL["blue"], "s", "--"),
           "tophat B (card)": (fs.PAL["blue"], "^", ":"), "S2-A": (fs.PAL["green"], "o", "-"),
           "S2c-A": (fs.PAL["red"], "o", "-"), "S2c-B": (fs.PAL["red"], "^", ":"), "S2c-A8": (fs.PAL["orange"], "d", "-")}
    for nm, m in res["members"].items():
        rr = [r for r in m["rows"] if r["t"] <= 5.0001]
        if len(rr) < 2:
            if rr:
                ax.plot([0.02], [rr[0]["ratio"]], marker="x", color="k", ls="none")
                ax.annotate(nm, (0.02, rr[0]["ratio"]), fontsize=5, xytext=(3, 0), textcoords="offset points")
            continue
        c, mk, ls = sty.get(nm, ("k", ".", "-"))
        ax.semilogy([max(r["t"], 0.02) for r in rr], [r["ratio"] for r in rr], ls=ls, marker=mk, ms=2.5, color=c, label=nm)
    ax.axhline(0.1, color="k", lw=0.7)
    ax.set_xscale("symlog", linthresh=0.25)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\|H\|/\|16\pi E\|$ on the $x$ line")
    ax.legend(fontsize=5.5, loc="lower right", ncol=2)
    res["figure"] = fs.save(fig, os.path.join(a.out, "fig_c3_verify"))
    with open(os.path.join(a.out, "c3_verify.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(dict(table=table, orders=orders, A8=res.get("A8_over_A")), indent=1))


if __name__ == "__main__":
    main()
