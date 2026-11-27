#!/usr/bin/env python3
"""
Pure-CPU Cyclic-Zoom physics and NR diagnostic figure generator for AGN Binary-EMRI ZKL runs.

Generates:
  - fig_physics_<tag>.png      (2x3: global alpha(x,y), comoving binary, r_prop & r_com, e_in, I & a_in, GW rPsi4)
  - fig_diagnostics_<tag>.png  (2x3: |H(x,y)|, Z4c L2 norms, M_AH drift & S_z, D_AH/dx_BH, NRPIC conservation, SMBH recoil + summary)
"""

import argparse
import glob
import json
import math
import os
import re
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
import numpy as np

CZ_DIR = "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources"
if os.path.isdir(CZ_DIR) and CZ_DIR not in sys.path:
    sys.path.insert(0, CZ_DIR)
import czstyle as cz

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
import pn_zkl_scout as scout
import render_zkl_movie as rzm


def safe_load_table(path, min_cols=2, tcol=None):
    """Load whitespace-delimited float rows tolerating partial lines and restart overlaps."""
    if not os.path.isfile(path):
        return None
    rows = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < min_cols:
                continue
            try:
                rows.append([float(x) for x in parts])
            except ValueError:
                continue
    if not rows:
        return None
    ncol = len(rows[0])
    rows = [r for r in rows if len(r) == ncol]
    if not rows:
        return None
    arr = np.asarray(rows, dtype=np.float64)
    if tcol is not None and len(arr) > 1:
        arr = arr[rzm.keep_latest_monotonic(arr[:, tcol])]
    return arr


def read_latest_bin(pattern):
    """Read newest complete AthenaK 2D binary slice, falling back if newest is still being flushed."""
    paths = sorted(glob.glob(pattern))
    for path in reversed(paths):
        try:
            t_s, vlist, blocks = rzm.read_athenak_bin(path)
            return path, t_s, vlist, blocks
        except (EOFError, OSError, ValueError):
            continue
    return None, None, None, None


def parse_idsolve_summary(path):
    """Extract solver iterations, M_psi, and |P_ADM| from <base>.idsolve.txt."""
    info = {"iters": None, "m_psi": None, "p_adm": None}
    if not os.path.isfile(path):
        return info
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("# converged after"):
                m = re.search(r"after\s+(\d+)\s+iteration", line)
                if m:
                    info["iters"] = int(m.group(1))
            elif line.startswith("# far field:"):
                mm = re.search(r"M_psi\s*=\s*([0-9eE+\-.]+)", line)
                if mm:
                    info["m_psi"] = float(mm.group(1))
                mp = re.search(r"P_ADM\s*=\s*\(([^)]+)\)", line)
                if mp:
                    vals = [float(x) for x in mp.group(1).split(",")]
                    info["p_adm"] = float(np.linalg.norm(vals))
    return info


def compute_fermi_elements(t, x0, x1, m0, m1, m2):
    """
    Invert centered coordinate trajectories into local Fermi-normal Keplerian elements
    (a_in, e_in, inc_deg, r_prop, r_com) free of particle self-potential bias.
    """
    m_bin = m1 + m2
    n = len(t)
    if n < 2:
        return (np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n))

    v0_all = np.gradient(x0, t, axis=0)
    v1_all = np.gradient(x1, t, axis=0)

    a_arr = np.zeros(n)
    e_arr = np.zeros(n)
    i_arr = np.zeros(n)
    r_arr = np.zeros(n)
    rc_arr = np.zeros(n)

    for k in range(n):
        x_cm = (m1 * x0[k] + m2 * x1[k]) / m_bin
        v_cm = (m1 * v0_all[k] + m2 * v1_all[k]) / m_bin
        r_out = max(float(np.linalg.norm(x_cm)), 1e-6)
        rc_arr[k] = r_out

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

        r = max(float(np.linalg.norm(dx_prop)), 1e-12)
        v2 = float(np.dot(dv_prop, dv_prop))
        h_in = np.cross(dx_prop, dv_prop)
        e_vec = np.cross(dv_prop, h_in) / m_bin - dx_prop / r
        h_out = np.cross(x_cm, v_orth_cm)
        cos_i = float(np.dot(h_in, h_out)) / max(float(np.linalg.norm(h_in) * np.linalg.norm(h_out)), 1e-30)

        spec_e = 0.5 * v2 - m_bin / r
        a_arr[k] = -m_bin / (2.0 * spec_e) if spec_e < -1e-12 else np.nan
        e_arr[k] = float(np.linalg.norm(e_vec))
        i_arr[k] = float(np.degrees(np.arccos(max(-1.0, min(1.0, cos_i)))))
        r_arr[k] = r

    return a_arr, e_arr, i_arr, r_arr, rc_arr


