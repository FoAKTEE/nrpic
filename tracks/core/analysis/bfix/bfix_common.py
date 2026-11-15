"""Shared helpers of the tests of work package bfix (requests of Track B).

The tests run AthenaK cases with the executables given on the command line, into the
directory of the registered run ($NRPIC_RUN_DIR), and analyse them with core's own
reader (python/nrpic/athena_bin.py) and with Track B's packages periodic_z4c and gw_diag,
read from a snapshot of its branch (default scratch/core/tmp/bfix/B, exported with
`git archive track/B-emd-gw ...`; the commit is recorded in the result files).
"""
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic import athena_bin  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

SYM = ["xx", "xy", "xz", "yy", "yz", "zz"]
PAIRS = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
B_DEFAULT = "/data/haiyangw/nrpic/scratch/core/tmp/bfix/B"


def out_dir(arg=None):
    d = arg or os.environ.get("NRPIC_RUN_DIR")
    if not d:
        raise SystemExit("no output directory: pass --out or run through nrpic-run")
    os.makedirs(d, exist_ok=True)
    return os.path.abspath(d)


def track_b(bdir):
    """Put Track B's packages on the path and return the modules used here."""
    pz = os.path.join(bdir, "tracks", "B-emd-gw", "periodic_z4c", "analysis")
    gw = os.path.join(bdir, "tracks", "B-emd-gw", "gw_diag")
    for p in (pz, gw):
        if not os.path.isdir(p):
            raise SystemExit(f"Track B snapshot not found: {p}")
        if p not in sys.path:
            sys.path.insert(0, p)
    import athena_dumps
    import predict_lw
    import refsol
    from gwdiag import analytic, grid, readers, tt, weyl
    return {"ad": athena_dumps, "pl": predict_lw, "rs": refsol, "tt": tt, "weyl": weyl,
            "readers": readers, "grid": grid, "analytic": analytic,
            "pz": os.path.dirname(pz), "gw": gw}


def run_athena(exe, inp, rundir, overrides=(), timeout=None):
    """One AthenaK run in rundir (created); returns a record with status and wall time."""
    os.makedirs(rundir, exist_ok=True)
    cmd = [exe, "-i", inp, "-d", rundir] + list(overrides)
    t0 = time.time()
    env = dict(os.environ, OMP_NUM_THREADS="1")
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        p = subprocess.run(cmd, cwd=rundir, stdout=log, stderr=subprocess.STDOUT,
                           timeout=timeout, env=env)
    return {"rundir": rundir, "cmd": cmd, "status": p.returncode,
            "wall_s": time.time() - t0}


def run_many(jobs, nproc=8):
    """jobs: dict name -> (exe, inp, rundir, overrides). Runs them nproc at a time and
    returns dict name -> record. Stops with an error if a run fails."""
    recs = {}
    with cf.ThreadPoolExecutor(max_workers=nproc) as ex:
        futs = {ex.submit(run_athena, *args): name for name, args in jobs.items()}
        for f in cf.as_completed(futs):
            name = futs[f]
            recs[name] = f.result()
            print(f"  ran {name}: status {recs[name]['status']}, "
                  f"{recs[name]['wall_s']:.1f} s", flush=True)
    bad = [n for n, r in recs.items() if r["status"] != 0]
    if bad:
        raise SystemExit(f"AthenaK failed for: {bad}")
    return recs


def mesh_overrides(n1, n2=None, n3=None):
    n2 = n1 if n2 is None else n2
    n3 = n1 if n3 is None else n3
    return [f"mesh/nx1={n1}", f"mesh/nx2={n2}", f"mesh/nx3={n3}",
            f"meshblock/nx1={n1}", f"meshblock/nx2={n2}", f"meshblock/nx3={n3}"]


def read_hst(path):
    """History file as (names, array); rows repeated at the same time keep the last."""
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    a = np.loadtxt(path, ndmin=2)
    return names, a


# ---------------------------------------------------------------- polarization tensors

