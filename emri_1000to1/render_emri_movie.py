#!/usr/bin/env python3
"""
Pure-CPU live orbital-motion figure & movie renderer for 1000:1 Schwarzschild EMRI NR runs.

Reads (without touching or stopping the live GPU run, CUDA_VISIBLE_DEVICES=""):
  - <base>.traj.bin                 (particle coordinates & covariant 4-velocity)
  - <base>.trajmet.bin              (metric components at particle -> geometric areal radius)
  - <base>.co_0.txt                 (SMBH puncture tracker position & velocity)
  - <base>.horizon_summary_0.txt    (SMBH apparent horizon radius & mass)
  - bin/<base>.alpha_xy.NNNNN.bin   (AthenaK v1.1 2D equatorial lapse slices + AMR blocks)
  - waveforms/rpsi4_{real,imag}_*.txt
  - run_meta.json

Produces:
  - <fig_dir>/fig_<prefix>_orbital_motion.png   (300 dpi static orbital-motion physics figure)
  - <run_dir>/movie_frames/frame_NNNNN.png      (incremental frames)
  - <fig_dir>/<prefix>_movie.webp & .gif        (animated movie)
  - <fig_dir>/<prefix>_movie_latest.png         (latest movie frame)
"""

import argparse
import glob
import json
import math
import os
import re
import shutil
import struct
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Rectangle
import numpy as np
from PIL import Image

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz

from analyze_emri_gw import (
    lm_col,
    load_waveform_spheres,
    r_areal_from_iso,
    read_single_traj,
    read_single_trajmet,
    safe_load_table,
)
from pn_2sf_reference import EMRIReferenceModel


def read_athenak_bin(path):
    """Pure-NumPy reader for AthenaK binary v1.1 slices (no h5py needed)."""
    fsize = os.path.getsize(path)
    if fsize < 64:
        raise EOFError(f"Small slice: {path}")
    with open(path, "rb") as fp:
        hdr = fp.readline().split()
        if not hdr or hdr[0] != b"Athena" or hdr[-1].split(b"=")[-1] != b"1.1":
            raise ValueError(f"Unexpected Athena header in {path}")
        pcount = int(fp.readline().split(b"=")[-1])
        pheader = {}
        for _ in range(pcount - 1):
            line = fp.readline().decode("utf-8", errors="replace")
            if "=" not in line:
                raise EOFError(f"Truncated preheader in {path}")
            k, v = [s.strip() for s in line.split("=", 1)]
            pheader[k] = v
        t = float(pheader["time"])
        loc_bytes = int(pheader["size of location"])
        var_bytes = int(pheader["size of variable"])
        _nv = int(fp.readline().split(b"=")[-1])
        var_list = [v.decode("utf-8") for v in fp.readline().split()[1:]]
        hdr_sz = int(fp.readline().split(b"=")[-1])
        fp.seek(hdr_sz, os.SEEK_CUR)

        loc_fmt = "<d" if loc_bytes == 8 else "<f"
        var_dtype = np.float64 if var_bytes == 8 else np.float32
        blocks = []
        while True:
            bhead = fp.read(6 * 4 + 4 + 3 * 4)
            if not bhead:
                break
            if len(bhead) < 40:
                raise EOFError(f"Truncated block header in {path}")
            is_, ie, js, je, ks, ke = struct.unpack("<6i", bhead[:24])
            nx1, nx2, nx3 = ie - is_ + 1, je - js + 1, ke - ks + 1
            ncells = nx1 * nx2 * nx3
            coords_raw = fp.read(loc_bytes * 6)
            if len(coords_raw) < loc_bytes * 6:
                raise EOFError(f"Truncated block coords in {path}")
            x1min, x1max, x2min, x2max, x3min, x3max = struct.unpack(
                loc_fmt.replace("<", "<6"), coords_raw
            )
            data_bytes = len(var_list) * ncells * var_bytes
            raw = fp.read(data_bytes)
            if len(raw) < data_bytes:
                raise EOFError(f"Truncated block data in {path}")
            arr = np.frombuffer(raw, dtype=var_dtype).reshape(
                len(var_list), nx3, nx2, nx1
            ).copy()
            blocks.append(((x1min, x1max, x2min, x2max, x3min, x3max), arr))
    return t, var_list, blocks


