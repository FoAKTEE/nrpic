"""Start of leg B against the step: decaying mode and early growth-rate error of test B at
32 cells, 1 per cell, for step limits 0.002 (card J1 to a = 1000; processors P3 to a = 9)
and 0.001 (processors P3 to a = 9). Tests whether the early floor of f_* - 1 (JOURNAL entry
7, PB3) is set by the step.

    python3 analyze_step.py <runs.json> [<outdir>]     (default outdir $NRPIC_RUN_DIR)

runs.json maps case names to '<run id>/<name>'; the cases read here are b_n32_p1 (J1),
s_n32_p1_dt2 and s_n32_p1_dt1 (P3). Writes <outdir>/flrw_step.json and fig_step (PDF, PNG).
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

CASES = (("b_n32_p1", "card, step limit 0.002"),
         ("s_n32_p1_dt2", "processors, 0.002"),
         ("s_n32_p1_dt1", "processors, 0.001"))
AFIT = 8.5          # common window of the decaying-mode fit (P3 ends at a = 9)


def main():
    runs = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
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
    # record-by-record differences on common times (P3 pair, and card against processors)
    pairs = (("s_n32_p1_dt1", "s_n32_p1_dt2"), ("s_n32_p1_dt2", "b_n32_p1"))
    for a_, b_ in pairs:
        if a_ in data and b_ in data:
            ga, gb = data[a_], data[b_]
            tmax = min(ga["t"][-1], gb["t"][-1])
            m = ga["t"] <= tmax
            eb = np.interp(ga["t"][m], gb["t"], gb["e_star"])
            summ[f"diff_{a_}_minus_{b_}"] = float(np.abs(ga["e_star"][m] - eb).max())
    fl.save_json(summ, os.path.join(out, "flrw_step.json"))

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.16, top=0.95, wspace=0.32)
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
