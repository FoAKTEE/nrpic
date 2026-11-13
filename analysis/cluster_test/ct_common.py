"""Shared helpers of the test-particle cluster analysis (docs/results_cluster_test.md).

Run registry, readers (history, snapshots, AthenaK binary dumps, logs), exact Kerr
quantities on the snapshots and on the mesh, and the static refinement-level map of
problems/cluster_test/cluster_mesh.athinput.
"""
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "analysis", "diag"))
sys.path.insert(0, os.path.join(REPO, "athenak", "vis", "python"))
from nrpic import kerr  # noqa: E402
import common as dc  # noqa: E402

RUNS = os.path.join(REPO, "runs", "cluster_test")
FIGS = os.path.join(HERE, "figs")
CACHE = os.path.join(RUNS, "cache")
BASE = "tpc"
M = 1.0
ALPHA_EXC = 0.62
DT = 0.05
TLIM = 1000.0
# orbital period of the centre (circular, prograde, r0 = 10 M): 2 pi (r^1.5 + a)
T_ORB = {0.0: 2 * np.pi * 10 ** 1.5, 0.9: 2 * np.pi * (10 ** 1.5 + 0.9)}
SPECIES_N = {0: 100, 1: 1000, 2: 10000}


def spin_of(name):
    return float(re.search(r"_a([0-9]+\.[0-9]+)", name).group(1))


def run_dir(name):
    return os.path.join(RUNS, name)


def exists(name):
    return os.path.exists(os.path.join(run_dir(name), f"{BASE}.nrpic.hst"))


# ----------------------------------------------------------------------------------------
# readers
# ----------------------------------------------------------------------------------------
def history(name):
    return dc.read_nrpic_hst(os.path.join(run_dir(name), f"{BASE}.nrpic.hst"))


def snapshots(name):
    return sorted(glob.glob(os.path.join(run_dir(name), f"{BASE}.part.[0-9]*.bin")))


def read_snap(path):
    """(t, x[N,3], u[N,3], m[N], tag[N], species[N]) sorted by tag."""
    t, d, tag, sp = dc.read_snapshot(path)
    o = np.argsort(tag)
    return t, d[o, :3], d[o, 3:6], d[o, 6], tag[o], sp[o]


def log_info(name):
    """Throughput and termination from the latest AthenaK log of a run."""
    p = os.path.join(run_dir(name), "athena.log")
    out = dict(ok=False)
    if not os.path.exists(p):
        return out
    s = open(p).read()
    for key, pat in [("pups", r"particle-updates/cpu_second = ([0-9.eE+-]+)"),
                     ("zcps", r"zone-cycles/cpu_second = ([0-9.eE+-]+)"),
                     ("cpu", r"cpu time used\s+= ([0-9.eE+-]+)"),
                     ("ncycle", r"time=[0-9.eE+-]+ cycle=(\d+)\ntlim"),
                     ("gpu_peak", r"gpu_mem_peak_MiB=([0-9.]+)")]:
        m = re.search(pat, s)
        if m:
            out[key] = float(m.group(1))
    m = re.search(r"# cmd: (.*)", s)
    out["cmd"] = m.group(1) if m else ""
    m = re.search(r"# host=\S+ slurm_job=(\S+)", s)
    out["job"] = m.group(1) if m else ""
    out["ok"] = ("Terminating on time limit" in s) and ("# exit=0" in s)
    out["log"] = os.path.realpath(p)
    return out


def read_bin(path):
    import bin_convert
    return bin_convert.read_binary(path)


def bin_files(name, fid):
    return sorted(glob.glob(os.path.join(run_dir(name), "bin", f"{BASE}.{fid}.[0-9]*.bin")))


def bin_cells(fd, var):
    """Cell centres x, y, z, cell volume and values of `var` of every output cell
    (flattened over MeshBlocks).  In this AthenaK version mb_geometry holds the block
    bounds (x1min, x1max, x2min, x2max, x3min, x3max) and mb_index the output index range
    inside the block (ghost cells removed), which also covers slices."""
    xs, ys, zs, vol, val = [], [], [], [], []
    nmb = (fd["nx1_mb"], fd["nx2_mb"], fd["nx3_mb"])
    for b in range(fd["n_mbs"]):
        g = fd["mb_geometry"][b]
        ix = fd["mb_index"][b]
        d = [(g[2 * k + 1] - g[2 * k]) / nmb[k] for k in range(3)]
        q = np.asarray(fd["mb_data"][var][b], dtype=float)
        n3, n2, n1 = q.shape
        c = [g[2 * k] + (ix[2 * k] + np.arange(n) + 0.5) * d[k]
             for k, n in enumerate((n1, n2, n3))]
        dx1, dx2, dx3 = d
        z, y, x = np.meshgrid(c[2], c[1], c[0], indexing="ij")
        xs.append(x.ravel()); ys.append(y.ravel()); zs.append(z.ravel())
        vol.append(np.full(q.size, dx1 * dx2 * dx3)); val.append(q.ravel())
    return (np.concatenate(xs), np.concatenate(ys), np.concatenate(zs),
            np.concatenate(vol), np.concatenate(val))


