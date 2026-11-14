"""Reduce the cluster with two collapsing overdensities to the arrays of
fig_overdensities.py.

This is the only script of the overdensity figure that reads the simulation outputs and
the analysis modules of the repository; the figure script reads
paper/data/overdensities.npz alone. Monoenergetic envelope (0.76 of the total mass M,
6000 macroparticles, species 0) with two Gaussian overdensities (0.12 M each, 2000
macroparticles each, species 1 at x = -3 M and species 2 at x = +3 M) on a circular
orbit in the x-y plane; they collapse to black holes A and B, which orbit inside the
envelope and accrete.

Runs (one physical evolution per mesh; a list of directories when it was restarted with
changed settings):
- finest cells M/64: runs/jeans/n1e4_v19 (one run from t = 0 on a domain of +-80 M, a
  restart chain);
- finest cells M/128: runs/jeans/n1e4_v11 (0 to 6.31 M), n1e4_v18 (6.31 M onward);
- comparison only (not drawn): the earlier M/64 run on +-256 M, n1e4_v7 (to 10.0 M),
  diag_v14b (to 13.0 M), n1e4_v17 (from 13.0 M).
Each directory is cut where the next one starts (first record of the next directory in
the same file, at the latest its restart time); within a directory records rewritten by
a later job segment are dropped (as make_tables.py does). Runs still writing are read as
far as they are complete: an unfinished last line, a snapshot or restart file shorter
than its header says, and snapshots or dumps later than the last current history record
of their directory (left over from a superseded job segment) are skipped, so the script
can be rerun at any time.

Positions of the black holes. Every restart rewrites the tracker files, so they hold
only the latest job segment, and the horizon files carry the shape about the tracker but
not the tracker itself. The positions are therefore taken from
- the trackers stored in the header of every restart dump (outputs/restart.cpp of the
  host code, step 3), and the tracker files where they exist (subsampled every 0.25 M;
  copies of earlier segments put in <run>/co_archive/ with co_0 or co_1 in their names
  are read too): these are exact;
- between these anchors, a monotone cubic (PCHIP) in the midpoint, separation, orbital
  phase and z difference of A and B through the anchors (thinned to at least 1 M apart),
  drawn only across gaps of at most 10 M in which the line from A to B turns by at most
  40 degrees and the separation stays above 1 M (otherwise the record has a gap); its
  error, from leaving out one restart dump at a time, is printed. Where the tracker files
  give a position every 0.25 M, those positions are the record and nothing is
  interpolated between them (only gaps longer than that get interpolated points);
- before the first apparent horizon (or before the first anchor after 7 M, when that is
  later), when the trackers lag the uncollapsed overdensities, the densest point of each
  overdensity's macroparticles in every snapshot (mean of the half of the species'
  particles nearest to it, iterated); its error against the anchors and the jump where
  the two sources meet are printed.

Kept, for each mesh:
- particle history (every step): particle number, removed particles, rest mass,
  smallest lapse, MeshBlock count;
- the position record of A and B: time, x, y, z, source (0 macroparticles, 1 anchor,
  2 interpolated), separation and unwrapped orbital phase; the anchors (time, positions, kind:
  0 restart dump, 1 tracker file);
- apparent-horizon searches of A, B and the common horizon: time, mass, spin vector and
  magnitude, area, mean and smallest coordinate radius (nan: no horizon found; a row
  identical in every column to the previous found row is the finder re-writing its last
  result after a failed search, flagged as stale and set to nan). Once the trackers are
  close, the searches of A and B can converge on the common horizon (warm start from the
  last surface): a row of A or B whose mass is within 1 percent of the common horizon
  found at the same search time is flagged as such and set to nan, so the curves of A and
  B hold the individual horizons only. The common-horizon search runs only while the
  trackers are closer than fastflow/merger_distance times the sum of the tracker masses
  z4c/co_<n>_mass (athenak/src/z4c/fastflow.cpp, PuncAreClose): its first row is the
  first search, and the time of the first found common horizon is an upper bound on its
  formation when that first search already finds it;
- from every complete snapshot (every 0.5 M): number and rest mass of the macroparticles
  of each species, and the densest point of each overdensity;
- from the horizon shape files: the offset of the centre of each found horizon from its
  expansion centre (the tracker), as a check that the tracker stays inside its black hole.
For the M/64 mesh also four particle snapshots (x, y and species of every particle) at
t = 0, 12 M, 50 M and the last complete snapshot; while the run has not passed 60 M the
third panel takes the snapshot half-way between 12 M and the last one. With each
snapshot: the black-hole positions from the record and the mean coordinate radius of the
horizons found within 0.25 M of it.

    python3 paper/scripts/make_data_overdensities.py
"""
import glob
import os
import re
import struct
import sys
from math import factorial
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
from common import H, read_snapshot, snapshot_files, snapshot_times  # noqa: E402

RUNS = REPO / "runs" / "jeans"
BASE = "jeans"
# (directory, time from which it is used: its restart time)
MESHES = {
    "64": [("n1e4_v19", 0.0)],
    "128": [("n1e4_v11", 0.0), ("n1e4_v18", 6.31)],
}
COMPARE = {"64old": [("n1e4_v7", 0.0), ("diag_v14b", 10.0), ("n1e4_v17", 13.0)]}
T_COMPARE = (10.5, 15.0, 20.0, 25.0, 27.0, 28.0)
DX = {"64": 1.0 / 64.0, "128": 1.0 / 128.0, "64old": 1.0 / 64.0}
TOL = 0.01                            # slack on the restart times, in M
T_END = 100.0                         # end time of the runs
LMAX = 8                              # degree of the horizon shape expansion
T_WIN = 0.25                          # largest distance in time of a horizon to a snapshot
T_LIST = np.arange(10.0, T_END + 1e-9, 10.0)   # times of the tabulated numbers
# positions
T_ON = 7.0          # trackers sit on the collapsing cores from here on (before: lag)
CO_EVERY = 0.25     # sampling of the tracker files used as anchors, in M
THIN = 1.0          # smallest spacing of the anchors of the interpolant, in M
DT_GRID = 0.125     # spacing of the interpolated record, in M
GAP_MAX = 10.0      # longest gap between anchors that is interpolated, in M
TURN_MAX = 40.0     # largest turn of the line A-B across an interpolated gap, degrees
SEP_MIN = 1.0       # no interpolation once the anchors are closer than this, in M
N_MIN = 20          # fewest macroparticles of an overdensity for its densest point
ON_COMMON = 0.01    # an A or B row within this fraction of the common-horizon mass found
                    # at the same search time is the common horizon (dropped from A, B)
