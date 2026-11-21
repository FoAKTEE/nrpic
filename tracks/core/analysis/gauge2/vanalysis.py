#!/usr/bin/env python3
"""Test V of tracks/core/JOURNAL-gauge-2.md: one black hole in vacuum on the slice of the
Einstein-Straus data, with plain 1+log, with the relaxed lapse of the first pass and with
its variants of the second pass.

For every run: mass and mean coordinate radius of the apparent horizon in time (file
<base>.horizon_summary_0.txt, columns 2, 3 and 11), their difference from the control,
the drift of the mass from its value at --t0, and lapse, radial shift and chi on the +x
axis of the z = 0.001 slices (finest level at each x).  Writes <out>/v_numbers.json and
<out>/v_<tag>.png|pdf.

    vanalysis.py --out DIR --tag NAME [--t0 100] [--control NAME] [--ref NAME=FILE ...]
                 NAME=RUNDIR[:BASE] ...

--ref adds a horizon summary of another owner's run (Track D's V-1B, V-1GB) to the
panels of mass and radius, drawn thin.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))

from nrpic.athena_bin import read_bin          # noqa: E402
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

TIMES = (5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0,
         180.0, 199.5)
AXIS_VARS = ("z4c_alpha", "z4c_betax", "z4c_chi")


def horizon(path):
    """time, mass, mean coordinate radius of the searches that found a horizon."""
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            w = line.split()
            try:
                t, m, r = float(w[1]), float(w[2]), float(w[10])
            except (ValueError, IndexError):
                continue
            if np.isfinite(m) and np.isfinite(r) and m > 0.0:
                rows.append((t, m, r))
    a = np.array(rows)
    # a restart or a repeated first search writes a time twice: keep the last
    _, idx = np.unique(a[:, 0][::-1], return_index=True)
    return a[::-1][idx]


def axis_row(path):
    """Values on x > 0 of the row of cells just above y = 0, finest level at each x."""
    d = read_bin(path, assemble=False)
    names = d["variables"]
    idx = [names.index(v) for v in AXIS_VARS]
    pts = {}
    for b in d["blocks"]:
        x1a, x1b, x2a, x2b = b["bounds"][:4]
        if not (x2a <= 0.0 < x2b) or x1b <= 0.0:
            continue
        arr = b["data"]
        n2, n1 = arr.shape[2], arr.shape[3]
        j = int((0.0 - x2a) / ((x2b - x2a) / n2))
        xs = x1a + (np.arange(n1) + 0.5) * (x1b - x1a) / n1
        for i, x in enumerate(xs):
            if x <= 0.0:
                continue
            key = round(float(x), 6)
            if key not in pts or pts[key][0] < b["level"]:
                pts[key] = (b["level"], [float(arr[k, 0, j, i]) for k in idx])
    xs = np.array(sorted(pts))
    vals = np.array([pts[x][1] for x in xs])
    return float(d["time"]), xs, {v: vals[:, k] for k, v in enumerate(AXIS_VARS)}


def at(a, t, col):
    """Value of column col at the search nearest to t (None beyond the run)."""
    if a[-1, 0] < t - 0.6:
        return None
    return float(a[int(np.argmin(np.abs(a[:, 0] - t))), col])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--t0", type=float, default=100.0)
    ap.add_argument("--control", default="")
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--axis-times", default="20,50,100")
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    runs, slices = {}, {}
    for spec in a.runs:
        name, rest = spec.split("=", 1)
        rundir, base = (rest.split(":") + ["v1s"])[:2]
        runs[name] = horizon(os.path.join(rundir, f"{base}.horizon_summary_0.txt"))
        files = sorted(glob.glob(os.path.join(rundir, "bin", f"{base}.z4c.*.bin")))
        slices[name] = files
    refs = {}
    for spec in a.ref:
        name, path = spec.split("=", 1)
        refs[name] = horizon(path)
    ctl = a.control or next(iter(runs))

    numbers = dict(t0=a.t0, control=ctl, runs={})
    print(f"control: {ctl}; drift measured from t0 = {a.t0:g} M")
    for name, h in runs.items():
        t_end = float(h[-1, 0])
        rec = dict(t_end=t_end, searches=int(len(h)), table={})
        for t in TIMES:
            m, r = at(h, t, 1), at(h, t, 2)
            if m is None:
                continue
            mc = at(runs[ctl], t, 1)
            rc = at(runs[ctl], t, 2)
            rec["table"][f"{t:g}"] = dict(
                mass=m, radius=r,
                dmass=None if mc is None else m - mc,
                radius_ratio=None if rc is None else r / rc)
        sel = h[:, 0] >= a.t0 - 1e-9
        if sel.sum() > 1:
            m0 = at(h, a.t0, 1)
            dr = h[sel, 1] - m0
            rec["drift"] = dict(lo=float(dr.min()), hi=float(dr.max()), end=float(dr[-1]),
                                t_lo=float(h[sel, 0][int(np.argmin(dr))]),
                                t_hi=float(h[sel, 0][int(np.argmax(dr))]))
        for lo, hi in ((40.0, 100.0), (100.0, 200.0)):
            w = (h[:, 0] >= lo) & (h[:, 0] <= hi)
            if w.sum() > 3 and t_end >= hi - 1.0:
                rec[f"spread_{lo:g}_{hi:g}"] = float(h[w, 1].max() - h[w, 1].min())
        numbers["runs"][name] = rec
        print(f"\n{name}: {len(h)} searches with a horizon, to t = {t_end:g} M")
        print("   t      mass      radius   mass-control  radius/control")
        for t, v in rec["table"].items():
            dm = "" if v["dmass"] is None else f"{v['dmass']:+.2e}"
            rr = "" if v["radius_ratio"] is None else f"{v['radius_ratio']:.3f}"
            print(f"  {float(t):6.1f} {v['mass']:.6f} {v['radius']:.3f}   {dm:>10s}   {rr:>6s}")
        if "drift" in rec:
            d = rec["drift"]
            print(f"  drift from {a.t0:g} M: [{d['lo']:+.2e} at {d['t_lo']:g}, "
                  f"{d['hi']:+.2e} at {d['t_hi']:g}], end {d['end']:+.2e}")
        for k in rec:
            if k.startswith("spread"):
                print(f"  {k}: {rec[k]:.2e}")

    # ---- figure
    fs.use_style()
    cols = fs.series_colors(max(len(runs), 2)) if hasattr(fs, "series_colors") else None
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.0))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.09, top=0.96, wspace=0.36,
                        hspace=0.28)
    color = {}
    for i, (name, h) in enumerate(runs.items()):
        c = "k" if name == ctl else cols[i % len(cols)]
        color[name] = c
        ax[0, 0].plot(h[:, 0], h[:, 2], color=c, label=name)
        ax[0, 1].plot(h[:, 0], h[:, 1] - 1.0, color=c)
        if name != ctl:
            hc = runs[ctl]
            tt = h[:, 0][h[:, 0] <= hc[-1, 0]]
            dm = np.interp(tt, h[:, 0], h[:, 1]) - np.interp(tt, hc[:, 0], hc[:, 1])
            ax[0, 2].plot(tt, dm, color=c)
    for (name, h), ls in zip(refs.items(), (":", "--", "-.")):
        ax[0, 0].plot(h[:, 0], h[:, 2], color="0.5", lw=0.9, ls=ls, label=name)
        ax[0, 1].plot(h[:, 0], h[:, 1] - 1.0, color="0.5", lw=0.9, ls=ls)
    ax[0, 0].set_ylabel(r"horizon radius (coordinate) $/M$")
    ax[0, 1].set_ylabel(r"horizon mass $M_{\rm AH}/M-1$")
    ax[0, 2].set_ylabel(r"$M_{\rm AH}$ minus control")
    mall = np.concatenate([h[h[:, 0] >= 8.0, 1] - 1.0 for h in runs.values()])
    if len(mall):
        lo, hi = np.percentile(mall, [1, 99])
        pad = 0.15 * (hi - lo) + 1e-6
        ax[0, 1].set_ylim(lo - pad, hi + pad)
    ax[0, 2].axhline(0.0, color="0.7", lw=0.6)
    for k in range(3):
        ax[0, k].set_xlabel(r"coordinate time $t/M$", labelpad=1)
    ax[0, 0].legend(fontsize=6.5)

    want = [float(x) for x in a.axis_times.split(",") if x]
    lss = ("-", "--", ":")
    axis_numbers = {}
    for name, files in slices.items():
        got = {}
        for f in files:
            try:
                t, xs, v = axis_row(f)
            except Exception as err:                       # a slice cut by a wall limit
                print(f"{name}: {os.path.basename(f)} not read ({err})")
                continue
            for tw in want:
                if abs(t - tw) < 0.26:
                    got[tw] = (xs, v)
        axis_numbers[name] = {}
        for tw, ls in zip(want, lss):
            if tw not in got:
                continue
            xs, v = got[tw]
            for k, var in enumerate(AXIS_VARS):
                ax[1, k].plot(xs, v[var], color=color[name], ls=ls, lw=1.0)
            axis_numbers[name][f"{tw:g}"] = {
                var: {f"{x:g}": float(np.interp(x, xs, v[var])) for x in (1.0, 2.0, 5.0, 20.0)}
                for var in AXIS_VARS}
            axis_numbers[name][f"{tw:g}"]["alpha_max"] = float(v["z4c_alpha"].max())
            axis_numbers[name][f"{tw:g}"]["x_alpha_max"] = float(xs[int(np.argmax(v["z4c_alpha"]))])
    numbers["axis"] = axis_numbers
    for k, lab in enumerate((r"lapse on the $+x$ axis", r"shift $\beta^x$ on the $+x$ axis",
                             r"$\chi$ on the $+x$ axis")):
        ax[1, k].set_xscale("log")
        ax[1, k].set_xlim(0.2, 64.0)
        ax[1, k].set_xlabel(r"$x/M$", labelpad=1)
        ax[1, k].set_ylabel(lab)
    for tw, ls in zip(want, lss):
        ax[1, 0].plot([], [], color="0.3", ls=ls, label=r"$t=%g\,M$" % tw)
    ax[1, 0].legend(fontsize=6.5)
    fs.save(fig, os.path.join(a.out, f"v_{a.tag}"))
    plt.close(fig)

    print("\naxis values (alpha, beta^x, chi at x = 1, 2, 5, 20 M; largest lapse and where)")
    for name, d in axis_numbers.items():
        for tw, v in d.items():
            print(f"  {name:12s} t={tw:>5s}  alpha " + " ".join(f"{x:.3f}" for x in v['z4c_alpha'].values())
                  + "  betax " + " ".join(f"{x:.3f}" for x in v['z4c_betax'].values())
                  + "  chi " + " ".join(f"{x:.3f}" for x in v['z4c_chi'].values())
                  + f"  alpha_max {v['alpha_max']:.3f} at x = {v['x_alpha_max']:.1f}")
    with open(os.path.join(a.out, f"v_numbers_{a.tag}.json"), "w") as f:
        json.dump(numbers, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
