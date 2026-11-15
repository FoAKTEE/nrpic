"""Figure: mesh size along the passage and card time of one passage.

Reads mesh_count_b.json of the three_punctures runs that built the MeshBlock trees of the
Hills meshes at the Newtonian positions every 10 M along the passage (q = 10:
F-hills-20261115-131348-634fb86; q = 4: F-hills-20261115-131933-907e5fe), and counts.txt
of nr_first E1 (F-20261115-173543-29e87e8: trees of the q = 4 input at t = 0 with the
release executable, at three resolutions). Card time = MeshBlock-cycles / measured rate
(median, with the slow and fast rates of the same file). The card memory limit (about 3000
MeshBlock slots) is core's estimate, coord/INTERFACES/multi_puncture.md:229-230; the
allotment to the next gate (50 card-hours) is decision 0014. Writes fig_cost.{pdf,png}.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_cost"
BLUE, RED, YEL = cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"]
SLOTS = 3000          # coord/INTERFACES/multi_puncture.md:229-230 ("about 3000")
ALLOT = 50.0          # coord/DECISIONS/0014-budgets-after-wave-1.md (F 50 to the next gate)


def read_counts(path):
    out = {}
    for line in open(path):
        parts = dict(p.split("=") for p in line.split()[1:] if "=" in p)
        if line.startswith("q4_three_bh"):
            out[int(parts["num_levels"])] = int(parts["t0_tree"])
    return out


def main():
    out = C.out_dir("figures")
    m10 = C.load_json("mesh10", "mesh_count_b.json")
    m4 = C.load_json("mesh4", "mesh_count_b.json")
    e1 = read_counts(C.run_file("e1", "counts.txt"))
    cz.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw=dict(width_ratios=[1.6, 1]))
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.17, top=0.96, wspace=0.28)
    a = axs[0]
    nums = {"runs": [C.RUNS["mesh10"], C.RUNS["mesh4"], C.RUNS["e1"]], "slots": SLOTS,
            "allotment": ALLOT, "e1_t0": e1}
    sel = [("q10", m10, "D205_m8_r1.8", RED, "-", r"$q=10$, $m/8$"),
           ("q10", m10, "D205_m16_r1.8", RED, "--", r"$q=10$, $m/16$"),
           ("q4", m4, "D256q4_m8_r1.8", BLUE, "-", r"$q=4$, $m/8$"),
           ("q4", m4, "D256q4_m16_r1.8", BLUE, "--", r"$q=4$, $m/16$")]
    for q, src, case, col, ls, lab in sel:
        tr = src["tracks"][case]
        a.plot(tr["t"], tr["n"], color=col, ls=ls, lw=1.3, label=lab)
        nums[case] = {k: tr[k] for k in ("n_max", "n_mean", "span", "cycles", "card_hours")}
        nums[case]["n_start"] = tr["n"][0]
        nums[case]["t_start"] = tr["t"][0]
    t4 = m4["tracks"]["D256q4_m8_r1.8"]["t"][0]
    for lev, mk in ((9, "v"), (10, "o"), (11, "s")):
        a.plot([t4], [e1[lev]], mk, color="k", ms=4, mfc="none",
               label=r"$q=4$ at the start" if lev == 10 else None)
    a.axhline(SLOTS, **cz.MASK_LINE)
    a.text(150, SLOTS + 80, "card memory", fontsize=7, ha="right", color="grey")
    a.set_xlabel(r"time from the pericentre $[M]$")
    a.set_ylabel("MeshBlocks")
    a.set_ylim(800, 5000)
    a.legend(loc="upper left", fontsize=6.8, ncol=2, columnspacing=0.8)
    b = axs[1]
    for q, src, cases, col, mk in (("q10", m10, ("D205_m8_r1.8", "D205_m16_r1.8"), RED, "s"),
                                   ("q4", m4, ("D256q4_m8_r1.8", "D256q4_m16_r1.8"), BLUE, "o")):
        res = [8, 16]
        ch = [src["tracks"][c]["card_hours"] for c in cases]
        med = np.array([c["median"] for c in ch])
        lo = med - np.array([c["fast"] for c in ch])
        hi = np.array([c["slow"] for c in ch]) - med
        b.errorbar(res, med, yerr=[lo, hi], fmt=mk + "-", color=col, ms=4, lw=1.2, capsize=2,
                   label=r"$q=10$" if q == "q10" else r"$q=4$")
    b.axhline(ALLOT, color="k", lw=1.0, ls="--")
    b.text(8.3, ALLOT * 1.12, "allotment", fontsize=7)
    b.set_xscale("log", base=2)
    b.set_yscale("log")
    b.set_xticks([8, 16])
    b.set_xticklabels([r"$m/8$", r"$m/16$"])
    b.set_xlim(6.5, 20)
    b.set_ylim(8, 300)
    b.set_xlabel("finest cell")
    b.set_ylabel("card-hours per passage")
    b.legend(loc="upper left", fontsize=7)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
