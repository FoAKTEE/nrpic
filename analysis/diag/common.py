"""Readers shared by the diagnostic figure scripts."""
import os
import struct
import sys

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")

# columns of <basename>.nrpic.hst (0-based)
H = dict(time=0, ncycle=1, np=2, sum_m=3, sum_mw=4, sum_mux=5, sum_muy=6, sum_muz=7,
         int_e=8, int_sx=9, int_sy=10, int_sz=11, alpha_probe=12, e_probe=13,
         tau_probe=14, alpha_min=15, n_excised=16, m_excised=17, n_escaped=18,
         m_escaped=19, push_maxit=20, push_unconverged=21, nmb=22)


def read_nrpic_hst(path):
    """History of the particle module; restarts append, so keep the last record of
    each time."""
    rows = [l.split() for l in open(path) if not l.startswith("#")]
    a = np.array([r for r in rows if len(r) == 23], dtype=float)
    _, idx = np.unique(a[::-1, 0], return_index=True)
    return a[::-1][idx]


def read_horizon(path):
    """FastFlow summary: time, mass, area, hrms, hmean, mean radius (found rows only)."""
    out = []
    if not os.path.exists(path):
        return np.zeros((0, 6))
    for l in open(path):
        if l.startswith("#"):
            continue
        x = l.split()
        if len(x) >= 12 and x[2] != "nan":
            out.append([float(x[1]), float(x[2]), float(x[7]), float(x[8]), float(x[9]),
                        float(x[10])])
    return np.array(out) if out else np.zeros((0, 6))


def read_traj(path, ncol=8):
    raw = np.fromfile(path)
    n = len(raw) // ncol
    return raw[:n * ncol].reshape(n, ncol)


def read_curv_slice(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        d = np.fromfile(f, dtype=np.float64).reshape(n, 7)
    return t, d


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7 * n).reshape(n, 7)
        tag = np.fromfile(f, dtype=np.int32, count=n)
        sp = np.fromfile(f, dtype=np.int32, count=n)
    return t, d, tag, sp
