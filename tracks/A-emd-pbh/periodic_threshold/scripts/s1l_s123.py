#!/usr/bin/env python3
"""Judgement of S1-S3 of S1L's card job 2 (periodic_threshold JOURNAL 2026-11-21 23:15Z), left unjudged (gate
review C19): central lapse and E_max / mean E against time from S1L's history, with the finder's status file.
    s1l_s123.py --run RUNDIR --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = np.loadtxt(os.path.join(a.run, "peak.nrpic.hst"), comments="#")
    t, amin, emax, eint, vol = d[:, 0], d[:, 15], d[:, 30], d[:, 8], d[:, 27]
    _, idx = np.unique(np.round(t, 9), return_index=True)
    t, amin, emax, eint, vol = t[idx], amin[idx], emax[idx], eint[idx], vol[idx]
    ratio = emax / (eint / vol)
    st = np.loadtxt(os.path.join(a.run, "peak.horizon_status_0.txt"), comments="#", usecols=range(12), ndmin=2)
    res = dict(t_end=float(t[-1]), n_searches=int(len(st)), n_found=int((st[:, 2] == 1).sum()),
               t_alpha_below_0p3=float(t[np.argmax(amin < 0.3)]) if (amin < 0.3).any() else None,
               t_Emax_above_1e3=float(t[np.argmax(ratio > 1e3)]) if (ratio > 1e3).any() else None,
               alpha_min_end=float(amin[-1]), Emax_over_mean_max=float(ratio.max()))
    print(json.dumps(res, indent=1))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.9, wspace=0.3)
    ax[0].plot(t, amin, color=fs.PAL["blue"])
    ax[0].axhline(0.3, **fs.MASK_LINE)
    ax[0].set_xlabel("t"); ax[0].set_ylabel(r"$\alpha_{\min}$"); ax[0].set_yscale("log")
    ax[0].set_title("(a) smallest lapse", fontsize=8)
    ax[1].plot(t, ratio, color=fs.PAL["red"])
    ax[1].axhline(1e3, **fs.MASK_LINE)
    ax[1].set_xlabel("t"); ax[1].set_ylabel(r"$E_{\max}/\bar E$"); ax[1].set_yscale("log")
    ax[1].set_title("(b) density contrast of the deposit", fontsize=8)
    for k in range(2):
        ax[k].axvspan(190.0, 210.0, color="grey", alpha=0.15, lw=0)
        fs.no_minor_labels(ax[k])
    figs = fs.save(fig, os.path.join(a.out, "fig_s1l_s123"))
    res["figures"] = figs
    with open(os.path.join(a.out, "s1l_s123.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
