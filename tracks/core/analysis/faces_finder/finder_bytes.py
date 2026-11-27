#!/usr/bin/env python3
"""Without the new options the horizon finder writes the same bytes as the release
(prediction S4 of tracks/core/JOURNAL-faces-finder.md).

    finder_bytes.py --base ATHENA --new ATHENA --out DIR

Decks: problems/tests/by_horizon_coarse.athinput (one cycle, a search after it) and
problems/tests/finder_polish.athinput (polishing), each with <fastflow> diagnostics = true
added, run with both executables; every output file but the log is compared byte for
byte.  Then the same deck of the first with `start_scan_0 = 12` and `trapped_tol_0 = 0.2`
with the new executable alone (the options are read and act: status file with eighteen
columns).  Writes DIR/summary.json and DIR/fig_finder_bytes.{pdf,png}; exit 0 if the
outputs of the first two decks are identical.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))


def deck(name, extra=""):
    txt = open(os.path.join(REPO, "problems", "tests", name + ".athinput")).read()
    if not re.search(r"(?m)^diagnostics\s*=", txt):
        txt = re.sub(r"(?m)^<fastflow>\s*$", "<fastflow>\ndiagnostics = true" + extra, txt,
                     count=1)
    elif extra:
        txt = re.sub(r"(?m)^<fastflow>\s*$", "<fastflow>" + extra, txt, count=1)
    return txt


def files(d):
    out = {}
    for root, _, fs in os.walk(d):
        for f in fs:
            if f in ("athena.log", "in.athinput"):
                continue
            p = os.path.join(root, f)
            out[os.path.relpath(p, d)] = open(p, "rb").read()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    jobs = []
    for name, args in (("by_horizon_coarse", []), ("finder_polish", ["time/nlim=8"])):
        for tag, exe in (("base", a.base), ("new", a.new)):
            jobs.append((name, tag, exe, deck(name), args))
    jobs.append(("by_horizon_coarse_opts", "new", a.new,
                 deck("by_horizon_coarse", "\nstart_scan_0 = 12\ntrapped_tol_0 = 0.2"), []))
    procs = []
    for name, tag, exe, txt, args in jobs:
        d = os.path.join(out, name, tag)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "in.athinput"), "w") as f:
            f.write(txt)
        log = open(os.path.join(d, "athena.log"), "w")
        procs.append((name, tag, subprocess.Popen([exe, "-i", "in.athinput"] + args, cwd=d,
                                                  stdout=log, stderr=subprocess.STDOUT), log))
    res = {}
    for name, tag, p, log in procs:
        res.setdefault(name, {})[tag] = {"status": p.wait()}
        log.close()
    ok = True
    for name in ("by_horizon_coarse", "finder_polish"):
        fb, fn = files(os.path.join(out, name, "base")), files(os.path.join(out, name, "new"))
        diff = sorted(k for k in set(fb) | set(fn) if fb.get(k) != fn.get(k))
        res[name]["files"] = len(set(fb) | set(fn))
        res[name]["differing"] = diff
        ok &= (not diff) and res[name]["base"]["status"] == 0 and res[name]["new"]["status"] == 0
        ok &= len(fb) > 0
        st = [k for k in fn if "horizon_status" in k]
        res[name]["status_rows"] = sum(1 for k in st for l in fn[k].decode().splitlines()
                                       if not l.startswith("#"))
    d = os.path.join(out, "by_horizon_coarse_opts", "new")
    st = [f for f in os.listdir(d) if "horizon_status" in f]
    rows = [l for f in st for l in open(os.path.join(d, f)) if not l.startswith("#")]
    res["by_horizon_coarse_opts"]["status_rows"] = rows
    res["by_horizon_coarse_opts"]["columns"] = [len(l.split("#")[0].split()) for l in rows]
    res["verdict"] = "PASS" if ok else "FAIL"
    json.dump(res, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(figsize=(5.4, 2.4))
    names = ["by_horizon_coarse", "finder_polish"]
    nf = [res[n]["files"] for n in names]
    nd = [len(res[n]["differing"]) for n in names]
    ax.barh(names, nf, color=figstyle.PAL["blue"], label="output files compared")
    ax.barh(names, nd, color=figstyle.PAL["red"], label="differing")
    for i, (a_, b_) in enumerate(zip(nf, nd)):
        ax.text(a_ + 0.2, i, "%d files, %d differ" % (a_, b_), va="center", fontsize=8)
    ax.set_xlim(0, max(nf) + 8)
    ax.set_xlabel("files (release core-v0.8 against this branch, no new option)")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "fig_finder_bytes"))
    print("FINDER BYTES", res["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