def pn_r_com(cfg, t_arr):
    """Keplerian circular reference radius a_out for scout panel overlay."""
    return np.full_like(t_arr, float(cfg["a_out"]), dtype=np.float64)


def plot_figures(run_dir, out_dir, tag):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(run_dir, "run_meta.json"), "r") as f:
        meta = json.load(f)
    cfg = meta["cfg"]
    base = cfg["name"]

    traj = rzm.read_traj_binary(os.path.join(run_dir, f"{base}.traj.bin"))
    if traj is None or len(traj[0]) < 3:
        raise RuntimeError(f"Insufficient trajectory records in {run_dir}")
    t_tr, x0_tr, _, x1_tr, _ = traj
    if len(t_tr) > 1:
        keep = rzm.keep_latest_monotonic(t_tr)
        t_tr, x0_tr, x1_tr = t_tr[keep], x0_tr[keep], x1_tr[keep]
    a_nr, e_nr, i_nr, r_nr, rc_nr = compute_fermi_elements(
        t_tr, x0_tr, x1_tr, 1.0, cfg["m1"], cfg["m2"]
    )
    t_max = max(float(t_tr[-1]), 1.0)

    pn_ref = scout.integrate_case(
        1.0, cfg["m1"], cfg["m2"], cfg["a_out"], cfg["a_in"],
        cfg["e0"], cfg["inc"], cfg["chi0"], t_end=t_max, dt=min(0.1, 0.01 * t_max)
    )
    r_pn = pn_ref["r_in"]

    hs = safe_load_table(os.path.join(run_dir, f"{base}.horizon_summary_0.txt"), min_cols=12, tcol=1)
    z4c_hst = safe_load_table(os.path.join(run_dir, f"{base}.z4c.user.hst"), min_cols=10, tcol=0)
    nrp_hst = safe_load_table(os.path.join(run_dir, f"{base}.nrpic.hst"), min_cols=27, tcol=0)
    co0 = safe_load_table(os.path.join(run_dir, f"{base}.co_0.txt"), min_cols=5, tcol=1)
    idinfo = parse_idsolve_summary(os.path.join(run_dir, f"{base}.idsolve.txt"))

    wf22_re = safe_load_table(os.path.join(run_dir, "waveforms", "rpsi4_real_0022.txt"), min_cols=6, tcol=0)
    wf22_im = safe_load_table(os.path.join(run_dir, "waveforms", "rpsi4_imag_0022.txt"), min_cols=6, tcol=0)
    wf30_re = safe_load_table(os.path.join(run_dir, "waveforms", "rpsi4_real_0030.txt"), min_cols=6, tcol=0)

    _, t_alp, vlist_a, blocks_a = read_latest_bin(os.path.join(run_dir, "bin", f"{base}.alpha_xy.*.bin"))
    _, t_con, vlist_c, blocks_c = read_latest_bin(os.path.join(run_dir, "bin", f"{base}.conH_xy.*.bin"))

    m_bin = cfg["m1"] + cfg["m2"]
    x_cm = (cfg["m1"] * x0_tr + cfg["m2"] * x1_tr) / m_bin
    k_alp = int(np.clip(np.searchsorted(t_tr, t_alp if t_alp is not None else t_max, side="right") - 1, 0, len(t_tr) - 1))
    k_con = int(np.clip(np.searchsorted(t_tr, t_con if t_con is not None else t_max, side="right") - 1, 0, len(t_tr) - 1))

    r_ah_min = float(hs[-1, 11]) if hs is not None else 0.5
    cz.use_style()

    # =========================================================================
    # FIGURE 1: Physics Overview (2 x 3)
    # =========================================================================
    fig = plt.figure(figsize=(12.6, 7.8))
    fig.subplots_adjust(left=0.065, right=0.935, bottom=0.080, top=0.895, wspace=0.54, hspace=0.35)
    axes = fig.subplots(2, 3)

    # (0,0) Global lapse alpha(x,y)
    ax = axes[0, 0]
    if blocks_a is not None:
        va_i = vlist_a.index("z4c_alpha") if "z4c_alpha" in vlist_a else 0
        gx, gy, alp_img = rzm.rasterize_xy_slice(blocks_a, va_i, (-18.0, 18.0), (-18.0, 18.0), ngrid=320)
        im0 = ax.pcolormesh(gx, gy, np.clip(alp_img, 0.2, 1.05), cmap="viridis", vmin=0.35, vmax=1.0,
                            shading="auto", rasterized=True)
        cz.side_colorbar(fig, ax, im0, r"$\alpha$")
    ax.add_patch(Circle((0.0, 0.0), r_ah_min, fc="k", ec="w", lw=0.9, zorder=5))
    ax.add_patch(Circle((0.0, 0.0), float(cfg["a_out"]), fc="none", ec="w", ls=":", lw=0.9, alpha=0.65))
    ax.plot(x_cm[:k_alp+1, 0], x_cm[:k_alp+1, 1], color="w", lw=1.2, alpha=0.85)
    ax.scatter([x0_tr[k_alp, 0], x1_tr[k_alp, 0]], [x0_tr[k_alp, 1], x1_tr[k_alp, 1]],
               s=[34, 24], c=[cz.PAL["red"], cz.PAL["blue"]], edgecolors="w", lw=0.6, zorder=6)
    ax.set_aspect("equal")
    ax.set_xlim(-18.0, 18.0); ax.set_ylim(-18.0, 18.0)
    ax.set_xticks([-10, 0, 10]); ax.set_yticks([-10, 0, 10])
    ax.set_xlabel(r"$x\,[M]$", labelpad=2); ax.set_ylabel(r"$y\,[M]$")
    ax.set_title(rf"Lapse $\alpha(x,y)$ ($t={t_alp if t_alp is not None else t_max:.1f}\,M$)")

    # (0,1) Comoving inner binary (x-z solid, x-y dashed)
    ax = axes[0, 1]
    d0 = x0_tr - x_cm
    d1 = x1_tr - x_cm
    ax.plot(d0[:, 0], d0[:, 2], color=cz.PAL["red"], lw=1.5, label=r"$m_1$ $(x\text{–}z)$")
    ax.plot(d1[:, 0], d1[:, 2], color=cz.PAL["blue"], lw=1.5, label=r"$m_2$ $(x\text{–}z)$")
    ax.plot(d0[:, 0], d0[:, 1], color=cz.PAL["red"], lw=1.0, ls="--", alpha=0.55)
    ax.plot(d1[:, 0], d1[:, 1], color=cz.PAL["blue"], lw=1.0, ls="--", alpha=0.55, label=r"$(x\text{–}y)$ proj.")
    ax.scatter([d0[0, 0], d1[0, 0]], [d0[0, 2], d1[0, 2]], s=18, facecolors="none",
               edgecolors=[cz.PAL["red"], cz.PAL["blue"]], lw=1.0, zorder=5)
    ax.scatter([d0[-1, 0], d1[-1, 0]], [d0[-1, 2], d1[-1, 2]], s=[48, 36], marker="*",
               c=[cz.PAL["red"], cz.PAL["blue"]], zorder=6)
    lim = max(0.68 * float(cfg["a_in"]) * (1.0 + float(cfg["e0"])), float(np.max(np.abs(d0))) * 1.25, 0.55)
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel(r"$\Delta x_{\rm com}\,[M]$", labelpad=2)
    ax.set_ylabel(r"$\Delta z_{\rm com}\,[M]$")
    ax.legend(loc="upper right", fontsize=8.0, ncol=1, frameon=False)
    ax.set_title(rf"Comoving binary ($r_{{\rm prop}}={r_nr[-1]:.3f}\,M$)")

    # (0,2) Proper binary separation & outer COM radius
    ax = axes[0, 2]
    ln1 = ax.plot(t_tr, r_nr, color=cz.PAL["red"], lw=1.6, label=r"$r_{\rm prop}$ NR")
    ln2 = ax.plot(pn_ref["t"], r_pn, **cz.GUIDE, label=r"$r_{\rm in}$ 1PN")
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2)
    ax.set_ylabel(r"$r_{\rm prop}\,[M]$")
    ax2_r = ax.twinx()
    ln3 = ax2_r.plot(t_tr, rc_nr, color=cz.PAL["blue"], ls=":", lw=1.5, label=r"$r_{\rm com}$ NR")
    ax2_r.set_ylabel(r"$r_{\rm com}\,[M]$", color=cz.PAL["blue"])
    ax2_r.tick_params(axis="y", colors=cz.PAL["blue"], direction="in", which="both")
    rc_pad = max(0.15, float(np.ptp(rc_nr)) * 0.6)
    ax2_r.set_ylim(float(np.mean(rc_nr)) - rc_pad, float(np.mean(rc_nr)) + rc_pad)
    lns = ln1 + ln2 + ln3
    ax.legend(lns, [l.get_label() for l in lns], loc="lower left", fontsize=8.0, ncol=1, frameon=False)
    ax.set_title("Inner separation & outer COM")

    # (1,0) Inner eccentricity e_in(t)
    ax = axes[1, 0]
    ax.axvspan(0.0, min(0.5, t_max), color="grey", alpha=0.12)
    ax.plot(pn_ref["t"], pn_ref["e_in"], **cz.GUIDE, label="1PN+1.5PN scout")
    ax.plot(t_tr, e_nr, color=cz.PAL["red"], lw=1.6, label="Full 3+1 NR")
    post_mask = (t_tr >= min(0.5, 0.25 * t_max)) & np.isfinite(e_nr)
    e_hi = float(np.nanmax(e_nr[post_mask])) if np.any(post_mask) else float(np.nanmax(e_nr))
    ax.set_xlim(0.0, t_max)
    ax.set_ylim(0.0, min(1.05, max(0.25, 1.35 * max(e_hi, float(np.max(pn_ref["e_in"]))))))
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2)
    ax.set_ylabel(r"Inner eccentricity $e_{\rm in}$")
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)
    med_e = float(np.nanmedian(e_nr[post_mask])) if np.any(post_mask) else float(e_nr[-1])
    ax.set_title(rf"Inner $e_{{\rm in}}(t)$ (med $={med_e:.3f}$)")

    # (1,1) Mutual inclination I(t) & semimajor axis a_in(t)
    ax = axes[1, 1]
    ln1 = ax.plot(t_tr, i_nr, color=cz.PAL["green"], lw=1.6, label=r"$I$ NR")
    ln2 = ax.plot(pn_ref["t"], pn_ref["inc_deg"], **cz.GUIDE, label=r"$I$ 1PN")
    ax.set_xlim(0.0, t_max)
    ax.set_ylim(float(cfg["inc"]) - 4.0, float(cfg["inc"]) + 4.0)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2)
    ax.set_ylabel(r"Inclination $I\,[\mathrm{deg}]$")
    ax2_i = ax.twinx()
    valid_a = np.isfinite(a_nr)
    ln3 = ax2_i.plot(t_tr[valid_a], a_nr[valid_a], color=cz.PAL["blue"], ls=":", lw=1.5, label=r"$a_{\rm in}$ NR")
    ax2_i.set_ylabel(r"$a_{\rm in}\,[M]$", color=cz.PAL["blue"])
    ax2_i.tick_params(axis="y", colors=cz.PAL["blue"], direction="in", which="both")
    ax2_i.set_ylim(0.75 * float(cfg["a_in"]), 1.25 * float(cfg["a_in"]))
    lns = ln1 + ln2 + ln3
    ax.legend(lns, [l.get_label() for l in lns], loc="upper right", fontsize=8.0, frameon=False)
    ax.set_title(rf"Inclination & $a_{{\rm in}}$ ($I_0={cfg['inc']:.0f}^\circ$)")

    # (1,2) High-cadence GW readout rPsi4^(2,2)
    ax = axes[1, 2]
    if wf22_re is not None and len(wf22_re) > 1:
        ax.plot(wf22_re[:, 0], 1e4 * wf22_re[:, 5], color=cz.PAL["blue"], lw=1.3, label=r"$\mathrm{Re}\,(22\,M)$")
    if wf22_im is not None and len(wf22_im) > 1:
        ax.plot(wf22_im[:, 0], 1e4 * wf22_im[:, 5], color=cz.PAL["orange"], ls="--", lw=1.2, label=r"$\mathrm{Im}\,(22\,M)$")
    if wf30_re is not None and len(wf30_re) > 1 and t_max > 10.0:
        m30 = wf30_re[:, 0] >= 8.0
        if np.any(m30):
            ax.plot(wf30_re[m30, 0] - 8.0, 1e4 * wf30_re[m30, 5], color="grey", lw=0.9, alpha=0.85,
                    label=r"$30\,M\,(t-8)$")
    ax.set_xlim(0.0, t_max)
    if wf22_re is not None and len(wf22_re) > 1:
        yabs = max(float(np.max(np.abs(1e4 * wf22_re[:, 5]))), 0.25)
        ax.set_ylim(-1.25 * yabs, 1.35 * yabs)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2)
    ax.set_ylabel(r"$10^4\,r\Psi_4^{(2,2)}$")
    ax.legend(loc="upper left", fontsize=8.0, frameon=False)
    ax.set_title(r"GW readout ($\Delta t_\Psi = 0.1\,M$)")

    for row in axes:
        for a in row:
            a.tick_params(which="both", direction="in", top=True, right=True)

    mesh_lbl = (
        rf"AMR $L_5\!\to\!L_{{{meta.get('track_max_level', 8)}}}$"
        if meta.get("mesh_preset") == "amr_dyn"
        else rf"$\Delta x_{{\rm bin}}=M/{1.0/meta['dx_bin']:.0f}$"
    )
    fig.suptitle(
        rf"{base} Physics ($\chi_0={cfg['chi0']:+.1f}$, $a_{{\rm in}}={cfg['a_in']:.2f}\,M$, "
        rf"$I_0={cfg['inc']:.0f}^\circ$, {mesh_lbl}, $t={t_max:.2f}\,M$)",
        fontsize=12.5, y=0.96
    )
    phys_path = os.path.join(out_dir, f"fig_physics_{tag}.png")
    fig.savefig(phys_path, dpi=300)
    plt.close(fig)

    # =========================================================================
    # FIGURE 2: NR Solver & Constraint Diagnostics (2 x 3)
    # =========================================================================
    fig = plt.figure(figsize=(13.2, 7.8))
    fig.subplots_adjust(left=0.060, right=0.940, bottom=0.080, top=0.895, wspace=0.64, hspace=0.35)
    axes = fig.subplots(2, 3)

    # (0,0) Spatial |H(x,y)|
    ax = axes[0, 0]
    if blocks_c is not None:
        vc_i = vlist_c.index("con_H") if "con_H" in vlist_c else 0
        gx, gy, h_img = rzm.rasterize_xy_slice(blocks_c, vc_i, (-18.0, 18.0), (-18.0, 18.0), ngrid=320)
        h_abs = np.clip(np.abs(h_img), 1e-8, 1e-1)
        imh = ax.pcolormesh(gx, gy, h_abs, cmap=cz.CMAP["dens"], norm=LogNorm(1e-7, 1e-1),
                            shading="auto", rasterized=True)
        cz.side_colorbar(fig, ax, imh, r"$|\mathcal{H}|$")
    ax.add_patch(Circle((0.0, 0.0), r_ah_min, fc="k", ec="c", lw=0.9, zorder=5))
    ax.scatter([x0_tr[k_con, 0], x1_tr[k_con, 0]], [x0_tr[k_con, 1], x1_tr[k_con, 1]],
               s=[30, 22], c=[cz.PAL["red"], cz.PAL["blue"]], edgecolors="w", lw=0.6, zorder=6)
    ax.set_aspect("equal")
    ax.set_xlim(-18.0, 18.0); ax.set_ylim(-18.0, 18.0)
    ax.set_xticks([-10, 0, 10]); ax.set_yticks([-10, 0, 10])
    ax.set_xlabel(r"$x\,[M]$", labelpad=2); ax.set_ylabel(r"$y\,[M]$")
    ax.set_title(rf"$|\mathcal{{H}}(x,y)|$ ($t={t_con if t_con is not None else t_max:.1f}\,M$)")

    # (0,1) Z4c constraint L2 norms
    ax = axes[0, 1]
    if z4c_hst is not None and len(z4c_hst) > 1:
        tz = z4c_hst[:, 0]
        ax.plot(tz, np.clip(z4c_hst[:, 3], 1e-18, None), color=cz.PAL["red"], lw=1.5, label=r"$\|\mathcal{H}\|_2$")
        ax.plot(tz, np.clip(z4c_hst[:, 4], 1e-18, None), color=cz.PAL["blue"], lw=1.5, label=r"$\|\mathcal{M}\|_2$")
        ax.plot(tz, np.clip(z4c_hst[:, 2], 1e-18, None), color="k", ls="--", lw=1.2, label=r"$\|\mathcal{C}\|_2$")
        th = np.clip(z4c_hst[:, 9], 1e-18, None)
        if np.any(th > 1e-17):
            ax.plot(tz, th, color=cz.PAL["green"], ls=":", lw=1.3, label=r"$\|\Theta\|_2$")
        ax.set_yscale("log")
        cz.no_minor_labels(ax, "y")
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2); ax.set_ylabel(r"Constraint $L_2$ norm")
    ax.legend(loc="best", fontsize=8.0, ncol=2, frameon=False)
    ax.set_title("Z4c constraint evolution")

    # (0,2) Horizon M_AH drift and spin S_z
    ax = axes[0, 2]
    if hs is not None and len(hs) > 0:
        th_s = hs[:, 1]
        dm_1e4 = (hs[:, 2] - hs[0, 2]) / hs[0, 2] * 1.0e4
        ln1 = ax.plot(th_s, dm_1e4, color=cz.PAL["red"], lw=1.6, label=r"$\Delta M_{\rm AH}/M_0\,[10^{-4}]$")
        ax2_s = ax.twinx()
        ln2 = ax2_s.plot(th_s, hs[:, 5], color=cz.PAL["blue"], ls="--", lw=1.4, label=r"$S_z\,[M^2]$")
        ax2_s.set_ylabel(r"$S_z\,[M^2]$", color=cz.PAL["blue"])
        ax2_s.tick_params(axis="y", colors=cz.PAL["blue"], direction="in", which="both")
        ax2_s.ticklabel_format(style="plain", useOffset=False, axis="y")
        s_span = max(float(np.ptp(hs[:, 5])) * 2.0, 0.02)
        ax2_s.set_ylim(float(np.mean(hs[:, 5])) - s_span, float(np.mean(hs[:, 5])) + s_span)
        lns = ln1 + ln2
        ax.legend(lns, [l.get_label() for l in lns], loc="best", fontsize=8.0, frameon=False)
        mah0 = float(hs[0, 2]); mdrift = float(np.max(np.abs(dm_1e4)))
        ax.set_title(rf"$M_{{\rm AH}}(0)={mah0:.4f}\,M$ ($|\Delta|<{mdrift:.2f}\times10^{{-4}}$)")
    else:
        ax.set_title("Apparent horizon (pending)")
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2); ax.set_ylabel(r"$\Delta M_{\rm AH}/M_0\,[10^{-4}]$")

    # (1,0) Horizon diameter resolution
    ax = axes[1, 0]
    dx_bh = float(meta["dx_bh"])
    if hs is not None and len(hs) > 0:
        th_s = hs[:, 1]
        d_min = 2.0 * hs[:, 11] / dx_bh
        d_mean = 2.0 * hs[:, 10] / dx_bh
        ax.plot(th_s, d_min, color=cz.PAL["red"], lw=1.6, label=r"$2 r_{\min}/\Delta x_{\rm BH}$")
        ax.plot(th_s, d_mean, color=cz.PAL["blue"], ls="--", lw=1.4, label=r"$2 r_{\rm mean}/\Delta x_{\rm BH}$")
        ymax = max(45.0, float(np.max(d_mean)) * 1.12)
        ax.set_title(rf"Horizon res. ({d_min[0]:.1f}$\to${d_min[-1]:.1f} cells)")
    else:
        ymax = 50.0
        ax.set_title("Horizon resolution")
    ax.axhline(32.0, **cz.GUIDE, label=r"$32$-cell floor")
    ax.axhspan(32.0, ymax, color=cz.PAL["green"], alpha=0.08)
    ax.set_xlim(0.0, t_max); ax.set_ylim(10.0, ymax)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2); ax.set_ylabel(r"$D_{\rm AH} / \Delta x_{\rm BH}$")
    ax.legend(loc="lower right", fontsize=8.0, frameon=False)

    # (1,1) NRPIC filter conservation & alpha_min
    ax = axes[1, 1]
    if nrp_hst is not None and len(nrp_hst) > 1:
        tn = nrp_hst[:, 0]
        e_err = np.abs(nrp_hst[:, 23] - nrp_hst[:, 4]) / np.maximum(np.abs(nrp_hst[:, 4]), 1e-30)
        p_dep = nrp_hst[:, 9:12]
        p_flt = nrp_hst[:, 24:27]
        p_err = np.linalg.norm(p_flt - p_dep, axis=1) / np.maximum(np.linalg.norm(p_dep, axis=1), 1e-12)
        ln1 = ax.plot(tn, np.clip(e_err, 1e-16, None), color=cz.PAL["red"], lw=1.5, label=r"$|\Delta E_{\rm filt}|/E$")
        ln2 = ax.plot(tn, np.clip(p_err, 1e-16, None), color=cz.PAL["blue"], lw=1.5, label=r"$\|\Delta \mathbf{P}_{\rm filt}\|/P$")
        ax.set_yscale("log")
        ax.set_ylim(1e-16, max(1e-6, 5.0 * float(np.max(np.maximum(e_err, p_err)))))
        cz.no_minor_labels(ax, "y")
        ax2_a = ax.twinx()
        ln3 = ax2_a.plot(tn, nrp_hst[:, 15], color=cz.PAL["green"], ls="--", lw=1.2, label=r"$\alpha_{\min}$")
        ax2_a.set_ylabel(r"$\alpha_{\min}$", color=cz.PAL["green"])
        ax2_a.tick_params(axis="y", colors=cz.PAL["green"], direction="in", which="both")
        lns = ln1 + ln2 + ln3
        ax.legend(lns, [l.get_label() for l in lns], loc="upper left", fontsize=8.0, frameon=False)
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2); ax.set_ylabel("Filter rel. error")
    ax.set_title("Metric-conservative conservation")

    # (1,2) SMBH puncture recoil & solver summary
    ax = axes[1, 2]
    if co0 is not None and len(co0) > 1:
        t_co = co0[:, 1]
        scale = 1e6 if np.max(np.abs(co0[:, 2:5])) < 1e-3 else 1.0
        unit = r"10^{-6}\,M" if scale > 1.0 else "M"
        ax.plot(t_co, co0[:, 2] * scale, color=cz.PAL["red"], lw=1.4, label=r"$x_{\rm BH}$")
        ax.plot(t_co, co0[:, 3] * scale, color=cz.PAL["blue"], lw=1.4, label=r"$y_{\rm BH}$")
        ax.plot(t_co, co0[:, 4] * scale, color=cz.PAL["green"], ls="--", lw=1.2, label=r"$z_{\rm BH}$")
        y_vals = co0[:, 2:5] * scale
        ylo, yhi = float(np.min(y_vals)), float(np.max(y_vals))
        ysp = max(yhi - ylo, 1e-3)
        ax.set_ylim(ylo - 0.65 * ysp, yhi + 0.25 * ysp)
        ax.set_ylabel(rf"$\Delta x_0\,[{unit}]$", labelpad=2)
        ax.legend(loc="upper right", fontsize=8.0, ncol=3, frameon=False)
    ax.set_xlim(0.0, t_max)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=2)
    max_lvl = meta.get("track_max_level", 8)
    min_lvl = meta.get("ring_level", 5)
    max_den = int(round(1.0 / (meta["dx_bin"] / (2 ** max(0, max_lvl - min_lvl)))))
    res_lbl = (
        rf"$L_{{{min_lvl}}}\to L_{{{max_lvl}}}$ ($M/{1.0/meta['dx_bin']:.0f}$–$M/{max_den}$)"
        if meta.get("mesh_preset") == "amr_dyn"
        else rf"$\Delta x_{{\rm bin}}=M/{1.0/meta['dx_bin']:.0f}$"
    )
    summary_lines = [
        rf"mesh: {meta['mesh_preset']}, {res_lbl}",
        rf"$\Delta x_{{\rm BH}}=M/{1.0/dx_bh:.0f}$, $\sigma_{{\rm eff}}={meta.get('sigma_eff', 0.0):.4f}\,M$",
        rf"$\mathtt{{id\_solve}}$: {idinfo['iters']} it., $M_\psi={idinfo['m_psi']:.5f}$" if idinfo["m_psi"] else r"$\mathtt{id\_solve}$: N/A",
        rf"$|\mathbf{{P}}_{{\rm ADM}}|={idinfo['p_adm']:.2e}$" if idinfo["p_adm"] is not None else "",
        rf"status: $t={t_max:.2f}\,M$",
    ]
    ax.text(0.04, 0.04, "\n".join(s for s in summary_lines if s), transform=ax.transAxes,
            fontsize=8.0, va="bottom", ha="left")
    ax.set_title("Puncture tracker & run summary")

    for row in axes:
        for a in row:
            a.tick_params(which="both", direction="in", top=True, right=True)

    fig.suptitle(
        rf"{base} Diagnostics ($\chi_0={cfg['chi0']:+.1f}$, pcs + quintic + nfilter={meta['nfilter']}, "
        rf"mstride={meta.get('matter_stride', 1)}, $t={t_max:.2f}\,M$)",
        fontsize=12.5, y=0.96
    )
    diag_path = os.path.join(out_dir, f"fig_diagnostics_{tag}.png")
    fig.savefig(diag_path, dpi=300)
    plt.close(fig)
    print(f"Wrote {phys_path} and {diag_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    with open(os.path.join(run_dir, "run_meta.json"), "r") as f:
        tag = args.tag or json.load(f)["cfg"]["name"].lower()
    plot_figures(run_dir, os.path.abspath(args.out_dir), tag)


if __name__ == "__main__":
    main()
