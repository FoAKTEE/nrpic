#!/usr/bin/python3 -I
"""Self-test of harness/bin/nrpic-run in a scratch repository (acceptance test 4 of brief 11.7).

    python3 -I harness/tests/test_nrpic_run.py [--full]     (--full: the dummy run lasts 30 s, not 3 s)

Covers: a dummy local run registered, run, checksummed, committed twice and re-verified; tampered
output detected; a literal '$NRPIC_RUN_DIR' argument replaced by nrpic-run; dirty worktree refused; budget refusals (kb has 0 GPU-hours, A asks more than 60,
cores above 16); production refused without a plan and before the previous gate's pass tag; the
caller's environment ignored; a background run; batch and chain launchers through the repository's
scripts/gpu_batch.sh and scripts/submit_chain.sh with a fake Slurm and a fake athena; GPU-hours
counted across runs; another owner's runs not counted; the wrong worktree's copy refused; decision 0033:
one route (a card submission without the dispatcher's marker, with a forged one, with another owner's,
or with no dispatch in progress is refused and registers nothing; the message gives the `nrpic-queue add`
line; --dry-run stays open) and the cap with the marker (five live fake jobs: refused, nothing
registered; four: accepted; squeue failing: refused). Card submissions of the other sections run inside
rc_fixture.fake_dispatch, as the dispatcher would run them. Decision 0039 item 5: runs continued in place
(`continuations`: C's chain closed, continued from its restart file and closed again by finish without
--status, card-hours summed over its jobs; D's chain with a record while still submitted; malformed lists
refused with what is wrong) and the checksum cache (.nrpic/sha256cache.json: unchanged tree hashed no
more, a touched file alone, a byte changed with size and time kept missed by the cached pass and caught by
--full, a new file hashed by finish; racy entries; four threads at most).
"""
import json
import os
import re
import shlex
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

    # 1b. '$NRPIC_RUN_DIR' and '${NRPIC_RUN_ID}' written literally (single-quoted) in the arguments of a
    # local command: the command runs without a shell, so nrpic-run replaces them (wave 2: five owners
    # got a directory named $NRPIC_RUN_DIR in the worktree root)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "literal run dir", "--allow-no-venv",
                    "--", "python3", "-c", "import sys; open(sys.argv[1] + '/lit.txt', 'w').write(sys.argv[2])",
                    "$NRPIC_RUN_DIR", "${NRPIC_RUN_ID}"])
    lrid = run_id_from(r.stdout)
    lit = os.path.join(fx["repo"], "scratch", "A-emd-pbh", lrid or "none", "lit.txt")
    c.ok(r.returncode == 0 and lrid and os.path.isfile(lit) and open(lit).read() == lrid
         and not os.path.exists(os.path.join(A, "$NRPIC_RUN_DIR"))
         and manifest(A, "A-emd-pbh", lrid)["command"][-2:] == ["$NRPIC_RUN_DIR", "${NRPIC_RUN_ID}"],
         "a literal $NRPIC_RUN_DIR / ${NRPIC_RUN_ID} argument is replaced by nrpic-run (manifest keeps the command "
         "as given); nothing lands in the worktree root", r.stdout + r.stderr)

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
    stray = os.path.join(A, "es.horizon_summary_0.txt")        # wave 2 (D): a finder's summary in the root
    open(stray, "w").write("summary written into the cwd\n")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--allow-no-venv", "--dry-run",
                    "--package", "tracks/A-emd-pbh/pkg", "--", "python3", "tracks/A-emd-pbh/pkg/run.py"])
    dm = json.loads(r.stdout[:r.stdout.rindex("}") + 1]) if r.returncode == 0 else {}
    c.ok(r.returncode == 0 and any("es.horizon_summary_0.txt" in x for x in dm["git"]["outside_package"]["first"]),
         "with --package: an untracked file in the worktree root is recorded, not refused", r.stderr)
    os.remove(stray)
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
    lj = os.path.join(fx["repo"], "scratch", "A-emd-pbh", bg or "none", ".nrpic", "launch.json")
    wait_until(lambda: os.path.isfile(lj) and "pid" in open(lj).read(), 30, 0.2)   # the wrapper has started
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
    with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:     # card runs: only inside a dispatch (0033)
        r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "batch of two",
                        "--launcher", "batch", "--list", "tracks/A-emd-pbh/inputs/batch.txt", "--wall", "00:10:00"],
                    env=denv)
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
    with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
        r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "chain of two segments",
                        "--launcher", "chain", "--gpu-hours", "2", "--", adeck, "time/tlim=1"], env=denv)
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
    # 11. the orchestrator's runs on main, beside other agents
    orch_runs(c, fx, A)
    # 12. --wait: a local run waits for the owner's cores instead of being refused (C's lead-core-share)
    wait_runs(c, fx, A)
    # 13. the cap on queued jobs (decision 0033)
    queue_cap(c, fx, A)
    # 14. runs continued in place by a queue wrapper: the manifest's `continuations` (decision 0039 item 5)
    continued_runs(c, fx, A)
    # 15. the checksum cache of finish and verify (decision 0039 item 5)
    checksum_cache(c, fx, A)
    hasher_unit(c, fx)
    return c.done()


def chain_status(od):
    p = os.path.join(od, "chain", "STATUS")
    return open(p).read().strip() if os.path.isfile(p) else ""


def checksums_line(out):
    """(files, hashed again, taken from the cache) of the `checksums:` / `checksummed` line of nrpic-run."""
    m = re.search(r"(\d+) output files: (\d+) hashed again \(bytes read, [^)]*\), (\d+) taken from the cache", out)
    return tuple(int(x) for x in m.groups()) if m else None


def commit_manifest(A, rid, m, msg):
    p = os.path.join(A, "tracks", "A-emd-pbh", "runs", rid, "manifest.json")
    F.H.write_json(p, m)
    rel = os.path.relpath(p, A)
    F.sh(["git", "-C", A, "add", "-f", "--", rel])
    F.sh(["git", "-C", A, "commit", "-q", "-m", msg, "--", rel])


