"""Readers of the G1 verifier of F-hills, written without the packages' readers.

Formats read (AthenaK output of the runs, as found in the files):
- tracker  ``hills.co_<n>.txt``: '#' header, columns iter time x y z vx vy vz;
- horizon summary ``hills.horizon_summary_<n>.txt``: '#' header, columns
  stage time mass Sx Sy Sz S area hrms hmean meanradius minradius;
- history ``hills.z4c.user.hst``: '#' lines (repeated at every continuation), columns named in
  the '[k]=name' header;
- waveforms ``waveforms/rpsi4_{real,imag}_<RRRR>.txt``: '#' header, time then modes.

Rules of the join (stated here, tested in vtest.py):
- a file of a later segment supersedes everything an earlier file holds from the later file's
  first time on (the later segment restarted from a restart file at that time);
- where both hold the same time, the positions are compared and the largest difference is
  reported (overlap check); times are matched on a 2^-20 grid (all output times are dyadic).
"""
import math
import os

import numpy as np

TKEY = 2.0 ** 20


def _tkey(t):
    return np.rint(np.asarray(t) * TKEY).astype(np.int64)


def read_numeric(path, ncol=None):
    """Numeric rows of a text file; '#' and blank lines skipped anywhere. Rows whose length
    differs from the first data row are dropped and counted."""
    rows, bad = [], 0
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if ncol is None:
                ncol = len(parts)
            if len(parts) != ncol:
                bad += 1
                continue
            rows.append([float(p) for p in parts])
    a = np.array(rows, dtype=float).reshape(-1, ncol if ncol else 0)
    return a, bad


def read_tracker(path):
    a, bad = read_numeric(path, 8)
    order = np.argsort(a[:, 1], kind="stable")
    return a[order]


def join_segments(arrays, names=None, tcol=1, xcols=(2, 3, 4)):
    """Join arrays (oldest first) with 'later supersedes from its first time'.
    Returns (joined, overlaps) where overlaps lists for each pair (earlier, later) holding a
    common time: n common, max |dx| (Euclidean over xcols), dx at the first common time."""
    names = names or [str(i) for i in range(len(arrays))]
    overlaps = []
    for j in range(1, len(arrays)):
        kj = _tkey(arrays[j][:, tcol])
        for i in range(j):
            ki = _tkey(arrays[i][:, tcol])
            common, ii, jj = np.intersect1d(ki, kj, return_indices=True)
            if len(common) == 0:
                continue
            d = np.sqrt(((arrays[i][ii][:, list(xcols)] - arrays[j][jj][:, list(xcols)]) ** 2).sum(1))
            overlaps.append({"earlier": names[i], "later": names[j], "n_common": int(len(common)),
                             "t_from": float(arrays[j][jj[0], tcol]),
                             "t_to": float(arrays[j][jj[-1], tcol]),
                             "max_dx": float(d.max()), "dx_first": float(d[0])})
    # build the join: walk from the newest file backwards
    pieces = []
    t_cut = math.inf
    for a in reversed(arrays):
        if len(a) == 0:
            continue
        keep = a[a[:, tcol] < t_cut]
        pieces.append(keep)
        t_cut = min(t_cut, a[0, tcol])
    joined = np.concatenate(list(reversed(pieces))) if pieces else np.zeros((0, arrays[0].shape[1]))
    joined = joined[np.argsort(joined[:, tcol], kind="stable")]
    return joined, overlaps


def gaps(t):
    dt = np.diff(t)
    if len(dt) == 0:
        return {"t_first": float(t[0]) if len(t) else None, "t_last": float(t[-1]) if len(t) else None,
                "n": int(len(t)), "max_step": None, "min_step": None, "t_at_max": None}
    k = int(np.argmax(dt))
    return {"t_first": float(t[0]), "t_last": float(t[-1]), "n": int(len(t)),
            "max_step": float(dt.max()), "min_step": float(dt.min()), "t_at_max": float(t[k])}


def kept_copies(rundir, name):
    """Kept tracker copies (oldest first, by the UTC stamp in the directory name) + live file."""
    keep = os.path.join(rundir, "trk_keep")
    files = []
    if os.path.isdir(keep):
        for stamp in sorted(os.listdir(keep)):
            p = os.path.join(keep, stamp, name)
            if os.path.exists(p):
                files.append(p)
    live = os.path.join(rundir, name)
    if os.path.exists(live):
        files.append(live)
    return files


