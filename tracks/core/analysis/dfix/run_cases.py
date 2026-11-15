#!/usr/bin/env python3
"""Run a list of AthenaK cases on the processors inside one registered run.

    harness/bin/nrpic-run submit --kind scouting --gate G2 --purpose "..." --cores N -- \
        python3 tracks/core/analysis/dfix/run_cases.py tracks/core/analysis/dfix/cases/<list> [--jobs N]

Each non-empty line of the list that does not start with '#':
    <name> <executable> <athinput | file.rst> [athena arguments ...]
The words {repo} and {run} are replaced by the worktree root and by the output directory
of the registered run ($NRPIC_RUN_DIR); a third word that ends in .rst is passed with -r,
anything else with -i. Each case runs in $NRPIC_RUN_DIR/<name>/ with its log in
athena.log there. A line `@wait` waits for the cases started so far (a later case may then
read their output, for example a restart file). Exit status: number of failed cases.
"""
import os
import shlex
import subprocess
import sys
import time


def main():
    args = sys.argv[1:]
    jobs = 1
    if "--jobs" in args:
        k = args.index("--jobs")
        jobs = int(args[k + 1])
        del args[k:k + 2]
    lst = args[0]
    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
    run = os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("run_cases.py: NRPIC_RUN_DIR is not set (start it through nrpic-run)")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    running, failed = [], 0

    def reap(block_all=False):
        nonlocal failed
        while running and (block_all or len(running) >= jobs):
            for item in list(running):
                name, p, t0, log = item
                rc = p.poll()
                if rc is not None:
                    log.close()
                    running.remove(item)
                    print(f"{name}: exit {rc} after {time.time() - t0:.1f} s", flush=True)
                    if rc != 0:
                        failed += 1
            if running and (block_all or len(running) >= jobs):
                time.sleep(0.2)

    for line in open(lst):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "@wait":
            reap(block_all=True)
            continue
        w = [x.replace("{repo}", repo).replace("{run}", run) for x in shlex.split(line)]
        name, exe, inp, rest = w[0], w[1], w[2], w[3:]
        d = os.path.join(run, name)
        os.makedirs(d, exist_ok=True)
        cmd = [exe, "-r" if inp.endswith(".rst") else "-i", inp, "-d", d] + rest
        reap()
        log = open(os.path.join(d, "athena.log"), "w")
        log.write("# " + " ".join(cmd) + "\n")
        log.flush()
        p = subprocess.Popen(cmd, cwd=d, env=env, stdout=log, stderr=subprocess.STDOUT)
        running.append((name, p, time.time(), log))
    reap(block_all=True)
    return failed


if __name__ == "__main__":
    sys.exit(main())
