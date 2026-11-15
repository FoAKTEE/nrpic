"""Particle number needed to resolve the spike inside ten horizon radii (r < 20 Gm) with
equal-mass particles drawn from the adiabatically grown DF truncated at E <= E_cut.

For each E_cut: dN/dr = 4 pi r^2 rho(r) / sqrt(1 - 2/r) of the truncated DF (canonical
action, m = 4e6 M_sun, Hernquist M = 1e12 M_sun, a = 20 kpc), the fraction of particles
inside 20 Gm, and the total N for which every one of 8 logarithmic bins between 5 and
20 Gm holds at least 100 (10 % Poisson) or 400 (5 %) particles at any instant.

usage: python3 particle_budget.py --out DIR
"""
import argparse
import json
import shutil
import sys
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from spike_lib import SpikeModel  # noqa
from nrpic import figstyle  # noqa

warnings.simplefilter("ignore", RuntimeWarning)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    sm = SpikeModel(m_sun=4e6)
    res = {"criterion": "8 log bins in 5-20 Gm; min expected count per bin 100 (10 %) or 400 (5 %)"}
    edges = np.logspace(np.log10(5.0), np.log10(20.0), 9)
    rows = []
    curves = {}
    for one_minus in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6):
        ecut = 1.0 - one_minus
        rmax = 2.0 / (1 - ecut * ecut) * 1.02 + 10
        rg = np.unique(np.concatenate([4.0 + np.logspace(-3, np.log10(6.0), 60),
                                       np.logspace(1.0, np.log10(rmax), 160)]))
        rho = sm.rho_rel(rg, "canonical", Eup=ecut, nE=48, nw=32)
        dNdr = 4 * np.pi * rg**2 * rho / np.sqrt(1 - 2 / rg)
        cdf = np.concatenate([[0], np.cumsum(0.5 * (dNdr[1:] + dNdr[:-1]) * np.diff(rg))])
        tot = cdf[-1]
        f20 = np.interp(20.0, rg, cdf) / tot
        pb = np.diff(np.interp(edges, rg, cdf)) / tot
        row = {"E_cut": ecut, "r_apo_max_Gm": float(rmax), "frac_inside_20Gm": float(f20),
               "frac_inside_10Gm": float(np.interp(10.0, rg, cdf) / tot),
               "min_bin_fraction_5-20Gm": float(pb.min()),
               "N_total_10pc": float(100 / pb.min()), "N_total_5pc": float(400 / pb.min()),
               "rest_mass_inside_20Gm_over_total": float(f20)}
        rows.append(row)
        curves[one_minus] = (rg, cdf / tot)
    res["rows"] = rows
    # deposit noise (self-gravitating run): relative L2 noise 0.24-0.28 of the deposited
    # energy density at 1.1 particles per occupied cell, falling as N^-1/2
    # (docs/results_cluster_test.md, section 2(d)); cells of dx = 0.25 Gm inside 20 Gm:
    ncell = 4.0 / 3.0 * np.pi * 20.0**3 / 0.25**3
    res["deposit_noise_estimate"] = {
        "cells_dx0.25_inside_20Gm": ncell,
        "particles_inside_20Gm_for_5pc_L2_noise": float(ncell * 1.1 * (0.26 / 0.05) ** 2),
        "source": "docs/results_cluster_test.md 2(d): s_10000 = 0.24-0.28 at 1.1 particles per occupied cell, N^-1/2"}
    (out / "budget.json").write_text(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.15, wspace=0.28)
    a = axs[0]
    for (k, (rg, c)), col in zip(curves.items(), figstyle.SERIES):
        a.loglog(rg, c, color=col, label=rf"$1-E_{{\rm cut}} = 10^{{{np.log10(k):.0f}}}$")
    a.axvline(20.0, **figstyle.MASK_LINE)
    a.set_xlabel(r"$r/Gm$"); a.set_ylabel(r"$N(<r)/N$")
    a.set_ylim(1e-6, 1.2); a.legend(loc="lower right", fontsize=7)
    b = axs[1]
    x = [r["r_apo_max_Gm"] for r in rows]
    b.loglog(x, [r["N_total_10pc"] for r in rows], "o-", color=figstyle.PAL["red"],
             label="10 % per bin (100 per bin)")
    b.loglog(x, [r["N_total_5pc"] for r in rows], "s--", color=figstyle.PAL["blue"],
             label="5 % per bin (400 per bin)")
    b.set_xlabel(r"largest apocentre of the sampled DF [$Gm$]")
    b.set_ylabel(r"total $N$ (equal masses)")
    b.legend(loc="upper left", fontsize=7)
    for ext in ("pdf", "png"):
        fig.savefig(out / f"particle_budget.{ext}")
    plt.close(fig)
    shutil.copy(out / "particle_budget.png", HERE / "figs" / "particle_budget.png")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
