#!/usr/bin/env python3
"""V3: fates of the five relativistic clusters (ladder row 4, met part) and one wave-2 member.

Own readers (column names from the header line of <base>.nrpic.hst; horizon summary
columns iter, time, mass). Central lapse: the hst column alpha_probe (probe at the
origin by default) and alpha_min, both reported.

usage: v3_clusters.py RUNS_ST_DIR WAVE2_DIR OUTDIR
"""
import json
import os
import re
import sys

import numpy as np


def read_hst(path):
    names = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") and "[1]=" in line:
                names = [m.group(1) for m in re.finditer(r"\[\d+\]=(\S+)", line)]
                break
    d = np.loadtxt(path, comments="#")
    return {n: d[:, i] for i, n in enumerate(names)}


def read_ah(path):
    if not os.path.exists(path):
        return np.array([]), np.array([])
    d = np.genfromtxt(path, comments="#")
    if d.ndim == 1:
        d = d[None, :]
    ok = np.isfinite(d[:, 2])
    return d[ok, 1], d[ok, 2]


def one(rundir, label):
    h = read_hst(os.path.join(rundir, "st.nrpic.hst"))
    t = h["time"]
    # a restarted run may repeat times: keep the last record of each time
    _, idx = np.unique(t[::-1], return_index=True)
    keep = np.sort(len(t) - 1 - idx)
    h = {k: v[keep] for k, v in h.items()}
    t = h["time"]
    ta, ma = read_ah(os.path.join(rundir, "st.horizon_summary_0.txt"))
    live = h["np"] > 0
    out = {"label": label, "t_last": float(t[-1]), "np_start": int(h["np"][0]), "np_end": int(h["np"][-1]),
           "alpha_probe_range_live": [float(h["alpha_probe"][live].min()), float(h["alpha_probe"][live].max())],
           "alpha_min_range_live": [float(h["alpha_min"][live].min()), float(h["alpha_min"][live].max())],
           "alpha_probe_t0": float(h["alpha_probe"][0])}
    if len(ta):
        out.update({"t_first_ah": float(ta[0]), "m_first_ah": float(ma[0]), "m_last_ah": float(ma[-1]),
                    "t_last_ah": float(ta[-1]), "n_ah": int(len(ta))})
    else:
        out["t_first_ah"] = None
    for t0 in (100.0, 200.0, 270.0, 300.0):
        if t0 <= t[-1] + 1e-6:
            i = int(np.argmin(np.abs(t - t0)))
            out[f"alpha_probe_at_{int(t0)}"] = [float(t[i]), float(h["alpha_probe"][i])]
    w = (t >= 200) & (t <= 300)
    if w.any():
        out["mean_alpha_probe_200_300"] = float(h["alpha_probe"][w].mean())
        out["mean_alpha_min_200_300"] = float(h["alpha_min"][w].mean())
    return out, (t, h["alpha_probe"], ta, ma)


def main():
    st, w2, outdir = sys.argv[1:4]
    os.makedirs(outdir, exist_ok=True)
    runs = {"0.900": os.path.join(st, "yc0900_v4"), "0.819": os.path.join(st, "yc0819_v4"),
            "0.605": os.path.join(st, "yc0605_v5"), "0.500": os.path.join(st, "yc0500_v5"),
            "0.283": os.path.join(st, "yc0283_v5"), "0.72 (wave 2, M/4)": os.path.join(w2, "st_yc0p720")}
    res, series = {}, {}
    for k, d in runs.items():
        res[k], series[k] = one(d, k)
    with open(os.path.join(outdir, "v3_clusters.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    for i, k in enumerate(runs):
        t, a, ta, ma = series[k]
        c = (fs.SERIES + ["grey"])[i % 6]
        axs[0].plot(t, a, lw=0.8, color=c, label=f"$y_c$ = {k}")
        if len(ta):
            axs[0].axvline(ta[0], color=c, lw=0.8, ls=":")
            axs[1].plot(ta, ma - 1, lw=0.9, color=c, label=f"$y_c$ = {k}")
    for tp in (109.0, 73.0):
        axs[0].axvline(tp, **fs.MASK_LINE)
    axs[0].text(75, 0.05, "paper AH 73, 109 M", fontsize=7, color="grey")
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"$\alpha$ at the probe (centre)")
    axs[0].legend(fontsize=6, loc="lower left")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel(r"$M_{\rm AH}/M - 1$")
    axs[1].legend(fontsize=7)
    fig.suptitle("V3: cluster sequence, central lapse and horizon mass (runs/st/*, wave-2 core-20261115-152843-5728b1d)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v3_clusters"))


if __name__ == "__main__":
    main()
