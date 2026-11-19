"""Figure and tally of the verdicts in CHECK.md (work package s31_32).

Reads the markdown tables of CHECK.md, counts the verdicts per brief line and per evidence
label of the brief, writes verdicts.json and fig_verdicts.{pdf,png} into the output directory
($NRPIC_RUN_DIR, or the first argument), and prints the tally. Left: verdicts per brief line.
Right: verdicts per label of the statement in the brief.

Run (registered): harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/kb/brief_check/s31_32 --purpose "..." -- python tracks/kb/brief_check/s31_32/scripts/fig_verdicts.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402  (vendored copy of harness/style/figstyle.py)
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CHECK = os.path.join(os.path.dirname(HERE), "CHECK.md")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "ANSWERED", "NOT FOUND"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "ANSWERED": fs.PAL["green"], "NOT FOUND": "grey"}


def classify(verdict):
    v = verdict.strip()
    if v.startswith("CORRECTED"):
        return "CORRECTED"
    if v.startswith("NOT FOUND"):
        return "NOT FOUND"
    if v.startswith("ANSWERED") or v.startswith("CONFIRMED, specified"):
        return "ANSWERED"
    if v.startswith("CONFIRMED (precision)"):
        return "CONFIRMED (precision)"
    if v.startswith("CONFIRMED"):
        return "CONFIRMED"
    raise ValueError("unknown verdict: %r" % verdict)


def label_class(label):
    lab = label.strip()
    if "VERIFIED" in lab and "unl" not in lab:
        return "[VERIFIED]"
    if "BACKGROUND" in lab:
        return "[BACKGROUND]"
    if "to verify" in lab.lower():
        return "[TO VERIFY] (sec. 15)"
    return "unlabelled"


def read_rows(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            if not re.match(r"^\| \d+ \|", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # columns: #, brief line, quotation, label, verdict, locator, note
            rows.append({"n": int(cells[0]), "line": cells[1], "label": cells[3],
                         "verdict": cells[4], "cls": classify(cells[4]),
                         "lab": label_class(cells[3])})
    return rows


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    rows = read_rows(CHECK)
    nums = [r["n"] for r in rows]
    assert nums == list(range(1, len(rows) + 1)), "row numbers not consecutive"

    lines = []
    for r in rows:
        if r["line"] not in lines:
            lines.append(r["line"])
    lines.sort(key=lambda s: int(s))
    by_line = {l: {c: 0 for c in CLASSES} for l in lines}
    labs = ["[BACKGROUND]", "[VERIFIED]", "unlabelled", "[TO VERIFY] (sec. 15)"]
    short = {"[BACKGROUND]": "BACKGROUND", "[VERIFIED]": "VERIFIED",
             "unlabelled": "no label", "[TO VERIFY] (sec. 15)": "sec. 15 item"}
    by_lab = {l: {c: 0 for c in CLASSES} for l in labs}
    for r in rows:
        by_line[r["line"]][r["cls"]] += 1
        by_lab[r["lab"]][r["cls"]] += 1
    tally = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    corrected = [(r["n"], r["line"]) for r in rows if r["cls"] == "CORRECTED"]
    result = {"rows": len(rows), "tally": tally, "by_line": by_line, "by_label": by_lab,
              "corrected_rows": corrected}
    with open(os.path.join(out, "verdicts.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"rows": len(rows), "tally": tally, "corrected_rows": corrected}))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    ax1 = fig.add_axes([0.09, 0.12, 0.44, 0.80])
    ax2 = fig.add_axes([0.73, 0.12, 0.24, 0.80])
    for ax, keys, table in ((ax1, lines, by_line), (ax2, labs, by_lab)):
        y = list(range(len(keys)))[::-1]
        left = [0] * len(keys)
        for c in CLASSES:
            w = [table[k][c] for k in keys]
            if sum(w) == 0:
                continue
            ax.barh(y, w, left=left, color=COLORS[c], height=0.7, label=c,
                    edgecolor="white", linewidth=0.5)
            left = [a + b for a, b in zip(left, w)]
        ax.set_yticks(y)
        ax.set_yticklabels([short.get(k, k) for k in keys])
        ax.tick_params(axis="y", which="minor", left=False, right=False)
        ax.set_xlabel("statements checked")
    ax1.set_ylabel("brief line")
    ax1.legend(loc="lower right", ncol=1)
    ax1.set_xlim(0, 10)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    plt.close(fig)


if __name__ == "__main__":
    main()
