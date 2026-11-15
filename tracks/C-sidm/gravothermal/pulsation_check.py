"""Independent check of the radial-pulsation FEM (prediction P6 of JOURNAL.md).

    python3 -E pulsation_check.py <outdir>

Relativistic polytropes p = K rho_0^Gamma, rho = rho_0 + p/(Gamma - 1), Gamma = 2, K = 100
(G = c = Msun = 1). TOV in the variable q = rho_0^{Gamma - 1} (linear zero at the surface):
    dm/dr = 4 pi r^2 rho,  dPhi/dr = (m + 4 pi r^3 p)/(r (r - 2m)),
    dp/dr = -(rho + p) dPhi/dr,  dq/dr = -((Gamma - 1)/(K Gamma) + q) dPhi/dr.
With Gamma_1 = Gamma the fundamental radial mode of the same equation that tmb.fem_lowest
solves must vanish at the maximum of M(rho_c) (turning-point theorem). Writes
polytrope_check.json and figure data.
"""
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar

import tmb

K, GAM = 100.0, 2.0


def tov(rhoc, dense=False):
    qc = rhoc ** (GAM - 1)
    pc = K * rhoc ** GAM

    def eos(q):
        q = max(q, 0.0)
        r0 = q ** (1.0 / (GAM - 1))
        p = K * r0 ** GAM
        return r0, p, r0 + p / (GAM - 1)

    def rhs(r, y):
        m, Phi, q = y
        r0, p, rho = eos(q)
        dPhi = (m + 4 * math.pi * r ** 3 * p) / (r * (r - 2 * m))
        # dq/dr = -((Gamma - 1)/(K Gamma) + q) dPhi/dr, from dp = -(rho + p) dPhi and
        # p = K q^{Gamma/(Gamma-1)}: regular at the surface q = 0
        dq = -((GAM - 1) / (K * GAM) + max(q, 0.0)) * dPhi
        return [4 * math.pi * r * r * rho, dPhi, dq]

    rhoc_e = rhoc + pc / (GAM - 1)
    r0 = 1e-6
    y0 = [4 * math.pi / 3 * rhoc_e * r0 ** 3, 0.0, qc]

    def surf(r, y):
        return y[2]
    surf.terminal = True
    surf.direction = -1
    s = solve_ivp(rhs, (r0, 100.0), y0, method="DOP853", rtol=1e-12, atol=1e-30, events=surf,
                  dense_output=dense)
    R = s.t_events[0][0]
    M = s.y_events[0][0][0]
    return dict(rhoc=rhoc, R=R, M=M, sol=s)


def omega2(rhoc, N=600):
    t = tov(rhoc, dense=True)
    s, R = t["sol"], t["R"]
    rr = np.linspace(s.t[0], R, 6000)
    yy = s.sol(rr)
    Msp, Psp, Qsp = CubicSpline(rr, yy[0]), CubicSpline(rr, yy[1]), CubicSpline(rr, yy[2])
    # uniform nodes from r = 0; an extra node at the start radius r0 = 1e-6 of the TOV
    # solve made a tiny first element whose quadrature points fell below r0, where the
    # splines extrapolate, and shifted omega^2 by ~5e-4 (probe of 2026-11-15, JOURNAL)
    nodes = np.linspace(0.0, R, N)

    def coeff(rq):
        q = np.clip(Qsp(rq), 0.0, None)
        r0 = q ** (1.0 / (GAM - 1))
        p = K * r0 ** GAM
        rho = r0 + p / (GAM - 1)
        return Msp(rq), rho, p, np.full_like(rq, GAM), np.exp(Psp(rq))

    ev, _, trial, _ = tmb.fem_lowest(nodes, coeff)
    return float(ev[0]), float(trial)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    grid = np.geomspace(5e-4, 2e-2, 40)
    Ms = [tov(x)["M"] for x in grid]
    i = int(np.argmax(Ms))
    res = minimize_scalar(lambda x: -tov(x)["M"], bounds=(grid[i - 1], grid[i + 1]),
                          method="bounded", options=dict(xatol=1e-12))
    rho_max, M_max = res.x, tov(res.x)["M"]
    om = {N: [omega2(x, N)[0] for x in grid] for N in (300, 600)}
    j = [k for k in range(len(grid) - 1) if om[600][k] > 0 >= om[600][k + 1]][0]
    roots = {}
    for N in (300, 600, 1200):
        roots[N] = brentq(lambda x: omega2(x, N)[0], grid[j], grid[j + 1], xtol=1e-12)
    out = dict(K=K, Gamma=GAM, rhoc_Mmax=rho_max, M_max=M_max,
               R_at_Mmax=tov(rho_max)["R"],
               rhoc_omega0={str(k): v for k, v in roots.items()},
               rel_diff={str(k): v / rho_max - 1 for k, v in roots.items()},
               grid=grid.tolist(), M=Ms, omega2_N300=om[300], omega2_N600=om[600],
               trial=[omega2(x, 300)[1] for x in grid])
    json.dump(out, open(os.path.join(outdir, "polytrope_check.json"), "w"), indent=1)
    print(f"M_max = {M_max:.6f} at rho_c = {rho_max:.6e}; FEM zero at rho_c = "
          + ", ".join(f"{v:.6e} (N={k}, rel {v / rho_max - 1:+.2e})" for k, v in roots.items()))


if __name__ == "__main__":
    main(sys.argv[1])
