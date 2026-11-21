#!/usr/bin/env python3
"""Test of scripts/submit_chain.sh without Slurm and without AthenaK: outside kills and
the run-specific process name (decision 0021 item 6).

    python3 scripts/tests/test_submit_chain.py --out DIR

A fake `sbatch` (records its arguments, prints a job id, starts nothing) and a fake
`squeue` (no job) come first in PATH. The "executable" is a bash script that takes its
next action from DIR/<scenario>/plan:
  kill9    sends SIGKILL to its own process id (an outside `pkill -9`: exit 137)
  kill15   sends SIGTERM to its own process id (an outside `pkill`: exit 143)
  wall     prints a cycle line and "Terminating on wall clock limit", writes a restart
  tlim     prints a cycle line and "Terminating on time limit"
  fail1    exits 1 without a message
  killmsg  prints "Terminating on time limit", then SIGKILL to itself
and records the name of its own process (/proc/self/comm) in DIR/<scenario>/comm.log.
Each Slurm job of the chain is played by calling `submit_chain.sh --job RUNDIR` directly,
as long as the chain is QUEUED. Kills are sent only to the fake's own process id.
Writes DIR/summary.json and DIR/fig_submit_chain.{pdf,png}; exit status 0 if every
expectation holds.
"""
import argparse
import json
import os
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CHAIN = os.path.join(REPO, "scripts", "submit_chain.sh")

FAKE_SBATCH = """#!/usr/bin/env bash
n=$(( $(cat "$FAKE_DIR/sbatch_count" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$FAKE_DIR/sbatch_count"
echo "$*" >> "$FAKE_DIR/sbatch_calls.log"
echo "$((900000 + n))"
"""
FAKE_SQUEUE = """#!/usr/bin/env bash
exit 0
"""
FAKE_EXE = """#!/usr/bin/env bash
# fake AthenaK for scripts/tests/test_submit_chain.py
echo "$(cat /proc/$$/comm) $(basename "$0")" >> "$FAKE_DIR/comm.log"
act=$(head -n 1 "$FAKE_DIR/plan"); sed -i 1d "$FAKE_DIR/plan"
n=$(( $(cat "$FAKE_DIR/cycle" 2>/dev/null || echo 0) + 10 )); echo "$n" > "$FAKE_DIR/cycle"
echo "Setup complete, entering main loop..."
case $act in
  kill9)   kill -KILL $$ ;;
  kill15)  kill -TERM $$ ;;
  wall)    mkdir -p rst; : > "rst/fake.$(printf %05d "$n").rst"
           echo "time=1.0e+00 cycle=$n"; echo; echo "Terminating on wall clock limit" ;;
  tlim)    echo "time=2.0e+00 cycle=$n"; echo; echo "Terminating on time limit" ;;
  fail1)   exit 1 ;;
  killmsg) echo "time=2.0e+00 cycle=$n"; echo; echo "Terminating on time limit"; kill -KILL $$ ;;
esac
exit 0
"""
INPUT = """<job>
basename = fake
<output1>
file_type = rst
dt = 1.0
"""

SCENARIOS = {
    # name: (plan, expected status after each job, expected number of sbatch calls,
    #        text the final reason must contain)
    "A_two_kills_then_done": (["kill9", "kill15", "wall", "tlim"],
                              ["QUEUED", "QUEUED", "QUEUED", "DONE"], 4, "tlim"),
    "B_three_kills_fail": (["kill9", "kill9", "kill9"],
                           ["QUEUED", "QUEUED", "FAILED"], 3, "killed from outside 3 times"),
    "C_count_resets": (["kill9", "kill15", "wall", "kill9", "kill9", "tlim"],
                       ["QUEUED"] * 5 + ["DONE"], 6, "tlim"),
    "D_plain_failure": (["fail1"], ["FAILED"], 1, "exit status 1"),
    "E_kill_after_message": (["killmsg"], ["FAILED"], 1, "exit status 137"),
    "G_old_config": (["kill9", "tlim"], ["QUEUED", "DONE"], 2, "tlim"),
}


def write_exec(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP)


def read(path, default=""):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return default


