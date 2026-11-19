#!/usr/bin/env python3
"""Readers of the AthenaK Z4c outputs of the Hills runs, and the energy of each member
relative to the large black hole (package nr_first of F-hills; tests: test_nrread.py).

Files read (formats: athenak/src/z4c/compact_object_tracker.cpp line 87,
athenak/src/z4c/fastflow.cpp lines 260-261, athenak/src/outputs/history.cpp,
athenak/src/z4c/z4c_wave_extr.cpp):
  <base>.co_<n>.txt              tracker n: iter time x y z vx vy vz (v = -beta at the
                                 tracker, tracker_mode = ode)
  <base>.horizon_summary_<n>.txt finder n: iter time mass Sx Sy Sz S area hrms hmean
                                 meanradius minradius
  <base>.z4c.user.hst            history: time dt C-norm2 H-norm2 M-norm2 ... Volume
  waveforms/rpsi4_{real,imag}_<RRRR>.txt   r psi4 modes (l, m), l = 2..8, about the origin

Restarts. The horizon summary, the history and the waveforms are opened for appending,
so a run restarted from an earlier restart file repeats rows: the readers keep the last
row of each time. The tracker file is opened with truncation (compact_object_tracker.cpp
line 78), so a restart in the same directory erases the rows of the earlier segments;
`athena_keep_trackers.sh` copies them into <rundir>/trk_keep/ before each start, and
`read_tracker_merged` joins the copies and the live file, the later segment winning
where times overlap.

Energies (units G = c = 1, coordinate quantities, gauge-dependent while the gauge settles):
  two-body energy of member i with the hole M:
      E_i = mu_i (|v_i - v_M|^2 / 2 - (M + m_i) / |x_i - x_M|),   mu_i = m_i M / (M + m_i)
  energy of member i against the barycentre of M and the other member j (the definition of
  the lead's check V5b, tracks/F-hills/stage/G0/checks/lead_checks.py lines 451-458), the
  conserved one when j stays bound to M:
      E_i^bc = mu (|v_i - v_c|^2 / 2 - (M + m_j + m_i) / |x_i - x_c|),
      x_c = (M x_M + m_j x_j) / (M + m_j),  mu = m_i (M + m_j) / (M + m_j + m_i)
  binding energy of the binary: mu_12 (|v_1 - v_2|^2 / 2 - (m_1 + m_2) / |x_1 - x_2|).
Masses may be bare masses or horizon masses (arrays over time are accepted).
"""
import glob
import os
import re

import numpy as np


# ----------------------------------------------------------------------------------------
# plain tables
# ----------------------------------------------------------------------------------------
def read_table(path):
    """Whitespace table without comment lines -> 2D float array; rows that do not parse
    (for example a row cut off by a killed job) are skipped; ragged rows are cut to the
    shortest complete width."""
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                rows.append([float(t) for t in s.split()])
            except ValueError:
                continue
    if not rows:
        return np.zeros((0, 0))
    n = max(set(len(r) for r in rows), key=lambda k: sum(len(r) == k for r in rows))
    return np.array([r for r in rows if len(r) == n])


def keep_last_per_time(a, col=0):
    """Rows of a sorted by the time column, keeping the LAST row written for each time
    (a restarted run repeats the times after its restart point)."""
    if a.size == 0:
        return a
    t = a[:, col]
    # np.unique sorts the distinct times; on the reversed array it returns the first
    # occurrence, i.e. the last row written for each time
    _, idx_rev = np.unique(t[::-1], return_index=True)
    return a[len(t) - 1 - idx_rev]


# ----------------------------------------------------------------------------------------
# trackers
# ----------------------------------------------------------------------------------------
def _tracker_dict(a):
    return {"iter": a[:, 0].astype(int), "t": a[:, 1], "x": a[:, 2:5], "v": a[:, 5:8]}


