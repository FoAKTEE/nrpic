#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-queue (decision 0033) in a scratch repository with the fake Slurm of
rc_fixture.py: no card, no real Slurm job; nothing of the live checkout is touched.

    python3 -I harness/tests/test_nrpic_queue.py

Fake card jobs (hold.sh, outside the worktrees) run until the test releases them, so the test decides when
a job ends (`sbatch --hold` makes one the fake squeue lists as PENDING); a thread samples the fake Slurm
state every 50 ms for the largest number of live jobs. The dispatcher looks every 0.5 s.
Covers: identity from the path (a command that changes the queue acts on the worktree the caller stands in;
-C only for the orchestrator standing in the main checkout); priorities 0 and 1 only from the orchestrator;
aging (one class per 8 h waited, never past 1; list and status show the effective priority); refusals of
add (duplicate label, unknown --after, both forms, a local launcher, arguments the dry run refuses); remove
by owner and orchestrator only; seven entries of three owners never give more than five jobs, in the order
status predicts; --after; nrpic-run's cap refusal (waiting, nothing registered) and the line its one-route
refusal prints; a chain stays submitted across its hand-over; waits, not failures, for a worktree mid-merge
or not clean; a failing command is failed with its stderr, the loop goes on; regressions of the review of
2026-11-24: a command that submitted a job and then failed or timed out keeps its job, so retry and
mark-done wait (3, 3b, 3c); a child left behind cannot hold the dispatcher, a setsid grandchild neither (4);
after a SIGKILL a restart ends the old command's process group before the first look (5); check-dispatch is
valid in the wrapper and not in the job it submits (6); a rise of two jobs named like a running job is an
ALERT (2); an error between claim and the end of a dispatch fails the entry; status says HUNG for a stopped
dispatcher; STOP; restart from the files; the cap keeper cancels an excess that lasted, newest pending first,
never a running job or a chain's next segment, and puts an entry back to waiting; `squeue -r` counts array
tasks; the pause flag does not stop submissions (decision 0026 item 2). The keeper never cancels a job of the
user's own (not of an entry, no run-id name, working directory outside the repository): cases (a) to (f).
"""
import calendar
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402

HOLD = r'''#!/bin/bash
# fake card job of the queue self-tests: runs until the test writes @REL@/<name> (at most ten minutes)
for ((i = 0; i < 3000; i++)); do [[ -e "@REL@/$1" ]] && exit 0; sleep 0.2; done
'''
CDJOB = r'''#!/bin/bash
# a job submitted by a --cmd wrapper itself: is the dispatcher's marker valid in here? (it must not be)
sleep 2
env | grep '^NRPIC_QUEUE_DISPATCH=' > "@REL@/cd-job"
harness/bin/nrpic-queue check-dispatch >> "@REL@/cd-job" 2>&1; echo "rc=$?" >> "@REL@/cd-job"
for ((i = 0; i < 3000; i++)); do [[ -e "@REL@/$1" ]] && exit 0; sleep 0.2; done
'''
POLL = "0.5"
FAST = ["--cmd-timeout", "4", "--keeper", "1", "--keeper-confirm", "2"]


def wait_until(pred, timeout=60, step=0.2):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if pred():
                return True
        except (OSError, ValueError, KeyError, TypeError):
            pass
        time.sleep(step)
    return False


class T:
    def __init__(self):
        self.fx = F.make_repo("test-queue", owners=("A-emd-pbh", "B-emd-gw", "C-sidm"))
        self.repo = self.fx["repo"]
        self.A, self.B, self.C = (self.fx["wt"][o] for o in ("A-emd-pbh", "B-emd-gw", "C-sidm"))
        self.rel = os.path.join(self.fx["root"], "release")
        os.makedirs(self.rel)
        self.hold = os.path.join(self.fx["root"], "hold.sh")
        F.write_exe(self.hold, HOLD.replace("@REL@", self.rel))
        self.qdir = os.path.join(self.repo, "locks", "queue")
        self.alert = os.path.join(self.qdir, "ALERT")
        self.ids, self.names = {}, set()
        self.disp = None
        self.max_live, self.samples, self.mon_stop, self.mon_pause = 0, 0, False, False
        self.mon = threading.Thread(target=self.monitor, daemon=True)

    # -- the command, in the copy of the worktree the call is made from (the main checkout's otherwise)
    def q(self, cwd, args, timeout=300):
        wt = cwd if os.path.isdir(os.path.join(cwd, "harness", "bin")) else self.repo
        return F.sh([os.path.join(wt, "harness", "bin", "nrpic-queue")] + args, cwd=cwd, check=False, timeout=timeout)

    def add(self, cwd, label, extra):
        r = self.q(cwd, ["add", "--label", label] + extra)
        eid = r.stdout.split()[0] if r.returncode == 0 and r.stdout.split() else None
        if eid:
            self.ids[label] = eid
        return r, eid

    def add_orch(self, wt, label, extra):
        """The orchestrator, standing in the main checkout, queues a run for the owner of wt."""
        r = self.q(self.repo, ["-C", wt, "add", "--label", label] + extra)
        eid = r.stdout.split()[0] if r.returncode == 0 and r.stdout.split() else None
        if eid:
            self.ids[label] = eid
        return r, eid

    def hold_cmd(self, name, hold=False):
        self.names.add(name)
        return ["--cmd", f"sbatch {'--hold ' if hold else ''}-J {name} {self.hold} {name}"]

    def foreign(self, name, key=None, hold=False, cwd=None):
        """A job submitted by another way than the queue (the test plays it). cwd: its working directory; by
        default one outside the fixture's repository, so that a job without a run-id name is the user's own."""
        key = key or name
        self.names.add(key)
        cwd = cwd or os.path.join(self.fx["root"], "elsewhere")
        os.makedirs(cwd, exist_ok=True)
        env = F.H.build_env(F.H.Worktree(self.A))
        r = F.sh(["sbatch"] + (["--hold"] if hold else []) + ["-J", name, self.hold, key], env=env, cwd=cwd)
        return r.stdout.split()[-1]

    def release(self, *names):
        for n in names:
            open(os.path.join(self.rel, n), "w").close()

    def live(self):
        """(id, name) of the live fake jobs, as the fake squeue sees them."""
        st, out = self.fx["state"], []
        for j in os.listdir(st):
            d = os.path.join(st, j)
            if not j.isdigit() or os.path.exists(os.path.join(d, "end")):
                continue
            try:
                os.kill(int(open(os.path.join(d, "pid")).read()), 0)
            except (OSError, ValueError):
                continue
            try:
                name = open(os.path.join(d, "name")).read()
            except OSError:
                name = ""
            out.append((j, name))
        return out

    def settle(self, *keep):
        """Release every job of the test but those named in keep; wait until only they are left."""
        self.release(*(self.names - set(keep)))
        return wait_until(lambda: {n for _, n in self.live()} <= set(keep), 60)

    def monitor(self):
        while not self.mon_stop:
            try:
                n = len(self.live())
            except OSError:
                n = 0
            if not self.mon_pause:
                self.max_live = max(self.max_live, n)
                self.samples += 1
            time.sleep(0.05)

    def e(self, label):
        return json.load(open(os.path.join(self.qdir, "entries", self.ids[label] + ".json")))

    def state(self, label):
        try:
            return self.e(label)["state"]
        except (OSError, ValueError, KeyError):
            return None

    def log(self):
        p = os.path.join(self.qdir, "queue.log")
        return open(p).read() if os.path.isfile(p) else ""

    def head(self, wt):
        return F.sh(["git", "-C", wt, "rev-parse", "HEAD"]).stdout.strip()

    def start(self, *extra):
        out = open(os.path.join(self.fx["root"], "dispatcher.out"), "a")
        self.disp = subprocess.Popen([os.path.join(self.repo, "harness", "bin", "nrpic-queue"), "-C", self.repo, "run",
                                      "--poll", POLL] + list(extra), cwd=self.repo, env=F.H.boot_env(),
                                     stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        return wait_until(lambda: "dispatcher start: pid %d" % self.disp.pid in self.log(), 30)

    def cleanup(self):
        if self.disp is not None and self.disp.poll() is None:
            try:
                os.kill(self.disp.pid, signal.SIGCONT)
            except OSError:
                pass
            open(os.path.join(self.qdir, "STOP"), "w").close()
            try:
                self.disp.wait(60)
            except subprocess.TimeoutExpired:
                self.disp.terminate()
                self.disp.wait(30)
        self.release(*self.names)
        wait_until(lambda: not self.live(), 60)
        self.mon_stop = True


def refusals(t, c):
    A, B, repo = t.A, t.B, t.repo
    elsewhere = os.path.join(repo, "scratch", "tmp-queue-test")
    os.makedirs(elsewhere, exist_ok=True)
    r = t.q(elsewhere, ["add", "--label", "zc", "--cmd", "true"])
    c.ok(r.returncode == 1 and "standing in your worktree" in r.stderr and not os.path.isdir(t.qdir),
         "add from a data root of the main checkout (scratch/) is refused, nothing written", r.stdout + r.stderr)
    r = t.q(elsewhere, ["-C", A, "add", "--label", "zc", "--cmd", "true"])
    c.ok(r.returncode == 1 and "standing in your worktree" in r.stderr and not os.path.isdir(t.qdir),
         "identity from the path: -C from outside a worktree is refused too", r.stdout + r.stderr)
    r = t.q(A, ["-C", B, "add", "--label", "zc", "--cmd", "true"])
    c.ok(r.returncode == 1 and "you stand in" in r.stderr, "identity from the path: A standing in its worktree "
         "cannot act on B's with -C", r.stderr)
    r, zc = t.add_orch(A, "zc", ["--cmd", "true"])
    c.ok(zc and t.e("zc")["owner"] == "A-emd-pbh" and t.e("zc")["worktree"] == os.path.realpath(A)
         and t.e("zc")["added_by"] == "orch" and t.e("zc")["state"] == "waiting",
         "the orchestrator, standing in the main checkout, queues an entry for A with -C (owner A, added by orch)",
         r.stdout + r.stderr)
    r = t.q(B, ["remove", zc or "q9999"])
    c.ok(r.returncode == 1 and "belongs to A-emd-pbh" in r.stderr, "another owner's remove is refused", r.stderr)
    r = t.q(B, ["-C", A, "remove", zc or "q9999"])
    c.ok(r.returncode == 1 and "you stand in" in r.stderr, "... also with -C naming the owner's worktree", r.stderr)
    r = t.q(A, ["remove", zc or "q9999"])
    c.ok(r.returncode == 0 and t.state("zc") == "removed", "the owner removes its own waiting entry", r.stdout + r.stderr)
    for cmd in (["stop"], ["clear-alert"], ["run", "--poll", POLL]):
        r = t.q(A, cmd)
        c.ok(r.returncode == 1 and "orchestrator" in r.stderr, f"`{cmd[0]}` from an owner's worktree is refused", r.stderr)
    r = t.q(A, ["-C", repo, "stop"])
    c.ok(r.returncode == 1 and "orchestrator" in r.stderr, "`stop` with -C <main checkout> from an owner's worktree is "
         "refused (the caller must stand in the main checkout)", r.stderr)
    r = t.q(A, ["add", "--label", "p0x", "--priority", "0", "--cmd", "true"])
    c.ok(r.returncode == 1 and "only by the orchestrator" in r.stderr, "an owner's --priority 0 is refused", r.stderr)
    r = t.q(A, ["add", "--label", "p1x", "--priority", "1", "--cmd", "true"])
    c.ok(r.returncode == 1 and "only by the orchestrator" in r.stderr, "an owner's --priority 1 is refused", r.stderr)
    r, p0 = t.add_orch(A, "p0x", ["--priority", "0", "--cmd", "true"])
    c.ok(p0 and t.e("p0x")["priority"] == 0, "the orchestrator gives priority 0", r.stdout + r.stderr)
    t.q(repo, ["remove", p0 or "q9999"])
    # aging: one class per 8 hours waited, never past 1
    r1, ag1 = t.add(B, "ag1", ["--cmd", "true"])
    r2, ag2 = t.add(A, "ag2", ["--priority", "4", "--cmd", "true"])
    r3, ag3 = t.add(t.C, "ag3", ["--cmd", "true"])
    for lab, hours in (("ag1", 17), ("ag3", 100)):
        p = os.path.join(t.qdir, "entries", t.ids[lab] + ".json")
        e = json.load(open(p))
        e["added"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - hours * 3600))
        json.dump(e, open(p, "w"))
    lst = t.q(repo, ["list"]).stdout
    st = t.q(repo, ["status"]).stdout
    inv = {v: k for k, v in t.ids.items()}
    got = [inv.get(g) for g in re.findall(r"^\s+\d+\. (q\d+) ", st, re.M)]
    c.ok(re.search(rf"^{ag1} .*waiting\s+3\(5\) ", lst, re.M) and re.search(rf"^{ag3} .*waiting\s+1\(5\) ", lst, re.M)
         and re.search(rf"^{ag2} .*waiting\s+4 ", lst, re.M) and got == ["ag3", "ag1", "ag2"],
         "aging: 17 h of waiting make priority 5 a 3, 100 h make it 1 (never past 1); list shows 3(5) and 1(5), "
         "status orders by the effective priority", lst + st)
    for x in (ag1, ag2, ag3):
        t.q(repo, ["remove", x or "q9999"])
    r1, dup = t.add(A, "dup", ["--cmd", "true"])
    r2 = t.q(A, ["add", "--label", "dup", "--cmd", "true"])
    c.ok(dup and r2.returncode == 1 and "already has an entry labelled 'dup'" in r2.stderr,
         "a second entry with a label that is not done is refused", r1.stderr + r2.stderr)
    r = t.q(repo, ["remove", dup or "q9999"])
    c.ok(r.returncode == 0 and t.state("dup") == "removed", "the orchestrator removes another owner's entry",
         r.stdout + r.stderr)
    r = t.q(A, ["add", "--label", "x", "--after", "nosuch", "--cmd", "true"])
    c.ok(r.returncode == 1 and "no entry of A-emd-pbh with that label" in r.stderr, "--after an unknown label is refused",
         r.stderr)
    r = t.q(A, ["add", "--label", "x", "--cmd", "true", "--", "--kind", "scouting"])
    c.ok(r.returncode == 1 and "one of the two" in r.stderr, "--cmd and an argument list at once are refused", r.stderr)
    r = t.q(A, ["add", "--label", "x", "--", "--kind", "scouting", "--gate", "G1", "--purpose", "p", "--", "true"])
    c.ok(r.returncode == 1 and "the queue is for card runs" in r.stderr, "a local run is refused (card runs only)",
         r.stderr)
    r = t.q(A, ["add", "--label", "x", "--", "submit", "--kind", "scouting", "--gate", "G1", "--purpose", "p",
                "--launcher", "batch", "--list", "tracks/A-emd-pbh/q/nope.txt"])
    c.ok(r.returncode == 1 and "--dry-run` refused" in r.stderr and "nope.txt" in r.stderr and "x" not in t.ids,
         "arguments that nrpic-run's dry run refuses (a missing list) are not queued", r.stderr)
    r, ns = t.add(A, "ns", ["--no-check", "--", "harness/bin/nrpic-run", "submit", "--kind", "scouting", "--gate", "G1",
                            "--purpose", "p", "--launcher", "batch", "--list", "x.txt"])
    c.ok(ns and t.e("ns")["argv"][:2] == ["--kind", "scouting"] and not t.e("ns")["checked"],
         "a leading `harness/bin/nrpic-run submit` is dropped; --no-check queues unchecked", r.stdout + r.stderr)
    t.q(A, ["remove", ns or "q9999"])


def order_and_cap(t, c):
    plan = [("a1", t.A, 5), ("a2", t.A, 5), ("a3", t.A, 5), ("b1", t.B, 5), ("b2", t.B, 2), ("c1", t.C, 0),
            ("c2", t.C, 5)]
    for lab, wt, p in plan:
        add = t.add_orch if p < 2 else t.add
        r, eid = add(wt, lab, ["--priority", str(p)] + t.hold_cmd(lab))
        if not c.ok(eid, f"add {lab} (priority {p}{', by the orchestrator' if p < 2 else ''})", r.stdout + r.stderr):
            return False
    want = ["c1", "b2", "a1", "c2", "b1", "a2", "a3"]
    inv = {v: k for k, v in t.ids.items()}
    st = t.q(t.repo, ["status"]).stdout
    got = [inv.get(g) for g in re.findall(r"^\s+\d+\. (q\d+) ", st, re.M)]
    c.ok(got == want and "NOT running" in st, "status predicts the order: priority 0, priority 2, then round robin over "
         "the owners at priority 5 (A never served, C, B, then A's rest); dispatcher not running yet", st)
    t.mon.start()
    c.ok(t.start(), "dispatcher started (run --poll 0.5, standing in the main checkout)")
    ok5 = wait_until(lambda: sum(t.state(l) == "submitted" for l in want) == 5, 60)
    time.sleep(3)
    sub = [l for _, l in sorted((t.e(l)["dispatch_no"], l) for l in want if t.state(l) == "submitted")]
    c.ok(ok5 and sub == want[:5] and t.state("a2") == "waiting" and t.state("a3") == "waiting" and len(t.live()) == 5,
         f"seven entries of three owners: five submitted in order {sub}, two wait at the cap for six looks",
         t.log()[-1500:])
    st = t.q(t.repo, ["status"]).stdout
    c.ok("5 of 5 jobs" in st and "dispatcher: running" in st and "heartbeat" in st and f"{t.ids['c1']} C-sidm/c1" in st,
         "status: 5 of 5 jobs, dispatcher running with its heartbeat's age, each job named with its entry", st)
    t.release("c1")
    c.ok(wait_until(lambda: t.state("a2") == "submitted", 30) and wait_until(lambda: t.state("c1") == "done", 30)
         and t.state("a3") == "waiting", "a job ends: the next entry (a2) is submitted, the ended one marked done; a3 waits")
    t.release("b2")
    c.ok(wait_until(lambda: t.state("a3") == "submitted", 30), "another job ends: a3 is submitted")
    order = [l for _, l in sorted((t.e(l)["dispatch_no"], l) for l in want)]
    c.ok(order == want, f"the dispatch order is {order} as predicted")
    c.ok(t.max_live <= 5, f"never more than five live jobs so far ({t.max_live})")
    return True


def after(t, c):
    r, a4 = t.add_orch(t.A, "a4", ["--after", "a3", "--priority", "0"] + t.hold_cmd("a4"))
    c.ok(a4 and t.e("a4")["after_id"] == t.ids["a3"], "--after a3 is recorded with a3's entry id", r.stdout + r.stderr)
    t.release("a1", "c2")
    wait_until(lambda: len(t.live()) == 3, 30)
    time.sleep(3)
    lst = t.q(t.A, ["list"]).stdout
    c.ok(t.state("a4") == "waiting" and len(t.live()) == 3 and re.search(rf"^{t.ids['a4']} .* waiting\* ", lst, re.M),
         "--after: a4 (priority 0) waits while a3's job is queued, though two places are free; list marks it *", lst)
    t.release("a3")
    ok = wait_until(lambda: t.state("a4") == "submitted", 30)
    a3, a4e = t.e("a3"), t.e("a4")
    c.ok(ok and a3["state"] == "done" and a4e["submitted"] >= a3["ended"],
         "--after: a4 is submitted once a3's job has left squeue (a3 marked done first)", json.dumps([a3, a4e])[:1500])


def refusal(t, c):
    A, B = t.A, t.B
    for wt, o in ((A, "A-emd-pbh"), (B, "B-emd-gw")):
        deck = f"tracks/{o}/q/b.athinput"
        F.commit_file(wt, deck, "<problem>\npgen_name = fake_batch\n")
        F.commit_file(wt, f"tracks/{o}/q/batch.txt", f"one {deck} time/nlim=5\n")
    t.foreign("foreign1")                                    # a job that came in by another way
    c.ok(wait_until(lambda: len(t.live()) == 4, 30), "four live jobs (three entries and one more)")
    t.names.add("foreign2")
    flag = os.path.join(t.fx["root"], "flag-r1")
    # the first attempt plays a job coming in between the dispatcher's count and nrpic-run's (unprinted)
    cmd = (f"test -e {flag} || {{ touch {flag}; sbatch -J foreign2 {t.hold} foreign2 > /dev/null; }}; "
           "exec harness/bin/nrpic-run submit --kind scouting --gate G1 --purpose 'queued, refused once by the cap' "
           "--launcher batch --list tracks/A-emd-pbh/q/batch.txt --wall 00:10:00")
    head0 = t.head(A)
    runs = os.path.join(A, "tracks", "A-emd-pbh", "runs")
    runs0 = sorted(os.listdir(runs))
    r, r1 = t.add_orch(A, "r1", ["--priority", "0", "--cmd", cmd])
    ok = wait_until(lambda: t.e("r1").get("refusals") == 1 and t.state("r1") == "waiting", 60)
    c.ok(ok and sorted(os.listdir(runs)) == runs0 and t.head(A) == head0 and f"refused {r1}" in t.log()
         and "queue cap: 5 jobs" in t.e("r1").get("last_refusal", ""),
         "refusal path: a job came in between the count and nrpic-run's own; nrpic-run refused (queue cap), the "
         "entry is waiting again and nothing was registered or committed", t.log()[-1500:])
    time.sleep(2)
    c.ok(t.e("r1").get("refusals") == 1 and t.state("r1") == "waiting" and len(t.live()) == 5,
         "at five jobs it is not tried again")
    t.release("foreign1")
    ok = wait_until(lambda: t.state("r1") in ("submitted", "done", "failed"), 120)
    e = t.e("r1")
    rid = e.get("run_id") or "none"
    log = F.sh(["git", "-C", A, "log", "-3", "--format=%s"]).stdout
    c.ok(ok and e["state"] in ("submitted", "done") and rid.startswith("A-") and e.get("job_ids")
         and e.get("job_name") == rid and os.path.isfile(os.path.join(runs, rid, "manifest.json"))
         and f"A(run): register {rid}" in log,
         "a job ends: the entry is submitted through nrpic-run (manifest committed; run id, job id kept, job name = "
         "run id)", json.dumps(e)[:2000] + log)
    sh = t.q(A, ["show", r1 or "q9999"]).stdout
    c.ok(f"nrpic-run finish {rid}" in sh, "show names the run and how to close it", sh[-800:])
    c.ok(wait_until(lambda: t.state("r1") == "done", 120), "its batch job ends: the entry is done")
    brun = os.path.join(B, "tracks", "B-emd-gw", "runs")
    bruns0, bhead0 = sorted(os.listdir(brun)), t.head(B)
    r = F.sh([os.path.join(B, "harness", "bin", "nrpic-run"), "submit", "--kind", "scouting", "--gate", "G1",
              "--purpose", "queued batch of B", "--launcher", "batch", "--list", "tracks/B-emd-gw/q/batch.txt",
              "--wall", "00:10:00"], cwd=B, check=False)
    m = re.search(r"^\s+(harness/bin/nrpic-queue add --label <label> -- .*)$", r.stderr, re.M)
    c.ok(r.returncode == 1 and "card runs are submitted only by the shared queue" in r.stderr and m
         and sorted(os.listdir(brun)) == bruns0 and t.head(B) == bhead0,
         "one route: a session's direct card submission is refused, nothing registered, and the message gives the "
         "`nrpic-queue add` line", r.stdout + r.stderr)
    r = F.sh(["bash", "-c", (m.group(1) if m else "false").replace("<label>", "p1")], cwd=B, check=False)
    p1 = r.stdout.split()[0] if r.returncode == 0 and r.stdout.split() else None
    if p1:
        t.ids["p1"] = p1
    c.ok(p1 and t.e("p1")["kind"] == "submit" and t.e("p1")["argv"][0] == "--kind" and t.e("p1")["checked"],
         "the line from the refusal, with a label, queues the run (checked by nrpic-run's dry run)", r.stdout + r.stderr)
    ok = wait_until(lambda: t.state("p1") == "done", 120)
    e = t.e("p1")
    prid = e.get("run_id") or "none"
    c.ok(ok and prid.startswith("B-") and os.path.isfile(os.path.join(brun, prid, "manifest.json")),
         "the queued argument list ran `nrpic-run submit` in B's worktree; done once its job left squeue",
         json.dumps(e)[:1500])


def chain(t, c):
    """A chain of two segments through the queue: the entry stays submitted across the hand-over (the next
    segment is submitted from inside the ending job, under the same job name) and is done only after the
    last segment's job has ended."""
    t.release("foreign2")
    c.ok(wait_until(lambda: len(t.live()) == 3, 30), "three live jobs before the chain (room for its hand-over)")
    deck = "tracks/A-emd-pbh/q/chain.athinput"
    F.commit_file(t.A, deck, "<problem>\npgen_name = fake_chain\n<output9>\nfile_type = rst\ndcycle = 5\n")
    r, ch = t.add(t.A, "ch1", ["--", "--kind", "scouting", "--gate", "G1", "--purpose", "queued chain of two segments",
                               "--launcher", "chain", "--gpu-hours", "2", "--", deck, "time/tlim=1"])
    if not c.ok(ch, "add a chain (nrpic-run submit --launcher chain)", r.stdout + r.stderr):
        return
    early = []

    def watch():
        e = t.e("ch1")
        rid = e.get("run_id")
        st = os.path.join(t.repo, "scratch", "A-emd-pbh", rid or "none", "chain", "STATUS")
        if e["state"] == "done" and not (os.path.isfile(st) and open(st).read().strip() == "DONE"):
            early.append(open(st).read().strip() if os.path.isfile(st) else "no STATUS")
        return e["state"] in ("done", "failed")
    ok = wait_until(watch, 240, 0.1)
    e = t.e("ch1")
    rid = e.get("run_id") or "none"
    ev = os.path.join(t.repo, "scratch", "A-emd-pbh", rid, "chain", "events.log")
    jids = re.findall(r"submitted job (\d+)", open(ev).read()) if os.path.isfile(ev) else []
    ends = [int(open(os.path.join(t.fx["state"], j, "end")).read()) for j in jids
            if os.path.isfile(os.path.join(t.fx["state"], j, "end"))]
    ended = calendar.timegm(time.strptime(e["ended"], "%Y-%m-%dT%H:%M:%SZ")) if e.get("ended") else 0
    c.ok(ok and e["state"] == "done" and not early and e.get("chain_status") == "DONE" and len(jids) == 2
         and len(ends) == 2 and F.H.parse_run_id(rid) and e.get("job_name") == rid and ended >= max(ends),
         f"a chain of two segments (jobs {jids}): the entry stays submitted across the hand-over and is done only "
         "after the last segment's job ended (chain_status DONE)", json.dumps(e)[:1500] + f" early={early}")


