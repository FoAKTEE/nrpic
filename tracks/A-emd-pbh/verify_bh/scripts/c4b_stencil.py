#!/usr/bin/env python3
"""C4b: how much does the first trapped line point depend on the reading of the line?
(follow-up of run A-20261121-125449-689b5ec: my stencil gives t = 11.25 at M/8, C4 says 11.0)

Variants of 2m/R = 1 + (R KT)^2 - |DR|^2 on the x line of the adm table outputs:
  a  offsets y = z = dx/2 in n and r (as c4_lines.py), dR/dr second-order (np.gradient)
  b  the line taken as the axis: r = |x|, n = (+-1, 0, 0), A = gxx, B = (gyy + gzz)/2,
     KT = (Kyy + Kzz)/(gyy + gzz), dR/dr second-order
  c  as a, dR/dr from a quartic through five neighbours (fourth order)
  d  as a, staggered: values at midpoints of neighbouring line points, dR/dr = dR/dr of the pair
Trapped: 2m/R > 1 and KT > 0. Writes c4b_stencil.json and fig_c4b_stencil.{png,pdf}.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import vbio as V               # noqa: E402
from c4_lines import local_dx  # noqa: E402

RUNS = ["bh_n128", "bh_n192", "bh_n256", "bh_smr"]
VARIANTS = ["a", "b", "c", "d"]


def decompose(adm, run, axis):
    x = adm["x1v"]
    g = {k: adm["adm_g" + k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")}
    K = {k: adm["adm_K" + k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")}
    if axis:
        r = np.abs(x)
        A = g["xx"]
        B = 0.5 * (g["yy"] + g["zz"])
        KT = (K["yy"] + K["zz"]) / (g["yy"] + g["zz"])
    else:
        dx = local_dx(x, run)
        y = z = 0.5 * dx
        r = np.sqrt(x * x + y * y + z * z)
        n = np.stack([x, y, z]) / r

        def nn(T):
            return (n[0] ** 2 * T["xx"] + n[1] ** 2 * T["yy"] + n[2] ** 2 * T["zz"]
                    + 2 * (n[0] * n[1] * T["xy"] + n[0] * n[2] * T["xz"] + n[1] * n[2] * T["yz"]))
        A = nn(g)
        B = 0.5 * (g["xx"] + g["yy"] + g["zz"] - A)
        b = 0.5 * (K["xx"] + K["yy"] + K["zz"] - nn(K))
        KT = b / B
    return x, r, r * np.sqrt(B), KT, A


def two_m_over_R(adm, run, var):
    x, r, R, KT, A = decompose(adm, run, axis=(var == "b"))
    rs, vals, kts = [], [], []
    for side in (x > 0, x < 0):
        idx = np.nonzero(side)[0]
        o = idx[np.argsort(r[idx])]
        ro, Ro, Ko, Ao = r[o], R[o], KT[o], A[o]
        if var in ("a", "b"):
            d = np.gradient(Ro, ro)
            rr, RR, KK, AA = ro, Ro, Ko, Ao
        elif var == "c":
            d = np.empty_like(Ro)
            for i in range(len(ro)):
                lo = min(max(i - 2, 0), len(ro) - 5)
                c = np.polyfit(ro[lo:lo + 5] - ro[i], Ro[lo:lo + 5], 4)
                d[i] = c[-2]
            rr, RR, KK, AA = ro, Ro, Ko, Ao
        else:
            d = np.diff(Ro) / np.diff(ro)
            rr, RR, KK, AA = [0.5 * (q[1:] + q[:-1]) for q in (ro, Ro, Ko, Ao)]
        rs.append(rr)
        vals.append(1.0 + (RR * KK) ** 2 - d ** 2 / AA)
        kts.append(KK)
    return np.concatenate(rs), np.concatenate(vals), np.concatenate(kts)


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    res, curves = {}, {}
    for run in RUNS:
        files = V.tabout_series(os.path.join(P.RUN_DIR[run], "tab"), "adm")
        tabs = [V.read_tabout(f) for f in files]
        tabs = [a for a in tabs if 9.5 <= a["time"] <= 14.0]
        res[run] = {}
        for var in VARIANTS:
            first, mx = None, []
            for a in tabs:
                r, tm, kt = two_m_over_R(a, run, var)
                ok = np.isfinite(tm) & (r < 1.5)
                mx.append((a["time"], float(np.nanmax(tm[ok])) if ok.any() else np.nan))
                tr = ok & (tm > 1.0) & (kt > 0)
                if first is None and tr.any():
                    first = dict(t=a["time"], r=sorted(set(np.round(r[tr], 4).tolist())),
                                 two_m_over_R=float(tm[tr].max()))
            res[run][var] = dict(first_trapped=first, max_two_m_over_R=mx)
            curves[(run, var)] = mx
    with open(os.path.join(out, "c4b_stencil.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.89, wspace=0.30)
    ls = {"a": "-", "b": "--", "c": ":", "d": "-."}
    for j, run in enumerate(["bh_n256", "bh_smr"]):
        ax = fig.add_subplot(1, 2, 1 + j)
        for var in VARIANTS:
            t, m = zip(*curves[(run, var)])
            ax.plot(t, m, ls=ls[var], lw=1.3, color=fs.PAL["blue"] if run == "bh_n256" else fs.PAL["red"],
                    label=f"variant {var}")
        ax.axhline(1.0, **fs.GUIDE)
        ax.set_xlim(10.0, 12.5)
        ax.set_ylim(0.85, 1.25)
        ax.set_xlabel(r"code time $t\,/M$")
        ax.set_ylabel(r"largest $2m/R$ on the line ($r<1.5$)")
        ax.legend(fontsize=7, frameon=False, loc="upper left")
        ax.set_title({"bh_n256": "BH-1 M/8", "bh_smr": "BH-1R"}[run] + ": reading of the line", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c4b_stencil"))
    print(json.dumps({r: {v: res[r][v]["first_trapped"] for v in VARIANTS} for r in RUNS}, indent=1))


if __name__ == "__main__":
    main()
