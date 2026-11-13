#!/usr/bin/env python3
"""(d) Convergence of the deposited energy density with particle number.

The bound clusters with N = 1e2, 1e3 and 1e4 particles (independent draws from the same
distribution, mesh metric, midpoint, nfilter = 2 in every run) are compared on the
common mesh: d_N = ||E_N - E_1e4||_2 / ||E_1e4||_2 with the proper-volume weight
sqrt(gamma) dV over all leaf cells.  Because the N = 1e4 field carries its own sampling
noise, the raw exponent between N = 1e2 and 1e3 is slightly shallower than the noise
scaling.  With independent draws the cross terms vanish, d_ij^2 = s_i^2 + s_j^2 for the
three pairwise differences, which gives the noise level s_N of each run (relative to
||E_1e4||) and the exponents ds/dN between 1e2, 1e3 and 1e4 without a model.

Figure: figs/density_convergence.{pdf,png}
Numbers: results/density_convergence.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import ct_common as C
from nrpic import figstyle as fs

T_STAR = 500.0          # comparison time shown in the slices
NS = (100, 1000, 10000)
COL = {100: fs.PAL["orange"], 1000: fs.PAL["yellow"], 10000: fs.PAL["red"]}


def field(name, t):
    for f in C.bin_files(name, "E3d"):
        fd = C.read_bin(f)
        if abs(fd["time"] - t) < 1e-6:
            return fd
    return None


def l2(a, b, w):
    return np.sqrt(np.sum((a - b) ** 2 * w) / np.sum(b ** 2 * w))


def main():
    fs.use_style()
    res = {}
    fig = plt.figure(figsize=(8.0, 6.2))
    for j, a in enumerate((0.0, 0.9)):
        names = {n: f"mesh_a{a}_n{n}_mid" for n in NS}
        if not all(C.exists(v) for v in names.values()):
            continue
        times = sorted({C.read_bin(f)["time"] for f in C.bin_files(names[10000], "E3d")})
        rec = dict(times=[], d={str(n): [] for n in NS[:2]}, slope_raw=[], slope_corr=[])
        for t in times:
            fds = {n: field(names[n], t) for n in NS}
            if any(v is None for v in fds.values()):
                continue
            x, y, z, vol, Eref = C.bin_cells(fds[10000], "tmunu_E")
            w = vol * C.sqrt_gamma(x, y, z, a)
            d = {}
            Es = {n: C.bin_cells(fds[n], "tmunu_E")[4] for n in NS[:2]}
            for n in NS[:2]:
                d[n] = l2(Es[n], Eref, w)
            nrm = np.sqrt(np.sum(Eref ** 2 * w))
            d12 = np.sqrt(np.sum((Es[100] - Es[1000]) ** 2 * w)) / nrm
            rec["times"].append(t)
            for n in NS[:2]:
                rec["d"][str(n)].append(d[n])
            rec.setdefault("d_100_1000", []).append(d12)
            p_raw = np.log(d[1000] / d[100]) / np.log(10.0)
            # noise of each run from the three pairwise differences
            s2 = {100: 0.5 * (d[100] ** 2 + d12 ** 2 - d[1000] ** 2),
                  1000: 0.5 * (d[1000] ** 2 + d12 ** 2 - d[100] ** 2),
                  10000: 0.5 * (d[100] ** 2 + d[1000] ** 2 - d12 ** 2)}
            sN = {n: np.sqrt(max(v, 0.0)) for n, v in s2.items()}
            for n in NS:
                rec.setdefault("s", {}).setdefault(str(n), []).append(sN[n])
            p_corr = np.log(sN[1000] / sN[100]) / np.log(10.0)
            p_corr2 = (np.log(sN[10000] / sN[1000]) / np.log(10.0)
                       if sN[10000] > 0 else float("nan"))
            rec["slope_raw"].append(p_raw)
            rec["slope_corr"].append(p_corr)
            rec.setdefault("slope_corr_1e3_1e4", []).append(p_corr2)
        res[f"a{a}"] = rec
        if not rec["times"]:
            continue
        # top: d_N vs N at T_STAR, and slope vs time
        ax = fs.inch_axes(fig, 0.75 + j * 3.75, 3.95, 3.0, 1.95)
        tt = np.array(rec["times"])
        for n in NS[:2]:
            ax.semilogy(tt, rec["d"][str(n)], color=COL[n], marker="o", ms=3,
                        label=f"$N = 10^{int(np.log10(n))}$")
        # noise levels of the individual runs from the pairwise differences
        for n in NS:
            ax.semilogy(tt, rec["s"][str(n)], color=COL[n], ls="--", lw=1.0)
        # N^(-1/2) from the N = 1e2 noise level
        ax.semilogy(tt, np.array(rec["s"]["100"]) * np.sqrt(100 / 1e4), **dict(fs.GUIDE, lw=1.0))
        ax.set_xlabel("$t/M$", labelpad=-1)
        ax.set_title(f"$a = {a}\\,M$")
        if j == 0:
            ax.set_ylabel(r"$\|E_N - E_{10^4}\|_2 / \|E_{10^4}\|_2$")
        ax.legend(loc="lower right", fontsize=8)
        k = int(np.argmin(np.abs(tt - T_STAR)))
        txt = (f"$t = {tt[k]:.0f}\\,M$: exponent {rec['slope_raw'][k]:.3f} (raw), "
               f"{rec['slope_corr'][k]:.3f} (noise levels)")
        ax.text(0.03, 0.04, txt, transform=ax.transAxes, fontsize=8)
        rec["at_T_STAR"] = dict(t=tt[k], d100=rec["d"]["100"][k], d1000=rec["d"]["1000"][k],
                                d_100_1000=rec["d_100_1000"][k],
                                s={n: rec["s"][str(n)][k] for n in NS},
                                slope_raw=rec["slope_raw"][k],
                                slope_corr=rec["slope_corr"][k],
                                slope_corr_1e3_1e4=rec["slope_corr_1e3_1e4"][k])
        # bottom: slices at T_STAR for N = 1e2, 1e3, 1e4
        for i, n in enumerate(NS):
            files = C.bin_files(names[n], "Eslice")
            fd = None
            for f in files:
                g = C.read_bin(f)
                if abs(g["time"] - T_STAR) < 1e-6:
                    fd = g
                    break
            if fd is None:
                continue
            p = 1.22
            axi = fs.inch_axes(fig, 0.75 + j * 3.75 + i * (p + 0.03), 0.45 + 1.7 - p, p, p)
            nmb = (fd["nx1_mb"], fd["nx2_mb"])
            for b in sorted(range(fd["n_mbs"]),
                            key=lambda b: -(fd["mb_geometry"][b][1] - fd["mb_geometry"][b][0])):
                g = fd["mb_geometry"][b]
                q = np.asarray(fd["mb_data"]["tmunu_E"][b], dtype=float)[0]
                if g[1] < -25 or g[0] > 25 or g[3] < -25 or g[2] > 25:
                    continue
                im = axi.imshow(np.maximum(q, 5e-12), origin="lower",
                                extent=(g[0], g[1], g[2], g[3]), cmap=fs.CMAP["dens"],
                                norm=LogNorm(1e-11, 1e-7), interpolation="nearest",
                                rasterized=True)
            axi.set_xlim(-25, 25); axi.set_ylim(-25, 25); axi.set_aspect("equal")
            fs.slice_ticks(axi, 25, show_x=True, show_y=(i == 0 and j == 0))
            axi.set_xlabel("$x/M$", labelpad=-2)
            if i == 0 and j == 0:
                axi.set_ylabel("$y/M$")
            axi.text(0.05, 0.95, f"$N = 10^{int(np.log10(n))}$", color="white",
                     transform=axi.transAxes, va="top", fontsize=8)
        if j == 1:
            cax = fs.inch_axes(fig, 0.75 + 3.75 + 3 * (1.22 + 0.03) + 0.03, 0.45 + 1.7 - 1.22,
                               0.08, 1.22)
            cb = fig.colorbar(im, cax=cax)
            cb.set_label(r"$E\ [M^{-2}]$", labelpad=1)
    fig.text(0.75, 2.27, f"deposited $E$ next to $z = 0$ at $t = {T_STAR:.0f}\\,M$ "
             "(mesh metric, midpoint, two filter passes)", fontsize=9,
             transform=fig.dpi_scale_trans)
    fs.save(fig, os.path.join(C.FIGS, "density_convergence"))
    plt.close(fig)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    with open(os.path.join(C.HERE, "results", "density_convergence.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(k)
        for i, t in enumerate(v["times"]):
            print(f"  t={t:7.1f} d100={v['d']['100'][i]:.4f} d1000={v['d']['1000'][i]:.4f} "
                  f"d(100,1000)={v['d_100_1000'][i]:.4f} s=" +
                  " ".join(f"{v['s'][str(n)][i]:.4f}" for n in NS) +
                  f" slope raw={v['slope_raw'][i]:.3f} noise={v['slope_corr'][i]:.3f} "
                  f"noise(1e3-1e4)={v['slope_corr_1e3_1e4'][i]:.3f}")


if __name__ == "__main__":
    main()
