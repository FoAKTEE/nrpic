"""Shared helpers of the note's figure and ledger scripts (C-sidm, working note v0).

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/C-sidm/<run_id>/ (manifest under tracks/C-sidm/runs/<run_id>/),
and every file is checked against the sha256 that the run recorded in its sha256sums.txt;
runs of wave 1 without that file are read as they are and reported as such.
Outputs go to ../figures and ../tables next to this file unless --out DIR is given.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)                       # tracks/C-sidm
WT = os.path.dirname(os.path.dirname(TRACK))        # worktree root
SCRATCH = os.environ.get("NRPIC_C_SCRATCH", "/data/haiyangw/nrpic/scratch/C-sidm")

# the registered runs the note reads (key -> run id); manifests in tracks/C-sidm/runs/
RUNS = {
    "mono": "C-sidm-20261115-115344-eb8b752",        # monoenergetic sequence, Wu-Most models
    "king": "C-sidm-20261115-115348-eb8b752",        # truncated-MB sequences b = 0.1..1 (scope)
    "kncost": "C-sidm-20261115-115400-eb8b752",      # Knudsen numbers (scope H), costs
    "models": "C-sidm-20261115-120610-b4592be",      # 13 near-threshold particle models
    "collref": "C-sidm-20261115-120703-9b3e868",     # collision references R1-R7
    "thermal": "C-sidm-20261115-120722-38ab057",         # thermal-core sequences, criteria, pulsation onsets
    "t60": "C-sidm-20261115-121302-313d399",         # AthenaK collisionless step T6-0
    "times": "C-sidm-20261115-121412-d463e1a",       # time scales at the onset
    "poly": "C-sidm-20261115-121524-5cebcf5",        # FEM check on Gamma = 2 polytropes
    "eqchk": "C-sidm-20261115-121626-e99907d",       # offline checks of the 13 models
    "init": "C-sidm-20261115-121748-4e8d6b5",        # candidate initial models, radii
    "kneq": "C-sidm-20261115-122915-cdc395c",        # Kn conversion (equilibria convention)
    "smoke": "C-sidm-20261115-125308-54870b9",       # AthenaK reads the King threshold files
    "xchk": "C-sidm-20261115-131130-3077a99",        # lead cross-checks X1-X5
    "t0": "C-sidm-20261115-132624-13a77db",          # T0 on core's committed kernels
    "boxs0": "C-20261115-164809-cd53539",            # wave 2: box smoke run (formats)
    "boxdesign": "C-20261115-165028-a559ab8",        # wave 2: box-test design numbers
}

CHECKED = []   # (run_id, relative path, "sha256 ok" | "no sha256sums.txt (wave-1 run)")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_dir(key):
    return os.path.join(SCRATCH, RUNS[key])


def run_file(key, rel):
    """Absolute path of file `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    rdir = os.path.join(SCRATCH, run_id)
    path = os.path.join(rdir, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    if not os.path.isfile(os.path.join(TRACK, "runs", run_id, "manifest.json")):
        raise SystemExit(f"run {run_id} has no manifest under tracks/C-sidm/runs/")
    sums = os.path.join(rdir, "sha256sums.txt")
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            parts = line.split(None, 1)
            if len(parts) == 2:
                table[parts[1].strip().lstrip("*").removeprefix("./")] = parts[0]
        if rel not in table:
            raise SystemExit(f"{rel} is not listed in {sums}")
        if table[rel] != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from the one run {run_id} recorded")
        CHECKED.append((run_id, rel, "sha256 ok"))
    else:
        man = json.load(open(os.path.join(TRACK, "runs", run_id, "manifest.json")))
        rec = dict(man.get("outputs_sha256") or {})
        if isinstance(man.get("outputs"), list):        # scope's schema: [{path, sha256}]
            rec.update({o["path"]: o["sha256"] for o in man["outputs"] if "sha256" in o})
        if rel in rec:
            if rec[rel] != _sha256(path):
                raise SystemExit(f"sha256 of {path} differs from its manifest")
            CHECKED.append((run_id, rel, "sha256 ok (manifest outputs_sha256)"))
        else:
            CHECKED.append((run_id, rel, "no sha256sums.txt (wave-1 run)"))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def manifest(key):
    with open(os.path.join(TRACK, "runs", RUNS[key], "manifest.json")) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (for a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv if argv is not None else sys.argv[1:])
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d


def report_checks(stem):
    for run_id, rel, st in CHECKED:
        print(f"{stem}: input {run_id}/{rel}: {st}")
