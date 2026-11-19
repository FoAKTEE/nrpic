"""Tally, locator check, coverage check and figure of CHECK.md (work package s310).

Adapted from the s35 script. Reads the markdown tables of CHECK.md and
  1. checks that the rows are numbered 1..N without gaps and that the totals stated in the
     header ("Totals: N rows; a CONFIRMED, b CONFIRMED (precision), c CORRECTED, d NOT FOUND")
     equal the tally of the verdict column;
  2. checks every locator of the locator column:
     - TeX `<key>/<v>/src/<file>:<lines>`: the file exists under kb-data/raw/arxiv and its
       length covers every line number given;
     - PDF `<key>/<v>/source.pdf#p<pages>`: the file exists and its page count (objects of
       /Type /Page, counted in the bytes) covers every page given;
     - `meta:arxiv-api/<id>`, `meta:inspire/<id>`: the file exists under kb-data/meta;
     - `github:<repo>/<path>`: the path exists under kb-data/raw/github;
     - `repo:<path>`: the path exists in this worktree;
     - a run id `kb-<date>-<time>-<sha7>`: tracks/kb/runs/<id>/manifest.json exists;
  3. coverage: every arXiv identifier written in brief lines 257-266 (only those lines are
     read) occurs in CHECK.md;
  4. counts the verdicts per brief line and per evidence label and draws them.
Writes verdicts.json and fig_verdicts.{pdf,png} into $NRPIC_RUN_DIR (or the first argument)
and prints the tally. Exit status 1 if a check fails. Files under kb-data are only opened
for reading; nothing there is executed or imported.

Run (registered): harness/bin/nrpic-run submit --kind scouting --gate G2 --package
tracks/kb/brief_check/s310 --input tracks/kb/brief_check/s310/CHECK.md --cores 1
--purpose "..." -- python tracks/kb/brief_check/s310/scripts/fig_verdicts.py
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

PKG = os.path.dirname(HERE)
CHECK = os.path.join(PKG, "CHECK.md")
WT = os.path.abspath(os.path.join(PKG, "..", "..", "..", ".."))  # worktree root
BRIEF = os.path.join(WT, "einstein_vlasov_pic_cosmology_agent_brief.en.md")
BRIEF_LINES = (257, 266)
KB = "/data/haiyangw/nrpic/kb-data"
RAW = os.path.join(KB, "raw", "arxiv")
GH = os.path.join(KB, "raw", "github")
RUNS = os.path.join(WT, "tracks", "kb", "runs")
CLASSES = ["CONFIRMED", "CONFIRMED (precision)", "CORRECTED", "NOT FOUND"]
COLORS = {"CONFIRMED": fs.PAL["blue"], "CONFIRMED (precision)": fs.PAL["yellow"],
          "CORRECTED": fs.PAL["red"], "NOT FOUND": "grey"}
LABS = ["[VERIFIED]", "[BACKGROUND]", "unlabelled"]


def classify(verdict):
    v = verdict.strip()
    for c in ("CORRECTED", "NOT FOUND", "CONFIRMED (precision)", "CONFIRMED"):
        if v.startswith(c):
            return c
    raise ValueError("unknown verdict: %r" % verdict)


def label_class(label):
    lab = label.strip()
    for k in ("[VERIFIED]", "[BACKGROUND]", "[TO VERIFY]"):
        if lab.startswith(k):
            return k
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


def numbers(spec):
    """'38-46, 320-328' -> [38, 46, 320, 328]"""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        for x in part.split("-"):
            out.append(int(x))
    return out


CACHE = {}


def nlines(path):
    key = ("lines", path)
    if key not in CACHE:
        with open(path, "rb") as fh:
            CACHE[key] = fh.read().count(b"\n") + 1
    return CACHE[key]


def npages(path):
    key = ("pages", path)
    if key not in CACHE:
        with open(path, "rb") as fh:
            data = fh.read()
        CACHE[key] = len(re.findall(rb"/Type\s*/Page(?![s\w])", data))
    return CACHE[key]


def check_locators(rows):
    problems, checked = [], 0
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
                top = max(numbers(lines))
                if top > nlines(path):
                    problems.append("row %d: line %d beyond end (%d) of %s"
                                    % (r["n"], top, nlines(path), sp))
                checked += 1
                continue
            m = re.match(r"^([A-Za-z0-9._-]+)/(v\d+)/source\.pdf#p([\d,\s-]+)$", sp)
            if m:
                key, ver, pages = m.groups()
                path = os.path.join(RAW, key, ver, "source.pdf")
                if not os.path.isfile(path):
                    problems.append("row %d: missing file %s" % (r["n"], sp))
                    continue
                n = npages(path)
                if n == 0 or max(numbers(pages)) > n:
                    problems.append("row %d: page beyond end (%d pages) of %s" % (r["n"], n, sp))
                checked += 1
                continue
            if re.match(r"^kb-\d{8}-\d{6}-[0-9a-f]{7}$", sp):
                if not os.path.isfile(os.path.join(RUNS, sp, "manifest.json")):
                    problems.append("row %d: no manifest for run %s" % (r["n"], sp))
                checked += 1
                continue
            m = re.match(r"^meta:(arxiv-api|inspire)/(.+)$", sp)
            if m:
                kind, aid = m.groups()
                path = os.path.join(KB, "meta", kind, aid.replace("/", "_") + ".json")
                if not os.path.isfile(path):
                    problems.append("row %d: missing metadata %s" % (r["n"], path))
                checked += 1
                continue
            m = re.match(r"^github:(.+)$", sp)
            if m:
                if not os.path.exists(os.path.join(GH, m.group(1))):
                    problems.append("row %d: missing repository path %s" % (r["n"], sp))
                checked += 1
                continue
            m = re.match(r"^repo:(.+)$", sp)
            if m:
                if not os.path.exists(os.path.join(WT, m.group(1))):
                    problems.append("row %d: missing file of this repository %s" % (r["n"], sp))
                checked += 1
                continue
            problems.append("row %d: unparsed locator %r" % (r["n"], sp))
    return problems, checked


def brief_ids():
    lo, hi = BRIEF_LINES
    ids = []
    with open(BRIEF) as fh:
        for i, line in enumerate(fh, 1):
            if i < lo:
                continue
            if i > hi:
                break
            for aid in re.findall(r"arXiv:([a-z-]+/\d{7}|\d{4}\.\d{4,5})", line):
                if aid not in ids:
                    ids.append(aid)
    return ids


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

    text = open(CHECK).read()
    ids = brief_ids()
    missing = [a for a in ids if a not in text]
    if missing:
        problems.append("brief ids absent from CHECK.md: %s" % ", ".join(missing))

    lines = sorted({r["line"] for r in rows}, key=int)
    by_line = {l: {c: 0 for c in CLASSES} for l in lines}
    by_lab = {l: {c: 0 for c in CLASSES} for l in LABS}
    for r in rows:
        by_line[r["line"]][r["cls"]] += 1
        by_lab[r["lab"]][r["cls"]] += 1
    corrected = [(r["n"], r["line"]) for r in rows if r["cls"] == "CORRECTED"]
    result = {"rows": len(rows), "tally": tally, "header": t_head,
              "locators_checked": n_loc, "brief_ids": len(ids), "brief_ids_missing": missing,
              "problems": problems, "by_line": by_line, "by_label": by_lab,
              "corrected_rows": corrected}
    with open(os.path.join(out, "verdicts.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"rows": len(rows), "tally": tally, "locators_checked": n_loc,
                      "brief_ids": len(ids), "brief_ids_missing": missing,
                      "corrected_rows": corrected, "problems": problems}))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.2))
    ax1 = fig.add_axes([0.09, 0.13, 0.44, 0.74])
    ax2 = fig.add_axes([0.73, 0.13, 0.24, 0.74])
    short = {"[VERIFIED]": "VERIFIED", "[BACKGROUND]": "BACKGROUND", "unlabelled": "no label"}
    for ax, keys, table in ((ax1, lines, by_line), (ax2, LABS, by_lab)):
        y = list(range(len(keys)))[::-1]
        left = [0] * len(keys)
        for c in CLASSES:
            w = [table[k][c] for k in keys]
            ax.barh(y, w, left=left, color=COLORS[c], height=0.7, label=c,
                    edgecolor="white", linewidth=0.5)
            left = [a + b for a, b in zip(left, w)]
        ax.set_xlim(0, 1.1 * max(left))  # room right of the longest bar
        ax.set_yticks(y)
        ax.set_yticklabels([short.get(k, k) for k in keys])
        ax.tick_params(axis="y", which="minor", left=False, right=False)
        ax.set_xlabel("statements checked")
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=5, integer=True))
    ax1.set_ylabel("brief line")
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(labels),
               bbox_to_anchor=(0.5, 0.99))  # above both panels
    fs.save(fig, os.path.join(out, "fig_verdicts"))
    plt.close(fig)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
