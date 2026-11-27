#!/usr/bin/env python3
"""
Generate Cyclic-Zoom publication physics figure for the converged Iteration 6
Variational GR-PIC EMRI full inspiral -> ISCO -> plunge -> merger -> Kerr QNM ringdown suite:
  - P1_iter6_M16_bssn_varpic_600 (Hero M/16 BSSN, q=1e-3, vac-sub P2)
  - P3_iter6_M8_bssn_varpic_600  (2x coarser M/8 BSSN convergence twin, vac-sub K15)
  - P4_iter6_M16_z4c_varpic_600  (M/16 Z4c formulation cross-check, vac-sub P5)
  - P6_iter6_M16_bssn_q2e3_350   (500:1 q=2e-3 mass-ratio scaling test, vac-sub P2)
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


def load_run(name, q, vac_name=None, radii=(20.0, 27.0, 38.0, 48.0, 58.0)):
    rdir = os.path.join(ROOT, name)
    tr = read_single_traj(os.path.join(rdir, f"{name}.traj.bin"))
    tm = read_single_trajmet(os.path.join(rdir, f"{name}.trajmet.bin"))
    co = safe_load_table(os.path.join(rdir, f"{name}.co_0.txt"), min_cols=5, tcol=1)
    hs = safe_load_table(os.path.join(rdir, f"{name}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    z4c = safe_load_table(os.path.join(rdir, f"{name}.z4c.user.hst"), min_cols=10, tcol=0)
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
    excised = (t_z4c - float(t[-1])) > 2.5

    sp_clean = {}
    if vac_name is not None:
        sp_raw = load_waveform_spheres(rdir, list(radii))
        sp_vac = load_waveform_spheres(os.path.join(ROOT, vac_name), list(radii))
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
        "name": name, "q": q, "t": t, "t_z4c": t_z4c, "excised": excised,
        "xr": xr, "r_iso": r_iso, "Rg": Rg, "phi": phi, "Lz": Lz,
        "co": co, "hs": hs, "z4c": z4c, "sp_clean": sp_clean,
    }


def fit_two_mode_qnm(u, z, u0, u1, w_init=0.3737, g_init=0.08896):
    m = (u >= u0) & (u <= u1)
    if np.sum(m) < 12:
        return np.nan, np.nan, np.array([0j, 0j]), np.nan
    uu = u[m] - u0
    zz = z[m]

    def solve_lin(w, g):
        M = np.column_stack([np.exp((-1j * w - g) * uu), np.exp((+1j * w - g) * uu)])
        coef, _, _, _ = np.linalg.lstsq(M, zz, rcond=None)
        return coef, M @ coef

    def res(p):
        _, zfit = solve_lin(p[0], p[1])
        d = zfit - zz
        return np.concatenate([d.real, d.imag])

    sol = least_squares(res, [w_init, g_init], bounds=([0.20, 0.02], [0.55, 0.20]))
    w_fit, g_fit = float(sol.x[0]), float(sol.x[1])
    coef, zfit = solve_lin(w_fit, g_fit)
    rel_rms = float(np.linalg.norm(zfit - zz) / max(np.linalg.norm(zz), 1e-30))
    return w_fit, g_fit, coef, rel_rms


def mode_at_r(run, l, m, rad=38.0):
    sp = run["sp_clean"][rad]
    col = lm_col(l, m)
    return sp["u"], sp["re"][:, col] + 1j * sp["im"][:, col]


def main():
    cz.use_style()
    p1 = load_run("P1_iter6_M16_bssn_varpic_600", 1e-3, "P2_iter6_M16_bssn_vac_600")
    p3 = load_run("P3_iter6_M8_bssn_varpic_600",  1e-3, "K15_iter6_M8_bssn_q0_vac550")
    p4 = load_run("P4_iter6_M16_z4c_varpic_600",  1e-3, "P5_iter6_M16_z4c_vac_600")
    p6 = load_run("P6_iter6_M16_bssn_q2e3_350",   2e-3, "P2_iter6_M16_bssn_vac_600")

    # Hero run for ringdown: P1 if merged, else fallback to P6 (if testing mid-run)
    hero = p1 if p1["excised"] else (p6 if p6["excised"] else p1)
    q_hero = hero["q"]

    ref = EMRIReferenceModel()
    ev_1sf = ref.evolve_inspiral("1SF", R0=6.25, q=1e-3, t_max=500.0, dt=0.25)
    ev_2sf = ref.evolve_inspiral("2SF", R0=6.25, q=1e-3, t_max=500.0, dt=0.25)
    ev_q2  = ref.evolve_inspiral("1SF", R0=6.25, q=2e-3, t_max=300.0, dt=0.25)

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 7.4))
    fig.subplots_adjust(left=0.062, right=0.980, bottom=0.080, top=0.905, wspace=0.29, hspace=0.35)

    # --- (0,0) Equatorial Inspiral & Plunge Orbit (P1 hero + P6 overlay) ---
    ax = axes[0, 0]
    m_ins = p1["Rg"] >= 6.0
    m_plg = p1["Rg"] < 6.0
    ax.plot(p1["xr"][m_ins, 0], p1["xr"][m_ins, 1], color=cz.PAL["blue"], lw=1.15, label=r"Inspiral ($R\geq 6\,M$)")
    if np.any(m_plg):
        ax.plot(p1["xr"][m_plg, 0], p1["xr"][m_plg, 1], color=cz.PAL["red"], lw=1.65, label=r"Plunge ($R<6\,M$)")
    ax.plot(p1["xr"][0, 0], p1["xr"][0, 1], "o", color=cz.PAL["green"], ms=4.8, zorder=5, label=r"$t=0$ ($6.25\,M$)")
    if p1["excised"]:
        ax.plot(p1["xr"][-1, 0], p1["xr"][-1, 1], "x", color="k", ms=6.5, mew=1.6, zorder=6,
                label=rf"Horizon ($t={p1['t'][-1]:.1f}\,M$)")
    ax.add_patch(Circle((0, 0), 4.949, fill=False, ec="grey", ls="--", lw=0.9, alpha=0.7))
    ax.add_patch(Circle((0, 0), 1.866, fill=False, ec=cz.PAL["orange"], ls=":", lw=1.0, alpha=0.85))
    r_ah = float(p1["hs"][-1, 10]) if (p1["hs"] is not None and len(p1["hs"])) else 0.93
    ax.add_patch(Circle((0, 0), r_ah, fc="black", ec="white", lw=0.8, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-6.8, 6.8)
    ax.set_ylim(-6.4, 8.6)
    ax.set_title("Equatorial Inspiral & Plunge (P1)")
    ax.set_xlabel(r"$x-x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y-y_{\rm BH}\,[M]$")
    ax.legend(frameon=False, fontsize=6.7, ncol=2, loc="upper center", columnspacing=0.6, handlelength=1.2)

    # --- (0,1) Areal Separation R_geom(t) Across Resolution, Formulation & Mass Ratio ---
    ax = axes[0, 1]
    ax.axhline(6.0, color="grey", lw=0.9, ls="--", alpha=0.7)
    ax.axhline(3.0, color=cz.PAL["orange"], lw=0.9, ls=":", alpha=0.8)
    ax.text(10, 5.72, r"ISCO ($6\,M$)", fontsize=7.0, color="grey")
    ax.text(10, 3.12, r"Light ring ($3\,M$)", fontsize=7.0, color=cz.PAL["orange"])
    ax.plot(ev_1sf["t"][ev_1sf["R"] >= 6.0], ev_1sf["R"][ev_1sf["R"] >= 6.0],
            color="k", lw=1.5, ls="--", label=r"1SF ($q=10^{-3}$)")
    ax.plot(ev_2sf["t"][ev_2sf["R"] >= 6.0], ev_2sf["R"][ev_2sf["R"] >= 6.0],
            color="0.45", lw=1.1, ls=":", label=r"2SF ($q=10^{-3}$)")
    ax.plot(ev_q2["t"][ev_q2["R"] >= 6.0], ev_q2["R"][ev_q2["R"] >= 6.0],
            color=cz.PAL["orange"], lw=1.1, ls="--", alpha=0.8)
    ax.plot(p1["t"], p1["Rg"], color=cz.PAL["red"], lw=1.7, label=r"P1 BSSN $M/16$")
    ax.plot(p4["t"], p4["Rg"], color=cz.PAL["green"], lw=1.4, ls="-.", label=r"P4 Z4c $M/16$")
    ax.plot(p3["t"], p3["Rg"], color=cz.PAL["blue"], lw=1.3, ls="--", label=r"P3 BSSN $M/8$")
    ax.plot(p6["t"], p6["Rg"], color=cz.PAL["orange"], lw=1.5, label=r"P6 $q=2\times 10^{-3}$")
    t_xlim = max(float(p1["t"][-1]) + 25.0, 260.0)
    ax.set_xlim(0, min(t_xlim, 600.0))
    ax.set_ylim(1.5, 6.65)
    ax.set_title("Areal Separation vs. 1SF & 2SF")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$R_{\rm geom}\,[M]$")
    ax.legend(frameon=False, fontsize=6.7, ncol=2, loc="lower left", columnspacing=0.6, handlelength=1.4)

    # --- (0,2) Remnant BH Mass Jump & Spin Conservation (Normalized by q) ---
    ax = axes[0, 2]
    ax.axhline(0.9428, color=cz.PAL["red"], lw=1.0, ls="--", alpha=0.65, label=r"GR $E_{\rm ISCO}=0.943$")
    ax.axhline(3.15, color=cz.PAL["blue"], lw=1.0, ls=":", alpha=0.70, label=r"GR $L_{\rm ISCO}-\Delta J_{\rm plg}\approx 3.15$")
    for run, col_m, col_s, ls, lbl_tag in [
        (p1, cz.PAL["red"], cz.PAL["blue"], "-",  r"P1 ($M/16$)"),
        (p3, cz.PAL["orange"], cz.PAL["green"], "--", r"P3 ($M/8$)"),
        (p6, "0.25", "0.55", ":", r"P6 ($q=2\times 10^{-3}$)"),
    ]:
        hs = run["hs"]
        if hs is None or len(hs) < 5:
            continue
        t_h = hs[:, 1]
        m_h = hs[:, 2]
        # Subtract slow pre-merger linear drift baseline if merged
        dM_q = (m_h - m_h[0]) / run["q"]
        af_q = (hs[:, 5] / (m_h * m_h)) / run["q"]
        ax.plot(t_h, dM_q, color=col_m, lw=1.5 if run is p1 else 1.15, ls=ls, label=rf"$\Delta M_{{\rm AH}}/q$ {lbl_tag}")
        ax.plot(t_h, af_q, color=col_s, lw=1.5 if run is p1 else 1.15, ls=ls, label=rf"$a_f/(M_f q)$ {lbl_tag}")
    ax.set_xlim(0, max(float(p1["t_z4c"]), 350.0))
    ax.set_ylim(-0.3, 4.1)
    ax.set_title("Remnant BH Mass & Spin Conservation")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\Delta M_{\rm AH}/(q M_0),\; a_f/(q M_f)$")
    ax.legend(frameon=False, fontsize=6.4, ncol=2, loc="upper left", columnspacing=0.6, handlelength=1.3)

    # --- (1,0) Full Vac-Subtracted Inspiral-Merger-Ringdown Re[rPsi4_22] / q ---
    ax = axes[1, 0]
    u1, z22_1 = mode_at_r(p1, 2, 2, 38.0)
    u3, z22_3 = mode_at_r(p3, 2, 2, 38.0)
    u4, z22_4 = mode_at_r(p4, 2, 2, 38.0)
    ax.plot(u1, np.real(z22_1) / p1["q"], color=cz.PAL["red"], lw=1.25, label=r"P1 BSSN $M/16$")
    ax.plot(u4, np.real(z22_4) / p4["q"], color=cz.PAL["green"], lw=1.0, ls="--", alpha=0.85, label=r"P4 Z4c $M/16$")
    ax.plot(u1, np.abs(z22_1) / p1["q"], color="k", lw=1.0, ls=":", alpha=0.7, label=r"P1 $|r\Psi_4^{22}|/q$")
    u_hi = max(float(u1[-1]), 120.0)
    ymax = max(0.035, 1.18 * float(np.max(np.abs(z22_1[u1 >= 25.0]))) / p1["q"]) if np.any(u1 >= 25.0) else 0.04
    ax.set_xlim(25.0, u_hi)
    ax.set_ylim(-ymax, ymax)
    ax.set_title(r"Vac.-Subtracted $r\Psi_4^{22}/q$ ($r=38\,M$)")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$r\Psi_4^{22}/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.4)

    # --- (1,1) Zoomed Merger & Kerr (2,+/-2,0) QNM Ringdown Fit ---
    ax = axes[1, 1]
    uh, z22_h = mode_at_r(hero, 2, 2, 38.0)
    m_srch = uh > max(80.0, float(hero["t"][-1]) - 60.0)
    if hero["excised"] and np.any(m_srch):
        i_pk = np.where(m_srch)[0][np.argmax(np.abs(z22_h[m_srch]))]
        u_pk = float(uh[i_pk])
        w_fit, g_fit, coef_qnm, qnm_rms = fit_two_mode_qnm(uh, z22_h, u_pk + 8.0, min(u_pk + 44.0, float(uh[-1])))
        Mf = float(hero["hs"][-1, 2])
        af = float(hero["hs"][-1, 5]) / (Mf * Mf)
        w_kerr = (0.37367 + 0.0628 * af) / Mf
        g_kerr = (0.08896 - 0.0005 * af) / Mf
        uz_lo, uz_hi = max(30.0, u_pk - 45.0), min(float(uh[-1]), u_pk + 55.0)
        mz = (uh >= uz_lo) & (uh <= uz_hi)
        ax.plot(uh[mz], np.real(z22_h[mz]) / q_hero, color=cz.PAL["red"], lw=1.6, label=rf"{hero['name'][:2]} $\mathrm{{Re}}[r\Psi_4^{{22}}]/q$")
        if np.isfinite(w_fit):
            uq = uh[(uh >= u_pk + 8.0) & (uh <= min(u_pk + 46.0, float(uh[-1])))]
            z_qnm = (coef_qnm[0] * np.exp((-1j * w_fit - g_fit) * (uq - (u_pk + 8.0)))
                     + coef_qnm[1] * np.exp((+1j * w_fit - g_fit) * (uq - (u_pk + 8.0))))
            ax.plot(uq, np.real(z_qnm) / q_hero, color="k", lw=1.4, ls="--", label="Kerr $(2,\pm 2,0)$ fit")
            ax.axvspan(u_pk + 8.0, min(u_pk + 44.0, float(uh[-1])), color=cz.PAL["blue"], alpha=0.08, lw=0)
            ax.text(0.97, 0.05,
                    rf"$M\omega_{{220}}={w_fit:.4f}$ (Kerr ${w_kerr:.4f}$)" + "\n"
                    + rf"$M/\tau_{{220}}={g_fit:.4f}$ (Kerr ${g_kerr:.4f}$)" + "\n"
                    + rf"RMS $= {100*qnm_rms:.1f}\%$",
                    transform=ax.transAxes, ha="right", va="bottom", fontsize=7.0)
            print(f"QNM fit ({hero['name']}): w={w_fit:.5f} vs {w_kerr:.5f} ({100*(w_fit-w_kerr)/w_kerr:+.2f}%), "
                  f"g={g_fit:.5f} vs {g_kerr:.5f} ({100*(g_fit-g_kerr)/g_kerr:+.2f}%), rms={qnm_rms:.3f}")
        ymax_z = 1.18 * float(np.max(np.abs(z22_h[mz]))) / q_hero
        ax.set_xlim(uz_lo, uz_hi)
        ax.set_ylim(-ymax_z, ymax_z)
        ax.set_title(rf"Merger & $(2,\pm 2,0)$ QNM Ringdown ({hero['name'][:2]})")
    else:
        # Inspiral zoom comparison of P1, P3, P4, P6/2
        u6, z22_6 = mode_at_r(p6, 2, 2, 38.0)
        ax.plot(u1, np.real(z22_1) / p1["q"], color=cz.PAL["red"], lw=1.5, label="P1 BSSN $M/16$")
        ax.plot(u4, np.real(z22_4) / p4["q"], color=cz.PAL["green"], lw=1.3, ls="--", label="P4 Z4c $M/16$")
        ax.plot(u3, np.real(z22_3) / p3["q"], color=cz.PAL["blue"], lw=1.2, ls=":", label="P3 BSSN $M/8$")
        ax.plot(u6, np.real(z22_6) / p6["q"], color=cz.PAL["orange"], lw=1.2, ls="-.", label="P6 $q=2e-3$ ($/q$)")
        ax.set_xlim(25.0, float(u1[-1]))
        ax.set_title(r"Cross-Resolution & Mass-Ratio Scaling")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\mathrm{Re}[r\Psi_4^{22}]/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=7.0, loc="upper left", handlelength=1.4)

    # --- (1,2) Multi-Mode Hierarchy |rPsi4_lm| / q ---
    ax = axes[1, 2]
    for (l, m), col, lbl in [
        ((2, 2), cz.PAL["red"],    r"$(2,2)$"),
        ((3, 3), cz.PAL["blue"],   r"$(3,3)$"),
        ((4, 4), cz.PAL["green"],  r"$(4,4)$"),
        ((2, 1), cz.PAL["orange"], r"$(2,1)$"),
    ]:
        um, zm = mode_at_r(hero, l, m, 38.0)
        ax.semilogy(um, np.maximum(np.abs(zm) / q_hero, 1e-5), color=col, lw=1.35, label=lbl)
    if hero["excised"] and np.any(m_srch):
        ug = np.linspace(u_pk + 8.0, min(u_pk + 48.0, float(uh[-1])), 50)
        amp0 = float(np.abs(z22_h[np.argmin(np.abs(uh - (u_pk + 8.0)))]) / q_hero)
        ax.semilogy(ug, 1.3 * amp0 * np.exp(-g_kerr * (ug - (u_pk + 8.0))),
                    color="k", lw=1.3, ls="--", label=r"Kerr $e^{-u/\tau_{220}}$")
        ax.set_xlim(max(30.0, u_pk - 90.0), min(float(uh[-1]), u_pk + 55.0))
    else:
        ax.set_xlim(25.0, float(uh[-1]))
    ax.set_ylim(2e-4, 6e-1)
    cz.no_minor_labels(ax, "y")
    ax.set_title(rf"Multi-Mode Hierarchy $|r\Psi_4^{{\ell m}}|/q$ ({hero['name'][:2]})")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|r\Psi_4^{\ell m}|/q\;[M^{-1}]$")
    ax.legend(frameon=False, fontsize=7.0, ncol=2, loc="lower left", columnspacing=0.6, handlelength=1.3)

    fig.suptitle(r"Converged Variational GR-PIC 1000:1 Schwarzschild EMRI — Inspiral, Plunge, Merger & Kerr QNM Ringdown",
                 fontsize=11.4, y=0.970)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
