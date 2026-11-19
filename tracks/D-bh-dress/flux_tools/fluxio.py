"""Readers of the AthenaK outputs that the horizon-flux comparison needs (Track D, G2).

Layouts follow `docs/FORMATS.md` and `coord/INTERFACES/diagnostics.md` of branch
core/requests-adf (removal record, accretion history) and of main (history, trajectories,
snapshots, particle files, horizon finder). Every reader checks the magic bytes and the
record length and raises on a mismatch, so a layout change cannot be read silently.

    read_removed(path)          <base>.removed.bin   -> dict of arrays (20 named fields)
    read_hst(path)              <base>.nrpic.hst, <base>.acc.hst (any "[k]=name" header)
    read_horizon(path)          <base>.horizon_summary_N.txt (finder, "k:name" header)
    read_traj(path, metpath)    <base>.traj.bin (+ .trajmet.bin) -> per-tag time series
    read_snapshot(path)         <base>.part.NNNNN.bin
    read_nrp(path)              particle file *.nrp
    write_nrp(path, ...)        particle file *.nrp

Text histories written across restarts may repeat times: `dedupe` keeps the last record
of each time (FORMATS.md: "Restarts append; keep the last record of each time").
"""
import re
import struct

import numpy as np

REMOVED_FIELDS = ("time", "tag", "species", "reason", "x1", "x2", "x3", "u1", "u2", "u3",
                  "m", "tau", "alpha", "beta1", "beta2", "beta3", "W", "E", "dist", "peri")
REASONS = {1: "left the mesh", 2: "lapse below alpha_exc", 3: "inside a horizon",
           4: "state not finite"}


