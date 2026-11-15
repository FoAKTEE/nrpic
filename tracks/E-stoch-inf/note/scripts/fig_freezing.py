"""Figure: freezing of super-horizon modes with and without metric perturbations, the
reference for the freezing criterion of the reproduction.

Reads quadratic.npz and inflection.npz of run E-stoch-inf-20261115-122806-ef0d039: per
lattice mode k (k = dk ... 64 dk) the Mukhanov-Sasaki solution R_ms (metric perturbations
included) and the solution R_def of the deformed equation of arXiv:2606.14853 (metric
perturbations dropped, as on an FLRW lattice). Power Delta = k^3 |R|^2/(2 pi^2).
(a) Slow roll: power of four modes divided by its value four e-folds after the mode
crossed the window scale, against e-folds since crossing; the dotted black line is the
super-horizon decay of the deformed equation, -4 eps1 per e-fold with eps1 integrated
along the background from N* + 4 (mode k = dk).
(b) Ratio deformed/full of the power at the end of the run, N_f, for every mode.
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
SHOW = (1.0, 4.0, 16.0, 64.0)


def power(d, key):
    k = d["k"][:, None]
    return k ** 3 * np.abs(d[key]) ** 2 / (2 * np.pi ** 2)


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    fig = plt.figure(figsize=(3.4, 4.8))
    a = cz.inch_axes(fig, 0.72, 2.85, 2.55, 1.72)
    b = cz.inch_axes(fig, 0.72, 0.48, 2.55, 1.55)
    q = np.load(C.path(RUN, "quadratic.npz"))
    N = q["N"]
    kd = q["k"] / float(q["dk"])
    Pms, Pdef = power(q, "R_ms"), power(q, "R_def")
    styles = ("-", "--", "-.", ":")
    for kk, ls in zip(SHOW, styles):
        i = int(np.argmin(np.abs(kd - kk)))
        x = N - q["Ncross"][i]
        ok = np.isfinite(Pms[i]) & (x >= 0)
        ref_ms = np.interp(4.0, x[ok], Pms[i][ok])
        ref_def = np.interp(4.0, x[ok], Pdef[i][ok])
        lab = rf"$k={kk:g}\,\Delta k$"
        a.plot(x[ok], Pms[i][ok] / ref_ms, color=cz.PAL["blue"], ls=ls, lw=1.2, label=lab)
        a.plot(x[ok], Pdef[i][ok] / ref_def, color=cz.PAL["red"], ls=ls, lw=1.2)
    # -4 eps1 per e-fold, integrated along the background from N* + 4 (mode k = dk)
    n0 = float(q["Nstar"])
    xs = np.linspace(4.0, 8.0, 81)
    ns = np.linspace(n0 + 4.0, n0 + 8.0, 4001)
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (np.interp(ns[1:], N, q["eps1"])
                                                  + np.interp(ns[:-1], N, q["eps1"])) * np.diff(ns))])
    a.plot(xs, np.exp(-4.0 * np.interp(n0 + xs, ns, cum)), color="k", lw=1.0, ls=(0, (1.5, 1.5)))
    a.set_xlim(0, 8)
    a.set_ylim(0.78, 1.32)
    a.axvline(4.0, **cz.MASK_LINE)
    a.set_xlabel(r"$N-N_k$")
    a.set_ylabel(r"$\Delta_\mathcal{R}(N)\,/\,\Delta_\mathcal{R}(N_k+4)$")
    a.legend(loc="upper right", fontsize=7, handlelength=2.2)
    a.text(0.4, 0.86, "full (blue)\ndeformed (red)", fontsize=7.5, va="center")
    a.set_title("(a) slow roll", fontsize=9, loc="left")

    for case, col, mk in (("quadratic", cz.PAL["blue"], "o"), ("inflection", cz.PAL["red"], "s")):
        d = np.load(C.path(RUN, f"{case}.npz"))
        kk = d["k"] / float(d["dk"])
        r = power(d, "R_def")[:, -1] / power(d, "R_ms")[:, -1]
        lab = "slow roll" if case == "quadratic" else "ultra-slow roll"
        b.loglog(kk, r, mk, color=col, ms=3.2, label=lab, ls="-", lw=0.8)
    b.axhline(1.0, **cz.GUIDE)
    b.set_xlabel(r"$k/\Delta k$")
    b.set_ylabel(r"$\Delta^\mathrm{def}_\mathcal{R}/\Delta_\mathcal{R}$ at $N_f$")
    b.legend(loc="upper right", fontsize=7.5)
    b.set_ylim(0.5, 15)
    b.set_title("(b) end of the run", fontsize=9, loc="left")
    cz.save(fig, os.path.join(out, "fig_freezing"))


if __name__ == "__main__":
    main()