# ----------------------------------------------------------------------------------------
# exact Kerr-Schild quantities
# ----------------------------------------------------------------------------------------
def sqrt_gamma(x, y, z, a):
    """sqrt(det gamma) of Cartesian Kerr-Schild: det = 1 + 2H."""
    X = np.stack([x, y, z], axis=-1)
    r = kerr.cks_radius(X, a)
    H = M * r ** 3 / (r ** 4 + a * a * z * z)
    return np.sqrt(1 + 2 * H)


def lapse(x, a):
    r = kerr.cks_radius(x, a)
    H = M * r ** 3 / (r ** 4 + a * a * x[..., 2] ** 2)
    return 1 / np.sqrt(1 + 2 * H)


def invariants(x, u, a):
    return kerr.invariants("cks", x, u, a, M)


def lorentz_W(x, u, a):
    m = kerr.adm("cks", x, a, M, derivs=False)
    return kerr.lorentz_factor(m, u)


# ----------------------------------------------------------------------------------------
# static mesh of cluster_mesh.athinput: refinement level (dx = 2^(1-level)) of a point
# ----------------------------------------------------------------------------------------
LEVEL_BOXES = [  # (level, half-widths x, y, z) after AthenaK's expansion to parent blocks
    (5, 2.0, 2.0, 2.0), (4, 4.0, 4.0, 4.0), (3, 24.0, 24.0, 8.0), (2, 32.0, 32.0, 16.0),
    (1, 64.0, 64.0, 32.0)]


def level_of(x):
    x = np.asarray(x)
    lev = np.zeros(x.shape[:-1], dtype=int)
    for L, hx, hy, hz in reversed(LEVEL_BOXES):
        inside = (np.abs(x[..., 0]) < hx) & (np.abs(x[..., 1]) < hy) & (np.abs(x[..., 2]) < hz)
        lev = np.where(inside, L, lev)
    return lev


def dx_of_level(L):
    return 2.0 ** (1 - np.asarray(L))


# ----------------------------------------------------------------------------------------
# per-run invariant histories (cached)
# ----------------------------------------------------------------------------------------
def invariant_history(name, force=False, every=1):
    """Per-particle exact-metric E, L_z, Q on every snapshot, aligned by tag.

    Returns dict(t[nt], tag[N], species[N], E0, L0, Q0 [N], E, L, Q [nt, N] with NaN after
    removal, r [nt, N] Kerr-Schild radius, x [nt, N, 3] positions (float32), alive [nt, N])."""
    os.makedirs(CACHE, exist_ok=True)
    cpath = os.path.join(CACHE, f"{name}_inv.npz")
    files = snapshots(name)[::every]
    if (not force and os.path.exists(cpath)
            and os.path.getmtime(cpath) > max(os.path.getmtime(f) for f in files)):
        z = np.load(cpath)
        return {k: z[k] for k in z.files}
    a = spin_of(name)
    t0, x0, u0, m0, tag0, sp0 = read_snap(files[0])
    N = len(tag0)
    idx = np.full(tag0.max() + 1, -1)
    idx[tag0] = np.arange(N)
    nt = len(files)
    out = dict(t=np.zeros(nt), tag=tag0, species=sp0, m=m0,
               E=np.full((nt, N), np.nan), L=np.full((nt, N), np.nan),
               Q=np.full((nt, N), np.nan), r=np.full((nt, N), np.nan),
               x=np.full((nt, N, 3), np.nan, dtype=np.float32))
    for k, f in enumerate(files):
        t, x, u, m, tag, sp = read_snap(f)
        j = idx[tag]
        E, L, Q = invariants(x, u, a)
        out["t"][k] = t
        out["E"][k, j], out["L"][k, j], out["Q"][k, j] = E, L, Q
        out["r"][k, j] = kerr.cks_radius(x, a)
        out["x"][k, j] = x
    out["alive"] = np.isfinite(out["E"])
    out["E0"], out["L0"], out["Q0"] = out["E"][0], out["L"][0], out["Q"][0]
    np.savez(cpath, **out)
    return out


def rel_err(h, key):
    """|X(t)/X(0) - 1| per particle (NaN after removal)."""
    return np.abs(h[key] / h[key + "0"][None, :] - 1.0)