def pol_tensors(k, upstream=False):
    """e+ and ex of athenak/src/pgen/tests/z4c_linear_wave.cpp as 3x3 arrays, with the
    file's angles theta = atan2(sqrt(k1^2 + k2^2), k3), phi = atan2(k1, k2).
    upstream = True: the signs of xy and yz of the plus tensor as in upstream AthenaK."""
    k1, k2, k3 = (float(v) for v in k)
    th = np.arctan2(np.sqrt(k1*k1 + k2*k2), k3)
    ph = np.arctan2(k1, k2)
    s = -1.0 if upstream else 1.0
    axx = -np.cos(th)**2*np.cos(2*ph) - np.cos(ph)**2*np.sin(th)**2
    axy = s*0.25*(3 + np.cos(2*th))*np.sin(2*ph)
    axz = -np.cos(th)*np.sin(th)*np.sin(ph)
    ayy = np.cos(th)**2*np.cos(2*ph) - np.sin(th)**2*np.sin(ph)**2
    ayz = -s*np.cos(th)*np.sin(th)*np.cos(ph)
    azz = np.sin(th)**2
    ep = np.array([[axx, axy, axz], [axy, ayy, ayz], [axz, ayz, azz]])
    bxx = -np.cos(th)*np.sin(2*ph)
    bxy = -np.cos(th)*np.cos(2*ph)
    bxz = np.sin(th)*np.cos(ph)
    byy = np.cos(th)*np.sin(2*ph)
    byz = -np.sin(th)*np.sin(ph)
    ex = np.array([[bxx, bxy, bxz], [bxy, byy, byz], [bxz, byz, 0.0]])
    return ep, ex


def frame(k):
    """khat, theta-hat, phi-hat (usual spherical unit vectors, theta from x3, phi from
    x1 towards x2) written with the file's angles."""
    k1, k2, k3 = (float(v) for v in k)
    th = np.arctan2(np.sqrt(k1*k1 + k2*k2), k3)
    ph = np.arctan2(k1, k2)
    kh = np.array([np.sin(th)*np.sin(ph), np.sin(th)*np.cos(ph), np.cos(th)])
    tht = np.array([np.cos(th)*np.sin(ph), np.cos(th)*np.cos(ph), -np.sin(th)])
    pht = np.array([-np.cos(ph), np.sin(ph), 0.0])
    return kh, tht, pht


def exact_wave(x, y, z, t, k, amp, ampx=0.0, phx=0.0):
    """Exact linear solution: h_ij (3,3,...) = gt_ij - delta_ij and At_ij."""
    ep, ex = pol_tensors(k)
    kn = np.linalg.norm(k)
    P = 2*np.pi*(k[0]*x + k[1]*y + k[2]*z - kn*t)
    shp = np.shape(P)
    h = np.zeros((3, 3) + shp)
    A = np.zeros((3, 3) + shp)
    for a in range(3):
        for b in range(3):
            h[a, b] = amp*ep[a, b]*np.sin(P) + ampx*ex[a, b]*np.sin(P + phx)
            A[a, b] = np.pi*kn*(amp*ep[a, b]*np.cos(P) + ampx*ex[a, b]*np.cos(P + phx))
    return h, A


def z4c_from_bin(d):
    """Dict with Track B's names (chi, gxx, Axx, Khat, ...) from a `bin` dump of variable
    z4c read with athena_bin.read_bin, plus coordinate arrays x, y, z (1D)."""
    out = {"time": d["time"], "cycle": d["cycle"], "params": d["params"]}
    for n in d["variables"]:
        out[n[4:] if n.startswith("z4c_") else n] = np.asarray(d[n], dtype=np.float64)
    out["x"], out["y"], out["z"] = d["x1v"], d["x2v"], d["x3v"]
    out["xmin"], out["xmax"] = d["xmin"], d["xmax"]
    return out


def tensor(d, pre):
    """(3,3,nz,ny,nx) array of the six components pre+xx ... of a dict."""
    shp = d[pre + "xx"].shape
    T = np.empty((3, 3) + shp)
    for (a, b), s in zip(PAIRS, SYM):
        T[a, b] = T[b, a] = d[pre + s]
    return T


def mesh3(d):
    """Z, Y, X arrays (index order k, j, i) of the cell centres of a dump dict."""
    return np.meshgrid(d["z"], d["y"], d["x"], indexing="ij")


def save_json(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
        f.write("\n")


def git_rev(ref="HEAD", cwd=REPO):
    return subprocess.run(["git", "rev-parse", ref], cwd=cwd, capture_output=True,
                          text=True).stdout.strip()
