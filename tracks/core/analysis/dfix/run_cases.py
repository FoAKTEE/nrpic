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

With --card [--time hh:mm:ss] the cases run one after another on one card inside a single
Slurm job (sbatch --wait, partition preempt), each through scripts/gpu_run.sh, which
writes the log athena.<stamp>.log with the peak card memory into the case directory. The
executables are copied into the run directory first. The line `CARD_SECONDS <s>` printed
at the end is the elapsed time of the job as Slurm reports it.
"""
import os
import shlex
import subprocess
import sys
import time


def run_card(lst, repo, run, tlimit, env):
    import shutil
    lines, exes = ["#!/usr/bin/env bash", "rc=0"], {}
    for line in open(lst):
        line = line.strip()
        if not line or line.startswith("#") or line == "@wait":
            continue
        w = [x.replace("{repo}", repo).replace("{run}", run) for x in shlex.split(line)]
        name, exe, inp, rest = w[0], w[1], w[2], w[3:]
        if exe not in exes:
            exes[exe] = os.path.join(run, f"exe_{len(exes)}")
            shutil.copy2(exe, exes[exe])
        d = os.path.join(run, name)
        os.makedirs(d, exist_ok=True)
        cmd = [os.path.join(repo, "scripts", "gpu_run.sh"), d, inp] + rest
        lines.append(f"ATHENA_EXE={shlex.quote(exes[exe])} " + " ".join(shlex.quote(c) for c in cmd)
                     + f" > {shlex.quote(os.path.join(d, 'gpu_run.out'))} 2>&1 || rc=$((rc+1))")
        lines.append(f"echo \"{name}: failures so far $rc\"")
    lines.append("exit $rc")
    job = os.path.join(run, "job.sh")
    open(job, "w").write("\n".join(lines) + "\n")
    os.chmod(job, 0o755)
    p = subprocess.run(["sbatch", "--wait", "--parsable", "-p", "preempt", "--gres=gpu:1", "-c", "1",
                        "-t", tlimit, "-J", "dfix", "-o", os.path.join(run, "slurm-%j.out"), job],
                       capture_output=True, text=True, env=env)
    jid = p.stdout.strip().split(";")[0]
    print(f"Slurm job {jid}: sbatch exit {p.returncode} {p.stderr.strip()}", flush=True)
    secs = None
    for _ in range(10):
        q = subprocess.run(["sacct", "-j", jid, "-X", "-n", "-P", "-o", "ElapsedRaw,State"],
                           capture_output=True, text=True, env=env)
        w = q.stdout.strip().split("|")
        if len(w) == 2 and w[0].isdigit() and not w[1].startswith(("RUNNING", "PENDING")):
            secs = int(w[0])
            print(f"Slurm state {w[1]}")
            break
        time.sleep(3)
    out = os.path.join(run, f"slurm-{jid}.out")
    if os.path.isfile(out):
        sys.stdout.write(open(out).read())
    if secs is not None:
        print(f"CARD_SECONDS {secs}")
    return p.returncode


def main():
    args = sys.argv[1:]
    jobs = 1
    if "--jobs" in args:
        k = args.index("--jobs")
        jobs = int(args[k + 1])
        del args[k:k + 2]
    card = "--card" in args
    if card:
        args.remove("--card")
    tlimit = "00:30:00"
    if "--time" in args:
        k = args.index("--time")
        tlimit = args[k + 1]
        del args[k:k + 2]
    lst = args[0]
    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
    run = os.environ.get("NRPIC_RUN_DIR")
    if not run:
        sys.exit("run_cases.py: NRPIC_RUN_DIR is not set (start it through nrpic-run)")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    if card:
        return run_card(lst, repo, run, tlimit, env)
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