def continued_runs(c, fx, A):
    """Decision 0039 item 5. C's case: a chain cut by its segment cap, closed as failed, then continued in place
    from its own restart file by a queue wrapper that appends a `continuations` record (as
    tracks/C-sidm/longruns/seq/qitem.sh does) and resumes scripts/submit_chain.sh on the run directory; `finish`
    (no --status) closes it again: completed, every job of the chain, card-hours the sum over the jobs (fake
    sacct), checksums of the unchanged outputs from the cache and the new ones hashed. D's case: a chain still
    submitted whose manifest got a record with a job id (tracks/D-bh-dress/g2long/tools/continue_chain.sh): live
    in `status` (not hand-written), finish closes it. A malformed `continuations` is refused with what is wrong
    and nothing changes. The fake Slurm of the fixture only (checked before the resume)."""
    import shutil
    adeck = "tracks/A-emd-pbh/inputs/chain.athinput"
    scr = os.path.join(fx["repo"], "scratch", "A-emd-pbh")
    wt = F.H.Worktree(A)
    sets = {"ATHENA_EXE": os.path.join(fx["fakebin"], "athena"), "PARTITION": "preempt", "MAX_SEGMENTS": "2",
            "SLURM_TIME": "00:59:00", "ATHENA_WALL": "00:50:00"}
    probe = F.H.build_env(wt, extra=sets)
    sb = shutil.which("sbatch", path=probe["PATH"])
    if not c.ok(sb and os.path.dirname(os.path.realpath(sb)) == os.path.realpath(fx["fakebin"]),
                "continuations: sbatch on the PATH of the fixture's environment is the fake one", str(sb)):
        return
    with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
        r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G2", "--purpose", "chain cut by its segment cap",
                        "--launcher", "chain", "--gpu-hours", "1", "--", adeck], env=denv)
    rid = run_id_from(r.stdout)
    if not c.ok(r.returncode == 0 and rid, "C's case: a chain of one segment submitted", r.stdout + r.stderr):
        return
    od = os.path.join(scr, rid)
    wait_until(lambda: chain_status(od) in ("DONE", "FAILED"), 180)
    time.sleep(2.5)                        # the first close comes a while after the outputs (no racy cache entry)
    wait_until(lambda: run_cmd(A, ["finish", rid]).returncode == 0, 60, 1.0)
    m1 = manifest(A, "A-emd-pbh", rid)
    c.ok(chain_status(od) == "FAILED" and m1["status"] == "failed" and len(m1["slurm"]["job_ids"]) == 1,
         "C's case: the chain stopped FAILED at its cap of one segment and was closed as failed",
         json.dumps(m1.get("slurm")) + chain_status(od))
    rst = sorted(os.listdir(os.path.join(od, "rst")))
    time.sleep(1.1)                        # the record is later than the close
    m1["continuations"] = [{"at": F.H.utcnow(), "by": "tracks/A-emd-pbh/q/qitem.sh A1+ (shared card queue, q9001)",
                            "kind": "in-place resume of a chain cut by its segment cap", "status_before": "failed",
                            "from_restart": os.path.join(od, "rst", rst[-1]), "max_segments": 2,
                            "extra_athena_args": [], "predictions": "JOURNAL.md (fixture)"}]
    commit_manifest(A, rid, m1, f"A(run): continue {rid} in place from its newest restart")
    r = run_cmd(A, ["lint"])
    c.ok(f"{rid}: continued in place at" in r.stdout and "close it again with finish" in r.stdout,
         "lint names a run continued in place after it was closed", r.stdout[-1500:])
    r = F.sh(["scripts/submit_chain.sh", od, os.path.join(A, adeck)], cwd=A,
             env=F.H.build_env(wt, extra=dict(sets, JOB_NAME=rid)), check=False)
    c.ok(r.returncode == 0 and "chain started" in r.stdout, "C's case: submit_chain.sh resumes the chain in place "
         "(fake Slurm, MAX_SEGMENTS 2, JOB_NAME the run id)", r.stdout + r.stderr)
    wait_until(lambda: chain_status(od) == "DONE", 180)
    time.sleep(1.0)
    r = run_cmd(A, ["finish", rid])
    m2 = manifest(A, "A-emd-pbh", rid)
    res = m2["resources"]
    c.ok(r.returncode == 0 and "not registered by nrpic-run" not in r.stderr and "closing it again" in r.stdout
         and m2["status"] == "completed" and m2["exit_code"] == 0 and m2["continuations"] == m1["continuations"],
         "C's case: finish without --status closes the run continued after its close again: completed, the record kept",
         r.stdout + r.stderr)
    truth = {}
    for j in m2["slurm"]["job_ids"]:
        d = os.path.join(fx["state"], j)
        truth[j] = max(1, int(open(os.path.join(d, "end")).read()) - int(open(os.path.join(d, "start")).read()))
    c.ok(len(m2["slurm"]["job_ids"]) == 2 and m2["slurm"]["job_ids"][0] == m1["slurm"]["job_ids"][0]
         and res.get("gpu_seconds_by_job") == {j: float(s) for j, s in truth.items()}
         and abs(res["gpu_hours"] * 3600 - sum(truth.values())) < 1.0 and res["gpu_hours"] > m1["resources"]["gpu_hours"]
         and "1 continuation(s) in place included" in res.get("gpu_hours_basis", "")
         and "sacct ElapsedRaw for 2" in res.get("gpu_hours_basis", ""),
         f"C's case: card-hours are the sum over both jobs of the chain ({res.get('gpu_seconds_by_job')} s from sacct; "
         f"{res['gpu_hours']} h), the basis recorded", json.dumps(res) + json.dumps(truth))
    cs = checksums_line(r.stdout)
    cache = json.load(open(os.path.join(od, ".nrpic", "sha256cache.json")))
    sums = dict(l.split("  ", 1)[::-1] for l in open(os.path.join(od, "sha256sums.txt")).read().splitlines())
    c.ok(cs and cs[2] >= 3 and cs[1] >= 2 and cs[0] == m2["outputs"]["files"]
         and sums.get("out2.txt") == F.H.sha256_file(os.path.join(od, "out2.txt"))
         and cache["entries"]["out2.txt"]["sha256"] == sums["out2.txt"]
         and sums.get("out1.txt") == F.H.sha256_file(os.path.join(od, "out1.txt")),
         f"C's case: the second close hashed the new and changed outputs and took the unchanged ones from the cache "
         f"(files, hashed again, from the cache = {cs})", r.stdout)
    c.ok(run_cmd(A, ["verify", rid]).returncode == 0, "C's case: the continued run verifies after the second close")
    r = run_cmd(A, ["finish", rid])
    c.ok(r.returncode == 0 and "already completed (closed after its last continuation" in r.stdout,
         "finish of a run closed after its last continuation: already closed", r.stdout + r.stderr)

    # D's case: a chain still submitted gets a record (its waiting job was continued by the queue wrapper)
    with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
        r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G2", "--purpose", "chain continued while waiting",
                        "--launcher", "chain", "--gpu-hours", "2", "--", adeck, "time/tlim=1"], env=denv)
    did = run_id_from(r.stdout)
    if not c.ok(r.returncode == 0 and did, "D's case: a chain of two segments submitted", r.stdout + r.stderr):
        return
    dod = os.path.join(scr, did)
    md = manifest(A, "A-emd-pbh", did)
    jid = json.load(open(os.path.join(dod, ".nrpic", "launch.json")))["job_ids"][0]
    md["continuations"] = [{"at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "job_id": jid, "from_restart": None,
                            "segments_used_before": 0, "max_segments": 2,
                            "via": "harness/bin/nrpic-queue --cmd tracks/A-emd-pbh/q/continue_chain.sh",
                            "reason": "continued in place after its waiting job was cancelled under the queue cap"}]
    commit_manifest(A, did, md, f"Run {did}: chain continued in place by the shared queue (job {jid})")
    st = run_cmd(A, ["status"]).stdout
    line = next((l for l in st.splitlines() if l.startswith(did)), "")
    word = line.split()[4] if len(line.split()) > 4 else ""
    c.ok(word in ("submitted*", "submitted?"),
         "D's case: a manifest with `continuations` is read as nrpic-run's (no h mark), its chain checked for life", line)
    mp = os.path.join(A, "tracks", "A-emd-pbh", "runs", did, "manifest.json")
    good = open(mp).read()
    for what, value, key in (
            ("a record without `at` and without who", [{"job_id": jid, "from_restart": None}], "record [0] has no `at`"),
            ("an object instead of a list", {"at": "2026-11-25T01:53:05-0800"}, "must be a list of records"),
            ("a time without a zone", [dict(md["continuations"][0], at="2026-11-25 01:53")], "is not an ISO 8601 time")):
        bad = dict(md, continuations=value)
        F.H.write_json(mp, bad)
        before = open(mp).read()
        r = run_cmd(A, ["finish", did, "--status", "stopped"])
        c.ok(r.returncode == 1 and "`continuations` is malformed, nothing was changed" in r.stderr and key in r.stderr
             and open(mp).read() == before, f"finish refuses a malformed `continuations` ({what}) and says what is wrong",
             r.stderr)
    r = run_cmd(A, ["verify", did])
    c.ok(r.returncode == 1 and "continuations: record [0]" in r.stdout, "verify fails a malformed `continuations`",
         r.stdout)
    open(mp, "w").write(good)
    wait_until(lambda: chain_status(dod) in ("DONE", "FAILED"), 180)
    r = run_cmd(A, ["finish", did])
    m3 = manifest(A, "A-emd-pbh", did)
    c.ok(r.returncode == 0 and m3["status"] == "completed" and jid in m3["slurm"]["job_ids"]
         and len(m3["slurm"]["job_ids"]) == 2 and m3["continuations"] == md["continuations"]
         and F.sh(["git", "-C", A, "status", "--porcelain"]).stdout.strip() == "",
         "D's case: finish closes the chain with its continuation record (completed, both jobs); the tree stays clean",
         r.stdout + r.stderr)
    r = run_cmd(A, ["finish", "--status", "stopped"])
    c.ok(r.returncode == 1 and "usage" in r.stderr, "finish without a run id first: usage", r.stderr)
    r = run_cmd(A, ["finish", did, "--fulll"])
    c.ok(r.returncode == 1 and "unknown argument" in r.stderr, "finish refuses an unknown option (no silent cached pass)",
         r.stderr)


