#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-run in a scratch repository (acceptance test 4 of brief 11.7).

    python3 -I harness/tests/test_nrpic_run.py [--full]     (--full: the dummy run lasts 30 s, not 3 s)

Covers: a dummy local run registered, run, checksummed, committed twice and re-verified; tampered
output detected; dirty worktree refused; budget refusals (kb has 0 GPU-hours, A asks more than 60,
cores above 16); production refused without a plan and before the previous gate's pass tag; the
caller's environment ignored; a background run; batch and chain launchers through the repository's
scripts/gpu_batch.sh and scripts/submit_chain.sh with a fake Slurm and a fake athena; GPU-hours
counted across runs; another owner's runs not counted; the wrong worktree's copy refused.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import rc_fixture as F  # noqa: E402


def run_cmd(wt, args, env=None, cwd=None, timeout=300):
    return F.sh([os.path.join(wt, "harness", "bin", "nrpic-run")] + args, cwd=cwd or wt, env=env,
                check=False, timeout=timeout)


def manifest(wt, owner, rid):
    return json.load(open(os.path.join(wt, "tracks", owner, "runs", rid, "manifest.json")))


def run_id_from(out):
    for tok in out.split():
        if tok.count("-") >= 3 and tok.rstrip(":").split("-")[0] in ("A", "B", "core", "kb"):
            return tok.rstrip(":")
    return None


def wait_until(pred, timeout=120, step=0.5):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if pred():
            return True
        time.sleep(step)
    return False


