"""Shared set-up of the scripts: paths, the run directory, the models, the figure style."""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRACK = os.path.dirname(PKG)
ROOT = os.path.dirname(os.path.dirname(TRACK))
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(TRACK, "expball"))
sys.path.insert(0, os.path.join(ROOT, "python", "nrpic"))   # figstyle.py (project style)

FIGDIR = os.path.join(PKG, "figures")

H = 1.0 / 16.0                 # Einstein-de Sitter rate on the initial slice (expball set 2)
PROFILE = (1.0, 2.4, 6.0)      # delta_c, R1, R2 of expball data set 2 (R_b = 8, H R_b = 0.5)
EPS = 0.1                      # dipole amplitude of the reference Szekeres model


def run_dir(name):
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join(ROOT, "scratch", "A-emd-pbh", "tmp", name)
    os.makedirs(d, exist_ok=True)
    return d


def run_id():
    return os.environ.get("NRPIC_RUN_ID", "unregistered")


def models(eps=EPS, kind="twist"):
    from szekeres.model import Szekeres, SmoothTopHat, Dipole
    ltb = Szekeres(H, SmoothTopHat(*PROFILE))
    szk = Szekeres(H, SmoothTopHat(*PROFILE), Dipole(eps, PROFILE[1], PROFILE[2], kind))
    return ltb, szk


def expball_ball():
    from expball.model import Ball, SmoothTopHat as ESTH
    return Ball.from_HRb(0.5, M=1.0, profile=ESTH(*PROFILE))


def dump(path, obj):
    def conv(o):
        try:
            import numpy as np
            if isinstance(o, (np.floating, np.integer)):
                return o.item()
            if isinstance(o, np.ndarray):
                return o.tolist()
        except ImportError:
            pass
        raise TypeError(type(o))
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=conv)


def git_commit():
    try:
        return subprocess.check_output(["git", "-C", PKG, "rev-parse", "--short=7", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def save_fig(fig, name, rdir):
    import figstyle
    os.makedirs(FIGDIR, exist_ok=True)
    figstyle.save(fig, os.path.join(rdir, name))
    figstyle.save(fig, os.path.join(FIGDIR, name))