def busy(t, c):
    """Waits, not failures: a merge in progress in A's worktree holds A's entry back; nrpic-run finding B's
    worktree not clean (a session's unfinished file) puts B's entry back to waiting, tried again at a later
    look; another owner's entry goes meanwhile; `list` says why each waits, and since when; both go once their
    worktree is ready. A hand-edited entry file that lacks fields is skipped, not fatal."""
    wait_until(lambda: len(t.live()) == 3, 30)
    gd = F.sh(["git", "-C", t.A, "rev-parse", "--absolute-git-dir"]).stdout.strip()
    mh = os.path.join(gd, "MERGE_HEAD")
    open(mh, "w").write(t.head(t.A) + "\n")
    draft = os.path.join(t.B, "tracks", "B-emd-gw", "draft-in-progress.txt")
    open(draft, "w").write("a session's unfinished edit\n")
    brun = os.path.join(t.B, "tracks", "B-emd-gw", "runs")
    bruns0 = sorted(os.listdir(brun))
    junk = os.path.join(t.qdir, "entries", "q9000.json")
    json.dump({"id": "q9000", "owner": "A-emd-pbh", "state": "waiting"}, open(junk, "w"))
    tries = 0
    try:
        r, m1 = t.add_orch(t.A, "m1", ["--priority", "0"] + t.hold_cmd("m1"))
        r, d1 = t.add_orch(t.B, "d1", ["--priority", "0", "--no-check", "--", "--kind", "scouting", "--gate", "G1",
                                       "--purpose", "queued while the worktree is dirty", "--launcher", "batch",
                                       "--list", "tracks/B-emd-gw/q/batch.txt", "--wall", "00:10:00"])
        r, m2 = t.add(t.C, "m2", ["--priority", "5"] + t.hold_cmd("m2"))
        ok = wait_until(lambda: t.state("m2") == "submitted" and t.state("d1") == "waiting"
                        and (t.e("d1").get("wait") or {}).get("tries", 0) >= 1, 30, 0.05)
        lst = t.q(t.repo, ["list"]).stdout       # right after a refusal: d1 is not tried again for five looks
        sh = t.q(t.B, ["show", d1 or "q9999"]).stdout
        time.sleep(2)
        c.ok(ok and t.state("m1") == "waiting" and t.state("d1") in ("waiting", "submitting")
             and sorted(os.listdir(brun)) == bruns0
             and re.search(rf"^{m1} .* waits: worktree in the middle of a merge since 20", lst, re.M)
             and re.search(rf"^{d1} .* waits: worktree not clean since 20\S+ \(\d+ tries\)", lst, re.M)
             and "draft-in-progress.txt" in sh and "skipped" in t.log() and "q9000.json" in t.log(),
             "waits, not failures: A mid-merge holds its entry back; B not clean puts its entry back to waiting "
             "(nothing registered); C's entry goes; list says why and since when, show names the unclean file; a "
             "malformed entry file is skipped and reported", lst + sh[-800:] + t.log()[-1200:])
        tries = t.e("d1")["wait"]["tries"]
    finally:
        os.remove(mh)
        os.remove(draft)
        os.remove(junk)
    t.release("m2")
    ok = wait_until(lambda: t.state("m1") == "submitted", 30)
    c.ok(ok and "wait" not in t.e("m1"), "the merge is over: A's entry is submitted, its wait cleared")
    ok = wait_until(lambda: t.state("d1") == "done", 60)
    e = t.e("d1")
    c.ok(ok and (e.get("run_id") or "").startswith("B-") and "wait" not in e and "error" not in e
         and e.get("attempts", 0) <= tries + 2,
         f"B's worktree clean again: the entry is tried at a later look and submitted, never marked failed "
         f"({e.get('attempts')} attempts)", json.dumps(e)[:1500])
    t.release("m1")


