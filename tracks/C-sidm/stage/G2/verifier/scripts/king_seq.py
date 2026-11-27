#!/usr/bin/env python3
"""Verifier's own equilibrium sequence of the relativistic King family (V1).

Ansatz of arXiv:2009.08163 (paper.tex:634-636): f = (exp(1 - E/E0) - 1)_+, isotropic, with
E = eps e^mu and y = ln E0 - mu (paper.tex:661), so f = phi(eps e^-y), phi(u) = e^(1-u) - 1
for u < 1. Rest mass of a particle 1, G = c = 1. With eps = cosh s:
    g(y) = 4 pi int_0^smax cosh^2 s sinh^2 s phi ds          (energy density)
    h(y) = 4 pi/3 int_0^smax sinh^4 s phi ds                 (pressure)
    n(y) = 4 pi int_0^smax cosh s sinh^2 s phi ds            (rest-frame number density)
smax = acosh(e^y). Field equation (paper.tex:670-673):
    y' = -(m/r^2 + 4 pi r h)/(1 - 2m/r),  m' = 4 pi r^2 g,  N' = 4 pi r^2 n / sqrt(1 - 2m/r)
from y(0) = y0 to the surface y = 0 (areal radius R). Binding energy E_b = (N - M)/N
(paper.tex:922), M = m(R). Central redshift to infinity Z(0) = e^y0 / sqrt(1 - 2M/R) - 1.

Tests before use (written by the verifier, not taken from the track):
  T1 constant density g = rho0, h = rho0 (e^y - 1) (the hydrostatic solution of dh/dy = g + h
     with h(0) = 0): the integrator must give 2M/R = 1 - s^2 with s = e^y0/(3 e^y0 - 2), the
     Schwarzschild interior solution;
  T2 the King quadrature obeys dh/dy = g + h (hydrostatic identity of an isotropic f(E)).
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

GL_X, GL_W = np.polynomial.legendre.leggauss(200)


def king_ghn(y):
    if y <= 0.0:
        return 0.0, 0.0, 0.0
    smax = np.arccosh(np.exp(y))
    s = 0.5 * smax * (GL_X + 1.0)
    w = 0.5 * smax * GL_W
    ch, sh = np.cosh(s), np.sinh(s)
    phi = np.expm1(1.0 - ch * np.exp(-y))
    phi = np.where(phi > 0.0, phi, 0.0)
    g = 4 * np.pi * np.sum(w * ch**2 * sh**2 * phi)
    h = 4 * np.pi / 3 * np.sum(w * sh**4 * phi)
    n = 4 * np.pi * np.sum(w * ch * sh**2 * phi)
    return g, h, n


def solve(y0, ghn, rtol=1e-12, atol=1e-16):
    g0, h0, n0 = ghn(y0)
    r0 = 1e-6 * np.sqrt(1.0 / (g0 + 3 * h0))
    yinit = y0 - (2 * np.pi / 3) * (g0 + 3 * h0) * r0**2
    m_init = 4 * np.pi / 3 * g0 * r0**3
    N_init = 4 * np.pi / 3 * n0 * r0**3

    def rhs(r, u):
        y, m, N = u
        g, h, n = ghn(y)
        f = 1.0 - 2.0 * m / r
        return [-(m / r**2 + 4 * np.pi * r * h) / f, 4 * np.pi * r**2 * g,
                4 * np.pi * r**2 * n / np.sqrt(f)]

    def surf(r, u):
        return u[0]
    surf.terminal = True
    surf.direction = -1
    rmax = 1e3 / np.sqrt(g0 + 3 * h0)
    sol = solve_ivp(rhs, (r0, rmax), [yinit, m_init, N_init], events=surf, rtol=rtol,
                    atol=atol, method="DOP853", dense_output=False)
    if sol.status != 1:
        raise RuntimeError(f"no surface for y0 = {y0}: {sol.message}")
    R = sol.t_events[0][0]
    _, M, N = sol.y_events[0][0]
    return dict(y0=y0, R=R, M=M, N=N, Eb=(N - M) / N, R_over_M=R / M,
                Z0=np.exp(y0) / np.sqrt(1 - 2 * M / R) - 1)


def test_constant_density():
    rho0 = 1e-3
    out = []
    for y0 in (0.05, 0.2, 0.5, 1.0):
        def ghn(y):
            return (rho0, rho0 * np.expm1(y), rho0) if y > 0 else (0.0, 0.0, 0.0)
        r = solve(y0, ghn)
        s = np.exp(y0) / (3 * np.exp(y0) - 2)
        exact = 1 - s**2
        # M = 4 pi/3 rho0 R^3 for constant density
        out.append(dict(y0=y0, twoM_over_R=2 * r["M"] / r["R"], exact=exact,
                        rel_err=abs(2 * r["M"] / r["R"] / exact - 1),
                        mass_rel_err=abs(r["M"] / (4 * np.pi / 3 * rho0 * r["R"]**3) - 1)))
    return out


def test_identity():
    out = []
    for y in (0.01, 0.1, 0.334, 0.8):
        d = 1e-4 * y  # relative step: central-difference error (d/y)^2 ~ 1e-8
        hp = king_ghn(y + d)[1]
        hm = king_ghn(y - d)[1]
        g, h, _ = king_ghn(y)
        out.append(dict(y=y, dhdy=(hp - hm) / (2 * d), g_plus_h=g + h,
                        rel_err=abs((hp - hm) / (2 * d) / (g + h) - 1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    res["T1_constant_density"] = test_constant_density()
    res["T2_identity"] = test_identity()
    t1 = max(t["rel_err"] for t in res["T1_constant_density"])
    t2 = max(t["rel_err"] for t in res["T2_identity"])
    res["tests_pass"] = bool(t1 < 1e-8 and t2 < 1e-7)
    print(f"T1 max rel err {t1:.2e}, T2 max rel err {t2:.2e}, pass {res['tests_pass']}")
    if not res["tests_pass"]:
        json.dump(res, open(os.path.join(a.out, "king_seq.json"), "w"), indent=1)
        sys.exit(1)

    ys = np.linspace(0.02, 1.0, 197)
    seq = [solve(y, king_ghn) for y in ys]
    res["sequence"] = seq
    Eb = np.array([s["Eb"] for s in seq])
    i = int(np.argmax(Eb[:150]))
    opt = minimize_scalar(lambda y: -solve(y, king_ghn)["Eb"], bracket=(ys[i - 1], ys[i], ys[i + 1]),
                          tol=1e-12)
    ymax = float(opt.x)
    res["max"] = solve(ymax, king_ghn)
    # tolerance study of the maximum: ODE rtol 1e-9 and a quadrature of 60 nodes
    global GL_X, GL_W
    keep = (GL_X, GL_W)
    GL_X, GL_W = np.polynomial.legendre.leggauss(60)
    opt2 = minimize_scalar(lambda y: -solve(y, king_ghn, rtol=1e-9, atol=1e-13)["Eb"],
                           bracket=(ys[i - 1], ys[i], ys[i + 1]), tol=1e-12)
    GL_X, GL_W = keep
    res["max"]["y_max_coarse"] = float(opt2.x)
    print(f"y_max {ymax:.9f}; coarse settings {opt2.x:.9f}")
    j = int(np.where((Eb[:-1] > 0) & (Eb[1:] <= 0))[0][0])
    yzero = brentq(lambda y: solve(y, king_ghn)["Eb"], ys[j], ys[j + 1], xtol=1e-12)
    res["zero"] = dict(y_zero=yzero)
    res["members"] = {f"{y:.6f}": solve(y, king_ghn) for y in (0.324, 0.334032, 0.344)}
    for k, v in res["members"].items():
        v["rel_dist_y"] = v["y0"] / ymax - 1
        v["Eb_minus_max"] = v["Eb"] - res["max"]["Eb"]
    # curvature of E_b at the maximum (second difference)
    d = 1e-3
    e0, ep, em = (solve(ymax + x, king_ghn)["Eb"] for x in (0.0, d, -d))
    res["max"]["d2Eb_dy2"] = (ep - 2 * e0 + em) / d**2
    res["max"]["y_max"] = ymax
    json.dump(res, open(os.path.join(a.out, "king_seq.json"), "w"), indent=1)
    print(f"y_max = {ymax:.6f}, Eb_max = {res['max']['Eb']:.6f}, R/M = {res['max']['R_over_M']:.4f},"
          f" Z0 = {res['max']['Z0']:.5f}; y_zero = {yzero:.5f}")
    for k, v in res["members"].items():
        print(f"  y0 {k}: Eb {v['Eb']:.7f} (max {v['Eb_minus_max']:+.2e}), Z0 {v['Z0']:.5f},"
              f" R/M {v['R_over_M']:.3f}, dy/ymax {v['rel_dist_y']:+.4f}")

    # figure
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import matplotlib
    matplotlib.use("Agg")
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.8))
    axs[0].plot(ys, Eb, color=fs.PAL["blue"], lw=1.2, label="verifier solver")
    axs[0].axvline(ymax, color="k", ls=":", lw=0.8)
    axs[0].axhline(0, color="0.6", lw=0.6)
    for y, c in ((0.324, fs.PAL["green"]), (0.344, fs.PAL["red"])):
        axs[0].plot([y], [res["members"][f"{y:.6f}"]["Eb"]], "o", color=c, ms=4,
                    label=f"$y_0={y}$")
    axs[0].plot([0.334], [res["max"]["Eb"]], "x", color="k", ms=5, label="printed $y_{\\max}=0.334$")
    axs[0].plot([0.784], [0.0], "+", color="k", ms=7, label="printed $y_{\\rm zero}=0.784$")
    axs[0].set_xlabel("$y_0$")
    axs[0].set_ylabel("$E_b=(N-M)/N$")
    axs[0].legend(fontsize=6, frameon=False)
    yy = np.linspace(0.30, 0.37, 57)
    ee = [solve(y, king_ghn)["Eb"] for y in yy]
    axs[1].plot(yy, (np.array(ee) - res["max"]["Eb"]) * 1e5, color=fs.PAL["blue"], lw=1.2)
    for y, c in ((0.324, fs.PAL["green"]), (0.344, fs.PAL["red"])):
        axs[1].plot([y], [res["members"][f"{y:.6f}"]["Eb_minus_max"] * 1e5], "o", color=c, ms=4)
    axs[1].axvline(ymax, color="k", ls=":", lw=0.8)
    axs[1].axvline(0.334032, color=fs.PAL["orange"], ls="--", lw=0.8, label="lead 0.334032")
    axs[1].set_xlabel("$y_0$")
    axs[1].set_ylabel("$(E_b-E_{b,\\max})\\times10^5$")
    axs[1].legend(fontsize=6, frameon=False)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_v1_king_sequence"))


if __name__ == "__main__":
    main()
