#!/usr/bin/env python3
"""Slices z = 0 of the field dumps <base>.field.NNNNN.bin of a run (particles
field_time1.., field_constraints = true; format NRFIELD2, reader as in
tracks/core/analysis/id/idlib.py): energy density E, lapse alpha, Hamiltonian residual H
and Theta, for the gauge-pathology figures of the package runs_ball.

    fields.py --seg <run dir> [--seg ...] --label <name> --out <dir> [--figdir <dir>] [--half 20]
"""
import argparse
import glob
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C   # noqa: E402,F401


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        n = np.frombuffer(f.read(24), dtype="<i8")
        nc = int(n[0] * n[1] * n[2])
        shape = (int(n[2]), int(n[1]), int(n[0]))
        out = dict(time=time, n=tuple(int(v) for v in n))
        out["E"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shape)
        out["chi"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shape)
        if magic == b"NRFIELD2":
            for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[name] = np.frombuffer(f.read(8 * nc), dtype="<f8").reshape(shape)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg", action="append", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figdir", default=None)
    ap.add_argument("--half", type=float, default=20.0, help="half-width of the plotted region")
    ap.add_argument("--L", type=float, default=64.0, help="half-width of the mesh")
    a = ap.parse_args()
    files = []
    for d in a.seg:
        files += sorted(glob.glob(os.path.join(d, "ball.field.*.bin")))
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm, TwoSlopeNorm
    nf = len(files)
    if nf == 0:
        print("no field dumps")
        return
    fig = plt.figure(figsize=(8.0, 1.9 * nf + 0.5))
    fig.subplots_adjust(left=0.07, right=0.93, bottom=0.05, top=0.96, wspace=0.42, hspace=0.30)
    rows = []
    for k, f in enumerate(files):
        F = read_field(f)
        n = F["n"][0]
        dx = 2 * a.L / n
        kz = n // 2                      # first cell above z = 0 (cell face at the origin)
        x = -a.L + (np.arange(n) + 0.5) * dx
        sel = np.abs(x) <= a.half
        ext = [x[sel][0] - dx / 2, x[sel][-1] + dx / 2] * 2
        stats = dict(t=F["time"], file=os.path.basename(f))
        panels = [("E", r"$E$", "magma", "log"), ("alpha", r"$\alpha$", "viridis", "lin"),
                  ("H", r"$H$", "RdBu_r", "sym"), ("Theta", r"$\Theta$", "RdBu_r", "sym")]
        for j, (key, lab, cmap, kind) in enumerate(panels):
            if key not in F:
                continue
            sl = np.asarray(F[key][kz][np.ix_(sel, sel)], dtype=float)
            ax = fig.add_subplot(nf, 4, 4 * k + j + 1)
            fin = np.isfinite(sl)
            stats[f"{key}_nonfinite_cells"] = int(np.sum(~np.isfinite(F[key])))
            if not np.any(fin):
                ax.text(0.5, 0.5, "non-finite", ha="center", va="center", transform=ax.transAxes)
                ax.set_title(f"{lab}, t = {F['time']:.2f}", fontsize=8)
                continue
            sl = np.where(fin, sl, np.nan)
            if kind == "log":
                vmax = max(float(np.nanmax(sl)), 1e-30)
                im = ax.imshow(np.maximum(sl, vmax * 1e-4), origin="lower", extent=ext, cmap=cmap,
                               norm=LogNorm(vmax * 1e-4, vmax), interpolation="none", rasterized=True)
            elif kind == "sym":
                v = np.nanmax(np.abs(sl)) or 1.0
                im = ax.imshow(sl, origin="lower", extent=ext, cmap=cmap, norm=TwoSlopeNorm(0, -v, v),
                               interpolation="none", rasterized=True)
            else:
                im = ax.imshow(sl, origin="lower", extent=ext, cmap=cmap, interpolation="none", rasterized=True)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
            ax.set_title(f"{lab}, t = {F['time']:.2f}", fontsize=8)
            ax.tick_params(labelsize=7)
            fa = np.asarray(F[key], dtype=float)
            fa = fa[np.isfinite(fa)]
            stats[f"{key}_min"] = float(fa.min()) if fa.size else None
            stats[f"{key}_max"] = float(fa.max()) if fa.size else None
            # where |key| peaks in the slice (x, y of the cell)
            if key in ("H", "Theta"):
                jj, ii = np.unravel_index(int(np.nanargmax(np.abs(sl))), sl.shape)
                stats[f"{key}_peak_xy"] = [float(x[sel][ii]), float(x[sel][jj])]
        rows.append(stats)
    os.makedirs(a.out, exist_ok=True)
    outs = fs.save(fig, os.path.join(a.out, f"{a.label}_fields"))
    C.write_json(os.path.join(a.out, f"{a.label}_fields.json"), rows)
    if a.figdir:
        import shutil
        os.makedirs(a.figdir, exist_ok=True)
        shutil.copy(outs[1], os.path.join(a.figdir, os.path.basename(outs[1])))
    for s in rows:
        print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in s.items()})


if __name__ == "__main__":
    main()
