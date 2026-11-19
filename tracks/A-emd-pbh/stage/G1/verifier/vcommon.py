"""Shared helpers of the G1 verifier (C18): paths, checksum checks, output, style.

Nothing here imports the track's own code; the only project module used is the figure
style python/nrpic/figstyle.py.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 5))          # worktree root
SCR = "/data/haiyangw/nrpic/scratch/A-emd-pbh"                 # run outputs of the owner
KB = "/data/haiyangw/nrpic/kb-data/raw/arxiv"                  # paper sources (read only)
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs  # noqa: E402

_SUMS = {}


def sha256(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def run_file(run_id, rel, check=True):
    """Absolute path of <run>/<rel>; checked against the run's sha256sums.txt when the run
    wrote one and lists the file. Returns (path, status) with status 'ok', 'unlisted' or
    'no-sums'; a mismatch raises."""
    p = os.path.join(SCR, run_id, rel)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    if not check:
        return p, "unchecked"
    sums = os.path.join(SCR, run_id, "sha256sums.txt")
    if not os.path.exists(sums):
        return p, "no-sums"
    if sums not in _SUMS:
        d = {}
        for line in open(sums):
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                d[parts[1].lstrip("*").lstrip("./")] = parts[0]
        _SUMS[sums] = d
    d = _SUMS[sums]
    key = rel.lstrip("./")
    if key not in d:
        return p, "unlisted"
    got = sha256(p)
    if got != d[key]:
        raise RuntimeError(f"checksum mismatch {p}: {got} != {d[key]}")
    return p, "ok"


def outdir(default_name):
    d = os.environ.get("NRPIC_RUN_DIR") or os.path.join(SCR, "tmp", "verifier2", default_name)
    os.makedirs(d, exist_ok=True)
    return d


class Ledger:
    """Collects rows (item, claimed, recomputed, verdict, evidence) and writes JSON + text."""

    def __init__(self, name):
        self.name = name
        self.rows = []
        self.inputs = {}

    def inp(self, run_id, rel, check=True):
        p, st = run_file(run_id, rel, check)
        self.inputs[f"{run_id}/{rel}"] = st
        return p

    def row(self, item, claim, mine, verdict, how=""):
        self.rows.append({"item": item, "claim": claim, "mine": mine, "verdict": verdict, "how": how})
        print(f"[{verdict:13s}] {item}: claim {claim} | mine {mine}" + (f"  ({how})" if how else ""))

    def write(self, out):
        with open(os.path.join(out, f"{self.name}.json"), "w") as f:
            json.dump({"rows": self.rows, "inputs": self.inputs}, f, indent=1, default=float)
        n = {}
        for r in self.rows:
            n[r["verdict"]] = n.get(r["verdict"], 0) + 1
        print(f"{self.name}: {len(self.rows)} rows {n}; inputs {dict((s, list(self.inputs.values()).count(s)) for s in set(self.inputs.values()))}")


def rel(a, b):
    return a / b - 1.0


def agree(x, claim, digits=None, rtol=None, atol=None):
    """Does x round to the claimed printed value? digits = significant digits of the claim
    taken from its string; or explicit tolerances."""
    if rtol is not None or atol is not None:
        return abs(x - claim) <= (atol or 0) + (rtol or 0) * abs(claim)
    return False
