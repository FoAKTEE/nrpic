#!/usr/bin/env python3
"""Where is the Z4c constraint variable Theta (and the Hamiltonian constraint H) of V-1 and
ES-1, and does it move inward from the outflow faces? (JOURNAL entry 1, prediction B3.)

    python3 theta_map.py --out DIR [--run NAME:RUNDIR:BASE ...]

Reads the z = 0.001 slices <BASE>.z4c.NNNNN.bin (every 10 M; Theta, alpha, chi, Khat) and
<BASE>.con.NNNNN.bin (every 25 M; H) with athenak/vis/python/bin_convert.py. For each
slice: values on the +x axis (the two cells next to y = 0, averaged) and on the diagonal
x = y > 0 (cells whose centres lie on it), finest cell at each position.

Writes DIR/theta_map.json and figures DIR/figs/theta_*.png|pdf:
  theta_spacetime_<run>   log10|Theta| against r and t on the axis and on the diagonal,
                          log10|H| on the axis; light-like lines r = 192 - v t (v = 1, 1.3)
  theta_profiles_<run>    |Theta|(r) on the axis at t = 0, 20, ..., 200 M
  theta_plane_<run>       log10|Theta| in the z = 0 plane at t = 50, 100, 150, 200 M
Measures per slice: median |Theta| in r = 3-10, 10-30, 30-60, 60-120, 120-185 M on the
axis and on the diagonal; radius of the maximum of |Theta| beyond 8 M; the smallest radius
beyond 8 M from which |Theta| stays above one tenth of its maximum out to that maximum
("inner edge" of the large-|Theta| region).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
from nrpic import figstyle  # noqa: E402
import bin_convert  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
DEFAULT_RUNS = [f"V-1:{S}/D-20261115-172730-c6d151b:v1",
                f"ES-1:{S}/D-20261115-172726-60ba4c2:es"]
BANDS = [(3, 10), (10, 30), (30, 60), (60, 120), (120, 185)]


def cells(fd, var_list):
    """All cells of the slice: x, y, dx and the variables (one row per cell)."""
    nmb = (fd["nx1_mb"], fd["nx2_mb"], fd["nx3_mb"])
    rows = []
    for b in range(fd["n_mbs"]):
        g = fd["mb_geometry"][b]
        ix = fd["mb_index"][b]
        dxs = [(g[2 * k + 1] - g[2 * k]) / nmb[k] for k in range(3)]
        q0 = np.asarray(fd["mb_data"][var_list[0]][b], dtype=float)
        n3, n2, n1 = q0.shape
        xc = g[0] + (ix[0] + np.arange(n1) + 0.5) * dxs[0]
        yc = g[2] + (ix[2] + np.arange(n2) + 0.5) * dxs[1]
        X, Y = np.meshgrid(xc, yc)
        cols = [X.ravel(), Y.ravel(), np.full(X.size, dxs[0])]
        for v in var_list:
            cols.append(np.asarray(fd["mb_data"][v][b], dtype=float)[0].ravel())
        rows.append(np.column_stack(cols))
    return np.vstack(rows)


def line(c, sel, coord):
    """Cells selected by sel, finest at each position along coord (1D), sorted."""
    a = c[sel]
    s = coord(a)
    order = np.lexsort((a[:, 2], s))
    a, s = a[order], s[order]
    keep = {}
    for i in range(len(a)):
        k = round(s[i], 6)
        if k not in keep or a[i, 2] < keep[k][0][2] - 1e-12:
            keep[k] = [a[i]]
        elif abs(a[i, 2] - keep[k][0][2]) < 1e-12:
            keep[k].append(a[i])
    ks = sorted(keep)
    v = np.array([np.mean(keep[k], axis=0) for k in ks])
    r = np.array(ks)
    # drop coarse cells whose centre is covered by finer ones
    ok = np.ones(len(r), bool)
    for i in range(len(r)):
        finer = v[:, 2] < v[i, 2] - 1e-12
        if finer.any() and np.any(np.abs(r[finer] - r[i]) < 0.5 * v[i, 2] * (1 if coord is _ax else np.sqrt(2))):
            ok[i] = False
    return r[ok], v[ok]


def _ax(a):
    return a[:, 0]


def _dg(a):
    return np.hypot(a[:, 0], a[:, 1])


def axis_and_diag(c):
    dy = c[:, 2]
    sel_ax = (c[:, 0] > 0) & (np.abs(np.abs(c[:, 1]) - 0.5 * dy) < 1e-9 * np.maximum(1, dy))
    sel_dg = (c[:, 0] > 0) & (np.abs(c[:, 0] - c[:, 1]) < 1e-9 * np.maximum(1, dy))
    return line(c, sel_ax, _ax), line(c, sel_dg, _dg)


def measures(r, th):
    a = np.abs(th)
    out = {}
    for lo, hi in BANDS:
        m = (r >= lo) & (r < hi)
        out[f"med_{lo}_{hi}"] = float(np.median(a[m])) if m.any() else None
    m = r > 8
    if m.any():
        rr, aa = r[m], a[m]
        imax = int(np.argmax(aa))
        out["r_max"] = float(rr[imax])
        out["max"] = float(aa[imax])
        thr = 0.1 * aa[imax]
        j = imax
        while j > 0 and aa[j - 1] >= thr:
            j -= 1
        out["r_inner_edge"] = float(rr[j])
    return out


def run_series(rundir, base):
    zs = sorted(glob.glob(os.path.join(rundir, "bin", f"{base}.z4c.[0-9]*.bin")))
    cs = sorted(glob.glob(os.path.join(rundir, "bin", f"{base}.con.[0-9]*.bin")))
    zser, cser, planes = [], [], {}
    for p in zs:
        fd = bin_convert.read_binary(p)
        c = cells(fd, ["z4c_Theta", "z4c_alpha", "z4c_chi", "z4c_Khat"])
        (ra, va), (rd, vd) = axis_and_diag(c)
        t = float(fd["time"])
        zser.append(dict(time=t, r_ax=ra, th_ax=va[:, 3], al_ax=va[:, 4], dx_ax=va[:, 2],
                         r_dg=rd, th_dg=vd[:, 3]))
        if any(abs(t - tq) < 1e-6 for tq in (50, 100, 150, 200)):
            planes[t] = c
    for p in cs:
        fd = bin_convert.read_binary(p)
        c = cells(fd, ["con_H", "con_Z"])
        (ra, va), (rd, vd) = axis_and_diag(c)
        cser.append(dict(time=float(fd["time"]), r_ax=ra, H_ax=va[:, 3], Z_ax=va[:, 4],
                         r_dg=rd, H_dg=vd[:, 3]))
    return zser, cser, planes


def spacetime(ax, ser, rkey, vkey, vmin, vmax, rmax=192):
    from matplotlib.colors import Normalize
    rg = np.linspace(0.5, rmax, 400)
    T = np.array([s["time"] for s in ser])
    Z = np.array([np.interp(rg, s[rkey], np.log10(np.abs(s[vkey]) + 1e-30)) for s in ser])
    dt = np.median(np.diff(T)) if len(T) > 1 else 10.0
    te = np.concatenate([T - dt / 2, [T[-1] + dt / 2]])
    re = np.concatenate([[0], 0.5 * (rg[1:] + rg[:-1]), [rmax]])
    im = ax.pcolormesh(re, te, Z, cmap=figstyle.CMAP["dens"], norm=Normalize(vmin, vmax),
                       shading="flat", rasterized=True)
    return im


def figures(name, zser, cser, planes, outdir, face):
    figstyle.use_style()
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    fd = os.path.join(outdir, "figs")
    os.makedirs(fd, exist_ok=True)
    allth = np.concatenate([np.abs(s["th_ax"]) for s in zser if s["time"] > 0])
    vmax = np.log10(np.percentile(allth[allth > 0], 99.5))
    vmin = vmax - 6
    fig, axs = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 3.6), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.9, top=0.9, bottom=0.14, wspace=0.06)
    im = spacetime(axs[0], zser, "r_ax", "th_ax", vmin, vmax, face)
    spacetime(axs[1], zser, "r_dg", "th_dg", vmin, vmax, face * np.sqrt(2))
    allH = np.concatenate([np.abs(s["H_ax"]) for s in cser if s["time"] > 0])
    hv = np.log10(np.percentile(allH[allH > 0], 99.5))
    im2 = spacetime(axs[2], cser, "r_ax", "H_ax", hv - 6, hv, face)
    tt = np.linspace(0, 200, 50)
    for ax, sc in ((axs[0], 1.0), (axs[1], np.sqrt(2)), (axs[2], 1.0)):
        for v, ls in ((1.0, "--"), (1.3, ":")):
            ax.plot(sc * (face - v * tt), tt, color="w", lw=1.0, ls=ls)
        ax.axhline(165, color="w", lw=0.8, alpha=0.6)
        ax.set_xlim(0, face * sc)
        ax.set_ylim(0, 200)
    axs[0].set_title(r"$\log_{10}|\Theta|$, $+x$ axis", fontsize=10)
    axs[1].set_title(r"$\log_{10}|\Theta|$, diagonal $x=y$", fontsize=10)
    axs[2].set_title(r"$\log_{10}|H|$, $+x$ axis", fontsize=10)
    axs[0].set_ylabel(r"$t\,[M]$")
    for ax in axs:
        ax.set_xlabel(r"$r\,[M]$")
    cax = fig.add_axes([0.91, 0.14, 0.012, 0.76])
    fig.colorbar(im, cax=cax)
    figstyle.save(fig, os.path.join(fd, f"theta_spacetime_{name}"))
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.6), sharey=True)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.92, bottom=0.14, wspace=0.06)
    sel = [s for s in zser if abs((s["time"] / 20) - round(s["time"] / 20)) < 1e-6]
    cols = figstyle.series_colors(len(sel))
    for s, c in zip(sel, cols):
        axs[0].semilogy(s["r_ax"], np.abs(s["th_ax"]) + 1e-30, color=c, lw=1.0,
                        label=f"{s['time']:g}")
        axs[1].semilogy(s["r_dg"], np.abs(s["th_dg"]) + 1e-30, color=c, lw=1.0)
    axs[0].set_title(r"$|\Theta|$ on the $+x$ axis", fontsize=10)
    axs[1].set_title(r"$|\Theta|$ on the diagonal", fontsize=10)
    axs[0].set_ylabel(r"$|\Theta|$")
    for ax in axs:
        ax.set_xlabel(r"$r\,[M]$")
        ax.set_ylim(10 ** (vmax - 8), 10 ** (vmax + 0.5))
    axs[0].legend(ncol=3, fontsize=7, title="t [M]", title_fontsize=7)
    figstyle.save(fig, os.path.join(fd, f"theta_profiles_{name}"))
    plt.close(fig)

    if planes:
        ts = sorted(planes)
        fig, axs = plt.subplots(1, len(ts), figsize=(figstyle.FULL_WIDTH, 2.4))
        fig.subplots_adjust(left=0.05, right=0.9, top=0.88, bottom=0.12, wspace=0.05)
        for ax, t in zip(np.atleast_1d(axs), ts):
            c = planes[t]
            order = np.argsort(-c[:, 2])        # coarse first, fine on top
            c = c[order]
            sc = ax.scatter(c[:, 0], c[:, 1], c=np.log10(np.abs(c[:, 3]) + 1e-30),
                            s=(c[:, 2] / 4.0) * 1.2, marker="s", lw=0,
                            cmap=figstyle.CMAP["dens"], norm=Normalize(vmin, vmax),
                            rasterized=True)
            ax.set_aspect("equal")
            ax.set_xlim(-face, face)
            ax.set_ylim(-face, face)
            ax.set_title(f"t = {t:g} M", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])
        cax = fig.add_axes([0.91, 0.12, 0.012, 0.76])
        fig.colorbar(sc, cax=cax, label=r"$\log_{10}|\Theta|$")
        figstyle.save(fig, os.path.join(fd, f"theta_plane_{name}"))
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run", action="append", default=None)
    ap.add_argument("--face", type=float, default=192.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    for spec in a.run or DEFAULT_RUNS:
        name, rundir, base = spec.split(":")
        zser, cser, planes = run_series(rundir, base)
        rec = {"theta": [], "H": []}
        for s in zser:
            rec["theta"].append(dict(time=s["time"], axis=measures(s["r_ax"], s["th_ax"]),
                                     diag=measures(s["r_dg"], s["th_dg"])))
        for s in cser:
            rec["H"].append(dict(time=s["time"], axis=measures(s["r_ax"], s["H_ax"]),
                                 diag=measures(s["r_dg"], s["H_dg"])))
        res[name] = rec
        figures(name, zser, cser, planes, a.out, a.face)
        print(f"== {name}")
        for x in rec["theta"]:
            m = x["axis"]
            d = x["diag"]
            print(f"  t={x['time']:6.1f} Theta axis med 3-10 {m['med_3_10']:.2e} 10-30 "
                  f"{m['med_10_30']:.2e} 30-60 {m['med_30_60']:.2e} 60-120 {m['med_60_120']:.2e} "
                  f"120-185 {m['med_120_185']:.2e} | rmax {m.get('r_max', 0):6.1f} "
                  f"edge {m.get('r_inner_edge', 0):6.1f} | diag rmax {d.get('r_max', 0):6.1f} "
                  f"edge {d.get('r_inner_edge', 0):6.1f}")
        for x in rec["H"]:
            m = x["axis"]
            print(f"  t={x['time']:6.1f} H axis med 3-10 {m['med_3_10']:.2e} 10-30 "
                  f"{m['med_10_30']:.2e} 30-60 {m['med_30_60']:.2e} 60-120 {m['med_60_120']:.2e} "
                  f"120-185 {m['med_120_185']:.2e}")
    with open(os.path.join(a.out, "theta_map.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
