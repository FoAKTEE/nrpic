"""Figures and numbers of repro/langevin from the output of simulate.py.

usage: python3 analyse.py SIMDIR OUTDIR [--install PKGDIR]
Writes OUTDIR/fig/*.png and OUTDIR/langevin.json; with --install also copies them into
PKGDIR/fig and PKGDIR/results.
"""
import json
import os
import shutil
import sys

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import lsde  # noqa: E402

fs.use_style()
TIMES = (3.0, 4.0, 5.0, 6.0)
ALLT = (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0)
RNG = np.random.Generator(np.random.PCG64(12345))
NBOOT = 200


def load(simdir, name):
    return dict(np.load(os.path.join(simdir, f"var_{name}.npz")))


def silverman(x):
    sd = x.std()
    iqr = np.subtract(*np.percentile(x, [75, 25]))
    return 0.9 * min(sd, iqr / 1.34) * len(x) ** -0.2


def kde_binned(x, lo, hi, bw, nb=2048):
    """Gaussian KDE on a fine histogram (linear binning error << bw)."""
    dx = (hi - lo) / nb
    centers = lo + (np.arange(nb) + 0.5) * dx
    m = int(np.ceil(5 * bw / dx))
    kx = np.arange(-m, m + 1) * dx
    ker = np.exp(-0.5 * (kx / bw) ** 2)
    ker /= ker.sum()

    def dens(xs):
        idx = np.floor((xs - lo) / dx).astype(int)
        idx = idx[(idx >= 0) & (idx < nb)]
        h = np.bincount(idx, minlength=nb).astype(float)
        return np.convolve(h, ker, mode="same") / (len(xs) * dx)
    return centers, dens


def kde_with_band(x, lo, hi):
    bw = silverman(x)
    c, dens = kde_binned(x, lo, hi, bw)
    p = dens(x)
    boots = np.empty((NBOOT, len(c)))
    n = len(x)
    for b in range(NBOOT):
        boots[b] = dens(x[RNG.integers(0, n, n)])
    lo95, hi95 = np.percentile(boots, [2.5, 97.5], axis=0)
    return c, p, lo95, hi95, bw


def tail_stats(x, q=0.90):
    """Right-tail diagnostics: exceedances above the q-quantile against an exponential
    (MLE rate) and against the Gaussian tail with the sample mean and variance."""
    mu, sd = x.mean(), x.std()
    x0 = np.quantile(x, q)
    y = x[x > x0] - x0
    lam = 1.0 / y.mean()
    cv = y.std() / y.mean()
    cvb = []
    for _ in range(NBOOT):
        yb = y[RNG.integers(0, len(y), len(y))]
        cvb.append(yb.std() / yb.mean())
    z0 = (x0 - mu) / sd
    tn = stats.truncnorm(z0, np.inf, loc=mu, scale=sd)
    gm, gv = tn.mean() - x0, tn.var()
    ks_exp = stats.kstest(y, "expon", args=(0, y.mean())).pvalue
    ks_gau = stats.kstest(y + x0, tn.cdf).pvalue
    ll_exp = np.mean(np.log(lam) - lam * y)
    ll_gau = np.mean(tn.logpdf(y + x0))
    return dict(q=q, x0=float(x0), n_exc=int(len(y)), rate=float(lam), cv=float(cv),
                cv_se=float(np.std(cvb)), cv_gauss_tail=float(np.sqrt(gv) / gm),
                ks_p_exp=float(ks_exp), ks_p_gauss_tail=float(ks_gau),
                dloglik_exp_minus_gauss=float(ll_exp - ll_gau))


def boot_moments(x):
    def mom(v):
        c = v - v.mean()
        s = c.std()
        return np.array([v.mean(), s, (c ** 3).mean() / s ** 3, (c ** 4).mean() / s ** 4 - 3])
    base = mom(x)
    bs = np.array([mom(x[RNG.integers(0, len(x), len(x))]) for _ in range(NBOOT)])
    se = bs.std(axis=0)
    keys = ("mean", "std", "skew", "exkurt")
    return {k: float(base[i]) for i, k in enumerate(keys)} | \
        {k + "_se": float(se[i]) for i, k in enumerate(keys)}


def finite(x):
    return x[np.isfinite(x)]


