#!/usr/bin/env python3
"""
Incremental pure-CPU live movie renderer for AGN Binary-EMRI ZKL full 3+1 NR runs.

Reads (using CUDA_VISIBLE_DEVICES=""):
  - <base>.traj.bin                 (records of 8 doubles: t, tag, x, y, z, ux, uy, uz)
  - bin/<base>.alpha_xy.NNNNN.bin   (AthenaK v1.1 AMR 2D lapse slice in z=0)
  - <base>.horizon_summary_0.txt    (SMBH apparent horizon mass/spin)
  - waveforms/rpsi4_real_0000.txt   (high-cadence dt=0.1 M Weyl waveform)
  - run_meta.json                   (configuration & 1PN scout reference parameters)

Produces cleanly in <run_dir>/:
  - movie_frames/frame_NNNNN.png
  - <base>.webp & <base>.gif
"""

import argparse
import glob
import json
import math
import os
import re
import struct
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Rectangle
import numpy as np
from PIL import Image

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
import pn_zkl_scout as scout


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
            x1min, x1max, x2min, x2max, x3min, x3max = struct.unpack(loc_fmt.replace("<", "<6"), coords_raw)
            data_bytes = len(var_list) * ncells * var_bytes
            raw = fp.read(data_bytes)
            if len(raw) < data_bytes:
                raise EOFError(f"Truncated block data in {path}")
            arr = np.frombuffer(raw, dtype=var_dtype).reshape(len(var_list), nx3, nx2, nx1).copy()
            blocks.append(((x1min, x1max, x2min, x2max, x3min, x3max), arr))
    return t, var_list, blocks


def rasterize_xy_slice(blocks, var_idx, xlim, ylim, ngrid=320):
    img = np.full((ngrid, ngrid), np.nan, dtype=np.float64)
    gx = np.linspace(xlim[0], xlim[1], ngrid)
    gy = np.linspace(ylim[0], ylim[1], ngrid)
    for (x1min, x1max, x2min, x2max, _, _), arr in blocks:
        if x1max < xlim[0] or x1min > xlim[1] or x2max < ylim[0] or x2min > ylim[1]:
            continue
        plane = arr[var_idx, 0, :, :]
        ny, nx = plane.shape
        ix0 = max(0, int(np.searchsorted(gx, x1min, side="left")))
        ix1 = min(ngrid, int(np.searchsorted(gx, x1max, side="right")))
        iy0 = max(0, int(np.searchsorted(gy, x2min, side="left")))
        iy1 = min(ngrid, int(np.searchsorted(gy, x2max, side="right")))
        if ix1 <= ix0 or iy1 <= iy0:
            continue
        xi = np.clip(((gx[ix0:ix1] - x1min) / max(x1max - x1min, 1e-12) * nx).astype(int), 0, nx - 1)
        yi = np.clip(((gy[iy0:iy1] - x2min) / max(x2max - x2min, 1e-12) * ny).astype(int), 0, ny - 1)
        img[iy0:iy1, ix0:ix1] = plane[np.ix_(yi, xi)]
    return gx, gy, img


def read_traj_binary(path):
    """Read <base>.traj.bin (8 float64 per record: t, tag, x, y, z, ux, uy, uz)."""
    sz = os.path.getsize(path)
    nrec = sz // 64
    if nrec <= 0:
        return None
    raw = np.fromfile(path, dtype="<f8", count=nrec * 8).reshape(nrec, 8)
    m0 = raw[:, 1] == 0.0
    m1 = raw[:, 1] == 1.0
    t = raw[m0, 0]
    p0 = raw[m0, 2:5]
    u0 = raw[m0, 5:8]
    p1 = raw[m1, 2:5]
    u1 = raw[m1, 5:8]
    n = min(len(t), len(p0), len(p1))
    return t[:n], p0[:n], u0[:n], p1[:n], u1[:n]


