#!/usr/bin/env python3
"""Test T3 of tracks/core/JOURNAL-oblate.md: the oblate collapse at two (or three)
resolutions, read from the run directories of the card job.

    collapse_analysis.py --run m4=DIR --run m8=DIR [--run m16=DIR] [--out DIR]
                         [--prolate m8=DIR --prolate m16=DIR]

Per run, from the files of the code:
  <base>.part.NNNNN.bin   rms height z_rms and rms cylindrical radius R_rms of the
                          particles, the fraction that is on the other side of the
                          equatorial plane from where it started (by tag), the number
                          left; time t_p of the smallest z_rms (the pancake)
  <base>.horizon_summary_0.txt   first apparent horizon, its mass history
  <base>.nrpic.hst        smallest lapse, removed and escaped particles and mass,
                          pusher convergence, number of MeshBlocks
  <base>.curv.hst         largest Kretschmann scalar and energy density
  <base>.z4c.user.hst     norm of the Hamiltonian constraint
  athena.log              wall time, peak card memory
The Newtonian homogeneous spheroid (newton_spheroid.py) is drawn for comparison.
Writes collapse.json and the figures figs/oblate_collapse.{png,pdf} (time histories),
figs/oblate_mosaic.{png,pdf} (energy density in the plane y = 0 at four times, every
resolution) and figs/oblate_particles.{png,pdf} (particles of the finest run in the
x-z and x-y projections at the same times).
"""
import argparse
import glob
import json
import math
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "analysis", "diag"))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from nrpic import figstyle as fs  # noqa: E402
from common import (read_athena_hst, read_curv_hst, read_nrpic_hst, read_snapshot,  # noqa: E402
                    keep_last, H as HC)
import newton_spheroid as newt  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

BASE = "obl"
LABEL = {"m4": "$M/4$", "m8": "$M/8$", "m16": "$M/16$"}
COLOR = {"m4": fs.PAL["yellow"], "m8": fs.PAL["red"], "m16": fs.PAL["green"]}
M_ADM = 1.0


def read_ah(path):
    rows = []
    if not os.path.exists(path):
        return np.zeros((0, 4))
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        x = line.split()
        if len(x) >= 12:
            rows.append([float(x[1]), float(x[2]), float(x[7]), float(x[10])])
    return keep_last(np.array(rows)) if rows else np.zeros((0, 4))


