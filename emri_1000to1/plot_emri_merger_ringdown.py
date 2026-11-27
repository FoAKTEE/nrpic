#!/usr/bin/env python3
"""
Generate publication Cyclic-Zoom figure of our full 1000:1 Schwarzschild EMRI
inspiral -> ISCO -> plunge -> merger -> quasinormal ringdown (E2_merger_500 vs A7_vac_twin_500).
"""

import json
import math
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

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
from plot_emri_300M_suite import extrap_mode

ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94/fig_e2_full_merger_ringdown.png"


def load_full_e2_traj():
    """Concatenate 0..300 M from E2_ecc_nomcons_nf6 and 300..409 M from E2_merger_500."""
    d0 = os.path.join(ROOT, "E2_ecc_nomcons_nf6")
    d1 = os.path.join(ROOT, "E2_merger_500")
    tr0 = read_single_traj(os.path.join(d0, "E2_ecc_nomcons_nf6.traj.bin"))
    tr1 = read_single_traj(os.path.join(d1, "E2_ecc_nomcons_nf6.traj.bin"))
    tm0 = read_single_trajmet(os.path.join(d0, "E2_ecc_nomcons_nf6.trajmet.bin"))
    tm1 = read_single_trajmet(os.path.join(d1, "E2_ecc_nomcons_nf6.trajmet.bin"))
    co0 = safe_load_table(os.path.join(d0, "E2_ecc_nomcons_nf6.co_0.txt"), min_cols=5, tcol=1)
    co1 = safe_load_table(os.path.join(d1, "E2_ecc_nomcons_nf6.co_0.txt"), min_cols=5, tcol=1)
    hs0 = safe_load_table(os.path.join(d0, "E2_ecc_nomcons_nf6.horizon_summary_0.txt"), min_cols=12, tcol=1)
    hs1 = safe_load_table(os.path.join(d1, "E2_ecc_nomcons_nf6.horizon_summary_0.txt"), min_cols=12, tcol=1)

    def stitch(a0, a1, tcol):
        if a1[0, tcol] <= 5.0:
            return a1  # already contains full history
        m1 = a1[:, tcol] > a0[-1, tcol] + 1e-9
        return np.vstack([a0, a1[m1]])

    tr = stitch(tr0, tr1, 0)
    tm = stitch(tm0, tm1, 0)
    co = stitch(co0, co1, 1)
    hs = stitch(hs0, hs1, 1)
    return tr, tm, co, hs


def fit_two_mode_qnm(u, z, u0, u1, w_init=0.3734, g_init=0.0889):
    """
    Fit prograde + retrograde fundamental (2,+/-2,0) Kerr QNM:
      z(u) = A_+ exp((-i*w - g)*(u - u0)) + A_- exp((+i*w - g)*(u - u0))
    where A_+ and A_- are complex amplitudes solved linearly for each (w, g).
    """
    m = (u >= u0) & (u <= u1)
    uu = u[m] - u0
    zz = z[m]

    def solve_lin(w, g):
        e1 = np.exp((-1j * w - g) * uu)
        e2 = np.exp((+1j * w - g) * uu)
        M = np.column_stack([e1, e2])
        coef, _, _, _ = np.linalg.lstsq(M, zz, rcond=None)
        return coef, M @ coef

    def res(p):
        w, g = p
        _, zfit = solve_lin(w, g)
        diff = zfit - zz
        return np.concatenate([diff.real, diff.imag])

    sol = least_squares(res, [w_init, g_init], bounds=([0.20, 0.02], [0.55, 0.20]))
    w_fit, g_fit = float(sol.x[0]), float(sol.x[1])
    coef, zfit = solve_lin(w_fit, g_fit)
    rel_rms = float(np.linalg.norm(zfit - zz) / max(np.linalg.norm(zz), 1e-30))
    return w_fit, g_fit, coef, rel_rms


