#!/usr/bin/env python3
"""Test of scripts/submit_chain.sh without Slurm and without AthenaK: outside kills and
the run-specific process name (decision 0021 item 6); attempts cut by SIGTERM, which do
not count as segments, the wait for an executable that writes a restart file on the
signal, and the end of a chain at its segment cap without a further job (decision 0032
item 2).

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
  jobterm  sends SIGTERM to the job script (its grandparent: the preemption of the job)
           and answers the forwarded signal as an AthenaK with the handler of
           utils/term_signal.cpp does: half a second later a restart file, "Terminating
           on signal SIGTERM", exit status 143
  jobterm_old   the same signal to the job; the executable has no handler and dies
  jobterm_late  as jobterm, two seconds after its start (with ATHENA_WALL=00:00:01 the
           attempt has then had its whole segment and counts)
  term_handled  an outside SIGTERM answered by the handler: restart file, the message,
           exit status 143, the job itself not signalled
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
FAKE_EXE = """#!/bin/bash
# fake AthenaK for scripts/tests/test_submit_chain.py. The interpreter is named directly:
# with "#!/usr/bin/env bash" env would exec bash and the process would be named "bash"
# (first run of this test, core-20261121-080555-9730e2a), whereas the kernel names a
# script started directly after the file it executed, as it names a binary.
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
  jobterm|jobterm_late)
           on_term() {
             sleep 0.5; mkdir -p rst; : > "rst/fake.$(printf %05d "$n").rst"
             echo "time=1.5e+00 cycle=$n"; echo; echo "Terminating on signal SIGTERM"
             echo "restart outputs written after the cycle in progress: 1 in 0.001 s, done 0.500 s after the signal reached rank 0; exit status 143"
             exit 143
           }
           trap on_term TERM
           [[ $act == jobterm_late ]] && sleep 2
           kill -TERM "$(ps -o ppid= -p $PPID | tr -d ' ')"
           for i in $(seq 100); do sleep 0.1; done; exit 9 ;;
  jobterm_old)
           kill -TERM "$(ps -o ppid= -p $PPID | tr -d ' ')"
           for i in $(seq 100); do sleep 0.1; done; exit 9 ;;
  term_handled)
           mkdir -p rst; : > "rst/fake.$(printf %05d "$n").rst"
           echo "time=1.5e+00 cycle=$n"; echo; echo "Terminating on signal SIGTERM"
           echo "restart outputs written after the cycle in progress: 1 in 0.001 s, done 0.300 s after the signal reached rank 0; exit status 143"
           exit 143 ;;
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
    # decision 0032 item 2 (a fifth entry: environment of the chain)
    # ten preempted attempts do not use up three segments; the three counted ones do,
    # and the chain ends in the job of the third without a further sbatch
    "I_preempted_not_counted": (["jobterm"] * 10 + ["wall", "wall", "wall"],
                                ["QUEUED"] * 12 + ["FAILED"], 13, "MAX_SEGMENTS=3 reached",
                                {"MAX_SEGMENTS": "3"}),
    # the stray resubmission: two segments allowed, both end at the wall clock
    "K_no_stray_job": (["wall", "wall"], ["QUEUED", "FAILED"], 2, "MAX_SEGMENTS=2 reached",
                       {"MAX_SEGMENTS": "2"}),
    "L_term_in_a_row": (["jobterm", "jobterm", "jobterm"], ["QUEUED", "QUEUED", "FAILED"], 3,
                        "ended by SIGTERM 3 times in a row", {"MAX_TERM_IN_A_ROW": "2"}),
    "M_outside_term_handled": (["term_handled", "tlim"], ["QUEUED", "DONE"], 2, "tlim"),
    "O_old_executable": (["jobterm_old", "tlim"], ["QUEUED", "DONE"], 2, "tlim"),
    # signalled after ATHENA_WALL: the attempt counts, and it was the only one allowed
    "P_late_term_counts": (["jobterm_late"], ["FAILED"], 1, "MAX_SEGMENTS=1 reached",
                           {"MAX_SEGMENTS": "1", "ATHENA_WALL": "00:00:01"}),
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


