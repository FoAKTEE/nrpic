#!/usr/bin/env python3
"""Test A of periodic_diag (JOURNAL.md entry 0): the outputs of card job 4799 read again.

For P0L and S1L of run A-20261121-131600-02b5d41: the step per cycle against the cell size
of level 4 (peak.nrpic.hst, every cycle), the constraint statistics (peak.cstat.hst, every
8 cycles), the Z4c history (peak.z4c.user.hst), and for P0L the line outputs along x
(tab/peak.z4c.0000N.tab at t = 0, 2.01, 4.0) with the cell-to-cell alternating part of
beta^x, Gam^x and alpha per refinement level. With --vn (the vonneumann_curves.npz of Test
B) the linear amplification of the grid-scale shift mode accumulated over the card's own
step history is added.

  python -I card_onset.py --job DIR --out DIR [--vn DIR]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DX4 = 20.0 / 64 / 16  # level-4 cell size of peak_leak.athinput (0.01953125)


def load_hst(path):
    with open(path) as f:
        head = [ln for ln in f if ln.startswith("#")]
    cols = []
    for ln in head:
        if "[1]=" in ln:
            cols = [c.split("=")[1] for c in ln.strip("# \n").split() if "=" in c]
    data = np.loadtxt(path, comments="#", ndmin=2)
    return cols, data


def load_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    cyc = int(first.split("cycle=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, cyc, {n: d[:, i] for i, n in enumerate(names)}


def alternating(x, f):
    """Per point: |f_{i-1} - 2 f_i + f_{i+1}|/4 on runs of equal spacing (the amplitude of a
    cell-to-cell alternation), and the spacing there."""
    dx = np.diff(x)
    amp = np.full_like(f, np.nan)
    h = np.full_like(f, np.nan)
    for i in range(1, len(f) - 1):
        if abs(dx[i - 1] - dx[i]) < 1e-6 * dx[i]:
            amp[i] = abs(f[i - 1] - 2 * f[i] + f[i + 1]) / 4.0
            h[i] = dx[i]
    return amp, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--vn", default=None)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    res = {"job": args.job, "dx_level4": DX4, "members": {}}
    series = {}
    vn = None
    if args.vn:
        z = np.load(os.path.join(args.vn, "vonneumann_curves.npz"))
        vn = (z["rs"], z["card_level4__shift"])
        thr = float(json.load(open(os.path.join(args.vn, "vonneumann.json")))
                    ["cases"]["card_level4"]["shift"]["threshold_dt_over_dx"])
    else:
        thr = 0.685
    for mem in ("P0L", "S1L"):
        d = os.path.join(args.job, mem)
        cn, nh = load_hst(os.path.join(d, "peak.nrpic.hst"))
        t = nh[:, cn.index("time")]
        cyc = nh[:, cn.index("ncycle")]
        dt = np.diff(t)            # step taken from cycle n to n+1
        r = dt / DX4
        cs, cst = load_hst(os.path.join(d, "peak.cstat.hst"))
        tc = cst[:, 0]
        hmax = cst[:, cs.index("H_max")]
        cz, zh = load_hst(os.path.join(d, "peak.z4c.user.hst"))
        # first step above the threshold, and first cstat line with H_max > 10 x its
        # median over t < 2
        k = int(np.argmax(r > thr))
        base = np.median(hmax[(tc > 0.3) & (tc < 2.0)])
        j = int(np.argmax(hmax > 10 * base))
        m = {"first_step_above_threshold": {"cycle": int(cyc[k]), "t": float(t[k]),
                                            "dt_over_dx": float(r[k]), "threshold": thr},
             "Hmax_baseline_t0.3_2": float(base),
             "first_cstat_Hmax_above_10x_baseline": {"t": float(tc[j]),
                                                      "Hmax": float(hmax[j]),
                                                      "previous_t": float(tc[j - 1]),
                                                      "previous_Hmax": float(hmax[j - 1])},
             "dt_over_dx_max_before_jump": float(r[t[:-1] < tc[j]].max()),
             "last_time": float(t[-1])}
        if vn is not None:
            rho = np.interp(r, vn[0], vn[1])
            lnA = np.concatenate([[0.0], np.cumsum(np.log(rho))])
            m["log10_linear_amplification_to_first_jump_line"] = float(
                lnA[np.searchsorted(t, tc[j])] / np.log(10))
            m["log10_linear_amplification_to_previous_line"] = float(
                lnA[np.searchsorted(t, tc[j - 1])] / np.log(10))
            series[mem + "_lnA"] = (t, lnA)
        res["members"][mem] = m
        series[mem] = (t[:-1], r, tc, hmax)
    # the two members' steps compared up to t = 2.3
    tp, rp = series["P0L"][0], series["P0L"][1]
    ts, rs_ = series["S1L"][0], series["S1L"][1]
    sel = tp < 2.3
    rel = np.abs(np.interp(tp[sel], ts, rs_) / rp[sel] - 1.0)
    res["step_P0L_vs_S1L_max_rel_diff_t_lt_2.3"] = float(rel.max())
    # line outputs of P0L
    lines = {}
    for f in sorted(glob.glob(os.path.join(args.job, "P0L", "tab", "peak.z4c.0000?.tab"))):
        tt, cy, d = load_tab(f)
        x = d["x1v"]
        o = np.argsort(x)
        x = x[o]
        rec = {"t": tt, "cycle": cy}
        for v in ("z4c_betax", "z4c_Gamx", "z4c_alpha", "z4c_Khat"):
            fv = d[v][o]
            amp, h = alternating(x, fv)
            per = {}
            for lev, hh in ((4, DX4), (3, 2 * DX4), (2, 4 * DX4), (1, 8 * DX4), (0, 16 * DX4)):
                s = np.abs(h - hh) < 1e-6
                if s.any():
                    per[str(lev)] = {"max_alternating": float(np.nanmax(amp[s])),
                                     "max_abs": float(np.abs(fv[s]).max())}
            rec[v] = per
        lines[os.path.basename(f)] = rec
        lines[os.path.basename(f)]["_arrays"] = (x, {v: d[v][o] for v in
                                                    ("z4c_betax", "z4c_Gamx", "z4c_alpha")})
    res["P0L_lines"] = {k: {kk: vv for kk, vv in v.items() if kk != "_arrays"}
                        for k, v in lines.items()}
    with open(os.path.join(args.out, "card_onset.json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.28, hspace=0.3)
    col = {"P0L": fs.PAL["red"], "S1L": fs.PAL["blue"]}
    ax = axs[0, 0]
    for mem in ("P0L", "S1L"):
        t, r, tc, h = series[mem]
        ax.plot(t, r, color=col[mem], label=mem)
    ax.axhline(thr, **fs.GUIDE)
    ax.text(0.1, thr + 0.02, "Test B threshold (shift, KO)", fontsize=8)
    ax.set_xlim(0, 3.0)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\Delta t/\Delta x_4$ (level 4)")
    ax.legend(loc="lower right")
    ax = axs[0, 1]
    for mem in ("P0L", "S1L"):
        t, r, tc, h = series[mem]
        ax.semilogy(tc, h, "o-", ms=3, color=col[mem], label=mem + r": $H_{\max}$ (cstat)")
        if mem + "_lnA" in series:
            ta, lnA = series[mem + "_lnA"]
            j = res["members"][mem]["first_cstat_Hmax_above_10x_baseline"]
            # linear amplification scaled to pass through the first jump line
            k = np.searchsorted(ta, j["t"])
            ax.semilogy(ta, j["Hmax"] * np.exp(lnA - lnA[k]), ls="--", color=col[mem],
                        lw=1.0, label=mem + ": Test B amplification (scaled)")
    ax.set_xlim(1.5, 3.0)
    ax.set_ylim(1e-3, 1e4)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$H_{\max}$")
    ax.legend(loc="upper left", fontsize=8)
    for ax, var, lab in ((axs[1, 0], "z4c_betax", r"$\beta^x$"),
                         (axs[1, 1], "z4c_Gamx", r"$\tilde\Gamma^x$")):
        cs_ = fs.series_colors(3)
        for i, key in enumerate(("peak.z4c.00001.tab", "peak.z4c.00002.tab")):
            if key not in lines:
                continue
            x, arr = lines[key]["_arrays"]
            s = np.abs(x) < 1.6
            ax.plot(x[s], arr[var][s], ".-", ms=2.5, lw=0.8,
                    color=[fs.PAL["blue"], fs.PAL["red"]][i],
                    label="t = %.2f" % lines[key]["t"])
        for b in (0.625, 1.25):
            ax.axvline(b, **fs.MASK_LINE)
            ax.axvline(-b, **fs.MASK_LINE)
        ax.set_xlabel("x (y = z = 0)")
        ax.set_ylabel(lab)
        ax.set_yscale("symlog", linthresh=1e-2)
        ax.legend(loc="lower right", fontsize=8)
    fig.savefig(os.path.join(args.out, "fig_card_onset.png"))
    print(json.dumps({k: v for k, v in res.items() if k != "P0L_lines"}, indent=1))
    for k, v in res["P0L_lines"].items():
        print(k, v["t"], {var: v[var].get("4") for var in ("z4c_betax", "z4c_Gamx", "z4c_alpha")})


if __name__ == "__main__":
    main()
