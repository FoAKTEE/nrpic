#!/usr/bin/env python3
"""Prediction T9 of tracks/core/JOURNAL.md (2026-11-28T02:02Z): the branch tests of
core/faces-finder run again with the serial build of the merged tree core/nrpic must
write the same bytes as the branch session's runs of the same scripts.

    rerun_compare.py --pair NAME=OLD_RUN_DIR,NEW_RUN_DIR [--pair ...] --out DIR

For every file under OLD (recursively) the file of the same relative path under NEW is
read and compared byte for byte.  Records of the harness and of the shell are skipped
(sha256sums.txt, .nrpic/, run.log, *.log, *.gpumem.csv, the figures fig_*.pdf/png).
Where the bytes differ, the comparison is repeated after the old run id and build path
are replaced by the new ones in the old file (a stored input deck names the run
directory and a summary names the executable): such a file counts as "same up to
paths".  A file that differs after that is "DIFFERS"; a file missing on one side is
listed.  The script's own verdict lines (summary.json, first level) are printed side by
side.

Writes DIR/rerun_compare.json and DIR/fig_rerun_compare.{pdf,png}; exit status 0 if no
file differs and none is missing.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "python"))

SKIP_DIRS = {".nrpic"}
SKIP_NAMES = {"sha256sums.txt", "run.log"}
SKIP_SUFFIX = (".log", ".gpumem.csv")
SKIP_PREFIX = ("fig_",)

OLD_BUILDS = [b"/data/haiyangw/nrpic/wt/core-s5/.work/build_cpu_ff/src/athena",
              b"/data/haiyangw/nrpic/wt/core-s5/.work/build_omp_ff/src/athena"]
NEW_BUILD = b"/data/haiyangw/nrpic/wt/core/.work/build_cpu_v09rc/src/athena"


def files_under(root):
    out = []
    for d, dirs, names in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for n in sorted(names):
            if n in SKIP_NAMES or n.endswith(SKIP_SUFFIX) or n.startswith(SKIP_PREFIX):
                continue
            out.append(os.path.relpath(os.path.join(d, n), root))
    return out


def read(path):
    with open(path, "rb") as f:
        return f.read()


def compare(old, new):
    old_id = os.path.basename(os.path.normpath(old)).encode()
    new_id = os.path.basename(os.path.normpath(new)).encode()
    res = {"identical": [], "same_up_to_paths": [], "differs": [],
           "missing_new": [], "missing_old": []}
    old_files = files_under(old)
    new_files = set(files_under(new))
    for rel in old_files:
        p_new = os.path.join(new, rel)
        if rel not in new_files:
            res["missing_new"].append(rel)
            continue
        a, b = read(os.path.join(old, rel)), read(p_new)
        if a == b:
            res["identical"].append(rel)
            continue
        a2 = a.replace(old_id, new_id)
        for ob in OLD_BUILDS:
            a2 = a2.replace(ob, NEW_BUILD)
        if a2 == b:
            res["same_up_to_paths"].append(rel)
        else:
            res["differs"].append(rel)
    res["missing_old"] = sorted(new_files - set(old_files))
    return res


def verdicts(run_dir):
    p = os.path.join(run_dir, "summary.json")
    if not os.path.exists(p):
        return None
    try:
        with open(p) as f:
            s = json.load(f)
    except (OSError, ValueError):
        return "unreadable"
    if isinstance(s, dict):
        return {k: v for k, v in s.items()
                if isinstance(v, (str, bool, int)) or k in ("checks", "verdict", "pass")}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", action="append", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    report = {}
    ok = True
    for spec in a.pair:
        name, dirs = spec.split("=", 1)
        old, new = dirs.split(",", 1)
        r = compare(old, new)
        r["old"], r["new"] = old, new
        r["verdict_old"], r["verdict_new"] = verdicts(old), verdicts(new)
        report[name] = r
        bad = r["differs"] or r["missing_new"] or r["missing_old"]
        ok = ok and not bad
        print(f"{name}: {len(r['identical'])} identical, {len(r['same_up_to_paths'])} "
              f"same up to paths, {len(r['differs'])} differ, {len(r['missing_new'])} "
              f"missing in new, {len(r['missing_old'])} only in new")
        for k in ("differs", "missing_new", "missing_old", "same_up_to_paths"):
            for rel in r[k][:12]:
                print(f"   {k}: {rel}")
    report["T9"] = "HOLDS" if ok else "FAILS"
    with open(os.path.join(a.out, "rerun_compare.json"), "w") as f:
        json.dump(report, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import nrpic.figstyle as fs
    fs.use_style()
    names = [n for n in report if n != "T9"]
    cats = [("identical", "identical"), ("same_up_to_paths", "same up to run path"),
            ("differs", "differs"), ("missing_new", "missing in rerun"),
            ("missing_old", "only in rerun")]
    fig, ax = plt.subplots(figsize=(6.8, 0.5 + 0.45 * len(names)))
    left = [0] * len(names)
    colors = [fs.PAL["blue"], fs.PAL2["sky"], fs.PAL["red"], fs.PAL["orange"], "grey"]
    for (key, label), c in zip(cats, colors):
        vals = [len(report[n][key]) for n in names]
        ax.barh(names, vals, left=left, color=c, label=label)
        left = [l + v for l, v in zip(left, vals)]
    ax.set_xlabel("output files of the branch run")
    ax.set_title(f"T9: merged build against the branch session's runs ({report['T9']})",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower right")
    ax.invert_yaxis()
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_rerun_compare"))
    print("T9", report["T9"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
