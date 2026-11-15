"""Readers and writers of the particle formats of docs/FORMATS.md (little-endian).

read_snapshot(path) -> dict(time, cycle, x (N,3), u (N,3) covariant u_i, m (N,), tag,
species) for `<base>.part.NNNNN.bin` (magic NRPSNAP1);
read_history(path) -> (header list, array) for `<base>.nrpic.hst` (restarts append: keep
the last record of each time);
write_nrp(path, x, u, m, species=None) writes `*.nrp` (magic NRPIC001);
read_nrp(path).
In a Minkowski box (metric kerr_schild with bh_mass = 0, Cartesian coordinates) u_i = u^i
and W = sqrt(1 + |u|^2).
"""
import glob
import os
import re

import numpy as np


def write_nrp(path, x, u, m, species=None):
    x = np.ascontiguousarray(x, dtype="<f8")
    u = np.ascontiguousarray(u, dtype="<f8")
    m = np.ascontiguousarray(m, dtype="<f8").reshape(-1)
    n = x.shape[0]
    rec = np.empty((n, 7), dtype="<f8")
    rec[:, 0:3] = x
    rec[:, 3:6] = u
    rec[:, 6] = m
    sp = np.zeros(n, dtype="<i4") if species is None else np.asarray(species, dtype="<i4")
    with open(path, "wb") as fh:
        fh.write(b"NRPIC001")
        fh.write(np.array([n], dtype="<i8").tobytes())
        fh.write(rec.tobytes())
        fh.write(sp.tobytes())


def read_nrp(path):
    with open(path, "rb") as fh:
        assert fh.read(8) == b"NRPIC001"
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        sp = np.frombuffer(fh.read(4 * n), "<i4")
    return dict(x=rec[:, 0:3].copy(), u=rec[:, 3:6].copy(), m=rec[:, 6].copy(), species=sp)


def read_snapshot(path):
    with open(path, "rb") as fh:
        magic = fh.read(8)
        assert magic == b"NRPSNAP1", magic
        t = float(np.frombuffer(fh.read(8), "<f8")[0])
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        cyc = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(fh.read(4 * n), "<i4")
        sp = np.frombuffer(fh.read(4 * n), "<i4")
    order = np.argsort(tag, kind="stable")
    return dict(time=t, cycle=cyc, x=rec[order, 0:3].copy(), u=rec[order, 3:6].copy(),
                m=rec[order, 6].copy(), tag=tag[order].copy(), species=sp[order].copy())


def snapshots(rundir, base):
    """Sorted list of snapshot paths of a run directory."""
    files = glob.glob(os.path.join(rundir, f"{base}.part.*.bin"))
    key = lambda p: int(re.findall(r"\.part\.(\d+)\.bin$", p)[0])
    return sorted(files, key=key)


def read_history(path):
    head = []
    rows = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                head.append(line.strip())
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    if a.size:
        # restarts append: keep the last record of each time
        _, idx = np.unique(a[::-1, 0], return_index=True)
        a = a[::-1][np.sort(idx)]
        a = a[np.argsort(a[:, 0], kind="stable")]
    return head, a


def W_flat(u):
    return np.sqrt(1.0 + np.sum(u * u, axis=-1))


def kinetic_flat(u):
    u2 = np.sum(u * u, axis=-1)
    return u2 / (np.sqrt(1.0 + u2) + 1.0)
