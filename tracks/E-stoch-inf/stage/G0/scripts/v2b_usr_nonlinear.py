#!/usr/bin/env python3
"""V2b of the G0 verifier: can the per-mode USR freezing test A3 (modes k <= 3 dk within
10 percent of the full MS at N_f) be contaminated by nonlinear mode coupling in the same box?

(1) delta-N f_NL of the inflection model for modes that exit at N_s (separate universe,
    e-folds, Mpl = 1: phi' = pi, pi' = -(3 - pi^2/2)(pi + V'/V); a kick delta phi at N_s with
    pi unchanged; e-folds to the surface phi = phi_b(N* + 10)); f_NL = (5/6) N''/N'^2.
(2) the power that a local quadratic term R = R_g + (3/5) f_NL (R_g^2 - <R_g^2>) adds at
    k << q, on the noise lattice (dk = 1, L = 2 pi, 1 <= |n| <= 64):
    P_2(k) = 2 (3 f_NL/5)^2 sum_n P(q_n)^2 / L^3 with P = 2 pi^2 Delta/q^3 and Delta(q) the
    full-MS spectrum at N_f of my run V2 (v2.json); ratio r(k) = Delta_2(k)/Delta_lin(k).
    A complex contamination of mean square r gives per-mode power deviations of about
    sqrt(2 r); the A3 tolerance of 10 percent needs r below about 5e-3.
The local quadratic model is a proxy [JUDGEMENT]; it shows the size, not the NR answer.
Writes v2b.json and fig_v2b.png.
"""
import argparse
import json
import os

import numpy as np
from scipy.integrate import solve_ivp

