#!/usr/bin/env python3
"""Close a chain run whose manifest nrpic-run calls hand-written (it carries `continuations`,
written by g2long/tools/continue_chain.sh when the shared queue continued the chain in place).

`nrpic-run finish` refuses such manifests ("close this one by hand (status, exit_code, ended,
outputs) and commit it"). This tool runs the SAME code path as nrpic-run's finish for the chain
launcher (its own functions, loaded from harness/bin/nrpic-run): chain STATUS -> status and exit
code, segment logs -> wall time, sacct -> card-hours, sha256sums.txt over the output directory.
It writes the manifest and does NOT commit: the lead commits it path-limited.

usage: python3 close_by_hand.py <worktree root> <run_id>
"""
import importlib.machinery
import importlib.util
import os
import sys


def load_nrpic_run(root):
    path = os.path.join(root, "harness", "bin", "nrpic-run")
    loader = importlib.machinery.SourceFileLoader("nrpic_run_mod", path)
    spec = importlib.util.spec_from_loader("nrpic_run_mod", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def main(root, run_id):
    R = load_nrpic_run(root)
    H = R.H
    wt = H.worktree_from_args(os.path.join(root, "harness", "bin", "nrpic-run"), None)
    mpath = R.manifest_path(wt, run_id)
    m = H.read_json(mpath)
    if m.get("status") in R.FINAL:
        print(f"{run_id} is already {m['status']}")
        return 0
    if m.get("launcher") != "chain":
        raise SystemExit("only chain runs are closed by this tool")
    outdir = os.path.join(wt.home, m["outputs"]["dir"])
    env = H.build_env(wt)
    info = R.launch_info(outdir)
    ids = list(info.get("job_ids", []))
    for j in R.chain_job_ids(outdir):
        if j not in ids:
            ids.append(j)
    live = R.slurm_active(env, ids)
    if live:
        raise SystemExit(f"{run_id}: Slurm job(s) still active: {live}")
    st = open(os.path.join(outdir, "chain", "STATUS")).read().strip()
    if st not in ("DONE", "FAILED", "STOPPED"):
        raise SystemExit(f"{run_id}: chain status is {st}")
    status = {"DONE": "completed", "FAILED": "failed", "STOPPED": "stopped"}[st]
    rc = 0 if st == "DONE" else 1
    cdir = os.path.join(outdir, "chain")
    import re
    logs = sorted(os.path.join(cdir, f) for f in os.listdir(cdir) if re.fullmatch(r"seg\d+\.job.*\.log", f))
    wall, started, ended = R.segment_wall(logs)
    el = R.sacct_elapsed(env, ids)
    gpu_h = (el if el is not None else wall) / 3600.0
    m["slurm"]["job_ids"] = ids
    sums_sha, nbytes, nfiles = R.sha256sums(outdir)
    m["status"] = status
    m["exit_code"] = rc
    m["started"] = started or m.get("started") or info.get("submitted")
    m["ended"] = ended or H.utcnow()
    m["resources"]["walltime_s"] = round(wall, 3) if wall is not None else None
    m["resources"]["gpu_hours"] = round(gpu_h or 0.0, 4)
    m["outputs"].update({"sha256sums_sha256": sums_sha, "bytes": nbytes, "files": nfiles})
    m["finished"] = H.utcnow()
    note = ("closed by hand with tracks/D-bh-dress/g2long/tools/close_by_hand.py (the code path of "
            "nrpic-run finish for chains), because nrpic-run refuses manifests with continuations")
    m["notes"] = (m.get("notes") or "") + ("; " if m.get("notes") else "") + note
    H.write_json(mpath, m)
    print(f"closed {run_id}: {status} (exit {rc}); wall {m['resources']['walltime_s']} s; "
          f"card-hours {m['resources']['gpu_hours']}; {nfiles} files, {nbytes} bytes; "
          f"jobs {','.join(ids)}; manifest written (not committed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
