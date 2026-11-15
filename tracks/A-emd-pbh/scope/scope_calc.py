#!/usr/bin/env python3
"""Semi-analytic numbers behind tracks/A-emd-pbh/scope/SCOPE.md (Track A, gate G0).

Tests T1-T5 of scope/JOURNAL.md (predictions written there before the first run):
  T1  hoop criterion of arXiv:2609.14218 (eigenvalues, h-hat, its blue line)
  T2  collapse times of the particle runs of arXiv:2609.14218 against top-hat shells
  T3  expanding-ball geometry: start epoch and largest amplitude the ball can hold
  T4  velocity-dispersion axis (critical s) and particle-number floor (T4b)
  T5  compute estimate from measured costs (run jeans/n1e4_v19, docs/ and cosmo/ TESTLOG)

Only exact or semi-analytic reference relations and arithmetic; no simulation. Units
G = c = 1. Usage:

    python3 scope_calc.py --out <dir> [--v19 <run dir of jeans/n1e4_v19>]

Writes <dir>/scope_numbers.json and the figures <dir>/fig_*.{pdf,png}.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np
from scipy.special import ellipe

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs  # noqa: E402

DELTA_C = 3.0 / 20.0 * (12.0 * np.pi) ** (2.0 / 3.0)   # 1.686, linear contrast at top-hat collapse
DELTA_TA = 3.0 / 20.0 * (6.0 * np.pi) ** (2.0 / 3.0)   # 1.062, at turnaround (2610.23218 main.tex l.126)


# ----------------------------------------------------------------------------- T1
def ln_psi(X, Y, Z, mu, k, e, p):
    """Profile of arXiv:2609.14218, MDPBH.tex line 839."""
    r2 = X * X + Y * Y + Z * Z
    return 0.5 * mu * np.exp(-k * k * r2 / 6.0) * (
        1.0 + k * k / 6.0 * (p * (2 * X * X - Y * Y - Z * Z) + 3 * e * (Y * Y - Z * Z)))


def hessian_at_origin(f, h):
    o = np.zeros(3)
    H = np.zeros((3, 3))
    f0 = f(*o)
    for i in range(3):
        ei = np.zeros(3); ei[i] = h
        H[i, i] = (f(*(o + ei)) - 2 * f0 + f(*(o - ei))) / h ** 2
        for j in range(i + 1, 3):
            ej = np.zeros(3); ej[j] = h
            H[i, j] = H[j, i] = (f(*(ei + ej)) - f(*(ei - ej)) - f(*(-ei + ej)) + f(*(-ei - ej))) / (4 * h * h)
    return H


def h_1609(a, b, g):
    """h(alpha, beta, gamma) of arXiv:1609.01588, apj_nonsphericalpbh.tex line 604-607
    (E(e) with modulus e: scipy's ellipe takes the parameter m = e^2)."""
    x = (a - b) / (a - g)
    return 2.0 / np.pi * (a - g) / a ** 2 * ellipe(1.0 - x * x)


def h_hat(e, p):
    """h-hat(e, p) of arXiv:2609.14218, MDPBH.tex line 918."""
    x = (e + p) / (2.0 * e)
    return 15.0 / np.pi * e / (1 + 3 * e + p) ** 2 * ellipe(1.0 - x * x)


def test_T1():
    k, K = 1.0, 6.0                  # K = k^2/(a^2 H^2); 6 at horizon entry
    out = {"eig_rel_err": [], "h_rel_err": []}
    for (mu, e, p) in [(0.05, 0.2, 0.0), (0.3, 0.1, 0.05), (0.5, 0.25, -0.1), (0.045, 0.2, 0.0)]:
        f = lambda X, Y, Z: ln_psi(X, Y, Z, mu, k, e, p)
        Hs = hessian_at_origin(f, 1e-3)
        mgD = -(4.0 / 5.0) * (K / k ** 2) * Hs       # -grad D, D = (4/5)(aH)^-2 grad ln Psi (l.892)
        num = np.sort(np.linalg.eigvalsh(mgD))[::-1]
        closed = 2 * mu / 15 * K * np.array([1 + 3 * e + p, 1 - 2 * p, 1 - 3 * e + p])
        out["eig_rel_err"].append(float(np.max(np.abs(num / closed - 1))))
        h_direct = h_1609(*closed)
        h_paper = h_hat(e, p) * 6.0 / (mu * K)
        out["h_rel_err"].append(float(abs(h_direct / h_paper - 1)))
    readoff_e = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
    readoff_mu = np.array([0.22, 0.34, 0.41, 0.45, 0.47, 0.48])   # blue line, thre_p0.pdf, by eye
    hh = h_hat(readoff_e, 0.0)
    out["readoff_e"] = readoff_e.tolist()
    out["readoff_mu"] = readoff_mu.tolist()
    out["h_hat_e_p0"] = hh.tolist()
    out["max_abs_dev_readoff"] = float(np.max(np.abs(hh - readoff_mu)))
    out["h_hat_0.2_0"] = float(h_hat(0.2, 0.0))
    out["pass"] = bool(max(out["eig_rel_err"]) < 1e-4 and max(out["h_rel_err"]) < 1e-4
                       and out["max_abs_dev_readoff"] < 0.03)
    return out


def fig_T1(path, t1):
    fs.use_style()
    fig = fs.plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax1 = fig.add_axes([0.08, 0.15, 0.36, 0.78])
    ax2 = fig.add_axes([0.60, 0.15, 0.36, 0.78])
    e = np.linspace(1e-3, 0.3, 300)
    p = np.linspace(-0.3, 0.3, 300)
    E, P = np.meshgrid(e, p)
    with np.errstate(invalid="ignore", divide="ignore"):
        Hh = h_hat(E, P)
    ok = (P >= -E) & (P <= E) & (1 - 3 * E + P >= 0)
    Hh = np.where(ok, Hh, np.nan)
    cs = ax1.contour(E, P, Hh, levels=[0.1, 0.2, 0.3, 0.4, 0.45, 0.5], colors="k", linewidths=1.0)
    ax1.clabel(cs, fmt="%.2f", fontsize=8)
    ax1.fill_between(e, -0.3, -e, color="grey", alpha=0.25, lw=0)
    ax1.fill_between(e, e, 0.3, color="grey", alpha=0.25, lw=0)
    ax1.set_xlabel(r"ellipticity $e$")
    ax1.set_ylabel(r"prolateness $p$")
    ax1.set_xlim(0, 0.3); ax1.set_ylim(-0.3, 0.3)
    ax1.text(0.02, 0.25, r"$\hat h(e,p)$; grey: excluded", fontsize=9)
    ax2.plot(e, h_hat(e, 0.0), color=fs.PAL["blue"], label=r"$\hat h(e,0)$ (this script)")
    ax2.plot(t1["readoff_e"], t1["readoff_mu"], "o", color=fs.PAL["red"], ms=5,
             label="blue line of 2609.14218, read by eye")
    ax2.set_xlabel(r"ellipticity $e$")
    ax2.set_ylabel(r"hoop threshold $\mu$ at $aH=k/\sqrt{6}$")
    ax2.set_xlim(0, 0.3); ax2.set_ylim(0, 0.55)
    ax2.legend(loc="lower right")
    return fs.save(fig, path)


# ----------------------------------------------------------------------------- T2
def mean_contrast_check(mu=0.05):
    """deltabar(r) at horizon entry from delta = -(4/5)(aH)^-2 lap ln Psi, numerically,
    against the closed form (12/5) mu exp(-k^2 r^2/6) (k = 1, K = 6)."""
    k, K, h = 1.0, 6.0, 1e-3
    r = np.linspace(1e-4, 4.0, 4001)
    f = lambda x: ln_psi(x, 0 * x, 0 * x, mu, k, 0.0, 0.0)
    lap = (f(r + h) - 2 * f(r) + f(r - h)) / h ** 2 + 2.0 / r * (f(r + h) - f(r - h)) / (2 * h)
    delta = -(4.0 / 5.0) * K * lap
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (delta[1:] * r[1:] ** 2 + delta[:-1] * r[:-1] ** 2) * np.diff(r))])
    dbar = 3.0 * cum[1:] / r[1:] ** 3
    closed = 12.0 / 5.0 * mu * np.exp(-r[1:] ** 2 / 6.0)
    sel = r[1:] > 0.05
    return float(np.max(np.abs(dbar[sel] - closed[sel]) / closed[0]))


