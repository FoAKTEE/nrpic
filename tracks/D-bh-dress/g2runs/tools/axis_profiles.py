#!/usr/bin/env python3
"""Lapse, radial shift and conformal factor along the +x axis from the z = 0.001 slices
(`<base>.z4c.NNNNN.bin`, every 10 M) of several runs, finest level at each x.

Writes axis_profiles.json (values at chosen x and times, horizon-region numbers) and the
figure axis_profiles.png: (a) alpha(x), (b) beta^x(x), (c) chi(x) at t = 50, 100, 150 and
the last common time, one colour per run; (d) alpha at x = 1, 2, 5, 20, 60 M against t.

Usage: axis_profiles.py --out DIR NAME=RUNDIR:BASE [...]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
from nrpic.athena_bin import read_bin  # noqa: E402
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

VARS = ("z4c_alpha", "z4c_betax", "z4c_chi")
XPROBE = (1.0, 2.0, 5.0, 20.0, 60.0)


def axis_row(path):
    """x > 0 on the line y ~ 0 of the slice, finest level wins."""
    d = read_bin(path, assemble=False)
    names = d["variables"]
    idx = [names.index(v) for v in VARS]
    pts = {}
    for b in d["blocks"]:
        x1a, x1b, x2a, x2b = b["bounds"][:4]
        if not (x2a <= 0.0 < x2b) or x1b <= 0.0:
            continue
        arr = b["data"]                      # (nvar, n3, n2, n1)
        n2, n1 = arr.shape[2], arr.shape[3]
        dx2 = (x2b - x2a) / n2
        j = int((0.0 - x2a) / dx2)           # row whose lower face is at or below y = 0
        dx1 = (x1b - x1a) / n1
        xs = x1a + (np.arange(n1) + 0.5) * dx1
        for i, x in enumerate(xs):
            if x <= 0:
                continue
            key = round(x, 6)
            if key not in pts or pts[key][0] < b["level"]:
                pts[key] = (b["level"], [float(arr[k, 0, j, i]) for k in idx])
    xs = np.array(sorted(pts))
    vals = np.array([pts[x][1] for x in xs])
    return d["time"], xs, {v: vals[:, k] for k, v in enumerate(VARS)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    data = {}
    for spec in a.runs:
        name, rest = spec.split("=", 1)
        rdir, base = rest.rsplit(":", 1)
        files = sorted(glob.glob(os.path.join(rdir, "bin", f"{base}.z4c.*.bin")))
        prof = {}
        for f in files:
            t, xs, v = axis_row(f)
            prof[round(t, 6)] = (xs, v)
        data[name] = prof
    tcommon = sorted(set.intersection(*[set(p) for p in data.values()]))
    show = [t for t in (50.0, 100.0, 150.0) if t in tcommon] + [tcommon[-1]]
    res = {"times_common": tcommon, "runs": {}}
    for name, prof in data.items():
        r = {}
        for t in sorted(prof):
            xs, v = prof[t]
            r[str(t)] = {f"{var}@{x}": float(np.interp(x, xs, v[var])) for var in VARS for x in XPROBE}
            r[str(t)]["alpha_max_x<100"] = float(v["z4c_alpha"][xs < 100].max())
            r[str(t)]["alpha_min"] = float(v["z4c_alpha"].min())
        res["runs"][name] = r
    json.dump(res, open(os.path.join(a.out, "axis_profiles.json"), "w"), indent=1)

    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2), constrained_layout=True)
    cols = fs.series_colors(len(data))
    styles = ["-", "--", ":", "-."]
    for c, (name, prof) in zip(cols, data.items()):
        for s, t in zip(styles, show):
            xs, v = prof[t]
            lab = f"{name}, t = {t:g}" if True else None
            ax[0, 0].plot(xs, v["z4c_alpha"], s, color=c, lw=1.1, label=lab)
            ax[0, 1].plot(xs, v["z4c_betax"], s, color=c, lw=1.1)
            ax[1, 0].plot(xs, v["z4c_chi"], s, color=c, lw=1.1)
        ts = np.array(sorted(prof))
        for k, x in enumerate((1.0, 5.0, 60.0)):
            al = [np.interp(x, prof[t][0], prof[t][1]["z4c_alpha"]) for t in ts]
            ax[1, 1].plot(ts, al, styles[k], color=c, lw=1.1,
                          label=f"{name}, x = {x:g} M" if True else None)
    for x in ax.flat[:3]:
        x.set_xscale("log")
        x.set_xlim(0.1, 300)
        x.set_xlabel(r"$x/M$ (axis, $y = 0$, $z = 0.001$)")
    ax[0, 0].set_ylabel(r"lapse $\alpha$")
    ax[0, 0].legend(fontsize=5.5, frameon=False, ncol=2, loc="lower right")
    ax[0, 0].set_title("(a) lapse; line style = time", loc="left", fontsize=9)
    ax[0, 1].set_ylabel(r"shift $\beta^x$")
    ax[0, 1].set_title("(b) radial shift on the axis", loc="left", fontsize=9)
    ax[1, 0].set_ylabel(r"$\chi$")
    ax[1, 0].set_title(r"(c) conformal factor $\chi$", loc="left", fontsize=9)
    ax[1, 1].set_xlabel(r"$t/M$")
    ax[1, 1].set_ylabel(r"$\alpha$")
    ax[1, 1].legend(fontsize=5.5, frameon=False, ncol=1)
    ax[1, 1].set_title("(d) lapse at x = 1, 5, 60 M against time", loc="left", fontsize=9)
    fs.save(fig, os.path.join(a.out, "axis_profiles"))
    for name, r in res["runs"].items():
        for t in show:
            row = r[str(t)]
            print(name, t, " ".join(f"{k}={row[k]:.4g}" for k in sorted(row)))


if __name__ == "__main__":
    main()
