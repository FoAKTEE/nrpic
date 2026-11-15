"""The near-threshold model set of this package.

Thresholds (first maximum of E_b along each family) are recomputed here, not taken from
the papers; the papers' printed values are the checks (paper_values.py, check_equilibria.py).

    king      2009.08163 King model; y0 = 0.314, 0.324 (stable), y_max, 0.344, 0.354
              (unstable): the values of 2009.08163 line 1146 plus the computed y_max.
    poly05    2009.08163 isotropic polytrope k = 0.5, l = L0 = 0; y0 = y_max + (-0.02,
              -0.01, 0, +0.01, +0.02), the spacing of the King runs.
    arshell   gr-qc/0601112 Case 1 shell, f = Theta(E0 - E) Theta(L - L0), L0 = 0.1;
              Z_c = 0.39 (Table 1: stable), the computed E_b maximum, Z_c = 0.43 (Table 1:
              unstable for A > 1).
"""

import functools
import math

from scipy.optimize import brentq

import evstatic as ev

FAMILIES = {
    "king": ev.Family("king", name="king"),
    "poly05": ev.Family("poly", k=0.5, name="poly05"),
    "arshell": ev.Family("poly", k=0.0, l=0.0, L0=0.1, name="arshell"),
}


@functools.lru_cache(maxsize=None)
def threshold(key):
    """(y_max, E_b,max) of family `key`."""
    return ev.first_maximum(FAMILIES[key], 0.05, 1.0, 40)


def y0_of_Zc(fam, Zc, lo=0.05, hi=1.5):
    """y0 with Z_c = 1/alpha_c - 1 on the branch below the E_b-zero (monotone there)."""
    return brentq(lambda v: ev.integrate(fam, v)["Zc_infinity"] - Zc, lo, hi, xtol=1e-13)


def model_set():
    """List of dict(tag, family key, y0, role)."""
    out = []
    ym, _ = threshold("king")
    for y0, role in ((0.314, "stable (2009.08163 l.1146)"), (0.324, "stable (2009.08163 l.1146)"),
                     (ym, "threshold (computed y_max)"), (0.344, "unstable (2009.08163 l.1146)"),
                     (0.354, "unstable (2009.08163 l.1146)")):
        out.append(dict(family="king", y0=y0, role=role))
    ym, _ = threshold("poly05")
    for dy in (-0.02, -0.01, 0.0, 0.01, 0.02):
        role = "threshold (computed y_max)" if dy == 0 else \
            ("stable side" if dy < 0 else "unstable side") + f" (y_max {dy:+.2f})"
        out.append(dict(family="poly05", y0=ym + dy, role=role))
    fam = FAMILIES["arshell"]
    ym, _ = threshold("arshell")
    out.append(dict(family="arshell", y0=y0_of_Zc(fam, 0.39),
                    role="stable (gr-qc/0601112 Table 1, Z_c = 0.39)"))
    out.append(dict(family="arshell", y0=ym, role="threshold (computed E_b maximum)"))
    out.append(dict(family="arshell", y0=y0_of_Zc(fam, 0.43),
                    role="unstable for A > 1 (gr-qc/0601112 Table 1, Z_c = 0.43)"))
    for d in out:
        d["tag"] = f"{d['family']}_y{d['y0']:.5f}".replace(".", "p")
    return out
