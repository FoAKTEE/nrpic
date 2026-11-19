#!/usr/bin/env python3
"""Check C2 of tracks/core/JOURNAL-scalar3.md: the card executable of the final source
against the processor executable on the same input (inputs/card_c2.list).

    python3 c2_compare.py --card DIR --exe EXE [--out DIR]

DIR is the run directory of the card list entry srg20.  Runs the same input on the
processors, then compares: the initial dump bit for bit; the later dumps (largest
difference per variable relative to its largest value); every column of the constraint
record including the seven of con_signed (largest relative difference).  Writes
OUT/summary.json and OUT/fig_c2.png."""
import argparse
import os

import s3
from s3 import common, np, sf

INP = os.path.join(common.PROB, "sr_stochastic_gauge.athinput")
BASE = "srg"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    rd = os.path.join(out, "srg20")
    wall = common.run_case(os.path.abspath(a.exe), rd, INP, [
        "scalar_field/noise_mode_file=" + os.path.join(common.PROB,
                                                       "sr_stochastic_modes.txt"),
        "time/nlim=20"])
    summ = dict(card=os.path.abspath(a.card), exe=os.path.abspath(a.exe), wall_cpu_s=wall)
    dc, dp = s3.dumps(a.card, BASE), s3.dumps(rd, BASE)
    rows = []
    for cy in sorted(set(dc) & set(dp)):
        fc, fp_ = dc[cy]["fields"], dp[cy]["fields"]
        row = dict(cycle=cy, time=float(dc[cy]["time"]))
        worst = 0.0
        ident = True
        for k in fc:
            x, y = fc[k], fp_[k]
            ident &= bool(np.array_equal(x, y))
            sc = max(np.abs(y).max(), 1e-300)
            worst = max(worst, float(np.abs(x - y).max()/sc))
            row["rel_" + k] = float(np.abs(x - y).max()/sc)
        row["identical"] = ident
        row["worst_rel"] = worst
        rows.append(row)
    summ["dumps"] = rows
    cc = sf.read_con_history(os.path.join(a.card, BASE + ".sf.con.hst"))
    cp = sf.read_con_history(os.path.join(rd, BASE + ".sf.con.hst"))
    con = {}
    for k in cp:
        if k in ("time", "cycle"):
            continue
        x, y = cc[k], cp[k]
        sc = np.maximum(np.abs(y), 1e-300)
        con[k] = float(np.max(np.abs(x - y)/sc))
    summ["con_rel_max"] = con
    summ["con_columns"] = len(cp)
    common.dump_json(summ, os.path.join(out, "summary.json"))
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.7))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.95, wspace=0.3)
    ax[0].plot(cp["cycle"], cp["H_ratio"], "-", color=fs.PAL["blue"],
               label=r"processors: $\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
    ax[0].plot(cc["cycle"], cc["H_ratio"], "o", mfc="none", ms=3, color=fs.PAL["blue"],
               label="card")
    if "Hp_ratio" in cp:
        ax[0].plot(cp["cycle"], np.maximum(cp["Hp_ratio"], 1e-30), "-",
                   color=fs.PAL["red"], label=r"processors: $\langle|\mathcal{H}'|/"
                   r"[\mathcal{H}]\rangle$")
        ax[0].plot(cc["cycle"], np.maximum(cc["Hp_ratio"], 1e-30), "o", mfc="none",
                   ms=3, color=fs.PAL["red"], label="card")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("cycle")
    ax[0].set_ylabel("ratio to the magnitude")
    ax[0].legend(fontsize=6, loc="lower right")
    ks = sorted(con, key=lambda k: -con[k])[:14]
    ax[1].barh(range(len(ks)), [max(con[k], 1e-17) for k in ks], color=fs.PAL["blue"])
    ax[1].set_yticks(range(len(ks)))
    ax[1].set_yticklabels(ks, fontsize=6)
    ax[1].set_xscale("log")
    ax[1].set_xlabel("largest relative difference, card against processors")
    fig.savefig(os.path.join(out, "fig_c2.png"), dpi=200)
    print("C2 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
