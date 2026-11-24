#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-queue (decision 0033) in a scratch repository with the fake Slurm of
rc_fixture.py: no card, no real Slurm job; nothing of the live checkout is touched.

    python3 -I harness/tests/test_nrpic_queue.py

Fake card jobs (hold.sh, outside the worktrees) run until the test releases them, so the test decides when
a job ends; a thread samples the fake Slurm state every 50 ms for the largest number of live jobs. The
dispatcher looks every 0.5 s. Covers: refusals of add (from a data root without -C, duplicate label,
unknown --after, both forms at once, a local launcher, arguments that nrpic-run's dry run refuses), remove
by the owner and by the orchestrator, not by another owner; seven entries of three owners never give more
than five jobs; the order (priority, then the owner served longest ago, then the order of adding) as
`status` predicts it; --after waits until the entry's job has left squeue; nrpic-run's queue-cap refusal
puts an entry back to waiting with nothing registered, and once a job ends it is submitted (registered,
committed, run id and job id kept); a queued `nrpic-run submit` argument list; a chain of two segments
stays submitted across its hand-over and is done only after its last job ended; an entry whose worktree is
mid-merge is passed over until the merge is over; a malformed entry file is skipped; a failing command is marked
failed with its stderr and the loop goes on; retry; STOP ends the dispatcher; a restart resumes from the
files (done detection, a new entry, an entry left `submitting` marked failed) and a second dispatcher is
refused; a command that submits two jobs writes ALERT and stops submissions until clear-alert; the pause
flag does not stop submissions (decision 0026 item 2).
"""
import calendar
import json
import os
import re
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
POLL = "0.5"


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
        self.max_live, self.samples, self.mon_stop = 0, 0, False
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

    def hold_cmd(self, name):
        self.names.add(name)
        return ["--cmd", f"sbatch -J {name} {self.hold} {name}"]

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

    def monitor(self):
        while not self.mon_stop:
            try:
                n = len(self.live())
            except OSError:
                n = 0
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

    def start(self):
        out = open(os.path.join(self.fx["root"], "dispatcher.out"), "a")
        self.disp = subprocess.Popen([os.path.join(self.repo, "harness", "bin", "nrpic-queue"), "-C", self.repo, "run",
                                      "--poll", POLL], cwd=self.repo, env=F.H.boot_env(), stdin=subprocess.DEVNULL,
                                     stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        return wait_until(lambda: "dispatcher start: pid %d" % self.disp.pid in self.log(), 30)

    def cleanup(self):
        if self.disp is not None and self.disp.poll() is None:
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
    c.ok(r.returncode == 1 and "not inside a worktree" in r.stderr and not os.path.isdir(t.qdir),
         "add from a data root of the main checkout (scratch/) is refused, nothing written", r.stdout + r.stderr)
    r = t.q(elsewhere, ["-C", A, "add", "--label", "zc", "--cmd", "true"])
    zc = r.stdout.split()[0] if r.returncode == 0 else None
    t.ids["zc"] = zc
    c.ok(zc and t.e("zc")["owner"] == "A-emd-pbh" and t.e("zc")["worktree"] == os.path.realpath(A)
         and t.e("zc")["state"] == "waiting", "add -C <worktree> from elsewhere records that worktree's owner and root",
         r.stdout + r.stderr)
    r = t.q(B, ["remove", zc or "q9999"])
    c.ok(r.returncode == 1 and "belongs to A-emd-pbh" in r.stderr, "another owner's remove is refused", r.stderr)
    r = t.q(A, ["remove", zc or "q9999"])
    c.ok(r.returncode == 0 and t.state("zc") == "removed", "the owner removes its own waiting entry", r.stdout + r.stderr)
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
        r, eid = t.add(wt, lab, ["--priority", str(p)] + t.hold_cmd(lab))
        if not c.ok(eid, f"add {lab} (priority {p})", r.stdout + r.stderr):
            return False
    want = ["c1", "b2", "a1", "c2", "b1", "a2", "a3"]
    inv = {v: k for k, v in t.ids.items()}
    st = t.q(t.repo, ["status"]).stdout
    got = [inv.get(g) for g in re.findall(r"^\s+\d+\. (q\d+) ", st, re.M)]
    c.ok(got == want and "NOT running" in st, "status predicts the order: priority 0, priority 2, then round robin over "
         "the owners at priority 5 (A never served, C, B, then A's rest); dispatcher not running yet", st)
    t.mon.start()
    c.ok(t.start(), "dispatcher started (run -C <main checkout> --poll 0.5)")
    ok5 = wait_until(lambda: sum(t.state(l) == "submitted" for l in want) == 5, 60)
    time.sleep(3)
    sub = [l for _, l in sorted((t.e(l)["dispatch_no"], l) for l in want if t.state(l) == "submitted")]
    c.ok(ok5 and sub == want[:5] and t.state("a2") == "waiting" and t.state("a3") == "waiting" and len(t.live()) == 5,
         f"seven entries of three owners: five submitted in order {sub}, two wait at the cap for six looks",
         t.log()[-1500:])
    st = t.q(t.repo, ["status"]).stdout
    c.ok("5 of 5 jobs" in st and "dispatcher: running" in st and f"{t.ids['c1']} C-sidm/c1" in st,
         "status: 5 of 5 jobs, dispatcher running, each job named with its entry", st)
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
    r, a4 = t.add(t.A, "a4", ["--after", "a3", "--priority", "0"] + t.hold_cmd("a4"))
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
    env = F.H.build_env(F.H.Worktree(A))
    t.names.update({"foreign1", "foreign2"})
    F.sh(["sbatch", "-J", "foreign1", t.hold, "foreign1"], env=env)        # another session's job
    c.ok(wait_until(lambda: len(t.live()) == 4, 30), "four live jobs (three entries and another session's)")
    flag = os.path.join(t.fx["root"], "flag-r1")
    cmd = (f"test -e {flag} || {{ touch {flag}; sbatch -J foreign2 {t.hold} foreign2; }}; "
           "exec harness/bin/nrpic-run submit --kind scouting --gate G1 --purpose 'queued, refused once by the cap' "
           "--launcher batch --list tracks/A-emd-pbh/q/batch.txt --wall 00:10:00")
    head0 = t.head(A)
    runs = os.path.join(A, "tracks", "A-emd-pbh", "runs")
    runs0 = sorted(os.listdir(runs))
    r, r1 = t.add(A, "r1", ["--priority", "0", "--cmd", cmd])
    ok = wait_until(lambda: t.e("r1").get("refusals") == 1 and t.state("r1") == "waiting", 60)
    c.ok(ok and sorted(os.listdir(runs)) == runs0 and t.head(A) == head0 and f"refused {r1}" in t.log()
         and "queue cap: 5 jobs" in t.e("r1").get("last_refusal", ""),
         "refusal path: another job came in between the count and nrpic-run's own; nrpic-run refused (queue cap), the "
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
    c.ok(ok and prid.startswith("B-") and os.path.isfile(os.path.join(B, "tracks", "B-emd-gw", "runs", prid,
                                                                       "manifest.json")),
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
    try:
        r, m1 = t.add(t.A, "m1", ["--priority", "0"] + t.hold_cmd("m1"))
        r, d1 = t.add(t.B, "d1", ["--priority", "0", "--no-check", "--", "--kind", "scouting", "--gate", "G1",
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
    r, f1 = t.add(t.C, "f1", ["--priority", "1", "--cmd",
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
    c.ok(t.start(), "dispatcher restarted")
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


def alert(t, c):
    t.release("a2", "a4", "h1")
    wait_until(lambda: len(t.live()) == 1, 30)
    t.names.update({"x1a", "x1b"})
    r, x1 = t.add(t.A, "x1", ["--priority", "0", "--cmd", f"sbatch -J x1a {t.hold} x1a; sbatch -J x1b {t.hold} x1b"])
    ok = wait_until(lambda: os.path.isfile(t.alert), 30)
    r, y1 = t.add(t.B, "y1", t.hold_cmd("y1"))
    time.sleep(3)
    a = json.load(open(t.alert)) if ok else {}
    c.ok(ok and a.get("entry") == x1 and len(a.get("new_jobs", [])) == 2 and "ALERT: the account's jobs rose by 2"
         in t.log() and t.state("y1") == "waiting" and len(t.live()) == 3,
         "a command that submits two jobs: ALERT written and logged; nothing more submitted (y1 waits six looks)",
         json.dumps(a) + t.log()[-800:])
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
            alert(t, c)
    finally:
        t.cleanup()
    c.ok(t.max_live <= 5 and t.samples > 100,
         f"over the whole test never more than five live jobs ({t.max_live} at most in {t.samples} samples)")
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
