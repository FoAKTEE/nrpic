"""Figure: what the two baselines predict for the first passages (q = 4 and q = 10).

Reads passage_curves.npz and passage_summary.json of this package's analysis run N1
(F-20261115-174648-25514db): from the start states of the three-black-hole inputs, the
distances of the two members from the heavy black hole in the full Newtonian problem, in
Newton with the black hole fixed and in the geodesic baseline (black hole fixed), and the
energy of the member that full Newton ejects (two-body with M; against the barycentre of M
and the captured member). The end times of the planned runs are read from the inputs the
run recorded. Writes fig_passage.{pdf,png} and the numbers.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_passage"
BLUE, RED = cz.PAL["blue"], cz.PAL["red"]


def tlim(rel):
    for line in open(os.path.join(C.TRACK, rel)):
        s = line.split("#")[0].strip()
        if s.startswith("tlim"):
            return float(s.split("=")[1])
    raise SystemExit(f"no tlim in {rel}")


def main():
    out = C.out_dir("figures")
    Z = np.load(C.run_file("n1", "passage_curves.npz"))
    S = C.load_json("n1", "passage_summary.json")
    man = C.manifest("n1")
    recorded = {i["path"]: i["sha256"] for i in man["inputs"]}
    cz.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 4.9), gridspec_kw=dict(width_ratios=[1.25, 1]))
    fig.subplots_adjust(left=0.075, right=0.965, bottom=0.09, top=0.985, wspace=0.24,
                        hspace=0.08)
    nums = {"run": C.RUNS["n1"]}
    for row, key, lab in ((0, "q4", r"$q=4$"), (1, "q10", r"$q=10$")):
        rel = "tracks/F-hills/" + S[key]["input"]
        if rel not in recorded or C._sha256(os.path.join(C.WT, rel)) != recorded[rel]:
            raise SystemExit(f"input {rel} differs from the one run N1 recorded")
        T = tlim(S[key]["input"])
        a = axs[row, 0]
        for law, ls, name in (("newton", "-", "Newton"), ("newton_fixed", ":", "Newton, fixed"),
                              ("hrna", "--", "geodesic")):
            t = Z[f"{key}_{law}_t"]
            for i, col in ((1, BLUE), (2, RED)):
                a.plot(t, Z[f"{key}_{law}_r{i}"], ls=ls, color=col, lw=1.2,
                       label=(fr"$m_{i}$, {name}" if row == 0 else None))
        a.axhline(4.0, **cz.MASK_LINE)
        a.axvline(T, color="k", lw=0.8, ls="-.")
        a.text(T - 4, 230, "end of run", fontsize=7, ha="right", va="center")
        a.set_yscale("log")
        a.set_xlim(0, 300)
        a.set_ylim(2, 400)
        a.set_ylabel(r"distance from $M$ $[M]$")
        a.text(0.03, 0.05, lab, transform=a.transAxes, ha="left", va="bottom")
        b = axs[row, 1]
        t = Z[f"{key}_newton_t"]
        ie = S[key]["newton"]["ejected"]
        b.plot(t, Z[f"{key}_newton_E{ie}_M"], color=BLUE, lw=0.9,
               label="two-body with $M$" if row == 0 else None)
        b.plot(t, Z[f"{key}_newton_E{ie}_bc"], color="k", lw=1.5,
               label="against barycentre" if row == 0 else None)
        b.set_xlim(0, 1500)
        b.set_xticks([0, 500, 1000, 1500])
        b.set_ylim(-0.5, 2.5)
        b.set_ylabel(r"energy of $m_%d$ [unit]" % ie)
        b.text(0.97, 0.05, lab, transform=b.transAxes, ha="right", va="bottom")
        if row == 0:
            a.tick_params(labelbottom=False)
            b.tick_params(labelbottom=False)
        nums[key] = {"tlim": T, "newton": S[key]["newton"], "hrna": S[key]["hrna"],
                     "newton_fixed": S[key]["newton_fixed"], "unit_E": S[key]["unit_E"],
                     "cm_rp": S[key]["cm_rp"], "a_b": S[key]["a_b"], "r0": S[key]["r0"]}
    axs[1, 0].set_xlabel(r"$t\,[M]$")
    axs[1, 1].set_xlabel(r"$t\,[M]$")
    axs[0, 0].legend(frameon=False, loc="upper left", fontsize=6.3, ncol=2, handlelength=2.0,
                     columnspacing=0.8)
    axs[0, 1].legend(frameon=False, loc="upper right", fontsize=7)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