def failing(t, c):
    wait_until(lambda: len(t.live()) == 3, 30)
    r, f1 = t.add_orch(t.C, "f1", ["--priority", "1", "--cmd",
                                   'echo boom-from-f1 >&2; echo "marker=$NRPIC_QUEUE_DISPATCH" >&2; exit 3'])
    r, h1 = t.add(t.C, "h1", t.hold_cmd("h1"))
    ok = wait_until(lambda: t.state("f1") == "failed" and t.state("h1") == "submitted", 30)
    e = t.e("f1")
    c.ok(ok and "boom-from-f1" in e.get("error", "") and "exit status 3" in e["error"] and e.get("exit_code") == 3
         and f"FAILED {f1}" in t.log(), "a failing command is marked failed with its stderr; the loop goes on (h1 "
         "submitted)", json.dumps(e)[:1200])
    c.ok(re.search(rf"marker={f1}:[0-9a-f]{{24}}", e.get("error", "")) and "dispatch_token" not in e,
         "the dispatcher marks the command it runs (NRPIC_QUEUE_DISPATCH=<id>:<token>, seen by a --cmd line); the "
         "token is dropped afterwards", e.get("error", ""))
    lst = t.q(t.repo, ["list"]).stdout
    c.ok(re.search(rf"^{f1} .* failed: boom-from-f1$", lst, re.M), "list shows the first line of a failed entry's stderr",
         lst)
    r = t.q(t.B, ["retry", f1 or "q9999"])
    c.ok(r.returncode == 1 and "belongs to C-sidm" in r.stderr, "another owner's retry is refused", r.stderr)
    r = t.q(t.repo, ["retry", f1 or "q9999"])
    ok = wait_until(lambda: t.e("f1").get("attempts") == 2 and t.state("f1") == "failed", 30)
    c.ok(r.returncode == 0 and ok, "retry (orchestrator): the failed entry runs again (and fails again, attempt 2)",
         r.stdout + r.stderr)
    # review 3b/3c: a command that submitted its job and then failed keeps the job: retry and mark-done wait
    r, bf = t.add(t.A, "bf1", ["--cmd", f"sbatch -J bf1 {t.hold} bf1; exit 4"])
    t.names.add("bf1")
    ok = wait_until(lambda: t.state("bf1") == "failed", 30)
    e = t.e("bf1")
    live_bf = [j for j, n in t.live() if n == "bf1"]
    c.ok(ok and live_bf and e.get("job_ids") == live_bf and e.get("job_name") == "bf1" and "it submitted job(s)" in
         e.get("error", ""), f"a command that submitted job {live_bf} and then failed: failed, its job recorded",
         json.dumps(e)[:1200])
    r = t.q(t.A, ["retry", bf or "q9999"])
    r2 = t.q(t.A, ["mark-done", bf or "q9999"])
    time.sleep(1.5)
    c.ok(r.returncode == 1 and "still in squeue" in r.stderr and r2.returncode == 1 and "still in squeue" in r2.stderr
         and t.state("bf1") == "failed" and len([1 for _, n in t.live() if n == "bf1"]) == 1,
         "review 3b, 3c: while its job is queued, retry (which would submit it again) and mark-done are refused",
         r.stderr + r2.stderr)
    t.release("bf1")
    wait_until(lambda: not any(n == "bf1" for _, n in t.live()), 30)
    r = t.q(t.A, ["mark-done", bf or "q9999"])
    c.ok(r.returncode == 0 and t.state("bf1") == "done", "once its job has ended, mark-done closes it", r.stderr)


