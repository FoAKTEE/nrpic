#!/usr/bin/env python3
"""K3 of threshold_ball (JOURNAL entry 9): where the line's largest |H| sits at early times.

    python -I hpeak.py --out DIR

For each member, every con line output (tab/ball.con.*.tab, x line at y = z = 0.01) with
0.5 <= t <= 6: the x > 0 position of max |H|, its distance to the nearest static refinement
boundary (|x| = 1, 2, 4, 8, 16 M; C-R1.25's deck has outer 16 M, boundaries 1, 2, 4, 8) and to the
nearest density jump of the data (core edge, compensation edge, matter edge in rbar, from the
member's exact.json spec when given, else data set 3's fractions 0.65 and 0.95 of R_b = 4.082 and
the matter edge 4.25), and the local cell width there. Figure: |H|(x) at t ~ 2 and ~ 5 with both
sets of radii marked, and the peak positions against time.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
MEM = {
    "B-d0.42": (S + "/A-20261121-204149-c48bd33", [1, 2, 4, 8, 16]),
    "A-d0.42": (S + "/A-20261121-235851-d2200d7/A-d0.42", [1, 2, 4, 8, 16]),
    "B-d1.00": (S + "/A-20261122-054155-4b3d92e", [1, 2, 4, 8, 16]),
    "C-R1.25": (S + "/A-20261122-141100-f00cfc2", [1, 2, 4, 8]),
}
RB = 4.082
JUMPS = {"B-d0.42": [0.65 * RB, 0.95 * RB, 4.25], "A-d0.42": [0.65 * RB, 0.95 * RB, 4.25],
         "B-d1.00": [0.65 * RB, 0.95 * RB, 4.25],
         # C-R1.25: lam = 1.25 ball (conv_ball DESIGN: R_b 5.10, R1 0.52, R2 0.76, matter edge 5.27)
         "C-R1.25": [0.52 * 5.1025, 0.76 * 5.1025, 5.270]}


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    prof = {}
    for n, (rd, lev) in MEM.items():
        rows = []
        for f in sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab"))):
            t, d = read_tab(f)
            if t < 0.5 or t > 6.0:
                continue
            x = d["x1v"]
            o = np.argsort(x)
            x, H = x[o], np.abs(d["con_H"][o])
            s = x > 0
            x, H = x[s], H[s]
            k = int(np.nanargmax(H))
            dx = np.gradient(x)[k]
            db = min(abs(x[k] - b) for b in lev)
            dj = min(abs(x[k] - j) for j in JUMPS[n])
            rows.append(dict(t=t, x=float(x[k]), H=float(H[k]), cell=float(dx), d_boundary=float(db),
                             d_jump=float(dj)))
            for tt in (2.0, 5.0):
                if abs(t - tt) < 0.13 and (n, tt) not in prof:
                    prof[(n, tt)] = (x, H)
        nb = sum(1 for r in rows if r["d_boundary"] <= 1.5 * r["cell"])
        nj = sum(1 for r in rows if r["d_jump"] <= 0.1)
        res[n] = dict(n_outputs=len(rows), near_boundary=nb, near_jump=nj,
                      other=len(rows) - nb - nj, rows=rows)
        print(n, "outputs", len(rows), "near boundary", nb, "near jump", nj,
              "peak x (first 6):", [round(r["x"], 3) for r in rows[:6]])
    json.dump(res, open(os.path.join(a.out, "hpeak.json"), "w"), indent=1)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.16, top=0.88, wspace=0.32)
    cs = {"B-d0.42": fs.PAL["red"], "A-d0.42": fs.PAL["blue"], "B-d1.00": "k", "C-R1.25": fs.PAL["yellow"]}
    for i, tt in enumerate((2.0, 5.0)):
        ax = axs[i]
        for n in MEM:
            if (n, tt) in prof:
                x, H = prof[(n, tt)]
                ax.semilogy(x, H, color=cs[n], lw=0.8, label=n)
        for b in (1, 2, 4, 8):
            ax.axvline(b, **fs.MASK_LINE)
        for j in JUMPS["B-d0.42"]:
            ax.axvline(j, color=fs.PAL["red"], ls=":", lw=0.8)
        ax.set_xlim(0, 9)
        ax.set_xlabel("x (M)")
        ax.set_ylabel("|H| on the line")
        ax.set_title("t ~ %g: grey level boundaries, dotted jumps" % tt, fontsize=8)
    axs[0].legend(fontsize=7)
    ax = axs[2]
    for n, r in res.items():
        ax.plot([q["t"] for q in r["rows"]], [q["x"] for q in r["rows"]], ".", ms=3, color=cs[n], label=n)
    for b in (1, 2, 4, 8):
        ax.axhline(b, **fs.MASK_LINE)
    for j in JUMPS["B-d0.42"]:
        ax.axhline(j, color=fs.PAL["red"], ls=":", lw=0.8)
    ax.set_xlabel("t (M)")
    ax.set_ylabel("x of max |H|")
    ax.set_title("peak position", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_hpeak.png"), dpi=150)


if __name__ == "__main__":
    main()
