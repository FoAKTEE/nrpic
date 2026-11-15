#!/usr/bin/env python3
"""V1: Langevin first passage against the exact drift-diffusion result of 1308.4754.

X = mu N + W first reaching m (1308.4754 v2 lines 285-365; slow-roll inflation with a
linear H maps onto it, lines 378-443). Checks: mean, variance and third central moment of
the first-passage time against m/mu, m/mu^3, 3 m/mu^5 (line 353-364), the density against
the inverse Gaussian, the step-size convergence with and without the Brownian-bridge test,
and importance sampling (constant bias) against the exact tail and the identity E_S[w] = 1,
for the weight sign derived here and for the sign printed in 2206.11234 method.tex line 78.
"""
from common import (np, figstyle, save_results, savefig, pmap, seeds, weighted_hist)
from sdn import langevin, exact
import matplotlib.pyplot as plt

CASES = [dict(mu=1.0, m=5.0), dict(mu=0.5, m=2.0)]
DNS = [0.1, 0.03, 0.01, 0.003, 0.001]
NREAL = 200000
CHUNKS = 8


def chunk(mu, m, dN, n, rng, bridge, A):
    D = lambda x: np.full_like(x, mu)
    S = lambda x: np.ones_like(x)
    bias = (lambda x: np.full_like(x, A)) if A else None
    r = langevin.fpt_overdamped(D, S, 0.0, m, dN, n, rng, bridge=bridge, bias=bias, N_max=400.0)
    return r["N"], r["logw"]


