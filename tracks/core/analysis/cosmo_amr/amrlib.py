"""Helpers of the tests of the work package cosmo-amr (tracks/core/JOURNAL-cosmo-amr.md):
input decks built from the inputs under problems/, runs of the processor executable,
readers of the histories."""
import collections
import concurrent.futures
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cosmo", "ic"))
sys.path.insert(0, os.path.join(ROOT, "python"))


class Inp:
    """An AthenaK input deck as ordered blocks of ordered parameters."""

    def __init__(self, path=None):
        self.blocks = collections.OrderedDict()
        if path is not None:
            cur = None
            with open(path) as f:
                for line in f:
                    s = line.split("#")[0].strip()
                    if not s:
                        continue
                    if s.startswith("<"):
                        cur = s[1:s.index(">")]
                        self.blocks.setdefault(cur, collections.OrderedDict())
                    elif "=" in s and cur is not None:
                        k, v = s.split("=", 1)
                        self.blocks[cur][k.strip()] = v.strip()

    def copy(self):
        c = Inp()
        for b, d in self.blocks.items():
            c.blocks[b] = collections.OrderedDict(d)
        return c

    def set(self, block, **kv):
        d = self.blocks.setdefault(block, collections.OrderedDict())
        for k, v in kv.items():
            if isinstance(v, bool):
                v = "true" if v else "false"
            elif isinstance(v, float):
                v = repr(v)
            d[k] = str(v)
        return self

    def drop(self, block, *keys):
        if block in self.blocks:
            if keys:
                for k in keys:
                    self.blocks[block].pop(k, None)
            else:
                del self.blocks[block]
        return self

    def write(self, path):
        with open(path, "w") as f:
            for b, d in self.blocks.items():
                f.write(f"<{b}>\n")
                for k, v in d.items():
                    f.write(f"{k} = {v}\n")
                f.write("\n")
        return path


def run_case(exe, inp, rundir, name="case", args=(), start_dir=None):
    """Runs one case: the deck is written to rundir/<name>.athinput, the executable is
    started in start_dir (default rundir) with -d rundir.  Returns (exit status, wall)."""
    os.makedirs(rundir, exist_ok=True)
    deck = inp.write(os.path.join(rundir, name + ".athinput"))
    t0 = time.time()
    with open(os.path.join(rundir, "log.txt"), "w") as log:
        p = subprocess.run([exe, "-i", deck, "-d", rundir] + list(args),
                           cwd=start_dir or rundir, stdout=log, stderr=subprocess.STDOUT,
                           env=dict(os.environ, OMP_NUM_THREADS="1"))
    wall = time.time() - t0
    with open(os.path.join(rundir, "status.txt"), "w") as f:
        f.write(f"exit {p.returncode}\nwall {wall:.2f}\nexe {exe}\n")
    return p.returncode, wall


def run_many(jobs, cores):
    """jobs: list of (exe, inp, rundir, name, args, start_dir).  At most `cores` at a
    time (the executable is serial).  Returns the list of (exit status, wall)."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, cores)) as ex:
        futs = [ex.submit(run_case, *j) for j in jobs]
        return [f.result() for f in futs]


def read_hst(path, like=None):
    """A history of the particle module (header line '# [1]=name [2]=name ...').  A
    history continued by a restart in another directory has no header: `like` names a
    file of the same kind whose header is taken instead."""
    names = None
    for p in (path, like):
        if p is None or names is not None:
            continue
        with open(p) as f:
            for line in f:
                if line.startswith("# [1]="):
                    names = [w.split("=", 1)[1] for w in line[1:].split()]
                    break
    a = np.loadtxt(path, ndmin=2)
    return collections.OrderedDict((n, a[:, i]) for i, n in enumerate(names))


def read_tab(path):
    """An AthenaK table: dict of columns, and the time of the header."""
    names, t = None, None
    with open(path) as f:
        for line in f:
            if line.startswith("# Athena") and "time=" in line:
                t = float(line.split("time=")[1].split()[0])
            elif line.startswith("#"):
                w = line[1:].split()
                if len(w) > 2:
                    names = w
            else:
                break
    a = np.loadtxt(path, ndmin=2)
    if names is None or len(names) != a.shape[1]:
        names = [f"c{i}" for i in range(a.shape[1])]
    return {n: a[:, i] for i, n in enumerate(names)}, t


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def exit_status(rundir):
    with open(os.path.join(rundir, "status.txt")) as f:
        return int(f.readline().split()[1])
