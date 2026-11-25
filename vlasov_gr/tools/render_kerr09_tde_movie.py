#!/usr/bin/env python3
"""
Incremental pure-CPU movie renderer for the 1M-particle Kerr 0.90 cloud disruption run.

Reads:
  - <base>.vlasov.NNNNN.bin   (GRLBV001 particle snapshots)
  - bin/<base>.{alpha_xy,E_xy,alpha_xz,E_xz}.NNNNN.bin  (AthenaK v1.1 AMR 2D slices)
  - <base>.horizon_summary_0.txt, <base>.co_0.txt, <base>.vlasov.hst
  - waveforms/rpsi4_real_NNNN.txt

Produces:
  - <out_dir>/frame_NNNNN.png (skips existing frames unless --overwrite; skips in-flight files safely)
  - <run_dir>/<basename>.webp (24-bit animated WebP via PIL)
  - <run_dir>/<basename>.gif  (animated GIF via PIL)
  - <run_dir>/<basename>.mp4  (if ffmpeg is found on PATH)
"""

import argparse
import glob
import os
import re
import shutil
import struct
import subprocess
import sys

# Ensure pure-CPU execution even on GPU nodes running the simulation
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.patches import Circle
import numpy as np
from PIL import Image

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz


def read_grlbv(path):
    """Read a GRLBV001 particle snapshot cleanly; raises ValueError/EOFError on incomplete writes."""
    fsize = os.path.getsize(path)
    if fsize < 32:
        raise EOFError(f"Snapshot too small ({fsize} bytes): {path}")
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"GRLBV001":
            raise ValueError(f"Unexpected magic {magic!r} in {path}")
        N, Nb = struct.unpack("<qq", f.read(16))
        t = struct.unpack("<d", f.read(8))[0]
        # Packet layout: 3N f64 (x) + N i32 (sp) + N*Nb f64 (m) + 3*N*Nb f64 (u) + 6*N*Nb f64 (s)
        expected = 32 + 8 * 3 * N + 4 * N + 8 * N * Nb + 8 * 3 * N * Nb + 8 * 6 * N * Nb
        if fsize < expected:
            raise EOFError(f"Incomplete snapshot {path}: {fsize} < {expected}")
        x = np.frombuffer(f.read(8 * 3 * N), np.float64).reshape(N, 3).copy()
        _sp = np.frombuffer(f.read(4 * N), np.int32).copy()
        m_all = np.frombuffer(f.read(8 * N * Nb), np.float64).reshape(N, Nb).copy()
        m = m_all[:, 0] if Nb == 1 else m_all.sum(axis=1)
        u = np.frombuffer(f.read(8 * 3 * N * Nb), np.float64).reshape(N, Nb, 3)[:, 0, :].copy()
    return float(t), x, u, m


