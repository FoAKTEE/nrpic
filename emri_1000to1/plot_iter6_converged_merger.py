#!/usr/bin/env python3
"""
Generate Cyclic-Zoom publication physics figure for the converged Iteration 6
Variational GR-PIC (Bug 7/8/10/11/12 fixed) EMRI full inspiral -> ISCO -> plunge ->
merger -> Kerr QNM ringdown suite:
  - P8 (Hero M/16 BSSN SpEC Ecc2, vac-sub P2_780)
  - P9 (M/16 Z4c SpEC Ecc2 formulation twin, vac-sub P5_880)
  - P1 (M/16 BSSN, vac-sub P2_780)
  - P4 (M/16 Z4c, vac-sub P5_880)
  - P7 (2x coarser M/8 BSSN convergence twin, vac-sub K15_920)
"""
import math
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from scipy.optimize import least_squares

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

ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94/fig_iter6_converged_merger_physics.png"


def stitch_tables(tables, tcol):
    out = None
    for a in tables:
        if a is None or len(a) == 0:
            continue
        if out is None:
            out = a.copy()
        else:
            if a[0, tcol] <= out[0, tcol] + 1.0 and a[-1, tcol] >= out[-1, tcol]:
                out = a.copy()
            else:
                m = a[:, tcol] > out[-1, tcol] + 1e-9
                if np.any(m):
                    out = np.vstack([out, a[m]])
    return out


def load_stitched_run(dir_list, base_name, q, vac_dir=None, radii=(20.0, 27.0, 38.0, 48.0, 58.0)):
    dirs = [os.path.join(ROOT, d) for d in dir_list]
    tr = stitch_tables([read_single_traj(os.path.join(d, f"{base_name}.traj.bin")) for d in dirs], 0)
    tm = stitch_tables([read_single_trajmet(os.path.join(d, f"{base_name}.trajmet.bin")) for d in dirs], 0)
    co = stitch_tables([safe_load_table(os.path.join(d, f"{base_name}.co_0.txt"), min_cols=5, tcol=1) for d in dirs], 1)
    hs = stitch_tables([safe_load_table(os.path.join(d, f"{base_name}.horizon_summary_0.txt"), min_cols=12, tcol=1) for d in dirs], 1)
    z4c = stitch_tables([safe_load_table(os.path.join(d, f"{base_name}.z4c.user.hst"), min_cols=10, tcol=0) for d in dirs], 0)

    t = tr[:, 0]
    xp = tr[:, 2:5]
    up = tr[:, 5:8]
    if co is not None and len(co) > 1:
        xbh = np.column_stack([np.interp(t, co[:, 1], co[:, j]) for j in (2, 3, 4)])
    else:
        xbh = np.zeros_like(xp)
    xr = xp - xbh
    r_iso = np.linalg.norm(xr, axis=1)
    gzz = np.interp(t, tm[:, 0], tm[:, 11])
    Rg = r_iso * np.sqrt(np.maximum(gzz, 1e-6))
    phi = np.unwrap(np.arctan2(xr[:, 1], xr[:, 0]))
    Lz = xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0]
    t_z4c = float(z4c[-1, 0]) if (z4c is not None and len(z4c)) else float(t[-1])
    excised = (t_z4c - float(t[-1])) > 1.5

    sp_clean = {}
    if vac_dir is not None:
        # Final dir already has full appended waveforms
        sp_raw = load_waveform_spheres(dirs[-1], list(radii))
        sp_vac = load_waveform_spheres(os.path.join(ROOT, vac_dir), list(radii))
        for rad, sp in sp_raw.items():
            if rad not in sp_vac:
                continue
            vsp = sp_vac[rad]
            t_max = min(sp["t"][-1], vsp["t"][-1])
            mc = sp["t"] <= t_max + 1e-9
            re_c = sp["re"][mc].copy()
            im_c = sp["im"][mc].copy()
            nc = min(re_c.shape[1], vsp["re"].shape[1])
            for c in range(1, nc):
                re_c[:, c] -= np.interp(sp["t"][mc], vsp["t"], vsp["re"][:, c])
                im_c[:, c] -= np.interp(sp["t"][mc], vsp["t"], vsp["im"][:, c])
            sp_clean[rad] = {
                "t": sp["t"][mc],
                "u": sp["u"][mc],
                "R_areal": sp["R_areal"],
                "re": re_c,
                "im": im_c,
            }

    return {
        "name": dir_list[-1], "q": q, "t": t, "t_z4c": t_z4c, "excised": excised,
        "xr": xr, "r_iso": r_iso, "Rg": Rg, "phi": phi, "Lz": Lz,
        "co": co, "hs": hs, "z4c": z4c, "sp_clean": sp_clean,
    }


