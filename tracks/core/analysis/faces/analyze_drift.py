#!/usr/bin/env python3
"""Card runs D of the package faces: apparent-horizon mass of Track D's vacuum puncture
(drift_dx8, faces at 128 M) with the new outer-face options, against Track D's own run.

    analyze_drift.py --ref <dir of run D-bh-dress-20261115-121313-284ec4f>
                     --case name=<dir> [--case ...] [--out results/drift.json]
                     [--fig figs/drift]

Each directory holds punc.horizon_summary_0.txt (columns 1:iter 2:time 3:mass ...).
Measures (journal entry 6): the largest |M - M_ref| for t <= 180 M (D-a); the
peak-to-peak of M in the windows 210-260 M and 295-345 M, and the same after removing a
straight line fitted over 150-345 M (D-b); the drift M(345) - M(50).
"""

import argparse
import glob
import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import flib  # noqa: F401,E402  (puts python/ on the path)
from nrpic import figstyle as fs  # noqa: E402

WINDOWS = ((210.0, 260.0), (295.0, 345.0))


def load(d):
    f = sorted(glob.glob(os.path.join(d, "**", "punc.horizon_summary_0.txt"), recursive=True))
    if not f:
        return None
    a = np.loadtxt(f[0], comments="#")
    t, m = a[:, 1], a[:, 2]
    # repeated times (finder not called between dumps): keep the first of each time
    _, idx = np.unique(t, return_index=True)
    return t[idx], m[idx]


def measures(t, m):
    out = {"t_end": float(t.max())}
    for a, b in WINDOWS:
        k = (t >= a) & (t <= b)
        if k.sum() > 2:
            out[f"p2p_{a:g}_{b:g}"] = float(m[k].max() - m[k].min())
    k = (t >= 150.0) & (t <= 345.0)
    if k.sum() > 2:
        c = np.polyfit(t[k], m[k], 1)
        res = m - np.polyval(c, t)
        out["slope_150_345"] = float(c[0])
        for a, b in WINDOWS:
            q = (t >= a) & (t <= b)
            if q.sum() > 2:
                out[f"p2p_detrended_{a:g}_{b:g}"] = float(res[q].max() - res[q].min())
    for t0 in (50.0, 100.0, 345.0):
        k = np.argmin(np.abs(t - t0))
        if abs(t[k] - t0) < 1.0:
            out[f"M_{t0:g}"] = float(m[k])
    if "M_50" in out and "M_345" in out:
        out["drift_50_345"] = out["M_345"] - out["M_50"]
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ref", required=True)
    p.add_argument("--case", action="append", default=[])
    p.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "results",
                                                  "drift.json"))
    p.add_argument("--fig", default=os.path.join(os.path.dirname(__file__), "figs", "drift"))
    a = p.parse_args()
    runs = {"Track D (stock)": load(a.ref)}
    for c in a.case:
        n, d = c.split("=", 1)
        r = load(d)
        if r is not None:
            runs[n] = r
    tr, mr = runs["Track D (stock)"]
    res = {}
    for n, (t, m) in runs.items():
        r = measures(t, m)
        if n != "Track D (stock)":
            mi = np.interp(t, tr, mr)
            k = t <= 180.0
            r["max_dM_to_ref_t_le_180"] = float(np.abs(m[k] - mi[k]).max())
            k = t <= 345.0
            r["max_dM_to_ref_t_le_345"] = float(np.abs(m[k] - mi[k]).max())
        res[n] = r
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    fs.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(fs.FULL_WIDTH * 0.75, 4.8), sharex=True)
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.1, top=0.97, hspace=0.06)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]
    for (n, (t, m)), c in zip(runs.items(), cols):
        k = t <= 360.0
        axs[0].plot(t[k], m[k] - 1.0, color=c, lw=1.0, label=n)
        if n != "Track D (stock)":
            axs[1].plot(t[k], m[k] - np.interp(t[k], tr, mr), color=c, lw=1.0, label=n)
    for ax in axs:
        for w in WINDOWS:
            ax.axvspan(w[0], w[1], color="0.9", zorder=0)
    axs[0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    axs[0].set_ylim(0.0010, 0.0018)
    axs[0].legend(fontsize=8, loc="lower right")
    axs[1].set_ylabel(r"$M_{\rm AH} - M_{\rm AH}^{\rm Track\,D}$")
    axs[1].set_xlabel(r"$t/M$")
    fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
