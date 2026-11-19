#!/usr/bin/env python3
"""Test R0 of the initial-data solver, second pass: without <particles> id_solve the new
executable writes the same bytes as the release executable (core-v0.3).

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/regress_r0.py
        --base <release athena> --new <athena of this branch> [--cases ...] [--jobs N]

Cases: the seven set-ups of tracks/core/tools/regress_relativistic.py (geodesics with
both pushers, deposit on a refined mesh, East's periodic cosmology, Oppenheimer-Snyder on
a refined mesh, Jeans wave and a binary on four multigrid levels: the multigrid module
with octets, whose boundary routine this branch touches) and the two Newtonian set-ups of
tracks/core/analysis/idsolve/regress_newton.py (isolated with the multipole boundary,
periodic). Both executables run every case in a directory of their own inside the run
directory; every output file except run.log is compared byte by byte, and for the gas
cases the result lines of the log. Report: regress_r0.json in the run directory and in
this directory.
"""
import argparse
import concurrent.futures
import filecmp
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "tools"))
sys.path.insert(0, os.path.join(WT, "tracks", "core", "analysis", "idsolve"))
import regress_relativistic as rr  # noqa: E402
import regress_newton as rn        # noqa: E402

CASES = {}
for k, v in rr.CASES.items():
    CASES[k] = dict(inp=v["inp"], files=list(v["files"]), args=list(v["args"]))
for k, v in rn.CASES.items():
    CASES["newton_" + k] = dict(inp=v["inp"], files=[os.path.join(rn.IC, v["ic"])],
                                args=["particles/particle_file=" + v["ic"]] + v["args"])


def run_one(job):
    exe, case, d = job
    c = CASES[case]
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(WT, c["inp"]), d)
    for f in c["files"]:
        dst = os.path.join(d, os.path.basename(f))
        if not os.path.exists(dst):
            os.symlink(f, dst)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(d, "run.log"), "w") as log:
        r = subprocess.run([exe, "-i", os.path.basename(c["inp"])] + c["args"], cwd=d,
                           stdout=log, stderr=subprocess.STDOUT, env=env)
    return case, d, r.returncode, time.time() - t0


def compare(da, db):
    differ, same = [], []
    names = set()
    for d in (da, db):
        for root, _, files in os.walk(d):
            for f in files:
                names.add(os.path.relpath(os.path.join(root, f), d))
    for n in sorted(names):
        if n in rr.SKIP or os.path.islink(os.path.join(da, n)) or n.endswith(".athinput"):
            continue
        fa, fb = os.path.join(da, n), os.path.join(db, n)
        if not (os.path.exists(fa) and os.path.exists(fb)):
            differ.append(n + " (missing in one run)")
        elif filecmp.cmp(fa, fb, shallow=False):
            same.append(n)
        else:
            differ.append(n)
    la = rr.log_results(os.path.join(da, "run.log"))
    lb = rr.log_results(os.path.join(db, "run.log"))
    if la or lb:
        (same if la == lb else differ).append("run.log (%d result lines)" % len(la))
    return same, differ


def figure(report, cases, out):
    """Files identical and differing per case (bars), into figs/ and the run directory."""
    sys.path.insert(0, os.path.join(WT, "python"))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    same = [len(report["cases"][c]["identical"]) for c in cases]
    diff = [len(report["cases"][c]["differ"]) for c in cases]
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 0.25*len(cases) + 0.9))
    y = list(range(len(cases)))
    ax.barh(y, same, color=fs.PAL["blue"], label="identical")
    ax.barh(y, diff, left=same, color=fs.PAL["red"], label="differing")
    ax.set_yticks(y)
    ax.set_yticklabels(cases, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("output files compared (release against this branch)")
    ax.legend(fontsize=6, loc="lower right")
    fig.tight_layout()
    for d in (os.path.join(HERE, "figs"), out):
        fs.save(fig, os.path.join(d, "regress_r0"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--cases", default=",".join(CASES))
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    cases = [c for c in a.cases.split(",") if c]
    jobs = []
    for c in cases:
        jobs.append((os.path.abspath(a.base), c, os.path.join(a.out, c, "base")))
        jobs.append((os.path.abspath(a.new), c, os.path.join(a.out, c, "new")))
    status = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for case, d, rc, sec in ex.map(run_one, jobs):
            status[os.path.relpath(d, a.out)] = dict(exit=rc, wall_s=round(sec, 1))
            print("%s: exit %d in %.0f s" % (os.path.relpath(d, a.out), rc, sec), flush=True)
    report, bad = dict(base=a.base, new=a.new, status=status, cases={}), 0
    for c in cases:
        same, differ = compare(os.path.join(a.out, c, "base"), os.path.join(a.out, c, "new"))
        ok = (status[c + "/base"]["exit"] == 0 and status[c + "/new"]["exit"] == 0)
        report["cases"][c] = dict(identical=same, differ=differ, both_exit_0=ok)
        bad += len(differ) + (0 if (same and ok) else 1)
        print("%-16s identical files: %3d  differing: %s  exit 0 in both: %s"
              % (c, len(same), differ if differ else "none", ok), flush=True)
    report["all_identical"] = (bad == 0)
    figure(report, cases, a.out)
    for p in (os.path.join(a.out, "regress_r0.json"), os.path.join(HERE, "regress_r0.json")):
        with open(p, "w") as f:
            json.dump(report, f, indent=1)
            f.write("\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
