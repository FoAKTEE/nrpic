"""Shared helpers of the note's figure and ledger scripts (Track A, working note v0).

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/ (manifest under tracks/A-emd-pbh/runs/),
and every file is checked against the sha256 the run recorded in its sha256sums.txt
(runs of wave 1 without that file are read as they are and reported).
Outputs go to ../figures and ../tables next to this file unless --out is given.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
SCRATCH = os.environ.get("NRPIC_A_SCRATCH", "/data/haiyangw/nrpic/scratch/A-emd-pbh")

# the registered runs the note reads (run id -> what it holds)
RUNS = {
    "scope": "A-20261115-130252-7877b7a",          # scope T1-T5, lead's rerun
    "criteria_scan": "A-emd-pbh-20261115-120425-80492f8",
    "criteria_check": "A-emd-pbh-20261115-130256-a7374a4",
    "convergence": "A-emd-pbh-20261115-130402-f5566fb",
    "convergence512": "A-emd-pbh-20261115-122117-aa1c84d",
    "crosscheck": "A-20261115-130257-a7374a4",
    "ball_exact": "A-emd-pbh-20261115-153719-91b03d1",
    "scouting": "A-20261115-130948-5a2b58a",
}

CHECKED = []   # (run_id, relative path, "sha256 ok" | "no sha256sums.txt")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_file(key, rel):
    """Absolute path of file `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    rdir = os.path.join(SCRATCH, run_id)
    path = os.path.join(rdir, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    sums = os.path.join(rdir, "sha256sums.txt")
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            parts = line.split(None, 1)
            if len(parts) == 2:
                table[parts[1].strip()] = parts[0]
        if rel not in table:
            raise SystemExit(f"{rel} is not listed in {sums}")
        if table[rel] != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from the one run {run_id} recorded")
        CHECKED.append((run_id, rel, "sha256 ok"))
    else:
        CHECKED.append((run_id, rel, "no sha256sums.txt (wave-1 run)"))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (for a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv)
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d


def report_checks(stem):
    for run_id, rel, st in CHECKED:
        print(f"{stem}: input {run_id}/{rel}: {st}")
