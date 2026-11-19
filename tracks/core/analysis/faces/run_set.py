#!/usr/bin/env python3
"""Run the cases of one plan of the package faces on the processors, several at a time.

    run_set.py <plan.json> [--jobs N] [--only case1,case2] [--out DIR]

A plan is a JSON file

    {"exe": "<path of the athena executable, relative to the worktree root>",
     "ball": {"M": 0.5, "Rb": 6, "edge": 1.5, "h": 0.5},        (only if a case needs it)
     "cases": {"<name>": {"input": "<athinput, relative to this directory>",
                          "args": ["block/par=value", ...],
                          "exe": "<optional: another executable for this case>"}}}

Each case runs in <out>/<name>/ (out: --out, else $NRPIC_RUN_DIR, the directory
nrpic-run gives a registered run).  The ball's initial data are written once into
<out>/ic by problems/ic/make_ball.py and given to the cases whose input is ball.athinput.
The serial executable uses one core per case.  cases.json in <out> records the command,
the exit status and the wall time of every case.
"""

import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


def make_ball(out, par):
    ic = os.path.join(out, "ic")
    os.makedirs(ic, exist_ok=True)
    stem = os.path.join(ic, "ball")
    if not os.path.exists(stem + ".nrp"):
        cmd = [sys.executable, os.path.join(ROOT, "problems", "ic", "make_ball.py"),
               "--M", str(par["M"]), "--Rb", str(par["Rb"]), "--edge", str(par["edge"]),
               "--h", str(par["h"]), "--tracers", "", "--sample", "0",
               "--out", ic, "--prefix", "ball"]
        with open(os.path.join(ic, "make_ball.log"), "w") as f:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT)
    return stem


def run_case(name, case, exe, out, ball_stem):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    inp = os.path.join(HERE, case["input"])
    args = list(case.get("args", []))
    if os.path.basename(inp).startswith("ball"):
        args += [f"particles/particle_file={ball_stem}.nrp",
                 f"problem/comp0_file={ball_stem}.tab"]
    cmd = [exe, "-i", inp, "-d", d] + args
    t0 = time.time()
    with open(os.path.join(d, "athena.log"), "w") as f:
        f.write(" ".join(cmd) + "\n")
        f.flush()
        rc = subprocess.run(cmd, cwd=d, stdout=f, stderr=subprocess.STDOUT).returncode
    return name, {"command": cmd, "exit": rc, "wall_s": round(time.time() - t0, 1)}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("plan")
    p.add_argument("--jobs", type=int, default=8)
    p.add_argument("--only", default="")
    p.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = p.parse_args()
    if not a.out:
        sys.exit("no output directory: give --out or run through nrpic-run")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    with open(a.plan) as f:
        plan = json.load(f)
    cases = plan["cases"]
    if a.only:
        cases = {k: cases[k] for k in a.only.split(",")}
    ball_stem = make_ball(out, plan["ball"]) if "ball" in plan else ""
    record = {}
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = []
        for name, case in cases.items():
            exe = os.path.join(ROOT, case.get("exe", plan["exe"]))
            futs.append(ex.submit(run_case, name, case, exe, out, ball_stem))
        for fu in cf.as_completed(futs):
            name, rec = fu.result()
            record[name] = rec
            print(f"{name}: exit {rec['exit']}, {rec['wall_s']} s", flush=True)
            with open(os.path.join(out, "cases.json"), "w") as f:
                json.dump({"plan": os.path.abspath(a.plan), "cases": record}, f, indent=1)
    bad = [k for k, v in record.items() if v["exit"] != 0]
    if bad:
        sys.exit("failed cases: " + ", ".join(bad))


if __name__ == "__main__":
    main()