def checksum_cache(c, fx, A):
    """Decision 0039 item 5: nrpic-run verify (and finish) hash through <run dir>/.nrpic/sha256cache.json. The
    outputs are aged by an hour (a run that ended a while ago). Second verify: nothing hashed again; a touched file
    (same bytes, new time): that file only, PASS; a byte changed with size kept and time restored: NOT detected
    by the cached pass (the documented limit), detected by --full, and then by the cached pass too; a new file:
    `output not in sha256sums.txt`, and finish hashes it (the others from the cache)."""
    prog = ("import os; d = os.environ['NRPIC_RUN_DIR']; os.makedirs(d + '/sub'); "
            "open(d + '/a.bin', 'wb').write(os.urandom(1 << 20)); open(d + '/b.txt', 'w').write('bee\\n'); "
            "open(d + '/sub/c.txt', 'w').write('sea\\n')")
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "outputs for the checksum cache",
                    "--allow-no-venv", "--", "python3", "-c", prog])
    rid = run_id_from(r.stdout)
    if not c.ok(r.returncode == 0 and rid, "cache: a local run with four outputs (a.bin, b.txt, sub/c.txt, run.log)",
                r.stdout + r.stderr):
        return
    od = os.path.join(fx["repo"], "scratch", "A-emd-pbh", rid)
    c.ok(os.path.isfile(os.path.join(od, ".nrpic", "sha256cache.json")) and checksums_line(r.stdout) == (4, 4, 0),
         "cache: finish hashed the four outputs and wrote .nrpic/sha256cache.json (not itself checksummed)", r.stdout)
    old = time.time_ns() - 3600 * 10 ** 9
    for rel in ("a.bin", "b.txt", "sub/c.txt", "run.log"):
        os.utime(os.path.join(od, rel), ns=(old, old))

    def verify(*extra):
        rr = run_cmd(A, ["verify", rid] + list(extra))
        return rr, checksums_line(rr.stdout)
    r, cs = verify()
    c.ok(r.returncode == 0 and cs == (4, 4, 0), f"cache: first verify after the times changed hashes all four {cs}",
         r.stdout)
    r, cs = verify()
    c.ok(r.returncode == 0 and cs == (4, 0, 4) and F.H.CACHE_SENTENCE in r.stdout,
         f"cache: a second verify of an unchanged tree hashes nothing again and says what a cached entry proves {cs}",
         r.stdout)
    os.utime(os.path.join(od, "b.txt"), ns=(old + 60 * 10 ** 9, old + 60 * 10 ** 9))
    r, cs = verify()
    c.ok(r.returncode == 0 and cs == (4, 1, 3), f"cache: a touched file (same bytes, new time) is hashed again, "
         f"alone, and passes {cs}", r.stdout)
    p = os.path.join(od, "a.bin")
    st = os.stat(p)
    with open(p, "r+b") as f:
        b = f.read(1)
        f.seek(0)
        f.write(bytes([b[0] ^ 0xFF]))
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
    r, cs = verify()
    c.ok(r.returncode == 0 and cs == (4, 0, 4) and os.path.getsize(p) == st.st_size,
         "cache, the documented limit: a byte changed with the size kept and the time restored is NOT detected by the "
         "cached pass", r.stdout)
    r, cs = verify("--full")
    c.ok(r.returncode == 1 and "changed output a.bin" in r.stdout and cs == (4, 4, 0) and "(--full)" in r.stdout,
         "cache: --full reads every byte and detects that change", r.stdout)
    r, cs = verify()
    c.ok(r.returncode == 1 and "changed output a.bin" in r.stdout and cs == (4, 0, 4),
         "cache: after --full the cache holds the new checksum: the cached pass fails too (a differing checksum is a "
         "failure as before)", r.stdout)
    open(os.path.join(od, "d.txt"), "w").write("new\n")
    r, cs = verify()
    c.ok(r.returncode == 1 and "output not in sha256sums.txt: d.txt" in r.stdout, "cache: a new file is reported by verify",
         r.stdout)
    r = run_cmd(A, ["finish", rid, "--status", "completed"])
    sums = dict(l.split("  ", 1)[::-1] for l in open(os.path.join(od, "sha256sums.txt")).read().splitlines())
    c.ok(r.returncode == 0 and checksums_line(r.stdout) == (5, 1, 4)
         and sums.get("d.txt") == F.H.sha256_file(os.path.join(od, "d.txt")),
         "cache: finish again hashes the new file and takes the other four from the cache", r.stdout)
    r = run_cmd(A, ["verify", rid, "--full"])
    c.ok(r.returncode == 0 and checksums_line(r.stdout) == (5, 5, 0), "cache: verify --full of the new record passes",
         r.stdout)
    r = run_cmd(A, ["verify", rid, "--fast"])
    c.ok(r.returncode == 1 and "usage" in r.stderr, "verify refuses an unknown option", r.stderr)


