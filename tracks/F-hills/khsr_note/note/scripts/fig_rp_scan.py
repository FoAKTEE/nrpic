"""Figure: separation and plunge fractions against pericentre distance, two baselines.

Reads v7_summary.json of the lead's run V7 (F-hills-20261115-145915-71abf93): 180 binary
phases per pericentre, coplanar prograde, start at four tidal radii, for q = 10 (a_b = 3 M)
and q = 4 (a_b = 5 M); full Newtonian three-body problem, Newton with the black hole fixed,
and the geodesic baseline HRNA (black hole fixed). The pericentres of the first passages are
read from N1 (F-20261115-174648-25514db). Writes fig_rp_scan.{pdf,png} and the numbers.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_rp_scan"
BLUE, RED, YEL = cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"]


def main():
    out = C.out_dir("figures")
    v7 = C.load_json("v7", "v7_summary.json")
    n1 = C.load_json("n1", "passage_summary.json")
    cz.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.75), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.83, wspace=0.06)
    nums = {"run": C.RUNS["v7"], "passage_run": C.RUNS["n1"]}
    for ax, key, lab in ((axs[0], "q10", r"$q=10$"), (axs[1], "q4", r"$q=4$")):
        rows = v7[key]
        rp = np.array([r["rp"] for r in rows])
        D = np.array([r["D"] for r in rows])
        f = {
            "newton_full_sep": [r["newton_full"]["separated"] for r in rows],
            "newton_full_in4": [r["newton_full"]["member_below_4M"] for r in rows],
            "newton_fixed_sep": [r["newton"]["separated"] for r in rows],
            "hrna_sep": [r["hrna"]["separated"] for r in rows],
            "hrna_plunge": [r["hrna"]["plunge"] for r in rows],
        }
        ax.plot(rp, f["newton_full_sep"], "-o", color=BLUE, ms=3, label="Newton, separated")
        ax.plot(rp, f["newton_fixed_sep"], ":", color=BLUE, lw=1.2,
                label="Newton, black hole fixed")
        ax.plot(rp, f["newton_full_in4"], "--", color=BLUE, lw=1.2,
                label=r"Newton, a member inside $4M$")
        ax.plot(rp, f["hrna_sep"], "-s", color=RED, ms=3, label="geodesic, separated")
        ax.plot(rp, f["hrna_plunge"], "--", color=RED, lw=1.2,
                label=r"geodesic, a member plunges")
        rp1 = n1[key]["cm_rp"]
        ax.axvline(rp1, **cz.MASK_LINE)
        ax.text(rp1 + 0.12, 0.56, "first\npassage", fontsize=7, color="grey", va="center")
        ax.set_xlabel(r"pericentre $r_p\,[M]$")
        ax.text(0.97, 0.06, lab, transform=ax.transAxes, ha="right", va="bottom")
        ax.set_ylim(-0.03, 1.05)
        ratio = float(np.mean(D / rp))
        sec = ax.secondary_xaxis("top", functions=(lambda x, k=ratio: x * k,
                                                   lambda d, k=ratio: d / k))
        sec.set_xlabel(r"penetration $D=r_p/r_t$", fontsize=9)
        nums[key] = {"rp": rp.tolist(), "D": D.tolist(), "r_t": 1 / ratio,
                     "rp_first_passage": rp1, **{k: list(map(float, v)) for k, v in f.items()}}
    axs[0].set_ylabel("fraction of phases")
    h, l = axs[0].get_legend_handles_labels()
    axs[1].legend(h, l, frameon=False, loc="lower left", fontsize=6.6, handlelength=2.2,
                  bbox_to_anchor=(0.17, 0.07))
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
