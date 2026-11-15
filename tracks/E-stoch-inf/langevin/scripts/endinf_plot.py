#!/usr/bin/env python3
"""Figure and tail slopes for the end-of-inflation run (replaces the first-draft figure).

    python3 endinf_plot.py <run_dir of the ref_endinf.py run>

Recomputes the BDF2 density (same domain and grid, N <= 300, where the survival is
already negligible), reads the Monte Carlo samples of the run, writes
fig/ref_inflection_endinf.png and results/ref_inflection_endinf_tail.json.
"""
import os
import sys
import json

SRC = sys.argv[1]
import common  # noqa: E402
from common import np, figstyle, savefig, weighted_hist, save_results  # noqa: E402
import ref_endinf as E  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main():
    figstyle.use_style()
    res = json.load(open(os.path.join(common.RES, "ref_inflection_endinf.json")))
    assert os.path.basename(SRC.rstrip("/")) == res["run_id"]
    smp = np.load(os.path.join(SRC, "endinf_samples.npz"))
    phiL = E.PHI_INF - 4.9e-4
    pde = E.exact.SurvivalPDE(E.D, E.S, E.PHI_A, phiL, E.PHI_S, M=250_000)
    pde.run(300.0, 0.02)
    rec = res["recursion"][f"rec_L{-4.9e-4:.1e}_M500000"]
    m, sd = rec["mean"], np.sqrt(rec["var"])
    lp = np.log(np.maximum(pde.pdf_v, 1e-300))
    slope = np.gradient(lp, pde.N)
    pts = [m + k * sd for k in (2, 4, 6, 8, 10, 12)]
    out = dict(source_run=res["run_id"], mean=m, sd=sd,
               local_tail_slope={f"{(x - m) / sd:.0f}sd": float(np.interp(x, pde.N, slope)) for x in pts},
               local_left_slope={f"-{k}sd": float(np.interp(m - k * sd, pde.N, slope)) for k in (2, 3, 4)},
               gaussian_slope_at={f"{(x - m) / sd:.0f}sd": float(-(x - m) / sd ** 2) for x in pts},
               pdf_at={f"{(x - m) / sd:.0f}sd": float(np.interp(x, pde.N, pde.pdf_v)) for x in pts})
    print(out, flush=True)
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.0))
    a1 = figstyle.inch_axes(fig, 0.7, 0.5, 3.1, 2.3)
    a2 = figstyle.inch_axes(fig, 4.65, 0.5, 3.1, 2.3)
    sel = pde.N > 40
    a1.semilogy(pde.N[sel], pde.pdf_v[sel], **figstyle.GUIDE, label="survival solver (BDF2)")
    edges = np.arange(60.0, 260.0, 2.0)
    cc = 0.5 * (edges[1:] + edges[:-1])
    for key, col, lab in (("dN0.02", figstyle.PAL["red"], "MC $2\\times10^5$, $\\Delta N=0.02$"),
                          ("dN0.005", figstyle.PAL["yellow"], "MC $10^5$, $\\Delta N=0.005$")):
        N = smp[key]
        p, e, cnt = weighted_hist(N, np.ones_like(N), edges)
        ok = cnt >= 10
        a1.errorbar(cc[ok], p[ok], yerr=e[ok], fmt="o", ms=2, color=col, lw=0.7, label=lab)
    xs = np.linspace(60, 260, 400)
    a1.semilogy(xs, np.exp(-(xs - m) ** 2 / (2 * sd ** 2)) / np.sqrt(2 * np.pi * sd ** 2),
                **figstyle.THIN, ls=":", label="Gaussian, same mean and variance")
    a1.set_ylim(1e-14, 1)
    a1.set_xlim(60, 260)
    a1.set_xlabel("$\\mathcal{N}$ from $N_s = 12$ to $\\phi_a$")
    a1.set_ylabel("$P(\\mathcal{N})$")
    a1.legend(loc="upper right", fontsize=6.5)
    Ng = np.linspace(E.NS, E.BG.N_end - 1e-6, 4001)
    Pz = np.array([E.BG.H(N) ** 2 / (8 * np.pi ** 2 * E.BG.eps1(N)) for N in Ng])
    a2.semilogy(Ng - E.NS, Pz, color=figstyle.PAL["blue"], label="$H^2/(8\\pi^2\\epsilon_1)$, classical path")
    a2.axvline(res["N_classical_s_to_a"], **figstyle.MASK_LINE)
    a2.axhline(1.0, **figstyle.THIN)
    a2.set_xlabel("$N - N_s$")
    a2.set_ylabel("$\\mathcal{P}_\\zeta$ per e-fold (slow roll)")
    a2.legend(loc="lower left", fontsize=7)
    savefig(fig, "ref_inflection_endinf")
    plt.close(fig)
    save_results("ref_inflection_endinf_tail", out)


if __name__ == "__main__":
    main()
