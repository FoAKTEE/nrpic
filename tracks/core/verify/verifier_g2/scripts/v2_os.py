#!/usr/bin/env python3
"""V2 (and V5a): Oppenheimer-Snyder collapse, horizon mass and deposition identity.

Own readers of the text files (column names from their header lines):
  <base>.horizon_summary_0.txt  columns iter, time, mass, ... (nan before a horizon)
  <base>.nrpic.hst              columns named in the '# [k]=name' header line
Units: the table is the OS ball of R_0 = 5 M with M = 1 (input file header), so
M_AH/M - 1 = mass - 1.

usage: v2_os.py REGRESSION_DIR REFERENCE_DIR OUTDIR
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
    d = np.genfromtxt(path, comments="#")
    t, m = d[:, 1], d[:, 2]
    ok = np.isfinite(m)
    return t[ok], m[ok]


def nearest(t, m, t0):
    i = int(np.argmin(np.abs(t - t0)))
    return float(t[i]), float(m[i])


def analyse(rundir, t_max):
    t, m = read_ah(os.path.join(rundir, "os.horizon_summary_0.txt"))
    sel = t <= t_max + 1e-9
    h = read_hst(os.path.join(rundir, "os.nrpic.hst"))
    live = h["np"] > 0
    ident = np.abs(h["int_E"][live] - h["sum_mW"][live]) / np.abs(h["sum_mW"][live])
    t_removed = float(h["time"][np.argmax(h["np"] == 0)]) if np.any(h["np"] == 0) else None
    out = {"t_first_ah": float(t[0]), "m_first_ah": float(m[0]),
           "max_abs_m_minus_1": float(np.max(np.abs(m[sel] - 1))),
           "t_of_max": float(t[sel][np.argmax(np.abs(m[sel] - 1))]),
           "n_found": int(sel.sum()), "np_start": int(h["np"][0]),
           "t_first_np0_hst": t_removed, "t_hst_last": float(h["time"][-1]),
           "max_identity_rel": float(ident.max()),
           "sum_mW0": float(h["sum_mW"][0])}
    for t0 in (20.0, 25.0, 40.0, 60.0):
        if t0 <= t[-1] + 0.2:
            out[f"m_near_{int(t0)}"] = nearest(t, m, t0)
    return out, (t, m), (h["time"][live], ident)


def main():
    reg, ref, outdir = sys.argv[1:4]
    os.makedirs(outdir, exist_ok=True)
    r_reg, s_reg, i_reg = analyse(reg, 25.0)
    r_ref, s_ref, i_ref = analyse(ref, 60.0)
    res = {"regression": r_reg, "reference_nocap_sc": r_ref}
    with open(os.path.join(outdir, "v2_os.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ax = axs[0]
    ax.plot(s_ref[0], s_ref[1] - 1, color=fs.PAL["blue"], lw=1.0, label="runs/os/nocap_sc (to 60 M)")
    ax.plot(s_reg[0], s_reg[1] - 1, color=fs.PAL["red"], lw=1.0, ls="--", label="core-20261115-065901-3629622")
    ax.axhline(1e-3, **fs.GUIDE)
    ax.axhline(-1e-3, **fs.GUIDE)
    ax.text(40, 1.1e-3, "paper: $\\lesssim 10^{-3}$ (main.tex 945)", fontsize=7)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$M_{\rm AH}/M - 1$")
    ax.legend(fontsize=7, loc="lower left")
    ax = axs[1]
    ax.semilogy(i_ref[0], np.maximum(i_ref[1], 1e-17), color=fs.PAL["blue"], lw=1.0, label="nocap_sc")
    ax.semilogy(i_reg[0], np.maximum(i_reg[1], 1e-17), color=fs.PAL["red"], lw=1.0, ls="--", label="regression O")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$|\int E\,dV - \sum m W| / \sum m W$")
    ax.legend(fontsize=7)
    fig.suptitle("V2: Oppenheimer-Snyder, horizon mass and deposition identity (own readers)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v2_os"))


if __name__ == "__main__":
    main()