def read_athenak_bin(path):
    """Pure-NumPy reader for AthenaK binary output v1.1 (no h5py dependency)."""
    fsize = os.path.getsize(path)
    if fsize < 64:
        raise EOFError(f"Binary slice too small: {path}")
    with open(path, "rb") as fp:
        code_header = fp.readline().split()
        if not code_header or code_header[0] != b"Athena":
            raise ValueError(f"Not an Athena binary file: {path}")
        version = code_header[-1].split(b"=")[-1]
        if version != b"1.1":
            raise ValueError(f"Unsupported Athena binary version {version!r} in {path}")

        pheader_count = int(fp.readline().split(b"=")[-1])
        pheader = {}
        for _ in range(pheader_count - 1):
            line = fp.readline().decode("utf-8", errors="replace")
            if "=" not in line:
                raise EOFError(f"Truncated preheader in {path}")
            key, val = [s.strip() for s in line.split("=", 1)]
            pheader[key] = val

        t = float(pheader["time"])
        cycle = int(pheader["cycle"])
        locsizebytes = int(pheader["size of location"])
        varsizebytes = int(pheader["size of variable"])

        _nvars = int(fp.readline().split(b"=")[-1])
        var_list = [v.decode("utf-8") for v in fp.readline().split()[1:]]
        header_size = int(fp.readline().split(b"=")[-1])
        hdr_bytes = fp.read(header_size)
        if len(hdr_bytes) < header_size:
            raise EOFError(f"Truncated parameter header in {path}")

        loc_dtype = np.float64 if locsizebytes == 8 else np.float32
        var_dtype = np.float64 if varsizebytes == 8 else np.float32
        n_vars = len(var_list)

        blocks = []
        while fp.tell() < fsize:
            idx_bytes = fp.read(24)
            if len(idx_bytes) < 24:
                raise EOFError(f"Truncated block index in {path}")
            idx = np.frombuffer(idx_bytes, dtype=np.int32).astype(np.int64)
            nx1_out = int(idx[1] - idx[0] + 1)
            nx2_out = int(idx[3] - idx[2] + 1)
            nx3_out = int(idx[5] - idx[4] + 1)

            log_bytes = fp.read(16)
            geom_bytes = fp.read(6 * locsizebytes)
            if len(log_bytes) < 16 or len(geom_bytes) < 6 * locsizebytes:
                raise EOFError(f"Truncated block metadata in {path}")
            mb_log = np.frombuffer(log_bytes, dtype=np.int32).copy()
            mb_geom = np.frombuffer(geom_bytes, dtype=loc_dtype).astype(np.float64).copy()

            count = nx1_out * nx2_out * nx3_out * n_vars
            arr = np.fromfile(fp, dtype=var_dtype, count=count)
            if arr.size != count:
                raise EOFError(f"Truncated block data in {path}: {arr.size} != {count}")
            arr = arr.reshape(n_vars, nx3_out, nx2_out, nx1_out).astype(np.float64)
            blocks.append((int(mb_log[3]), mb_geom, arr))

    return {
        "time": t,
        "cycle": cycle,
        "var_names": var_list,
        "blocks": blocks,
    }


def rasterize_slice(bindata, var_idx, plane, u_bounds, v_bounds, nu=384, nv=384, fill=np.nan):
    """
    Rasterize a 2D AthenaK AMR slice onto a uniform grid [u0, u1] x [v0, v1].
    plane='xy': u=x1, v=x2 (slices across x3, nx3_out=1).
    plane='xz': u=x1, v=x3 (slices across x2, nx2_out=1).
    Coarser blocks are painted first so finer levels cleanly overwrite them.
    """
    u0, u1 = u_bounds
    v0, v1 = v_bounds
    grid = np.full((nv, nu), fill, dtype=np.float64)
    du = (u1 - u0) / nu
    dv = (v1 - v0) / nv
    u_cent = u0 + (np.arange(nu) + 0.5) * du
    v_cent = v0 + (np.arange(nv) + 0.5) * dv

    sorted_blocks = sorted(bindata["blocks"], key=lambda item: item[0])
    for _lvl, geom, arr in sorted_blocks:
        bx1_0, bx1_1, bx2_0, bx2_1, bx3_0, bx3_1 = geom
        data3d = arr[var_idx]
        if plane == "xy":
            b_u0, b_u1 = bx1_0, bx1_1
            b_v0, b_v1 = bx2_0, bx2_1
            patch = data3d[0, :, :]  # shape (ny, nx)
        elif plane == "xz":
            b_u0, b_u1 = bx1_0, bx1_1
            b_v0, b_v1 = bx3_0, bx3_1
            patch = data3d[:, 0, :]  # shape (nz, nx)
        else:
            raise ValueError(f"Unsupported slice plane {plane!r}")

        if b_u1 <= u0 or b_u0 >= u1 or b_v1 <= v0 or b_v0 >= v1:
            continue

        pnv, pnu = patch.shape
        iu_mask = (u_cent >= b_u0) & (u_cent < b_u1)
        iv_mask = (v_cent >= b_v0) & (v_cent < b_v1)
        if not np.any(iu_mask) or not np.any(iv_mask):
            continue

        iu_idx = np.nonzero(iu_mask)[0]
        iv_idx = np.nonzero(iv_mask)[0]
        pu = np.clip(np.floor((u_cent[iu_idx] - b_u0) / (b_u1 - b_u0) * pnu).astype(int), 0, pnu - 1)
        pv = np.clip(np.floor((v_cent[iv_idx] - b_v0) / (b_v1 - b_v0) * pnv).astype(int), 0, pnv - 1)
        grid[np.ix_(iv_idx, iu_idx)] = patch[np.ix_(pv, pu)]

    return u_cent, v_cent, grid