def t_collapse(dbar):
    return (DELTA_C / dbar) ** 1.5


def test_T2():
    mus = np.array([0.15, 0.10, 0.075, 0.06, 0.05])
    t_read = np.array([46.0, 74.0, 106.0, 144.0, 199.0])     # alpha.pdf of 2609.14218, by eye
    t_err = np.array([3.0, 3.0, 3.0, 3.0, 10.0])
    extra = {"mu0.3_e0.2": 24.0, "mu0.3_e0.0": 11.5}
    d0 = 12.0 / 5.0 * mus
    t_lo = t_collapse(d0)                       # centre
    t_hi = t_collapse(d0 / np.e)                # compaction radius r_m: deltabar = d0/e
    inside = (t_read >= t_lo - t_err) & (t_read <= t_hi + t_err)
    slope = np.polyfit(np.log(mus), np.log(t_read), 1)[0]
    mu_fd = lambda tend: DELTA_C * np.e / (12.0 / 5.0) / tend ** (2.0 / 3.0)
    ratio = t_read / t_hi
    out = {
        "mean_contrast_formula_max_err": mean_contrast_check(),
        "mu": mus.tolist(), "t_read": t_read.tolist(), "t_c_centre": t_lo.tolist(),
        "t_c_rm": t_hi.tolist(), "inside": inside.tolist(), "slope": float(slope),
        "ratio_read_to_tc_rm": ratio.tolist(),
        "mu_fd_250": float(mu_fd(250.0)), "mu_fd_100": float(mu_fd(100.0)),
        "mu_fd_400": float(mu_fd(400.0)), "mu_fd_1000": float(mu_fd(1000.0)),
        "extra_readoffs": extra,
        "t_c_rm_mu0.3": float(t_collapse(12 / 5 * 0.3 / np.e)),
        "t_c_centre_mu0.3": float(t_collapse(12 / 5 * 0.3)),
        "t_c_rm_mu0.045": float(t_collapse(12 / 5 * 0.045 / np.e)),
        "t_pancake_e0.2_mu0.05": float((1.0 / (0.8 * 0.05 * 1.6)) ** 1.5),
    }
    # amplitude whose collapse at the measured ratio (median of read/t_c(r_m)) is 250 t_H
    rmed = float(np.median(ratio))
    out["median_ratio"] = rmed
    out["mu_fd_250_scaled"] = float(DELTA_C * np.e / 2.4 * (rmed / 250.0) ** (2.0 / 3.0))
    out["pass"] = bool(np.sum(~inside) < 2 and -1.8 <= slope <= -1.2)
    return out