def stop_and_restart(t, c):
    r = t.q(t.repo, ["stop", "--wait", "30"])
    try:
        t.disp.wait(30)
    except subprocess.TimeoutExpired:
        pass
    c.ok(r.returncode == 0 and "has ended" in r.stdout and t.disp.poll() is not None
         and not os.path.exists(os.path.join(t.qdir, "dispatcher.pid")) and not os.path.exists(os.path.join(t.qdir, "STOP"))
         and "dispatcher exit (STOP file)" in t.log(), "STOP: the dispatcher ends, removes its pid file and the STOP file",
         r.stdout + r.stderr + t.log()[-600:])
    c.ok("NOT running" in t.q(t.repo, ["status"]).stdout, "status says the dispatcher is not running")
    t.release("b1")
    wait_until(lambda: not any(n == "b1" for _, n in t.live()), 30)
    r, n1 = t.add(t.B, "n1", t.hold_cmd("n1"))
    c.ok(n1 and "no dispatcher is running" in r.stdout, "add while no dispatcher runs says so", r.stdout + r.stderr)
    r, z1 = t.add(t.A, "z1", ["--cmd", "true"])
    p = os.path.join(t.qdir, "entries", (z1 or "q9999") + ".json")
    e = json.load(open(p))
    e.update(state="submitting", dispatch_started=F.H.utcnow())         # as if the dispatcher had died meanwhile
    json.dump(e, open(p, "w"))
    c.ok(t.state("b1") == "submitted", "while stopped, b1's job has ended but its entry still reads submitted")
    c.ok(t.start(*FAST), "dispatcher restarted (--cmd-timeout 4 --keeper 1 --keeper-confirm 2)")
    r = t.q(t.repo, ["run", "--poll", POLL], timeout=60)
    c.ok(r.returncode == 1 and "already running" in r.stderr, "a second dispatcher is refused", r.stdout + r.stderr)
    ok = wait_until(lambda: t.state("b1") == "done" and t.state("n1") == "submitted" and t.state("z1") == "failed", 30)
    c.ok(ok and "dispatcher ended while" in t.e("z1").get("error", ""),
         "restart resumes from the files: b1 marked done, n1 submitted, the entry left submitting marked failed (it "
         "may have submitted; not run again by itself)", t.log()[-1500:])
    r = t.q(t.B, ["remove", n1 or "q9999"])
    c.ok(r.returncode == 1 and "only a waiting entry" in r.stderr, "a submitted entry cannot be removed", r.stderr)
    r = t.q(t.B, ["mark-done", n1 or "q9999"])
    c.ok(r.returncode == 1 and "still in squeue" in r.stderr, "mark-done refuses an entry whose job is queued", r.stderr)
    r = t.q(t.A, ["mark-done", z1 or "q9999"])
    c.ok(r.returncode == 0 and t.state("z1") == "done", "mark-done: the owner closes its failed entry that left no job",
         r.stdout + r.stderr)
    os.kill(t.disp.pid, signal.SIGSTOP)                  # the test's own dispatcher, stopped for three looks and more
    time.sleep(2.5)
    st = t.q(t.repo, ["status"]).stdout
    os.kill(t.disp.pid, signal.SIGCONT)
    ok = wait_until(lambda: "dispatcher: running" in t.q(t.repo, ["status"]).stdout, 20)
    c.ok("dispatcher: HUNG" in st and ok, "status says HUNG when the heartbeat is older than three looks, and running "
         "again once the dispatcher goes on", st)


