"""Sequencer of B-emd-gw's queued runs (decision 0025 item 5): keeps at most two card jobs of
the owner eligible to run, submits the next queued run when a slot is free and its inputs are
ready, starts queued processor runs when their inputs are ready, and closes finished runs with
`nrpic-run finish`. Standard library only; run with python3 -I.

    setsid nohup /usr/bin/python3 -I tracks/B-emd-gw/cards/sequencer.py \
        > /data/haiyangw/nrpic/scratch/B-emd-gw/sequencer/sequencer.log 2>&1 < /dev/null &

Queue: tracks/B-emd-gw/cards/queue.json (re-read at every pass, so a session may edit and
commit it while the sequencer runs). State (what was submitted, run ids, what was finished):
scratch/B-emd-gw/sequencer/state.json. Stop: `touch scratch/B-emd-gw/sequencer/STOP` (the
sequencer exits at its next pass) or `kill <pid>` with the pid in scratch/B-emd-gw/sequencer/pid.

Queue entries (in order; an entry is considered only when every earlier card entry has been
submitted, so the order of the card runs is the order of the file):
  {"name": ..., "kind": "card" | "local",
   "needs": [condition, ...],          # all must hold
   "argv": [...]}                      # nrpic-run submit command, run in the worktree root
Conditions:
  {"result_ok": RUN}                   # RUN has .nrpic/result.json with exit_code 0
  {"result_any": RUN}                  # RUN has .nrpic/result.json (ended, any exit)
  {"json_below": [RUN, RELPATH, KEY, LIMIT]}   # finite value of KEY in RUN/RELPATH below LIMIT
RUN is a run id or "@name" (the run id the sequencer recorded for queue entry `name`); the
same "@name" placeholder is replaced inside argv strings. "finish": run ids (or @names) that the
sequencer closes with `nrpic-run finish` once they have ended (finish refuses while a run is
active, so trying is harmless). The pause flag is logged but does not stop card or processor
submissions: they cost card or processor time, not the account's usage window (decision 0025
item 4); the sequencer itself starts no agent.
"""
import json
import math
import os
import re
import subprocess
import sys
import time

WT = "/data/haiyangw/nrpic/wt/B-emd-gw"
QUEUE = os.path.join(WT, "tracks", "B-emd-gw", "cards", "queue.json")
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
STATE_DIR = os.path.join(SCR, "sequencer")
STATE = os.path.join(STATE_DIR, "state.json")
NRPIC_RUN = os.path.join(WT, "harness", "bin", "nrpic-run")
PAUSE = "/data/haiyangw/nrpic/locks/PAUSE"
MAX_ELIGIBLE = 2
PERIOD = 300


def log(*a):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, STATE)


def resolve(x, st):
    def sub(m):
        return st["runs"].get(m.group(1), m.group(0))
    return re.sub(r"@([A-Za-z0-9_.-]+)", sub, x)


def result(run):
    return load(os.path.join(SCR, run, ".nrpic", "result.json"), None)


def cond_ok(c, st):
    if "result_ok" in c:
        r = result(resolve(c["result_ok"], st))
        return bool(r) and r.get("exit_code") == 0
    if "result_any" in c:
        return result(resolve(c["result_any"], st)) is not None
    if "json_below" in c:
        run, rel, key, lim = c["json_below"]
        d = load(os.path.join(SCR, resolve(run, st), resolve(rel, st)), None)
        if not isinstance(d, dict) or not isinstance(d.get(key), (int, float)):
            return False
        v = float(d[key])
        return math.isfinite(v) and v < float(lim)
    return False


def note_wait(st, name, why):
    """Log why an entry waits, once per change of the reason (a silent wait stalled the
    queue from 2026-11-21 to 2026-11-22: pop_s028_gr's condition never held)."""
    w = st.setdefault("waiting", {})
    if w.get(name) != why:
        w[name] = why
        log("waiting:", name, "|", why)


def owner_card_jobs():
    r = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "haiyangw"), "-o", "%j %T"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    n = 0
    for line in r.stdout.splitlines():
        w = line.split()
        if len(w) == 2 and w[0].startswith("B-") and w[1] in ("PENDING", "RUNNING", "CONFIGURING"):
            n += 1
    return n


def run_cmd(argv):
    r = subprocess.run(argv, cwd=WT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def one_pass(st):
    q = load(QUEUE, {"entries": [], "finish": []})
    if os.path.exists(PAUSE):
        log("pause flag present (cards and processors are not limited by it; continuing)")
    # close runs that have ended
    for run in list(q.get("finish", [])) + list(st["runs"].values()):
        run = resolve(run, st)
        if run.startswith("@") or run in st["finished"]:
            continue
        rc, out = run_cmd([NRPIC_RUN, "finish", run])
        if rc == 0:
            st["finished"].append(run)
            log("finished", run, "|", out.strip().splitlines()[-1] if out.strip() else "")
    # submit what is ready
    blocked_card = False
    for e in q.get("entries", []):
        name = e["name"]
        if name in st["runs"]:
            continue
        if e["kind"] == "card" and blocked_card:
            continue
        failing = [c for c in e.get("needs", []) if not cond_ok(c, st)]
        if failing:
            note_wait(st, name, "condition not met: " + json.dumps(failing[0]))
            if e["kind"] == "card":
                blocked_card = True          # keep the order of the card runs
            continue
        if e["kind"] == "card":
            n = owner_card_jobs()
            if n is None or n >= MAX_ELIGIBLE:
                note_wait(st, name, f"card slots of the owner taken ({n} of {MAX_ELIGIBLE})")
                blocked_card = True
                continue
        argv = [resolve(a, st) for a in e["argv"]]
        rc, out = run_cmd(argv)
        m = re.search(r"registered (B-\d{8}-\d{6}-[0-9a-f]{7})", out)
        if m and ("submitted" in out or "running in the background" in out):
            st["runs"][name] = m.group(1)
            log("submitted", name, "as", m.group(1))
        else:
            st["errors"].append({"name": name, "time": time.time(), "rc": rc, "out": out[-2000:]})
            st["errors"] = st["errors"][-20:]
            log("submission of", name, "refused or failed (rc", rc, "); retry at the next pass:",
                out.strip().splitlines()[-1] if out.strip() else "")
            if m:                             # registered but the launch failed: do not resubmit blindly
                st["runs"][name] = m.group(1)
            if e["kind"] == "card":
                blocked_card = True
    save_state(st)
    left = [e["name"] for e in q.get("entries", []) if e["name"] not in st["runs"]]
    return left


def main():
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, "pid"), "w") as f:
        f.write(str(os.getpid()) + "\n")
    st = load(STATE, {"runs": {}, "finished": [], "errors": []})
    log("sequencer started, pid", os.getpid())
    while True:
        if os.path.exists(os.path.join(STATE_DIR, "STOP")):
            log("STOP file found; exiting")
            return 0
        try:
            left = one_pass(st)
        except Exception as exc:                  # keep running; the next pass retries
            log("pass failed:", repr(exc))
            left = ["?"]
        q = load(QUEUE, {"entries": [], "finish": []})
        pending_finish = [r for r in list(q.get("finish", [])) + list(st["runs"].values())
                          if resolve(r, st) not in st["finished"]]
        if not left and not pending_finish:
            log("queue empty and every run closed; exiting")
            return 0
        time.sleep(PERIOD)


if __name__ == "__main__":
    sys.exit(main())