def fig_T2(path, t2):
    fs.use_style()
    fig = fs.plt.figure(figsize=(fs.COLUMN_WIDTH + 0.6, 3.4))
    ax = fig.add_axes([0.16, 0.14, 0.80, 0.82])
    mu = np.logspace(np.log10(0.03), np.log10(0.4), 200)
    d0 = 2.4 * mu
    fs.band(ax, mu, t_collapse(d0), t_collapse(d0 / np.e), fs.PAL["blue"])
    ax.plot(mu, t_collapse(d0), color=fs.PAL["blue"], lw=1.0, ls=":", label=r"top hat, centre")
    ax.plot(mu, t_collapse(d0 / np.e), color=fs.PAL["blue"], label=r"top hat, shell $r_m$")
    ax.plot(mu, (1.0 / (0.8 * mu * 1.6)) ** 1.5, color=fs.PAL["green"], lw=1.0, ls="--",
            label=r"first pancake, $e=0.2$")
    ax.errorbar(t2["mu"], t2["t_read"], yerr=[3, 3, 3, 3, 10], fmt="o", color=fs.PAL["red"], ms=4,
                label="2609.14218 particles, $e=0.2$")
    ax.plot([0.3], [t2["extra_readoffs"]["mu0.3_e0.2"]], "o", color=fs.PAL["red"], ms=4)
    ax.plot([0.3], [t2["extra_readoffs"]["mu0.3_e0.0"]], "s", mfc="none", color=fs.PAL["red"], ms=5,
            label=r"same, $e=0$")
    ax.axhline(250.0, **fs.MASK_LINE)
    ax.axvspan(0.045, 0.05, color=fs.PAL["red"], alpha=0.12, lw=0)
    ax.axvline(t2["mu_fd_250"], **fs.GUIDE)
    ax.text(0.0505, 330, r"$\mu_{\rm fd}(250\,t_H)$", fontsize=8)
    ax.text(0.17, 270, "end of plotted runs", fontsize=8, color="grey")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.03, 0.4); ax.set_ylim(2, 600)
    ax.set_xlabel(r"amplitude $\mu$")
    ax.set_ylabel(r"collapse time $t/t_H$")
    ax.legend(loc="lower left", fontsize=8)
    return fs.save(fig, path)