def fig_background(simdir, out):
    names = [("euler01", "Euler, step 0.01 (paper's tuning)", fs.PAL["red"], "-"),
             ("exact", "converged (RK4)", fs.PAL["blue"], "-"),
             ("euler005", "Euler, step 0.005", fs.PAL["yellow"], "--"),
             ("tuned", r"converged, $\pi_b^*$ tuned to cross at 3.045", fs.PAL["green"], ":")]
    fig, ax = plt.subplots(2, 2, figsize=(8, 5.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.97, hspace=0.28, wspace=0.28)
    for k, lab, col, ls in names:
        b = np.load(os.path.join(simdir, f"bg_{k}.npz"))
        N = b["N"]
        sig = lsde.sigma_of(b["eps1"], b["H"])
        m = N >= 1.5
        ax[0, 0].plot(N[m], 1e3 * (b["phi"][m] - lsde.PHI_C), color=col, ls=ls, label=lab)
        ax[0, 1].semilogy(N, b["eps1"], color=col, ls=ls)
        ax[1, 0].plot(N, b["eps2"], color=col, ls=ls)
        ax[1, 1].semilogy(N[N >= 1.0], sig[N >= 1.0], color=col, ls=ls)
    ax[0, 0].axhline(0, **fs.THIN)
    ax[0, 0].set_ylabel(r"$10^3(\phi_b-\phi_c)$")
    ax[0, 0].set_ylim(-1, 10)
    ax[0, 0].legend(fontsize=7, loc="upper right")
    ax[0, 1].set_ylabel(r"$\varepsilon_1$")
    ax[1, 0].set_ylabel(r"$\varepsilon_2=-d\ln\varepsilon_1/d\mathcal{N}_b$")
    ax[1, 1].set_ylabel(r"$\sqrt{\langle S^2\rangle}$")
    for a in ax.flat:
        a.set_xlabel(r"$\mathcal{N}_b$")
        a.axvspan(2, 6, color="grey", alpha=0.1)
    ax[1, 1].set_ylim(1e-5, 10)
    fs.save(fig, os.path.join(out, "fig_background"))
    plt.close(fig)


def fig_paths(v, out):
    N = v["N"]
    fig, ax = plt.subplots(2, 1, figsize=(8, 5.2), sharex=True)
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.98, hspace=0.06)
    cols = fs.series_colors(100, "viridis")
    for i in range(100):
        ax[0].plot(N, v["keep_a"][:, i], lw=0.5, alpha=0.35, color=cols[i])
        ax[1].plot(N, v["keep_D"][:, i], lw=0.5, alpha=0.35, color=cols[i])
    ax[0].plot(N, np.nanmean(v["keep_a"], axis=1), color=fs.PAL["red"], lw=1.8,
               label="mean of the 100 paths shown")
    ax[0].plot(N, v["m_mean_a"], color="k", lw=1.2, ls="--", label="mean of all 50 000")
    ax[1].plot(N, np.nanmean(v["keep_D"], axis=1), color=fs.PAL["red"], lw=1.8)
    ax[1].plot(N, v["m_mean_D"], color="k", lw=1.2, ls="--")
    ax[0].set_ylabel(r"$\alpha-\alpha_b$")
    ax[1].set_ylabel(r"$\mathcal{N}-\mathcal{N}_b$")
    ax[1].set_xlabel(r"$\mathcal{N}_b$")
    ax[0].set_ylim(-0.45, 1.0)
    ax[1].set_ylim(-0.4, 0.6)
    ax[0].set_xlim(2, 6)
    ax[0].legend(loc="upper left", ncol=2)
    fs.save(fig, os.path.join(out, "fig1_paths"))
    plt.close(fig)


