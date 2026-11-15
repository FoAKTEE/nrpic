#!/usr/bin/env python3
"""Figure of Test 4 (AthenaK smoke test) from smoke_athenak.py output.

    python3 fig_smoke.py --run DIR --out FIGDIR
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evstatic  # noqa: E402,F401
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from nrpic import figstyle as fs  # noqa: E402
from smoke_athenak import read_hst  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    ax1 = fig.add_axes([0.12, 0.16, 0.36, 0.74])
    ax2 = fig.add_axes([0.58, 0.16, 0.40, 0.74])
    cases = (("new", "King $y_{\\max}$ (this package)", fs.PAL["red"]),
             ("ref_st0819", "monoenergetic $y_c=0.819$ (make_ic.py)", fs.PAL["blue"]))
    for i, (name, lab, c) in enumerate(cases):
        cz, rz = read_hst(os.path.join(a.run, name, "smoke.z4c.user.hst"))
        z = dict(zip(cz, np.array(rz).T))
        V = z["Volume"][0]
        vals = [np.sqrt(z["H-norm2"][0] / V), np.sqrt(z["M-norm2"][0] / V)]
        ax1.bar(np.arange(2) + (i - 0.5) * 0.35, vals, width=0.35, color=c, label=lab)
        cn, rn = read_hst(os.path.join(a.run, name, "smoke.nrpic.hst"))
        n = dict(zip(cn, np.array(rn).T))
        ax2.plot(n["ncycle"], n["sum_mW"] / n["sum_mW"][0] - 1, "-o", color=c, ms=3,
                 label=f"{lab.split(' (')[0]}: $\\sum mW$")
        ax2.plot(n["ncycle"], n["int_E"] / n["sum_mW"][0] - 1, "--s", color=c, ms=3, mfc="none",
                 label="$\\int E\\sqrt{\\gamma}\\,dV$")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["$\\|H\\|_2$ at $t=0$", "$\\|M\\|_2$ at $t=0$"])
    ax1.set_yscale("log")
    ax1.set_ylim(3e-6, 3e-4)
    ax1.set_ylabel("volume-normalised norm")
    ax1.legend(loc="upper right", fontsize=7, ncol=1)
    ax2.set_xlabel("cycle")
    ax2.set_ylabel("relative to $\\sum mW$ at $t=0$")
    ax2.legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(a.out, "athenak_smoke"))
    print("ok")


if __name__ == "__main__":
    sys.exit(main())
