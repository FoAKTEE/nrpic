#!/usr/bin/env python3
"""Independent cross-check of the batch-11 collapse times (lead recheck, REVIEW-wave3.md
section 14): a reader that shares no code with blockA_delta.py, d2_analysis.py or
analyze_decisive.py. Columns are found by name in the first header line of cc.nrpic.hst;
rows of a restarted segment replace earlier rows from their first time on (a later row with a
time not after the previous one truncates what came before it). t_c is the first record with
alpha_min < 0.3 (no interpolation, so it lies up to 0.25 M after the interpolated value).

    python3 xcheck_b11.py --out DIR LABEL=RUN [...]

Writes DIR/xcheck.json and DIR/fig_xcheck.png (alpha_min of every run against time).
"""
import argparse
import json
import os
import re
import sys

import numpy as np

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def load(path):
    names, rows = None, []
    for ln in open(path):
        if ln.startswith("#"):
            if names is None and "[1]=" in ln:
                names = re.findall(r"\[\d+\]=(\S+)", ln)
            continue
        p = ln.split()
        if not p:
            continue
        t = float(p[0])
        while rows and rows[-1][0] >= t:
            rows.pop()
        rows.append([float(x) for x in p])
    a = np.array(rows)
    return {n: a[:, i] for i, n in enumerate(names) if i < a.shape[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    series = {}
    for s in a.runs:
        lab, r = s.split("=", 1)
        d = r if os.path.isdir(r) else os.path.join(SCR, r)
        h = load(os.path.join(d, "cc.nrpic.hst"))
        t, am, ac = h["time"], h["alpha_min"], h["alpha_probe"]
        k = np.flatnonzero(am < 0.3)
        w = (t >= 390) & (t <= 410)
        res[lab] = dict(t_end=float(t[-1]), t_c_record=float(t[k[0]]) if len(k) else None,
                        dalpha_c_400=float(np.mean(ac[w] - ac[0])) if w.any() else None,
                        rows=int(len(t)))
        series[lab] = (t, am)
    json.dump(res, open(os.path.join(a.out, "xcheck.json"), "w"), indent=1)
    for k, v in res.items():
        print(k, v)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "python")))
    from nrpic import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    cols = fs.series_colors(max(3, len(series)))
    for i, (lab, (t, am)) in enumerate(series.items()):
        ax.plot(t, am, lw=0.8, color=cols[i % len(cols)], label=lab)
    ax.axhline(0.3, color="0.5", ls="--", lw=0.8)
    ax.set_xlabel("t / M")
    ax.set_ylabel(r"$\alpha_{\min}$")
    ax.legend(fontsize=5, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_xcheck.png"), dpi=150)


if __name__ == "__main__":
    main()
