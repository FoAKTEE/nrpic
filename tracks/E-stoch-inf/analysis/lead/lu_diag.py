#!/usr/bin/env python3
"""Lead check L-U2: where does the code's noise field differ from the reference of the
keys? Per mode n and output, the coefficient difference |xi_code - xi_ref| divided by the
base amplitude amp q^-3/2 L^-3/2, against the window increment dW_n of the output step.

For the Markov scheme the coefficient is base sqrt(dW) alpha with dW = W(t) - W(t - dt)
formed as a difference of two numbers close to 1 once a mode has crossed. One unit in the
last place of W (u = 1.1e-16 near 1) changes sqrt(dW) by about u/(2 sqrt(dW)); the line
2 u |alpha|/(2 sqrt(dW)) with |alpha| = 3 is drawn as the conditioning bound.

    lu_diag.py --run DIR --input FILE --out DIR [--run2 DIR --input2 FILE]
Writes lu_diag.json and fig_lu_diag.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "noise", "validate"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "noise", "ref"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))
import athenak_io as aio  # noqa: E402
import noise_ref as nr  # noqa: E402
from validate_noise import Analysed  # noqa: E402
from nrpic import figstyle  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def diag(path, inp):
    run = aio.read_run(path, inp)
    a = Analysed(run)
    p = a.p
    base = nr.base_amplitude(a.lat, p)
    rows = []
    out = {"scheme": p["scheme"], "window": p["window"], "N": a.lat.N, "outputs": {}}
    for key in sorted(a.keys()):
        v, cyc = key
        t = nr.out_time(cyc, p)
        dW = nr.window(a.lat, t, p) - nr.window(a.lat, t - p["dt"], p)
        d = np.abs(a.coef[key] - a.ref[key]) / base
        rms = a.rms_m(key)
        big = dW > 1e-6
        small = (dW > 0) & (dW < 1e-10)
        out["outputs"][f"{v}@{cyc}"] = dict(
            max_rel_rms=float(np.abs(a.coef[key] - a.ref[key]).max() / rms),
            max_diff_dW_gt_1em6=float(d[big].max()) if big.any() else None,
            max_diff_dW_lt_1em10=float(d[small].max()) if small.any() else None,
            n_modes_dW_lt_1em10=int(small.sum()),
            max_diff_over_bound=float(np.max(d[dW > 0] * 2 * np.sqrt(dW[dW > 0]) / (6 * 1.1e-16)))
            if (dW > 0).any() else None)
        rows.append((dW, d, f"{v}@{cyc}"))
    return out, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--run2")
    ap.add_argument("--input2")
    ap.add_argument("--out", required=True)
    x = ap.parse_args()
    os.makedirs(x.out, exist_ok=True)
    res = {}
    figstyle.use_style()
    fig, axs = plt.subplots(1, 2 if x.run2 else 1, figsize=(figstyle.FULL_WIDTH, 3.4),
                            squeeze=False)
    for i, (r, inp) in enumerate([(x.run, x.input)] + ([(x.run2, x.input2)] if x.run2 else [])):
        out, rows = diag(r, inp)
        res[os.path.basename(r.rstrip("/"))] = out
        ax = axs[0, i]
        cols = figstyle.series_colors(len(rows))
        for (dW, d, lab), c in zip(rows, cols):
            m = dW > 0
            ax.loglog(dW[m], np.maximum(d[m], 1e-20), ".", ms=2, color=c, label=lab)
        xx = np.logspace(-17, 0, 100)
        ax.loglog(xx, 6 * 1.1e-16 / (2 * np.sqrt(xx)), **figstyle.GUIDE,
                  label=r"$3\times 2u/(2\sqrt{\Delta W})$")
        ax.set_xlabel(r"window increment $\Delta W_n$ of the output step")
        ax.set_ylabel(r"$|\xi_n^\mathrm{code}-\xi_n^\mathrm{ref}|$ / base$_n$")
        ax.set_title(f"{os.path.basename(r.rstrip('/'))}: {out['scheme']}, {out['window']}")
        ax.set_ylim(1e-20, 1e-6)
        ax.legend(frameon=False, fontsize=6, markerscale=3)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(x.out, "fig_lu_diag"))
    with open(os.path.join(x.out, "lu_diag.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
