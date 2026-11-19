"""Figure of the lead's equation checks L10 and L11 (tracks/kb/JOURNAL.md, lead entry).

    kb/.venv/bin/python -I kb/scripts/fig_lead_equations.py L10.tsv L11.tsv <out stem>

Left: numbered equation rows in the database against an independent count of numbered
display lines (shorthands defined through \\nc expanded), before (open) and after (filled)
the alias fix. Right: equation rows gained by the composite-shorthand fix against the
number of uses of the shorthand in the paper's files (comments and definitions excluded).
Points on the dashed line agree exactly; axes are log(1 + n).
"""
import csv
import os
import sys

import numpy as np

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def read(p):
    with open(p) as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main(l10, l11, out):
    fs.use_style()
    a, b = read(l10), read(l11)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    x = np.array([int(r["independent"]) for r in a])
    y0 = np.array([int(r["rows_before"]) for r in a])
    y1 = np.array([int(r["rows_after"]) for r in a])
    t = np.linspace(0, 2.4, 10)
    for ax in (ax1, ax2):
        ax.plot(10 ** t - 1, 10 ** t - 1, **fs.GUIDE, label="equal")
        ax.set_xscale("symlog", linthresh=1)
        ax.set_yscale("symlog", linthresh=1)
        ax.set_xlim(-0.3, 300)
        ax.set_ylim(-0.3, 300)
    ax1.plot(x, y0, "o", mfc="none", mec=fs.PAL["red"], ms=7, label="before the fix")
    ax1.plot(x, y1, "o", color=fs.PAL["blue"], ms=4, label="after the fix")
    ax1.set_xlabel("independent count of numbered lines")
    ax1.set_ylabel("numbered equation rows in the database")
    ax1.set_title(r"L10: \nc{\beq}{\begin{equation}} (7 papers)", fontsize=10)
    ax1.legend(loc="upper left", frameon=False)
    u = np.array([int(r["uses"]) for r in b])
    g = np.array([int(r["rows_after"]) - int(r["rows_before"]) for r in b])
    ax2.plot(u, g, "o", color=fs.PAL["blue"], ms=4, label="gain after the fix")
    ax2.set_xlabel("uses of the composite shorthand")
    ax2.set_ylabel("equation rows gained")
    ax2.set_title(r"L11: \bea = equation + aligned (20 papers)", fontsize=10)
    ax2.legend(loc="upper left", frameon=False)
    fig.savefig(out + ".png", dpi=200)
    fig.savefig(out + ".pdf")
    print(f"written {out}.png/.pdf; L10 after==independent: {int(np.sum(y1 == x))}/{len(x)}; "
          f"L11 gain==uses: {int(np.sum(g == u))}/{len(u)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