# ----------------------------------------------------------------------------- T3
def test_T3():
    out = {}
    for q in (2.0, 3.0, 4.0):
        rows = []
        for RbH in (0.5, 0.7, 0.9):
            ai = (q / RbH) ** 2          # a_i/a_H: R_b H_i = q (a_H/a_i)^(1/2), r_m H_H = 1
            mu_mean = 0.3 / (2.4 / np.e * ai)       # deltabar(r_m) at start <= 0.3
            mu_centre = 0.3 / (2.4 * ai)            # central linear contrast at start <= 0.3
            rows.append({"RbH_i": RbH, "a_i_over_a_H": ai, "mu_max_mean03": mu_mean,
                         "mu_max_centre03": mu_centre,
                         "dbar_ent_max_mean03": mu_mean * 2.4 / np.e,
                         "ball_compactness_2M_over_R": RbH ** 2,
                         "profile_at_edge_rel": float(np.exp(-q * q))})
        out[f"q{q:.0f}"] = rows
    out["pass"] = bool(abs(out["q3"][2]["mu_max_mean03"] / 0.03 - 1) < 0.2
                       and abs(out["q2"][2]["mu_max_mean03"] / 0.07 - 1) < 0.2)
    return out


# ----------------------------------------------------------------------------- T4
def test_T4():
    s_2211 = 1.5                         # sigma_v R > (3/2) R_ent, R_ent = 2M (MD_threshold10.tex l.358)
    s_virial = np.sqrt(3.0 / 10.0)       # (10/3) s^2 C_ta < C_ta with the 5/3 of 2507.18312 (Main.tex l.542)
    dbar = np.array([0.01, 0.02, 0.04, 0.08])
    bBH = 5.0 / 3.0 * dbar
    N_lat = (0.1 * bBH) ** (-9.0 / 4.0)
    N_poi = (1.2 / (0.1 * bBH)) ** 3
    out = {"s_c_2211": s_2211, "s_c_virial": float(s_virial),
           "dbar": dbar.tolist(), "b_BH": bBH.tolist(),
           "N_lattice_for_noise_0.1bBH": N_lat.tolist(), "N_random_for_noise_0.1bBH": N_poi.tolist()}
    out["pass_T4"] = bool(0.4 <= s_virial <= 2 and 0.4 <= s_2211 <= 2)
    out["pass_T4b"] = bool(abs(np.log(N_lat[2] / 1e5)) < np.log(2) and abs(np.log(N_poi[2] / 5e6)) < np.log(2)
                           and abs(np.log(N_lat[0] / 2e6)) < np.log(2))
    return out


# ----------------------------------------------------------------------------- T5
def v19_cost(v19dir):
    segs = sorted(glob.glob(os.path.join(v19dir, "chain", "seg*.log")))
    cpu, zc = [], []
    for s in segs:
        txt = open(s, errors="replace").read()
        m = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        if m:
            cpu.append(float(m[-1]))
        z = re.findall(r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)", txt)
        if z:
            zc.append(float(z[-1]))
    return {"segments": len(segs), "seconds": float(np.sum(cpu)), "card_hours": float(np.sum(cpu) / 3600.0),
            "zone_cycles_per_s": zc, "cycles": 25600, "s_per_cycle": float(np.sum(cpu) / 25600.0)}


