#!/usr/bin/env python3
"""Prepare the three card tests (O, F, L) and submit them as one Slurm job on one A100
through scripts/gpu_batch.sh (runs one after another; a failed run does not stop the
others). Prints the run ids. Card time of the job is recorded by the judges from the
athena logs (header start, footer end).

    python3 submit_gpu.py [--tests O F L] [--time 00:30:00]
"""
import argparse
import datetime as dt
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

MODS = {"O": "os/run.py", "F": "flrw/run.py", "L": "growth/run.py",
        "Lnewtonian": "growth/run.py", "Lcopy": "growth/run.py"}
VARIANT = {"L": "number", "Lnewtonian": "newtonian", "Lcopy": "copy"}


def load(rel):
    spec = importlib.util.spec_from_file_location(rel.replace("/", "_")[:-3],
                                                  lib.HERE / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", nargs="+", default=["O", "F", "L"])
    ap.add_argument("--time", default="00:30:00")
    a = ap.parse_args()
    ids, lines = [], []
    for t in a.tests:
        mod = load(MODS[t])
        run_id, line = mod.prepare(VARIANT[t]) if t in VARIANT else mod.prepare()
        ids.append(run_id)
        lines.append(line)
        time.sleep(1.1)          # distinct run ids (one-second resolution)
    tmp = lib.SCRATCH / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    lst = tmp / f"verify_batch_{dt.datetime.now():%Y%m%d-%H%M%S}.list"
    lst.write_text("\n".join(lines) + "\n")
    env = dict(os.environ, ATHENA_EXE=str(lib.EXE_GPU), TIME=a.time, JOB_NAME="core-verify")
    r = subprocess.run([str(lib.WT / "scripts" / "gpu_batch.sh"), str(lst)], env=env,
                       check=True, capture_output=True, text=True)
    print(r.stdout.strip())
    jid = r.stdout.strip().split()[2] if r.stdout.startswith("submitted job") else None
    for run_id in ids:
        lib.write_manifest(run_id, batch_list=str(lst), slurm_job=jid, status="submitted",
                           submitted=dt.datetime.now().isoformat(timespec="seconds"))
    print(" ".join(ids))


if __name__ == "__main__":
    main()