def index_slice_files(bin_dir, basename, slice_id):
    """Return sorted list of (time, filepath) for readable binary slices of given slice_id."""
    pattern = os.path.join(bin_dir, f"{basename}.{slice_id}.*.bin")
    items = []
    for p in sorted(glob.glob(pattern)):
        try:
            d = read_athenak_bin(p)
            items.append((d["time"], p))
        except Exception:
            continue
    items.sort(key=lambda x: x[0])
    return items


def find_nearest_slice(items, target_t):
    """Return filepath in items closest in time to target_t, or None."""
    if not items:
        return None
    times = np.array([it[0] for it in items])
    idx = int(np.argmin(np.abs(times - target_t)))
    return items[idx][1]


def safe_loadtxt(path):
    """Load whitespace/tab numeric table, safely dropping any partial last line during live writes."""
    if not path or not os.path.isfile(path):
        return None
    rows = []
    with open(path, "r") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                vals = [float(tok) for tok in s.split()]
            except ValueError:
                continue
            if rows and len(vals) != len(rows[0]):
                continue
            rows.append(vals)
    if not rows:
        return None
    arr = np.asarray(rows, dtype=np.float64)
    return arr


def dedup_sort(t_arr, *cols):
    """Sort by time and keep the latest record for duplicate timestamps (e.g. after restarts)."""
    if t_arr is None or len(t_arr) == 0:
        return (t_arr,) + cols
    # Iterate in reverse so the latest entry wins on ties, then reverse back
    seen = {}
    for i in range(len(t_arr)):
        seen[round(float(t_arr[i]), 12)] = i
    idx = sorted(seen.values(), key=lambda i: t_arr[i])
    idx = np.asarray(idx, dtype=np.int64)
    return (t_arr[idx],) + tuple(c[idx] for c in cols)


def load_waveform_22(wf_dir):
    """Load innermost rpsi4_real_NNNN.txt and extract (t, r*Re(Psi4^{22}))."""
    if not os.path.isdir(wf_dir):
        return None, None, None
    cands = sorted(glob.glob(os.path.join(wf_dir, "rpsi4_real_*.txt")))
    if not cands:
        return None, None, None
    wf_path = cands[0]  # zero-padded ascending radius -> innermost first
    m_rad = re.search(r"rpsi4_real_(\d+)\.txt$", os.path.basename(wf_path))
    rad_val = int(m_rad.group(1)) if m_rad else None

    col22 = 5
    with open(wf_path, "r") as f:
        for line in f:
            if line.startswith("#"):
                toks = line.lstrip("#").strip().split()
                for idx, tok in enumerate(toks):
                    if tok.endswith(":22"):
                        col22 = idx
                break
    arr = safe_loadtxt(wf_path)
    if arr is None or arr.shape[1] <= col22:
        return None, None, rad_val
    return arr[:, 0], arr[:, col22], rad_val


def load_diagnostics(run_dir, basename):
    """Load horizon summary, BH tracker, Vlasov history, and waveforms."""
    diag = {}
    ah = safe_loadtxt(os.path.join(run_dir, f"{basename}.horizon_summary_0.txt"))
    if ah is not None and ah.shape[1] >= 12:
        t_ah, m_ah, s_ah, r_ah = dedup_sort(ah[:, 1], ah[:, 2], ah[:, 6], ah[:, 10])
        chi_ah = np.where(m_ah > 0, s_ah / (m_ah ** 2), 0.0)
        diag["ah"] = (t_ah, m_ah, chi_ah, r_ah)
    else:
        diag["ah"] = None

    co = safe_loadtxt(os.path.join(run_dir, f"{basename}.co_0.txt"))
    if co is not None and co.shape[1] >= 5:
        diag["co"] = dedup_sort(co[:, 1], co[:, 2], co[:, 3], co[:, 4])
    else:
        diag["co"] = None

    vl = safe_loadtxt(os.path.join(run_dir, f"{basename}.vlasov.hst"))
    if vl is not None and vl.shape[1] >= 4:
        tv, nact, mtot = dedup_sort(vl[:, 0], vl[:, 2], vl[:, 3])
        n0 = max(nact[0], 1.0)
        diag["vl"] = (tv, nact / n0, mtot)
    else:
        diag["vl"] = None

    t_wf, psi22, rad_wf = load_waveform_22(os.path.join(run_dir, "waveforms"))
    if t_wf is not None:
        t_wf, psi22 = dedup_sort(t_wf, psi22)
        diag["wf"] = (t_wf, psi22, rad_wf)
    else:
        diag["wf"] = None
    return diag