def fit_two_mode_qnm(u, z, u0, u1, w_init=0.34, g_init=0.075):
    """Unbiased 2-mode (prograde + retrograde) Kerr QNM least-squares fit."""
    m = (u >= u0) & (u <= u1)
    if np.sum(m) < 12:
        return np.nan, np.nan, np.array([0j, 0j]), np.nan
    uu = u[m] - u0
    zz = z[m]
    scale = max(float(np.max(np.abs(zz))), 1e-30)
    zz_n = zz / scale

    def solve_lin(w, g):
        M = np.column_stack([np.exp((-1j * w - g) * uu), np.exp((+1j * w - g) * uu)])
        coef, _, _, _ = np.linalg.lstsq(M, zz_n, rcond=None)
        return coef, M @ coef

    def res(p):
        _, zfit = solve_lin(p[0], p[1])
        d = zfit - zz_n
        return np.concatenate([d.real, d.imag])

    sol = least_squares(res, [w_init, g_init], bounds=([0.20, 0.02], [0.55, 0.20]),
                        ftol=1e-12, xtol=1e-12, gtol=1e-12)
    w_fit, g_fit = float(sol.x[0]), float(sol.x[1])
    coef_n, zfit_n = solve_lin(w_fit, g_fit)
    rel_rms = float(np.linalg.norm(zfit_n - zz_n) / max(np.linalg.norm(zz_n), 1e-30))
    return w_fit, g_fit, coef_n * scale, rel_rms


def mode_at_r(run, l, m, rad=38.0):
    sp = run["sp_clean"][rad]
    col = lm_col(l, m)
    return sp["u"], sp["re"][:, col] + 1j * sp["im"][:, col]