def joined_tracker(rundirs, n):
    """Trackers of several runs (each with its own kept copies), oldest run first."""
    files = []
    for r in rundirs:
        files += kept_copies(r, f"hills.co_{n}.txt")
    arrays = [read_tracker(p) for p in files]
    names = [os.path.relpath(p, os.path.dirname(rundirs[0])) for p in files]
    joined, ov = join_segments(arrays, names)
    return joined, ov, list(zip(names, [(float(a[0, 1]), float(a[-1, 1]), len(a)) if len(a) else (None, None, 0)
                                       for a in arrays]))


def common_times(*arrays, tcol=1):
    keys = [_tkey(a[:, tcol]) for a in arrays]
    c = keys[0]
    for k in keys[1:]:
        c = np.intersect1d(c, k)
    out = []
    for a, k in zip(arrays, keys):
        idx = np.searchsorted(k, c)
        out.append(a[idx])
    return out


def minima(t, d, refine=True):
    """Local minima of a sampled d(t) (interior points), refined by a parabola through the
    three samples around each. Returns list of (t_min, d_min)."""
    out = []
    for k in range(1, len(d) - 1):
        if d[k] < d[k - 1] and d[k] <= d[k + 1]:
            if refine:
                t0, t1, t2 = t[k - 1], t[k], t[k + 1]
                y0, y1, y2 = d[k - 1], d[k], d[k + 1]
                den = (t0 - t1) * (t0 - t2) * (t1 - t2)
                A = (t2 * (y1 - y0) + t1 * (y0 - y2) + t0 * (y2 - y1)) / den
                B = (t2 * t2 * (y0 - y1) + t1 * t1 * (y2 - y0) + t0 * t0 * (y1 - y2)) / den
                C = (t1 * t2 * (t1 - t2) * y0 + t2 * t0 * (t2 - t0) * y1 + t0 * t1 * (t0 - t1) * y2) / den
                if A > 0:
                    tm = -B / (2 * A)
                    out.append((float(tm), float(C - B * B / (4 * A))))
                    continue
            out.append((float(t[k]), float(d[k])))
    return out


def read_horizon_summary(path):
    """-> dict with arrays t, mass, ... of the rows kept (last row per time), and the failure
    count by the signature: non-finite or non-positive mass, or columns 3-12 identical as text
    to the previous kept row (a failed search rewrites the last accepted row)."""
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) != 12:
                continue
            rows.append(parts)
    # last row per time, ordered by time
    bytime = {}
    for r in rows:
        bytime[int(round(float(r[1]) * 1e4))] = r
    keys = sorted(bytime)
    kept = [bytime[k] for k in keys]
    fail = np.zeros(len(kept), dtype=bool)
    for i, r in enumerate(kept):
        m = float(r[2])
        if not math.isfinite(m) or m <= 0:
            fail[i] = True
        elif i > 0 and r[2:] == kept[i - 1][2:]:
            fail[i] = True
    a = np.array([[float(x) for x in r] for r in kept]).reshape(-1, 12)
    names = ["stage", "t", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean", "meanradius", "minradius"]
    d = {nm: a[:, i] for i, nm in enumerate(names)}
    d["failed"] = fail
    d["n_raw"] = len(rows)
    return d


def read_hst(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]" in line:
                names = [tok.split("=", 1)[1] for tok in line[1:].split() if "=" in tok]
    a, _ = read_numeric(path)
    bytime = {}
    for r in a:
        bytime[int(round(r[0] * 1e5))] = r
    a = np.array([bytime[k] for k in sorted(bytime)])
    return {nm: a[:, i] for i, nm in enumerate(names[:a.shape[1]])}, len(_raw_rows(path))


def _raw_rows(path):
    out = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
    return out


def read_wave_times(path):
    """-> (raw row count, unique times sorted) of a waveform file."""
    raw = _raw_rows(path)
    t = np.array([float(s.split()[0]) for s in raw])
    return len(raw), np.unique(np.round(t, 9))


def grid_check(times, t0, t1, dt):
    grid = np.round(np.arange(t0, t1 + 0.5 * dt, dt), 9)
    have = set(np.round(times, 9).tolist())
    missing = [float(g) for g in grid if g not in have]
    return {"n_grid": int(len(grid)), "n_missing": len(missing), "missing": missing[:20]}
