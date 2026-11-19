"""Check every locator span in markdown files (work package s37_38).

Every backtick span of the form <key>/<v>/src/<file>:<lines> must name an existing file under
kb-data/raw/arxiv long enough for every line given; iq:<sha16> must name an existing stored INSPIRE
query; meta:arxiv-api/<id> and meta:inspire/<id> must name existing metadata files. Other backtick
spans (paths of this repository, code) are counted and skipped. Prints a JSON summary per file and
writes spans.json into $NRPIC_RUN_DIR (or the last argument if it is a directory). Exit 1 on a
problem. Also draws fig_spans.{pdf,png} (span kinds per file; problems in red) into the
output directory. Files under kb-data are only opened for reading.
Usage: python check_spans.py <file.md> [<file.md> ...]
"""
import json
import os
import re
import sys

KB = "/data/haiyangw/nrpic/kb-data"
RAW = os.path.join(KB, "raw", "arxiv")
TEX = re.compile(r"^([A-Za-z0-9._-]+)/(v\d+)/src/(.+?):([\d,\s-]+)$")


def check_file(path):
    text = open(path).read()
    spans = re.findall(r"`([^`\n]+)`", text)
    res = {"file": path, "spans": len(spans), "tex": 0, "iq": 0, "meta": 0, "other": 0, "problems": []}
    for sp in spans:
        if "<" in sp:  # placeholder in a description, e.g. meta:arxiv-api/<id>
            res["other"] += 1
            continue
        m = TEX.match(sp)
        if m:
            key, ver, rel, lines = m.groups()
            f = os.path.join(RAW, key, ver, "src", rel)
            res["tex"] += 1
            if not os.path.isfile(f):
                res["problems"].append("missing %s" % sp)
                continue
            with open(f, "rb") as fh:
                nl = fh.read().count(b"\n") + 1
            top = max(int(x) for part in lines.split(",") for x in part.strip().split("-") if x)
            if top > nl:
                res["problems"].append("line %d beyond end (%d): %s" % (top, nl, sp))
            continue
        m = re.match(r"^iq:([0-9a-f]{16})$", sp)
        if m:
            res["iq"] += 1
            if not os.path.isfile(os.path.join(KB, "meta", "inspire", "query", m.group(1) + ".json")):
                res["problems"].append("missing query %s" % sp)
            continue
        m = re.match(r"^meta:(arxiv-api|inspire)/(.+)$", sp)
        if m:
            res["meta"] += 1
            if not os.path.isfile(os.path.join(KB, "meta", m.group(1), m.group(2).replace("/", "_") + ".json")):
                res["problems"].append("missing metadata %s" % sp)
            continue
        res["other"] += 1
    return res


def main(args):
    out = os.environ.get("NRPIC_RUN_DIR")
    if not out and args and os.path.isdir(args[-1]):
        out = args.pop()
    results = [check_file(a) for a in args]
    for r in results:
        print(json.dumps({k: r[k] for k in ("file", "spans", "tex", "iq", "meta", "other", "problems")}))
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "spans.json"), "w") as fh:
            json.dump(results, fh, indent=1)
    if out:
        draw(results, out)
    if any(r["problems"] for r in results):
        sys.exit(1)


def draw(results, out):
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import figstyle as fs  # vendored copy of harness/style/figstyle.py
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    kinds = [("tex", "TeX locator", fs.PAL["blue"]), ("iq", "INSPIRE query", fs.PAL["green"]),
             ("meta", "metadata", fs.PAL["yellow"]), ("other", "other span (not a locator)", "grey")]
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.6))
    ax = fig.add_axes([0.20, 0.22, 0.75, 0.55])
    names = [os.path.basename(r["file"]) for r in results]
    y = list(range(len(results)))[::-1]
    left = [0] * len(results)
    for k, lab, col in kinds:
        w = [r[k] for r in results]
        ax.barh(y, w, left=left, color=col, height=0.6, label=lab, edgecolor="white", linewidth=0.5)
        left = [a + b for a, b in zip(left, w)]
    for yy, r, l in zip(y, results, left):
        ax.text(l + 1, yy, "%d problems" % len(r["problems"]), va="center", fontsize=8,
                color=fs.PAL["red"] if r["problems"] else "k")
    ax.set_xlim(0, 1.25 * max(left))
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_xlabel("backtick spans")
    fig.legend(loc="upper center", ncol=4, fontsize=7, bbox_to_anchor=(0.55, 0.99))
    fs.save(fig, os.path.join(out, "fig_spans"))
    plt.close(fig)


if __name__ == "__main__":
    main(sys.argv[1:])