def rasterize_xy_slice(blocks, var_idx, xlim, ylim, ngrid=320, shift=(0.0, 0.0)):
    """Rasterize 2D xy AMR blocks into (xlim, ylim) after shifting coords by (-shift[0], -shift[1])."""
    sx, sy = shift
    img = np.full((ngrid, ngrid), np.nan, dtype=np.float64)
    gx = np.linspace(xlim[0], xlim[1], ngrid)
    gy = np.linspace(ylim[0], ylim[1], ngrid)
    # Paint coarser blocks first, finer blocks last so finer AMR always overwrites
    blocks_sorted = sorted(blocks, key=lambda item: -(item[0][1] - item[0][0]))
    for (x1min, x1max, x2min, x2max, _, _), arr in blocks_sorted:
        bx0, bx1 = x1min - sx, x1max - sx
        by0, by1 = x2min - sy, x2max - sy
        if bx1 < xlim[0] or bx0 > xlim[1] or by1 < ylim[0] or by0 > ylim[1]:
            continue
        plane = arr[var_idx, 0, :, :]
        ny, nx = plane.shape
        ix0 = max(0, int(np.searchsorted(gx, bx0, side="left")))
        ix1 = min(ngrid, int(np.searchsorted(gx, bx1, side="right")))
        iy0 = max(0, int(np.searchsorted(gy, by0, side="left")))
        iy1 = min(ngrid, int(np.searchsorted(gy, by1, side="right")))
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        xi = np.clip(((gx[ix0:ix1] - bx0) / max(bx1 - bx0, 1e-12) * nx).astype(int), 0, nx - 1)
        yi = np.clip(((gy[iy0:iy1] - by0) / max(by1 - by0, 1e-12) * ny).astype(int), 0, ny - 1)
        img[iy0:iy1, ix0:ix1] = plane[np.ix_(yi, xi)]
    return gx, gy, img


def draw_amr_blocks(ax, blocks, xlim, ylim, shift=(0.0, 0.0), max_bw=2.1):
    sx, sy = shift
    for (x1min, x1max, x2min, x2max, _, _), _ in blocks:
        bx0, bx1 = x1min - sx, x1max - sx
        by0, by1 = x2min - sy, x2max - sy
        bw, bh = bx1 - bx0, by1 - by0
        if bw <= max_bw and bx1 >= xlim[0] and bx0 <= xlim[1] and by1 >= ylim[0] and by0 <= ylim[1]:
            is_fine = bw <= 1.1  # L=7 around BH
            ax.add_patch(
                Rectangle(
                    (bx0, by0),
                    bw,
                    bh,
                    fill=False,
                    ec="cyan" if not is_fine else "#7FFFD4",
                    lw=0.45 if not is_fine else 0.35,
                    alpha=0.50 if not is_fine else 0.35,
                    zorder=4,
                )
            )


def compute_lab_box(x_p, x_bh):
    """Fixed equal-aspect lab-frame box covering both SMBH and particle cleanly."""
    all_x = np.concatenate([x_p[:, 0], x_bh[:, 0]])
    all_y = np.concatenate([x_p[:, 1], x_bh[:, 1]])
    xmin, xmax = float(np.min(all_x)) - 2.5, float(np.max(all_x)) + 2.5
    ymin, ymax = float(np.min(all_y)) - 2.5, float(np.max(all_y)) + 2.5
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    half = max(0.5 * (xmax - xmin), 0.5 * (ymax - ymin), 8.5)
    half = math.ceil(half)
    return (cx - half, cx + half), (cy - half, cy + half)


