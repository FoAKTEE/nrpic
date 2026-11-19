"""Shared helpers of the package runs_ball (Track A, wave 2): the model of data set 2t,
readers of the AthenaK outputs used by the comparison (docs/FORMATS.md), and the
spherical-symmetry formulas of the invariant comparison.

Nothing here evolves anything: the evolution is AthenaK's (decision 0010). The exact
solution is expball/exact.py (A-pre-1).
"""
import glob
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(HERE)
WT = os.path.normpath(os.path.join(TRACK, "..", ".."))
sys.path.insert(0, os.path.join(TRACK, "expball"))
sys.path.insert(0, os.path.join(WT, "python"))

from expball import exact as XE, model as XM   # noqa: E402

# data set 2t (run A-emd-pbh-20261115-130609-947c898, tracks/A-emd-pbh/stage/G1/STATUS.md 3)
DATA2T = "/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898"
STEM2T = "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875"
TAB2T = os.path.join(DATA2T, STEM2T + ".tab")
LAT2T = os.path.join(DATA2T, STEM2T + "_lat38.nrp")
JSON2T = os.path.join(DATA2T, STEM2T + ".json")


def ball2t():
    """The expball model of data set 2t (same call as analysis/scouting_predictions.py)."""
    return XM.Ball.from_HRb(0.5, 1.0, XM.SmoothTopHat(1.0, 2.4, 6.0), edge_width=1.5)


def ball_from_spec(spec):
    """expball model from a specification dict (written by prep_bh.py into exact.json as
    "spec"): profile tophat | smooth_tophat, HRb, M, delta_c, R1 and R2 (areal radii in M,
    not in units of R_b), edge_width (absolute, in M). None gives data set 2t."""
    if not spec:
        return ball2t()
    cls = {"tophat": XM.TopHat, "smooth_tophat": XM.SmoothTopHat}[spec["profile"]]
    prof = cls(spec["delta_c"], spec["R1"], spec["R2"])
    return XM.Ball.from_HRb(spec["HRb"], spec.get("M", 1.0), prof, edge_width=spec["edge_width"])


def relaxed_lapse_reference(tau_tab, a_tab, rate, alpha0=1.0, t_end=80.0, dt=0.01):
    """Central lapse of the relaxed 1+log condition of core's gauge package
    (scratch/core/exe/core_gauge/READY option 1) in a homogeneous core whose scale factor
    a(tau) is tabulated (exact.json "central"): zero shift at the centre (symmetry), so
        d ln(alpha)/dt = -2 K - rate max(ln(alpha/alpha0), 0),  d tau/dt = alpha,
    K = -3 (da/dtau)/a (code sign). Classical RK4 in coordinate time from alpha = 1, tau = 0
    (the table lapse of the data); stops at t_end, when tau leaves the table or alpha < 1e-6.
    Returns arrays (t, tau, alpha)."""
    tau_tab = np.asarray(tau_tab, dtype=float)
    a_tab = np.asarray(a_tab, dtype=float)
    lna = np.log(a_tab)
    hub = np.gradient(lna, tau_tab)          # (da/dtau)/a

    def rhs(y):
        la, tau = y
        H = np.interp(tau, tau_tab, hub)
        return np.array([6.0 * H - rate * max(la - math.log(alpha0), 0.0), math.exp(la)])
    y = np.array([0.0, 0.0])
    T, TA, AL = [0.0], [0.0], [1.0]
    t = 0.0
    while t < t_end and y[1] < tau_tab[-1] and math.exp(y[0]) > 1e-6:
        k1 = rhs(y)
        k2 = rhs(y + 0.5 * dt * k1)
        k3 = rhs(y + 0.5 * dt * k2)
        k4 = rhs(y + dt * k3)
        y = y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        t += dt
        T.append(t); TA.append(y[1]); AL.append(math.exp(y[0]))
    return np.array(T), np.array(TA), np.array(AL)


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ readers
def read_hst(path):
    """Text history: array of the last record of each time (restarts append)."""
    rows = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            try:
                v = [float(t) for t in line.split()]
            except ValueError:
                continue
            rows[v[0]] = v
    if not rows:
        return np.zeros((0, 0))
    n = min(len(v) for v in rows.values())
    return np.array([rows[t][:n] for t in sorted(rows)])


