#!/usr/bin/env python3
"""(b) Phase mixing of the bound N = 1e4 cluster: particle positions (x-y and
cylindrical R-z) and the deposited energy density E in the plane next to z = 0 at the
same times, mesh metric, midpoint pusher.  A second figure gives the azimuthal order
parameter |<exp(i phi)>| and the vertical spread versus time for all N = 1e4 runs.

Figures: figs/phase_mixing_a0.0.{pdf,png}, figs/phase_mixing_a0.9.{pdf,png},
         figs/phase_mixing_order.{pdf,png}
Numbers: results/phase_mixing.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import ct_common as C
from nrpic import figstyle as fs

TIMES = (0.0, 50.0, 100.0, 200.0, 500.0, 1000.0)
HALF = 30.0
VMIN, VMAX = 1e-11, 1e-6


def slice_at(name, t):
    """Eslice output closest to time t: list of (extent, 2D array) per MeshBlock."""
    files = C.bin_files(name, "Eslice")
    best, fd_best = None, None
    for f in files:
        fd = C.read_bin(f)
        if best is None or abs(fd["time"] - t) < abs(best - t):
            best, fd_best = fd["time"], fd
        if fd["time"] > t + 30:
            break
    patches = []
    nmb = (fd_best["nx1_mb"], fd_best["nx2_mb"])
    for b in range(fd_best["n_mbs"]):
        g = fd_best["mb_geometry"][b]
        q = np.asarray(fd_best["mb_data"]["tmunu_E"][b], dtype=float)[0]
        patches.append(((g[0], g[1], g[2], g[3]), q, (g[1] - g[0]) / nmb[0]))
    patches.sort(key=lambda p: -p[2])        # coarse first
    return best, patches


def main():
    fs.use_style()
    res = {}
    for a in (0.0, 0.9):
        name = f"mesh_a{a}_n10000_mid"
        if not C.exists(name):
            continue
        files = C.snapshots(name)
        ts = C.dc.snapshot_times(files)
        ncol = len(TIMES)
        panel = 1.06
        fig = plt.figure(figsize=(8.0, 0.42 + 2 * panel + 0.04 + 0.62 * panel + 0.46 + 0.30))
        W, Hf = fig.get_size_inches()
        left, gap = 0.55, 0.04
        y_rz = 0.42
        h_rz = 0.62 * panel
        y_img = y_rz + h_rz + 0.46
        y_xy = y_img + panel + gap
        ax_xy = [fs.inch_axes(fig, left + j * (panel + gap), y_xy, panel, panel)
                 for j in range(ncol)]
        ax_im = [fs.inch_axes(fig, left + j * (panel + gap), y_img, panel, panel)
                 for j in range(ncol)]
        ax_rz = [fs.inch_axes(fig, left + j * (panel + gap), y_rz, panel, h_rz)
                 for j in range(ncol)]
        cax = fs.inch_axes(fig, left + ncol * (panel + gap) + 0.02, y_img, 0.08, panel)
        info = []
        for j, t in enumerate(TIMES):
            k = int(np.argmin(np.abs(ts - t)))
            tk, x, u, m, tag, sp = C.read_snap(files[k])
            # x-y
            ax = ax_xy[j]
            ax.scatter(x[:, 0], x[:, 1], s=0.15, color=fs.PAL["red"], lw=0, rasterized=True)
            ax.add_patch(plt.Circle((0, 0), 1 + np.sqrt(1 - a * a), color="k"))
            ax.set_xlim(-HALF, HALF); ax.set_ylim(-HALF, HALF); ax.set_aspect("equal")
            fs.slice_ticks(ax, HALF, show_x=False, show_y=(j == 0))
            ax.text(0.04, 0.96, f"$t = {tk:.0f}\\,M$", transform=ax.transAxes, va="top",
                    fontsize=8)
            # density slice
            ts_, patches = slice_at(name, t)
            ax = ax_im[j]
            for ext, q, d in patches:
                if ext[1] < -HALF or ext[0] > HALF or ext[3] < -HALF or ext[2] > HALF:
                    continue
                im = ax.imshow(np.maximum(q, VMIN * 0.5), origin="lower", extent=ext,
                               cmap=fs.CMAP["dens"], norm=LogNorm(VMIN, VMAX),
                               interpolation="nearest", rasterized=True)
            ax.set_xlim(-HALF, HALF); ax.set_ylim(-HALF, HALF); ax.set_aspect("equal")
            fs.slice_ticks(ax, HALF, show_x=True, show_y=(j == 0))
            ax.set_xlabel("$x/M$", labelpad=1)
            ax.text(0.04, 0.96, f"$t = {ts_:.0f}\\,M$", transform=ax.transAxes, va="top",
                    fontsize=8, color="white")
            # R-z
            ax = ax_rz[j]
            R = np.hypot(x[:, 0], x[:, 1])
            ax.scatter(R, x[:, 2], s=0.15, color=fs.PAL["red"], lw=0, rasterized=True)
            ax.set_xlim(0, HALF); ax.set_ylim(-6, 6)
            ax.set_xticks([10, 20]); ax.set_yticks([-4, 0, 4])
            if j > 0:
                ax.yaxis.set_major_formatter(plt.NullFormatter())
            ax.set_xlabel("$R/M$", labelpad=1)
            phi = np.arctan2(x[:, 1], x[:, 0])
            info.append(dict(t=float(tk), order=float(np.abs(np.mean(np.exp(1j * phi)))),
                             z_rms=float(np.sqrt(np.mean(x[:, 2] ** 2))),
                             R_pct=np.percentile(R, [1, 50, 99]).tolist(), n=int(len(R))))
        ax_xy[0].set_ylabel("$y/M$")
        ax_im[0].set_ylabel("$y/M$")
        ax_rz[0].set_ylabel("$z/M$")
        cb = fig.colorbar(im, cax=cax)
        cb.set_label(r"$E\ [M^{-2}]$", labelpad=1)
        fig.text(left, Hf - 0.20, f"$a = {a}\\,M$, $N = 10^4$, mesh metric, midpoint pusher: "
                 "particles (top, bottom) and deposited $E$ next to $z = 0$ (middle)",
                 fontsize=9, transform=fig.dpi_scale_trans)
        fs.save(fig, os.path.join(C.FIGS, f"phase_mixing_a{a}"))
        plt.close(fig)
        res[name] = info

    # ---- order parameter, vertical spread and per-particle position differences ------
    series = [("ana_a{a}_mid", 2, "analytic, midpoint", fs.PAL["blue"]),
              ("mesh_a{a}_n10000_mid", None, "mesh, midpoint", fs.PAL["red"]),
              ("ana_a{a}_boris", 2, "analytic, Boris", fs.PAL["yellow"]),
              ("mesh_a{a}_n10000_boris", None, "mesh, Boris", fs.PAL["green"])]
    fig, axes = plt.subplots(3, 2, figsize=(8.0, 6.6), sharex="col")
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.92, hspace=0.07,
                        wspace=0.24)
    for j, a in enumerate((0.0, 0.9)):
        ref = None
        for pat, sp, lab, col in series:
            name = pat.format(a=a)
            if not C.exists(name):
                continue
            h = C.invariant_history(name)
            sel = slice(None) if sp is None else (h["species"] == sp)
            x = h["x"][:, sel].astype(float)
            tags = h["tag"][sel] - (1100 if sp == 2 else 0)
            phi = np.arctan2(x[..., 1], x[..., 0])
            ok = np.isfinite(phi)
            order = np.abs(np.nansum(np.where(ok, np.exp(1j * phi), 0), 1) / ok.sum(1))
            zrms = np.sqrt(np.nanmean(x[..., 2] ** 2, 1))
            t = h["t"] / C.T_ORB[a]
            axes[0, j].semilogy(t, order, color=col, label=lab)
            axes[1, j].plot(t, zrms, color=col)
            rec = dict(t=h["t"].tolist(), order=order.tolist(), z_rms=zrms.tolist())
            if ref is None:
                ref = (tags, x)
            else:
                o = np.searchsorted(ref[0], tags)
                d = np.sqrt(np.sum((x - ref[1][:, o]) ** 2, axis=2))
                with np.errstate(all="ignore"):
                    med = np.nanmedian(d, 1)
                    p99 = np.nanpercentile(d, 99, 1)
                axes[2, j].semilogy(t[1:], med[1:], color=col, ls="-")
                axes[2, j].semilogy(t[1:], p99[1:], color=col, ls="--")
                rec.update(dx_median=med.tolist(), dx_p99=p99.tolist())
            res.setdefault("order", {})[name] = rec
        axes[0, j].set_title(f"$a = {a}\\,M$")
        axes[2, j].set_xlabel("$t / T_\\mathrm{orb}$")
        axes[0, j].set_xlim(0, C.TLIM / C.T_ORB[a])
        axes[0, j].axhline(np.sqrt(np.pi / 4e4), **fs.GUIDE)
    axes[0, 0].set_ylabel(r"$|\langle e^{i\phi}\rangle|$")
    axes[1, 0].set_ylabel(r"$z_\mathrm{rms}/M$")
    axes[2, 0].set_ylabel("$|x - x_\\mathrm{analytic,\\,midpoint}|/M$")
    axes[0, 0].plot([], [], **fs.GUIDE, label=r"uniform phases, $N = 10^4$")
    axes[2, 1].legend([plt.Line2D([], [], color="k", ls="-"),
                       plt.Line2D([], [], color="k", ls="--")],
                      ["median", "99th percentile"], loc="lower right", fontsize=8)
    h0, l0 = axes[0, 0].get_legend_handles_labels()
    fig.legend(h0, l0, loc="upper center", ncol=5, fontsize=8, frameon=False,
               bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "phase_mixing_order"))
    plt.close(fig)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    with open(os.path.join(C.HERE, "results", "phase_mixing.json"), "w") as f:
        json.dump(res, f)
    for k, v in res.items():
        if k != "order":
            for e in v:
                print(k, e)


if __name__ == "__main__":
    main()
