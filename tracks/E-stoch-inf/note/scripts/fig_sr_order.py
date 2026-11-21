"""Figure: temporal order of the slow-roll reproduction (criterion A6).

Three processor runs at 32^3 (k_max = 8 dk, the same Gaussian numbers) with Courant factors
0.25, 0.125 and 0.0625, dumped at the same times.
(a) largest relative difference between two Courant factors against the e-folds since the
    start: R^NR over all modes inside the window, the perturbation of the conformal factor
    chi and its box mean.
(b) order log2[Delta(0.25, 0.125) / Delta(0.125, 0.0625)] of these and of the perturbations
    of phi and K; shaded: the accepted band 4 +- 0.5.
(c) deviation D_n of every mode from the linear solution at the last dump for the three
    Courant factors: the upper shells do not move when the step is halved, so their
    deviation is spatial.

Inputs: the committed ladder/results/a6/a6.json and a6_modes.npz (read from the run
directory by absolute path; the JSON lacks the wave numbers of its per-mode list) of the
analysis E-20261119-145230-ff0dff2 of the runs E-20261119-142317-c851f27, each checked
against the sha256 its run recorded.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402

RUN = "E-20261119-145230-ff0dff2"
A6 = "ladder/results/a6/a6.json"
PAIRS = {"T25-T12": (cz.PAL["blue"], r"$\theta=0.25$ vs $0.125$"),
         "T12-T06": (cz.PAL["red"], r"$\theta=0.125$ vs $0.0625$")}
QTY = {"R_all": ("o-", r"$\mathcal{R}^\mathrm{NR}_n$"), "chi_pert": ("s--", r"$\delta\chi$"),
       "chi_mean": ("d-.", r"$\langle\chi\rangle$")}
ORD = {"R_all": ("o-", cz.PAL["blue"], r"$\mathcal{R}^\mathrm{NR}_n$"),
       "phi_pert": ("^-", cz.PAL["green"], r"$\delta\phi$"),
       "chi_pert": ("s--", cz.PAL["red"], r"$\delta\chi$"),
       "K_pert": ("v:", cz.PAL["orange"], r"$\delta K$"),
       "chi_mean": ("d-.", "k", r"$\langle\chi\rangle$")}
TCOL = {"T25": cz.PAL["yellow"], "T12": cz.PAL["green"], "T06": cz.PAL["blue"]}
TLAB = {"T25": r"$\theta=0.25$", "T12": r"$\theta=0.125$", "T06": r"$\theta=0.0625$"}


def main():
    out = C.out_dir(C.FIGDIR)
    os.makedirs(out, exist_ok=True)
    cz.use_style()
    s = C.committed_json(A6)
    zm = np.load(C.path(RUN, "a6_modes.npz"))
    x = np.array(s["efolds"])
    fig = plt.figure(figsize=(7.0, 2.75))
    a = cz.inch_axes(fig, 0.66, 0.50, 1.75, 2.10)
    b = cz.inch_axes(fig, 2.98, 0.50, 1.65, 2.10)
    c = cz.inch_axes(fig, 5.22, 0.50, 1.65, 2.10)
    for pair, (col, plab) in PAIRS.items():
        for q, (ls, qlab) in QTY.items():
            y = np.array(s["diff"][pair][q], dtype=float)
            a.plot(x[1:], y[1:], ls, ms=2.2, lw=1.0, color=col)
    for q, (ls, qlab) in QTY.items():
        a.plot([], [], ls, ms=2.2, lw=1.0, color="0.3", label=qlab)
    a.set_yscale("log")
    a.set_ylim(1e-9, 1e-2)
    a.set_xlim(0.2, 4.6)
    a.set_xlabel(r"$N-N_*$")
    a.set_ylabel("largest relative difference")
    a.legend(frameon=False, fontsize=7, loc="lower right", handlelength=2.0)
    a.text(0.4, 3e-3, r"$\theta=0.25$ vs $0.125$", fontsize=7, color=PAIRS["T25-T12"][0])
    a.text(0.4, 1.2e-3, r"$\theta=0.125$ vs $0.0625$", fontsize=7, color=PAIRS["T12-T06"][0])
    a.text(0.05, 0.05, "(a)", transform=a.transAxes, fontsize=9)
    b.axhspan(3.5, 4.5, color="0.88", lw=0)
    b.axhline(4.0, **cz.GUIDE)
    for q, (ls, col, lab) in ORD.items():
        y = np.array(s["orders"][q], dtype=float)
        b.plot(x[1:], y[1:], ls, ms=2.2, lw=1.0, color=col, label=lab)
    b.set_ylim(2.0, 6.0)
    b.set_xlim(0.2, 4.6)
    b.set_xlabel(r"$N-N_*$")
    b.set_ylabel("order in the time step")
    b.legend(frameon=False, fontsize=7, loc="upper right", ncol=2, handlelength=1.8, columnspacing=0.8)
    b.text(0.05, 0.05, "(b)", transform=b.transAxes, fontsize=9)
    k = np.sqrt(zm["n2"])
    for t in ("T25", "T12", "T06"):
        dl = zm[f"D_last_{t}"]
        c.plot(k, dl, ".", ms=2.0, color=TCOL[t], label=TLAB[t])
        if np.abs(dl - np.array(s["D"][t]["last_per_mode"], dtype=float)).max() != 0.0:
            raise SystemExit(f"fig_sr_order: a6_modes.npz differs from a6.json for {t}")
    c.set_xscale("log")
    c.set_yscale("log")
    c.set_xticks([1, 2, 4, 8])
    c.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    c.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    c.set_ylim(1e-8, 1e-1)
    c.set_xlabel(r"$k/k_{\sigma*}$")
    c.set_ylabel(r"$D_n$ at the last dump")
    c.legend(frameon=False, fontsize=7, loc="upper left", handlelength=1.0, markerscale=2.0)
    c.text(0.95, 0.05, "(c)", transform=c.transAxes, ha="right", fontsize=9)
    cz.save(fig, os.path.join(out, "fig_sr_order"))
    lo = min(min(v["orders"]) for k_, v in s["A6"].items() if k_ in ("R_all", "R_top", "R_low",
                                                                    "phi_pert", "chi_pert",
                                                                    "K_pert", "chi_mean"))
    hi = max(max(v["orders"]) for k_, v in s["A6"].items() if k_ in ("R_all", "R_top", "R_low",
                                                                    "phi_pert", "chi_pert",
                                                                    "K_pert", "chi_mean"))
    top = [np.max(zm[f"D_last_{t}"][zm["n2"] >= 49]) for t in ("T25", "T12", "T06")]
    print(f"fig_sr_order: A6 orders {lo:.3f}-{hi:.3f}; top shells (|n|^2 >= 49) max D_n "
          + ", ".join(f"{v:.3e}" for v in top))


if __name__ == "__main__":
    main()