import common
from common import Background, inflection, save_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--v2", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mdl = inflection("dN")
    Ns = mdl["dNstar"]
    bg = Background(mdl, Nend=Ns + 13.0)
    V, dV = mdl["V"], mdl["dV"]
    # end surface 2.5 e-folds after N_f: phi_b(N* + 10) = -0.2798 lies just past the
    # stationary inflection point -sqrt(2) v = -0.2800, where kicked paths may stall
    phi_end = bg.at_N(Ns + 12.5)["phi"]

    def rhs(N, y):
        f, p = y
        return [p, -(3 - 0.5 * p * p) * (p + dV(f) / V(f))]

    def ev(N, y):
        return y[0] - phi_end
    ev.terminal = True
    ev.direction = 1

    def efolds(N0, f0, p0):
        sol = solve_ivp(rhs, (N0, N0 + 40), [f0, p0], method="LSODA", rtol=1e-11,
                        atol=1e-16, events=ev)
        if len(sol.t_events[0]) == 0:
            return np.nan
        return sol.t_events[0][0] - N0

    out = {"phi_end": phi_end, "fNL": {}}
    for dNs in (2.0, 3.0, 3.5, 4.2):
        s = bg.at_N(Ns + dNs)
        f0, p0 = s["phi"], s["phidot"] / s["H"]
        h = 1e-4 * abs(p0)
        xs = h * np.linspace(-1, 1, 9)
        Nv = np.array([efolds(Ns + dNs, f0 + x, p0) for x in xs])
        if not np.all(np.isfinite(Nv)):
            out["fNL"][str(dNs)] = dict(fNL=np.nan, pi=p0, note="a kicked path did not reach the surface")
            print("exit at N*+%.1f: a kicked path did not reach the end surface" % dNs)
            continue
        c = np.polyfit(xs / h, Nv, 4)
        N1 = c[-2] / h
        N2 = 2 * c[-3] / h**2
        out["fNL"][str(dNs)] = dict(N1=N1, N2=N2, fNL=5.0 / 6.0 * N2 / N1**2, pi=p0)
        print("exit at N*+%.1f: dN/dphi %.4g, d2N/dphi2 %.4g, f_NL %.4g" % (
            dNs, N1, N2, 5.0 / 6.0 * N2 / N1**2), flush=True)

    # N(delta phi) over kicks of a few H/2pi (realistic amplitudes, not the curvature only)
    out["N_of_kick"] = {}
    for dNs in (3.0, 4.2):
        s0 = bg.at_N(Ns + dNs)
        f0, p0 = s0["phi"], s0["phidot"] / s0["H"]
        unit = s0["H"] / (2 * np.pi)
        us = np.linspace(-6, 6, 13)
        Nv = np.array([efolds(Ns + dNs, f0 + u * unit, p0) for u in us])
        i0 = int(np.argmin(np.abs(us)))
        lin = out["fNL"][str(dNs)]["N1"] * us * unit
        out["N_of_kick"][str(dNs)] = dict(kick_over_H2pi=us.tolist(), dN=(Nv - Nv[i0]).tolist(),
                                          linear=lin.tolist(), unit=unit, pi=p0)
        print("N(kick) at N*+%.1f, kick/(H/2pi) -6..6:" % dNs,
              np.round(Nv - Nv[i0], 4), "linear:", np.round(lin, 4), flush=True)
    g = bg.grid(6000)
    cN = g["N"] - Ns
    ratio = np.abs(g["phidot"] / g["H"]) / (g["H"] / (2 * np.pi))
    sel = (cN > 0) & (cN < 10.5)
    out["drift_over_diffusion"] = dict(cN=cN[sel][::20].tolist(), ratio=ratio[sel][::20].tolist(),
                                       min=float(ratio[sel].min()),
                                       cN_min=float(cN[sel][np.argmin(ratio[sel])]),
                                       at_Nf=float(np.interp(10.0, cN, ratio)))
    print("drift/diffusion min %.3g at N*+%.2f, at N_f %.3g" % (
        out["drift_over_diffusion"]["min"], out["drift_over_diffusion"]["cN_min"],
        out["drift_over_diffusion"]["at_Nf"]))
    v2 = json.load(open(a.v2))
    rows = v2["USR"]
    q = np.array([r["k_over_dk"] for r in rows])
    D = np.array([r["full_Nf"] for r in rows])
    lnD = lambda x: np.interp(np.log(x), np.log(q), np.log(D))   # noqa: E731
    m = 64
    r = np.arange(-m, m + 1)
    nx, ny, nz = np.meshgrid(r, r, r, indexing="ij")
    q2 = nx**2 + ny**2 + nz**2
    qq = np.sqrt(q2[(q2 >= 1) & (q2 <= 4096)].astype(float))
    L = 2 * np.pi
    P = 2 * np.pi**2 * np.exp(lnD(qq)) / qq**3
    S = np.sum(P**2) / L**3
    low = q <= 3.0
    res_r = {}
    for fnl in (0.05, 0.1, 0.5, 2.5):
        D2 = q[low] ** 3 / (2 * np.pi**2) * 2 * (0.6 * fnl) ** 2 * S
        res_r[str(fnl)] = dict(k=q[low].tolist(), r=(D2 / D[low]).tolist())
        print("f_NL %.2f: r(k) =" % fnl, np.round(D2 / D[low], 4))
    out["r_of_k"] = res_r
    out["Delta_lin_low_k"] = dict(k=q[low].tolist(), Delta=D[low].tolist())
    out["sum_P2_over_L3"] = S
    save_json(os.path.join(a.out, "v2b.json"), out)

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.88, wspace=0.45)
    xs_ = [float(k) for k in out["fNL"]]
    for c_, (k_, d) in zip([fs.PAL["red"], fs.PAL["blue"]], out["N_of_kick"].items()):
        ax[0].plot(d["kick_over_H2pi"], d["dN"], "o", color=c_, label=r"kick at $N^\ast+%s$" % k_)
        ax[0].plot(d["kick_over_H2pi"], d["linear"], "-", color=c_, lw=1.0)
    ax[0].set_xlabel(r"kick $\delta\phi/(H/2\pi)$")
    ax[0].set_ylabel(r"$\delta N$ (lines: linear)")
    ax[0].set_title(r"$f_{\rm NL}\approx%.3f$; surface $N^\ast+12.5$"
                    % out["fNL"]["4.2"]["fNL"], fontsize=9)
    ax[0].legend(fontsize=7)
    dd = out["drift_over_diffusion"]
    ax[2].semilogy(dd["cN"], dd["ratio"], color=fs.PAL["red"])
    ax[2].axhline(1.0, **fs.GUIDE)
    ax[2].set_xlabel(r"$N-N^\ast$")
    ax[2].set_ylabel(r"$|d\phi/dN|\,/\,(H/2\pi)$")
    ax[2].set_title("drift / diffusion per e-fold", fontsize=9)
    cols = fs.series_colors(4)
    for c_, (fnl, d) in zip(cols, res_r.items()):
        ax[1].semilogy(d["k"], d["r"], "o-", color=c_, label=r"$f_{\rm NL}=%s$" % fnl)
    ax[1].axhline(5e-3, **fs.GUIDE, label="A3 10 % tolerance")
    ax[1].set_xlabel(r"$k/dk$")
    ax[1].set_ylabel(r"$\Delta_2/\Delta_{\rm lin}$ at $N_f$")
    ax[1].set_title("local quadratic coupling, modes of A3 (USR)", fontsize=9)
    ax[1].legend(fontsize=7, ncol=2)
    fig.savefig(os.path.join(a.out, "fig_v2b.png"))


if __name__ == "__main__":
    main()
