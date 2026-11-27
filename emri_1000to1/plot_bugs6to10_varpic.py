#!/usr/bin/env python3
"""Publication-grade Cyclic-Zoom 2x2 figure: Bugs 6–10 forensic ablation & Variational GR-PIC convergence."""
import os
import sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
from scipy.interpolate import LinearNDInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/schmidt/ssci-haiyangw/nrpic/emri_1000to1")
sys.path.insert(0, "/home/schmidt/ssci-haiyangw/.gemini/config/skills/cz-figure-style/resources")
import czstyle as cz
from analyze_emri_gw import read_single_traj, safe_load_table

ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/phaseA_it5"
OUT = "/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/3d042f0d-783f-49ae-b143-9b8687f98c94"


def dLz_1sf_exact(R, q=1.0e-3):
    Rs = np.array([6.0, 6.25, 6.5, 7.0])
    Fs = np.array([1.4043e-2, 1.1593e-2, 9.714e-3, 7.068e-3])
    c = np.polyfit(np.log(Rs), np.log(Fs), 2)
    return -q * np.exp(np.polyval(c, np.log(R)))


def load_orbit(nm):
    rdir = os.path.join(ROOT, nm)
    tr = read_single_traj(os.path.join(rdir, f"{nm}.traj.bin"))
    co = safe_load_table(os.path.join(rdir, f"{nm}.co_0.txt"), min_cols=5, tcol=1)
    zh = safe_load_table(os.path.join(rdir, f"{nm}.z4c.user.hst"), min_cols=5, tcol=0)
    if tr is None or len(tr) < 15:
        return None
    t = tr[:, 0]
    xp = tr[:, 2:5]
    up = tr[:, 5:8]
    if co is not None and len(co) > 1:
        xbh = np.column_stack([np.interp(t, co[:, 1], co[:, j]) for j in (2, 3, 4)])
    else:
        xbh = np.zeros_like(xp)
    xr = xp - xbh
    Lz = xr[:, 0] * up[:, 1] - xr[:, 1] * up[:, 0]
    phi = np.unwrap(np.arctan2(xr[:, 1], xr[:, 0]))
    m_late = (t >= 70.0) & (t <= t[-1])
    if np.sum(m_late) < 10:
        m_late = (t >= max(20.0, t[-1] - 30.0)) & (t <= t[-1])
    Om = np.polyfit(t[m_late], phi[m_late], 1)[0]
    R_Om = Om ** (-2.0 / 3.0)
    return {"t": t, "Lz": Lz, "xr": xr, "R_Om": R_Om, "zh": zh}


def sliding_dLz_ratio(d, win=16.0, norm_ROm=True):
    t, Lz = d["t"], d["Lz"]
    denom = dLz_1sf_exact(d["R_Om"]) if norm_ROm else -1.1593e-5
    tc = np.arange(14.0, t[-1] - 0.5 * win + 1e-6, 1.5)
    vals = []
    for c in tc:
        m = (t >= c - 0.5 * win) & (t <= c + 0.5 * win)
        if np.sum(m) >= 5:
            vals.append(np.polyfit(t[m], Lz[m], 1)[0] / denom)
        else:
            vals.append(np.nan)
    return tc, np.array(vals)


def steady_ratio(d, t0=70.0, t1=120.0, norm_ROm=True):
    if d is None:
        return np.nan
    t, Lz = d["t"], d["Lz"]
    t1_eff = min(t1, t[-1])
    t0_eff = min(t0, max(35.0, t1_eff - 25.0))
    m = (t >= t0_eff) & (t <= t1_eff)
    if np.sum(m) < 8:
        return np.nan
    denom = dLz_1sf_exact(d["R_Om"]) if norm_ROm else -1.1593e-5
    return np.polyfit(t[m], Lz[m], 1)[0] / denom


