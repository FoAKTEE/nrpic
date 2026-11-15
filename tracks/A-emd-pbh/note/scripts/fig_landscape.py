"""Amplitude-ellipticity plane of the S1 threshold problem (note v0, Fig. landscape).

Reads only registered outputs:
  scope run A-20261115-130252-7877b7a, scope/scope_numbers.json
    T1: Zel'dovich-hoop line h-hat(e, p = 0) reproduced from arXiv:2609.14218 (MDPBH.tex:918)
        and the values read by eye from that paper's figure;
    T2: amplitudes whose top-hat collapse time of the compaction shell is t_end (100-1000 t_H);
    T3: largest mu the expanding ball holds (mean contrast in r_m at most 0.3 at the start).
The two outcomes of arXiv:2609.14218 drawn as brackets are statements of that paper, with
their locators (kb-data/raw/arxiv/2609.14218/v1/src/MDPBH.tex):
  particles, e = 0.2: horizon for mu >= 0.05, none for mu <= 0.045 (lines 1101-1103);
  LTB, e = 0: black hole for mu = 0.33, globally naked for mu = 0.32 (lines 765-768).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from czstyle import use_style, save, PAL  # noqa: E402
import common  # noqa: E402

STEM = "fig_landscape"
PARTICLE_BRACKET_E02 = (0.045, 0.05)   # MDPBH.tex:1101-1103
LTB_BRACKET_E0 = (0.32, 0.33)          # MDPBH.tex:765-768


def main():
    out = common.out_dir("figures")
    d = common.load_json("scope", "scope/scope_numbers.json")
    e = np.array(d["T1"]["readoff_e"])
    hhat = np.array(d["T1"]["h_hat_e_p0"])
    read = np.array(d["T1"]["readoff_mu"])
    T2 = d["T2"]
    cap = {q: [r for r in d["T3"][q] if abs(r["RbH_i"] - 0.9) < 1e-12][0]["mu_max_mean03"]
           for q in ("q2", "q3")}

    use_style()
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    fig.subplots_adjust(left=0.19, right=0.75, bottom=0.15, top=0.97)
    ax.fill_between([0, 0.32], 1e-3, cap["q2"], color=PAL["green"], alpha=0.10, lw=0)
    ax.fill_between([0, 0.32], 1e-3, cap["q3"], color=PAL["green"], alpha=0.18, lw=0)
    # labels inside each band, between its top and the duration line below it
    ax.text(0.012, np.sqrt(cap["q2"] * T2["mu_fd_250"]), r"ball, $R_b=2r_m$",
            color=PAL["green"], fontsize=8, va="center")
    ax.text(0.012, np.sqrt(cap["q3"] * T2["mu_fd_1000"]), r"ball, $R_b=3r_m$",
            color=PAL["green"], fontsize=8, va="center")
    for tend, key, ls in ((250, "mu_fd_250", "--"), (1000, "mu_fd_1000", ":")):
        ax.axhline(T2[key], color="k", lw=1.0, ls=ls)
        ax.text(0.325, T2[key], rf"$t_{{\rm end}}={tend}\,t_H$", fontsize=8, va="center", ha="left")
    ax.plot(e, hhat, color="k", lw=1.5)
    ax.plot(e, read, ls="none", marker="o", mfc="none", mec="k", ms=4.5)
    ax.text(0.30, hhat[-1] * 1.25, "hoop line", fontsize=8, ha="right", va="bottom")
    lo, hi = PARTICLE_BRACKET_E02
    ax.errorbar([0.2], [np.sqrt(lo * hi)], yerr=[[np.sqrt(lo * hi) - lo], [hi - np.sqrt(lo * hi)]],
                color=PAL["red"], lw=2.0, capsize=3.5, capthick=1.5, ls="none")
    ax.text(0.2, hi * 1.12, "particles", color=PAL["red"], fontsize=8, ha="center", va="bottom")
    lo, hi = LTB_BRACKET_E0
    ax.errorbar([0.0], [np.sqrt(lo * hi)], yerr=[[np.sqrt(lo * hi) - lo], [hi - np.sqrt(lo * hi)]],
                color=PAL["blue"], lw=2.0, capsize=3.5, capthick=1.5, ls="none", clip_on=False)
    ax.text(0.012, np.sqrt(lo * hi), "LTB", color=PAL["blue"], fontsize=8, va="center")
    ax.set_xlim(0, 0.32)
    ax.set_ylim(5e-3, 1.0)
    ax.set_yscale("log")
    ax.set_xlabel(r"ellipticity $e$ ($p=0$)")
    ax.set_ylabel(r"amplitude $\mu$")
    save(fig, os.path.join(out, STEM))
    plt.close(fig)
    common.report_checks(STEM)
    print(f"{STEM}: h_hat(0.2,0) = {d['T1']['h_hat_0.2_0']:.3f}; mu_fd(250) = {T2['mu_fd_250']:.3f}; "
          f"mu_fd(1000) = {T2['mu_fd_1000']:.3f}; ball capacity q=3 {cap['q3']:.3f}, q=2 {cap['q2']:.3f}")


if __name__ == "__main__":
    main()
