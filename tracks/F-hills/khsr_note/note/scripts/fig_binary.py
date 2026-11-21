"""Figure: the binary of the first passage alone, at three resolutions of the members.

Reads the trackers of the card runs of the binary without the heavy black hole at finest
cells m/8, m/12, m/16 (common.RUNS["bc8"], ["bc12"], ["bc16"]) and of the first passage P1
(["p1"], members at m/8 with the heavy black hole), with the readers of the code's output
(common.nrread()); the separations at fixed times are checked against analysis.json of the
package's analysis run (["bcan"], checked against its sha256), which also gives the EIH
(canonical first post-Newtonian) reference at those times. Top: member separation against
time; bottom: its decrease from the start at t = 15 and 20 M against the cell size in member
masses. Writes fig_binary.{pdf,png} and fig_binary_numbers.json.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_binary"
RUNS = (("bc8", "R8", "alone, $m/8$", cz.PAL["red"], 8), ("bc16", "R16n", "alone, $m/16$", cz.PAL["blue"], 16),
        ("bc12", "R12", "alone, $m/12$", cz.PAL["yellow"], 12))


def separation(key):
    nr = C.nrread()
    rd = os.path.join(C.SCRATCH, C.RUNS[key])
    t, X, _ = nr.common_times(nr.read_trackers(rd), keys=[0, 1])
    return t, np.linalg.norm(X[:, 1] - X[:, 0], axis=1)


def main():
    out = C.out_dir("figures")
    an = C.load_json("bcan", "analysis.json")
    cz.use_style()
    fig, (ax, bx) = plt.subplots(2, 1, figsize=(4.0, 5.4))
    fig.subplots_adjust(left=0.17, right=0.95, bottom=0.10, top=0.98, hspace=0.36)
    nums = {"runs": [C.RUNS[k] for k in ("bc8", "bc12", "bc16", "p1", "bcan")], "checks": {}}
    t, s = separation("p1")
    sel = t <= 50
    ax.plot(t[sel], s[sel], color="k", lw=1.0, label="with the heavy hole, $m/8$")
    for key, name, lab, col, _ in RUNS:
        t, s = separation(key)
        ax.plot(t, s, color=col, label=lab, ls="--" if name == "R12" else "-")
        for tt in ("7.5", "15", "20"):
            ref = an[name]["s_at"][tt]
            got = float(np.interp(float(tt), t, s))
            nums["checks"][f"{name}_s_{tt}"] = [got, ref]
            if abs(got - ref) > 1e-6:
                raise SystemExit(f"{name}: separation at {tt} M {got} differs from analysis.json {ref}")
    tr = sorted(float(k) for k, v in an["refs_at"]["eih_c"].items() if v is not None and float(k) <= 30)
    ax.plot(tr, [an["refs_at"]["eih_c"][f"{x:g}"] for x in tr], "s", color="grey", ms=4, mfc="none",
            label="first post-Newtonian (EIH)")
    ax.set_xlim(0, 50)
    ax.set_ylim(3.0, 5.1)
    ax.set_xlabel("$t$ [$M$]", labelpad=-2)
    ax.set_ylabel("member separation [$M$]")
    ax.legend(loc="lower left", fontsize=8)
    h = np.array([1 / 8, 1 / 12, 1 / 16])
    for tt, mk in (("15", "o"), ("20", "s")):
        ds = [an[name]["ds_at"][tt] for name in ("R8", "R12", "R16n")]
        bx.plot(h, ds, mk + "-", color="k", ms=4, lw=1.0, label=f"$t={tt}M$")
        nums[f"ds_{tt}"] = dict(zip(["m8", "m12", "m16"], ds))
        nums[f"eih_ds_{tt}"] = an["refs_at"]["eih_c"]["0"] - an["refs_at"]["eih_c"][tt] if "0" in an["refs_at"]["eih_c"] else None
    bx.set_xlim(0, 0.14)
    bx.set_ylim(0, 0.62)
    bx.set_xlabel("finest cell [member masses]")
    bx.set_ylabel(r"$s(0)-s(t)$ [$M$]")
    bx.legend(loc="upper left", fontsize=8)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
