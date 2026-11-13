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
         m_escaped=19, push_maxit=20, push_unconverged=21, nmb=22,
         int_e_filt=23, int_sx_filt=24, int_sy_filt=25, int_sz_filt=26)


def read_nrpic_hst(path):
    """History of the particle module; restarts append, so keep the last record of
    each time."""
    rows = [l.split() for l in open(path) if not l.startswith("#")]
    # 23 columns up to 2026-11-13; 27 columns (filtered integrals appended) afterwards
    ncol = max((len(r) for r in rows if len(r) in (23, 27)), default=23)
    a = np.array([r + ["nan"] * (ncol - len(r)) for r in rows if len(r) in (23, 27)],
                 dtype=float)
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


# ---------------------------------------------------------------------------------------
# additions (helpers used by the newer scripts; the readers above are unchanged)
# ---------------------------------------------------------------------------------------
def parse_cli(argv, defaults=(), options=()):
    """Split ``<label>=<dir>`` arguments from ``--key value`` options.

    Returns (runs, opts): runs is a list of (label, dir); a bare directory gets its
    basename as label. ``options`` lists option names that take a value; any other
    ``--flag`` is stored as True. ``defaults`` is used when no run is given."""
    def split(a):
        if "=" not in a:
            return (os.path.basename(os.path.normpath(a)), a)
        # the label may itself contain "=": take the first split whose right-hand side
        # is an existing directory, else the first split
        pos = [i for i, ch in enumerate(a) if ch == "="]
        for p in pos:
            if os.path.isdir(run_path(a[p + 1:])):
                return (a[:p], a[p + 1:])
        return (a[:pos[0]], a[pos[0] + 1:])

    runs, opts, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            key = a[2:]
            if key in options:
                opts[key] = argv[i + 1]
                i += 2
                continue
            opts[key] = True
        else:
            runs.append(split(a))
        i += 1
    if not runs:
        runs = [split(r) for r in defaults]
    return runs, opts


def run_path(d, *parts):
    """Path inside a run directory; relative run directories are taken relative to
    the repository root when they do not exist relative to the working directory."""
    if not os.path.isabs(d) and not os.path.exists(d):
        d = os.path.join(REPO, d)
    return os.path.join(d, *parts)


def keep_last(a, keys=(0,)):
    """Rows of ``a`` unique in the columns ``keys`` (restarts append, so the last
    record of each key wins), sorted by the keys (last key varies fastest)."""
    if len(a) == 0:
        return a
    k = a[::-1][:, list(keys)]
    _, idx = np.unique(k, axis=0, return_index=True)
    return a[::-1][idx]


def read_athena_hst(path):
    """AthenaK history file (``# [1]=time [2]=dt ...`` header) as a dict of columns,
    de-duplicated in time (last record wins). Empty dict when the file is absent."""
    if not os.path.exists(path):
        return {}
    names, rows = None, []
    for line in open(path):
        if line.startswith("#"):
            if "[1]=" in line:
                names = [w.split("=", 1)[1] for w in line[1:].split() if "]=" in w]
            continue
        x = line.split()
        if names and len(x) == len(names):
            rows.append(x)
    if not rows:
        return {}
    a = keep_last(np.array(rows, dtype=float))
    return {n: a[:, i] for i, n in enumerate(names)}


def read_curv_hst(path):
    """``<base>.curv.hst``: time, max|I|, x, y, z, max E, x, y, z, file number."""
    if not os.path.exists(path):
        return np.zeros((0, 10))
    a = np.loadtxt(path, comments="#", ndmin=2)
    return keep_last(a)


def read_traj_tagged(path, ncol=8):
    """Trajectory-type file (records of ``ncol`` doubles beginning with time, tag)
    de-duplicated in (tag, time) and returned as {tag: array sorted in time}."""
    if not os.path.exists(path):
        return {}
    a = read_traj(path, ncol)
    if len(a) == 0:
        return {}
    a = keep_last(a, keys=(1, 0))
    return {int(t): a[a[:, 1] == t] for t in np.unique(a[:, 1])}


def snapshot_files(d, base):
    """Sorted list of the particle snapshot files ``<base>.part.NNNNN.bin``."""
    import glob
    return sorted(glob.glob(run_path(d, f"{base}.part.[0-9][0-9][0-9][0-9][0-9].bin")))


def snapshot_times(files):
    """Times of the snapshots without reading the particle data."""
    out = []
    for p in files:
        with open(p, "rb") as f:
            f.read(8)
            out.append(struct.unpack("d", f.read(8))[0])
    return np.array(out)


def initial_radius_by_tag(d, base, files=None):
    """{tag -> coordinate radius in the first snapshot} as a lookup array indexed by tag,
    plus the first-snapshot data (for the centre)."""
    files = files or snapshot_files(d, base)
    t0, d0, tag0, _ = read_snapshot(files[0])
    r0 = np.full(tag0.max() + 1, np.nan)
    r0[tag0] = np.sqrt((d0[:, :3] ** 2).sum(1))
    return r0


def floor_log(v, floor=1e-17):
    """Absolute values with exact zeros (and anything below ``floor``) replaced by
    ``floor`` for drawing on a log axis; returns (values, mask of floored points)."""
    v = np.abs(np.asarray(v, dtype=float))
    low = ~(v >= floor)
    return np.where(low, floor, v), low


def ks_schwarzschild(x, u, M=1.0):
    """Exact Cartesian Kerr-Schild (a = 0) quantities at positions x [N,3] for covariant
    u_i [N,3]: returns dict(alpha, W, E = alpha W - beta^i u_i, r)."""
    x = np.atleast_2d(x)
    u = np.atleast_2d(u)
    r = np.sqrt((x ** 2).sum(1))
    H = M / r
    l = x / r[:, None]
    lu = (l * u).sum(1)
    W = np.sqrt(1.0 + (u * u).sum(1) - 2.0 * H * lu ** 2 / (1.0 + 2.0 * H))
    alpha = 1.0 / np.sqrt(1.0 + 2.0 * H)
    betau = 2.0 * H * lu / (1.0 + 2.0 * H)
    return dict(alpha=alpha, W=W, E=alpha * W - betau, r=r)


def inv_sym3(gxx, gxy, gxz, gyy, gyz, gzz):
    """Inverse and determinant of symmetric 3x3 matrices given by their components."""
    det = (gxx * (gyy * gzz - gyz * gyz) - gxy * (gxy * gzz - gyz * gxz)
           + gxz * (gxy * gyz - gyy * gxz))
    uxx = (gyy * gzz - gyz * gyz) / det
    uxy = (gxz * gyz - gxy * gzz) / det
    uxz = (gxy * gyz - gxz * gyy) / det
    uyy = (gxx * gzz - gxz * gxz) / det
    uyz = (gxy * gxz - gxx * gyz) / det
    uzz = (gxx * gyy - gxy * gxy) / det
    return (uxx, uxy, uxz, uyy, uyz, uzz), det