def read_bin_xy(fname):
    filesize = os.path.getsize(fname)
    with open(fname, "rb") as fp:
        fp.readline()
        pheader_count = int(fp.readline().split(b"=")[-1])
        pheader = {}
        for _ in range(pheader_count - 1):
            k, v = [x.strip() for x in fp.readline().decode("utf-8").split("=", 1)]
            pheader[k] = v
        time = float(pheader["time"])
        locsz = int(pheader["size of location"])
        varsz = int(pheader["size of variable"])
        nvars = int(fp.readline().split(b"=")[-1])
        fp.readline()
        header_size = int(fp.readline().split(b"=")[-1])
        fp.read(header_size)
        mbs = []
        while fp.tell() < filesize:
            idx = np.frombuffer(fp.read(24), dtype=np.int32).astype(np.int64) - 4
            nx1, nx2, nx3 = int(idx[1] - idx[0] + 1), int(idx[3] - idx[2] + 1), int(idx[5] - idx[4] + 1)
            fp.read(16)
            geom = np.frombuffer(fp.read(6 * locsz), dtype=np.float64 if locsz == 8 else np.float32)
            dat = np.fromfile(fp, dtype=np.float64 if varsz == 8 else np.float32,
                              count=nvars * nx3 * nx2 * nx1).reshape(nvars, nx3, nx2, nx1)
            mbs.append((geom, dat))
    return time, mbs