def main():
    cz.use_style()
    tr, tm, co, hs = load_full_e2_traj()
    t = tr[:, 0]
    xp = tr[:, 2:5]
    xbh = np.column_stack([
        np.interp(t, co[:, 1], co[:, 2]),
        np.interp(t, co[:, 1], co[:, 3]),
        np.interp(t, co[:, 1], co[:, 4]),
    ])
    xr = xp - xbh
    r_iso = np.linalg.norm(xr, axis=1)
    gzz = np.interp(t, tm[:, 0], tm[:, 11])
    Rg = r_iso * np.sqrt(np.maximum(gzz, 1e-6))
    phi = np.unwrap(np.arctan2(xr[:, 1], xr[:, 0]))
    om = np.gradient(phi, t)
    dt_med = float(np.median(np.diff(t)))
    ks = max(1, int(round(1.0 / max(dt_med, 1e-6))))
    om[ks:-ks] = (phi[2 * ks:] - phi[:-2 * ks]) / (t[2 * ks:] - t[:-2 * ks])
    t_exc = float(t[-1])

    # Load full 0..500 M vac-sub waveforms
    radii = [20.0, 27.0, 38.0, 48.0, 58.0]
    sp_raw = load_waveform_spheres(os.path.join(ROOT, "E2_merger_500"), radii)
    sp_vac = load_waveform_spheres(os.path.join(ROOT, "A7_vac_twin_500"), radii)
    sp_clean = {}
    for rad, sp in sp_raw.items():
        re_c = sp["re"].copy(); im_c = sp["im"].copy()
        vsp = sp_vac[rad]
        nc = min(re_c.shape[1], vsp["re"].shape[1])
        for c in range(1, nc):
            re_c[:, c] -= np.interp(sp["t"], vsp["t"], vsp["re"][:, c])
            im_c[:, c] -= np.interp(sp["t"], vsp["t"], vsp["im"][:, c])
        sp_clean[rad] = dict(sp, re=re_c, im=im_c)

    # Extrapolated modes on common u (up to u ~ 433 M) and r=38 M sphere (up to u ~ 455 M)
    u_inf, z22_inf, _ = extrap_mode(sp_clean, 2, 2)
    sp38 = sp_clean[38.0]
    u38 = sp38["u"]
    z22_38 = sp38["re"][:, lm_col(2, 2)] + 1j * sp38["im"][:, lm_col(2, 2)]
    z33_38 = sp38["re"][:, lm_col(3, 3)] + 1j * sp38["im"][:, lm_col(3, 3)]
    z44_38 = sp38["re"][:, lm_col(4, 4)] + 1j * sp38["im"][:, lm_col(4, 4)]
    z21_38 = sp38["re"][:, lm_col(2, 1)] + 1j * sp38["im"][:, lm_col(2, 1)]

    m_pk = u38 > 350.0
    i_pk = np.where(m_pk)[0][np.argmax(np.abs(z22_38[m_pk]))]
    u_pk = float(u38[i_pk])

    # Fit 2-mode (prograde + retrograde) fundamental QNM at r=38 M over [u_pk+8, u_pk+42]
    w_fit, g_fit, coef_qnm, qnm_rms = fit_two_mode_qnm(u38, z22_38, u_pk + 8.0, u_pk + 42.0)
    Mf = float(hs[-1, 2])
    af = float(hs[-1, 5]) / (Mf * Mf)
    w_kerr = (0.37367 + 0.0628 * af) / Mf
    g_kerr = (0.08896 - 0.0005 * af) / Mf
    print(f"2-mode QNM fit (r=38M, [{u_pk+8:.1f}..{u_pk+42:.1f}M]):")
    print(f"  omega_220 = {w_fit:.5f} vs exact Kerr {w_kerr:.5f} ({100*(w_fit-w_kerr)/w_kerr:+.2f}%)")
    print(f"  1/tau_220 = {g_fit:.5f} vs exact Kerr {g_kerr:.5f} ({100*(g_fit-g_kerr)/g_kerr:+.2f}%)")
    print(f"  |A_+|={abs(coef_qnm[0]):.3e}, |A_-|={abs(coef_qnm[1]):.3e}, rel_rms={qnm_rms:.3f}")

    ref = EMRIReferenceModel()
    ev_1sf = ref.evolve_inspiral("1SF", R0=6.25, q=1e-3, t_max=420.0, dt=0.25)

    fig, axes = plt.subplots(2, 3, figsize=(12.8, 7.2))
    fig.subplots_adjust(left=0.065, right=0.975, bottom=0.082, top=0.895, wspace=0.31, hspace=0.36)

    # (0,0) Full Equatorial Inspiral + Plunge Trajectory
    ax = axes[0, 0]
    m_ins = Rg >= 6.0
    m_plg = Rg < 6.0
    ax.plot(xr[m_ins, 0], xr[m_ins, 1], color=cz.PAL["blue"], lw=1.25, label=r"Inspiral ($R\geq 6\,M$)")
    ax.plot(xr[m_plg, 0], xr[m_plg, 1], color=cz.PAL["red"], lw=1.6, label=r"Plunge ($R<6\,M$)")
    ax.plot(xr[0, 0], xr[0, 1], "o", color=cz.PAL["green"], ms=5, zorder=5, label=r"$t=0$ ($R_0=6.25\,M$)")
    ax.plot(xr[-1, 0], xr[-1, 1], "x", color="k", ms=6.5, mew=1.6, zorder=6, label=rf"Excised ($t={t_exc:.1f}\,M$)")
    # Reference circles: ISCO (r_iso ~ 4.95 M), light ring (r_iso ~ 1.87 M), AH (r_AH = 0.93 M)
    ax.add_patch(Circle((0, 0), 4.949, fill=False, ec="grey", ls="--", lw=0.9, alpha=0.7))
    ax.add_patch(Circle((0, 0), 1.866, fill=False, ec=cz.PAL["orange"], ls=":", lw=1.0, alpha=0.85))
    ax.add_patch(Circle((0, 0), float(hs[-1, 10]), fc="black", ec="white", lw=0.8, zorder=5))
    ax.set_aspect("equal")
    ax.set_xlim(-6.8, 6.8); ax.set_ylim(-6.4, 8.4)
    ax.set_title("Equatorial inspiral & plunge orbit")
    ax.set_xlabel(r"$x-x_{\rm BH}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$y-y_{\rm BH}\,[M]$")
    ax.legend(fontsize=6.9, ncol=2, loc="upper center", columnspacing=0.6, handlelength=1.2)

    # (0,1) Areal Radius R_geom(t) & Orbital Frequency Omega(t) through Plunge
    ax = axes[0, 1]
    ax.axhline(6.0, color="grey", lw=0.9, ls="--", alpha=0.7)
    ax.axhline(3.0, color=cz.PAL["orange"], lw=0.9, ls=":", alpha=0.8)
    ax.text(12, 5.72, r"ISCO ($6\,M$)", fontsize=7.2, color="grey")
    ax.text(12, 3.12, r"Light ring ($3\,M$)", fontsize=7.2, color=cz.PAL["orange"])
    ax.plot(ev_1sf["t"][ev_1sf["R"] >= 6.0], ev_1sf["R"][ev_1sf["R"] >= 6.0],
            color="k", lw=1.5, ls="--", label="Exact 1SF (to ISCO)")
    ax.plot(t, Rg, color=cz.PAL["red"], lw=1.6, label=r"$R_{\rm geom}(t)$ (NR)")
    ax.axvline(t_exc, color="k", lw=0.9, ls="-.", alpha=0.5)
    ax.set_xlim(0, 430)
    ax.set_ylim(1.6, 6.65)
    ax.set_title("Areal separation through plunge")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$R_{\rm geom}\,[M]$")
    ax.legend(fontsize=7.4, loc="lower left", handlelength=1.4)
    ax.text(t_exc - 6, 2.05, rf"Horizon entry" + "\n" + rf"$t={t_exc:.1f}\,M$",
            ha="right", va="bottom", fontsize=7.3)

    # (0,2) Horizon Mass & Spin Conservation Across Merger
    ax = axes[0, 2]
    t_h = hs[:, 1]
    m_h = hs[:, 2]
    dM_1e3 = 1e3 * (m_h - m_h[0])
    af_1e3 = 1e3 * (hs[:, 5] / (m_h * m_h))
    # Pre-merger drift baseline (~0.27e-3 at t=398) + exact ISCO binding energy (+0.943e-3)
    m_pre = float(np.interp(395.0, t_h, dM_1e3))
    dM_jump = float(dM_1e3[-1] - m_pre)
    ax.plot(t_h, dM_1e3, color=cz.PAL["red"], lw=1.6, label=rf"$10^3\,\Delta M_{{\rm AH}}/M_0$ (jump $+{dM_jump:.2f}$)")
    ax.plot(t_h, af_1e3, color=cz.PAL["blue"], lw=1.6, label=rf"$10^3\,a_f/M_f$ (final $+{af_1e3[-1]:.2f}$)")
    ax.axhline(m_pre + 0.9428, color=cz.PAL["red"], lw=1.0, ls="--", alpha=0.65, label=r"GR $E_{\rm ISCO}\,q = +0.943$")
    ax.axhline(3.10, color=cz.PAL["blue"], lw=1.0, ls=":", alpha=0.75, label=r"GR $L_{\rm ISCO}\,q-\Delta J_{\rm plg}\approx 3.1$")
    ax.axvline(t_exc, color="k", lw=0.9, ls="-.", alpha=0.5)
    ax.set_xlim(0, 500)
    ax.set_ylim(-0.25, 3.65)
    ax.set_title("Remnant BH mass & spin conservation")
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^3\,\Delta M_{\rm AH}/M_0,\; 10^3\,a_f/M_f$")
    ax.legend(fontsize=6.9, loc="center left", bbox_to_anchor=(0.01, 0.57), handlelength=1.3)

    # (1,0) Full 0..455 M Inspiral + Plunge + Merger + Ringdown Waveform Re[rPsi4_22]
    ax = axes[1, 0]
    ax.plot(u38, 1e4 * np.real(z22_38), color=cz.PAL["red"], lw=1.15, label=r"NR $\mathrm{Re}[r\Psi_4^{22}]$ ($r=38\,M$)")
    ax.plot(u38, 1e4 * np.abs(z22_38), color="k", lw=1.0, ls="--", alpha=0.65, label=r"Envelope $|r\Psi_4^{22}|$")
    ax.axvline(u_pk, color="grey", lw=0.9, ls=":", alpha=0.7)
    ax.set_xlim(40, 455)
    ax.set_ylim(-2.8, 2.8)
    ax.set_title(r"Full inspiral–merger–ringdown $r\Psi_4^{22}$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^4\,r\Psi_4^{22}$")
    ax.legend(fontsize=7.3, loc="upper left", handlelength=1.3)
    ax.text(0.04, 0.06, rf"$14\times$ chirp: $1.6\times 10^{{-5}} \to 2.4\times 10^{{-4}}$",
            transform=ax.transAxes, fontsize=7.4)

    # (1,1) Zoomed Merger & Quasinormal Ringdown vs Exact Kerr (2,+/-2,0) QNM Fit
    ax = axes[1, 1]
    uz = u38[(u38 >= 365.0) & (u38 <= 454.0)]
    zz = z22_38[(u38 >= 365.0) & (u38 <= 454.0)]
    uq = u38[(u38 >= u_pk + 8.0) & (u38 <= u_pk + 46.0)]
    z_qnm = (
        coef_qnm[0] * np.exp((-1j * w_fit - g_fit) * (uq - (u_pk + 8.0)))
        + coef_qnm[1] * np.exp((+1j * w_fit - g_fit) * (uq - (u_pk + 8.0)))
    )
    ax.plot(uz, 1e4 * np.real(zz), color=cz.PAL["red"], lw=1.5, label=r"NR $\mathrm{Re}[r\Psi_4^{22}]$")
    ax.plot(uq, 1e4 * np.real(z_qnm), color="k", lw=1.4, ls="--", label="Kerr $(2,\pm 2,0)$ QNM fit")
    ax.axvspan(u_pk + 8.0, u_pk + 42.0, color=cz.PAL["blue"], alpha=0.08, lw=0)
    ax.set_xlim(365, 454)
    ax.set_ylim(-2.7, 2.7)
    ax.set_title(r"Merger & $(2,\pm 2,0)$ QNM ringdown")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$10^4\,\mathrm{Re}[r\Psi_4^{22}]$")
    ax.legend(fontsize=7.2, loc="upper left", handlelength=1.3)
    ax.text(0.97, 0.05,
            rf"$M\omega_{{220}}={w_fit:.4f}$ (Kerr ${w_kerr:.4f}$)" + "\n"
            + rf"$M/\tau_{{220}}={g_fit:.4f}$ (Kerr ${g_kerr:.4f}$)",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.2)

    # (1,2) Multi-Mode Plunge & Ringdown Hierarchy |rPsi4_lm|
    ax = axes[1, 2]
    for zm, col, lbl in [
        (z22_38, cz.PAL["red"], r"$(2,2)$"),
        (z33_38, cz.PAL["blue"], r"$(3,3)$"),
        (z44_38, cz.PAL["green"], r"$(4,4)$"),
        (z21_38, cz.PAL["orange"], r"$(2,1)$"),
    ]:
        ax.semilogy(u38, np.maximum(np.abs(zm), 1e-8), color=col, lw=1.4, label=lbl)
    # Exact Kerr (2,2,0) damping slope guide line
    ug = np.linspace(u_pk + 8.0, u_pk + 45.0, 50)
    ax.semilogy(ug, 1.5e-4 * np.exp(-g_kerr * (ug - (u_pk + 8.0))),
                color="k", lw=1.3, ls="--", label=r"Kerr $e^{-u/\tau_{220}}$")
    ax.set_xlim(320, 454)
    ax.set_ylim(3e-7, 6e-4)
    cz.no_minor_labels(ax, "y")
    ax.set_title(r"Multi-mode merger & ringdown $|r\Psi_4^{\ell m}|$")
    ax.set_xlabel(r"Retarded time $u\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$|r\Psi_4^{\ell m}|$ ($r=38\,M$, vac-sub)")
    ax.legend(fontsize=7.1, ncol=2, loc="lower left", columnspacing=0.6, handlelength=1.3)

    fig.suptitle(r"1000:1 Schwarzschild EMRI — Complete Inspiral, Plunge, Merger & Quasinormal Ringdown (E2_merger_500, $q=10^{-3}$)",
                 fontsize=11.3, y=0.972)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
