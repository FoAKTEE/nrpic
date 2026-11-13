"""Kretschmann scalar of a Brill-Lindquist puncture at t = 0 against the exact
I = 48 M^2/R^6, R = r (1 + M/2r)^2, in the plane y = y0 written by the curvature
diagnostic, for runs with different finite-difference orders (nghost).

    python3 curvature.py [<label>=<rundir> ...] [--out NAME]

Defaults: ng2=runs/dev/curv/ng2 ng4=runs/dev/curv/ng4 (basename ``curv``). The
plane position y0 is not stored in the slice file; it is recovered from the
recorded sqrt(gamma) = psi^6, psi = 1 + M/2r, and checked against alpha = psi^-2
(precollapsed lapse).
"""
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from common import FIGS, parse_cli, read_curv_hst, read_curv_slice, run_path
from nrpic import figstyle as fs

runs, opts = parse_cli(sys.argv[1:], defaults=["ng2=runs/dev/curv/ng2",
                                               "ng4=runs/dev/curv/ng4"], options=("out",))
out = opts.get("out", "curvature_puncture")
M = 1.0
L = 8.0                              # half-width of the test domain
colors = [fs.PAL["yellow"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]


def nghost_of(d, label):
    """nghost from the run log / input copy / label (in this order)."""
    for name in ("cmd.txt", "run.log"):
        p = run_path(d, name)
        if os.path.exists(p):
            m = re.search(r"mesh/nghost=(\d)", open(p).read())
            if m:
                return int(m.group(1))
    m = re.search(r"(\d)", label)
    return int(m.group(1)) if m else 4


data = []
for label, d in runs:
    t, a = read_curv_slice(run_path(d, "curv.curv.00000.bin"))
    x, z, dx, I, E, al, sg = a.T
    # plane position from sqrt(gamma) = psi^6 (vacuum Brill-Lindquist)
    rg = M / (2.0 * (sg ** (1.0 / 6.0) - 1.0))
    ra = M / (2.0 * (al ** -0.5 - 1.0))
    near = x ** 2 + z ** 2 < 4.0
    y0 = np.sqrt(np.median(rg[near] ** 2 - x[near] ** 2 - z[near] ** 2))
    y0a = np.sqrt(np.median(ra[near] ** 2 - x[near] ** 2 - z[near] ** 2))
    r = np.sqrt(x ** 2 + y0 ** 2 + z ** 2)
    R = r * (1.0 + M / (2.0 * r)) ** 2
    Iex = 48.0 * M ** 2 / R ** 6
    rel = I / Iex - 1.0
    ng = nghost_of(d, label)
    bnd = (np.abs(x) > L - ng * dx) | (np.abs(z) > L - ng * dx)
    data.append(dict(label=label, x=x, z=z, r=r, I=I, Iex=Iex, rel=rel, ng=ng, bnd=bnd,
                     dx=dx[0]))
    hst = read_curv_hst(run_path(d, "curv.curv.hst"))
    print(f"{label}: t = {t}, {len(x)} cells, dx = {dx[0]}, nghost = {ng} "
          f"(FD order {2 * (ng - 1)}); y0 from sqrt(gamma) = {y0:.12f}, from alpha = "
          f"{y0a:.12f}")
    for lo, hi in ((0, 1), (1, 2), (2, 4), (4, 6), (6, 12)):
        s = (r >= lo) & (r < hi) & ~bnd
        print(f"   r in [{lo},{hi}) interior: median |rel| {np.median(np.abs(rel[s])):.2e}"
              f", max {np.abs(rel[s]).max():.2e}")
    print(f"   cells within nghost of the outer boundary: max |rel| "
          f"{np.abs(rel[bnd]).max():.2e}, median {np.median(np.abs(rel[bnd])):.2e}")
    if len(hst):
        print(f"   curv.hst: max|I| = {hst[0, 1]:.4e} at ({hst[0, 2]}, {hst[0, 3]}, "
              f"{hst[0, 4]}); exact maximum 48/(2M)^6 = {48 / 64:.4f}; max E column = "
              f"{hst[0, 5]:.4e} at ({hst[0, 6]:.3e}, {hst[0, 7]:.3e}, {hst[0, 8]:.3e})")

fs.use_style()
fig = plt.figure(figsize=(fs.FULL_WIDTH, 7.0))
ax_i = fs.inch_axes(fig, 0.72, 4.18, 3.05, 2.74)
ax_e = fs.inch_axes(fig, 4.72, 4.18, 3.05, 2.74)
# maps: two square touching panels with a colorbar on the right
pw = 3.2
maps = [fs.inch_axes(fig, 0.72 + i * (pw + 0.06), 0.5, pw, pw) for i in range(2)]
cax = fs.inch_axes(fig, 0.72 + 2 * pw + 0.06 + 0.12, 0.5, 0.1, pw)

rr = np.geomspace(0.12, 12.5, 600)
RR = rr * (1 + M / (2 * rr)) ** 2
for D, c in zip(data, colors):
    lab = f"nghost = {D['ng']} (order {2 * (D['ng'] - 1)})"
    i, b = ~D["bnd"], D["bnd"]
    ax_i.plot(D["r"][i], D["I"][i], ls="none", marker="o", ms=2.0, mew=0, color=c,
              alpha=0.7, label=lab, rasterized=True)
    ax_i.plot(D["r"][b], D["I"][b], ls="none", marker="o", ms=2.6, mfc="none", mec=c,
              mew=0.5, alpha=0.8, rasterized=True)
    ax_e.plot(D["r"][i], np.abs(D["rel"][i]), ls="none", marker="o", ms=2.0, mew=0,
              color=c, alpha=0.7, label=lab, rasterized=True)
    ax_e.plot(D["r"][b], np.abs(D["rel"][b]), ls="none", marker="o", ms=2.6, mfc="none",
              mec=c, mew=0.5, alpha=0.8, rasterized=True)
ax_i.plot(rr, 48 * M ** 2 / RR ** 6, **fs.GUIDE, label=r"$48M^2/R^6$")
for ax in (ax_i, ax_e):
    ax.axvline(M / 2, **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.12, 12.5)
    ax.set_xlabel(r"$r\,[M]$")
ax_i.text(M / 2 * 0.94, 2e-3, "minimal\nsurface", color="grey", fontsize="small",
          ha="right")
ax_i.set_ylabel(r"$I\,[M^{-4}]$")
ax_i.set_ylim(1e-6, 2e2)
ax_i.legend(loc="lower left", fontsize="small", handletextpad=0.2)
ax_e.set_ylabel(r"$|I/I_{\rm exact}-1|$")
ax_e.set_ylim(1e-9, 1e3)
ax_e.plot([], [], ls="none", marker="o", ms=3, mfc="none", mec="k", mew=0.6,
          label="within nghost cells\nof the outer boundary")
ax_e.legend(loc="lower left", fontsize="small", handletextpad=0.2)

norm = LogNorm(1e-8, 1e1)
for ax, D in zip(maps, data[:2]):
    dx = D["dx"]
    n = int(round(2 * L / dx))
    img = np.full((n, n), np.nan)
    ix = np.floor((D["x"] + L) / dx).astype(int)
    iz = np.floor((D["z"] + L) / dx).astype(int)
    img[iz, ix] = np.abs(D["rel"])
    im = ax.imshow(img, origin="lower", extent=(-L, L, -L, L), cmap=fs.CMAP["dens"],
                   norm=norm, interpolation="none", aspect="equal", rasterized=True)
    ax.text(0.04, 0.95, f"nghost = {D['ng']}", transform=ax.transAxes, va="top",
            color="white")
    fs.slice_ticks(ax, L, show_y=(ax is maps[0]))
    ax.set_xlabel(r"$x\,[M]$", labelpad=-2)
maps[0].set_ylabel(r"$z\,[M]$")
fig.colorbar(im, cax=cax, label=r"$|I/I_{\rm exact}-1|$ in the plane $y=y_0$")
maps[0].text(0.04, 0.04, rf"plane $y_0={y0:.3f}\,M$, dx = {data[0]['dx']:g} M",
             transform=maps[0].transAxes, color="white")
print("\n".join(fs.save(fig, os.path.join(FIGS, out))))
