#!/usr/bin/env python3
"""Check C2 of tracks/core/JOURNAL-scalar3.md: the card executable of the final source
against the processor executable on the same input (inputs/card_c2.list).

    python3 c2_compare.py --card DIR (--exe EXE | --cpu DIR2) [--out DIR]

DIR is the run directory of the card list entry srg20.  Runs the same input on the
processors (or, with --cpu, takes the processor run of an earlier call from DIR2), then
compares: the initial dump bit for bit; the later dumps (largest difference per
variable, relative to its largest value and in absolute units); every column of the
constraint record including the seven of con_signed (largest relative and largest
absolute difference).  The perturbations of this case are small (At_ij of order 1e-7, H
of order 1e-11), so only the absolute differences tell rounding from a defect (journal
entry 16).  Writes OUT/summary.json, OUT/fig_c2.png and OUT/fig_c2_abs.png."""
import argparse
import os

import s3
from s3 import common, np, sf

INP = os.path.join(common.PROB, "sr_stochastic_gauge.athinput")
BASE = "srg"
CONSTRAINT_FIELDS = ("H", "Mx", "My", "Mz", "E")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--exe")
    ap.add_argument("--cpu", help="run directory of the processor run of an earlier call")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    if a.cpu:
        rd = os.path.abspath(a.cpu)
        summ = dict(card=os.path.abspath(a.card), cpu=rd)
    else:
        rd = os.path.join(out, "srg20")
        wall = common.run_case(os.path.abspath(a.exe), rd, INP, [
            "scalar_field/noise_mode_file=" + os.path.join(common.PROB,
                                                           "sr_stochastic_modes.txt"),
            "time/nlim=20"])
        summ = dict(card=os.path.abspath(a.card), exe=os.path.abspath(a.exe),
                    wall_cpu_s=wall)
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
            row["abs_" + k] = float(np.abs(x - y).max())
            row["max_" + k] = float(np.abs(y).max())
        row["identical"] = ident
        row["differing"] = [k for k in fc if not np.array_equal(fc[k], fp_[k])]
        row["worst_rel"] = worst
        con_names = [k for k in fc if k in CONSTRAINT_FIELDS]
        row["worst_abs_evolved"] = max(row["abs_" + k] for k in fc
                                       if k not in con_names)
        row["worst_abs_evolved_var"] = max((k for k in fc if k not in con_names),
                                           key=lambda k: row["abs_" + k])
        row["worst_abs_constraint"] = max(row["abs_" + k] for k in con_names) \
            if con_names else None
        rows.append(row)
    summ["dumps"] = rows
    if len(rows) >= 3 and rows[1]["worst_abs_evolved"] > 0.0:
        summ["growth_evolved_last_over_middle"] = \
            rows[-1]["worst_abs_evolved"]/rows[1]["worst_abs_evolved"]
    cc = sf.read_con_history(os.path.join(a.card, BASE + ".sf.con.hst"))
    cp = sf.read_con_history(os.path.join(rd, BASE + ".sf.con.hst"))
    con, con_abs, con_size = {}, {}, {}
    for k in cp:
        if k in ("time", "cycle"):
            continue
        x, y = cc[k], cp[k]
        sc = np.maximum(np.abs(y), 1e-300)
        con[k] = float(np.max(np.abs(x - y)/sc))
        con_abs[k] = float(np.max(np.abs(x - y)))
        con_size[k] = float(np.max(np.abs(y)))
    summ["con_rel_max"] = con
    summ["con_abs_max"] = con_abs
    summ["con_value_max"] = con_size
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
    ax[1].set_xlabel("largest relative difference, card to processors", fontsize=8)
    fig.savefig(os.path.join(out, "fig_c2.png"), dpi=200)
    plt.close(fig)

    # absolute differences: the dumps per variable, and the record
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.2, top=0.96, wspace=0.42)
    names = [k[4:] for k in rows[0] if k.startswith("abs_")]
    for row, cl, mk in zip(rows, (fs.PAL["blue"], fs.PAL["orange"], fs.PAL["red"]),
                           ("o", "s", "^")):
        ax[0].plot(range(len(names)), [max(row["abs_" + k], 1e-18) for k in names], mk,
                   ms=3.5, mfc="none", color=cl, label=f"cycle {row['cycle']}")
    ax[0].axhline(1e-13, **fs.MASK_LINE)
    ax[0].set_xticks(range(len(names)))
    ax[0].set_xticklabels(names, rotation=90, fontsize=5.5)
    ax[0].set_yscale("log")
    ax[0].set_ylim(3e-19, 1e-11)
    ax[0].set_ylabel("largest absolute difference in the dump", fontsize=8)
    ax[0].legend(loc="upper left", fontsize=6.5)
    ks = sorted(con_abs, key=lambda k: -con_abs[k])
    ax[1].barh(range(len(ks)), [max(con_abs[k], 1e-19) for k in ks],
               color=fs.PAL["blue"])
    ax[1].set_yticks(range(len(ks)))
    ax[1].set_yticklabels(ks, fontsize=5.5)
    ax[1].set_xscale("log")
    ax[1].set_xlabel("largest absolute difference in the record", fontsize=8)
    fig.savefig(os.path.join(out, "fig_c2_abs.png"), dpi=200)
    print("C2 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
