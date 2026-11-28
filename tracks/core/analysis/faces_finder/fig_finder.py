#!/usr/bin/env python3
"""Figure and table of the finder tests on Track A's restart files.

    fig_finder.py --out DIR --f0 RUN --f1 RUN [--f1b RUN] --new RUN [RUN ...]

RUN are output directories of finder_box.py: --f0 the standard flow with verbose
histories (release core-v0.8), --f1 / --f1b the weighted flow with verbose histories
(S1L, P0L6), --new the runs of the new build (start scan, trapped check).  Reads only
summary.json, the status files and the verbose files.  Writes DIR/finder_table.json and
DIR/fig_finder.{pdf,png}: (a) mean radius against flow iteration, standard and weighted
flow from the same start; (b) the mean expansion of the scanned round spheres with the
start radius the scan gives and the radius of the surface found; (c) rms expansion times
area mass (column 16 of the status file) of every member that has it, found or not.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from finder_box import read_verbose  # noqa: E402


def history(run, n):
    f = glob.glob(os.path.join(run, "*.horizon_verbose_%d.txt" % n))
    h = read_verbose(f[0]) if f else []
    return np.array(h[-1]) if h and h[-1] else np.zeros((0, 6))


def scan(run, n):
    f = glob.glob(os.path.join(run, "*.horizon_verbose_%d.txt" % n))
    rows = [ln.split()[1:] for ln in open(f[0]) if ln.startswith("scan ")] if f else []
    return np.array(rows, dtype=float)[:, 1:] if rows else np.zeros((0, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--f0", required=True)
    ap.add_argument("--f1", required=True)
    ap.add_argument("--f1b", default=None)
    ap.add_argument("--new", nargs="+", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    table = []
    for run in [a.f0, a.f1] + ([a.f1b] if a.f1b else []) + a.new:
        s = json.load(open(os.path.join(run, "summary.json")))
        flow = "shear" if any("flow=shear" in ln for ln in
                              open(os.path.join(run, "athena.log")).readlines()[:1]) \
            else "standard"
        for h in s["horizons"]:
            c = h.get("columns_all", [])
            table.append(dict(run=os.path.basename(run.rstrip("/")),
                              rst=os.path.basename(s["rst"]), time=s["header"]["time"],
                              flow=flow, name=h["name"], found=h["found"],
                              reason=h.get("reason"), iterations=h.get("flow_iterations"),
                              area_mass=h.get("area_mass"), meanradius=h.get("meanradius"),
                              minradius=h.get("minradius"),
                              expansion_integral=h.get("mean_expansion"),
                              rms_expansion_x_mass=c[15] if len(c) > 15 else None,
                              scan_start=c[16] if len(c) > 16 else None,
                              scan_trapped=int(c[17]) if len(c) > 17 else None))
    json.dump(table, open(os.path.join(a.out, "finder_table.json"), "w"), indent=1)
    for t in table:
        print("%-28s %-8s %-9s %-52s %d r%s it %4s m %-10.6g r %-8.5g res %s scan %s/%s" % (
            t["run"], t["rst"][5:10], t["flow"], t["name"][:52], t["found"], t["reason"],
            int(t["iterations"] or 0), t["area_mass"] or 0, t["meanradius"] or 0,
            "%.3g" % t["rms_expansion_x_mass"] if t["rms_expansion_x_mass"] is not None
            else "-", t["scan_start"], t["scan_trapped"]))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(4)
    fig, axs = plt.subplots(1, 3, figsize=(13.0, 3.6),
                            gridspec_kw={"width_ratios": [1.0, 1.0, 0.8]})

    ax = axs[0]
    for c, (run, lab) in zip(cols, ((a.f0, "standard flow (default)"),
                                    (a.f1, "weighted flow (flow = shear)"))):
        for n, ls in ((0, "-"), (1, "--"), (2, ":")):
            h = history(run, n)
            if len(h):
                ax.semilogx(h[:, 0] + 1, h[:, 3], ls, color=c, lw=1.1,
                            label=lab if n == 0 else None)
    ax.set_xlabel("flow iteration")
    ax.set_ylabel("mean coordinate radius of the surface")
    ax.set_title("(a) S1L, t = 220: from 0.6, 0.2 and 0.1", fontsize=9)
    ax.legend(fontsize=7)

    ax = axs[1]
    k = 0
    seen = set()
    for run in a.new:
        s = json.load(open(os.path.join(run, "summary.json")))
        for h in s["horizons"]:
            sc = scan(run, h["horizon"])
            if len(sc) == 0:
                continue
            lab = "%s t = %.0f" % ("S1L" if "97bab8d" in s["rst"] else "P0L6",
                                   s["header"]["time"])
            if lab in seen:          # the scan does not depend on the flow function
                break
            seen.add(lab)
            ax.semilogx(sc[:, 0], sc[:, 2] * np.sqrt(sc[:, 1] / (16 * np.pi)), "o-", ms=2.5,
                        lw=0.9, color=cols[k % 4], label=lab)
            c = h.get("columns_all", [])
            if len(c) > 16 and c[16] > 0:
                ax.axvline(c[16], color=cols[k % 4], lw=0.6, ls="--")
            k += 1
            break
    ax.axhline(0.0, color="0.5", lw=0.6)
    ax.set_xlabel("coordinate radius of the round sphere")
    ax.set_ylabel("mean expansion times area mass")
    ax.set_title("(b) start scan (dashed: start radius it gives)", fontsize=9)
    ax.legend(fontsize=7)

    ax = axs[2]
    rows = [t for t in table if t["rms_expansion_x_mass"] is not None
            and t["rms_expansion_x_mass"] > 0]
    y = np.arange(len(rows))
    ax.barh(y, [t["rms_expansion_x_mass"] for t in rows],
            color=[figstyle.PAL["blue"] if t["found"] else figstyle.PAL["red"] for t in rows])
    ax.set_yticks(y)
    ax.set_yticklabels(["%s %s: %s" % (t["rst"][5:10], t["flow"][:5], t["name"][:34])
                        for t in rows], fontsize=5)
    ax.set_xscale("log")
    ax.set_xlabel("rms expansion times area mass")
    ax.set_title("(c) the measure of trapped_tol (blue: found, red: not)", fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_finder"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
