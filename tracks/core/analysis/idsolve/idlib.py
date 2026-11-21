"""Readers for the outputs of the initial-data solver of the code (<particles> id_solve)
and small helpers shared by the test scripts of this directory."""
import json
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCRATCH = "/data/haiyangw/nrpic/scratch/core"
FIGS = os.path.join(HERE, "figs")
sys.path.insert(0, os.path.join(WT, "python"))

IDSOLVE_FIELDS = ("psi", "K", "A2", "E", "H", "F7", "H0")


def read_idsolve_bin(path):
    """<basename>.idsolve.bin -> dict with n (n1, n2, n3), box (6 numbers) and the fields
    psi, K, A2 (Abar_ij Abar_ij), E, H (constraint monitor at the last evaluation), F7
    (seven-point residual there), H0 (monitor at the first evaluation), each an array
    indexed [i, j, k] = (x, y, z)."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRIDSOL1":
            raise ValueError("%s: bad magic" % path)
        n = struct.unpack("3q", f.read(24))
        box = struct.unpack("6d", f.read(48))
        nf, = struct.unpack("q", f.read(8))
        out = dict(n=n, box=box)
        nc = n[0]*n[1]*n[2]
        for name in IDSOLVE_FIELDS[:nf]:
            a = np.fromfile(f, dtype=np.float64, count=nc)
            out[name] = a.reshape(n, order="F")
    return out


def read_idsolve_txt(path):
    """<basename>.idsolve.txt -> (array of the iteration records, last comment line)."""
    rows, last = [], ""
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                last = line[1:].strip()
            elif line.strip():
                rows.append([float(w) for w in line.split()])
    return np.array(rows), last


def read_field(path):
    """<basename>.field.NNNNN.bin (NRFIELD2) -> dict with time, n, E, chi (float32) and
    H, Mx, My, Mz, Khat, Theta, alpha (float64), arrays indexed [i, j, k]."""
    with open(path, "rb") as f:
        magic = f.read(8)
        t, = struct.unpack("d", f.read(8))
        n = struct.unpack("3q", f.read(24))
        nc = n[0]*n[1]*n[2]
        out = dict(time=t, n=n)
        for name in ("E", "chi"):
            out[name] = np.fromfile(f, dtype=np.float32, count=nc).reshape(n, order="F")
        if magic == b"NRFIELD2":
            for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[name] = np.fromfile(f, dtype=np.float64, count=nc).reshape(n, order="F")
    return out


def centres(n, lo, hi):
    """Cell centres of n cells between lo and hi."""
    h = (hi - lo)/n
    return lo + (np.arange(n) + 0.5)*h


def mesh_r(d):
    """Radius of the cell centres of a dump about the origin, and the cell size."""
    n, box = d["n"], d["box"]
    x = centres(n[0], box[0], box[1])
    y = centres(n[1], box[2], box[3])
    z = centres(n[2], box[4], box[5])
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    return np.sqrt(X*X + Y*Y + Z*Z), (box[1] - box[0])/n[0], (X, Y, Z)


def interior(a, nb):
    """Array without its outer nb cells in every direction."""
    return a[nb:-nb, nb:-nb, nb:-nb] if nb > 0 else a


def run_dir(run_id):
    return os.path.join(SCRATCH, run_id)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


def git_commit7():
    return subprocess.run(["git", "-C", WT, "rev-parse", "--short=7", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
