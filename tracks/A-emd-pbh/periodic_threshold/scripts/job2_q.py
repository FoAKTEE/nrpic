#!/usr/bin/env python3
"""Card job 2 of periodic_threshold (P0L and S1L at cfl_number 0.5): predictions Q1-Q3 of
JOURNAL.md entry 2026-11-21 23:15Z, judged from the chain outputs.

    python -I job2_q.py --run P0L=DIR [--run S1L=DIR] --out DIR

Q1 (remedy): (a) the L2 norm of H (peak.z4c.user.hst, H-norm2) never jumps by more than a
factor 10 between consecutive records for t in [1.5, 6]; (b) H_max (peak.cstat.hst) below 0.1
to t = 5; (c) the step dt (peak.nrpic.hst, every cycle) at most 0.5 dx of level 4; (d) no
grid-scale (odd-even) pattern in beta^x or alpha on the x line outputs (tab/peak.z4c.*.tab)
at t = 2, 4, 6, 8, 10: the odd-even amplitude is estimated per point as the 8-point running
mean of (-1)^i (f_{i-1} - 2 f_i + f_{i+1})/4 on runs of equal spacing (a smooth f gives about
zero, an odd-even mode of amplitude a gives a), divided by the largest |f| on that level.
Q2: last time reached, no guard stop or non-finite field in the segment logs.
Q3: cost per step from the segment logs ("cpu time used" against cycles of the segment).

Chains that restarted from an older restart file repeat times in their histories: the
records written last win (a row is kept when its time is below that of the next kept row,
reading backwards).

Also written: the history around the jump of H_r near t = 48-52 of P0L (cstat, nrpic).
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DX4 = 20.0 / 64 / 16  # level-4 cell size of peak_leak.athinput (0.01953125)


def load_hst(path):
    cols = []
    with open(path) as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            if "[1]=" in ln:
                cols = [c.split("=")[1] for c in ln.strip("# \n").split() if "=" in c]
    data = np.loadtxt(path, comments="#", ndmin=2)
    return cols, last_written(data)


def last_written(d):
    """Rows of a history in time order, the latest-written copy of every repeated time span."""
    keep = []
    tnext = np.inf
    for i in range(d.shape[0] - 1, -1, -1):
        if d[i, 0] < tnext:
            keep.append(i)
            tnext = d[i, 0]
    return d[keep[::-1]]


def load_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    cyc = int(first.split("cycle=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, cyc, {n: d[:, i] for i, n in enumerate(names)}


def odd_even(x, f, win=8):
    """Odd-even amplitude per point and the spacing there (see module docstring)."""
    dx = np.diff(x)
    n = len(f)
    hp = np.full(n, np.nan)
    h = np.full(n, np.nan)
    for i in range(1, n - 1):
        if abs(dx[i - 1] - dx[i]) < 1e-3 * dx[i]:
            hp[i] = (f[i - 1] - 2 * f[i] + f[i + 1]) / 4.0 * (-1) ** i
            h[i] = dx[i]
    amp = np.full(n, np.nan)
    for i in range(n):
        lo, hi = max(0, i - win // 2), min(n, i + win // 2)
        seg, hs = hp[lo:hi], h[lo:hi]
        if np.all(np.isfinite(seg)) and np.all(np.abs(hs - hs[0]) < 1e-3 * hs[0]):
            amp[i] = abs(seg.mean())
    return amp, h


def seg_logs(run):
    return sorted(glob.glob(os.path.join(run, "chain", "seg*.log")))


def cost(run):
    out = []
    for lg in seg_logs(run):
        txt = open(lg, errors="replace").read()
        cyc = [int(m) for m in re.findall(r"cycle=(\d+) time=", txt)]
        cpu = re.findall(r"cpu time used\s*=\s*([0-9.e+-]+)", txt)
        el = re.findall(r"elapsed=([0-9.e+-]+) cycle=(\d+)", txt)
        rec = {"log": os.path.basename(lg), "first_cycle": cyc[0] if cyc else None,
               "last_cycle": cyc[-1] if cyc else None,
               "terminated": ("Terminating on time limit" in txt),
               "guard": bool(re.search(r"z4c_guard|guard.*stop|not finite", txt, re.I)),
               "nan": bool(re.search(r"\bnan\b", txt.split("Setup complete")[-1], re.I))}
        if cpu and len(cyc) > 1:
            rec["cpu_s"] = float(cpu[-1])
            rec["s_per_step"] = float(cpu[-1]) / max(1, cyc[-1] - cyc[0])
        elif len(el) > 1:
            (e0, c0), (e1, c1) = el[0], el[-1]
            if int(c1) > int(c0):
                rec["s_per_step_elapsed"] = (float(e1) - float(e0)) / (int(c1) - int(c0))
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="LABEL=DIR")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    res = {"dx_level4": DX4, "members": {}}
    S = {}
    for spec in args.run:
        lab, run = spec.split("=", 1)
        cz, zh = load_hst(os.path.join(run, "peak.z4c.user.hst"))
        cs, cst = load_hst(os.path.join(run, "peak.cstat.hst"))
        cn, nh = load_hst(os.path.join(run, "peak.nrpic.hst"))
        tz, Hn = zh[:, 0], zh[:, cz.index("H-norm2")]
        tc, Hmax, Hrmax = cst[:, 0], cst[:, cs.index("H_max")], cst[:, cs.index("Hr_max")]
        chimin = cst[:, cs.index("chi_min")]
        tn = nh[:, cn.index("time")]
        dt = np.diff(tn)
        r = dt / DX4
        m = {"t_last": float(tn[-1]), "ncycle_last": int(nh[-1, cn.index("ncycle")])}
        w = (tz >= 1.5) & (tz <= 6.0)
        ratio = Hn[1:] / Hn[:-1]
        ww = w[1:] & w[:-1]
        m["Q1a_max_ratio_Hnorm2_consecutive_t1.5_6"] = float(ratio[ww].max()) if ww.any() else None
        m["Q1a_n_records_t1.5_6"] = int(w.sum())
        wc = (tc >= 1.5) & (tc <= 6.0)
        rc = Hmax[1:] / Hmax[:-1]
        m["Q1a_cstat_max_ratio_Hmax_consecutive_t1.5_6"] = float(rc[(wc[1:] & wc[:-1])].max())
        m["Q1b_Hmax_max_t_le_5"] = float(Hmax[(tc > 0.0) & (tc <= 5.0)].max())
        m["Q1b_Hmax_t0"] = float(Hmax[0])
        m["Q1b_Hmax_max_t_le_5_over_t0"] = float(Hmax[(tc > 0.0) & (tc <= 5.0)].max() / Hmax[0])
        m["Hmax_at_t"] = {str(tt): float(np.interp(tt, tc, Hmax)) for tt in (1, 2, 2.4, 3, 5, 10, 20, 50)}
        m["Q1c_max_dt_over_dx4"] = float(r.max())
        m["Q1c_median_dt_over_dx4_t_gt_5"] = float(np.median(r[tn[:-1] > 5]))
        m["Hnorm2_max"] = float(Hn.max())
        m["Hr_max_max"] = float(Hrmax.max())
        # jump of Hr: largest single-record rise of H_r max after t = 10
        jr = Hrmax[1:] / Hrmax[:-1]
        jr[tc[1:] < 10.0] = 0.0
        k = int(np.argmax(jr))
        m["largest_Hr_rise"] = {"t": float(tc[k + 1]), "from": float(Hrmax[k]),
                                "to": float(Hrmax[k + 1]), "factor": float(jr[k])}
        # line outputs: odd-even amplitude of beta^x and alpha per level at t ~ 2..10, and later
        tabs = sorted(glob.glob(os.path.join(run, "tab", "peak.z4c.*.tab")))
        lines = []
        gxx_max = []
        for f in tabs:
            t, cy, d = load_tab(f)
            x = d["x1v"]
            o = np.argsort(x)
            x = x[o]
            rec = {"t": t, "cycle": cy, "file": os.path.basename(f)}
            for v in ("z4c_betax", "z4c_alpha"):
                fv = d[v][o]
                amp, h = odd_even(x, fv)
                per = {}
                for lev in range(5):
                    hh = DX4 * 2 ** (4 - lev)
                    s = np.abs(h - hh) < 1e-3 * hh
                    if s.any() and np.isfinite(amp[s]).any():
                        scale = max(np.abs(fv[s]).max(), 1e-300)
                        per[str(lev)] = {"odd_even_max": float(np.nanmax(amp[s])),
                                         "rel": float(np.nanmax(amp[s]) / scale)}
                rec[v] = per
            gxx_max.append((t, float(d["z4c_gxx"].max())))
            lines.append(rec)
        sel = {}
        for tt in (2, 4, 6, 8, 10):
            if lines:
                j = int(np.argmin([abs(l["t"] - tt) for l in lines]))
                if abs(lines[j]["t"] - tt) < 1.0:
                    sel[str(tt)] = lines[j]
        m["Q1d_lines"] = sel
        rel4 = [max(l[v].get("4", {}).get("rel", 0.0) for v in ("z4c_betax",))
                for l in sel.values()]
        m["Q1d_max_rel_odd_even_betax_level4_t2_10"] = float(max(rel4)) if rel4 else None
        rel_all = [(l["t"], v, lev, q["rel"]) for l in lines for v in ("z4c_betax", "z4c_alpha")
                   for lev, q in l[v].items()]
        if rel_all:
            mx = max(rel_all, key=lambda q: q[3])
            m["odd_even_max_rel_any_line"] = {"t": mx[0], "var": mx[1], "level": mx[2], "rel": mx[3]}
        m["gxx_max_on_x_line"] = max(gxx_max, key=lambda q: q[1]) if gxx_max else None
        m["segments"] = cost(run)
        m["Q2_guard_or_nan_in_logs"] = any(s["guard"] or s["nan"] for s in m["segments"])
        S[lab] = dict(tz=tz, Hn=Hn, tc=tc, Hmax=Hmax, Hrmax=Hrmax, chimin=chimin, tn=tn, r=r,
                      lines=lines, run=run, nh=nh, cn=cn)
        res["members"][lab] = m
    with open(os.path.join(args.out, "job2_q.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("Q1d_lines", "segments")}
                      for k, v in res["members"].items()}, indent=1))
    for k, v in res["members"].items():
        for s in v["segments"]:
            print(k, s)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    col = {"P0L": fs.PAL["red"], "S1L": fs.PAL["blue"]}
    fig, axs = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 8.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.06, top=0.97, wspace=0.3, hspace=0.38)
    ax = axs[0, 0]
    for lab, s in S.items():
        ax.semilogy(s["tz"], s["Hn"], color=col.get(lab, "k"), label=lab)
    ax.axvspan(1.5, 6.0, color="0.9", zorder=0)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\|H\|_2$ (z4c history)")
    ax.set_title("(a) Q1a: no jump in the shaded window", fontsize=9)
    ax.legend(loc="lower right")
    ax = axs[0, 1]
    for lab, s in S.items():
        sel = s["tc"] <= 10
        ax.semilogy(s["tc"][sel], s["Hmax"][sel], color=col.get(lab, "k"), label=lab)
    ax.axhline(0.1, **fs.GUIDE)
    ax.axvline(5.0, **fs.MASK_LINE)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$H_{\max}$ (cstat)")
    ax.set_title(r"(b) Q1b: $H_{\max}<0.1$ to $t=5$", fontsize=9)
    ax = axs[1, 0]
    for lab, s in S.items():
        ax.plot(s["tn"][:-1], s["r"], color=col.get(lab, "k"), lw=0.8, label=lab)
    ax.axhline(0.5, **fs.GUIDE)
    ax.axhline(0.685, color=fs.PAL["red"], ls=":", lw=0.8)
    ax.text(1, 0.695, "Test B threshold 0.685", fontsize=7)
    ax.set_ylim(0, 0.8)
    ax.set_xscale("symlog", linthresh=1.0)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\Delta t/\Delta x_4$")
    ax.set_title("(c) Q1c: step on level 4", fontsize=9)
    ax = axs[1, 1]
    for lab, s in S.items():
        t = [l["t"] for l in s["lines"]]
        for v, ls in (("z4c_betax", "-"), ("z4c_alpha", "--")):
            y = [max([q["rel"] for q in l[v].values()] or [np.nan]) for l in s["lines"]]
            ax.semilogy(t, y, ls, color=col.get(lab, "k"), lw=1.0,
                        label="%s %s" % (lab, r"$\beta^x$" if v == "z4c_betax" else r"$\alpha$"))
    ax.set_xlabel("t")
    ax.set_ylabel("odd-even amplitude / max|f| (any level)")
    ax.set_title("(d) Q1d: grid-scale pattern on the x line", fontsize=9)
    ax.legend(loc="lower right", fontsize=7)
    ax = axs[2, 0]
    lab0 = "P0L" if "P0L" in S else list(S)[0]
    s = S[lab0]
    cs_ = fs.series_colors(5)
    for i, tt in enumerate((2, 4, 6, 8, 10)):
        if not s["lines"]:
            break
        j = int(np.argmin([abs(l["t"] - tt) for l in s["lines"]]))
        f = os.path.join(s["run"], "tab", s["lines"][j]["file"])
        t, cy, d = load_tab(f)
        o = np.argsort(d["x1v"])
        x = d["x1v"][o]
        sl = np.abs(x) < 2.0
        ax.plot(x[sl], d["z4c_betax"][o][sl], ".-", ms=1.5, lw=0.6, color=cs_[i],
                label="t = %.2f" % t)
    ax.set_xlabel("x (y = z = 0)")
    ax.set_ylabel(r"$\beta^x$ (%s)" % lab0)
    ax.set_title(r"(e) $\beta^x$ lines near the centre", fontsize=9)
    ax.legend(loc="best", fontsize=7)
    ax = axs[2, 1]
    for lab, s in S.items():
        ax.semilogy(s["tc"], s["Hrmax"], color=col.get(lab, "k"), label=lab + r": $H_r$ max")
        ax.semilogy(s["tc"], s["chimin"], ":", color=col.get(lab, "k"), lw=0.8,
                    label=lab + r": $\chi_{\min}$")
    ax.set_xlabel("t")
    ax.set_title(r"(f) relative $H$ and $\chi_{\min}$ over the run", fontsize=9)
    ax.legend(loc="lower left", fontsize=7)
    fig.savefig(os.path.join(args.out, "fig_job2_q.png"), dpi=150)


if __name__ == "__main__":
    main()
