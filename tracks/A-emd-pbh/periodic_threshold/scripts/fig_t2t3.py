"""Figure of T2/T3 from the two registered runs (T2a, T3 from the first; T2b, T2c from the
repeat with the corrected data; JOURNAL.md).

    python3 fig_t2t3.py --first DIR --repeat DIR --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", required=True)
    ap.add_argument("--repeat", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r1 = json.load(open(os.path.join(a.first, "t2t3_results.json")))
    r2 = json.load(open(os.path.join(a.repeat, "t2t3_results.json")))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 5.8))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.97, wspace=0.32,
                        hspace=0.38)
    lab = {"T2a_uniform": "uniform", "T2a_smr_adaptive": "static, adaptive cloud",
           "T2a_smr_finest": "static, finest cloud"}
    col = {"T2a_uniform": fs.PAL["blue"], "T2a_smr_adaptive": fs.PAL["red"],
           "T2a_smr_finest": fs.PAL["yellow"]}
    ax = fig.add_subplot(2, 2, 1)
    for n in lab:
        c = r1[n]["cstat"]
        ax.semilogy(c["time"], np.maximum(c["Hr_max"], 1e-17), "o-", color=col[n],
                    label=lab[n])
        ax.semilogy(c["time"], np.maximum(c["Hr_mean"], 1e-17), "--", color=col[n])
    ax.set_xlabel(r"$t$ (conformal), homogeneous universe")
    ax.set_ylabel(r"$H_r$ max (solid), mean (dashed)")
    ax.legend(frameon=False, fontsize=8, loc="center right")
    ax = fig.add_subplot(2, 2, 2)
    for n in lab:
        c = r1[n]["cstat"]
        sp = np.array(c["chi_max"])/np.array(c["chi_min"]) - 1.0
        ax.semilogy(c["time"], np.maximum(sp, 1e-17), "o-", color=col[n])
    ax.axhline(1e-12, **fs.GUIDE)
    ax.set_xlabel(r"$t$ (conformal), homogeneous universe")
    ax.set_ylabel(r"$\chi_{\max}/\chi_{\min} - 1$ (floor $10^{-17}$)")
    ax = fig.add_subplot(2, 2, 3)
    for mu, mk in (("0.5", "-"), ("0.03", "--")):
        for kind, cc in (("uniform", fs.PAL["blue"]), ("smr", fs.PAL["red"])):
            ln = r2[f"T2b_{kind}_mu{mu}"]["line_t0"]
            E = np.array(ln["E"])
            dE = 16*np.pi*np.abs(E - 3/(8*np.pi)).max()
            ax.plot(ln["x"], np.array(ln["H"])/dE, mk, color=cc, lw=1.2,
                    label=f"{'uniform' if kind == 'uniform' else 'static'}, mu = {mu}")
    ax.axvspan(-5, 5, color="0.5", alpha=0.1)
    ax.axvspan(-2.5, 2.5, color="0.5", alpha=0.1)
    ax.set_xlabel(r"$k x$ (line through the peak), $t = 0$")
    ax.set_ylabel(r"$H/(16\pi\,\max|E-\bar E|)$")
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax = fig.add_subplot(2, 2, 4)
    names = ["T3a_outflow", "T3b_periodic", "T3c_periodic_shift"]
    for i, n in enumerate(names):
        m = r1[n]["horizon"][0]["mass"] if r1[n].get("horizon") else np.nan
        if np.isfinite(m):
            ax.plot([i], [m], "o", color=fs.PAL["red"], ms=7)
        else:
            ax.text(i, 0.99155, "not\nfound", ha="center", va="center", fontsize=8,
                    color=fs.PAL["red"])
    ax.axhline(0.991521, label="calibration (docs/TESTLOG.md)", **fs.GUIDE)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["outflow", "periodic", "periodic,\ncentre +32 M"], fontsize=8)
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(0.99145, 0.99160)
    ax.set_ylabel(r"finder mass / $M$, $t = 0$")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fs.save(fig, os.path.join(a.out, "fig_t2t3"))


if __name__ == "__main__":
    main()