def hst_columns(path):
    """Column names of a history file from its header lines ([k]=name or k:name)."""
    names = []
    with open(path) as f:
        for line in f:
            if not line.startswith("#"):
                break
            names += re.findall(r"\[\d+\]=?\s*([A-Za-z0-9_\-\.^/()]+)", line)
    return names


def read_traj_many(dirs, base="ball"):
    """Tracked particles over one or several run directories (segments of one run, in
    time order). Records of 8 (traj.bin) and 17 (trajmet.bin) doubles; a particle missing
    from a record (removed) gets NaN. Returns dict(time[nt], tag[np], x[nt,np,3],
    u[nt,np,3], alpha, beta[...,3], g[...,6], tau, E)."""
    A, B = [], []
    for d in dirs:
        fa, fb = os.path.join(d, base + ".traj.bin"), os.path.join(d, base + ".trajmet.bin")
        if not (os.path.exists(fa) and os.path.exists(fb)):
            continue
        a = np.fromfile(fa, dtype="<f8")
        b = np.fromfile(fb, dtype="<f8")
        na, nb = len(a) // 8, len(b) // 17
        n = min(na, nb)
        A.append(a[:8 * n].reshape(n, 8))
        B.append(b[:17 * n].reshape(n, 17))
    a = np.concatenate(A)
    b = np.concatenate(B)
    # a restart repeats records of times already written: keep the last of each (time, tag)
    key = np.round(a[:, 0], 12) * 1e7 + a[:, 1]
    _, last = np.unique(key[::-1], return_index=True)
    sel = len(key) - 1 - last
    a, b = a[sel], b[sel]
    times = np.unique(a[:, 0])
    tags = np.unique(a[:, 1]).astype(int)
    it = np.searchsorted(times, a[:, 0])
    ip = np.searchsorted(tags, a[:, 1].astype(int))
    nt, npart = len(times), len(tags)

    def grid(cols, src):
        out = np.full((nt, npart) + ((len(cols),) if len(cols) > 1 else ()), np.nan)
        out[it, ip] = src[:, cols] if len(cols) > 1 else src[:, cols[0]]
        return out
    return dict(time=times, tag=tags, x=grid([2, 3, 4], a), u=grid([5, 6, 7], a),
                alpha=grid([2], b), beta=grid([3, 4, 5], b), g=grid(list(range(6, 12)), b),
                tau=grid([12], b), E=grid([13], b))


def read_tab_series(dirs, file_id, base="ball"):
    """All formatted-table outputs tab/<base>.<file_id>.NNNNN.tab of the given run
    directories: list of dict(time, cycle, x1v, <variables>) sorted by cycle (later
    segments win for repeated cycles)."""
    out = {}
    for d in dirs:
        for f in sorted(glob.glob(os.path.join(d, "tab", f"{base}.{file_id}.*.tab"))):
            with open(f) as fh:
                h1 = fh.readline()
                h2 = fh.readline()
            m = re.search(r"time=\s*([-+0-9.eE]+)\s+cycle=\s*(\d+)", h1)
            if not m:
                continue
            names = h2.lstrip("#").split()
            try:
                dat = np.loadtxt(f, comments="#", ndmin=2)
            except ValueError:
                continue
            if dat.size == 0:
                continue
            rec = dict(time=float(m.group(1)), cycle=int(m.group(2)), file=f)
            for k, nm in enumerate(names):
                if k < dat.shape[1]:
                    rec[nm] = dat[:, k]
            order = np.argsort(rec["x1v"])
            for k in list(rec):
                if isinstance(rec[k], np.ndarray):
                    rec[k] = rec[k][order]
            out[rec["cycle"]] = rec
    return [out[c] for c in sorted(out)]


def read_horizon(dirs, base="ball", n=0):
    """Horizon summaries: array of rows (iter, time, mass, Sx, Sy, Sz, S, area, hrms,
    hmean, meanradius, minradius), rows with a finite mass only."""
    rows = []
    for d in dirs:
        f = os.path.join(d, f"{base}.horizon_summary_{n}.txt")
        if os.path.exists(f):
            for line in open(f):
                if line.startswith("#") or not line.strip():
                    continue
                v = [float(t) for t in line.split()]
                if len(v) >= 12 and np.isfinite(v[2]):
                    rows.append(v[:12])
    return np.array(rows) if rows else np.zeros((0, 12))


