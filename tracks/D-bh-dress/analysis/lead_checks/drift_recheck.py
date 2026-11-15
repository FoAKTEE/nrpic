#!/usr/bin/env python3
"""Lead's independent re-check of D-pre-4 (puncture_drift) from the raw finder output.

Reads punc.horizon_summary_0.txt of the two card runs (columns: iter, time, mass, Sx, Sy,
Sz, S, ...), forms a centred running mean of the mass over a window w (default 20 M), and
prints: the drift <M>(500) - <M>(50); the largest |<M>(t) - <M>(50)| for 50 <= t <= T for
T = 100, 150, 200, 210 M; the scatter of the raw values about the running mean before
210 M; the peak-to-peak of a 5 M running mean in 220-255 M and of the raw values in
300-340 M; max |S|/M^2 after 5 M. Written without reading tools/analyse_drift.py.
Figure: lead_drift_recheck.png (both resolutions, raw and running mean).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/python")
from nrpic import figstyle  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = {"M/8": "D-bh-dress-20261115-121313-284ec4f", "M/16": "D-bh-dress-20261115-121314-284ec4f"}


def load(rid):
    d = np.loadtxt(os.path.join(SCR, rid, "punc.horizon_summary_0.txt"))
    t, m, s = d[:, 1], d[:, 2], d[:, 6]
    o = np.argsort(t)
    t, m, s = t[o], m[o], s[o]
    keep = np.concatenate([[True], np.diff(t) > 0])
    return t[keep], m[keep], s[keep]


def runmean(t, y, w):
    out = np.full_like(y, np.nan)
    for i, ti in enumerate(t):
        sel = np.abs(t - ti) <= w / 2
        if ti - w / 2 >= t[0] and ti + w / 2 <= t[-1]:
            out[i] = y[sel].mean()
    return out


def at(t, y, t0):
    return float(np.interp(t0, t, y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--w", type=float, default=20.0)
    a = ap.parse_args()
    res = {}
    figstyle.use_style()
    fig, axs = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    for k, (lab, rid) in enumerate(RUNS.items()):
        t, m, s = load(rid)
        rm = runmean(t, m, a.w)
        rm5 = runmean(t, m, 5.0)
        ok = np.isfinite(rm)
        r = dict(run=rid, n=len(t), t_last=float(t[-1]))
        r["drift_50_490"] = at(t[ok], rm[ok], 490.0) - at(t[ok], rm[ok], 50.0)
        for T in (100, 150, 200, 210):
            sel = ok & (t >= 50) & (t <= T)
            r[f"maxabsD_50_{T}"] = float(np.max(np.abs(rm[sel] - at(t[ok], rm[ok], 50.0))))
        sel = ok & (t >= 50) & (t <= 210)
        r["sigma_raw_about_mean_50_210"] = float(np.std(m[sel] - rm[sel]))
        sel = np.isfinite(rm5) & (t >= 220) & (t <= 255)
        r["p2p_rm5_220_255"] = float(np.ptp(rm5[sel]))
        sel = (t >= 300) & (t <= 340)
        r["p2p_raw_300_340"] = float(np.ptp(m[sel]))
        r["max_S_over_M2_after5"] = float(np.max(s[t > 5] / m[t > 5] ** 2))
        res[lab] = r
        c = ["C0", "C1"][k]
        axs[0].plot(t, m - 1, lw=0.4, color=c, alpha=0.5)
        axs[0].plot(t, rm - 1, lw=1.5, color=c, label=f"{lab}, {a.w:.0f} M mean")
        axs[1].plot(t, rm - at(t[ok], rm[ok], 50.0), lw=1.5, color=c, label=lab)
    axs[0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    axs[0].legend(frameon=False)
    axs[1].axhline(0, color="k", lw=0.5)
    axs[1].axvspan(220, 255, color="0.9")
    axs[1].axvspan(300, 340, color="0.9")
    axs[1].set_ylabel(r"$\langle M\rangle(t)-\langle M\rangle(50\,M)$")
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_xlim(0, 500)
    axs[1].set_ylim(-1e-4, 3.5e-4)
    axs[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "lead_drift_recheck.png"), dpi=150)
    with open(os.path.join(a.out, "lead_drift_recheck.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
