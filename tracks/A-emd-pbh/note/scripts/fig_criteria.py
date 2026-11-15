"""Thresholds of the analytic criteria against ellipticity (note v0, Fig. criteria).

Reads only the registered criteria scan, run A-emd-pbh-20261115-120425-80492f8,
scan_summary.json: the threshold in the linear central contrast at horizon entry of six
criteria at e = 0, 0.1, 0.2 (p = 0, rms contrast sigma_H = 0.01 on the scale, matter era
lasting until a_end/a_H = 100), and the particle threshold of arXiv:2609.14218 at e = 0.2
in the same measure (12 mu / 5 with mu = 0.045, MDPBH.tex:1101-1103, 907-908).
A criterion whose threshold is zero (the hoop criteria at e = 0) is drawn at the lower edge.
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from czstyle import use_style, save, PAL, PAL2  # noqa: E402
import common  # noqa: E402

STEM = "fig_criteria"
E = np.array([0.0, 0.1, 0.2])
STYLE = {   # key of scan_summary -> (label, colour, marker)
    "R1 hoop ball (1609.01588)": ("hoop, ball", "k", "o"),
    "R2 hoop peak (2508.10070)": ("hoop, peak", "0.45", "s"),
    "R9 top hat (2507.18312)": ("profile", PAL["blue"], "D"),
    "R8 dispersion (2211.13950)": ("dispersion", PAL["green"], "^"),
    "R3 Kerr bound (1707.03595)": ("spin", PAL["orange"], "v"),
    "R4 duration (1707.03595)": ("duration", PAL2["sky"], "x"),
}
YMIN = 5e-3


def main():
    out = common.out_dir("figures")
    d = common.load_json("criteria_scan", "scan_summary.json")
    th = d["thresholds_sigmaH_0.01"]
    assert d["thresholds_columns"].startswith("values at e = 0, 0.1, 0.2")
    part = d["particle_2609_delta_at_e0.2"]

    use_style()
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    fig.subplots_adjust(left=0.19, right=0.72, bottom=0.16, top=0.97)
    for k, (lab, col, mk) in STYLE.items():
        y = np.array(th[k], dtype=float)
        pos = y > 0
        ax.plot(E[pos], y[pos], color=col, marker=mk, ms=4.5, lw=1.2, clip_on=False, zorder=3)
        ax.text(0.207, y[-1], lab, color=col, fontsize=8, va="center", ha="left")
        for xi, yi in zip(E, y):
            if yi <= 0:   # zero threshold: arrow onto the lower edge
                ax.annotate("", xy=(xi, YMIN), xytext=(xi, YMIN * 2.2),
                            arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
    ax.plot([0.2], [part], ls="none", marker="*", ms=10, color=PAL["red"], zorder=4, clip_on=False)
    ax.text(0.19, part, "particles (Yoo et al.)", color=PAL["red"], fontsize=8,
            va="center", ha="right")
    ax.set_yscale("log")
    ax.set_ylim(YMIN, 3.0)
    ax.set_xlim(-0.01, 0.2)
    ax.set_xticks(E)
    ax.set_xlabel(r"ellipticity $e$ ($p=0$)")
    ax.set_ylabel(r"threshold central contrast $\delta_c$")
    save(fig, os.path.join(out, STEM))
    plt.close(fig)
    common.report_checks(STEM)
    print(f"{STEM}: at e = 0.2 " + "; ".join(f"{STYLE[k][0]} {th[k][2]:.3g}" for k in STYLE)
          + f"; particles {part:.3g}; hoop ball / particles = {th['R1 hoop ball (1609.01588)'][2] / part:.1f}")


if __name__ == "__main__":
    main()