def read_snapshot(path):
    """Particle snapshot: dict(time, x[N,3], u[N,3], m[N], tag[N])."""
    with open(path, "rb") as f:
        f.read(8)
        time = float(np.frombuffer(f.read(8), dtype="<f8")[0])
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
    return dict(time=time, x=rec[:, 0:3], u=rec[:, 3:6], m=rec[:, 6], tag=tag)


# ------------------------------------------------------------------ spherical formulas
def radial_tangential(x, S):
    """Radial and tangential eigenvalues of a spherically symmetric symmetric tensor
    S[...,6] (xx, xy, xz, yy, yz, zz) at points x[...,3]: S_ij = A n_i n_j + B (d_ij - n_i n_j).
    Returns (A, B, r, n)."""
    r = np.sqrt(np.sum(x * x, axis=-1))
    n = x / r[..., None]
    xx, xy, xz, yy, yz, zz = (S[..., i] for i in range(6))
    A = (xx * n[..., 0] ** 2 + yy * n[..., 1] ** 2 + zz * n[..., 2] ** 2
         + 2.0 * (xy * n[..., 0] * n[..., 1] + xz * n[..., 0] * n[..., 2] + yz * n[..., 1] * n[..., 2]))
    B = 0.5 * (xx + yy + zz - A)
    return A, B, r, n


def areal_radius(x, g):
    """R = r sqrt(g_T) of the round sphere through x (centre at the origin)."""
    A, B, r, _ = radial_tangential(x, g)
    return r * np.sqrt(B), r, A


def misner_sharp_line(x, g, K):
    """Misner-Sharp mass along a mesh line of points x[n,3] (sorted by x1, one side of
    the centre) from gamma_ij and K_ij (code convention, K < 0 for expansion):
        m = (R/2) (1 + R^2 K_T^2 - (dR/dr)^2 / g_rr),   K_T = K^theta_theta,
    with n.grad R = -R K_T. Returns dict(r, R, m, KT, grr, dRdr, trapped)
    where trapped = (2m/R > 1) & (K_T > 0) (both null expansions negative) and
    antitrapped = (2m/R > 1) & (K_T < 0)."""
    Ag, Bg, r, _ = radial_tangential(x, g)
    AK, BK, _, _ = radial_tangential(x, K)
    R = r * np.sqrt(Bg)
    KT = BK / Bg
    # dR/dr from the derivative along the line (uniform in x1, sorted), fourth order in
    # the interior, dr/dx1 = x1/r
    x1 = x[:, 0]
    if np.any(np.diff(x1) <= 0):
        raise ValueError("line points must be sorted by x1")
    h = x1[1] - x1[0]
    dRdx = np.gradient(R, x1, edge_order=2)
    dxs = np.diff(x1)
    if dxs.max() - dxs.min() <= 1e-9 * dxs.max():
        # uniform line: fourth order in the interior
        dRdx[2:-2] = (-R[4:] + 8.0 * R[3:-1] - 8.0 * R[1:-3] + R[:-4]) / (12.0 * h)
    # a line through refinement levels keeps np.gradient's second-order non-uniform rule
    dRdr = dRdx * r / x1
    m = 0.5 * R * (1.0 + R ** 2 * KT ** 2 - dRdr ** 2 / Ag)
    c = 2.0 * m / R
    return dict(r=r, R=R, m=m, KT=KT, grr=Ag, dRdr=dRdr, compact=c,
                trapped=(c > 1.0) & (KT > 0.0), antitrapped=(c > 1.0) & (KT < 0.0))


def line_points(rec, dx, dx_fine=None, fine_half=None):
    """Cell centres of a formatted-table line output at y = z = dx/2 (slice_x2 =
    slice_x3 = 0.01 picks the cell [0, dx]). With static refinement (dx_fine, fine_half):
    cells with |x| < fine_half have the fine width and sit at y = z = dx_fine/2."""
    x1 = rec["x1v"]
    d = np.full_like(x1, float(dx))
    if dx_fine is not None and fine_half is not None:
        d = np.where(np.abs(x1) < fine_half, float(dx_fine), d)
    return np.stack([x1, 0.5 * d, 0.5 * d], axis=-1)


def tensor6(rec, prefix):
    return np.stack([rec[prefix + c] for c in ("xx", "xy", "xz", "yy", "yz", "zz")], axis=-1)


def load_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=lambda v: float(v) if np.isscalar(v) else str(v))


def finite_or_none(v):
    v = float(v)
    return v if math.isfinite(v) else None