def read_curv_slice(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
    return t, d


def log_facts(d):
    out = dict(wall_s=None, gpu_mem_peak_MiB=None, terminated=None, logs=[])
    wall = 0.0
    for p in sorted(glob.glob(os.path.join(d, "athena.2*.log"))):
        txt = open(p, errors="replace").read()
        m = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        if m:
            wall += float(m[-1])
        m = re.findall(r"gpu_mem_peak_MiB=(\d+)", txt)
        if m:
            out["gpu_mem_peak_MiB"] = max(out["gpu_mem_peak_MiB"] or 0, int(m[-1]))
        m = re.findall(r"Terminating on ([a-z ]+)", txt)
        if m:
            out["terminated"] = m[-1].strip()
        out["logs"].append(os.path.basename(p))
    out["wall_s"] = wall
    return out


def particle_history(d):
    files = sorted(glob.glob(os.path.join(d, BASE + ".part.[0-9][0-9][0-9][0-9][0-9].bin")))
    t0, d0, tag0, _ = read_snapshot(files[0])
    z0 = np.full(tag0.max() + 1, np.nan)
    z0[tag0] = d0[:, 2]
    rows = {}
    for p in files:
        t, dd, tag, _ = read_snapshot(p)
        n = len(tag)
        if n == 0:
            rows[t] = [t, 0, np.nan, np.nan, np.nan, np.nan, np.nan]
            continue
        x, y, z = dd[:, 0], dd[:, 1], dd[:, 2]
        crossed = np.mean(np.sign(z) != np.sign(z0[tag]))
        rows[t] = [t, n, math.sqrt(np.mean(z * z)), math.sqrt(np.mean(x * x + y * y)),
                   crossed, float(np.max(np.abs(z))), float(np.max(np.sqrt(x * x + y * y)))]
    a = np.array([rows[t] for t in sorted(rows)])
    return a, files


def numbers(d):
    ph, files = particle_history(d)
    n0 = ph[0, 1]
    full = ph[:, 1] == n0                        # before the first removal
    zr, Rr = ph[:, 2] / ph[0, 2], ph[:, 3] / ph[0, 3]
    kp = int(np.nanargmin(np.where(full, zr, np.nan)))
    # refine t_p with a parabola through the three snapshots around the minimum
    tp = float(ph[kp, 0])
    if 0 < kp < len(ph) - 1 and full[kp + 1]:
        c = np.polyfit(ph[kp - 1:kp + 2, 0], zr[kp - 1:kp + 2], 2)
        if c[0] > 0:
            tp = float(-c[1] / (2 * c[0]))
    after = full & (ph[:, 0] > ph[kp, 0])
    ah = read_ah(os.path.join(d, BASE + ".horizon_summary_0.txt"))
    found = ah[np.isfinite(ah[:, 1])] if len(ah) else ah
    cv = read_curv_hst(os.path.join(d, BASE + ".curv.hst"))
    h = read_nrpic_hst(os.path.join(d, BASE + ".nrpic.hst"))
    z = read_athena_hst(os.path.join(d, BASE + ".z4c.user.hst"))
    res = dict(dir=d, t_end=float(h[-1, 0]), snapshots=len(files),
               z_rms0=float(ph[0, 2]), R_rms0=float(ph[0, 3]),
               t_pancake=tp, t_pancake_snapshot=float(ph[kp, 0]),
               z_rms_min_over_initial=float(zr[kp]), R_rms_over_initial_at_pancake=float(Rr[kp]),
               crossed_at_pancake_snapshot=float(ph[kp, 4]),
               crossed_max=float(np.nanmax(ph[:, 4])),
               t_crossed_half=float(ph[np.argmax(ph[:, 4] >= 0.5), 0]) if np.nanmax(ph[:, 4]) >= 0.5 else None,
               t_crossed_09=float(ph[np.argmax(ph[:, 4] >= 0.9), 0]) if np.nanmax(ph[:, 4]) >= 0.9 else None,
               t_crossed_01=float(ph[np.argmax(ph[:, 4] >= 0.1), 0]) if np.nanmax(ph[:, 4]) >= 0.1 else None,
               z_rms_rebound_max_over_initial=float(np.nanmax(zr[after])) if after.any() else None,
               t_z_rms_rebound_max=float(ph[after][np.nanargmax(zr[after]), 0]) if after.any() else None,
               t_first_AH=float(found[0, 0]) if len(found) else None,
               M_AH_first=float(found[0, 1]) if len(found) else None,
               M_AH_max=float(found[:, 1].max()) if len(found) else None,
               t_M_AH_max=float(found[np.argmax(found[:, 1]), 0]) if len(found) else None,
               M_AH_last=float(found[-1, 1]) if len(found) else None,
               t_AH_last=float(found[-1, 0]) if len(found) else None,
               AH_searches=int(len(ah)), AH_found=int(len(found)),
               AH_meanradius_first=float(found[0, 3]) if len(found) else None,
               alpha_min_end=float(h[-1, HC["alpha_min"]]),
               np0=int(h[0, HC["np"]]), np_end=int(h[-1, HC["np"]]),
               sum_m0=float(h[0, HC["sum_m"]]),
               m_excised_end=float(h[-1, HC["m_excised"]]),
               n_excised_end=int(h[-1, HC["n_excised"]]),
               n_escaped_end=int(h[-1, HC["n_escaped"]]),
               push_unconverged_total=int(np.nansum(h[:, HC["push_unconverged"]])),
               push_maxit_max=int(np.nanmax(h[:, HC["push_maxit"]])),
               nmb_max=int(np.nanmax(h[:, HC["nmb"]])), nmb_start=int(h[0, HC["nmb"]]),
               sum_mW_max_rel_change=float(np.nanmax(np.abs(
                   (h[:, HC["sum_mw"]] + 0.0) [h[:, HC["n_excised"]] == 0]
                   / h[0, HC["sum_mw"]] - 1.0))),
               finite=bool(np.all(np.isfinite(h[:, :HC["nmb"]]))))
    rem = np.nonzero(h[:, HC["n_excised"]] > 0)[0]
    res["t_first_removal"] = float(h[rem[0], 0]) if len(rem) else None
    if len(cv):
        i = int(np.argmax(cv[:, 1]))
        j = int(np.argmax(cv[:, 5]))
        res.update(I_max=float(cv[i, 1]), t_I_max=float(cv[i, 0]),
                   x_I_max=[float(v) for v in cv[i, 2:5]],
                   E_max=float(cv[j, 5]), t_E_max=float(cv[j, 0]),
                   x_E_max=[float(v) for v in cv[j, 6:9]])
        # largest density before the horizon phase (the pancake), t < t_p + 3
        pre = cv[:, 0] < tp + 3.0
        jj = int(np.argmax(np.where(pre, cv[:, 5], -1)))
        res.update(E_max_pancake=float(cv[jj, 5]), t_E_max_pancake=float(cv[jj, 0]),
                   x_E_max_pancake=[float(v) for v in cv[jj, 6:9]])
    key = next((k for k in z if "H-norm2" in k), None)
    if key:
        hn = np.sqrt(np.abs(z[key]))
        res.update(Hnorm0=float(hn[0]), Hnorm_max=float(hn.max()),
                   t_Hnorm_max=float(z["time"][np.argmax(hn)]))
        pre = z["time"] < tp + 3.0
        res.update(Hnorm_max_pancake=float(hn[pre].max()),
                   t_Hnorm_max_pancake=float(z["time"][pre][np.argmax(hn[pre])]))
    res.update(log_facts(d))
    series = dict(ph=ph, ah=found, cv=cv, h=h,
                  hn=(z["time"], np.sqrt(np.abs(z[key]))) if key else None)
    return res, series


def raster(rec, half, npx=300, col=4):
    """npx^2 image of [-half, half]^2 (x horizontal, z vertical) from the cell records
    (x, z, dx, I, E, alpha, sqrt gamma), coarse cells first, finer on top."""
    img = np.full((npx, npx), np.nan)
    pix = 2.0 * half / npx
    sel = (np.abs(rec[:, 0]) - 0.5 * rec[:, 2] < half) & (np.abs(rec[:, 1]) - 0.5 * rec[:, 2] < half)
    r = rec[sel]
    r = r[np.argsort(-r[:, 2])]
    for x, zc, dx, v in zip(r[:, 0], r[:, 1], r[:, 2], r[:, col]):
        i0 = int(np.floor((x - 0.5 * dx + half) / pix))
        i1 = int(np.ceil((x + 0.5 * dx + half) / pix))
        j0 = int(np.floor((zc - 0.5 * dx + half) / pix))
        j1 = int(np.ceil((zc + 0.5 * dx + half) / pix))
        img[max(j0, 0):max(min(j1, npx), 0), max(i0, 0):max(min(i1, npx), 0)] = v
    return img


def slice_at(d, t):
    cv = read_curv_hst(os.path.join(d, BASE + ".curv.hst"))
    k = int(np.argmin(np.abs(cv[:, 0] - t)))
    return read_curv_slice(os.path.join(d, f"{BASE}.curv.{int(cv[k, 9]):05d}.bin"))


def snapshot_at(d, t):
    files = sorted(glob.glob(os.path.join(d, BASE + ".part.[0-9][0-9][0-9][0-9][0-9].bin")))
    best, bt = None, None
    for p in files:
        with open(p, "rb") as f:
            f.read(8)
            tt, = struct.unpack("d", f.read(8))
        if best is None or abs(tt - t) < abs(bt - t):
            best, bt = p, tt
    return read_snapshot(best)


def fig_histories(runs, ser, res, newton, prolate):
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.085, top=0.975, wspace=0.27,
                        hspace=0.05)
    tN, aN, bN = newton
    for name in runs:
        s, c, lab = ser[name], COLOR[name], LABEL[name]
        ph = s["ph"]
        ax[0, 0].plot(ph[:, 0], ph[:, 2] / ph[0, 2], color=c, label=f"$z_{{\\rm rms}}$, {lab}")
        ax[0, 0].plot(ph[:, 0], ph[:, 3] / ph[0, 3], color=c, ls="--",
                      label=f"$R_{{\\rm rms}}$, {lab}")
        ax[0, 1].plot(ph[:, 0], ph[:, 4], color=c, label=f"crossed the plane, {lab}")
        ax[0, 1].plot(ph[:, 0], ph[:, 1] / ph[0, 1], color=c, ls=":",
                      label=f"particles left, {lab}")
        if len(s["ah"]):
            ax[0, 2].plot(s["ah"][:, 0], s["ah"][:, 1], color=c, marker="o", ms=2.0, lw=1.0,
                          label=f"oblate, {lab}")
        h = s["h"]
        ax[1, 0].plot(h[:, 0], h[:, HC["alpha_min"]], color=c, label=lab)
        if len(s["cv"]):
            ax[1, 1].semilogy(s["cv"][:, 0], s["cv"][:, 5], color=c, label=f"max $E$, {lab}")
            ax[1, 1].semilogy(s["cv"][:, 0], np.sqrt(np.abs(s["cv"][:, 1])), color=c, ls="--",
                              label=f"max $|I|^{{1/2}}$, {lab}")
        if s["hn"] is not None:
            ax[1, 2].semilogy(s["hn"][0], s["hn"][1], color=c, label=lab)
        for axx in ax.ravel():
            axx.axvline(res[name]["t_pancake"], color=c, lw=0.8, alpha=0.5)
            if res[name]["t_first_AH"] is not None:
                axx.axvline(res[name]["t_first_AH"], color=c, lw=0.8, alpha=0.5, ls="-.")
    ax[0, 0].plot(tN, np.abs(bN) / abs(bN[0]), color="k", lw=1.0, label="Newtonian $|b|/b_0$")
    ax[0, 0].plot(tN, np.abs(aN) / abs(aN[0]), color="k", lw=1.0, ls="--",
                  label="Newtonian $a/a_0$")
    for name, (pd, pc) in prolate.items():
        if len(pd):
            ax[0, 2].plot(pd[:, 0], pd[:, 1], color=pc, lw=1.0, ls=":",
                          label=f"prolate, {LABEL[name]}")
    ax[0, 2].axhline(M_ADM, **fs.GUIDE)
    ax[0, 0].set_ylabel("rms extent / initial")
    ax[0, 0].set_ylim(0, 1.25)
    ax[0, 1].set_ylabel("fraction of particles")
    ax[0, 2].set_ylabel("horizon mass [$M$]")
    ax[0, 2].set_ylim(0.80, 1.02)
    ax[1, 0].set_ylabel("smallest lapse")
    ax[1, 1].set_ylabel("largest $E$, $|I|^{1/2}$ [$M^{-2}$]")
    ax[1, 2].set_ylabel(r"$\|H\|_2$ (history norm)")
    for axx in ax[1]:
        axx.set_xlabel("$t/M$", labelpad=-1)
    ax[0, 0].legend(fontsize=6.5, ncol=2, loc="upper center")
    ax[0, 1].legend(fontsize=6.5, loc="center left")
    ax[0, 2].legend(fontsize=6.5, loc="lower left")
    ax[1, 0].legend(fontsize=7, loc="lower left")
    ax[1, 1].legend(fontsize=6.5, loc="upper left")
    ax[1, 2].legend(fontsize=7, loc="upper left")
    ax[0, 0].set_xlim(0, max(res[n]["t_end"] for n in runs))
    out = os.path.join(HERE, "figs", "oblate_collapse")
    fs.save(fig, out)
    plt.close(fig)
    return out + ".png"