def main():
    full = "--full" in sys.argv
    fx = F.make_repo("test-run")
    A, B, KB = fx["wt"]["A-emd-pbh"], fx["wt"]["B-emd-gw"], fx["wt"]["kb"]
    c = F.Checks(f"nrpic-run (scratch repo {fx['repo']})")

    # 1. dummy local run, with a polluted caller environment that must not leak into the run
    secs = 30 if full else 3
    prog = ("import os, time, json; d = os.environ['NRPIC_RUN_DIR']; t0 = time.time(); "
            f"time.sleep({secs}); "
            "json.dump({k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'POLLUTED', 'NRPIC_TRACK', "
            "'NRPIC_RUN_ID', 'PYTHONPATH')}, open(os.path.join(d, 'env.json'), 'w')); "
            "open(os.path.join(d, 'result.txt'), 'w').write('slept %.1f s\\n' % (time.time() - t0)); "
            "print('dummy done')")
    polluted = dict(F.H.boot_env(), POLLUTED="yes", OMP_NUM_THREADS="99", PYTHONPATH="/nonexistent",
                    GIT_DIR="/nonexistent")
    t0 = time.time()
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "no venv", "--dry-run",
                    "--", "python3", "-c", "print(1)"])
    c.ok(r.returncode == 1 and "nrpic-env create --no-kokkos" in r.stderr,
         "a local python command without the worktree's .venv is refused with the fix", r.stderr)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", f"dummy {secs} s run",
                    "--cores", "2", "--allow-no-venv", "--", "python3", "-c", prog], env=polluted, timeout=secs + 120)
    rid = run_id_from(r.stdout)
    c.ok(r.returncode == 0 and rid, "dummy local run registered and finished", r.stdout + r.stderr)
    m = manifest(A, "A-emd-pbh", rid)
    c.ok(m["status"] == "completed" and m["exit_code"] == 0, "manifest status completed, exit 0")
    c.ok(m["resources"]["walltime_s"] >= secs - 0.5, f"wall time recorded ({m['resources']['walltime_s']} s)")
    log = F.sh(["git", "-C", A, "log", "--format=%s", "-3"]).stdout
    c.ok(f"A(run): register {rid}" in log and f"A(run): finish {rid} (completed)" in log,
         "manifest committed before and after the run (two path-limited commits)", log)
    c.ok(F.sh(["git", "-C", A, "status", "--porcelain"]).stdout.strip() == "", "worktree clean afterwards")
    out = os.path.join(fx["repo"], m["outputs"]["dir"])
    envj = json.load(open(os.path.join(out, "env.json")))
    c.ok(envj["OMP_NUM_THREADS"] == "2" and envj["POLLUTED"] is None and envj["PYTHONPATH"] is None
         and envj["NRPIC_TRACK"] == "A-emd-pbh" and envj["NRPIC_RUN_ID"] == rid,
         "run environment built from files: caller's variables absent, OMP_NUM_THREADS = --cores", str(envj))
    c.ok(m["outputs"]["dir"] == f"scratch/A-emd-pbh/{rid}" and os.path.isfile(os.path.join(out, "sha256sums.txt")),
         "output under scratch/<ID>/<run_id>/ with sha256sums.txt")
    c.ok(m["git"]["sha"].startswith(rid.split("-")[-1]) and m["git"]["dirty"] is False,
         "run id carries the commit of the code; manifest records dirty=false")
    c.ok(m["env"]["env_hash"] and m["env"]["machine_file_sha256"] and m["env"]["uv_lock_sha256"],
         "environment hash and its components recorded")
    r = run_cmd(A, ["verify", rid])
    c.ok(r.returncode == 0 and "PASS" in r.stdout, "verify re-checks the output checksums", r.stdout)
    sha = F.sh(["sha256sum", "-c", "sha256sums.txt"], cwd=out)
    c.ok(sha.returncode == 0, "sha256sums.txt is valid for `sha256sum -c`")
    with open(os.path.join(out, "result.txt"), "a") as f:
        f.write("tampered\n")
    r = run_cmd(A, ["verify", rid])
    c.ok(r.returncode == 1 and "changed output result.txt" in r.stdout, "verify detects a changed output", r.stdout)

    # 2. dirty worktree refused
    junk = os.path.join(A, "tracks", "A-emd-pbh", "junk.txt")
    open(junk, "w").write("uncommitted\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--", "true"])
    c.ok(r.returncode == 1 and "not clean" in r.stderr, "a dirty worktree is refused", r.stderr)
    os.remove(junk)

    # 2b. helpers sharing one worktree: --package scopes the cleanliness check
    F.commit_file(A, "tracks/A-emd-pbh/pkg/run.py", "print('pkg run')\n")
    other = os.path.join(A, "tracks", "A-emd-pbh", "other_helper", "draft.txt")
    os.makedirs(os.path.dirname(other), exist_ok=True)
    open(other, "w").write("another helper's uncommitted work\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv",
                    "--dry-run", "--", "python3", "tracks/A-emd-pbh/pkg/run.py"])
    c.ok(r.returncode == 1 and "--package DIR" in r.stderr, "another helper's untracked file: refused, with the --package hint",
         r.stderr)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv", "--dry-run",
                    "--package", "tracks/A-emd-pbh/pkg", "--", "python3", "tracks/A-emd-pbh/pkg/run.py"])
    dm = json.loads(r.stdout[:r.stdout.rindex("}") + 1]) if r.returncode == 0 else {}
    c.ok(r.returncode == 0 and dm["git"]["package"] == ["tracks/A-emd-pbh/pkg"]
         and dm["git"]["outside_package"]["count"] == 1, "with --package: accepted, the other helper's file recorded", r.stderr)
    open(os.path.join(A, "tracks", "A-emd-pbh", "pkg", "new.py"), "w").write("x = 1\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv", "--dry-run",
                    "--package", "tracks/A-emd-pbh/pkg", "--", "python3", "tracks/A-emd-pbh/pkg/run.py"])
    c.ok(r.returncode == 1 and "pkg/new.py" in r.stderr, "an untracked file inside the package: refused", r.stderr)
    os.remove(os.path.join(A, "tracks", "A-emd-pbh", "pkg", "new.py"))
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv", "--dry-run",
                    "--package", "tracks/A-emd-pbh/pkg", "--", "python3", "tracks/A-emd-pbh/other_helper/draft.txt"])
    c.ok(r.returncode == 1 and "other_helper" in r.stderr, "an untracked input outside the package: refused", r.stderr)
    sc = os.path.join(A, "scripts", "gpu_batch.sh")
    orig_sc = open(sc).read()
    open(sc, "a").write("# local edit\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv", "--dry-run",
                    "--package", "tracks/A-emd-pbh/pkg", "--", "python3", "tracks/A-emd-pbh/pkg/run.py"])
    c.ok(r.returncode == 1 and "shared code" in r.stderr, "a modified shared script: refused even with --package", r.stderr)
    open(sc, "w").write(orig_sc)
    os.remove(other)
    os.rmdir(os.path.dirname(other))

    # 3. budgets (decision 0006)
    deck = "tracks/kb/inputs/t.athinput"
    F.commit_file(KB, deck, "<problem>\npgen_name = fake\n")
    F.commit_file(KB, "tracks/kb/inputs/list.txt", f"r1 {deck}\n")
    r = run_cmd(KB, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--launcher", "batch",
                     "--list", "tracks/kb/inputs/list.txt"])
    c.ok(r.returncode == 1 and "beyond the allotment" in r.stderr, "kb (0 GPU-hours) card run refused", r.stderr)
    adeck = "tracks/A-emd-pbh/inputs/chain.athinput"
    F.commit_file(A, adeck, "<problem>\npgen_name = fake_chain\n<output9>\nfile_type = rst\ndcycle = 5\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--launcher", "chain",
                    "--gpu-hours", "61", "--", adeck])
    c.ok(r.returncode == 1 and "beyond the allotment" in r.stderr, "A asking 61 of 60 GPU-hours refused", r.stderr)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--cores", "17", "--", "true"])
    c.ok(r.returncode == 1 and "allotment 16" in r.stderr, "17 cores refused (16 at a time)", r.stderr)

    # 4. production rules
    r = run_cmd(A, ["submit", "--kind", "production", "--gate", "G1", "--purpose", "x", "--", "true"])
    c.ok(r.returncode == 1 and "--preregistered" in r.stderr, "production without a plan refused", r.stderr)
    F.commit_file(A, "tracks/A-emd-pbh/stage/G1/PLAN.md", "# plan\n## scan-1\n")
    r = run_cmd(A, ["submit", "--kind", "production", "--gate", "G1", "--purpose", "x",
                    "--preregistered", "tracks/A-emd-pbh/stage/G1/PLAN.md#scan-1", "--", "true"])
    c.ok(r.returncode == 1 and "G0-pass" in r.stderr, "production for G1 refused before the G0 pass tag", r.stderr)
    F.sh(["git", "-C", A, "tag", "-a", "stage/A-emd-pbh/G0-pass-20261115", "-m", "test tag"])
    r = run_cmd(A, ["submit", "--kind", "production", "--gate", "G1", "--purpose", "x", "--dry-run",
                    "--preregistered", "tracks/A-emd-pbh/stage/G1/PLAN.md#scan-1", "--", "true"])
    c.ok(r.returncode == 0 and "dry run" in r.stdout, "production allowed after the tag (dry run)", r.stderr)

    # 5. wrong worktree's copy refused
    r = F.sh([os.path.join(A, "harness", "bin", "nrpic-run"), "status"], cwd=B, check=False)
    c.ok(r.returncode == 1 and "pass -C" in r.stderr, "calling A's copy from B's worktree is refused", r.stderr)

    # 6. background local run
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "background",
                    "--background", "--allow-no-venv", "--", "python3", "-c", "import time; time.sleep(2); print('bg')"])
    bg = run_id_from(r.stdout)
    st = run_cmd(A, ["status"]).stdout
    c.ok(r.returncode == 0 and bg and "running*" in st, "background run registered and live", r.stdout + st)
    od = os.path.join(fx["repo"], "scratch", "A-emd-pbh", bg)
    wait_until(lambda: os.path.isfile(os.path.join(od, ".nrpic", "result.json")), 60)
    r = run_cmd(A, ["finish", bg])
    c.ok(r.returncode == 0 and manifest(A, "A-emd-pbh", bg)["status"] == "completed",
         "background run closed with finish", r.stdout + r.stderr)

    # 7. batch launcher: scripts/gpu_batch.sh under the fake Slurm
    bdeck = "tracks/A-emd-pbh/inputs/b.athinput"
    F.commit_file(A, bdeck, "<problem>\npgen_name = fake_batch\n")
    F.commit_file(A, "tracks/A-emd-pbh/inputs/batch.txt", f"lo {bdeck} time/nlim=5\nhi {bdeck} time/nlim=9\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "batch of two",
                    "--launcher", "batch", "--list", "tracks/A-emd-pbh/inputs/batch.txt", "--wall", "00:10:00"])
    brid = run_id_from(r.stdout)
    c.ok(r.returncode == 0 and brid and "Slurm job" in r.stdout, "batch submitted through gpu_batch.sh", r.stdout + r.stderr)
    bod = os.path.join(fx["repo"], "scratch", "A-emd-pbh", brid)
    wait_until(lambda: os.path.isfile(os.path.join(bod, "batch.list.status")) and
               len(open(os.path.join(bod, "batch.list.status")).read().splitlines()) == 2, 120)
    wait_until(lambda: run_cmd(A, ["finish", brid]).returncode == 0, 60, 1.0)
    bm = manifest(A, "A-emd-pbh", brid)
    c.ok(bm["status"] == "completed" and bm["slurm"]["job_ids"] and bm["resources"]["gpu_hours"] > 0,
         f"batch finished: completed, job {bm['slurm']['job_ids']}, {bm['resources']['gpu_hours']} GPU-h",
         json.dumps(bm, indent=1)[:2000])
    c.ok(os.path.isfile(os.path.join(bod, "lo", "out1.txt")) and os.path.isfile(os.path.join(bod, "hi", "fake.hst")),
         "each batch entry wrote into scratch/<ID>/<run_id>/<name>/")
    c.ok(bm["code"]["problem"] == "fake_batch" and len(bm["batch_entries"]) == 2 and
         any(i["role"] == "exe" for i in bm["inputs"]), "problem, entries and executable checksum recorded")
    c.ok(run_cmd(A, ["verify", brid]).returncode == 0, "batch outputs re-verified")

    # 8. chain launcher: scripts/submit_chain.sh under the fake Slurm (two segments)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "chain of two segments",
                    "--launcher", "chain", "--gpu-hours", "2", "--", adeck, "time/tlim=1"])
    crid = run_id_from(r.stdout)
    c.ok(r.returncode == 0 and crid, "chain submitted through submit_chain.sh", r.stdout + r.stderr)
    cod = os.path.join(fx["repo"], "scratch", "A-emd-pbh", crid)
    wait_until(lambda: os.path.isfile(os.path.join(cod, "chain", "STATUS")) and
               open(os.path.join(cod, "chain", "STATUS")).read().strip() in ("DONE", "FAILED"), 180)
    wait_until(lambda: run_cmd(A, ["finish", crid]).returncode == 0, 60, 1.0)
    cm = manifest(A, "A-emd-pbh", crid)
    cfg = open(os.path.join(cod, "chain", "config.sh")).read()
    c.ok(cm["status"] == "completed" and len(cm["slurm"]["job_ids"]) == 2,
         f"chain finished after two segments (jobs {cm['slurm']['job_ids']})", json.dumps(cm, indent=1)[:2000])
    c.ok(cm["resources"]["segments_max"] == 2 and "MAX_SEGMENTS=2" in cfg,
         "chain capped at floor(2 h / 59 min) = 2 segments (MAX_SEGMENTS)")
    c.ok(os.path.isfile(os.path.join(cod, "out2.txt")) and run_cmd(A, ["verify", crid]).returncode == 0,
         "restart segment ran; chain outputs re-verified")

    # 9. accounting across runs and owners
    used = bm["resources"]["gpu_hours"] + cm["resources"]["gpu_hours"]
    lst = "tracks/A-emd-pbh/inputs/batch.txt"
    over = 60 - used + 0.0002
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "too much", "--launcher",
                    "batch", "--list", lst, "--gpu-hours", f"{over:.4f}", "--dry-run"])
    c.ok(r.returncode == 1 and "beyond the allotment" in r.stderr,
         f"used GPU-hours counted: {used:.4f} used, asking {over:.4f} more refused", r.stderr)
    under = 60 - used - 0.0002
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "just fits", "--launcher",
                    "batch", "--list", lst, "--gpu-hours", f"{under:.4f}", "--dry-run"])
    c.ok(r.returncode == 0, f"... and asking {under:.4f} allowed (dry run)", r.stderr)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G2", "--purpose", "other gate", "--launcher",
                    "chain", "--gpu-hours", "59", "--dry-run", "--", adeck])
    c.ok(r.returncode == 0, "the allotment is per gate: 59 GPU-hours toward G2 still allowed (dry run)", r.stderr)
    bdeck_b = "tracks/B-emd-gw/inputs/b.athinput"
    F.commit_file(B, bdeck_b, "<problem>\npgen_name = fake\n<output9>\nfile_type = rst\n")
    r = run_cmd(B, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "B", "--launcher", "chain",
                    "--gpu-hours", "40", "--dry-run", "--", bdeck_b])
    c.ok(r.returncode == 0, "B's allotment untouched by A's runs (all 40 of 40, dry run)", r.stderr)
    st = run_cmd(A, ["budget"]).stdout
    c.ok("G1: used" in st, "budget summary lists the GPU-hours used", st)
    c.ok(rid.startswith("A-2") and F.H.parse_run_id(rid) == ("A-emd-pbh", rid[2:17], rid[-7:]),
         "run id <short owner>-<YYYYMMDD-HHMMSS>-<commit7> (decision 0012)", rid)

    # 10. hand-written manifests of wave 1 (decision 0012): read, never fatal
    hand_manifests(c, fx, A, used)
    return c.done()


