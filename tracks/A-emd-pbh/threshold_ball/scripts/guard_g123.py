#!/usr/bin/env python3
"""Outcome figure of threshold_ball entry 5 (A-mesh guard stop, processor restarts G1-G3 from t = 44).

    guard_g123.py --run <run dir of A-20261124-132016-ecf12c3> --out DIR

For each variant: end of the run (guard stop or time limit, from athena.log), the finder's searches
after t = 44 (found or not, rows written last kept) and the mass of each successful search.
Writes guard_g123.json and fig_guard_g123.png.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABEL = {"G1": "G1: deck as on the card", "G2": "G2: lapse_leak = 0", "G3": "G3: alpha_exc = 0.3"}


def searches(p):
    rows = []
    for ln in open(p):
        if ln.startswith("#") or not ln.strip():
            continue
        v = ln.split("#")[0].split()
        rows.append((float(v[1]), int(v[2]), float(v[6])))
    a = np.array(rows)
    keep, tn = [], np.inf
    for i in range(len(a) - 1, -1, -1):
        if a[i, 0] < tn:
            keep.append(i)
            tn = a[i, 0]
    a = a[keep[::-1]]
    return a[a[:, 0] >= 44.0]


def end_state(p):
    txt = open(p, errors="replace").read()
    m = re.search(r"NRPIC guard: the run stops at time ([0-9.eE+-]+), cycle (\d+)", txt)
    if m:
        return dict(end="guard", t_end=float(m.group(1)), cycle=int(m.group(2)))
    m = re.search(r"Terminating on time limit", txt)
    t = re.findall(r"time=([0-9.eE+-]+)", txt)
    return dict(end="tlim" if m else "other", t_end=float(t[-1]) if t else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, S = {}, {}
    for g in ("G1", "G2", "G3"):
        s = searches(os.path.join(a.run, g, "ball.horizon_status_0.txt"))
        S[g] = s
        e = end_state(os.path.join(a.run, g, "athena.log"))
        f = s[s[:, 1] > 0]
        e.update(n_searches=int(len(s)), n_found=int(len(f)),
                 first_found=float(f[0, 0]) if len(f) else None, last_found=float(f[-1, 0]) if len(f) else None,
                 last_search=float(s[-1, 0]) if len(s) else None)
        res[g] = e
    json.dump(res, open(os.path.join(a.out, "guard_g123.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(HERE, "..", "..", "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    col = {"G1": fs.PAL["red"], "G2": fs.PAL["yellow"], "G3": fs.PAL["blue"]}
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.9, wspace=0.3)
    ax = axs[0]
    for k, g in enumerate(("G1", "G2", "G3")):
        s = S[g]
        y = np.full(len(s), k)
        ax.plot(s[s[:, 1] > 0, 0], y[s[:, 1] > 0], "o", ms=4, color=col[g])
        ax.plot(s[s[:, 1] == 0, 0], y[s[:, 1] == 0], "x", ms=3, color="0.6")
        r = res[g]
        ax.plot([r["t_end"]], [k], marker="|" if r["end"] == "tlim" else "*", ms=12, color="k")
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["G1", "G2", "G3"])
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel(r"$t/M$")
    ax.set_title(r"searches: found (dot), failed (x); end: guard $\ast$, tlim $|$", fontsize=9)
    ax = axs[1]
    for g in ("G1", "G2", "G3"):
        s = S[g]
        f = s[s[:, 1] > 0]
        ax.plot(f[:, 0], f[:, 2], "o-", ms=3, color=col[g], label=LABEL[g])
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"finder mass $/M$")
    ax.legend(fontsize=7)
    ax.set_title("mass of the successful searches (mesh A, M/16)", fontsize=9)
    fig.savefig(os.path.join(a.out, "fig_guard_g123.png"), dpi=150)
    fig.savefig(os.path.join(a.out, "fig_guard_g123.pdf"))


if __name__ == "__main__":
    main()