def azimuthal_H_line(rn, idx=3):
    """Interpolate finest-level con_H cleanly along the azimuthal line through x_p."""
    d = os.path.join(ROOT, rn)
    bf = os.path.join(d, "bin", f"{rn}.conH_xy.{idx:05d}.bin")
    if not os.path.exists(bf):
        return None, None
    t_bin, mbs = read_bin_xy(bf)
    tr = read_single_traj(os.path.join(d, f"{rn}.traj.bin"))
    xp = np.interp(t_bin, tr[:, 0], tr[:, 2])
    yp = np.interp(t_bin, tr[:, 0], tr[:, 3])
    r = np.hypot(xp, yp)
    er = np.array([xp / r, yp / r])
    ep = np.array([-yp / r, xp / r])
    xs, ys, hs, dxs = [], [], [], []
    for geom, dat in mbs:
        if xp < geom[0] - 1.3 or xp > geom[1] + 1.3 or yp < geom[2] - 1.3 or yp > geom[3] + 1.3:
            continue
        arr3 = dat[0]
        nz, ny, nx = arr3.shape
        dx = (geom[1] - geom[0]) / nx
        dy = (geom[3] - geom[2]) / ny
        X, Y = np.meshgrid(geom[0] + (np.arange(nx) + 0.5) * dx,
                           geom[2] + (np.arange(ny) + 0.5) * dy)
        H2 = arr3[nz // 2]
        m = np.hypot(X - xp, Y - yp) < 1.25
        if np.any(m):
            xs.append(X[m])
            ys.append(Y[m])
            hs.append(H2[m])
            dxs.append(np.full(np.sum(m), dx))
    xs = np.concatenate(xs)
    ys = np.concatenate(ys)
    hs = np.concatenate(hs)
    dxs = np.concatenate(dxs)
    # Keep strictly finest level covering the particle neighborhood
    finest = np.min(dxs)
    mf = dxs <= finest * 1.05
    dr = (xs[mf] - xp) * er[0] + (ys[mf] - yp) * er[1]
    dp = (xs[mf] - xp) * ep[0] + (ys[mf] - yp) * ep[1]
    interp = LinearNDInterpolator(np.column_stack([dp, dr]), hs[mf])
    s = np.linspace(-0.90, 0.90, 181)
    # Average over thin radial band dr in [-0.05, 0, +0.05] to suppress sub-cell aliasing cleanly
    vals = np.nanmean([interp(np.column_stack([s, np.full_like(s, off)])) for off in (-0.04, 0.0, 0.04)], axis=0)
    return s, vals


def load_psi4_22_sub(rn, vac, rval=38):
    fre = os.path.join(ROOT, rn, "waveforms", f"rpsi4_real_{rval:04d}.txt")
    fim = os.path.join(ROOT, rn, "waveforms", f"rpsi4_imag_{rval:04d}.txt")
    vre = os.path.join(ROOT, vac, "waveforms", f"rpsi4_real_{rval:04d}.txt")
    vim = os.path.join(ROOT, vac, "waveforms", f"rpsi4_imag_{rval:04d}.txt")
    dr = np.loadtxt(fre, comments="#")
    di = np.loadtxt(fim, comments="#")
    vr = np.loadtxt(vre, comments="#")
    vi = np.loadtxt(vim, comments="#")
    t = dr[:, 0]
    rstar = rval + 2.0 * np.log(rval / 2.0 - 1.0)
    u = t - rstar
    re_s = dr[:, 5] - np.interp(t, vr[:, 0], vr[:, 5])
    im_s = di[:, 5] - np.interp(t, vi[:, 0], vi[:, 5])
    return u, re_s, im_s, np.sqrt(re_s ** 2 + im_s ** 2)


def main():
    cz.use_style()
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 6.3))
    fig.subplots_adjust(left=0.095, right=0.97, bottom=0.085, top=0.935, wspace=0.26, hspace=0.30)

    names = [
        "V0_iter6_M8_q0_varpic",
        "V1_iter6_M8_z4c_varpic",
        "V2_iter6_M8_bssn_varpic",
        "V3_iter6_M16_z4c_varpic",
        "V4_iter6_M16_bssn_varpic",
        "V5_iter6_M16_s223_z4c_varpic",
        "K3_iter6_M8_std_eta_lagr_diss010",
        "K9_iter6_M8_bssn_lagr_diss010",
        "K7_iter6_M16_nf8_std_eta_lagr_diss005",
        "K12_iter6_M16_nf8_bssn_lagr_diss005",
        "B1_iter6_M8_z4c_bianchi",
        "B2_iter6_M8_bssn_bianchi",
        "B3_iter6_M16_nf8_z4c_bianchi",
        "B4_iter6_M16_nf8_bssn_bianchi",
    ]
    data = {n: load_orbit(n) for n in names}

    # --- Panel 1 (Top-Left): Time-resolved dLz/dt / dLz_1SF at M/16 ---
    ax = axes[0, 0]
    ax.axhline(1.0, **cz.REF_LINE, label="1SF exact")
    ax.axhline(0.0, color="grey", lw=1.0, ls=":", alpha=0.6)
    series_tl = [
        ("K7_iter6_M16_nf8_std_eta_lagr_diss005",  cz.PAL["blue"],   "--", 1.5, r"Rigid Z4c ($M/16$)"),
        ("K12_iter6_M16_nf8_bssn_lagr_diss005",    cz.PAL["orange"], "--", 1.5, r"Rigid BSSN ($M/16$)"),
        ("B4_iter6_M16_nf8_bssn_bianchi",          cz.PAL["yellow"], ":",  1.8, r"Bianchi-only ($M/16$)"),
        ("V3_iter6_M16_z4c_varpic",                cz.PAL["green"],  "-",  2.0, r"Var-PIC Z4c ($M/16$)"),
        ("V4_iter6_M16_bssn_varpic",               cz.PAL["red"],    "-",  2.2, r"Var-PIC BSSN ($M/16$)"),
        ("V0_iter6_M8_q0_varpic",                  "0.45",           "-",  1.2, r"Var-PIC $q=0$"),
    ]
    for nm, col, ls, lw, lab in series_tl:
        if data[nm] is not None:
            tc, rv = sliding_dLz_ratio(data[nm], win=16.0, norm_ROm=(nm != "V0_iter6_M8_q0_varpic"))
            ax.plot(tc, rv, color=col, ls=ls, lw=lw, label=lab)
    ax.set_xlim(15, 112)
    ax.set_ylim(-1.7, 10.2)
    ax.set_xlabel(r"Time $t\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$\dot{L}_z / \dot{L}_z^{\rm 1SF}(R_\Omega)$")
    ax.set_title(r"Radiation-Reaction Evolution ($M/16$)", fontsize=10.8)
    ax.legend(frameon=False, fontsize=7.2, ncol=2, loc="center right",
              bbox_to_anchor=(0.995, 0.56), columnspacing=0.7, handlelength=1.6)

    # --- Panel 2 (Top-Right): Steady-state summary across M/8 vs M/16 & Z4c vs BSSN ---
    ax = axes[0, 1]
    ax.axhline(1.0, **cz.REF_LINE)
    ax.axhline(0.0, color="grey", lw=1.0, ls=":", alpha=0.6)
    cats = [
        ("Rigid\n$M/8$",    "K3_iter6_M8_std_eta_lagr_diss010",      "K9_iter6_M8_bssn_lagr_diss010"),
        ("Rigid\n$M/16$",   "K7_iter6_M16_nf8_std_eta_lagr_diss005", "K12_iter6_M16_nf8_bssn_lagr_diss005"),
        ("Bianchi\n$M/8$",  "B1_iter6_M8_z4c_bianchi",               "B2_iter6_M8_bssn_bianchi"),
        ("Bianchi\n$M/16$", "B3_iter6_M16_nf8_z4c_bianchi",          "B4_iter6_M16_nf8_bssn_bianchi"),
        ("Var-PIC\n$M/8$",  "V1_iter6_M8_z4c_varpic",                "V2_iter6_M8_bssn_varpic"),
        ("Var-PIC\n$M/16$", "V3_iter6_M16_z4c_varpic",               "V4_iter6_M16_bssn_varpic"),
    ]
    xs_cat = np.arange(len(cats))
    z4c_vals = [steady_ratio(data[z]) for _, z, _ in cats]
    bssn_vals = [steady_ratio(data[b]) for _, _, b in cats]
    wbar = 0.35
    ax.bar(xs_cat - 0.5 * wbar, z4c_vals, width=wbar, color=cz.PAL["blue"], alpha=0.88, label="Z4c")
    ax.bar(xs_cat + 0.5 * wbar, bssn_vals, width=wbar, color=cz.PAL["red"], alpha=0.88, label="BSSN")
    for xi, zv, bv in zip(xs_cat, z4c_vals, bssn_vals):
        if np.isfinite(zv):
            va = "bottom" if zv >= 0 else "top"
            off = 0.16 if zv >= 0 else -0.18
            ax.text(xi - 0.62 * wbar, zv + off, f"{zv:.2f}", ha="center", va=va, fontsize=6.1, color=cz.PAL["blue"])
        if np.isfinite(bv):
            ax.text(xi + 0.62 * wbar, bv + 0.16, f"{bv:.2f}", ha="center", va="bottom", fontsize=6.1, color=cz.PAL["red"])
    ax.set_xticks(xs_cat)
    ax.set_xticklabels([c[0] for c in cats], fontsize=7.6)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_ylim(-0.9, 9.4)
    ax.set_ylabel(r"Steady $\dot{L}_z / \dot{L}_z^{\rm 1SF}(R_\Omega)$")
    ax.set_title("Z4c vs. BSSN & Resolution Collapse", fontsize=10.8)
    ax.legend(frameon=False, fontsize=8.5, ncol=2, loc="upper left")

    # --- Panel 3 (Bottom-Left): Smooth finest-level azimuthal con_H line cut at t=30 M ---
    ax = axes[1, 0]
    ax.axhline(0.0, color="grey", lw=1.0, ls=":", alpha=0.6)
    ax.axvline(0.0, color="grey", lw=1.0, ls="--", alpha=0.45)
    h_series = [
        ("K9_iter6_M8_bssn_lagr_diss010",         3, cz.PAL["orange"], "--", 1.8, r"Rigid BSSN ($M/8$, $n_f=6$)"),
        ("K17_iter6_M16_nf25_bssn_lagr_diss010",  3, "k",              ":",  1.8, r"Rigid BSSN ($M/16$, $n_f=25$)"),
        ("V2_iter6_M8_bssn_varpic",               3, cz.PAL["red"],    "-",  2.0, r"Var-PIC BSSN ($M/8$)"),
        ("V1_iter6_M8_z4c_varpic",                3, cz.PAL["blue"],   "-",  1.9, r"Var-PIC Z4c ($M/8$)"),
    ]
    for rn, idx, col, ls, lw, lab in h_series:
        s, prof = azimuthal_H_line(rn, idx=idx)
        if s is not None:
            ax.plot(s, prof * 1e3, color=col, ls=ls, lw=lw, label=lab)
    ax.set_xlim(-0.88, 0.88)
    ax.set_ylim(-3.1, 1.9)
    ax.set_xlabel(r"Azimuthal offset $(\mathbf{x}-\mathbf{x}_p)\cdot\hat{\boldsymbol{\phi}}\,[M]$", labelpad=-1)
    ax.set_ylabel(r"Hamiltonian $\mathcal{H}\;[10^{-3}\,M^{-2}]$")
    ax.set_title(r"Particle Constraint Wake ($t = 30\,M$, $\sigma=0.223\,M$)", fontsize=10.3)
    ax.legend(frameon=False, fontsize=7.2, ncol=1, loc="lower left")

    # --- Panel 4 (Bottom-Right): Matched-grid vacuum-subtracted (2,2) waveform & amplitude ---
    ax = axes[1, 1]
    ax.axhline(1.560, **cz.REF_LINE, label=r"1SF ($1.56\times 10^{-5}$)")
    ax.axhline(-1.560, color="k", lw=1.2, ls="--", alpha=0.55)
    u1, re1, _, amp1 = load_psi4_22_sub("V1_iter6_M8_z4c_varpic", "V0_iter6_M8_q0_varpic", rval=38)
    u2, re2, _, amp2 = load_psi4_22_sub("V2_iter6_M8_bssn_varpic", "K15_iter6_M8_bssn_q0_vac550", rval=38)
    m1 = (u1 >= 15.0) & (u1 <= 78.0)
    m2 = (u2 >= 15.0) & (u2 <= 78.0)
    ax.plot(u1[m1], re1[m1] * 1e5, color=cz.PAL["blue"], lw=1.5, ls="--", label=r"$\mathrm{Re}$ Var-PIC Z4c")
    ax.plot(u2[m2], re2[m2] * 1e5, color=cz.PAL["red"],  lw=1.6, ls="-",  label=r"$\mathrm{Re}$ Var-PIC BSSN")
    ax.plot(u1[m1], amp1[m1] * 1e5, color=cz.PAL["blue"], lw=1.3, alpha=0.75)
    ax.plot(u2[m2], amp2[m2] * 1e5, color=cz.PAL["red"],  lw=1.5, alpha=0.85, label=r"$|r\Psi_4^{(2,2)}|_{\rm sub}$ env.")
    ax.set_xlim(15, 78)
    ax.set_ylim(-2.1, 3.25)
    ax.set_xlabel(r"Retarded time $u = t - r_*\,[M]$", labelpad=-1)
    ax.set_ylabel(r"$r\Psi_4^{(2,2)}\;[10^{-5}\,M^{-1}]$")
    ax.set_title(r"Matched Vac.-Subtracted $(2,2)$ ($r = 38\,M$)", fontsize=10.3)
    ax.legend(frameon=False, fontsize=7.0, ncol=2, loc="upper right", columnspacing=0.6, handlelength=1.5)

    out_png = os.path.join(OUT, "fig_bugs6to10_varpic_convergence.png")
    fig.savefig(out_png, dpi=300)
    plt.close(fig)
    print("Saved:", out_png)


if __name__ == "__main__":
    main()
