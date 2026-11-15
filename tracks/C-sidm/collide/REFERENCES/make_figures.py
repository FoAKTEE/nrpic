"""Figures and key numbers of the reference solutions (run: python3 make_figures.py OUT).

Writes OUT/ref_*.png and OUT/ref_numbers.json. Figures go to ../figs when OUT is omitted.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from nrpic import figstyle as fs

import mj
import rate
import kinematics as kin
import relax
import conduction as cd
import entropy as en

fs.use_style()
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "figs")
os.makedirs(OUT, exist_ok=True)
NUM = {}


def gamma_m1_norm_form(ua, ub):
    """The first, rejected form (norm difference) for the comparison panel."""
    a, b = np.linalg.norm(ua, axis=-1), np.linalg.norm(ub, axis=-1)
    Wa, Wb = np.sqrt(1 + a * a), np.sqrt(1 + b * b)
    S = (a - b) * (a + b) / (a * Wb + b * Wa)
    t1 = S * S / (np.sqrt(1 + S * S) + 1)
    d = ua / a[:, None] - ub / b[:, None]
    return t1 + a * b * 0.5 * np.sum(d * d, -1)


# ------------------------------------------------------------------ rate
def fig_rate():
    th = np.logspace(-4, 3, 300)
    v = rate.vmol_mean(th)
    rng = np.random.default_rng(101)
    thm = np.logspace(-3, 2, 11)
    mc = np.array([rate.vmol_mean_mc(t, 1_000_000, rng) for t in thm])
    dev = (mc[:, 0] - rate.vmol_mean(thm)) / mc[:, 1]
    NUM["rate_mc_dev_sigma"] = dict(zip([f"{t:.3g}" for t in thm], dev.round(2).tolist()))
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 4.6))
    ax = fig.add_axes([0.17, 0.36, 0.78, 0.6])
    ax2 = fig.add_axes([0.17, 0.1, 0.78, 0.22], sharex=ax)
    ax.loglog(th, v, color=fs.PAL["blue"], label=r"$4K_3(2\zeta)/(\zeta K_2^2)$")
    ax.loglog(th, 4 / np.sqrt(np.pi) * np.sqrt(th), **fs.GUIDE, label=r"$\sqrt{16\theta/\pi}$")
    ax.axhline(1.0, color="k", lw=1.0, ls=":", label=r"$c$")
    ax.errorbar(thm, mc[:, 0], yerr=mc[:, 1], fmt="o", ms=3.5, color=fs.PAL["red"],
                label="Monte Carlo pairs")
    ax.set_ylabel(r"$\langle v_{\rm M\o l}\rangle$")
    ax.set_ylim(5e-3, 3)
    ax.legend(loc="lower right")
    plt.setp(ax.get_xticklabels(), visible=False)
    ax2.axhspan(-2, 2, color=fs.PAL["blue"], alpha=0.15, lw=0)
    ax2.semilogx(thm, dev, "o", ms=3.5, color=fs.PAL["red"])
    ax2.axhline(0, **fs.GUIDE)
    ax2.set_ylim(-4.5, 4.5)
    ax2.set_ylabel(r"$\Delta/\sigma_{\rm MC}$")
    ax2.set_xlabel(r"$\theta = T/m$")
    fs.save(fig, os.path.join(OUT, "ref_rate"))
    plt.close(fig)


# ------------------------------------------------------------------ kinematics
def fig_kinematics():
    import mpmath  # noqa: F401
    rng = np.random.default_rng(1)
    n = 6000
    th = 10.0 ** rng.uniform(-8, 6, n)
    gb = 10.0 ** rng.uniform(0, 4, n)
    d = rng.normal(size=(n, 3)); d /= np.linalg.norm(d, axis=1)[:, None]
    bulk = np.sqrt(gb * gb - 1)[:, None] * d
    sc = (np.sqrt(th) * (1 + np.sqrt(th)))[:, None]
    ua = bulk + sc * rng.normal(size=(n, 3))
    ub = bulk + sc * rng.normal(size=(n, 3))
    nh = rng.normal(size=(n, 3)); nh /= np.linalg.norm(nh, axis=1)[:, None]
    a2, b2 = kin.scatter(ua, ub, 1.0, 1.0, nh)
    scale = np.maximum(1.0, np.maximum(np.abs(ua).max(1), np.abs(ub).max(1)))
    err_new = np.empty(n)
    err_g_old = np.empty(n)
    err_g_new = np.empty(n)
    g_new = kin.gamma_rel_m1(ua, ub)
    g_old = gamma_m1_norm_form(ua, ub)
    import mpmath as mp
    mp.mp.dps = 60
    for i in range(n):
        ra, rb = kin.mp_scatter(ua[i], ub[i], 1.0, 1.0, nh[i])
        err_new[i] = max(max(abs(float(ra[k]) - a2[i, k]) for k in range(3)),
                         max(abs(float(rb[k]) - b2[i, k]) for k in range(3))) / scale[i]
        A = [mp.mpf(float(x)) for x in ua[i]]; B = [mp.mpf(float(x)) for x in ub[i]]
        g = mp.sqrt(1 + sum(x * x for x in A)) * mp.sqrt(1 + sum(x * x for x in B)) - \
            sum(x * y for x, y in zip(A, B)) - 1
        err_g_new[i] = abs(float((g_new[i] - g) / g))
        err_g_old[i] = abs(float((g_old[i] - g) / g))
    P0 = ua + ub; P1 = a2 + b2
    E0 = kin.W_of(ua) + kin.W_of(ub); E1 = kin.W_of(a2) + kin.W_of(b2)
    resP = np.abs(P1 - P0).max(1) / E0
    resE = np.abs(E1 - E0) / E0
    eps = np.finfo(float).eps
    NUM["kin_err_max"] = float(err_new.max())
    NUM["kin_gamma_m1_relerr_max_new"] = float(err_g_new.max())
    NUM["kin_gamma_m1_relerr_max_norm_form"] = float(err_g_old.max())
    NUM["kin_resP_max_over_eps"] = float(resP.max() / eps)
    NUM["kin_resE_max_over_eps"] = float(resE.max() / eps)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.4, 0.8])
    ax.loglog(scale, np.maximum(err_g_old, 1e-18), ".", ms=2, color=fs.PAL["red"],
              alpha=0.5, label=r"norm form of $\gamma_{\rm rel}-1$ (rejected)")
    ax.loglog(scale, np.maximum(err_g_new, 1e-18), ".", ms=2, color=fs.PAL["blue"],
              alpha=0.6, label="final form")
    ax.axhline(eps, **fs.GUIDE)
    ax.set_xlabel(r"$\max(1,|u|)$ of the pair")
    ax.set_ylabel(r"relative error of $\gamma_{\rm rel}-1$")
    ax.set_ylim(1e-18, 1e-6)
    ax.legend(loc="upper left", markerscale=4)
    ax = fig.add_axes([0.57, 0.15, 0.4, 0.8])
    bins = np.logspace(-19, -13, 61)
    ax.hist(np.maximum(err_new, 1e-19), bins=bins, histtype="step", color=fs.PAL["blue"],
            label=r"$|u'-u'_{\rm ref}|/\max(1,|u|)$")
    ax.hist(np.maximum(resP, 1e-19), bins=bins, histtype="step", color=fs.PAL["yellow"],
            label=r"$|\Delta P|/E$")
    ax.hist(np.maximum(resE, 1e-19), bins=bins, histtype="step", color=fs.PAL["red"],
            label=r"$|\Delta E|/E$")
    ax.axvline(eps, **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("error of one scattered pair")
    ax.set_ylabel("pairs")
    ax.legend(loc="upper left")
    fs.save(fig, os.path.join(OUT, "ref_kinematics"))
    plt.close(fig)


# ------------------------------------------------------------------ relaxation
def fig_relax():
    th = np.logspace(-3, 2, 30)
    ratio = []
    for t in th:
        d1, d2 = relax.dtheta_dt(0.5, 0.5, 1.0, 2 * t, t)
        ratio.append((d1 - d2) / relax.dT_rate_nr(0.5, 0.5, 1.0, 2 * t, t))
    ratio = np.array(ratio)
    NUM["relax_rate_ratio_rel_over_nr"] = dict(theta=th[[0, 10, 20, 29]].round(4).tolist(),
                                              ratio=ratio[[0, 10, 20, 29]].round(5).tolist())
    rng = np.random.default_rng(55)
    mc_pts = []
    for t in (1e-3, 0.1, 1.0, 10.0):
        q = relax.de1_dt(0.5, 0.5, 1.0, 2 * t, t)
        m, se = relax.de1_dt_mc(0.5, 0.5, 1.0, 2 * t, t, 1_000_000, rng, scatter=True)
        mc_pts.append((t, m / q, se / abs(q)))
    mc_pts = np.array(mc_pts)
    NUM["relax_mc_over_quad"] = mc_pts.round(5).tolist()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.4, 0.8])
    ax.semilogx(th, ratio, color=fs.PAL["blue"], label="exact initial rate / NR closed form")
    ax.errorbar(mc_pts[:, 0], mc_pts[:, 1] * np.interp(np.log(mc_pts[:, 0]), np.log(th),
                ratio), yerr=mc_pts[:, 2] * np.interp(np.log(mc_pts[:, 0]), np.log(th),
                ratio), fmt="o", ms=3.5, color=fs.PAL["red"], label="Monte Carlo integral")
    ax.axhline(1, **fs.GUIDE)
    ax.set_xlabel(r"$\theta_2$ ($\theta_1 = 2\theta_2$)")
    ax.set_ylabel(r"$\dot{(\theta_1-\theta_2)}\,/\,{\rm NR}$")
    ax.legend(loc="lower left")
    ax = fig.add_axes([0.57, 0.15, 0.4, 0.8])
    for t2, col in ((1e-3, fs.PAL["blue"]), (1.0, fs.PAL["red"])):
        t1 = 3 * t2
        tau = relax.relaxation_time(0.5, 0.5, 1.0, t1, t2)
        tt, y = relax.two_mj_model(0.5, 0.5, 1.0, t1, t2, 4 * tau, 120)
        teq = relax.theta_eq(0.5, 0.5, t1, t2)
        ax.plot(tt / tau, y[0] / teq, color=col, label=rf"$\theta_2={t2:g}$")
        ax.plot(tt / tau, y[1] / teq, color=col, ls="--")
        x = np.linspace(0, 1, 10)
        ax.plot(x, (t1 + (relax.dtheta_dt(0.5, 0.5, 1.0, t1, t2)[0]) * x * tau) / teq,
                color="k", lw=1.0, ls=":")
    ax.axhline(1, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/\tau_{\rm rel}$")
    ax.set_ylabel(r"$\theta_i/\theta_{\rm eq}$ (two-MJ model, guide)")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(OUT, "ref_relax"))
    plt.close(fig)


# ------------------------------------------------------------------ conduction
def fig_conduction():
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.25, 0.8])
    th = np.logspace(-4, 3, 200)
    ax.loglog(th, cd.phi_N(1.0, th), color=fs.PAL["blue"], label=r"$\Phi_N/n$")
    ax.loglog(th, cd.phi_E(1.0, th) - cd.phi_N(1.0, th), color=fs.PAL["red"],
              label=r"$(\Phi_E-m\Phi_N)/n$")
    ax.loglog(th, np.sqrt(th / (2 * np.pi)), **fs.GUIDE)
    ax.loglog(th, 0.25 + 0 * th, color="k", lw=1, ls=":")
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("one-sided flux")
    ax.legend(loc="upper left")
    ax = fig.add_axes([0.41, 0.15, 0.25, 0.8])
    L = 1.0
    for t2, col in ((0.01, fs.PAL["blue"]), (1.0, fs.PAL["red"])):
        t1 = 1.2 * t2
        n1, n2 = 1 / t1, 1 / t2
        tc = L / rate.vmol_mean(t2)
        t = np.linspace(0, 6 * tc, 400)
        NL, EL, KL = cd.step_collisionless(t, L, n1, t1, n2, t2)
        Ninf = 0.25 * L * (n1 + n2)
        ax.plot(t / tc, (NL - Ninf) / (NL[0] - Ninf), color=col, label=rf"$\theta_2={t2:g}$")
        Einf = 0.25 * L * (n1 * mj.mean_W(t1) + n2 * mj.mean_W(t2))
        ax.plot(t / tc, (EL - Einf) / (EL[0] - Einf), color=col, ls="--")
    ax.axhline(0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t\,\langle v_{\rm M\o l}\rangle/L$")
    ax.set_ylabel(r"$(X_L - X_\infty)/(X_L(0)-X_\infty)$")
    ax.legend(loc="upper right", title="collisionless")
    ax = fig.add_axes([0.73, 0.15, 0.25, 0.8])
    # short mean free path: diffusive step, chi from kappa_1, three Knudsen numbers
    th0 = 0.01
    for lam, col in ((1 / 50, fs.PAL["blue"]), (1 / 100, fs.PAL["red"]),
                     (1 / 200, fs.PAL["yellow"])):
        sig = 1.0                    # sigma_tot; n = 1/(lam sigma)
        n = 1 / (lam * sig)
        kap = cd.kappa_ce_nr(th0, sig)
        ch = cd.chi(kap, n, th0)
        tdiff = L * L / (4 * np.pi ** 2 * ch)
        t = np.linspace(0, 3 * tdiff, 300)
        X = cd.step_diffusive(t, L, 1.0, 0.0, ch)
        ax.plot(t / tdiff, X, color=col, label=rf"$\lambda/L={lam:g}$")
    ax.set_xlabel(r"$t\,\chi k_1^2$")
    ax.set_ylabel("slab excess (diffusive)")
    ax.legend(loc="upper right")
    fs.save(fig, os.path.join(OUT, "ref_conduction"))
    plt.close(fig)
    NUM["kappa1_coefficient"] = 75 * np.sqrt(np.pi) / 64
    NUM["kappa_ratio_KS_over_BSI"] = float(cd.B_KS / cd.B_BSI)


# ------------------------------------------------------------------ entropy
def fig_entropy():
    rng = np.random.default_rng(77)
    th = np.array([1e-3, 1e-2, 0.1, 1.0, 10.0])
    dev = []
    for t in th:
        u = mj.sample_u(1_000_000, t, rng)
        r = en.s_estimate(u, 1.0, t)
        dev.append((r["s_mm"] - en.s_mj(1.0, t)) / r["stderr"])
    NUM["entropy_estimator_dev_sigma"] = dict(zip([f"{t:g}" for t in th],
                                                  np.round(dev, 2).tolist()))
    t2 = np.logspace(-3, 1, 30)
    gap = []
    for t in t2:
        t1 = 3 * t
        teq = relax.theta_eq(0.5, 0.5, t1, t)
        gap.append(en.s_mj(1.0, teq) - en.s_mixture(0.5, t1, 0.5, t))
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.4, 0.8])
    ax.semilogx(t2, gap, color=fs.PAL["blue"])
    ax.set_xlabel(r"$\theta_2$ ($\theta_1 = 3\theta_2$, $n_1=n_2$)")
    ax.set_ylabel(r"$s_{\rm MJ}(\theta_{\rm eq}) - s(0)$ per particle")
    ax = fig.add_axes([0.57, 0.15, 0.4, 0.8])
    ax.semilogx(th, dev, "o", ms=4, color=fs.PAL["red"])
    ax.axhspan(-2, 2, color=fs.PAL["blue"], alpha=0.15, lw=0)
    ax.axhline(0, **fs.GUIDE)
    ax.set_ylim(-5, 5)
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel(r"estimator $-\,s_{\rm MJ}$ [standard errors]")
    fs.save(fig, os.path.join(OUT, "ref_entropy"))
    plt.close(fig)
    NUM["entropy_gap_theta2_1e-3"] = float(gap[0])
    NUM["entropy_gap_theta2_1"] = float(gap[np.argmin(abs(t2 - 1))])


if __name__ == "__main__":
    fig_rate()
    fig_kinematics()
    fig_relax()
    fig_conduction()
    fig_entropy()
    with open(os.path.join(OUT, "ref_numbers.json"), "w") as fh:
        json.dump(NUM, fh, indent=1)
    print(json.dumps(NUM, indent=1))
