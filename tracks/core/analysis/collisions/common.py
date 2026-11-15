"""Shared helpers of the collision tests: paths, particle files for the periodic box,
running the code, statistics, figures."""
import hashlib
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))

from nrpic import collide, rng  # noqa: E402
from nrpic.io import write_nrp  # noqa: E402

EXE_CPU = os.path.join(REPO, ".work", "build_cpu", "src", "athena")
EXE_GPU = os.path.join(REPO, ".work", "build_gpu", "src", "athena")
EXE_CPU_BASE = os.path.join(REPO, ".work", "build_cpu_base", "src", "athena")
EXE_GPU_BASE = os.path.join(REPO, ".work", "build_gpu_base", "src", "athena")
DECK_BOX = os.path.join(REPO, "problems", "tests", "coll_box.athinput")
BOX_MIN, BOX_LEN = 100.0, 1.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for blk in iter(lambda: fp.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _uni(seed, sub, n, draw):
    """Uniform deviates of the initial-data stream for the tags 0..n-1."""
    return np.asarray(rng.uniform(seed=seed, stream=rng.stream(rng.STREAM_INITIAL_DATA, sub),
                                  entity=np.arange(n, dtype=np.uint64), step=0, draw=draw))


def _dirs(seed, sub, n, draw):
    return np.asarray(rng.direction(seed=seed,
                                    stream=rng.stream(rng.STREAM_INITIAL_DATA, sub),
                                    entity=np.arange(n, dtype=np.uint64), step=0,
                                    draw=draw)).reshape(n, 3)


def make_box(path, kind, n, seed=1, theta=0.1, theta2=None, u0=0.3, mass_ratio=4.0,
             xmin=BOX_MIN, length=BOX_LEN, lengths=None, mode_eps=0.0, drift=0.0,
             gmat=None):
    """Particle file for the periodic box: total rest mass rho_0 x volume with
    rho_0 = 1. Positions uniform random (a Poisson-like occupation of the cells).
    kind: mj (Maxwell-Juttner at theta), shell (|u| = u0), twotemp (first half theta,
    second half theta2, species 0 and 1), unequal (first half mass 1, second half mass
    mass_ratio in relative units, equal numbers, twotemp momenta), mode (isobaric
    temperature mode along x: T = theta (1 + eps cos kx), n = n0/(1 + eps cos kx)).
    All draws come from the initial-data stream of nrpic.rng (entity = tag, step 0).
    gmat: constant spatial metric gamma_ij (3x3) of a homogeneous curved box; the
    distribution described above is then that of the triad components, the file holds
    u_j = S[j][m] u_(m) with the Cholesky factor S, and the rest masses are multiplied
    by sqrt(det gamma) so that the proper density stays rho_0 = 1.
    Returns a dict of metadata."""
    lengths = [length]*3 if lengths is None else list(lengths)
    vol = lengths[0]*lengths[1]*lengths[2]
    x = np.stack([xmin + lengths[d]*_uni(seed, 0, n, d) for d in range(3)], axis=1)
    nh = _dirs(seed, 0, n, 4)
    uq = _uni(seed, 0, n, 3)
    sp = np.zeros(n, dtype=np.int32)
    m = np.full(n, vol/n)
    half = n//2
    if kind == "mj":
        umag = collide.mj_sample(theta, uq)
    elif kind == "shell":
        umag = np.full(n, u0)
    elif kind in ("twotemp", "unequal"):
        umag = np.empty(n)
        umag[:half] = collide.mj_sample(theta, uq[:half])
        umag[half:] = collide.mj_sample(theta2, uq[half:])
        sp[half:] = 1
        if kind == "unequal":
            # equal numbers, masses 1 : mass_ratio, total mass rho_0 x volume
            m1 = vol/(half + mass_ratio*(n - half))
            m[:half] = m1
            m[half:] = mass_ratio*m1
    elif kind == "mode":
        # density n0/(1 + eps cos kx) by rejection-free inversion on a table, then the
        # temperature of each particle from its position
        k = 2.0*np.pi/lengths[0]
        xi = np.linspace(0.0, lengths[0], 20001)
        dens = 1.0/(1.0 + mode_eps*np.cos(k*xi))
        cdf = np.concatenate(([0.0], np.cumsum(0.5*(dens[1:] + dens[:-1])*np.diff(xi))))
        cdf /= cdf[-1]
        x[:, 0] = xmin + np.interp(_uni(seed, 0, n, 0), cdf, xi)
        th = theta*(1.0 + mode_eps*np.cos(k*(x[:, 0] - xmin)))
        # |u| of the local temperature: tabulate the inverse distribution for a set of
        # temperatures and interpolate in temperature
        tgrid = np.linspace(theta*(1.0 - mode_eps), theta*(1.0 + mode_eps), 65)
        table = np.stack([collide.mj_sample(t, uq) for t in tgrid], axis=0)
        ft = (th - tgrid[0])/(tgrid[1] - tgrid[0])
        i0 = np.clip(np.floor(ft).astype(int), 0, len(tgrid) - 2)
        w1 = ft - i0
        ar = np.arange(n)
        umag = (1.0 - w1)*table[i0, ar] + w1*table[i0 + 1, ar]
    else:
        raise ValueError("unknown kind " + kind)
    u = umag[:, None]*nh
    if drift != 0.0:
        # boost of every particle along x with velocity `drift`
        gam = 1.0/np.sqrt(1.0 - drift*drift)
        w = np.sqrt(1.0 + np.sum(u*u, axis=1))
        u[:, 0] = gam*(u[:, 0] + drift*w)
    if gmat is not None:
        gmat = np.asarray(gmat, dtype=np.float64)
        u = u @ np.linalg.cholesky(gmat).T
        m = m*np.sqrt(np.linalg.det(gmat))
    write_nrp(path, x, u, m, sp)
    return dict(kind=kind, n=n, seed=seed, theta=theta, theta2=theta2, u0=u0,
                mass_ratio=mass_ratio, lengths=lengths, rho0=float(np.sum(m)/vol),
                sha256=sha256(path))


def run_athena(exe, deck, rundir, overrides=(), log="athena.log", restart=None,
               timeout=None):
    """Runs the code in rundir; returns (exit status, wall time in s)."""
    os.makedirs(rundir, exist_ok=True)
    if restart is None:
        cmd = [exe, "-i", deck, "-d", rundir] + list(overrides)
    else:
        cmd = [exe, "-r", restart, "-d", rundir] + list(overrides)
    t0 = time.time()
    with open(os.path.join(rundir, log), "w") as fp:
        proc = subprocess.run(cmd, cwd=rundir, stdout=fp, stderr=subprocess.STDOUT,
                              timeout=timeout)
    return proc.returncode, time.time() - t0


def run_many(jobs, nproc):
    """jobs: list of (exe, deck, rundir, overrides). Runs them nproc at a time; returns
    the list of (exit status, wall time)."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=nproc) as pool:
        futs = [pool.submit(run_athena, *job) for job in jobs]
        return [f.result() for f in futs]


def snapshots(rundir, base="box"):
    """Sorted list of the snapshot files of a run."""
    return sorted(os.path.join(rundir, f) for f in os.listdir(rundir)
                  if f.startswith(base + ".part.") and f.endswith(".bin"))


def exact_sum(a):
    """Correctly rounded sum of an array."""
    import math
    return math.fsum(np.asarray(a, dtype=np.float64).ravel().tolist())


def style():
    from nrpic import figstyle
    figstyle.use_style()
    return figstyle
