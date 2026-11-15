#!/usr/bin/env python3
"""Test 2 of secondary_infall: the collisionless self-similar secondary infall onto a
point-mass (delta-function) seed in an Einstein-de Sitter background, radial orbits
through the centre (the matter-era solution cited by 1901.08528 :235 and 2106.07480
sections/numerical_results.tex:71 as Bertschinger 1985 / Fillmore-Goldreich 1984).

Self-similar variables (derived here, not copied): the turnaround radius r_ta(t) ~ t^(8/9)
and the mass inside it M_ta(t) ~ t^(2/3) obey G M_ta t^2 / r_ta^3 = kappa = pi^2/8 (a
cycloid that turns around at t). Every shell follows the same orbit
    r(t) = r_ta(t*) Lambda(tau),   tau = t/t*,   t* = its turnaround time,
    Lambda'' = -kappa tau^(2/3) m(|Lambda| tau^(-8/9)) Lambda/|Lambda|^3,
    Lambda(1) = 1, Lambda'(1) = 0,
with m(lambda) = M(<lambda r_ta(t), t)/M_ta(t) built from the same orbit:
    m(lambda) = int_0^1 du  H(lambda - |Lambda(u^(-3/2))| u^(4/3)),   u = tau^(-2/3)
(u is the mass fraction of M_ta(t) that turned around before t* = t u^(3/2)). Fixed-point
iteration on m; the orbit is integrated to tau_max and continued beyond as stationary in
Lambda (the inner mass profile is static in physical units when m ~ lambda^(3/4)).
Density: rho/rho_b(t) = (9 pi^2/16) dm/d(lambda^3); the frozen-in estimate (background
density at the turnaround time of the shell now at r) is rho_fr/rho_b(t) = lambda^(-9/4).

Usage: python3 selfsimilar.py --out <dir> [--taumax 300] [--soft 1e-5]
"""
import argparse
import json
import math
import os
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.ndimage import gaussian_filter1d

from common import load_figstyle, KAPPA, PI

L0 = math.log(1e-9)
NL = 1801
DL = -L0 / (NL - 1)
LGRID = L0 + DL * np.arange(NL)              # ln lambda on [1e-9, 1]


class MassProfile:
    """ln m on the ln lambda grid, cubic Hermite interpolation (continuous force
    derivative: piecewise-linear interpolation made the adaptive integrator take ~40
    times more steps, run D-bh-dress-20261115-122303-4e8e8af)."""

    def __init__(self, lnm):
        self.lnm = np.asarray(lnm, float).copy()
        self.lst = self.lnm.tolist()
        self.dl = (np.gradient(self.lnm, DL) * DL).tolist()   # slope per grid step

    def __call__(self, lam):
        if lam <= 0.0:
            return 0.0
        if lam >= 1.0:
            return 1.0
        ll = math.log(lam)
        x = (ll - L0) / DL
        if x < 0.0:
            return math.exp(self.lst[0] + 0.75 * (ll - L0))
        i = int(x)
        if i >= NL - 1:
            return math.exp(self.lst[-1])
        f = x - i
        f2 = f * f
        f3 = f2 * f
        y = ((2 * f3 - 3 * f2 + 1) * self.lst[i] + (f3 - 2 * f2 + f) * self.dl[i]
             + (-2 * f3 + 3 * f2) * self.lst[i + 1] + (f3 - f2) * self.dl[i + 1])
        return math.exp(y)


def orbit(mp, taumax, soft, rtol=1e-8):
    s2 = soft * soft
    p89 = -8.0 / 9.0

    def rhs(tau, y):
        L, V = y
        lam = abs(L) * tau ** p89
        m = mp(lam)
        r2 = L * L + s2
        return [V, -KAPPA * tau ** (2.0 / 3.0) * m * L / (r2 * math.sqrt(r2))]

    sol = solve_ivp(rhs, (1.0, taumax), [1.0, 0.0], method="DOP853", rtol=rtol,
                    atol=1e-12, dense_output=True)
    return sol


def mass_from_orbit(sol, taumax, nu=1_500_000):
    ut = taumax ** (-2.0 / 3.0)
    u = np.linspace(1.0, ut, nu)                 # tau increasing
    tau = u ** -1.5
    Y = sol.sol(tau)
    x = np.abs(Y[0]) * tau ** (-8.0 / 9.0)
    du = (1.0 - ut) / nu
    lam = np.exp(LGRID)
    xs = np.sort(x)
    m_main = np.searchsorted(xs, lam) * du
    # stationary continuation: distribution of |Lambda| over the last half of the orbit
    tt = np.linspace(0.5 * taumax, taumax, 200_001)
    absL = np.sort(np.abs(sol.sol(tt)[0]))
    ug = np.geomspace(1e-16, ut, 3000)
    F = lambda yv: np.searchsorted(absL, yv) / absL.size
    yv = lam[:, None] * ug[None, :] ** (-4.0 / 3.0)
    integrand = F(yv)                                           # (NL, nug)
    m_tail = np.trapezoid(integrand, ug, axis=1) + 1e-16 * integrand[:, 0]
    return m_main + m_tail, dict(u=u, tau=tau, L=Y[0], V=Y[1], x=x, ut=ut,
                                 lamap_tail=absL[-1] * taumax ** (-8.0 / 9.0))