def ball_run_steps(dbar, bh=True, f_bh=0.3, n_R=32, cfl=0.25, t_end_tH=250.0, post_M=30.0, b_min=0.1):
    """Steps of one expanding-ball run in units M_p (mass inside r_m). Top-hat cycloid of
    the r_m shell; finest cell max(R/n_R, dx_AH); dx_AH = 0.06 M_BH (twelve cells over a
    coordinate horizon radius of 0.73 M_BH, docs/TESTLOG.md 'M/128 production chain')."""
    C = 5.0 / 3.0 * dbar
    Rta = 2.0 / C
    tc = 2.0 * np.pi / C ** 1.5               # t_c = 2 pi M C^-3/2
    tH = 4.0 / 3.0
    th = np.linspace(1e-3, 2 * np.pi, 200001)
    R = 0.5 * Rta * (1 - np.cos(th))
    t = tc / (2 * np.pi) * (th - np.sin(th))
    dx_ah = 0.06 * f_bh
    if bh:
        Rstop = 2.0 * f_bh                    # areal radius of the forming horizon
        sel = (th <= np.pi) | (R >= Rstop)    # expansion, then infall down to the horizon
        tt, RR = t[sel], R[sel]
        dx = np.maximum(RR / n_R, dx_ah)
        steps = np.trapezoid(1.0 / (cfl * dx), tt) + post_M / (cfl * dx_ah)
        t_run = tt.max() + post_M
    else:
        Rmin = b_min * Rta
        sel = (th <= np.pi) | (R >= Rmin)
        tt, RR = t[sel], R[sel]
        dx = np.maximum(RR / n_R, dx_ah)
        steps = np.trapezoid(1.0 / (cfl * dx), tt)
        t_end = t_end_tH * tH
        steps += max(t_end - tt.max(), 0.0) / (cfl * Rmin / n_R)
        t_run = max(t_end, tt.max())
    return float(steps), float(t_run / tH)


def test_T5(v19dir):
    v19 = v19_cost(v19dir) if v19dir and os.path.isdir(v19dir) else None
    s_cycle = v19["s_per_cycle"] if v19 else 19475.5 / 25600
    c_p = (0.31 - 128 ** 3 / 2.0e7) / 2097152      # cosmo/TESTLOG.md l.913-915; docs/TESTLOG.md l.46
    rows = []
    for dbar in (0.01, 0.02, 0.04, 0.08):
        for bh in (True, False):
            steps, trun = ball_run_steps(dbar, bh=bh)
            for Np in (1e5, 1e6):
                hours = steps * (s_cycle + Np * c_p) / 3600.0
                rows.append({"dbar_ent": dbar, "bh": bh, "N_p": Np, "steps": steps,
                             "t_run_over_tH": trun, "card_hours": hours})
    # scan size (SCOPE.md section 5): 5 e-values x 5 bisection runs; convergence 2 x 3 x 3;
    # prolateness 2 x 5; dispersion 3 x 4 -> 25 + 18 + 10 + 12 = 65 runs
    n_runs = 65
    typical = np.median([r["card_hours"] for r in rows if r["N_p"] == 1e6 and r["dbar_ent"] in (0.02, 0.04)])
    out = {"v19": v19, "s_per_cycle_used": s_cycle, "c_p_s_per_particle_step": c_p,
           "rows": rows, "n_runs_first_scan": n_runs,
           "typical_run_card_hours_1e6": float(typical),
           "scan_card_hours": float(n_runs * typical)}
    out["pass"] = bool(1.0 <= typical <= 3.0)
    return out


