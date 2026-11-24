#!/usr/bin/env python3
"""Constraint norms against time on the three meshes (G2 items C3 and C12 of Track A):
the volume L2 norms of H and M (<base>.z4c.user.hst) and the mean |H| (cstat) of conv_ball's
members A (M/16), B (M/32), C (M/64) at delta_c = 1.5, and of the threshold pair B-d0.42 /
B-d0.40 and A-d0.42; ratios between meshes at fixed times before the horizon forms.

    python -I constraint_conv.py --out DIR

Norms are read as AthenaK writes them (H-norm2 = sqrt of the volume integral of H^2 over the
whole domain; the interior of the horizon is included after it forms, so only t < 10.5 counts
for the delta_c = 1.5 convergence; first detection at 10.75-10.88). Repeated times after a
restart: the records written last win.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
RUNS = {
    "A (M/16)": S + "/A-20261121-075926-d10c2c1/A",
    "B (M/32)": S + "/A-20261121-075926-d10c2c1/B",
    "C (M/64)": S + "/A-20261121-083336-6a82131",
}
NLEG = {       # entry 7 (K2): particle-number leg at fixed mesh
    "A x1": S + "/A-20261121-075926-d10c2c1/A",
    "A x8": S + "/A-20261121-075926-d10c2c1/A-N8",
    "A x64": S + "/A-20261121-091934-ac62f5f/A-N64",
    "B x1": S + "/A-20261121-075926-d10c2c1/B",
    "B x8": S + "/A-20261121-091934-ac62f5f/B-N8",
}
THR = {
    "B-d0.42": S + "/A-20261121-204149-c48bd33",
    "A-d0.42": S + "/A-20261121-235851-d2200d7/A-d0.42",
    "B-d0.40": S + "/A-20261121-204250-0bf45c7",
}


def load(path):
    cols = []
    with open(path) as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            if "[1]=" in ln:
                cols = [c.split("=")[1] for c in ln.strip("# \n").split() if "=" in c]
    d = np.loadtxt(path, comments="#", ndmin=2)
    keep, tn = [], np.inf
    for i in range(len(d) - 1, -1, -1):
        if d[i, 0] < tn:
            keep.append(i)
            tn = d[i, 0]
    return cols, d[keep[::-1]]


def series(rd):
    cz, z = load(os.path.join(rd, "ball.z4c.user.hst"))
    cs, c = load(os.path.join(rd, "ball.cstat.hst"))
    return dict(t=z[:, 0], H=z[:, cz.index("H-norm2")], M=z[:, cz.index("M-norm2")],
                tc=c[:, 0], Hmean=c[:, cs.index("H_mean")], Hrmean=c[:, cs.index("Hr_mean")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    D = {k: series(v) for k, v in RUNS.items()}
    T = {k: series(v) for k, v in THR.items()}
    NL = {k: series(v) for k, v in NLEG.items()}
    res = {"times": {}, "orders": {}}
    keys = list(RUNS)
    for tt in (0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0):
        row = {}
        for k in keys:
            d = D[k]
            row[k] = dict(H=float(np.interp(tt, d["t"], d["H"])), M=float(np.interp(tt, d["t"], d["M"])),
                          Hmean=float(np.interp(tt, d["tc"], d["Hmean"])))
        res["times"][str(tt)] = row
        for q in ("H", "M", "Hmean"):
            v = [row[k][q] for k in keys]
            res["orders"].setdefault(q, {})[str(tt)] = [float(np.log2(v[0] / v[1])), float(np.log2(v[1] / v[2]))]
    # K2: factor per x8 particles at fixed mesh
    res["nleg"] = {}
    for tt in (1.0, 2.0, 4.0, 6.0, 8.0):
        r = {}
        for lo, hi in (("A x1", "A x8"), ("A x8", "A x64"), ("B x1", "B x8")):
            for q in ("H", "M"):
                v0 = float(np.interp(tt, NL[lo]["t"], NL[lo][q]))
                v1 = float(np.interp(tt, NL[hi]["t"], NL[hi][q]))
                r[f"{q} {lo}->{hi}"] = v0 / v1
        res["nleg"][str(tt)] = r
        print("K2 t=%g" % tt, {k: round(v, 2) for k, v in r.items()})
    json.dump(res, open(os.path.join(a.out, "constraint_conv.json"), "w"), indent=1)
    for q in ("H", "M", "Hmean"):
        print(q, {t: [round(x, 2) for x in o] for t, o in res["orders"][q].items()})
    for tt in ("0.0", "2.0", "8.0", "10.0"):
        print(tt, {k: {q: "%.3e" % v for q, v in r.items()} for k, r in res["times"][tt].items()})

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH * 1.3, 3.0))
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.16, top=0.88, wspace=0.35)
    cs = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"]]
    for i, k in enumerate(keys):
        d = D[k]
        axs[0].semilogy(d["t"], d["H"], color=cs[i], label=k)
        axs[1].semilogy(d["t"], d["M"], color=cs[i], label=k)
    for ax, lab in ((axs[0], r"$\|H\|_2$"), (axs[1], r"$\|M\|_2$")):
        ax.axvspan(10.7, 16, color="0.92", zorder=0)
        ax.set_xlabel("t (M)")
        ax.set_ylabel(lab)
    axs[0].set_title(r"(a) $\delta_c = 1.5$, three meshes; grey: after the horizon", fontsize=8)
    axs[0].legend(fontsize=7)
    axs[1].set_title("(b) momentum constraint", fontsize=8)
    cs2 = [fs.PAL["red"], fs.PAL["blue"], "k"]
    for i, (k, d) in enumerate(T.items()):
        axs[2].semilogy(d["t"], d["H"], color=cs2[i], label=k)
    axs[2].set_xlabel("t (M)")
    axs[2].set_ylabel(r"$\|H\|_2$")
    axs[2].set_title("(c) threshold members", fontsize=8)
    axs[2].legend(fontsize=7)
    cs3 = {"A x1": (fs.PAL["blue"], "-"), "A x8": (fs.PAL["blue"], "--"), "A x64": (fs.PAL["blue"], ":"),
           "B x1": (fs.PAL["red"], "-"), "B x8": (fs.PAL["red"], "--")}
    for k, d in NL.items():
        sel = d["t"] <= 10.5
        axs[3].semilogy(d["t"][sel], d["H"][sel], color=cs3[k][0], ls=cs3[k][1], label=k)
    axs[3].set_xlabel("t (M)")
    axs[3].set_ylabel(r"$\|H\|_2$")
    axs[3].set_title("(d) particle number at fixed mesh", fontsize=8)
    axs[3].legend(fontsize=7)
    fig.savefig(os.path.join(a.out, "fig_constraint_conv.png"), dpi=150)


if __name__ == "__main__":
    main()
