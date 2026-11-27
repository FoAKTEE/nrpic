#!/usr/bin/env python3
"""
Pure-CPU 2D xy & xz multi-variable field renderer (figures + movies) for 1000:1 EMRI NR runs.

Reads without touching or interrupting live GPU runs (CUDA_VISIBLE_DEVICES=""):
  1) High-cadence 2D equatorial slices (dt = 20 M):
     - bin/<base>.alpha_xy.NNNNN.bin   (lapse alpha in xy plane)
     - bin/<base>.conH_xy.NNNNN.bin    (Hamiltonian constraint H in xy plane)
  2) Full 3D AMR restart checkpoints (dt = 200 M):
     - rst/<base>.NNNNN.rst            (all 22 Z4c evolved fields with 4 ghost cells per block)
     Directly extracts BOTH xy (z = 0) and xz (y = 0) 2D slices of:
       alpha, chi, |beta|, Khat, |Theta|, and 6th-order ADM Hamiltonian H_geom = R + K^2 - K_ab K^ab.
  3) Trajectory & horizon files (<base>.traj.bin, <base>.co_0.txt, <base>.horizon_summary_0.txt).

Produces (in <fig_dir>):
  - fig_<prefix>_xy_alpha_H.png            (2x2 latest xy: alpha, |H|, signed H, wave-zone |H|)
  - <prefix>_xy_alpha_H_movie.{webp,gif}   (animated 2x2 xy movie across all bin/ slices)
  - fig_<prefix>_xy_xz_fields.png          (2x6 orbital xy & xz: alpha, chi, |beta|, Khat, |H|, |Theta|)
  - <prefix>_xy_xz_fields_movie.{webp,gif} (animated 2x6 xy & xz movie across all 3D rst/ checkpoints)
  - fig_<prefix>_xy_xz_wavezone.png        (2x4 wave-zone xy & xz [-64, 64] M: |1-alpha|, |beta|, |H|, |Theta|)
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
from matplotlib.colors import LogNorm, SymLogNorm
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
from PIL import Image

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz

from analyze_emri_gw import read_single_traj, safe_load_table
from render_emri_movie import read_athenak_bin, rasterize_xy_slice, draw_amr_blocks


# Z4c u0 variable indices from athenak/src/z4c/z4c.hpp
I_CHI = 0
I_GXX, I_GXY, I_GXZ, I_GYY, I_GYZ, I_GZZ = 1, 2, 3, 4, 5, 6
I_KHAT = 7
I_AXX, I_AXY, I_AXZ, I_AYY, I_AYZ, I_AZZ = 8, 9, 10, 11, 12, 13
I_GAMX, I_GAMY, I_GAMZ = 14, 15, 16
I_THETA = 17
I_ALPHA = 18
I_BETAX, I_BETAY, I_BETAZ = 19, 20, 21
NZ4C = 22

# 6th-order central finite difference weights matching athenak/src/utils/finite_diff.hpp (NGHOST == 4)
W_D1 = np.array([-1.0 / 60.0, 3.0 / 20.0, -3.0 / 4.0, 0.0, 3.0 / 4.0, -3.0 / 20.0, 1.0 / 60.0])
W_D2 = np.array([1.0 / 90.0, -3.0 / 20.0, 3.0 / 2.0, -49.0 / 18.0, 3.0 / 2.0, -3.0 / 20.0, 1.0 / 90.0])


def _d1_axis(arr, axis, dx):
    """6th-order central 1st derivative along `axis`, trimming 3 cells from each end of `axis`."""
    sl = [slice(None)] * arr.ndim
    n = arr.shape[axis]
    out = np.zeros(
        tuple(n - 6 if ax == axis else s for ax, s in enumerate(arr.shape)),
        dtype=np.float64,
    )
    for m, w in enumerate(W_D1):
        if w == 0.0:
            continue
        sl[axis] = slice(m, n - 6 + m)
        out += w * arr[tuple(sl)]
    return out / dx


def _d2_axis(arr, axis, dx):
    """6th-order central 2nd derivative along `axis`, trimming 3 cells from each end of `axis`."""
    sl = [slice(None)] * arr.ndim
    n = arr.shape[axis]
    out = np.zeros(
        tuple(n - 6 if ax == axis else s for ax, s in enumerate(arr.shape)),
        dtype=np.float64,
    )
    for m, w in enumerate(W_D2):
        sl[axis] = slice(m, n - 6 + m)
        out += w * arr[tuple(sl)]
    return out / (dx * dx)


def compute_adm_H_on_slice(u, plane, idx, dx, ng=4):
    """
    Compute 6th-order ADM vacuum Hamiltonian H_geom = R + K^2 - K^a_b K^b_a
    on a single 2D slice of a 3D MeshBlock u with shape (22, nz, ny, nx).
      plane == 'xy': k = idx (in active range ng..nz-ng-1), returns (nx_act, nx_act) = (ny_act, nx_act)
      plane == 'xz': j = idx (in active range ng..ny-ng-1), returns (nz_act, nx_act)
    Uses exact formulas from athenak/src/z4c/z4c_adm.cpp (chi_psi_power = -4).
    """
    nz, ny, nx = u.shape[1], u.shape[2], u.shape[3]
    assert ng >= 3
    if plane == "xy":
        ks = slice(idx - 3, idx + 4)   # len 7 -> trimmed to len 1
        js = slice(ng - 3, ny - ng + 3)  # len ny_act + 6
        is_ = slice(ng - 3, nx - ng + 3)  # len nx_act + 6
    elif plane == "xz":
        ks = slice(ng - 3, nz - ng + 3)
        js = slice(idx - 3, idx + 4)
        is_ = slice(ng - 3, nx - ng + 3)
    else:
        raise ValueError(plane)

    # Extract local stencil sub-volume (7, ny+6, nx+6) or (nz+6, 7, nx+6)
    chi_sub = np.maximum(u[I_CHI, ks, js, is_], 1.0e-12)
    psi4_sub = 1.0 / chi_sub

    # Symmetric 3x3 physical ADM metric g_ab = psi4 * gtilde_ab on sub-volume
    # Indices: (a, b, k, j, i) where a,b in {0,1,2} correspond to {x,y,z} (axes 2, 1, 0 in array!)
    # CAREFUL: array spatial layout is (k=z, j=y, i=x) -> axis_map = {0: 2 (x), 1: 1 (y), 2: 0 (z)}
    ax_map = (2, 1, 0)
    g_sub = np.empty((3, 3) + psi4_sub.shape, dtype=np.float64)
    g_sub[0, 0] = psi4_sub * u[I_GXX, ks, js, is_]
    g_sub[0, 1] = g_sub[1, 0] = psi4_sub * u[I_GXY, ks, js, is_]
    g_sub[0, 2] = g_sub[2, 0] = psi4_sub * u[I_GXZ, ks, js, is_]
    g_sub[1, 1] = psi4_sub * u[I_GYY, ks, js, is_]
    g_sub[1, 2] = g_sub[2, 1] = psi4_sub * u[I_GYZ, ks, js, is_]
    g_sub[2, 2] = psi4_sub * u[I_GZZ, ks, js, is_]

    # Central active slice inside sub-volume has 3-cell margin on all 3 axes
    c_sl = (slice(3, -3), slice(3, -3), slice(3, -3))
    g_c = g_sub[:, :, c_sl[0], c_sl[1], c_sl[2]]  # (3, 3, s0, s1, s2)
    shp = g_c.shape[2:]

    # 1st derivatives dg[c, a, b, ...] = d_c g_ab
    dg = np.empty((3, 3, 3) + shp, dtype=np.float64)
    for c in range(3):
        arr_ax = ax_map[c] + 2  # +2 for leading (a, b)
        # Keep only central slices along the other two axes before differentiating along c
        in_sl = [slice(None), slice(None), slice(3, -3), slice(3, -3), slice(3, -3)]
        in_sl[arr_ax] = slice(None)
        dg[c] = _d1_axis(g_sub[tuple(in_sl)], arr_ax, dx[c])

    # 2nd derivatives ddg[a, b, c, d, ...] = d_a d_b g_cd
    ddg = np.empty((3, 3, 3, 3) + shp, dtype=np.float64)
    for a in range(3):
        ax_a = ax_map[a] + 2
        in_sl = [slice(None), slice(None), slice(3, -3), slice(3, -3), slice(3, -3)]
        in_sl[ax_a] = slice(None)
        ddg[a, a] = _d2_axis(g_sub[tuple(in_sl)], ax_a, dx[a])
        for b in range(a + 1, 3):
            ax_b = ax_map[b] + 2
            in_sl2 = [slice(None), slice(None), slice(3, -3), slice(3, -3), slice(3, -3)]
            in_sl2[ax_a] = slice(None)
            in_sl2[ax_b] = slice(None)
            tmp = _d1_axis(g_sub[tuple(in_sl2)], ax_a, dx[a])
            val = _d1_axis(tmp, ax_b, dx[b])
            ddg[a, b] = val
            ddg[b, a] = val

    # Invert g_c (3x3 symmetric)
    g00, g01, g02 = g_c[0, 0], g_c[0, 1], g_c[0, 2]
    g11, g12, g22 = g_c[1, 1], g_c[1, 2], g_c[2, 2]
    det = (
        g00 * (g11 * g22 - g12 * g12)
        - g01 * (g01 * g22 - g12 * g02)
        + g02 * (g01 * g12 - g11 * g02)
    )
    inv_det = np.where(np.abs(det) > 1.0e-30, 1.0 / np.where(np.abs(det) > 1.0e-30, det, 1.0), 0.0)
    gu = np.empty_like(g_c)
    gu[0, 0] = (g11 * g22 - g12 * g12) * inv_det
    gu[0, 1] = gu[1, 0] = (g02 * g12 - g01 * g22) * inv_det
    gu[0, 2] = gu[2, 0] = (g01 * g12 - g02 * g11) * inv_det
    gu[1, 1] = (g00 * g22 - g02 * g02) * inv_det
    gu[1, 2] = gu[2, 1] = (g01 * g02 - g00 * g12) * inv_det
    gu[2, 2] = (g00 * g11 - g01 * g01) * inv_det

    # Christoffel symbols Gamma_ddd[c, a, b] = 0.5*(dg[a,b,c] + dg[b,a,c] - dg[c,a,b])
    Gam_ddd = 0.5 * (
        np.transpose(dg, (2, 0, 1, 3, 4, 5))
        + np.transpose(dg, (2, 1, 0, 3, 4, 5))
        - dg
    )
    Gam_udd = np.einsum("cd...,dab...->cab...", gu, Gam_ddd)

    # Ricci tensor R_dd[a, b] and scalar R
    R_dd = (
        np.einsum("cd...,eac...,ebd...->ab...", gu, Gam_udd, Gam_ddd)
        - np.einsum("cd...,eab...,ecd...->ab...", gu, Gam_udd, Gam_ddd)
        + 0.5 * np.einsum(
            "cd...,cdab...->ab...",
            gu,
            -ddg
            - np.transpose(ddg, (2, 3, 0, 1, 4, 5, 6))
            + np.transpose(ddg, (2, 0, 3, 1, 4, 5, 6))
            + np.transpose(ddg, (3, 0, 2, 1, 4, 5, 6)),
        )
    )
    R = np.einsum("ab...,ab...->...", gu, R_dd)

    # Extrinsic curvature K_ab on central slice
    psi4_c = psi4_sub[c_sl]
    khat_c = u[I_KHAT, ks, js, is_][c_sl]
    th_c = u[I_THETA, ks, js, is_][c_sl]
    trK = khat_c + 2.0 * th_c
    K_dd = np.empty_like(g_c)
    K_dd[0, 0] = psi4_c * u[I_AXX, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[0, 0]
    K_dd[0, 1] = K_dd[1, 0] = psi4_c * u[I_AXY, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[0, 1]
    K_dd[0, 2] = K_dd[2, 0] = psi4_c * u[I_AXZ, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[0, 2]
    K_dd[1, 1] = psi4_c * u[I_AYY, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[1, 1]
    K_dd[1, 2] = K_dd[2, 1] = psi4_c * u[I_AYZ, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[1, 2]
    K_dd[2, 2] = psi4_c * u[I_AZZ, ks, js, is_][c_sl] + (1.0 / 3.0) * trK * g_c[2, 2]

    K_ud = np.einsum("ac...,cb...->ab...", gu, K_dd)
    K_tr = K_ud[0, 0] + K_ud[1, 1] + K_ud[2, 2]
    KK = np.einsum("ab...,ba...->...", K_ud, K_ud)
    H = R + K_tr * K_tr - KK

    if plane == "xy":
        return H[0, :, :]   # (ny_act, nx_act)
    return H[:, 0, :]       # (nz_act, nx_act)


def read_rst_slices(rst_path, z_slice=0.001, y_slice=0.001, nco=1):
    """
    Parse an AthenaK 3D Z4c restart file and extract 2D xy (z=z_slice) and xz (y=y_slice) slices
    for alpha, chi, |beta|, Khat, Theta, and 6th-order ADM H_geom.
    Only seeks and reads MeshBlocks crossing z_slice or y_slice -> fast & low RAM.
    """
    fsize = os.path.getsize(rst_path)
    with open(rst_path, "rb") as fp:
        # Read parameter dump until <par_end>\n
        chunks = []
        found = False
        while True:
            line = fp.readline()
            if not line:
                break
            chunks.append(line)
            if line.strip() == b"<par_end>":
                found = True
                break
        if not found:
            raise EOFError(f"Missing <par_end> in {rst_path}")

        # Step 1: Mesh metadata
        nmb_total, root_level = struct.unpack("<2i", fp.read(8))
        mesh_size = struct.unpack("<9d", fp.read(72))  # x1min..x3min, x1max..x3max, dx1..dx3
        mesh_indcs = struct.unpack("<19i", fp.read(76))
        mb_indcs = struct.unpack("<19i", fp.read(76))
        t_rst, dt_rst, ncycle = struct.unpack("<2di", fp.read(20))

        # Step 2: LogicalLocations & costs
        lloc = np.frombuffer(fp.read(nmb_total * 16), dtype="<i4").reshape(nmb_total, 4).copy()
        _cost = fp.read(nmb_total * 4)

        # Step 3: Z4c last_output_time + nco tracker positions
        _z4c_last_t = struct.unpack("<d", fp.read(8))[0]
        tracker_pos = np.frombuffer(fp.read(nco * 24), dtype="<f8").reshape(nco, 3).copy()

        # Step 4: data_size per MeshBlock
        data_size = struct.unpack("<Q", fp.read(8))[0]
        data_offset = fp.tell()

        ng = mb_indcs[0]
        nx1, nx2, nx3 = mb_indcs[1], mb_indcs[2], mb_indcs[3]
        nout1, nout2, nout3 = nx1 + 2 * ng, nx2 + 2 * ng, nx3 + 2 * ng
        expected_mb_bytes = nout1 * nout2 * nout3 * NZ4C * 8
        if data_size != expected_mb_bytes:
            raise ValueError(
                f"Unexpected data_size={data_size} vs expected {expected_mb_bytes} in {rst_path}"
            )
        if data_offset + nmb_total * data_size > fsize:
            raise EOFError(f"Incomplete rst file (still writing?): {rst_path}")

        x1min_m, x2min_m, x3min_m, x1max_m, x2max_m, x3max_m = mesh_size[:6]
        Lx1 = x1max_m - x1min_m
        Lx2 = x2max_m - x2min_m
        Lx3 = x3max_m - x3min_m
        nroot1 = mesh_indcs[1] // nx1
        nroot2 = mesh_indcs[2] // nx2
        nroot3 = mesh_indcs[3] // nx3

        xy_blocks = []
        xz_blocks = []
        for m in range(nmb_total):
            lx1, lx2, lx3, lev = int(lloc[m, 0]), int(lloc[m, 1]), int(lloc[m, 2]), int(lloc[m, 3])
            scale = 1 << (lev - root_level)
            bw1 = Lx1 / (nroot1 * scale)
            bw2 = Lx2 / (nroot2 * scale)
            bw3 = Lx3 / (nroot3 * scale)
            bx10 = x1min_m + lx1 * bw1
            bx11 = bx10 + bw1
            bx20 = x2min_m + lx2 * bw2
            bx21 = bx20 + bw2
            bx30 = x3min_m + lx3 * bw3
            bx31 = bx30 + bw3

            hit_xy = (bx30 <= z_slice <= bx31)
            hit_xz = (bx20 <= y_slice <= bx21)
            if not (hit_xy or hit_xz):
                continue

            fp.seek(data_offset + m * data_size)
            raw = fp.read(data_size)
            u = np.frombuffer(raw, dtype="<f8").reshape(NZ4C, nout3, nout2, nout1)
            dx = (bw1 / nx1, bw2 / nx2, bw3 / nx3)

            if hit_xy:
                k_act = int(np.clip(math.floor((z_slice - bx30) / dx[2]), 0, nx3 - 1))
                k_idx = ng + k_act
                sl_a = (slice(ng, ng + nx2), slice(ng, ng + nx1))
                alp = u[I_ALPHA, k_idx, sl_a[0], sl_a[1]].copy()
                chi = u[I_CHI, k_idx, sl_a[0], sl_a[1]].copy()
                khat = u[I_KHAT, k_idx, sl_a[0], sl_a[1]].copy()
                theta = u[I_THETA, k_idx, sl_a[0], sl_a[1]].copy()
                bmag = np.sqrt(
                    u[I_BETAX, k_idx, sl_a[0], sl_a[1]] ** 2
                    + u[I_BETAY, k_idx, sl_a[0], sl_a[1]] ** 2
                    + u[I_BETAZ, k_idx, sl_a[0], sl_a[1]] ** 2
                )
                H_xy = compute_adm_H_on_slice(u, "xy", k_idx, dx, ng=ng)
                xy_blocks.append(
                    (
                        (bx10, bx11, bx20, bx21),
                        {
                            "alpha": alp,
                            "chi": chi,
                            "beta": bmag,
                            "khat": khat,
                            "H": H_xy,
                            "theta": theta,
                        },
                    )
                )

            if hit_xz:
                j_act = int(np.clip(math.floor((y_slice - bx20) / dx[1]), 0, nx2 - 1))
                j_idx = ng + j_act
                sl_a = (slice(ng, ng + nx3), slice(ng, ng + nx1))
                alp = u[I_ALPHA, sl_a[0], j_idx, sl_a[1]].copy()
                chi = u[I_CHI, sl_a[0], j_idx, sl_a[1]].copy()
                khat = u[I_KHAT, sl_a[0], j_idx, sl_a[1]].copy()
                theta = u[I_THETA, sl_a[0], j_idx, sl_a[1]].copy()
                bmag = np.sqrt(
                    u[I_BETAX, sl_a[0], j_idx, sl_a[1]] ** 2
                    + u[I_BETAY, sl_a[0], j_idx, sl_a[1]] ** 2
                    + u[I_BETAZ, sl_a[0], j_idx, sl_a[1]] ** 2
                )
                H_xz = compute_adm_H_on_slice(u, "xz", j_idx, dx, ng=ng)
                xz_blocks.append(
                    (
                        (bx10, bx11, bx30, bx31),
                        {
                            "alpha": alp,
                            "chi": chi,
                            "beta": bmag,
                            "khat": khat,
                            "H": H_xz,
                            "theta": theta,
                        },
                    )
                )

    return {
        "time": t_rst,
        "ncycle": ncycle,
        "nmb_total": nmb_total,
        "tracker_pos": tracker_pos,
        "xy_blocks": xy_blocks,
        "xz_blocks": xz_blocks,
    }


def rasterize_2d_dict(blocks, key, ulim, vlim, ngrid=360, shift=(0.0, 0.0)):
    """Rasterize 2D AMR blocks [(u0, u1, v0, v1), dict] onto (ulim, vlim) after shifting by -shift."""
    su, sv = shift
    img = np.full((ngrid, ngrid), np.nan, dtype=np.float64)
    gu = np.linspace(ulim[0], ulim[1], ngrid)
    gv = np.linspace(vlim[0], vlim[1], ngrid)
    blocks_sorted = sorted(blocks, key=lambda item: -(item[0][1] - item[0][0]))
    for (u0, u1, v0, v1), d in blocks_sorted:
        bu0, bu1 = u0 - su, u1 - su
        bv0, bv1 = v0 - sv, v1 - sv
        if bu1 < ulim[0] or bu0 > ulim[1] or bv1 < vlim[0] or bv0 > vlim[1]:
            continue
        plane = d[key]
        nv, nu = plane.shape
        iu0 = max(0, int(np.searchsorted(gu, bu0, side="left")))
        iu1 = min(ngrid, int(np.searchsorted(gu, bu1, side="right")))
        iv0 = max(0, int(np.searchsorted(gv, bv0, side="left")))
        iv1 = min(ngrid, int(np.searchsorted(gv, bv1, side="right")))
        if iu1 <= iu0 or iv1 <= iv0:
            continue
        ui = np.clip(((gu[iu0:iu1] - bu0) / max(bu1 - bu0, 1e-12) * nu).astype(int), 0, nu - 1)
        vi = np.clip(((gv[iv0:iv1] - bv0) / max(bv1 - bv0, 1e-12) * nv).astype(int), 0, nv - 1)
        img[iv0:iv1, iu0:iu1] = plane[np.ix_(vi, ui)]
    return gu, gv, img


def draw_amr_2d(ax, blocks_2d, ulim, vlim, shift=(0.0, 0.0), max_bw=2.1):
    su, sv = shift
    for (u0, u1, v0, v1), _ in blocks_2d:
        bu0, bu1 = u0 - su, u1 - su
        bv0, bv1 = v0 - sv, v1 - sv
        bw, bh = bu1 - bu0, bv1 - bv0
        if bw <= max_bw and bu1 >= ulim[0] and bu0 <= ulim[1] and bv1 >= vlim[0] and bv0 <= vlim[1]:
            is_fine = bw <= 1.1
            ax.add_patch(
                Rectangle(
                    (bu0, bv0),
                    bw,
                    bh,
                    fill=False,
                    ec="#7FFFD4" if is_fine else "cyan",
                    lw=0.35 if is_fine else 0.45,
                    alpha=0.38 if is_fine else 0.48,
                    zorder=4,
                )
            )


def render_xy_alpha_H_frame(
    out_png,
    name,
    R0,
    q,
    t_sl,
    a_blocks,
    h_blocks,
    t_tr,
    x_rel,
    x_bh_at_t,
    r_ah_at_t,
    ext_radii,
    dpi=140,
):
    """2x2 xy figure/frame: Lapse (zoom), |H| (zoom), signed H (zoom), |H| (wave zone [-64, 64] M)."""
    cz.use_style()
    fig = plt.figure(figsize=(10.9, 9.4))
    fig.subplots_adjust(left=0.072, right=0.915, bottom=0.065, top=0.905, wspace=0.42, hspace=0.25)
    axes = fig.subplots(2, 2)

    lim_z = 8.0
    lim_w = 64.0
    sh = (float(x_bh_at_t[0]), float(x_bh_at_t[1]))

    gx_z, gy_z, alp_z = rasterize_xy_slice(a_blocks, 0, (-lim_z, lim_z), (-lim_z, lim_z), ngrid=320, shift=sh)
    _, _, H_z = rasterize_xy_slice(h_blocks, 0, (-lim_z, lim_z), (-lim_z, lim_z), ngrid=320, shift=sh)
    gx_w, gy_w, H_w = rasterize_xy_slice(h_blocks, 0, (-lim_w, lim_w), (-lim_w, lim_w), ngrid=320, shift=sh)

    m_t = t_tr <= t_sl + 1e-6
    x_cur = x_rel[m_t][-1] if np.any(m_t) else x_rel[0]
    trail = x_rel[m_t] if np.any(m_t) else x_rel[:1]
    if len(trail) > 600:
        trail = trail[np.linspace(0, len(trail) - 1, 600, dtype=int)]
    cmap_mag = cz.truncate_cmap("magma", 0.08, 1.0)

    # (0,0) Lapse alpha (orbital zoom)
    ax = axes[0, 0]
    im0 = ax.pcolormesh(gx_z, gy_z, alp_z, cmap="viridis", vmin=0.0, vmax=1.0, shading="auto", rasterized=True)
    draw_amr_blocks(ax, a_blocks, (-lim_z, lim_z), (-lim_z, lim_z), shift=sh, max_bw=2.1)
    ax.plot(trail[:, 0], trail[:, 1], color="white", lw=0.9, alpha=0.80, zorder=5)
    ax.scatter([x_cur[0]], [x_cur[1]], s=36, color=cz.PAL["red"], ec="white", lw=0.9, zorder=7)
    ax.add_patch(Circle((0.0, 0.0), r_ah_at_t, fc="black", ec="white", lw=0.9, zorder=6))
    ax.set_aspect("equal")
    ax.set_xlim(-lim_z, lim_z); ax.set_ylim(-lim_z, lim_z)
    ax.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=-1); ax.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
    ax.set_title(r"Equatorial lapse $\alpha(x, y)$ (zoom)")
    cz.side_colorbar(fig, ax, im0, r"$\alpha$", size="4.5%", pad=0.03)

    # (0,1) Log |H| (orbital zoom)
    ax = axes[0, 1]
    im1 = ax.pcolormesh(
        gx_z, gy_z, np.clip(np.abs(H_z), 1e-10, None),
        cmap=cmap_mag, norm=LogNorm(vmin=1e-7, vmax=1e-1), shading="auto", rasterized=True,
    )
    ax.plot(trail[:, 0], trail[:, 1], color="cyan", lw=0.7, alpha=0.60, zorder=5)
    ax.scatter([x_cur[0]], [x_cur[1]], s=36, facecolors="none", ec="cyan", lw=1.2, zorder=7)
    ax.add_patch(Circle((0.0, 0.0), r_ah_at_t, fc="none", ec="white", ls="--", lw=0.9, zorder=6))
    ax.set_aspect("equal")
    ax.set_xlim(-lim_z, lim_z); ax.set_ylim(-lim_z, lim_z)
    ax.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=-1); ax.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
    ax.set_title(r"Hamiltonian constraint $|H(x, y)|$ (zoom)")
    cz.side_colorbar(fig, ax, im1, r"$|H|$", size="4.5%", pad=0.03)

    # (1,0) Signed H (orbital zoom)
    ax = axes[1, 0]
    im2 = ax.pcolormesh(
        gx_z, gy_z, H_z,
        cmap="RdBu_r", norm=SymLogNorm(linthresh=1e-5, linscale=0.6, vmin=-1e-2, vmax=1e-2),
        shading="auto", rasterized=True,
    )
    ax.scatter([x_cur[0]], [x_cur[1]], s=36, facecolors="none", ec="k", lw=1.1, zorder=7)
    ax.add_patch(Circle((0.0, 0.0), r_ah_at_t, fc="none", ec="k", ls="--", lw=0.9, zorder=6))
    ax.set_aspect("equal")
    ax.set_xlim(-lim_z, lim_z); ax.set_ylim(-lim_z, lim_z)
    ax.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=-1); ax.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
    ax.set_title(r"Signed Hamiltonian $H(x, y)$ (zoom)")
    cz.side_colorbar(fig, ax, im2, r"$H$", size="4.5%", pad=0.03)

    # (1,1) Wave-zone |H| ([-64, 64] M)
    ax = axes[1, 1]
    im3 = ax.pcolormesh(
        gx_w, gy_w, np.clip(np.abs(H_w), 1e-12, None),
        cmap=cmap_mag, norm=LogNorm(vmin=1e-9, vmax=1e-2), shading="auto", rasterized=True,
    )
    for rext in ext_radii:
        ax.add_patch(Circle((0.0, 0.0), rext, fc="none", ec="white", ls=":", lw=0.65, alpha=0.65, zorder=5))
    ax.add_patch(Rectangle((-lim_z, -lim_z), 2 * lim_z, 2 * lim_z, fc="none", ec="cyan", lw=0.8, zorder=6))
    ax.scatter([x_cur[0]], [x_cur[1]], s=20, color="cyan", ec="k", lw=0.5, zorder=7)
    ax.set_aspect("equal")
    ax.set_xlim(-lim_w, lim_w); ax.set_ylim(-lim_w, lim_w)
    ax.set_xlabel(r"$x - x_{\rm BH}\,[M]$", labelpad=-1); ax.set_ylabel(r"$y - y_{\rm BH}\,[M]$")
    ax.set_title(r"Wave-zone $|H(x, y)|$ ($r_{\rm ext}=20..58\,M$)")
    cz.side_colorbar(fig, ax, im3, r"$|H|$", size="4.5%", pad=0.03)

    for row in axes:
        for a in row:
            a.tick_params(which="both", direction="in", top=True, right=True)

    bh_d = float(np.linalg.norm(x_bh_at_t))
    fig.suptitle(
        rf"{name}: 2D Equatorial Fields ($R_0={R0:.2f}\,M$, $q={q:.0e}$, $t={t_sl:.1f}\,M$, $|\mathbf{{x}}_{{\rm BH}}|={bh_d:.4f}\,M$)",
        fontsize=11.5,
        y=0.962,
    )
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def render_xy_xz_6var_figure(
    out_png,
    name,
    R0,
    q,
    rst_data,
    conH_xy_blocks,
    t_tr,
    x_rel,
    r_ah_at_t,
    lim=8.0,
    dpi=300,
):
    """
    2 rows (xy plane z=0 on top; xz plane y=0 on bottom) x 6 columns:
      1. Lapse alpha
      2. Conformal factor chi = psi^-4
      3. Shift magnitude |beta|
      4. Extrinsic curvature Khat
      5. Hamiltonian constraint |H| (exact conH_xy on xy if available; 6th-order ADM |H_geom| on xz)
      6. Z4c constraint scalar |Theta|
    """
    cz.use_style()
    t_rst = rst_data["time"]
    bh_pos = rst_data["tracker_pos"][0]
    sh_xy = (float(bh_pos[0]), float(bh_pos[1]))
    sh_xz = (float(bh_pos[0]), float(bh_pos[2]))

    m_t = t_tr <= t_rst + 1e-6
    x_cur = x_rel[m_t][-1] if np.any(m_t) else x_rel[0]
    trail = x_rel[m_t] if np.any(m_t) else x_rel[:1]
    if len(trail) > 500:
        trail = trail[np.linspace(0, len(trail) - 1, 500, dtype=int)]

    cmap_mag = cz.truncate_cmap("magma", 0.08, 1.0)
    cmap_chi = cz.truncate_cmap("magma", 0.15, 1.0)

    specs = [
        ("alpha", r"Lapse $\alpha$", "viridis", None, (0.0, 1.0), False),
        ("chi", r"Conformal $\chi=\psi^{-4}$", cmap_chi, None, (0.0, 1.0), False),
        ("beta", r"Shift $|\boldsymbol{\beta}|$", "inferno", LogNorm(vmin=1e-4, vmax=0.5), None, True),
        ("khat", r"Extrinsic $\hat{K}$", "RdBu_r", SymLogNorm(linthresh=1e-3, linscale=0.6, vmin=-0.5, vmax=0.5), None, False),
        ("H", r"Hamiltonian $|H|$", cmap_mag, LogNorm(vmin=1e-7, vmax=1e-1), None, True),
        ("theta", r"Z4c $|\Theta|$", "plasma", LogNorm(vmin=1e-8, vmax=1e-2), None, True),
    ]

    fig = plt.figure(figsize=(15.4, 6.1))
    # Explicit margins with top colorbar space above each column
    left, right, bottom, top = 0.045, 0.988, 0.085, 0.815
    wspace, hspace = 0.09, 0.13
    ncols = 6
    panel_w = (right - left - (ncols - 1) * wspace * 0.14) / ncols
    gs = fig.add_gridspec(2, ncols, left=left, right=right, bottom=bottom, top=top, wspace=0.14, hspace=0.14)
    axes = np.empty((2, ncols), dtype=object)

    for col, (key, title, cmap, norm, vlim, take_abs) in enumerate(specs):
        # Row 0: xy plane
        ax_xy = fig.add_subplot(gs[0, col])
        axes[0, col] = ax_xy
        if key == "H" and conH_xy_blocks is not None:
            gu, gv, arr_xy = rasterize_xy_slice(conH_xy_blocks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
        else:
            gu, gv, arr_xy = rasterize_2d_dict(rst_data["xy_blocks"], key, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
        data_xy = np.clip(np.abs(arr_xy), 1e-12, None) if take_abs else arr_xy

        # Row 1: xz plane
        ax_xz = fig.add_subplot(gs[1, col])
        axes[1, col] = ax_xz
        gu2, gv2, arr_xz = rasterize_2d_dict(rst_data["xz_blocks"], key, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xz)
        data_xz = np.clip(np.abs(arr_xz), 1e-12, None) if take_abs else arr_xz

        kw = dict(cmap=cmap, shading="auto", rasterized=True)
        if norm is not None:
            kw["norm"] = norm
        else:
            kw["vmin"], kw["vmax"] = vlim

        im_xy = ax_xy.pcolormesh(gu, gv, data_xy, **kw)
        ax_xz.pcolormesh(gu2, gv2, data_xz, **kw)

        # Overlays
        if col == 0:
            draw_amr_2d(ax_xy, rst_data["xy_blocks"], (-lim, lim), (-lim, lim), shift=sh_xy, max_bw=2.1)
            draw_amr_2d(ax_xz, rst_data["xz_blocks"], (-lim, lim), (-lim, lim), shift=sh_xz, max_bw=2.1)
            ax_xy.plot(trail[:, 0], trail[:, 1], color="white", lw=0.75, alpha=0.80, zorder=5)
            ax_xy.scatter([x_cur[0]], [x_cur[1]], s=24, color=cz.PAL["red"], ec="white", lw=0.7, zorder=7)
            # Equatorial plane guide & projected particle x on xz plane
            ax_xz.axhline(0.0, color="white", ls=":", lw=0.65, alpha=0.55, zorder=5)
            ax_xz.scatter([x_cur[0]], [x_cur[2]], s=24, color=cz.PAL["red"], ec="white", lw=0.7, zorder=7)
        else:
            ec_p = "k" if key == "khat" else "cyan"
            ax_xy.scatter([x_cur[0]], [x_cur[1]], s=20, facecolors="none", ec=ec_p, lw=0.9, zorder=7)
            ax_xz.axhline(0.0, color="k" if key == "khat" else "white", ls=":", lw=0.55, alpha=0.40, zorder=5)
            ax_xz.scatter([x_cur[0]], [x_cur[2]], s=20, facecolors="none", ec=ec_p, lw=0.9, zorder=7)

        for ax_p in (ax_xy, ax_xz):
            ec_h = "k" if key == "khat" else "white"
            fc_h = "black" if key in ("alpha", "chi") else "none"
            ls_h = "-" if key in ("alpha", "chi") else "--"
            ax_p.add_patch(Circle((0.0, 0.0), r_ah_at_t, fc=fc_h, ec=ec_h, ls=ls_h, lw=0.85, zorder=6))
            ax_p.set_aspect("equal")
            ax_p.set_xlim(-lim, lim)
            ax_p.set_ylim(-lim, lim)
            cz.slice_ticks(ax_p, lim, show_x=(ax_p is ax_xz), show_y=(col == 0))
            ax_p.tick_params(which="both", direction="in", top=True, right=True, labelsize=8.5)

        if col == 0:
            ax_xy.set_ylabel(r"$xy$ plane: $y - y_{\rm BH}\,[M]$", fontsize=9.5)
            ax_xz.set_ylabel(r"$xz$ plane: $z - z_{\rm BH}\,[M]$", fontsize=9.5)
        ax_xz.set_xlabel(r"$x - x_{\rm BH}\,[M]$", fontsize=9.0, labelpad=-1)

        # Horizontal colorbar cleanly above each column
        pos = ax_xy.get_position()
        cax = fig.add_axes([pos.x0, pos.y1 + 0.016, pos.width, 0.022])
        cb = fig.colorbar(im_xy, cax=cax, orientation="horizontal")
        if key == "khat":
            cb.set_ticks([-1e-1, -1e-2, 0.0, 1e-2, 1e-1])
        cax.xaxis.set_ticks_position("top")
        cax.xaxis.set_label_position("top")
        cb.ax.tick_params(labelsize=7.5, pad=1.5, direction="in")
        if key in ("beta", "H", "theta", "khat"):
            cz.no_minor_labels(cb.ax, "x")
        cax.set_title(title, fontsize=10.0, pad=18.0)

    bh_d = float(np.linalg.norm(bh_pos))
    fig.suptitle(
        rf"{name}: 2D $xy$ & $xz$ Multi-Variable Z4c Atlas ($R_0={R0:.2f}\,M$, $q={q:.0e}$, $t={t_rst:.1f}\,M$, $|\mathbf{{x}}_{{\rm BH}}|={bh_d:.4f}\,M$)",
        fontsize=12.0,
        y=0.975,
    )
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def render_xy_xz_wavezone_figure(
    out_png,
    name,
    R0,
    q,
    rst_data,
    conH_xy_blocks,
    ext_radii,
    lim=64.0,
    dpi=300,
):
    """2 rows (xy, xz) x 4 columns wide-field wave-zone atlas ([-64, 64] M): |1-alpha|, |beta|, |H|, |Theta|."""
    cz.use_style()
    t_rst = rst_data["time"]
    bh_pos = rst_data["tracker_pos"][0]
    sh_xy = (float(bh_pos[0]), float(bh_pos[1]))
    sh_xz = (float(bh_pos[0]), float(bh_pos[2]))
    cmap_mag = cz.truncate_cmap("magma", 0.08, 1.0)

    specs = [
        ("1malpha", r"Lapse dev. $|1 - \alpha|$", "viridis", LogNorm(vmin=1e-3, vmax=1.0)),
        ("beta", r"Shift $|\boldsymbol{\beta}|$", "inferno", LogNorm(vmin=1e-6, vmax=0.3)),
        ("H", r"Hamiltonian $|H|$", cmap_mag, LogNorm(vmin=1e-9, vmax=1e-2)),
        ("theta", r"Z4c $|\Theta|$", "plasma", LogNorm(vmin=1e-9, vmax=1e-3)),
    ]

    fig = plt.figure(figsize=(11.4, 6.2))
    gs = fig.add_gridspec(2, 4, left=0.065, right=0.985, bottom=0.085, top=0.815, wspace=0.14, hspace=0.14)

    for col, (key, title, cmap, norm) in enumerate(specs):
        ax_xy = fig.add_subplot(gs[0, col])
        ax_xz = fig.add_subplot(gs[1, col])

        if key == "1malpha":
            gu, gv, a_xy = rasterize_2d_dict(rst_data["xy_blocks"], "alpha", (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
            gu2, gv2, a_xz = rasterize_2d_dict(rst_data["xz_blocks"], "alpha", (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xz)
            d_xy = np.clip(np.abs(1.0 - a_xy), 1e-12, None)
            d_xz = np.clip(np.abs(1.0 - a_xz), 1e-12, None)
        elif key == "H":
            if conH_xy_blocks is not None:
                gu, gv, h_xy = rasterize_xy_slice(conH_xy_blocks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
            else:
                gu, gv, h_xy = rasterize_2d_dict(rst_data["xy_blocks"], "H", (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
            gu2, gv2, h_xz = rasterize_2d_dict(rst_data["xz_blocks"], "H", (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xz)
            d_xy = np.clip(np.abs(h_xy), 1e-12, None)
            d_xz = np.clip(np.abs(h_xz), 1e-12, None)
        else:
            gu, gv, arr_xy = rasterize_2d_dict(rst_data["xy_blocks"], key, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
            gu2, gv2, arr_xz = rasterize_2d_dict(rst_data["xz_blocks"], key, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xz)
            d_xy = np.clip(np.abs(arr_xy), 1e-12, None)
            d_xz = np.clip(np.abs(arr_xz), 1e-12, None)

        im = ax_xy.pcolormesh(gu, gv, d_xy, cmap=cmap, norm=norm, shading="auto", rasterized=True)
        ax_xz.pcolormesh(gu2, gv2, d_xz, cmap=cmap, norm=norm, shading="auto", rasterized=True)

        for ax_p in (ax_xy, ax_xz):
            for rext in ext_radii:
                ax_p.add_patch(Circle((0.0, 0.0), rext, fc="none", ec="white", ls=":", lw=0.60, alpha=0.55, zorder=5))
            ax_p.add_patch(Rectangle((-8.0, -8.0), 16.0, 16.0, fc="none", ec="cyan", lw=0.75, zorder=6))
            ax_p.set_aspect("equal")
            ax_p.set_xlim(-lim, lim); ax_p.set_ylim(-lim, lim)
            cz.slice_ticks(ax_p, lim, show_x=(ax_p is ax_xz), show_y=(col == 0))
            ax_p.tick_params(which="both", direction="in", top=True, right=True, labelsize=8.5)

        if col == 0:
            ax_xy.set_ylabel(r"$xy$ plane: $y - y_{\rm BH}\,[M]$", fontsize=9.5)
            ax_xz.set_ylabel(r"$xz$ plane: $z - z_{\rm BH}\,[M]$", fontsize=9.5)
        ax_xz.set_xlabel(r"$x - x_{\rm BH}\,[M]$", fontsize=9.0, labelpad=-1)

        pos = ax_xy.get_position()
        cax = fig.add_axes([pos.x0, pos.y1 + 0.016, pos.width, 0.022])
        cb = fig.colorbar(im, cax=cax, orientation="horizontal")
        cax.xaxis.set_ticks_position("top")
        cax.xaxis.set_label_position("top")
        cb.ax.tick_params(labelsize=7.5, pad=1.5, direction="in")
        cz.no_minor_labels(cb.ax, "x")
        cax.set_title(title, fontsize=10.0, pad=18.0)

    fig.suptitle(
        rf"{name}: Wave-Zone $xy$ & $xz$ Slices ($[-64, 64]\,M$, $r_{{\rm ext}}=20..58\,M$, $t={t_rst:.1f}\,M$)",
        fontsize=12.0,
        y=0.975,
    )
    fig.savefig(out_png, dpi=dpi)
    plt.close(fig)


def assemble_animation(frame_paths, webp_out, gif_out, fps):
    if not frame_paths:
        return
    imgs = [Image.open(p).convert("RGB") for p in frame_paths]
    dur_ms = int(round(1000.0 / max(fps, 1)))
    imgs[0].save(webp_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0, quality=88)
    imgs[0].save(gif_out, save_all=True, append_images=imgs[1:], duration=dur_ms, loop=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--fig-dir", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--fps-xy", type=int, default=5)
    ap.add_argument("--fps-rst", type=int, default=2)
    args = ap.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    fig_dir = os.path.abspath(args.fig_dir)
    os.makedirs(fig_dir, exist_ok=True)

    with open(os.path.join(run_dir, "run_meta.json")) as f:
        meta = json.load(f)
    name = meta["name"]
    R0 = float(meta["R0"])
    q = float(meta["q"])
    ext_radii = meta.get("extraction_radii", [20.0, 27.0, 38.0, 48.0, 58.0])

    # Load trajectory, BH tracker, and horizon radius
    traj = read_single_traj(os.path.join(run_dir, f"{name}.traj.bin"))
    if traj is None or len(traj) < 2:
        raise RuntimeError(f"Trajectory missing or empty in {run_dir}")
    t_tr = traj[:, 0]
    x_p = traj[:, 2:5]
    co = safe_load_table(os.path.join(run_dir, f"{name}.co_0.txt"), min_cols=5, tcol=1)
    hs = safe_load_table(os.path.join(run_dir, f"{name}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    if co is not None and len(co) > 1:
        x_bh = np.column_stack([np.interp(t_tr, co[:, 1], co[:, c]) for c in (2, 3, 4)])
    else:
        x_bh = np.zeros_like(x_p)
    x_rel = x_p - x_bh

    def get_r_ah(tt):
        if hs is not None and len(hs) > 0:
            return float(np.interp(tt, hs[:, 1], hs[:, 11]))
        return 0.93

    def get_x_bh(tt):
        if co is not None and len(co) > 1:
            return np.array([float(np.interp(tt, co[:, 1], co[:, c])) for c in (2, 3, 4)])
        return np.zeros(3)

    # =========================================================================
    # PART 1: High-cadence 2D xy (alpha + |H| + signed H + wave-zone |H|) movie & figure
    # =========================================================================
    alpha_files = sorted(glob.glob(os.path.join(run_dir, "bin", f"{name}.alpha_xy.*.bin")))
    conH_map = {}
    for hp in sorted(glob.glob(os.path.join(run_dir, "bin", f"{name}.conH_xy.*.bin"))):
        m = re.search(r"\.(\d{5})\.bin$", hp)
        if m:
            conH_map[m.group(1)] = hp

    xy_frame_dir = os.path.join(run_dir, "frames_xy_alpha_H")
    os.makedirs(xy_frame_dir, exist_ok=True)
    xy_frames = []
    valid_xy_pairs = []
    for apath in alpha_files:
        m = re.search(r"\.(\d{5})\.bin$", apath)
        if not m:
            continue
        idx_str = m.group(1)
        hpath = conH_map.get(idx_str)
        if hpath is None:
            continue
        try:
            t_a, _, a_blocks = read_athenak_bin(apath)
            t_h, _, h_blocks = read_athenak_bin(hpath)
        except Exception as exc:
            print(f"[skip incomplete bin slice {idx_str}]: {exc}")
            continue
        valid_xy_pairs.append((idx_str, t_a, a_blocks, h_blocks))
        fpng = os.path.join(xy_frame_dir, f"frame_{idx_str}.png")
        render_xy_alpha_H_frame(
            fpng, name, R0, q, t_a, a_blocks, h_blocks,
            t_tr, x_rel, get_x_bh(t_a), get_r_ah(t_a), ext_radii, dpi=135,
        )
        xy_frames.append(fpng)

    if valid_xy_pairs:
        # High-res 300 dpi static figure of latest xy slice
        _, t_last, a_last, h_last = valid_xy_pairs[-1]
        xy_fig_out = os.path.join(fig_dir, f"fig_{args.prefix}_xy_alpha_H.png")
        render_xy_alpha_H_frame(
            xy_fig_out, name, R0, q, t_last, a_last, h_last,
            t_tr, x_rel, get_x_bh(t_last), get_r_ah(t_last), ext_radii, dpi=300,
        )
        webp_xy = os.path.join(fig_dir, f"{args.prefix}_xy_alpha_H_movie.webp")
        gif_xy = os.path.join(fig_dir, f"{args.prefix}_xy_alpha_H_movie.gif")
        assemble_animation(xy_frames, webp_xy, gif_xy, args.fps_xy)
        print(f"Wrote {xy_fig_out} + {len(xy_frames)}-frame movie ({webp_xy}, {gif_xy}) up to t={t_last:.1f} M")

    # =========================================================================
    # PART 2: Full 3D .rst -> 2D xy & xz 6-variable atlas (figures + movie) & wave-zone atlas
    # =========================================================================
    rst_files = sorted(glob.glob(os.path.join(run_dir, "rst", f"{name}.*.rst")))
    rst_frame_dir = os.path.join(run_dir, "frames_xy_xz_fields")
    os.makedirs(rst_frame_dir, exist_ok=True)
    rst_frames = []
    valid_rsts = []

    for rpath in rst_files:
        m = re.search(r"\.(\d{5})\.rst$", rpath)
        if not m:
            continue
        idx_str = m.group(1)
        try:
            rdata = read_rst_slices(rpath, z_slice=0.001, y_slice=0.001, nco=1)
        except Exception as exc:
            print(f"[skip incomplete rst {idx_str}]: {exc}")
            continue
        t_rst = rdata["time"]

        # Match closest conH_xy slice (within 1.5 M) if present, and cross-check our 6th-order ADM H!
        matched_h = None
        for _, t_bin, _, h_blks in valid_xy_pairs:
            if abs(t_bin - t_rst) < 1.5:
                matched_h = h_blks
                break

        if matched_h is not None:
            bh_pos = rdata["tracker_pos"][0]
            sh_xy = (float(bh_pos[0]), float(bh_pos[1]))
            gx, gy, h_bin = rasterize_xy_slice(matched_h, 0, (-8.0, 8.0), (-8.0, 8.0), ngrid=160, shift=sh_xy)
            _, _, h_rst = rasterize_2d_dict(rdata["xy_blocks"], "H", (-8.0, 8.0), (-8.0, 8.0), ngrid=160, shift=sh_xy)
            XX, YY = np.meshgrid(gx, gy)
            RR = np.hypot(XX, YY)
            m_t = t_tr <= t_rst + 1e-6
            xp_c = x_rel[m_t][-1] if np.any(m_t) else x_rel[0]
            R_p = np.hypot(XX - xp_c[0], YY - xp_c[1])
            # Vacuum comparison outside BH core (r > 1.8 M) and outside particle support (r_p > 1.5 M)
            vm = (RR > 1.8) & (RR < 7.5) & (R_p > 1.5) & np.isfinite(h_bin) & np.isfinite(h_rst)
            if np.any(vm):
                med_bin = float(np.median(np.abs(h_bin[vm])))
                med_rst = float(np.median(np.abs(h_rst[vm])))
                med_diff = float(np.median(np.abs(h_rst[vm] - h_bin[vm])))
                print(
                    f"[H cross-check {name} rst {idx_str} t={t_rst:.1f} M]: "
                    f"med|H_bin|={med_bin:.3e}, med|H_rst|={med_rst:.3e}, med|diff|={med_diff:.3e}"
                )

        valid_rsts.append((idx_str, rdata, matched_h))
        fpng = os.path.join(rst_frame_dir, f"frame_{idx_str}.png")
        render_xy_xz_6var_figure(
            fpng, name, R0, q, rdata, matched_h, t_tr, x_rel, get_r_ah(t_rst), lim=8.0, dpi=150,
        )
        rst_frames.append(fpng)

    if valid_rsts:
        _, rdata_last, h_last_match = valid_rsts[-1]
        t_rst_last = rdata_last["time"]
        atlas_out = os.path.join(fig_dir, f"fig_{args.prefix}_xy_xz_fields.png")
        render_xy_xz_6var_figure(
            atlas_out, name, R0, q, rdata_last, h_last_match, t_tr, x_rel, get_r_ah(t_rst_last), lim=8.0, dpi=300,
        )
        wz_out = os.path.join(fig_dir, f"fig_{args.prefix}_xy_xz_wavezone.png")
        render_xy_xz_wavezone_figure(
            wz_out, name, R0, q, rdata_last, h_last_match, ext_radii, lim=64.0, dpi=300,
        )
        webp_rst = os.path.join(fig_dir, f"{args.prefix}_xy_xz_fields_movie.webp")
        gif_rst = os.path.join(fig_dir, f"{args.prefix}_xy_xz_fields_movie.gif")
        assemble_animation(rst_frames, webp_rst, gif_rst, args.fps_rst)
        print(
            f"Wrote {atlas_out}, {wz_out}, and {len(rst_frames)}-frame xy/xz movie "
            f"({webp_rst}, {gif_rst}) from 3D rst checkpoints up to t={t_rst_last:.1f} M"
        )


if __name__ == "__main__":
    main()
