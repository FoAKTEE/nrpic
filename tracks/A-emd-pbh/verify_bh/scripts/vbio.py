"""Readers of the verifier verify_bh, written from docs/FORMATS.md,
coord/INTERFACES/diagnostics.md, coord/INTERFACES/spherical_id_format2.md and the source
athenak/src/particles/nrpic_io.cpp (lines 799-937). Nothing here is imported from another
package of the track.

All binary files: little-endian float64 / int32 / int64 (native order of anta).
"""
import os
import re

import numpy as np


# --------------------------------------------------------------- format-2 radial table
def read_tab2(path):
    """Return (header dict, breaks array, data array with columns rbar u KL KT alpha betar)."""
    hdr, rows = {}, []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                m = re.match(r"#\s*([^=]+?)\s*=\s*(.*)$", s)
                if m:
                    hdr[m.group(1)] = m.group(2)
                continue
            rows.append([float(v) for v in s.split()])
    data = np.array(rows)
    if hdr.get("format") != "2":
        raise ValueError(f"{path}: not a format-2 table")
    cols = hdr["columns"].split()
    if cols != ["rbar", "u", "KL", "KT", "alpha", "betar"]:
        raise ValueError(f"{path}: columns {cols}")
    br = np.array([float(v) for v in hdr.get("breaks", "").split()]) if "breaks" in hdr else np.zeros(0)
    return hdr, br, data


