#!/usr/bin/env python3
"""V10b: initial-data solver, second pass (core-v0.6), test C: static refinement.

Claim (tracks/core/interfaces/id_solver2.md, test C, run core-20261119-153510-d1eaa30):
Gaussian on one and two static levels; the run's own monitor at t = 0 at 2.4e-12 to
2.0e-11 on every level; central error equal to the uniform run of the finest cell size
(-5.01e-3 against -5.03e-3).
Own readers: NRIDSOL1 (v10a_idsolve.read_idsolve) and NRIDBLK1 (docs/FORMATS.md line 212:
8 bytes, 5 int64 nmb, nx1, nx2, nx3, nfields; per MeshBlock int64 level, 6 float64
extents; then each field as nmb blocks of nx3*nx2*nx1 float64, first index fastest:
psi, K, AA, E, H last, residual, H first). Own continuum reference psi (v10a).
Centre error: relative error of psi - 1, (a) in the eight cells around the origin on the
finest level (the measure V10a found for T1), (b) mean over the cells with r < 1 (the
measure of the claim, read from tracks/core/analysis/idsolve2/test_c.py after (a)
differed by 4 per cent).

usage: v10b_idsolve2.py RUNDIR OUTDIR
"""
import json
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v10a_idsolve import psi_ref, read_idsolve  # noqa: E402


def read_blk(path):
    b = open(path, "rb").read()
    assert b[:8] == b"NRIDBLK1"
    nmb, n1, n2, n3, nf = struct.unpack_from("<5q", b, 8)
    off = 48
    meta = []
    for _ in range(nmb):
        (lev,) = struct.unpack_from("<q", b, off)
        ext = struct.unpack_from("<6d", b, off + 8)
        meta.append((lev, ext))
        off += 56
    n = n1 * n2 * n3
    assert len(b) == off + 8 * nf * nmb * n, (len(b), off + 8 * nf * nmb * n)
    f = np.frombuffer(b, "<f8", nf * nmb * n, off).reshape(nf, nmb, n3, n2, n1)
    return (n1, n2, n3), meta, f


def coords(ext, n1, n2, n3):
    x = ext[0] + (np.arange(n1) + 0.5) * (ext[1] - ext[0]) / n1
    y = ext[2] + (np.arange(n2) + 0.5) * (ext[3] - ext[2]) / n2
    z = ext[4] + (np.arange(n3) + 0.5) * (ext[5] - ext[4]) / n3
    Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
    return X, Y, Z


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    res = {}
    for case in ("g_uni32", "g_uni64"):
        (n1, n2, n3), ext, f = read_idsolve(os.path.join(rd, case, "gauss.idsolve.bin"))
        X, Y, Z = coords(ext, n1, n2, n3)
        r = np.sqrt(X * X + Y * Y + Z * Z)
        c = [n1 // 2 - 1, n1 // 2]
        rel = (f[0] - psi_ref(r)) / (psi_ref(r) - 1)
        res[case] = {"dx": (ext[1] - ext[0]) / n1, "centre_rel_err": float(rel[np.ix_(c, c, c)].mean()),
                     "rel_err_mean_r_lt_1": float(rel[r < 1.0].mean()),
                     "monitor_H_last_max": float(np.abs(f[4]).max())}
    for case in ("g_smr1", "g_smr2"):
        (n1, n2, n3), meta, f = read_blk(os.path.join(rd, case, "gauss.idsolve.blk.bin"))
        levels = sorted(set(m[0] for m in meta))
        per_level = {}
        cen, sphere = [], []
        for lev in levels:
            idx = [i for i, m in enumerate(meta) if m[0] == lev]
            per_level[int(lev)] = {"nmb": len(idx), "dx": (meta[idx[0]][1][1] - meta[idx[0]][1][0]) / n1,
                                   "monitor_H_last_max": float(np.abs(f[4][idx]).max()),
                                   "monitor_H_first_max": float(np.abs(f[6][idx]).max())}
        top = levels[-1]
        dx_top = per_level[int(top)]["dx"]
        for i, (lev, ext) in enumerate(meta):
            if lev != top:
                continue
            X, Y, Z = coords(ext, n1, n2, n3)
            r = np.sqrt(X * X + Y * Y + Z * Z)
            sel = (np.abs(X) < dx_top) & (np.abs(Y) < dx_top) & (np.abs(Z) < dx_top)
            rel = (f[0][i] - psi_ref(r)) / (psi_ref(r) - 1)
            if sel.any():
                cen.extend(rel[sel].tolist())
            sphere.extend(rel[r < 1.0].tolist())
        res[case] = {"levels": per_level, "n_centre_cells": len(cen),
                     "centre_rel_err": float(np.mean(cen)), "centre_spread": float(np.ptp(cen)),
                     "rel_err_mean_r_lt_1": float(np.mean(sphere))}
    with open(os.path.join(outdir, "v10b_idsolve2.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.8))
    names = ["g_uni32", "g_uni64", "g_smr1", "g_smr2"]
    axs[0].bar(range(4), [-res[k]["centre_rel_err"] for k in names], color=fs.SERIES[:4])
    axs[0].set_xticks(range(4))
    axs[0].set_xticklabels(names, fontsize=7)
    axs[0].set_ylabel(r"$-(\psi-\psi_{\rm ex})/(\psi_{\rm ex}-1)$ at the centre")
    xs, ys, cs = [], [], []
    for k, name in enumerate(names):
        if "levels" in res[name]:
            for lev, v in res[name]["levels"].items():
                xs.append(f"{name} L{lev}")
                ys.append(v["monitor_H_last_max"])
                cs.append(fs.SERIES[k])
        else:
            xs.append(name)
            ys.append(res[name]["monitor_H_last_max"])
            cs.append(fs.SERIES[k])
    axs[1].bar(range(len(xs)), ys, color=cs)
    axs[1].set_yscale("log")
    axs[1].set_xticks(range(len(xs)))
    axs[1].set_xticklabels(xs, fontsize=6, rotation=30)
    axs[1].set_ylabel("max |H| of the monitor after the solve")
    fig.suptitle("V10b: solver on static refinement, run core-20261119-153510-d1eaa30 (own readers, own psi)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v10b_idsolve2"))


if __name__ == "__main__":
    main()
