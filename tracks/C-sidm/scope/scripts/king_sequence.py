#!/usr/bin/env python3
"""Truncated Maxwell-Boltzmann (relativistic King) equilibria, an independent solver of
arXiv:2108.11967 (Feng, Yu, Zhong), main.tex lines 103-153:

    f = exp(alpha) [exp(-eps/kT) - exp(-eps_c/kT)],  eps <= eps_c (kinetic energy),
    w = eps_c/kT,  b = kT(R)/m,  T(r) = T(R)/(1 - b w)          (Tolman-Klein)
    rho-hat = 4 sqrt2 pi I_rho,  n-hat = 4 sqrt2 pi I_n,  p-hat = (8/3) sqrt2 pi I_p,
    u-hat = 4 sqrt2 pi I_u                                      (eq:eos, eq:integrals)
    dM/dr = 4 pi r^2 rho,  dw/dr = -((1 - b w)/b) (4 pi p r^3 + M) / (r (r - 2M))   (eq:tov)

in the units of its eq:Length_scale (G = c = 1, r = zeta r-hat). Per model (b, w0): M-hat,
E_rest-hat, binding energy, fractional binding energy eps_b = 1 - M/E_rest, R-hat,
compactness C = M/R, central redshift Z(0) = (1 - 2C)^(-1/2)/(1 - b w0) - 1, central
3D velocity dispersion v(0) = (3 p/rho)^(1/2), pressure-averaged adiabatic index <gamma>
and critical index gamma_cr (eq:Adiabatic_avg, eq:Adiabatic_cr, lines 208-219), and the
central values needed for Knudsen numbers (rest-mass density, energy density, pressure,
scale height H_c = (p_c/(4 pi rho_c^2))^(1/2)).

The same family written with the conserved energy E is f = A [exp(-E/T_inf) -
exp(-E_c/T_inf)] with b = T_inf/E_c; the King model (exp(1 - E/E_0) - 1)_+ of
arXiv:2009.08163 is b = 1, with y_0 = ln(E_0) - mu(0) = -ln(1 - b w0) (SCOPE.md 3.2).

Output (in $NRPIC_RUN_DIR): king_sequence.json, fig_king_sequence.{pdf,png},
fig_king_check.{pdf,png}.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp, simpson
from scipy.optimize import minimize_scalar, brentq

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic import figstyle as fs           # noqa: E402
import matplotlib.pyplot as plt            # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", ".")
SQ2PI4 = 4.0 * math.sqrt(2.0) * math.pi
GL_S, GL_W = np.polynomial.legendre.leggauss(64)
GL_S = 0.5 * (GL_S + 1.0)          # nodes on [0, 1]
GL_W = 0.5 * GL_W


def integrals(b, w):
    """I_n, I_rho, I_u, I_p of eq:integrals; x = w s^2 removes the x^(1/2) singularity."""
    w = max(float(w), 0.0)
    if w == 0.0:
        return 0.0, 0.0, 0.0, 0.0
    beta = b / (1.0 - b * w)
    s = GL_S
    x = w * s * s
    g = np.expm1(w - x)                     # e^(w - x) - 1
    a = np.sqrt(1.0 + 0.5 * beta * x)
    c = 1.0 + beta * x
    # x^(1/2) dx = 2 w^(3/2) s^2 ds ; x^(3/2) dx = 2 w^(5/2) s^4 ds
    k12 = 2.0 * w ** 1.5 * s * s
    k32 = 2.0 * w ** 2.5 * s ** 4
    In = beta ** 1.5 * np.dot(GL_W, g * a * c * k12)
    Ir = beta ** 1.5 * np.dot(GL_W, g * a * c * c * k12)
    Iu = beta ** 2.5 * np.dot(GL_W, g * a * c * k32)
    Ip = beta ** 2.5 * np.dot(GL_W, g * a ** 3 * k32)
    return In, Ir, Iu, Ip


def moments(b, w):
    In, Ir, Iu, Ip = integrals(b, w)
    return SQ2PI4 * In, SQ2PI4 * Ir, SQ2PI4 * Iu, (2.0 / 3.0) * SQ2PI4 * Ip


def rhs(r, y, b):
    M, w, Er = y
    n, rho, u, p = moments(b, w)
    dM = 4.0 * math.pi * r * r * rho
    dw = -((1.0 - b * w) / b) * (4.0 * math.pi * p * r ** 3 + M) / (r * (r - 2.0 * M))
    dE = 4.0 * math.pi * r * r * n / math.sqrt(1.0 - 2.0 * M / r)
    return [dM, dw, dE]


def model(b, w0, dense=False, rtol=1e-10):
    n0, rho0, u0, p0 = moments(b, w0)
    r0 = 1e-7
    M0 = 4.0 / 3.0 * math.pi * rho0 * r0 ** 3
    wst = w0 - ((1.0 - b * w0) / b) * 2.0 * math.pi * (p0 + rho0 / 3.0) * r0 ** 2
    E0 = 4.0 / 3.0 * math.pi * n0 * r0 ** 3

    def surf(r, y, b):
        return y[1]
    surf.terminal = True
    surf.direction = -1
    sol = solve_ivp(rhs, (r0, 1e4), [M0, wst, E0], args=(b,), method="DOP853",
                    rtol=rtol, atol=1e-14, events=surf, dense_output=dense)
    if sol.status != 1:
        raise RuntimeError(f"no surface for b={b}, w0={w0}: {sol.message}")
    R = float(sol.t_events[0][0])
    M, _, Er = sol.y_events[0][0]
    C = M / R
    Z0 = (1.0 - 2.0 * C) ** -0.5 / (1.0 - b * w0) - 1.0
    out = dict(b=b, w0=w0, y0=-math.log(1.0 - b * w0), M=M, E_rest=Er, B=Er - M,
               eps_b=(Er - M) / Er, R=R, C=C, Z0=Z0, eps_c0=b * w0 / (1.0 - b * w0),
               v0=math.sqrt(3.0 * p0 / rho0), n_c=n0, rho_c=rho0, p_c=p0, u_c=u0,
               H_c=math.sqrt(p0 / (4.0 * math.pi * rho0 ** 2)))
    if dense:
        out["sol"] = sol
    return out


def adiabatic(b, w0, nr=4001):
    """<gamma> and gamma_cr of eq:Adiabatic_avg and eq:Adiabatic_cr (main.tex 208-219)."""
    m = model(b, w0, dense=True)
    R, C = m["R"], m["C"]
    r = np.linspace(1e-7, R, nr)
    Y = m["sol"].sol(r)
    M, w = Y[0], np.clip(Y[1], 0.0, None)
    mom = np.array([moments(b, wi) for wi in w])
    rho, u, p = mom[:, 1], mom[:, 2], mom[:, 3]
    gam = np.where(u > 0, 1.0 + p / np.where(u > 0, u, 1.0), 5.0 / 3.0)
    ePhi = math.sqrt(1.0 - 2.0 * C) * (1.0 - b * w)
    e2L = 1.0 / (1.0 - 2.0 * M / r)
    eL = np.sqrt(e2L)
    wgt = ePhi ** 3 * eL
    D = simpson(wgt * p * r * r, x=r)
    gavg = simpson(gam * wgt * p * r * r, x=r) / D
    t1 = simpson(wgt * (16 * p + (e2L - 1) * (rho + p)) * (e2L - 1) * r * r, x=r) / D
    t2 = simpson(ePhi ** 3 * eL ** 3 * (8 * p + (e2L + 1) * (rho + p)) * p * r ** 4, x=r) / D
    t3 = simpson(ePhi ** 3 * eL ** 5 * (rho + p) * p * p * r ** 6, x=r) / D
    gcr = 4.0 / 3.0 + t1 / 36.0 + 4.0 * math.pi / 9.0 * t2 + 16.0 * math.pi ** 2 / 9.0 * t3
    return gavg, gcr


# 2108.11967 Table, b = 0.1 (main.tex lines 490-503): w0, M, E_rest, eps, R, C, Z0, v0, <g>, gcr
TAB = [(0.6, 3.47240e-2, 3.51790e-2, 1.29311e-2, 1.63800, 2.11990e-2, 8.71214e-2,
        2.25450e-1, 1.65936, 1.37799),
       (1.9, 2.72897e-2, 2.81385e-2, 3.01659e-2, 5.81001e-1, 4.69701e-2, 2.96903e-1,
        3.95398e-1, 1.64377, 1.47651),
       (3.2, 1.84498e-2, 1.91224e-2, 3.51754e-2, 3.78001e-1, 4.88088e-2, 5.47883e-1,
        5.06132e-1, 1.62919, 1.57054),
       (4.0515, 1.42556e-2, 1.47424e-2, 3.30243e-2, 3.68001e-1, 3.87378e-2, 7.50107e-1,
        5.66189e-1, 1.62117, 1.62117)]
KEYS = ["M", "E_rest", "eps_b", "R", "C", "Z0", "v0", "gavg", "gcr"]


def eps_max(b, lo, hi):
    r = minimize_scalar(lambda x: -model(b, x)["eps_b"], bounds=(lo, hi), method="bounded",
                        options=dict(xatol=1e-7))
    return model(b, r.x)


def main():
    res = dict(check_b0p1=[], maxima={}, zero_b1=None, adiabatic_crit={}, sequences={})
    # ---- P2: Table rows at b = 0.1
    for row in TAB:
        m = model(0.1, row[0])
        ga, gc = adiabatic(0.1, row[0])
        mine = [m["M"], m["E_rest"], m["eps_b"], m["R"], m["C"], m["Z0"], m["v0"], ga, gc]
        rel = {k: (a / t - 1.0) for k, a, t in zip(KEYS, mine, row[1:])}
        res["check_b0p1"].append(dict(w0=row[0], mine=dict(zip(KEYS, mine)),
                                      table=dict(zip(KEYS, row[1:])), rel_diff=rel))
    # ---- maxima of eps_b and adiabatic-index crossing for several b
    brk = {0.1: (2.0, 4.5), 0.2: (1.0, 2.2), 0.3: (0.6, 1.6), 0.5: (0.3, 1.0),
           1.0: (0.1, 0.6)}
    for b, (lo, hi) in brk.items():
        m = eps_max(b, lo, hi)
        res["maxima"][str(b)] = {k: v for k, v in m.items() if k != "sol"}
    for b, (lo, hi) in {0.1: (3.5, 4.5), 0.2: (1.5, 2.0)}.items():
        f = lambda x: (lambda g: g[0] - g[1])(adiabatic(b, x))
        wc = brentq(f, lo, hi, xtol=1e-5)
        m = model(b, wc)
        res["adiabatic_crit"][str(b)] = dict(w0=wc, Z0=m["Z0"], v0=m["v0"], C=m["C"],
                                             eps_b=m["eps_b"],
                                             gamma=adiabatic(b, wc)[0])
    # ---- P3: b = 1 (King model of 2009.08163): first zero of eps_b after the maximum
    wmax1 = res["maxima"]["1.0"]["w0"]
    grid = np.linspace(wmax1, 0.95, 60)
    vals = [model(1.0, x)["eps_b"] for x in grid]
    j = next(i for i, v in enumerate(vals) if v < 0)
    wz = brentq(lambda x: model(1.0, x)["eps_b"], grid[j - 1], grid[j], xtol=1e-10)
    res["zero_b1"] = dict(w0=wz, y0=-math.log(1.0 - wz))
    # ---- sequences for the figure
    for b, top in [(0.1, 6.0), (0.2, 3.2), (0.5, 1.4), (1.0, 0.85)]:
        ws = np.linspace(0.02 * top, top, 70)
        seq = [model(b, x) for x in ws]
        res["sequences"][str(b)] = [{k: s[k] for k in ("w0", "y0", "eps_b", "Z0", "C", "v0",
                                                        "M", "R")} for s in seq]
    with open(os.path.join(OUT, "king_sequence.json"), "w") as f:
        json.dump(res, f, indent=1)

    # ---- figures
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.1))
    a1 = fs.inch_axes(fig, 0.75, 0.55, 3.0, 2.4)
    a2 = fs.inch_axes(fig, 4.75, 0.55, 3.0, 2.4)
    cols = fs.series_colors(4)
    for c, (bs, seq) in zip(cols, res["sequences"].items()):
        Z = [s["Z0"] for s in seq]
        a1.plot(Z, [s["eps_b"] for s in seq], color=c, label=f"b = {bs}")
        a2.plot([s["y0"] for s in seq], [s["eps_b"] for s in seq], color=c)
        mx = res["maxima"][bs]
        a1.plot(mx["Z0"], mx["eps_b"], "o", color=c, ms=5)
    a1.plot([0.548], [0.0352], "x", color="k", ms=7, label="2108.11967, b = 0.1")
    a1.axhline(0.0, **fs.MASK_LINE)
    a1.set_xlim(0, 1.2)
    a1.set_xlabel(r"central redshift $Z(0)$ (to infinity)")
    a1.set_ylabel(r"fractional binding energy $\varepsilon$")
    a1.legend(loc="lower left", fontsize=8, ncol=1)
    a2.axvline(0.334, ls=":", **fs.THIN)
    a2.axvline(0.784, ls=":", **fs.THIN)
    a2.text(0.345, -0.012, "2009.08163:\n$y_{max}$, $y_{zero}$", fontsize=8)
    a2.axhline(0.0, **fs.MASK_LINE)
    a2.set_xlim(0, 1.2)
    a2.set_xlabel(r"$y_0=-\ln(1-b\,w_0)$")
    a2.set_ylabel(r"$\varepsilon$")
    fs.save(fig, os.path.join(OUT, "fig_king_sequence"))

    fig = plt.figure(figsize=(fs.COLUMN_WIDTH, 2.9))
    ax = fs.inch_axes(fig, 0.85, 0.4, 3.0, 2.4)
    for i, k in enumerate(KEYS):
        d = [abs(c["rel_diff"][k]) for c in res["check_b0p1"]]
        ax.semilogy([i] * len(d), np.maximum(d, 1e-9), "o", color=fs.PAL["red"], ms=4,
                    mfc="none")
    ax.axhline(5e-3, **fs.GUIDE)
    ax.text(5.2, 6e-3, "0.5 percent", fontsize=8)
    ax.set_ylim(5e-8, 2e-2)
    ax.set_xticks(range(len(KEYS)))
    ax.set_xticklabels([r"$M$", r"$E_{\rm r}$", r"$\varepsilon$", r"$R$", r"$C$",
                        r"$Z_0$", r"$v_0$", r"$\langle\gamma\rangle$",
                        r"$\gamma_{\rm cr}$"], fontsize=8)
    ax.minorticks_off()
    ax.set_ylabel("|this solver / Table - 1|")
    fs.save(fig, os.path.join(OUT, "fig_king_check"))
    for c in res["check_b0p1"]:
        print(c["w0"], {k: f"{v:+.2e}" for k, v in c["rel_diff"].items()})
    for b, m in res["maxima"].items():
        print("max", b, {k: round(m[k], 6) for k in ("w0", "y0", "eps_b", "Z0", "C", "v0")})
    print("adiabatic", res["adiabatic_crit"])
    print("zero b=1", res["zero_b1"])


if __name__ == "__main__":
    main()
