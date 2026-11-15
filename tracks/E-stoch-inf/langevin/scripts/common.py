"""Helpers shared by the scripts of the langevin package (paths, style, parallel MC, output)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(WT, "python"))

import numpy as np  # noqa: E402
from nrpic import figstyle  # noqa: E402

RUN_DIR = os.environ.get("RUN_DIR", os.path.join("/data/haiyangw/nrpic/scratch/E-stoch-inf/tmp", "norun"))
RUN_ID = os.environ.get("RUN_ID", "norun")
CORES = int(os.environ.get("NRPIC_CORES", "1"))
FIG = os.path.join(PKG, "fig")
RES = os.path.join(PKG, "results")
os.makedirs(RUN_DIR, exist_ok=True)


def save_results(name, obj):
    obj = dict(run_id=RUN_ID, **obj)
    path = os.path.join(RES, f"{name}.json")
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
    with open(os.path.join(RUN_DIR, f"{name}.json"), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    return path


def savefig(fig, name):
    """Figure into the package fig/ directory (PNG + PDF) and a PNG copy in the run dir."""
    figstyle.save(fig, os.path.join(FIG, name))
    fig.savefig(os.path.join(RUN_DIR, name + ".png"), dpi=150)


def pmap(func, args_list, cores=None):
    """Map over argument tuples with a process pool (fork), one process per core."""
    cores = CORES if cores is None else cores
    if cores <= 1 or len(args_list) == 1:
        return [func(*a) for a in args_list]
    import multiprocessing as mp
    with mp.get_context("fork").Pool(min(cores, len(args_list))) as pool:
        return pool.starmap(func, args_list)


def seeds(master, n):
    return [np.random.default_rng(s) for s in np.random.SeedSequence(master).spawn(n)]


def weighted_hist(x, w, edges):
    """Density estimate sum(w in bin) / (n_total * width) and its standard error."""
    n = len(x)
    idx = np.digitize(x, edges) - 1
    ok = (idx >= 0) & (idx < len(edges) - 1)
    s1 = np.bincount(idx[ok], weights=w[ok], minlength=len(edges) - 1)
    s2 = np.bincount(idx[ok], weights=w[ok] ** 2, minlength=len(edges) - 1)
    cnt = np.bincount(idx[ok], minlength=len(edges) - 1)
    width = np.diff(edges)
    p = s1 / (n * width)
    # variance of the mean of w * indicator over n draws
    err = np.sqrt(np.maximum(s2 / n - (s1 / n) ** 2, 0.0) / n) / width
    return p, err, cnt
