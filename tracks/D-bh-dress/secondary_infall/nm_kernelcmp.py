#!/usr/bin/env python3
"""Compare measured clump kernels f(q) = g_r r^2/M, q = r/dx (nm_field.py tables): the
clump at a mesh vertex (wave 2) against the clump at a cell centre (wave 3). Prints the
median kernels and their ratio in q bins and draws them. Analysis of AthenaK output only.

Usage: python3 nm_kernelcmp.py --k LABEL:FILE [--k ...] --ratio NUM_LABEL:DEN_LABEL [...] --out DIR
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import load_figstyle   # noqa: E402

QB = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 8.0, 16.0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--k", action="append", required=True)
    ap.add_argument("--ratio", action="append", default=[])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    K = {}
    for spec in a.k:
        lab, fn = spec.split(":", 1)
        t = np.loadtxt(fn)
        K[lab] = dict(q=t[:, 0], f=t[:, 1], lo=t[:, 2], hi=t[:, 3], file=fn)
    res = dict(kernels={k: v["file"] for k, v in K.items()}, at_q={}, ratios={})
    for lab, k in K.items():
        res["at_q"][lab] = {f"{q:g}": float(np.exp(np.interp(np.log(q), np.log(k["q"]), np.log(np.maximum(k["f"], 1e-300)))))
                            for q in QB if k["q"][0] <= q <= k["q"][-1]}
    for spec in a.ratio:
        n, d = spec.split(":")
        res["ratios"][spec] = {q: res["at_q"][n][q] / res["at_q"][d][q] for q in res["at_q"][n] if q in res["at_q"][d]}
    with open(os.path.join(a.out, "nm_kernelcmp.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    fs = load_figstyle()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 5.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.10, top=0.98, hspace=0.05)
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"]]
    sty = ["-", "--", "-", "--"]
    for i, (lab, k) in enumerate(K.items()):
        axs[0].plot(k["q"], k["f"], sty[i % 4], color=cols[i % 4], lw=1.2, label=lab)
        axs[0].fill_between(k["q"], k["lo"], k["hi"], color=cols[i % 4], alpha=0.12, lw=0)
    qq = np.geomspace(0.02, 32, 200)
    axs[0].plot(qq, np.ones_like(qq), **fs.GUIDE, label="point mass")
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_ylim(1e-4, 2.0)
    axs[0].set_ylabel(r"$f(q) = g_r r^2/(GM)$")
    axs[0].legend(fontsize=7, loc="lower right")
    for i, spec in enumerate(a.ratio):
        n, d = spec.split(":")
        kn, kd = K[n], K[d]
        q = kn["q"][(kn["q"] >= kd["q"][0]) & (kn["q"] <= kd["q"][-1])]
        fn_ = np.interp(np.log(q), np.log(kn["q"]), kn["f"])
        fd_ = np.interp(np.log(q), np.log(kd["q"]), kd["f"])
        axs[1].plot(q, fn_ / fd_, color=cols[(2 * i) % 4], lw=1.2, label=f"{n} / {d}")
    axs[1].axhline(1, **fs.GUIDE)
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$q = r/\Delta x$")
    axs[1].set_ylabel("ratio")
    axs[1].legend(fontsize=7)
    fs.save(fig, os.path.join(a.out, "nm_kernelcmp"))


if __name__ == "__main__":
    main()
