"""Figure: slice mosaic of the curvature perturbation at the end of the ultra-slow-roll run.

Reads the last dump (N_f) of the release card run E-20261121-211214-0377aab (256^3, first seed,
full amplitude; the size of the dump is checked against the run's sha256sums.txt entry, the file
itself is too large to hash in a figure run) and builds the linear curvature perturbation R^NR on
the whole lattice as the track's analysis does (usr/scripts/card_lib.py, Extractor.curvature with
full = True): c[chi]/(2<chi>) + (H/Pi) c[phi] + (1/4) k_i k_j/k^2 c[gt_ij], the box mean removed.
Draws the slice through the cell of largest R^NR, rolled (periodic box) so that cell sits at the
centre, at three magnifications: the whole box, a quarter of its side, a sixteenth (16 cells);
axes in cells.
Writes OUT/fig_g2_mosaic.{pdf,png,json}.

    fig_g2_mosaic.py OUT
"""
import json
import os
import sys

import numpy as np
from scipy import fft as sfft

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, *[".."] * 4, "usr", "scripts"))
import figstyle as fs  # noqa: E402
import card_lib as cl  # noqa: E402

RUN = "/data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261121-211214-0377aab"
DUMP = "usr.sf.00020.dump"
NAMES = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gyy", "gzz", "gxy", "gxz", "gyz"]
WORKERS = 2


def size_listed(run_dir, rel):
    """The dump is listed in the run's sha256sums.txt (written when the run finished)."""
    for ln in open(os.path.join(run_dir, "sha256sums.txt")):
        h, f = ln.split(None, 1)
        if f.strip().lstrip("*").lstrip("./") == rel:
            return h
    sys.exit(f"{rel} not listed in {run_dir}/sha256sums.txt")


def curvature_field(f):
    N = f["chi"].shape[0]
    chi_m = f["chi"].mean()
    hb = -f["K"].mean() / (3.0 * f["alpha"].mean())
    pib = f["Pi"].mean()
    kz = sfft.fftfreq(N, 1.0 / N)[:, None, None]
    ky = sfft.fftfreq(N, 1.0 / N)[None, :, None]
    kx = np.arange(N // 2 + 1, dtype=float)[None, None, :]
    k2 = kx * kx + ky * ky + kz * kz
    k2[0, 0, 0] = 1.0
    kv = (kx, ky, kz)
    F = sfft.rfftn(f["chi"], workers=WORKERS) / (2.0 * chi_m) + (hb / pib) * sfft.rfftn(f["phi"], workers=WORKERS)
    for name, i, j, w in cl.GPAIRS:
        F += 0.25 * w * (kv[i] * kv[j] / k2) * sfft.rfftn(f[name], workers=WORKERS)
    F[0, 0, 0] = 0.0
    return sfft.irfftn(F, s=(N,) * 3, workers=WORKERS), dict(chi=float(chi_m), H=float(hb), Pi=float(pib))


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    sha = size_listed(RUN, DUMP)
    h, f = cl.read_fields(os.path.join(RUN, DUMP), NAMES)
    R, bg = curvature_field(f)
    del f
    N = R.shape[0]
    iz, iy, ix = np.unravel_index(np.argmax(R), R.shape)
    sl = np.roll(np.roll(R[iz], N // 2 - iy, axis=0), N // 2 - ix, axis=1)   # [y, x], peak at centre
    vmax = float(np.abs(sl).max())
    fs.use_style()
    import matplotlib.pyplot as plt
    halves = [N / 2, N / 8, N / 32]          # in cells: the box, 64 cells, 16 cells
    fig, axes, cax = fs.slice_mosaic(1, 3, panel=2.2, gap=0.06, left=0.62, bottom=0.42, fig_w=8.0,
                                     cbar="right", cbar_gap=0.0)
    ext = [-N / 2, N / 2, -N / 2, N / 2]
    for k, ax in enumerate(axes[0]):
        im = ax.imshow(sl, origin="lower", extent=ext, cmap=fs.CMAP["diverging"], vmin=-vmax, vmax=vmax,
                       interpolation="nearest")
        if k + 1 < len(halves):
            fs.zoom_marker(ax, halves[k + 1], halves[k], connect="right")
        else:
            ax.set_xlim(-halves[k], halves[k])
            ax.set_ylim(-halves[k], halves[k])
        fs.slice_ticks(ax, halves[k], show_y=(k == 0))
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.0f}"))
        if k == 0:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.0f}"))
        ax.set_xlabel(r"$x/\Delta x$")
    axes[0, 0].set_ylabel(r"$y/\Delta x$")
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"$\mathcal{R}^{\mathrm{NR}}$ at $N_f$")
    fs.save(fig, os.path.join(out, "fig_g2_mosaic"))
    summary = dict(dump=DUMP, dump_sha256_listed=sha, time=h["time"], cycle=h["cycle"], N=N, bg=bg,
                   peak_cell=[int(iz), int(iy), int(ix)], slice_max_abs=vmax, rms_R=float(R.std()),
                   max_R=float(R.max()), min_R=float(R.min()))
    json.dump(summary, open(os.path.join(out, "fig_g2_mosaic.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
