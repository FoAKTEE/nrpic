#!/usr/bin/env python3
"""Constraint norms of the long runs (g2long entry 8) from <base>.z4c.user.hst.

Columns: 1 time, 3 C-norm2, 4 H-norm2, 5 M-norm2 (volume norms over the whole mesh).
Usage: constraints_long.py --out DIR NAME=RUNDIR:BASE ...
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4), constrained_layout=True)
    cols = fs.series_colors(len(a.runs))
    out = {}
    for c, s in zip(cols, a.runs):
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        h = np.loadtxt(os.path.join(rd, base + ".z4c.user.hst"), comments="#", ndmin=2)
        t, H, M = h[:, 0], h[:, 3], h[:, 4]
        res = {"t_end": float(t[-1])}
        for lab, y in (("H", H), ("M", M)):
            w = t >= 100.0
            y100 = float(np.interp(100.0, t, y))
            jump = 0.0
            for i in np.nonzero(w)[0]:
                j = np.searchsorted(t, t[i] + 10.0)
                if j < t.size:
                    jump = max(jump, float(y[i:j + 1].max() / y[i]))
            res[lab] = dict(at100=y100, end=float(y[-1]), max_after_100=float(y[w].max()),
                            growth=float(y[w].max() / y100), max_jump_10M=jump,
                            finite=bool(np.all(np.isfinite(y))))
        res["holds"] = all(res[k]["growth"] <= 10 and res[k]["max_jump_10M"] <= 3 and res[k]["finite"]
                           for k in ("H", "M"))
        out[name] = res
        ax[0].semilogy(t, H, color=c, lw=1.0, label=name)
        ax[1].semilogy(t, M, color=c, lw=1.0, label=name)
    for x, lab in zip(ax, ("H-norm2", "M-norm2")):
        x.set_xlabel(r"$t/M$")
        x.set_ylabel(lab)
        x.axvline(100.0, **fs.GUIDE)
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_title("(a) Hamiltonian constraint, volume norm", loc="left", fontsize=9)
    ax[1].set_title("(b) momentum constraint, volume norm", loc="left", fontsize=9)
    fs.save(fig, os.path.join(a.out, "constraints_long"))
    with open(os.path.join(a.out, "constraints_long.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