def apocentres(sol, taumax, n=40000):
    tt = np.geomspace(1.0, min(taumax, 40.0), n)
    L, V = sol.sol(tt)
    vr = np.sign(L) * V                 # radial velocity d|Lambda|/dtau
    k = np.where((vr[:-1] > 0) & (vr[1:] <= 0))[0]
    out = []
    for i in k:
        # refine with a quadratic through three samples of |Lambda|
        j = min(max(i, 1), tt.size - 2)
        a = np.abs(L[j - 1:j + 2])
        t3 = tt[j - 1:j + 2]
        c = np.polyfit(t3, a, 2)
        tm = -c[1] / (2 * c[0])
        am = np.polyval(c, tm)
        out.append((float(tm), float(am), float(am * tm ** (-8.0 / 9.0))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--taumax", type=float, default=300.0)
    ap.add_argument("--soft", type=float, default=1e-5)
    ap.add_argument("--maxit", type=int, default=30)
    ap.add_argument("--tol", type=float, default=2e-3)
    ap.add_argument("--mix", type=float, default=0.5)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lam = np.exp(LGRID)
    lnm = 0.75 * LGRID                           # start: m = lambda^(3/4)
    hist = []
    for it in range(a.maxit):
        t0 = time.time()
        mp = MassProfile(lnm)
        sol = orbit(mp, a.taumax, a.soft)
        m_new, aux = mass_from_orbit(sol, a.taumax)
        # light smoothing (3 grid cells, 3.5 % in lambda) of the sampled profile before it
        # drives the next orbit: blurs the caustic kinks slightly, cuts the steps 7-fold
        lnm_new = gaussian_filter1d(np.log(np.maximum(m_new, 1e-300)), 3.0, mode="nearest")
        # convergence measured where m > ~0.01 (below lambda ~ 1e-3 the sampled m is
        # noise-limited at a few per cent; run D-bh-dress-20261115-122303-4e8e8af)
        sel = (lam > 1e-3) & (lam < 0.98)
        dmax = float(np.max(np.abs(lnm_new[sel] - lnm[sel])))
        sel6 = (lam > 1e-6) & (lam < 0.98)
        dmax6 = float(np.max(np.abs(lnm_new[sel6] - lnm[sel6])))
        hist.append(dict(it=it, dmax=dmax, dmax_1e6=dmax6, nfev=int(sol.nfev),
                         wall=time.time() - t0))
        print(f"iteration {it}: max |d ln m| = {dmax:.3e}  nfev = {sol.nfev}  "
              f"{time.time() - t0:.1f} s", flush=True)
        lnm = (1.0 - a.mix) * lnm + a.mix * lnm_new
        if dmax < a.tol:
            break
    # final orbit with the converged profile
    mp = MassProfile(lnm)
    sol = orbit(mp, a.taumax, a.soft)
    m_fin, aux = mass_from_orbit(sol, a.taumax)
    apo = apocentres(sol, a.taumax)
    lam1 = max(p[2] for p in apo)
    m = np.exp(lnm)
    # density in log bins
    edges = np.geomspace(1e-5, 1.0, 101)
    me = np.interp(np.log(edges), LGRID, m)
    rho = (9.0 * PI**2 / 16.0) * np.diff(me) / np.diff(edges**3)
    rc = np.sqrt(edges[1:] * edges[:-1])
    ratio_fr = rho / rc ** (-2.25)
    # slope of m on [3e-3, 3e-2] by least squares
    s = (lam > 3e-3) & (lam < 3e-2)
    slope_m, lnA = np.polyfit(LGRID[s], lnm[s], 1)
    s2 = (lam > 1e-4) & (lam < 1e-3)
    slope_m2, lnA2 = np.polyfit(LGRID[s2], lnm[s2], 1)
    A = math.exp(lnA)
    inner = (rc > 1e-4) & (rc < 1e-2)
    res = dict(taumax=a.taumax, soft=a.soft, iterations=hist,
               slope_m_3em3_3em2=float(slope_m), slope_m_1em4_1em3=float(slope_m2),
               A=A, rho_over_frozen_inner_mean=float(np.mean(ratio_fr[inner])),
               rho_over_frozen_closed=9.0 * PI**2 / 64.0 * A,
               apocentres=apo, lambda1=lam1, m_at_lambda1=float(np.interp(math.log(lam1), LGRID, lnm)),
               lamap_tail=aux["lamap_tail"],
               m_at=dict((f"{x:g}", float(np.exp(np.interp(math.log(x), LGRID, lnm))))
                         for x in (1e-4, 1e-3, 1e-2, 0.03, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9)),
               final_vs_last_iterate_max_dlnm=float(np.max(np.abs(
                   np.log(np.maximum(m_fin, 1e-300))[sel] - lnm[sel]))))
    res["m_at_lambda1"] = float(np.exp(res["m_at_lambda1"]))
    with open(os.path.join(a.out, "selfsimilar.json"), "w") as f:
        json.dump(res, f, indent=1)
    np.savez(os.path.join(a.out, "selfsimilar_profile.npz"), lngrid=LGRID, lnm=lnm,
             rc=rc, rho=rho, edges=edges)

    # ------------------------------------------------------------------ figures
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28, hspace=0.30)
    ax = axs[0, 0]
    tt = np.linspace(1.0, 6.0, 4000)
    L = sol.sol(tt)[0]
    ax.plot(tt, np.abs(L), color=fs.PAL["red"], label=r"$|\Lambda(\tau)|$ (shell)")
    ax.plot(tt, tt ** (8.0 / 9.0), **fs.GUIDE, label=r"$r_{\rm ta}(t)/r_{\rm ta}(t_*)$")
    ax.plot(tt, lam1 * tt ** (8.0 / 9.0), color="grey", ls=":", lw=1.0,
            label=r"outermost caustic $\lambda_1 r_{\rm ta}$")
    ax.set_xlim(1, 6)
    ax.set_ylim(0, 2.0)
    ax.set_xlabel(r"$\tau = t/t_*$")
    ax.set_ylabel(r"$r / r_{\rm ta}(t_*)$")
    ax.legend(loc="upper left", fontsize=7)
    ax = axs[0, 1]
    k = slice(None, None, 7)
    vr = np.sign(aux["L"]) * aux["V"] * aux["tau"] ** (1.0 / 9.0)
    ax.plot(aux["x"][k], vr[k], ",", color=fs.PAL["red"], alpha=0.5, rasterized=True)
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 1.2)
    ax.set_ylim(-6, 6)
    ax.axvline(lam1, **fs.MASK_LINE)
    ax.set_xlabel(r"$\lambda = r/r_{\rm ta}(t)$")
    ax.set_ylabel(r"$v_r \,/\, [r_{\rm ta}(t)/t]$")
    ax.text(0.04, 0.92, "phase space, all shells at one time", transform=ax.transAxes, fontsize=8)
    ax = axs[1, 0]
    ax.plot(rc, rho, color=fs.PAL["red"], label="self-similar solution (this work)")
    ax.plot(rc, rc ** (-2.25), **fs.GUIDE, label=r"frozen-in, $\lambda^{-9/4}$")
    ax.plot(rc, res["rho_over_frozen_closed"] * rc ** (-2.25), color="k", lw=1.0, ls=":",
            label=rf"$(9\pi^2/64)A\,\lambda^{{-9/4}}$, $A={A:.3f}$")
    ax.axvline(lam1, **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-5, 1.0)
    ax.set_xlabel(r"$\lambda = r/r_{\rm ta}(t)$")
    ax.set_ylabel(r"$\rho/\rho_b(t)$")
    ax.legend(loc="lower left", fontsize=7)
    ax = axs[1, 1]
    dl = np.gradient(lnm, LGRID)
    ax.plot(lam, dl, color=fs.PAL["red"], label=r"$d\ln m/d\ln\lambda$")
    ax.axhline(0.75, **fs.GUIDE)
    ax.plot(rc, ratio_fr / res["rho_over_frozen_closed"] * 0.75, color=fs.PAL["blue"], lw=1.0,
            label=r"$\rho/\rho_{\rm fr}$ (scaled to 3/4 at the plateau)")
    ax.axvline(lam1, **fs.MASK_LINE)
    ax.set_xscale("log")
    ax.set_xlim(1e-6, 1.0)
    ax.set_ylim(0.0, 1.5)
    ax.set_xlabel(r"$\lambda$")
    ax.set_ylabel("local slope")
    ax.legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "selfsimilar"))
    with open(os.path.join(a.out, "selfsimilar.txt"), "w") as f:
        for k_, v in res.items():
            f.write(f"{k_} = {v}\n")
    print(open(os.path.join(a.out, "selfsimilar.txt")).read())


if __name__ == "__main__":
    main()
