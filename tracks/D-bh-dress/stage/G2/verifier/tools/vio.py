"""Readers of AthenaK/NRPIC outputs for the G2 verifier, written from docs/FORMATS.md and
coord/INTERFACES/diagnostics.md (not from the package's readers).

Every function returns numpy arrays; nothing here knows about criteria.
"""
import numpy as np

# removal record columns (docs/FORMATS.md, `<base>.removed.bin`)
RT, RTAG, RSPEC, RREASON = 0, 1, 2, 3
RX = slice(4, 7)
RU = slice(7, 10)
RM, RTAU, RALPHA = 10, 11, 12
RBETA = slice(13, 16)
RW, RE, RDIST, RPERI = 16, 17, 18, 19


def read_nrp(path):
    """Particle file NRPIC001: x(N,3), u(N,3), m(N), species(N)."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRPIC001":
            raise ValueError(f"{path}: magic {magic!r}")
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        spec = np.frombuffer(f.read(4 * n), dtype="<i4")
        rest = f.read()
    if rest:
        raise ValueError(f"{path}: {len(rest)} trailing bytes")
    return rec[:, 0:3].copy(), rec[:, 3:6].copy(), rec[:, 6].copy(), spec.copy()


def read_removed(path):
    """Removal record NRPREM01: array (n, 20) in file order."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRPREM01":
            raise ValueError(f"{path}: magic {magic!r}")
        ncol = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        if ncol != 20:
            raise ValueError(f"{path}: {ncol} columns")
        raw = f.read()
    if len(raw) % (8 * ncol):
        raise ValueError(f"{path}: truncated record ({len(raw)} bytes)")
    return np.frombuffer(raw, dtype="<f8").reshape(-1, ncol).copy()


def dedupe_removed(rec):
    """Keep, for every tag, its last record in file order (a segment cut without its own
    restart file is re-run after the resumption and writes its removals again).
    Returns (records sorted by time, number of dropped records, number of times the
    record time went backwards in file order)."""
    t = rec[:, RT]
    nback = int(np.sum(np.diff(t) < 0))
    tag = rec[:, RTAG].astype(np.int64)
    # last occurrence of each tag
    rev = tag[::-1]
    _, idx_rev = np.unique(rev, return_index=True)
    keep = len(tag) - 1 - idx_rev
    out = rec[np.sort(keep)]
    out = out[np.argsort(out[:, RT], kind="stable")]
    return out, len(rec) - len(out), nback


def read_text_table(path):
    """Whitespace table with '#' comment lines anywhere (headers repeat at
    continuations). Returns a 2D float array."""
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            rows.append([float(v) for v in s.split()])
    ncol = max(len(r) for r in rows)
    rows = [r for r in rows if len(r) == ncol]
    return np.array(rows)


def read_summary(path):
    """horizon_summary: columns 1 iter, 2 time, 3 mass, 4-6 S, 7 S, 8 area, 9 hrms,
    10 hmean, 11 meanradius, 12 minradius. For a time that appears more than once
    (continuation after a restart) the last record is kept. Returns the array sorted by
    time and a boolean array 'repeat' that marks a record whose columns 3-12 are
    bit-identical to those of the record before it (failure signature of the finder:
    a failed search writes the previous surface again), or whose mass is not finite."""
    a = read_text_table(path)
    t = a[:, 1]
    # last record of each time
    rev_t = t[::-1]
    _, idx_rev = np.unique(rev_t, return_index=True)
    keep = np.sort(len(t) - 1 - idx_rev)
    a = a[keep]
    a = a[np.argsort(a[:, 1], kind="stable")]
    rep = np.zeros(len(a), bool)
    rep[1:] = np.all(a[1:, 2:12] == a[:-1, 2:12], axis=1)
    bad = ~np.isfinite(a[:, 2]) | rep
    return a, bad


def read_snapshot(path):
    """Snapshot NRPSNAP1: time, x(N,3), u(N,3), m, tag, species, tau."""
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != b"NRPSNAP1":
            raise ValueError(f"{path}: magic {magic!r}")
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        _cyc = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), "<i4")
        spec = np.frombuffer(f.read(4 * n), "<i4")
        tau = np.frombuffer(f.read(8 * n), "<f8")
    return t, rec[:, :3], rec[:, 3:6], rec[:, 6], tag.copy(), spec.copy(), tau.copy()


def read_records(path, ncol):
    """Plain float64 records (traj.bin: 8; trajmet.bin: 17)."""
    raw = np.fromfile(path, dtype="<f8")
    n = raw.size // ncol
    return raw[: n * ncol].reshape(n, ncol)
