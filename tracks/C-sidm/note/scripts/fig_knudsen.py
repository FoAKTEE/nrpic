"""Figure: the Knudsen number of real cores against what the planned scan covers.

(a) central Knudsen number Kn_c = lambda_c/H_c of the near-threshold models scaled to a
core mass M, for sigma/m = 5 cm^2/g (band over the 13 models) and 1-100 cm^2/g (band for
the King threshold model), against the planned scan Kn_c = 0.3-100; (b) the conversion
constant K = sigma_tilde * Kn_c of the 13 particle models against their central redshift.
Kn_c = K * c_M * (M/M_sun) / (sigma/m), c_M = cgs_per_code_at_1Msun (run xchk, X4).
Reads runs xchk (X4), models (index.json), times (scaled F21 models, cross-check only).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as cm  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_knudsen"
SCAN = (0.3, 100.0)            # planned Kn_c range (stage/G0/REPORT.md section 3, a design choice)
M_SEED_FLUID = 200.0           # horizon mass of the fluid model, 2601.17117 SIDM_MS.tex:476
M_SEED_J1205 = 1.9e9           # seed of the J1205-0000 benchmark, 2108.11967 main.tex:349


def main():
    out = cm.out_dir("figures")
    x4 = cm.load_json("xchk", "crosscheck.json")["X4"]
    idx = cm.load_json("models", "index.json")
    zc = {r["stem"].split("_stratified")[0]: r["Zc"] for r in idx["models"]}
    cM = x4["cgs_per_code_at_1Msun"]
    Ks = np.array([m["Kn_sigma_lead"] for m in x4["models"]])
    Kthr = x4["Kn_sigma_lead_scope_solver"]

    M = np.logspace(0, 10, 50)
    cz.use_style()
    fig = plt.figure(figsize=(7.0, 2.7))
    axa = fig.add_axes([0.10, 0.17, 0.49, 0.75])
    axb = fig.add_axes([0.70, 0.17, 0.285, 0.75])

    kn = lambda K, s: K * cM * M / s          # noqa: E731
    axa.fill_between(M, kn(Kthr, 100.0), kn(Kthr, 1.0), color=cz.PAL["blue"], alpha=0.18,
                     lw=0, label=r"King threshold, $\sigma/m=1$-$100\,$cm$^2$/g")
    axa.fill_between(M, kn(Ks.min(), 5.0), kn(Ks.max(), 5.0), color=cz.PAL["blue"], alpha=0.6,
                     lw=0, label=r"13 models, $\sigma/m=5\,$cm$^2$/g")
    axa.axhspan(*SCAN, color=cz.PAL["red"], alpha=0.25, lw=0, label="planned scan")
    for Ms in (M_SEED_FLUID, M_SEED_J1205):
        axa.axvline(Ms, **cz.GUIDE, alpha=0.6)
    axa.text(M_SEED_FLUID * 1.4, 3e-5, "fluid-model\nseed", fontsize=7.5, va="center")
    axa.text(M_SEED_J1205 / 1.4, 3e-5, "quasar\nseed", fontsize=7.5, va="center", ha="right")
    axa.set_xscale("log")
    axa.set_yscale("log")
    axa.set_xlim(1, 1e10)
    axa.set_ylim(1e-24, 1e4)
    axa.set_yticks(10.0 ** np.arange(-24, 5, 4))
    axa.set_xlabel(r"core mass $M/M_\odot$")
    axa.set_ylabel(r"central Knudsen number $\mathrm{Kn}_c$")
    axa.legend(loc="center", bbox_to_anchor=(0.52, 0.53), fontsize=7.5, handlelength=1.6)
    axa.text(0.03, 0.92, "(a)", transform=axa.transAxes, fontsize=9)

    styles = {"king": ("o", cz.PAL["green"], "King"),
              "poly05": ("s", cz.PAL["orange"], "polytrope"),
              "arshell": ("^", cz.PAL["blue"], "shell")}
    for fam, (mk, col, lab) in styles.items():
        rows = [m for m in x4["models"] if m["tag"].startswith(fam)]
        axb.plot([zc[m["tag"]] for m in rows], [m["Kn_sigma_lead"] for m in rows], mk,
                 ms=4.5, color=col, mfc="none", mew=1.0, label=lab)
    axb.set_xlabel(r"central redshift $z_c$")
    axb.set_ylabel(r"$K=\tilde\sigma\,\mathrm{Kn}_c$")
    axb.set_ylim(140, 215)
    axb.legend(loc="upper right", fontsize=7.5, handlelength=1.0)
    axb.text(0.05, 0.92, "(b)", transform=axb.transAxes, fontsize=9)

    cz.save(fig, os.path.join(out, STEM))
    cm.report_checks(STEM)
    for Ms in (M_SEED_FLUID, M_SEED_J1205):
        lo, hi = Ks.min() * cM * Ms / 5.0, Ks.max() * cM * Ms / 5.0
        print(f"{STEM}: M = {Ms:.3g} Msun, sigma/m = 5: Kn_c = {lo:.3e} .. {hi:.3e} (13 models)")
    print(f"{STEM}: K threshold King = {Kthr:.4f}; K range {Ks.min():.4f} .. {Ks.max():.4f}; "
          f"c_M = {cM:.6e}")


if __name__ == "__main__":
    main()
