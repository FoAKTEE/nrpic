"""Shared helpers of the figure and ledger scripts of Track B's working note v0.

Every number the scripts use is read from the output directory of a registered run,
/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/ (manifest under tracks/B-emd-gw/runs/).
A file is checked against the sha256 its run recorded, either in the run's
sha256sums.txt or in the manifest field outputs_sha256; wave-1 runs that recorded neither
are read as they are and the ledger says so. Outputs go to ../figures and ../tables next to
this file unless --out DIR is given.
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)                       # tracks/B-emd-gw
WT = os.path.dirname(os.path.dirname(TRACK))        # worktree root
SCRATCH = "/data/haiyangw/nrpic/scratch/B-emd-gw"

# the registered runs the note reads (key -> run id)
RUNS = {
    "lead_recheck": "B-emd-gw-20261115-131016-03b1119",   # L1: clean-export rerun of all wave-1 packages
    "lead_checks": "B-emd-gw-20261115-131027-03b1119",    # L2: independent derivations a-f
    "athenak_gw": "B-emd-gw-20261115-120128-7dfaa38",     # diagnostics on the AthenaK linear-wave dumps
    "wave_dumps": "B-emd-gw-20261115-113218-0ea0f74",     # the AthenaK run that wrote those dumps
    "crossed_tt": "B-emd-gw-20261115-113148-4e5c33b",     # crossed-wave quasi-static TT strain
    "item3": "B-emd-gw-20261115-113102-bc5e082",          # symbolic checks of the plane-symmetric null
    "regime": "B-emd-gw-20261115-113632-2960145",         # junk decay, virial frequency, cost
    "pancake": "B-emd-gw-20261115-123852-ea4475c",        # analysis of the pancake runs
    "pancake_gr": "B-emd-gw-20261115-115217-69ab1db",     # GR card runs, one particle per cell
    "pancake_gr_p2": "B-emd-gw-20261115-115902-a3207d7",  # GR card run, two per cell and direction
    "pancake_nw": "B-emd-gw-20261115-115239-69ab1db",     # Newtonian particle-mesh reference
    "pancake_nw_p2": "B-emd-gw-20261115-122451-01801f6",  # the same, two per cell and direction
    "cosmo_dumps": "B-emd-gw-20261115-120846-d1509b5",    # projection of earlier three-wave relativistic dumps
    "late_rise": "B-20261115-164616-a6d9477",             # spatial-gauge piece on those dumps (first-source helper)
    "flrw": "B-emd-gw-20261115-115414-7ffbde1",           # homogeneous runs against the exact solution
    "baseline": "B-emd-gw-20261115-115752-840e994",       # semi-analytic baseline T1-T8
    # wave 2 (G1): the first source in full relativity (first_source helper)
    "scan_ic64": "B-20261115-161656-03d75e1",             # initial data, 64^3, eps = 0, 0.1, 0.3
    "scan_ic64_eps1": "B-20261115-164104-886798f",        # initial data, 64^3, eps = 1
    "scan_cards_a": "B-20261115-164059-d802e82",          # card runs eps = 0, 0.1, 0.3, 64^3
    "scan_cards_b": "B-20261115-165353-b592d43",          # card runs eps = 1, zero shift and Gamma driver
    "scan_cpu32": "B-20261115-165525-f7c2004",            # processor runs, the five cases at 32^3
    "scan64_a": "B-20261115-174722-ba1048d",              # per-dump diagnostics, 64^3, eps = 0, 0.1, 0.3
    "scan64_b": "B-20261115-180834-c77a132",              # per-dump diagnostics, 64^3, eps = 1 (both gauges)
    "scan32": "B-20261115-184650-2d155b6",                # per-dump diagnostics, 32^3, all five cases
    "t0_gauge": "B-20261115-164221-6a6b779",              # gauge piece on exact pure-gauge data (T0)
    "slicing": "B-20261115-170610-c82b10c",               # first-order slicing of the earlier three-wave runs (P9)
    # wave 2 (G1): AthenaK's Newtonian mode (newton_tests helper)
    "nw_pancake": "B-20261115-173904-a7297e3",            # plane-wave pancake against Zel'dovich, n = 16, 32, 64
    "nw_ellipsoid": "B-20261115-174405-af11300",          # isolated ellipsoid against the ODE; self-similarity
    "nw_card": "B-20261115-163653-f6324ea",               # the card run of the n = 64 pancakes
    # the lead's rechecks of wave 2 (second readings, stage/REVIEW-wave2.md)
    "review_fs": "B-20261115-190007-e09a0d2",
    "review_nw": "B-20261115-190015-4dd3416",
}

# the claims check reads the lead's stage documents as they stood when the note v0 checked
# them (git sha of run B-20261115-165556-a399d4e); the lead has rewritten them since
CLAIMS_REV = "a399d4e"

CHECKED = []   # (run_id, relative path, how it was checked)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(key_or_id):
    run_id = RUNS.get(key_or_id, key_or_id)
    with open(os.path.join(TRACK, "runs", run_id, "manifest.json")) as f:
        return json.load(f)


def _recorded_sums(run_id):
    """{relative path: sha256} that the run recorded, or None."""
    rdir = os.path.join(SCRATCH, run_id)
    sums = os.path.join(rdir, "sha256sums.txt")
    if os.path.isfile(sums):
        table = {}
        for line in open(sums):
            parts = line.split(None, 1)
            if len(parts) == 2:
                name = parts[1].strip().lstrip("*")
                if name.startswith("./"):
                    name = name[2:]
                table[name] = parts[0]
        return table
    m = manifest(run_id)
    if isinstance(m.get("outputs_sha256"), dict):
        return {k.lstrip("./"): v for k, v in m["outputs_sha256"].items()}
    return None


def run_file(key, rel):
    """Absolute path of file `rel` of the run named by `key`, checked against its sha256."""
    run_id = RUNS[key]
    path = os.path.join(SCRATCH, run_id, rel)
    if not os.path.isfile(path):
        raise SystemExit(f"missing output {path} of run {run_id}")
    table = _recorded_sums(run_id)
    if table is None:
        CHECKED.append((run_id, rel, "no checksum recorded (wave-1 run)"))
    elif rel in table or os.path.basename(rel) in table:
        want = table.get(rel, table.get(os.path.basename(rel)))
        if want != _sha256(path):
            raise SystemExit(f"sha256 of {path} differs from the one run {run_id} recorded")
        CHECKED.append((run_id, rel, "sha256 ok"))
    else:
        CHECKED.append((run_id, rel, "not in the run's checksum list"))
    return path


def load_json(key, rel):
    with open(run_file(key, rel)) as f:
        return json.load(f)


def out_dir(default_sub, argv=None):
    """--out DIR (inside a registered run) or ../<default_sub> next to the scripts."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a, _ = ap.parse_known_args(argv)
    d = a.out or os.path.join(NOTE, default_sub)
    os.makedirs(d, exist_ok=True)
    return d
