#!/usr/bin/env python3
"""Figures of the work package cosmo-amr redrawn from the outputs of the registered runs
(the figures of the test scripts are kept in the run directories; two of them hid data:
T4 put the release's wrong horizon on a face outside the axis, T9 clipped its labels).

    figs_cosmo_amr.py --t4 RUNDIR --t9 RUNDIR --out DIR

Writes DIR/fig_t4_finder.{pdf,png} and DIR/fig_t9_peak.{pdf,png}."""
import argparse
import json
import os
import sys

import numpy as np

import amrlib as A


def t4(rd, out, fs, plt):
    s = json.load(open(os.path.join(rd, "t4_summary.json")))
    names = ["a", "b", "c", "c2", "d", "e", "brel", "crel"]
    names = [n for n in names if n in s]
    m = np.array([s[n]["mass"] if s[n]["found"] else np.nan for n in names])
    ma = s["a"]["mass"]
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.93, wspace=0.30)
    x = np.arange(len(names))
    new = np.array([not n.endswith("rel") for n in names])
    ax[0].plot(x[new], m[new], "o", color=fs.PAL["blue"], label="this branch")
    ax[0].plot(x[~new & np.isfinite(m)], m[~new & np.isfinite(m)], "s",
               color=fs.PAL["red"], label="release")
    for i in np.where(~np.isfinite(m))[0]:
        ax[0].annotate("no horizon", (x[i], 0.80), ha="center", fontsize=8,
                       color=fs.PAL["red"])
        ax[0].plot([x[i]], [0.78], "x", color=fs.PAL["red"])
    ax[0].axhline(ma, **fs.GUIDE)
    ax[0].set_ylim(0.6, 1.05)
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(names)
    ax[0].set_ylabel("apparent-horizon mass")
    ax[0].legend(frameon=False, loc="lower left", fontsize=8)
    d = np.abs(m/ma - 1.0)
    ax[1].semilogy(x[new][1:], np.maximum(d[new][1:], 1e-17), "o", color=fs.PAL["blue"])
    ok = ~new & np.isfinite(m)
    ax[1].semilogy(x[ok], d[ok], "s", color=fs.PAL["red"])
    ax[1].axhline(1e-10, **fs.GUIDE)
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(names)
    ax[1].set_ylabel(r"$|M/M_a-1|$")
    fs.save(fig, os.path.join(out, "fig_t4_finder"))
    plt.close(fig)


def t9(rd, out, fs, plt):
    names = ["lohner", "lohnerrel", "ladder", "ladderc", "chi", "ppc"]
    fig, ax = plt.subplots(1, 3, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.90, wspace=0.42)
    cols = fs.SERIES + ["k", "grey"]
    ls = {"chi": "--", "ppc": ":"}
    for i, n in enumerate(names):
        d = os.path.join(rd, n)
        hp = os.path.join(d, "peak.nrpic.hst")
        if not os.path.exists(hp):
            continue
        h, s = A.read_hst(hp), A.read_hst(os.path.join(d, "peak.cstat.hst"))
        kw = dict(color=cols[i], ls=ls.get(n, "-"), label=n)
        ax[0].plot(h["ncycle"], h["nmb"], **kw)
        ax[1].semilogy(s["time"], s["Hr_max"], **kw)
        rp = os.path.join(d, "peak.region.hst")
        if os.path.exists(rp):
            g = A.read_hst(rp)
            ax[2].semilogy(g["time"], g["H2_in_s1"]/g["E2_in_s1"], **kw)
    ax[0].set_xlabel("cycle")
    ax[0].set_ylabel("MeshBlocks")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_xlabel("conformal time")
    ax[1].set_ylabel(r"largest $|H|/H_{\rm scale}$")
    ax[2].set_xlabel("conformal time")
    ax[2].set_ylabel(r"$\|H\|_2/\|16\pi E\|_2$, $r<r_m$")
    ax[0].set_title("refinement", fontsize=9)
    ax[1].set_title("relative Hamiltonian constraint", fontsize=9)
    ax[2].set_title("inside the compaction radius", fontsize=9)
    fs.save(fig, os.path.join(out, "fig_t9_peak"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t4", required=True)
    ap.add_argument("--t9", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    t4(a.t4, a.out, fs, plt)
    t9(a.t9, a.out, fs, plt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