def children(t, c):
    """Review 3 and 4: what a command leaves behind cannot hold the dispatcher, and what it submitted is kept."""
    t.settle("n1")
    r, bg = t.add(t.A, "bg1", ["--cmd", f"sbatch -J bg1 {t.hold} bg1; sleep 30 &"])
    t.names.add("bg1")
    t0 = time.time()
    ok = wait_until(lambda: t.state("bg1") in ("submitted", "failed"), 30)
    e = t.e("bg1")
    live_bg = [j for j, n in t.live() if n == "bg1"]
    lg = open(e["output_log"]).read() if e.get("output_log") and os.path.isfile(e["output_log"]) else ""
    c.ok(ok and e["state"] == "submitted" and time.time() - t0 < 10 and e.get("job_ids") == live_bg and live_bg
         and "processes it left in its group were ended" in lg,
         f"review 3: a wrapper that submits its job and leaves a child is submitted at once (output to files, not "
         f"pipes), job {live_bg} recorded, the child ended", json.dumps(e)[:1200] + lg[-400:])
    r, bt = t.add(t.B, "bt1", ["--cmd", f"sbatch -J bt1 {t.hold} bt1; sleep 60"])
    t.names.add("bt1")
    ok = wait_until(lambda: t.state("bt1") == "failed", 40)
    e = t.e("bt1")
    live_bt = [j for j, n in t.live() if n == "bt1"]
    r = t.q(t.B, ["retry", bt or "q9999"])
    c.ok(ok and "timed out" in e.get("error", "") and live_bt and e.get("job_ids") == live_bt and r.returncode == 1
         and "still in squeue" in r.stderr,
         "review 3: a command that submitted its job and then timed out (--cmd-timeout 4) is failed with its job "
         "recorded; retry is refused while that job is queued", json.dumps(e)[:1200] + r.stderr)
    t.release("bg1", "bt1")
    wait_until(lambda: len(t.live()) == 1, 30)
    t.names.update({"sg1", "sgx", "nx"})
    r, sg = t.add(t.C, "sg1", ["--cmd", f"sbatch -J sg1 {t.hold} sg1; "
                                        f"setsid bash -c 'while [ ! -e {t.rel}/sgx ]; do sleep 0.2; done' &"])
    r, nx = t.add(t.A, "nx", t.hold_cmd("nx"))
    ok = wait_until(lambda: t.state("sg1") == "submitted" and t.state("nx") == "submitted", 20)
    st = t.q(t.repo, ["status"]).stdout
    c.ok(ok and "dispatcher: running" in st and len(t.live()) == 3,
         "review 4: a grandchild that left the process group (setsid) and holds the command's output does not hold "
         "the dispatcher: sg1 and the next entry are submitted within seconds, its heartbeat is fresh",
         st + t.log()[-800:])
    t.release("sgx")


