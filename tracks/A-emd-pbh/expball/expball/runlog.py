"""Run manifests (CLAUDE.md rule 4): tracks/A-emd-pbh/runs/<run_id>/manifest.json with
run_id = A-emd-pbh-<YYYYMMDD-HHMMSS>-<commit7>; outputs under scratch/A-emd-pbh/<run_id>/.

The ignore list of the repository (`runs/`) also matches tracks/<ID>/runs/, so a copy of
every manifest is kept in expball/manifests/<run_id>.json, which git does track.
"""

import hashlib
import json
import os
import socket
import subprocess
import sys
import time

OWNER = "A-emd-pbh"
_HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(_HERE, ".."))                  # tracks/A-emd-pbh/expball
WT = os.path.normpath(os.path.join(PKG, "..", "..", ".."))         # worktree root
SCRATCH = "/data/haiyangw/nrpic/scratch/" + OWNER


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit():
    c = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", WT, "status", "--porcelain", "--",
                            "tracks/A-emd-pbh/expball"], capture_output=True, text=True)
    return c.stdout.strip(), bool(dirty.stdout.strip())


class Run:
    """Context manager: creates the run id and output directory, writes the manifest at
    the end (also when the run fails, with status 'failed')."""

    def __init__(self, purpose, kind="scouting", inputs=(), cores=1, extra=None):
        self.commit, self.dirty = git_commit()
        self.run_id = f"{OWNER}-{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}-{self.commit[:7]}"
        self.out = os.path.join(SCRATCH, self.run_id)
        os.makedirs(self.out, exist_ok=False)
        self.purpose, self.kind, self.cores = purpose, kind, cores
        self.inputs = list(inputs)
        self.extra = dict(extra or {})
        self.results = {}

    def __enter__(self):
        self.t0 = time.time()
        print(f"run {self.run_id} -> {self.out}")
        return self

    def __exit__(self, et, ev, tb):
        wall = time.time() - self.t0
        man = dict(run_id=self.run_id, owner=OWNER, purpose=self.purpose, kind=self.kind,
                   command=" ".join([os.path.basename(sys.executable)] + sys.argv),
                   cwd=os.getcwd(), commit=self.commit,
                   worktree_dirty_in_package=self.dirty, host=socket.gethostname(),
                   inputs=[dict(path=p, sha256=sha256(p)) for p in self.inputs if os.path.isfile(p)],
                   output_dir=self.out, wall_time_s=round(wall, 2), cores=self.cores,
                   card_hours=0.0, status="failed" if et else "ok",
                   outputs=[dict(path=os.path.join(self.out, f), sha256=sha256(os.path.join(self.out, f)))
                            for f in sorted(os.listdir(self.out))
                            if os.path.isfile(os.path.join(self.out, f))],
                   results=self.results, **self.extra)
        if et:
            man["error"] = repr(ev)
        d = os.path.join(WT, "tracks", OWNER, "runs", self.run_id)
        os.makedirs(d, exist_ok=True)
        for p in (os.path.join(d, "manifest.json"),
                  os.path.join(PKG, "manifests", self.run_id + ".json")):
            with open(p, "w") as f:
                json.dump(man, f, indent=2, default=float)
        print(f"manifest {self.run_id}: status {man['status']}, wall {wall:.1f} s")
        return False
