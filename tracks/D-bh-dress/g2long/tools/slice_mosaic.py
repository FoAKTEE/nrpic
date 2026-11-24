#!/usr/bin/env python3
"""Multi-scale slice mosaic of a long run (checklist C12 of stage/G2): the z = 0 slice at one
time, four zoom levels (half-widths 384, 96, 24, 6 M by default), each panel boxing the next;
row 1 the lapse alpha (z4c slice), row 2 the energy density E of the particles (tmunu_E slice; white:
no particle cloud in the slice;
log scale), with the finder's mean horizon radius drawn in the innermost panels.

Every pixel takes the value of the finest leaf cell that contains it (AthenaK MeshBlocks are
leaves; nearest-cell sampling, no interpolation), so refinement boundaries stay visible.

    slice_mosaic.py --run RUNDIR --base esfl --time 500 [--halves 384 96 24 6] [--npix 300]
                    --out DIR
Writes DIR/slice_mosaic_<base>_t<time>.png/.pdf and a JSON with the files and times used.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/athenak/vis/python")
import bin_convert  # noqa: E402
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402


def pick(run, base, kind, t):
    best = None
    for p in sorted(glob.glob(os.path.join(run, "bin", f"{base}.{kind}.[0-9]*.bin"))):
        fd = bin_convert.read_binary(p)
        d = abs(float(fd["time"]) - t)
        if best is None or d < best[0]:
            best = (d, p, fd)
    return best[1], best[2]


def sample(fd, var, half, npix):
    """Image of `var` on [-half, half]^2 (pixel centres), finest leaf cell wins."""
    xs = (np.arange(npix) + 0.5) / npix * 2 * half - half
    img = np.full((npix, npix), np.nan)
    lev = np.full((npix, npix), np.inf)          # cell size of the value placed
    nx1, nx2 = fd["nx1_mb"], fd["nx2_mb"]
    for b in range(fd["n_mbs"]):
        g = fd["mb_geometry"][b]
        ix = fd["mb_index"][b]
        dx = (g[1] - g[0]) / nx1
        dy = (g[3] - g[2]) / nx2
        x0 = g[0] + ix[0] * dx
        y0 = g[2] + ix[2] * dy
        q = np.asarray(fd["mb_data"][var][b], dtype=float)[0]
        n2, n1 = q.shape
        x1, y1 = x0 + n1 * dx, y0 + n2 * dy
        ii = np.nonzero((xs >= x0) & (xs < x1))[0]
        jj = np.nonzero((xs >= y0) & (xs < y1))[0]
        if ii.size == 0 or jj.size == 0:
            continue
        ci = np.clip(((xs[ii] - x0) / dx).astype(int), 0, n1 - 1)
        cj = np.clip(((xs[jj] - y0) / dy).astype(int), 0, n2 - 1)
        sub = q[np.ix_(cj, ci)]
        J, I = np.meshgrid(jj, ii, indexing="ij")
        better = dx < lev[J, I]
        img[J[better], I[better]] = sub[better]
        lev[J[better], I[better]] = dx
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--time", type=float, required=True)
    ap.add_argument("--halves", type=float, nargs="+", default=[384.0, 96.0, 24.0, 6.0])
    ap.add_argument("--npix", type=int, default=300)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pz, fz = pick(a.run, a.base, "z4c", a.time)
    pe, fe = pick(a.run, a.base, "tmunu_E", a.time)
    hz = None
    hp = os.path.join(a.run, a.base + ".horizon_summary_0.txt")
    if os.path.exists(hp):
        h = np.loadtxt(hp, comments="#", ndmin=2)
        i = int(np.argmin(np.abs(h[:, 1] - float(fz["time"]))))
        hz = float(h[i, 10]) if np.isfinite(h[i, 10]) else None
    H = a.halves
    fs.use_style()
    panel, gap, left, bottom = 1.585, 0.06, 0.62, 0.36
    fig, axes, cax = fs.slice_mosaic(2, len(H), left=left, cbar="right")
    cax.remove()
    xc = left + len(H) * (panel + gap) + 0.04
    cax_a = fs.inch_axes(fig, xc, bottom + panel + gap, 0.08, panel)
    cax_e = fs.inch_axes(fig, xc, bottom, 0.08, panel)
    imgs_a = [sample(fz, "z4c_alpha", L, a.npix) for L in H]
    imgs_e = [sample(fe, "tmunu_E", L, a.npix) for L in H]
    epos = np.concatenate([im[np.isfinite(im) & (im > 0)].ravel() for im in imgs_e])
    vmax_e = float(np.percentile(epos, 99.9)) if epos.size else 1.0
    vmin_e = vmax_e * 1e-4
    for j, L in enumerate(H):
        ext = [-L, L, -L, L]
        ia = axes[0, j].imshow(imgs_a[j], origin="lower", extent=ext, cmap=fs.CMAP.get("dens", "magma"),
                               vmin=0.0, vmax=1.0, interpolation="nearest")
        ie = axes[1, j].imshow(np.where(imgs_e[j] > 0, imgs_e[j], np.nan), origin="lower", extent=ext,
                               cmap="viridis", norm=LogNorm(vmin=vmin_e, vmax=vmax_e), interpolation="nearest")
        for i in range(2):
            ax = axes[i, j]
            if j + 1 < len(H):
                s = H[j + 1]
                ax.plot([-s, s, s, -s, -s], [-s, -s, s, s, -s], color="w" if i == 1 else "k", lw=1.0)
            if j > 0:
                ax.set_xlim(-L, L)
                ax.set_ylim(-L, L)
            if hz is not None and L <= 8 * hz:
                th = np.linspace(0, 2 * np.pi, 200)
                ax.plot(hz * np.cos(th), hz * np.sin(th), color="w", lw=1.0, ls="--")
            fs.slice_ticks(ax, L, show_x=(i == 1), show_y=(j == 0))
            if i == 0:
                ax.set_title(f"$\\pm{L:g}\\,M$", fontsize=9)
        if j == 0:
            axes[0, j].set_ylabel(r"$y/M$")
            axes[1, j].set_ylabel(r"$y/M$")
        axes[1, j].set_xlabel(r"$x/M$")
    fig.colorbar(ia, cax=cax_a, label=r"lapse $\alpha$")
    fig.colorbar(ie, cax=cax_e, label=r"particle $E$")
    stem = os.path.join(a.out, f"slice_mosaic_{a.base}_t{int(round(a.time))}")
    fs.save(fig, stem)
    plt.close(fig)
    info = dict(z4c=pz, tmunu_E=pe, t_z4c=float(fz["time"]), t_E=float(fe["time"]), r_AH_mean=hz,
                halves=H, E_range=[vmin_e, vmax_e], out=stem + ".png")
    with open(stem + ".json", "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
