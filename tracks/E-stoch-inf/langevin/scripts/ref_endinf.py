#!/usr/bin/env python3
"""End-of-inflation delta-N for the inflection potential, after the USR phase.

After USR (N ~ 10-11) the classical field sits delta = phi + sqrt2 v ~ 2e-4 M_Pl to the
right of the exact inflection point and creeps (eps1 ~ 1e-12, eps2 ~ -0.028) for about
145 e-folds; there the drift per e-fold is comparable to H/(2pi). Slow roll holds again
(|eps2| << 1), so the overdamped Langevin equation (2206.11234 intro.tex 26-33) is used
from the classical state at N_s = 12 [JUDGEMENT: conditional on that state; the noise
before N_s, including the lattice band, is not included].
Domain: reflecting wall at phi_L (left of the inflection point, where the drift still
points right), absorbing wall at phi_a = -sqrt2 v + 1e-3 (beyond it the remaining noise
variance S^2/(5 kappa^3 delta_a^5) ~ 1e-2 is negligible); from phi_a to the end of
inflation the classical e-folds are added. Methods: moment recursion, BDF2 survival
solver, Sturm-Liouville eigenvalues (tail rates), Monte Carlo; linear slow-roll estimate
int H^2/(8 pi^2 eps1) dN along the classical background.
"""
import common
from common import np, figstyle, save_results, savefig, pmap, seeds, weighted_hist
from sdn import models, linear, langevin, exact
import matplotlib.pyplot as plt
from scipy.linalg import eigh_tridiagonal

MOD = models.HiggsInflection()
DP, H0 = models.h0_fixing(MOD, -1.2)
BG = linear.ClassicalBackground(MOD, -1.2, DP, N0=0.0, Nstar=3.0, N_extra=250.0)
NS = 12.0
PHI_S = BG.state(NS)[0]
PHI_INF = -np.sqrt(2.0) * MOD.v
PHI_A = PHI_INF + 1e-3
CH = 16


def D(p):
    return -MOD.dV(p) / MOD.V(p)


def S(p):
    return np.sqrt(MOD.V(p) / 3.0) / (2 * np.pi)


def N_classical_from(phi):
    from scipy.optimize import brentq
    Nc = brentq(lambda N: BG.state(N)[0] - phi, NS, BG.N_end)
    return Nc


def chunk(n, rng, phiL, dN):
    r = langevin.fpt_overdamped(D, S, PHI_S, PHI_A, dN, n, rng, x_uv=phiL, bridge=True, N_max=2000.0)
    return r["N"]


