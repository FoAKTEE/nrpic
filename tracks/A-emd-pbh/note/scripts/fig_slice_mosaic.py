"""Multi-scale slice mosaic of the Szekeres hole in the code (gate G2, item C13).

Reads the plane next to z = 0 (cells k = N/2, z = +h/2) of the AthenaK field dumps of the
256-cell member (run SZK256, dumps at proper time 0, 20 and 40; checked against the run's
sha256sums.txt) and draws, at three magnifications (the whole box of side 16, a quarter of
it, a sixteenth), the deposited density E relative to its plane mean (top row) and the local
Hamiltonian residual |H| / (16 pi E) (bottom row) at proper time 40. Zoom boxes mark the next
panel's extent. Dump layout: tracks/A-emd-pbh/szekeres/scripts/analyse_code_runs.py.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

common.RUNS["szk256"] = "A-20261125-231808-0784bc9"
STEM = "fig_slice_mosaic"
DUMP = "szk.field.00004.bin"   # proper time 40


def read_plane(path):
    with open(path, "rb") as f:
        head = f.read(40)
        t = float(np.frombuffer(head[8:16], "<f8")[0])
        n1, n2, n3 = (int(v) for v in np.frombuffer(head[16:40], "<i8"))
    nc, k, npl = n1 * n2 * n3, n3 // 2, n1 * n2
    E = np.fromfile(path, "<f4", count=npl, offset=40 + 4 * npl * k).astype(float).reshape(n2, n1)
    H = np.fromfile(path, "<f8", count=npl, offset=40 + 8 * nc + 8 * npl * k).reshape(n2, n1)
    return t, n1, E, H


def main():
    out = common.out_dir("figures")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    t, n, E, H = read_plane(common.run_file("szk256", DUMP))
    half_box, h = 8.0, 16.0 / n
    x = -half_box + (np.arange(n) + 0.5) * h
    # (centre x, half width): the whole box, the shell on the +x side, the core edge inside it
    views = ((0.0, 8.0), (3.5, 2.0), (2.75, 0.5))
    rel = np.log10(E / E.mean())
    res = np.log10(np.abs(H) / (16 * np.pi * E) + 1e-30)
    fig, axes, cax = fs.slice_mosaic(2, 3, panel=2.05, left=0.75, bottom=0.45, fig_w=8.0, cbar="right",
                                     cbar_w=0.08, cbar_gap=0.1)
    ext = (x[0] - h / 2, x[-1] + h / 2, x[0] - h / 2, x[-1] + h / 2)
    vr = (np.percentile(rel, 0.5), np.percentile(rel, 99.95))
    vh = (np.percentile(res, 5), np.percentile(res, 99.9))
    for row, (img, cmap, vlim) in enumerate(((rel, fs.CMAP["dens"], vr), (res, "viridis", vh))):
        for col, (xc, half) in enumerate(views):
            ax = axes[row, col]
            im = ax.imshow(img, origin="lower", extent=ext, cmap=cmap, vmin=vlim[0], vmax=vlim[1],
                           interpolation="nearest")
            ax.set_xlim(xc - half, xc + half)
            ax.set_ylim(-half, half)
            if col + 1 < len(views):
                c2, s2 = views[col + 1]
                ax.plot([c2 - s2, c2 + s2, c2 + s2, c2 - s2, c2 - s2], [-s2, -s2, s2, s2, -s2], color="w", lw=1.0)
            ax.set_xticks([xc - half / 2, xc, xc + half / 2])
            ax.set_yticks([-half / 2, 0, half / 2])
            if row == 0:
                ax.set_xticklabels([])
            if col != 0:
                ax.set_yticklabels([])
            if row == 1:
                ax.set_xlabel("x")
            if col == 0:
                ax.set_ylabel("y")
            if row == 0:
                ims0 = im
            else:
                ims1 = im
    # two colorbars stacked on the right
    W, Hh = fig.get_size_inches()
    pos = cax.get_position()
    cax.set_visible(False)
    c0 = fig.add_axes([pos.x0, pos.y0 + pos.height * 0.53, pos.width, pos.height * 0.47])
    c1 = fig.add_axes([pos.x0, pos.y0, pos.width, pos.height * 0.47])
    fig.colorbar(ims0, cax=c0, label=r"$\log_{10} E/\langle E\rangle$")
    fig.colorbar(ims1, cax=c1, label=r"$\log_{10}|H|/(16\pi E)$")
    fs.save(fig, os.path.join(out, STEM))
    print(f"{STEM}: tau = {t:.3f}, N = {n}, plane mean E = {E.mean():.6e}, max E/<E> = {E.max() / E.mean():.4g}, "
          f"median |H|/(16 pi E) = {np.median(np.abs(H) / (16 * np.pi * E)):.3e}, "
          f"max = {np.max(np.abs(H) / (16 * np.pi * E)):.3e}")
    common.report_checks(STEM)


if __name__ == "__main__":
    main()