def fig_moments(v, out, name="fig2_moments", title=None):
    N = v["N"]
    fig, ax = plt.subplots(figsize=(8, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.95)
    ax.plot(N, v["m_skew_a"], color=fs.PAL["red"], lw=1.0, label=r"$\kappa_3(\alpha)$")
    ax.plot(N, v["m_skew_D"], color=fs.PAL["red"], ls="--", label=r"$\kappa_3(\mathcal{N})$")
    ax.plot(N, v["m_kurt_a"], color=fs.PAL["blue"], lw=1.0, label=r"$\kappa_4(\alpha)$")
    ax.plot(N, v["m_kurt_D"], color=fs.PAL["blue"], ls="--", label=r"$\kappa_4(\mathcal{N})$")
    ax.axhline(0, **fs.THIN)
    ax.set_ylim(-1, 8)
    ax.set_xlim(2, N[-1])
    ax.set_xlabel(r"$\mathcal{N}_b$")
    ax.set_ylabel("skewness, excess kurtosis")
    ax.legend(loc="upper left", ncol=2)
    if title:
        ax.set_title(title, fontsize=10)
    fs.save(fig, os.path.join(out, name))
    plt.close(fig)


def fig_pdfs(v, out, tails, log=False):
    fig, ax = plt.subplots(4, 2, figsize=(8, 9.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.06, top=0.98, hspace=0.38, wspace=0.22)
    for r, t in enumerate(TIMES):
        for c, (key, lab) in enumerate((("a", r"$\alpha-\alpha_b$"),
                                        ("D", r"$\mathcal{N}-\mathcal{N}_b$"))):
            x = finite(v[f"{key}_{t:g}"])
            q0, q1 = np.quantile(x, [1e-4, 1 - 1e-4])
            pad = 0.15 * (q1 - q0)
            lo, hi = q0 - pad, q1 + pad
            cc, p, l95, h95, bw = kde_with_band(x, lo, hi)
            g = stats.norm.pdf(cc, x.mean(), x.std())
            a = ax[r, c]
            if log:
                ok = p > 0
                a.fill_between(cc[ok], np.log(np.maximum(l95[ok], 1e-300)),
                               np.log(np.maximum(h95[ok], 1e-300)),
                               color=fs.PAL["red"], alpha=0.25, lw=0)
                a.plot(cc[ok], np.log(p[ok]), color=fs.PAL["blue"])
                a.plot(cc, np.log(g), color="k", ls="--", lw=1.0)
                ts = tails[f"{t:g}"][key]
                xx = np.linspace(ts["x0"], hi, 50)
                a.plot(xx, np.log(0.1 * ts["rate"]) - ts["rate"] * (xx - ts["x0"]),
                       color="k", lw=1.0, label="exponential fit (top 10%)")
                pk = np.log(p.max())
                a.set_ylim(pk - 8.5, pk + 0.6)
                a.set_ylabel("ln PDF")
                if r == 0 and c == 0:
                    a.legend(loc="lower center", fontsize=7)
            else:
                a.fill_between(cc, l95, h95, color=fs.PAL["red"], alpha=0.25, lw=0)
                a.plot(cc, p, color=fs.PAL["blue"])
                a.plot(cc, g, color="k", ls="--", lw=1.0)
                a.set_ylabel("PDF")
                a.set_ylim(0, None)
            a.set_xlim(lo, hi)
            a.set_xlabel(lab, labelpad=-1)
            a.text(0.98, 0.88, rf"$\mathcal{{N}}_b={t:g}$", transform=a.transAxes,
                   ha="right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig4_logpdfs" if log else "fig3_pdfs"))
    plt.close(fig)


def fig_variants(simdir, out, groups, name):
    fig, ax = plt.subplots(2, 2, figsize=(8, 5.6), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, hspace=0.08, wspace=0.25)
    for vn, lab, col, ls in groups:
        try:
            v = load(simdir, vn)
        except FileNotFoundError:
            continue
        N = v["N"]
        m = N <= 6.0 + 1e-9
        for a, k in zip(ax.flat, ("std_a", "std_D", "skew_a", "skew_D")):
            a.plot(N[m], v["m_" + k][m], color=col, ls=ls, lw=1.0, label=lab)
    for a, lab in zip(ax.flat, (r"std$(\alpha)$", r"std$(\mathcal{N}-\mathcal{N}_b)$",
                                r"skewness $\alpha$", r"skewness $\mathcal{N}$")):
        a.set_ylabel(lab)
        a.set_xlim(2, 6)
    ax[1, 0].set_ylim(-1, 4)
    ax[1, 1].set_ylim(-1, 2)
    ax[0, 0].set_yscale("log")
    ax[0, 1].set_yscale("log")
    ax[0, 0].set_ylim(1e-4, 1)
    ax[0, 1].set_ylim(1e-5, 1)
    for a in ax[1]:
        a.set_xlabel(r"$\mathcal{N}_b$")
    ax[0, 0].legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(out, name))
    plt.close(fig)


