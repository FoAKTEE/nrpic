#!/usr/bin/env python3
"""V4: lowest radial mode of F21's pulsation operator by Rayleigh-Ritz with a global basis.

Operator (Chandrasekhar 1964 as printed in F21 main.tex:201-206), u = r^2 e^{-Phi} xi:
    (P u')' + (Q + omega^2 W) u = 0,
    P = e^{3Phi+Lambda} gamma p / r^2,
    Q = -e^{3Phi+Lambda}/r^2 [ (4/r) p' + 8 pi e^{2Lambda} p (rho + p) - p'^2/(rho + p) ],
    W = e^{3Lambda+Phi} (rho + p) / r^2.
Rayleigh quotient omega^2 = (int P u'^2 - int Q u^2) / int W u^2 (boundary terms vanish:
p(R) = 0, u ~ r^3 at the centre). Basis u_k = r^3 L_k(x), x = 2 phi(r)/phi(R) - 1,
phi = r^2/(r^2 + a^2) (even in r, a a core scale), L_k Legendre. This is not the track's
piecewise-linear FEM. Limit check: Gamma = 2, K = 100 polytrope, where omega_0^2 = 0 must
sit at the maximum of M(rho_c) (turning-point theorem for barotropic stars, BACKGROUND).
Output (argv[1]): v_pulsation.json, fig_v4_pulsation.{png,pdf}.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh
from scipy.optimize import brentq, minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, *[".."] * 5))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "python"))
import kingsolve as ks          # noqa: E402

FOURPI = 4 * np.pi


def nodes(R, npanel=400, ng=8):
    # panels clustered towards the centre and the surface
    t = np.linspace(0, 1, npanel + 1)
    edges = R * (0.5 - 0.5 * np.cos(np.pi * t))
    x, w = np.polynomial.legendre.leggauss(ng)
    a, b = edges[:-1, None], edges[1:, None]
    r = (0.5 * (b - a) * x + 0.5 * (a + b)).ravel()
    wt = (0.5 * (b - a) * w).ravel()
    return r, wt


def rr_lowest(prof, wt, R, K, a, return_trial=False):
    r = prof["r"]
    e3 = prof["ePhi"] ** 3 * prof["eL"]
    P = e3 * prof["gamma"] * prof["p"] / r ** 2
    rp = prof["rho"] + prof["p"]
    Q = -e3 / r ** 2 * (4 / r * prof["dp"] + 8 * np.pi * prof["eL"] ** 2 * prof["p"] * rp
                        - prof["dp"] ** 2 / rp)
    Wt = prof["eL"] ** 3 * prof["ePhi"] * rp / r ** 2
    phi = r * r / (r * r + a * a)
    dphi = 2 * r * a * a / (r * r + a * a) ** 2
    phR = R * R / (R * R + a * a)
    x = 2 * phi / phR - 1
    dx = 2 * dphi / phR
    L = np.polynomial.legendre.legvander(x, K - 1)                     # (n, K)
    dL = np.stack([np.polynomial.legendre.legval(x, np.polynomial.legendre.legder(np.eye(K)[k]))
                   for k in range(K)], axis=1)
    U = r[:, None] ** 3 * L
    dU = 3 * r[:, None] ** 2 * L + r[:, None] ** 3 * dL * dx[:, None]
    A = (dU * (wt * P)[:, None]).T @ dU - (U * (wt * Q)[:, None]).T @ U
    B = (U * (wt * Wt)[:, None]).T @ U
    ev = eigh(A, B, eigvals_only=True, subset_by_index=[0, 0])[0]
    if return_trial:
        I0 = np.sum(wt * e3 * prof["p"] * r * r)
        gcr_op = np.sum(wt * Q * r ** 6) / (9 * I0)
        gav = np.sum(wt * e3 * prof["gamma"] * prof["p"] * r * r) / I0
        trial = (A[0, 0] if K >= 1 else None)
        u0 = r ** 3
        trial = (np.sum(wt * P * (3 * r * r) ** 2) - np.sum(wt * Q * u0 ** 2)) / np.sum(wt * Wt * u0 ** 2)
        return ev, dict(gamma_cr_operator=gcr_op, gamma_avg=gav, omega2_trial=trial)
    return ev


def king_omega2(b, w0, K=14, gamma_fixed=None, trial=False):
    m = ks.solve(b, w0, dense=True)
    R = m["R"]
    r, wt = nodes(R)
    prof = ks.profile(m, r)
    if gamma_fixed is not None:
        prof["gamma"] = np.full_like(r, gamma_fixed)
    # core scale: radius where rho = rho_c/2 (rough)
    a = r[np.argmin(abs(prof["rho"] - 0.5 * m["rho_c"]))]
    out = rr_lowest(prof, wt, R, K, a, return_trial=trial)
    return out, m


# ---- Gamma = 2, K = 100 polytrope (G = c = M_sun = 1) ----
GAM, KPOL = 2.0, 100.0


def poly_solve(rhoc, dense=True):
    def eos(P):
        P = max(P, 0.0)
        r0 = (P / KPOL) ** (1 / GAM)
        return r0, r0 + P / (GAM - 1)

    def rhs(r, y):
        M, P = y[0], y[1]
        r0, e = eos(P)
        g = 1 - 2 * M / r
        dphi = (M + FOURPI * r ** 3 * P) / (r * r * g)
        return [FOURPI * r * r * e, -(e + P) * dphi, dphi]

    def surf(r, y):
        return y[1] - 1e-14 * Pc
    surf.terminal = True
    Pc = KPOL * rhoc ** GAM
    ec = rhoc + Pc / (GAM - 1)
    r0 = 1e-6
    sol = solve_ivp(rhs, [r0, 100], [FOURPI / 3 * ec * r0 ** 3, Pc, 0.0], events=surf,
                    method="DOP853", rtol=1e-11, atol=1e-16, dense_output=dense)
    R = sol.t_events[0][0]
    M = sol.y_events[0][0][0]
    return dict(R=R, M=M, sol=sol, rhoc=rhoc, eos=eos, PhiR=sol.y_events[0][0][2])


def poly_omega2(rhoc, K=12):
    m = poly_solve(rhoc)
    R, M = m["R"], m["M"]
    r, wt = nodes(R)
    Y = m["sol"].sol(r)
    Mr, P = Y[0], np.maximum(Y[1], 0)
    r0 = (P / KPOL) ** (1 / GAM)
    rho = r0 + P / (GAM - 1)
    g = 1 - 2 * Mr / r
    dPhi = (Mr + FOURPI * r ** 3 * P) / (r * r * g)
    ePhi = np.exp(Y[2] - m["PhiR"]) * np.sqrt(1 - 2 * M / R)
    prof = dict(r=r, rho=rho, p=P, gamma=np.full_like(r, GAM), ePhi=ePhi, eL=g ** -0.5,
                dp=-(rho + P) * dPhi)
    return rr_lowest(prof, wt, R, K, a=0.4 * R), M


def main(out):
    os.makedirs(out, exist_ok=True)
    res = {}
    # polytrope limit check
    rmax = minimize_scalar(lambda x: -poly_solve(x, dense=False)["M"], bounds=(2e-3, 5e-3),
                           method="bounded", options=dict(xatol=1e-10)).x
    rzero = brentq(lambda x: poly_omega2(x)[0], 2.0e-3, 4.5e-3, xtol=1e-10)
    conv = {K: poly_omega2(rmax, K)[0] for K in (4, 8, 12)}
    res["polytrope"] = dict(rhoc_Mmax=rmax, M_max=poly_solve(rmax, False)["M"],
                            rhoc_omega0=rzero, omega2_at_Mmax_vs_K=conv)
    # F21 b = 0.1: convergence, trial check, root
    conv = {}
    for K in (4, 8, 12, 16, 20):
        conv[K] = king_omega2(0.1, 4.0515, K=K)[0]
    ev, tr = king_omega2(0.1, 4.0515, K=16, trial=True)[0]
    m = ks.solve(0.1, 4.0515)
    res["b0.1_w4.0515"] = dict(omega2_vs_K=conv, trial=tr, gamma_cr_closed_form=m["gamma_cr"],
                               gamma_avg_solver=m["gamma_avg"], rho_c=m["rho_c"])
    roots = {}
    for b, (lo, hi) in {0.1: (3.2, 4.0), 0.5: (0.57, 0.66)}.items():
        w = brentq(lambda x: king_omega2(b, x, K=16)[0], lo, hi, xtol=1e-7)
        mm = ks.solve(b, w)
        w8 = brentq(lambda x: king_omega2(b, x, K=10)[0], lo, hi, xtol=1e-7)
        roots[str(b)] = dict(w0=w, Z0=mm["Z0"], eps=mm["eps"], w0_K10=w8,
                             Z0_K10=ks.solve(b, w8)["Z0"])
    res["fluid_onset_gamma_1_plus_p_over_u"] = roots
    w53 = brentq(lambda x: king_omega2(0.1, x, K=16, gamma_fixed=5 / 3)[0], 3.6, 6.0, xtol=1e-7)
    res["fluid_onset_gamma_5_3_b0.1"] = dict(w0=w53, Z0=ks.solve(0.1, w53)["Z0"])
    # curve for the figure
    ws = np.linspace(2.6, 4.6, 21)
    res["curve_b0.1"] = [dict(w0=float(w), Z0=float(ks.solve(0.1, w)["Z0"]),
                              omega2=float(king_omega2(0.1, w, K=16)[0]),
                              trial=float(king_omega2(0.1, w, K=16, trial=True)[0][1]["omega2_trial"]))
                         for w in ws]
    with open(os.path.join(out, "v_pulsation.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(4, 3.2))
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
    c = res["curve_b0.1"]
    ax.plot([q["Z0"] for q in c], [q["omega2"] for q in c], "o-", color=fs.PAL["red"],
            label=r"lowest $\omega^2$ (Ritz, 16 terms)")
    ax.plot([q["Z0"] for q in c], [q["trial"] for q in c], "s--", color=fs.PAL["blue"],
            label=r"trial $\xi = r e^{\Phi}$")
    ax.axhline(0, color="grey", lw=0.8)
    ax.axvline(roots["0.1"]["Z0"], **fs.GUIDE, label=f"onset Z(0)={roots['0.1']['Z0']:.4f}")
    ax.set_xlabel("$Z(0)$ (b = 0.1)")
    ax.set_ylabel(r"$\hat\omega^2$")
    ax.set_yscale("symlog", linthresh=1.0)
    ax.legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(out, "fig_v4_pulsation"))
    print(json.dumps({k: v for k, v in res.items() if k != "curve_b0.1"}, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NRPIC_RUN_DIR", "."))
