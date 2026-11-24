#!/usr/bin/env python3
"""Multi-scale slice mosaic with zoom boxes (G2 item C13) from a full-GR population run.

    python3 fig_mosaic.py --run DIR [--snap N] [--dump M] [--out $NRPIC_RUN_DIR]

Top row: particle density (cloud-in-cell on a 256^3 mesh, projected over a slab of thickness
L/8 about the plane through the largest FoF halo) of the whole box, a zoom of side L/4 and a
zoom of side L/16 around that halo, each zoom box drawn on the panel before it. Bottom row:
the metric on the same plane from the double-precision Z4c dump nearest in time (lapse over
its box mean, mean curvature K over the background -3 a^(-3/2), and the flat TT strain
|Lambda h| of the conformal metric), whole box. Writes pop_gr_mosaic.png/.pdf and
mosaic.json (the halo, the slab, the dump and snapshot times).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "gw_diag"))
sys.path.insert(0, os.path.join(ROOT, "python"))
import analyze as an                                   # noqa: E402
from gwdiag import binio, readers, tt                  # noqa: E402
from nrpic import figstyle as fs                       # noqa: E402
from nrpic.newton import read_snapshot                 # noqa: E402

L = 8.0


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


def slab_projection(x, m, centre, half, width, nz_axis=2, npix=256):
    """Surface density of the particles in the square of side 2 half about centre (periodic),
    projected over |x_z - centre_z| < width/2; returns the image [iy, ix] and the extent."""
    d = np.mod(x - centre + 0.5*L, L) - 0.5*L
    sel = (np.abs(d[:, nz_axis]) < 0.5*width) & (np.abs(d[:, 0]) < half) & (np.abs(d[:, 1]) < half)
    H, xe, ye = np.histogram2d(d[sel, 0], d[sel, 1], bins=npix, range=[[-half, half], [-half, half]],
                               weights=m[sel])
    area = (2*half/npix)**2
    rho_bar = m.sum()/L**3
    img = H.T/(area*width*rho_bar)                     # mean density over the slab, / mean
    return img, (centre[0] - half, centre[0] + half, centre[1] - half, centre[1] + half)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--snap", type=int, default=-1, help="index of pop.part.NNNNN.bin (-1: last)")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    snaps = sorted(glob.glob(os.path.join(a.run, "pop.part.*.bin")))
    sn = snaps[a.snap]
    t, cyc, x, u, m, tag = read_snapshot(sn)
    asn = float(scale(t))
    n = round(len(x)**(1/3))
    W = np.sqrt(1.0 + (u*u).sum(1)/asn**2)
    hal, _ = an.halo_catalog(x, u/W[:, None], m, tag, asn, L, L/n)
    c = np.array(hal[0]["x"])
    dumps = sorted(glob.glob(os.path.join(a.run, "bin", "pop.z4cd.*.bin")))
    tdump = []
    for p in dumps:
        with open(p, "rb") as f:
            head = f.read(400).decode(errors="replace")
        tdump.append(float(head.split("time=")[1].split()[0]))
    j = int(np.argmin(np.abs(np.array(tdump) - t)))
    d = binio.read_bin(dumps[j], strip_prefix=True)
    grid = d["grid"]
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    ad = float(scale(d["time"]))
    k = int(np.floor(c[2]/grid.dx[2])) % grid.n[2]
    h = gt - np.eye(3)[:, :, None, None, None]
    hTT = tt.tt_project(h, grid)
    hnorm = np.sqrt((hTT**2).sum((0, 1)))
    info = {"snapshot": os.path.basename(sn), "t": float(t), "a": asn,
            "halo": {"x": c.tolist(), "M": hal[0]["M"], "N": hal[0]["N"], "r_half": hal[0]["r_half"]},
            "n_halos": len(hal), "dump": os.path.basename(dumps[j]), "t_dump": float(d["time"]),
            "plane_k": k, "slab_width": L/8}

    fs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, axs = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.06, right=0.97, bottom=0.07, top=0.95, wspace=0.42, hspace=0.32)
    halves = (0.5*L, L/8, L/32)
    for p, half in enumerate(halves):
        cen = np.array([0.5*L, 0.5*L, c[2]]) if p == 0 else c
        img, ext = slab_projection(x, m, cen, half, L/8)
        ax = axs[0, p]
        im = ax.imshow(np.log10(np.maximum(img, 1e-2)), origin="lower", extent=ext, cmap="magma",
                       vmin=-1, vmax=max(2.0, float(np.log10(img.max()))))
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        ax.set_title([r"box, $a = %.0f$" % asn, r"zoom $L/4$", r"zoom $L/16$"][p], fontsize=8)
        ax.set_xlabel(r"$x$")
        if p == 0:
            ax.set_ylabel(r"$y$" + "\n" + r"$\log_{10}\rho/\bar\rho$ (slab $L/8$)")
        if p < 2:
            hz = halves[p + 1]
            ax.add_patch(Rectangle((c[0] - hz, c[1] - hz), 2*hz, 2*hz, fill=False, ec="c", lw=1.0))
    ext = (0, L, 0, L)
    panels = [(alpha[k]/alpha.mean(), r"$\alpha/\langle\alpha\rangle$", "viridis"),
              ((trK[k] - (-3*ad**-1.5))/(3*ad**-1.5), r"$(K - \bar K)/|\bar K|$", "RdBu_r"),
              (np.log10(np.maximum(hnorm[k], 1e-12)), r"$\log_{10}|\Lambda h|$", "cividis")]
    for p, (f2, lab, cm) in enumerate(panels):
        ax = axs[1, p]
        if cm == "RdBu_r":
            v = float(np.percentile(np.abs(f2), 99.5))  # the full range (B-20261124-135412-ab31dae) washes the plane out
            im = ax.imshow(f2, origin="lower", extent=ext, cmap=cm, vmin=-v, vmax=v)
        else:
            im = ax.imshow(f2, origin="lower", extent=ext, cmap=cm)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        ax.set_title(lab + r", $a = %.0f$" % ad, fontsize=8)
        ax.set_xlabel(r"$x$")
        ax.plot(c[0], c[1], "c+", ms=7)
        if p == 0:
            ax.set_ylabel(r"$y$ (plane through the largest halo)")
    fs.save(fig, os.path.join(a.out, "pop_gr_mosaic"))
    plt.close(fig)
    with open(os.path.join(a.out, "mosaic.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
