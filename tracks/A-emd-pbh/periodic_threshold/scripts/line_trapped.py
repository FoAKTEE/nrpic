#!/usr/bin/env python3
"""F1 of periodic_threshold (JOURNAL 2026-11-24 13:25Z): trapped spheres on P0L's slices, from
the Misner-Sharp mass along the x line of the z4c line outputs.

    python -I line_trapped.py --run DIR --out DIR [--label P0L]

Physical metric gamma_ij = gt_ij / chi, K_ij = (At_ij + gt_ij K / 3) / chi with K = Khat + 2 Theta
(Z4c variables of AthenaK). Line points: cell centres of the tab output (slice_x2 = slice_x3 =
0.001 picks the first cell of each level, so a point of level l sits at y = z = h_l / 2), levels
of inputs/peak_leak.athinput: half-widths 10, 5, 2.5, 1.25, 0.625 and cells 20/64 / 2^l.
Misner-Sharp mass, compactness 2m/R and trapped points (2m/R > 1 with K_T > 0) from
conv_ball/scripts/common.misner_sharp_line (unchanged). For every line output: the largest 2m/R,
the outermost marginally trapped sphere (r, R, m), and R at r = 0.45 (where the deck's finder
stalled). Figure: R(r), 2m/R(r), m(r) at t = 80, 100, 120, 140 and the history of the outermost
trapped sphere's mass.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "conv_ball", "scripts"))
import common as C  # noqa: E402

LEVELS = [(10.0, 20.0 / 64 / 2 ** l) if l == 0 else (10.0 / 2 ** l, 20.0 / 64 / 2 ** l) for l in range(5)]


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def points(x1):
    h = np.full_like(x1, LEVELS[0][1])
    for b, hl in LEVELS[1:]:
        h = np.where(np.abs(x1) < b, hl, h)
    return np.stack([x1, 0.5 * h, 0.5 * h], axis=-1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="P0L")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, keep = [], {}
    for f in sorted(glob.glob(os.path.join(a.run, "tab", "peak.z4c.*.tab"))):
        t, d = read_tab(f)
        x1 = d["x1v"]
        o = np.argsort(x1)
        d = {k: v[o] for k, v in d.items()}
        x = points(d["x1v"])
        pos = x[:, 0] > 0
        chi = d["z4c_chi"][pos]
        gt = np.stack([d["z4c_g" + c][pos] for c in ("xx", "xy", "xz", "yy", "yz", "zz")], -1)
        At = np.stack([d["z4c_A" + c][pos] for c in ("xx", "xy", "xz", "yy", "yz", "zz")], -1)
        K = d["z4c_Khat"][pos] + 2.0 * d["z4c_Theta"][pos]
        g = gt / chi[:, None]
        Kij = (At + gt * K[:, None] / 3.0) / chi[:, None]
        ms = C.misner_sharp_line(x[pos], g, Kij)
        r, R, m, c = ms["r"], ms["R"], ms["m"], ms["compact"]
        tr = np.nonzero(ms["trapped"])[0]
        rec = dict(t=t, max_compact=float(np.nanmax(c)), r_at_max=float(r[int(np.nanargmax(c))]),
                   n_trapped=int(len(tr)), R_at_r045=float(np.interp(0.45, r, R)),
                   chi_min=float(chi.min()), alpha_c=float(d["z4c_alpha"][pos][0]) if "z4c_alpha" in d else None)
        if len(tr):
            j = tr.max()
            if j + 1 < len(r):
                w = (c[j] - 1.0) / (c[j] - c[j + 1]) if c[j] != c[j + 1] else 0.0
                rec["outer_mts"] = dict(r=float(r[j] + w * (r[j + 1] - r[j])), R=float(R[j] + w * (R[j + 1] - R[j])),
                                        m=float(m[j] + w * (m[j + 1] - m[j])))
            rec["inner_trapped_r"] = float(r[tr.min()])
        rows.append(rec)
        for tt in (80, 100, 120, 140):
            if abs(t - tt) < 1.0:
                keep[tt] = (r, R, m, c, ms["KT"])
    first = next((q for q in rows if q["n_trapped"] > 0), None)
    res = dict(run=a.run, label=a.label, n_lines=len(rows), first_trapped_t=first["t"] if first else None,
               rows=rows)
    json.dump(res, open(os.path.join(a.out, "line_trapped.json"), "w"), indent=1)
    for q in rows[::4] + rows[-3:]:
        print(q["t"], round(q["max_compact"], 4), q["n_trapped"], q.get("outer_mts"), round(q["R_at_r045"], 3),
              q["chi_min"])
    print("first trapped line t:", res["first_trapped_t"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.35)
    cs = fs.series_colors(4)
    for i, tt in enumerate((80, 100, 120, 140)):
        if tt not in keep:
            continue
        r, R, m, c, KT = keep[tt]
        axs[0, 0].plot(r, R, color=cs[i], label="t = %d" % tt)
        axs[0, 1].plot(r, c, color=cs[i], label="t = %d" % tt)
        axs[1, 0].plot(r, m, color=cs[i], label="t = %d" % tt)
    axs[0, 0].axvline(0.45, **fs.MASK_LINE)
    axs[0, 0].set_xscale("log")
    axs[0, 0].set_yscale("log")
    axs[0, 0].set_xlabel("coordinate r (x line)")
    axs[0, 0].set_ylabel("areal radius R")
    axs[0, 0].set_title("(a) R(r); grey: finder's stall radius 0.45", fontsize=9)
    axs[0, 0].legend(fontsize=7)
    axs[0, 1].axhline(1.0, **fs.GUIDE)
    axs[0, 1].set_xscale("log")
    axs[0, 1].set_xlabel("coordinate r")
    axs[0, 1].set_ylabel("2m/R")
    axs[0, 1].set_title("(b) compactness; trapped above the dashed line", fontsize=9)
    axs[1, 0].set_xscale("log")
    axs[1, 0].set_yscale("symlog", linthresh=0.1)
    axs[1, 0].set_xlabel("coordinate r")
    axs[1, 0].set_ylabel("Misner-Sharp m")
    axs[1, 0].set_title("(c) m(r)", fontsize=9)
    ax = axs[1, 1]
    tt = [q["t"] for q in rows if "outer_mts" in q]
    mm = [q["outer_mts"]["m"] for q in rows if "outer_mts" in q]
    ax.plot(tt, mm, "o-", ms=3, color=fs.PAL["red"], label="outermost trapped sphere, line")
    ax.step([87, 90, 101, 119, 140], [0.25, 0.79, 1.74, 3.14, 3.14], where="post", color="k", lw=0.8, ls="--",
            label=r"$M_B$ of the outermost code shell with $R\leq 2M_B$ (read from fig_compare_ltb_P0L)")
    ax.set_xlabel("t")
    ax.set_ylabel("mass")
    ax.set_title("(d) slice-side horizon mass", fontsize=9)
    ax.legend(fontsize=7)
    fig.savefig(os.path.join(a.out, "fig_line_trapped.png"), dpi=150)


if __name__ == "__main__":
    main()