def fig_off6(v, out):
    N = v["N"]
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.96, wspace=0.28)
    ax[0].semilogy(N, v["m_med_absa"], color=fs.PAL["red"], label=r"median $|\alpha-1|$")
    ax[0].semilogy(N, v["m_max_absa"], color=fs.PAL["red"], ls="--", label=r"max $|\alpha-1|$")
    ax[0].semilogy(N, v["m_std_D"], color=fs.PAL["blue"], label=r"std$(\mathcal{N}-\mathcal{N}_b)$")
    ax[0].axvline(6, **fs.MASK_LINE)
    ax[0].set_xlabel(r"$\mathcal{N}_b$")
    ax[0].legend(fontsize=8, loc="lower left")
    ax[0].set_ylim(1e-14, 10)
    for i in range(30):
        ax[1].plot(N, v["keep_D"][:, i], lw=0.5, color="grey", alpha=0.6)
    ax[1].plot(N, v["m_mean_D"], color=fs.PAL["red"], label="mean of all")
    ax[1].axvline(6, **fs.MASK_LINE)
    ax[1].set_xlabel(r"$\mathcal{N}_b$")
    ax[1].set_ylabel(r"$\mathcal{N}-\mathcal{N}_b$ (30 paths)")
    ax[1].legend(fontsize=8)
    for a in ax:
        a.set_xlim(2, N[-1])
    fs.save(fig, os.path.join(out, "fig_off6"))
    plt.close(fig)


def fig_a3one(base, a3, out):
    fig, ax = plt.subplots(2, 3, figsize=(8, 4.6))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.10, top=0.95, hspace=0.38, wspace=0.28)
    for c, t in enumerate((4.0, 5.0, 6.0)):
        for r, (key, lab) in enumerate((("a", r"$\alpha-\alpha_b$"),
                                        ("D", r"$\mathcal{N}-\mathcal{N}_b$"))):
            a = ax[r, c]
            for v, col, lb in ((base, fs.PAL["blue"], r"$\alpha^3 S$ (printed)"),
                               (a3, fs.PAL["red"], r"$\alpha^3\to1$")):
                x = finite(v[f"{key}_{t:g}"])
                q0, q1 = np.quantile(x, [1e-4, 1 - 1e-4])
                cc, dens = kde_binned(x, q0, q1, silverman(x))
                a.plot(cc, dens(x), color=col, label=lb)
            a.set_xlabel(lab, labelpad=-1)
            a.text(0.97, 0.88, rf"$\mathcal{{N}}_b={t:g}$", transform=a.transAxes,
                   ha="right", fontsize=8)
            a.set_ylim(0, None)
    ax[0, 0].legend(fontsize=7, loc="upper left")
    ax[0, 0].set_ylabel("PDF")
    ax[1, 0].set_ylabel("PDF")
    fs.save(fig, os.path.join(out, "fig_a3one"))
    plt.close(fig)


def fig_linear(simdir, v, out):
    L = np.load(os.path.join(simdir, "linear_euler01.npz"))
    fig, ax = plt.subplots(figsize=(4, 3.0))
    fig.subplots_adjust(left=0.18, right=0.97, bottom=0.16, top=0.96)
    ax.semilogy(v["N"], v["m_std_a"], color=fs.PAL["red"], label=r"std $\alpha$, run")
    ax.semilogy(L["N"], L["std_a"], color="k", ls="--", lw=1.0, label="linear theory")
    ax.semilogy(v["N"], v["m_std_D"], color=fs.PAL["red"], ls=":", label=r"std $\mathcal{N}$, run")
    ax.semilogy(L["N"], L["std_D"], color="k", ls=":", lw=1.0)
    ax.set_xlim(2, 6)
    ax.set_ylim(1e-6, 3)
    ax.set_xlabel(r"$\mathcal{N}_b$")
    ax.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(out, "fig_linear"))
    plt.close(fig)


