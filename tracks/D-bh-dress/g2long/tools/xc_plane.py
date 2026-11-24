#!/usr/bin/env python3
"""Constraint norms OUTSIDE the horizon from the z = 0 slices of the long runs (entry 10, test XC).

The history norms of `<base>.z4c.user.hst` skip chi < 0.0625 and are dominated by the region
just inside the horizon (entry 8). Every long run also wrote the constraint variables on the
slice z = 0.001 every 25 M (`<base>.con.<n>.bin`: con_C, con_H, con_M, con_Z, con_Mx..z).
Here, for each slice, the plane L2 norms
    ||H||_A = ( sum_A H^2 dx dy / sum_A dx dy )^(1/2),  ||M||_A = ( sum_A con_M dx dy / sum_A dx dy )^(1/2)
(con_M is already the square g_ab M^a M^b, athenak/src/z4c/z4c_adm.cpp:513),
over three annuli of coordinate radius r = (x^2 + y^2)^(1/2):
    A1 = [1.2 r_AH(t), 6 M]    (outside the horizon, inside the refined region)
    A2 = [6 M, 30 M]
    A3 = [30 M, 100 M]          (the dust wall of ES-1 at 36-44 M, outer edge 52-60 M)
with r_AH(t) the finder's mean coordinate radius at the nearest sample (2.0 M if none).
AthenaK MeshBlocks are leaves of the tree, so every point of the plane is counted once.

Usage: xc_plane.py --out DIR NAME=RUNDIR:BASE[:H] ...   (H: finest spacing in M, for the
convergence panel; e.g. V-1L=$S/<id>:v1l:0.125). Writes xc_plane.json, xc_plane.png.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/athenak/vis/python")
import bin_convert  # noqa: E402
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ANN = {"A1": (None, 6.0), "A2": (6.0, 30.0), "A3": (30.0, 100.0)}


def horizon_radius(rd, base):
    p = os.path.join(rd, base + ".horizon_summary_0.txt")
    if not os.path.exists(p):
        return None
    a = np.loadtxt(p, comments="#", ndmin=2)
    return a[:, 1], a[:, 10]


def radius_at(hz, t):
    if hz is None:
        return 2.0
    tt, rr = hz
    ok = np.isfinite(rr) & (rr > 0)
    if not ok.any():
        return 2.0
    return float(rr[ok][int(np.argmin(np.abs(tt[ok] - t)))])


def norms(path, hz):
    fd = bin_convert.read_binary(path)
    t = float(fd["time"])
    rah = radius_at(hz, t)
    nmb = (fd["nx1_mb"], fd["nx2_mb"])
    acc = {k: np.zeros(3) for k in ANN}       # sum w, sum w H^2, sum w M^2
    rin = 1.2 * rah
    for b in range(fd["n_mbs"]):
        g = fd["mb_geometry"][b]
        ix = fd["mb_index"][b]
        dx = (g[1] - g[0]) / nmb[0]
        dy = (g[3] - g[2]) / nmb[1]
        H = np.asarray(fd["mb_data"]["con_H"][b], dtype=float)[0]
        Mc = np.asarray(fd["mb_data"]["con_M"][b], dtype=float)[0]
        n2, n1 = H.shape
        xc = g[0] + (ix[0] + np.arange(n1) + 0.5) * dx
        yc = g[2] + (ix[2] + np.arange(n2) + 0.5) * dy
        X, Y = np.meshgrid(xc, yc)
        r = np.hypot(X, Y)
        w = dx * dy
        for k, (lo, hi) in ANN.items():
            lo = rin if lo is None else lo
            s = (r >= lo) & (r < hi) & np.isfinite(H) & np.isfinite(Mc)
            if s.any():
                acc[k] += [w * s.sum(), w * np.sum(H[s] ** 2), w * np.sum(Mc[s])]   # con_M = g_ab M^a M^b
    out = dict(t=t, r_AH=rah)
    for k, v in acc.items():
        out[k] = dict(H2=float(np.sqrt(v[1] / v[0])) if v[0] > 0 else None,
                      M2=float(np.sqrt(v[2] / v[0])) if v[0] > 0 else None, area=float(v[0]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        parts = rest.split(":")
        rd, base = parts[0], parts[1]
        h = float(parts[2]) if len(parts) > 2 else None
        hz = horizon_radius(rd, base)
        rows = []
        for p in sorted(glob.glob(os.path.join(rd, "bin", f"{base}.con.[0-9]*.bin"))):
            rows.append(norms(p, hz))
        R[name] = dict(dir=rd, base=base, h=h, rows=rows)
        print(name, len(rows), "slices")
    # summary: growth from 100 M to the end, largest rise within 25 M, values at 100/200/300 M
    summ = {}
    for k, v in R.items():
        t = np.array([r["t"] for r in v["rows"]])
        d = {}
        for ann in ANN:
            h2 = np.array([r[ann]["H2"] if r[ann]["H2"] is not None else np.nan for r in v["rows"]])
            m2 = np.array([r[ann]["M2"] if r[ann]["M2"] is not None else np.nan for r in v["rows"]])
            w = t >= 100.0 - 1e-9
            e = dict()
            if w.any():
                e["H_growth_100_end"] = float(h2[w][-1] / h2[w][0])
                e["M_growth_100_end"] = float(m2[w][-1] / m2[w][0])
                e["H_max_over_100"] = float(np.nanmax(h2[w]) / h2[w][0])
                e["M_max_over_100"] = float(np.nanmax(m2[w]) / m2[w][0])
                rh = h2[w][1:] / h2[w][:-1]
                e["H_largest_step_ratio"] = float(np.nanmax(rh)) if rh.size else None
            for tt in (100.0, 200.0, 300.0):
                i = np.nonzero(np.abs(t - tt) < 1e-6)[0]
                if i.size:
                    e[f"H2_{int(tt)}"] = float(h2[i[0]])
                    e[f"M2_{int(tt)}"] = float(m2[i[0]])
            d[ann] = e
        summ[k] = d
    with open(os.path.join(a.out, "xc_plane.json"), "w") as f:
        json.dump(dict(annuli={k: list(v) for k, v in ANN.items()}, runs=R, summary=summ), f, indent=1)
    print(json.dumps(summ, indent=1))
    figure(a.out, R)


def figure(outdir, R):
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.6), constrained_layout=True)
    cols = fs.series_colors(len(R))
    for (k, v), c in zip(R.items(), cols):
        t = np.array([r["t"] for r in v["rows"]])
        ls = "--" if k.startswith("ES-FL") else (":" if k.startswith("ES") else "-")
        for j, ann in enumerate(ANN):
            h2 = np.array([r[ann]["H2"] if r[ann]["H2"] is not None else np.nan for r in v["rows"]])
            m2 = np.array([r[ann]["M2"] if r[ann]["M2"] is not None else np.nan for r in v["rows"]])
            ax[0, j].semilogy(t, h2, ls, color=c, lw=1.0, label=k)
            ax[1, j].semilogy(t, m2, ls, color=c, lw=1.0, label=k)
    for j, ann in enumerate(ANN):
        lo, hi = ANN[ann]
        lab = (r"$1.2\,r_{\rm AH}$" if lo is None else f"{lo:g} M") + f" - {hi:g} M"
        ax[0, j].set_title(f"({'abc'[j]}) $\\|H\\|$ on {lab}", loc="left", fontsize=9)
        ax[1, j].set_title(f"({'def'[j]}) $\\|M\\|$ on {lab}", loc="left", fontsize=9)
        ax[1, j].set_xlabel(r"$t/M$")
    ax[0, 0].set_ylabel("plane L2 norm (z = 0)")
    ax[1, 0].set_ylabel("plane L2 norm (z = 0)")
    ax[0, 2].legend(fontsize=6, frameon=False, ncol=1)
    fs.save(fig, os.path.join(outdir, "xc_plane"))
    plt.close(fig)


if __name__ == "__main__":
    main()
