"""Tally of CHECK.md and figure of the frontier scan (work package s39_frontier).

Usage: python fig_frontier.py <queries.tsv> [<queries.tsv> ...]
Output directory: $NRPIC_RUN_DIR (or ./fig_frontier_out). Runs frontier_scan.py on the query
results (candidates.tsv, abstracts.tsv, queries_summary.tsv, fwd_counts.json), counts the
verdicts of CHECK.md per brief line, writes tally.json and fig_frontier.{pdf,png}:
(a) verdicts per brief line, (b) forward citations of the 32 ids of brief lines 243-255
split into papers the brief cites and papers it does not, (c) papers not cited by the brief per
arXiv month, by the track whose query found them. Prints the tally.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import frontier_scan  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CHECK = os.path.join(os.path.dirname(HERE), "CHECK.md")
ROW_IDS = {
    243: ["2609.14218", "2605.04487"], 244: ["2610.23218"], 245: ["2608.13206", "2609.03051"],
    246: ["2603.24838", "2606.05479", "2606.18437"], 247: ["2607.17929", "2603.24179", "2508.20606"],
    248: ["2501.13046", "2509.26470", "2607.21308"], 249: ["2512.13673", "2607.06441"],
    250: ["2401.08530", "2512.14649", "2610.32592"], 251: ["2606.14853", "2604.00978", "2506.11795"],
    252: ["2404.16270", "2402.02178", "2610.13294"], 253: ["2505.01495", "2511.20567"],
    254: ["2611.12831", "2504.15978", "2509.19769"], 255: ["2601.17117", "2506.17641"]}
TRACK_OF_ROW = {243: "A", 244: "A", 245: "A", 246: "B", 247: "B", 248: "A", 249: "E", 250: "E",
                251: "E", 252: "F", 253: "F", 254: "core", 255: "C"}
ORDER = ["A", "B", "C", "D", "E", "F", "core"]
ROW_OF_ID = {i: r for r, ids in ROW_IDS.items() for i in ids}


def tag_track(tag):
    if tag.startswith("fwd "):
        return TRACK_OF_ROW[ROW_OF_ID[tag.split()[1]]]
    m = re.match(r"r(\d{3})$", tag)
    if m:
        return TRACK_OF_ROW[int(m.group(1))]
    return {"rA": "A", "rB": "B", "rC": "C", "rD": "D", "rE": "E", "rF": "F", "rX": "core"}[tag]


def check_tally():
    rows = []
    with open(CHECK) as fh:
        for l in fh:
            m = re.match(r"\|\s*(\d+)\s*\|\s*(\d{3})\s*\|", l)
            if not m:
                continue
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            v = cells[4]
            if v.startswith("CONFIRMED (precision") or v.startswith("CONFIRMED (prec"):
                cls = "CONFIRMED (precision)"
            elif v.startswith("CONFIRMED"):
                cls = "CONFIRMED"
            elif v.startswith("CORRECTED"):
                cls = "CORRECTED"
            elif v.startswith("NOT FOUND"):
                cls = "NOT FOUND"
            else:
                cls = "?"
            rows.append((int(m.group(1)), int(m.group(2)), cls))
    return rows


def main(tsvs):
    out = os.environ.get("NRPIC_RUN_DIR", os.path.abspath("fig_frontier_out"))
    os.makedirs(out, exist_ok=True)
    frontier_scan.main(list(tsvs) + ["--out", out])
    with open(os.path.join(out, "fwd_counts.json")) as fh:
        fwd = json.load(fh)
    cands = []
    with open(os.path.join(out, "candidates.tsv")) as fh:
        next(fh)
        for l in fh:
            p = l.rstrip("\n").split("\t")
            cands.append({"id": p[0], "month": p[1], "in_brief": p[2] == "1", "tags": p[6].split(",")})
    rows = check_tally()
    classes = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
    per_line = {}
    for _n, line, cls in rows:
        per_line.setdefault(line, {c: 0 for c in classes})[cls] += 1
    tally = {c: sum(1 for r in rows if r[2] == c) for c in classes}
    tally["rows"] = len(rows)
    tally["unclassified"] = sum(1 for r in rows if r[2] == "?")
    months = ["2025-%02d" % m for m in range(1, 13)] + ["2026-%02d" % m for m in range(1, 12)]
    hist = {t: [0] * len(months) for t in ORDER}
    n_old = 0
    for c in cands:
        if c["in_brief"]:
            continue
        if c["month"] not in months:
            n_old += 1
            continue
        tracks = sorted(set(tag_track(t) for t in c["tags"]), key=ORDER.index)
        hist[tracks[0]][months.index(c["month"])] += 1
    tally["not_in_brief_by_track_since_2025"] = {t: sum(v) for t, v in hist.items()}
    tally["not_in_brief_before_2025"] = n_old
    tally["fwd"] = fwd
    with open(os.path.join(out, "tally.json"), "w") as fo:
        json.dump(tally, fo, indent=1, sort_keys=True)

    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 4.2),
                            gridspec_kw={"width_ratios": [1.0, 1.5, 1.6]})
    colors = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
              "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey"}
    ax = axs[0]
    lines = sorted(per_line)
    left = [0] * len(lines)
    for c in classes:
        vals = [per_line[l][c] for l in lines]
        ax.barh(range(len(lines)), vals, left=left, color=colors[c], label=c, height=0.7)
        left = [a + b for a, b in zip(left, vals)]
    ax.set_yticks(range(len(lines)))
    ax.set_yticklabels([str(l) for l in lines])
    ax.invert_yaxis()
    ax.set_xlabel("statements checked")
    ax.set_ylabel("brief line")
    ax.set_xlim(0, 4.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.13), ncol=2, fontsize=7, frameon=False)
    ax.set_title("(a) verdicts, lines 239-255", fontsize=9)

    ax = axs[1]
    ids = [i for r in sorted(ROW_IDS) for i in ROW_IDS[r]]
    ib = [fwd.get(i, {}).get("in_brief", 0) for i in ids]
    nb = [fwd.get(i, {}).get("not_in_brief", 0) for i in ids]
    x = range(len(ids))
    ax.bar(x, ib, color=fs.PAL["blue"], label="cited in the brief")
    ax.bar(x, nb, bottom=ib, color=fs.PAL["orange"], label="not cited in the brief")
    ax.set_xticks(list(x))
    ax.set_xticklabels(ids, rotation=90, fontsize=6)
    ax.set_ylabel("citing papers (INSPIRE)")
    ax.legend(loc="upper left", fontsize=7, frameon=False)
    ax.set_title("(b) forward citations of the 32 ids", fontsize=9)

    ax = axs[2]
    bottom = [0] * len(months)
    # categorical colours (seven tracks: the five of the palette, PAL2 sky, grey for core)
    tcol = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"],
            fs.PAL2["sky"], "grey"]
    for t, col in zip(ORDER, tcol):
        ax.bar(range(len(months)), hist[t], bottom=bottom, color=col, label=t, width=0.85)
        bottom = [a + b for a, b in zip(bottom, hist[t])]
    ax.set_xticks(range(0, len(months), 2))
    ax.set_xticklabels(months[::2], rotation=90, fontsize=6)
    ax.axvline(months.index("2026-11") - 0.5, **fs.MASK_LINE)  # month of the brief's survey
    ax.set_ylabel("papers not cited in the brief")
    ax.legend(loc="upper left", fontsize=7, frameon=False, ncol=2)
    ax.set_title("(c) new papers per arXiv month, by track", fontsize=9)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_frontier"))
    print(json.dumps({k: v for k, v in tally.items() if k != "fwd"}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main(sys.argv[1:])