def kill_restart(t, c):
    """Review 5: after a SIGKILL of the dispatcher, the command it was running is ended by the restart before
    its first look, so it cannot submit beside the new dispatcher's submissions."""
    t.settle("n1", "sg1", "nx")
    t.foreign("kfill")                                   # four live jobs
    wait_until(lambda: len(t.live()) == 4, 30)
    t.names.update({"orph", "y0"})
    r, x = t.add_orch(t.A, "orph", ["--priority", "0", "--cmd", f"sleep 8; sbatch -J orph {t.hold} orph"])
    ok = wait_until(lambda: t.state("orph") == "submitting" and t.e("orph").get("pgid"), 30, 0.05)
    pg = t.e("orph").get("pgid") if ok else None
    r, y = t.add(t.C, "y0", t.hold_cmd("y0"))
    time.sleep(1.0)
    os.kill(t.disp.pid, signal.SIGKILL)                  # the test's own dispatcher
    t.disp.wait(10)
    c.ok(ok and pg and t.start(*FAST), "dispatcher killed (SIGKILL) while orph's command ran; restarted")
    seen = []
    wait_until(lambda: seen.extend(n for _, n in t.live() if n == "orph") or False, 12, 0.1)
    e = t.e("orph")
    c.ok(not seen and e["state"] == "failed" and "was ended" in e.get("error", "") and t.state("y0") == "submitted"
         and t.max_live <= 5 and not os.path.exists(f"/proc/{pg}"),
         f"review 5: the restart ended the old command's process group ({pg}): orph never submitted, orph failed, "
         f"y0 submitted, never more than five jobs ({t.max_live})", json.dumps(e)[:1200] + t.log()[-800:])


def dispatch_marker(t, c):
    """Review 6: the marker reaches a job that a --cmd wrapper submits itself; check-dispatch is valid in the
    wrapper and not in that job, which is why wrappers call it."""
    t.settle("n1", "nx", "y0")
    cdjob = os.path.join(t.fx["root"], "cdjob.sh")
    F.write_exe(cdjob, CDJOB.replace("@REL@", t.rel))
    t.names.add("cd1")
    wrap = os.path.join(t.rel, "cd-wrap")
    r, cd = t.add(t.A, "cd1", ["--cmd", f"harness/bin/nrpic-queue check-dispatch > {wrap} 2>&1; echo rc=$? >> {wrap}; "
                                        f"sbatch -J cd1 {cdjob} cd1"])
    jobf = os.path.join(t.rel, "cd-job")
    ok = wait_until(lambda: "rc=" in open(jobf).read(), 30)
    w, j = (open(wrap).read() if os.path.isfile(wrap) else ""), (open(jobf).read() if os.path.isfile(jobf) else "")
    c.ok(ok and "rc=0" in w and "valid:" in w and "rc=1" in j and "not inside a dispatch" in j
         and re.search(rf"^NRPIC_QUEUE_DISPATCH={cd}:", j, re.M),
         "review 6: the marker reaches the job the wrapper submitted itself, but check-dispatch says it is valid only "
         "inside the dispatch (0 in the wrapper, 1 in the job)", w + j)
    r = t.q(t.A, ["check-dispatch"])
    c.ok(r.returncode == 1 and "does not come from the dispatcher" in r.stderr, "check-dispatch without a marker: 1",
         r.stderr)


