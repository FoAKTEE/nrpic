#!/usr/bin/env python3
"""Summary figure of the package faces: the Hamiltonian residual against time in the
interior and over the whole box, before (stock conditions) and after (the recommended
options), for the expanding ball, the vacuum puncture and the boosted puncture.

    analyze_summary.py <spec.json> --out results/summary.json --fig figs/summary

spec.json: {"rows": [{"title": "...", "lines": [{"label": "...", "json": "<analyze_evo
output>", "case": "<case name in it>", "style": "stock|new|ref|other"}]}]}
Paths of "json" are relative to the spec file.  Columns: inner (ball r < 8, punctures
5 <= r < 8), shell 8 <= r < 12, whole box (punctures r >= 5).  The table of the output
lists the mean |H| of each line at t = 2, 4, 8 and at its last dump.
"""

import argparse
import json
import os

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import flib  # noqa: F401,E402  (puts python/ on the path)
from nrpic import figstyle as fs  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("spec")
    p.add_argument("--out", required=True)
    p.add_argument("--fig", required=True)
    a = p.parse_args()
    base = os.path.dirname(os.path.abspath(a.spec))
    spec = json.load(open(a.spec))
    cache = {}
    sty = {"stock": dict(color=fs.PAL["red"], ls="-"),
           "new": dict(color=fs.PAL["blue"], ls="-"),
           "ref": dict(color="0.4", ls="--"),
           "other": dict(color=fs.PAL["yellow"], ls="-")}
    rows = spec["rows"]
    fs.use_style()
    fig, axs = plt.subplots(len(rows), 3, figsize=(fs.FULL_WIDTH, 2.2 * len(rows) + 0.4),
                            sharex="row", squeeze=False)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.07, top=0.95, wspace=0.3,
                        hspace=0.32)
    table = {}
    others = 0
    for i, row in enumerate(rows):
        for ln in row["lines"]:
            path = os.path.join(base, ln["json"])
            if path not in cache:
                cache[path] = json.load(open(path))
            h = cache[path]["cases"].get(ln["case"])
            if not h:
                continue
            t = np.array(h["time"])
            st = dict(sty[ln.get("style", "other")])
            if ln.get("style") == "other":
                st["color"] = [fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]][others % 3]
                others += 1
            row_tab = {}
            for j, reg in enumerate(("inner", "shell", "all")):
                v = np.array(h[f"H.{reg}.mean"])
                axs[i, j].semilogy(t, np.maximum(v, 1e-20), lw=1.2, label=ln["label"], **st)
                for tq in (2.0, 4.0, 8.0, float(t.max())):
                    k = int(np.argmin(np.abs(t - tq)))
                    row_tab[f"{reg}@{t[k]:g}"] = float(v[k])
            table[f"{row['title']} | {ln['label']}"] = row_tab
        axs[i, 0].set_ylabel(r"mean $|H|$")
        r0 = "0" if "ball" in row["title"] else "5"
        for j, ttl in enumerate((rf"{row['title']}: ${r0} \leq r < 8$", r"$8 \leq r < 12$",
                                 rf"whole box, $r \geq {r0}$")):
            axs[i, j].set_title(ttl, fontsize=9)
        axs[i, 0].legend(fontsize=6.5, loc="lower right")
    for j in range(3):
        axs[-1, j].set_xlabel(r"$t$", labelpad=-1)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(table, f, indent=1)
    for k, v in table.items():
        print(k)
        print("   ", "  ".join(f"{kk} {vv:.2e}" for kk, vv in v.items()))
    fs.save(fig, a.fig)


if __name__ == "__main__":
    main()
