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


def compute():
    res = {}
    for a in (0.0, 0.9):
        names = {n: f"mesh_a{a}_n{n}_mid" for n in NS}
        if not all(C.exists(v) for v in names.values()):
            continue
        times = sorted({C.read_bin(f)["time"] for f in C.bin_files(names[10000], "E3d")})
        rec = dict(times=[], d={str(n): [] for n in NS[:2]}, d_100_1000=[],
                   s={str(n): [] for n in NS}, slope_raw=[], slope_corr=[],
                   slope_corr_1e3_1e4=[])
        for t in times:
            fds = {n: field(names[n], t) for n in NS}
            if any(v is None for v in fds.values()):
                continue
            x, y, z, vol, Eref = C.bin_cells(fds[10000], "tmunu_E")
            w = vol * C.sqrt_gamma(x, y, z, a)
            Es = {n: C.bin_cells(fds[n], "tmunu_E")[4] for n in NS[:2]}
            d = {n: l2(Es[n], Eref, w) for n in NS[:2]}
            nrm = np.sqrt(np.sum(Eref ** 2 * w))
            d12 = np.sqrt(np.sum((Es[100] - Es[1000]) ** 2 * w)) / nrm
            s2 = {100: 0.5 * (d[100] ** 2 + d12 ** 2 - d[1000] ** 2),
                  1000: 0.5 * (d[1000] ** 2 + d12 ** 2 - d[100] ** 2),
                  10000: 0.5 * (d[100] ** 2 + d[1000] ** 2 - d12 ** 2)}
            sN = {n: (np.sqrt(v) if v > 0 else float("nan")) for n, v in s2.items()}
            rec["times"].append(float(t))
            for n in NS[:2]:
                rec["d"][str(n)].append(float(d[n]))
            rec["d_100_1000"].append(float(d12))
            for n in NS:
                rec["s"][str(n)].append(float(sN[n]))
            rec["slope_raw"].append(float(np.log10(d[1000] / d[100])))
            rec["slope_corr"].append(float(np.log10(sN[1000] / sN[100])))
            rec["slope_corr_1e3_1e4"].append(float(np.log10(sN[10000] / sN[1000])))
        tt = np.array(rec["times"])
        late = tt >= 200
        k = int(np.argmin(np.abs(tt - T_STAR)))
        rec["at_T_STAR"] = dict(t=float(tt[k]), d100=rec["d"]["100"][k],
                                d1000=rec["d"]["1000"][k], d_100_1000=rec["d_100_1000"][k],
                                s={str(n): rec["s"][str(n)][k] for n in NS},
                                slope_raw=rec["slope_raw"][k], slope_corr=rec["slope_corr"][k],
                                slope_corr_1e3_1e4=rec["slope_corr_1e3_1e4"][k])
        for key in ("slope_raw", "slope_corr", "slope_corr_1e3_1e4"):
            v = np.array(rec[key])[late]
            v = v[np.isfinite(v)]
            rec[key + "_late_mean_std"] = [float(v.mean()), float(v.std()), int(len(v))]
        res[f"a{a}"] = rec
    return res


def slice_patches(name, t):
    for f in C.bin_files(name, "Eslice"):
        g = C.read_bin(f)
        if abs(g["time"] - t) < 1e-6:
            out = []
            for b in range(g["n_mbs"]):
                gm = g["mb_geometry"][b]
                q = np.asarray(g["mb_data"]["tmunu_E"][b], dtype=float)[0]
                out.append(((gm[0], gm[1], gm[2], gm[3]), q, gm[1] - gm[0]))
            return sorted(out, key=lambda p: -p[2])
    return None