HAND = {
    # B and C: no outputs.dir, status "done", card_hours at the top level
    "A-emd-pbh-20261115-112946-b7b431d": {"run_id": "A-emd-pbh-20261115-112946-b7b431d", "command": ["x"],
                                          "commit": "b7b431d", "output_dir": "scratch/A-emd-pbh/hand1",
                                          "status": "done", "gate": "G1", "card_hours": 1.5, "kind": "scouting"},
    # E: status "failed (exit 1)", outputs as a list of files
    "A-emd-pbh-20261115-125316-dafadc4": {"run_id": "A-emd-pbh-20261115-125316-dafadc4", "status": "failed (exit 1)",
                                          "outputs": ["a.txt", "b.txt"], "gate": "G1", "launcher": "local"},
    # core: no status, output_directory, resources.card_hours, no gate
    "A-20261115-031705-b7b431d": {"run_id": "A-20261115-031705-b7b431d", "output_directory": "/nonexistent/x",
                                  "resources": {"card_hours": 0.25, "walltime_s": {"run1": 3.0, "run2": 1.5}}},
    # D: status None, outputs a list, "running" claimed by hand (cannot be checked: never live)
    "A-emd-pbh-20261115-042626-f3da881": {"run_id": "A-emd-pbh-20261115-042626-f3da881", "status": "running",
                                          "outputs": [{"path": "x"}], "gate": "G1", "launcher": "batch"},
    # F: superseded; kb: finished
    "A-emd-pbh-20261115-045332-ae6bca8": {"run_id": "A-emd-pbh-20261115-045332-ae6bca8", "status": "superseded",
                                          "outputs": {"files": 3}, "gate": "G1"},
    "A-emd-pbh-20261115-112414-6bb2b7d": {"run_id": "A-emd-pbh-20261115-112414-6bb2b7d", "status": "finished",
                                          "gate": "G1", "card_hours": 0.0},
}


