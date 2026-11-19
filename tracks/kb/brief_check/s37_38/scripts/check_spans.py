"""Check every locator span in markdown files (work package s37_38).

Every backtick span of the form <key>/<v>/src/<file>:<lines> must name an existing file under
kb-data/raw/arxiv long enough for every line given; iq:<sha16> must name an existing stored INSPIRE
query; meta:arxiv-api/<id> and meta:inspire/<id> must name existing metadata files. Other backtick
spans (paths of this repository, code) are counted and skipped. Prints a JSON summary per file and
writes spans.json into $NRPIC_RUN_DIR (or the last argument if it is a directory). Exit 1 on a
problem. Files under kb-data are only opened for reading.
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
    if any(r["problems"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
