#!/usr/bin/env python3
"""Prolate collapse at two resolutions (ladder row 3): the earlier run with finest cells
M/16 (runs/prolate/e09_v8) against the wave-2 run with finest cells M/8, same particles.

Numbers: first apparent horizon and its mass, largest horizon mass, horizon mass at the
last search; largest Kretschmann scalar and where/when; smallest lapse; particle
removal; Hamiltonian-constraint norm (z4c.user.hst). Figures (figstyle):
  figs/prolate_resolution.{pdf,png}   time histories at the two resolutions
  figs/prolate_mosaic.{pdf,png}       slice mosaic with zoom boxes: energy density in the
                                      plane y = 0 at the spindle time, both resolutions,
                                      four nested windows (stage check C11)

    prolate_compare.py --m16 DIR --m8 DIR [--t-slice 27.75] [--out DIR]
"""
import argparse
import glob
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "analysis", "diag"))
sys.dont_write_bytecode = True
from nrpic import figstyle as fs  # noqa: E402
from common import read_athena_hst, read_curv_hst, keep_last  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

FIGS = os.path.join(WT, "tracks", "core", "verify", "figs")
BASE = "prol"


def read_curv_slice(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
    return t, d


def read_ah(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        x = line.split()
        rows.append([float(x[1]), float(x[2]), float(x[7]), float(x[10])])
    return keep_last(np.array(rows))


def read_nrpic_hst(path):
    rows = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        v = [float(x) for x in line.split()]
        rows[v[0]] = v
    return np.array([rows[t] for t in sorted(rows)])


def numbers(d):
    ah = read_ah(os.path.join(d, BASE + ".horizon_summary_0.txt"))
    found = ah[np.isfinite(ah[:, 1])]
    cv = read_curv_hst(os.path.join(d, BASE + ".curv.hst"))
    h = read_nrpic_hst(os.path.join(d, BASE + ".nrpic.hst"))
    z = read_athena_hst(os.path.join(d, BASE + ".z4c.user.hst"))
    i = int(np.argmax(cv[:, 1]))
    rem = np.nonzero(h[:, 16] > 0)[0]
    res = dict(dir=d, t_end=float(h[-1, 0]),
               t_first_AH=float(found[0, 0]) if len(found) else None,
               M_AH_first=float(found[0, 1]) if len(found) else None,
               M_AH_max=float(found[:, 1].max()) if len(found) else None,
               t_M_AH_max=float(found[np.argmax(found[:, 1]), 0]) if len(found) else None,
               M_AH_last=float(found[-1, 1]) if len(found) else None,
               t_AH_last=float(found[-1, 0]) if len(found) else None,
               I_max=float(cv[i, 1]), t_I_max=float(cv[i, 0]),
               x_I_max=[float(cv[i, 2]), float(cv[i, 3]), float(cv[i, 4])],
               alpha_min_end=float(h[-1, 15]), np0=int(h[0, 2]), np_end=int(h[-1, 2]),
               t_first_removal=float(h[rem[0], 0]) if len(rem) else None,
               m_removed=float(h[-1, 17]), nmb_max=int(h[:, 22].max()),
               ah=dict(t=found[:, 0].tolist(), M=found[:, 1].tolist()),
               curv=dict(t=cv[:, 0].tolist(), I=cv[:, 1].tolist(), z=cv[:, 4].tolist(),
                         E=cv[:, 5].tolist()),
               hst=dict(t=h[::5, 0].tolist(), alpha_min=h[::5, 15].tolist(),
                        np=h[::5, 2].tolist()))
    key = next((k for k in z if "H-norm2" in k or k.lower().startswith("h-norm")), None)
    if key:
        res["Hnorm"] = dict(t=z["time"].tolist(), v=np.sqrt(np.abs(z[key])).tolist(), key=key)
        res["Hnorm_max"] = float(np.sqrt(np.abs(z[key])).max())
        res["t_Hnorm_max"] = float(z["time"][np.argmax(np.abs(z[key]))])
    return res


def slice_file(d, t):
    cv = read_curv_hst(os.path.join(d, BASE + ".curv.hst"))
    k = int(np.argmin(np.abs(cv[:, 0] - t)))
    return os.path.join(d, f"{BASE}.curv.{int(cv[k, 9]):05d}.bin")


def raster(rec, half, npx=300, col=4):
    """Fill a npx^2 image of [-half, half]^2 (x horizontal, z vertical) from the cell
    records (x, z, dx, I, E, alpha, sqrt gamma), coarse cells first, finer on top."""
    img = np.full((npx, npx), np.nan)
    pix = 2.0 * half / npx
    sel = (np.abs(rec[:, 0]) - 0.5 * rec[:, 2] < half) & (np.abs(rec[:, 1]) - 0.5 * rec[:, 2] < half)
    r = rec[sel]
    r = r[np.argsort(-r[:, 2])]
    for x, z, dx, v in zip(r[:, 0], r[:, 1], r[:, 2], r[:, col]):
        i0 = int(np.floor((x - 0.5 * dx + half) / pix))
        i1 = int(np.ceil((x + 0.5 * dx + half) / pix))
        j0 = int(np.floor((z - 0.5 * dx + half) / pix))
        j1 = int(np.ceil((z + 0.5 * dx + half) / pix))
        img[max(j0, 0):max(min(j1, npx), 0), max(i0, 0):max(min(i1, npx), 0)] = v
    return img


def mosaic(runs, t_slice, halves=(10.0, 4.0, 1.5, 0.6)):
    fig, axes, cax = fs.slice_mosaic(len(runs), len(halves), panel=1.585, left=1.37,
                                     bottom=0.36, fig_w=8.0)
    norm = LogNorm(1e-4, 3.0)
    im = None
    tt = []
    for i, (lab, d) in enumerate(runs):
        t, rec = read_curv_slice(slice_file(d, t_slice))
        tt.append(t)
        for j, half in enumerate(halves):
            ax = axes[i, j]
            img = raster(rec, half)
            im = ax.imshow(np.clip(img, 1e-12, None), origin="lower", extent=[-half, half, -half, half],
                           cmap=fs.CMAP["dens"], norm=norm, interpolation="nearest")
            ax.set_facecolor("black")
            if j + 1 < len(halves):
                s = halves[j + 1]
                ax.plot([-s, s, s, -s, -s], [-s, -s, s, s, -s], color="w", lw=0.8)
            fs.slice_ticks(ax, half, show_x=(i == len(runs) - 1), show_y=False)
            ax.tick_params(which="both", color="w")
            if j == 0:
                ax.text(0.04, 0.95, lab, transform=ax.transAxes, color="w", va="top",
                        fontsize=8)
            ax.text(0.96, 0.04, r"$\pm%g\,M$" % half, transform=ax.transAxes, ha="right",
                    va="bottom", fontsize=8, color="w")
            if i == len(runs) - 1:
                ax.set_xlabel(r"$x/M$", labelpad=1)
            if j == 0:
                ax.text(-0.08, 0.5, r"$z/M$", transform=ax.transAxes, rotation=90, ha="right",
                        va="center")
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"energy density $E$ at $y=0$ [$M^{-2}$]")
    cax.yaxis.set_label_position("left")
    cax.yaxis.set_ticks_position("left")
    return fig, tt


def history_figure(res):
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.92, wspace=0.36)
    for (lab, r), c in zip(res.items(), (fs.PAL["blue"], fs.PAL["red"])):
        ax[0].semilogy(r["curv"]["t"], r["curv"]["I"], color=c, label=lab)
        ax[1].plot(r["ah"]["t"], r["ah"]["M"], "o-", color=c, ms=2.5, lw=1.0, label=lab)
        if "Hnorm" in r:
            ax[2].semilogy(r["Hnorm"]["t"], r["Hnorm"]["v"], color=c, label=lab)
    ax[0].axvline(27.75, **fs.MASK_LINE)
    ax[0].axvline(32.0, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$t/M$", labelpad=-2)
    ax[0].set_ylabel(r"largest Kretschmann scalar [$M^{-4}$]")
    ax[0].legend(fontsize=7, loc="upper left")
    ax[1].axhline(1.0, **fs.GUIDE)
    ax[1].axvline(32.0, **fs.MASK_LINE)
    ax[1].set_xlabel(r"$t/M$", labelpad=-2)
    ax[1].set_ylabel(r"apparent-horizon mass $M_{\rm AH}/M$")
    ax[1].set_xlim(30.0, 46.0)
    ax[2].set_xlabel(r"$t/M$", labelpad=-2)
    ax[2].set_ylabel(r"norm of the Hamiltonian constraint")
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m16", required=True)
    ap.add_argument("--m8", required=True)
    ap.add_argument("--t-slice", type=float, default=27.75)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    fs.use_style()
    os.makedirs(FIGS, exist_ok=True)
    res = {r"finest $M/16$ (e09_v8)": numbers(a.m16), r"finest $M/8$ (wave 2)": numbers(a.m8)}
    for k, r in res.items():
        print(k, json.dumps({x: r[x] for x in r if x not in ("ah", "curv", "hst", "Hnorm")}))
    fig = history_figure(res)
    fs.save(fig, os.path.join(FIGS, "prolate_resolution"))
    plt.close(fig)
    fig, tt = mosaic([(r"$M/16$", a.m16), (r"$M/8$", a.m8)], a.t_slice)
    fs.save(fig, os.path.join(FIGS, "prolate_mosaic"))
    plt.close(fig)
    res_out = {k: v for k, v in res.items()}
    res_out["slice_times"] = tt
    with open(os.path.join(a.out, "prolate_compare.json"), "w") as f:
        json.dump(res_out, f)
    print("slice times", tt)


if __name__ == "__main__":
    main()