def hand_manifests(c, fx, A, used_before):
    rdir = os.path.join(A, "tracks", "A-emd-pbh", "runs")
    for rid, m in HAND.items():
        os.makedirs(os.path.join(rdir, rid), exist_ok=True)
        json.dump(m, open(os.path.join(rdir, rid, "manifest.json"), "w"), indent=1)
    os.makedirs(os.path.join(rdir, "A-20261115-000001-0000000"))
    open(os.path.join(rdir, "A-20261115-000001-0000000", "manifest.json"), "w").write("{not json")
    os.makedirs(os.path.join(rdir, "A-20261115-000002-0000000"))
    open(os.path.join(rdir, "A-20261115-000002-0000000", "manifest.json"), "w").write("[1, 2]")
    F.sh(["git", "-C", A, "add", "--", "tracks/A-emd-pbh/runs"])
    F.sh(["git", "-C", A, "commit", "-q", "-m", "A(run): wave-1 manifests written by hand"])
    for sub in (["status"], ["budget"]):
        r = run_cmd(A, sub)
        c.ok(r.returncode == 0 and "Traceback" not in r.stderr and "nrpic-run lint" in r.stderr,
             f"`{sub[0]}` reads hand-written and unreadable manifests without crashing and says so", r.stdout + r.stderr)
    st = run_cmd(A, ["status"]).stdout
    c.ok("completedh" in st and "failedh" in st and "unknownh" in st and "supersededh" in st,
         "status words done/finished -> completed, 'failed (exit 1)' -> failed, none -> unknown, superseded kept", st)
    bud = run_cmd(A, ["budget"]).stdout
    want = used_before + 1.5
    c.ok(f"G1: used {want:.2f}" in bud and "no gate recorded: 0.25" in bud,
         f"card_hours of hand-written manifests counted toward their gate ({want:.2f}); gate-less ones listed apart", bud)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "after hand manifests",
                    "--dry-run", "--allow-no-venv", "--", "true"])
    c.ok(r.returncode == 0 and "Traceback" not in r.stderr, "submit works beside hand-written manifests", r.stderr)
    r = run_cmd(A, ["lint"])
    c.ok(r.returncode == 1 and "UNREADABLE" in r.stdout and "not JSON" in r.stdout and "not a JSON object" in r.stdout
         and "'failed (exit 1)' x1" in r.stdout and "'done' x1" in r.stdout,
         "lint lists the unreadable manifests (exit 1) and the status words read with defaults", r.stdout)
    r = run_cmd(A, ["finish", "A-emd-pbh-20261115-112946-b7b431d"])
    c.ok(r.returncode == 1 and "not registered by nrpic-run" in r.stderr, "finish refuses a hand-written run", r.stderr)
    r = run_cmd(A, ["stop", "A-emd-pbh-20261115-042626-f3da881"])
    c.ok(r.returncode == 1 and "not registered by nrpic-run" in r.stderr, "stop refuses a hand-written run", r.stderr)
    od = os.path.join(fx["repo"], "scratch", "A-emd-pbh", "hand1")
    os.makedirs(od, exist_ok=True)
    r = run_cmd(A, ["verify", "A-emd-pbh-20261115-112946-b7b431d"])
    c.ok(r.returncode == 0 and "not re-verifiable" in r.stdout,
         "verify of a hand-written run without sha256sums.txt: PASS with a note", r.stdout + r.stderr)
    open(os.path.join(od, "o.txt"), "w").write("one\n")
    F.sh(["sha256sum", "o.txt"], cwd=od)
    open(os.path.join(od, "sha256sums.txt"), "w").write(F.sh(["sha256sum", "o.txt"], cwd=od).stdout)
    open(os.path.join(od, "o.txt"), "a").write("changed\n")
    r = run_cmd(A, ["verify", "A-emd-pbh-20261115-112946-b7b431d"])
    c.ok(r.returncode == 1 and "changed output o.txt" in r.stdout,
         "verify of a hand-written run with sha256sums.txt still catches a changed output", r.stdout)
    # decision 0014 amends the allotments of 0006 ("To the next gate: ... A 70 ...")
    d14 = os.path.join(fx["repo"], "coord", "DECISIONS", "0014-budgets-after-wave-1.md")
    open(d14, "w").write("# 0014 Card-time allotments after wave 1 (amends 0006)\n\nStatus: PROVISIONAL\n\n"
                         "Use in wave 1: core 3.4, B 0.5. To the next gate: core 40, A 70, B 40, kb 0. Order...\n")
    F.sh(["git", "-C", fx["repo"], "add", "coord/DECISIONS"])
    F.sh(["git", "-C", fx["repo"], "commit", "-q", "-m", "decision 0014"])
    bud = run_cmd(A, ["budget"]).stdout
    c.ok("owner A-emd-pbh: 70 GPU-hours" in bud and "0014-budgets-after-wave-1.md" in bud,
         "an allotment amended by a later decision on main (0014) is the one applied", bud)
    lst = "tracks/A-emd-pbh/inputs/batch.txt"
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G2", "--purpose", "big", "--launcher", "batch",
                    "--list", lst, "--gpu-hours", "9", "--dry-run"])
    c.ok(r.returncode == 0 and "above eight" in r.stderr, "a request above eight card-hours is noted (0014)", r.stderr)


if __name__ == "__main__":
    sys.exit(main())
