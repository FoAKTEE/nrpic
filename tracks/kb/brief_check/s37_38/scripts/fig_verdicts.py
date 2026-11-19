"""Tally, locator check and figure of the verdicts in CHECK.md (work package s37_38; adapted copy of s34_36's script).

Reads the markdown tables of CHECK.md and
  1. checks that the rows are numbered 1..N without gaps and that the totals stated in the
     header ("Totals: N rows; a CONFIRMED, b CONFIRMED (precision), c CORRECTED, d NOT FOUND")
     equal the tally of the verdict column;
  2. checks every locator of the locator column: a TeX locator `<key>/<v>/src/<file>:<lines>`
     must name an existing file under kb-data/raw/arxiv whose length covers every line number
     given; a metadata locator `meta:arxiv-api/<id>` or `meta:inspire/<id>` (and the short
     forms `/<id>` that follow it) must name an existing file under kb-data/meta;
  3. counts the verdicts per brief line and per evidence label and draws them.
Writes verdicts.json and fig_verdicts.{pdf,png} into $NRPIC_RUN_DIR (or the first argument)
and prints the tally. Exit status 1 if a check fails. Files under kb-data are only opened
for reading and counted in lines; nothing there is executed or imported.

Run (registered): harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/kb/brief_check/s37_38 --purpose "..." -- python tracks/kb/brief_check/s37_38/scripts/fig_verdicts.py
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
KB = "/data/haiyangw/nrpic/kb-data"
RAW = os.path.join(KB, "raw", "arxiv")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey"}


def classify(verdict):
    v = verdict.strip()
    for c in ("CORRECTED", "NOT FOUND", "CONFIRMED (precision)", "CONFIRMED"):
        if v.startswith(c):
            return c
    raise ValueError("unknown verdict: %r" % verdict)


def label_class(label):
    lab = label.strip()
    if lab.startswith("[VERIFIED]"):
        return "[VERIFIED]"
    if lab.startswith("[BACKGROUND]"):
        return "[BACKGROUND]"
    if lab.startswith("[TO VERIFY]"):
        return "[TO VERIFY]"
    if lab.startswith("[title only verified]"):
        return "[title only verified]"
    if lab.startswith("(unl.)"):
        return "unlabelled"
    raise ValueError("unknown label: %r" % label)


def read_rows(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            if not re.match(r"^\| \d+ \|", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # columns: #, brief line, quotation, label, verdict, locator, note
            if len(cells) != 7:
                raise ValueError("row with %d cells: %s" % (len(cells), line[:80]))
            rows.append({"n": int(cells[0]), "line": cells[1], "label": cells[3],
                         "verdict": cells[4], "cls": classify(cells[4]),
                         "lab": label_class(cells[3]), "loc": cells[5]})
    return rows


def header_totals(path):
    text = open(path).read().replace("\n", " ")
    m = re.search(r"Totals: (\d+) rows; (\d+) CONFIRMED, (\d+) CONFIRMED \(precision\), "
                  r"(\d+) CORRECTED, (\d+) NOT FOUND", text)
    if not m:
        raise ValueError("no totals sentence in the header")
    n, a, b, c, d = (int(x) for x in m.groups())
    return n, {"CONFIRMED": a, "CONFIRMED (precision)": b, "CORRECTED": c, "NOT FOUND": d}


def line_numbers(spec):
    """'38-46, 320-328' -> [38, 46, 320, 328]"""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        for x in part.split("-"):
            out.append(int(x))
    return out


NLINES = {}


def nlines(path):
    if path not in NLINES:
        with open(path, "rb") as fh:
            NLINES[path] = fh.read().count(b"\n") + 1
    return NLINES[path]


def check_locators(rows):
    problems, checked = [], 0
    for r in rows:
        spans = re.findall(r"`([^`]+)`", r["loc"])
        if r["cls"] in ("CONFIRMED", "CONFIRMED (precision)", "CORRECTED") and not spans:
            problems.append("row %d: no locator" % r["n"])
        for sp in spans:
            m = re.match(r"^([A-Za-z0-9._-]+)/(v\d+)/src/(.+?):([\d,\s-]+)$", sp)
            if m:
                key, ver, rel, lines = m.groups()
                path = os.path.join(RAW, key, ver, "src", rel)
                if not os.path.isfile(path):
                    problems.append("row %d: missing file %s" % (r["n"], sp))
                    continue
                top = max(line_numbers(lines))
                if top > nlines(path):
                    problems.append("row %d: line %d beyond end (%d) of %s"
                                    % (r["n"], top, nlines(path), sp))
                checked += 1
                continue
            m = re.match(r"^iq:([0-9a-f]{16})$", sp)
            if m:
                path = os.path.join(KB, "meta", "inspire", "query", m.group(1) + ".json")
                if not os.path.isfile(path):
                    problems.append("row %d: missing INSPIRE query file %s" % (r["n"], path))
                checked += 1
                continue
            m = re.match(r"^meta:(arxiv-api|inspire)/(.+)$", sp)
            if m:
                kind, aid = m.groups()
                last_kind = kind
            else:
                m = re.match(r"^/(.+)$", sp)
                if not m:
                    problems.append("row %d: unparsed locator %r" % (r["n"], sp))
                    continue
                aid = m.group(1)
                kind = last_kind
            path = os.path.join(KB, "meta", kind, aid.replace("/", "_") + ".json")
            if not os.path.isfile(path):
                problems.append("row %d: missing metadata %s" % (r["n"], path))
            checked += 1
    return problems, checked


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    rows = read_rows(CHECK)
    problems = []
    nums = [r["n"] for r in rows]
    if nums != list(range(1, len(rows) + 1)):
        problems.append("row numbers not consecutive")
    tally = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    n_head, t_head = header_totals(CHECK)
    if n_head != len(rows) or t_head != tally:
        problems.append("header totals %s (%d rows) differ from the tally %s (%d rows)"
                        % (t_head, n_head, tally, len(rows)))
    loc_problems, n_loc = check_locators(rows)
    problems += loc_problems

    lines = []
    for r in rows:
        if r["line"] not in lines:
            lines.append(r["line"])
    lines.sort(key=int)
    order = ["[VERIFIED]", "[title only verified]", "[BACKGROUND]", "[TO VERIFY]", "unlabelled"]
    labs = [l for l in order if any(r["lab"] == l for r in rows)]
    by_line = {l: {c: 0 for c in CLASSES} for l in lines}
    by_lab = {l: {c: 0 for c in CLASSES} for l in labs}
    for r in rows:
        by_line[r["line"]][r["cls"]] += 1
        by_lab[r["lab"]][r["cls"]] += 1
    corrected = [(r["n"], r["line"]) for r in rows if r["cls"] == "CORRECTED"]
    result = {"rows": len(rows), "tally": tally, "header": t_head,
              "locators_checked": n_loc, "problems": problems,
              "by_line": by_line, "by_label": by_lab, "corrected_rows": corrected}
    with open(os.path.join(out, "verdicts.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"rows": len(rows), "tally": tally, "locators_checked": n_loc,
                      "corrected_rows": corrected, "problems": problems}))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.2))
    ax1 = fig.add_axes([0.09, 0.13, 0.44, 0.74])
    ax2 = fig.add_axes([0.73, 0.13, 0.24, 0.74])
    short = {"[VERIFIED]": "VERIFIED", "[BACKGROUND]": "BACKGROUND", "[TO VERIFY]": "TO VERIFY",
             "[title only verified]": "title only", "unlabelled": "no label"}
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
        ax.set_xlim(0, 1.1 * max(left))  # margin: the longest bar must not touch the frame
        ax.set_yticks(y)
        ax.set_yticklabels([short.get(k, k) for k in keys])
        ax.tick_params(axis="y", which="minor", left=False, right=False)
        ax.set_xlabel("statements checked")
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
    ax1.set_ylabel("brief line")
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels),
               bbox_to_anchor=(0.5, 0.99))  # above both panels, clear of every bar
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    plt.close(fig)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