def fig_mosaic(runs, dirs, times, half=12.0):
    names = list(runs)
    fig, axes, cax = fs.slice_mosaic(len(names), len(times), panel=1.585, left=1.37,
                                     bottom=0.36, fig_w=8.0)
    norm = LogNorm(1e-5, 1.0)
    im = None
    for i, name in enumerate(names):
        for j, t in enumerate(times):
            ax = axes[i, j]
            tt, rec = slice_at(dirs[name], t)
            img = raster(rec, half)
            im = ax.imshow(np.clip(img, 1e-12, None), origin="lower",
                           extent=[-half, half, -half, half], cmap=fs.CMAP["dens"],
                           norm=norm, interpolation="nearest", rasterized=True)
            ax.set_facecolor("black")
            fs.slice_ticks(ax, 2 * half, show_x=(i == len(names) - 1), show_y=(j == 0))
            ax.text(0.04, 0.95, f"$t={tt:.2f}M$" + (f", {LABEL[name]}" if j == 0 else ""),
                    transform=ax.transAxes, color="w", fontsize=8, va="top")
            if i == len(names) - 1:
                ax.set_xlabel("$x/M$", labelpad=-1)
            if j == 0:
                ax.set_ylabel("$z/M$", labelpad=-4)
    cb = fig.colorbar(im, cax=cax)
    cax.yaxis.set_ticks_position("left")
    cax.yaxis.set_label_position("left")
    cb.set_label("energy density $E$ [$M^{-2}$], plane $y=0$")
    out = os.path.join(HERE, "figs", "oblate_mosaic")
    fs.save(fig, out)
    plt.close(fig)
    return out + ".png"


