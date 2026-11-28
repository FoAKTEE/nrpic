"""Figure: slice mosaic of the nonlinear curvature perturbation zeta of one G3 baseline box at N_f.

Reads the zeta field that g3/read_pilot.py --save-fields wrote for one member (the delta-N variable of
SCOPE 4d.1 (ii) on the 128^3 box, box mean removed, from the table map of g3/JOURNAL.md entry 12) and,
beside it, the same member's R^NR; draws the slice through the cell of largest zeta, rolled (periodic box)
so that cell sits at the centre, at three magnifications (the box, 32 cells, 8 cells), in units of the
box's own standard deviation of zeta. A bottom row shows zeta + R^NR, the part of zeta that is not linear
(R^NR = -zeta at first order), on its own colour scale. Axes in cells.
Writes OUT/fig_g3_mosaic.{pdf,png,json}.

    fig_g3_mosaic.py OUT --read <reading run dir> --member p000
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--read", required=True)
    ap.add_argument("--member", default="b000")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    z = np.load(os.path.join(a.read, f"{a.member}_zeta.npy")).astype(np.float64)
    R = np.load(os.path.join(a.read, f"{a.member}_R.npy")).astype(np.float64)
    rec = json.load(open(os.path.join(a.read, f"{a.member}.json")))
    N = z.shape[0]
    sz = z.std()
    iz, iy, ix = np.unravel_index(np.argmax(z), z.shape)

    def sl(f):
        return np.roll(np.roll(f[iz], N // 2 - iy, axis=0), N // 2 - ix, axis=1)

    s1 = sl(z) / sz
    s2 = sl(z + R) / sz
    v1 = float(np.abs(s1).max())
    v2 = float(np.abs(s2).max())
    fs.use_style()
    import matplotlib.pyplot as plt
    halves = [N / 2, N / 8, N / 32]
    fig, axes, cax = fs.slice_mosaic(2, 3, panel=2.2, gap=0.06, left=0.62, bottom=0.42, fig_w=8.3,
                                     cbar="right", cbar_gap=0.0)
    cax.remove()
    W, H = fig.get_size_inches()
    caxes = [fs.inch_axes(fig, 0.62 + 3 * 2.26 + 0.05, 0.42 + 2.26, 0.08, 2.2),
             fs.inch_axes(fig, 0.62 + 3 * 2.26 + 0.05, 0.42, 0.08, 2.2)]
    ext = [-N / 2, N / 2, -N / 2, N / 2]
    for row, (img, vm, cmap, lab) in enumerate(((s1, v1, fs.CMAP["diverging"], r"$\zeta/\sigma_\zeta$"),
                                                 (s2, v2, "PuOr_r", r"$(\zeta + \mathcal{R})/\sigma_\zeta$"))):
        for k, ax in enumerate(axes[row]):
            h = int(halves[k])                     # draw only the cells of this panel (smaller vector file)
            c0 = N // 2
            sub = img[c0 - h:c0 + h, c0 - h:c0 + h]
            im = ax.imshow(sub, origin="lower", extent=[-h, h, -h, h], cmap=cmap, vmin=-vm, vmax=vm,
                           interpolation="nearest")
            if k + 1 < len(halves):
                fs.zoom_marker(ax, halves[k + 1], halves[k], connect="right")
            else:
                ax.set_xlim(-halves[k], halves[k])
                ax.set_ylim(-halves[k], halves[k])
            fs.slice_ticks(ax, halves[k], show_x=(row == 1), show_y=(k == 0))
            if row == 1:
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.0f}"))
                ax.set_xlabel(r"$x/\Delta x$")
            if k == 0:
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.0f}"))
                ax.set_ylabel(r"$y/\Delta x$")
        cb = fig.colorbar(im, cax=caxes[row])
        cb.set_label(lab)
    fs.save(fig, os.path.join(a.out, "fig_g3_mosaic"))
    summary = dict(read=a.read, member=a.member, run=rec["run"], N=int(N), sigma_zeta=float(sz),
                   sigma_lin=rec["sigma_lin"], peak_cell=[int(iz), int(iy), int(ix)],
                   peak_over_sigma=float(z.max() / sz), min_over_sigma=float(z.min() / sz),
                   rms_nonlinear_over_sigma=float((z + R).std() / sz), slice_max_nonlinear=v2)
    json.dump(summary, open(os.path.join(a.out, "fig_g3_mosaic.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
