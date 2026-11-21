"""Inputs of the working note v0 of Track E: the registered runs it reads, and a reader
that checks every file against the checksum its run manifest records.

Every figure and table of the note is made from files listed in RUNS. A file is opened
only through `path(run_id, rel)`, which compares its sha256 with the manifest
(`tracks/E-stoch-inf/runs/<run_id>/manifest.json` or `tracks/core/runs/...`) and stops on
a mismatch. Manifests of wave 1 record output checksums in three ways (a dict
`outputs_sha256`, a list `outputs` of {path, sha256}, or a `sha256sums.txt` named in
`outputs`); a run without recorded output checksums is allowed only where RUNS says so,
and the sha256 read is then printed into the ledger.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
TRACK = os.path.dirname(NOTE)
TRACKS = os.path.dirname(TRACK)
# root of all owners' scratch directories (the harness's NRPIC_SCRATCH is the owner's own
# scratch directory, so it is not used here)
SCRATCH = os.environ.get("NOTE_SCRATCH_ROOT", "/data/haiyangw/nrpic/scratch")
FIGDIR = os.path.join(NOTE, "figures")
TABDIR = os.path.join(NOTE, "tables")

# run id -> (owner directory, what the note reads from it, checksums recorded?)
RUNS = {
    "E-stoch-inf-20261115-122806-ef0d039": ("E-stoch-inf", "background and Mukhanov-Sasaki modes, full and deformed (spec T1, T2)", True),
    "E-stoch-inf-20261115-130139-176cdd6": ("E-stoch-inf", "stochastic delta-N reference, quadratic (SR)", True),
    "E-stoch-inf-20261115-130137-176cdd6": ("E-stoch-inf", "stochastic delta-N reference, inflection (USR)", True),
    "E-20261115-140502-2957846": ("E-stoch-inf", "validations of core's noise generator, U1-U8 outputs of E-20261115-135523-a32c3a6", True),
    "E-20261115-140116-87c1cc5": ("E-stoch-inf", "lead's rerun of the cost model and synthesis counts (identical to E-stoch-inf-20261115-123936-b2ec5c7)", True),
    "E-20261115-135532-3f958a1": ("E-stoch-inf", "lead's independent background, freezing and delta-N checks", True),
    "core-20261115-143907-cea4c86": ("core", "core's card throughput of Z4c, field and sources at 128^3", False),
    "E-20261115-172423-5234cce": ("E-stoch-inf", "Markov-tanh noise of the release executable against the standard and a cancellation-free reference", True),
    # gate G1: the slow-roll ladder (ladder/README.md) and the checks of its pipeline
    "E-20261115-194633-9e04ed8": ("E-stoch-inf", "final analysis of the slow-roll ladder: A1-A5, spectrum, halving, negative controls, cost (ladder/results/final/, per-mode arrays res/*.npz)", True),
    "E-20261119-142713-32c883a": ("E-stoch-inf", "floor analysis of the odd constraint parts, A5 before the floor, halving, crossing against ln(N/8) (ladder/results/floor/)", True),
    "E-20261119-145230-ff0dff2": ("E-stoch-inf", "temporal order A6 at N = 32, Courant 0.25, 0.125, 0.0625 (ladder/results/a6/, a6_modes.npz)", True),
    "E-20261115-172618-f948386": ("E-stoch-inf", "card job A: P256, 256^3 slow roll in the paper's set-up, 8.1 e-folds (cost from the manifest)", True),
    "E-20261115-171445-36152c4": ("E-stoch-inf", "synthetic tests T1-T5 of the analysis module", True),
    "E-20261115-172935-ddfade0": ("E-stoch-inf", "ladder reader against core's, R^NR at t = 0", True),
    "E-20261115-174214-74becdd": ("E-stoch-inf", "extraction factor of the anisotropic term of R^NR (SPEC 9 E6)", True),
    "E-20261115-180533-24a7781": ("E-stoch-inf", "noise validation of the card base case: frozen scheme, MeshBlock layouts (A11)", True),
    "E-20261115-184748-9b010fa": ("E-stoch-inf", "card against processors (A14)", True),
    "E-20261119-141654-c2a10d1": ("E-stoch-inf", "restart bit-identity on processors and card (A12)", True),
}

# committed copies of run outputs: repository path (relative to the track) -> (run id, path in the run)
COMMITTED = {
    "ladder/results/final": ("E-20261115-194633-9e04ed8", "res"),
    "ladder/results/floor": ("E-20261119-142713-32c883a", ""),
    "ladder/results/a6": ("E-20261119-145230-ff0dff2", ""),
}

_cache = {}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def manifest(run_id):
    owner = RUNS[run_id][0]
    with open(os.path.join(TRACKS, owner, "runs", run_id, "manifest.json")) as f:
        return json.load(f)


def run_dir(run_id):
    return os.path.join(SCRATCH, RUNS[run_id][0], run_id)


def recorded(run_id):
    """{relative path: sha256} as the manifest records it ({} if nothing is recorded)."""
    m = manifest(run_id)
    if isinstance(m.get("outputs_sha256"), dict):
        return dict(m["outputs_sha256"])
    out = m.get("outputs")
    if isinstance(out, list):
        return {e["path"]: e["sha256"] for e in out if "path" in e and "sha256" in e}
    if isinstance(out, dict) and out.get("sha256sums"):
        p = os.path.join(run_dir(run_id), out["sha256sums"])
        if out.get("sha256sums_sha256") and sha256(p) != out["sha256sums_sha256"]:
            raise SystemExit(f"{run_id}: sha256sums.txt differs from the manifest")
        d = {}
        for line in open(p):
            h, rel = line.rstrip("\n").split(None, 1)
            d[rel.lstrip("*").removeprefix("./")] = h
        return d
    return {}


def path(run_id, rel):
    """Absolute path of an output file of a registered run, after its checksum check."""
    p = os.path.join(run_dir(run_id), rel)
    if not os.path.isfile(p):
        raise SystemExit(f"missing input {p}")
    key = (run_id, rel)
    if key not in _cache:
        got = sha256(p)
        rec = recorded(run_id)
        if rel in rec:
            if rec[rel] != got:
                raise SystemExit(f"{run_id}/{rel}: sha256 {got} differs from the manifest {rec[rel]}")
            _cache[key] = (got, "manifest")
        elif RUNS[run_id][2]:
            raise SystemExit(f"{run_id}/{rel}: no checksum recorded in the manifest")
        else:
            _cache[key] = (got, "not recorded by the run; read value")
    return p


def load_json(run_id, rel):
    with open(path(run_id, rel)) as f:
        return json.load(f)


def committed(rel):
    """Absolute path of a committed copy of a run output (relative to the track directory,
    e.g. 'ladder/results/final/P256_judge.json'), after checking that its sha256 equals the
    one the run recorded for the original. Read from the repository, so a clean export
    (nrpic-stage verify) needs only the run's sha256sums.txt."""
    d, fn = os.path.split(rel)
    if d not in COMMITTED:
        raise SystemExit(f"{rel}: not a committed copy of a registered run")
    run_id, sub = COMMITTED[d]
    orig = fn if (fn == "summary.json" and sub == "res") else (f"{sub}/{fn}" if sub else fn)
    p = os.path.join(TRACK, rel)
    key = (run_id, orig)
    if key not in _cache:
        got = sha256(p)
        rec = recorded(run_id)
        if rec.get(orig) != got:
            raise SystemExit(f"{rel}: sha256 {got} differs from {run_id}/{orig} ({rec.get(orig)})")
        _cache[key] = (got, f"manifest (committed copy {rel})")
    return p


def committed_json(rel):
    with open(committed(rel)) as f:
        return json.load(f)


def checked():
    """[(run_id, rel, sha256, how)] of every file opened so far."""
    return [(r, rel, h, how) for (r, rel), (h, how) in sorted(_cache.items())]


def out_dir(default):
    """--out DIR from the command line, else the default."""
    import sys
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
