"""Shared helpers of the secondary_infall package (Track D, D-pre-3).

Reference calculations only (decision 0010): nothing here is a simulation code of the
program; these are semi-analytic solutions and a spherical-shell reference calculation
that fix the parameters of AthenaK runs.
"""
import hashlib
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))      # worktree root
FIGSTYLE = os.path.join(ROOT, "python", "nrpic", "figstyle.py")

# closed-form constants used by several scripts
PI = 3.141592653589793
KAPPA = PI**2 / 8.0          # G M_ta t^2 / r_ta^3 for a cycloid that turns around at t
C_TA = (4.0 / (3.0 * PI)) ** (2.0 / 3.0)   # 0.5648: M_b,ta/(M a/a_i) as a/a_i -> infinity


def load_figstyle():
    spec = importlib.util.spec_from_file_location("figstyle", FIGSTYLE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.use_style()
    return mod


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kepler_radial(r_i, v_i, m, t_i):
    """Radial Kepler orbit (no angular momentum) through (r_i, v_i) at t_i, central mass m.
    Returns energy, apocentre, turnaround time and the time it reaches r = 0 (collapse).
    Valid for bound orbits (E < 0) moving outwards at t_i."""
    import numpy as np
    r_i = np.asarray(r_i, float)
    v_i = np.asarray(v_i, float)
    m = np.asarray(m, float)
    energy = 0.5 * v_i**2 - m / r_i
    r_max = m / (-energy)
    eta_i = np.arccos(np.clip(1.0 - 2.0 * r_i / r_max, -1.0, 1.0))
    ts = np.sqrt(r_max**3 / (8.0 * m))
    t_ta = t_i + ts * (PI - (eta_i - np.sin(eta_i)))
    t_c = t_i + ts * (2.0 * PI - (eta_i - np.sin(eta_i)))
    return dict(energy=energy, r_max=r_max, t_ta=t_ta, t_c=t_c)
