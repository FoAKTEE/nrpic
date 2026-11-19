#!/usr/bin/env python3
"""Design numbers and reference predictions of T6-T8 (written before any collisional run
of this package). Writes design.json and design_references.png into the run directory.

Contents:
  T6  step, theta_1 = 0.02 | theta_2 = 0.01, equal pressure, mean rest-mass density 1, L = 1:
      (a) collisionless exact curves and initial slopes -2 (Phi(1) - Phi(2)) of the slab
          rest mass, energy and kinetic energy;
      (b) lambda/L = 0.01: the nonlinear isobaric reference (isobaric.py) with kappa_1, the
          fit window [20 t_coll, 2/(chi k_1^2)], and the literal statistic of TESTS.md
          (step_diffusive with chi free, divided by chi(kappa_1) at the mean temperature)
          evaluated on the reference itself, i.e. what a code with kappa = kappa_1 exactly
          would score; the same for kappa = 1.025 kappa_1;
  T7  isobaric mode, theta in {0.003, 0.1, 1}, k lambda in {0.4, 0.2, 0.1}: t_coll, the
      kappa_1 rate Gamma_1, the fit window [10 t_coll, 2/Gamma_1], the bias of the
      exponential fit from the finite amplitude (nonlinear reference at eps = 0.05 and 0.2),
      and the statistical error of the fitted rate for N particles, from a Monte Carlo of
      the fit with Ornstein-Uhlenbeck noise of the entropy mode (variance 2 c_p/N... see
      `noise_var`, rate Gamma: Onsager regression) sampled at the snapshot times;
  T8  the same at k lambda = 0.2 for the parameter variants;
  cost per run from the smoke test S0 (run C-20261119-143228-31ba665).
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heatlib as hl          # noqa: E402
import isobaric as iso        # noqa: E402
import conduction as cd       # noqa: E402
import mj                     # noqa: E402
import rate                   # noqa: E402

import matplotlib             # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

# measured in S0 (C-20261119-143228-31ba665): processor, one core, coll_energy = particle
C_PAIR_CPU = 1.19e-6        # s per tested pair, push included (60 steps, 2e5 particles)
PAIRS_PER_PARTICLE_TCOLL = 17.3   # tested pairs per particle per t_coll at dt = 0.1 t_coll
CARD_SPEEDUP = 100.0        # wave 2: 96-173 (box_tests README, cost per pair)


def noise_var(theta, N):
    """Variance of the entropy-mode estimator A_S = (2/N) sum cos(k x_i) g_i with
    g_i = (K_i/<K> - 1) G - 1, G = (<W> - 1)/theta, in an equilibrium gas of N particles
    at Poisson positions: (2/N) (G^2 Var(K)/<K>^2 + 1); non-relativistically 5/N."""
    rng = np.random.default_rng(5)
    u = mj.sample_u(400000, theta, rng)
    K = hl.kin_flat(u)
    G = (float(mj.mean_W(theta)) - 1.0) / theta
    return 2.0 / N * (G * G * np.var(K) / np.mean(K) ** 2 + 1.0)


def fit_error_mc(G, t_snap, t0, t1, A0, var, nrep=400, seed=3):
    """Relative standard deviation of the least-squares rate of A0 exp(-G t) + n(t) over
    [t0, t1], n an Ornstein-Uhlenbeck process of variance var and rate G (stationary at
    t = 0), sampled at t_snap."""
    rng = np.random.default_rng(seed)
    out = []
    dt = np.diff(t_snap, prepend=0.0)
    for _ in range(nrep):
        n = np.empty(len(t_snap))
        x = rng.normal(0, np.sqrt(var))
        for i, d in enumerate(dt):
            a = np.exp(-G * d)
            x = a * x + rng.normal(0, np.sqrt(var * (1 - a * a)))
            n[i] = x
        A = A0 * np.exp(-G * t_snap) + n
        try:
            g, _, _ = iso.fit_exp(t_snap, A, t0, t1)
            out.append(g / G)
        except Exception:
            out.append(np.nan)
    out = np.array(out)
    return float(np.nanstd(out)), float(np.nanmean(out) - 1.0)


def main():
    out = hl.outdir("design")
    D = dict(note="design of T6-T8, heat package; numbers from the references")
    # ------------------------------------------------------------------ T6
    L, th1, th2, nbar = 1.0, 0.02, 0.01, 1.0
    p0 = 2 * nbar / (1 / th1 + 1 / th2)
    n1, n2 = p0 / th1, p0 / th2
    vbar2 = float(np.sqrt(8 * th2 / np.pi))          # <|v|> of the cold slab (~NR)
    tcross = L / vbar2
    T6 = dict(L=L, theta1=th1, theta2=th2, n1=n1, n2=n2, p0=p0, tcross=tcross,
              snap_dt=0.1 * tcross, t_end_a=5 * tcross)
    slopes = []
    for which in ("N", "E"):
        f = cd.phi_N if which == "N" else cd.phi_E
        slopes.append(float(-2 * (f(n1, th1) - f(n2, th2))))
    # kinetic: energy minus rest mass
    slopes.append(slopes[1] - slopes[0])
    T6["initial_slopes_M_E_K_per_area"] = slopes
    tt = np.linspace(0, 5 * tcross, 51)
    NL, EL, KL = cd.step_collisionless(tt, L, n1, th1, n2, th2)
    T6["collisionless_curve"] = dict(t=tt.tolist(), M=NL.tolist(), E=EL.tolist(),
                                     K=KL.tolist())
    # (b) lambda/L = 0.01
    lam = 0.01 * L
    sig = 1.0 / (nbar * lam)
    thm = 0.5 * (th1 + th2)
    tcoll_m = 1.0 / (nbar * sig * float(rate.vmol_mean(thm)))
    tcoll_cold = 1.0 / (n2 * sig * float(rate.vmol_mean(th2)))
    tcoll_hot = 1.0 / (n1 * sig * float(rate.vmol_mean(th1)))
    k1 = 2 * np.pi / L
    chi1 = iso.chi_kappa1(thm, nbar, sig)
    t_lo, t_hi = 20 * tcoll_m, 2.0 / (chi1 * k1 * k1)
    tb = np.linspace(0, 1.1 * t_hi, 441)
    refb = {}
    for f in (1.0, 1.025):
        X, s = iso.step_reference(L, nbar, th1, th2, sig, tb, f=f, nm=1200)
        Xinf = X[-1] * 0 + np.array([nbar * L / 2, 0, 0])
        chi_fit, chi_se, nfit = iso.fit_step_linear(tb, X[:, 0], L, X[0, 0], nbar * L / 2,
                                                    t_lo, t_hi, chi1)
        refb[f"f={f}"] = dict(chi_fit=chi_fit, literal_ratio=chi_fit / chi1, n_fit=nfit,
                              M=X[:, 0].tolist(), E=X[:, 1].tolist(), K=X[:, 2].tolist(),
                              p_end_over_p0=float(s.p[-1] / s.p[0]),
                              energy_drift=float(np.ptp(s.energy()) / s.energy()[0]))
    T_f = p0 / nbar
    T6["b"] = dict(lambda_mfp=lam, sigma=sig, theta_mean=thm, t_coll_mean=tcoll_m,
                   t_coll_cold=tcoll_cold, t_coll_hot=tcoll_hot, chi_kappa1_mean=chi1,
                   chi_kappa1_final=iso.chi_kappa1(T_f, nbar, sig), theta_final=T_f,
                   window=[t_lo, t_hi], t=tb.tolist(), ref=refb,
                   dt=0.1 * tcoll_cold, nx=int(np.ceil(4 * L / lam)),
                   window_in_tcoll=[20.0, t_hi / tcoll_m])
    D["T6"] = T6
    # ------------------------------------------------------------------ T7 / T8
    T7 = {}
    eps_list = (0.05, 0.2)
    bias = {}
    for th in (0.003, 0.1, 1.0):
        G1u = cd.mode_rate(cd.kappa_ce_nr(th, 1.0), 1.0, th, 1.0)   # rate at k = 1
        tc = 1.0 / float(rate.vmol_mean(th))                         # lambda = 1
        for e in eps_list:
            # the amplitude bias depends on eps and on theta only (pure diffusion scales
            # as Gamma_1 t); evaluate at k = 0.1 over the k lambda = 0.1 window
            k = 0.1
            G1 = G1u * k * k
            t = np.linspace(0, 2.2 / G1, 221)
            r = iso.mode_reference(k, 1.0, th, e, 1.0, t, nm=512)
            gS = iso.fit_exp(r["t"], r["AS"], 10 * tc, 2.0 / G1)[0] / G1
            gN = iso.fit_exp(r["t"], r["AN"], 10 * tc, 2.0 / G1)[0] / G1
            bias[f"theta={th},eps={e}"] = dict(G_fit_over_G1_entropy=gS,
                                                G_fit_over_G1_number=gN)
        for kl in (0.4, 0.2, 0.1):
            k = kl
            G1 = G1u * k * k
            Lx = 2 * np.pi / k
            nx = int(2 ** np.ceil(np.log2(4 * Lx)))
            cp = float(mj.c_p(th))
            win = [10 * tc, 2.0 / G1]
            t_end = 2.0 / G1
            nsnap = 24
            t_snap = np.linspace(0, t_end, nsnap + 1)
            var1 = noise_var(th, 1)          # times 1/N
            errs = {}
            for N in (2e5, 1e6, 4e6, 1.6e7):
                sd, b = fit_error_mc(G1, t_snap, win[0], win[1], 0.05 * cp, var1 / N)
                errs[f"{N:.0e}"] = dict(rel_sd=sd, mean_bias=b)
            sd2, _ = fit_error_mc(G1, t_snap, win[0], win[1], 0.2 * cp, var1 / 4e6)
            pairs = PAIRS_PER_PARTICLE_TCOLL * t_end / tc
            T7[f"theta={th},kl={kl}"] = dict(
                theta=th, k_lambda=kl, k=k, Lx=Lx, nx=nx, dx_over_lambda=Lx / nx,
                t_coll=tc, Gamma1=G1, Gamma1_tcoll=G1 * tc, window=win,
                window_in_tcoll=[10.0, win[1] / tc], t_end=t_end, nsnap=nsnap,
                dt=0.1 * tc, nsteps=int(np.ceil(t_end / (0.1 * tc))), c_p=cp,
                kappa1=float(cd.kappa_ce_nr(th, 1.0)), A_S0=0.05 * cp,
                noise_var_times_N=var1, fit_rel_sd=errs,
                fit_rel_sd_eps0p2_N4e6=sd2,
                cpu_s_per_particle=pairs * C_PAIR_CPU,
                card_s_per_particle=pairs * C_PAIR_CPU / CARD_SPEEDUP)
    D["T7"] = T7
    D["amplitude_bias"] = bias
    D["cost_basis"] = dict(C_PAIR_CPU=C_PAIR_CPU, PAIRS_PER_PARTICLE_TCOLL=
                           PAIRS_PER_PARTICLE_TCOLL, CARD_SPEEDUP=CARD_SPEEDUP,
                           source="S0 run C-20261119-143228-31ba665; card ratio wave 2")
    with open(os.path.join(out, "design.json"), "w") as fh:
        json.dump(D, fh, indent=1)
    # ------------------------------------------------------------------ figure
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.3))
    ax = fig.add_axes([0.085, 0.15, 0.245, 0.78])
    ax.plot(np.array(tt) / tcross, NL, color=fs.PAL["blue"], label="collisionless, exact")
    ax.plot(tt / tcross, NL[0] + slopes[0] * tt, **fs.GUIDE, label="initial slope")
    ax.set_xlabel(r"$t\,\langle|v|\rangle_2/L$")
    ax.set_ylabel("left-slab rest mass per area")
    ax.set_title(r"T6(a): $\lambda/L\to\infty$", fontsize=10)
    ax.set_ylim(NL[0] * 0.95, nbar * L / 2 * 1.08)
    ax.legend(loc="lower right", fontsize=8)
    ax = fig.add_axes([0.40, 0.15, 0.26, 0.78])
    ax.plot(tb / tcoll_m, refb["f=1.0"]["M"], color=fs.PAL["blue"],
            label=r"isobaric, $\kappa_1(T)$")
    ax.plot(tb / tcoll_m, cd.step_diffusive(tb, L, refb["f=1.0"]["M"][0], nbar * L / 2, chi1),
            **fs.GUIDE, label=r"linear, $\chi(\kappa_1,\bar\theta)$")
    fit = refb["f=1.0"]["chi_fit"]
    ax.plot(tb / tcoll_m, cd.step_diffusive(tb, L, refb["f=1.0"]["M"][0], nbar * L / 2, fit),
            color=fs.PAL["yellow"], lw=1.0, label=r"linear fit to isobaric")
    fs.average_window(ax, t_lo / tcoll_m, t_hi / tcoll_m)
    ax.set_xscale("log")
    ax.set_xlabel(r"$t/t_{\rm coll}$")
    ax.set_title(r"T6(b): $\lambda/L=0.01$", fontsize=10)
    ax.legend(loc="lower right", fontsize=8)
    ax = fig.add_axes([0.73, 0.15, 0.25, 0.78])
    for e, c in zip(eps_list, (fs.PAL["red"], fs.PAL["yellow"])):
        th = 0.003
        G1 = cd.mode_rate(cd.kappa_ce_nr(th, 1.0), 1.0, th, 0.1)
        t = np.linspace(0, 2.2 / G1, 221)
        r = iso.mode_reference(0.1, 1.0, th, e, 1.0, t)
        ax.semilogy(G1 * t, np.abs(r["AS"]) / abs(r["AS"][0]), color=c,
                    label=rf"$\epsilon={e}$")
    ax.semilogy(G1 * t, np.exp(-G1 * t), **fs.GUIDE, label="linear")
    ax.set_xlabel(r"$\Gamma_1 t$")
    ax.set_ylabel(r"$|A_S(t)/A_S(0)|$")
    ax.set_title(r"T7: isobaric mode, $\theta=0.003$", fontsize=10)
    ax.legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, "design_references"))
    short = dict(T6_slopes=slopes, T6b={k: (v["literal_ratio"], v["chi_fit"])
                                        for k, v in refb.items()},
                 T6b_window=[t_lo, t_hi], T6b_tcoll=tcoll_m, bias=bias,
                 T7={k: dict(G1tc=v["Gamma1_tcoll"], win_tc=v["window_in_tcoll"],
                             nx=v["nx"],
                             sd={n: e["rel_sd"] for n, e in v["fit_rel_sd"].items()},
                             sd_eps02_4e6=v["fit_rel_sd_eps0p2_N4e6"],
                             cpu=v["cpu_s_per_particle"])
                     for k, v in T7.items()})
    print(json.dumps(short, indent=1, default=str))


if __name__ == "__main__":
    main()
