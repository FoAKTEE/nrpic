#!/usr/bin/env python3
"""
Generate Cyclic-Zoom publication Diagnostics & 2D Multi-Field Physics Slices figure
for the converged Iteration 6 Variational GR-PIC EMRI hero run (P1_iter6_M16_bssn_varpic_600)
with P3 (M/8) & P4 (Z4c) convergence overlays and exact vacuum-subtracted (P1 - P2) 2D spiral rPsi4!
"""
import glob
import math
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
from matplotlib.patches import Circle
import numpy as np

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
    read_single_traj,
    read_single_trajmet,
    safe_load_table,
)
from plot_bugs6to10_varpic import read_bin_xy
from plot_emri_diagnostics_physics import extrap_mode

ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94/fig_iter6_diagnostics_2d_fields.png"


def rasterize_mbs(mbs, xlim, ylim, ngrid=320, shift=(0.0, 0.0), var_idx=0):
    """Paint AMR MeshBlocks (coarsest to finest) onto a uniform 2D equatorial grid."""
    x0, x1 = xlim
    y0, y1 = ylim
    sx, sy = shift
    gx = np.linspace(x0, x1, ngrid)
    gy = np.linspace(y0, y1, ngrid)
    img = np.full((ngrid, ngrid), np.nan, dtype=np.float64)
    # Sort blocks by cell size descending so finer levels overwrite coarser levels cleanly
    ordered = sorted(mbs, key=lambda item: (item[0][1] - item[0][0]) / item[1].shape[3], reverse=True)
    for geom, dat in ordered:
        bx0, bx1, by0, by1 = geom[0] - sx, geom[1] - sx, geom[2] - sy, geom[3] - sy
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
            continue
        arr = dat[var_idx]
        nz, ny, nx = arr.shape
        sl = arr[nz // 2]
        ix = np.where((gx >= bx0) & (gx <= bx1))[0]
        iy = np.where((gy >= by0) & (gy <= by1))[0]
        if len(ix) == 0 or len(iy) == 0:
            continue
        fx = np.clip(((gx[ix] - bx0) / (bx1 - bx0) * nx).astype(int), 0, nx - 1)
        fy = np.clip(((gy[iy] - by0) / (by1 - by0) * ny).astype(int), 0, ny - 1)
        img[np.ix_(iy, ix)] = sl[np.ix_(fy, fx)]
    return gx, gy, img


def draw_amr_boxes(ax, mbs, xlim, ylim, shift=(0.0, 0.0), color="white", alpha=0.22, lw=0.45):
    x0, x1 = xlim
    y0, y1 = ylim
    sx, sy = shift
    for geom, _ in mbs:
        bx0, bx1, by0, by1 = geom[0] - sx, geom[1] - sx, geom[2] - sy, geom[3] - sy
        if bx1 < x0 or bx0 > x1 or by1 < y0 or by0 > y1:
            continue
        ax.plot([bx0, bx1, bx1, bx0, bx0], [by0, by0, by1, by1, by0],
                color=color, alpha=alpha, lw=lw)


def pick_slice(rdir, prefix, target_t=None):
    files = sorted(glob.glob(os.path.join(rdir, "bin", f"{prefix}.*.bin")))
    if not files:
        return None, None, None
    if target_t is None:
        f = files[-1]
        t_sl, mbs = read_bin_xy(f)
        return f, t_sl, mbs
    best = None
    best_dt = 1e30
    for f in files:
        t_sl, _ = read_bin_xy(f)
        if abs(t_sl - target_t) < best_dt:
            best_dt = abs(t_sl - target_t)
            best = f
    t_sl, mbs = read_bin_xy(best)
    return best, t_sl, mbs


def main():
    cz.use_style()
    p1_dir = os.path.join(ROOT, "P1_iter6_M16_bssn_varpic_600")
    p2_dir = os.path.join(ROOT, "P2_iter6_M16_bssn_vac_600")
    p3_dir = os.path.join(ROOT, "P3_iter6_M8_bssn_varpic_600")
    p4_dir = os.path.join(ROOT, "P4_iter6_M16_z4c_varpic_600")

    z1 = safe_load_table(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.z4c.user.hst"), min_cols=10, tcol=0)
    z2 = safe_load_table(os.path.join(p2_dir, "P2_iter6_M16_bssn_vac_600.z4c.user.hst"), min_cols=10, tcol=0)
    z3 = safe_load_table(os.path.join(p3_dir, "P3_iter6_M8_bssn_varpic_600.z4c.user.hst"), min_cols=10, tcol=0)
    z4 = safe_load_table(os.path.join(p4_dir, "P4_iter6_M16_z4c_varpic_600.z4c.user.hst"), min_cols=10, tcol=0)

    tr1 = read_single_traj(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.traj.bin"))
    tm1 = read_single_trajmet(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.trajmet.bin"))
    co1 = safe_load_table(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.co_0.txt"), min_cols=5, tcol=1)
    hs1 = safe_load_table(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.horizon_summary_0.txt"), min_cols=12, tcol=1)
    nrp1 = safe_load_table(os.path.join(p1_dir, "P1_iter6_M16_bssn_varpic_600.nrpic.hst"), min_cols=27, tcol=0)

    t1 = tr1[:, 0]
    xbh1 = np.column_stack([np.interp(t1, co1[:, 1], co1[:, j]) for j in (2, 3, 4)])
    xr1 = tr1[:, 2:5] - xbh1
    t_end_z = float(z1[-1, 0])

    fig, axes = plt.subplots(2, 4, figsize=(14.8, 7.4))
    fig.subplots_adjust(left=0.050, right=0.945, bottom=0.078, top=0.900, wspace=0.45, hspace=0.36)

    # --- (0,0) Global ADM Constraint L2 Norms & 2x Resolution Convergence ---
    ax = axes[0, 0]
    ax.semilogy(z3[:, 0], np.maximum(z3[:, 3], 1e-12), color=cz.PAL["orange"], lw=1.35, ls="--", label=r"$\|\mathcal{H}\|_2$ P3 ($M/8$)")
    ax.semilogy(z1[:, 0], np.maximum(z1[:, 3], 1e-12), color=cz.PAL["red"],    lw=1.65, label=r"$\|\mathcal{H}\|_2$ P1 ($M/16$)")
    ax.semilogy(z4[:, 0], np.maximum(z4[:, 3], 1e-12), color=cz.PAL["green"],  lw=1.35, ls="-.", label=r"$\|\mathcal{H}\|_2$ P4 Z4c")
    ax.semilogy(z1[:, 0], np.maximum(z1[:, 4], 1e-12), color=cz.PAL["blue"],   lw=1.35, label=r"$\|\mathcal{M}\|_2$ P1 ($M/16$)")
    ax.semilogy(z2[:, 0], np.maximum(z2[:, 3], 1e-12), color="0.45",           lw=1.1, ls=":", label=r"$\|\mathcal{H}\|_2$ P2 vac")
    ax.set_xlim(0, max(t_end_z, 100.0))
    ax.set_ylim(3e-6, 2e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_title("Constraint Convergence (BSSN & Z4c)")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Global $L_2$ norm")
    ax.legend(frameon=False, fontsize=6.6, ncol=2, loc="upper right", columnspacing=0.5, handlelength=1.3)

    # --- (0,1) BH Puncture Recoil Spiral & Variational Conservation ---
    ax = axes[0, 1]
    ax.plot(1e3 * co1[:, 2], 1e3 * co1[:, 3], color=cz.PAL["red"], lw=1.3, label=r"P1 BH recoil ($q=10^{-3}$)")
    ax.plot(1e3 * co1[-1, 2], 1e3 * co1[-1, 3], "o", color=cz.PAL["red"], ms=4.5)
    ax.plot(0, 0, "k+", ms=7, mew=1.2)
    ax.set_aspect("equal")
    rmax_bh = max(8.0, 1.2 * float(np.max(np.hypot(1e3 * co1[:, 2], 1e3 * co1[:, 3]))))
    ax.set_xlim(-0.4 * rmax_bh, 1.15 * rmax_bh)
    ax.set_ylim(-0.78 * rmax_bh, 0.78 * rmax_bh)
    ax.set_title("SMBH Recoil & Source Conservation")
    ax.set_xlabel(r"$10^3\,x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,y_{\rm BH}\,[M]$")
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.3)
    # Report exact variational energy conservation |E_filt - E_dep|/E_dep
    if nrp1 is not None and len(nrp1) > 2:
        m_act = nrp1[:, 8] > 1e-8
        max_rel = float(np.max(np.abs(nrp1[m_act, 23] - nrp1[m_act, 8]) / nrp1[m_act, 8])) if np.any(m_act) else 0.0
        ax.text(0.04, 0.05, rf"$\max|E_{{\rm filt}}/E - 1| = {max_rel:.1e}$",
                transform=ax.transAxes, fontsize=7.0)

    # --- (0,2) Strong-Field Metric & Redshift Along Particle Worldline ---
    ax = axes[0, 2]
    alpha_p = np.interp(t1, tm1[:, 0], tm1[:, 2])
    bx = np.interp(t1, tm1[:, 0], tm1[:, 3])
    by = np.interp(t1, tm1[:, 0], tm1[:, 4])
    bz = np.interp(t1, tm1[:, 0], tm1[:, 5])
    gxx = np.interp(t1, tm1[:, 0], tm1[:, 6])
    gxy = np.interp(t1, tm1[:, 0], tm1[:, 7])
    gxz = np.interp(t1, tm1[:, 0], tm1[:, 8])
    gyy = np.interp(t1, tm1[:, 0], tm1[:, 9])
    gyz = np.interp(t1, tm1[:, 0], tm1[:, 10])
    gzz = np.interp(t1, tm1[:, 0], tm1[:, 11])
    tau_p = np.interp(t1, tm1[:, 0], tm1[:, 12])
    detg = np.maximum(gxx * (gyy * gzz - gyz**2) - gxy * (gxy * gzz - gyz * gxz) + gxz * (gxy * gyz - gyy * gxz), 1e-12)
    psi_p = detg ** (1.0 / 12.0)
    beta_mag = np.sqrt(bx**2 + by**2 + bz**2)
    dtau_dt = np.gradient(tau_p, t1)
    ax.plot(t1, alpha_p, color=cz.PAL["red"], lw=1.5, label=r"Lapse $\alpha(\mathbf{x}_p)$")
    ax.plot(t1, dtau_dt, color=cz.PAL["blue"], lw=1.5, label=r"Redshift $d\tau/dt$")
    ax.plot(t1, psi_p,   color=cz.PAL["green"], lw=1.4, label=r"Conformal $\psi(\mathbf{x}_p)$")
    ax.plot(t1, beta_mag, color=cz.PAL["orange"], lw=1.4, label=r"Shift $|\boldsymbol{\beta}(\mathbf{x}_p)|$")
    ax.axhline(math.sqrt(1.0 - 3.0 / 6.25), color=cz.PAL["blue"], lw=0.9, ls=":", alpha=0.7)
    ax.set_xlim(0, max(float(t1[-1]), 60.0))
    ax.set_ylim(0.0, 1.55)
    ax.set_title("Strong-Field Worldline Metric")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Dimensionless metric fields")
    ax.legend(frameon=False, fontsize=6.7, ncol=2, loc="upper left", columnspacing=0.5, handlelength=1.3)

    # --- (0,3) Extraction Radius Convergence & I+ Extrapolation (P1 - P2) ---
    ax = axes[0, 3]
    radii = [20.0, 27.0, 38.0, 48.0, 58.0]
    sp_raw = load_waveform_spheres(p1_dir, radii)
    sp_vac = load_waveform_spheres(p2_dir, radii)
    sp_clean = {}
    for rad, sp in sp_raw.items():
        if rad not in sp_vac:
            continue
        vsp = sp_vac[rad]
        tm_c = min(sp["t"][-1], vsp["t"][-1])
        mc = sp["t"] <= tm_c + 1e-9
        if np.sum(mc) < 5 or float(sp["u"][mc][-1]) < 5.0:
            continue
        re_c = sp["re"][mc].copy()
        im_c = sp["im"][mc].copy()
        for c in range(1, min(re_c.shape[1], vsp["re"].shape[1])):
            re_c[:, c] -= np.interp(sp["t"][mc], vsp["t"], vsp["re"][:, c])
            im_c[:, c] -= np.interp(sp["t"][mc], vsp["t"], vsp["im"][:, c])
        sp_clean[rad] = dict(sp, t=sp["t"][mc], u=sp["u"][mc], re=re_c, im=im_c)
    if len(sp_clean) >= 2:
        u_inf, z_inf, by_r = extrap_mode(sp_clean, 2, 2)
    elif len(sp_clean) == 1:
        r0 = next(iter(sp_clean))
        u_inf = sp_clean[r0]["u"]
        col22 = lm_col(2, 2)
        z_inf = sp_clean[r0]["re"][:, col22] + 1j * sp_clean[r0]["im"][:, col22]
        by_r = {r0: z_inf}
    else:
        u_inf = np.array([20.0, 60.0])
        z_inf = np.zeros_like(u_inf, dtype=complex)
        by_r = {}
    rad_cols = [cz.PAL["yellow"], cz.PAL["orange"], cz.PAL["green"], cz.PAL["blue"], cz.PAL["red"]]
    for rad, col in zip(sorted(by_r.keys()), rad_cols):
        ax.plot(u_inf, 1e5 * np.abs(by_r[rad]), color=col, lw=1.0, alpha=0.85, label=rf"$r={rad:.0f}\,M$")
    ax.plot(u_inf, 1e5 * np.abs(z_inf), color="k", lw=1.5, label=r"Extrap $\mathscr{I}^+$")
    ax.axhline(1.560, color="0.4", lw=1.0, ls="--", alpha=0.7)
    ax.set_xlim(20.0, max(float(u_inf[-1]), 60.0))
    ymax_e = max(3.0, 1.15 * float(np.max(1e5 * np.abs(z_inf[u_inf >= 20.0])))) if np.any(u_inf >= 20.0) else 3.5
    ax.set_ylim(0.0, ymax_e)
    ax.set_title(r"Extraction Convergence $|r\Psi_4^{22}|$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,|r\Psi_4^{22}|$")
    ax.legend(frameon=False, fontsize=6.6, ncol=2, loc="upper left", columnspacing=0.5, handlelength=1.2)

    # --- Pick best late-inspiral / pre-plunge time for 2D near-field panels (1,0)-(1,3) ---
    t_near_target = min(float(t1[-1]) - 10.0, max(40.0, 0.85 * float(t1[-1])))
    _, t_a, a_mbs = pick_slice(p1_dir, "P1_iter6_M16_bssn_varpic_600.alpha_xy", target_t=t_near_target)
    _, t_h, h_mbs = pick_slice(p1_dir, "P1_iter6_M16_bssn_varpic_600.conH_xy", target_t=t_a)
    _, t_e, e_mbs = pick_slice(p1_dir, "P1_iter6_M16_bssn_varpic_600.tmunuE_xy", target_t=t_near_target)
    _, t_k, k_mbs = pick_slice(p1_dir, "P1_iter6_M16_bssn_varpic_600.Khat_xy", target_t=t_e)

    def state_at(t_sl):
        ix = int(np.argmin(np.abs(t1 - t_sl)))
        sh = (float(xbh1[ix, 0]), float(xbh1[ix, 1]))
        xp = xr1[ix]
        rah = float(np.interp(t_sl, hs1[:, 1], hs1[:, 10])) if (hs1 is not None and len(hs1)) else 0.93
        return sh, xp, rah

    lim = 8.0
    sh_a, xp_a, rah_a = state_at(t_a)
    gx, gy, a_img = rasterize_mbs(a_mbs, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_a)
    _, _, h_img = rasterize_mbs(h_mbs, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_a)

    # --- (1,0) 2D Lapse alpha(x,y) + AMR ---
    ax = axes[1, 0]
    im_a = ax.pcolormesh(gx, gy, a_img, cmap="viridis", vmin=0.10, vmax=0.96, shading="auto", rasterized=True)
    draw_amr_boxes(ax, a_mbs, (-lim, lim), (-lim, lim), shift=sh_a)
    m_tr = t1 <= t_a + 1e-6
    ax.plot(xr1[m_tr, 0], xr1[m_tr, 1], color="white", lw=0.8, ls="--", alpha=0.8)
    ax.plot(xp_a[0], xp_a[1], "o", color=cz.PAL["red"], mec="white", mew=0.8, ms=5.0, zorder=5)
    ax.add_patch(Circle((0, 0), rah_a, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim)
    ax.set_title(rf"Lapse $\alpha(x,y)$ ($t={t_a:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$", labelpad=-2)
    cz.side_colorbar(fig, ax, im_a, r"$\alpha$", size="5%", pad=0.04)

    # --- (1,1) 2D Hamiltonian Constraint |H(x,y)| ---
    ax = axes[1, 1]
    im_h = ax.pcolormesh(gx, gy, np.maximum(np.abs(h_img), 1e-10),
                         cmap=cz.CMAP["dens"], norm=LogNorm(1e-8, 1e-2), shading="auto", rasterized=True)
    draw_amr_boxes(ax, h_mbs, (-lim, lim), (-lim, lim), shift=sh_a)
    ax.plot(xp_a[0], xp_a[1], "o", color="cyan", mec="black", mew=0.7, ms=5.0, zorder=5)
    ax.add_patch(Circle((0, 0), rah_a, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim, show_x=True, show_y=False)
    ax.set_title(rf"$|\mathcal{{H}}(x,y)|$ ($t={t_h:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    cz.side_colorbar(fig, ax, im_h, r"$|\mathcal{H}|$", size="5%", pad=0.04)

    # --- (1,2) 2D Zoomed Spherical-Gaussian Variational Cloud E(x,y) ---
    ax = axes[1, 2]
    sh_e, xp_e, rah_e = state_at(t_e)
    plim = 1.0
    ex, ey, e_img = rasterize_mbs(e_mbs, (xp_e[0] - plim, xp_e[0] + plim),
                                  (xp_e[1] - plim, xp_e[1] + plim), ngrid=240, shift=sh_e)
    im_e = ax.pcolormesh(ex - xp_e[0], ey - xp_e[1], np.maximum(e_img, 1e-11),
                         cmap="inferno", norm=LogNorm(1e-8, 1e-1), shading="auto", rasterized=True)
    ax.plot(0.0, 0.0, "+", color="cyan", ms=7, mew=1.2, zorder=5)
    ax.add_patch(Circle((0, 0), 0.129, fill=False, ec="cyan", ls="--", lw=0.9, alpha=0.85))
    ax.add_patch(Circle((0, 0), 3.0 * 0.129, fill=False, ec="white", ls=":", lw=0.8, alpha=0.7))
    ax.set_aspect("equal")
    ax.set_xlim(-plim, plim); ax.set_ylim(-plim, plim)
    ax.set_title(rf"Var.-PIC Cloud $E$ ($t={t_e:.0f}\,M$)")
    ax.set_xlabel(r"$x-x_p\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y-y_p\,[M]$", labelpad=-2)
    cz.side_colorbar(fig, ax, im_e, r"$E\;[M^{-2}]$", size="5%", pad=0.04)

    # --- (1,3) 2D Extrinsic Curvature Trace Khat(x,y) ---
    ax = axes[1, 3]
    sh_k, xp_k, rah_k = state_at(t_k)
    kx, ky, k_img = rasterize_mbs(k_mbs, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_k)
    im_k = ax.pcolormesh(kx, ky, k_img, cmap="RdBu_r",
                         norm=SymLogNorm(linthresh=3e-4, linscale=0.6, vmin=-0.12, vmax=0.25),
                         shading="auto", rasterized=True)
    draw_amr_boxes(ax, k_mbs, (-lim, lim), (-lim, lim), shift=sh_k, color="k", alpha=0.16)
    m_trk = t1 <= t_k + 1e-6
    ax.plot(xr1[m_trk, 0], xr1[m_trk, 1], color="k", lw=0.75, ls="--", alpha=0.65)
    ax.plot(xp_k[0], xp_k[1], "o", color=cz.PAL["green"], mec="k", mew=0.7, ms=5.0, zorder=5)
    ax.add_patch(Circle((0, 0), rah_k, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim, show_x=True, show_y=False)
    ax.set_title(rf"Curvature $\hat{{K}}(x,y)$ ($t={t_k:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    cz.side_colorbar(fig, ax, im_k, r"$\hat{K}\;[M^{-1}]$", size="5%", pad=0.04)

    fig.suptitle(r"Converged Variational GR-PIC 1000:1 EMRI — Diagnostics, Convergence & Multi-Field Equatorial Slices (P1, $M/16$)",
                 fontsize=11.4, y=0.970)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