def run_scenario(out, name, plan, fakebin, extra_env=None):
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
        if k.startswith(("SLURM_", "SBATCH_", "PROC_NAME", "MAX_", "ATHENA_WALL")):
            del env[k]
    env.update(PATH=fakebin + os.pathsep + env["PATH"], FAKE_DIR=d, ATHENA_EXE=exe,
               ATHENA_WALL="00:01:00")
    env.update(extra_env or {})
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
    while read(os.path.join(c, "STATUS")).strip() == "QUEUED" and jobs < 20:
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
    res["uncounted_file"] = read(os.path.join(c, "uncounted"), "0").strip()
    res["rst_files"] = sorted(os.listdir(os.path.join(rundir, "rst"))) if os.path.isdir(
        os.path.join(rundir, "rst")) else []
    res["env"] = extra_env or {}
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
    for name, sc in SCENARIOS.items():
        plan, want, nsb, reason = sc[:4]
        r = run_scenario(out, name, plan, fakebin, sc[4] if len(sc) > 4 else None)
        summary[name] = r
        checks[name + ": statuses"] = r["statuses"] == want
        checks[name + ": sbatch calls"] = r["sbatch_calls"] == nsb
        checks[name + ": final reason"] = reason in r["final_reason"]
        checks[name + ": every run under the run-specific name"] = (
            len(r["comm"]) == len(want) and len(set(r["comm"])) == 1
            and r["comm"][0].startswith("nrc-") and "athena" not in r["comm"][0])
    # decision 0032 item 2: what the new scenarios must show beyond their statuses
    ev = lambda n, text: sum(text in x for x in summary[n]["events"])
    checks["I: ten attempts not counted"] = (
        summary["I_preempted_not_counted"]["uncounted_file"] == "10"
        and ev("I_preempted_not_counted", "not counted as a segment") == 10)
    checks["I: the executable ended by itself after every signal, with a restart file"] = (
        ev("I_preempted_not_counted", "the run stopped by itself") == 10
        and len(summary["I_preempted_not_counted"]["rst_files"]) == 13)
    checks["I: resubmitted before the executable had ended"] = all(
        a < b for a, b in zip(
            [i for i, x in enumerate(summary["I_preempted_not_counted"]["events"])
             if "resubmitted after SIGTERM" in x],
            [i for i, x in enumerate(summary["I_preempted_not_counted"]["events"])
             if "the run stopped by itself" in x]))
    checks["K: no job after the last segment"] = (
        ev("K_no_stray_job", "submitted job") == 2 and len(summary["K_no_stray_job"]["comm"]) == 2)
    checks["M: outside SIGTERM with restart file, not counted"] = (
        ev("M_outside_term_handled", "restart file written") == 1
        and summary["M_outside_term_handled"]["uncounted_file"] == "1")
    checks["O: old executable ends without a restart file of its own"] = (
        ev("O_old_executable", "without a restart file of its own") == 1
        and summary["O_old_executable"]["uncounted_file"] == "1")
    checks["P: late signal counted"] = (summary["P_late_term_counts"]["uncounted_file"] == "0")
    # the start command on a chain that has used its segments is refused, no job
    dk = os.path.join(out, "K_no_stray_job")
    envk = dict(os.environ, PATH=fakebin + os.pathsep + os.environ["PATH"], FAKE_DIR=dk,
                ATHENA_EXE=os.path.join(dk, "fake_athena"), MAX_SEGMENTS="2")
    r = subprocess.run(["bash", CHAIN, os.path.join(dk, "run"), os.path.join(dk, "in.athinput")],
                       env=envk, capture_output=True, text=True)
    summary["N_start_at_cap"] = {"rc": r.returncode, "out": r.stdout + r.stderr,
                                 "sbatch_calls": int(read(os.path.join(dk, "sbatch_count"), "0"))}
    checks["N_start_at_cap: refused, no job"] = (
        r.returncode != 0 and "used its 2 segments" in r.stderr
        and summary["N_start_at_cap"]["sbatch_calls"] == 2)
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
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    fig.subplots_adjust(left=0.19, right=0.66, bottom=0.12, top=0.92)
    style = {"kill9": ("x", fs.SERIES[1], "outside SIGKILL (137)"),
             "kill15": ("+", fs.SERIES[1], "outside SIGTERM (143)"),
             "wall": ("o", fs.SERIES[0], "wall-clock stop"),
             "tlim": ("s", fs.SERIES[2], "time limit"),
             "fail1": ("v", "k", "exit 1, no message"),
             "killmsg": ("^", "k", "SIGKILL after the message"),
             "jobterm": ("D", fs.SERIES[3], "SIGTERM to the job, restart file on the signal"),
             "jobterm_late": ("D", "k", "the same after ATHENA_WALL (counts)"),
             "jobterm_old": ("d", fs.SERIES[3], "SIGTERM to the job, no handler"),
             "term_handled": ("*", fs.SERIES[1], "outside SIGTERM, restart file")}
    seen = set()
    for i, (name, sc) in enumerate(SCENARIOS.items()):
        plan = sc[0]
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
    ax.set_xlim(0.5, max(len(sc[0]) for sc in SCENARIOS.values()) + 0.8)
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
