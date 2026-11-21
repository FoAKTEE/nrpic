"""verify_g0 K5, K13: figure of my scans against the track's.

Left, middle: pericentre scan at q = 10 and q = 4: fractions of phases (Newton separated, Newton
member inside 4 M, HRNA separated, HRNA plunge) of the track's V7 (v7_summary.json of
F-hills-20261115-145915-71abf93) against my R4 runs (hand-off and GR-matched starts) and R8
(H-mu). Right: separated fraction of the HRNA at the set-up of 2404.16270, the track's S1 scan
(s1.npz of F-hills-20261115-130405-ce17dcf, 400 phases) against my R7 (200 phases).

Usage: python3 fig_scan.py --out DIR --scan RUN[,RUN...] --mu RUN --s1 RUN
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--scan", required=True)
    ap.add_argument("--mu", default="")
    ap.add_argument("--s1", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    mine = []
    for run in a.scan.split(","):
        mine += json.load(open(os.path.join(SCR, run, "scan.json")))
    mu = json.load(open(os.path.join(SCR, a.mu, "scan.json"))) if a.mu else []
    v7 = json.load(open(os.path.join(SCR, "F-hills-20261115-145915-71abf93", "v7_summary.json")))
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
    fig.subplots_adjust(wspace=0.32, left=0.06, right=0.99, bottom=0.14, top=0.9)
    out = {"rows": []}
    for k, (key, q) in enumerate((("q10", 10.0), ("q4", 4.0))):
        axx = ax[k]
        rr = v7[key]
        rp = [r["rp"] for r in rr]
        series = (("Newton separated", [r["newton_full"]["separated"] for r in rr], fs.PAL["blue"]),
                  ("Newton inside 4M", [r["newton_full"]["member_below_4M"] for r in rr], fs.PAL["green"]),
                  ("HRNA separated", [r["hrna"]["separated"] for r in rr], fs.PAL["orange"]),
                  ("HRNA plunge", [r["hrna"]["plunge"] for r in rr], fs.PAL["red"]))
        for lab, y, col in series:
            axx.plot(rp, y, "-", color=col, lw=1.2, label=f"V7 {lab}")
        mm = sorted([m for m in mine if m["q"] == q], key=lambda m: m["rp"])
        x = [m["rp"] for m in mm]
        for (lab, _, col), y in zip(series, ([m["newton"]["separated"] for m in mm], [m["newton"]["member_below_4M"] for m in mm],
                                              [m["hrna_handoff"]["separated"] for m in mm], [m["hrna_handoff"]["plunge"] for m in mm])):
            axx.plot(x, y, "o", mfc="none", color=col)
        axx.plot(x, [m["hrna_grmatched"]["plunge"] for m in mm], "s", color=fs.PAL["red"], ms=4, label="mine, HRNA plunge, GR-matched CM")
        mq = [m for m in mu if m["q"] == q]
        if mq:
            axx.plot([m["rp"] for m in mq], [m["newton"]["member_below_4M"] for m in mq], "^", color=fs.PAL["green"], ms=5,
                     label="mine, Newton inside 4M, H-mu")
        for m in mm:
            out["rows"].append(dict(q=q, rp=m["rp"], newton=m["newton"], hrna_handoff=m["hrna_handoff"], hrna_grmatched=m["hrna_grmatched"]))
        axx.set_xlabel(r"$r_p/M$ (Newtonian conic)")
        axx.set_ylabel("fraction of phases")
        axx.set_title(f"q = {int(q)}: lines V7, open symbols mine (180 phases)", fontsize=9)
        axx.set_ylim(-0.03, 1.05)
        axx.legend(fontsize=6, loc="center right")
    if a.s1:
        S1 = np.load(os.path.join(SCR, "F-hills-20261115-130405-ce17dcf", "s1.npz"))
        meta = json.loads(str(S1["meta"]))
        il = meta["laws"].index("hrna")
        sep = S1["separated"] > 0
        b = S1["betas"]
        axx = ax[2]
        for s_, lab, col in ((1, "pro", fs.PAL["blue"]), (-1, "retro", fs.PAL["red"])):
            axx.plot(b, sep[il, meta["senses"].index(s_)].mean(-1), "-", color=col, lw=1.2, label=f"S1 HRNA {lab} (track)")
        R7 = json.load(open(os.path.join(SCR, a.s1, "s1check.json")))
        for r in R7:
            col = fs.PAL["blue"] if r["sense"] == 1 else fs.PAL["red"]
            p = r["separated"]
            e = np.sqrt(max(p * (1 - p), 1 / r["nphase"]) / r["nphase"])
            axx.errorbar([r["beta"]], [p], yerr=[3 * e], fmt="o", mfc="none", color=col, capsize=3)
            out.setdefault("s1", []).append({k: v for k, v in r.items() if k != "sep_flags"})
        axx.set_xlabel(r"$\beta=r_t/r_p$")
        axx.set_ylabel("separated fraction")
        axx.set_title("2404.16270 set-up: lines S1, circles mine (3 sigma)", fontsize=9)
        axx.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(a.out, "fig_scan"))
    json.dump(out, open(os.path.join(a.out, "fig_scan_numbers.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
