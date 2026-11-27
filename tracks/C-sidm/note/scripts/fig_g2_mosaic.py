"""Figure (gate G2): multi-scale slice mosaic of the two bracket members on the fine mesh M/16
at a million particles (release core-v0.6 card build).

Rows: y0 = 0.344 kicked inward at t = 0 (top), the stable member y0 = 0.324 kicked inward at
t = 220 M (middle), the unstable member y0 = 0.344 at t = 220 M (bottom), the first snapshot
after its lapse marker (alpha_min = 0.3 at about 218 M; no horizon finder). Columns: square
windows of half-width 12, 3 and 0.75 M about the origin; each box marks the window of the panel
to its right. Colour: rest mass per coordinate volume in the slab |z| < half-width / 8, from the
particle snapshots (sum of particle masses in a cell of the 96 x 96 grid over the cell's
coordinate volume), in units of M^-2; white cells hold no particle.
Reads cc.part.00000.bin and cc.part.00022.bin of the registered runs g2_b344m16 and g2_b324m16
(common.RUNS), checked against the checksums the runs recorded.
"""
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

STEM = "fig_g2_mosaic"
HALVES = (12.0, 3.0, 0.75)
NBIN = 96
ROWS = (("g2_b344m16", "cc.part.00000.bin", r"$y_0=0.344$, $t=0$"),
        ("g2_b324m16", "cc.part.00022.bin", r"$y_0=0.324$, $t=220\,M$"),
        ("g2_b344m16", "cc.part.00022.bin", r"$y_0=0.344$, $t=220\,M$"))


def snapshot(key, rel):
    """Particle snapshot NRPSNAP1 (python/nrpic/collide.py read_snapshot): positions, mass."""
    with open(cm.run_file(key, rel), "rb") as f:
        if f.read(8) != b"NRPSNAP1":
            raise SystemExit(f"{rel} of {cm.RUNS[key]} is not a particle snapshot")
        t, = struct.unpack("<d", f.read(8))
        n, _ = struct.unpack("<2q", f.read(16))
        r = np.fromfile(f, dtype="<f8", count=7 * n).reshape(n, 7)
    return t, r[:, 0:3], r[:, 6]


def slab_density(x, m, half):
    dz = half / 8.0
    s = np.abs(x[:, 2]) < dz
    edges = np.linspace(-half, half, NBIN + 1)
    H, _, _ = np.histogram2d(x[s, 0], x[s, 1], bins=(edges, edges), weights=m[s])
    vol = (2 * half / NBIN) ** 2 * (2 * dz)
    return H.T / vol, int(s.sum())


def main():
    out = cm.out_dir("figures")
    cz.use_style()
    fig, axes, cax = cz.slice_mosaic(len(ROWS), len(HALVES), fig_w=6.4, cbar="left")
    data, info = [], {}
    for i, (key, rel, lab) in enumerate(ROWS):
        t, x, m = snapshot(key, rel)
        row = []
        for j, half in enumerate(HALVES):
            rho, ns = slab_density(x, m, half)
            row.append(rho)
            info[f"{key}:{rel}:half{half:g}"] = dict(t=t, n_part=len(m), n_slab=ns,
                                                    rho_max=float(rho.max()))
        data.append(row)
    pos = np.concatenate([r[r > 0] for row in data for r in row])
    norm = LogNorm(vmin=np.percentile(pos, 2), vmax=pos.max())
    for i, row in enumerate(data):
        for j, rho in enumerate(row):
            ax = axes[i, j]
            half = HALVES[j]
            im = ax.imshow(np.ma.masked_equal(rho, 0.0), origin="lower", cmap=cz.CMAP["dens"],
                           norm=norm, extent=(-half, half, -half, half), interpolation="nearest")
            if j + 1 < len(HALVES):
                cz.zoom_marker(ax, HALVES[j + 1], half, connect="right")
            cz.slice_ticks(ax, half, show_x=(i == len(ROWS) - 1), show_y=True)
            if j == 0:
                cz.run_label(ax, ROWS[i][2], on_dark=False)
            if i == len(ROWS) - 1:
                ax.set_xlabel(r"$x/M$")
            if j == 0:
                ax.set_ylabel(r"$y/M$")
    cz.tall_colorbar(fig, im, cax, r"rest mass per volume in the slab $[M^{-2}]$")
    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    for k, v in info.items():
        print(f"{STEM}: {k}: {v}")


if __name__ == "__main__":
    main()