def run_scenario(out, name, plan, fakebin):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=False)
    rundir = os.path.join(d, "run")
    exe = os.path.join(d, "fake_athena")
    write_exec(exe, FAKE_EXE)
    with open(os.path.join(d, "plan"), "w") as f:
        f.write("\n".join(plan) + "\n")
    inp = os.path.join(d, "in.athinput")
    with open(inp, "w") as f:
        f.write(INPUT)
    env = dict(os.environ)
    for k in list(env):
        if k.startswith(("SLURM_", "SBATCH_", "PROC_NAME", "MAX_OUTSIDE")):
            del env[k]
    env.update(PATH=fakebin + os.pathsep + env["PATH"], FAKE_DIR=d, ATHENA_EXE=exe,
               ATHENA_WALL="00:01:00")
    r = subprocess.run(["bash", CHAIN, rundir, inp], env=env, capture_output=True, text=True)
    res = {"start_rc": r.returncode, "start_out": r.stdout + r.stderr, "statuses": []}
    c = os.path.join(rundir, "chain")
    if name == "G_old_config":
        # a chain started before PROC_NAME existed: its config.sh has no such lines
        cfg = os.path.join(c, "config.sh")
        lines = [x for x in read(cfg).splitlines(True)
                 if not x.startswith(("PROC_NAME=", "MAX_OUTSIDE_KILLS="))]
        with open(cfg, "w") as f:
            f.writelines(lines)
        for fn in os.listdir(c):
            if fn.startswith("nrc-"):
                os.unlink(os.path.join(c, fn))
    jobs = 0
    while read(os.path.join(c, "STATUS")).strip() == "QUEUED" and jobs < 10:
        jobs += 1
        jenv = dict(env, SLURM_JOB_ID=str(800000 + jobs))
        jr = subprocess.run(["bash", CHAIN, "--job", rundir], env=jenv, capture_output=True,
                            text=True)
        res["statuses"].append(read(os.path.join(c, "STATUS")).strip())
        res.setdefault("job_rc", []).append(jr.returncode)
    ev = read(os.path.join(c, "events.log")).splitlines()
    res["events"] = ev
    res["final_reason"] = [x for x in ev if "STATUS" in x][-1] if ev else ""
    res["sbatch_calls"] = int(read(os.path.join(d, "sbatch_count"), "0").strip() or 0)
    res["comm"] = [x.split()[0] for x in read(os.path.join(d, "comm.log")).splitlines()]
    res["exe_names"] = [x.split()[1] for x in read(os.path.join(d, "comm.log")).splitlines()]
    res["proc_name_config"] = [x for x in read(os.path.join(c, "config.sh")).splitlines()
                               if x.startswith("PROC_NAME=")]
    res["outside_kills_file"] = read(os.path.join(c, "outside_kills")).strip()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    fakebin = os.path.join(out, "fakebin")
    os.makedirs(fakebin, exist_ok=True)
    write_exec(os.path.join(fakebin, "sbatch"), FAKE_SBATCH)
    write_exec(os.path.join(fakebin, "squeue"), FAKE_SQUEUE)

    summary, checks = {}, {}
    for name, (plan, want, nsb, reason) in SCENARIOS.items():
        r = run_scenario(out, name, plan, fakebin)
        summary[name] = r
        checks[name + ": statuses"] = r["statuses"] == want
        checks[name + ": sbatch calls"] = r["sbatch_calls"] == nsb
        checks[name + ": final reason"] = reason in r["final_reason"]
        checks[name + ": every run under the run-specific name"] = (
            len(r["comm"]) == len(want) and len(set(r["comm"])) == 1
            and r["comm"][0].startswith("nrc-") and "athena" not in r["comm"][0])
    # the name is the same for every segment of one chain and differs between chains
    names = {n: summary[n]["comm"][0] for n in summary if summary[n]["comm"]}
    checks["names differ between chains"] = len(set(names.values())) == len(names)
    # a PROC_NAME that contains "athena" is refused at start
    d = os.path.join(out, "H_bad_name")
    os.makedirs(d)
    with open(os.path.join(d, "in.athinput"), "w") as f:
        f.write(INPUT)
    write_exec(os.path.join(d, "fake_athena"), FAKE_EXE)
    env = dict(os.environ, PATH=fakebin + os.pathsep + os.environ["PATH"], FAKE_DIR=d,
               ATHENA_EXE=os.path.join(d, "fake_athena"), PROC_NAME="athena_run1")
    r = subprocess.run(["bash", CHAIN, os.path.join(d, "run"), os.path.join(d, "in.athinput")],
                       env=env, capture_output=True, text=True)
    summary["H_bad_name"] = {"rc": r.returncode, "out": r.stdout + r.stderr}
    checks["H_bad_name: refused"] = (r.returncode != 0 and "PROC_NAME" in r.stderr
                                     and not os.path.exists(os.path.join(d, "sbatch_count")))
    summary["checks"] = checks
    summary["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    for k, v in checks.items():
        print("%-62s %s" % (k, "held" if v else "FAILED"))
    for n in SCENARIOS:
        print("%-24s statuses %s  sbatch %d  name %s" % (
            n, summary[n]["statuses"], summary[n]["sbatch_calls"],
            summary[n]["comm"][0] if summary[n]["comm"] else "-"))

    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    fig.subplots_adjust(left=0.27, right=0.80, bottom=0.17, top=0.90)
    style = {"kill9": ("x", fs.SERIES[1], "outside SIGKILL (137)"),
             "kill15": ("+", fs.SERIES[1], "outside SIGTERM (143)"),
             "wall": ("o", fs.SERIES[0], "wall-clock stop"),
             "tlim": ("s", fs.SERIES[2], "time limit"),
             "fail1": ("v", "k", "exit 1, no message"),
             "killmsg": ("^", "k", "SIGKILL after the message")}
    seen = set()
    for i, (name, (plan, want, _, _)) in enumerate(SCENARIOS.items()):
        st = summary[name]["statuses"]
        for j, act in enumerate(plan[:len(st)]):
            m, c, lab = style[act]
            ax.plot(j + 1, i, m, color=c, ms=8, mew=1.6,
                    label=None if lab in seen else lab)
            seen.add(lab)
            ax.annotate(st[j][0], (j + 1, i), xytext=(0, 7), textcoords="offset points",
                        ha="center", fontsize=7)
    ax.set_yticks(range(len(SCENARIOS)))
    ax.set_yticklabels(list(SCENARIOS), fontsize=7)
    ax.set_xlabel("segment (one Slurm job each)")
    ax.set_xlim(0.5, 6.8)
    ax.set_ylim(-0.6, len(SCENARIOS) - 0.4)
    ax.invert_yaxis()
    ax.set_title("chain state after each segment (Q queued, D done, F failed)", fontsize=9)
    ax.legend(frameon=False, fontsize=7, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fs.save(fig, os.path.join(out, "fig_submit_chain"))
    plt.close(fig)
    print("TEST", summary["verdict"])
    return 0 if summary["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
