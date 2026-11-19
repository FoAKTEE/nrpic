"""Shared helpers of the box tests (package tracks/C-sidm/box_tests).

Particle files come from the track's own generator `collide/analysis/make_box.py`
(NumPy Philox-free draws, Poisson positions in [10, 11)^3, mirrored momenta); the code is
the release executable of core-v0.3 (read-only, main checkout). Readers: the track's
`collide/analysis/snap.py`; the collision history and the dump follow
`coord/INTERFACES/collisions.md` section 5.
"""
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRACK = os.path.dirname(PKG)
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
COLLIDE = os.path.join(TRACK, "collide")
sys.path.insert(0, os.path.join(COLLIDE, "REFERENCES"))
sys.path.insert(0, os.path.join(COLLIDE, "analysis"))
sys.path.insert(0, os.path.join(REPO, "python"))

import snap  # noqa: E402

MAIN = "/data/haiyangw/nrpic"
EXE_CPU = os.path.join(MAIN, ".work", "build_cpu_v03", "src", "athena")
EXE_GPU = os.path.join(MAIN, ".work", "build_gpu_v03", "src", "athena")
# wave 2b: core's published executables of branch core/collisions-2 (commit f46f159,
# READY in the same directory; option <particles> coll_energy = cell | particle)
EXE_CPU_C2 = os.path.join(MAIN, "scratch", "core", "exe", "core_collisions-2", "athena_cpu")
EXE_GPU_C2 = os.path.join(MAIN, "scratch", "core", "exe", "core_collisions-2", "athena_gpu")
DECK = os.path.join(PKG, "inputs", "box.athinput")
MAKE_BOX = os.path.join(COLLIDE, "analysis", "make_box.py")
X0, L = 10.0, 1.0


def outdir():
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join(MAIN, "scratch", "C-sidm", "tmp", "box_tests_manual")
    os.makedirs(d, exist_ok=True)
    return d