def main():
    figstyle.use_style()
    out = dict(N_s=NS, phi_s=PHI_S, delta_s=PHI_S - PHI_INF, phi_a=PHI_A, phi_inf=PHI_INF,
               N_end_classical=BG.N_end, H_s=BG.H(NS), eps1_s=BG.eps1(NS), eps2_s=BG.eps2(NS))
    Na = N_classical_from(PHI_A)
    out["N_classical_s_to_a"] = Na - NS
    out["N_classical_a_to_end"] = BG.N_end - Na
    # linear slow-roll estimate along the classical path
    Ng = np.linspace(NS, BG.N_end - 1e-6, 20001)
    Pz = np.array([BG.H(N) ** 2 / (8 * np.pi ** 2 * BG.eps1(N)) for N in Ng])
    out["linear_var_s_to_end"] = np.trapezoid(Pz, Ng)
    ia = np.searchsorted(Ng, Na)
    out["linear_var_s_to_a"] = np.trapezoid(Pz[:ia], Ng[:ia])
    out["Pzeta_at_s"] = Pz[0]
    print(out, flush=True)
    # semi-analytic
    res = {}
    for phiL in (PHI_INF - 4.9e-4, PHI_INF - 1e-3):
        for M in (250_000, 500_000):
            r = exact.fpt_moments(D, S, PHI_A, phiL, PHI_S, nmax=4, M=M)
            res[f"rec_L{phiL - PHI_INF:.1e}_M{M}"] = {k: v for k, v in r.items() if k != "raw"}
            print("recursion", phiL - PHI_INF, M, res[f"rec_L{phiL - PHI_INF:.1e}_M{M}"], flush=True)
    out["recursion"] = res
    phiL = PHI_INF - 4.9e-4
    pde = exact.SurvivalPDE(D, S, PHI_A, phiL, PHI_S, M=250_000)
    pde.run(1200.0, 0.02)
    m1 = np.trapezoid(pde.N * pde.pdf_v, pde.N)
    out["bdf2_mean_var"] = [m1, np.trapezoid((pde.N - m1) ** 2 * pde.pdf_v, pde.N)]
    out["bdf2_surv_at_end"] = pde.surv[-1]
    # lowest eigenvalues (tail rates) of the same operator
    sp = exact.SpectralFPT.__new__(exact.SpectralFPT)
    lam = None
    try:
        dom = exact.Domain(D, S, PHI_A, phiL, 250_000)
        y, h = dom.y, dom.h
        lpn = dom.lnpsi(y)
        lpm = dom.lnpsi(0.5 * (y[1:] + y[:-1]))
        lW = np.log(2.0) + lpn - np.log(dom.S2(y)) + np.log(np.r_[np.full(len(y) - 1, h), 0.5 * h])
        idx = np.arange(1, len(y))
        dg = np.exp(lpm[idx - 1] - lW[idx]) / h
        dg[:-1] += np.exp(lpm[idx[:-1]] - lW[idx[:-1]]) / h
        off = -np.exp(lpm[idx[:-1]] - 0.5 * (lW[idx[:-1]] + lW[idx[:-1] + 1])) / h
        lam = eigh_tridiagonal(dg, off, eigvals_only=True, select="i", select_range=(0, 3))
    except Exception as e:  # noqa: BLE001
        print("eigen failed", e)
    out["eigenvalues"] = lam
    # Monte Carlo
    mc = {}
    for dN, n, seed in ((0.02, 200_000, 31), (0.005, 100_000, 32)):
        N = np.concatenate(pmap(chunk, [(n // CH, r, phiL, dN) for r in seeds(seed, CH)]))
        mc[dN] = N
        x = N[np.isfinite(N)]
        c = x - x.mean()
        bs = np.array_split(x, 20)
        out[f"mc_dN{dN}"] = dict(n=len(N), n_nan=int((~np.isfinite(N)).sum()), mean=x.mean(), var=np.mean(c ** 2),
                                 skew=np.mean(c ** 3) / np.mean(c ** 2) ** 1.5,
                                 exkurt=np.mean(c ** 4) / np.mean(c ** 2) ** 2 - 3,
                                 se_mean=np.std([b.mean() for b in bs], ddof=1) / np.sqrt(20),
                                 se_var=np.std([b.var() for b in bs], ddof=1) / np.sqrt(20))
        print("mc", dN, out[f"mc_dN{dN}"], flush=True)
    np.savez_compressed(f"{common.RUN_DIR}/endinf_samples.npz", **{f"dN{k}": v for k, v in mc.items()})
    # tail: survival function of the BDF2 solution and of the MC
    rec = res[f"rec_L{-4.9e-4:.1e}_M500000"]
    sd = np.sqrt(rec["var"])
    out["tail_bdf2"] = {str(k): float(np.interp(rec["mean"] + k * sd, pde.N, pde.surv)) for k in (1, 2, 3, 5, 8, 12)}
    out["gaussian_tail"] = {str(k): float(0.5 * __import__("scipy").special.erfc(k / np.sqrt(2))) for k in (1, 2, 3, 5, 8, 12)}
    # figure
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.0))
    a1 = figstyle.inch_axes(fig, 0.7, 0.5, 3.1, 2.3)
    a2 = figstyle.inch_axes(fig, 4.65, 0.5, 3.1, 2.3)
    a1.semilogy(pde.N, pde.pdf_v, **figstyle.GUIDE, label="survival solver (BDF2)")
    edges = np.arange(0.0, 1200.0, 2.0)
    N = mc[0.02]
    p, e, cnt = weighted_hist(N, np.ones_like(N), edges)
    cc = 0.5 * (edges[1:] + edges[:-1])
    ok = cnt >= 10
    a1.errorbar(cc[ok], p[ok], yerr=e[ok], fmt="o", ms=2, color=figstyle.PAL["red"], lw=0.7, label="Monte Carlo, $2\\times10^5$")
    xs = np.linspace(0, 1200, 600)
    a1.semilogy(xs, np.exp(-(xs - rec["mean"]) ** 2 / (2 * rec["var"])) / np.sqrt(2 * np.pi * rec["var"]),
                **figstyle.THIN, ls=":", label="Gaussian, same mean and variance")
    if lam is not None:
        a1.semilogy(xs, pde.pdf_v[int(400 / 0.02)] * np.exp(-lam[0] * (xs - 400)), color="grey", lw=1.0, ls="-.",
                    label="$e^{-\\lambda_0\\mathcal{N}}$")
    a1.set_ylim(1e-12, 1)
    a1.set_xlim(0, 1200)
    a1.set_xlabel("$\\mathcal{N}$ from $N_s = 12$ to $\\phi_a$")
    a1.set_ylabel("$P(\\mathcal{N})$")
    a1.legend(loc="upper right", fontsize=7)
    a2.semilogy(Ng - NS, Pz, color=figstyle.PAL["blue"], label="$H^2/(8\\pi^2\\epsilon_1)$")
    a2.axvline(Na - NS, **figstyle.MASK_LINE)
    a2.axhline(1.0, **figstyle.THIN)
    a2.set_xlabel("$N - N_s$ (classical)")
    a2.set_ylabel("$\\mathcal{P}_\\zeta$ per e-fold (slow roll)")
    a2.legend(loc="upper right", fontsize=7)
    savefig(fig, "ref_inflection_endinf")
    plt.close(fig)
    save_results("ref_inflection_endinf", out)


if __name__ == "__main__":
    main()