def main():
    cz.use_style()
    p8 = load_stitched_run(
        ["P8_iter6_M16_bssn_ecc2_450", "P8_iter6_M16_bssn_ecc2_600_exc030"],
        "P8_iter6_M16_bssn_ecc2_450", 1e-3, "P2_iter6_M16_bssn_vac_780",
    )
    p9 = load_stitched_run(
        ["P9_iter6_M16_z4c_ecc2_450", "P9_iter6_M16_z4c_ecc2_650_exc030"],
        "P9_iter6_M16_z4c_ecc2_450", 1e-3, "P5_iter6_M16_z4c_vac_880",
    )
    p1 = load_stitched_run(
        ["P1_iter6_M16_bssn_varpic_600", "P1_iter6_M16_bssn_varpic_780_exc030"],
        "P1_iter6_M16_bssn_varpic_600", 1e-3, "P2_iter6_M16_bssn_vac_780",
    )
    p4 = load_stitched_run(
        ["P4_iter6_M16_z4c_varpic_600", "P4_iter6_M16_z4c_varpic_780", "P4_iter6_M16_z4c_varpic_880_exc030"],
        "P4_iter6_M16_z4c_varpic_600", 1e-3, "P5_iter6_M16_z4c_vac_880",
    )
    p7 = load_stitched_run(
        ["P7_iter6_M8_bssn_uy1002_600", "P7_iter6_M8_bssn_uy1002_780", "P7_iter6_M8_bssn_uy1002_920_exc030"],
        "P7_iter6_M8_bssn_uy1002_600", 1e-3, "K15_iter6_M8_bssn_q0_vac920",
    )

    hero = p8
    q_h = hero["q"]
    ref = EMRIReferenceModel()
    ev_1sf = ref.evolve_inspiral("1SF", R0=6.25, q=1e-3, t_max=500.0, dt=0.25)

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.4))
    fig.subplots_adjust(left=0.062, right=0.980, bottom=0.080, top=0.905, wspace=0.29, hspace=0.35)

    # --- (0,0) Equatorial Inspiral & Plunge Orbit (P8 Hero) ---
    ax = axes[0, 0]
    m_ins = hero["Rg"] >= 6.0
    m_plg = hero["Rg"] < 6.0
    ax.plot(hero["xr"][m_ins, 0], hero["xr"][m_ins, 1], color=cz.PAL["blue"], lw=1.15, label=r"Inspiral ($R\geq 6\,M$)")
    ax.plot(hero["xr"][m_plg, 0], hero["xr"][m_plg, 1], color=cz.PAL["red"], lw=1.65, label=r"Plunge ($R<6\,M$)")
    ax.plot(hero["xr"][0, 0], hero["xr"][0, 1], "o", color=cz.PAL["green"], ms=4.8, zorder=5, label=r"$t=0$ ($6.25\,M$)")
    ax.plot(hero["xr"][-1, 0], hero["xr"][-1, 1], "x", color="k", ms=6.5, mew=1.6, zorder=6,
            label=rf"Excised ($t={hero['t'][-1]:.1f}\,M$)")
    ax.add_patch(Circle((0, 0), 4.949, fill=False, ec="grey", ls="--", lw=0.9, alpha=0.7))
    ax.add_patch(Circle((0, 0), 1.866, fill=False, ec=cz.PAL["orange"], ls=":", lw=1.0, alpha=0.85))
    r_ah = float(hero["hs"][-1, 10])
    ax.add_patch(Circle((0, 0), r_ah, fc="black", ec="white", lw=0.8, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-6.8, 6.8); ax.set_ylim(-6.4, 8.6)
    ax.set_title(r"Equatorial Inspiral & Plunge (P8 $M/16$)")
    ax.set_xlabel(r"$x-x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y-y_{\rm BH}\,[M]$")
    ax.legend(frameon=False, fontsize=6.7, ncol=2, loc="upper center", columnspacing=0.6, handlelength=1.2)

    # --- (0,1) Areal Separation R_geom(t) Across Formulation & Resolution ---
    ax = axes[0, 1]
    ax.axhline(6.0, color="grey", lw=0.9, ls="--", alpha=0.7)
    ax.axhline(3.0, color=cz.PAL["orange"], lw=0.9, ls=":", alpha=0.8)
    ax.text(15, 5.72, r"ISCO ($6\,M$)", fontsize=7.0, color="grey")
    ax.text(15, 3.12, r"Light ring ($3\,M$)", fontsize=7.0, color=cz.PAL["orange"])
    ax.plot(ev_1sf["t"][ev_1sf["R"] >= 6.0], ev_1sf["R"][ev_1sf["R"] >= 6.0],
            color="k", lw=1.4, ls="--", label="Exact 1SF (to ISCO)")
    ax.plot(p8["t"], p8["Rg"], color=cz.PAL["red"],    lw=1.75, label=r"P8 BSSN Ecc2 ($M/16$)")
    ax.plot(p9["t"], p9["Rg"], color=cz.PAL["green"],  lw=1.45, ls="-.", label=r"P9 Z4c Ecc2 ($M/16$)")
    ax.plot(p1["t"], p1["Rg"], color=cz.PAL["blue"],   lw=1.25, ls="--", alpha=0.85, label=r"P1 BSSN ($M/16$)")
    ax.plot(p4["t"], p4["Rg"], color="0.45",           lw=1.15, ls=":",  alpha=0.9, label=r"P4 Z4c ($M/16$)")
    ax.plot(p7["t"], p7["Rg"], color=cz.PAL["orange"], lw=1.20, ls="--", alpha=0.85, label=r"P7 BSSN ($M/8$)")
    ax.set_xlim(0, max(float(p7["t"][-1]) + 25.0, 520.0))
    ax.set_ylim(1.2, 6.68)
    ax.set_title("Areal Separation Across Suite")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$R_{\rm geom}\,[M]$")
    ax.legend(frameon=False, fontsize=6.5, ncol=2, loc="lower left", columnspacing=0.5, handlelength=1.3)

    # --- (0,2) Remnant BH Mass Jump & Final Kerr Spin Across Merger (Aligned to t - t_exc) ---
    ax = axes[0, 2]
    ax.axhline(0.9428, color=cz.PAL["red"], lw=1.0, ls="--", alpha=0.65, label=r"GR $E_{\rm ISCO}=0.943$")
    ax.axhline(3.15,   color=cz.PAL["blue"], lw=1.0, ls=":", alpha=0.70, label=r"GR $L_{\rm ISCO}-\Delta J_{\rm plg}$")
    ax.axvline(0.0, color="k", lw=0.8, ls="-.", alpha=0.45)
    for run, col_m, col_s, ls, tag in [
        (p8, cz.PAL["red"],    cz.PAL["blue"],  "-",  "P8 BSSN"),
        (p4, cz.PAL["orange"], cz.PAL["green"], "--", "P4 Z4c"),
        (p7, "0.30",           "0.55",          ":",  "P7 $M/8$"),
    ]:
        if not run["excised"]:
            continue
        hs = run["hs"]
        t_exc = float(run["t"][-1])
        t_rel = hs[:, 1] - t_exc
        m_pre = float(np.interp(max(hs[0, 1], t_exc - 20.0), hs[:, 1], hs[:, 2]))
        dM_q = (hs[:, 2] - m_pre) / run["q"]
        af_q = (hs[:, 5] / (hs[:, 2] ** 2)) / run["q"]
        lw = 1.6 if run is p8 else 1.25
        ax.plot(t_rel, dM_q, color=col_m, lw=lw, ls=ls, label=rf"$\Delta M_{{\rm AH}}/q$ {tag}")
        ax.plot(t_rel, af_q, color=col_s, lw=lw, ls=ls, label=rf"$a_f/(M_f q)$ {tag}")
    ax.set_xlim(-35, 95)
    ax.set_ylim(-0.35, 4.35)
    ax.set_title("Remnant BH Mass & Spin Conservation")
    ax.set_xlabel(r"Time relative to horizon entry $t - t_{\rm exc}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\Delta M_{\rm AH}/(q M_0),\; a_f/(q M_f)$")
    ax.legend(frameon=False, fontsize=6.3, ncol=2, loc="center right",
              bbox_to_anchor=(0.995, 0.54), columnspacing=0.5, handlelength=1.2)

    # --- (1,0) Full Vac-Subtracted Inspiral-Merger-Ringdown Re[rPsi4_22] / q (P8 Hero) ---
    ax = axes[1, 0]
    u8, z22_8 = mode_at_r(p8, 2, 2, 38.0)
    ax.plot(u8, np.real(z22_8) / q_h, color=cz.PAL["red"], lw=1.15, label=r"P8 $\mathrm{Re}[r\Psi_4^{22}]/q$ ($r=38\,M$)")
    ax.plot(u8, np.abs(z22_8) / q_h,  color="k", lw=1.0, ls="--", alpha=0.65, label=r"Envelope $|r\Psi_4^{22}|/q$")
    m_pk = u8 > 440.0
    i_pk = np.where(m_pk)[0][np.argmax(np.abs(z22_8[m_pk]))]
    u_pk = float(u8[i_pk])
    pk_val = float(np.abs(z22_8[i_pk]) / q_h)
    ax.axvline(u_pk, color="grey", lw=0.9, ls=":", alpha=0.7)
    ax.set_xlim(35.0, float(u8[-1]))
    ax.set_ylim(-1.18 * pk_val, 1.18 * pk_val)
    ax.set_title(r"Full Inspiral–Merger–Ringdown $r\Psi_4^{22}/q$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$r\Psi_4^{22}/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.3)
    ax.text(0.04, 0.06, rf"$10\times$ chirp: $0.0156 \to {pk_val:.3f}$",
            transform=ax.transAxes, fontsize=7.3)

    # --- (1,1) Zoomed Merger & Unbiased Kerr (2,+/-2,0) QNM Ringdown Fit ---
    ax = axes[1, 1]
    u0_f = u_pk + 8.0
    u1_f = min(u_pk + 44.0, float(u8[-1]))
    w_fit, g_fit, coef_qnm, qnm_rms = fit_two_mode_qnm(u8, z22_8, u0_f, u1_f)
    Mf = float(hero["hs"][-1, 2])
    af = float(hero["hs"][-1, 5]) / (Mf * Mf)
    w_kerr = (0.37367 + 0.0628 * af) / Mf
    g_kerr = (0.08896 - 0.0005 * af) / Mf
    print(f"P8 r=38M unbiased QNM [{u0_f:.1f},{u1_f:.1f}]: w={w_fit:.5f} vs Kerr {w_kerr:.5f} ({100*(w_fit-w_kerr)/w_kerr:+.2f}%), "
          f"g={g_fit:.5f} vs Kerr {g_kerr:.5f} ({100*(g_fit-g_kerr)/g_kerr:+.2f}%), "
          f"|A-|/|A+|={abs(coef_qnm[1])/max(abs(coef_qnm[0]),1e-30):.3f}, rms={qnm_rms:.4f}")

    uz_lo, uz_hi = u_pk - 42.0, min(float(u8[-1]), u_pk + 56.0)
    mz = (u8 >= uz_lo) & (u8 <= uz_hi)
    ax.plot(u8[mz], np.real(z22_8[mz]) / q_h, color=cz.PAL["red"], lw=1.6, label=r"NR P8 $\mathrm{Re}[r\Psi_4^{22}]/q$")
    # Overlay P4 Z4c time-shifted to merger peak if merged!
    if p4["excised"]:
        u4, z22_4 = mode_at_r(p4, 2, 2, 38.0)
        mp4 = u4 > float(p4["t"][-1]) - 30.0
        if np.any(mp4):
            ip4 = np.where(mp4)[0][np.argmax(np.abs(z22_4[mp4]))]
            dt4 = u_pk - float(u4[ip4])
            # Align phase at peak
            dphi = np.angle(z22_8[i_pk]) - np.angle(z22_4[ip4])
            u4s = u4 + dt4
            m4z = (u4s >= uz_lo) & (u4s <= uz_hi)
            ax.plot(u4s[m4z], np.real(z22_4[m4z] * np.exp(1j * dphi)) / p4["q"],
                    color=cz.PAL["green"], lw=1.15, ls=":", alpha=0.9, label=r"NR P4 Z4c (aligned)")
    uq = u8[(u8 >= u0_f) & (u8 <= min(u_pk + 48.0, float(u8[-1])))]
    z_qnm = (coef_qnm[0] * np.exp((-1j * w_fit - g_fit) * (uq - u0_f))
             + coef_qnm[1] * np.exp((+1j * w_fit - g_fit) * (uq - u0_f)))
    ax.plot(uq, np.real(z_qnm) / q_h, color="k", lw=1.4, ls="--", label=r"Kerr $(2,\pm 2,0)$ fit")
    ax.axvspan(u0_f, u1_f, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.set_xlim(uz_lo, uz_hi)
    ax.set_ylim(-1.18 * pk_val, 1.18 * pk_val)
    ax.set_title(r"Merger & Kerr $(2,2,0)$ QNM Ringdown")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\mathrm{Re}[r\Psi_4^{22}]/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=6.9, loc="upper left", handlelength=1.3)
    ax.text(0.97, 0.05,
            rf"$M\omega_{{220}}={w_fit:.4f}$ (Kerr ${w_kerr:.4f}$)" + "\n"
            + rf"$M/\tau_{{220}}={g_fit:.4f}$ (Kerr ${g_kerr:.4f}$)" + "\n"
            + rf"RMS $= {100*qnm_rms:.1f}\%$",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.0)

    # --- (1,2) Multi-Mode Hierarchy |rPsi4_lm| / q ---
    ax = axes[1, 2]
    for (l, m), col, lbl in [
        ((2, 2), cz.PAL["red"],    r"$(2,2)$"),
        ((3, 3), cz.PAL["blue"],   r"$(3,3)$"),
        ((4, 4), cz.PAL["green"],  r"$(4,4)$"),
        ((2, 1), cz.PAL["orange"], r"$(2,1)$"),
    ]:
        um, zm = mode_at_r(hero, l, m, 38.0)
        ax.semilogy(um, np.maximum(np.abs(zm) / q_h, 1e-5), color=col, lw=1.35, label=lbl)
    ug = np.linspace(u0_f, min(u_pk + 50.0, float(u8[-1])), 50)
    amp0 = float(np.abs(z22_8[np.argmin(np.abs(u8 - u0_f))]) / q_h)
    ax.semilogy(ug, 1.25 * amp0 * np.exp(-g_kerr * (ug - u0_f)),
                color="k", lw=1.3, ls="--", label=r"Kerr $e^{-u/\tau_{220}}$")
    ax.set_xlim(u_pk - 90.0, min(float(u8[-1]), u_pk + 56.0))
    ax.set_ylim(3e-4, 4e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_title(r"Multi-Mode Hierarchy $|r\Psi_4^{\ell m}|/q$ (P8)")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|r\Psi_4^{\ell m}|/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=7.0, ncol=2, loc="upper left", columnspacing=0.6, handlelength=1.3)

    fig.suptitle(r"Converged Variational GR-PIC 1000:1 Schwarzschild EMRI — Inspiral, Plunge, Merger & Kerr QNM Ringdown",
                 fontsize=11.4, y=0.970)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