def read_removed(path):
    """<base>.removed.bin: 8 bytes NRPREM01, int64 20, records of 20 float64."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"NRPREM01":
        raise ValueError(f"{path}: magic {raw[:8]!r}, expected NRPREM01")
    nrec = struct.unpack("<q", raw[8:16])[0]
    if nrec != len(REMOVED_FIELDS):
        raise ValueError(f"{path}: record length {nrec}, expected {len(REMOVED_FIELDS)}")
    body = raw[16:]
    if len(body) % (8 * nrec):
        raise ValueError(f"{path}: {len(body)} bytes after the header is not a multiple "
                         f"of {8 * nrec} (truncated record)")
    a = np.frombuffer(body, dtype="<f8").reshape(-1, nrec)
    out = {k: a[:, i].copy() for i, k in enumerate(REMOVED_FIELDS)}
    for k in ("tag", "species", "reason", "peri"):
        out[k] = np.rint(out[k]).astype(np.int64)
    out["n"] = a.shape[0]
    return out


_HST_NAME = re.compile(r"\[(\d+)\]=(\S+)")
_HOR_NAME = re.compile(r"(\d+):(\S+)")


def _parse_text_table(path, pattern):
    names = None
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                found = pattern.findall(s)
                if len(found) >= 2:
                    names = [n for _, n in sorted(found, key=lambda p: int(p[0]))]
                continue
            rows.append([float(x) for x in s.split()])
    if names is None:
        raise ValueError(f"{path}: no column header")
    if not rows:
        return {n: np.zeros(0) for n in names}
    width = max(len(r) for r in rows)
    if width != len(names):
        raise ValueError(f"{path}: {width} columns, header names {len(names)}")
    a = np.array([r for r in rows if len(r) == width])
    return {n: a[:, i] for i, n in enumerate(names)}


def dedupe(cols, key="time"):
    """Keep the last record of each value of `key`, sorted by it (restart appends)."""
    t = cols[key]
    if t.size == 0:
        return cols
    # last occurrence of each time: walk backwards
    _, idx_rev = np.unique(t[::-1], return_index=True)
    idx = t.size - 1 - idx_rev
    idx = np.sort(idx)
    order = idx[np.argsort(t[idx], kind="stable")]
    return {k: v[order] for k, v in cols.items()}


def read_hst(path, unique=True):
    """Text history with a '[k]=name' header (nrpic.hst, acc.hst)."""
    cols = _parse_text_table(path, _HST_NAME)
    return dedupe(cols) if unique else cols


def read_horizon(path, unique=True, finite=True):
    """Finder summary: columns iter, time, mass, Sx, Sy, Sz, S, area, hrms, hmean,
    meanradius, minradius. `finite` drops rows where the finder had no surface (nan)."""
    cols = _parse_text_table(path, _HOR_NAME)
    if unique:
        cols = dedupe(cols)
    if finite:
        ok = np.isfinite(cols["mass"])
        cols = {k: v[ok] for k, v in cols.items()}
    return cols


TRAJ_FIELDS = ("time", "tag", "x1", "x2", "x3", "u1", "u2", "u3")
TRAJMET_FIELDS = ("time", "tag", "alpha", "beta1", "beta2", "beta3", "gxx", "gxy", "gxz",
                  "gyy", "gyz", "gzz", "tau", "E_src", "S1_src", "S2_src", "S3_src")


def read_traj(path, metpath=None):
    """Trajectories of the tracked particles. Returns {tag: dict of arrays} sorted by
    time; with `metpath` the metric at the particle is merged (same order as traj.bin) and
    the particle energy E = alpha W - beta^i u_i is computed (W from gamma^ij u_i u_j)."""
    a = np.fromfile(path, dtype="<f8")
    if a.size % 8:
        raise ValueError(f"{path}: size not a multiple of 8 doubles")
    a = a.reshape(-1, 8)
    m = None
    if metpath is not None:
        m = np.fromfile(metpath, dtype="<f8")
        if m.size % 17:
            raise ValueError(f"{metpath}: size not a multiple of 17 doubles")
        m = m.reshape(-1, 17)
        n = min(a.shape[0], m.shape[0])
        if np.any(a[:n, 0] != m[:n, 0]) or np.any(a[:n, 1] != m[:n, 1]):
            raise ValueError("traj.bin and trajmet.bin records are not aligned")
        a, m = a[:n], m[:n]
    out = {}
    tags = np.rint(a[:, 1]).astype(np.int64)
    for tag in np.unique(tags):
        sel = np.where(tags == tag)[0]
        order = sel[np.argsort(a[sel, 0], kind="stable")]
        d = {k: a[order, i] for i, k in enumerate(TRAJ_FIELDS)}
        if m is not None:
            for i, k in enumerate(TRAJMET_FIELDS):
                if k not in ("time", "tag"):
                    d[k] = m[order, i]
            d["W"], d["E"] = particle_energy(d)
        out[int(tag)] = d
    return out


def particle_energy(d):
    """W = sqrt(1 + gamma^ij u_i u_j), E = alpha W - beta^i u_i from a dict with the
    metric fields of trajmet.bin (or the removal record without gamma: not possible)."""
    g = np.empty(d["gxx"].shape + (3, 3))
    g[..., 0, 0], g[..., 0, 1], g[..., 0, 2] = d["gxx"], d["gxy"], d["gxz"]
    g[..., 1, 0], g[..., 1, 1], g[..., 1, 2] = d["gxy"], d["gyy"], d["gyz"]
    g[..., 2, 0], g[..., 2, 1], g[..., 2, 2] = d["gxz"], d["gyz"], d["gzz"]
    gi = np.linalg.inv(g)
    u = np.stack([d["u1"], d["u2"], d["u3"]], axis=-1)
    uu = np.einsum("...i,...ij,...j->...", u, gi, u)
    W = np.sqrt(1.0 + uu)
    E = d["alpha"] * W - (d["beta1"] * d["u1"] + d["beta2"] * d["u2"] + d["beta3"] * d["u3"])
    return W, E


def read_snapshot(path, peri=False):
    """<base>.part.NNNNN.bin (NRPSNAP1); `peri` reads the trailing int32 passage counts."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"NRPSNAP1":
        raise ValueError(f"{path}: magic {raw[:8]!r}")
    t, n, cyc = struct.unpack("<dqq", raw[8:32])
    off = 32
    rec = np.frombuffer(raw, "<f8", 7 * n, off).reshape(n, 7)
    off += 56 * n
    tags = np.frombuffer(raw, "<i4", n, off)
    off += 4 * n
    spec = np.frombuffer(raw, "<i4", n, off)
    off += 4 * n
    tau = np.frombuffer(raw, "<f8", n, off) if len(raw) >= off + 8 * n else None
    off += 8 * n
    pc = None
    if peri:
        pc = np.frombuffer(raw, "<i4", n, off)
    return dict(time=t, n=n, cycle=cyc, x=rec[:, :3].copy(), u=rec[:, 3:6].copy(),
                m=rec[:, 6].copy(), tag=tags.astype(np.int64), species=spec.astype(np.int64),
                tau=None if tau is None else tau.copy(), peri=pc)


def read_nrp(path):
    """Particle file: NRPIC001, int64 N, N x 7 float64 (x, u_i, m), N int32 species."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"NRPIC001":
        raise ValueError(f"{path}: magic {raw[:8]!r}")
    n = struct.unpack("<q", raw[8:16])[0]
    rec = np.frombuffer(raw, "<f8", 7 * n, 16).reshape(n, 7)
    spec = np.frombuffer(raw, "<i4", n, 16 + 56 * n)
    return dict(n=n, x=rec[:, :3].copy(), u=rec[:, 3:6].copy(), m=rec[:, 6].copy(),
                species=spec.astype(np.int64))


def write_nrp(path, x, u, m, species=None):
    x = np.asarray(x, float).reshape(-1, 3)
    u = np.asarray(u, float).reshape(-1, 3)
    m = np.broadcast_to(np.asarray(m, float), (x.shape[0],))
    n = x.shape[0]
    sp = np.zeros(n, np.int32) if species is None else np.asarray(species, np.int32)
    rec = np.empty((n, 7))
    rec[:, :3], rec[:, 3:6], rec[:, 6] = x, u, m
    with open(path, "wb") as f:
        f.write(b"NRPIC001")
        f.write(struct.pack("<q", n))
        f.write(rec.astype("<f8").tobytes())
        f.write(sp.astype("<i4").tobytes())