def nr_osculating_elements(t, x0, u0, x1, u1, m0, m1, m2):
    """
    Invert centered coordinate trajectories into local Fermi-normal Keplerian (e_in, inc_deg, r_prop).
    """
    m_bin = m1 + m2
    n = len(t)
    e_arr = np.zeros(n)
    i_arr = np.zeros(n)
    r_arr = np.zeros(n)
    if n < 2:
        return e_arr, i_arr, r_arr

    v0_all = np.gradient(x0, t, axis=0)
    v1_all = np.gradient(x1, t, axis=0)

    for k in range(n):
        x_cm = (m1 * x0[k] + m2 * x1[k]) / m_bin
        v_cm = (m1 * v0_all[k] + m2 * v1_all[k]) / m_bin
        r_out = max(float(np.linalg.norm(x_cm)), 1e-6)
        psi_cm = 1.0 + m0 / (2.0 * r_out)
        alp_cm = psi_cm ** (-2)
        v_orth_cm = (psi_cm ** 2 / alp_cm) * v_cm
        vb2 = min(float(np.dot(v_orth_cm, v_orth_cm)), 0.85)
        W = 1.0 / math.sqrt(max(1.0 - vb2, 1e-12))

        dx_iso = x1[k] - x0[k]
        dv_iso = v1_all[k] - v0_all[k]
        if vb2 > 1e-16:
            vhat = v_orth_cm / math.sqrt(vb2)
            dx_prop = (psi_cm ** 2) * (dx_iso + (W - 1.0) * float(np.dot(dx_iso, vhat)) * vhat)
            dv_prop = (W / alp_cm) * (psi_cm ** 2) * (dv_iso + (W - 1.0) * float(np.dot(dv_iso, vhat)) * vhat)
        else:
            dx_prop = (psi_cm ** 2) * dx_iso
            dv_prop = (W / alp_cm) * (psi_cm ** 2) * dv_iso

        r = float(np.linalg.norm(dx_prop))
        h_in = np.cross(dx_prop, dv_prop)
        e_vec = np.cross(dv_prop, h_in) / m_bin - dx_prop / max(r, 1e-12)
        h_out = np.cross(x_cm, v_orth_cm)
        cos_i = float(np.dot(h_in, h_out)) / max(float(np.linalg.norm(h_in) * np.linalg.norm(h_out)), 1e-30)
        e_arr[k] = float(np.linalg.norm(e_vec))
        i_arr[k] = float(np.degrees(np.arccos(max(-1.0, min(1.0, cos_i)))))
        r_arr[k] = r
    return e_arr, i_arr, r_arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    with open(os.path.join(run_dir, "run_meta.json"), "r") as f:
        meta = json.load(f)
    cfg = meta["cfg"]
    base = cfg["name"]

    traj = read_traj_binary(os.path.join(run_dir, f"{base}.traj.bin"))
    if traj is None:
        print("No trajectory records yet.")
        return
    t_tr, x0_tr, u0_tr, x1_tr, u1_tr = traj
    if len(t_tr) > 1:
        keep = np.concatenate([[True], np.diff(t_tr) > 1e-12])
        t_tr, x0_tr, u0_tr, x1_tr, u1_tr = t_tr[keep], x0_tr[keep], u0_tr[keep], x1_tr[keep], u1_tr[keep]
    e_nr, i_nr, r_nr = nr_osculating_elements(
        t_tr, x0_tr, u0_tr, x1_tr, u1_tr, 1.0, cfg["m1"], cfg["m2"]
    )
    t_max = max(float(t_tr[-1]), 10.0)

    # Compute 1PN+1.5PN secular reference curve over [0, t_max] (stride nicely if short)
    pn_ref = scout.integrate_case(
        1.0, cfg["m1"], cfg["m2"], cfg["a_out"], cfg["a_in"],
        cfg["e0"], cfg["inc"], cfg["chi0"], t_end=t_max, dt=0.10
    )

    # Read high-cadence rPsi4 waveform if present
    wf_files = sorted(glob.glob(os.path.join(run_dir, "waveforms", "rpsi4_real_*.txt")))
    wf_t, wf_22 = np.array([0.0]), np.array([0.0])
    if wf_files:
        try:
            wf_dat = np.loadtxt(wf_files[0], comments="#")
            if wf_dat.ndim == 2 and len(wf_dat) > 1:
                wf_t = wf_dat[:, 0]
                # col 1 is usually l=2, m=-2..2; pick column with max RMS after initial junk
                wf_22 = wf_dat[:, min(5, wf_dat.shape[1] - 1)]
        except Exception:
            pass

    # Horizon summary
    hs_path = os.path.join(run_dir, f"{base}.horizon_summary_0.txt")
    hs_t, hs_m, hs_rmin = np.array([0.0]), np.array([1.0]), np.array([0.5])
    if os.path.isfile(hs_path):
        try:
            hs = np.loadtxt(hs_path, comments="#")
            if hs.ndim == 2 and len(hs) > 0:
                hs_t, hs_m, hs_rmin = hs[:, 1], hs[:, 2], hs[:, 11]
        except Exception:
            pass

    slice_paths = sorted(glob.glob(os.path.join(run_dir, "bin", f"{base}.alpha_xy.*.bin")))
    frame_dir = os.path.join(run_dir, "movie_frames")
    os.makedirs(frame_dir, exist_ok=True)
    cz.use_style()

    rendered = 0
    for idx_s, sp in enumerate(slice_paths):
        m_num = re.search(r"\.(\d{5})\.bin$", sp)
        if not m_num:
            continue
        out_png = os.path.join(frame_dir, f"frame_{m_num.group(1)}.png")
        if os.path.isfile(out_png) and not args.overwrite:
            continue
        try:
            t_s, vlist, blocks = read_athenak_bin(sp)
            va_i = vlist.index("z4c_alpha") if "z4c_alpha" in vlist else 0
            gx, gy, alpha_img = rasterize_xy_slice(blocks, va_i, (-18.0, 18.0), (-18.0, 18.0), ngrid=320)
        except (EOFError, OSError, ValueError):
            continue

        k_cur = int(np.searchsorted(t_tr, t_s, side="right")) - 1
        k_cur = max(0, min(k_cur, len(t_tr) - 1))
        m_bin = cfg["m1"] + cfg["m2"]
        x_cm_all = (cfg["m1"] * x0_tr[:k_cur+1] + cfg["m2"] * x1_tr[:k_cur+1]) / m_bin

        fig = plt.figure(figsize=(11.0, 8.6))
        gs = GridSpec(2, 2, figure=fig, left=0.075, right=0.96, bottom=0.075, top=0.90, wspace=0.26, hspace=0.30)

        # Panel 1: Global lapse & outer orbit
        ax0 = fig.add_subplot(gs[0, 0])
        ax0.pcolormesh(gx, gy, alpha_img, cmap="viridis", vmin=0.35, vmax=1.0, shading="auto", rasterized=True)
        if meta.get("mesh_preset") == "amr_dyn":
            for (bx0, bx1, by0, by1, _, _), _ in blocks:
                bw, bh = bx1 - bx0, by1 - by0
                if bw <= 2.1 and bx1 >= -18.0 and bx0 <= 18.0 and by1 >= -18.0 and by0 <= 18.0:
                    ax0.add_patch(Rectangle(
                        (bx0, by0), bw, bh, fill=False, ec="cyan",
                        lw=0.35 if bw > 0.6 else 0.50, alpha=0.38 if bw > 0.6 else 0.55, zorder=4
                    ))
        ah_idx = max(0, int(np.searchsorted(hs_t, t_s, side="right")) - 1) if len(hs_t) else 0
        r_ah_now = float(hs_rmin[ah_idx]) if len(hs_rmin) else 0.5
        ax0.add_patch(Circle((0.0, 0.0), r_ah_now, color="k", ec="w", lw=1.0, zorder=5))
        ax0.plot(x_cm_all[:, 0], x_cm_all[:, 1], color="w", lw=1.0, alpha=0.75)
        ax0.scatter([x0_tr[k_cur, 0], x1_tr[k_cur, 0]], [x0_tr[k_cur, 1], x1_tr[k_cur, 1]],
                    s=[34, 24], c=[cz.PAL["red"], cz.PAL["blue"]], edgecolors="w", linewidths=0.7, zorder=6)
        ax0.set_aspect("equal")
        ax0.set_xlim(-18.0, 18.0); ax0.set_ylim(-18.0, 18.0)
        ax0.set_xlabel(r"$x\,[M]$"); ax0.set_ylabel(r"$y\,[M]$")
        ax0.set_title(r"Global lapse $\alpha(x,y)$ & outer orbit")

        # Panel 2: Comoving inner binary zoom
        ax1 = fig.add_subplot(gs[0, 1])
        win_start = int(np.searchsorted(t_tr, max(0.0, t_s - max(float(cfg.get("p_in", 50.0)), 30.0)), side="left"))
        win_start = min(win_start, k_cur)
        d0 = x0_tr[win_start:k_cur+1] - x_cm_all[win_start:k_cur+1]
        d1 = x1_tr[win_start:k_cur+1] - x_cm_all[win_start:k_cur+1]
        ax1.plot(d0[:, 0], d0[:, 1], color=cz.PAL["red"], lw=1.2, alpha=0.8, label=r"$m_1$ $(x\text{–}y)$")
        ax1.plot(d1[:, 0], d1[:, 1], color=cz.PAL["blue"], lw=1.2, alpha=0.8, label=r"$m_2$ $(x\text{–}y)$")
        ax1.scatter([d0[-1, 0], d1[-1, 0]], [d0[-1, 1], d1[-1, 1]], s=[45, 34], c=[cz.PAL["red"], cz.PAL["blue"]], zorder=5)
        max_r_win = float(max(np.max(np.linalg.norm(d0[:, :2], axis=1)), np.max(np.linalg.norm(d1[:, :2], axis=1))))
        lim = min(max(1.25 * cfg["a_in"], 1.0), max(1.6 * max_r_win, 0.08))
        ax1.set_aspect("equal")
        ax1.set_xlim(-lim, lim); ax1.set_ylim(-lim, lim)
        ax1.set_xlabel(r"$\Delta x_{\rm com}\,[M]$"); ax1.set_ylabel(r"$\Delta y_{\rm com}\,[M]$")
        ax1.legend(loc="upper right", fontsize=8.0, frameon=False)
        ax1.set_title(rf"Comoving binary ($r_{{12}}={r_nr[k_cur]:.3f}\,M$, $I={i_nr[k_cur]:.1f}^\circ$)")

        # Panel 3: Full-NR vs 1PN scout eccentricity & inclination
        ax2 = fig.add_subplot(gs[1, 0])
        pn_m = pn_ref["t"] <= t_s + 1e-6
        ax2.plot(pn_ref["t"][pn_m], pn_ref["e_in"][pn_m], color="k", ls="--", lw=1.2, label="1PN+1.5PN scout")
        ax2.plot(t_tr[:k_cur+1], e_nr[:k_cur+1], color=cz.PAL["red"], lw=1.6, label="Full 3+1 NR")
        ax2.set_xlim(0.0, max(t_s, 10.0)); ax2.set_ylim(0.0, max(0.35, float(np.max(e_nr[:k_cur+1])) * 1.25))
        ax2.set_xlabel(r"Time $t\,[M]$"); ax2.set_ylabel(r"Inner eccentricity $e_{\rm in}$")
        ax2.legend(loc="upper left", fontsize=8.5, frameon=False)
        ax2.set_title("Inner eccentricity: Full NR vs 1PN baseline")

        # Panel 4: High-cadence (dt=0.1 M) rPsi4 waveform
        ax3 = fig.add_subplot(gs[1, 1])
        w_m = wf_t <= t_s + 1e-6
        if np.any(w_m):
            ax3.plot(wf_t[w_m], 1e4 * wf_22[w_m], color=cz.PAL["blue"], lw=1.1)
        ax3.set_xlim(0.0, max(t_s, 10.0))
        ax3.set_xlabel(r"Time $t\,[M]$"); ax3.set_ylabel(r"$10^4\,r\Psi_4\,(r=22\,M)$")
        mah_now = float(hs_m[np.searchsorted(hs_t, t_s, side="right") - 1]) if len(hs_t) else 1.0
        ax3.set_title(rf"GW readout ($\Delta t_\Psi = 0.1\,M$, $M_{{\rm AH}}={mah_now:.4f}\,M$)")

        for ax in (ax0, ax1, ax2, ax3):
            ax.tick_params(which="both", direction="in", top=True, right=True)

        fig.suptitle(
            rf"{base} (Full 3+1 NR, $\chi_0={cfg['chi0']:+.1f}$, $I_0={cfg['inc']:.0f}^\circ$, $\epsilon_{{\rm GR}}={cfg['eps_gr']:.2f}$)   $t = {t_s:.2f}\,M$",
            fontsize=12.5, y=0.96
        )
        fig.savefig(out_png, dpi=180)
        plt.close(fig)
        rendered += 1

    frames = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
    if frames:
        imgs = [Image.open(p).convert("RGB") for p in frames]
        dur_ms = int(round(1000.0 / max(args.fps, 1)))
        webp_out = os.path.join(run_dir, f"{base}.webp")
        gif_out = os.path.join(run_dir, f"{base}.gif")
        imgs[0].save(webp_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0, quality=88)
        imgs[0].save(gif_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0)
        print(f"Rendered {rendered} new frame(s); {len(frames)} total frames in {frame_dir}")
        print(f"Wrote {webp_out} and {gif_out}")


if __name__ == "__main__":
    main()