def sample(mu, m, dN, n, bridge, A, seed):
    res = pmap(chunk, [(mu, m, dN, n // CHUNKS, r, bridge, A) for r in seeds(seed, CHUNKS)])
    return np.concatenate([a for a, _ in res]), np.concatenate([b for _, b in res])


def stats(N):
    n = len(N)
    mean = N.mean()
    c = N - mean
    var = np.mean(c ** 2)
    mu3 = np.mean(c ** 3)
    # standard errors by batch means (20 batches)
    bm = np.array([b.mean() for b in np.array_split(N, 20)])
    bv = np.array([np.var(b) for b in np.array_split(N, 20)])
    b3 = np.array([np.mean((b - b.mean()) ** 3) for b in np.array_split(N, 20)])
    se = lambda x: x.std(ddof=1) / np.sqrt(len(x))
    return dict(n=n, mean=mean, var=var, mu3=mu3, se_mean=se(bm), se_var=se(bv), se_mu3=se(b3),
                n_nan=int(np.isnan(N).sum()))


def main():
    out = dict(cases=[])
    figstyle.use_style()
    for ci, cs in enumerate(CASES):
        mu, m = cs["mu"], cs["m"]
        ex = exact.ig_moments(m, mu)
        rec = dict(mu=mu, m=m, exact=ex, conv=[])
        for bridge in (False, True):
            for k, dN in enumerate(DNS):
                N, _ = sample(mu, m, dN, NREAL, bridge, 0.0, 1000 * ci + 10 * k + bridge)
                st = stats(N)
                st.update(dN=dN, bridge=bridge)
                rec["conv"].append(st)
                print(f"mu={mu} m={m} bridge={bridge} dN={dN}: mean {st['mean']:.5f}+-{st['se_mean']:.5f}"
                      f" (exact {ex['mean']:.5f}) var {st['var']:.4f}+-{st['se_var']:.4f} (exact {ex['var']:.4f})"
                      f" mu3 {st['mu3']:.3f}+-{st['se_mu3']:.3f} (exact {ex['mu3']:.3f})", flush=True)
                if bridge and dN == DNS[-1]:
                    keepN = N
        # fit of the mean bias vs dN (no bridge): bias = c dN^p
        nb = [c for c in rec["conv"] if not c["bridge"]]
        b = np.array([c["mean"] - ex["mean"] for c in nb])
        h = np.array([c["dN"] for c in nb])
        p, lc = np.polyfit(np.log(h), np.log(np.abs(b)), 1)
        rec["nobridge_bias_fit"] = dict(exponent=p, coeff=np.exp(lc), coeff_times_mu=np.exp(lc) * mu)
        # importance sampling at the finest-but-one step with bridge
        rec["IS"] = []
        Nmax_plot = ex["mean"] + 25 * np.sqrt(ex["var"])
        is_curves = []
        for A in (-0.5 * mu, -0.8 * mu):
            N, lw = sample(mu, m, 0.003, NREAL, True, A, 5000 + 100 * ci + int(-10 * A))
            w = np.exp(lw)
            # printed sign of 2206.11234 method.tex line 78: log w_printed = -log w - B^2 dN... per
            # step the exponent is +(B/S^2)(B dN/2 + S xi sqrt(dN)) = -(our exponent)
            w_pr = np.exp(-lw)
            Jtest = 0.5
            lap_IS = np.mean(w * np.exp(-Jtest * N))
            rec["IS"].append(dict(A=A, mean_w=w.mean(), se_w=w.std() / np.sqrt(len(w)),
                                  mean_w_printed_sign=w_pr.mean(),
                                  laplace_J=Jtest, laplace_IS=lap_IS,
                                  laplace_exact=exact.ig_laplace(Jtest, m, mu),
                                  mean_N_reweighted=np.sum(w * N) / np.sum(w)))
            edges = np.linspace(0.0, Nmax_plot, 121)
            pdf, err, cnt = weighted_hist(N, w, edges)
            is_curves.append((A, edges, pdf, err, cnt))
            print(f"IS A={A}: <w>={w.mean():.4f}+-{w.std()/np.sqrt(len(w)):.4f}, printed-sign <w>={w_pr.mean():.3e}, "
                  f"Laplace(J=0.5) IS {lap_IS:.5f} exact {exact.ig_laplace(Jtest, m, mu):.5f}", flush=True)
        out["cases"].append(rec)
        np.savez_compressed(f"{__import__('common').RUN_DIR}/v1_case{ci}.npz", N=keepN)

        # ---- figure: PDF (direct and IS) against the inverse Gaussian; convergence
        fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.2))
        ax1 = figstyle.inch_axes(fig, 0.75, 0.55, 3.0, 2.45)
        ax2 = figstyle.inch_axes(fig, 4.6, 0.55, 3.0, 2.45)
        x = np.linspace(1e-3, Nmax_plot, 800)
        ax1.semilogy(x, exact.ig_pdf(x, m, mu), **figstyle.GUIDE, label="inverse Gaussian")
        edges = np.linspace(0.0, Nmax_plot, 121)
        pdf, err, cnt = weighted_hist(keepN, np.ones_like(keepN), edges)
        c = 0.5 * (edges[1:] + edges[:-1])
        ok = cnt >= 10
        ax1.errorbar(c[ok], pdf[ok], yerr=err[ok], fmt="o", ms=2.5, color=figstyle.PAL["red"],
                     label="direct, $\\Delta N=10^{-3}$")
        for (A, e2, p2, er2, cn2), col in zip(is_curves, [figstyle.PAL["yellow"], figstyle.PAL["green"]]):
            ok = cn2 >= 10
            c2 = 0.5 * (e2[1:] + e2[:-1])
            ax1.errorbar(c2[ok], p2[ok], yerr=er2[ok], fmt="s", ms=2.0, color=col,
                         label=f"bias $B={A:g}$")
        ax1.set_xlabel("first-passage time $\\mathcal{N}$")
        ax1.set_ylabel("$P(\\mathcal{N})$")
        ax1.set_ylim(1e-16, 2)
        ax1.legend(loc="upper right", fontsize=8)
        for bridge, col, lab in ((False, figstyle.PAL["red"], "no bridge test"),
                                 (True, figstyle.PAL["blue"], "Brownian-bridge test")):
            cc = [c for c in rec["conv"] if c["bridge"] == bridge]
            hh = np.array([c["dN"] for c in cc])
            bb = np.array([abs(c["mean"] - ex["mean"]) for c in cc])
            ee = np.array([c["se_mean"] for c in cc])
            ax2.errorbar(hh, bb, yerr=ee, fmt="o-", color=col, ms=3, label=lab)
        hh = np.array(DNS)
        ax2.loglog(hh, rec["nobridge_bias_fit"]["coeff"] * hh ** rec["nobridge_bias_fit"]["exponent"],
                   **figstyle.THIN, ls=":")
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.axhline(np.sqrt(ex["var"] / NREAL), **figstyle.MASK_LINE)
        ax2.set_xlabel("step $\\Delta N$")
        ax2.set_ylabel("$|\\langle\\mathcal{N}\\rangle - m/\\mu|$")
        ax2.legend(loc="lower right", fontsize=8)
        savefig(fig, f"v1_drift_mu{mu:g}_m{m:g}")
        plt.close(fig)
    save_results("v1_drift_diffusion", out)


if __name__ == "__main__":
    main()
