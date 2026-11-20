"""Shared helpers of the note's figure and ledger scripts (Track A, working note v0).

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/ (manifest under tracks/A-emd-pbh/runs/),
and every file is checked against the sha256 the run recorded in its sha256sums.txt. Runs
that recorded none (wave 1, and the hand-run criteria checks of wave 2) are checked against
the listing that the integrity run INTEGRITY_RUN wrote into its own directory
(<INTEGRITY_RUN>/<run_id>.sha256, taken on 2026-11-20 without touching their directories).
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
    "dataset2t": "A-emd-pbh-20261115-130609-947c898",  # data set 2t (scouting data)
    # wave 2
    "criteria_w2": "A-emd-pbh-20261115-161813-6c820fb",     # all checks (T1, T3-T5 taken from here)
    "criteria_w2_t2": "A-emd-pbh-20261115-163358-9b2d048",  # T2 after the T2.6 fix
    "ball_runs": "A-20261115-182657-53da696",       # SR-1/SR-2 at dx = M, M/2, M/4: summary table
    "ball_runs_w2": "A-emd-pbh-20261115-163659-4dbacd0",  # SR-1/SR-2 at dx = M, M/2: per-run numbers
    "newton": "A-emd-pbh-20261115-164420-4528861",  # Newtonian mode: top hat and scan points
    "newton_range": "A-emd-pbh-20261115-164757-b8bc9a3",  # range of the full-relativity scan
}

# the run that listed the sha256 of every file of the runs above without sha256sums.txt
INTEGRITY_RUN = None

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
    elif INTEGRITY_RUN:
        listing = os.path.join(SCRATCH, INTEGRITY_RUN, f"{run_id}.sha256")
        table = {}
        for line in open(listing):
            parts = line.split(None, 1)
            if len(parts) == 2:
                table[parts[1].strip()] = parts[0]
        if rel not in table:
            raise SystemExit(f"{rel} is not listed in {listing}")
        if table[rel] != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from the listing of run {INTEGRITY_RUN}")
        CHECKED.append((run_id, rel, f"sha256 ok against the listing of {INTEGRITY_RUN}"))
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