def hasher_unit(c, fx):
    """H.OutputHasher in process: a file hashed less than RACY_NS after its last change is hashed again at the next
    pass; at most HASH_THREADS (four) files are hashed at once."""
    import threading
    H = F.H
    d = os.path.join(fx["root"], "hashunit")
    os.makedirs(d)
    rels = [f"f{i:02d}.dat" for i in range(12)]
    for i, rel in enumerate(rels):
        open(os.path.join(d, rel), "wb").write(bytes([i]) * (4096 + i))
    h1 = H.OutputHasher(d)
    got = h1.digests(rels)
    h1.save()
    h2 = H.OutputHasher(d)
    h2.digests(rels)
    c.ok(len(got) == 12 and h1.stats["rehashed"] == 12 and h2.stats["rehashed"] == 12,
         "hasher: files changed less than 2 s before they were hashed (racy entries) are hashed again at the next pass",
         json.dumps(h2.stats))
    old = time.time_ns() - 600 * 10 ** 9
    for rel in rels:
        os.utime(os.path.join(d, rel), ns=(old, old))
    h3 = H.OutputHasher(d)
    h3.digests(rels)
    h3.save()
    h4 = H.OutputHasher(d)
    got4 = h4.digests(rels)
    c.ok(h3.stats["rehashed"] == 12 and h4.stats["rehashed"] == 0 and h4.stats["cached"] == 12 and got4 == got,
         "hasher: aged files are taken from the cache with the same checksums", json.dumps(h4.stats))
    orig, lock, state = H.sha256_file, threading.Lock(), {"now": 0, "peak": 0}

    def slow(path, bufsize=1 << 22):
        with lock:
            state["now"] += 1
            state["peak"] = max(state["peak"], state["now"])
        time.sleep(0.1)
        try:
            return orig(path, bufsize)
        finally:
            with lock:
                state["now"] -= 1
    H.sha256_file = slow
    try:
        h5 = H.OutputHasher(d, full=True)
        got5 = h5.digests(rels)
    finally:
        H.sha256_file = orig
    c.ok(H.HASH_THREADS == 4 and state["peak"] == 4 and got5 == got and h5.stats["rehashed"] == 12,
         f"hasher: --full hashes every file, at most four at once (peak {state['peak']})", json.dumps(state))
    bad = os.path.join(d, ".nrpic", "sha256cache.json")
    open(bad, "w").write("{broken")
    h6 = H.OutputHasher(d)
    h6.digests(rels)
    c.ok(h6.stats["rehashed"] == 12 and any("unreadable" in n for n in h6.stats["notes"]),
         "hasher: an unreadable cache is ignored with a note, every file hashed", json.dumps(h6.stats["notes"]))


