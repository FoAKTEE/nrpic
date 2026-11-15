#!/usr/bin/env python3
"""V2: quadratic inflation in the diffusion-dominated regime, the benchmark of 2206.11234.

V = m^2 phi^2 / 2, m = 1 M_Pl, phi_in = phi_UV = sqrt(42), phi_end = sqrt(2)
(2206.11234 v2 demonstration.tex lines 18-25, 42-55, Fig. 2). Semi-analytic references:
the closed-form characteristic function of appendix.tex lines 60-102 (Laplace transform and
its poles), the BDF2 survival solver and the moment recursion of sdn/exact.py, the lowest
Sturm-Liouville eigenvalues. Monte Carlo: direct sampling (dN = 0.01 and 0.002) and
importance sampling with B = A H/(2 pi), A = 0.4 and 0.8 (naive estimator), as in the paper.
"""
import common
from common import np, figstyle, save_results, savefig, pmap, seeds, weighted_hist
from sdn import langevin, exact
import matplotlib.pyplot as plt
import mpmath as mp

M_INF = 1.0
PHI_IN = np.sqrt(42.0)
PHI_UV = PHI_IN
PHI_END = np.sqrt(2.0)
V0 = M_INF ** 2 / (48 * np.pi ** 2)        # reduced potential v = v0 phi^2 (appendix.tex 34, 63)
CH = 16


def D(p):
    return -2.0 / p


def S(p):
    return M_INF * np.abs(p) / (2 * np.pi * np.sqrt(6.0))


def chunk(dN, n, rng, A):
    bias = (lambda p: A * S(p)) if A else None
    r = langevin.fpt_overdamped(D, S, PHI_IN, PHI_END, dN, n, rng, x_uv=PHI_UV, bridge=True,
                                bias=bias, N_max=300.0)
    return r["N"], r["logw"]


