"""Readers and writers of the files exchanged with the code (formats in docs/FORMATS.md
and in athenak/src/pgen/nrpic/nrpic_cosmo.cpp)."""
import struct

import numpy as np


def write_particles(path, x, u, m, species=None):
    """NRPIC001 particle file: positions x (N,3), covariant momenta per unit rest mass
    u (N,3), rest masses m (N), optional species (N)."""
    x = np.asarray(x, dtype=np.float64)
    u = np.asarray(u, dtype=np.float64)
    m = np.asarray(m, dtype=np.float64)
    n = len(m)
    sp = np.zeros(n, dtype=np.int32) if species is None else np.asarray(species, np.int32)
    rec = np.empty((n, 7), dtype=np.float64)
    rec[:, 0:3] = x
    rec[:, 3:6] = u
    rec[:, 6] = m
    with open(path, "wb") as f:
        f.write(b"NRPIC001")
        f.write(struct.pack("q", n))
        rec.tofile(f)
        sp.tofile(f)


def write_fields(path, psi, trk, alpha, ahat=None):
    """NRCOSMO1 field file. Arrays have shape (n1, n2, n3) indexed [i, j, k] (x, y, z);
    ahat is a sequence of the six components xx, xy, xz, yy, yz, zz or None (zero)."""
    psi = np.asarray(psi, dtype=np.float64)
    n1, n2, n3 = psi.shape
    if ahat is None:
        ahat = [np.zeros_like(psi)]*6
    with open(path, "wb") as f:
        f.write(b"NRCOSMO1")
        f.write(struct.pack("qqq", n1, n2, n3))
        for a in [psi, trk, alpha] + list(ahat):
            # the code reads the first index fastest: Fortran order of [i, j, k]
            np.asarray(a, dtype=np.float64).ravel(order="F").tofile(f)


def read_snapshot(path):
    """Particle snapshot: time, records (N,7), tags, species, proper times (or None)."""
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
        tag = np.fromfile(f, dtype=np.int32, count=n)
        sp = np.fromfile(f, dtype=np.int32, count=n)
        tau = np.fromfile(f, dtype=np.float64, count=n)
    return t, d, tag, sp, (tau if len(tau) == n else None)


def read_history(path):
    """nrpic history as a dict of columns named as in the header."""
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("# [1]="):
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    a = np.loadtxt(path, ndmin=2)
    # drop records superseded by a restart (time not increasing)
    keep = np.ones(len(a), dtype=bool)
    tmin = np.inf
    for i in range(len(a) - 1, -1, -1):
        if a[i, 0] >= tmin:
            keep[i] = False
        else:
            tmin = a[i, 0]
    a = a[keep]
    return {n: a[:, i] for i, n in enumerate(names)}
