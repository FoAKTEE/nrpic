#!/usr/bin/env python3
"""Time/space split of the X error (JOURNAL.md 2026-11-20 22:30, XS-1 to XS-4), from the
analyses of the step test (analyze_r1.py --mode xdt) and the round-1 predictions.

    xs_split.py --card results/xdt_card_results.json [--cpu results/xdt_cpu_results.json]
                [--pred results/predictions_r1.json]
        (through nrpic-run; writes $NRPIC_RUN_DIR/xs_split.{json,png,pdf}, copies into
         ../results and ../figs)

Measured, per N and per polarization (TT diagnostic, forward combination at t = 10):
  e(0.01)   reference error (dt_expansion = 0.01, final analysis B-20261119-164402-7438a99),
  e(0.001)  error of the step test: the space part plus a time part predicted at <= 1e-9,
  time part = e(0.01) - e(0.001).
Predicted (code's RK4()4[2S] on the coupled background, wlib/predict.py): the same three at
0.01, 0.001 and 1e-4 (the space part).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import PKG  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

Q = (("amp", "amplitude"), ("phase", "phase (rad)"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--cpu", default=None)
    ap.add_argument("--pred", default=os.path.join(PKG, "results", "predictions_r1.json"))
    a = ap.parse_args()
    out = os.environ["NRPIC_RUN_DIR"]
    card = json.load(open(a.card))
    cpu = json.load(open(a.cpu)) if a.cpu else None
    pred = json.load(open(a.pred))["x_step"]
    ns = [int(n) for n in card["ns"]]
    res = {"inputs": {"card": a.card, "cpu": a.cpu, "pred": a.pred}, "N": {}}
    for n in ns:
        s, ref = card[str(n)], card["reference"][str(n)]
        p = pred[str(n)]
        r = {}
        for pol in ("x", "p"):
            for q, _ in Q:
                key = f"{q}_{pol}_end"
                e1, e2 = ref["tt"][key], s["tt"][key]
                r[key] = {"e_0.01": e1, "e_0.001": e2, "time_meas": e1 - e2,
                          "pred_0.01": p["0.01"][f"{q}_end"], "pred_0.001": p["0.001"][f"{q}_end"],
                          "pred_space": p["0.0001"][f"{q}_end"],
                          "time_pred": p["0.01"][f"{q}_end"] - p["0.001"][f"{q}_end"]}
                r[key]["new_over_pred"] = e2 / r[key]["pred_0.001"]
                r[key]["time_meas_over_pred"] = r[key]["time_meas"] / r[key]["time_pred"]
        r["pol_phase_end"] = {"e_0.01": ref["tt"]["pol_phase_end"], "e_0.001": s["tt"]["pol_phase_end"],
                              "ratio": s["tt"]["pol_phase_end"] / ref["tt"]["pol_phase_end"]}
        r["pol_amp_end"] = {"e_0.01": ref["tt"]["pol_amp_end"], "e_0.001": s["tt"]["pol_amp_end"],
                            "ratio": s["tt"]["pol_amp_end"] / ref["tt"]["pol_amp_end"]}
        r["steps"] = {"0.01": p["0.01"]["nsteps"], "0.001": s.get("cycle_end"),
                      "ratio": s.get("cycle_end", 0) / p["0.01"]["nsteps"]}
        r["weylS_vs_tt_max"] = {"e_0.01": ref["weylS_vs_tt_max"], "e_0.001": s["weylS"]["vs_tt_max"]}
        r["background"] = {"a_rel_err_max": s["a_rel_err_max"], "alpha_over_a_max": s["alpha_over_a_max"],
                           "calH_rel_err_max": s["calH_rel_err_max"],
                           "ref_a_rel_err_max": ref.get("a_rel_err_max"),
                           "ref_alpha_over_a_max": ref.get("alpha_over_a_max")}
        if cpu and str(n) in cpu:
            c = cpu[str(n)]
            r["card_minus_cpu"] = {k: s["tt"][k] - c["tt"][k] for k in
                                   ("amp_x_end", "phase_x_end", "amp_p_end", "phase_p_end", "pol_phase_end")}
            r["cpu"] = {k: c["tt"][k] for k in ("amp_x_end", "phase_x_end", "amp_p_end", "phase_p_end",
                                                 "pol_phase_end")}
            r["cpu"]["weylS_vs_tt_max"] = c["weylS"]["vs_tt_max"]
            r["cpu"]["a_rel_err_max"] = c["a_rel_err_max"]
        res["N"][str(n)] = r
    with open(os.path.join(out, "xs_split.json"), "w") as f:
        json.dump(res, f, indent=1)

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    nn = np.array(ns, float)
    for ax, (q, lab) in zip(axs, Q):
        key = f"{q}_x_end"
        R = [res["N"][str(n)][key] for n in ns]

        def plot(vals, marker, color, label, ls="-"):
            v = np.array(vals)
            ax.loglog(nn, np.abs(v), ls=ls, color=color, lw=1.0, label=label)
            pos, neg = v > 0, v < 0
            ax.loglog(nn[pos], v[pos], marker, color=color, ls="none")
            ax.loglog(nn[neg], -v[neg], marker, color=color, mfc="none", ls="none")
        plot([r["e_0.01"] for r in R], "o", fs.PAL["red"], "measured, dt_exp 0.01")
        plot([r["pred_0.01"] for r in R], "x", "k", "2S, 0.01", ls=":")
        plot([r["e_0.001"] for r in R], "s", fs.PAL["blue"], "measured, 0.001")
        plot([r["pred_space"] for r in R], "+", "k", "2S, 1e-4 (space part)", ls="--")
        plot([r["time_meas"] for r in R], "D", fs.PAL["green"], "time part, measured")
        plot([r["time_pred"] for r in R], "1", "k", "time part, 2S", ls="-.")
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.minorticks_off()
        ax.set_xlabel("N (cells per side)")
        ax.set_ylabel(f"cross-pol. {lab} error at t = 10")
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi * (hi / lo) ** 0.35)
        ax.legend(loc="upper right", ncol=2, fontsize=6)
    axs[0].set_title("X: time and space parts (open markers: negative)", fontsize=9)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"xs_split.{ext}"))
    plt.close(fig)
    shutil.copy(os.path.join(out, "xs_split.json"), os.path.join(PKG, "results", "xs_split.json"))
    shutil.copy(os.path.join(out, "xs_split.png"), os.path.join(PKG, "figs", "xs_split.png"))
    print(json.dumps(res["N"], indent=1))


if __name__ == "__main__":
    main()