def main():
    simdir, out = sys.argv[1], sys.argv[2]
    install = sys.argv[sys.argv.index("--install") + 1] if "--install" in sys.argv else None
    figdir = os.path.join(out, "fig")
    os.makedirs(figdir, exist_ok=True)
    summ = json.load(open(os.path.join(simdir, "summary.json")))
    base = load(simdir, "base")
    res = dict(simdir=simdir, backgrounds=summ["backgrounds"], tails={}, base_moments={},
               variants={}, linear={})
    for t in ALLT:
        res["tails"][f"{t:g}"] = {k: tail_stats(finite(base[f"{k}_{t:g}"])) for k in "aD"}
        res["base_moments"][f"{t:g}"] = {k: boot_moments(finite(base[f"{k}_{t:g}"]))
                                         for k in "aD"}
    L = np.load(os.path.join(simdir, "linear_euler01.npz"))
    for t in (2.5, 3.0, 3.25, 3.5, 4.0):
        j = int(round((t - 2) / 0.001))
        i = int(round((t - 2) / 0.01))
        res["linear"][f"{t:g}"] = dict(lin_std_a=float(L["std_a"][j]),
                                       lin_std_D=float(L["std_D"][j]),
                                       run_std_a=float(base["m_std_a"][i]),
                                       run_std_D=float(base["m_std_D"][i]))
    for vn, info in summ["variants"].items():
        v = load(simdir, vn)
        d = dict(config=info["config"], ndead=info["ndead"], wall_s=info["wall_s"], at={})
        for t, row in info["at"].items():
            d["at"][t] = {k: row[k] for k in ("mean_a", "std_a", "skew_a", "kurt_a", "mean_D",
                                              "std_D", "skew_D", "kurt_D", "min_a",
                                              "med_absa", "max_absa", "nlive")}
        if vn == "off6":
            N = v["N"]
            for t in (6.0, 7.0, 8.0, 10.0):
                j = int(round((t - N[0]) / (N[1] - N[0])))
                d["at"][f"{t:g}"] = d["at"].get(f"{t:g}", {})
                d["at"][f"{t:g}"].update(med_absa=float(v["m_med_absa"][j]),
                                         max_absa=float(v["m_max_absa"][j]))
            Dd = finite(v["D_10"] - v["D_7"])
            d["D10_minus_D7"] = dict(median_abs=float(np.median(np.abs(Dd))),
                                     max_abs=float(np.abs(Dd).max()))
        # first time half of the paths are dead (for the backgrounds that never cross)
        nl = v["m_nlive"]
        half = np.nonzero(nl < 0.5 * nl[0])[0]
        d["N_half_dead"] = float(v["N"][half[0]]) if len(half) else None
        res["variants"][vn] = d
    fig_background(simdir, figdir)
    fig_paths(base, figdir)
    fig_moments(base, figdir)
    fig_pdfs(base, figdir, res["tails"])
    fig_pdfs(base, figdir, res["tails"], log=True)
    fig_variants(simdir, figdir, [
        ("base", "Heun, printed (Stratonovich), h=0.01", fs.PAL["red"], "-"),
        ("ito_em", "EM on Ito-equivalent, h=0.01", fs.PAL["blue"], "--"),
        ("heun_h001", "Heun, h=0.001", "k", ":"),
        ("ito_em_h001", "EM Ito-equivalent, h=0.001", fs.PAL["green"], ":"),
        ("ito_naive", "EM on printed (Ito reading)", fs.PAL["yellow"], "-"),
        ("no_ito", "Heun, Ito term off", fs.PAL["orange"], "-.")], "fig_scheme")
    fig_variants(simdir, figdir, [
        ("base", "seed 1, h=0.01", fs.PAL["red"], "-"),
        ("seed2", "seeds 2-4", "grey", "-"), ("seed3", None, "grey", "-"),
        ("seed4", None, "grey", "-"),
        ("h005", "SDE step 0.005", fs.PAL["blue"], "--"),
        ("h02", "SDE step 0.02", fs.PAL["green"], "--"),
        ("bg_tuned", r"converged bg, $\pi_b^*$ tuned", fs.PAL["orange"], "-."),
        ("bg_e005", "Euler-0.005 bg (no slope)", fs.PAL["yellow"], ":"),
        ("bg_exact", "converged bg (no slope)", "k", ":")], "fig_step_seed")
    fig_off6(load(simdir, "off6"), figdir)
    a3 = load(simdir, "a3one")
    fig_a3one(base, a3, figdir)
    fig_moments(a3, figdir, "fig_a3one_moments", r"$\alpha^3\to1$ in front of the noise")
    fig_linear(simdir, base, figdir)
    with open(os.path.join(out, "langevin.json"), "w") as f:
        json.dump(res, f, indent=1)
    if install:
        os.makedirs(os.path.join(install, "fig"), exist_ok=True)
        os.makedirs(os.path.join(install, "results"), exist_ok=True)
        for fn in os.listdir(figdir):
            if fn.endswith(".png"):
                shutil.copy(os.path.join(figdir, fn), os.path.join(install, "fig", fn))
        shutil.copy(os.path.join(out, "langevin.json"),
                    os.path.join(install, "results", "langevin.json"))
        shutil.copy(os.path.join(simdir, "summary.json"),
                    os.path.join(install, "results", "simulate_summary.json"))


if __name__ == "__main__":
    main()
