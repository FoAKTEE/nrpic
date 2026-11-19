"""Tally, locator check and figure of CHECK.md (work package s7_s8; after the s35 script).

Reads the three markdown tables of CHECK.md:
  part A, statements: rows "| <n> | line | quotation | label | verdict | locator | note |";
  part B, open questions: rows "| Q<n> | line | question | status | locator | note |";
  part C, candidates: rows "| U<n> | line | candidate | status | locator | note |".
Checks
  1. part A rows numbered 1..N without gaps, and the header sentence "Totals: N rows; a
     CONFIRMED, b CONFIRMED (precision), c CORRECTED, d NOT FOUND" equal to the tally;
     part B has Q1..Q26 and the sentence "Counts: 26 questions; a ANSWERED, b PARTLY ANSWERED,
     c OPEN" equals its tally; part C has U1..U12;
  2. every locator span in backticks: a TeX locator `<key>/<v>/src/<file>:<lines>` names an
     existing file under kb-data/raw/arxiv whose length covers every line given;
     `meta:arxiv-api/<id>` names kb-data/meta/arxiv-api/<id>.json; `meta:inspire/query/<sha16>`
     names kb-data/meta/inspire/query/<sha16>.json with status ok; a run id
     `kb-<date>-<time>-<sha7>` has tracks/kb/runs/<id>/manifest.json; every row with a verdict
     other than NOT FOUND / NOT SEARCHED has at least one locator;
  3. draws the verdicts of part A per brief line and the status of parts B and C.
Writes verdicts.json and fig_verdicts.{pdf,png} into $NRPIC_RUN_DIR (or the first argument)
and prints the tally. Exit status 1 if a check fails. Files under kb-data are only opened for
reading (line counts, JSON status); nothing there is executed or imported.
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
RUNS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "runs")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
STATUS = ["ANSWERED", "PARTLY ANSWERED", "OPEN", "NOT SEARCHED"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey",
          "ANSWERED": fs.PAL["blue"], "PARTLY ANSWERED": fs.PAL["yellow"],
          "OPEN": fs.PAL["red"], "NOT SEARCHED": "grey"}


def classify(v, classes):
    v = v.strip()
    for c in sorted(classes, key=len, reverse=True):
        if v.startswith(c):
            return c
    raise ValueError("unknown verdict or status: %r" % v)


def read_tables(path):
    a, b, c = [], [], []
    with open(path) as fh:
        for line in fh:
            m = re.match(r"^\| (\d+|Q\d+|U\d+) \|", line)
            if not m:
                continue
            cells = [x.strip() for x in line.strip().strip("|").split("|")]
            key = m.group(1)
            if key.isdigit():
                if len(cells) != 7:
                    raise ValueError("part A row with %d cells: %s" % (len(cells), line[:80]))
                a.append({"id": key, "n": int(key), "line": cells[1], "label": cells[3],
                          "cls": classify(cells[4], CLASSES), "loc": cells[5]})
            else:
                if len(cells) != 6:
                    raise ValueError("part B/C row with %d cells: %s" % (len(cells), line[:80]))
                row = {"id": key, "n": int(key[1:]), "line": cells[1],
                       "cls": classify(cells[3], STATUS), "loc": cells[4]}
                (b if key[0] == "Q" else c).append(row)
    return a, b, c


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


def check_locators(rows, needs_loc):
    problems, checked = [], 0
    for r in rows:
        spans = re.findall(r"`([^`]+)`", r["loc"])
        if r["cls"] in needs_loc and not spans:
            problems.append("%s: no locator" % r["id"])
        for sp in spans:
            m = re.match(r"^([A-Za-z0-9._-]+)/(v\d+)/src/(.+?):([\d,\s-]+)$", sp)
            if m:
                key, ver, rel, lines = m.groups()
                path = os.path.join(RAW, key, ver, "src", rel)
                if not os.path.isfile(path):
                    problems.append("%s: missing file %s" % (r["id"], sp))
                elif max(line_numbers(lines)) > nlines(path):
                    problems.append("%s: line beyond end (%d) of %s" % (r["id"], nlines(path), sp))
                checked += 1
                continue
            if re.match(r"^kb-\d{8}-\d{6}-[0-9a-f]{7}$", sp):
                if not os.path.isfile(os.path.join(RUNS, sp, "manifest.json")):
                    problems.append("%s: no manifest for run %s" % (r["id"], sp))
                checked += 1
                continue
            m = re.match(r"^meta:inspire/query/([0-9a-f]{16})$", sp)
            if m:
                p = os.path.join(KB, "meta", "inspire", "query", m.group(1) + ".json")
                if not os.path.isfile(p):
                    problems.append("%s: missing INSPIRE answer %s" % (r["id"], sp))
                else:
                    with open(p) as fh:
                        if json.load(fh).get("status") != "ok":
                            problems.append("%s: INSPIRE answer not ok %s" % (r["id"], sp))
                checked += 1
                continue
            m = re.match(r"^meta:arxiv-api/(.+)$", sp)
            if m:
                p = os.path.join(KB, "meta", "arxiv-api", m.group(1).replace("/", "_") + ".json")
                if not os.path.isfile(p):
                    problems.append("%s: missing metadata %s" % (r["id"], sp))
                checked += 1
                continue
            problems.append("%s: unparsed locator %r" % (r["id"], sp))
    return problems, checked


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    a, b, c = read_tables(CHECK)
    text = open(CHECK).read().replace("\n", " ")
    problems = []
    if [r["n"] for r in a] != list(range(1, len(a) + 1)):
        problems.append("part A rows not numbered 1..N")
    if [r["n"] for r in b] != list(range(1, 27)):
        problems.append("part B is not Q1..Q26")
    if [r["n"] for r in c] != list(range(1, 13)):
        problems.append("part C is not U1..U12")
    tally_a = {k: sum(1 for r in a if r["cls"] == k) for k in CLASSES}
    m = re.search(r"Totals: (\d+) rows; (\d+) CONFIRMED, (\d+) CONFIRMED \(precision\), "
                  r"(\d+) CORRECTED, (\d+) NOT FOUND", text)
    head_a = dict(zip(CLASSES, (int(x) for x in m.groups()[1:]))) if m else None
    if not m or int(m.group(1)) != len(a) or head_a != tally_a:
        problems.append("part A header %s differs from tally %s" % (head_a, tally_a))
    tally_b = {k: sum(1 for r in b if r["cls"] == k) for k in STATUS}
    m = re.search(r"Counts: (\d+) questions; (\d+) ANSWERED, (\d+) PARTLY ANSWERED, (\d+) OPEN",
                  text)
    head_b = {"ANSWERED": int(m.group(2)), "PARTLY ANSWERED": int(m.group(3)),
              "OPEN": int(m.group(4)), "NOT SEARCHED": 0} if m else None
    if not m or head_b != tally_b:
        problems.append("part B counts %s differ from tally %s" % (head_b, tally_b))
    tally_c = {k: sum(1 for r in c if r["cls"] == k) for k in STATUS}
    pa, na = check_locators(a, set(CLASSES) - {"NOT FOUND"})
    pb, nb = check_locators(b + c, {"ANSWERED", "PARTLY ANSWERED", "OPEN"})
    problems += pa + pb
    result = {"part_A_rows": len(a), "part_A_tally": tally_a, "part_B_tally": tally_b,
              "part_C_tally": tally_c, "locators_checked": na + nb,
              "corrected_rows": [(r["n"], r["line"]) for r in a if r["cls"] == "CORRECTED"],
              "labels": {lab: sum(1 for r in a if r["label"].startswith(lab))
                         for lab in ("[BACKGROUND]", "[TO VERIFY]", "[VERIFIED]", "(unl.)")},
              "problems": problems}
    with open(os.path.join(out, "verdicts.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps(result, indent=1))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    ax1 = fig.add_axes([0.08, 0.12, 0.40, 0.72])
    ax2 = fig.add_axes([0.60, 0.12, 0.37, 0.72])
    lines = sorted({r["line"] for r in a}, key=int)
    y = list(range(len(lines)))[::-1]
    left = [0] * len(lines)
    for k in CLASSES:
        w = [sum(1 for r in a if r["line"] == l and r["cls"] == k) for l in lines]
        if sum(w):
            ax1.barh(y, w, left=left, color=COLORS[k], height=0.7, label=k,
                     edgecolor="white", linewidth=0.5)
            left = [p + q for p, q in zip(left, w)]
    ax1.set_yticks(y)
    ax1.set_yticklabels(lines, fontsize=7)
    ax1.tick_params(axis="y", which="minor", left=False, right=False)
    ax1.set_xlabel("statements checked")
    ax1.set_ylabel("brief line")
    ax1.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=4, integer=True))
    ax1.set_title("(a) part A: verdicts", fontsize=10)
    groups = [("Q1-5", b[0:5]), ("Q6-10", b[5:10]), ("Q11-20", b[10:20]), ("Q21-26", b[20:26]),
              ("U1-12", c)]
    yy = list(range(len(groups)))[::-1]
    left = [0] * len(groups)
    for k in STATUS:
        w = [sum(1 for r in g if r["cls"] == k) for _, g in groups]
        if sum(w):
            ax2.barh(yy, w, left=left, color=COLORS[k], height=0.6, label=k,
                     edgecolor="white", linewidth=0.5)
            left = [p + q for p, q in zip(left, w)]
    ax2.set_yticks(yy)
    ax2.set_yticklabels([g for g, _ in groups])
    ax2.tick_params(axis="y", which="minor", left=False, right=False)
    ax2.set_xlabel("questions or candidates")
    ax2.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=6, integer=True))
    ax2.set_title("(b) parts B and C: status", fontsize=10)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    fig.legend(h1, l1, loc="upper left", ncol=2, fontsize=8, bbox_to_anchor=(0.06, 1.0))
    fig.legend(h2, l2, loc="upper left", ncol=2, fontsize=8, bbox_to_anchor=(0.58, 1.0))
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    plt.close(fig)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