def make_box(rundir, kind, **kw):
    """Run the track's make_box.py into rundir/box.{nrp,json}; returns the metadata."""
    os.makedirs(rundir, exist_ok=True)
    cmd = [sys.executable, MAKE_BOX, kind, "--out", os.path.join(rundir, "box")]
    for k, v in kw.items():
        if isinstance(v, (list, tuple)):
            cmd += ["--" + k] + [repr(float(x)) for x in v]
        else:
            cmd += ["--" + k, str(v)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    with open(os.path.join(rundir, "box.json")) as fh:
        return json.load(fh)


def mesh_overrides(nx, mb=None):
    mb = nx if mb is None else mb
    return ([f"mesh/nx{d}={nx}" for d in (1, 2, 3)] +
            [f"meshblock/nx{d}={mb}" for d in (1, 2, 3)])


def run_athena(rundir, overrides=(), exe=EXE_CPU, restart=None, deck=DECK,
               log="athena.log"):
    """Run the executable in rundir (the particle file is read from there). Returns
    dict(rc, wall)."""
    os.makedirs(rundir, exist_ok=True)
    if restart is None:
        cmd = [exe, "-i", deck, "-d", rundir] + list(overrides)
    else:
        cmd = [exe, "-r", restart, "-d", rundir] + list(overrides)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(rundir, log), "w") as fh:
        fh.write(" ".join(cmd) + "\n")
        fh.flush()
        p = subprocess.run(cmd, cwd=rundir, stdout=fh, stderr=subprocess.STDOUT, env=env)
    res = dict(rc=p.returncode, wall=time.time() - t0, cmd=cmd)
    with open(os.path.join(rundir, "wall.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return res


def run_many(jobs, nproc):
    """jobs: list of (rundir, overrides, kwargs) -> list of results (same order)."""
    with ThreadPoolExecutor(max_workers=nproc) as ex:
        futs = [ex.submit(run_athena, j[0], j[1], **(j[2] if len(j) > 2 else {}))
                for j in jobs]
        return [f.result() for f in futs]


COLL_COLUMNS = ("time ncycle n_part n_cells n_tested sum_P n_coll n_updated n_trunc max_P "
                "max_nsub mean_nsub min_N mean_N max_dx_mfp sum_MW sum_Mu1 sum_Mu2 sum_Mu3 "
                "dE dP1 dP2 dP3 abs_dE abs_dP n_bad_cells sum_W sum_MW_species0 "
                "sum_M_species0 sum_MW_particles dE_particles").split()


# columns 32-36, present when <particles> coll_energy is given (either value):
# collisions.md section 5 on branch core/collisions-2
COLL_COLUMNS_EXT = COLL_COLUMNS + ["sum_MH_particles", "dH_particles", "n_noroot",
                                   "max_dlam", "n_balance"]


def coll_history(rundir, base="box"):
    """(dict name -> column array) of <base>.coll.hst. A run resumed from a restart file
    in a new directory appends records without a header: the column order of
    collisions.md section 5 (checked against the header of the fresh runs) is used,
    with 31 columns (core-v0.3, option coll_energy absent) or 36 (coll_energy given)."""
    head, h = snap.read_history(os.path.join(rundir, f"{base}.coll.hst"))
    ci = snap.history_columns(head)
    h = np.atleast_2d(h)
    if ci:
        names = [k for k, _ in sorted(ci.items(), key=lambda kv: kv[1])]
        assert names in (list(COLL_COLUMNS), list(COLL_COLUMNS_EXT)), names
    else:
        cols = COLL_COLUMNS if h.shape[1] == len(COLL_COLUMNS) else COLL_COLUMNS_EXT
        assert h.shape[1] == len(cols), h.shape
        ci = {k: i for i, k in enumerate(cols)}
    return {k: h[:, i] for k, i in ci.items()}


def nrpic_history(rundir, base="box"):
    head, h = snap.read_history(os.path.join(rundir, f"{base}.nrpic.hst"))
    ci = snap.history_columns(head)
    h = np.atleast_2d(h)
    return {k: h[:, i] for k, i in ci.items()}


def snapshots(rundir, base="box"):
    return snap.snapshots(rundir, base)


def read_dump(path):
    """Collision dump of coord/INTERFACES/collisions.md section 5: version 1 (magic
    NRPCOLD1, release core-v0.3) and version 2 (NRPCOLD2, branch core/collisions-2, when
    <particles> coll_energy is given): after the triad gauge two more int64 (energy
    mode 0 cell / 1 particle; flag 1 if the records hold the metric at the particles)
    and ten more doubles per particle record, read here as appended to the 18 of
    version 1: lapse, beta^x, beta^y, beta^z, gamma^xx, ^xy, ^xz, ^yy, ^yz, ^zz at the
    particle. Written from the interface text; the total length is checked."""
    with open(path, "rb") as fh:
        buf = fh.read()
    assert buf[:8] in (b"NRPCOLD1", b"NRPCOLD2"), buf[:8]
    version = 1 if buf[:8] == b"NRPCOLD1" else 2
    o = 8
    i64 = lambda k: (np.frombuffer(buf, "<i8", k, o), o + 8 * k)
    (n, cyc, f), o = i64(3)
    n, cyc, f = int(n), int(cyc), int(f)
    (dt, sig, w, pmax), o = np.frombuffer(buf, "<f8", 4, o), o + 32
    (model, weights, subcycle, nsub_max), o = i64(4)
    seed = int(np.frombuffer(buf, "<u8", 1, o)[0]); o += 8
    triad = int(np.frombuffer(buf, "<i8", 1, o)[0]); o += 8
    energy, pflag = -1, 0
    if version == 2:
        (energy, pflag), o = i64(2)
        energy, pflag = int(energy), int(pflag)
    nd = 18 if version == 1 else 28
    rec = np.frombuffer(buf, "<f8", nd * n, o).reshape(n, nd); o += 8 * nd * n
    irec = np.frombuffer(buf, "<i4", 7 * n, o).reshape(n, 7); o += 4 * 7 * n
    assert o == len(buf), (o, len(buf))
    out = dict(version=version, n=n, cycle=cyc, f=f, dt=float(dt), sigma=float(sig),
               w=float(w), pmax=float(pmax), model=int(model), weights=int(weights),
               subcycle=int(subcycle), nsub_max=int(nsub_max), seed=seed, triad=triad,
               energy=energy, pmetric_flag=pflag,
               x=rec[:, 0:3].copy(), u0=rec[:, 3:6].copy(), u1=rec[:, 6:9].copy(),
               m=rec[:, 9].copy(), alpha=rec[:, 10].copy(), gam=rec[:, 11:17].copy(),
               vol=rec[:, 17].copy(), tag=irec[:, 0].copy(), level=irec[:, 1].copy(),
               I=irec[:, 2].copy(), J=irec[:, 3].copy(), K=irec[:, 4].copy(),
               nsub=irec[:, 5].copy(), nupd=irec[:, 6].copy())
    if version == 2:
        out.update(alpha_p=rec[:, 18].copy(), beta_p=rec[:, 19:22].copy(),
                   ginv_p=rec[:, 22:28].copy())
    return out


def particle_energies(u, alpha_p, beta_p, ginv_p):
    """W = sqrt(1 + gamma^ij u_i u_j) and H = alpha W - beta^i u_i with the metric at
    each particle (gamma^ij as xx, xy, xz, yy, yz, zz). Returns (W, H)."""
    gxx, gxy, gxz, gyy, gyz, gzz = (ginv_p[:, k] for k in range(6))
    ux, uy, uz = u[:, 0], u[:, 1], u[:, 2]
    q = (gxx * ux * ux + gyy * uy * uy + gzz * uz * uz +
         2.0 * (gxy * ux * uy + gxz * ux * uz + gyz * uy * uz))
    Wp = np.sqrt(1.0 + q)
    return Wp, alpha_p * Wp - np.sum(beta_p * u, axis=1)


def fsum_cols(a):
    """Exactly rounded column sums of a 2-D array (math.fsum)."""
    a = np.atleast_2d(a)
    return np.array([math.fsum(a[:, j]) for j in range(a.shape[1])])


def W(u):
    return np.sqrt(1.0 + np.sum(u * u, axis=-1))


def save_json(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=float)