def exception(t, c):
    """An error between the claim and the end of a dispatch fails the entry with the error's last line."""
    lock = os.path.join(t.qdir, "submit.lock")
    if os.path.exists(lock):
        os.remove(lock)
    os.mkdir(lock)                                       # opening it for the lock now fails
    try:
        r, ex = t.add(t.C, "ex1", ["--cmd", "true"])
        ok = wait_until(lambda: t.state("ex1") == "failed", 20)
        e = t.e("ex1")
    finally:
        os.rmdir(lock)
    c.ok(ok and "IsADirectoryError" in e.get("error_line", "") and t.disp.poll() is None,
         "an error between the claim and the end of the dispatch fails the entry (last line of the traceback), it "
         "is not left submitting; the dispatcher goes on", json.dumps(e)[:1000])


def alert(t, c):
    """Review 2: two jobs named like a running job are not a chain's hand-over: ALERT. A job of the user's own
    that comes in during a dispatch is not counted as the entry's rise."""
    t.settle()
    out = os.path.join(t.fx["root"], "elsewhere")
    os.makedirs(out, exist_ok=True)
    t.names.update({"u1", "u1x"})
    r, u1 = t.add(t.A, "u1", ["--cmd", f"sbatch -J u1 {t.hold} u1; sbatch -D {out} -J other {t.hold} u1x > /dev/null"])
    ok = wait_until(lambda: t.state("u1") == "submitted", 30)
    time.sleep(1.5)
    c.ok(ok and not os.path.exists(t.alert) and len(t.live()) == 2 and f"during the dispatch of {u1} job(s) of the "
         "user's own came in" in t.log(), "a job of the user's own (working directory outside the repository, not "
         "printed) that came in during a dispatch is not counted as its rise: no ALERT", t.log()[-800:])
    t.settle()
    t.foreign("dupq", "dupq0")
    wait_until(lambda: len(t.live()) == 1, 30)
    t.names.update({"x1a", "x1b"})
    r, x1 = t.add_orch(t.A, "x1", ["--priority", "0", "--cmd",
                                   f"sbatch -J dupq {t.hold} x1a; sbatch -J dupq {t.hold} x1b"])
    ok = wait_until(lambda: os.path.isfile(t.alert), 30)
    r, y1 = t.add(t.B, "y1", t.hold_cmd("y1"))
    time.sleep(3)
    a = json.load(open(t.alert)) if ok else {}
    c.ok(ok and a.get("entry") == x1 and len(a.get("new_jobs", [])) == 2
         and all(j["printed_by_the_command"] for j in a["new_jobs"]) and not a.get("chain_successors")
         and "ALERT: the account's jobs rose by 2" in t.log() and t.state("y1") == "waiting" and len(t.live()) == 3,
         "review 2: a command that submits two jobs named like a running job: both count (it printed them), ALERT; "
         "nothing more submitted (y1 waits six looks)", json.dumps(a) + t.log()[-800:])
    c.ok("ALERT since" in t.q(t.repo, ["status"]).stdout, "status shows the ALERT")
    r = t.q(t.A, ["clear-alert"])
    c.ok(r.returncode == 1 and "orchestrator" in r.stderr, "clear-alert is the orchestrator's", r.stderr)
    pause = os.path.join(t.repo, "locks", "PAUSE")
    open(pause, "w").write('{"window": "test"}\n')
    r = t.q(t.repo, ["clear-alert"])
    ok = wait_until(lambda: t.state("y1") == "submitted", 30)
    c.ok(r.returncode == 0 and ok and not os.path.exists(t.alert) and "the pause flag locks/PAUSE exists" in t.log(),
         "clear-alert: submissions resume (y1), also while the pause flag exists (decision 0026 item 2)",
         r.stdout + r.stderr + t.log()[-600:])
    os.remove(pause)


def keeper_record(t):
    """The last cap-keeper record of the ALERT file, and how many records the file holds."""
    try:
        a = json.load(open(t.alert))
    except (OSError, ValueError):
        return {}, 0
    recs = [a] + list(a.get("more") or [])
    keep = [r for r in recs if r.get("kind") == "cap-keeper"]
    return (keep[-1] if keep else {}), len(recs)


