#!/usr/bin/env python3
"""V2 of the G0 verifier: freezing of super-horizon modes, full vs deformed MS equation.

Independent of the track's ms_reference.py: background and modes are integrated jointly in
cosmic time (time unit 1/H0, Mpl = 1).
  full:      Rddot + (3 - eps2) H Rdot + (k/a)^2 R = 0          (P1 PRD_v2.tex:302-304)
  deformed:  delta phi on unperturbed FLRW (no metric perturbations, sigma_BZ = 0 of
             BZ Manuscript.tex:186-189), dphi_ddot + 3 H dphi_dot + (k^2/a^2 + V'') dphi = 0,
             R_def = H dphi / phidot.
Both start from the same Bunch-Davies delta phi (flat gauge, R = H dphi/phidot) at
N_start = max(N0, N where k = 1000 a H). Lattice wave numbers k = q dk with dk = a* H* (sigma =
1, L k_sigma* = 2 pi, a* = 1; P1:511-519). Writes v2.json and two figures into --out.
"""
import argparse
import os

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

import common
from common import Background, inflection, quadratic, save_json

Q2 = [1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 1024, 4096]


def run_mode(bg, q2, Nend):
    m = bg.m
    T = bg.T                                  # 1/H0
    Ns = m["dNstar"]
    Hs = bg.at_N(Ns)["H"] * T                 # H* in units of H0
    q = np.sqrt(q2)
    k = q * Hs                                # a* = 1, dk = a* H*, |n| = sqrt(q2)

    def aH(N):
        s = bg.at_N(N)
        return np.exp(N - Ns) * s["H"] * T

    if k / aH(0.0) <= 1000.0:
        Nst = 0.0
    else:
        Nst = brentq(lambda N: k / aH(N) - 1000.0, 0.0, Ns + 0.5, xtol=1e-12)
    s = bg.at_N(Nst)
    tau0 = s["tau"]
    f, fd = s["phi"], s["phidot"] * T
    H = s["H"] * T
    a = np.exp(Nst - Ns)
    e1, e2 = s["eps1"], s["eps2"]
    ct = -1.0 / ((1 - e1) * a * H)            # conformal time (quasi de Sitter)
    ph = np.exp(-1j * k * ct) / np.sqrt(2 * k)
    fm = ph * (1 - 1j / (k * ct))             # f = a delta phi
    dfm = ph * (-1j * k * (1 - 1j / (k * ct)) + 1j / (k * ct**2))
    dphi = fm / a
    dphi_dot = (dfm - a * H * fm) / a**2      # d/dt = (1/a) d/dct
    R = H * dphi / fd
    Rdot = (H / fd) * (dphi_dot + 0.5 * H * e2 * dphi)

    V, dV, d2V = m["V"], m["dV"], m["d2V"]

    def rhs(t, y):
        f, fd, lna = y[0], y[1], y[2]
        Vt = V(f) * T**2
        H = np.sqrt((0.5 * fd**2 + Vt) / 3.0)
        fdd = -3 * H * fd - dV(f) * T**2
        e1 = 0.5 * fd**2 / H**2
        e2 = -2 * fdd / (H * fd) - 2 * e1
        k2a2 = k**2 * np.exp(-2 * (lna - Ns))
        Rr, Ri, Rdr, Rdi, pr, pi, pdr, pdi = y[3:]
        out = [fd, fdd, H,
               Rdr, Rdi, -(3 - e2) * H * Rdr - k2a2 * Rr, -(3 - e2) * H * Rdi - k2a2 * Ri,
               pdr, pdi, -3 * H * pdr - (k2a2 + d2V(f) * T**2) * pr,
               -3 * H * pdi - (k2a2 + d2V(f) * T**2) * pi]
        return out

    y0 = [f, fd, Nst, R.real, R.imag, Rdot.real, Rdot.imag,
          dphi.real, dphi.imag, dphi_dot.real, dphi_dot.imag]

    def ev(t, y):
        return y[2] - Nend
    ev.terminal = True
    sol = solve_ivp(rhs, (tau0, tau0 + 60.0), y0, method="DOP853", rtol=1e-11, atol=1e-30,
                    events=ev, dense_output=True)
    assert sol.status == 1, sol.message
    tt = np.linspace(tau0, sol.t[-1], 6000)
    Y = sol.sol(tt)
    N = Y[2]
    fdv = Y[1]
    Hv = np.sqrt((0.5 * fdv**2 + V(Y[0]) * T**2) / 3.0)
    e1v = 0.5 * fdv**2 / Hv**2
    Pf = k**3 * (Y[3]**2 + Y[4]**2) / (2 * np.pi**2)
    Rd = (Hv / fdv) * (Y[7] + 1j * Y[8])
    Pd = k**3 * np.abs(Rd)**2 / (2 * np.pi**2)
    # crossing k = aH and the slow-roll estimate there
    aHv = np.exp(N - Ns) * Hv
    i = np.argmin(np.abs(np.log(k / aHv)))
    Nk = np.interp(0.0, np.log(k / aHv)[::-1], N[::-1])
    Pstar = (np.interp(Nk, N, Hv))**2 * (1 / T**2) / (8 * np.pi**2 * np.interp(Nk, N, e1v))
    # P in units: k^3 |R|^2 with k in H0 units and R from delta phi in units... convert:
    # dphi was built with k in H0 units (time unit 1/H0, Mpl = 1): |dphi|^2 ~ 1/k carries
    # H0^2 relative to physical units -> multiply P by H0^2 = 1/T^2.
    Pf = Pf / T**2
    Pd = Pd / T**2
    return dict(q=q, N=N - Ns, Pf=Pf, Pd=Pd, Nk=Nk - Ns, Pstar=Pstar, Nstart=Nst - Ns)


