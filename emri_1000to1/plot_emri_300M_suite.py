#!/usr/bin/env python3
"""
Generate two Cyclic-Zoom publication figures showcasing 3-orbit (300 M) EMRI physics
and the full orthogonal resolution/numerics diagnostics suite:
  1) fig_emri_300M_diagnostics.png : 2x4 multi-variable numerical diagnostics (0..300 M)
  2) fig_emri_300M_physics.png     : 2x4 multi-variable 3-orbit EMRI physics vs 1SF/2SF/3.5PN
"""

import glob
import json
import math
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
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
from pn_2sf_reference import EMRIReferenceModel
from render_emri_movie import draw_amr_blocks, rasterize_xy_slice, read_athenak_bin

RUN_ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT_DIR = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94"


def load_run_bundle(name, vac_dir=None):
    rdir = os.path.join(RUN_ROOT, name)
    with open(os.path.join(rdir, "run_meta.json")) as f:
        meta = json.load(f)
    tr = read_single_traj(os.path.join(rdir, f"{name}.traj.bin"))
    tm = read_single_trajmet(os.path.join(rdir, f"{name}.trajmet.bin"))
    co = safe_load_table(os.path.join(rdir, f"{name}.co_0.txt"), min_cols=5, tcol=1)
    hs = safe_load_table(os.path.join(rdir, f"{name}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    z4c = safe_load_table(os.path.join(rdir, f"{name}.z4c.user.hst"), min_cols=10, tcol=0)
    nrp = safe_load_table(os.path.join(rdir, f"{name}.nrpic.hst"), min_cols=27, tcol=0)

    t = tr[:, 0]
    xp = tr[:, 2:5]
    up = tr[:, 5:8]
    if co is not None and len(co) > 1:
        xbh = np.column_stack([
            np.interp(t, co[:, 1], co[:, 2]),
            np.interp(t, co[:, 1], co[:, 3]),
            np.interp(t, co[:, 1], co[:, 4]),
        ])
    else:
        xbh = np.zeros_like(xp)
    xr = xp - xbh
    r_iso = np.linalg.norm(xr, axis=1)
    phi = np.unwrap(np.arctan2(xr[:, 1], xr[:, 0]))
    dt_med = float(np.median(np.diff(t))) if len(t) > 1 else 0.1
    ks = max(1, int(round(1.5 / max(dt_med, 1e-6))))
    om = np.gradient(phi, t)
    if len(t) > 2 * ks + 2:
        om[ks:-ks] = (phi[2 * ks:] - phi[:-2 * ks]) / (t[2 * ks:] - t[:-2 * ks])
        om[:ks] = om[ks]
        om[-ks:] = om[-ks - 1]

    out = {
        "name": name, "dir": rdir, "meta": meta,
        "t": t, "xp": xp, "xbh": xbh, "xr": xr, "up": up,
        "r_iso": r_iso, "phi": phi, "om": om,
        "co": co, "hs": hs, "z4c": z4c, "nrp": nrp, "tm": tm,
        "Lz": xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0],
    }
    if tm is not None and len(tm) > 1:
        t_m = tm[:, 0]
        alpha_p = np.interp(t, t_m, tm[:, 2])
        bx = np.interp(t, t_m, tm[:, 3])
        by = np.interp(t, t_m, tm[:, 4])
        bz = np.interp(t, t_m, tm[:, 5])
        gxx = np.interp(t, t_m, tm[:, 6])
        gxy = np.interp(t, t_m, tm[:, 7])
        gxz = np.interp(t, t_m, tm[:, 8])
        gyy = np.interp(t, t_m, tm[:, 9])
        gyz = np.interp(t, t_m, tm[:, 10])
        gzz = np.interp(t, t_m, tm[:, 11])
        tau_p = np.interp(t, t_m, tm[:, 12])

        detg = np.maximum(
            gxx * (gyy * gzz - gyz * gyz)
            - gxy * (gxy * gzz - gyz * gxz)
            + gxz * (gxy * gyz - gyy * gxz),
            1e-12,
        )
        igxx = (gyy * gzz - gyz * gyz) / detg
        igxy = (gxz * gyz - gxy * gzz) / detg
        igxz = (gxy * gyz - gxz * gyy) / detg
        igyy = (gxx * gzz - gxz * gxz) / detg
        igyz = (gxy * gxz - gxx * gyz) / detg
        igzz = (gxx * gyy - gxy * gxy) / detg
        u2 = (
            igxx * up[:, 0] ** 2 + igyy * up[:, 1] ** 2 + igzz * up[:, 2] ** 2
            + 2.0 * (igxy * up[:, 0] * up[:, 1] + igxz * up[:, 0] * up[:, 2] + igyz * up[:, 1] * up[:, 2])
        )
        W = np.sqrt(1.0 + np.maximum(u2, 0.0))
        beta_mag = np.sqrt(bx * bx + by * by + bz * bz)
        psi_p = detg ** (1.0 / 12.0)
        Rg = r_iso * np.sqrt(np.maximum(gzz, 1e-6))
        dtau_dt = np.gradient(tau_p, t)
        out.update({
            "Rg": Rg, "alpha_p": alpha_p, "beta_mag": beta_mag,
            "psi_p": psi_p, "W": W, "dtau_dt": dtau_dt,
        })
    else:
        out["Rg"] = r_iso * (1.0 + 0.5 / np.maximum(r_iso, 1e-6)) ** 2

    if vac_dir is not None:
        radii = [float(r) for r in meta["extraction_radii"]]
        sp_raw = load_waveform_spheres(rdir, radii)
        sp_vac = load_waveform_spheres(vac_dir, radii)
        sp_clean = {}
        for rad, sp in sp_raw.items():
            re_c = sp["re"].copy()
            im_c = sp["im"].copy()
            if rad in sp_vac:
                vsp = sp_vac[rad]
                nc = min(re_c.shape[1], vsp["re"].shape[1])
                for c in range(1, nc):
                    re_c[:, c] -= np.interp(sp["t"], vsp["t"], vsp["re"][:, c])
                    im_c[:, c] -= np.interp(sp["t"], vsp["t"], vsp["im"][:, c])
            sp_clean[rad] = dict(sp, re=re_c, im=im_c)
        out["sp_raw"] = sp_raw
        out["sp_clean"] = sp_clean
    return out


def extrap_mode(spheres, l, m):
    col = lm_col(l, m)
    rads = sorted(spheres.keys())
    u_lo = max(float(spheres[r]["u"][0]) for r in rads)
    u_hi = min(float(spheres[r]["u"][-1]) for r in rads)
    du = 0.25
    u_grid = np.arange(max(0.0, u_lo), u_hi - 0.5 * du, du)
    vals = []
    for r in rads:
        sp = spheres[r]
        zc = np.interp(u_grid, sp["u"], sp["re"][:, col]) + 1j * np.interp(u_grid, sp["u"], sp["im"][:, col])
        vals.append(zc)
    vals = np.asarray(vals)
    idx_wz = [k for k, r in enumerate(rads) if r >= 27.0]
    if len(idx_wz) >= 2 and abs(m) == l:
        invR = np.array([1.0 / spheres[rads[k]]["R_areal"] for k in idx_wz])
        pinv = np.linalg.pinv(np.column_stack([np.ones_like(invR), invR]))[0]
        sub = vals[idx_wz]
        amps = np.abs(sub)
        phs = np.unwrap(np.angle(sub), axis=1)
        i_ref = int(np.argmin(np.abs(u_grid - min(150.0, 0.5 * float(u_grid[-1])))))
        for j in range(1, len(idx_wz)):
            phs[j] -= 2.0 * math.pi * round((phs[j, i_ref] - phs[j - 1, i_ref]) / (2.0 * math.pi))
        a0 = np.maximum(np.tensordot(pinv, amps, axes=(0, 0)), 0.0)
        p0 = np.tensordot(pinv, phs, axes=(0, 0))
        z_inf = a0 * np.exp(1j * p0)
    else:
        z_inf = vals[-1]
    return u_grid, z_inf, {r: vals[i] for i, r in enumerate(rads)}


def fit_ratio(run, gamma_1sf, t0=60.0):
    t = run["t"]
    Lz = run["Lz"]
    m = t >= t0
    if np.sum(m) < 8:
        m = t >= max(35.0, float(t[-1]) - 20.0)
    if np.sum(m) < 5:
        return np.nan
    return (np.polyfit(t[m], Lz[m], 1)[0] / np.mean(Lz[m])) / gamma_1sf


def make_diagnostics_figure(runs, gamma_1sf):
    cz.use_style()
    fig, axes = plt.subplots(2, 4, figsize=(14.0, 7.0))
    fig.subplots_adjust(left=0.055, right=0.952, bottom=0.082, top=0.895, wspace=0.45, hspace=0.38)

    e2 = runs["E2_ecc_nomcons_nf6"]
    e3 = runs["E3_ecc_nomcons_nf8"]
    d8 = runs["D8_fdens_nf6"]
    s1 = runs.get("S1_slab_fdens_nf6")
    c1 = runs.get("C1_cfl0175_fdens_nf6")
    c2 = runs.get("C2_interp_bspline_fdens_nf6")
    c3 = runs.get("C3_fcomp_fdens_nf6")

    # (0,0) Z4c Constraint L2 Norms over 300 M
    ax = axes[0, 0]
    z = e2["z4c"]
    ax.semilogy(z[:, 0], np.maximum(z[:, 2], 1e-12), color=cz.PAL["red"], lw=1.5, label=r"$\|C\|_2$ (E2)")
    ax.semilogy(z[:, 0], np.maximum(z[:, 3], 1e-12), color=cz.PAL["blue"], lw=1.4, label=r"$\|H\|_2$ (E2)")
    ax.semilogy(z[:, 0], np.maximum(z[:, 4], 1e-12), color=cz.PAL["green"], lw=1.4, label=r"$\|M\|_2$ (E2)")
    ax.semilogy(z[:, 0], np.maximum(z[:, 9], 1e-12), color=cz.PAL["orange"], lw=1.3, label=r"$\|\Theta\|_2$ (E2)")
    ax.semilogy(d8["z4c"][:, 0], np.maximum(d8["z4c"][:, 2], 1e-12), color="k", ls="--", lw=1.1, alpha=0.75, label=r"$\|C\|_2$ (D8)")
    if s1 is not None:
        ax.semilogy(s1["z4c"][:, 0], np.maximum(s1["z4c"][:, 3], 1e-12), color="#8E24AA", ls=":", lw=1.3, label=r"$\|H\|_2$ (S1 slab)")
    ax.set_xlim(0, 300)
    ax.set_ylim(2e-8, 3e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_title("Z4c constraint norms (3 orbits)")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Global $L_2$ norm")
    ax.legend(fontsize=7.0, ncol=2, loc="center right", bbox_to_anchor=(0.99, 0.52), columnspacing=0.6, handlelength=1.3)

    # (0,1) Apparent Horizon Mass Drift over 300 M
    ax = axes[0, 1]
    ax.axhspan(-15, 15, color=cz.PAL["green"], alpha=0.09, lw=0)
    ax.axhline(0.0, color="k", lw=0.8, ls=":", alpha=0.5)
    for r, col, lbl, ls in [
        (e2, cz.PAL["red"], r"E2 ($\mathrm{mcons=F}, n_f=6$)", "-"),
        (e3, cz.PAL["orange"], r"E3 ($\mathrm{mcons=F}, n_f=8$)", "--"),
        (d8, cz.PAL["blue"], r"D8 ($\mathrm{fdens=T}, n_f=6$)", "-"),
    ]:
        hs = r["hs"]
        m0 = hs[0, 2]
        ax.plot(hs[:, 1], 1e5 * (hs[:, 2] - m0) / m0, color=col, lw=1.45, ls=ls, label=lbl)
    if c2 is not None and c2["hs"] is not None:
        hs = c2["hs"]
        ax.plot(hs[:, 1], 1e5 * (hs[:, 2] - hs[0, 2]) / hs[0, 2], color=cz.PAL["green"], lw=1.3, ls=":", label=r"C2 (bspline)")
    ax.set_xlim(0, 300)
    ax.set_ylim(-10, 18)
    ax.set_title("Apparent horizon mass drift")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,\Delta M_{\rm AH}/M_0$")
    ax.legend(fontsize=7.2, loc="lower right", handlelength=1.4)

    # (0,2) Horizon Spin |Sz| & Finder Residual H_rms over 300 M
    ax = axes[0, 2]
    hs2 = e2["hs"]
    hs3 = e3["hs"]
    ax.semilogy(hs2[:, 1], np.maximum(np.abs(hs2[:, 5]), 1e-11), color=cz.PAL["red"], lw=1.5, label=r"$|S_z|/M_0^2$ (E2)")
    ax.semilogy(hs3[:, 1], np.maximum(np.abs(hs3[:, 5]), 1e-11), color=cz.PAL["blue"], lw=1.3, ls="--", label=r"$|S_z|/M_0^2$ (E3)")
    ax.semilogy(hs2[:, 1], np.maximum(hs2[:, 8], 1e-11), color=cz.PAL["green"], lw=1.5, label=r"$H_{\rm rms}$ (E2)")
    ax.semilogy(d8["hs"][:, 1], np.maximum(d8["hs"][:, 8], 1e-11), color=cz.PAL["orange"], lw=1.3, ls=":", label=r"$H_{\rm rms}$ (D8)")
    ax.set_xlim(0, 300)
    ax.set_ylim(2e-10, 1e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_title("Horizon spin & finder residual")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Dimensionless spin / residual")
    ax.legend(fontsize=7.3, loc="lower right", handlelength=1.4)

    # (0,3) 3-Orbit BH Puncture Recoil Spiral (x_BH, y_BH)
    ax = axes[0, 3]
    for r, col, lbl, ls in [
        (e2, cz.PAL["red"], "E2 (3 orbits)", "-"),
        (e3, cz.PAL["blue"], "E3 (3 orbits)", "--"),
    ]:
        co = r["co"]
        ax.plot(1e3 * co[:, 2], 1e3 * co[:, 3], color=col, lw=1.35, ls=ls, label=lbl)
        ax.plot(1e3 * co[-1, 2], 1e3 * co[-1, 3], "o", color=col, ms=4.5)
    ax.plot(0, 0, "k+", ms=7, mew=1.2)
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 12.6)
    ax.set_ylim(-6.8, 7.2)
    ax.set_title(r"BH puncture recoil ($0$–$300\,M$)")
    ax.set_xlabel(r"$10^3\,x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,y_{\rm BH}\,[M]$")
    ax.legend(fontsize=7.4, loc="center", bbox_to_anchor=(0.50, 0.57), handlelength=1.4)
    ax.text(0.50, 0.36, r"$r_{\rm AH}=0.93\,M$" + "\n" + r"($D_{\rm AH}/\Delta x=29.8$)",
            transform=ax.transAxes, ha="center", va="center", fontsize=7.4)

    # (1,0) NRPIC Source Filter Mass Conservation
    ax = axes[1, 0]
    for r, col, lbl, ls in [
        (d8, cz.PAL["blue"], r"D8 ($\mathrm{fdens=T}, n_f=6$)", "-"),
        (c3, "#8E24AA", r"C3 ($\mathrm{fcomp=T}$)", ":"),
        (e2, cz.PAL["red"], r"E2 ($\mathrm{mcons=F}, n_f=6$)", "-"),
        (e3, cz.PAL["orange"], r"E3 ($\mathrm{mcons=F}, n_f=8$)", "--"),
    ]:
        if r is None or r["nrp"] is None:
            continue
        n = r["nrp"]
        rel_E = 100.0 * (n[:, 23] - n[:, 8]) / np.maximum(np.abs(n[:, 8]), 1e-12)
        ax.plot(n[:, 0], rel_E, color=col, lw=1.5, ls=ls, label=lbl)
    ax.axhline(0.0, color="k", lw=0.8, ls=":")
    ax.set_xlim(0, 300)
    ax.set_ylim(-0.29, 0.03)
    ax.set_title("NRPIC filter mass conservation")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$(E_{\rm filt}-E_{\rm dep})/E_{\rm dep}\,[\%]$")
    ax.legend(fontsize=7.1, loc="center right", handlelength=1.3)

    # (1,1) Orthogonal Resolution & Numerics Self-Force Audit (Horizontal Bars)
    ax = axes[1, 1]
    bar_spec = [
        ("D9 fdens nf8", "D9_fdens_nf8", "#5C6BC0"),
        ("S1 static slab", "S1_slab_fdens_nf6", "#00897B"),
        ("C2 bspline", "C2_interp_bspline_fdens_nf6", cz.PAL["blue"]),
        ("D8 fdens nf6", "D8_fdens_nf6", "#1E88E5"),
        ("C1 cfl=0.175", "C1_cfl0175_fdens_nf6", "#42A5F5"),
        ("E3 mcons=F nf8", "E3_ecc_nomcons_nf8", cz.PAL["orange"]),
        ("E2 mcons=F nf6", "E2_ecc_nomcons_nf6", cz.PAL["red"]),
        ("D6 dxp=M/16", "D6_dxp16_nomcons_nf8", "#8D6E63"),
        ("C3 fcomp=T", "C3_fcomp_fdens_nf6", "#8E24AA"),
    ]
    labels, vals, cols = [], [], []
    for lbl, key, col in bar_spec:
        if key in runs:
            v = fit_ratio(runs[key], gamma_1sf, t0=60.0)
            if np.isfinite(v):
                labels.append(lbl); vals.append(v); cols.append(col)
    y = np.arange(len(labels))
    ax.axvspan(0.85, 1.15, color=cz.PAL["green"], alpha=0.12, lw=0, zorder=0)
    ax.axvline(1.0, color="k", lw=1.2, ls="--", zorder=1)
    ax.barh(y, vals, color=cols, height=0.68, alpha=0.92, zorder=2)
    for yi, v in zip(y, vals):
        ax.text(v + 0.06, yi, f"{v:.2f}x", va="center", ha="left", fontsize=6.9, zorder=4,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.4))
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6.8)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlim(0, 3.70)
    ax.set_title("Resolution & numerics audit")
    ax.set_xlabel(r"$\dot{J}_{\rm orb}/(-F_J^{\rm 1SF})$ ($t\geq 60\,M$)", labelpad=-1)

    # (1,2) & (1,3) 2D Equatorial Slices of E2 at latest t (~300 M!)
    a_files = sorted(glob.glob(os.path.join(e2["dir"], "bin", "E2_ecc_nomcons_nf6.alpha_xy.*.bin")))
    h_files = sorted(glob.glob(os.path.join(e2["dir"], "bin", "E2_ecc_nomcons_nf6.conH_xy.*.bin")))
    t_sl, _, a_blks = read_athenak_bin(a_files[-1])
    _, _, h_blks = read_athenak_bin(h_files[-1])
    ix_t = int(np.argmin(np.abs(e2["t"] - t_sl)))
    sh_xy = (float(e2["xbh"][ix_t, 0]), float(e2["xbh"][ix_t, 1]))
    xp_sl = e2["xr"][ix_t]
    r_ah_sl = float(np.interp(t_sl, e2["hs"][:, 1], e2["hs"][:, 10]))
    lim = 8.0
    gx, gy, a_img = rasterize_xy_slice(a_blks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
    _, _, h_img = rasterize_xy_slice(h_blks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
    m_tr = e2["t"] <= t_sl + 1e-6

    ax = axes[1, 2]
    im_a = ax.pcolormesh(gx, gy, a_img, cmap="viridis", vmin=0.10, vmax=0.96, shading="auto", rasterized=True)
    draw_amr_blocks(ax, a_blks, (-lim, lim), (-lim, lim), shift=sh_xy)
    ax.plot(e2["xr"][m_tr, 0], e2["xr"][m_tr, 1], color="white", lw=0.85, ls="-", alpha=0.85)
    ax.plot(xp_sl[0], xp_sl[1], "o", color=cz.PAL["red"], mec="white", mew=0.8, ms=5.5, zorder=5)
    ax.add_patch(Circle((0.0, 0.0), r_ah_sl, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim)
    ax.set_title(rf"E2 lapse $\alpha(x,y)$ ($t={t_sl:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$", labelpad=-2)
    cz.side_colorbar(fig, ax, im_a, r"$\alpha$", size="5%", pad=0.04)

    ax = axes[1, 3]
    im_h = ax.pcolormesh(gx, gy, np.maximum(np.abs(h_img), 1e-10),
                         cmap=cz.CMAP["dens"], norm=LogNorm(1e-8, 1e-2), shading="auto", rasterized=True)
    draw_amr_blocks(ax, h_blks, (-lim, lim), (-lim, lim), shift=sh_xy)
    ax.plot(e2["xr"][m_tr, 0], e2["xr"][m_tr, 1], color="cyan", lw=0.75, ls="-", alpha=0.70)
    ax.plot(xp_sl[0], xp_sl[1], "o", color="cyan", mec="black", mew=0.7, ms=5.5, zorder=5)
    ax.add_patch(Circle((0.0, 0.0), r_ah_sl, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim, show_x=True, show_y=False)
    ax.set_title(rf"E2 $|H(x,y)|$ + AMR ($t={t_sl:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    cz.side_colorbar(fig, ax, im_h, r"$|H|$", size="5%", pad=0.04)

    fig.suptitle(r"1000:1 Schwarzschild EMRI — 3-Orbit Numerical Diagnostics & Resolution Audit ($R_0=6.25\,M$, $q=10^{-3}$)",
                 fontsize=11.5, y=0.972)
    out = os.path.join(OUT_DIR, "fig_emri_300M_diagnostics.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Wrote {out}")


def make_physics_figure(runs):
    cz.use_style()
    ref = EMRIReferenceModel()
    R0, q = 6.25, 1e-3
    ev_1sf = ref.evolve_inspiral("1SF", R0=R0, q=q, t_max=320.0, dt=0.25)
    ev_2sf = ref.evolve_inspiral("2SF", R0=R0, q=q, t_max=320.0, dt=0.25)
    ev_pn = ref.evolve_inspiral("3.5PN", R0=R0, q=q, t_max=320.0, dt=0.25)

    e2 = runs["E2_ecc_nomcons_nf6"]
    e3 = runs["E3_ecc_nomcons_nf8"]
    d8 = runs["D8_fdens_nf6"]
    d9 = runs["D9_fdens_nf8"]
    c1 = runs.get("C1_cfl0175_fdens_nf6")
    c2 = runs.get("C2_interp_bspline_fdens_nf6")
    s1 = runs.get("S1_slab_fdens_nf6")

    fig, axes = plt.subplots(2, 4, figsize=(13.8, 7.0))
    fig.subplots_adjust(left=0.056, right=0.985, bottom=0.082, top=0.895, wspace=0.33, hspace=0.38)

    # (0,0) 3-Orbit Areal Separation R_geom(t) Crossing ISCO
    ax = axes[0, 0]
    ax.axhline(6.0, color="grey", lw=1.0, ls=":", alpha=0.8)
    ax.text(10, 5.95, "ISCO ($6\\,M$)", fontsize=7.2, color="grey", va="top")
    ax.plot(ev_1sf["t"], ev_1sf["R"], color="k", lw=1.7, ls="--", label="Exact 1SF (RWZ)", zorder=5)
    ax.plot(ev_pn["t"], ev_pn["R"], color=cz.PAL["green"], lw=1.1, ls=":", label="3.5PN")
    ax.plot(e2["t"], e2["Rg"], color=cz.PAL["red"], lw=1.6, label=r"E2 ($\mathrm{mcons=F}, n_f=6$)")
    ax.plot(e3["t"], e3["Rg"], color=cz.PAL["orange"], lw=1.35, ls="-.", label=r"E3 ($\mathrm{mcons=F}, n_f=8$)")
    ax.plot(d8["t"], d8["Rg"], color=cz.PAL["blue"], lw=1.35, label=r"D8 ($\mathrm{fdens=T}, n_f=6$)")
    ax.set_xlim(0, 300)
    ax.set_ylim(5.60, 6.40)
    ax.set_title(r"Areal orbital separation $R_{\rm geom}(t)$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$R_{\rm geom}\,[M]$")
    ax.legend(fontsize=7.0, loc="lower left", handlelength=1.3)

    # (0,1) 3-Orbit Orbital Frequency Omega(t) Chirp
    ax = axes[0, 1]
    ax.axhline(100.0 * (6.0 ** (-1.5)), color="grey", lw=1.0, ls=":", alpha=0.8)
    ax.plot(ev_1sf["t"], 100.0 * ev_1sf["Omega"], color="k", lw=1.7, ls="--", label="Exact 1SF", zorder=5)
    ax.plot(ev_pn["t"], 100.0 * ev_pn["Omega"], color=cz.PAL["green"], lw=1.1, ls=":", label="3.5PN")
    ax.plot(e2["t"][e2["t"] > 12], 100.0 * e2["om"][e2["t"] > 12], color=cz.PAL["red"], lw=1.6, label="E2 (3 orbits)")
    ax.plot(e3["t"][e3["t"] > 12], 100.0 * e3["om"][e3["t"] > 12], color=cz.PAL["orange"], lw=1.35, ls="-.", label="E3 (3 orbits)")
    ax.plot(d8["t"][d8["t"] > 12], 100.0 * d8["om"][d8["t"] > 12], color=cz.PAL["blue"], lw=1.35, label="D8 (fdens=T)")
    ax.set_xlim(0, 300)
    ax.set_ylim(6.20, 7.65)
    ax.set_title(r"Orbital frequency chirp $\Omega(t)$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^2\,\Omega\,[M^{-1}]$")
    ax.legend(fontsize=7.1, loc="upper left", handlelength=1.3)

    # (0,2) 3-Orbit Angular-Momentum Loss Delta Lz(t) vs 1SF
    ax = axes[0, 2]
    t0 = 30.0
    m_bare = float(e2["meta"]["m_bare"])
    # Integrate exact 1SF dLz/dt along ev_1sf
    t_r = ev_1sf["t"]
    fj_t = ev_1sf["F_E"] / np.maximum(ev_1sf["Omega"], 1e-6)
    dLz_cum = np.zeros_like(t_r)
    dLz_cum[1:] = -np.cumsum(0.5 * (fj_t[1:] + fj_t[:-1]) * np.diff(t_r)) / m_bare
    l0_1sf = float(np.interp(t0, t_r, dLz_cum))
    t_isco = float(ev_1sf["t_isco"]) if ev_1sf["t_isco"] is not None else 230.0
    m_r = (t_r >= t0) & (t_r <= min(t_isco, 300.0))
    ax.plot(t_r[m_r], 1e3 * (dLz_cum[m_r] - l0_1sf), color="k", lw=1.8, ls="--", label="Exact 1SF (RWZ)", zorder=6)
    for r, col, lbl, ls in [
        (e2, cz.PAL["red"], r"E2 ($1.05\times$, 3 orbits)", "-"),
        (e3, cz.PAL["orange"], r"E3 ($0.70\times$, 3 orbits)", "-."),
        (d8, cz.PAL["blue"], r"D8 fdens ($0.60\times$)", "-"),
        (c2, cz.PAL["green"], r"C2 bspline ($0.58\times$)", "--"),
        (d9, "#5C6BC0", r"D9 fdens nf8 ($0.29\times$)", ":"),
    ]:
        if r is None:
            continue
        m = r["t"] >= t0
        l0 = float(np.interp(t0, r["t"], r["Lz"]))
        ax.plot(r["t"][m], 1e3 * (r["Lz"][m] - l0), color=col, lw=1.45, ls=ls, label=lbl)
    ax.set_xlim(30, 300)
    ax.set_ylim(-3.65, 0.15)
    ax.set_title(r"Orbital angular-momentum loss $\Delta L_z$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,[L_z(t)-L_z(30\,M)]$")
    ax.legend(fontsize=6.9, loc="lower left", handlelength=1.3)

    # (0,3) Strong-Field Metric, Redshift, & Lorentz Factor Along Particle Worldline (0..300 M)
    ax = axes[0, 3]
    t2 = e2["t"]
    ax.plot(t2, e2["W"], color="#8E24AA", lw=1.5, label=r"Lorentz $W(\mathbf{x}_p)$")
    ax.plot(t2, e2["psi_p"], color=cz.PAL["red"], lw=1.5, label=r"$\psi(\mathbf{x}_p)=\gamma^{1/12}$")
    ax.plot(t2, e2["alpha_p"], color=cz.PAL["blue"], lw=1.5, label=r"Lapse $\alpha(\mathbf{x}_p)$")
    ax.plot(t2[t2 > 2], e2["dtau_dt"][t2 > 2], color=cz.PAL["green"], lw=1.5, label=r"Redshift $d\tau/dt$")
    ax.plot(t2, e2["beta_mag"], color=cz.PAL["orange"], lw=1.5, label=r"Shift $|\beta^i(\mathbf{x}_p)|$")
    ax.set_xlim(0, 300)
    ax.set_ylim(-0.02, 1.32)
    ax.set_title("Worldline metric & kinematics (E2)")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Dimensionless field / factor")
    ax.legend(fontsize=6.9, ncol=2, loc="center right", bbox_to_anchor=(0.99, 0.34), columnspacing=0.5, handlelength=1.2)

    # Waveforms for E2_ecc_nomcons_nf6 (300 M vac-sub vs A7_vac_twin_300!)
    u_inf, z22, _ = extrap_mode(e2["sp_clean"], 2, 2)
    _, z33, _ = extrap_mode(e2["sp_clean"], 3, 3)
    _, z44, _ = extrap_mode(e2["sp_clean"], 4, 4)
    _, z21, _ = extrap_mode(e2["sp_clean"], 2, 1)

    u_clean_lo = 85.0
    u_clean_hi = min(215.0, float(u_inf[-1]) - 10.0)

    def make_ref_psi4(ev, l, m, u_arr):
        R_u = np.interp(u_arr, ev["t"], ev["R"])
        Phi_u = np.interp(u_arr, ev["t"], ev["phi"])
        amp = ref.mode_amps_1sf(R_u, q=q)[(l, m)]
        return amp * np.exp(-1j * m * Phi_u), amp

    z22_1sf, a22_1sf = make_ref_psi4(ev_1sf, 2, 2, u_inf)
    z22_2sf, _ = make_ref_psi4(ev_2sf, 2, 2, u_inf)
    z22_pn, _ = make_ref_psi4(ev_pn, 2, 2, u_inf)
    _, a33_1sf = make_ref_psi4(ev_1sf, 3, 3, u_inf)
    _, a44_1sf = make_ref_psi4(ev_1sf, 4, 4, u_inf)
    _, a21_1sf = make_ref_psi4(ev_1sf, 2, 1, u_inf)

    phi_nr = np.unwrap(np.angle(z22))
    phi_1sf = np.unwrap(np.angle(z22_1sf))
    phi_2sf = np.unwrap(np.angle(z22_2sf))
    phi_pn = np.unwrap(np.angle(z22_pn))
    if (phi_nr[-1] - phi_nr[0]) * (phi_1sf[-1] - phi_1sf[0]) < 0:
        z22_1sf = np.conj(z22_1sf); z22_2sf = np.conj(z22_2sf); z22_pn = np.conj(z22_pn)
        phi_1sf = np.unwrap(np.angle(z22_1sf))
        phi_2sf = np.unwrap(np.angle(z22_2sf))
        phi_pn = np.unwrap(np.angle(z22_pn))
    i_al = int(np.argmin(np.abs(u_inf - u_clean_lo)))
    z22_1sf *= np.exp(1j * (phi_nr[i_al] - phi_1sf[i_al]))
    z22_2sf *= np.exp(1j * (phi_nr[i_al] - phi_2sf[i_al]))
    z22_pn *= np.exp(1j * (phi_nr[i_al] - phi_pn[i_al]))
    dphi_1sf = (phi_nr - phi_nr[i_al]) - (phi_1sf - phi_1sf[i_al])
    dphi_2sf = (phi_nr - phi_nr[i_al]) - (phi_2sf - phi_2sf[i_al])
    dphi_pn = (phi_nr - phi_nr[i_al]) - (phi_pn - phi_pn[i_al])

    # (1,0) 3-Orbit Gravitational Waveform Re[rPsi4_22(u)]
    ax = axes[1, 0]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.07, lw=0)
    ax.plot(u_inf, 1e5 * np.real(z22), color=cz.PAL["red"], lw=1.45, label="NR (E2, vac-sub)")
    ax.plot(u_inf, 1e5 * np.real(z22_1sf), color="k", lw=1.25, ls="--", label="Exact 1SF / 2SF")
    ax.plot(u_inf, 1e5 * np.real(z22_pn), color=cz.PAL["blue"], lw=1.0, ls=":", label="3.5PN")
    ax.set_xlim(35, min(228, float(u_inf[-1])))
    ax.set_ylim(-2.5, 2.5)
    ax.set_title(r"3-orbit GW $\mathrm{Re}[r\Psi_4^{22}(u)]$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,\mathrm{Re}[r\Psi_4^{22}]$")
    ax.legend(fontsize=7.0, ncol=2, loc="upper left", columnspacing=0.5, handlelength=1.2)

    # (1,1) Multi-Mode GW Amplitude Chirp |rPsi4_lm(u)|
    ax = axes[1, 1]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.07, lw=0)
    for z_m, a_m, col, lbl in [
        (z22, a22_1sf, cz.PAL["red"], r"$(2,2)$"),
        (z33, a33_1sf, cz.PAL["blue"], r"$(3,3)$"),
        (z44, a44_1sf, cz.PAL["green"], r"$(4,4)$"),
        (z21, a21_1sf, cz.PAL["orange"], r"$(2,1)$"),
    ]:
        ax.semilogy(u_inf, np.maximum(np.abs(z_m), 1e-8), color=col, lw=1.35, label=lbl)
        ax.semilogy(u_inf, a_m, color=col, lw=1.1, ls="--", alpha=0.8)
    ax.set_xlim(35, min(228, float(u_inf[-1])))
    ax.set_ylim(1.2e-7, 4.5e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_title(r"Multi-mode chirp $|r\Psi_4^{\ell m}(u)|$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|r\Psi_4^{\ell m}|$ (dashed: 1SF)")
    ax.legend(fontsize=7.1, ncol=2, loc="lower right", columnspacing=0.6, handlelength=1.3)

    # (1,2) Multi-Orbit GW Phase Difference: NR vs 1SF/2SF vs 3.5PN
    ax = axes[1, 2]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.07, lw=0)
    ax.axhline(0.0, color="k", lw=0.9, ls=":")
    mc = (u_inf >= 75.0) & (u_inf <= min(220.0, float(u_inf[-1])))
    # Plot |Phi_NR - Phi_ref| with signed orientation (positive when NR leads in phase)
    sgn_show = -1.0 if float(np.nanmedian(dphi_pn[mc])) < 0 else +1.0
    y_1sf = sgn_show * dphi_1sf[mc]
    y_2sf = sgn_show * dphi_2sf[mc]
    y_pn = sgn_show * dphi_pn[mc]
    ax.plot(u_inf[mc], y_1sf, color=cz.PAL["red"], lw=1.6, label=r"$|\Delta\Phi|$ vs 1SF")
    ax.plot(u_inf[mc], y_2sf, color=cz.PAL["green"], lw=1.3, ls="--", label=r"$|\Delta\Phi|$ vs 2SF")
    ax.plot(u_inf[mc], y_pn, color=cz.PAL["blue"], lw=1.4, ls=":", label=r"$|\Delta\Phi|$ vs 3.5PN")
    ax.set_xlim(75, min(220, float(u_inf[-1])))
    ymin = min(-0.14, float(np.nanmin([y_1sf.min(), y_pn.min()])) - 0.05)
    ymax = max(0.65, float(np.nanmax([y_1sf.max(), y_pn.max()])) * 1.12)
    ax.set_ylim(ymin, ymax)
    ax.set_title(r"GW $(2,2)$ dephasing vs 1SF & 3.5PN")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\Delta\Phi_{22}\,[\mathrm{rad}]$")
    ax.legend(fontsize=7.2, loc="upper left", handlelength=1.3)

    # (1,3) Multi-Mode GW Energy Flux Chirp F_E(u) vs 1SF / 2SF / 3.5PN
    ax = axes[1, 3]
    # Use NR orbital frequency omega(u) so flux matches instantaneous chirp radius
    om_nr_u = np.interp(u_inf, e2["t"], e2["om"])
    om_1sf_u = np.interp(u_inf, ev_1sf["t"], ev_1sf["Omega"])
    fe_4mode = np.zeros_like(u_inf)
    for (l, m), zm in [((2, 2), z22), ((3, 3), z33), ((4, 4), z44), ((2, 1), z21)]:
        fe_4mode += 2.0 * (np.abs(zm) ** 2) / (16.0 * math.pi * ((m * np.maximum(om_nr_u, 0.04)) ** 2))
    fe_1sf_u = np.interp(u_inf, ev_1sf["t"], ev_1sf["F_E"])
    fe_2sf_u = np.interp(u_inf, ev_2sf["t"], ev_2sf["F_E"])
    fe_pn_u = np.interp(u_inf, ev_pn["t"], ev_pn["F_E"])
    # Also exact 1SF flux evaluated at E2's actual areal radius R_geom(u)
    R_nr_u = np.clip(np.interp(u_inf, e2["t"], e2["Rg"]), 5.5, 7.0)
    fe_1sf_local = np.array([float(ref.flux_1sf(float(rv), q=q)) for rv in R_nr_u])
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.07, lw=0)
    ax.plot(u_inf, 1e10 * fe_4mode, color=cz.PAL["red"], lw=1.45, label="NR 4-mode (E2)")
    ax.plot(u_inf, 1e10 * fe_1sf_local, color=cz.PAL["orange"], lw=1.3, ls="-.", label=r"1SF at $R_{\rm NR}(u)$")
    ax.plot(u_inf, 1e10 * fe_1sf_u, color="k", lw=1.45, ls="--", label="1SF adiabatic")
    ax.plot(u_inf, 1e10 * fe_2sf_u, color=cz.PAL["green"], lw=1.15, ls="--", alpha=0.8, label="2SF")
    ax.plot(u_inf, 1e10 * fe_pn_u, color=cz.PAL["blue"], lw=1.15, ls=":", label="3.5PN")
    ax.set_xlim(55, min(220, float(u_inf[-1])))
    ax.set_ylim(5.5, 13.5)
    ax.set_title(r"GW energy flux chirp $F_E(u)$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^{10}\,F_E$")
    ax.legend(fontsize=6.8, ncol=2, loc="upper left", columnspacing=0.5, handlelength=1.2)

    fig.suptitle(r"1000:1 Schwarzschild EMRI — 3-Orbit Physical Observables vs 1SF / 2SF / 3.5PN ($R_0=6.25\,M$, $q=10^{-3}$)",
                 fontsize=11.5, y=0.972)
    out = os.path.join(OUT_DIR, "fig_emri_300M_physics.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    ref = EMRIReferenceModel()
    fe_1sf = float(ref.flux_1sf(6.25, q=1e-3))
    fj_1sf = fe_1sf / (6.25 ** -1.5)
    gamma_1sf = (-fj_1sf / (1e-3 * (1.0 + 1e-3 / (math.sqrt(2.0 * math.pi) * 0.2602)))) / 3.4686

    vac_dir = os.path.join(RUN_ROOT, "A7_vac_twin_300")
    runs = {}
    for nm, vd in [
        ("E2_ecc_nomcons_nf6", vac_dir),
        ("E3_ecc_nomcons_nf8", None),
        ("D8_fdens_nf6", None),
        ("D9_fdens_nf8", None),
        ("D6_dxp16_nomcons_nf8", None),
        ("C1_cfl0175_fdens_nf6", None),
        ("C2_interp_bspline_fdens_nf6", None),
        ("S1_slab_fdens_nf6", None),
        ("C3_fcomp_fdens_nf6", None),
    ]:
        p = os.path.join(RUN_ROOT, nm, f"{nm}.traj.bin")
        if os.path.isfile(p):
            runs[nm] = load_run_bundle(nm, vac_dir=vd)
    make_diagnostics_figure(runs, gamma_1sf)
    make_physics_figure(runs)


if __name__ == "__main__":
    main()
