"""Figure: Hamiltonian constraint of the three-black-hole data at t = 0 against resolution.

Reads c0_constraints.json of the analysis run of the package's test E2 (common.RUNS["e2"]),
which evaluated the t = 0 data of the q = 4 passage input (run common.RUNS["c0"]: corrected
data with the background factor, uncorrected data, plain sum) at finest cells m/4, m/8, m/16:
the code's norm <H^2>^(1/2) over the volume where psi^4 <= 16, the closed-form residual of the
same data on the same cells, and their difference (the truncation error), in the whole volume
and in three regions (members r < 1 M, heavy black hole r < 4 M, the rest). Nothing is
recomputed; the truncation orders printed by the run are checked against the JSON's numbers.
Writes fig_constraints.{pdf,png} and fig_constraints_numbers.json.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_constraints"
LEV = (9, 10, 11)                       # finest cells m/4, m/8, m/16
H = np.array([1 / 4, 1 / 8, 1 / 16])    # finest cell in units of the member mass


def main():
    out = C.out_dir("figures")
    d = C.load_json("e2", "c0_constraints.json")
    BLUE, RED, YEL = cz.PAL["blue"], cz.PAL["red"], cz.PAL["yellow"]
    nums = {"runs": [C.RUNS["c0"], C.RUNS["e2"]]}
    ser = {}
    for case in ("approx", "none"):
        ser[case] = {k: np.array([d[f"{case}_L{lv}"]["all"][k] for lv in LEV])
                     for k in ("code", "closed", "diff")}
        ser[case]["blocks"] = [d[f"{case}_L{lv}"]["blocks"] for lv in LEV]
        order = [math.log2(ser[case]["diff"][i] / ser[case]["diff"][i + 1]) for i in range(2)]
        for a, b in zip(order, d[f"order_{case}"]):
            C.close(a, b, 1e-9, f"truncation order of {case}")
        nums[case] = {k: list(map(float, v)) for k, v in ser[case].items() if k != "blocks"}
        nums[case]["blocks"] = ser[case]["blocks"]
        nums[case]["order"] = order
    nums["plain_m8"] = d["plain_L10"]["all"]
    nums["ratio_closed_none_over_approx_m16"] = float(ser["none"]["closed"][2] / ser["approx"]["closed"][2])
    nums["ratio_code_none_over_approx_m8"] = float(ser["none"]["code"][1] / ser["approx"]["code"][1])
    nums["ratio_code_none_over_approx_m16"] = float(ser["none"]["code"][2] / ser["approx"]["code"][2])
    nums["regions_approx_m8"] = {r: d["approx_L10"][r] for r in ("members (r < 1 M)", "heavy (r < 4 M)", "rest")}
    nums["regions_approx_m16"] = {r: d["approx_L11"][r] for r in ("members (r < 1 M)", "heavy (r < 4 M)", "rest")}

    cz.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.75))
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.2, top=0.965, wspace=0.27)
    a = axs[0]
    for case, col in (("none", BLUE), ("approx", RED)):
        s = ser[case]
        a.loglog(H, s["code"], "o-", color=col, ms=4, lw=1.3)
        a.loglog(H, s["closed"], "s--", color=col, ms=4, mfc="none", lw=1.0)
        a.loglog(H, s["diff"], "^:", color=col, ms=4, lw=1.0)
    p = d["plain_L10"]["all"]
    a.loglog([H[1]], [p["closed"]], "D", color=YEL, ms=4, mfc="none")
    a.loglog(H, s["diff"][2] * (H / H[2]) ** 8, **cz.GUIDE)
    from matplotlib.lines import Line2D
    sty = [Line2D([], [], color="k", marker="o", ms=4, lw=1.3, label="code"),
           Line2D([], [], color="k", marker="s", ms=4, mfc="none", ls="--", lw=1.0,
                  label="closed form"),
           Line2D([], [], color="k", marker="^", ms=4, ls=":", lw=1.0, label="difference"),
           Line2D([], [], **cz.GUIDE, label=r"$\propto h^{8}$"),
           Line2D([], [], color=YEL, marker="D", ms=4, mfc="none", ls="none",
                  label="plain sum, closed form")]
    lg = a.legend(handles=sty, frameon=False, fontsize=6.5, loc="upper right",
                  handlelength=2.4)
    a.add_artist(lg)
    col = [Line2D([], [], color=BLUE, lw=1.6, label="uncorrected"),
           Line2D([], [], color=RED, lw=1.6, label="corrected")]
    a.legend(handles=col, frameon=False, fontsize=6.5, loc="lower left",
             bbox_to_anchor=(0.0, 0.19))
    a.set_xlabel(r"finest cell $h$ at the members $[m]$")
    a.set_ylabel(r"$\langle H^2\rangle^{1/2}$ at $t=0$")
    a.set_xticks(H)
    a.set_xticklabels([r"$1/4$", r"$1/8$", r"$1/16$"])
    a.xaxis.set_minor_formatter(plt.NullFormatter())
    a.set_xlim(0.05, 0.33)
    a.set_ylim(5e-8, 5e-2)
    a.invert_xaxis()
    b = axs[1]
    regs = (("members (r < 1 M)", "members\n" + r"$r<1M$"),
            ("heavy (r < 4 M)", "heavy\n" + r"$r<4M$"), ("rest", "elsewhere"))
    xb = np.arange(3)
    wbar = 0.26
    for j, lv in enumerate(LEV):
        e = d[f"approx_L{lv}"]
        code = [e[r]["code"] for r, _ in regs]
        clo = [e[r]["closed"] for r, _ in regs]
        col = ("#9aa9c9", RED, "#7a1f1a")[j]
        b.bar(xb + (j - 1) * wbar, code, wbar * 0.92, color=col, alpha=0.85,
              label=(r"code, $h=m/4$", r"code, $h=m/8$", r"code, $h=m/16$")[j])
        b.plot(xb + (j - 1) * wbar, clo, "_", color="k", ms=9, mew=1.5,
               label="closed form" if j == 0 else None)
    b.set_yscale("log")
    b.set_xticks(xb)
    b.set_xticklabels([lab for _, lab in regs], fontsize=8.5)
    b.xaxis.set_minor_locator(plt.NullLocator())
    b.set_ylim(5e-11, 1e1)
    b.set_ylabel(r"$\langle H^2\rangle^{1/2}$, corrected data")
    b.legend(frameon=False, fontsize=6.2, loc="upper right", ncol=2)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
