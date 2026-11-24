"""Start of leg B against the step: decaying mode and early growth-rate error of test B at
32 cells, 1 per cell, for step limits 0.002 (card J1 to a = 1000; processors P3 to a = 9)
and 0.001 (processors P3 to a = 9). Tests whether the early floor of f_* - 1 (JOURNAL entry
7, PB3) is set by the step.

    python3 analyze_step.py <runs.json> [<outdir>] [--set n32|n128]   (default outdir $NRPIC_RUN_DIR)

runs.json maps case names to '<run id>/<name>'; the cases read with the default set n32 are
b_n32_p1 (J1), s_n32_p1_dt2, s_n32_p1_dt1 (P3) and s_n32_p1_dt05 (P4). The set n128 (added in
batch 11 for J4, entry 14) reads b_n128_p1 (J3, card chain, limit 0.002), s_n128_p1_dt2,
s_n128_p1_dt1 and s_n128_p1_dt10 (J4, limits 0.002, 0.001, 0.01). Writes
<outdir>/flrw_step.json and fig_step (PDF, PNG); the n32 output is unchanged by the option.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import flrwlib as fl  # noqa: E402

SETS = {
    "n32": {"cases": (("b_n32_p1", "card, step limit 0.002"),
                      ("s_n32_p1_dt2", "processors, 0.002"),
                      ("s_n32_p1_dt1", "processors, 0.001"),
                      ("s_n32_p1_dt05", "processors, 0.0005")),
            "pairs": (("s_n32_p1_dt1", "s_n32_p1_dt2"), ("s_n32_p1_dt05", "s_n32_p1_dt1"),
                      ("s_n32_p1_dt2", "b_n32_p1"))},
    "n128": {"cases": (("b_n128_p1", "card chain J3, 0.002"),
                       ("s_n128_p1_dt2", "card J4, 0.002"),
                       ("s_n128_p1_dt1", "card J4, 0.001"),
                       ("s_n128_p1_dt10", "card J4, 0.01")),
             "pairs": (("s_n128_p1_dt1", "s_n128_p1_dt2"), ("s_n128_p1_dt10", "s_n128_p1_dt2"),
                       ("s_n128_p1_dt2", "b_n128_p1"))},
}
AFIT = 8.5          # common window of the decaying-mode fit (P3 ends at a = 9)


def main():
    args = list(sys.argv[1:])
    cset = "n32"
    if "--set" in args:
        i = args.index("--set")
        cset = args[i + 1]
        del args[i:i + 2]
    CASES, pairs = SETS[cset]["cases"], SETS[cset]["pairs"]
    runs = json.load(open(args[0]))
    out = args[1] if len(args) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    data = {k: fl.growth(fl.rundir(runs[k])) for k, _ in CASES if k in runs}
    summ = {}
    for k, g in data.items():
        early = (g["a"] >= 1.05) & (g["a"] <= 2.0)
        summ[k] = {"a_end": float(g["a"][-1]), "records": int(len(g["a"])),
                   "fit": fl.decaying_fit_log(g, amax=AFIT),
                   "df_star_early_max": float(np.abs(g["df_star"][early]).max()),
                   "e_star_at": {f"{a0:g}": float(np.interp(np.log(a0), np.log(g["a"]), g["e_star"]))
                                 for a0 in (1.1, 1.5, 2.0, 4.0, 8.0)}}
    # record-by-record differences on common times (step pairs, and the same limit twice)
    for a_, b_ in pairs:
        if a_ in data and b_ in data:
            ga, gb = data[a_], data[b_]
            tmax = min(ga["t"][-1], gb["t"][-1])
            m = ga["t"] <= tmax
            eb = np.interp(ga["t"][m], gb["t"], gb["e_star"])
            summ[f"diff_{a_}_minus_{b_}"] = float(np.abs(ga["e_star"][m] - eb).max())
            summ[f"diff_at_end_{a_}_minus_{b_}"] = float(ga["e_star"][m][-1] - eb[-1])
    fl.save_json(summ, os.path.join(out, "flrw_step.json"))

    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.42)
    for (a_, b_), col in zip(pairs[:2], fs.SERIES[2:]):
        if a_ in data and b_ in data:
            ga, gb = data[a_], data[b_]
            m = ga["t"] <= min(ga["t"][-1], gb["t"][-1])
            eb = np.interp(ga["t"][m], gb["t"], gb["e_star"])
            axs[2].semilogx(ga["a"][m], (ga["e_star"][m] - eb)*1e6, color=col, lw=1.0,
                            label=a_.split("_")[-1] + " - " + b_.split("_")[-1])
    axs[2].set_xlabel(r"$a$")
    axs[2].set_ylabel(r"difference of $D_\star/A a$ ($10^{-6}$)")
    axs[2].legend(fontsize=6.5, loc="best")
    for (k, lab), col in zip(CASES, fs.SERIES):
        if k not in data:
            continue
        g = data[k]
        m = g["a"] <= 9.5
        axs[0].semilogx(g["a"][m], g["e_star"][m]*1e6, color=col, lw=1.0, label=lab)
        axs[1].loglog(g["a"][m], np.maximum(np.abs(g["df_star"][m]), 1e-10), color=col, lw=1.0)
        f = summ[k]["fit"]
        aa = np.geomspace(1.0, 9.0, 100)
        model = np.expm1(f["c0"] + f["df_const"]*np.log(aa) + f["eps"]*aa**-2.5)
        axs[0].semilogx(aa, model*1e6, **{**fs.GUIDE, "color": col, "lw": 0.7})
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"$(D_\star/A a - 1)\times 10^{6}$")
    axs[0].legend(fontsize=7, loc="best")
    axs[0].text(0.03, 0.04, r"dashed: fit $c_0 + c_1\ln a + \epsilon a^{-5/2}$",
                transform=axs[0].transAxes, fontsize=7)
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"$|f_\star - 1|$")
    fs.save(fig, os.path.join(out, "fig_step"))
    plt.close(fig)
    for k, s in summ.items():
        if isinstance(s, dict):
            f = s["fit"]
            print(f"{k}: a_end {s['a_end']:.2f}; eps {f['eps']:+.3e}, c1 {f['df_const']:+.2e}, "
                  f"c0 {f['c0']:+.2e}, rms {f['rms_resid']:.1e}; early max |f*-1| "
                  f"{s['df_star_early_max']:.2e}")
        else:
            print(f"{k}: {s:.2e}")


if __name__ == "__main__":
    main()
