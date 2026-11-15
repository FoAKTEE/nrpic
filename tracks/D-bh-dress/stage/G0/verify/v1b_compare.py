#!/usr/bin/env python3
"""C1b: compare the t = 0 constraint fields of the release executable with the wave-1 dumps
of the branch build, and evaluate regional maxima and orders with the track's own analysis
(code_t0_check.analyse), its figure directory redirected into the run directory so that no
file of the track is overwritten.

Usage: v1b_compare.py --out DIR --new DX1 DX05 --old DX1 DX05
"""
import argparse
import json
import math
import os
import shutil
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ES = os.path.normpath(os.path.join(HERE, "..", "..", "..", "einstein_straus"))
sys.path.insert(0, ES)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "..", "python")))
import code_t0_check as ctc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--new", nargs=2, required=True)
    ap.add_argument("--old", nargs=2, required=True)
    a = ap.parse_args()
    res = {"cellwise": {}}
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    for j, (nd, od) in enumerate(zip(a.new, a.old)):
        fn = ctc.read_field(os.path.join(nd, "es.field.00000.bin"))
        fo = ctc.read_field(os.path.join(od, "es.field.00000.bin"))
        rec = {}
        for k in ("E", "chi", "H", "Mx", "My", "Mz", "Khat", "alpha"):
            d = np.abs(fn[k] - fo[k])
            sc = np.max(np.abs(fo[k]))
            rec[k] = {"max_abs_diff": float(np.nanmax(d)), "max_abs_old": float(sc),
                      "nan_new": int(np.isnan(fn[k]).sum()), "nan_old": int(np.isnan(fo[k]).sum())}
        res["cellwise"][os.path.basename(nd)] = rec
        n = fn["n"][0]
        dx = 96.0 / n
        xc = -48 + (np.arange(n) + 0.5) * dx
        Z, Y, X = np.meshgrid(xc, xc, xc, indexing="ij")
        r = np.sqrt(X * X + Y * Y + Z * Z).ravel()
        sel = np.abs(fo["H"]).ravel() > 0
        ax[0].loglog(r[sel][::7], np.abs(fn["H"]).ravel()[sel][::7], ".", ms=1, color=fs.SERIES[j],
                     label=f"release, dx = {dx:g} M")
        ax[1].loglog(np.abs(fo["H"]).ravel()[::7] + 1e-20, np.abs(fn["H"]).ravel()[::7] + 1e-20, ".", ms=1,
                     color=fs.SERIES[j], label=f"dx = {dx:g} M")
    ax[0].set_xlabel(r"$r/M$"); ax[0].set_ylabel(r"$|H|$ at $t = 0$ (release)")
    ax[0].legend(frameon=False, fontsize=8, markerscale=6)
    ax[1].set_xlabel(r"$|H|$ wave-1 branch build"); ax[1].set_ylabel(r"$|H|$ release core-v0.3")
    lim = [1e-16, 10]
    ax[1].plot(lim, lim, **fs.GUIDE)
    ax[1].legend(frameon=False, fontsize=8, markerscale=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "v1b_code_t0"))
    shutil.copy(os.path.join(a.out, "v1b_code_t0.png"), os.path.join(HERE, "..", "figs"))
    # the track's own regional analysis on the release dumps, figure redirected
    ctc.FIGS = a.out
    ns = types.SimpleNamespace(runs=list(a.new), out=a.out, half=48.0)
    os.makedirs(a.out, exist_ok=True)
    ctc.analyse(ns)
    with open(os.path.join(a.out, "v1b_compare.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