def fig_T345(path, t3, t4, t5):
    fs.use_style()
    fig = fs.plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.07, 0.15, 0.25, 0.80])
    ax2 = fig.add_axes([0.40, 0.15, 0.25, 0.80])
    ax3 = fig.add_axes([0.73, 0.15, 0.25, 0.80])
    # left: ball window
    RbH = np.linspace(0.3, 0.99, 100)
    for q, c in ((2.0, fs.PAL["blue"]), (3.0, fs.PAL["red"]), (4.0, fs.PAL["green"])):
        ai = (q / RbH) ** 2
        ax1.plot(RbH, 0.3 / (2.4 / np.e * ai), color=c, label=fr"$R_b/r_m={q:.0f}$")
        ax1.plot(RbH, 0.3 / (2.4 * ai), color=c, ls=":", lw=1.0)
    ax1.axhspan(0.045, 0.05, color="grey", alpha=0.3, lw=0)
    ax1.set_yscale("log")
    ax1.set_xlabel(r"$R_b H_i$ (ball / Hubble radius)")
    ax1.set_ylabel(r"largest $\mu$ the ball holds")
    ax1.set_ylim(1e-3, 0.3)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.text(0.32, 0.055, "2609.14218 particle threshold", fontsize=7)
    # middle: velocity dispersion
    s = np.linspace(0, 2.2, 200)
    ax2.plot(s, (10.0 / 3.0) * s ** 2, color=fs.PAL["blue"], label=r"virial, $5/3$ (2507.18312)")
    ax2.plot(s, (8.0 / 9.0) * s ** 2 / 2.0, color=fs.PAL["red"], label=r"$t_{\rm ff}=t_{\rm cross}$ (2211.13950)")
    ax2.axhline(1.0, **fs.GUIDE)
    for sv in (0.25, 0.5, 0.75, 1.0, 1.5, 2.0):
        ax2.axvline(sv, **fs.MASK_LINE)
    ax2.set_yscale("log")
    ax2.set_ylim(1e-2, 20)
    ax2.set_xlabel(r"$s=\sigma_v R/(2M)$")
    ax2.set_ylabel(r"$b_{\rm min}/b_{\rm BH}$")
    ax2.legend(loc="lower right", fontsize=8)
    # right: particle floor and cost
    d = np.logspace(-2.2, -0.9, 100)
    bBH = 5.0 / 3.0 * d
    ax3.plot(d, (0.1 * bBH) ** (-9.0 / 4.0), color=fs.PAL["blue"], label=r"lattice, $N^{-4/9}$")
    ax3.plot(d, (1.2 / (0.1 * bBH)) ** 3, color=fs.PAL["red"], label=r"random, $1.2N^{-1/3}$")
    ax3.axvline(0.044, **fs.MASK_LINE)
    ax3.set_xscale("log"); ax3.set_yscale("log")
    ax3.set_xlabel(r"$\bar\delta_{\rm ent}$")
    ax3.set_ylabel(r"$N$ for noise floor $0.1\,b_{\rm BH}$")
    ax3.legend(loc="upper right", fontsize=8)
    return fs.save(fig, path)


def fig_cost(path, t5):
    fs.use_style()
    fig = fs.plt.figure(figsize=(fs.COLUMN_WIDTH + 0.6, 3.2))
    ax = fig.add_axes([0.16, 0.15, 0.80, 0.80])
    for bh, mk in ((True, "o"), (False, "s")):
        for Np, c in ((1e5, fs.PAL["blue"]), (1e6, fs.PAL["red"])):
            r = [x for x in t5["rows"] if x["bh"] == bh and x["N_p"] == Np]
            ax.plot([x["dbar_ent"] for x in r], [x["card_hours"] for x in r], mk + "-", color=c, ms=4, lw=1.0,
                    mfc=c if bh else "none",
                    label=f"N={Np:.0e}, " + ("black hole" if bh else "no black hole, to 250 $t_H$"))
    if t5["v19"]:
        ax.axhline(t5["v19"]["card_hours"], **fs.MASK_LINE)
        ax.text(0.011, t5["v19"]["card_hours"] * 1.08, "measured: n1e4_v19 (100 M)", fontsize=7, color="grey")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"$\bar\delta_{\rm ent}$")
    ax.set_ylabel("card-hours per run (estimate)")
    ax.legend(loc="upper right", fontsize=7)
    return fs.save(fig, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--v19", default="/data/haiyangw/nrpic/runs/jeans/n1e4_v19")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"T1": test_T1(), "T2": test_T2(), "T3": test_T3(), "T4": test_T4(), "T5": test_T5(a.v19)}
    figs = []
    figs += fig_T1(os.path.join(a.out, "fig_hoop"), res["T1"])
    figs += fig_T2(os.path.join(a.out, "fig_timing"), res["T2"])
    figs += fig_T345(os.path.join(a.out, "fig_design"), res["T3"], res["T4"], res["T5"])
    figs += fig_cost(os.path.join(a.out, "fig_cost"), res["T5"])
    res["figures"] = [os.path.basename(f) for f in figs]
    with open(os.path.join(a.out, "scope_numbers.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for key in ("T1", "T2", "T3", "T4", "T5"):
        r = res[key]
        print(key, {k: v for k, v in r.items() if k.startswith("pass")})


if __name__ == "__main__":
    main()