# values of the original paper (from its text)
ORIG = dict(
    t_first=np.array([8.475, 8.525]),               # first apparent horizons
    t_M=np.array([10.0, 10.0, 60.0, 60.0]),         # individual horizon masses ...
    M=np.array([0.0880, 0.0877, 0.1742, 0.1761]),   # ... of A, B at 10 M and at 60 M
    t_common=64.16, M_common=0.3833, chi_common=0.5036,
    t_final=100.0, M_final=0.6474, chi_final=0.1713,
    chi_individual=1e-5)
OUT = HERE.parent / "data" / "overdensities.npz"


# ---- readers that tolerate files still being written -------------------------------
def current(t_raw):
    """Mask of the records of an appended time series that no later record supersedes:
    a job segment restarted from an earlier dump rewrites every time from its start on,
    so a record is kept only if all later records have larger times (as make_tables.py)."""
    t_raw = np.asarray(t_raw, dtype=float)
    later = np.r_[np.minimum.accumulate(t_raw[::-1])[::-1][1:], np.inf]
    return t_raw < later


def read_table(path, ncols, tcol, pad_to=None):
    """Numeric rows of a text file with a column count in ``ncols`` (comments and an
    unfinished last line skipped), without superseded records; rows shorter than
    ``pad_to`` are padded with nan."""
    width = pad_to or max(ncols)
    if not os.path.exists(path):
        return np.zeros((0, width))
    with open(path) as f:
        txt = f.read()
    lines = txt.split("\n")
    if not txt.endswith("\n"):
        lines = lines[:-1]            # the run is writing this line
    rows = []
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        x = line.split()
        if len(x) not in ncols:
            continue
        try:
            rows.append([float(v) for v in x] + [np.nan] * (width - len(x)))
        except ValueError:
            continue
    if not rows:
        return np.zeros((0, width))
    a = np.array(rows)
    return a[current(a[:, tcol])]


def read_hst(d):
    return read_table(d / f"{BASE}.nrpic.hst", (23, 27), 0, pad_to=27)


def read_co(d, i):
    """Tracker i: iteration, time, x, y, z, vx, vy, vz (the current file and any copies
    of earlier job segments in <run>/co_archive/), one record per time."""
    parts = [read_table(d / f"{BASE}.co_{i}.txt", (8,), 1)]
    for p in sorted(glob.glob(str(d / "co_archive" / f"*co_{i}*"))):
        parts.append(read_table(Path(p), (8,), 1))
    a = np.concatenate(parts)
    if len(a) == 0:
        return a
    _, idx = np.unique(np.round(a[:, 1], 9), return_index=True)
    return a[idx]


def read_ah(d, i):
    """Horizon searches: iter, time, mass, Sx, Sy, Sz, S, area, hrms, hmean, mean radius,
    smallest radius (nan where no horizon was found)."""
    return read_table(d / f"{BASE}.horizon_summary_{i}.txt", (12,), 1)


def complete_snapshots(d):
    """(times, files) of the snapshots whose size matches their particle number."""
    files = []
    for p in snapshot_files(str(d), BASE):
        try:
            with open(p, "rb") as f:
                head = f.read(32)
            n = int(np.frombuffer(head[16:24], dtype="<i8")[0])
            if len(head) == 32 and os.path.getsize(p) == 32 + 64 * n:
                files.append(p)
        except (OSError, IndexError, ValueError):
            continue
    return snapshot_times(files), files


# header of an AthenaK restart file after the parameter dump (outputs/restart.cpp step
# 1, Real = double; the layout of analysis/diag/slicemass.py): nmb, root level,
# RegionSize, two RegionIndcs, time, dt, ncycle
RST_FMT = "<ii9d19i19iddi"
RST_LEN = struct.calcsize(RST_FMT)


def rst_trackers(path, nco=2):
    """(time, positions [nco, 3]) of the puncture trackers stored in a restart dump
    (step 3: Z4c output time, then the tracker positions, then the size of one
    MeshBlock record), or None if the file is incomplete or not of this layout."""
    try:
        with open(path, "rb") as f:
            head = f.read(1 << 20)
            i = head.find(b"<par_end>")
            if i < 0:
                return None
            off = i + 10
            f.seek(off)
            v = struct.unpack(RST_FMT, f.read(RST_LEN))
            nmb, t = v[0], v[49]
            off += RST_LEN + 20 * nmb             # logical locations and costs
            f.seek(off)
            s3 = f.read(8 + 24 * nco + 8)
        ds, = struct.unpack_from("<Q", s3, 8 + 24 * nco)
        if ds == 0 or os.path.getsize(path) != off + len(s3) + nmb * ds:
            return None
        return t, np.frombuffer(s3[8:8 + 24 * nco], dtype="<f8").reshape(nco, 3).copy()
    except (OSError, struct.error, ValueError):
        return None


def stitch(parts, starts, tcol):
    """Concatenate the pieces of one evolution: piece k ends before the first record of
    piece k+1 (at the latest at its restart time), piece k+1 begins at its restart time.
    Returns the rows and the index of the piece each row comes from."""
    out, seg = [], []
    for k, a in enumerate(parts):
        t = a[:, tcol]
        keep = np.ones(len(a), dtype=bool)
        if k + 1 < len(parts):
            nxt = parts[k + 1]
            if len(nxt):
                keep &= t < nxt[0, tcol]
            keep &= t <= starts[k + 1] + TOL
        if k > 0:
            keep &= t >= starts[k] - TOL
        out.append(a[keep])
        seg.append(np.full(keep.sum(), k, dtype=np.int8))
    return np.concatenate(out), np.concatenate(seg)


