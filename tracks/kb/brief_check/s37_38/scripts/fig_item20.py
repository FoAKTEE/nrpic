"""Landscape of future stability results for FLRW-type solutions (open question 20, brief item 6 of section 15).

Reads data/item20_landscape.tsv (matter, expansion, status, papers, locators), checks every locator
(a TeX locator <key>/<v>/src/<file>:<lines> must name an existing file under kb-data/raw/arxiv long
enough for every line given; iq:<sha16> must name an existing stored INSPIRE query), and draws the
matter-by-expansion grid coloured by status. Writes landscape.json and fig_item20.{pdf,png} into
$NRPIC_RUN_DIR (or the first argument). Exit status 1 if a locator check fails. Files under kb-data
are only opened for reading; nothing there is executed or imported.
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
from matplotlib.patches import Rectangle  # noqa: E402

DATA = os.path.join(os.path.dirname(HERE), "data", "item20_landscape.tsv")
KB = "/data/haiyangw/nrpic/kb-data"
RAW = os.path.join(KB, "raw", "arxiv")
STATUS = {  # colour, legend text
    "proven": (fs.PAL["blue"], "theorem, no symmetry"),
    "symmetric": (fs.PAL["yellow"], "theorem with symmetry or homogeneity only"),
    "numerical": (fs.PAL["green"], "numerical evidence only"),
    "unstable": (fs.PAL["red"], "unstable (linear theory or numerics)"),
    "open": ("white", "nothing found"),
    "unchecked": ("#DDDDDD", "not searched here"),
}


def read_rows(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        cells = line.rstrip("\n").split("\t")
        if len(cells) != 5:
            raise ValueError("row with %d cells: %s" % (len(cells), line[:60]))
        matter, expansion, status, papers, locs = cells
        if status not in STATUS:
            raise ValueError("unknown status %r" % status)
        rows.append(dict(matter=matter, expansion=expansion, status=status, papers=papers,
                         locs=[l.strip() for l in locs.split(";") if l.strip() and l.strip() != "-"]))
    return rows


def check(rows):
    problems, n = [], 0
    for r in rows:
        if r["status"] not in ("unchecked", "open") and not r["locs"]:
            problems.append("%s / %s: no locator" % (r["matter"], r["expansion"]))
        for sp in r["locs"]:
            m = re.match(r"^iq:([0-9a-f]{16})$", sp)
            if m:
                if not os.path.isfile(os.path.join(KB, "meta", "inspire", "query", m.group(1) + ".json")):
                    problems.append("missing query file %s" % sp)
                n += 1
                continue
            m = re.match(r"^([A-Za-z0-9._-]+)/(v\d+)/src/(.+?):([\d,\s-]+)$", sp)
            if not m:
                problems.append("unparsed locator %r" % sp)
                continue
            key, ver, rel, lines = m.groups()
            path = os.path.join(RAW, key, ver, "src", rel)
            if not os.path.isfile(path):
                problems.append("missing file %s" % sp)
                continue
            with open(path, "rb") as fh:
                nl = fh.read().count(b"\n") + 1
            top = max(int(x) for part in lines.split(",") for x in part.strip().split("-") if x)
            if top > nl:
                problems.append("line %d beyond end (%d) of %s" % (top, nl, sp))
            n += 1
    return problems, n


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or (sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(out, exist_ok=True)
    rows = read_rows(DATA)
    problems, n = check(rows)
    matters, exps = [], []
    for r in rows:
        if r["matter"] not in matters:
            matters.append(r["matter"])
        if r["expansion"] not in exps:
            exps.append(r["expansion"])
    cell = {(r["matter"], r["expansion"]): r for r in rows}
    if len(cell) != len(rows):
        problems.append("duplicate cells")
    summary = {"cells": len(rows), "locators_checked": n, "problems": problems,
               "status": {s: [(r["matter"], r["expansion"]) for r in rows if r["status"] == s]
                          for s in STATUS}}
    with open(os.path.join(out, "landscape.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({"cells": len(rows), "locators_checked": n, "problems": problems,
                      "open_or_symmetric_only": summary["status"]["symmetric"] + summary["status"]["open"]}))

    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 4.4))
    ax = fig.add_axes([0.25, 0.13, 0.73, 0.72])
    for j, mat in enumerate(matters):
        y = len(matters) - 1 - j
        for i, ex in enumerate(exps):
            r = cell.get((mat, ex))
            st = r["status"] if r else "unchecked"
            ax.add_patch(Rectangle((i, y), 1, 1, facecolor=STATUS[st][0], edgecolor="k", lw=0.8,
                                   hatch="//" if st == "open" else None))
            txt = r["papers"] if r and r["papers"] != "-" else ""
            txt = "\n".join(t.strip() for t in txt.split(";"))
            ax.text(i + 0.5, y + 0.5, txt, ha="center", va="center", fontsize=6.5,
                    color="white" if st in ("proven", "unstable") else "k", wrap=True)
    # the cell of open question 20: massive Vlasov on the decelerated (Einstein-de Sitter) background
    if ("massive Vlasov", exps[-1]) in cell:
        j = matters.index("massive Vlasov")
        ax.add_patch(Rectangle((len(exps) - 1, len(matters) - 1 - j), 1, 1, fill=False, edgecolor="k", lw=3.0))
    ax.set_xlim(0, len(exps))
    ax.set_ylim(0, len(matters))
    ax.set_xticks([i + 0.5 for i in range(len(exps))])
    ax.set_xticklabels(exps)
    ax.set_yticks([len(matters) - 1 - j + 0.5 for j in range(len(matters))])
    ax.set_yticklabels([m.replace(" (", "\n(").replace(" p=", "\np=").replace(" n>", "\nn>") for m in matters])
    ax.tick_params(which="both", length=0)
    ax.set_xlabel("background expansion (cosmological constant, spatial curvature)")
    handles = [Rectangle((0, 0), 1, 1, facecolor=STATUS[s][0], edgecolor="k", lw=0.6,
                         hatch="//" if s == "open" else None, label=STATUS[s][1])
               for s in STATUS if any(r["status"] == s for r in rows)]
    fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=7, bbox_to_anchor=(0.55, 0.995))
    fs.save(fig, os.path.join(out, "fig_item20"))
    plt.close(fig)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
