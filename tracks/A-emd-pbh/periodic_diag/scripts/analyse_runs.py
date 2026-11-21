#!/usr/bin/env python3
"""Analysis of the processor runs of periodic_diag (G series on the uniform mesh, R series on
the card deck): step against the finest cell, constraint statistics, onset of growth, and
the cell-to-cell alternating part of beta^x, Gam^x and alpha on the line outputs.

  python -I analyse_runs.py --run LABEL=DIR[:DX] [--run ...] --out DIR [--name NAME]
        [--tmax T] [--vn DIR]

DX is the finest cell size of the run (default 0.3125, the uniform 64^3 mesh). Onset: the
first cstat line after t = 1 whose H_max exceeds ten times the median of H_max over
0.3 < t < 2.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from card_onset import load_hst, load_tab, alternating  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="runs")
    ap.add_argument("--tmax", type=float, default=12.0)
    ap.add_argument("--vn", default=None)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    thr = None
    if args.vn:
        js = json.load(open(os.path.join(args.vn, "vonneumann.json")))
    res = {}
    data = {}
    for spec in args.run:
        lab, rest = spec.split("=", 1)
        if ":" in rest:
            d, dx = rest.rsplit(":", 1)
            dx = float(dx)
        else:
            d, dx = rest, 0.3125
        cn, nh = load_hst(os.path.join(d, "peak.nrpic.hst"))
        t = nh[:, cn.index("time")]
        amin = nh[:, cn.index("alpha_min")]
        amax = nh[:, cn.index("alpha_max")]
        r = np.diff(t) / dx
        cs, cst = load_hst(os.path.join(d, "peak.cstat.hst"))
        tc, hmax = cst[:, 0], cst[:, cs.index("H_max")]
        cz, zh = load_hst(os.path.join(d, "peak.z4c.user.hst"))
        tz, hn = zh[:, 0], zh[:, cz.index("H-norm2")]
        base = np.median(hmax[(tc > 0.3) & (tc < 2.0)])
        big = np.nonzero((hmax > 10 * base) & (tc > 1.0))[0]
        log = open(os.path.join(d, "athena.log")).read()
        guard = "NRPIC guard" in log
        rec = {"dir": d, "dx": dx, "last_t": float(t[-1]), "cycles": int(nh[-1, cn.index("ncycle")]),
               "guard_stop": guard, "Hmax_baseline": float(base),
               "dt_over_dx_max": float(r.max()) if r.size else None,
               "Hmax_final": float(hmax[-1]), "Hnorm2_final": float(hn[-1]),
               "Hnorm2_at_2": float(np.interp(2.0, tz, hn)),
               "alpha_min_final": float(amin[-1]), "alpha_max_final": float(amax[-1])}
        if big.size:
            j = big[0]
            k = int(np.searchsorted(t, tc[j]))
            rec["onset"] = {"t": float(tc[j]), "cycle": int(nh[min(k, len(t) - 1),
                                                                cn.index("ncycle")]),
                            "Hmax": float(hmax[j]), "previous_Hmax": float(hmax[j - 1]),
                            "dt_over_dx_of_steps_before": [float(x) for x in r[max(k - 4, 0):k]]}
        else:
            rec["onset"] = None
        # line outputs: alternating amplitude on the finest cells
        lines = []
        for f in sorted(glob.glob(os.path.join(d, "tab", "peak.z4c.*.tab"))):
            tt, cy, dd = load_tab(f)
            x = dd["x1v"]
            o = np.argsort(x)
            x = x[o]
            row = {"t": tt, "cycle": cy}
            for v in ("z4c_betax", "z4c_Gamx", "z4c_alpha"):
                amp, h = alternating(x, dd[v][o])
                s = np.abs(h - dx) < 1e-3 * dx
                row[v] = float(np.nanmax(amp[s])) if s.any() else None
            lines.append(row)
            data.setdefault(lab, {}).setdefault("lines", []).append((tt, x, {v: dd[v][o] for v in
                                                                      ("z4c_betax", "z4c_Gamx",
                                                                       "z4c_alpha")}))
        rec["lines_alternating_finest"] = lines
        res[lab] = rec
        data.setdefault(lab, {})["series"] = (t, r, tc, hmax, tz, hn, amin, amax)
    with open(os.path.join(args.out, args.name + ".json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    labs = list(res)
    cols = dict(zip(labs, fs.SERIES * 3))
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.28, hspace=0.3)
    for lab in labs:
        t, r, tc, hmax, tz, hn, amin, amax = data[lab]["series"]
        axs[0, 0].plot(t[1:], r, color=cols[lab], label=lab)
        hh = np.where(np.isfinite(hmax) & (hmax < 1e8), hmax, np.nan)
        axs[0, 1].semilogy(tc, hh, color=cols[lab], label=lab)
        axs[1, 0].plot(t, amin, color=cols[lab], label=lab)
        axs[1, 0].plot(t, amax, color=cols[lab], ls="--", lw=1.0)
    if args.vn:
        for key, ls in (("uniform_root", "--"), ("card_level4", ":")):
            thr = js["cases"][key]["shift"]["threshold_dt_over_dx"]
            axs[0, 0].axhline(thr, color="k", lw=1.0, ls=ls)
    axs[0, 0].set_ylabel(r"$\Delta t/\Delta x$ (finest)")
    axs[0, 1].set_ylabel(r"$H_{\max}$ (cstat)")
    axs[0, 1].set_ylim(1e-4, 1e4)
    axs[1, 0].set_ylabel(r"$\alpha_{\min}$ (solid), $\alpha_{\max}$ (dashed)")
    for ax in (axs[0, 0], axs[0, 1], axs[1, 0]):
        ax.set_xlabel("t")
        ax.set_xlim(0, args.tmax)
    axs[0, 0].legend(loc="lower right", fontsize=8)
    # bottom right: alternating amplitude of beta^x on the finest cells against time
    ax = axs[1, 1]
    for lab in labs:
        rows = res[lab]["lines_alternating_finest"]
        tt = [q["t"] for q in rows if q["z4c_betax"] is not None]
        bb = [min(max(q["z4c_betax"], 1e-16), 1e8) for q in rows if q["z4c_betax"] is not None]
        aa = [min(max(q["z4c_alpha"], 1e-16), 1e8) for q in rows if q["z4c_alpha"] is not None]
        ax.semilogy(tt, bb, "o-", ms=3, color=cols[lab], label=lab + r": $\beta^x$")
        ax.semilogy(tt[:len(aa)], aa, "s--", ms=2.5, lw=1.0, color=cols[lab],
                    label=lab + r": $\alpha$")
    ax.set_xlabel("t")
    ax.set_xlim(0, args.tmax)
    ax.set_ylabel("cell-to-cell alternation (finest, line)")
    ax.set_ylim(1e-9, 1e2)
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    fig.savefig(os.path.join(args.out, "fig_" + args.name + ".png"))
    for lab in labs:
        q = res[lab]
        print(lab, "last_t", q["last_t"], "guard", q["guard_stop"], "onset", q["onset"],
              "dt/dx max", q["dt_over_dx_max"], "H2(2)", q["Hnorm2_at_2"],
              "H2 final", q["Hnorm2_final"])


if __name__ == "__main__":
    main()
