#!/usr/bin/env python3
"""K4 of threshold_ball (JOURNAL entry 10): ||H||_2 and ||M||_2 of the three processor variants
against each other and against conv_ball's card member A.   k4_compare.py --run DIR --out DIR"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from constraint_conv import load  # noqa: E402

CARD_A = "/data/haiyangw/nrpic/scratch/A-emd-pbh/A-20261121-075926-d10c2c1/A"


def series(rd):
    c, z = load(os.path.join(rd, "ball.z4c.user.hst"))
    return z[:, 0], z[:, c.index("H-norm2")], z[:, c.index("M-norm2")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    S = {n: series(os.path.join(a.run, n)) for n in ("K4-ref", "K4-dt", "K4-src")}
    S["card A"] = series(CARD_A)
    res = {}
    for tt in (1.0, 2.0, 3.0, 4.0, 5.0):
        ref = np.interp(tt, S["K4-ref"][0], S["K4-ref"][1])
        res[str(tt)] = {n: float(np.interp(tt, s[0], s[1]) / ref) for n, s in S.items()}
        res[str(tt)]["H_ref"] = float(ref)
    json.dump(res, open(os.path.join(a.out, "k4.json"), "w"), indent=1)
    for k, v in res.items():
        print(k, {n: round(x, 3) for n, x in v.items()})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.9, wspace=0.3)
    cs = {"K4-ref": "k", "K4-dt": fs.PAL["red"], "K4-src": fs.PAL["blue"], "card A": fs.PAL["yellow"]}
    for n, s in S.items():
        sel = s[0] <= 5.0
        axs[0].semilogy(s[0][sel], s[1][sel], color=cs[n], label=n)
        axs[1].semilogy(s[0][sel], s[2][sel], color=cs[n], label=n)
    for ax, lab in ((axs[0], r"$\|H\|_2$"), (axs[1], r"$\|M\|_2$")):
        ax.set_xlabel("t (M)")
        ax.set_ylabel(lab)
    axs[0].legend(fontsize=7)
    axs[0].set_title("K4: step, source extrapolation, build", fontsize=8)
    fig.savefig(os.path.join(a.out, "fig_k4.png"), dpi=150)


if __name__ == "__main__":
    main()
