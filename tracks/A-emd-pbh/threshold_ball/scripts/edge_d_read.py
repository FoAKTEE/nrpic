#!/usr/bin/env python3
"""Entry 13, test D: line ratio of SCOPE section 3 and the rms of H on x in [1.2, 4] at t = 0 for D-ref, D-cic, D-pcs0
against S2-A0; figure of |H| on the x line.   edge_d_read.py --run DIR --ref S2-A0 --out DIR"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edge_compare import line_ratio  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs = {"S2-A0": a.ref}
    for n in ("D-ref", "D-cic", "D-pcs0"):
        runs[n] = os.path.join(a.run, n)
    res, lines = {}, {}
    for n, rd in runs.items():
        lr = line_ratio(rd)
        if not lr:
            continue
        r0 = lr[0]
        lines[n] = r0
        k = (r0["x"] >= 1.2) & (r0["x"] <= 4.0)
        kin = r0["x"] < 0.9
        res[n] = dict(ratio_t0=r0["ratio"], H_rms_1p2_4=float(np.sqrt(np.mean(r0["H"][k] ** 2))),
                      H_rms_inner=float(np.sqrt(np.mean(r0["H"][kin] ** 2))),
                      E16pi_rms_1p2_4=float(np.sqrt(np.mean((16 * math.pi * r0["E"][k]) ** 2))))
    base = res["S2-A0"]
    for n in res:
        res[n]["ratio_rel"] = res[n]["ratio_t0"] / base["ratio_t0"]
        res[n]["Hcoarse_rel"] = res[n]["H_rms_1p2_4"] / base["H_rms_1p2_4"]
    json.dump(res, open(os.path.join(a.out, "edge_d.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(HERE, "..", "..", "periodic_threshold", "scripts"))
    import figstyle as fs
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.5))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.18, top=0.88, wspace=0.3)
    cols = {"S2-A0": "0.2", "D-ref": fs.PAL["yellow"], "D-cic": fs.PAL["blue"], "D-pcs0": fs.PAL["red"]}
    for n, r0 in lines.items():
        ax[0].plot(r0["x"], np.abs(r0["H"]), color=cols[n], lw=0.8, label=f"{n}: ratio {res[n]['ratio_t0']:.3f}")
        ax[1].plot(r0["x"], 16 * math.pi * r0["E"], color=cols[n], lw=0.8, label=n)
    ax[0].set_yscale("log")
    ax[0].set_xlim(0, 6)
    ax[0].set_xlabel("$x/M$ ($t = 0$)")
    ax[0].set_ylabel("$|H|$")
    ax[0].set_title("(a) Hamiltonian residual, S2 on mesh A", fontsize=8)
    ax[0].legend(fontsize=5)
    ax[1].set_xlim(0, 6)
    ax[1].set_xlabel("$x/M$ ($t = 0$)")
    ax[1].set_ylabel(r"$16\pi E$")
    ax[1].set_title("(b) deposited source", fontsize=8)
    ax[1].legend(fontsize=5)
    fig.savefig(os.path.join(a.out, "fig_edge_d.png"), dpi=150)


if __name__ == "__main__":
    main()
