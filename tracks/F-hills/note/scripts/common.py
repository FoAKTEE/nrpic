"""Shared helpers of the note's figure and ledger scripts (F-hills, working note v0).

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/F-hills/<run_id>/ (manifest under tracks/F-hills/runs/<run_id>/),
and every file is checked against the sha256 that the run recorded (its sha256sums.txt, or
the output list of its manifest); wave-1 runs without either record are read as they are and
reported as such. Outputs go to ../figures and ../tables next to this file unless --out DIR
is given.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)                       # tracks/F-hills
WT = os.path.dirname(os.path.dirname(TRACK))        # worktree root
SCRATCH = os.environ.get("NRPIC_F_SCRATCH", "/data/haiyangw/nrpic/scratch/F-hills")

# the registered runs the note reads (key -> run id); manifests in tracks/F-hills/runs/
RUNS = {
    "scale": "F-hills-20261115-045435-f62d553",       # novelty: plunge bound, Peters time
    "coplanar": "F-hills-20261115-130237-cbfaf6b",    # newton3 P1: restricted coplanar scan
    "deep": "F-hills-20261115-132156-efddfc0",        # newton3 P1: deep supplement (D < 1e-3)
    "coplanar_an": "F-hills-20261115-133222-9cb10db",  # newton3 P1: analysis of the two above
    "skr": "F-hills-20261115-132703-0bfc352",         # newton3: comparison with SKR's figures
    "general_an": "F-hills-20261115-133200-05ee76a",  # newton3 P2: isotropic scan analysis
    "h1": "F-hills-20261115-132942-2f7ad7f",          # newton3 P7/P8: BKRS curves, survival criterion H1
    "s1_an": "F-hills-20261115-142554-c10b371",       # geodesic_binary: analysis of S1, S2, S4
    "v4": "F-hills-20261115-145246-090f5dc",          # lead V4: independent restricted problem
    "v4b": "F-hills-20261115-145544-a314517",         # lead V4b: wide binaries followed on
    "v5v6": "F-hills-20261115-145251-090f5dc",        # lead V5, V6
    "v5b": "F-hills-20261115-145559-a314517",         # lead V5b
    "v7": "F-hills-20261115-145915-71abf93",          # lead V7: pericentre scan
    "mesh10": "F-hills-20261115-131348-634fb86",      # three_punctures: trees along q = 10
    "mesh4": "F-hills-20261115-131933-907e5fe",       # three_punctures: trees along q = 4
    "e1": "F-20261115-173543-29e87e8",                # nr_first E1: t = 0 trees at q = 4
    "e6": "F-20261115-174102-ffa764f",                # nr_first E6: baselines of P1 at q = 4
    "e4": "F-20261115-173821-b2c969a",                # nr_first E4: readers on a synthetic run
    "n1": "F-20261115-174648-25514db",                # this package N1: passage time series
}

CHECKED = []   # (run_id, relative path, state)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(key):
    with open(os.path.join(TRACK, "runs", RUNS[key], "manifest.json")) as f:
        return json.load(f)


def run_file(key, rel):
    """Absolute path of file `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    rdir = os.path.join(SCRATCH, run_id)
    path = os.path.join(rdir, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    mpath = os.path.join(TRACK, "runs", run_id, "manifest.json")
    if not os.path.isfile(mpath):
        raise SystemExit(f"run {run_id} has no manifest under tracks/F-hills/runs/")
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
        CHECKED.append((run_id, rel, "sha256 ok (sha256sums.txt)"))
        return path
    man = json.load(open(mpath))
    rec = {}
    outs = man.get("outputs")
    if isinstance(outs, list):
        for o in outs:
            if isinstance(o, dict) and "sha256" in o:
                rec[os.path.basename(o.get("path", ""))] = o["sha256"]
                rec[o.get("path", "")] = o["sha256"]
    elif isinstance(outs, dict):
        for k in ("files", "sha256"):
            v = outs.get(k)
            if isinstance(v, dict):
                for p, h in v.items():
                    if isinstance(h, str):
                        rec[p] = h
                        rec[os.path.basename(p)] = h
            elif isinstance(v, list):
                for o in v:
                    if isinstance(o, dict) and "sha256" in o:
                        rec[o.get("path", "")] = o["sha256"]
                        rec[os.path.basename(o.get("path", ""))] = o["sha256"]
    for k in ("outputs_sha256", "output_sha256"):
        if isinstance(man.get(k), dict):
            for p, h in man[k].items():
                rec[p] = h
                rec[os.path.basename(p)] = h
    if rel in rec:
        if rec[rel] != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from its manifest")
        CHECKED.append((run_id, rel, "sha256 ok (manifest)"))
    else:
        CHECKED.append((run_id, rel, "no recorded sha256 (wave-1 run, read as it is)"))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (for a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv if argv is not None else sys.argv[1:])
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d


def write_numbers(out, stem, numbers):
    """Numbers a figure shows, with their run ids, for the ledger (stem_numbers.json)."""
    with open(os.path.join(out, f"{stem}_numbers.json"), "w") as f:
        json.dump(numbers, f, indent=1, sort_keys=True)


def report_checks(stem):
    for run_id, rel, st in CHECKED:
        print(f"{stem}: input {run_id}/{rel}: {st}")


def close(a, b, rel=1e-9, what=""):
    if abs(a - b) > rel * max(1.0, abs(b)):
        raise SystemExit(f"check failed: {what}: {a} against {b}")
