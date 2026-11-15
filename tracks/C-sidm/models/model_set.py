"""The model set of the wave-2 package: the science family the lead chose and the King
threshold models (tracks/C-sidm/stage/G0/REPORT.md section 2, decision 1).

    tmb01  truncated Maxwell-Boltzmann core of arXiv:2108.11967 (F21) with b = 0.1,
           f = (exp((1 - E/E0)/b) - 1)_+ (evstatic_b.py), labelled by the central redshift
           Z(0) = 1/alpha_c - 1 (F21 main.tex:255-257; evstatic's Zc_infinity):
             0.50, 0.52                 stable side of the E_b maximum
             0.53306 (J_E onset)        fluid onset with the adiabatic index of a Juttner gas
                                        at the energy-matched temperature (run
                                        C-20261115-165315-7b473b8, fluid_onset.json,
                                        results["0.1"].onset.J_E_N1200.w0 = 3.13077157766327)
             0.54041 (E_b maximum)      computed here (first maximum of E_b along y0); F21's
                                        turning point, criteria.json max_eps Z0 = 0.5404129
             0.56, 0.58, 0.60           past the E_b maximum, below the F21-gamma onset
             0.63482 (F21-gamma onset)  fluid onset with F21's gamma = 1 + p/u (run
                                        C-sidm-20261115-120722-38ab057, criteria.json
                                        omega2_zero_F21gamma.w0 = 3.5870994678343244)
    king   the five King models of tracks/C-sidm/equilibria/models.py (y0 = 0.314, 0.324,
           y_max = 0.334032, 0.344, 0.354), taken from that file so that y0 is the same to
           the last bit.

y0 = ln E0 - mu(0) = -ln(1 - b w0) relates the variable of evstatic_b to F21's w0.
"""

import functools
import math
import os
import sys

from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import evstatic_b as evb  # noqa: E402

B_SCIENCE = 0.1
W0_JE_ONSET = 3.13077157766327           # run C-20261115-165315-7b473b8 (N = 1200 FEM)
W0_F21_ONSET = 3.5870994678343244        # run C-sidm-20261115-120722-38ab057
Z0_GRID = (0.50, 0.52, 0.56, 0.58, 0.60)

FAMILIES = {
    "king": evb.Family("king", name="king"),
    "tmb01": evb.Family("tmb", b=B_SCIENCE, name="tmb01"),
}


def y0_of_w0(w0, b=B_SCIENCE):
    return -math.log1p(-b * w0)


def w0_of_y0(y0, b=B_SCIENCE):
    return -math.expm1(-y0) / b


@functools.lru_cache(maxsize=None)
def threshold(key):
    """(y_max, E_b,max) of family `key` (first maximum of E_b along y0)."""
    return evb.first_maximum(FAMILIES[key], 0.05, 1.0, 40)


def y0_of_Z0(fam, Z, lo=0.2, hi=0.7):
    return brentq(lambda v: evb.integrate(fam, v)["Zc_infinity"] - Z, lo, hi, xtol=1e-14)


def king_specs():
    """The King rows of tracks/C-sidm/equilibria/models.py (imported, not copied)."""
    import importlib.util
    p = os.path.join(HERE, "..", "equilibria", "models.py")
    sys.path.insert(1, os.path.dirname(p))
    spec = importlib.util.spec_from_file_location("equilibria_models", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [d for d in mod.model_set() if d["family"] == "king"]


def tmb_specs():
    fam = FAMILIES["tmb01"]
    ym, _ = threshold("tmb01")
    rows = [(y0_of_Z0(fam, 0.50), "stable side of the E_b maximum (Z(0) = 0.50)"),
            (y0_of_Z0(fam, 0.52), "stable side of the E_b maximum (Z(0) = 0.52)"),
            (y0_of_w0(W0_JE_ONSET), "fluid onset, Juttner Gamma_1 at the energy-matched "
                                    "temperature (run C-20261115-165315-7b473b8)"),
            (ym, "E_b maximum (computed), F21 turning point"),
            (y0_of_Z0(fam, 0.56), "past the E_b maximum (Z(0) = 0.56)"),
            (y0_of_Z0(fam, 0.58), "past the E_b maximum (Z(0) = 0.58)"),
            (y0_of_Z0(fam, 0.60), "past the E_b maximum (Z(0) = 0.60)"),
            (y0_of_w0(W0_F21_ONSET), "fluid onset, F21 gamma = 1 + p/u (run "
                                     "C-sidm-20261115-120722-38ab057)")]
    out = []
    for y0, role in rows:
        Z = evb.integrate(fam, y0)["Zc_infinity"]
        out.append(dict(family="tmb01", y0=y0, role=role, b=B_SCIENCE, w0=w0_of_y0(y0),
                        tag=f"tmb01_Z{Z:.4f}".replace(".", "p")))
    return out


def model_set():
    """List of dict(tag, family, y0, role[, b, w0]) in the form of
    tracks/C-sidm/equilibria/models.model_set()."""
    return king_specs() + tmb_specs()