def read_tracker(path):
    """One tracker file -> dict iter, t, x (N, 3), v (N, 3)."""
    a = read_table(path)
    if a.size == 0:
        return _tracker_dict(np.zeros((0, 8)))
    return _tracker_dict(keep_last_per_time(a, col=1))


def read_tracker_merged(paths):
    """Several tracker files of one tracker, in the order they were written (oldest first):
    each later file replaces the rows of the earlier ones from its first time on."""
    out = np.zeros((0, 8))
    for p in paths:
        a = read_table(p)
        if a.size == 0:
            continue
        t0 = a[0, 1]
        out = np.vstack([out[out[:, 1] < t0], a])
    return _tracker_dict(keep_last_per_time(out, col=1)) if out.size else \
        _tracker_dict(np.zeros((0, 8)))


def tracker_files(rundir, n, base=None):
    """The copies kept by athena_keep_trackers.sh (oldest first) and the live file of
    tracker n."""
    live = glob.glob(os.path.join(rundir, f"{base or '*'}.co_{n}.txt"))
    kept = sorted(glob.glob(os.path.join(rundir, "trk_keep", "*", f"*.co_{n}.txt")))
    return kept + live


def read_trackers(rundir, base=None):
    """All trackers of a run directory -> {n: tracker dict}, segments merged."""
    ns = set()
    for p in glob.glob(os.path.join(rundir, f"{base or '*'}.co_*.txt")) + \
            glob.glob(os.path.join(rundir, "trk_keep", "*", "*.co_*.txt")):
        m = re.search(r"\.co_(\d+)\.txt$", p)
        if m:
            ns.add(int(m.group(1)))
    return {n: read_tracker_merged(tracker_files(rundir, n, base)) for n in sorted(ns)}


# ----------------------------------------------------------------------------------------
# horizons, history, waveforms
# ----------------------------------------------------------------------------------------
HORIZON_COLS = ["iter", "t", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean",
                "meanradius", "minradius"]


def read_horizon(path):
    """Horizon summary -> (dict of columns over the searches that found a horizon, number of
    searches without one). Last row of each time kept.

    A failed search writes the properties of the last successful one again (AthenaK
    z4c/fastflow.cpp: FastFlowLoop sets ah_prop only when ah_found, lines 808-822, and
    Write prints ah_prop for every search, lines 379-392), or NaN before the first success.
    So a row whose columns 3-12 equal those of the row before is a failed search."""
    a = read_table(path)
    if a.size == 0:
        return {c: np.zeros(0) for c in HORIZON_COLS}, 0
    a = keep_last_per_time(a, col=1)
    ok = np.isfinite(a[:, 2]) & (a[:, 2] > 0)
    if len(a) > 1:
        rep = np.zeros(len(a), dtype=bool)
        rep[1:] = np.all(a[1:, 2:] == a[:-1, 2:], axis=1)
        ok &= ~rep
    return {c: a[ok, i] for i, c in enumerate(HORIZON_COLS[:a.shape[1]])}, int(np.sum(~ok))


def read_horizons(rundir, base=None):
    out = {}
    for p in glob.glob(os.path.join(rundir, f"{base or '*'}.horizon_summary_*.txt")):
        n = int(re.search(r"horizon_summary_(\d+)\.txt$", p).group(1))
        out[n] = read_horizon(p)
    return dict(sorted(out.items()))


def read_hst(path):
    """Z4c history -> dict of columns by name, last record of each time kept; adds the
    norms <X^2> = X-norm2 / Volume as 'X2' for C, H, M, Z."""
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]" in line:
                names = [t.split("=")[1] for t in line[1:].split()]
    a = keep_last_per_time(read_table(path), col=0)
    d = {nm: a[:, i] for i, nm in enumerate(names[:a.shape[1]])}
    for k in ("C", "H", "M", "Z"):
        if k + "-norm2" in d and "Volume" in d:
            d[k + "2"] = d[k + "-norm2"] / d["Volume"]
    return d