def window(times, k, starts, t_last, first_next):
    """Mask of times that belong to piece k: not after the last current history record
    of its directory, before the next piece's first record and restart time, not before
    its own restart time."""
    keep = times <= t_last + TOL
    if k + 1 < len(starts):
        if first_next is not None:
            keep &= times < first_next
        keep &= times <= starts[k + 1] + TOL
    if k > 0:
        keep &= times >= starts[k] - TOL
    return keep


# ---- apparent-horizon shape (as make_data_prolate.py) ------------------------------
def ylm(l, m, theta, phi):
    """Complex spherical harmonic in the Wigner-d form of the horizon finder
    (real and imaginary part)."""
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += ((-1.0) ** k * c ** (2 * l + m - 2 * k) * s ** (2 * k - m)
              / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m)))
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(
        factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_radius(coef, theta, phi):
    """Coordinate radius r(theta, phi) about the expansion centre from the coefficients
    of the shape file (per l: a_l0, then a_lm^c, a_lm^s for m = 1 .. l)."""
    r, i = np.zeros_like(theta, dtype=float), 0
    for l in range(LMAX + 1):
        re_, _ = ylm(l, 0, theta, phi)
        r += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, theta, phi)
            r += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return r


def read_shapes(path):
    """{time: coefficient array} from the shape file (complete lines only), without the
    blocks that a later job segment rewrote."""
    if not os.path.exists(path):
        return {}
    ncoef = (LMAX + 1) ** 2
    ts, cs, t = [], [], None
    for line in open(path):
        if line.startswith("#"):
            m = re.search(r"Time\s*=\s*([-+0-9.eE]+)", line)
            t = float(m.group(1)) if m else None
        elif line.strip() and t is not None:
            x = line.split()
            if len(x) == ncoef:
                ts.append(t)
                cs.append(np.array(x, dtype=float))
            t = None
    keep = current(ts) if ts else []
    return {a: c for a, c, k in zip(ts, cs, keep) if k}


def centre_offset(coef):
    """Offset (dx, dy, dz) of the centre of the horizon surface from its expansion
    centre: half the difference of the radii in opposite directions."""
    th = np.array([np.pi / 2, np.pi / 2, np.pi / 2, np.pi / 2, 0.0, np.pi])
    ph = np.array([0.0, np.pi, np.pi / 2, 3 * np.pi / 2, 0.0, 0.0])
    r = horizon_radius(coef, th, ph)
    return np.array([r[0] - r[1], r[2] - r[3], r[4] - r[5]]) / 2.0


