"""Figure: stochastic delta-N reference statistics for the two test cases (separate-universe
Langevin solver of the track, the comparison outside numerical relativity).

Reads ref_<case>.json and ref_<case>_samples.npz of runs E-stoch-inf-20261115-130139-176cdd6
(quadratic, slow roll) and E-stoch-inf-20261115-130137-176cdd6 (inflection, ultra-slow
roll); checksums verified against the manifests. Noise band dk ... 64 dk of the 256^3
lattice; delta N measured at the uniform-field surface N_e = N* + 15.
(a) Probability density of (N - <N>)/sigma_lin, sigma_lin^2 the linear variance of the
band, for the coarse-graining sigma = 0.01; the dashed curve is the unit Gaussian.
(b) Variance over the linear variance against the coarse-graining parameter sigma
(error bars three standard errors); the dotted line marks the lattice sum of the band in
the slow-roll case (lattice density of states over the continuum integral).
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402

RUNS = {"quadratic": "E-stoch-inf-20261115-130139-176cdd6",
        "inflection": "E-stoch-inf-20261115-130137-176cdd6"}
LAB = {"quadratic": "slow roll", "inflection": "ultra-slow roll"}
COL = {"quadratic": cz.PAL["blue"], "inflection": cz.PAL["red"]}


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    fig = plt.figure(figsize=(3.4, 4.7))
    a = cz.inch_axes(fig, 0.72, 2.72, 2.55, 1.75)
    b = cz.inch_axes(fig, 0.72, 0.48, 2.55, 1.6)
    edges = np.linspace(-6.0, 7.0, 105)
    cc = 0.5 * (edges[1:] + edges[:-1])
    xs = np.linspace(-6.0, 7.0, 400)
    a.semilogy(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi), **cz.GUIDE, label="Gaussian")
    sig_list = (1.0, 0.1, 0.01)
    for j, (case, run) in enumerate(RUNS.items()):
        res = C.load_json(run, f"ref_{case}.json")
        smp = np.load(C.path(run, f"ref_{case}_samples.npz"))
        sl = np.sqrt(res["linear"]["var_cont_Ne"])
        x = smp["s0.01"][:, 1]
        x = x[np.isfinite(x)]
        d = (x - x.mean()) / sl
        h, _ = np.histogram(d, edges)
        w = len(d) * np.diff(edges)
        ok = h >= 5
        a.errorbar(cc[ok], h[ok] / w[ok], yerr=np.sqrt(h[ok]) / w[ok], fmt="o" if j == 0 else "s",
                   ms=2.0, color=COL[case], lw=0.6, label=LAB[case])
        rat = [res["ratios_Ne"][f"s{s:g}"] for s in sig_list]
        off = 1.0 + (0.08 if j else -0.08)
        b.errorbar(np.array(sig_list) * off, [r["var_over_lin"] for r in rat],
                   yerr=[3 * r["se"] for r in rat], fmt="o" if j == 0 else "s", ms=3.5,
                   color=COL[case], lw=0.9, label=LAB[case])
        if case == "quadratic":
            b.axhline(res["linear"]["lattice_over_cont"], color=COL[case], lw=1.0,
                      ls=(0, (1.5, 1.5)))
    a.set_xlim(-5.5, 5.5)
    a.set_ylim(1e-6, 1.0)
    a.set_xlabel(r"$(\mathcal{N}-\langle\mathcal{N}\rangle)/\sigma_\mathrm{lin}$")
    a.set_ylabel("probability density")
    a.legend(loc="upper right", fontsize=7)
    a.set_title(r"(a) $\sigma=0.01$", fontsize=9, loc="left")
    b.axhline(1.0, **cz.GUIDE)
    b.set_xscale("log")
    b.set_xlim(0.005, 2.0)
    b.set_ylim(0.9, 1.55)
    b.set_xlabel(r"coarse-graining parameter $\sigma$")
    b.set_ylabel(r"$\mathrm{var}\,\mathcal{N}\,/\,\sigma_\mathrm{lin}^2$")
    b.legend(loc="upper left", fontsize=7)
    b.set_title("(b) variance", fontsize=9, loc="left")
    cz.save(fig, os.path.join(out, "fig_deltan"))


if __name__ == "__main__":
    main()
