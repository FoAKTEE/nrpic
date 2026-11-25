#!/usr/bin/env python3
"""The marker of the shared card queue never reaches a job (decision 0037 item 4).

    python3 scripts/tests/test_queue_marker.py --out DIR

The dispatcher of harness/bin/nrpic-queue marks the commands it runs with
NRPIC_QUEUE_DISPATCH=<entry id>:<token>. sbatch and srun export the caller's environment to
the job, so a job submitted by scripts/ would carry the marker, and a job could then itself
register and submit a card run beside the dispatcher. scripts/gpu_run.sh, gpu_batch.sh,
submit_chain.sh and _athena_job.sh remove every NRPIC_QUEUE_* variable at their top (and
submit_chain.sh again in its sbatch call). This test runs them end to end with the fake Slurm
of harness/tests/rc_fixture.py (its sbatch starts the job script at once in the background
with the environment sbatch was given, its srun runs the command, its nvidia-smi fails), in a
directory under DIR, with no card and no real job:

  A  gpu_run.sh BATCH=1 (sbatch, the job runs _athena_job.sh and the executable)
  B  gpu_run.sh blocking (srun)
  C  gpu_batch.sh with two runs (sbatch; in the job gpu_run.sh -> srun -> executable, twice)
  D  submit_chain.sh: first segment ends at the wall clock, the job resubmits its own next
     segment (the hand-over), the second ends at the time limit: DONE, two sbatch calls
  E  job side, the worst case of a job that was given the marker anyway: gpu_batch.sh with
     SLURM_JOB_ID set, and _athena_job.sh, both called with the marker
  F  control: A and D with the scripts as they were before the change (--old DIR, files
     taken from git), which must show the marker to sbatch and to the executable; otherwise
     this test could not fail

Every caller environment holds NRPIC_QUEUE_DISPATCH=q9001:<token>. Wrappers in front of the
fake sbatch and srun, and a wrapper in front of the fake executable, record whether they see
it. Writes DIR/summary.json and DIR/fig_queue_marker.{pdf,png}; exit status 0 if every
expectation holds.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "harness", "tests"))
import rc_fixture as RC  # noqa: E402  (fake Slurm programs only; make_repo is not used)

MARKER = "NRPIC_QUEUE_DISPATCH"
TOKEN = "q9001:" + "cd" * 12
NAMES = ("gpu_run.sh", "gpu_batch.sh", "submit_chain.sh", "_athena_job.sh")

RECORDER = """#!/bin/bash
# records whether the queue marker is in this process's environment, then runs the real one
echo "@WHAT@ ${NRPIC_QUEUE_DISPATCH-unset}" >> "@LOG@"
exec "@REAL@" "$@"
"""

DECK_RST = "<job>\nbasename = fake\n<output1>\nfile_type = rst\ndt = 1.0\n"
DECK_PLAIN = "<job>\nbasename = fake\n<output1>\nfile_type = hst\ndt = 1.0\n"


def write_exe(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, 0o755)


def setup(out):
    fb = os.path.join(out, "fakebin")
    st = os.path.join(out, "slurmstate")
    os.makedirs(fb)
    os.makedirs(st)
    log = os.path.join(out, "sightings.log")
    for fn, text in (("sbatch", RC.FAKE_SBATCH), ("squeue", RC.FAKE_SQUEUE), ("sacct", RC.FAKE_SACCT),
                     ("scancel", RC.FAKE_SCANCEL), ("srun", RC.FAKE_SRUN), ("nvidia-smi", RC.FAKE_NVSMI)):
        write_exe(os.path.join(fb, fn + (".real" if fn in ("sbatch", "srun") else "")),
                  text.replace("@STATE@", st))
    for fn in ("sbatch", "srun"):
        write_exe(os.path.join(fb, fn), RECORDER.replace("@WHAT@", fn).replace("@LOG@", log)
                  .replace("@REAL@", os.path.join(fb, fn + ".real")))
    write_exe(os.path.join(out, "athena.real"), RC.FAKE_ATHENA)
    write_exe(os.path.join(out, "athena"), RECORDER.replace("@WHAT@", "exe").replace("@LOG@", log)
              .replace("@REAL@", os.path.join(out, "athena.real")))
    for name, text in (("deck_rst.athinput", DECK_RST), ("deck_plain.athinput", DECK_PLAIN)):
        with open(os.path.join(out, name), "w") as f:
            f.write(text)
    return fb, st, log


def base_env(fb, out):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("SLURM_", "SBATCH_", "NRPIC_QUEUE_", "MAX_", "PROC_NAME", "ATHENA_"))}
    env.update(PATH=fb + os.pathsep + env["PATH"], ATHENA_EXE=os.path.join(out, "athena"),
               OMP_NUM_THREADS="1")
    env[MARKER] = TOKEN
    return env


def wait_jobs(st, timeout=90):
    """Until every fake job has an end file (the fake sbatch runs jobs in the background)."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        jobs = [j for j in os.listdir(st) if j.isdigit()]
        if all(os.path.exists(os.path.join(st, j, "end")) for j in jobs):
            time.sleep(0.5)       # a job may submit its successor just before it ends
            jobs2 = [j for j in os.listdir(st) if j.isdigit()]
            if jobs2 == jobs or all(os.path.exists(os.path.join(st, j, "end")) for j in jobs2):
                if sorted(jobs2) == sorted(jobs):
                    return True
        time.sleep(0.3)
    return False