HOLD = r'''#!/bin/bash
# fake card job of the cap test: runs until the test writes @REL@/<name> (at most ten minutes)
for ((i = 0; i < 3000; i++)); do [[ -e "@REL@/$1" ]] && exit 0; sleep 0.2; done
'''


def queue_cap(c, fx, A):
    """Decision 0033. One route: a card submission without the dispatcher's marker is refused and registers
    nothing (also with a forged marker, or with no dispatch in progress), and the message gives the
    `nrpic-queue add` line; outside a dispatch a local run or `nrpic-env exec` meets the stubs of
    harness/shims/slurm on its PATH, so the forms of the second review (C1) submit no job and those that only
    mention Slurm (L1) run, and sbatch as the first word is refused before anything is registered; inside a
    dispatch the local run reaches sbatch and nothing of the stubs reaches the job's PATH; with the marker, the cap still holds: five live jobs of the account (held by the
    test) refuse a card run, four accept it, a failing squeue refuses it. The fake jobs and their release
    files live outside the worktree, which stays clean."""
    rel = os.path.join(fx["root"], "release-cap")
    os.makedirs(rel, exist_ok=True)
    hold = os.path.join(fx["root"], "hold-cap.sh")
    F.write_exe(hold, HOLD.replace("@REL@", rel))
    env = F.H.build_env(F.H.Worktree(A))
    names = [f"cap{i}" for i in range(5)]
    sq = os.path.join(fx["fakebin"], "squeue")
    orig = open(sq).read()
    runs = os.path.join(A, "tracks", "A-emd-pbh", "runs")
    scr = os.path.join(fx["repo"], "scratch", "A-emd-pbh")

    def snap():
        return (sorted(os.listdir(runs)), sorted(os.listdir(scr)), F.sh(["git", "-C", A, "rev-parse", "HEAD"]).stdout,
                F.sh(["git", "-C", A, "status", "--porcelain"]).stdout)
    args = ["submit", "--kind", "scouting", "--gate", "G3", "--purpose", "one job too many", "--launcher", "batch",
            "--list", "tracks/A-emd-pbh/inputs/batch.txt", "--wall", "00:10:00"]
    want = "  harness/bin/nrpic-queue add --label <label> -- " + shlex.join(args[1:])
    local = ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "a local run that reaches sbatch"]
    q = "tracks/A-emd-pbh/q"
    pathjob = os.path.join(fx["root"], "pathjob-cap.sh")
    F.write_exe(pathjob, "#!/bin/bash\necho \"$PATH\" > \"@REL@/path-$1\"\n".replace("@REL@", rel)
                + HOLD.replace("@REL@", rel).split("\n", 1)[1])
    scripts = {   # the forms of the second review (C1: reach sbatch; L1: submit nothing)
        f"{q}/s.sh": f"#!/bin/bash\nn=${{1:-s}}\nsbatch -J $n {hold} $n\n",
        f"{q}/outer.sh": f"#!/bin/bash\n# drives one submission\nbash {q}/s.sh \"$1\"\n",
        f"{q}/fs.py": ("import subprocess, sys\nd = '.'\nn = sys.argv[1]\n"
                       f"subprocess.run(['bash', '-c', f'cd {{d}} && sbatch -J {{n}} {hold} {{n}}'])\n"),
        f"{q}/plain.py": f"import subprocess, sys\nn = sys.argv[1]\nsubprocess.run(['sbatch', '-J', n, '{hold}', n])\n",
        f"{q}/status.py": ("import subprocess, sys\n# asks the chain helper for the state of a run\n"
                           "subprocess.run(['scripts/submit_chain.sh', '--status', sys.argv[1]], check=True)\n"),
        f"{q}/parse.py": ("import sys\n# counts srun steps in a log\n"
                          "print(sum(1 for ln in open(sys.argv[1]) if ln.startswith(\"srun\")))\n"),
        f"{q}/note.sh": "#!/bin/bash\necho 'this analysis never calls sbatch'\nwc -l \"$1\"\n",
    }
    for rel_, text in scripts.items():                     # run through bash or python3: no mode bit needed
        F.commit_file(A, rel_, text, "the review's forms")
    names += [f"d{i}" for i in range(1, 8)] + ["lm1"]
    ne = os.path.join(A, "harness", "bin", "nrpic-env")
    try:
        for n in names[:5]:
            F.sh(["sbatch", "-J", n, hold, n], env=env)
        c.ok(wait_until(lambda: F.H.queue_count(env) == 5, 30), "queue cap: five live fake jobs of the account",
             str(F.H.queue_count(env)))
        before = snap()
        r = run_cmd(A, args)
        c.ok(r.returncode == 1 and "card runs are submitted only by the shared queue" in r.stderr
             and want in r.stderr.splitlines() and snap() == before,
             "one route: a direct card submission (no dispatcher's marker) is refused, registers nothing (no "
             "manifest, no output directory, no commit), and the message gives the exact `nrpic-queue add` line",
             r.stdout + r.stderr)
        # second review, C1: outside a dispatch sbatch on the command's PATH is a stub, whatever the form
        for what, cmd, key in (("timeout 60 bash s.sh", ["timeout", "60", "bash", f"{q}/s.sh", "d1"], "d1"),
                               ("env bash s.sh", ["env", "bash", f"{q}/s.sh", "d2"], "d2"),
                               ("bash outer.sh (a script that runs s.sh)", ["bash", f"{q}/outer.sh", "d3"], "d3"),
                               ("python3 fs.py (an f-string `cd {d} && sbatch ...`)", ["python3", f"{q}/fs.py", "d4"],
                                "d4"),
                               ("python3 -W ignore plain.py", ["python3", "-W", "ignore", f"{q}/plain.py", "d5"], "d5")):
            r = run_cmd(A, local + ["--allow-no-venv", "--"] + cmd)
            rid = run_id_from(r.stdout)
            lg = os.path.join(scr, rid or "none", "run.log")
            time.sleep(0.5)
            c.ok(F.H.queue_count(env) == 5 and os.path.isfile(lg) and "refused: card jobs reach Slurm only" in open(lg).read(),
                 f"review 2, C1: a local run of `{what}` outside a dispatch submits no job (the sbatch it reaches is the "
                 "stub, which refuses); five jobs still", r.stdout[-400:] + r.stderr[-400:])
        for what, cmd in (("timeout 60 bash s.sh", ["timeout", "60", "bash", f"{q}/s.sh", "d6"]),
                          ("/usr/bin/env bash outer.sh", ["/usr/bin/env", "bash", f"{q}/outer.sh", "d7"])):
            r = F.sh([ne, "exec", "--"] + cmd, cwd=A, check=False)
            time.sleep(0.5)
            c.ok(r.returncode != 0 and "refused: card jobs reach Slurm only" in r.stderr and F.H.queue_count(env) == 5,
                 f"review 2, C1: `nrpic-env exec -- {what}` submits no job either", r.stderr[-400:])
        for what, cmd in (("nrpic-run submit -- sbatch ...", None), ("nrpic-env exec -- sbatch ...", True)):
            before = snap()
            r = (F.sh([ne, "exec", "--", "sbatch", "-J", "byp", hold, "byp"], cwd=A, check=False) if cmd else
                 run_cmd(A, local + ["--", "sbatch", "-J", "byp", hold, "byp"]))
            c.ok(r.returncode == 1 and ("may not submit Slurm jobs" in r.stderr or "submits Slurm jobs" in r.stderr)
                 and snap() == before and F.H.queue_count(env) == 5,
                 f"`{what}` (sbatch as the first word) is refused before anything runs or is registered", r.stderr)
        # second review, L1: commands that only mention Slurm run
        rd = os.path.join(fx["repo"], "scratch", "A-emd-pbh", "nochain")
        os.makedirs(rd, exist_ok=True)
        for what, cmd in (("python3 status.py (`submit_chain.sh --status` in a list)", ["python3", f"{q}/status.py", rd]),
                          ("grep -c sbatch scripts/gpu_batch.sh", ["grep", "-c", "sbatch", "scripts/gpu_batch.sh"]),
                          ("python3 parse.py (a string beginning with srun)", ["python3", f"{q}/parse.py", "CLAUDE.md"]),
                          ("bash note.sh (an echo text naming sbatch)", ["bash", f"{q}/note.sh", "CLAUDE.md"]),
                          ("scripts/submit_chain.sh --status", ["scripts/submit_chain.sh", "--status", rd])):
            r = F.sh([ne, "exec", "--"] + cmd, cwd=A, check=False)
            c.ok(r.returncode == 0 and "refused" not in r.stderr, f"review 2, L1: `nrpic-env exec -- {what}` runs",
                 r.stdout[-300:] + r.stderr[-300:])
        r = run_cmd(A, local + ["--", "bash", "-c", "echo PATH=$PATH"])
        rid = run_id_from(r.stdout)
        lg = os.path.join(scr, rid or "none", "run.log")
        txt = open(lg).read() if os.path.isfile(lg) else ""
        c.ok(re.search(r"^PATH=\S*/harness/shims/slurm:", txt, re.M), "outside a dispatch a local run's PATH begins "
             "with harness/shims/slurm", txt[-400:])
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
            before = snap()
            r = run_cmd(A, args, env=denv)
        c.ok(r.returncode == 1 and "queue cap: 5 jobs of this account are queued or running" in r.stderr
             and "decision 0033" in r.stderr and snap() == before,
             "queue cap: with the marker and five jobs queued the card submission is refused (the marker does not "
             "lift the cap); nothing registered", r.stdout + r.stderr)
        open(os.path.join(rel, names[0]), "w").close()
        c.ok(wait_until(lambda: F.H.queue_count(env) == 4, 30), "queue cap: one job ended, four left")
        before = snap()
        r = run_cmd(A, args)
        c.ok(r.returncode == 1 and "card runs are submitted only by the shared queue" in r.stderr and snap() == before,
             "one route: with four jobs queued a direct card submission is still refused", r.stderr)
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh", token="0" * 24) as denv:
            r = run_cmd(A, args, env=denv)
        c.ok(r.returncode == 1 and "not being dispatched with this marker" in r.stderr and snap() == before,
             "one route: a forged marker (another token) is refused; nothing registered", r.stderr)
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh", hold_lock=False) as denv:
            r = run_cmd(A, args, env=denv)
        c.ok(r.returncode == 1 and "no dispatch is in progress" in r.stderr and snap() == before,
             "one route: a marker while no dispatch is in progress (the submit lock free) is refused", r.stderr)
        with F.fake_dispatch(fx["repo"], fx["wt"]["B-emd-gw"], "B-emd-gw") as denv:
            r = run_cmd(A, args, env=denv)
        c.ok(r.returncode == 1 and "belongs to B-emd-gw" in r.stderr and snap() == before,
             "one route: the marker of another owner's entry is refused", r.stderr)
        r = run_cmd(A, args[:1] + ["--dry-run"] + args[1:])
        c.ok(r.returncode == 0 and "dry run" in r.stdout, "one route: --dry-run of a card run stays open without a marker",
             r.stderr)
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
            r = run_cmd(A, args, env=denv)
        rid = run_id_from(r.stdout)
        c.ok(r.returncode == 0 and rid and "Slurm job" in r.stdout
             and os.path.isfile(os.path.join(runs, rid, "manifest.json")),
             "queue cap: with the marker and four jobs queued the card submission is accepted", r.stdout + r.stderr)
        lj = os.path.join(scr, rid or "none", ".nrpic", "launch.json")
        c.ok(os.path.isfile(lj) and F.H.QUEUE_DISPATCH_VAR not in open(lj).read(),
             "one route: the marker is not passed on into the job's settings", lj)
        if rid:
            wait_until(lambda: run_cmd(A, ["finish", rid]).returncode == 0, 120, 1.0)
        wait_until(lambda: F.H.queue_count(env) == 4, 60)
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
            r = run_cmd(A, local + ["--", "bash", "-c", f"sbatch -J lm1 {pathjob} lm1"], env=denv)
        pf = os.path.join(rel, "path-lm1")
        c.ok(r.returncode == 0 and wait_until(lambda: F.H.queue_count(env) == 5, 10),
             "inside a dispatch (the marker valid) a local run that submits a job goes through (a --cmd wrapper's way)",
             r.stdout[-400:] + r.stderr)
        c.ok(wait_until(lambda: os.path.isfile(pf) and open(pf).read().strip(), 10) and "harness/shims" not in open(pf).read(),
             "inside a dispatch nothing of the stubs reaches the job: its PATH has no harness/shims", open(pf).read()
             if os.path.isfile(pf) else "no PATH file")
        open(os.path.join(rel, "lm1"), "w").close()
        wait_until(lambda: F.H.queue_count(env) == 4, 30)
        names.append("lb1")
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
            r = run_cmd(A, local + ["--background", "--", "bash", "-c", f"sleep 1; sbatch -J lb1 {hold} lb1"], env=denv)
        brid = run_id_from(r.stdout)
        res = os.path.join(scr, brid or "none", ".nrpic", "result.json")
        ok = wait_until(lambda: os.path.isfile(res), 60)
        lg = os.path.join(scr, brid or "none", "run.log")
        c.ok(ok and "refused: card jobs reach Slurm only" in open(lg).read() and F.H.queue_count(env) == 4,
             "second review L3: a --background local run started inside a dispatch still gets the stubs (it outlives "
             "the dispatch and its process group): no job", (open(lg).read() if os.path.isfile(lg) else "")[-400:])
        if brid:
            run_cmd(A, ["finish", brid])
        open(sq, "w").write("#!/bin/bash\necho 'squeue: error: Unable to contact slurm controller' >&2\nexit 1\n")
        before = snap()
        with F.fake_dispatch(fx["repo"], A, "A-emd-pbh") as denv:
            r = run_cmd(A, args, env=denv)
        c.ok(r.returncode == 1 and "squeue did not answer" in r.stderr and snap() == before,
             "queue cap: with the marker, when squeue fails the card submission is refused; nothing registered",
             r.stdout + r.stderr)
    finally:
        open(sq, "w").write(orig)
        for n in names:
            open(os.path.join(rel, n), "w").close()
        wait_until(lambda: F.H.queue_count(env) == 0, 60)


