#!/usr/bin/env python3
"""Package step-limit, tests T3 and T4: Track A's decks without and with <z4c> dt_gauge.

For every run: the step against the finest cell, the largest Hamiltonian constraint of
the constraint statistics, the extremes of the lapse, the cell-to-cell alternating part
of beta^x, Gam^x and alpha on the line outputs (finest cells only), the number of cycles
and the messages of the step limit in the log.  Onset of growth, as Track A defined it
(periodic_diag/scripts/analyse_runs.py): the first record after t = 1 whose H_max exceeds
ten times the median of H_max over 0.3 < t < 2.

  python analyse_runs.py --run LABEL=DIR[:DX] [--run ...] --out DIR [--name NAME]
         [--tmax T] [--bound B] [--basename peak]

DX: finest cell of the run (default 0.3125); --bound: a stability bound in cells, drawn
in the first panel.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def load_hst(path):
    names, rows = [], []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                found = re.findall(r"\[\d+\]=(\S+)", ln)
                if found:
                    names = found
                continue
            try:
                rows.append([float(x) for x in ln.split()])
            except ValueError:
                pass
    n = min(len(r) for r in rows) if rows else 0
    return names, np.array([r[:n] for r in rows])


def load_tab(path):
    with open(path) as f:
        head = f.readline()
        cols = f.readline().lstrip("#").split()
        data = np.loadtxt(f, ndmin=2)
    t = float(re.search(r"time=([-+.0-9eE]+)", head).group(1))
    cyc = int(re.search(r"cycle=(\d+)", head).group(1))
    return t, cyc, {c: data[:, i] for i, c in enumerate(cols)}


def alternating(x, u):
    """|u_i - (u_(i-1) + u_(i+1))/2|/2 at the points whose two neighbours are equally
    far (amplitude A for u_i = A (-1)^i), and that spacing."""
    hl = x[1:-1] - x[:-2]
    hr = x[2:] - x[1:-1]
    amp = np.abs(u[1:-1] - 0.5 * (u[:-2] + u[2:])) / 2.0
    ok = np.abs(hl - hr) < 1e-6 * np.abs(hl)
    return np.where(ok, amp, np.nan), hl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="runs")
    ap.add_argument("--tmax", type=float, default=12.0)
    ap.add_argument("--bound", type=float, action="append", default=[])
    ap.add_argument("--basename", default="peak")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    bn = args.basename
    res, data = {}, {}
    for spec in args.run:
        lab, rest = spec.split("=", 1)
        d, dx = (rest.rsplit(":", 1) + [None])[:2] if ":" in rest else (rest, None)
        dx = float(dx) if dx else 0.3125
        cn, nh = load_hst(os.path.join(d, bn + ".nrpic.hst"))
        t = nh[:, cn.index("time")]
        amin, amax = nh[:, cn.index("alpha_min")], nh[:, cn.index("alpha_max")]
        r = np.diff(t) / dx
        cs, cst = load_hst(os.path.join(d, bn + ".cstat.hst"))
        tc, hmax = cst[:, 0], cst[:, cs.index("H_max")]
        sel = (tc > 0.3) & (tc < 2.0)
        base = float(np.median(hmax[sel])) if sel.any() else float("nan")
        big = np.nonzero((hmax > 10 * base) & (tc > 1.0))[0]
        log = open(os.path.join(d, "athena.log")).read()
        msgs = [ln for ln in log.splitlines() if "Z4c step limit" in ln]
        fin = np.isfinite(hmax)
        rec = {"dir": d, "dx": dx, "last_t": float(t[-1]), "steps": int(len(t) - 1),
               "guard_stop": "NRPIC guard" in log,
               "dt_over_dx_max": float(r.max()) if r.size else None,
               "dt_over_dx_last": float(r[-1]) if r.size else None,
               "Hmax_baseline": base, "Hmax_last": float(hmax[-1]),
               "Hmax_largest_finite": float(hmax[fin].max()) if fin.any() else None,
               "alpha_min_last": float(amin[-1]), "alpha_max_last": float(amax[-1]),
               "onset_t": float(tc[big[0]]) if big.size else None,
               "step_limit_messages": [m[:400] for m in msgs]}
        m = re.search(r"cpu time used\s*=\s*([-+.0-9eE]+)", log)
        rec["cpu_time_s"] = float(m.group(1)) if m else None
        lines = []
        for f in sorted(glob.glob(os.path.join(d, "tab", bn + ".z4c.*.tab"))):
            try:
                tt, cy, dd = load_tab(f)
            except Exception:
                continue
            x = dd["x1v"]
            o = np.argsort(x)
            x = x[o]
            row = {"t": tt, "cycle": cy}
            for v in ("z4c_betax", "z4c_Gamx", "z4c_alpha"):
                amp, h = alternating(x, dd[v][o])
                s = (np.abs(h - dx) < 1e-3 * dx) & np.isfinite(amp)
                row[v] = float(amp[s].max()) if s.any() else None
            lines.append(row)
        rec["lines_alternating_finest"] = lines
        res[lab] = rec
        data[lab] = (t, r, tc, hmax, amin, amax)
    with open(os.path.join(args.out, args.name + ".json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
    import figstyle as fs
    fs.use_style()
    labs = list(res)
    cols = dict(zip(labs, (fs.SERIES + ["k", "grey"]) * 2))
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.96, wspace=0.28,
                        hspace=0.3)
    for lab in labs:
        t, r, tc, hmax, amin, amax = data[lab]
        axs[0, 0].plot(t[1:], r, color=cols[lab], label=lab)
        hh = np.where(np.isfinite(hmax) & (hmax < 1e8) & (hmax > 0), hmax, np.nan)
        axs[0, 1].semilogy(tc, hh, color=cols[lab], label=lab)
        axs[1, 0].plot(t, np.clip(amin, -1, 10), color=cols[lab], label=lab)
        axs[1, 0].plot(t, np.clip(amax, -1, 10), color=cols[lab], ls="--", lw=1.0)
    for b in args.bound:
        axs[0, 0].axhline(b, **fs.GUIDE)
    axs[0, 0].set_ylabel(r"$\Delta t/\Delta x$ (finest cells)")
    axs[0, 0].set_ylim(0.0, 1.1)
    axs[0, 1].set_ylabel(r"largest $|H|$ (constraint statistics)")
    axs[0, 1].set_ylim(1e-4, 1e4)
    axs[1, 0].set_ylabel(r"$\alpha_{\min}$ (solid), $\alpha_{\max}$ (dashed)")
    axs[1, 0].set_ylim(0.0, 1.6)
    for ax in (axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]):
        ax.set_xlabel("t")
        ax.set_xlim(0, args.tmax)
    axs[0, 0].legend(loc="lower right", fontsize=8)
    ax = axs[1, 1]
    for lab in labs:
        rows = res[lab]["lines_alternating_finest"]
        tt = [q["t"] for q in rows if q["z4c_betax"] is not None]
        bb = [min(max(q["z4c_betax"], 1e-16), 1e8) for q in rows
              if q["z4c_betax"] is not None]
        aa = [min(max(q["z4c_alpha"], 1e-16), 1e8) for q in rows
              if q["z4c_alpha"] is not None]
        ax.semilogy(tt, bb, "o-", ms=3, color=cols[lab], label=lab + r": $\beta^x$")
        ax.semilogy(tt[:len(aa)], aa, "s--", ms=2.5, lw=1.0, color=cols[lab],
                    label=lab + r": $\alpha$")
    ax.set_ylabel("cell-to-cell alternation on the line (finest cells)")
    ax.set_ylim(1e-10, 1e2)
    ax.legend(loc="upper left", fontsize=6.5, ncol=2)
    fig.savefig(os.path.join(args.out, "fig_" + args.name + ".png"), dpi=150)
    for lab, rec in res.items():
        print(lab, {k: rec[k] for k in ("last_t", "steps", "guard_stop", "dt_over_dx_max",
                                         "dt_over_dx_last", "Hmax_baseline", "Hmax_last",
                                         "Hmax_largest_finite", "onset_t", "cpu_time_s")})
        for m in rec["step_limit_messages"]:
            print("   ", m[:300])
        al = [q for q in rec["lines_alternating_finest"] if q["z4c_betax"] is not None]
        if al:
            print("    alternation of beta^x: first %.2e (t=%.2f) largest %.2e last %.2e "
                  "(t=%.2f); alpha: largest %.2e" % (
                      al[0]["z4c_betax"], al[0]["t"], max(q["z4c_betax"] for q in al),
                      al[-1]["z4c_betax"], al[-1]["t"],
                      max((q["z4c_alpha"] or 0.0) for q in al)))


if __name__ == "__main__":
    main()
