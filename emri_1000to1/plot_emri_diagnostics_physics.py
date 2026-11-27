#!/usr/bin/env python3
"""
Generate two Cyclic-Zoom publication figures for the 1000:1 Schwarzschild EMRI NR runs:
  1) fig_emri_diagnostics.png : 2x4 multi-variable numerical diagnostics
     (Z4c constraint norms, AH mass drift, AH spin & residual, BH puncture recoil,
      NRPIC deposition vs filter conservation, wave-extraction radius convergence,
      2D equatorial lapse alpha + AMR, 2D equatorial |H| + AMR)
  2) fig_emri_physics.png     : 2x4 multi-variable EMRI physics vs 1SF / 2SF / 3.5PN
     (Areal separation R_geom(t), orbital frequency Omega(t), angular-momentum & energy
      loss vs 1SF, strong-field metric & redshift along particle worldline, Re[rPsi4_22],
      multi-mode |rPsi4_lm|, GW phase difference dPhi_22, multi-mode energy flux F_E)
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
    ffi_strain_and_dh,
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

        # Compute exact det(gamma), inverse metric g^{ij}, Lorentz factor W, -u_t
        detg = (
            gxx * (gyy * gzz - gyz * gyz)
            - gxy * (gxy * gzz - gyz * gxz)
            + gxz * (gxy * gyz - gyy * gxz)
        )
        detg = np.maximum(detg, 1e-12)
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
        minus_ut = alpha_p * W - (bx * up[:, 0] + by * up[:, 1] + bz * up[:, 2])
        beta_mag = np.sqrt(bx * bx + by * by + bz * bz)
        psi_p = detg ** (1.0 / 12.0)
        Rg = r_iso * np.sqrt(np.maximum(gzz, 1e-6))
        dtau_dt = np.gradient(tau_p, t)
        out.update({
            "Rg": Rg, "alpha_p": alpha_p, "beta_mag": beta_mag,
            "psi_p": psi_p, "W": W, "minus_ut": minus_ut, "dtau_dt": dtau_dt,
            "Lz": xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0],
        })
    else:
        out["Rg"] = r_iso * (1.0 + 0.5 / np.maximum(r_iso, 1e-6)) ** 2
        out["Lz"] = xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0]

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
    # Boyle-Mroue amplitude/phase 1/R_areal extrapolation on wave-zone spheres (r >= 27 M) for |m|==l
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


def make_diagnostics_figure(runs, vac_dir):
    cz.use_style()
    fig, axes = plt.subplots(2, 4, figsize=(13.6, 6.9))
    fig.subplots_adjust(left=0.055, right=0.950, bottom=0.082, top=0.895, wspace=0.38, hspace=0.38)

    d5 = runs["D5_nomcons_nf6"]
    e1 = runs["E1_spec_ecc1"]
    d4 = runs["D4_nf6_pcs"]
    d3 = runs["D3_nomcons"]
    e2 = runs.get("E2_ecc_nomcons_nf6")
    d8 = runs.get("D8_fdens_nf6")

    # (0,0) Z4c Constraint L2 Norms
    ax = axes[0, 0]
    z5 = d5["z4c"]
    ze1 = e1["z4c"]
    ax.semilogy(z5[:, 0], np.maximum(z5[:, 2], 1e-12), color=cz.PAL["red"], lw=1.5, label=r"$\|C\|_2$ (D5)")
    ax.semilogy(z5[:, 0], np.maximum(z5[:, 3], 1e-12), color=cz.PAL["blue"], lw=1.4, label=r"$\|H\|_2$ (D5)")
    ax.semilogy(z5[:, 0], np.maximum(z5[:, 4], 1e-12), color=cz.PAL["green"], lw=1.4, label=r"$\|M\|_2$ (D5)")
    ax.semilogy(z5[:, 0], np.maximum(z5[:, 9], 1e-12), color=cz.PAL["orange"], lw=1.3, label=r"$\|\Theta\|_2$ (D5)")
    ax.semilogy(ze1[:, 0], np.maximum(ze1[:, 2], 1e-12), color="k", ls="--", lw=1.1, alpha=0.7, label=r"$\|C\|_2$ (E1)")
    ax.set_xlim(0, 150)
    ax.set_ylim(2e-8, 3e-2)
    cz.no_minor_labels(ax, "y")
    ax.set_title("Z4c constraint norms")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Global $L_2$ norm")
    ax.legend(fontsize=7.4, ncol=2, loc="center right", bbox_to_anchor=(0.99, 0.42), columnspacing=0.8, handlelength=1.4)

    # (0,1) Apparent Horizon Mass Drift dM_AH / M0
    ax = axes[0, 1]
    ax.axhspan(-1e-4, 1e-4, color=cz.PAL["green"], alpha=0.10, lw=0)
    ax.axhline(0.0, color="k", lw=0.8, ls=":", alpha=0.5)
    for r, col, lbl, ls in [
        (d5, cz.PAL["red"], r"D5 ($\mathrm{mcons=F}, n_f=6$)", "-"),
        (d4, cz.PAL["green"], r"D4 ($\mathrm{mcons=T}, n_f=6$)", "-"),
        (d3, cz.PAL["orange"], r"D3 ($\mathrm{mcons=F}, n_f=8$)", "--"),
        (e1, cz.PAL["blue"], r"E1 (SpEC Ecc1)", "-"),
    ]:
        hs = r["hs"]
        m0 = hs[0, 2]
        ax.plot(hs[:, 1], 1e5 * (hs[:, 2] - m0) / m0, color=col, lw=1.4, ls=ls, label=lbl)
    if e2 is not None and e2["hs"] is not None and len(e2["hs"]) > 2:
        hs = e2["hs"]
        ax.plot(hs[:, 1], 1e5 * (hs[:, 2] - hs[0, 2]) / hs[0, 2], color="#8E24AA", lw=1.5, ls="-", label=r"E2 (live)")
    ax.set_xlim(0, 150)
    ax.set_ylim(-12, 12)
    ax.set_title("Apparent horizon mass drift")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,\Delta M_{\rm AH}/M_0$")
    ax.legend(fontsize=7.3, ncol=1, loc="lower right", handlelength=1.4)

    # (0,2) Horizon Spin |Sz| & Mean-Curvature Residual H_rms
    ax = axes[0, 2]
    hs5 = d5["hs"]
    hse1 = e1["hs"]
    ax.semilogy(hs5[:, 1], np.maximum(np.abs(hs5[:, 5]), 1e-11), color=cz.PAL["red"], lw=1.5, label=r"$|S_z|/M_0^2$ (D5)")
    ax.semilogy(hse1[:, 1], np.maximum(np.abs(hse1[:, 5]), 1e-11), color=cz.PAL["blue"], lw=1.3, ls="--", label=r"$|S_z|/M_0^2$ (E1)")
    ax.semilogy(hs5[:, 1], np.maximum(hs5[:, 8], 1e-11), color=cz.PAL["green"], lw=1.5, label=r"$H_{\rm rms}$ (D5)")
    ax.semilogy(hse1[:, 1], np.maximum(hse1[:, 8], 1e-11), color=cz.PAL["orange"], lw=1.2, ls=":", label=r"$H_{\rm rms}$ (E1)")
    ax.set_xlim(0, 150)
    ax.set_ylim(2e-10, 1e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_title(r"Horizon spin & finder residual")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Dimensionless residual / spin")
    ax.legend(fontsize=7.5, ncol=1, loc="lower right", handlelength=1.5)

    # (0,3) BH Puncture Recoil Spiral (x_BH, y_BH)
    ax = axes[0, 3]
    for r, col, lbl, ls in [
        (d5, cz.PAL["red"], "D5 (Ecc0)", "-"),
        (e1, cz.PAL["blue"], "E1 (SpEC Ecc1)", "--"),
    ]:
        co = r["co"]
        ax.plot(1e3 * co[:, 2], 1e3 * co[:, 3], color=col, lw=1.5, ls=ls, label=lbl)
        ax.plot(1e3 * co[-1, 2], 1e3 * co[-1, 3], "o", color=col, ms=4.5)
    ax.plot(0, 0, "k+", ms=7, mew=1.2)
    ax.set_aspect("equal")
    ax.set_xlim(-1.4, 12.6)
    ax.set_ylim(-6.8, 7.2)
    ax.set_title(r"BH puncture recoil ($q=10^{-3}$)")
    ax.set_xlabel(r"$10^3\,x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,y_{\rm BH}\,[M]$")
    ax.legend(fontsize=7.5, loc="center", bbox_to_anchor=(0.50, 0.56), handlelength=1.4)
    ax.text(0.50, 0.36, r"$r_{\rm AH}=0.93\,M$" + "\n" + r"($D_{\rm AH}/\Delta x=29.8$)",
            transform=ax.transAxes, ha="center", va="center", fontsize=7.5)

    # (1,0) NRPIC Source Conservation: Filtered vs Deposited Proper-Volume Integral
    ax = axes[1, 0]
    for r, col, lbl, ls in [
        (d4, cz.PAL["green"], r"D4 ($\mathrm{mcons=T}, n_f=6$)", "-"),
        (d5, cz.PAL["red"], r"D5 ($\mathrm{mcons=F}, n_f=6$)", "-"),
        (d3, cz.PAL["orange"], r"D3 ($\mathrm{mcons=F}, n_f=8$)", "--"),
    ]:
        n = r["nrp"]
        # col 8 = int_E (0-based), col 23 = int_E_filtered
        rel_E = 100.0 * (n[:, 23] - n[:, 8]) / np.maximum(np.abs(n[:, 8]), 1e-12)
        ax.plot(n[:, 0], rel_E, color=col, lw=1.5, ls=ls, label=lbl)
    if d8 is not None and d8["nrp"] is not None and len(d8["nrp"]) > 2:
        n8 = d8["nrp"]
        rel_E8 = 100.0 * (n8[:, 23] - n8[:, 8]) / np.maximum(np.abs(n8[:, 8]), 1e-12)
        ax.plot(n8[:, 0], rel_E8, color=cz.PAL["blue"], lw=1.7, ls="-", label=r"D8 ($\mathrm{fdens=T}$, live)")
    ax.axhline(0.0, color="k", lw=0.9, ls=":")
    ax.set_xlim(0, 150)
    ax.set_ylim(-0.27, 0.025)
    ax.set_title("NRPIC filter mass conservation")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$(E_{\rm filt}-E_{\rm dep})/E_{\rm dep}\,[\%]$")
    ax.legend(fontsize=7.3, loc="center right", handlelength=1.4)

    # (1,1) Wave-Extraction Radius Convergence & Vacuum-Twin Subtraction
    ax = axes[1, 1]
    u_inf, z_inf, by_r = extrap_mode(d5["sp_clean"], 2, 2)
    _, _, raw_by_r = extrap_mode(d5["sp_raw"], 2, 2)
    rad_cols = [cz.PAL["yellow"], cz.PAL["orange"], cz.PAL["green"], cz.PAL["blue"], cz.PAL["red"]]
    for rad, col in zip(sorted(by_r.keys()), rad_cols):
        ax.plot(u_inf, 1e5 * np.abs(by_r[rad]), color=col, lw=1.1, alpha=0.85, label=rf"$r={rad:.0f}\,M$")
    ax.plot(u_inf, 1e5 * np.abs(raw_by_r[58.0]), color="grey", lw=1.0, ls=":", alpha=0.85, label=r"Raw $58\,M$")
    ax.plot(u_inf, 1e5 * np.abs(z_inf), color="k", lw=1.6, ls="-", label=r"Extrap $\mathscr{I}^+$")
    ax.axvspan(37.8, 69.0, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.set_xlim(15, 82)
    ax.set_ylim(0.6, 3.2)
    ax.set_title(r"Extraction convergence $|r\Psi_4^{22}|$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,|r\Psi_4^{22}|$")
    ax.legend(fontsize=7.0, ncol=2, loc="upper right", columnspacing=0.6, handlelength=1.2)

    # (1,2) & (1,3) 2D Equatorial Slices (alpha_xy and conH_xy at latest t ~ 140 M)
    a_files = sorted(glob.glob(os.path.join(d5["dir"], "bin", "D5_nomcons_nf6.alpha_xy.*.bin")))
    h_files = sorted(glob.glob(os.path.join(d5["dir"], "bin", "D5_nomcons_nf6.conH_xy.*.bin")))
    t_sl, _, a_blks = read_athenak_bin(a_files[-1])
    _, _, h_blks = read_athenak_bin(h_files[-1])
    # BH and particle positions at t_sl
    ix_t = int(np.argmin(np.abs(d5["t"] - t_sl)))
    sh_xy = (float(d5["xbh"][ix_t, 0]), float(d5["xbh"][ix_t, 1]))
    xp_sl = d5["xr"][ix_t]
    r_ah_sl = float(np.interp(t_sl, d5["hs"][:, 1], d5["hs"][:, 10]))
    lim = 8.0
    gx, gy, a_img = rasterize_xy_slice(a_blks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)
    _, _, h_img = rasterize_xy_slice(h_blks, 0, (-lim, lim), (-lim, lim), ngrid=320, shift=sh_xy)

    ax = axes[1, 2]
    im_a = ax.pcolormesh(gx, gy, a_img, cmap="viridis", vmin=0.10, vmax=0.96, shading="auto", rasterized=True)
    draw_amr_blocks(ax, a_blks, (-lim, lim), (-lim, lim), shift=sh_xy)
    m_tr = d5["t"] <= t_sl + 1e-6
    ax.plot(d5["xr"][m_tr, 0], d5["xr"][m_tr, 1], color="white", lw=0.9, ls="--", alpha=0.85)
    ax.plot(xp_sl[0], xp_sl[1], "o", color=cz.PAL["red"], mec="white", mew=0.8, ms=5.5, zorder=5)
    ax.add_patch(Circle((0.0, 0.0), r_ah_sl, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim)
    ax.set_title(rf"Lapse $\alpha(x,y)$ ($t={t_sl:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y\,[M]$", labelpad=-2)
    cz.side_colorbar(fig, ax, im_a, r"$\alpha$", size="5%", pad=0.04)

    ax = axes[1, 3]
    im_h = ax.pcolormesh(gx, gy, np.maximum(np.abs(h_img), 1e-10),
                         cmap=cz.CMAP["dens"], norm=LogNorm(1e-8, 1e-2), shading="auto", rasterized=True)
    draw_amr_blocks(ax, h_blks, (-lim, lim), (-lim, lim), shift=sh_xy)
    ax.plot(d5["xr"][m_tr, 0], d5["xr"][m_tr, 1], color="cyan", lw=0.8, ls="--", alpha=0.75)
    ax.plot(xp_sl[0], xp_sl[1], "o", color="cyan", mec="black", mew=0.7, ms=5.5, zorder=5)
    ax.add_patch(Circle((0.0, 0.0), r_ah_sl, fc="black", ec="white", lw=0.9, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    cz.slice_ticks(ax, lim, show_x=True, show_y=False)
    ax.set_title(rf"$|H(x,y)|$ + AMR ($t={t_sl:.0f}\,M$)")
    ax.set_xlabel(r"$x\,[M]$", labelpad=-1)
    cz.side_colorbar(fig, ax, im_h, r"$|H|$", size="5%", pad=0.04)

    fig.suptitle(r"1000:1 Schwarzschild EMRI — Numerical Diagnostics ($R_0=6.25\,M$, $q=10^{-3}$, $\Delta x_{\rm BH}=M/16$, $\Delta x_p=M/8$)",
                 fontsize=11.5, y=0.972)
    out = os.path.join(OUT_DIR, "fig_emri_diagnostics.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Wrote {out}")


def make_physics_figure(runs):
    cz.use_style()
    ref = EMRIReferenceModel()
    R0, q = 6.25, 1e-3
    ev_1sf = ref.evolve_inspiral("1SF", R0=R0, q=q, t_max=155.0, dt=0.25)
    ev_2sf = ref.evolve_inspiral("2SF", R0=R0, q=q, t_max=155.0, dt=0.25)
    ev_pn = ref.evolve_inspiral("3.5PN", R0=R0, q=q, t_max=155.0, dt=0.25)

    d5 = runs["D5_nomcons_nf6"]
    e1 = runs["E1_spec_ecc1"]
    d4 = runs["D4_nf6_pcs"]
    d3 = runs["D3_nomcons"]
    e2 = runs.get("E2_ecc_nomcons_nf6")

    fig, axes = plt.subplots(2, 4, figsize=(13.6, 6.9))
    fig.subplots_adjust(left=0.055, right=0.985, bottom=0.082, top=0.895, wspace=0.33, hspace=0.38)

    # (0,0) Areal Separation R_geom(t)
    ax = axes[0, 0]
    ax.plot(ev_1sf["t"], ev_1sf["R"], color="k", lw=1.8, ls="--", label="Exact 1SF (RWZ)", zorder=5)
    ax.plot(d5["t"], d5["Rg"], color=cz.PAL["red"], lw=1.4, label=r"D5 (Ecc0, $\mathrm{mcons=F}, n_f=6$)")
    ax.plot(e1["t"], e1["Rg"], color=cz.PAL["blue"], lw=1.5, label=r"E1 (SpEC Ecc1, $e_R=0.003$)")
    if e2 is not None and len(e2["t"]) > 10:
        ax.plot(e2["t"], e2["Rg"], color="#8E24AA", lw=1.8, label=r"E2 (Ecc1+D5, live)")
    ax.set_xlim(0, 150)
    ax.set_ylim(6.10, 6.62)
    ax.set_title(r"Areal orbital separation $R_{\rm geom}(t)$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$R_{\rm geom}\,[M]$")
    ax.legend(fontsize=7.1, loc="upper left", handlelength=1.4)

    # (0,1) Orbital Angular Frequency Omega(t)
    ax = axes[0, 1]
    om_1sf = ev_1sf["R"] ** (-1.5) * math.sqrt(1.0 + q)
    ax.plot(ev_1sf["t"], 1e2 * om_1sf, color="k", lw=1.8, ls="--", label="Exact 1SF", zorder=5)
    ax.plot(d5["t"][d5["t"] > 5], 1e2 * d5["om"][d5["t"] > 5], color=cz.PAL["red"], lw=1.4, label="D5 (Ecc0)")
    ax.plot(e1["t"][e1["t"] > 5], 1e2 * e1["om"][e1["t"] > 5], color=cz.PAL["blue"], lw=1.5, label="E1 (SpEC Ecc1)")
    if e2 is not None and len(e2["t"]) > 10:
        m2 = e2["t"] > 5
        ax.plot(e2["t"][m2], 1e2 * e2["om"][m2], color="#8E24AA", lw=1.8, label="E2 (Ecc1+D5)")
    ax.set_xlim(0, 150)
    ax.set_ylim(5.85, 6.65)
    ax.set_title(r"Orbital angular frequency $\Omega(t)$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^2\,\Omega\,[M^{-1}]$")
    ax.legend(fontsize=7.3, loc="lower left", handlelength=1.4)

    # (0,2) Orbital Angular-Momentum Loss vs Exact 1SF
    ax = axes[0, 2]
    t0 = 30.0
    fe_1sf = float(ref.flux_1sf(R0, q=q))
    om0 = R0 ** (-1.5)
    fj_1sf = fe_1sf / om0
    m_bare_d5 = float(d5["meta"]["m_bare"])
    t_ref = np.linspace(t0, 150.0, 200)
    dLz_1sf = -(fj_1sf / m_bare_d5) * (t_ref - t0)
    ax.plot(t_ref, 1e3 * dLz_1sf, color="k", lw=1.8, ls="--", label=r"Exact 1SF (RWZ)")
    for r, col, lbl in [
        (d5, cz.PAL["red"], r"D5 ($\mathrm{mcons=F}, n_f=6$: $1.06\times$)"),
        (d4, cz.PAL["green"], r"D4 ($\mathrm{mcons=T}, n_f=6$: $0.88\times$)"),
        (d3, cz.PAL["orange"], r"D3 ($\mathrm{mcons=F}, n_f=8$: $0.70\times$)"),
        (e1, cz.PAL["blue"], r"E1 ($\mathrm{mcons=T}, n_f=8$: $0.47\times$)"),
    ]:
        m = r["t"] >= t0
        l0 = float(np.interp(t0, r["t"], r["Lz"]))
        ax.plot(r["t"][m], 1e3 * (r["Lz"][m] - l0), color=col, lw=1.45, label=lbl)
    if e2 is not None and e2["t"][-1] > 40:
        m2 = e2["t"] >= t0
        l02 = float(np.interp(t0, e2["t"], e2["Lz"]))
        ax.plot(e2["t"][m2], 1e3 * (e2["Lz"][m2] - l02), color="#8E24AA", lw=1.8, label=r"E2 (Ecc1+D5, live: $1.07\times$)")
    ax.set_xlim(30, 150)
    ax.set_ylim(-1.60, 0.12)
    ax.set_title(r"Orbital angular-momentum loss $\Delta L_z$")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,[L_z(t)-L_z(30\,M)]$")
    ax.legend(fontsize=6.8, ncol=1, loc="lower left", handlelength=1.3)

    # (0,3) Strong-Field Metric & Redshift Along Particle Worldline (trajmet.bin)
    ax = axes[0, 3]
    t5 = d5["t"]
    # Analytic Schwarzschild circular expectations at R0=6.25 M
    alpha_schw = math.sqrt(1.0 - 2.0 / R0)
    ut_inv_schw = math.sqrt(1.0 - 3.0 / R0)  # dtau/dt = 1/u^t = sqrt(1 - 3M/R)
    psi_schw = 1.0 + 0.5 / float(d5["meta"]["ic"]["r_iso"])
    ax.plot(t5, d5["psi_p"], color=cz.PAL["red"], lw=1.5, label=r"$\psi(\mathbf{x}_p)=\gamma^{1/12}$")
    ax.plot(t5, d5["alpha_p"], color=cz.PAL["blue"], lw=1.5, label=r"Lapse $\alpha(\mathbf{x}_p)$")
    ax.plot(t5[t5 > 1], d5["dtau_dt"][t5 > 1], color=cz.PAL["green"], lw=1.5, label=r"Redshift $d\tau/dt$")
    ax.plot(t5, d5["beta_mag"], color=cz.PAL["orange"], lw=1.5, label=r"Shift $|\beta^i(\mathbf{x}_p)|$")
    ax.axhline(psi_schw, color=cz.PAL["red"], lw=0.9, ls=":", alpha=0.6)
    ax.axhline(alpha_schw, color=cz.PAL["blue"], lw=0.9, ls=":", alpha=0.6)
    ax.axhline(ut_inv_schw, color=cz.PAL["green"], lw=0.9, ls=":", alpha=0.6)
    ax.set_xlim(0, 150)
    ax.set_ylim(-0.02, 1.22)
    ax.set_title("Worldline metric & redshift")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel("Dimensionless metric / redshift")
    ax.legend(fontsize=7.3, ncol=2, loc="center right", columnspacing=0.6, handlelength=1.3)

    # Waveforms for D5_nomcons_nf6 (vac-sub extrapolated) vs 1SF / 2SF / 3.5PN
    u_inf, z22, _ = extrap_mode(d5["sp_clean"], 2, 2)
    _, z33, _ = extrap_mode(d5["sp_clean"], 3, 3)
    _, z44, _ = extrap_mode(d5["sp_clean"], 4, 4)
    _, z21, _ = extrap_mode(d5["sp_clean"], 2, 1)

    u_clean_lo, u_clean_hi = 37.8, 69.0
    # Compute 1SF / 2SF / 3.5PN reference waveforms aligned at u_clean_lo
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

    # Align phase at u_clean_lo
    phi_nr = np.unwrap(np.angle(z22))
    phi_1sf = np.unwrap(np.angle(z22_1sf))
    phi_2sf = np.unwrap(np.angle(z22_2sf))
    phi_pn = np.unwrap(np.angle(z22_pn))
    # Fix sign convention of phase (choose consistent branch with decreasing phase)
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

    # (1,0) Dominant Waveform Re[rPsi4_22]
    ax = axes[1, 0]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.plot(u_inf, 1e5 * np.real(z22), color=cz.PAL["red"], lw=1.6, label="NR (D5, vac-sub)")
    ax.plot(u_inf, 1e5 * np.real(z22_1sf), color="k", lw=1.4, ls="--", label="Exact 1SF / 2SF")
    ax.plot(u_inf, 1e5 * np.real(z22_pn), color=cz.PAL["blue"], lw=1.1, ls=":", label="3.5PN")
    ax.set_xlim(22, 82)
    ax.set_ylim(-2.1, 2.1)
    ax.set_title(r"Gravitational wave $\mathrm{Re}[r\Psi_4^{22}(u)]$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^5\,\mathrm{Re}[r\Psi_4^{22}]$")
    ax.legend(fontsize=7.3, loc="upper right", handlelength=1.4)

    # (1,1) Multi-Mode Amplitudes |rPsi4_lm|
    ax = axes[1, 1]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.08, lw=0)
    for z_m, a_m, col, lbl in [
        (z22, a22_1sf, cz.PAL["red"], r"$(2,2)$ ($0.998\times$)"),
        (z33, a33_1sf, cz.PAL["blue"], r"$(3,3)$ ($0.992\times$)"),
        (z44, a44_1sf, cz.PAL["green"], r"$(4,4)$ ($0.984\times$)"),
        (z21, a21_1sf, cz.PAL["orange"], r"$(2,1)$ ($1.15\times$)"),
    ]:
        ax.semilogy(u_inf, np.maximum(np.abs(z_m), 1e-8), color=col, lw=1.5, label=lbl)
        ax.semilogy(u_inf, a_m, color=col, lw=1.1, ls="--", alpha=0.8)
    ax.set_xlim(22, 82)
    ax.set_ylim(7.0e-8, 3.8e-5)
    cz.no_minor_labels(ax, "y")
    ax.set_title(r"Multi-mode amplitudes $|r\Psi_4^{\ell m}(u)|$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|r\Psi_4^{\ell m}|$ (dashed: 1SF)")
    ax.legend(fontsize=7.0, ncol=2, loc="lower left", columnspacing=0.5, handlelength=1.2)

    # (1,2) GW Phase Difference dPhi_22(u)
    ax = axes[1, 2]
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.axhline(0.0, color="k", lw=0.9, ls=":")
    mc = (u_inf >= 35.0) & (u_inf <= 73.0)
    ax.plot(u_inf[mc], dphi_1sf[mc], color=cz.PAL["red"], lw=1.6, label=r"$\Phi_{\rm NR}-\Phi_{\rm 1SF}$")
    ax.plot(u_inf[mc], dphi_2sf[mc], color=cz.PAL["green"], lw=1.3, ls="--", label=r"$\Phi_{\rm NR}-\Phi_{\rm 2SF}$")
    ax.plot(u_inf[mc], dphi_pn[mc], color=cz.PAL["blue"], lw=1.3, ls=":", label=r"$\Phi_{\rm NR}-\Phi_{\rm 3.5PN}$")
    ax.set_xlim(35, 73)
    ax.set_ylim(-0.08, 0.11)
    ax.set_title(r"GW $(2,2)$ phase error $\Delta\Phi_{22}(u)$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\Delta\Phi_{22}\,[\mathrm{rad}]$")
    ax.legend(fontsize=7.3, loc="upper left", handlelength=1.4)
    ax.text(0.96, 0.92, r"$\Delta\Phi(69\,M)=+0.021\,\mathrm{rad}$",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.3)

    # (1,3) Multi-Mode GW Energy Flux F_E(u) vs 1SF / 2SF / 3.5PN
    ax = axes[1, 3]
    om_u = np.interp(u_inf, ev_1sf["t"], ev_1sf["Omega"])
    fe_4mode = np.zeros_like(u_inf)
    for (l, m), zm in [((2, 2), z22), ((3, 3), z33), ((4, 4), z44), ((2, 1), z21)]:
        fe_4mode += 2.0 * (np.abs(zm) ** 2) / (16.0 * math.pi * ((m * om_u) ** 2))
    fe_1sf_4m = (
        2.0 * (a22_1sf ** 2) / (16.0 * math.pi * ((2 * om_u) ** 2))
        + 2.0 * (a33_1sf ** 2) / (16.0 * math.pi * ((3 * om_u) ** 2))
        + 2.0 * (a44_1sf ** 2) / (16.0 * math.pi * ((4 * om_u) ** 2))
        + 2.0 * (a21_1sf ** 2) / (16.0 * math.pi * ((1 * om_u) ** 2))
    )
    fe_1sf_u = np.interp(u_inf, ev_1sf["t"], ev_1sf["F_E"])
    fe_2sf_u = np.interp(u_inf, ev_2sf["t"], ev_2sf["F_E"])
    fe_pn_u = np.interp(u_inf, ev_pn["t"], ev_pn["F_E"])
    ax.axvspan(u_clean_lo, u_clean_hi, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.plot(u_inf, 1e10 * fe_4mode, color=cz.PAL["red"], lw=1.6, label=r"NR 4-mode (D5)")
    ax.plot(u_inf, 1e10 * fe_1sf_4m, color=cz.PAL["orange"], lw=1.3, ls="--", label="1SF 4-mode")
    ax.plot(u_inf, 1e10 * fe_1sf_u, color="k", lw=1.5, ls="--", label=r"1SF total (all $\ell m$)")
    ax.plot(u_inf, 1e10 * fe_2sf_u, color=cz.PAL["green"], lw=1.2, ls="-.", label="2SF total")
    ax.plot(u_inf, 1e10 * fe_pn_u, color=cz.PAL["blue"], lw=1.2, ls=":", label="3.5PN total")
    ax.set_xlim(32, 75)
    ax.set_ylim(4.8, 9.6)
    ax.set_title(r"Radiated GW energy flux $F_E(u)$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^{10}\,F_E$")
    ax.legend(fontsize=7.0, ncol=2, loc="lower left", columnspacing=0.6, handlelength=1.3)

    fig.suptitle(r"1000:1 Schwarzschild EMRI — Physical Observables vs 1SF / 2SF / 3.5PN ($R_0=6.25\,M$, $q=10^{-3}$)",
                 fontsize=11.5, y=0.975)
    out = os.path.join(OUT_DIR, "fig_emri_physics.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Wrote {out}")


def main():
    vac_dir = os.path.join(RUN_ROOT, "A7_vac_twin_lean")
    runs = {}
    for nm, vd in [
        ("D5_nomcons_nf6", vac_dir),
        ("E1_spec_ecc1", vac_dir),
        ("D4_nf6_pcs", None),
        ("D3_nomcons", None),
        ("E2_ecc_nomcons_nf6", None),
        ("D8_fdens_nf6", None),
    ]:
        p = os.path.join(RUN_ROOT, nm, f"{nm}.traj.bin")
        if os.path.isfile(p):
            runs[nm] = load_run_bundle(nm, vac_dir=vd)
    make_diagnostics_figure(runs, vac_dir)
    make_physics_figure(runs)


if __name__ == "__main__":
    main()