def sample(dN, n, A, seed):
    res = pmap(chunk, [(dN, n // CH, r, A) for r in seeds(seed, CH)])
    return np.concatenate([a for a, _ in res]), np.concatenate([b for _, b in res])


def batch_stats(N, w=None, nb=20):
    w = np.ones_like(N) if w is None else w
    mean = np.sum(w * N) / np.sum(w)
    var = np.sum(w * (N - mean) ** 2) / np.sum(w)
    bm = [np.mean(b) for b in np.array_split(N, nb)]
    bv = [np.var(b) for b in np.array_split(N, nb)]
    return dict(mean=mean, var=var, se_mean=np.std(bm, ddof=1) / np.sqrt(nb),
                se_var=np.std(bv, ddof=1) / np.sqrt(nb), n=len(N), n_nan=int(np.isnan(N).sum()))


def closed_form_pole(lo, hi):
    """Bisection on the sign change of chi(iJ) across a simple pole, J in [lo, hi] (negative)."""
    f = lambda J: exact.quadratic_laplace_closed_form([J], PHI_IN, M_INF, PHI_END, PHI_UV)[0]
    flo, fhi = f(lo), f(hi)
    assert np.sign(flo) != np.sign(fhi)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if np.sign(fm) == np.sign(flo):
            lo, flo = mid, fm
        else:
            hi, fhi = mid, fm
    return 0.5 * (lo + hi)


def main():
    figstyle.use_style()
    out = dict(model=dict(m=M_INF, phi_in=PHI_IN, phi_uv=PHI_UV, phi_end=PHI_END, v0=V0,
                          v0_over_4=V0 / 4))
    # ---- semi-analytic references
    J = np.array([0.01, 0.03, 0.1, 0.3, 1.0])
    out["laplace_closed_form"] = dict(J=J, chi=exact.quadratic_laplace_closed_form(J, PHI_IN, M_INF, PHI_END, PHI_UV))
    spec = {}
    for M in (4000, 8000):
        sp = exact.SpectralFPT(D, S, PHI_END, PHI_UV, PHI_IN, M=M)
        spec[M] = sp.lam[:6]
    out["eigenvalues"] = {str(k): v for k, v in spec.items()}
    lam0 = spec[8000][0]
    pdes = {}
    for M in (4000, 8000):
        pde = exact.SurvivalPDE(D, S, PHI_END, PHI_UV, PHI_IN, M=M)
        pde.run(120.0, 0.002)
        pdes[M] = pde
        out[f"laplace_pde_M{M}"] = pde.laplace(J, lam_tail=lam0)
        Nn, pp = pde.N, pde.pdf_v
        m1 = np.trapezoid(Nn * pp, Nn)
        out[f"pde_M{M}_mean_var"] = [m1, np.trapezoid((Nn - m1) ** 2 * pp, Nn)]
    rec = {}
    for M in (20000, 40000):
        r = exact.fpt_moments(D, S, PHI_END, PHI_UV, PHI_IN, nmax=4, M=M)
        rec[M] = {k: v for k, v in r.items() if k != "raw"}
    out["moments_recursion"] = {str(k): v for k, v in rec.items()}
    # poles of the closed form: scan J from -1e-5 to -1.2 for sign changes
    scan = -np.concatenate([np.linspace(1e-5, 2e-3, 41), np.linspace(2e-3, 1.25, 500)])
    vals = exact.quadratic_laplace_closed_form(scan, PHI_IN, M_INF, PHI_END, PHI_UV)
    poles = []
    for i in range(len(scan) - 1):
        if np.sign(vals[i]) != np.sign(vals[i + 1]) and abs(vals[i]) > 10 and abs(vals[i + 1]) > 10:
            poles.append(-closed_form_pole(scan[i], scan[i + 1]))
    out["closed_form_poles"] = poles
    out["closed_form_near_v0_over_4"] = dict(
        J=[-0.999 * V0 / 4, -1.001 * V0 / 4],
        chi=exact.quadratic_laplace_closed_form([-0.999 * V0 / 4, -1.001 * V0 / 4], PHI_IN, M_INF, PHI_END, PHI_UV))
    print("eigenvalues", spec, "closed-form poles", poles, flush=True)
    print("recursion", rec, "pde mean/var", out["pde_M8000_mean_var"], flush=True)
    print("laplace closed", out["laplace_closed_form"]["chi"], "pde", out["laplace_pde_M8000"], flush=True)

    # ---- Monte Carlo
    mc = {}
    for dN, n, seed in ((0.01, 1_000_000, 11), (0.002, 1_000_000, 12)):
        N, _ = sample(dN, n, 0.0, seed)
        mc[f"direct_dN{dN}"] = (N, np.ones_like(N))
        out[f"direct_dN{dN}"] = batch_stats(N)
        out[f"direct_dN{dN}"]["laplace"] = [np.mean(np.exp(-j * N)) for j in J]
        print("direct", dN, out[f"direct_dN{dN}"], flush=True)
    for A, seed in ((0.4, 21), (0.8, 22)):
        N, lw = sample(0.002, 200_000, A, seed)
        w = np.exp(lw)
        mc[f"IS_A{A}"] = (N, w)
        out[f"IS_A{A}"] = dict(mean_w=w.mean(), se_w=w.std() / np.sqrt(len(w)),
                               laplace=[np.mean(w * np.exp(-j * N)) for j in J],
                               mean_N_reweighted=np.sum(w * N) / len(w))
        print("IS", A, out[f"IS_A{A}"], flush=True)
    np.savez_compressed(f"{common.RUN_DIR}/v2_samples.npz",
                        **{k: v[0] for k, v in mc.items()}, **{k + "_w": v[1] for k, v in mc.items()})

    # ---- densities against the BDF2 reference
    pde = pdes[8000]
    edges = np.arange(0.0, 80.0 + 1e-9, 0.25)
    c = 0.5 * (edges[1:] + edges[:-1])
    pref_bin = np.array([np.trapezoid(pde.pdf_v[(pde.N >= a) & (pde.N <= b)], pde.N[(pde.N >= a) & (pde.N <= b)]) / (b - a)
                         for a, b in zip(edges[:-1], edges[1:])])
    dens = {}
    for key, (N, w) in mc.items():
        p, e, cnt = weighted_hist(N, w, edges)
        dens[key] = (p, e, cnt)
        ok = cnt >= 100
        z = (p[ok] - pref_bin[ok]) / np.maximum(e[ok], 1e-300)
        out[f"{key}_vs_pde"] = dict(n_bins=int(ok.sum()), chi2_per_bin=float(np.mean(z ** 2)),
                                    max_abs_z=float(np.max(np.abs(z))),
                                    deepest_P_with_100=float(p[ok].min()),
                                    deepest_N_with_100=float(c[ok].max()),
                                    max_rel_dev=float(np.max(np.abs(p[ok] / pref_bin[ok] - 1))))
        print(key, out[f"{key}_vs_pde"], flush=True)
    # paper statement (demonstration.tex 53): direct 2e5 runs, bins with n_j > 400
    N2 = mc["direct_dN0.002"][0][:200_000]
    p, e, cnt = weighted_hist(N2, np.ones_like(N2), edges)
    out["direct_2e5_deepest_P_400_per_bin"] = float(p[cnt > 400].min())
    # tail slope of the A = 0.8 data for N > 20
    p, e, cnt = dens["IS_A0.8"]
    ok = (cnt >= 100) & (c > 20)
    sl = np.polyfit(c[ok], np.log(p[ok]), 1, w=p[ok] / e[ok])[0]
    out["IS_A0.8_tail_slope"] = dict(fit_range=[float(c[ok].min()), float(c[ok].max())], slope=sl,
                                     minus_lam0=-lam0, minus_v0_over_4=-V0 / 4)
    out["pde_tail_slope_40_80"] = (np.log(pde.pdf_v[int(80 / 0.002)]) - np.log(pde.pdf_v[int(40 / 0.002)])) / 40
    print("tail", out["IS_A0.8_tail_slope"], out["pde_tail_slope_40_80"], flush=True)

    # ---- figure
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.3))
    ax1 = figstyle.inch_axes(fig, 0.75, 0.55, 3.2, 2.55)
    ax2 = figstyle.inch_axes(fig, 4.75, 0.55, 3.0, 2.55)
    sel = pde.N >= 2.5      # below, the start-up error (~1e-12) exceeds the true density
    ax1.semilogy(pde.N[sel], pde.pdf_v[sel], **figstyle.GUIDE, label="survival solver (BDF2)")
    styles = [("direct_dN0.002", figstyle.PAL["red"], "o", "direct, $10^6$"),
              ("IS_A0.4", figstyle.PAL["yellow"], "s", "IS, $A=0.4$"),
              ("IS_A0.8", figstyle.PAL["green"], "^", "IS, $A=0.8$")]
    for key, col, mk, lab in styles:
        p, e, cnt = dens[key]
        ok = cnt >= 100
        ax1.errorbar(c[ok], p[ok], yerr=e[ok], fmt=mk, ms=2.2, color=col, lw=0.8, label=lab)
        ax2.errorbar(c[ok], p[ok] / pref_bin[ok] - 1, yerr=e[ok] / pref_bin[ok], fmt=mk, ms=2.2,
                     color=col, lw=0.8, label=lab)
    Nt = np.linspace(20, 80, 10)
    i40 = int(40 / 0.002)
    ax1.semilogy(Nt, pde.pdf_v[i40] * np.exp(-lam0 * (Nt - 40)), **figstyle.THIN, ls=":",
                 label="$e^{-\\lambda_0 \\mathcal{N}}$, $\\lambda_0=%.4f$" % lam0)
    ax1.semilogy(Nt, pde.pdf_v[i40] * np.exp(-V0 / 4 * (Nt - 40)), color="grey", lw=1.0, ls="-.",
                 label="$e^{-v_0 \\mathcal{N}/4}$")
    ax1.set_ylim(1e-16, 1)
    ax1.set_xlim(0, 80)
    ax1.set_xlabel("$\\mathcal{N}$")
    ax1.set_ylabel("$P(\\mathcal{N})$")
    ax1.legend(loc="upper right", fontsize=7.5)
    ax2.axhline(0, **figstyle.THIN)
    ax2.set_ylim(-0.3, 0.3)
    ax2.set_xlim(0, 60)
    ax2.set_xlabel("$\\mathcal{N}$")
    ax2.set_ylabel("Monte Carlo / reference $-1$")
    savefig(fig, "v2_quadratic_m1")
    plt.close(fig)

    # Laplace-transform figure: closed form vs BDF2 vs MC
    fig = plt.figure(figsize=(figstyle.COLUMN_WIDTH, 3.0))
    ax = figstyle.inch_axes(fig, 0.8, 0.55, 3.0, 2.3)
    cf = out["laplace_closed_form"]["chi"]
    ax.semilogx(J, out["laplace_pde_M8000"] / cf - 1, "o-", color=figstyle.PAL["blue"], ms=3, label="BDF2 / closed form $-1$")
    ax.semilogx(J, np.array(out["direct_dN0.002"]["laplace"]) / cf - 1, "s-", color=figstyle.PAL["red"], ms=3,
                label="direct MC / closed form $-1$")
    ax.axhline(0, **figstyle.THIN)
    ax.set_xlabel("$J$")
    ax.set_ylabel("relative difference of $\\langle e^{-J\\mathcal{N}}\\rangle$")
    ax.legend(loc="lower left", fontsize=7.5)
    savefig(fig, "v2_quadratic_m1_laplace")
    plt.close(fig)
    save_results("v2_quadratic", out)


if __name__ == "__main__":
    main()
