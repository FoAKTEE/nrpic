#!/usr/bin/env python3
"""Size of the differences in a run of regress_v04.py that is not byte-identical (the
threaded build): every history (*.hst) of DIR/<case>/base against DIR/<case>/new.

    hst_pair_v06.py REGRESSION_RUN_DIR --out DIR

Per history: the largest difference of a column over the largest magnitude of the
column, for the columns above 1e-6 of the largest column of the file, and the largest
absolute difference of the other columns (card_v06.hst_pair).  Writes DIR/hst_pair.json
and DIR/fig_hst_pair.{pdf,png}.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "python")))
import card_v06 as cv                          # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.run, "summary.json")) as f:
        summ = json.load(f)
    rep = {}
    for case in summ["cases"]:
        base = os.path.join(a.run, case, "base")
        for p in sorted(glob.glob(os.path.join(base, "**", "*.hst"), recursive=True)):
            rel = os.path.relpath(p, base)
            q = os.path.join(a.run, case, "new", rel)
            rep["%s/%s" % (case, rel)] = (cv.hst_pair(q, p) if os.path.exists(q)
                                          else dict(error="missing"))
    def n(x):
        return len(x) if isinstance(x, (list, dict)) else int(x)

    nid = sum(n(v["identical"]) for v in summ["cases"].values())
    nall = sum(n(v["identical"]) + n(v["a"]) + n(v["b"]) + n(v["a+b"]) + n(v["other"])
               for v in summ["cases"].values())
    out = dict(run=a.run, identical=nid, items=nall, hst=rep,
               exits={c: v["exit"] for c, v in summ["cases"].items()})
    with open(os.path.join(a.out, "hst_pair.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k, v in rep.items():
        print("%-28s %s" % (k, v))
    print("identical items: %d of %d" % (nid, nall))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 2.6))
    names = list(rep)
    x = np.arange(len(names))
    ax.bar(x, [max(rep[n].get("rel_large", 1.0), 1e-18) for n in names],
           color=fs.PAL["blue"])
    ax.set_yscale("log")
    ax.set_ylim(1e-18, 1e-6)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=4, rotation=60, ha="right")
    ax.set_ylabel("threaded against serial:\nlargest column difference / column",
                  fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_hst_pair"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
