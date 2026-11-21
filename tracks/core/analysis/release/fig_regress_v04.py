#!/usr/bin/env python3
"""Figure and table of a byte regression made by regress_v04.py.

    fig_regress_v04.py RUNDIR_OF_THE_REGRESSION --out DIR

Reads RUNDIR/summary.json; writes DIR/fig_regress_v04.{pdf,png} (per set-up the number
of compared items in every class) and DIR/regress_table.md (the table of
tracks/core/RELEASE-v0.4.md), and prints the table.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

WHAT = {
    "geo": "test particle in Kerr, analytic metric, midpoint",
    "boris": "the same, spacetime-Boris pusher on the lattice",
    "dep": "deposit on a statically refined flat mesh",
    "east": "periodic cosmology with Z4c, 16^3, 20 steps",
    "os": "Oppenheimer-Snyder ball with Z4c, refined, 3 steps",
    "jeans": "gas with self-gravity, Jeans wave, 20 steps",
    "binary": "gas with self-gravity, four levels, 1 step",
    "c1": "cluster on the analytic Kerr metric, 2000 particles",
    "c2": "static mesh metric, deposit, filter",
    "c3": "cluster on a refined mesh, deposit, excision",
    "c4": "homogeneous universe, Z4c with particle sources",
    "c5": "kick deck with the kick off: restart files, removal",
}
CLASSES = [("identical", "identical", fs.PAL["blue"]),
           ("a", "a: 36 unset restart bytes", fs.PAL["yellow"]),
           ("b", "b: last_time lines of the dump", fs.PAL["green"]),
           ("a+b", "a and b", fs.PAL["orange"]),
           ("other", "other", fs.PAL["red"])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.rundir, "summary.json")) as f:
        s = json.load(f)
    names = list(s["cases"])
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.14, top=0.95)
    y = np.arange(len(names))[::-1]
    left = np.zeros(len(names))
    for key, lab, col in CLASSES:
        n = np.array([len(s["cases"][c][key]) for c in names], dtype=float)
        ax.barh(y, n, left=left, color=col, label=lab, height=0.7)
        left += n
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlabel("compared items (output files; result lines of the log for jeans, "
                  "binary)", labelpad=2)
    # room on the right for the legend, clear of the longest bars
    ax.set_xlim(0, left.max()*1.75)
    ax.set_xticks(np.arange(0, left.max() + 1, 2))
    ax.legend(loc="center right")
    fs.save(fig, os.path.join(a.out, "fig_regress_v04"))
    rows = ["| Set-up | What | Items | identical | a | b | a+b | other | Verdict |",
            "|---|---|---|---|---|---|---|---|---|"]
    for c in names:
        r = s["cases"][c]
        rows.append("| %s | %s | %d | %d | %d | %d | %d | %d | %s |"
                    % (c, WHAT.get(c, ""), r["compared"], len(r["identical"]),
                       len(r["a"]), len(r["b"]), len(r["a+b"]), len(r["other"]),
                       r["verdict"]))
    tot = {k: sum(len(s["cases"][c][k]) for c in names) for k, _, _ in CLASSES}
    rows.append("| all | | %d | %d | %d | %d | %d | %d | %s |"
                % (sum(tot.values()), tot["identical"], tot["a"], tot["b"], tot["a+b"],
                   tot["other"], s["verdict"]))
    text = "\n".join(rows) + "\n"
    with open(os.path.join(a.out, "regress_table.md"), "w") as f:
        f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