def sightings(log, start):
    with open(log) as f:
        rows = [x.split() for x in f.read().splitlines()[start:]]
    return rows


def nlines(log):
    try:
        with open(log) as f:
            return len(f.read().splitlines())
    except OSError:
        return 0


def run_case(name, cmd, env, st, log, cwd, chain_dir=None, timeout=90):
    n0 = nlines(log)
    r = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    ok_wait = wait_jobs(st, timeout)
    if chain_dir:
        t0 = time.time()
        while time.time() - t0 < timeout:
            s = open(os.path.join(chain_dir, "chain", "STATUS")).read().strip() if os.path.exists(
                os.path.join(chain_dir, "chain", "STATUS")) else ""
            if s in ("DONE", "FAILED", "STOPPED"):
                break
            time.sleep(0.3)
        wait_jobs(st, timeout)
    rows = sightings(log, n0)
    res = {"rc": r.returncode, "out": (r.stdout + r.stderr)[-2000:], "jobs_ended": ok_wait,
           "rows": rows,
           "sbatch": [v for w, v in rows if w == "sbatch"],
           "srun": [v for w, v in rows if w == "srun"],
           "exe": [v for w, v in rows if w == "exe"]}
    if chain_dir:
        c = os.path.join(chain_dir, "chain")
        res["chain_status"] = open(os.path.join(c, "STATUS")).read().strip()
        res["chain_events"] = open(os.path.join(c, "events.log")).read().splitlines()
    print(f"{name:26s} rc={r.returncode} sbatch={res['sbatch']} srun={res['srun']} exe={res['exe']}"
          + (f" chain={res.get('chain_status')}" if chain_dir else ""))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--old", required=True,
                    help="directory holding the four scripts as they were before the change")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=False)
    fb, st, log = setup(out)
    open(log, "w").close()
    env = base_env(fb, out)
    new = os.path.join(out, "scripts_new")
    old = os.path.join(out, "scripts_old")
    os.makedirs(new)
    os.makedirs(old)
    for n in NAMES:
        shutil.copy2(os.path.join(REPO, "scripts", n), os.path.join(new, n))
        shutil.copy2(os.path.join(os.path.abspath(a.old), n), os.path.join(old, n))
        os.chmod(os.path.join(old, n), 0o755)     # files written by `git show >` are not executable
    deck_rst = os.path.join(out, "deck_rst.athinput")
    deck = os.path.join(out, "deck_plain.athinput")
    S = {}

    def cases(tag, sd):
        S[tag + "A_gpu_run_batch"] = run_case(
            tag + "A_gpu_run_batch", ["bash", os.path.join(sd, "gpu_run.sh"), os.path.join(out, tag + "A"), deck],
            dict(env, BATCH="1"), st, log, out)
        S[tag + "D_chain_handover"] = run_case(
            tag + "D_chain_handover",
            ["bash", os.path.join(sd, "submit_chain.sh"), os.path.join(out, tag + "D"), deck_rst],
            dict(env, ATHENA_WALL="00:01:00", MAX_SEGMENTS="3"), st, log, out,
            chain_dir=os.path.join(out, tag + "D"))

    cases("new_", new)
    S["new_B_gpu_run_srun"] = run_case(
        "new_B_gpu_run_srun", ["bash", os.path.join(new, "gpu_run.sh"), os.path.join(out, "new_B"), deck],
        env, st, log, out)
    lst = os.path.join(out, "new_C.list")
    with open(lst, "w") as f:
        f.write(f"{out}/new_C/r1 {deck}\n{out}/new_C/r2 {deck}\n")
    S["new_C_gpu_batch"] = run_case(
        "new_C_gpu_batch", ["bash", os.path.join(new, "gpu_batch.sh"), lst], env, st, log, out)
    lst2 = os.path.join(out, "new_E.list")
    with open(lst2, "w") as f:
        f.write(f"{out}/new_E/r1 {deck}\n")
    S["new_E_batch_in_job"] = run_case(
        "new_E_batch_in_job", ["bash", os.path.join(new, "gpu_batch.sh"), lst2],
        dict(env, SLURM_JOB_ID="777001", NRPIC_SCRIPTS=new), st, log, out)
    os.makedirs(os.path.join(out, "new_E2"))
    S["new_E_athena_job"] = run_case(
        "new_E_athena_job", ["bash", os.path.join(new, "_athena_job.sh"), os.path.join(out, "new_E2"),
                             os.path.join(out, "new_E2", "a.log"), os.path.join(out, "athena"), "-i", deck,
                             "-d", os.path.join(out, "new_E2")], env, st, log, out)
    cases("old_", old)

    unset = lambda v: len(v) > 0 and set(v) == {"unset"}
    seen = lambda v: len(v) > 0 and set(v) == {TOKEN}
    ch = {}
    ch["A: sbatch and the job's executable without the marker"] = (
        unset(S["new_A_gpu_run_batch"]["sbatch"]) and unset(S["new_A_gpu_run_batch"]["exe"]))
    ch["B: srun and the executable without the marker"] = (
        unset(S["new_B_gpu_run_srun"]["srun"]) and unset(S["new_B_gpu_run_srun"]["exe"]))
    ch["C: sbatch, both srun steps and both runs without the marker"] = (
        unset(S["new_C_gpu_batch"]["sbatch"]) and len(S["new_C_gpu_batch"]["srun"]) == 2
        and unset(S["new_C_gpu_batch"]["srun"]) and len(S["new_C_gpu_batch"]["exe"]) == 2
        and unset(S["new_C_gpu_batch"]["exe"]))
    d = S["new_D_chain_handover"]
    ch["D: chain DONE after the hand-over, two sbatch calls, two segments"] = (
        d["chain_status"] == "DONE" and len(d["sbatch"]) == 2 and len(d["exe"]) == 2
        and sum("submitted job" in x for x in d["chain_events"]) == 2)
    ch["D: neither sbatch call (start, hand-over in the job) nor any segment sees the marker"] = (
        unset(d["sbatch"]) and unset(d["exe"]))
    ch["E: in-job gpu_batch.sh and _athena_job.sh given the marker: the executable does not see it"] = (
        unset(S["new_E_batch_in_job"]["exe"]) and unset(S["new_E_athena_job"]["exe"])
        and not S["new_E_batch_in_job"]["sbatch"])
    ch["F: control, old scripts: sbatch and the executable see the marker (the test can fail)"] = (
        seen(S["old_A_gpu_run_batch"]["sbatch"]) and seen(S["old_A_gpu_run_batch"]["exe"])
        and seen(S["old_D_chain_handover"]["sbatch"]) and seen(S["old_D_chain_handover"]["exe"]))
    ch["F: control chain also reaches DONE (same mechanics)"] = (
        S["old_D_chain_handover"]["chain_status"] == "DONE")
    ch["every fake job ended"] = all(v["jobs_ended"] for v in S.values())
    S["checks"] = ch
    S["verdict"] = "PASS" if all(ch.values()) else "FAIL"
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(S, f, indent=1)
        f.write("\n")
    for k, v in ch.items():
        print("%-92s %s" % (k, "held" if v else "FAILED"))

    sys.path.insert(0, os.path.join(REPO, "python"))
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    rows = [k for k in S if k not in ("checks", "verdict")]
    cols = ("sbatch", "srun", "exe")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    fig.subplots_adjust(left=0.30, right=0.97, bottom=0.12, top=0.90)
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            v = S[r][c]
            if not v:
                ax.text(j, i, "-", ha="center", va="center", fontsize=9, color="0.5")
                continue
            ns = sum(x != "unset" for x in v)
            col = fs.SERIES[1] if ns else fs.SERIES[0]
            ax.plot(j, i, "s", ms=17, color=col, alpha=0.85)
            ax.text(j, i, f"{ns}/{len(v)}", ha="center", va="center", fontsize=8, color="white")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(["sbatch call", "srun call", "executable"])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.set_xlim(-0.6, len(cols) - 0.4)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_title("calls that saw NRPIC_QUEUE_DISPATCH / all calls (blue: none, orange: some)", fontsize=9)
    fs.save(fig, os.path.join(out, "fig_queue_marker"))
    plt.close(fig)
    print("TEST", S["verdict"])
    return 0 if S["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
