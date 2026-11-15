"""Shared helpers of the analysis scripts of the work package "id": run lookup by tag,
readers of the outputs of the particle module (docs/FORMATS.md)."""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
RUNS = os.path.join(WT, "tracks/core/runs")
FIGS = os.path.join(HERE, "figs")
sys.path.insert(0, os.path.join(WT, "python"))


def manifests(prefix=""):
    """{tag: manifest} of the registered runs whose tag starts with prefix; of several
    runs with one tag the latest successful one."""
    out = {}
    for f in sorted(glob.glob(os.path.join(RUNS, "*", "manifest.json"))):
        with open(f) as fh:
            m = json.load(fh)
        tag = m.get("tag", "")
        if tag.startswith(prefix) and m.get("exit_status") == 0:
            out[tag] = m
    return out


def run_meta(man):
    """JSON parameter file of the initial data of a run (the .json among its inputs)."""
    for inp in man["inputs"]:
        if inp["path"].endswith(".json"):
            with open(inp["path"]) as fh:
                return json.load(fh)
    return {}


def read_field(path):
    """Field dump: dict(time, n, E, chi[, H, Mx, My, Mz, Khat, Theta, alpha]) with
    arrays indexed [k, j, i]."""
    with open(path, "rb") as f:
        magic = f.read(8)
        time = np.frombuffer(f.read(8), dtype="<f8")[0]
        n = np.frombuffer(f.read(24), dtype="<i8")
        nc = int(n[0] * n[1] * n[2])
        shape = (int(n[2]), int(n[1]), int(n[0]))
        out = dict(time=float(time), n=tuple(int(v) for v in n))
        out["E"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shape).astype(float)
        out["chi"] = np.frombuffer(f.read(4 * nc), dtype="<f4").reshape(shape).astype(float)
        if magic == b"NRFIELD2":
            for name in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[name] = np.frombuffer(f.read(8 * nc), dtype="<f8").reshape(shape)
    return out


def cell_radius(n, half):
    """Radius of the cell centres of the uniform mesh [-half, half]^3, [k, j, i]."""
    x = [-half + (np.arange(m) + 0.5) * (2.0 * half / m) for m in n]
    return np.sqrt(x[2][:, None, None] ** 2 + x[1][None, :, None] ** 2 + x[0][None, None, :] ** 2)


def read_hst(path):
    """Text history: array of the last record of each time."""
    rows = {}
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            v = [float(t) for t in line.split()]
            rows[v[0]] = v
    return np.array([rows[t] for t in sorted(rows)])


def read_traj(rundir, base="ball"):
    """Tracked particles: dict(time[nt], tag[np], x[nt,np,3], u[nt,np,3], alpha[nt,np],
    beta[nt,np,3], g[nt,np,6] (xx, xy, xz, yy, yz, zz), tau[nt,np], E[nt,np]).
    Particles that left the run are dropped from all records."""
    a = np.fromfile(os.path.join(rundir, base + ".traj.bin"), dtype="<f8").reshape(-1, 8)
    b = np.fromfile(os.path.join(rundir, base + ".trajmet.bin"), dtype="<f8").reshape(-1, 17)
    times = np.unique(a[:, 0])
    tags = np.unique(a[:, 1]).astype(int)
    nt, npart = len(times), len(tags)
    if len(a) != nt * npart:
        raise ValueError("tracked particles were removed during the run")
    order = np.lexsort((a[:, 1], a[:, 0]))
    a = a[order].reshape(nt, npart, 8)
    b = b[order].reshape(nt, npart, 17)
    return dict(time=times, tag=tags, x=a[:, :, 2:5], u=a[:, :, 5:8], alpha=b[:, :, 2],
                beta=b[:, :, 3:6], g=b[:, :, 6:12], tau=b[:, :, 12], E=b[:, :, 13])


def areal_radius(x, g):
    """Areal radius of the sphere through a particle at x[...,3] in a spherically
    symmetric metric g[...,6] about the origin: R = r sqrt(g_T), g_T the tangential
    eigenvalue (trace minus radial component, halved).  Also returns r and g_rr."""
    r = np.sqrt(np.sum(x * x, axis=-1))
    n = x / r[..., None]
    gxx, gxy, gxz, gyy, gyz, gzz = (g[..., i] for i in range(6))
    grr = (gxx * n[..., 0] ** 2 + gyy * n[..., 1] ** 2 + gzz * n[..., 2] ** 2
           + 2.0 * (gxy * n[..., 0] * n[..., 1] + gxz * n[..., 0] * n[..., 2]
                    + gyz * n[..., 1] * n[..., 2]))
    gt = 0.5 * (gxx + gyy + gzz - grr)
    return r * np.sqrt(gt), r, grr


def read_snapshot(path):
    """Snapshot: dict(time, x[N,3], u[N,3], m[N], tag[N], tau[N])."""
    with open(path, "rb") as f:
        f.read(8)
        time = np.frombuffer(f.read(8), dtype="<f8")[0]
        n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
        f.read(8)
        rec = np.frombuffer(f.read(56 * n), dtype="<f8").reshape(n, 7)
        tag = np.frombuffer(f.read(4 * n), dtype="<i4")
        f.read(4 * n)
        tau = np.frombuffer(f.read(8 * n), dtype="<f8")
    return dict(time=float(time), x=rec[:, 0:3], u=rec[:, 3:6], m=rec[:, 6], tag=tag, tau=tau)