def fig_particles(d, name, times, ah_first):
    fig, ax = plt.subplots(2, len(times), figsize=(fs.FULL_WIDTH, 4.3))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.10, top=0.94, wspace=0.22,
                        hspace=0.22)
    for j, t in enumerate(times):
        tt, dd, tag, _ = snapshot_at(d, t)
        x, y, z = dd[:, 0], dd[:, 1], dd[:, 2]
        half = max(1.0, 1.15 * float(np.max(np.sqrt(x * x + y * y)))) if len(x) else 1.0
        for i, (u, v, yl) in enumerate(((x, z, "$z/M$"), (x, y, "$y/M$"))):
            a = ax[i, j]
            a.plot(u, v, ls="none", marker=".", ms=0.9, color=fs.PAL["red"], alpha=0.6,
                   rasterized=True)
            a.set_xlim(-half, half)
            a.set_ylim(-half, half)
            a.set_aspect("equal")
            a.set_ylabel(yl, labelpad=-3)
        ax[0, j].set_title(f"$t={tt:.1f}M$, {len(x)} particles", fontsize=9)
        ax[1, j].set_xlabel("$x/M$", labelpad=-1)
    out = os.path.join(HERE, "figs", "oblate_particles")
    fs.save(fig, out)
    plt.close(fig)
    return out + ".png"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="name=DIR (m4, m8, m16)")
    ap.add_argument("--prolate", action="append", default=[],
                    help="name=DIR of a prolate run, for the horizon-mass panel")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", os.getcwd()))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
    fs.use_style()
    dirs = dict(r.split("=", 1) for r in a.run)
    res, ser = {}, {}
    for name, d in dirs.items():
        res[name], ser[name] = numbers(d)
        print(name, json.dumps(res[name], indent=1))
    q = math.sqrt(1 - 0.81)
    so = newt.evolve(10.0, 10.0 * q, amin=0.02)
    res["newtonian"] = dict(t_pancake=float(so.t_events[1][0]), t_a_zero=float(so.t[-1]))
    prolate = {}
    for r in a.prolate:
        name, d = r.split("=", 1)
        rows = []
        p = os.path.join(d, "prol.horizon_summary_0.txt")
        for line in open(p):
            if line.startswith("#") or not line.strip():
                continue
            x = line.split()
            if len(x) >= 12 and x[2] != "nan":
                rows.append([float(x[1]), float(x[2])])
        pd = keep_last(np.array(rows)) if rows else np.zeros((0, 2))
        prolate[name] = (pd, COLOR[name])
        res.setdefault("prolate", {})[name] = dict(
            dir=d, t_first_AH=float(pd[0, 0]) if len(pd) else None,
            M_AH_max=float(pd[:, 1].max()) if len(pd) else None)
    names = list(dirs)
    figs = [fig_histories(names, ser, res, (so.t, so.y[0], so.y[1]), prolate)]
    fine = names[-1]
    tp = res[fine]["t_pancake"]
    tah = res[fine]["t_first_AH"]
    times = [0.0, tp, 0.5 * (tp + tah) if tah else tp + 4.0, tah if tah else tp + 8.0]
    figs.append(fig_mosaic(names, dirs, times))
    figs.append(fig_particles(dirs[fine], fine, times, tah))
    res["figure_times"] = times
    res["figures"] = figs
    # resolution comparison
    if len(names) >= 2:
        lo, hi = names[0], names[-1]
        res["pair"] = dict(
            coarse=lo, fine=hi,
            dt_pancake=res[hi]["t_pancake"] - res[lo]["t_pancake"],
            dt_first_AH=(res[hi]["t_first_AH"] - res[lo]["t_first_AH"])
            if res[hi]["t_first_AH"] and res[lo]["t_first_AH"] else None,
            dM_AH_max=(res[hi]["M_AH_max"] - res[lo]["M_AH_max"])
            if res[hi]["M_AH_max"] and res[lo]["M_AH_max"] else None)
    with open(os.path.join(a.out, "collapse.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("wrote", os.path.join(a.out, "collapse.json"), figs)


if __name__ == "__main__":
    main()