def render_static_orbital_figure(
    out_png,
    name,
    R0,
    q,
    r_iso0,
    t_tr,
    x_p,
    x_bh,
    x_rel,
    R_geom,
    om_smooth,
    R_om,
    phi_orb,
    bh_disp,
    hs_t,
    hs_rmin,
    ev_1sf,
    ev_2sf,
    ev_pn,
    latest_slice,
):
    cz.use_style()
    fig = plt.figure(figsize=(11.2, 8.8))
    gs = GridSpec(2, 2, figure=fig, left=0.075, right=0.94, bottom=0.075, top=0.90, wspace=0.28, hspace=0.31)

    t_max = float(t_tr[-1])
    n_orb_tot = float((phi_orb[-1] - phi_orb[0]) / (2.0 * math.pi))
    r_ah_end = float(hs_rmin[-1]) if len(hs_rmin) else 0.93

    # --- Panel 1 (Top-Left): BH-centered inspiral orbit on latest 2D lapse slice ---
    ax0 = fig.add_subplot(gs[0, 0])
    lim_bh = (-8.5, 8.5)
    if latest_slice is not None:
        t_s, vlist, blocks = latest_slice
        va_i = vlist.index("z4c_alpha") if "z4c_alpha" in vlist else 0
        xbh_s = (
            float(np.interp(t_s, t_tr, x_bh[:, 0])),
            float(np.interp(t_s, t_tr, x_bh[:, 1])),
        )
        gx, gy, alpha_bh = rasterize_xy_slice(blocks, va_i, lim_bh, lim_bh, ngrid=360, shift=xbh_s)
        pcm = ax0.pcolormesh(
            gx, gy, alpha_bh, cmap="viridis", vmin=0.25, vmax=1.0, shading="auto", rasterized=True
        )
        draw_amr_blocks(ax0, blocks, lim_bh, lim_bh, shift=xbh_s, max_bw=2.1)
    else:
        pcm = None

    # Reference circles: initial isotropic radius & approximate ISCO coordinate radius (4.95 M)
    ax0.add_patch(Circle((0.0, 0.0), r_iso0, fill=False, ec="w", ls=":", lw=0.9, alpha=0.65, zorder=4))
    ax0.add_patch(Circle((0.0, 0.0), r_ah_end, color="k", ec="w", lw=1.0, zorder=6))

    # Subsample trajectory cleanly for time-colored LineCollection
    stride = max(1, len(t_tr) // 2500)
    xr_s = x_rel[::stride, 0]
    yr_s = x_rel[::stride, 1]
    t_col = t_tr[::stride]
    pts = np.column_stack([xr_s, yr_s]).reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, cmap="plasma", norm=plt.Normalize(0.0, t_max), linewidths=1.35, alpha=0.92, zorder=5)
    lc.set_array(t_col[:-1])
    ax0.add_collection(lc)
    cbar = fig.colorbar(lc, ax=ax0, fraction=0.046, pad=0.025)
    cbar.set_label(r"Time $t\,[M]$", fontsize=9.0)
    cbar.ax.tick_params(labelsize=8.0, direction="in")

    ax0.scatter([x_rel[0, 0]], [x_rel[0, 1]], s=42, c=cz.PAL["green"], marker="D", edgecolors="w", lw=0.7, zorder=7, label=r"$t=0$")
    ax0.scatter([x_rel[-1, 0]], [x_rel[-1, 1]], s=52, c=cz.PAL["red"], marker="o", edgecolors="w", lw=0.8, zorder=8, label=rf"$t={t_max:.0f}\,M$")
    ax0.set_aspect("equal")
    ax0.set_xlim(lim_bh); ax0.set_ylim(lim_bh)
    ax0.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=1)
    ax0.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
    ax0.legend(loc="lower left", fontsize=8.0, frameon=False, labelcolor="w")
    ax0.set_title(rf"BH-centered orbit on $\alpha(\Delta x,\Delta y)$ ({n_orb_tot:.1f} orbits)")

    # --- Panel 2 (Top-Right): Lab-frame SMBH + particle trajectories ---
    ax1 = fig.add_subplot(gs[0, 1])
    lab_xlim, lab_ylim = compute_lab_box(x_p, x_bh)
    if latest_slice is not None:
        t_s, vlist, blocks = latest_slice
        va_i = vlist.index("z4c_alpha") if "z4c_alpha" in vlist else 0
        gx2, gy2, alpha_lab = rasterize_xy_slice(blocks, va_i, lab_xlim, lab_ylim, ngrid=320, shift=(0.0, 0.0))
        ax1.pcolormesh(gx2, gy2, alpha_lab, cmap="viridis", vmin=0.25, vmax=1.0, shading="auto", rasterized=True, alpha=0.85)
    ax1.plot(x_p[::stride, 0], x_p[::stride, 1], color="w", lw=0.75, alpha=0.65, label="Particle (lab)", zorder=4)
    ax1.plot(x_bh[::stride, 0], x_bh[::stride, 1], color=cz.PAL["yellow"], lw=2.0, alpha=0.95, label="SMBH tracker", zorder=5)
    ax1.add_patch(Circle((x_bh[-1, 0], x_bh[-1, 1]), r_ah_end, color="k", ec="w", lw=1.0, zorder=6))
    ax1.scatter([x_p[-1, 0]], [x_p[-1, 1]], s=46, c=cz.PAL["red"], edgecolors="w", lw=0.8, zorder=7)
    # Mark key epochs on SMBH track if it moved noticeably
    if float(bh_disp[-1]) > 0.5:
        for t_mark in [500.0, 700.0, 900.0]:
            if t_mark < t_max:
                xm = float(np.interp(t_mark, t_tr, x_bh[:, 0]))
                ym = float(np.interp(t_mark, t_tr, x_bh[:, 1]))
                ax1.scatter([xm], [ym], s=20, c="k", edgecolors=cz.PAL["yellow"], lw=0.8, zorder=8)
                ax1.annotate(
                    rf"${int(t_mark)}\,M$",
                    xy=(xm, ym),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha="center",
                    fontsize=7.5,
                    color="w",
                    zorder=9,
                )
    ax1.set_aspect("equal")
    ax1.set_xlim(lab_xlim); ax1.set_ylim(lab_ylim)
    ax1.set_xlabel(r"Lab $x\,[M]$", labelpad=1)
    ax1.set_ylabel(r"Lab $y\,[M]$")
    ax1.legend(loc="upper left", fontsize=8.0, frameon=False, labelcolor="w")
    ax1.set_title(rf"Lab frame ($|\mathbf{{x}}_{{\rm BH}}|={bh_disp[-1]:.2f}\,M$ at $t={t_max:.0f}\,M$)")

    # --- Panel 3 (Bottom-Left): Areal separation R_geom(t) & R_Omega(t) vs 1SF/2SF/3.5PN ---
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(t_tr, R_geom, color=cz.PAL["blue"], lw=1.6, label=r"NR $R_{\rm geom}(t)$")
    m_om = (t_tr >= 25.0) & (R_om > 4.0) & (R_om < 8.5)
    ax2.plot(t_tr[m_om], R_om[m_om], color=cz.PAL["orange"], lw=1.1, ls="-", alpha=0.85, label=r"NR $R_\Omega = \Omega^{-2/3}$")
    m1 = ev_1sf["t"] <= t_max
    m2 = ev_2sf["t"] <= t_max
    mp = ev_pn["t"] <= t_max
    ax2.plot(ev_1sf["t"][m1], ev_1sf["R"][m1], color="k", ls="--", lw=1.2, label="1SF (RWZ)")
    ax2.plot(ev_2sf["t"][m2], ev_2sf["R"][m2], color=cz.PAL["red"], ls=":", lw=1.4, label="2SF (1PA)")
    ax2.plot(ev_pn["t"][mp], ev_pn["R"][mp], color=cz.PAL["green"], ls="-.", lw=1.2, label="3.5PN")
    ax2.axhline(6.0, color="grey", ls="--", lw=1.0, alpha=0.75)
    ax2.text(0.02 * t_max, 5.93, r"Schwarzschild ISCO ($6\,M$)", fontsize=8.0, color="0.35", va="top")

    # Mark onset of BH coordinate drift (|x_BH| > 0.25 M) if present
    idx_drift = np.where(bh_disp > 0.25)[0]
    if len(idx_drift) > 0:
        t_dr = float(t_tr[idx_drift[0]])
        ax2.axvspan(t_dr, t_max, color=cz.PAL["red"], alpha=0.07)
        ax2.axvline(t_dr, color=cz.PAL["red"], ls=":", lw=0.9, alpha=0.7)
        ax2.text(t_dr + 8.0, 5.50, r"$|\mathbf{x}_{\rm BH}| > 0.25\,M$", fontsize=7.5, color=cz.PAL["red"], va="bottom")

    ax2.set_xlim(0.0, t_max)
    ax2.set_ylim(5.4, 6.65)
    ax2.set_xlabel(r"Time $t\,[M]$", labelpad=1)
    ax2.set_ylabel(r"Areal separation $R\,[M]$")
    ax2.legend(loc="lower left", ncol=2, fontsize=7.8, frameon=False)
    ax2.set_title("Inspiral separation vs 1SF / 2SF / 3.5PN")

    # --- Panel 4 (Bottom-Right): Orbital frequency Omega(t) vs 1SF/2SF/3.5PN + BH drift ---
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(t_tr[m_om], om_smooth[m_om], color=cz.PAL["blue"], lw=1.5, label=r"NR $\Omega(t)$")
    ax3.plot(ev_1sf["t"][m1], ev_1sf["Omega"][m1], color="k", ls="--", lw=1.2, label="1SF (RWZ)")
    ax3.plot(ev_2sf["t"][m2], ev_2sf["Omega"][m2], color=cz.PAL["red"], ls=":", lw=1.4, label="2SF (1PA)")
    ax3.plot(ev_pn["t"][mp], ev_pn["Omega"][mp], color=cz.PAL["green"], ls="-.", lw=1.2, label="3.5PN")
    ax3.axhline(6.0 ** (-1.5), color="grey", ls="--", lw=1.0, alpha=0.7)
    ax3.set_xlim(0.0, t_max)
    ax3.set_ylim(0.056, 0.072)
    ax3.set_xlabel(r"Time $t\,[M]$", labelpad=1)
    ax3.set_ylabel(r"Orbital frequency $\Omega\,[M^{-1}]$")
    ax3.set_title(r"Orbital frequency $\Omega(t)$ & SMBH tracker drift")

    ax3_r = ax3.twinx()
    ax3_r.plot(t_tr, bh_disp, color=cz.PAL["red"], lw=1.2, ls="-", alpha=0.70, label=r"$|\mathbf{x}_{\rm BH}(t)|$")
    ax3_r.set_ylabel(r"SMBH drift $|\mathbf{x}_{\rm BH}|\,[M]$", color=cz.PAL["red"])
    ax3_r.tick_params(axis="y", colors=cz.PAL["red"], direction="in")
    ax3_r.set_ylim(0.0, max(1.0, float(np.max(bh_disp)) * 1.15))

    # Combined clean legend in upper left
    h1, l1 = ax3.get_legend_handles_labels()
    h2, l2 = ax3_r.get_legend_handles_labels()
    ax3.legend(h1 + h2, l1 + l2, loc="upper left", ncol=2, fontsize=7.6, frameon=False)

    for ax in (ax0, ax1, ax2, ax3):
        ax.tick_params(which="both", direction="in", top=True, right=True)

    fig.suptitle(
        rf"{name}: Live Orbital Motion Physics ($q={q:.0e}$, $R_0={R0:.2f}\,M$, $t={t_max:.1f}\,M$, {n_orb_tot:.2f} orbits)",
        fontsize=12.0,
        y=0.96,
    )
    fig.savefig(out_png, dpi=300)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--fig-dir", required=True)
    ap.add_argument("--prefix", default="emri_it3_live")
    ap.add_argument("--fps", type=int, default=6)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    fig_dir = os.path.abspath(args.fig_dir)
    os.makedirs(fig_dir, exist_ok=True)

    with open(os.path.join(run_dir, "run_meta.json"), "r") as f:
        meta = json.load(f)
    name = meta["name"]
    R0 = float(meta["R0"])
    q = float(meta["q"])
    r_iso0 = float(meta["ic"]["r_iso"])
    radii = [float(r) for r in meta["extraction_radii"]]

    traj = read_single_traj(os.path.join(run_dir, f"{name}.traj.bin"))
    tmet = read_single_trajmet(os.path.join(run_dir, f"{name}.trajmet.bin"))
    co0 = safe_load_table(os.path.join(run_dir, f"{name}.co_0.txt"), min_cols=5, tcol=1)
    hs = safe_load_table(os.path.join(run_dir, f"{name}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    if traj is None or len(traj) < 2:
        raise RuntimeError("Trajectory file missing or empty")

    t_tr = traj[:, 0]
    x_p = traj[:, 2:5]
    if co0 is not None and len(co0) > 1:
        x_bh = np.column_stack([
            np.interp(t_tr, co0[:, 1], co0[:, 2]),
            np.interp(t_tr, co0[:, 1], co0[:, 3]),
            np.interp(t_tr, co0[:, 1], co0[:, 4]),
        ])
    else:
        x_bh = np.zeros_like(x_p)

    x_rel = x_p - x_bh
    r_iso_t = np.linalg.norm(x_rel, axis=1)
    if tmet is not None and len(tmet) > 1:
        gzz_t = np.interp(t_tr, tmet[:, 0], tmet[:, 11])
        R_geom = r_iso_t * np.sqrt(np.maximum(gzz_t, 1.0e-6))
    else:
        R_geom = r_areal_from_iso(r_iso_t)

    phi_orb = np.unwrap(np.arctan2(x_rel[:, 1], x_rel[:, 0]))
    dt_med = float(np.median(np.diff(t_tr)))
    ks = max(1, int(round(1.5 / max(dt_med, 1.0e-6))))
    om_smooth = np.gradient(phi_orb, t_tr)
    if len(t_tr) > 2 * ks + 2:
        om_smooth[ks:-ks] = (phi_orb[2 * ks:] - phi_orb[:-2 * ks]) / (t_tr[2 * ks:] - t_tr[:-2 * ks])
        om_smooth[:ks] = om_smooth[ks]
        om_smooth[-ks:] = om_smooth[-ks - 1]
    R_om = np.maximum(np.abs(om_smooth), 1.0e-6) ** (-2.0 / 3.0)
    bh_disp = np.linalg.norm(x_bh, axis=1)

    hs_t = hs[:, 1] if (hs is not None and len(hs) > 0) else np.array([0.0])
    hs_m = hs[:, 2] if (hs is not None and len(hs) > 0) else np.array([1.0])
    hs_rmin = hs[:, 11] if (hs is not None and len(hs) > 0) else np.array([0.93])

    t_max = float(t_tr[-1])
    ref = EMRIReferenceModel()
    ev_1sf = ref.evolve_inspiral("1SF", R0=R0, q=q, t_max=t_max + 20.0, dt=0.5)
    ev_2sf = ref.evolve_inspiral("2SF", R0=R0, q=q, t_max=t_max + 20.0, dt=0.5)
    ev_pn = ref.evolve_inspiral("3.5PN", R0=R0, q=q, t_max=t_max + 20.0, dt=0.5)

    # Load outermost wave-zone sphere for live movie GW panel
    spheres = load_waveform_spheres(run_dir, radii)
    r_out = max(spheres.keys())
    sp_out = spheres[r_out]
    col22 = lm_col(2, 2)
    u_wf = sp_out["u"]
    psi22_nr = sp_out["re"][:, col22] + 1j * sp_out["im"][:, col22]
    r_star_out = sp_out["r_star"]
    u_wf_max = float(u_wf[-1])

    # Phase-align 1SF (2,2) reference at u_align ~ 120 M (past junk) matching NR handedness
    u_align = min(120.0, 0.5 * max(u_wf_max, 20.0))
    m_ref = ev_1sf["t"] <= max(u_wf_max, 20.0)
    u_1sf = ev_1sf["t"][m_ref]
    phi_wf = np.unwrap(np.angle(psi22_nr))
    dphi_wf = np.gradient(phi_wf, u_wf)
    cm_wf = (u_wf >= 90.0) & (u_wf <= max(u_wf_max - 15.0, 95.0))
    m_sgn = float(np.median(dphi_wf[cm_wf])) if np.any(cm_wf) else -1.0
    raw_1sf = np.conj(ev_1sf["rPsi4_22"][m_ref]) if m_sgn > 0 else ev_1sf["rPsi4_22"][m_ref]
    psi22_1sf = raw_1sf.copy()
    if u_wf_max > 100.0 and len(u_1sf) > 10:
        ph_nr_a = float(np.angle(np.interp(u_align, u_wf, np.real(psi22_nr)) + 1j * np.interp(u_align, u_wf, np.imag(psi22_nr))))
        ph_1sf_a = float(np.angle(np.interp(u_align, u_1sf, np.real(psi22_1sf)) + 1j * np.interp(u_align, u_1sf, np.imag(psi22_1sf))))
        psi22_1sf = psi22_1sf * np.exp(1j * (ph_nr_a - ph_1sf_a))

    # Discover all alpha_xy slices
    slice_paths = sorted(glob.glob(os.path.join(run_dir, "bin", f"{name}.alpha_xy.*.bin")))
    frame_dir = os.path.join(run_dir, "movie_frames")
    os.makedirs(frame_dir, exist_ok=True)
    lab_xlim, lab_ylim = compute_lab_box(x_p, x_bh)
    lim_bh = (-8.5, 8.5)

    cz.use_style()
    rendered = 0
    latest_slice = None
    last_frame_path = None
    for sp in slice_paths:
        m_num = re.search(r"\.(\d{5})\.bin$", sp)
        if not m_num:
            continue
        try:
            t_s, vlist, blocks = read_athenak_bin(sp)
            latest_slice = (t_s, vlist, blocks)
        except (EOFError, OSError, ValueError):
            continue

        out_png = os.path.join(frame_dir, f"frame_{m_num.group(1)}.png")
        last_frame_path = out_png
        if os.path.isfile(out_png) and not args.overwrite:
            continue

        va_i = vlist.index("z4c_alpha") if "z4c_alpha" in vlist else 0
        k_cur = max(0, min(int(np.searchsorted(t_tr, t_s, side="right")) - 1, len(t_tr) - 1))
        xbh_s = (float(x_bh[k_cur, 0]), float(x_bh[k_cur, 1]))
        bh_d_now = float(bh_disp[k_cur])
        r_now = float(R_geom[k_cur])
        n_orb_now = float((phi_orb[k_cur] - phi_orb[0]) / (2.0 * math.pi))
        ah_i = max(0, min(int(np.searchsorted(hs_t, t_s, side="right")) - 1, len(hs_rmin) - 1))
        r_ah_now = float(hs_rmin[ah_i])
        m_ah_now = float(hs_m[ah_i])

        gx_bh, gy_bh, img_bh = rasterize_xy_slice(blocks, va_i, lim_bh, lim_bh, ngrid=280, shift=xbh_s)
        gx_lb, gy_lb, img_lb = rasterize_xy_slice(blocks, va_i, lab_xlim, lab_ylim, ngrid=280, shift=(0.0, 0.0))

        fig = plt.figure(figsize=(11.0, 8.6))
        gs = GridSpec(2, 2, figure=fig, left=0.075, right=0.96, bottom=0.075, top=0.90, wspace=0.25, hspace=0.30)

        # Panel 1: BH-centered lapse + AMR + relative orbit trail
        ax0 = fig.add_subplot(gs[0, 0])
        ax0.pcolormesh(gx_bh, gy_bh, img_bh, cmap="viridis", vmin=0.25, vmax=1.0, shading="auto", rasterized=True)
        draw_amr_blocks(ax0, blocks, lim_bh, lim_bh, shift=xbh_s, max_bw=2.1)
        ax0.add_patch(Circle((0.0, 0.0), r_iso0, fill=False, ec="w", ls=":", lw=0.8, alpha=0.55, zorder=4))
        ax0.add_patch(Circle((0.0, 0.0), r_ah_now, color="k", ec="w", lw=1.0, zorder=6))
        # Full faint trail + bright last-orbit trail
        k_orb0 = int(np.searchsorted(t_tr, max(0.0, t_s - 105.0), side="left"))
        stride_f = max(1, (k_cur + 1) // 1200)
        ax0.plot(x_rel[:k_cur+1:stride_f, 0], x_rel[:k_cur+1:stride_f, 1], color="w", lw=0.75, alpha=0.35, zorder=4)
        ax0.plot(x_rel[k_orb0:k_cur+1, 0], x_rel[k_orb0:k_cur+1, 1], color=cz.PAL["yellow"], lw=1.6, alpha=0.95, zorder=5)
        ax0.scatter([x_rel[k_cur, 0]], [x_rel[k_cur, 1]], s=48, c=cz.PAL["red"], edgecolors="w", lw=0.8, zorder=7)
        ax0.set_aspect("equal")
        ax0.set_xlim(lim_bh); ax0.set_ylim(lim_bh)
        ax0.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=1)
        ax0.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
        ax0.set_title(rf"BH-centered $\alpha(\Delta x,\Delta y)$ & AMR ($N_{{\rm orb}}={n_orb_now:.2f}$)")

        # Panel 2: Lab-frame lapse + SMBH & particle trajectories
        ax1 = fig.add_subplot(gs[0, 1])
        ax1.pcolormesh(gx_lb, gy_lb, img_lb, cmap="viridis", vmin=0.25, vmax=1.0, shading="auto", rasterized=True)
        ax1.plot(x_p[:k_cur+1:stride_f, 0], x_p[:k_cur+1:stride_f, 1], color="w", lw=0.75, alpha=0.55, zorder=4)
        ax1.plot(x_bh[:k_cur+1:stride_f, 0], x_bh[:k_cur+1:stride_f, 1], color=cz.PAL["yellow"], lw=1.8, alpha=0.95, zorder=5)
        ax1.add_patch(Circle(xbh_s, r_ah_now, color="k", ec="w", lw=1.0, zorder=6))
        ax1.scatter([x_p[k_cur, 0]], [x_p[k_cur, 1]], s=42, c=cz.PAL["red"], edgecolors="w", lw=0.8, zorder=7)
        ax1.set_aspect("equal")
        ax1.set_xlim(lab_xlim); ax1.set_ylim(lab_ylim)
        ax1.set_xlabel(r"Lab $x\,[M]$", labelpad=1)
        ax1.set_ylabel(r"Lab $y\,[M]$")
        ax1.set_title(rf"Lab frame ($|\mathbf{{x}}_{{\rm BH}}|={bh_d_now:.2f}\,M$, $M_{{\rm AH}}={m_ah_now:.4f}\,M$)")

        # Panel 3: Inspiral separation R_geom(t) vs 1SF / 2SF / 3.5PN
        ax2 = fig.add_subplot(gs[1, 0])
        m1 = ev_1sf["t"] <= t_max
        m2 = ev_2sf["t"] <= t_max
        mp = ev_pn["t"] <= t_max
        ax2.plot(ev_1sf["t"][m1], ev_1sf["R"][m1], color="k", ls="--", lw=1.1, alpha=0.7, label="1SF (RWZ)")
        ax2.plot(ev_2sf["t"][m2], ev_2sf["R"][m2], color=cz.PAL["red"], ls=":", lw=1.3, alpha=0.7, label="2SF (1PA)")
        ax2.plot(ev_pn["t"][mp], ev_pn["R"][mp], color=cz.PAL["green"], ls="-.", lw=1.1, alpha=0.7, label="3.5PN")
        ax2.plot(t_tr[:k_cur+1], R_geom[:k_cur+1], color=cz.PAL["blue"], lw=1.7, label="Full 3+1 NR")
        ax2.scatter([t_tr[k_cur]], [r_now], s=36, c=cz.PAL["red"], edgecolors="w", lw=0.7, zorder=6)
        ax2.axhline(6.0, color="grey", ls="--", lw=0.9, alpha=0.7)
        ax2.set_xlim(0.0, t_max)
        ax2.set_ylim(5.4, 6.65)
        ax2.set_xlabel(r"Time $t\,[M]$", labelpad=1)
        ax2.set_ylabel(r"Areal separation $R\,[M]$")
        ax2.legend(loc="lower left", ncol=2, fontsize=7.8, frameon=False)
        ax2.set_title(rf"Inspiral orbit ($R_{{\rm geom}}={r_now:.3f}\,M$, ISCO $=6\,M$)")

        # Panel 4: Quadrupole GW signal advancing in retarded time u = t - r_*
        ax3 = fig.add_subplot(gs[1, 1])
        u_cur = t_s - r_star_out
        ax3.axvspan(0.0, 90.0, color="grey", alpha=0.14)
        ax3.plot(u_1sf, 1e5 * np.real(psi22_1sf), color="k", ls=":", lw=1.0, alpha=0.65, label="1SF (RWZ)")
        if u_cur > 0.0:
            mw = (u_wf >= 0.0) & (u_wf <= u_cur)
            if np.any(mw):
                ax3.plot(u_wf[mw], 1e5 * np.real(psi22_nr[mw]), color=cz.PAL["blue"], lw=1.25, label=rf"NR ($r={int(r_out)}\,M$)")
            ax3.axvline(u_cur, color=cz.PAL["red"], ls="--", lw=0.9, alpha=0.8)
        ax3.set_xlim(0.0, max(u_wf_max, 50.0))
        ax3.set_ylim(-3.5, 3.5)
        ax3.set_xlabel(r"Retarded time $u\,[M]$", labelpad=1)
        ax3.set_ylabel(r"$10^5\,\mathrm{Re}\,r\Psi_4^{(2,2)}$")
        ax3.legend(loc="upper right", ncol=2, fontsize=7.8, frameon=False)
        ax3.set_title(rf"Quadrupole GW ($u={max(u_cur, 0.0):.1f}\,M$ at $r={int(r_out)}\,M$)")

        for ax in (ax0, ax1, ax2, ax3):
            ax.tick_params(which="both", direction="in", top=True, right=True)

        fig.suptitle(
            rf"{name} (Full 3+1 NR, $q={q:.0e}$, $R_0={R0:.2f}\,M$)   $t = {t_s:.1f}\,M$",
            fontsize=12.0,
            y=0.96,
        )
        fig.savefig(out_png, dpi=150)
        plt.close(fig)
        rendered += 1

    # Render high-res static orbital motion physics figure
    static_png = os.path.join(fig_dir, f"fig_{args.prefix}_orbital_motion.png")
    render_static_orbital_figure(
        static_png,
        name,
        R0,
        q,
        r_iso0,
        t_tr,
        x_p,
        x_bh,
        x_rel,
        R_geom,
        om_smooth,
        R_om,
        phi_orb,
        bh_disp,
        hs_t,
        hs_rmin,
        ev_1sf,
        ev_2sf,
        ev_pn,
        latest_slice,
    )
    print(f"Wrote static orbital figure: {static_png}")

    # Assemble WebP & GIF animations
    frames = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
    if frames:
        imgs = [Image.open(p).convert("RGB") for p in frames]
        dur_ms = int(round(1000.0 / max(args.fps, 1)))
        webp_out = os.path.join(fig_dir, f"{args.prefix}_movie.webp")
        gif_out = os.path.join(fig_dir, f"{args.prefix}_movie.gif")
        latest_out = os.path.join(fig_dir, f"{args.prefix}_movie_latest.png")
        imgs[0].save(webp_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0, quality=88)
        imgs[0].save(gif_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0)
        shutil.copy2(frames[-1], latest_out)
        print(f"Rendered {rendered} new frame(s); {len(frames)} total frames -> {webp_out}, {gif_out}, {latest_out}")

    # Print key orbital motion diagnostics summary
    idx_d025 = np.where(bh_disp > 0.25)[0]
    t_d025 = float(t_tr[idx_d025[0]]) if len(idx_d025) else None
    print(
        json.dumps(
            {
                "t_max": t_max,
                "n_orbits": float((phi_orb[-1] - phi_orb[0]) / (2.0 * math.pi)),
                "R_geom_end": float(R_geom[-1]),
                "R_geom_min": float(np.min(R_geom[t_tr >= 25.0])),
                "R_om_end": float(R_om[-1]),
                "Omega_end": float(om_smooth[-1]),
                "bh_pos_end": [float(v) for v in x_bh[-1]],
                "bh_disp_end": float(bh_disp[-1]),
                "bh_disp_t400": float(np.interp(400.0, t_tr, bh_disp)) if t_max >= 400.0 else None,
                "bh_disp_t500": float(np.interp(500.0, t_tr, bh_disp)) if t_max >= 500.0 else None,
                "bh_disp_t600": float(np.interp(600.0, t_tr, bh_disp)) if t_max >= 600.0 else None,
                "t_bh_disp_0p25M": t_d025,
                "n_frames": len(frames),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
