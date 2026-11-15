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
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", f"dummy {secs} s run",
                    "--cores", "2", "--", "python3", "-c", prog], env=polluted, timeout=secs + 120)
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
                    "--background", "--", "python3", "-c", "import time; time.sleep(2); print('bg')"])
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
    return c.done()


if __name__ == "__main__":
    sys.exit(main())