def read_rpsi4(rundir, radius):
    """r psi4 modes on the sphere of the given radius -> (t, {(l, m): complex array})."""
    tag = f"{int(round(radius)):04d}"
    pr = os.path.join(rundir, "waveforms", f"rpsi4_real_{tag}.txt")
    pi = os.path.join(rundir, "waveforms", f"rpsi4_imag_{tag}.txt")
    with open(pr) as f:
        head = f.readline().split()[1:]
    labels = [h.split(":")[1] for h in head[1:]]
    re_ = keep_last_per_time(read_table(pr))
    im_ = keep_last_per_time(read_table(pi))
    n = min(len(re_), len(im_))
    t = re_[:n, 0]
    modes = {}
    for k, lab in enumerate(labels):
        l = int(lab[0])
        m = int(lab[1:])
        modes[(l, m)] = re_[:n, k + 1] + 1j * im_[:n, k + 1]
    return t, modes


def radiated_energy(t, modes, highpass_window=None):
    """Cumulative radiated energy E(t) = int (1/16 pi) sum_lm |int r psi4_lm dt|^2 dt
    [BACKGROUND formula; as three_punctures/scripts/junk_energy.py].
    highpass_window = (t0, t1): a quadratic in t fitted to each mode outside [t0, t1] is
    subtracted first (the slowly varying near-zone part of a hole off the sphere's centre),
    and the integration starts at t0 - (t1 - t0) / 4 so that the drift before the window
    does not enter. Returns (E, rate, the modes used)."""
    use = {}
    for k, z in modes.items():
        if highpass_window is not None:
            t0, t1 = highpass_window
            out = (t < t0) | (t > t1)
            cr = np.polyfit(t[out], z.real[out], 2)
            ci = np.polyfit(t[out], z.imag[out], 2)
            z = (z.real - np.polyval(cr, t)) + 1j * (z.imag - np.polyval(ci, t))
        use[k] = z
    Z = np.array(list(use.values())).T                          # (nt, nmodes)
    if highpass_window is not None:
        ts = highpass_window[0] - 0.25 * (highpass_window[1] - highpass_window[0])
        Z = np.where((t >= ts)[:, None], Z, 0.0)
    dt = np.diff(t)
    news = np.zeros_like(Z)
    news[1:] = np.cumsum(0.5 * (Z[1:] + Z[:-1]) * dt[:, None], axis=0)
    rate = np.sum(np.abs(news) ** 2, axis=1) / (16 * np.pi)
    E = np.zeros_like(t)
    E[1:] = np.cumsum(0.5 * (rate[1:] + rate[:-1]) * dt)
    return E, rate, use


# ----------------------------------------------------------------------------------------
# energies of the members
# ----------------------------------------------------------------------------------------
def _m(a, n):
    a = np.asarray(a, dtype=float)
    return np.full(n, float(a)) if a.ndim == 0 else a


def twobody_energy(xi, vi, mi, xM, vM, M):
    """Two-body energy of member i with the hole: arrays (N, 3); masses scalars or (N,)."""
    n = len(xi)
    mi, M = _m(mi, n), _m(M, n)
    dx, dv = xi - xM, vi - vM
    mu = mi * M / (mi + M)
    return mu * (0.5 * np.sum(dv * dv, 1) - (M + mi) / np.linalg.norm(dx, axis=1))


def barycentric_energy(xi, vi, mi, xM, vM, M, xj, vj, mj):
    """Energy of member i against the barycentre of the hole and member j (V5b)."""
    n = len(xi)
    mi, M, mj = _m(mi, n), _m(M, n), _m(mj, n)
    mc = M + mj
    xc = (M[:, None] * xM + mj[:, None] * xj) / mc[:, None]
    vc = (M[:, None] * vM + mj[:, None] * vj) / mc[:, None]
    dx, dv = xi - xc, vi - vc
    mu = mi * mc / (mi + mc)
    return mu * (0.5 * np.sum(dv * dv, 1) - (mc + mi) / np.linalg.norm(dx, axis=1))


