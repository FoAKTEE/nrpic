#!/usr/bin/env python3
"""Fresh verifier, part 1: the one-patch Langevin system of arXiv:2401.08530 (P0).

Own code throughout (no reader or integrator of the reproduction packages is imported).
Equations: P0:802-838 (lapse and e-fold equations, noise amplitude), P0:842-847 (model),
P0:1034-1076 (appendix D). Units M_Pl = 1. Conventions of P0: eps1 = pi^2/2 with
pi = dphi/dN, eps2 = -dln eps1/dN (so that USR has eps2 = 6, P0:842; checked below
against P0:914 in the misprint script).

V1  background: forward Euler at 0.01, 0.005, 0.001; Heun and RK4 at 0.01; DOP853 rtol 1e-12.
V2  50 000 paths, noise on N_b in [2, 6], step 0.01: Ito (Euler-Maruyama) and Stratonovich
    (stochastic Heun) readings of the printed SDE; also Ito with the alpha^5 term, the
    alpha^3 -> 1 variant, and the converged background (paths lost).
V3  Monte Carlo of Ito's lemma for alpha = c/Z, dZ = alpha s dW.
V4  appendix-D amplitude against my Mukhanov-Sasaki solutions (SR quadratic, exact USR).

Usage: python onepatch.py --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PHI0, PI0, PHIC, HSTAR = 10.0, -2.0001, 9.056, 1e-5          # P0:847
V0 = HSTAR**2*(3.0 - PI0**2/2.0)                              # Friedmann at N = 0


def V(phi):
    x = phi/PHIC
    return np.where(phi >= PHIC, V0, V0*(3*x**2 - 2*x**3))


def dV(phi):
    x = phi/PHIC
    return np.where(phi >= PHIC, 0.0, 6*V0*x*(1 - x)/PHIC)


def rhs_bg(phi, pi):
    h2 = V(phi)/(3.0 - pi**2/2.0)
    return pi, -(3.0 - pi**2/2.0)*pi - dV(phi)/h2


# ---------------------------------------------------------------- V1 background
def fixed_step(scheme, h, nend=12.0):
    n = int(round(nend/h))
    phi, pi = np.empty(n + 1), np.empty(n + 1)
    phi[0], pi[0] = PHI0, PI0
    for i in range(n):
        p, q = phi[i], pi[i]
        if scheme == "euler":
            a, b = rhs_bg(p, q)
            phi[i+1], pi[i+1] = p + h*a, q + h*b
        elif scheme == "heun":
            a1, b1 = rhs_bg(p, q)
            a2, b2 = rhs_bg(p + h*a1, q + h*b1)
            phi[i+1], pi[i+1] = p + 0.5*h*(a1 + a2), q + 0.5*h*(b1 + b2)
        elif scheme == "rk4":
            a1, b1 = rhs_bg(p, q)
            a2, b2 = rhs_bg(p + 0.5*h*a1, q + 0.5*h*b1)
            a3, b3 = rhs_bg(p + 0.5*h*a2, q + 0.5*h*b2)
            a4, b4 = rhs_bg(p + h*a3, q + h*b3)
            phi[i+1] = p + h*(a1 + 2*a2 + 2*a3 + a4)/6
            pi[i+1] = q + h*(b1 + 2*b2 + 2*b3 + b4)/6
    return np.arange(n + 1)*h, phi, pi


def crossing(N, phi):
    j = np.where(phi < PHIC)[0]
    if len(j) == 0:
        return None
    j = j[0]
    return float(N[j-1] + (PHIC - phi[j-1])/(phi[j] - phi[j-1])*(N[j] - N[j-1]))


def converged(nend=12.0):
    ev = lambda t, y: y[0] - PHIC  # noqa: E731
    sol = solve_ivp(lambda t, y: rhs_bg(y[0], y[1]), (0, nend), [PHI0, PI0], method="DOP853",
                    rtol=1e-12, atol=1e-14, dense_output=True, events=ev)
    return sol


def bg_quantities(N, phi, pi):
    """H, eps1, eps2 (P0 convention: -dln eps1/dN) on the grid of a fixed-step background."""
    eps1 = pi**2/2
    _, dpi = rhs_bg(phi, pi)
    eps2 = -2*dpi/pi
    H = np.sqrt(V(phi)/(3 - eps1))
    return H, eps1, eps2


# ---------------------------------------------------------------- V2 Langevin
def langevin(H, eps1, eps2, h, i0, i1, npath, seed, reading="ito", ito_pow=3, ito_coef=1.0,
             mult_pow=3, store_every=1):
    """Paths of (alpha, N - N_b) from index i0 (N_b = i0 h, alpha = 1, N = N_b) to i1.
    reading: 'ito' (Euler-Maruyama), 'strat' (stochastic Heun, converges to Stratonovich)."""
    rng = np.random.default_rng(seed)
    a = np.ones(npath)
    dn = np.zeros(npath)
    alive = np.ones(npath, bool)
    out_t, out_a, out_n, out_alive = [], [], [], []

    def drift(a, k):
        s2 = (3/(2*np.pi)*H[k]/np.sqrt(2*eps1[k]))**2
        root = np.sqrt(1 + (a**2 - 1)*(1 - eps1[k]/3))
        da = 3*a*(root - 1) + ito_coef*a**ito_pow*s2 + (-3 + eps1[k] + eps2[k]/2)*a*(a**2 - 1)
        return da, root - 1, np.sqrt(s2)

    for k in range(i0, i1):
        if (k - i0) % store_every == 0:
            out_t.append(k*h)
            out_a.append(a.copy())
            out_n.append(dn.copy())
            out_alive.append(alive.copy())
        dW = rng.standard_normal(npath)*np.sqrt(h)
        with np.errstate(all="ignore"):
            f1, g1n, s = drift(a, k)
            g1 = a**mult_pow*s
            if reading == "ito":
                a_new = a + h*f1 + g1*dW
                dn_new = dn + h*g1n
            else:
                ap = a + h*f1 + g1*dW
                f2, g2n, s2 = drift(ap, k + 1)
                g2 = ap**mult_pow*s2
                a_new = a + 0.5*h*(f1 + f2) + 0.5*(g1 + g2)*dW
                dn_new = dn + 0.5*h*(g1n + g2n)
        bad = ~np.isfinite(a_new) | (a_new <= 0) | (a_new > 1e3)
        alive &= ~bad
        a = np.where(alive, a_new, np.nan)
        dn = np.where(alive, dn_new, np.nan)
    out_t.append(i1*h)
    out_a.append(a.copy())
    out_n.append(dn.copy())
    out_alive.append(alive.copy())
    return np.array(out_t), np.array(out_a), np.array(out_n), np.array(out_alive)


def moments(x):
    x = x[np.isfinite(x)]
    m = x.mean()
    s = x.std()
    k3 = np.mean((x - m)**3)/s**3
    k4 = np.mean((x - m)**4)/s**4 - 3
    return m, s, k3, k4


# ---------------------------------------------------------------- V3 Ito MC
def ito_mc(alpha0, s_over_c, T, nsub, npath, seed, chunk=2_000_000):
    """Drift of alpha = c/Z with dZ = alpha s dW (c = 1). Control variate: subtract the
    martingale term -(alpha0^2) (Z_T - Z_0) whose mean is zero."""
    rng = np.random.default_rng(seed)
    c, s = 1.0, s_over_c
    dt = T/nsub
    acc, acc2, n = 0.0, 0.0, 0
    while n < npath:
        m = min(chunk, npath - n)
        z = np.full(m, c/alpha0)
        for _ in range(nsub):
            z = z + (c/z)*s*rng.standard_normal(m)*np.sqrt(dt)
        a = c/z
        est = (a - alpha0) + alpha0**2/c*(z - c/alpha0)
        acc += est.sum()
        acc2 += (est**2).sum()
        n += m
    mean = acc/n
    var = acc2/n - mean**2
    return mean/T, np.sqrt(var/n)/T


# ---------------------------------------------------------------- V4 Mukhanov-Sasaki
def ms_ratio(case, sigma, Nc, kpre=200.0):
    """Amplitude of P0 appendix D from a numerical mode function, over the printed one,
    for the mode with k = sigma a H at N = Nc. case: 'sr' (V = m^2 phi^2/2, phi(0) = 14.14),
    'usr' (V constant, pi tiny)."""
    if case == "sr":
        m2 = 1e-10

        def pot(phi):
            return 0.5*m2*phi**2, m2*phi
        y0 = [14.1421356, -2/14.1421356]      # slow-roll attractor pi ~ -2/phi
        N0 = 0.0
    else:
        def pot(phi):
            return 1e-10*np.ones_like(phi), 0.0*phi
        y0 = [1.0, -1e-3]
        N0 = 0.0

    def bg(N, y):
        phi, pi = y[0], y[1]
        v, dv = pot(phi)
        e1 = pi**2/2
        h2 = v/(3 - e1)
        dpi = -(3 - e1)*pi - dv/h2
        return pi, dpi, np.sqrt(h2), e1, 2*dpi/pi        # last: dln eps1/dN (standard)

    # first find aH(Nc) to fix k; integrate the background alone
    sol = solve_ivp(lambda N, y: bg(N, y)[:2], (N0, Nc + 1), y0, method="DOP853", rtol=1e-12,
                    atol=1e-20, dense_output=True)
    yc = sol.sol(Nc)
    Hc = bg(Nc, yc)[2]
    k = sigma*np.exp(Nc)*Hc
    # start of the mode: k/(aH) = kpre
    from scipy.optimize import brentq
    Ni = brentq(lambda N: k/(np.exp(N)*bg(N, sol.sol(N))[2]) - kpre, N0, Nc)
    yi = sol.sol(Ni)
    _, _, Hi, e1i, e2si = bg(Ni, yi)
    ai = np.exp(Ni)
    z = ai*np.sqrt(2*e1i)
    R0 = 1/(z*np.sqrt(2*k))
    dR0 = R0*(-1j*k/(ai*Hi) - (1 + e2si/2))

    def rhs(N, u):
        phi, pi = u[0], u[1]
        R = u[2] + 1j*u[3]
        dR = u[4] + 1j*u[5]
        dphi, dpi, H, e1, e2s = bg(N, [phi, pi])
        ddR = -(3 - e1 + e2s)*dR - (k/(np.exp(N)*H))**2*R
        return [dphi, dpi, dR.real, dR.imag, ddR.real, ddR.imag]
    s2 = solve_ivp(rhs, (Ni, Nc), [yi[0], yi[1], R0.real, R0.imag, dR0.real, dR0.imag],
                   method="DOP853", rtol=1e-11, atol=1e-30)
    u = s2.y[:, -1]
    R = u[2] + 1j*u[3]
    dR = u[4] + 1j*u[5]
    _, _, H, e1, e2s = bg(Nc, u[:2])
    eps2_p0 = -e2s
    B = dR + (3 - e1 - eps2_p0)*R
    amp = abs(B)*np.sqrt(k**3*(1 - e1)/(2*np.pi**2))
    printed = 3/(2*np.pi)*H/np.sqrt(2*e1)
    # also: the bracket the printed derivation keeps, (3 - eps1 - eps2) R with |R| exact
    return dict(case=case, sigma=sigma, Nc=Nc, ratio=float(amp/printed), eps1=float(e1),
                eps2_p0=float(eps2_p0), absR_over_A=float(abs(R)*np.sqrt(4*e1*k**3)/H))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--npath", type=int, default=50000)
    ap.add_argument("--nmc", type=int, default=4_000_000)
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    res = {}
    figstyle.use_style()

    # ---------------- V1
    bgs = {}
    for name, sch, h in [("euler_0.01", "euler", 0.01), ("euler_0.005", "euler", 0.005),
                         ("euler_0.001", "euler", 0.001), ("heun_0.01", "heun", 0.01),
                         ("rk4_0.01", "rk4", 0.01)]:
        N, phi, pi = fixed_step(sch, h)
        bgs[name] = (N, phi, pi)
        res[f"V1_{name}"] = dict(cross_N=crossing(N, phi), phi_at_12=float(phi[-1]),
                                 phi_min=float(phi.min()))
    sol = converged()
    res["V1_dop853"] = dict(cross_N=(float(sol.t_events[0][0]) if len(sol.t_events[0]) else None),
                            phi_at_12=float(sol.y[0, -1]))
    dphi_an = (1/np.sqrt(6))*np.log((np.sqrt(6) + abs(PI0))/(np.sqrt(6) - abs(PI0)))
    res["V1_analytic_plateau_stop"] = PHI0 - dphi_an
    # eps2 of the Euler 0.01 background at N = 2 and 3
    N, phi, pi = bgs["euler_0.01"]
    H, e1, e2 = bg_quantities(N, phi, pi)
    res["V1_euler001_eps1_eps2_at_2"] = [float(e1[200]), float(e2[200])]
    res["V1_euler001_eps1_eps2_at_3"] = [float(e1[300]), float(e2[300])]
    print(json.dumps(res, default=float), flush=True)

    fig, axs = plt.subplots(1, 2, figsize=(figstyle.FULL_WIDTH, 3.0))
    ax = axs[0]
    for (name, (N_, p_, _)), c in zip(bgs.items(), figstyle.SERIES):
        ax.plot(N_, p_, color=c, label=name.replace("_", " "))
    Nd = np.linspace(0, 12, 1201)
    ax.plot(Nd, sol.sol(Nd)[0], "k--", label="DOP853 (rtol 1e-12)")
    ax.axhline(PHIC, **figstyle.MASK_LINE)
    ax.set_xlim(0, 6)
    ax.set_ylim(8.9, 10.05)
    ax.set_xlabel(r"$\mathcal{N}_b$")
    ax.set_ylabel(r"$\phi_b$")
    ax.legend(fontsize=7)
    ax = axs[1]
    for (name, (N_, p_, _)), c in zip(bgs.items(), figstyle.SERIES):
        ax.plot(N_, p_ - PHIC, color=c)
    ax.plot(Nd, sol.sol(Nd)[0] - PHIC, "k--")
    ax.axhline(0, **figstyle.MASK_LINE)
    ax.set_xlim(2, 6)
    ax.set_ylim(-0.03, 0.03)
    ax.set_xlabel(r"$\mathcal{N}_b$")
    ax.set_ylabel(r"$\phi_b-\phi_c$")
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_p0_background.png"), dpi=150)
    plt.close(fig)

    # ---------------- V2
    h = 0.01
    N, phi, pi = bgs["euler_0.01"]
    H, e1, e2 = bg_quantities(N, phi, pi)
    runs = {}
    variants = [("ito_a3", dict(reading="ito")),
                ("strat_a3", dict(reading="strat")),
                ("ito_a5", dict(reading="ito", ito_pow=5)),
                ("ito_noitoterm", dict(reading="ito", ito_coef=0.0)),
                ("ito_a3_mult1", dict(reading="ito", mult_pow=0, ito_pow=0)),
                ("ito_a3_h0.001", None), ("ito_a3_bg_euler0.001", None)]
    Nfine = np.arange(0, 12001)*0.001
    for name, kw in variants:
        if name == "ito_a3_h0.001":
            # Langevin step 0.001 on the Euler-0.01 background (linear interpolation)
            Hf, e1f, e2f = (np.interp(Nfine, N, q) for q in (H, e1, e2))
            t, A, D, ok = langevin(Hf, e1f, e2f, 0.001, 2000, 6000, args.npath, 11, reading="ito",
                                   store_every=10)
        elif name == "ito_a3_bg_euler0.001":
            # background of forward Euler at 0.001 (stays on the plateau), Langevin step 0.001
            Nf, phf, pif = bgs["euler_0.001"]
            Hf, e1f, e2f = bg_quantities(Nf, phf, pif)
            t, A, D, ok = langevin(Hf, e1f, e2f, 0.001, 2000, 6000, args.npath, 11, reading="ito",
                                   store_every=10)
        else:
            t, A, D, ok = langevin(H, e1, e2, h, 200, 600, args.npath, 7, **kw)
        runs[name] = (t, A, D, ok)
        rows = {}
        for nb in (3.0, 4.0, 5.0, 6.0):
            j = int(np.argmin(abs(t - nb)))
            ma, sa, k3a, k4a = moments(A[j] - 1)
            mn, sn, k3n, k4n = moments(D[j])
            rows[str(nb)] = dict(mean_a=ma, std_a=sa, skew_a=k3a, kurt_a=k4a, mean_n=mn,
                                 std_n=sn, skew_n=k3n, kurt_n=k4n,
                                 alive=float(ok[j].mean()))
        sel = (t >= 4.5) & (t <= 6.0)
        k3series = np.array([moments(A[j] - 1)[2] for j in np.where(sel)[0]])
        rows["median_skew_a_4.5_6"] = float(np.median(k3series))
        runs_alive = ok[-1].mean()
        rows["alive_at_6"] = float(runs_alive)
        res[f"V2_{name}"] = rows
        print(name, json.dumps(rows, default=float), flush=True)
    # converged background: paths lost
    Ns = np.arange(0, 1201)*0.01
    yy = sol.sol(Ns)
    Hc, e1c, e2c = bg_quantities(Ns, yy[0], yy[1])
    t, A, D, ok = langevin(Hc, e1c, e2c, 0.01, 200, 600, args.npath, 7, reading="ito")
    frac = ok.mean(axis=1)
    half = t[np.argmax(frac < 0.5)] if (frac < 0.5).any() else None
    res["V2_converged_bg_ito"] = dict(alive_at_6=float(frac[-1]), N_half_lost=half,
                                      eps1_at_6=float(e1c[600]))

    # figure: widths and skewness against my read-off values of P0 Fig. 3
    ro_t = np.array([3, 4, 5, 6.0])
    ro_a = np.array([0.0068, 0.117, 0.133, 0.122])
    ro_n = np.array([0.0016, 0.042, 0.150, 0.188])
    fig, axs = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 2.8))
    for (name, lab), c in zip([("ito_a3", r"It\^o, $\alpha^3$ (printed)"),
                               ("strat_a3", r"Stratonovich, $\alpha^3$"),
                               ("ito_a5", r"It\^o, $\alpha^5$")], figstyle.SERIES):
        t, A, D, ok = runs[name]
        sa = np.array([moments(A[j] - 1)[1] for j in range(len(t))])
        sn = np.array([moments(D[j])[1] for j in range(len(t))])
        k3 = np.array([moments(A[j] - 1)[2] for j in range(len(t))])
        axs[0].plot(t, sa, color=c, label=lab)
        axs[1].plot(t, sn, color=c)
        axs[2].plot(t, k3, color=c)
    axs[0].plot(ro_t, ro_a, "ko", ms=4, label="P0 Fig. 3, read off")
    axs[1].plot(ro_t, ro_n, "ko", ms=4)
    axs[2].axhline(1.1, color="k", ls=":", lw=1, label=r"P0 Fig. 2 plateau, read off")
    axs[0].set_ylabel(r"std $(\alpha-\alpha_b)$")
    axs[1].set_ylabel(r"std $(\mathcal{N}-\mathcal{N}_b)$")
    axs[2].set_ylabel(r"$\kappa_3(\alpha)$")
    for ax in axs:
        ax.set_xlabel(r"$\mathcal{N}_b$")
        ax.set_xlim(2, 6)
    axs[0].legend(fontsize=6)
    axs[2].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_p0_moments.png"), dpi=150)
    plt.close(fig)

    # ---------------- V3
    mc = []
    for a0 in (2.0, 1.5):
        for T in (0.004, 0.002, 0.001):
            d, e = ito_mc(a0, 0.1, T, 40, args.nmc, 3 + int(1000*T) + int(10*a0))
            mc.append(dict(alpha0=a0, T=T, drift=d, se=e, pred_a5=a0**5*0.01, pred_a3=a0**3*0.01))
    res["V3_ito_mc"] = mc
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH, 2.8))
    for a0, c in zip((2.0, 1.5), figstyle.SERIES):
        rows = [r for r in mc if r["alpha0"] == a0]
        ax.errorbar([r["T"] for r in rows], [r["drift"] for r in rows],
                    yerr=[r["se"] for r in rows], fmt="o", color=c, label=rf"MC, $\alpha_0={a0}$")
        ax.axhline(a0**5*0.01, color=c, ls="-", lw=1)
        ax.axhline(a0**3*0.01, color=c, ls=":", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel(r"horizon $T$")
    ax.set_ylabel(r"drift of $\alpha$")
    ax.set_title(r"solid $\alpha^5 s^2/c^2$, dotted $\alpha^3 s^2/c^2$", fontsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_p0_ito_mc.png"), dpi=150)
    plt.close(fig)

    # ---------------- V4
    amp = []
    for case, Nc in (("sr", 10.0), ("sr", 30.0), ("usr", 12.0)):
        for sg in (0.05, 0.1, 0.2, 0.5):
            amp.append(ms_ratio(case, sg, Nc))
    res["V4_amplitude"] = amp
    fig, ax = plt.subplots(figsize=(figstyle.COLUMN_WIDTH, 2.8))
    sg = np.logspace(np.log10(0.04), np.log10(0.6), 50)
    ax.plot(sg, np.sqrt(1 + sg**2/3 + sg**4/9), "k--", lw=1, label="SR, analytic")
    ax.plot(sg, sg**2/3, "k:", lw=1, label=r"USR, $\sigma^2/3$")
    for case, c in (("sr", figstyle.SERIES[0]), ("usr", figstyle.SERIES[1])):
        rows = [r for r in amp if r["case"] == case and r["Nc"] != 30.0]
        ax.plot([r["sigma"] for r in rows], [r["ratio"] for r in rows], "o", color=c,
                label=f"{case.upper()}, my Mukhanov-Sasaki")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$\sigma$")
    ax.set_ylabel("amplitude / printed (P0:1072)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_p0_noise_amp.png"), dpi=150)
    plt.close(fig)

    with open(os.path.join(out, "onepatch.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
