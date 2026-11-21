#!/usr/bin/env python3
"""Analysis of the finished members of the G2 series (package conv_ball, Track A, wave 3):
compare.py on every member found in the card-run directories given (DESIGN.md section 4),
then converge.py over all members analysed in this call and the numbers of earlier analyses
named with --prior. Run through nrpic-run (registered).

    analyse.py --card <card run dir> [--card ...] [--prior NAME=<numbers.json> ...] --out DIR [--jobs 4]

A member directory is <card run dir>/<member> (batch) or the card run directory itself when
it holds a chain (its name is given as --card <dir>:<member>).
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)

# member: (nest OUTER:HF_INV, legs [(leg, x)])
GEOM = {
    "A": ("16:16", [("mesh", 1 / 16), ("N", 1), ("R", 1.0), ("L", 16)]),
    "B": ("16:32", [("mesh", 1 / 32), ("NB", 1), ("RB", 1.0), ("LB", 16)]),
    "C": ("16:64", [("mesh", 1 / 64), ("meshN", 1 / 64)]),
    "A-N8": ("16:16", [("N", 8)]),
    "A-N64": ("16:16", [("N", 64), ("meshN", 1 / 16)]),
    "B-N8": ("16:32", [("NB", 8), ("meshN", 1 / 32)]),
    "A-R1.25": ("16:16", [("R", 1.25)]),
    "A-R1.35": ("16:16", [("R", 1.35)]),
    "B-R1.25": ("16:32", [("RB", 1.25)]),
    "A-L32": ("32:16", [("L", 32)]),
    "B-L32": ("32:32", [("LB", 32)]),
}


def compare(name, seg, prep, out):
    nest = GEOM[name][0]
    o_, hf_ = nest.split(":")
    root_dx = float(o_) / float(hf_)          # root cell: 2 outer / (2 / h_f) cells
    cmd = [sys.executable, os.path.join(HERE, "compare.py"), "--prep", prep, "--seg", seg, "--gauge", "leak",
           "--leak", "8", "--dx", f"{root_dx:g}", "--nest", nest, "--label", name, "--out", out,
           "--figdir", os.path.join(out, "figs")]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MPLBACKEND="Agg")
    with open(os.path.join(out, f"{name}_compare.log"), "w") as f:
        f.write("# " + " ".join(cmd) + "\n")
        f.flush()
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    return name, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", action="append", required=True)
    ap.add_argument("--prior", action="append", default=[])
    ap.add_argument("--prior-turnaround", action="append", default=[], help="turnaround.json of an earlier analysis")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    members = json.load(open(os.path.join(PKG, "lists", "members.json")))
    todo = []
    for c in a.card:
        if ":" in c:
            d, name = c.rsplit(":", 1)
            todo.append((name, d))
            continue
        for name in members:
            d = os.path.join(c, name)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "ball.nrpic.hst")):
                todo.append((name, d))
    print("members:", [t[0] for t in todo])
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        res = list(ex.map(lambda t: compare(t[0], t[1], members[t[0]]["prep"], a.out), todo))
    status = {n: rc for n, rc in res}
    print("compare.py exit codes:", status)
    specs = []
    numbers = {n: os.path.join(a.out, f"{n}_numbers.json") for n, rc in res if rc == 0}
    for p in a.prior:
        n, path = p.split("=", 1)
        numbers.setdefault(n, path)
    for n, path in numbers.items():
        for leg, x in GEOM[n][1]:
            specs += ["--member", f"{n}:{leg}:{x:g}:{path}"]
    # turnaround estimators of runs_ball entry 13 (cycloid fit C) on the core particles; the core
    # and its exact shells are the same in all data sets (DESIGN.md 2f), so data set 3's prep serves
    ok = [n for n, rc_ in res if rc_ == 0]
    tspec = []
    for n in ok:
        tspec += ["--run", f"{a.out}:{n}:{1.0 / float(GEOM[n][0].split(':')[1]):g}:leak"]
    ta_json = []
    if tspec:
        with open(os.path.join(a.out, "turnaround.log"), "w") as f:
            rc_t = subprocess.call([sys.executable, os.path.join(HERE, "turnaround.py")] + tspec +
                                   ["--prep", members["A"]["prep"], "--out", a.out, "--figdir", os.path.join(a.out, "figs")],
                                   stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ, MPLBACKEND="Agg"))
        status["turnaround.py"] = rc_t
        if rc_t == 0:
            ta_json = ["--turnaround", os.path.join(a.out, "turnaround.json")]
    for p in a.prior_turnaround:
        ta_json += ["--turnaround", p]
    rc = subprocess.call([sys.executable, os.path.join(HERE, "converge.py")] + specs + ta_json + ["--out", a.out],
                         env=dict(os.environ, MPLBACKEND="Agg"))
    json.dump(dict(compare_exit=status, numbers=numbers, converge_exit=rc),
              open(os.path.join(a.out, "analyse.json"), "w"), indent=1)
    sys.exit(0 if rc == 0 and all(v == 0 for v in status.values()) else 1)


if __name__ == "__main__":
    main()