def lagrange4_eval(tab_rbar, col, breaks, r):
    """Evaluation rule of the interface (spherical_id_format2.md, 'Evaluation'): four-point
    Lagrange through rows i-1..i+2, i = floor(r/dr), moved so that the four rows lie in the
    piece containing r; beyond the last row the caller continues. Vectorised in r."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    n = len(tab_rbar)
    dr = tab_rbar[1] - tab_rbar[0]
    edges = np.concatenate([[-np.inf], np.sort(breaks), [np.inf]])
    out = np.empty_like(r)
    for j, x in enumerate(r):
        p = np.searchsorted(edges, x, side="right") - 1          # piece index (x >= r_b -> outside)
        lo_r, hi_r = edges[p], edges[p + 1]
        # rows of the piece
        k_lo = 0 if not np.isfinite(lo_r) else int(np.floor(lo_r / dr)) + 1
        k_hi = n - 1 if not np.isfinite(hi_r) else int(np.floor(hi_r / dr))
        i = int(np.floor(x / dr))
        s = i - 1
        s = max(s, k_lo)
        s = min(s, k_hi - 3)
        idx = np.arange(s, s + 4)
        xs = tab_rbar[idx]
        ys = col[idx]
        val = 0.0
        for a in range(4):
            w = 1.0
            for b in range(4):
                if b != a:
                    w *= (x - xs[b]) / (xs[a] - xs[b])
            val += w * ys[a]
        out[j] = val
    return out


# --------------------------------------------------------------- particle file
def read_nrp(path):
    with open(path, "rb") as fh:
        magic = fh.read(8)
        if magic != b"NRPIC001":
            raise ValueError(f"{path}: magic {magic!r}")
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        sp = np.frombuffer(fh.read(4 * n), "<i4")
        rest = fh.read()
    if rest:
        raise ValueError(f"{path}: {len(rest)} trailing bytes")
    return rec[:, 0:3].copy(), rec[:, 3:6].copy(), rec[:, 6].copy(), sp.copy()


# --------------------------------------------------------------- snapshots
def read_snap(path):
    """diagnostics.md section 7: NRPSNAP1, time, N, cycle, 7N float64, N int32 tags, N int32
    species, N float64 proper times."""
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        magic = fh.read(8)
        if magic != b"NRPSNAP1":
            raise ValueError(f"{path}: magic {magic!r}")
        t = float(np.frombuffer(fh.read(8), "<f8")[0])
        n = int(np.frombuffer(fh.read(8), "<i8")[0])
        cyc = int(np.frombuffer(fh.read(8), "<i8")[0])
        rec = np.frombuffer(fh.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(fh.read(4 * n), "<i4")
        sp = np.frombuffer(fh.read(4 * n), "<i4")
        tau = np.frombuffer(fh.read(8 * n), "<f8") if size >= 32 + 72 * n else None
    if size != 32 + 72 * n:
        raise ValueError(f"{path}: size {size} != 32 + 72 N = {32 + 72 * n}")
    return dict(t=t, n=n, cycle=cyc, x=rec[:, 0:3].copy(), u=rec[:, 3:6].copy(), m=rec[:, 6].copy(),
                tag=tag.copy(), species=sp.copy(), tau=None if tau is None else tau.copy())


# --------------------------------------------------------------- trajectories
TRAJMET_COLS = ["time", "tag", "alpha", "bx", "by", "bz", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz",
                "tau", "E", "Sx", "Sy", "Sz"]


def read_traj(path_traj, path_met=None):
    """traj.bin: records of 8 float64 (time, tag, x, y, z, u_x, u_y, u_z); trajmet.bin: records
    of 17 float64 (TRAJMET_COLS), same order. The record length of trajmet is checked from the
    file sizes, not assumed."""
    tr = np.fromfile(path_traj, "<f8")
    if tr.size % 8:
        raise ValueError(f"{path_traj}: {tr.size} doubles, not a multiple of 8")
    tr = tr.reshape(-1, 8)
    out = dict(traj=tr, nrec=tr.shape[0])
    if path_met is not None:
        mt = np.fromfile(path_met, "<f8")
        if mt.size % tr.shape[0]:
            raise ValueError(f"{path_met}: {mt.size} doubles for {tr.shape[0]} records")
        L = mt.size // tr.shape[0]
        out["met_reclen"] = L
        mt = mt.reshape(-1, L)
        if not (np.array_equal(mt[:, 0], tr[:, 0]) and np.array_equal(mt[:, 1], tr[:, 1])):
            raise ValueError("trajmet time/tag columns differ from traj")
        out["met"] = mt
    return out


def traj_by_time(tr):
    """Split the record array into a list of (time, index array), times increasing;
    a time written twice (restart) keeps the last block."""
    t = tr[:, 0]
    # blocks of equal time in file order
    cut = np.nonzero(np.diff(t) != 0)[0] + 1
    starts = np.concatenate([[0], cut])
    ends = np.concatenate([cut, [len(t)]])
    blocks = {}
    for s, e in zip(starts, ends):
        blocks[float(t[s])] = np.arange(s, e)
    return [(k, blocks[k]) for k in sorted(blocks)]


# --------------------------------------------------------------- text outputs
def read_hst(path):
    """nrpic.hst / cstat.hst: names from the last header line with [k]=name; keeps the last
    record of each time."""
    names = None
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") and "[1]=" in line:
                names = [m.group(1) for m in re.finditer(r"\[\d+\]=(\S+)", line)]
    d = np.loadtxt(path, comments="#", ndmin=2)
    t = d[:, 0]
    _, last = np.unique(t[::-1], return_index=True)
    keep = np.sort(len(t) - 1 - last)
    d = d[keep]
    return names, d


def read_horizon_summary(path):
    """Columns: 1 iter, 2 time, 3 mass, 4-6 S_i, 7 S, 8 area, 9 hrms, 10 hmean, 11 meanradius,
    12 minradius (header line of the file; diagnostics.md section 10)."""
    with open(path) as fh:
        head = fh.readline()
    names = [m.group(2) for m in re.finditer(r"(\d+):(\S+)", head)]
    rows = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            rows.append([float(v) for v in line.split()])
    return names, np.array(rows) if rows else np.zeros((0, len(names)))


def read_tabout(path):
    """AthenaK table output of a line: '# Athena++ data at time=...', column names line,
    rows gid i x1v values..."""
    with open(path) as fh:
        l1 = fh.readline()
        l2 = fh.readline()
    t = float(re.search(r"time=\s*([0-9eE+.\-]+)", l1).group(1))
    names = l2.lstrip("#").split()
    d = np.loadtxt(path, comments="#", ndmin=2)
    out = {n: d[:, k] for k, n in enumerate(names)}
    out["time"] = t
    return out


def tabout_series(dirpath, var):
    files = sorted(f for f in os.listdir(dirpath) if re.match(rf".*\.{var}\.\d+\.tab$", f))
    return [os.path.join(dirpath, f) for f in files]
