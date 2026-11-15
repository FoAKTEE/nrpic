"""Registration of analysis runs: tracks/A-emd-pbh/runs/<run_id>/manifest.json, outputs under
scratch/A-emd-pbh/<run_id>/ (CLAUDE.md rule 4)."""
import datetime as _dt
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TRACK))
SCRATCH = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
OWNER = "A-emd-pbh"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _commit():
    out = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True,
                         text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", WT, "status", "--porcelain", "--",
                            os.path.relpath(HERE, WT)], capture_output=True, text=True,
                           check=True).stdout.strip()
    return out, bool(dirty)


class Run:
    """Context manager: creates the run id and output directory, writes the manifest."""

    def __init__(self, purpose, kind, inputs, cores=1):
        self.commit, self.dirty = _commit()
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
        self.run_id = f"{OWNER}-{stamp}-{self.commit[:7]}"
        self.out = os.path.join(SCRATCH, self.run_id)
        os.makedirs(self.out, exist_ok=True)
        self.purpose, self.kind, self.cores = purpose, kind, cores
        self.inputs = [os.path.abspath(p) for p in inputs]
        self.manifest_dir = os.path.join(TRACK, "runs", self.run_id)

    def __enter__(self):
        self.t0 = time.time()
        self.started = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        return self

    def __exit__(self, exc_type, exc, tb):
        wall = time.time() - self.t0
        man = {
            "run_id": self.run_id,
            "command": " ".join([os.path.basename(sys.executable)] + sys.argv),
            "cwd": os.getcwd(),
            "commit": self.commit,
            "worktree_dirty_in_package": self.dirty,
            "inputs": [{"path": os.path.relpath(p, WT), "sha256": _sha256(p)}
                       for p in self.inputs],
            "output_dir": self.out,
            "purpose": self.purpose,
            "kind": self.kind,
            "started_utc": self.started,
            "wall_time_s": round(wall, 1),
            "cores": self.cores,
            "card_hours": 0.0,
            "host": socket.gethostname(),
            "exit": "ok" if exc_type is None else f"error: {exc_type.__name__}: {exc}",
        }
        os.makedirs(self.manifest_dir, exist_ok=True)
        with open(os.path.join(self.manifest_dir, "manifest.json"), "w") as f:
            json.dump(man, f, indent=2)
            f.write("\n")
        return False
