#!/usr/bin/env python3
"""Step time of the batch-5 card runs (prediction T, tracks/C-sidm/JOURNAL.md 2026-11-21T20:25Z):
seconds of card time per M of simulated time, from the AthenaK logs.

    python3 step_time.py --out DIR --timing RUN LABEL=RUN [LABEL=RUN ...]

--timing: the batch timing job (cases T_*/; 'cpu time used' over the simulated span).
LABEL=RUN: chain runs; every segment log chain/seg*.log that reached 'Terminating on' gives
(elapsed of its last 'time=' line - elapsed of its first) / (simulated span), so preempted
segments and set-up time do not enter. Writes DIR/step_time.json and DIR/fig_step_time.png.
"""
import argparse
import glob
import json
import os
import re

import numpy as np

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
LINE = re.compile(r"elapsed=([0-9.eE+-]+) cycle=\d+ time=([0-9.eE+-]+)")


def seg_rates(d):
    out = []
    for p in sorted(glob.glob(os.path.join(d, "chain", "seg*.log"))):
        txt = open(p, errors="replace").read()
        pts = [(float(e), float(t)) for e, t in LINE.findall(txt)]
        if len(pts) >= 2 and "Terminating on" in txt and pts[-1][1] > pts[0][1]:
            out.append((pts[-1][0] - pts[0][0]) / (pts[-1][1] - pts[0][1]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--timing", required=True)
    ap.add_argument("runs", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(timing={}, chains={})
    td = a.timing if os.path.isdir(a.timing) else os.path.join(SCR, a.timing)
    for c in sorted(glob.glob(os.path.join(td, "T_*"))):
        logs = sorted(glob.glob(os.path.join(c, "athena.*.log")))
        txt = open(logs[-1]).read() if logs else ""
        cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        tt = [float(t) for _, t in LINE.findall(txt)] + [float(t) for t in re.findall(r"^time=([0-9.eE+-]+) cycle=", txt, re.M)]
        tt = [max(tt)] if tt else []
        zc = re.search(r"zone-cycles/cpu_second\s*=\s*([0-9.eE+-]+)", txt)
        if cpu and tt:
            res["timing"][os.path.basename(c)] = dict(s_per_M=float(cpu.group(1)) / max(tt[-1], 1e-30),
                                                     zone_cycles_per_s=float(zc.group(1)) if zc else None)
    for s in a.runs:
        lab, r = s.split("=", 1)
        d = r if os.path.isdir(r) else os.path.join(SCR, r)
        rr = seg_rates(d)
        res["chains"][lab] = dict(segments=len(rr), s_per_M=rr, median=float(np.median(rr)) if rr else None)
    with open(os.path.join(a.out, "step_time.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import sys
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "python")))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    labs, vals, cols = [], [], []
    c3 = fs.series_colors(3)
    for k, v in res["timing"].items():
        labs.append(k.replace("T_", "T:"))
        vals.append(v["s_per_M"])
        cols.append(c3[0])
    for k, v in res["chains"].items():
        if v["median"]:
            labs.append(k)
            vals.append(v["median"])
            cols.append(c3[1])
    ax.bar(range(len(vals)), vals, color=cols)
    ax.axhspan(8.2, 8.4, color="0.85", lw=0, label="prediction T, collisionless (8.2-8.4 s/M)")
    ax.axhline(18.0, color="0.4", ls="--", lw=0.8, label="sequencer stop rule (18 s/M)")
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, rotation=60, ha="right", fontsize=6)
    ax.set_ylabel("card seconds per M")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_step_time.png"), dpi=150)


if __name__ == "__main__":
    main()