def slope(N, P, a, b):
    sel = (N >= a) & (N <= b)
    if sel.sum() < 5:
        return np.nan
    return np.polyfit(N[sel], np.log(P[sel]), 1)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    curves = {}
    for mdl in (quadratic(), inflection("dN")):
        Ns, Nf = mdl["dNstar"], mdl["dNstar"] + mdl["dNsim"]
        bg = Background(mdl, Nend=Nf + 0.2)
        rows = []
        cur = []
        for q2 in Q2:
            r = run_mode(bg, q2, Nf)
            N, Pf, Pd = r["N"], r["Pf"], r["Pd"]
            iF = -1
            Nf_ = mdl["dNsim"]
            row = dict(k_over_dk=r["q"], Nk=r["Nk"], Nstart=r["Nstart"],
                       full_over_SR_at_crossing=Pf[iF] / r["Pstar"],
                       deformed_over_full_Nf=Pd[iF] / Pf[iF],
                       drift_full_from_Nk4=slope(N, Pf, r["Nk"] + 4, Nf_),
                       drift_full_from_Nk3=slope(N, Pf, r["Nk"] + 3, Nf_),
                       drift_def_from_Nk3=slope(N, Pd, r["Nk"] + 3, Nf_),
                       ratio_full_Nf_over_Nk4=(Pf[iF] / np.interp(r["Nk"] + 4, N, Pf)
                                               if r["Nk"] + 4 < Nf_ else np.nan),
                       ratio_def_Nf_over_Nk4=(Pd[iF] / np.interp(r["Nk"] + 4, N, Pd)
                                              if r["Nk"] + 4 < Nf_ else np.nan),
                       full_Nf=Pf[iF])
            row["A3_def_over_full_ratio"] = row["ratio_def_Nf_over_Nk4"] / row["ratio_full_Nf_over_Nk4"]
            rows.append(row)
            cur.append(r)
            print(mdl["name"], {k: float("%.6g" % v) for k, v in row.items()})
        res[mdl["name"]] = rows
        curves[mdl["name"]] = cur
    save_json(os.path.join(a.out, "v2.json"), res)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    for j, case in enumerate(["SR", "USR"]):
        cols = fs.series_colors(4)
        for c, r in zip(cols, [cur for cur in curves[case] if round(cur["q"]**2) in (1, 4, 32, 4096)]):
            sel = r["N"] > -0.5
            ax[j].semilogy(r["N"][sel], r["Pf"][sel], color=c, label=r"$k=%.3g\,dk$" % r["q"])
            ax[j].semilogy(r["N"][sel], r["Pd"][sel], color=c, ls="--")
        ax[j].set_xlabel(r"$N-N^\ast$")
        ax[j].set_title({"SR": "quadratic: full (solid), deformed (dashed)",
                         "USR": "inflection: full (solid), deformed (dashed)"}[case], fontsize=9)
        ax[j].legend(ncol=2, fontsize=8)
    ax[0].set_ylabel(r"$\Delta_{\mathcal{R}}=k^3|\mathcal{R}_k|^2/2\pi^2$")
    fig.savefig(os.path.join(a.out, "fig_v2_modes.png"))

    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.9, wspace=0.3)
    for j, case in enumerate(["SR", "USR"]):
        q = [r["k_over_dk"] for r in res[case]]
        ax[j].semilogx(q, [r["deformed_over_full_Nf"] for r in res[case]], "o-",
                       color=fs.PAL["red"], label="mine")
        ax[j].set_xlabel(r"$k/dk$")
        ax[j].set_title(case + r": deformed/full at $N_f$", fontsize=9)
    cl_sr = dict(q=[1, 64], v=[0.65, 0.79])
    cl_usr = dict(q=[1, 2.83, 4, 5.66, 11.3, 64], v=[8.40, 1.4, 1.18, 1.07, 1.003, 1.0])
    ax[0].plot(cl_sr["q"], cl_sr["v"], "s", color=fs.PAL["blue"], mfc="none", label="track's claim")
    ax[1].plot(cl_usr["q"], cl_usr["v"], "s", color=fs.PAL["blue"], mfc="none", label="track's claim")
    ax[1].set_yscale("log")
    for x in ax:
        x.legend()
    fig.savefig(os.path.join(a.out, "fig_v2_ratio.png"))


if __name__ == "__main__":
    main()