def wait_runs(c, fx, A):
    import re
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "holds 15 of 16 cores",
                    "--cores", "15", "--background", "--", "bash", "-c", "sleep 8"])
    m = re.search(r"registered (A-\d{8}-\d{6}-[0-9a-f]{7})", r.stdout)
    if not c.ok(r.returncode == 0 and m, "--wait: a background run holding 15 of A's 16 cores", r.stdout + r.stderr):
        return
    bg = m.group(1)
    li = os.path.join(fx["repo"], "scratch", "A-emd-pbh", bg, ".nrpic", "launch.json")
    wait_until(lambda: os.path.isfile(li) and "pid" in json.load(open(li)), timeout=60)
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--cores", "2", "--dry-run",
                    "--", "bash", "-c", "true"])
    c.ok(r.returncode == 1 and "allotment 16" in r.stderr and "--wait SECONDS" in r.stderr,
         "--wait: without it, 2 more cores are refused and the message names --wait", r.stderr)
    t0 = time.time()
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "the lead's analysis, waits",
                    "--cores", "2", "--wait", "120", "--", "bash", "-c", "echo after the wait"], timeout=300)
    dt = time.time() - t0
    m2 = re.search(r"registered (A-\d{8}-\d{6}-[0-9a-f]{7})", r.stdout)
    c.ok(r.returncode == 0 and m2 and "waiting for cores" in r.stderr and "after the wait" in r.stdout and dt >= 25,
         f"--wait 120: the run waited ({dt:.0f} s) until the background run ended, then ran", r.stdout + r.stderr)
    bm = manifest(A, "A-emd-pbh", bg)
    if bm["status"] != "completed":
        run_cmd(A, ["finish", bg])
    r = run_cmd(A, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--launcher", "chain",
                    "--gpu-hours", "1", "--wait", "10", "--dry-run", "--", "x.athinput"])
    c.ok(r.returncode == 1 and "--wait SECONDS is for local runs" in r.stderr, "--wait is refused for card launchers",
         r.stderr)