def interp_scalar(t_arr, v_arr, t_cur, default=0.0):
    if t_arr is None or len(t_arr) == 0:
        return default
    if t_cur <= t_arr[0]:
        return float(v_arr[0])
    if t_cur >= t_arr[-1]:
        return float(v_arr[-1])
    return float(np.interp(t_cur, t_arr, v_arr))


def render_frame(snap_path, slice_maps, diag, out_png, half_wide=14.0, half_zoom=4.5, dpi=150):
    """Render one 4-panel dashboard PNG."""
    t, x, _u, m = read_grlbv(snap_path)
    valid = np.isfinite(x).all(axis=1) & np.isfinite(m) & (m > 0.0)
    xv = x[valid]
    mv = m[valid]

    # BH state at time t
    if diag["co"] is not None:
        tc, xbc, ybc, zbc = diag["co"]
        xb = interp_scalar(tc, xbc, t, 0.0)
        yb = interp_scalar(tc, ybc, t, 0.0)
        zb = interp_scalar(tc, zbc, t, 0.0)
        trail_mask = tc <= t + 1e-12
        trail_x, trail_y, trail_z = xbc[trail_mask], ybc[trail_mask], zbc[trail_mask]
    else:
        xb = yb = zb = 0.0
        trail_x = trail_y = trail_z = np.array([0.0])

    if diag["ah"] is not None:
        ta, ma_arr, chia_arr, ra_arr = diag["ah"]
        mah = interp_scalar(ta, ma_arr, t, 1.0)
        chiah = interp_scalar(ta, chia_arr, t, 0.9)
        rah = interp_scalar(ta, ra_arr, t, 0.228)
    else:
        mah, chiah, rah = 1.0, 0.9, 0.228

    # Column-density maps
    nbins = 280
    dx_bin = (2.0 * half_wide) / nbins
    h_xy, _, _ = np.histogram2d(
        xv[:, 0], xv[:, 1], bins=nbins,
        range=[[-half_wide, half_wide], [-half_wide, half_wide]], weights=mv
    )
    h_xz, _, _ = np.histogram2d(
        xv[:, 0], xv[:, 2], bins=nbins,
        range=[[-half_wide, half_wide], [-half_wide, half_wide]], weights=mv
    )
    sig_xy = np.maximum(h_xy.T / (dx_bin ** 2), 1e-10)
    sig_xz = np.maximum(h_xz.T / (dx_bin ** 2), 1e-10)

    # Slices
    alp_xy_p = find_nearest_slice(slice_maps["alpha_xy"], t)
    alp_xz_p = find_nearest_slice(slice_maps["alpha_xz"], t)
    e_xy_p = find_nearest_slice(slice_maps["E_xy"], t)

    alp_xy_grid = None
    if alp_xy_p is not None:
        d = read_athenak_bin(alp_xy_p)
        ax_u, ax_v, alp_xy_grid = rasterize_slice(
            d, 0, "xy", (-half_wide, half_wide), (-half_wide, half_wide), nu=320, nv=320, fill=np.nan
        )
        zx_u, zx_v, alp_zoom = rasterize_slice(
            d, 0, "xy", (xb - half_zoom, xb + half_zoom), (yb - half_zoom, yb + half_zoom),
            nu=320, nv=320, fill=np.nan
        )
    else:
        alp_zoom = None

    alp_xz_grid = None
    if alp_xz_p is not None:
        d = read_athenak_bin(alp_xz_p)
        axz_u, axz_v, alp_xz_grid = rasterize_slice(
            d, 0, "xz", (-half_wide, half_wide), (-half_wide, half_wide), nu=320, nv=320, fill=np.nan
        )

    e_zoom = None
    if e_xy_p is not None:
        d = read_athenak_bin(e_xy_p)
        eu, ev, e_zoom_raw = rasterize_slice(
            d, 0, "xy", (xb - half_zoom, xb + half_zoom), (yb - half_zoom, yb + half_zoom),
            nu=360, nv=360, fill=0.0
        )
        e_zoom = np.maximum(np.nan_to_num(e_zoom_raw, nan=0.0), 1e-12)

    # Set up Cyclic-Zoom style figure
    cz.use_style()
    cmap_dens = cz.truncate_cmap("magma", 0.16, 1.0)
    cmap_dens.set_bad("#140924")
    norm_sig = LogNorm(vmin=2.0e-6, vmax=3.0e-2)
    norm_e = LogNorm(vmin=3.0e-7, vmax=1.5e-2)

    fig = plt.figure(figsize=(10.8, 8.8))
    gs = GridSpec(2, 2, figure=fig, left=0.068, right=0.925, bottom=0.068, top=0.925,
                  wspace=0.33, hspace=0.25)

    fig.suptitle(
        rf"Kerr $\chi_0={0.90:.2f}$ + $10^6$ Massive Cloud ($M_{{\rm cl}}=0.05\,M$)"
        rf"$\quad t = {t:.2f}\,M,\; M_{{\rm AH}} = {mah:.4f}\,M,\; \chi_{{\rm AH}} = {chiah:.4f}$",
        fontsize=11.5, y=0.97
    )

    # 1. Top-left: Equatorial x-y column density
    ax0 = fig.add_subplot(gs[0, 0])
    im0 = ax0.imshow(
        sig_xy, origin="lower", extent=[-half_wide, half_wide, -half_wide, half_wide],
        cmap=cmap_dens, norm=norm_sig, aspect="equal", interpolation="nearest"
    )
    if alp_xy_grid is not None and np.any(np.isfinite(alp_xy_grid)):
        lvls = [l for l in (0.3, 0.5, 0.7, 0.85) if np.nanmin(alp_xy_grid) < l < np.nanmax(alp_xy_grid)]
        if lvls:
            ax0.contour(ax_u, ax_v, alp_xy_grid, levels=lvls, colors="white", linewidths=0.75, alpha=0.55)
    if len(trail_x) > 1:
        ax0.plot(trail_x, trail_y, color="#0496FF", lw=1.0, alpha=0.85)
    ax0.add_patch(Circle((xb, yb), max(rah, 0.22), fc="black", ec="white", lw=1.0, zorder=6))
    ax0.set_xlim(-half_wide, half_wide)
    ax0.set_ylim(-half_wide, half_wide)
    ax0.set_title(r"Equatorial density $\Sigma_{xy}$", fontsize=11, pad=5)
    ax0.set_xlabel(r"$x\,[M]$", labelpad=2)
    ax0.set_ylabel(r"$y\,[M]$")
    ax0.tick_params(which="both", direction="in", top=True, right=True, color="white")
    cz.side_colorbar(fig, ax0, im0, r"$\Sigma_{xy}\,[M^{-1}]$", size="4.2%", pad=0.05)

    # 2. Top-right: Meridional x-z column density
    ax1 = fig.add_subplot(gs[0, 1])
    im1 = ax1.imshow(
        sig_xz, origin="lower", extent=[-half_wide, half_wide, -half_wide, half_wide],
        cmap=cmap_dens, norm=norm_sig, aspect="equal", interpolation="nearest"
    )
    if alp_xz_grid is not None and np.any(np.isfinite(alp_xz_grid)):
        lvls = [l for l in (0.3, 0.5, 0.7, 0.85) if np.nanmin(alp_xz_grid) < l < np.nanmax(alp_xz_grid)]
        if lvls:
            ax1.contour(axz_u, axz_v, alp_xz_grid, levels=lvls, colors="white", linewidths=0.75, alpha=0.55)
    if len(trail_x) > 1:
        ax1.plot(trail_x, trail_z, color="#0496FF", lw=1.0, alpha=0.85)
    ax1.add_patch(Circle((xb, zb), max(rah, 0.22), fc="black", ec="white", lw=1.0, zorder=6))
    ax1.set_xlim(-half_wide, half_wide)
    ax1.set_ylim(-half_wide, half_wide)
    ax1.set_title(r"Meridional density $\Sigma_{xz}$ ($i=20^\circ$)", fontsize=11, pad=5)
    ax1.set_xlabel(r"$x\,[M]$", labelpad=2)
    ax1.set_ylabel(r"$z\,[M]$")
    ax1.tick_params(which="both", direction="in", top=True, right=True, color="white")
    cz.side_colorbar(fig, ax1, im1, r"$\Sigma_{xz}\,[M^{-1}]$", size="4.2%", pad=0.05)

    # 3. Bottom-left: Near-horizon zoom E_xy (tmunu_E)
    ax2 = fig.add_subplot(gs[1, 0])
    if e_zoom is not None:
        im2 = ax2.imshow(
            e_zoom, origin="lower",
            extent=[xb - half_zoom, xb + half_zoom, yb - half_zoom, yb + half_zoom],
            cmap=cmap_dens, norm=norm_e, aspect="equal", interpolation="nearest"
        )
    else:
        im2 = ax2.imshow(
            np.full((32, 32), 1e-12), origin="lower",
            extent=[xb - half_zoom, xb + half_zoom, yb - half_zoom, yb + half_zoom],
            cmap=cmap_dens, norm=norm_e, aspect="equal"
        )
    if alp_zoom is not None and np.any(np.isfinite(alp_zoom)):
        lvls = [l for l in (0.35, 0.5, 0.7) if np.nanmin(alp_zoom) < l < np.nanmax(alp_zoom)]
        if lvls:
            cs2 = ax2.contour(zx_u, zx_v, alp_zoom, levels=lvls, colors="white", linewidths=0.85, alpha=0.75)
            ax2.clabel(cs2, fmt="%.2f", fontsize=7.5, inline=True)
    ax2.add_patch(Circle((xb, yb), rah, fc="black", ec="white", lw=1.2, zorder=6))
    ax2.set_xlim(xb - half_zoom, xb + half_zoom)
    ax2.set_ylim(yb - half_zoom, yb + half_zoom)
    ax2.set_title(r"Horizon zoom: ADM energy density $E(x,y)$", fontsize=11, pad=5)
    ax2.set_xlabel(r"$x\,[M]$", labelpad=2)
    ax2.set_ylabel(r"$y\,[M]$")
    ax2.tick_params(which="both", direction="in", top=True, right=True, color="white")
    cz.side_colorbar(fig, ax2, im2, r"$E_{\rm ADM}\,[M^{-2}]$", size="4.2%", pad=0.05)

    # 4. Bottom-right: 3-strip live physics diagnostics
    sub_gs = GridSpecFromSubplotSpec(3, 1, subplot_spec=gs[1, 1], hspace=0.14)
    sax0 = fig.add_subplot(sub_gs[0])
    sax1 = fig.add_subplot(sub_gs[1], sharex=sax0)
    sax2 = fig.add_subplot(sub_gs[2], sharex=sax0)

    # Time range across available diagnostics
    t_max_all = max(t, 1.0)
    for key in ("ah", "vl", "wf"):
        if diag[key] is not None and len(diag[key][0]) > 0:
            t_max_all = max(t_max_all, float(diag[key][0][-1]))

    # Strip 0: chi_AH & M_AH
    if diag["ah"] is not None:
        ta, ma_arr, chia_arr, _ = diag["ah"]
        sax0.plot(ta, chia_arr, color=cz.PAL["red"], lw=1.0, alpha=0.25)
        m_cur = ta <= t + 1e-12
        sax0.plot(ta[m_cur], chia_arr[m_cur], color=cz.PAL["red"], lw=1.6)
        sax0_r = sax0.twinx()
        sax0_r.plot(ta, ma_arr, color=cz.PAL["blue"], lw=1.0, alpha=0.25)
        sax0_r.plot(ta[m_cur], ma_arr[m_cur], color=cz.PAL["blue"], lw=1.4, ls="--")
        sax0_r.set_ylabel(r"$M_{\rm AH}\,[M]$", fontsize=8.5, color=cz.PAL["blue"])
        sax0_r.tick_params(axis="y", colors=cz.PAL["blue"], labelsize=8, direction="in")
        sax0_r.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3, prune="both"))
        sax0_r.ticklabel_format(axis="y", style="plain", useOffset=False)
        chi_pad = max(0.015, 0.25 * (float(np.max(chia_arr)) - float(np.min(chia_arr))))
        sax0.set_ylim(float(np.min(chia_arr)) - chi_pad, float(np.max(chia_arr)) + chi_pad)
        m_pad = max(0.005, 0.25 * (float(np.max(ma_arr)) - float(np.min(ma_arr))))
        sax0_r.set_ylim(float(np.min(ma_arr)) - m_pad, float(np.max(ma_arr)) + m_pad)
    sax0.axvline(t, color=cz.PAL["red"], ls="--", lw=1.1, zorder=5)
    sax0.set_ylabel(r"$\chi_{\rm AH}$", fontsize=9, color=cz.PAL["red"])
    sax0.tick_params(axis="y", colors=cz.PAL["red"], labelsize=8)
    sax0.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3, prune="both"))
    sax0.ticklabel_format(axis="y", style="plain", useOffset=False)
    sax0.set_title("Horizon spin/mass, active cloud & GW", fontsize=11, pad=5)
    plt.setp(sax0.get_xticklabels(), visible=False)

    # Strip 1: Active particle fraction
    if diag["vl"] is not None:
        tv, frac_arr, _ = diag["vl"]
        sax1.plot(tv, frac_arr, color=cz.PAL["green"], lw=1.0, alpha=0.25)
        m_cur = tv <= t + 1e-12
        sax1.plot(tv[m_cur], frac_arr[m_cur], color=cz.PAL["green"], lw=1.6)
        ymin = min(0.95, float(np.min(frac_arr)) - 0.02)
        sax1.set_ylim(max(0.0, ymin), 1.02)
    sax1.axvline(t, color=cz.PAL["red"], ls="--", lw=1.1, zorder=5)
    sax1.set_ylabel(r"$N_{\rm act}/N_0$", fontsize=9)
    sax1.tick_params(axis="y", labelsize=8)
    sax1.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3, prune="both"))
    plt.setp(sax1.get_xticklabels(), visible=False)

    # Strip 2: GW r Re(Psi4^22), scaled to avoid scientific offset overlap
    if diag["wf"] is not None:
        tw, p22, rwf = diag["wf"]
        pmax = float(np.max(np.abs(p22))) if len(p22) else 0.0
        exp10 = int(np.floor(np.log10(pmax))) if (0.0 < pmax < 1.0e-2) else 0
        scale = 10.0 ** (-exp10)
        p_plot = p22 * scale
        sax2.plot(tw, p_plot, color=cz.PAL["orange"], lw=1.0, alpha=0.25)
        m_cur = tw <= t + 1e-12
        sax2.plot(tw[m_cur], p_plot[m_cur], color=cz.PAL["orange"], lw=1.5)
        r_tag = rf"\,(r={rwf})" if rwf else ""
        if exp10 != 0:
            sax2.set_ylabel(rf"$10^{{{-exp10}}}r\Psi_4^{{22}}{r_tag}$", fontsize=8.0)
        else:
            sax2.set_ylabel(rf"$r\Psi_4^{{22}}{r_tag}$", fontsize=8.5)
        sax2.ticklabel_format(axis="y", style="plain", useOffset=False)
    else:
        sax2.set_ylabel(r"$r\Psi_4^{22}$", fontsize=8.5)
    sax2.axvline(t, color=cz.PAL["red"], ls="--", lw=1.1, zorder=5)
    sax2.tick_params(axis="both", labelsize=8)
    sax2.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(3, prune="both"))
    sax2.set_xlim(0.0, t_max_all)
    sax2.set_xlabel(r"Time $t\,[M]$", labelpad=2)

    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def build_animations(frame_paths, run_dir, basename, fps=20):
    """Build animated WebP + GIF (via PIL), plus MP4 if ffmpeg is present."""
    if len(frame_paths) < 2:
        print(f"Only {len(frame_paths)} frame(s); skipping animation encoding (need >= 2).")
        return

    webp_path = os.path.join(run_dir, f"{basename}.webp")
    gif_path = os.path.join(run_dir, f"{basename}.gif")
    dur_ms = max(20, int(round(1000.0 / fps)))

    imgs = [Image.open(p).convert("RGB") for p in frame_paths]
    imgs[0].save(
        webp_path, save_all=True, append_images=imgs[1:],
        duration=dur_ms, loop=0, quality=88
    )
    print(f"Wrote animated WebP: {webp_path} ({len(imgs)} frames @ {fps} fps)")

    p_imgs = [im.quantize(colors=256, method=Image.Quantize.FASTOCTREE) for im in imgs]
    p_imgs[0].save(
        gif_path, save_all=True, append_images=p_imgs[1:],
        duration=dur_ms, loop=0, optimize=True
    )
    print(f"Wrote animated GIF:  {gif_path}")

    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        mp4_path = os.path.join(run_dir, f"{basename}.mp4")
        frames_dir = os.path.dirname(frame_paths[0])
        # Use concat demuxer so sparse/non-contiguous frame indices work cleanly
        concat_txt = os.path.join(frames_dir, "ffmpeg_concat.txt")
        with open(concat_txt, "w") as f:
            for p in frame_paths:
                f.write(f"file '{os.path.abspath(p)}'\n")
                f.write(f"duration {1.0 / fps:.6f}\n")
            f.write(f"file '{os.path.abspath(frame_paths[-1])}'\n")
        cmd = [
            ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", mp4_path,
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"Wrote MP4:           {mp4_path}")
        else:
            print(f"Warning: ffmpeg failed (rc={res.returncode}): {res.stderr[-300:]}")