def main():
    import sys
    fs.use_style()
    jpath = os.path.join(C.HERE, "results", "density_convergence.json")
    if "--plot" in sys.argv and os.path.exists(jpath):
        res = json.load(open(jpath))
    else:
        res = compute()
        os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
        with open(jpath, "w") as f:
            json.dump(res, f, indent=1)
    fig = plt.figure(figsize=(8.0, 5.0))
    ax_t = [fs.inch_axes(fig, 0.62, 2.55, 2.35, 2.05), fs.inch_axes(fig, 3.17, 2.55, 2.35, 2.05)]
    ax_n = fs.inch_axes(fig, 6.05, 2.55, 1.85, 2.05)
    for j, a in enumerate((0.0, 0.9)):
        rec = res.get(f"a{a}")
        if rec is None:
            continue
        tt = np.array(rec["times"])
        ax = ax_t[j]
        for n in NS[:2]:
            ax.semilogy(tt, rec["d"][str(n)], color=COL[n], marker="o", ms=2.5,
                        label=f"$\\|E_{{10^{int(np.log10(n))}}} - E_{{10^4}}\\|$")
        for n in NS:
            ax.semilogy(tt, rec["s"][str(n)], color=COL[n], ls="--", lw=1.0)
        ax.set_xlabel("$t/M$", labelpad=1)
        ax.set_title(f"$a = {a}\\,M$")
        ax.set_ylim(0.05, 6)
        ax.axvline(T_STAR, **fs.MASK_LINE)
        if j == 0:
            ax.set_ylabel("relative $L_2$ difference, noise")
        else:
            ax.yaxis.set_major_formatter(plt.NullFormatter())
        # d and s versus N at T_STAR
        r = rec["at_T_STAR"]
        mk = "o" if a == 0.0 else "s"
        fill = "none" if a == 0.0 else fs.PAL["red"]
        ax_n.loglog([100, 1000], [r["d100"], r["d1000"]], color=fs.PAL["red"], marker=mk,
                    mfc=fill, ls="-", label=f"$d_N$, $a = {a}$")
        ax_n.loglog(NS, [r["s"][str(n)] for n in NS], color=fs.PAL["red"], marker=mk,
                    mfc=fill, ls="--", lw=1.0)
    for rec in res.values():
        r = rec["at_T_STAR"]
        nn = np.array([60, 2e4])
        ax_n.loglog(nn, r["s"]["100"] * np.sqrt(100 / nn), **dict(fs.GUIDE, lw=1.0))
        break
    ax_n.set_xlabel("$N$", labelpad=1)
    ax_n.set_title(f"$t = {T_STAR:.0f}\\,M$")
    ax_n.set_xlim(50, 2e4)
    ax_n.set_ylim(0.05, 6)
    ax_n.yaxis.set_major_formatter(plt.NullFormatter())
    L = plt.Line2D
    ax_t[0].legend(loc="lower right", fontsize=8)
    ax_t[1].legend([L([], [], color="k", ls="-", marker="o", ms=2.5),
                    L([], [], color="k", ls="--", lw=1.0)],
                   ["difference to $N = 10^4$", "noise of each run"],
                   loc="lower right", fontsize=8)
    ax_n.legend([L([], [], color=fs.PAL["red"], marker="o", mfc="none", ls=""),
                 L([], [], color=fs.PAL["red"], marker="s", ls=""),
                 L([], [], **fs.GUIDE)],
                ["$a = 0$", "$a = 0.9\\,M$", "$N^{-1/2}$"], loc="lower left", fontsize=8)
    # slices at T_STAR
    p, gap, x0 = 1.06, 0.03, 0.62
    k = 0
    im = None
    for j, a in enumerate((0.0, 0.9)):
        for n in NS:
            pt = slice_patches(f"mesh_a{a}_n{n}_mid", T_STAR)
            xl = x0 + k * (p + gap) + (0.12 if j == 1 else 0.0)
            axi = fs.inch_axes(fig, xl, 0.42, p, p)
            k += 1
            if pt is None:
                continue
            for ext, q, _ in pt:
                if ext[1] < -25 or ext[0] > 25 or ext[3] < -25 or ext[2] > 25:
                    continue
                im = axi.imshow(np.maximum(q, 5e-12), origin="lower", extent=ext,
                                cmap=fs.CMAP["dens"], norm=LogNorm(1e-11, 1e-7),
                                interpolation="nearest", rasterized=True)
            axi.set_xlim(-25, 25); axi.set_ylim(-25, 25); axi.set_aspect("equal")
            axi.set_xticks([-15, 0, 15]); axi.set_yticks([-15, 0, 15])
            if k > 1:
                axi.yaxis.set_major_formatter(plt.NullFormatter())
            else:
                axi.set_ylabel("$y/M$")
            axi.set_xlabel("$x/M$", labelpad=1)
            axi.text(0.05, 0.95, f"$N = 10^{int(np.log10(n))}$", color="white",
                     transform=axi.transAxes, va="top", fontsize=8)
            if n == 100:
                axi.text(0.05, 0.05, f"$a = {a}$", color="white",
                         transform=axi.transAxes, va="bottom", fontsize=8)
    if im is not None:
        cax = fs.inch_axes(fig, x0 + 6 * (p + gap) + 0.12 + 0.03, 0.42, 0.07, p)
        cb = fig.colorbar(im, cax=cax)
        cb.set_label(r"$E\ [M^{-2}]$", labelpad=1)
    fig.text(0.62, 1.66, f"deposited $E$ next to $z = 0$ at $t = {T_STAR:.0f}\\,M$ "
             "(mesh metric, midpoint pusher, two filter passes)", fontsize=9,
             transform=fig.dpi_scale_trans)
    fs.save(fig, os.path.join(C.FIGS, "density_convergence"))
    plt.close(fig)
    for key, v in res.items():
        print(key, "at", v["at_T_STAR"])
        print("   late-time (t >= 200 M) exponents mean/std/n:",
              v["slope_raw_late_mean_std"], v["slope_corr_late_mean_std"],
              v["slope_corr_1e3_1e4_late_mean_std"])


if __name__ == "__main__":
    main()