def member_energies(X, V, masses, iM=2):
    """X, V: (N, 3 bodies, 3) positions and velocities of members 0, 1 and the hole iM;
    masses (3,) or (N, 3). Returns a dict of arrays (N,):
      E_<i>_M      two-body energy of member i with the hole
      E_<i>_bc     energy of member i against the barycentre of the hole and the other one
      E_bin        binding energy of the two members with each other
      r_<i>M, r_12 distances."""
    N = len(X)
    ms = np.asarray(masses, dtype=float)
    ms = np.broadcast_to(ms, (N, 3)) if ms.ndim == 1 else ms
    i0, i1 = [k for k in range(3) if k != iM]
    out = {}
    for i, j in ((i0, i1), (i1, i0)):
        out[f"E_{i}_M"] = twobody_energy(X[:, i], V[:, i], ms[:, i], X[:, iM], V[:, iM], ms[:, iM])
        out[f"E_{i}_bc"] = barycentric_energy(X[:, i], V[:, i], ms[:, i], X[:, iM], V[:, iM],
                                              ms[:, iM], X[:, j], V[:, j], ms[:, j])
        out[f"r_{i}M"] = np.linalg.norm(X[:, i] - X[:, iM], axis=1)
    m1, m2 = ms[:, i0], ms[:, i1]
    dx, dv = X[:, i0] - X[:, i1], V[:, i0] - V[:, i1]
    out["E_bin"] = m1 * m2 / (m1 + m2) * (0.5 * np.sum(dv * dv, 1)
                                          - (m1 + m2) / np.linalg.norm(dx, axis=1))
    out["r_12"] = np.linalg.norm(dx, axis=1)
    return out


def common_times(trackers, keys=None, dt=None):
    """Trackers {n: dict} -> (t, X (N, nb, 3), V (N, nb, 3)) on the times all have
    (rows of equal cycle number), or interpolated onto a grid of step dt."""
    keys = sorted(trackers) if keys is None else keys
    if dt is None:
        it = set(trackers[keys[0]]["iter"].tolist())
        for k in keys[1:]:
            it &= set(trackers[k]["iter"].tolist())
        it = np.array(sorted(it))
        sel = [np.searchsorted(trackers[k]["iter"], it) for k in keys]
        t = trackers[keys[0]]["t"][sel[0]]
        X = np.stack([trackers[k]["x"][s] for k, s in zip(keys, sel)], axis=1)
        V = np.stack([trackers[k]["v"][s] for k, s in zip(keys, sel)], axis=1)
        return t, X, V
    t0 = max(trackers[k]["t"][0] for k in keys)
    t1 = min(trackers[k]["t"][-1] for k in keys)
    t = np.arange(t0, t1 + 0.5 * dt, dt)
    X = np.stack([np.stack([np.interp(t, trackers[k]["t"], trackers[k]["x"][:, c])
                            for c in range(3)], 1) for k in keys], axis=1)
    V = np.stack([np.stack([np.interp(t, trackers[k]["t"], trackers[k]["v"][:, c])
                            for c in range(3)], 1) for k in keys], axis=1)
    return t, X, V


def velocity_from_positions(t, x, window=1.0):
    """Velocity from tracker positions: derivative at the centre of a least-squares
    quadratic over +-window/2 in time (one-sided at the ends; the quadratic removes the
    bias of the acceleration there). An alternative to the tracker's own v = -beta, which
    is the same quantity at the tracker; the fit smooths the step-to-step noise."""
    v = np.empty_like(x)
    h = 0.5 * window
    lo = np.searchsorted(t, t - h)
    hi = np.searchsorted(t, t + h, side="right")
    for k in range(len(t)):
        a, b = lo[k], hi[k]
        if b - a < 4:
            a, b = max(0, k - 2), min(len(t), k + 3)
        tt = t[a:b] - t[k]
        for c in range(x.shape[1]):
            v[k, c] = np.polyfit(tt, x[a:b, c], 2)[1]
    return v
