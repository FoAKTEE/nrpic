"""Tally, locator check and figure of the verdicts in CHECK.md (work package s5_s6).

Adapted from tracks/kb/brief_check/s35/scripts/fig_verdicts.py. Reads the markdown tables of
CHECK.md and
  1. checks that the rows are numbered 1..N without gaps and that the totals stated in the
     header ("Totals: N rows; a CONFIRMED, b CONFIRMED (precision), c CORRECTED, d NOT FOUND")
     equal the tally of the verdict column;
  2. checks every locator of the locator column: a TeX locator `<key>/<v>/src/<file>:<lines>`
     must name an existing file under kb-data/raw/arxiv whose length covers every line given;
     `github:<repo>/<path>` must exist under kb-data/raw/github; `meta:inspire/query/<sha16>`
     must exist under kb-data/meta/inspire/query; a run id `kb-<date>-<time>-<sha7>` must have
     tracks/kb/runs/<id>/manifest.json; every CONFIRMED or CORRECTED row needs one locator;
  3. counts the verdicts per item of the brief (S5 ... S10, M1 ... M12) and per label and draws
     them.
Writes verdicts.json and fig_verdicts.{pdf,png} into $NRPIC_RUN_DIR (or the first argument)
and prints the tally. Exit status 1 if a check fails. Files under kb-data are only opened for
reading and counted in lines; nothing there is executed or imported.
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
GH = os.path.join(KB, "raw", "github")
RUNS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "runs")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey"}
LABELS = ["[VERIFIED]", "[BACKGROUND]", "[TO VERIFY]", "unlabelled"]

# brief lines -> item of the brief
ITEMS = [("S5", 406, 417), ("S6", 418, 429), ("S7", 430, 438), ("S8", 441, 441),
         ("S9", 442, 442), ("S10", 443, 443), ("M1", 497, 501), ("M2", 503, 508),
         ("M3", 510, 512), ("M4", 514, 516), ("M6", 522, 526), ("M7", 528, 530),
         ("M8", 532, 534), ("M10", 540, 542), ("M12", 548, 550)]


def item_of(line):
    for name, a, b in ITEMS:
        if a <= line <= b:
            return name
    raise ValueError("brief line %d outside the items" % line)


def classify(verdict):
    v = verdict.strip()
    for c in ("CORRECTED", "NOT FOUND", "CONFIRMED (precision)", "CONFIRMED"):
        if v.startswith(c):
            return c
    raise ValueError("unknown verdict: %r" % verdict)


def label_class(label):
    lab = label.strip()
    for l in LABELS[:3]:
        if lab.startswith(l):
            return l
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
            if len(cells) != 7:
                raise ValueError("row with %d cells: %s" % (len(cells), line[:80]))
            rows.append({"n": int(cells[0]), "line": int(cells[1]), "label": cells[3],
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
    out = []
    for part in spec.split(","):
        part = part.strip()
        if part:
            out += [int(x) for x in part.split("-")]
    return out


NLINES = {}


def nlines(path):
    if path not in NLINES:
        with open(path, "rb") as fh:
            NLINES[path] = fh.read().count(b"\n") + 1
    return NLINES[path]


def check_locators(rows):
    problems, kinds = [], {"tex": 0, "github": 0, "inspire": 0, "run": 0}
    for r in rows:
        spans = re.findall(r"`([^`]+)`", r["loc"])
        if not spans:
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
                kinds["tex"] += 1
                continue
            m = re.match(r"^github:(.+)$", sp)
            if m:
                if not os.path.isfile(os.path.join(GH, m.group(1))):
                    problems.append("row %d: missing github file %s" % (r["n"], sp))
                kinds["github"] += 1
                continue
            m = re.match(r"^meta:inspire/query/([0-9a-f]{16})$", sp)
            if m:
                if not os.path.isfile(os.path.join(KB, "meta", "inspire", "query",
                                                   m.group(1) + ".json")):
                    problems.append("row %d: missing query file %s" % (r["n"], sp))
                kinds["inspire"] += 1
                continue
            if re.match(r"^kb-\d{8}-\d{6}-[0-9a-f]{7}$", sp):
                if not os.path.isfile(os.path.join(RUNS, sp, "manifest.json")):
                    problems.append("row %d: no manifest for run %s" % (r["n"], sp))
                kinds["run"] += 1
                continue
            # other spans in the locator column (file names in this repository) are not locators
            if not (sp.startswith("athenak/") or sp.endswith(".md")):
                problems.append("row %d: unparsed locator %r" % (r["n"], sp))
    return problems, kinds


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    rows = read_rows(CHECK)
    problems = []
    if [r["n"] for r in rows] != list(range(1, len(rows) + 1)):
        problems.append("row numbers not consecutive")
    tally = {c: sum(1 for r in rows if r["cls"] == c) for c in CLASSES}
    n_head, t_head = header_totals(CHECK)
    if n_head != len(rows) or t_head != tally:
        problems.append("header totals %s (%d rows) differ from the tally %s (%d rows)"
                        % (t_head, n_head, tally, len(rows)))
    loc_problems, kinds = check_locators(rows)
    problems += loc_problems

    items = [name for name, _a, _b in ITEMS]
    by_item = {k: {c: 0 for c in CLASSES} for k in items}
    by_lab = {k: {c: 0 for c in CLASSES} for k in LABELS}
    for r in rows:
        by_item[item_of(r["line"])][r["cls"]] += 1
        by_lab[r["lab"]][r["cls"]] += 1
    corrected = [(r["n"], r["line"]) for r in rows if r["cls"] == "CORRECTED"]
    result = {"rows": len(rows), "tally": tally, "header": t_head, "locators": kinds,
              "problems": problems, "by_item": by_item, "by_label": by_lab,
              "corrected_rows": corrected}
    with open(os.path.join(out, "verdicts.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"rows": len(rows), "tally": tally, "locators": kinds,
                      "corrected_rows": corrected, "by_label": by_lab,
                      "problems": problems}, indent=1))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    ax1 = fig.add_axes([0.08, 0.12, 0.45, 0.78])
    ax2 = fig.add_axes([0.72, 0.12, 0.25, 0.78])
    short = {"[VERIFIED]": "VERIFIED", "[BACKGROUND]": "BACKGROUND",
             "[TO VERIFY]": "TO VERIFY", "unlabelled": "no label"}
    for ax, keys, table in ((ax1, items, by_item), (ax2, LABELS, by_lab)):
        y = list(range(len(keys)))[::-1]
        left = [0] * len(keys)
        for c in CLASSES:
            w = [table[k][c] for k in keys]
            ax.barh(y, w, left=left, color=COLORS[c], edgecolor="white", lw=0.5,
                    label=c if ax is ax1 else None)
            left = [a + b for a, b in zip(left, w)]
        ax.set_yticks(y)
        ax.set_yticklabels([short.get(k, k) for k in keys], fontsize=8)
        ax.set_xlabel("statements checked")
        ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax1.set_title("by item of the brief (lines 406-444, 493-553)", fontsize=9)
    ax2.set_title("by label", fontsize=9)
    ax1.legend(loc="lower right", fontsize=7, frameon=False)
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    if problems:
        print("PROBLEMS:", problems)
        sys.exit(1)


if __name__ == "__main__":
    main()
