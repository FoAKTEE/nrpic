"""Shared helpers of the heat-conduction package (tracks/C-sidm/heat): paths, particle
files, running the executable, reducing snapshots to the few numbers the tests need.

Particle files come from the track's generator `collide/analysis/make_box.py` (Poisson
positions, mirrored momenta, equal masses); readers from `collide/analysis/snap.py`;
reference functions from `collide/REFERENCES/`. The executable is core's branch
core/collisions-2 (READY in its directory), processors unless a driver says otherwise.

Snapshots of large runs are reduced while the run goes on (one record per snapshot:
slab sums or Fourier sums, fraction of particles that have collided) and deleted after
reduction, except the first and the last; the reduction is the run's output
(`reduced.npz`). This keeps a run of 2e6 particles at ~0.3 GB instead of ~5 GB.
"""
import json
import os
import subprocess
import sys
import threading
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRACK = os.path.dirname(PKG)
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
COLLIDE = os.path.join(TRACK, "collide")
for p in (os.path.join(COLLIDE, "REFERENCES"), os.path.join(COLLIDE, "analysis"),
          os.path.join(REPO, "python"), HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import snap  # noqa: E402

MAIN = "/data/haiyangw/nrpic"
EXE_DIR = os.path.join(MAIN, "scratch", "core", "exe", "core_collisions-2")
EXE_CPU = os.path.join(EXE_DIR, "athena_cpu")
EXE_GPU = os.path.join(EXE_DIR, "athena_gpu")
DECK = os.path.join(PKG, "inputs", "heat.athinput")
MAKE_BOX = os.path.join(COLLIDE, "analysis", "make_box.py")
X0 = 10.0
BASE = "heat"


def outdir(default_name="manual"):
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join(MAIN, "scratch", "C-sidm", "tmp", "heat", default_name)
    os.makedirs(d, exist_ok=True)
    return d


def make_box(rundir, kind, **kw):
    """make_box.py KIND into rundir/heat.{nrp,json}; returns the metadata."""
    os.makedirs(rundir, exist_ok=True)
    cmd = [sys.executable, MAKE_BOX, kind, "--out", os.path.join(rundir, BASE)]
    for k, v in kw.items():
        if isinstance(v, (list, tuple, np.ndarray)):
            cmd += ["--" + k] + [repr(float(x)) for x in v]
        else:
            cmd += ["--" + k, str(v)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    with open(os.path.join(rundir, BASE + ".json")) as fh:
        return json.load(fh)


def overrides(box, nx, dt, tlim, snap_dt, sigma, seed, pmax=0.1, mb=None, nsub_max=1000,
              subcycle="measured", energy="particle", extra=()):
    """Command-line parameters for the deck: box (Lx, Ly, Lz) at x0 = 10, nx cells per
    direction (list of three), one MeshBlock unless mb is given."""
    mb = list(nx) if mb is None else list(mb)
    o = []
    for d in range(3):
        o += [f"mesh/nx{d + 1}={nx[d]}", f"mesh/x{d + 1}min={X0!r}",
              f"mesh/x{d + 1}max={X0 + box[d]!r}", f"meshblock/nx{d + 1}={mb[d]}"]
    o += [f"particles/dt={dt!r}", f"time/tlim={tlim!r}", f"particles/snap_dt={snap_dt!r}",
          f"particles/coll_sigma={sigma!r}", f"job/rng_seed={seed}",
          f"particles/coll_pmax={pmax!r}", f"particles/coll_nsub_max={nsub_max}",
          f"particles/coll_subcycle={subcycle}", f"particles/coll_energy={energy}"]
    if not any(str(e).startswith("particles/particle_file=") for e in extra):
        o.append(f"particles/particle_file={BASE}.nrp")
    return o + list(extra)


def run_athena(rundir, ovr, exe=EXE_CPU, reducer=None, log="athena.log"):
    """Run the executable in rundir; if `reducer` is given (a SnapReducer), it reduces
    snapshots while the run goes on and once more at the end. Returns dict(rc, wall)."""
    cmd = [exe, "-i", DECK, "-d", rundir] + list(ovr)
    env = dict(os.environ, OMP_NUM_THREADS="1")
    t0 = time.time()
    with open(os.path.join(rundir, log), "w") as fh:
        fh.write(" ".join(cmd) + "\n")
        fh.flush()
        p = subprocess.Popen(cmd, cwd=rundir, stdout=fh, stderr=subprocess.STDOUT, env=env)
        while p.poll() is None:
            if reducer is not None:
                reducer.step(final=False)
            time.sleep(5.0)
    if reducer is not None:
        reducer.step(final=True)
        reducer.save()
    res = dict(rc=p.returncode, wall=time.time() - t0, cmd=cmd)
    with open(os.path.join(rundir, "wall.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    return res


class SnapReducer:
    """Reduces the snapshots of one run directory to records (function `fun(snapshot)` ->
    dict of floats or arrays) in time order; a snapshot is read once the next one exists
    (or the run has ended), and deleted after reduction unless it is the first or the last
    or keep_all is set."""

    def __init__(self, rundir, fun, keep_all=False):
        self.rundir, self.fun, self.keep_all = rundir, fun, keep_all
        self.done = []          # paths reduced
        self.records = []
        self.lock = threading.Lock()

    def step(self, final):
        files = snap.snapshots(self.rundir, BASE)
        todo = [f for f in files if f not in self.done]
        if not final:
            todo = todo[:-1]            # the newest may still be written
        for f in todo:
            s = snap.read_snapshot(f)
            rec = self.fun(s)
            rec["file"] = os.path.basename(f)
            self.records.append(rec)
            first = not self.done
            self.done.append(f)
            last = final and f == files[-1]
            if not (self.keep_all or first or last):
                os.remove(f)

    def save(self, name="reduced.npz"):
        keys = [k for k in self.records[0] if k != "file"]
        out = {k: np.array([r[k] for r in self.records]) for k in keys}
        out["files"] = np.array([r["file"] for r in self.records])
        np.savez(os.path.join(self.rundir, name), **out)
        return out


# --------------------------------------------------------------------- reductions
def W_flat(u):
    return np.sqrt(1.0 + np.sum(u * u, axis=-1))


def kin_flat(u):
    u2 = np.sum(u * u, axis=-1)
    return u2 / (np.sqrt(1.0 + u2) + 1.0)


def mode_fun(k, u0=None, nharm=3):
    """Fourier sums of a mode box: for harmonics j = 1..nharm the sums of M, M K, M W and
    M u_x times cos(j k (x - x0)) and sin(...); totals; fraction of particles whose u
    differs from the initial one (u0 sorted by tag)."""
    def fun(s):
        x = s["x"][:, 0] - X0
        M = s["m"]
        u = s["u"]
        K = kin_flat(u)
        W = W_flat(u)
        rec = dict(time=s["time"], cycle=s["cycle"], n=len(M), sM=M.sum(),
                   sMK=(M * K).sum(), sMW=(M * W).sum(), sMux=(M * u[:, 0]).sum(),
                   sMu2W=(M * np.sum(u * u, 1) / W).sum())
        for j in range(1, nharm + 1):
            c = np.cos(j * k * x)
            sn = np.sin(j * k * x)
            for name, w in (("M", M), ("MK", M * K), ("MW", M * W), ("Mux", M * u[:, 0])):
                rec[f"c{j}_{name}"] = float((w * c).sum())
                rec[f"s{j}_{name}"] = float((w * sn).sum())
        if u0 is not None:
            rec["frac_moved"] = float(np.mean(np.any(u != u0, axis=1)))
        return rec
    return fun


def step_fun(L, nbins=64, u0=None):
    """Slab sums of a step box (left slab [x0, x0 + L/2)): M, M W, M K; profiles of M and
    M K in nbins bins along x; fraction of particles that have collided."""
    def fun(s):
        xl = np.mod(s["x"][:, 0] - X0, L)
        M = s["m"]
        u = s["u"]
        K = kin_flat(u)
        W = W_flat(u)
        left = xl < 0.5 * L
        ib = np.minimum((xl / L * nbins).astype(int), nbins - 1)
        rec = dict(time=s["time"], cycle=s["cycle"], n=len(M),
                   slab_M=float(M[left].sum()), slab_MW=float((M * W)[left].sum()),
                   slab_MK=float((M * K)[left].sum()),
                   prof_M=np.bincount(ib, M, nbins), prof_MK=np.bincount(ib, M * K, nbins),
                   prof_Mux=np.bincount(ib, M * u[:, 0], nbins))
        if u0 is not None:
            rec["frac_moved"] = float(np.mean(np.any(u != u0, axis=1)))
        return rec
    return fun


def coll_summary(rundir):
    """A few columns of <base>.coll.hst over the run: steps, collisions, tested pairs,
    sum_P, n_trunc, max_P, max/mean n_sub, min/mean N per cell, max dx/lambda, the
    conservation columns, n_noroot and n_balance."""
    path = os.path.join(rundir, f"{BASE}.coll.hst")
    head, h = snap.read_history(path)
    ci = snap.history_columns(head)
    h = np.atleast_2d(h)
    col = lambda k: h[:, ci[k]] if k in ci else np.full(len(h), np.nan)
    out = dict(steps=int(len(h)), n_coll=float(np.sum(col("n_coll"))),
               n_tested=float(np.sum(col("n_tested"))), sum_P=float(np.sum(col("sum_P"))),
               n_trunc=float(np.sum(col("n_trunc"))), max_P=float(np.nanmax(col("max_P"))),
               max_nsub=float(np.nanmax(col("max_nsub"))),
               mean_nsub=float(np.nanmean(col("mean_nsub"))),
               min_N=float(np.nanmin(col("min_N"))), mean_N=float(np.nanmean(col("mean_N"))),
               max_dx_mfp=float(np.nanmax(col("max_dx_mfp"))),
               max_abs_dE_rel=float(np.nanmax(np.abs(col("dE")) / col("sum_MW"))),
               n_noroot=float(np.nansum(col("n_noroot"))),
               n_balance=float(np.nansum(col("n_balance"))))
    return out
