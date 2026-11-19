"""Figure of a `kb verify-downloads` inventory (inventory.json of a run).

    kb/.venv/bin/python kb/scripts/fig_inventory.py <inventory.json> <out path without extension>

Top: per group of brief section 16, the manifest entries (grey outline) and the entries
stored and verified ok (filled: blue priority 3, red priority 2, yellow priority 1).
Bottom: sizes of the stored e-prints (source.bin), by content-sniffed kind, extras included.
"""
import json
import os
import sys

import numpy as np

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def main(inv_path, out):
    inv = json.load(open(inv_path))
    papers = inv["papers"]
    groups = sorted({p["group"] for p in papers})
    x = np.arange(len(groups))
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 6.0))
    ax = fig.add_axes([0.09, 0.47, 0.88, 0.47])
    total = np.array([sum(1 for p in papers if p["group"] == g) for g in groups])
    ax.bar(x, total, width=0.8, facecolor="none", edgecolor="grey", lw=1.0, label="in manifest")
    bottom = np.zeros(len(groups))
    for pri, col in ((3, fs.PAL["blue"]), (2, fs.PAL["red"]), (1, fs.PAL["yellow"])):
        n = np.array([sum(1 for p in papers if p["group"] == g and p["priority"] == pri and p["status"] == "ok")
                      for g in groups])
        nall = sum(1 for p in papers if p["priority"] == pri)
        nok = int(n.sum())
        ax.bar(x, n, width=0.8, bottom=bottom, color=col, label=f"ok, priority {pri} ({nok} of {nall})")
        bottom += n
    bad = np.array([sum(1 for p in papers if p["group"] == g and p["status"] in ("problem", "incomplete", "failed"))
                    for g in groups])
    if bad.sum():
        ax.bar(x, bad, width=0.8, bottom=bottom, color="k", label=f"problem, incomplete or failed ({int(bad.sum())})")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=90)
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.set_ylabel("entries")
    ax.set_title(f"verify-downloads {inv['checked_at']}: {inv['arxiv']['status'].get('ok', 0)} of "
                 f"{inv['arxiv']['manifest_rows']} manifest entries ok, {inv['arxiv']['extra']} extra")
    ax.legend(loc="upper left", ncol=2)
    ax.set_ylim(0, total.max() * 1.35)

    ax2 = fig.add_axes([0.09, 0.08, 0.88, 0.25])
    stored = [p for p in papers + inv["extras"] if p.get("bytes")]
    kinds = sorted({p["sniffed_kind"] for p in stored})
    bins = np.logspace(3, 8, 26)
    data = [[p["bytes"] for p in stored if p["sniffed_kind"] == k] for k in kinds]
    cols = [fs.SERIES[i % len(fs.SERIES)] for i in range(len(kinds))]
    ax2.hist(data, bins=bins, stacked=True, color=cols, label=[f"{k} ({len(d)})" for k, d in zip(kinds, data)])
    ax2.set_xscale("log")
    ax2.set_xlabel("size of source.bin [bytes]")
    ax2.set_ylabel("e-prints")
    ax2.legend(loc="upper left")
    fs.save(fig, out)
    print(out + ".png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
