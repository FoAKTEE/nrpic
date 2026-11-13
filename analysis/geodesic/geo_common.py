"""Shared helpers for the single-test-particle geodesic campaign (analysis/geodesic/).

All paths are located relative to this file, so the scripts run from any directory.

Contents
--------
* paths: REPO, RUNS (run directories, gitignored), reference and result locations
* readers for the NRPIC outputs: <basename>.traj.bin (records of 8 doubles),
  <basename>.trajmet.bin (records of 12 doubles), <basename>.nrpic.hst (text)
* error measures: invariant errors with the exact metric, final position error in
  (r/M, theta, phi) with phi unwrapped against the exact value, pericentre detection,
  least-squares convergence order
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "python"))

from nrpic import kerr  # noqa: E402

RUNS = REPO / "runs" / "geodesic"
KERR_DIR = REPO / "problems" / "kerr"
SCHW_DIR = REPO / "problems" / "schwarzschild"
KERR_REF_JSON = KERR_DIR / "ref" / "initial_conditions.json"
SCHW_REF_JSON = SCHW_DIR / "ref" / "orbits.json"
KERR_RESULTS = KERR_DIR / "results"
SCHW_RESULTS = SCHW_DIR / "results"
FIG_DIR = REPO / "paper" / "figures"

GPU_EXE = REPO / ".work" / "build_gpu_dev" / "src" / "athena"
CPU_EXE = REPO / ".work" / "build_check" / "src" / "athena"
GPU_RUN = REPO / "scripts" / "gpu_run.sh"

# paper values (arXiv:2611.12831, Sec. III A), max relative errors (E, L_z, Q) at dt = 0.01 M
PAPER_PASSAGE = {
    "mid_ks": (2.8e-8, None, 1.3e-7),      # L_z: "retains the cyclic momentum to stored precision"
    "bsym_ks": (9.0e-8, 1.1e-8, 7.8e-7),
    "mid_lat": (2.2e-6, 5.3e-6, 5.1e-5),
    "bchol_lat": (2.0e-6, 3.8e-6, 5.3e-5),
}
# numbers from the standalone build of the same kernels (given with the task)
STANDALONE_PASSAGE = {
    "mid_ks": (2.781e-8, 0.0, 1.254e-7),
    "bsym_ks": (9.046e-8, 1.136e-8, 7.825e-7),
    "mid_lat": (2.162e-6, 5.304e-6, 5.060e-5),
    "bchol_lat": (2.046e-6, 3.788e-6, 5.289e-5),
}


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def kerr_ref():
    return load_json(KERR_REF_JSON)


def schw_ref():
    return load_json(SCHW_REF_JSON)


# ------------------------------------------------------------------------------------------
# readers
# ------------------------------------------------------------------------------------------

def read_traj(rundir, basename="geo", tag=0):
    """Trajectory of one tracked particle: dict t, x (N,3), u (N,3)."""
    d = np.fromfile(Path(rundir) / f"{basename}.traj.bin", dtype="<f8").reshape(-1, 8)
    d = d[d[:, 1] == tag]
    return dict(t=d[:, 0].copy(), x=d[:, 2:5].copy(), u=d[:, 5:8].copy())


def read_trajmet(rundir, basename="geo", tag=0):
    """Metric reconstructed at the particle (metric = mesh): t, alpha, beta (N,3), g (N,6)."""
    f = Path(rundir) / f"{basename}.trajmet.bin"
    d = np.fromfile(f, dtype="<f8").reshape(-1, 12)
    d = d[d[:, 1] == tag]
    return dict(t=d[:, 0].copy(), alpha=d[:, 2].copy(), beta=d[:, 3:6].copy(), g=d[:, 6:12].copy())


def read_hist(rundir, basename="geo"):
    """NRPIC history; returns dict of the columns used here."""
    h = np.loadtxt(Path(rundir) / f"{basename}.nrpic.hst", ndmin=2)
    return dict(t=h[:, 0], ncycle=h[:, 1].astype(int), np=h[:, 2].astype(int),
                n_excised=h[:, 16].astype(int), n_escaped=h[:, 18].astype(int),
                maxit=h[:, 20].astype(int), unconverged=h[:, 21].astype(int),
                nmb=h[:, 22].astype(int))


def hist_summary(rundir, basename="geo"):
    """Non-convergence statistics from a history written every cycle (hist_dcycle = 1)."""
    h = read_hist(rundir, basename)
    c = h["ncycle"]
    every_cycle = bool(len(c) > 1 and np.all(np.diff(c) == 1))
    return dict(ncycles=int(c[-1]), hist_every_cycle=every_cycle,
                n_unconverged_steps=int(np.sum(h["unconverged"] > 0)),
                max_iterations=int(h["maxit"].max()),
                mean_iterations=float(h["maxit"][1:].mean()) if len(c) > 1 else 0.0,
                n_particles_end=int(h["np"][-1]), n_escaped=int(h["n_escaped"][-1]),
                n_excised=int(h["n_excised"][-1]))


def run_log_info(rundir):
    """Exit status, wall time and termination message from the newest athena log."""
    rundir = Path(rundir)
    logs = sorted(rundir.glob("athena.*.log"))
    logs = [p for p in logs if not p.is_symlink()]
    if not logs:
        return dict(ok=False, reason="no log")
    txt = logs[-1].read_text(errors="replace")
    ok = "Terminating on time limit" in txt and "# exit=0" in txt
    cpu = None
    for line in txt.splitlines():
        if line.startswith("cpu time used"):
            cpu = float(line.split("=")[1])
    return dict(ok=ok, log=str(logs[-1].relative_to(REPO)), cpu_time_s=cpu,
                fatal=("FATAL" in txt), nan=("nan" in txt.lower() and "nanosleep" not in txt))


# ------------------------------------------------------------------------------------------
# error measures
# ------------------------------------------------------------------------------------------

def invariant_errors(system, x, u, a, M=1.0, ref=None, q_abs_threshold=1e-12):
    """Histories of E, L_z, Q (exact metric) and their errors relative to the initial values.

    Returns dict with arrays dE, dLz, dQ (relative unless |ref| < threshold, then absolute)
    and the maxima of their absolute values, and flags *_relative.
    """
    E, Lz, Q = kerr.invariants(system, x, u, a, M)
    E, Lz, Q = np.broadcast_to(E, x.shape[:1]), np.broadcast_to(Lz, x.shape[:1]), \
        np.broadcast_to(Q, x.shape[:1])
    if ref is None:
        ref = (E[0], Lz[0], Q[0])
    out = dict(E=E, Lz=Lz, Q=Q, ref=tuple(float(v) for v in ref))
    for name, val, r0 in zip(("E", "Lz", "Q"), (E, Lz, Q), ref):
        rel = abs(r0) > q_abs_threshold
        d = (val - r0) / abs(r0) if rel else (val - r0)
        out["d" + name] = d
        out["d" + name + "_relative"] = bool(rel)
        out["max_d" + name] = float(np.max(np.abs(d)))
    return out


def to_rthph(system, x, a):
    """(r, theta, phi) of positions in 'bl', 'ks' (identity) or 'cks' (phi_KS in (-pi, pi])."""
    x = np.asarray(x, dtype=float)
    if system == "cks":
        return kerr.cks_to_ks_position(x, a)
    return x.copy()


def unwrap_to(phi, phi_ref):
    """Add the multiple of 2 pi that brings phi closest to phi_ref."""
    return phi + 2 * np.pi * np.round((phi_ref - phi) / (2 * np.pi))


def position_error(system, x, x_exact_rthph, a):
    """Component errors (dr/M, dtheta, dphi) of position x (in `system`) against the exact
    (r, theta, phi) of the same system family ('cks' is compared in spherical KS)."""
    q = to_rthph(system, x, a)
    qe = np.asarray(x_exact_rthph, dtype=float)
    q = q.copy()
    q[..., 2] = unwrap_to(q[..., 2], qe[..., 2])
    return q - qe


def final_position_error(system, traj, x_exact_rthph, a):
    """max |component error| in (r/M, theta, phi) at the last record, and the components."""
    d = position_error(system, traj["x"][-1], x_exact_rthph, a)
    return float(np.max(np.abs(d))), d.tolist()


def radius(system, x, a):
    if system == "cks":
        return kerr.cks_radius(np.asarray(x), a)
    return np.asarray(x)[..., 0]


def local_extrema(t, r, kind="min"):
    """Parabolic refinement of the strict local minima (or maxima) of r(t) on the samples.

    Returns arrays (t_ext, r_ext)."""
    s = 1.0 if kind == "min" else -1.0
    rr = s * r
    i = np.where((rr[1:-1] < rr[:-2]) & (rr[1:-1] <= rr[2:]))[0] + 1
    te, re = [], []
    for k in i:
        t0, t1, t2 = t[k - 1], t[k], t[k + 1]
        y0, y1, y2 = rr[k - 1], rr[k], rr[k + 1]
        h1, h2 = t1 - t0, t2 - t1
        if h1 <= 0 or h2 <= 0:
            continue
        # parabola through the three points, y = y1 + b (t - t1) + c2 (t - t1)^2
        d1 = (y1 - y0) / h1
        d2 = (y2 - y1) / h2
        c2 = (d2 - d1) / (h1 + h2)
        if c2 <= 0:
            te.append(t1)
            re.append(s * y1)
            continue
        b = (d1 * h2 + d2 * h1) / (h1 + h2)
        dt = -b / (2 * c2)
        te.append(t1 + dt)
        re.append(s * (y1 + b * dt + c2 * dt * dt))
    return np.array(te), np.array(re)


def fit_order(dts, errs):
    """Least-squares slope of log(err) against log(dt); returns (order, prefactor)."""
    dts = np.asarray(dts, dtype=float)
    errs = np.asarray(errs, dtype=float)
    ok = (errs > 0) & np.isfinite(errs)
    if ok.sum() < 2:
        return float("nan"), float("nan")
    p = np.polyfit(np.log(dts[ok]), np.log(errs[ok]), 1)
    return float(p[0]), float(math.exp(p[1]))


def pairwise_orders(dts, errs):
    dts = np.asarray(dts, dtype=float)
    errs = np.asarray(errs, dtype=float)
    return [float(np.log(errs[i] / errs[i + 1]) / np.log(dts[i] / dts[i + 1]))
            for i in range(len(dts) - 1)]


def nearest_index(t, tq):
    """Index of the record whose time is closest to each tq."""
    i = np.searchsorted(t, tq)
    i = np.clip(i, 1, len(t) - 1)
    return np.where(np.abs(t[i - 1] - tq) <= np.abs(t[i] - tq), i - 1, i)


def envelope(t, y, edges):
    """max |y| over the records in each bin [edges[k], edges[k+1]) (the last bin is closed);
    returns len(edges) - 1 values."""
    y = np.abs(np.asarray(y, dtype=float))
    lo = np.searchsorted(t, edges[:-1], side="left")
    hi = np.searchsorted(t, edges[1:], side="left")
    hi[-1] = len(t)
    out = np.zeros(len(edges) - 1)
    for k in range(len(out)):
        if hi[k] > lo[k]:
            out[k] = y[lo[k]:hi[k]].max()
    return out


def reference_samples_ks(a, t_checks, x_checks, u_checks, t_samples, M=1.0):
    """Reference (r, theta, phi) in spherical KS at t_samples: DOP853 (rtol = atol = 2.5e-14,
    max step 0.1 M) restarted from the exact state at every checkpoint."""
    from nrpic import geodesic
    t_samples = np.asarray(t_samples, dtype=float)
    out = np.full((len(t_samples), 3), np.nan)
    for k in range(len(t_checks) - 1):
        t0, t1 = float(t_checks[k]), float(t_checks[k + 1])
        sel = np.where((t_samples >= t0 - 1e-12) & (t_samples < t1 - 1e-12))[0]
        if len(sel) == 0:
            continue
        te = np.r_[np.clip(t_samples[sel], t0, t1), t1]
        tr = geodesic.integrate("ks", x_checks[k], u_checks[k], t1, t0=t0, t_eval=te,
                                rtol=2.5e-14, atol=2.5e-14, a=a, M=M, max_step=0.1)
        out[sel] = tr.x[:-1]
    last = np.where(np.abs(t_samples - t_checks[-1]) < 1e-12)[0]
    out[last] = x_checks[-1]
    return out


def sampled_errors(system, a, traj, inv, t_samples, xref_ks):
    """Position error max(|dr|, |dth|, |dphi|) at t_samples (nearest record) against the
    reference (r, theta, phi), and the envelopes of |dE|, |dLz|, |dQ| in the bins between
    consecutive samples."""
    idx = nearest_index(traj["t"], t_samples)
    ok = np.isfinite(xref_ks[:, 0])
    dpos = np.full(len(t_samples), np.nan)
    if ok.any():
        d = position_error(system, traj["x"][idx[ok]], xref_ks[ok], a)
        dpos[ok] = np.max(np.abs(d), axis=1)
    out = dict(dpos=dpos, tmis=float(np.max(np.abs(traj["t"][idx] - t_samples))))
    for q in ("dE", "dLz", "dQ"):
        out[q] = envelope(traj["t"], inv[q], t_samples)
    out["x"] = traj["x"][idx]
    return out


def fmt(v, nd=3):
    """Scientific format for tables; None -> '-'."""
    if v is None:
        return "-"
    if isinstance(v, str):
        return v
    if v == 0:
        return "0"
    return f"{v:.{nd}e}"


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        raise TypeError(type(o))

    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=conv)