def keeper(t, c):
    """The cap keeper never cancels a job of the user's own (not of an entry, no run-id name, working directory
    outside the repository): it counts toward the cap, and only our pending jobs are cancelled, newest first,
    never a running one and never a running chain's next segment: first ours of no entry, then those of the
    newest submitted entries, which go back to waiting. Cases (a) to (f) of the decisions on the keeper."""
    t.settle("y1")
    under = os.path.join(t.repo, "scratch", "tmp-queue-test")        # a directory under the fixture's repository
    os.makedirs(under, exist_ok=True)
    # (a) five of ours plus one pending job of the user's own, submitted last
    for lab, hold in (("ka", False), ("kb", True), ("kc", True), ("kd", False)):
        t.add(t.B, lab, t.hold_cmd(lab, hold=hold))
    ok = wait_until(lambda: all(t.state(l) == "submitted" for l in ("ka", "kb", "kc", "kd")), 30)
    c.ok(ok and len(t.live()) == 5, "(a) five jobs of ours: y1, ka and kd running, kb and kc pending")
    jid = {l: t.e(l)["job_ids"][0] for l in ("ka", "kb", "kc", "kd", "y1")}
    t.mon_pause = True                                   # the excesses below are made on purpose
    fa1 = t.foreign("fa1", hold=True)
    ok = wait_until(lambda: keeper_record(t)[0].get("ts"), 30)
    time.sleep(1)
    rec, nrec = keeper_record(t)
    live_ids = {j for j, _ in t.live()}
    c.ok(ok and [j["id"] for j in rec.get("cancelled", [])] == [jid["kc"]] and fa1 in live_ids
         and jid["kc"] not in live_ids and len(live_ids) == 5 and rec.get("foreign") == 1 and rec.get("halts")
         and t.state("kc") == "waiting" and "cancelled by the cap keeper" in (t.e("kc").get("wait") or {}).get("what", ""),
         "(a) the user's pending job submitted last is left; exactly one of ours, the newest entry's pending job (kc), "
         "is cancelled and kc is back to waiting; five jobs queued", json.dumps(rec)[:2000])
    t.q(t.repo, ["clear-alert"])
    time.sleep(1.5)
    c.ok(t.state("kc") == "waiting", "(a) at five jobs kc waits")
    # (b) two jobs of the user's own and five of ours: two of ours are cancelled, the user's are left
    t.release("fa1")
    ok = wait_until(lambda: t.state("kc") == "submitted", 30)
    jid["kc"] = t.e("kc")["job_ids"][0] if ok else "?"
    fb1, fb2 = t.foreign("fb1"), t.foreign("fb2", hold=True)
    ok = wait_until(lambda: keeper_record(t)[0].get("ts"), 30)
    time.sleep(1)
    rec, nrec = keeper_record(t)
    live_ids = {j for j, _ in t.live()}
    c.ok(ok and sorted(j["id"] for j in rec.get("cancelled", [])) == sorted([jid["kc"], jid["kb"]])
         and fb1 in live_ids and fb2 in live_ids and len(live_ids) == 5 and rec.get("foreign") == 2
         and t.state("kb") == "waiting" and t.state("kc") == "waiting",
         "(b) two jobs of the user's own (one pending) and five of ours: two of ours are cancelled (the newest "
         "entries' pending jobs, kc and kb), the user's are left; five jobs queued", json.dumps(rec)[:2000])
    t.q(t.repo, ["clear-alert"])
    for lab in ("kb", "kc"):
        t.q(t.B, ["remove", t.ids[lab]])
    # (c) a job with a run-id name and no entry, and one from a directory under the repository with any name,
    # are ours: they are cancelled before an entry's pending job
    t.release("fb1", "fb2", "ka", "kd")
    wait_until(lambda: len(t.live()) == 1, 30)
    t.add(t.B, "kp", t.hold_cmd("kp", hold=True))
    ok = wait_until(lambda: t.state("kp") == "submitted", 30)
    jid["kp"] = t.e("kp")["job_ids"][0] if ok else "?"
    rid = t.foreign("A-20261125-010203-abcdef1", "rid1", hold=True)          # outside the repository
    zz = t.foreign("zzwd", hold=True, cwd=under)                              # under the repository
    fcs = [t.foreign("fc1"), t.foreign("fc2", hold=True), t.foreign("fc3", hold=True)]
    ok = wait_until(lambda: keeper_record(t)[0].get("ts"), 30)
    time.sleep(1)
    rec, nrec = keeper_record(t)
    live_ids = {j for j, _ in t.live()}
    how = {j["id"]: j.get("ours") for j in rec.get("cancelled", [])}
    c.ok(ok and sorted(how) == sorted([rid, zz]) and how.get(rid) == "run id" and how.get(zz) == "under the repository"
         and jid["kp"] in live_ids and t.state("kp") == "submitted" and all(f in live_ids for f in fcs)
         and len(live_ids) == 5,
         "(c) a run-id-named job without an entry and a job from a directory under the repository are ours: both are "
         "cancelled, before the entry's pending job (kp, left) and none of the user's three", json.dumps(rec)[:2000])
    t.q(t.repo, ["clear-alert"])
    # (d) six jobs of the user's own and none of ours: nothing cancelled, one ALERT, not a second one
    t.release("y1", "kp")
    wait_until(lambda: len(t.live()) == 3, 30)
    fds = fcs + [t.foreign("fd1"), t.foreign("fd2", hold=True), t.foreign("fd3", hold=True)]
    ok = wait_until(lambda: keeper_record(t)[0].get("ts"), 30)
    time.sleep(4)                                        # four more looks of the keeper
    rec, nrec = keeper_record(t)
    live_ids = {j for j, _ in t.live()}
    c.ok(ok and nrec == 1 and not rec.get("cancelled") and rec.get("foreign") == 6 and rec.get("ours") == 0
         and not rec.get("halts") and all(f in live_ids for f in fds),
         "(d) six jobs of the user's own and none of ours: nothing cancelled, one ALERT record (not halting), no "
         "second one at the next looks", json.dumps(rec)[:1500])
    fd4 = t.foreign("fd4")
    time.sleep(4)
    rec, nrec = keeper_record(t)
    c.ok(nrec == 1 and "none of ours may be cancelled" in t.log(), "(d) a seventh job of the user's own: logged, still "
         "one ALERT record", t.log()[-600:])
    # (e) status lists the user's own jobs on a line of their own
    st = t.q(t.repo, ["status"]).stdout
    m = re.search(r"^  not ours: (.*)$", st, re.M)
    c.ok(m and all(f in m.group(1) for f in fds + [fd4]) and "0 of this program, 7 of the user's own" in st
         and "does not halt the dispatcher" in st,
         "(e) status: the user's own jobs on the line 'not ours: ...'; the ALERT says it does not halt", st)
    r, kw = t.add(t.C, "kw", t.hold_cmd("kw"))
    time.sleep(2)
    c.ok(t.state("kw") == "waiting", "(d) at seven jobs an entry waits (the count rule)")
    t.release("fc1", "fc2", "fc3", "fd1")
    ok = wait_until(lambda: t.state("kw") == "submitted", 30)
    c.ok(ok and os.path.isfile(t.alert), "(d) below five jobs the entry is dispatched although that ALERT stands: it "
         "records an excess of the user's own jobs only and does not halt")
    t.q(t.repo, ["clear-alert"])
    # (f) our pending job that is the next segment of our running chain is never cancelled
    t.settle()
    cs0 = t.foreign("csr", "csr0", cwd=under)
    cs1 = t.foreign("csr", "csr1", hold=True, cwd=under)
    fs = [t.foreign(f"ff{i}") for i in range(4)]
    ok = wait_until(lambda: keeper_record(t)[0].get("ts"), 30)
    time.sleep(1)
    rec, nrec = keeper_record(t)
    live_ids = {j for j, _ in t.live()}
    c.ok(ok and not rec.get("cancelled") and rec.get("left_above_the_cap") == 1 and cs0 in live_ids and cs1 in live_ids
         and all(f in live_ids for f in fs),
         "(f) six jobs: our running chain, its pending next segment (protected) and four of the user's own: nothing is "
         "cancelled, one job is reported left above the cap", json.dumps(rec)[:1500])
    t.q(t.repo, ["clear-alert"])
    t.settle()
    t.mon_pause = False


def arrays(t, c):
    """`squeue -r`: every task of a job array is counted."""
    sq = os.path.join(t.fx["fakebin"], "squeue")
    orig = open(sq).read()
    open(sq, "w").write("#!/bin/bash\nfor a in \"$@\"; do [[ $a == -r ]] && r=1; done\n"
                        "if [[ -n $r ]]; then printf '7_0|arr|PENDING\\n7_1|arr|PENDING\\n7_2|arr|PENDING\\n'; "
                        "else echo '7_[0-2]|arr|PENDING'; fi\n")
    try:
        n = F.H.queue_count(F.H.build_env(F.H.Worktree(t.A)))
    finally:
        open(sq, "w").write(orig)
    c.ok(n == 3, f"queue_jobs asks squeue -r: an array of three pending tasks counts three ({n})")


def main():
    t = T()
    c = F.Checks(f"nrpic-queue (scratch repo {t.repo})")
    try:
        refusals(t, c)
        if order_and_cap(t, c):
            after(t, c)
            refusal(t, c)
            chain(t, c)
            busy(t, c)
            failing(t, c)
            stop_and_restart(t, c)
            children(t, c)
            kill_restart(t, c)
            dispatch_marker(t, c)
            exception(t, c)
            alert(t, c)
            keeper(t, c)
        r = t.q(t.repo, ["stop", "--wait", "30"])
        arrays(t, c)
    finally:
        t.cleanup()
    c.ok(t.max_live <= 5 and t.samples > 100,
         f"over the whole test (but the keeper's own excess) never more than five live jobs ({t.max_live} at most in "
         f"{t.samples} samples)")
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
