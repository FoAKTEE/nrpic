#!/usr/bin/env python3
"""PDF files of figstyle.save are the same bytes from run to run (core/restart-finder,
item 3; request of Track E, figstyle-reproducible-pdf).

    python figstyle_test.py --out DIR

One figure is written twice, two seconds apart, with python/nrpic/figstyle.py (new) and
with harness/style/figstyle.py (the vendored copy, unchanged: the state before), each in
a process of its own, and once more twice with SOURCE_DATE_EPOCH set.  Checks: the two
PDF files of the new module are byte-identical and hold no /CreationDate; those of the
old module differ; with SOURCE_DATE_EPOCH the two are identical and hold that date; the
PNG files are identical in every case.  Writes DIR/summary.json and DIR/fig_new_a.{pdf,png}
(the figure itself, to look at); exit status 0 if the checks of the new module hold.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

MAKE = r'''
import sys, importlib.util
spec = importlib.util.spec_from_file_location("figstyle", sys.argv[1])
fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fs.use_style()
fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
fig.subplots_adjust(left=0.17, right=0.97, bottom=0.16, top=0.96)
x = np.linspace(0.0, 2.0*np.pi, 200)
ax.plot(x, np.sin(x), color=fs.PAL["blue"], label="reference")
ax.plot(x, np.sin(x + 0.1), color=fs.PAL["red"], ls="--", label="test")
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend()
fs.save(fig, sys.argv[2])
'''


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make(module, stem, env=None):
    e = dict(os.environ)
    e.pop("SOURCE_DATE_EPOCH", None)
    if env:
        e.update(env)
    subprocess.run([sys.executable, "-c", MAKE, module, stem], check=True, env=e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    new = os.path.join(REPO, "python", "nrpic", "figstyle.py")
    old = os.path.join(REPO, "harness", "style", "figstyle.py")
    res = {}
    for tag, mod, env in (("new", new, None), ("old", old, None),
                          ("epoch", new, {"SOURCE_DATE_EPOCH": "1700000000"})):
        sa, sb = os.path.join(out, "fig_%s_a" % tag), os.path.join(out, "fig_%s_b" % tag)
        make(mod, sa, env)
        time.sleep(2.0)
        make(mod, sb, env)
        pdf = open(sa + ".pdf", "rb").read()
        res[tag] = dict(module=os.path.relpath(mod, REPO), module_sha256=sha(mod),
                        pdf_identical=(sha(sa + ".pdf") == sha(sb + ".pdf")),
                        png_identical=(sha(sa + ".png") == sha(sb + ".png")),
                        pdf_sha256=[sha(sa + ".pdf"), sha(sb + ".pdf")],
                        has_creation_date=(b"/CreationDate" in pdf),
                        creation_date=(pdf.split(b"/CreationDate (")[1].split(b")")[0].decode()
                                       if b"/CreationDate (" in pdf else None))
    ck = {
        "new: two runs give byte-identical PDF files": res["new"]["pdf_identical"],
        "new: no creation date in the PDF": not res["new"]["has_creation_date"],
        "new: PNG files identical": res["new"]["png_identical"],
        "SOURCE_DATE_EPOCH: two runs identical": res["epoch"]["pdf_identical"],
        "SOURCE_DATE_EPOCH: the PDF holds that date (2023-11-14)":
            (res["epoch"]["creation_date"] or "").startswith("D:20231114"),
        "old (vendored copy): the two PDF files differ (the defect, for the record)":
            not res["old"]["pdf_identical"],
    }
    import matplotlib
    summary = dict(checks=ck, cases=res, matplotlib=matplotlib.__version__,
                   all_ok=all(ck.values()))
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    for k, v in ck.items():
        print("%-4s %s" % ("ok" if v else "FAIL", k))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