def orch_runs(c, fx, A):
    """Owner orch registers from the main checkout: manifest in tracks/orch/runs/ on main, committed
    path-limited while another agent holds index.lock, has a file staged and others modified."""
    import re
    import subprocess
    repo = fx["repo"]
    g = ["git", "-C", repo]
    F.commit_file(repo, "tracks/orch/outbox/.gitkeep", "", "orch: outbox")
    F.commit_file(repo, "tracks/orch/inputs/o.athinput", "<problem>\npgen_name = fake\n", "orch: a deck")
    # another agent at work on main: a tracked document modified, a draft untracked, a file staged
    with open(os.path.join(repo, "coord", "CHARTER.md"), "a") as f:
        f.write("\nanother agent's edit in progress\n")
    os.makedirs(os.path.join(repo, "coord", "digests"), exist_ok=True)
    open(os.path.join(repo, "coord", "digests", "draft.md"), "w").write("draft\n")
    open(os.path.join(repo, "coord", "STAGED.md"), "w").write("staged by another agent\n")
    F.sh(g + ["add", "--", "coord/STAGED.md"])
    lock = os.path.join(repo, ".git", "index.lock")
    open(lock, "w").close()
    t0 = time.time()
    p = subprocess.Popen([os.path.join(repo, "harness", "bin", "nrpic-run"), "submit", "--kind", "scouting",
                          "--gate", "G1", "--purpose", "orchestrator's analysis beside other agents", "--",
                          "bash", "-c", "echo orch > \"$NRPIC_RUN_DIR/o.txt\""],
                         cwd=repo, env=F.H.boot_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(7)
    held = p.poll() is None
    os.remove(lock)
    out, err = p.communicate(timeout=300)
    m = re.search(r"registered (orch-\d{8}-\d{6}-[0-9a-f]{7})", out)
    rid = m.group(1) if m else None
    c.ok(p.returncode == 0 and rid and held and time.time() - t0 >= 7,
         "orch: a run registered from the main checkout waits while another writer holds index.lock, then commits",
         out + err)
    if not rid:
        return
    shown = F.sh(g + ["show", f"main:tracks/orch/runs/{rid}/manifest.json"], check=False)
    om = json.loads(shown.stdout) if shown.returncode == 0 else {}
    c.ok(om.get("status") == "completed" and om.get("track") == "orch" and om["outputs"]["dir"] == f"scratch/orch/{rid}"
         and open(os.path.join(repo, "scratch", "orch", rid, "o.txt")).read() == "orch\n",
         "orch: manifest tracks/orch/runs/<run_id>/ committed on main (finished), output in scratch/orch/<run_id>/",
         shown.stdout[-600:] + shown.stderr)
    names = F.sh(g + ["log", "-2", "--format=%s", "--name-only"]).stdout
    files = {l for l in names.splitlines() if "/" in l}
    c.ok(files == {f"tracks/orch/runs/{rid}/manifest.json"} and f"orch(run): register {rid}" in names
         and f"orch(run): finish {rid} (completed)" in names,
         "orch: the two commits hold the manifest only (path-limited)", names)
    staged = F.sh(g + ["diff", "--cached", "--name-only"]).stdout.split()
    st = F.sh(g + ["status", "--porcelain"]).stdout
    c.ok(staged == ["coord/STAGED.md"] and " M coord/CHARTER.md" in st and "?? coord/digests/" in st,
         "orch: the other agent's staged, modified and untracked files are left as they were", st)
    c.ok(om["git"].get("outside_package", {}).get("count", 0) >= 3 and om["git"].get("package") == [],
         "orch: the other agent's files are recorded in manifest.git.outside_package, not refused",
         json.dumps(om.get("git")))
    with open(os.path.join(repo, "harness", "templates", "STATUS.md"), "a") as f:
        f.write("\nan unfinished edit of the harness\n")
    r = run_cmd(repo, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--dry-run", "--",
                       "bash", "-c", "true"])
    c.ok(r.returncode == 1 and "harness/templates/STATUS.md" in r.stderr and "code roots" in r.stderr,
         "orch: a change in a code root (harness/) is refused", r.stderr)
    F.sh(g + ["checkout", "-q", "--", "harness/templates/STATUS.md"])
    r = run_cmd(repo, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "card", "--launcher", "chain",
                       "--gpu-hours", "1", "--dry-run", "--", "tracks/orch/inputs/o.athinput"])
    c.ok(r.returncode == 1 and "beyond the allotment" in r.stderr and "0019" in r.stderr,
         "orch: no card-hours without a row in decision 0006 (card run refused)", r.stderr)
    r = run_cmd(repo, ["submit", "--kind", "scouting", "--gate", "G1", "--purpose", "x", "--cores", "7", "--dry-run",
                       "--", "bash", "-c", "true"])
    c.ok(r.returncode == 1 and "allotment 6" in r.stderr, "orch: seven cores refused (six per session, 0019)", r.stderr)
    bud = run_cmd(repo, ["budget"]).stdout
    c.ok("owner orch: 0 GPU-hours" in bud and "6 cores" in bud, "orch: budget prints the default allotment", bud)
    r = run_cmd(A, ["lint", "--all"])
    c.ok("orch: 1 runs (1 by nrpic-run" in r.stdout, "lint --all lists the orchestrator's runs, read from main", r.stdout)
    r = run_cmd(repo, ["verify", rid])
    c.ok(r.returncode == 0 and "PASS" in r.stdout, "orch: verify re-checks the run's checksums", r.stdout + r.stderr)


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
    # D, wave 2: a helper's registration script copied the nrpic-run schema (hand_marker: registered_by)
    "A-20261115-120001-abcdef3": {"schema": "nrpic-run-manifest/1", "run_id": "A-20261115-120001-abcdef3",
                                  "track": "A-emd-pbh", "gate": "G1", "status": "submitted", "launcher": "batch",
                                  "registered_by": "hand: helper script", "resources": {"gpu_hours_requested": 5.0},
                                  "outputs": {"dir": "scratch/A-emd-pbh/A-20261115-120001-abcdef3"}},
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
    r = run_cmd(A, ["finish", "A-20261115-120001-abcdef3"])
    r2 = run_cmd(A, ["stop", "A-20261115-120001-abcdef3"])
    st = run_cmd(A, ["status"]).stdout
    c.ok(r.returncode == 1 and "registered_by" in r.stderr and r2.returncode == 1 and "not registered by nrpic-run"
         in r2.stderr and "submitted?h" in st and "submitted*h" not in st,
         "a hand registration that copied the schema: finish and stop refuse it, status marks it h and never live",
         r.stderr + r2.stderr + st[-800:])
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
