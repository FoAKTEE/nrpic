"""Shared helpers of the periodic_z4c analysis: locating registered runs, the figure
style of the project, mode projections."""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
WT = os.path.abspath(os.path.join(PKG, "..", "..", ".."))
RUNS = os.path.join(WT, "tracks", "B-emd-gw", "runs")
FIGS = os.path.join(PKG, "figs")
TABLES = os.path.join(PKG, "tables")
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle  # noqa: E402,F401


def manifests():
    out = []
    for p in sorted(glob.glob(os.path.join(RUNS, "*", "manifest.json"))):
        with open(p) as f:
            out.append(json.load(f))
    return out


def find_run(name, require_done=True):
    """Latest registered run with this case name; returns its manifest."""
    ms = [m for m in manifests() if m.get("name") == name
          and (not require_done or m.get("status") == "done")]
    if not ms:
        raise FileNotFoundError(f"no finished run named {name}")
    return ms[-1]


def tab_files(run, var="z4c"):
    return sorted(glob.glob(os.path.join(run["output_dir"], "tab", f"*.{var}.*.tab")))


def project(x, f, k, L):
    """Least-squares fit f = c0 + s sin(2 pi k x/L) + c cos(2 pi k x/L) on a uniform
    periodic grid (exact discrete orthogonality). Returns (s, c)."""
    ph = 2*np.pi*k*x/L
    n = len(x)
    return 2.0/n*np.sum(f*np.sin(ph)), 2.0/n*np.sum(f*np.cos(ph))


def orders(errs):
    e = np.abs(np.asarray(errs, float))
    return [np.log2(e[i]/e[i + 1]) if e[i + 1] > 0 else np.nan for i in range(len(e) - 1)]


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=float)
        f.write("\n")