# ---- positions -------------------------------------------------------------------------
def densest_point(x, it=10):
    """Mean of the half of the points nearest to it, iterated from the median."""
    c = np.median(x, axis=0)
    for _ in range(it):
        r = ((x - c) ** 2).sum(1)
        c = x[np.argsort(r)[:max(8, len(x) // 2)]].mean(0)
    return c


def phase_of(A, B):
    """Unwrapped angle of the line from A to B about the z axis (nan where undefined,
    including where the two trackers coincide)."""
    dx = B - A
    phi = np.full(len(dx), np.nan)
    ok = np.isfinite(dx).all(1) & (np.abs(dx[:, :2]).sum(1) > 1e-9)
    if ok.any():
        phi[ok] = np.unwrap(np.arctan2(dx[ok, 1], dx[ok, 0]))
    return phi


def interp_ok(ta, PA):
    """For each gap between consecutive anchors: may it be interpolated?"""
    d = np.sqrt(((PA[:, 1] - PA[:, 0]) ** 2).sum(1))
    phi = phase_of(PA[:, 0], PA[:, 1])
    return ((np.diff(ta) <= GAP_MAX) & (np.degrees(np.abs(np.diff(phi))) <= TURN_MAX)
            & (np.minimum(d[:-1], d[1:]) >= SEP_MIN))


def to_polar(PA):
    """Midpoint (3), separation, unwrapped phase and z difference of A and B."""
    c = 0.5 * (PA[:, 0] + PA[:, 1])
    r = PA[:, 1] - PA[:, 0]
    return np.c_[c, np.sqrt((r ** 2).sum(1)), np.unwrap(np.arctan2(r[:, 1], r[:, 0])),
                 r[:, 2]]


def from_polar(Q):
    c, d, phi, rz = Q[:, :3], Q[:, 3], Q[:, 4], Q[:, 5]
    dxy = np.sqrt(np.maximum(d ** 2 - rz ** 2, 0.0))
    r = np.c_[dxy * np.cos(phi), dxy * np.sin(phi), rz]
    return np.stack([c - r / 2, c + r / 2], axis=1)


def thin(ta, PA, ka, dmin=THIN):
    """Anchors for the interpolant: every restart dump, and tracker-file samples at least
    dmin from the previous kept anchor (dense, lattice-rounded tracker samples next to a
    long gap make any cubic overshoot)."""
    keep, last = [], -np.inf
    for i, (t, k) in enumerate(zip(ta, ka)):
        if k == 0 or t - last >= dmin - 1e-9:
            keep.append(i)
            last = t
    if len(ta) and keep[-1] != len(ta) - 1:       # the last anchor ends the record
        if ka[keep[-1]] == 1 and ta[-1] - ta[keep[-1]] < 0.5 * dmin and len(keep) > 1:
            keep.pop()
        keep.append(len(ta) - 1)
    keep = np.array(keep, dtype=int)
    return ta[keep], PA[keep]


def interpolate(ta, PA, t):
    """Positions [len(t), 2, 3] from a monotone cubic (PCHIP) in midpoint, separation,
    phase and z difference through the anchors, one interpolant per run of consecutive
    gaps that may be interpolated; nan elsewhere (anchors themselves are returned)."""
    out = np.full((len(t), 2, 3), np.nan)
    ok = interp_ok(ta, PA) if len(ta) > 1 else np.zeros(0, dtype=bool)
    k = 0
    while k < len(ta):
        j = k
        while j < len(ok) and ok[j]:
            j += 1
        tt = ta[k:j + 1]
        if j > k:
            sel = (t >= tt[0]) & (t <= tt[-1])
            f = PchipInterpolator(tt, to_polar(PA[k:j + 1]), axis=0)
            out[sel] = from_polar(f(t[sel]))
        for m in range(k, j + 1):
            out[np.abs(t - ta[m]) < 1e-9] = PA[m]
        k = j + 1
    return out


def anchors(dirs, starts, h, h_seg):
    """Exact tracker positions: restart dumps and tracker files (every CO_EVERY M) of each
    piece, within its window. Returns times, positions [n, 2, 3] and kind (0 dump, 1 file)."""
    T, P, K = [], [], []
    cos = [[read_co(d, i) for i in (0, 1)] for d in dirs]
    for k, d in enumerate(dirs):
        hk = h[h_seg == k, 0]
        t_last = hk[-1] if len(hk) else -np.inf
        nxt = None
        if k + 1 < len(dirs):
            nh = h[h_seg == k + 1, 0]
            nxt = nh[0] if len(nh) else None
        for p in sorted(glob.glob(str(d / "rst" / f"{BASE}.*.rst"))):
            r = rst_trackers(p)
            if r is not None and window(np.array([r[0]]), k, starts, t_last, nxt)[0]:
                T.append(r[0])
                P.append(r[1])
                K.append(0)
        a, b = cos[k]
        if len(a) and len(b):
            tc, ia, ib = np.intersect1d(np.round(a[:, 1], 9), np.round(b[:, 1], 9),
                                        return_indices=True)
            sub = np.abs(tc / CO_EVERY - np.round(tc / CO_EVERY)) < 1e-6
            sub &= window(tc, k, starts, t_last, nxt)
            for m in np.where(sub)[0]:
                T.append(tc[m])
                P.append(np.array([a[ia[m], 2:5], b[ib[m], 2:5]]))
                K.append(1)
    if not T:
        return np.zeros(0), np.zeros((0, 2, 3)), np.zeros(0, dtype=int)
    T, P, K = np.array(T), np.array(P), np.array(K)
    o = np.lexsort((K, T))                       # dumps first at equal times
    T, P, K = T[o], P[o], K[o]
    _, u = np.unique(np.round(T, 6), return_index=True)
    return T[u], P[u], K[u]


def position_record(ta, PA, ka, st, est, t_first):
    """Record of the positions of A and B: the densest points of the overdensities before
    the switch time, the anchors and the interpolation between them after it."""
    on = ta >= T_ON
    t_on = ta[on][0] if on.any() else np.inf
    t_sw = max(t_first if np.isfinite(t_first) else np.inf, t_on)
    pre = st < t_sw
    t_rec = list(st[pre])
    P_rec = list(est[pre])
    src = [0] * int(pre.sum())
    if np.isfinite(t_sw):
        ta_on, PA_on, ka_on = ta[on], PA[on], ka[on]
        t_last = ta_on[-1]
        # interpolated points only inside gaps between anchors that are wider than the
        # sampling of the tracker files; where those give a position every CO_EVERY, the
        # record is those positions (an interpolated point there would be nan wherever
        # the rules of interp_ok refuse the thinned anchors, and break the record)
        grid = np.arange(t_sw, t_last, DT_GRID)
        j = np.searchsorted(ta_on, grid, side="right")
        lo = ta_on[np.clip(j - 1, 0, len(ta_on) - 1)]
        hi = ta_on[np.clip(j, 0, len(ta_on) - 1)]
        grid = grid[(hi - lo > CO_EVERY + 1e-6) | (j == 0)]
        tg = np.unique(np.r_[grid, t_sw, ta_on[ta_on >= t_sw]])
        Pg = interpolate(*thin(ta_on, PA_on, ka_on), tg)
        exact = np.isin(np.round(tg, 6), np.round(ta_on, 6))
        for i in np.where(exact)[0]:
            Pg[i] = PA_on[np.argmin(np.abs(ta_on - tg[i]))]
        t_rec += list(tg)
        P_rec += list(Pg)
        src += [1 if e else 2 for e in exact]
    t_rec, P_rec, src = np.array(t_rec), np.array(P_rec).reshape(-1, 2, 3), np.array(src)
    return t_rec, P_rec, src, t_sw


def position_checks(ta, PA, ka, st, est, t_rec, P_rec, t_sw):
    """Accuracy numbers: interpolation error from leaving out each restart dump after the switch
    time; densest point against the anchors at snapshot times; the jump at the switch."""
    on = ta >= T_ON
    ti, Pi = thin(ta[on], PA[on], ka[on])
    dumps = ta[on][ka[on] == 0]
    loo = []
    for j in range(1, len(ti) - 1):
        if ti[j] <= t_sw or not np.any(np.abs(dumps - ti[j]) < 1e-9):
            continue
        keep = np.ones(len(ti), dtype=bool)
        keep[j] = False
        p = interpolate(ti[keep], Pi[keep], np.array([ti[j]]))[0]
        if np.isfinite(p).all():
            e = np.sqrt(((p - Pi[j]) ** 2).sum(1))
            dd = (np.linalg.norm(p[1] - p[0]) - np.linalg.norm(Pi[j, 1] - Pi[j, 0]))
            loo.append((ti[j], ti[j - 1], ti[j + 1], e[0], e[1], dd))
    dens = []
    for t, P in zip(ta, PA):
        k = np.where(np.abs(st - t) < 1e-9)[0]
        if len(k) and np.isfinite(est[k[0]]).all():
            e = np.sqrt(((est[k[0]] - P) ** 2).sum(1))
            dd = np.linalg.norm(est[k[0], 1] - est[k[0], 0]) - np.linalg.norm(P[1] - P[0])
            dens.append((t, e[0], e[1], dd))
    jump = None
    if np.isfinite(t_sw):
        i = np.where(np.abs(t_rec - t_sw) < 1e-9)[0]
        fin = np.isfinite(est).all(axis=(1, 2))
        if len(i) and fin.sum() > 1 and st[fin][0] <= t_sw <= st[fin][-1]:
            e = np.array([[np.interp(t_sw, st[fin], est[fin, b, c]) for c in range(3)]
                          for b in (0, 1)])
            p = P_rec[i[0]]
            if np.isfinite(p).all():
                jump = (t_sw, np.linalg.norm(e[0] - p[0]), np.linalg.norm(e[1] - p[1]),
                        np.linalg.norm(e[1] - e[0]) - np.linalg.norm(p[1] - p[0]),
                        np.degrees(phase_of(e[None, 0], e[None, 1])[0]
                                   - phase_of(p[None, 0], p[None, 1])[0]))
    return loo, dens, jump


# ---- one run ---------------------------------------------------------------------------
def reduce_run(spec, with_snapshots=True):
    dirs = [RUNS / name for name, _ in spec]
    starts = [t for _, t in spec]
    h, h_seg = stitch([read_hst(d) for d in dirs], starts, 0)
    ah, ah_seg = zip(*[stitch([read_ah(d, i) for d in dirs], starts, 1) for i in (0, 1, 2)])
    # snapshots: the windows of the pieces
    st, sf = [], []
    snaps = [complete_snapshots(d) for d in dirs]
    for k, (t, f) in enumerate(snaps):
        hk = h[h_seg == k, 0]
        nxt = snaps[k + 1][0][0] if k + 1 < len(snaps) and len(snaps[k + 1][0]) else None
        keep = window(t, k, starts, hk[-1] if len(hk) else -np.inf, nxt)
        st.extend(t[keep])
        sf.extend(np.array(f)[keep])
    st = np.array(st)
    sn, sm = np.zeros((len(sf), 3)), np.zeros((len(sf), 3))
    est = np.full((len(sf), 2, 3), np.nan)
    if with_snapshots:
        for k, p in enumerate(sf):
            _, q, _, sp = read_snapshot(p)
            for s in range(3):
                sel = sp == s
                sn[k, s] = sel.sum()
                sm[k, s] = q[sel, 6].sum()
                if s > 0 and sel.sum() >= N_MIN:
                    est[k, s - 1] = densest_point(q[sel, :3])
    d = {"h_t": h[:, H["time"]], "h_np": h[:, H["np"]], "h_nexc": h[:, H["n_excised"]],
         "h_alpha_min": h[:, H["alpha_min"]], "h_nmb": h[:, H["nmb"]],
         "h_sum_m": h[:, H["sum_m"]], "h_seg": h_seg,
         "snap_t": st, "snap_n": sn, "snap_m": sm, "snap_dens": est,
         "restart_t": np.array(starts[1:]),
         "dirs": np.array([p.name for p in dirs])}
    cm = ah[2][np.isfinite(ah[2][:, 2])]
    c_mass = dict(zip(np.round(cm[:, 1], 6), cm[:, 2]))       # common horizon by search time
    for i, lab in enumerate("ABC"):
        a = ah[i].copy()
        # a search that fails after a success can re-write the previous result: every
        # column equal to the last found row to the last digit; counted as not found
        fi = np.where(np.isfinite(a[:, 2]))[0]
        rep = fi[1:][np.all(a[fi[1:], 2:12] == a[fi[:-1], 2:12], axis=1)]
        a[rep, 2:12] = np.nan
        d[f"ah{lab}_stale"] = np.isin(np.arange(len(a)), rep)
        if lab in "AB":
            # the search of A or B converged on the common horizon: not an individual one
            mc = np.array([c_mass.get(t, np.nan) for t in np.round(a[:, 1], 6)])
            onc = np.isfinite(a[:, 2]) & (np.abs(a[:, 2] - mc) <= ON_COMMON * mc)
            a[onc, 2:12] = np.nan
            d[f"ah{lab}_oncommon"] = onc
        d.update({f"ah{lab}_t": a[:, 1], f"ah{lab}_M": a[:, 2], f"ah{lab}_S": a[:, 6],
                  f"ah{lab}_Svec": a[:, 3:6], f"ah{lab}_area": a[:, 7],
                  f"ah{lab}_rmean": a[:, 10], f"ah{lab}_rmin": a[:, 11],
                  f"ah{lab}_seg": ah_seg[i]})
    # positions
    ta, PA, ka = anchors(dirs, starts, h, h_seg)
    firsts = [d[f"ah{lab}_t"][np.isfinite(d[f"ah{lab}_M"])] for lab in "AB"]
    t_first = min([f[0] for f in firsts if len(f)], default=np.nan)
    t_rec, P_rec, src, t_sw = position_record(ta, PA, ka, st, est, t_first)
    sep = np.sqrt(((P_rec[:, 1] - P_rec[:, 0]) ** 2).sum(1))
    d.update(anc_t=ta, anc_A=PA[:, 0], anc_B=PA[:, 1], anc_kind=ka,
             pos_t=t_rec, pos_A=P_rec[:, 0], pos_B=P_rec[:, 1], pos_src=src,
             pos_sep=sep, pos_phi=phase_of(P_rec[:, 0], P_rec[:, 1]), t_switch=t_sw,
             t_first=t_first)
    d["_checks"] = position_checks(ta, PA, ka, st, est, t_rec, P_rec, t_sw)
    # offset of each found horizon from its expansion centre (the tracker)
    for i, lab in enumerate("AB"):
        shp = {}
        for p in dirs:
            shp.update(read_shapes(p / f"{BASE}.horizon_shape_{i}.txt"))
        # shapes of individual horizons only (not stale rows, not the common horizon)
        ind = set(np.round(d[f"ah{lab}_t"][np.isfinite(d[f"ah{lab}_M"])], 6).tolist())
        ts = np.array([t for t in sorted(shp) if round(t, 6) in ind])
        off = np.array([centre_offset(shp[t]) for t in ts]) if len(ts) else np.zeros((0, 3))
        d[f"off{lab}_t"], d[f"off{lab}"] = ts, off
    return d, sf


def nearest_found(d, lab, t, win=T_WIN):
    """Mean radius of the found horizon nearest in time to t (nan if none within win)."""
    tt, M, r = d[f"ah{lab}_t"], d[f"ah{lab}_M"], d[f"ah{lab}_rmean"]
    ok = np.isfinite(M) & (np.abs(tt - t) <= win)
    if not ok.any():
        return np.nan, np.nan
    k = np.where(ok)[0][np.argmin(np.abs(tt[ok] - t))]
    return tt[k], r[k]


def position_at(d, t):
    """Positions of A and B at time t from the record (linear between record points);
    the densest points of the overdensities where the record has a gap."""
    tr, A, B = d["pos_t"], d["pos_A"], d["pos_B"]
    ok = np.isfinite(A).all(1) & np.isfinite(B).all(1)
    out = []
    for X, b in ((A, 0), (B, 1)):
        p = np.full(3, np.nan)
        if ok.sum() > 1 and tr[ok][0] <= t <= tr[ok][-1]:
            k = np.searchsorted(tr, t)
            lo, hi = max(k - 1, 0), min(k, len(tr) - 1)
            if ok[lo] and ok[hi]:
                p = np.array([np.interp(t, tr[ok], X[ok, c]) for c in range(3)])
        if not np.isfinite(p).all():
            k = np.where(np.abs(d["snap_t"] - t) < 1e-9)[0]
            if len(k):
                p = d["snap_dens"][k[0], b]
        out.append(p)
    return out


def panel_times(st):
    t_last = st[-1]
    mid = 50.0 if t_last >= 60.0 else 0.5 * (12.0 + t_last)
    return (0.0, 12.0, mid, t_last)


def main():
    data = {f"orig_{k}": v for k, v in ORIG.items()}
    data.update(t_end=T_END, t_list=T_LIST)
    checks, runs = {}, {}
    for key, spec in list(MESHES.items()) + list(COMPARE.items()):
        d, files = reduce_run(spec, with_snapshots=True)
        checks[key] = d.pop("_checks")
        runs[key] = (d, files)
        if key in MESHES:
            data.update({f"m{key}_{k}": v for k, v in d.items()})
        else:                          # comparison: horizons and positions only
            data.update({f"m{key}_{k}": d[k] for k in d if k.startswith(("ah", "pos_"))})
        print(f"M/{DX[key] ** -1:.0f} ({key}): " + ", ".join(n for n, _ in spec)
              + f"; history t = {d['h_t'][0]:g} .. {d['h_t'][-1]:g} ({len(d['h_t'])}); "
              f"{len(d['anc_t'])} position anchors ({int((d['anc_kind'] == 0).sum())} dumps), "
              f"record to {np.nanmax(d['pos_t']) if len(d['pos_t']) else np.nan:g}; "
              f"{len(d['snap_t'])} snapshots to {d['snap_t'][-1]:g}; horizons found A "
              f"{np.isfinite(d['ahA_M']).sum()}, B {np.isfinite(d['ahB_M']).sum()}, "
              f"common {np.isfinite(d['ahC_M']).sum()}")
    # particle panels (M/64)
    d64, files64 = runs["64"]
    st = d64["snap_t"]
    for j, tw in enumerate(panel_times(st)):
        k = int(np.argmin(np.abs(st - tw)))
        tk, q, _, sp = read_snapshot(files64[k])
        data[f"p{j}_t"] = tk
        data[f"p{j}_x"] = q[:, 0].astype(np.float32)
        data[f"p{j}_y"] = q[:, 1].astype(np.float32)
        data[f"p{j}_sp"] = sp.astype(np.int8)
        pA, pB = position_at(d64, tk)
        hz = []
        for lab, pos in (("A", pA), ("B", pB), ("C", 0.5 * (pA + pB))):
            t_ah, r = nearest_found(d64, lab, tk)
            hz.append([pos[0], pos[1], r, t_ah])
        data[f"p{j}_hz"] = np.array(hz)          # rows A, B, common: x, y, radius, time
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")
    summary(data, checks)


# ---- numbers for the text and the table ----------------------------------------------
def at_time(t, y, t0, win):
    if len(t) == 0:
        return np.nan
    k = int(np.argmin(np.abs(t - t0)))
    return y[k] if abs(t[k] - t0) <= win else np.nan


def rec_at(D, m, key, t0):
    """Record quantity at t0 (linear between finite record points, nan in gaps)."""
    t, y = D[f"m{m}_pos_t"], D[f"m{m}_{key}"]
    ok = np.isfinite(y)
    if ok.sum() < 2 or not (t[ok][0] - 1e-9 <= t0 <= t[ok][-1] + 1e-9):
        return np.nan
    k = np.searchsorted(t, t0)
    near = [i for i in (k - 1, k) if 0 <= i < len(t)]
    if not all(ok[i] for i in near):
        return np.nan
    return float(np.interp(t0, t[ok], y[ok]))


def found(D, m, lab):
    M = D[f"m{m}_ah{lab}_M"]
    ok = np.isfinite(M)
    return D[f"m{m}_ah{lab}_t"][ok], M[ok], D[f"m{m}_ah{lab}_S"][ok]


def gaps(t_search, M, longer=0.5):
    """Stretches without a found horizon between the first and last found search."""
    ok = np.isfinite(M)
    if ok.sum() < 2:
        return []
    tf = t_search[ok]
    return [(tf[k], tf[k + 1]) for k in np.where(np.diff(tf) > longer)[0]]


def summary(D, checks):
    print("summary:")
    print("  particle panels at " + ", ".join(f"{D[f'p{j}_t']:g} M" for j in range(4)))
    for m in ("64", "128"):
        ht = D[f"m{m}_h_t"]
        print(f"  --- M/{m} ({', '.join(D[f'm{m}_dirs'])}); history to {ht[-1]:.4f} M, "
              f"snapshots to {D[f'm{m}_snap_t'][-1]:g} M")
        # positions
        ta, ka = D[f"m{m}_anc_t"], D[f"m{m}_anc_kind"]
        dumps = ta[ka == 0]
        files = ta[ka == 1]
        print(f"      positions: densest points of the overdensities to "
              f"{D[f'm{m}_t_switch']:.4f} M (first horizon {D[f'm{m}_t_first']:.4f} M); "
              f"exact at the dumps " + ", ".join(f"{t:.3f}" for t in dumps)
              + (f" and from the tracker files {files[0]:.3f} .. {files[-1]:.3f} M"
                 if len(files) else ""))
        loo, dens, jump = checks[m]
        if jump:
            print(f"      jump where the sources meet (t = {jump[0]:.4f} M): A {jump[1]:.4f} M, "
                  f"B {jump[2]:.4f} M, separation {jump[3]:+.4f} M, phase {jump[4]:+.2f} deg")
        for t, a, b, ae, be, dd in loo:
            print(f"      interpolation without the dump at {t:.3f} (gap {a:.3f}..{b:.3f}): error "
                  f"A {ae:.4f}, B {be:.4f} M, separation {dd:+.4f} M")
        for t, ae, be, dd in dens:
            print(f"      densest point against the tracker at {t:.3f}: A {ae:.4f}, "
                  f"B {be:.4f} M, separation {dd:+.4f} M")
        sep, phi, tr = D[f"m{m}_pos_sep"], D[f"m{m}_pos_phi"], D[f"m{m}_pos_t"]
        ok = np.isfinite(sep)
        if ok.any():
            gap = np.where(~ok & (tr > D[f"m{m}_t_switch"]))[0]
            if len(gap):
                print(f"      record has gaps (no interpolation) at {len(gap)} points between "
                      f"{tr[gap[0]]:.3f} and {tr[gap[-1]]:.3f} M")
            below = np.where(ok & (sep < 1.0))[0]
            okp = np.isfinite(phi)
            orbits = (phi[okp][-1] - phi[okp][0]) / (2 * np.pi)
            print(f"      orbital phase {np.degrees(phi[okp][-1] - phi[okp][0]):.1f} deg "
                  f"({orbits:.3f} orbits, {int(np.floor(abs(orbits)))} completed) by "
                  f"{tr[okp][-1]:.3f} M (last record with distinct trackers); separation below 1 M: "
                  + (f"from t = {tr[below[0]]:.4f} M" if len(below) else "not yet")
                  + f"; smallest {sep[ok].min():.4f} M at {tr[ok][np.argmin(sep[ok])]:.4f} M")
            zA, zB = D[f"m{m}_pos_A"][ok][-1, 2], D[f"m{m}_pos_B"][ok][-1, 2]
            print(f"      z of A and B at {tr[ok][-1]:.3f} M: {zA:+.4f}, {zB:+.4f} M")
        for lab in "AB":
            tf, M, S = found(D, m, lab)
            if len(tf):
                print(f"      {lab}: first found t = {tf[0]:.4f} M, mass {M[0]:.5f}; {len(tf)} of "
                      f"{(D[f'm{m}_ah{lab}_t'] >= tf[0]).sum()} searches from the first; "
                      f"{D[f'm{m}_ah{lab}_stale'].sum()} stale; last {M[-1]:.5f} at {tf[-1]:.4f} M "
                      f"(S/M^2 {S[-1] / M[-1] ** 2:.2e}; median {np.median(S / M ** 2):.2e})")
                g = gaps(D[f"m{m}_ah{lab}_t"], D[f"m{m}_ah{lab}_M"])
                if g:
                    print(f"         stretches > 0.5 M without a found {lab}: "
                          + ", ".join(f"{a:.3f}-{b:.3f}" for a, b in g))
                onc = D[f"m{m}_ah{lab}_oncommon"]
                if onc.any():
                    print(f"         {onc.sum()} searches of {lab} found the common horizon (dropped), "
                          f"the first at t = {D[f'm{m}_ah{lab}_t'][onc][0]:.4f} M; last individual "
                          f"{lab} before the first common horizon: see below")
            else:
                print(f"      {lab}: no horizon found in {len(D[f'm{m}_ah{lab}_t'])} searches")
        tf, M, S = found(D, m, "C")
        if len(tf):
            tc0 = tf[0]
            print(f"      common horizon first found t = {tc0:.4f} M (first search of it at "
                  f"{D[f'm{m}_ahC_t'][0]:.4f} M), mass {M[0]:.5f}, S {S[0]:.5f}, "
                  f"S/M^2 {S[0] / M[0] ** 2:.4f}; last {M[-1]:.5f}, S/M^2 "
                  f"{S[-1] / M[-1] ** 2:.4f} at {tf[-1]:.4f} M; found in {len(tf)} of "
                  f"{len(D[f'm{m}_ahC_t'])} searches")
            for lab in "AB":
                ta_, Ma, Sa = found(D, m, lab)
                b = ta_ < tc0 - 1e-9
                e = np.abs(ta_ - tc0) < 1e-6
                print(f"      {lab} just before: t = {ta_[b][-1]:.4f} M, mass {Ma[b][-1]:.5f}, "
                      f"S/M^2 {Sa[b][-1] / Ma[b][-1] ** 2:.4f}"
                      + (f"; at {tc0:.4f} M: {Ma[e][0]:.5f}" if e.any() else "")
                      + f"; last individual {lab} found at {ta_[-1]:.4f} M ({Ma[-1]:.5f})")
            s0, s1 = rec_at(D, m, "pos_sep", D[f"m{m}_t_first"]), rec_at(D, m, "pos_sep", tc0)
            p0, p1 = rec_at(D, m, "pos_phi", D[f"m{m}_t_first"]), rec_at(D, m, "pos_phi", tc0)
            print(f"      separation at the first individual horizon ({D[f'm{m}_t_first']:.4f} M) "
                  f"{s0:.4f} M, at the first common horizon {s1:.4f} M; the line from A to B "
                  f"turned by {np.degrees(p1 - p0):.1f} deg ({(p1 - p0) / (2 * np.pi):.3f} turns) "
                  f"between them ({np.degrees(p1 - rec_at(D, m, 'pos_phi', 0.0)):.1f} deg from t = 0)")
            for t0 in (tc0, 60.0, 70.0, 80.0, 90.0, 100.0):
                k = np.where(np.abs(tf - t0) <= T_WIN)[0]
                if len(k):
                    k = k[np.argmin(np.abs(tf[k] - t0))]
                    print(f"         common at {tf[k]:8.4f} M: mass {M[k]:.5f}, S {S[k]:.5f}, "
                          f"S/M^2 {S[k] / M[k] ** 2:.4f}")
        else:
            print(f"      common horizon: none found ({len(D[f'm{m}_ahC_t'])} searches)")
        sep_ = D[f"m{m}_pos_sep"]
        z0 = np.where(np.isfinite(sep_) & (sep_ < 1e-9) & (D[f"m{m}_pos_t"] > D[f"m{m}_t_switch"]))[0]
        if len(z0):
            print(f"      trackers coincide from t = {D[f'm{m}_pos_t'][z0[0]]:.4f} M")
        n0 = D[f"m{m}_snap_n"][0]
        print("        t     sep   phase/deg  M_A      M_B      M_C     N_env N_A  N_B "
              "  (fractions)")
        for t0 in np.r_[[D["orig_t_first"][0]], D["t_list"]]:
            if t0 > ht[-1] + 1e-9:
                break
            s = rec_at(D, m, "pos_sep", t0)
            p = np.degrees(rec_at(D, m, "pos_phi", t0))
            ms = []
            for lab in "ABC":
                tf, M, _ = found(D, m, lab)
                mv = at_time(tf, M, t0, T_WIN)
                ms.append(f"{mv:.5f}" if np.isfinite(mv) else "   --  ")
            k = np.where(np.abs(D[f"m{m}_snap_t"] - t0) < 0.01)[0]
            ns = ""
            if len(k):
                n = D[f"m{m}_snap_n"][k[0]]
                ns = (" ".join(f"{int(v):4d}" for v in n) + "  ("
                      + " ".join(f"{v / w:.3f}" for v, w in zip(n, n0)) + ")")
            print(f"      {t0:5.1f} {s:6.3f} {p:8.2f}  " + " ".join(ms) + "  " + ns)
        nmb = D[f"m{m}_h_nmb"]
        k = int(np.argmax(nmb))
        print(f"      largest MeshBlock count {nmb[k]:.0f} at t = {ht[k]:.4f} M; now "
              f"{nmb[-1]:.0f}; particles now {D[f'm{m}_h_np'][-1]:.0f}, removed "
              f"{D[f'm{m}_h_nexc'][-1]:.0f}; smallest lapse now "
              f"{D[f'm{m}_h_alpha_min'][-1]:.4f}")
        ne = D[f"m{m}_h_nexc"]
        k0 = int(np.argmax(ne > 0))
        print(f"      first removal at t = {ht[k0]:.4f} M ({ne[k0]:.0f} particles)")
        # history across the restarts (dumps) inside the run and between directories
        hs = D[f"m{m}_h_seg"]
        for tr_ in np.r_[dumps, D[f"m{m}_restart_t"]]:
            a = np.where(ht <= tr_ + 1e-9)[0]
            b = np.where(ht > tr_ + 1e-9)[0]
            if len(a) and len(b) and a[-1] > 0:
                a, b = a[-1], b[0]
                print(f"      across t = {tr_:.4f}: np {D[f'm{m}_h_np'][a - 1]:.0f}/"
                      f"{D[f'm{m}_h_np'][a]:.0f}/{D[f'm{m}_h_np'][b]:.0f}, lapse "
                      f"{D[f'm{m}_h_alpha_min'][a]:.4f}/{D[f'm{m}_h_alpha_min'][b]:.4f}, "
                      f"blocks {nmb[a]:.0f}/{nmb[b]:.0f}, rest mass step "
                      f"{D[f'm{m}_h_sum_m'][b] - D[f'm{m}_h_sum_m'][a]:+.2e}"
                      + (" (directories)" if hs[a] != hs[b] else ""))
        for lab in "AB":
            ts, off = D[f"m{m}_off{lab}_t"], D[f"m{m}_off{lab}"]
            if len(ts):
                o = np.sqrt((off ** 2).sum(1))
                ok = np.isfinite(D[f"m{m}_ah{lab}_M"])
                r = np.interp(ts, D[f"m{m}_ah{lab}_t"][ok], D[f"m{m}_ah{lab}_rmean"][ok])
                k = int(np.argmax(o / r))
                print(f"      horizon {lab} centre from its tracker: median {np.median(o):.4f} "
                      f"M, largest {o[k]:.4f} M ({o[k] / r[k]:.2f} of the mean radius) at "
                      f"{ts[k]:.4f} M ({len(ts)} shapes)")
    # the two domains at M/64
    print("  --- M/64 on +-80 M (n1e4_v19) against the earlier run on +-256 M "
          f"(record to {np.nanmax(D['m64old_pos_t']):.3f} M)")
    print("        t   M_A new/old (diff)            M_B new/old (diff)            "
          "separation new/old (diff)")
    for t0 in T_COMPARE:
        row = f"      {t0:5.1f}"
        for lab in "AB":
            vals = [at_time(*found(D, m, lab)[:2], t0, 0.01) for m in ("64", "64old")]
            row += f"  {vals[0]:.5f}/{vals[1]:.5f} ({vals[0] - vals[1]:+.5f})"
        s = [rec_at(D, m, "pos_sep", t0) for m in ("64", "64old")]
        row += f"  {s[0]:.4f}/{s[1]:.4f} ({s[0] - s[1]:+.4f})"
        print(row)


if __name__ == "__main__":
    main()
