#!/usr/bin/env python3
"""Test t1 of the package faces: a refined region (cells of 1/2) that touches the +x
outflow face, so that the fall-off ghost fill also runs on the coarse array before
prolongation.  Stock conditions against the full set with damping, eight steps.

    analyze_t1.py <run dir with smr_stock, smr_full> [--out results/t1.json] [--fig figs/t1_smrface]

Measures at the last dump (journal entry 9): non-finite values in any dump; the largest
|H| in the face layer (within 4 of the +x face) on the fine part (cells of 1/2) and on
the coarse part of that face; the largest |H| in the junction zone (within 4 of the +x
face, 2 <= max(|y|, |z|) < 6: the fine/coarse junction sits at 4).
"""

import argparse
import json
import os

import numpy as np

import flib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

LBOX = 16.0


def nonfinite(rundir):
    n = 0
    for var in ("con", "z4c"):
        for p in flib.dumps(rundir, var):
            d = flib.Dump(p)
            for b in d.blocks:
                for v in b["data"].values():
                    n += int(np.size(v) - np.isfinite(v).sum())
    return n


def one(rundir):
    d = flib.Dump(flib.dumps(rundir, "con")[-1])
    x, y, z, dv, h = d.flat("con_H")
    _, _, _, _, mx = d.flat("con_Mx")
    _, _, _, _, zz = d.flat("con_Z")
    gz = 2.0 * np.sqrt(np.maximum(zz, 0.0))
    a = np.abs(h)
    dx = dv ** (1.0 / 3.0)
    lay = x > LBOX - 4.0
    t = np.maximum(np.abs(y), np.abs(z))
    fine = lay & (dx < 0.75) & (dx > 0.3)
    coarse = lay & (dx > 0.75) & (t < 12.0)   # away from the other faces
    junc = lay & (t >= 2.0) & (t < 6.0)
    r = {"time": d.time, "nonfinite": nonfinite(rundir),
         "H_face_fine_max": float(a[fine].max()), "H_face_coarse_max": float(a[coarse].max()),
         "H_junction_max": float(a[junc].max()),
         "G_face_fine_max": float(gz[fine].max()), "G_face_coarse_max": float(gz[coarse].max()),
         "Mx_face_fine_max": float(np.abs(mx[fine]).max()),
         "n_fine": int(fine.sum()), "n_coarse": int(coarse.sum())}
    # boundary cells of the +x face along y at the smallest positive z
    bc = (np.abs(x + 0.5 * dx - LBOX) < 1e-9) & (np.abs(z - 0.5 * dx) < 1e-9)
    o = np.argsort(y[bc])
    r["face_y"] = [float(q) for q in y[bc][o]]
    r["face_H"] = [float(q) for q in h[bc][o]]
    # line along x at the smallest positive y, z
    ln = (np.abs(y - 0.5 * dx) < 1e-9) & (np.abs(z - 0.5 * dx) < 1e-9) & (x > 4.0)
    o = np.argsort(x[ln])
    r["line_x"] = [float(q) for q in x[ln][o]]
    r["line_H"] = [float(q) for q in h[ln][o]]
    # plane z = smallest positive cell centre, x > 8: scattered points for the map
    pl = (np.abs(z - 0.5 * dx) < 1e-9) & (x > 8.0) & (np.abs(y) < 8.0)
    return r, (x[pl], y[pl], dx[pl], a[pl])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rundir")
    p.add_argument("--out", default=os.path.join(flib._HERE, "results", "t1.json"))
    p.add_argument("--fig", default=os.path.join(flib._HERE, "figs", "t1_smrface"))
    a = p.parse_args()
    res, maps = {}, {}
    for c in ("smr_stock", "smr_full"):
        res[c], maps[c] = one(os.path.join(a.rundir, c))
    s, f = res["smr_stock"], res["smr_full"]
    res["ratios"] = {"H_face_fine": f["H_face_fine_max"] / s["H_face_fine_max"],
                     "H_face_coarse": f["H_face_coarse_max"] / s["H_face_coarse_max"],
                     "H_junction_full_over_stock_face_max":
                         f["H_junction_max"] / max(s["H_face_fine_max"], s["H_face_coarse_max"])}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    for c in ("smr_stock", "smr_full"):
        print(c, {k: v for k, v in res[c].items() if not isinstance(v, list)})
    print(res["ratios"])

    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH * 0.8, 5.6))
    fig.subplots_adjust(left=0.11, right=0.9, bottom=0.09, top=0.94, wspace=0.3, hspace=0.3)
    col = {"smr_stock": fs.PAL["red"], "smr_full": fs.PAL["blue"]}
    lab = {"smr_stock": "stock", "smr_full": "full set with damping"}
    for c in ("smr_stock", "smr_full"):
        axs[0, 0].semilogy(res[c]["line_x"], np.maximum(np.abs(res[c]["line_H"]), 1e-12),
                           "o-", ms=2.5, lw=0.9, color=col[c], label=lab[c])
        axs[0, 1].semilogy(res[c]["face_y"], np.maximum(np.abs(res[c]["face_H"]), 1e-12),
                           "o-", ms=2.5, lw=0.9, color=col[c], label=lab[c])
    axs[0, 0].set_xlabel(r"$x$ (line $y = z = 0^+$)", labelpad=-1)
    axs[0, 0].set_ylabel(r"$|H|$")
    axs[0, 0].set_title(r"towards the $+x$ face, $t = %g$" % s["time"], fontsize=10)
    axs[0, 0].legend(fontsize=8)
    axs[0, 1].set_xlabel(r"$y$ (boundary cells of the $+x$ face, $z = 0^+$)", labelpad=-1)
    for yy in (-4.0, 4.0):
        axs[0, 1].axvline(yy, color="0.6", lw=0.8)
    axs[0, 1].set_title("along the face; grey: fine/coarse junction", fontsize=10)
    for ax, c in zip(axs[1], ("smr_stock", "smr_full")):
        x, y, dx, v = maps[c]
        sc = ax.scatter(x, y, c=np.log10(np.maximum(v, 1e-12)), s=np.where(dx < 0.75, 3.0, 12.0),
                        marker="s", cmap=fs.CMAP["dens"], vmin=-9, vmax=-3, rasterized=True,
                        linewidths=0)
        ax.set_xlim(8, 16)
        ax.set_ylim(-8, 8)
        ax.set_xlabel(r"$x$", labelpad=-1)
        ax.set_ylabel(r"$y$", labelpad=-2)
        ax.set_title(lab[c] + r": $\log_{10}|H|$, plane $z = 0^+$", fontsize=10)
    cax = fig.add_axes([0.915, 0.09, 0.012, 0.36])
    fig.colorbar(sc, cax=cax)
    fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
