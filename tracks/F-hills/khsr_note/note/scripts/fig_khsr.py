"""Figure: ejection from elliptic centre-of-mass orbits, the comparison with Ref. KHSR
(arXiv:1201.4794, Sec. 6.2 and Fig. 4).

Reads khsr_ecc.json of the scan common.RUNS["khsr"] (checked against its sha256): M/m = 1e6,
m1/m2 = 3, coplanar circular binaries, semi-major axes of the centre-of-mass orbit
r_a/r_t = 500, 200, 130, 100 and the parabola. Lines: KHSR's parabolic approximation from the
restricted parabolic problem (2000 phases per D); circles: the full three-body problem on the
elliptic orbit (512 phases). Top: probability that one member is ejected; bottom: ratio of the
ejection probabilities of the primary and the secondary. Writes fig_khsr.{pdf,png} and
fig_khsr_numbers.json.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_khsr"
RA = ["inf", "500.0", "200.0", "130.0", "100.0"]
LAB = {"inf": "parabolic", "500.0": "$r_a/r_t=500$", "200.0": "$200$", "130.0": "$130$", "100.0": "$100$"}
COL = dict(zip(RA, (cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"], cz.PAL["green"], "k")))


def main():
    out = C.out_dir("figures")
    S = C.load_json("khsr", "khsr_ecc.json")
    cz.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(8.0, 5.0), sharex="col")
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.10, top=0.94, wspace=0.18, hspace=0.07)
    nums = {"run": C.RUNS["khsr"], "points": []}
    for j, s in enumerate(("pro", "ret")):
        for ra in RA:
            L = S["lines"][s][ra]
            D = np.array([x["D"] for x in L])
            P = np.array([x["Pej"] for x in L])
            P1 = np.array([x["P1"] for x in L])
            P2 = np.array([x["P2"] for x in L])
            with np.errstate(divide="ignore", invalid="ignore"):
                R = np.where(P2 > 0, P1 / P2, np.nan)
            axs[0, j].plot(D, P, color=COL[ra], label=LAB[ra])
            axs[1, j].plot(D, R, color=COL[ra])
            pts = [r for r in S["direct"][s] if r["r_a"] == ra]
            Dd = [r["D"] for r in pts]
            axs[0, j].plot(Dd, [r["Pej"] for r in pts], "o", color=COL[ra], ms=4)
            axs[1, j].plot(Dd, [r["P1"] / r["P2"] if r["P2"] > 0 else np.nan for r in pts], "o",
                           color=COL[ra], ms=4)
            for r in pts:
                nums["points"].append(dict(sense=s, D=r["D"], r_a=ra, Pej=r["Pej"], P1=r["P1"],
                                           P2=r["P2"], Pdis=r["Pdis"], Eej=r["Eej"], n_fail=r["n_fail"]))
        axs[0, j].set_ylim(0, 1.05)
        axs[1, j].set_yscale("log")
        axs[1, j].set_ylim(2e-2, 2)
        axs[1, j].axhline(1, **cz.GUIDE)
        axs[1, j].set_xlabel("penetration factor $D$", labelpad=-2)
        axs[0, j].set_title("prograde" if s == "pro" else "retrograde")
        axs[1, j].set_xlim(0, 2.2 if s == "pro" else 0.45)
    axs[0, 0].set_ylabel("ejection probability")
    axs[1, 0].set_ylabel("primary / secondary")
    axs[0, 0].legend(loc="lower left", ncol=2, fontsize=8)
    axs[0, 1].plot([], [], "o", color="grey", ms=4, label="three-body problem, elliptic orbit")
    axs[0, 1].plot([], [], "-", color="grey", label="parabolic approximation")
    axs[0, 1].legend(loc="upper right", fontsize=8)
    cz.save(fig, os.path.join(out, STEM))
    nums["K1"], nums["K2"] = S["K1"], S["K2"]
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