def main():
    ap = argparse.ArgumentParser(description="Render incremental Kerr 0.90 1M-cloud disruption movie.")
    ap.add_argument("--run-dir", default="/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/kerr09_cloud_1m_24h")
    ap.add_argument("--basename", default="kerr09_tde_1m")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--max-frames", type=int, default=0)
    args = ap.parse_args()

    out_dir = args.out_dir or os.path.join(args.run_dir, "movie_frames")
    os.makedirs(out_dir, exist_ok=True)

    snaps = sorted(glob.glob(os.path.join(args.run_dir, f"{args.basename}.vlasov.*.bin")))
    if not snaps:
        print(f"No snapshots found matching {args.run_dir}/{args.basename}.vlasov.*.bin")
        return
    if args.max_frames > 0:
        snaps = snaps[:args.max_frames]

    bin_dir = os.path.join(args.run_dir, "bin")
    slice_maps = {
        sid: index_slice_files(bin_dir, args.basename, sid)
        for sid in ("alpha_xy", "E_xy", "alpha_xz", "E_xz")
    }
    diag = load_diagnostics(args.run_dir, args.basename)

    rendered_paths = []
    new_count = 0
    for sp in snaps:
        m_num = re.search(r"\.vlasov\.(\d+)\.bin$", os.path.basename(sp))
        tag = m_num.group(1) if m_num else os.path.basename(sp)
        out_png = os.path.join(out_dir, f"frame_{tag}.png")
        if os.path.isfile(out_png) and os.path.getsize(out_png) > 0 and not args.overwrite:
            rendered_paths.append(out_png)
            continue
        try:
            render_frame(sp, slice_maps, diag, out_png, dpi=args.dpi)
            rendered_paths.append(out_png)
            new_count += 1
        except (EOFError, ValueError, OSError) as exc:
            print(f"Skipping incomplete snapshot {os.path.basename(sp)}: {exc}")
            continue

    print(f"Rendered {new_count} new frame(s); {len(rendered_paths)} total frame(s) in {out_dir}")
    build_animations(rendered_paths, args.run_dir, args.basename, fps=args.fps)


if __name__ == "__main__":
    main()
