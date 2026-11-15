#!/usr/bin/env python3
"""Figures of the reference runs (replaces the first-draft figures written by ref_spec.py).

    python3 ref_plot.py quadratic|inflection <run_dir of the ref_spec.py run>

Reads results/ref_<case>.json and <run_dir>/ref_<case>_samples.npz of the production run,
recomputes the noise tables and P_R(k) (cheap, deterministic) for the set-up figure.
"""
import os
import sys
import json

CASE, SRC = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], CASE, "16"]
import common  # noqa: E402
from common import np, figstyle, savefig, pmap  # noqa: E402
import ref_spec as R  # noqa: E402
from sdn import linear  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main():
    figstyle.use_style()
    out = json.load(open(os.path.join(common.RES, f"ref_{CASE}.json")))
    assert os.path.basename(SRC.rstrip("/")) == out["run_id"], "samples and results must be the same run"
    smp = np.load(os.path.join(SRC, f"ref_{CASE}_samples.npz"))
    P, BG = R.P, R.BG
    sig_lin = np.sqrt(out["linear"]["var_cont_Ne"])
    kinds = [(s, "modes") for s in R.SIGMAS]
    tabs = dict(zip(kinds, pmap(R.table, kinds)))
    ks = R.KMIN * np.exp(np.linspace(0.0, np.log(R.NLAT), 61))
    PRe = linear.PR_late(BG, ks, P["Ne"])

    # ---- set-up figure
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 2.9))
    a1 = figstyle.inch_axes(fig, 0.62, 0.5, 2.0, 2.2)
    a2 = figstyle.inch_axes(fig, 3.3, 0.5, 2.0, 2.2)
    a3 = figstyle.inch_axes(fig, 6.2, 0.5, 1.7, 2.2)
    Ng = np.linspace(P["N0"], P["Ne"], 600)
    a1.semilogy(Ng, [BG.eps1(N) for N in Ng], color=figstyle.PAL["blue"], label="$\\epsilon_1$")
    a1.semilogy(Ng, np.abs([BG.eps2(N) for N in Ng]), color=figstyle.PAL["red"], ls="--", label="$|\\epsilon_2|$")
    cols = [figstyle.PAL["yellow"], figstyle.PAL["green"], figstyle.PAL["orange"]]
    ytxt = [3e2, 3e1, 3e0] if CASE != "quadratic" else [3e-1, 1.5e-1, 7e-2]
    for s, c, yt in zip(R.SIGMAS, cols, ytxt):
        a, b = R.window(s)
        a1.axvspan(a, b, color=c, alpha=0.18)
        a1.text(0.5 * (a + b), yt, f"$\\sigma={s:g}$", fontsize=7, ha="center")
    for lab in ("Nf", "Ne"):
        a1.axvline(P[lab], **figstyle.MASK_LINE)
    a1.set_ylim(1e-13 if CASE != "quadratic" else 3e-3, 3e3 if CASE != "quadratic" else 1.0)
    a1.set_xlabel("$N$")
    a1.set_ylabel("slow-roll parameters")
    a1.legend(loc="center left", fontsize=7)
    for (s, kd), c in zip(kinds, cols):
        t = tabs[(s, kd)]
        Hn = np.array([BG.H(N) for N in t.N])
        e1 = np.array([BG.eps1(N) for N in t.N])
        ref = (Hn / (2 * np.pi)) ** 2 * (1 - e1)
        a2.semilogy(t.N, t.C[:, 0, 0] / ref, color=c, label=f"$\\sigma={s:g}$")
        a2.semilogy(t.N, t.C[:, 1, 1] / (Hn ** 2 * ref), color=c, ls="--")
    a2.axhline(1.0, **figstyle.THIN)
    a2.set_xlabel("$N$")
    a2.set_ylabel("noise / $(H/2\\pi)^2(1-\\epsilon_1)$")
    a2.legend(loc="center right", fontsize=7)
    a2.set_title("solid: $\\phi\\phi$, dashed: $\\varpi\\varpi/H^2$", fontsize=7.5)
    a3.loglog(ks / R.KMIN, PRe, color=figstyle.PAL["blue"])
    a3.set_xlabel("$k/\\mathrm{d}k$")
    a3.set_ylabel("$\\mathcal{P}_\\mathcal{R}(k, N_e)$")
    if CASE == "quadratic":
        a3.set_yscale("linear")
        a3.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    figstyle.no_minor_labels(a3)
    savefig(fig, f"ref_{CASE}_setup")
    plt.close(fig)

    # ---- PDF, variance ratio, skewness and kurtosis
    fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 3.0))
    b1 = figstyle.inch_axes(fig, 0.62, 0.5, 2.3, 2.3)
    b2 = figstyle.inch_axes(fig, 3.55, 0.62, 1.65, 2.18)
    b3 = figstyle.inch_axes(fig, 5.95, 0.62, 1.95, 2.18)
    edges = np.linspace(-7.0, 7.0, 141) if CASE == "quadratic" else np.linspace(-6.0, 7.0, 131)
    cc = 0.5 * (edges[1:] + edges[:-1])
    xs = np.linspace(edges[0], edges[-1], 400)
    b1.semilogy(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), **figstyle.GUIDE, label="Gaussian, var$_\\mathrm{lin}$")
    show = [("s1", figstyle.PAL["yellow"], "$\\sigma=1$"), ("s0.1", figstyle.PAL["green"], "$\\sigma=0.1$"),
            ("s0.01", figstyle.PAL["red"], "$\\sigma=0.01$"), ("s0.01_lattice", figstyle.PAL["blue"], "$\\sigma=0.01$, lattice")]
    for name, c, lab in show:
        x = smp[name][:, 1]
        x = x[np.isfinite(x)]
        d = (x - x.mean()) / sig_lin
        h, _ = np.histogram(d, edges)
        w = len(d) * np.diff(edges)
        ok = h >= 5
        b1.errorbar(cc[ok], h[ok] / w[ok], yerr=np.sqrt(h[ok]) / w[ok], fmt="o", ms=1.6, color=c, lw=0.6, label=lab)
    b1.set_ylim(1e-7, 1.0)
    b1.set_xlim(edges[0], edges[-1])
    b1.set_xlabel("$(\\mathcal{N}-\\langle\\mathcal{N}\\rangle)/\\sigma_\\mathrm{lin}$ at $N_e$")
    b1.set_ylabel("probability density")
    b1.legend(loc="upper right", fontsize=6.5)
    names = [n for n in out["ratios_Ne"]]
    short = {"s1": "1", "s1_dN4e-3": "1,\n$\\Delta N$x2", "s0.1": "0.1", "s0.01": "0.01",
             "s0.01_desitter": "0.01\ndS", "s0.01_lattice": "0.01\nlatt.", "s0.01_lin": "0.01\nlin."}
    for i, name in enumerate(names):
        r = out["ratios_Ne"][name]
        b2.errorbar(i, r["var_over_lin"], yerr=3 * r["se"], fmt="o", color=figstyle.PAL["blue"], ms=3.5)
        st = out[name]["Ne"]
        b3.errorbar(i - 0.12, st["skew"], yerr=3 * st["se_skew"], fmt="s", color=figstyle.PAL["red"], ms=3,
                    label="skewness" if i == 0 else None)
        b3.errorbar(i + 0.12, st["exkurt"], yerr=3 * st["se_exkurt"], fmt="^", color=figstyle.PAL["green"], ms=3,
                    label="excess kurtosis" if i == 0 else None)
    b2.axhline(1.0, **figstyle.THIN)
    b2.set_yscale("log")
    from matplotlib.ticker import FixedLocator, NullFormatter, FormatStrFormatter
    tk = [0.8, 1.0, 1.5] if CASE == "quadratic" else [0.8, 1.0, 1.5, 2.0, 5.0]
    b2.yaxis.set_major_locator(FixedLocator(tk))
    b2.yaxis.set_major_formatter(FormatStrFormatter("%g"))
    b2.yaxis.set_minor_formatter(NullFormatter())
    b3.axhline(0.0, **figstyle.THIN)
    for b in (b2, b3):
        b.set_xticks(range(len(names)))
        b.set_xticklabels([short.get(n, n) for n in names], fontsize=6)
        b.tick_params(axis="x", which="minor", bottom=False, top=False)
        b.set_xlim(-0.6, len(names) - 0.4)
    b2.set_ylabel("var / var$_\\mathrm{lin}$ (3 s.e.)")
    b3.set_ylabel("cumulant ratios (3 s.e.)")
    b3.legend(loc="best", fontsize=6.5)
    fig.text(0.5 * (3.55 + 5.2) / figstyle.FULL_WIDTH, 0.02, "$\\sigma$ / variant", ha="center", fontsize=8)
    fig.text(0.5 * (5.95 + 7.9) / figstyle.FULL_WIDTH, 0.02, "$\\sigma$ / variant", ha="center", fontsize=8)
    savefig(fig, f"ref_{CASE}_pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
