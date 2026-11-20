"""Figure: the refinement tree of a single member against a model of the refinement rules.

Reads tree_check.json of test E11 (common.RUNS["e11"]; the same numbers as the first pass
F-20261119-143931-4fbf2d0): the MeshBlock trees stored in the restart files of the two
single-puncture card runs (S3 at t = 0, 10, 20 m; S2 at t = 0, 10 m), level by level, with the
tracker position of each restart and the tree that a model of AthenaK's refinement rules
(tracker nest, wave-zone radius, 2:1 balance between all 26 neighbours) builds at that
position; and tree_path.json (common.RUNS["e11path"]), the model along x = 0-20 m. The stop
positions of the two runs (tracker x when the tree exceeded the 1600 slots of the input) come
from single_analysis.json of the lead's E3 rerun (common.RUNS["e3"]). Nothing is recomputed;
the script checks that every restart tree equals its model level by level.
Writes fig_tree.{pdf,png} and fig_tree_numbers.json.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_tree"
SLOTS = 1600        # max_nmb_per_rank of the single-puncture input (nr_first E3, E11)


def main():
    out = C.out_dir("figures")
    tc = C.load_json("e11", "tree_check.json")
    tp = C.load_json("e11path", "tree_path.json")
    e3 = C.load_json("e3", "single_analysis.json")
    col = {"S3": cz.PAL["yellow"], "S2": cz.PAL["red"]}
    lab = {"S3": r"$\eta m=2$", "S2": r"$\eta m=0.25$"}
    nums = {"runs": [C.RUNS["e11"], C.RUNS["e11path"], C.RUNS["e3"]], "slots": SLOTS,
            "restarts": []}
    for name, rows in tc["runs"].items():
        for r in rows:
            assert r["counts"] == r["model_counts"], f"{name} {r['file']}: tree differs from model"
            assert r["nmb"] == r["model_total"] == sum(r["counts"].values())
            nums["restarts"].append(dict(run=name, t=r["time"], x=r["tracker"][0], nmb=r["nmb"],
                                         counts=r["counts"]))
    xp = np.array([r["x"] for r in tp["rows"]])
    npth = np.array([r["total"] for r in tp["rows"]])
    assert int(npth.max()) == tp["max"]
    over = xp[npth > SLOTS]
    nums.update(path_max=int(npth.max()), path_values=sorted(set(map(int, npth))),
                first_x_above_slots=float(over.min()) if len(over) else None,
                x_stop={n: e3[n]["x_end"] for n in ("S3", "S2")},
                t_stop={n: e3[n]["t_end"] for n in ("S3", "S2")})

    cz.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw=dict(width_ratios=[1.45, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.18, top=0.96, wspace=0.27)
    a = axs[0]
    a.step(xp, npth, where="mid", color="k", lw=1.3, label="rule model")
    for r in nums["restarts"]:
        if r["t"] > 0:
            a.plot(r["x"], r["nmb"], "o", color=col[r["run"]], ms=6, mfc="none", mew=1.4,
                   label=f"restart tree, {lab[r['run']]}" if r["t"] == 10 else None)
    for n in ("S3", "S2"):
        a.axvline(nums["x_stop"][n], color=col[n], lw=1.0, ls=":")
    a.axhline(SLOTS, **cz.MASK_LINE)
    a.text(19.7, SLOTS + 3, "slots of the input", fontsize=7, ha="right", va="bottom", color="grey")
    a.text(nums["x_stop"]["S2"] + 0.3, 1616, "both runs stop", fontsize=7, ha="left", va="center")
    a.set_xlabel(r"tracker position $x\;[m]$")
    a.set_ylabel("MeshBlocks")
    a.set_xlim(0, 20)
    a.set_ylim(1530, 1740)
    a.legend(frameon=False, fontsize=6.8, loc="upper right")
    b = axs[1]
    lev = np.arange(7)
    shown = [r for r in nums["restarts"] if r["run"] == "S3"]
    mk = {0.0: "s", 10.0: "o", 20.0: "^"}
    model = {r["time"]: r["model_counts"] for r in tc["runs"]["S3"]}
    for r in shown:
        k = [j for j in lev if r["counts"].get(str(j), 0) > 0]
        c = [r["counts"][str(j)] for j in k]
        b.plot(k, c, mk[r["t"]] + "-", color="k", ms=5, mfc="none", lw=0.9,
               label=fr"$t={r['t']:g}\,m$, {r['nmb']} blocks")
        km = [j for j in lev if model[r["t"]].get(str(j), 0) > 0]
        b.plot(km, [model[r["t"]][str(j)] for j in km], "+", color=cz.PAL["blue"], ms=5,
               mew=1.0, label="rule model" if r["t"] == 20 else None)
    b.set_yscale("log")
    b.set_xlabel("refinement level")
    b.set_ylabel("MeshBlocks per level")
    b.set_xticks(lev)
    b.xaxis.set_minor_locator(plt.NullLocator())
    b.set_ylim(20, 2000)
    b.legend(frameon=False, fontsize=6.8, loc="upper right")
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
