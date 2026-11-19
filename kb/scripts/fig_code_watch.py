#!/usr/bin/env python3
"""Figure of one `kb watch upstream` snapshot (test P5).

    kb/.venv/bin/python -I kb/scripts/fig_code_watch.py SNAPSHOT.json OUT_WITHOUT_EXT

Top: every branch tip of IAS-Astrophysics/athenak at its commit date against the number of
files in src/particles; blue = the stock particle module (no z4c/adm/tmunu/deposit line),
yellow = src/particles reads the metric (z4c/adm lines), red = src/particles mentions tmunu
or deposit (matter handed to the spacetime). Bottom: number of such lines per branch, for the
branches that have any.
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(WT, "python"))
import numpy as np                     # noqa: E402
import matplotlib.pyplot as plt        # noqa: E402
import matplotlib.dates as mdates      # noqa: E402
from nrpic import figstyle as fs       # noqa: E402


def main(snap_path, out):
    s = json.load(open(snap_path))
    insp = s["inspection"]
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 5.6))
    ax = fig.add_axes([0.08, 0.50, 0.89, 0.44])
    groups = {"stock": [], "metric": [], "back": []}
    for b, d in insp.items():
        t = dt.datetime.fromisoformat(d["commit_date"])
        cat = "back" if d["backreaction_hits"] else ("metric" if d["metric_hits"] else "stock")
        groups[cat].append((t, len(d["particles_files"]), b))
    rng = np.random.default_rng(0)
    for cat, col, lab in (("stock", fs.PAL["blue"], "stock particle module"),
                          ("metric", fs.PAL["yellow"], "src/particles reads the metric (z4c, adm)"),
                          ("back", fs.PAL["red"], "src/particles mentions tmunu or deposit")):
        g = groups[cat]
        if g or cat == "back":
            ax.scatter([x[0] for x in g], [x[1] + rng.uniform(-0.15, 0.15) for x in g], s=14, color=col,
                       label=f"{lab} ({len(g)})", zorder=3, edgecolor="k" if cat != "stock" else "none", lw=0.4)
    m = insp.get(s["default_branch"])
    if m:
        ax.scatter([dt.datetime.fromisoformat(m["commit_date"])], [len(m["particles_files"])], s=80,
                   facecolor="none", edgecolor="k", lw=1.0, label=f"main {m['sha'][:7]}", zorder=4)
    for t, n, b in groups["metric"] + groups["back"]:
        if b in ("particles_gr", "flash-beam"):
            ax.annotate(b, (t, n), xytext=(4, 4), textcoords="offset points", fontsize=7)
    ax.set_ylabel("files in src/particles")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.legend(loc="upper left", fontsize=7)
    ax.set_title(f"{s['repo']}: {len(insp)} branch tips, watch {s['at']}", fontsize=10)
    ax2 = fig.add_axes([0.30, 0.08, 0.67, 0.32])
    hit = sorted((b for b, d in insp.items() if d["coupling_hits"]), key=lambda b: -len(insp[b]["coupling_hits"]))
    y = np.arange(len(hit))[::-1]
    ax2.barh(y - 0.18, [len(insp[b]["metric_hits"]) for b in hit], height=0.36, color=fs.PAL["yellow"],
             label="z4c / adm lines")
    ax2.barh(y + 0.18, [len(insp[b]["backreaction_hits"]) for b in hit], height=0.36, color=fs.PAL["red"],
             label="tmunu / deposit lines")
    ax2.set_yticks(y)
    ax2.set_yticklabels(hit, fontsize=7)
    ax2.tick_params(axis="y", which="minor", left=False, right=False)
    ax2.set_xlabel("matching lines in src/particles")
    ax2.legend(loc="lower right", fontsize=7)
    fs.save(fig, out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
