"""Figure: background of the two test cases (slow roll in the quadratic potential, ultra-slow
roll at the inflection point), from the reference run of the specification package.

Reads quadratic.npz and inflection.npz of run E-stoch-inf-20261115-122806-ef0d039
(checksums verified against its manifest). Shows the first and second slow-roll parameters
(eps2 = -d ln eps1/dN, the convention of the source papers) against the e-folds since the
start of the simulation, the interval in which the lattice modes enter the noise window,
and the ultra-slow-roll interval (eps2 > 3).
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

RUN = "E-stoch-inf-20261115-122806-ef0d039"
NF = {"quadratic": 8.0, "inflection": 10.0}     # N_f - N* of the specification (SCOPE.md 2)


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    fig = plt.figure(figsize=(7.0, 3.5))
    W, Hh = 2.7, 1.25
    axes = {}
    for j, case in enumerate(("quadratic", "inflection")):
        x0 = 0.78 + j * (W + 0.74)
        axes[case] = (cz.inch_axes(fig, x0, 1.82, W, Hh), cz.inch_axes(fig, x0, 0.52, W, Hh))
    for case, (a1, a2) in axes.items():
        d = np.load(C.path(RUN, f"{case}.npz"))
        cN = d["N"] - float(d["Nstar"])
        sel = (cN >= -0.3) & (cN <= NF[case] + 1e-9)
        x, e1, e2 = cN[sel], d["eps1"][sel], d["eps2"][sel]
        nc = d["Ncross"] - float(d["Nstar"])
        for a in (a1, a2):
            a.axvspan(nc.min(), nc.max(), color=cz.PAL["blue"], alpha=0.12, lw=0)
            if case == "inflection":
                usr = x[e2 > 3.0]
                a.axvspan(usr.min(), usr.max(), color=cz.PAL["red"], alpha=0.12, lw=0)
            a.set_xlim(-0.3, NF[case])
        a1.semilogy(x, e1, color="k")
        a2.plot(x, e2, color="k")
        a2.axhline(0.0, **cz.GUIDE) if case == "quadratic" else a2.axhline(3.0, **cz.GUIDE)
        a1.set_ylabel(r"$\epsilon_1$")
        a2.set_ylabel(r"$\epsilon_2$")
        a2.set_xlabel(r"$N-N_*$")
        a1.tick_params(labelbottom=False)
        title = "slow roll, quadratic" if case == "quadratic" else "ultra-slow roll, inflection"
        a1.set_title(title, fontsize=10)
        if case == "quadratic":
            a1.set_ylim(9e-3, 1.5e-2)
            a1.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            a1.set_yticks([1e-2, 1.2e-2, 1.4e-2])
            a1.set_yticklabels(["0.010", "0.012", "0.014"])
            a2.set_ylim(-0.03, 0.005)
            a1.text(0.5 * (nc.min() + nc.max()), 1.43e-2, "modes enter", ha="center",
                    va="top", fontsize=8, color=cz.PAL["blue"])
        else:
            a1.set_ylim(3e-13, 0.1)
            a2.set_ylim(-1.0, 6.8)
            a1.text(1.25, 1e-8, "modes\nenter", ha="center",
                    va="center", fontsize=8, color=cz.PAL["blue"])
            a1.text(0.5 * (usr.min() + usr.max()), 2e-12, "USR", ha="center", fontsize=8,
                    color=cz.PAL["red"])
    cz.save(fig, os.path.join(out, "fig_background"))


if __name__ == "__main__":
    main()
