#!/usr/bin/env python3
"""SC7: GR test-particle invariants of the members and the CM of the NR start state
(three_punctures/inputs/hills_q10_m8.athinput), against the two baselines' meaning of
"r_p = 8 M". Usage: nr_invariants.py <outdir>. Writes nr_invariants.json.

Reading of the data [JUDGEMENT, stated in the output]: puncture momenta P_i are read as m u_i
(covariant spatial 4-velocity) in isotropic coordinates of a Schwarzschild hole of mass M_h
at the heavy puncture, E = alpha sqrt(1 + psi^-4 |u|^2), L = (x x u)_z, areal radius
r_S = r (1 + M_h/2r)^2. Two brackets: M_h = M (test-mass picture, hole at rest or moving with
its momentum) and M_h = M + m_b (total mass, effective-one-body-like)."""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models as mdl  # noqa: E402
from nrstate import INPUT, read_problem  # noqa: E402


def iso_invariants(x, u, Mh):
    r = float(np.linalg.norm(x))
    psi = 1.0 + Mh / (2 * r)
    alpha = (1 - Mh / (2 * r)) / (1 + Mh / (2 * r))
    E = alpha * math.sqrt(1.0 + float(u @ u) / psi ** 4)
    L = float(x[0] * u[1] - x[1] * u[0])
    rS = r * psi ** 2
    return E, L, rS


def turning_point(E, L, Mh, r_start):
    """Largest r < r_start with V^2(r) = E^2 (inward motion from r_start); None if captured."""
    def g(r):
        return (1 - 2 * Mh / r) * (1 + L * L / (r * r)) - E * E
    if _cap(E, L, Mh):
        return None
    rs = np.linspace(r_start, 2.0 * Mh * 1.0001, 200000)
    v = g(rs)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    if idx.size == 0:
        return None
    i = idx[0]
    return brentq(g, rs[i + 1], rs[i])


def _cap(E, L, Mh):
    # scale to units of Mh
    return mdl.gr_captured(E, L / Mh, -1.0, 1.0)


def main(out):
    os.makedirs(out, exist_ok=True)
    m, x, p = read_problem(INPUT)
    m1, m2, M = m
    mb = m1 + m2
    res = {"input": INPUT, "reading": __doc__.split("Reading of the data")[1].strip()}
    for lab, Mh, sub_hole in (("test_mass_hole_at_rest", M, False),
                              ("test_mass_hole_frame", M, True),
                              ("total_mass_hole_frame", M + mb, True)):
        vh = p[2] / M if sub_hole else np.zeros(3)
        rows = {}
        for name, k in (("m1", 0), ("m2", 1)):
            xr = x[k] - x[2]
            u = p[k] / m[k] - vh
            E, L, rS = iso_invariants(xr, u, Mh)
            cap = _cap(E, L, Mh)
            rows[name] = dict(E=E, L=L, rS=rS, captured=bool(cap),
                              turning_point_rS=None if cap else turning_point(E, L, Mh, rS))
        xc = (m1 * x[0] + m2 * x[1]) / mb - x[2]
        uc = (p[0] + p[1]) / mb - vh
        E, L, rS = iso_invariants(xc, uc, Mh)
        cap = _cap(E, L, Mh)
        rows["cm"] = dict(E=E, L=L, rS=rS, captured=bool(cap),
                          turning_point_rS=None if cap else turning_point(E, L, Mh, rS),
                          turning_point_riso=None)
        tp = rows["cm"]["turning_point_rS"]
        if tp:
            # invert r_S = r (1 + Mh/2r)^2 for the isotropic radius
            rows["cm"]["turning_point_riso"] = brentq(lambda r: r * (1 + Mh / (2 * r)) ** 2 - tp,
                                                      Mh / 2 * 1.0001, tp)
        rows["M_h"] = Mh
        res[lab] = rows
    # the baselines' meanings of r_p = 8 M (Newton about M, Newton about M + m_b, 2404 parabola)
    res["baselines_rp8"] = dict(
        newton_hole_fixed=dict(E=1.0, L=math.sqrt(2 * 8.0)),
        newton_full_relative=dict(E=1.0, L=math.sqrt(2 * 1.1 * 8.0)),
        hrna_2404=dict(E=1.0, L=math.sqrt(2 * 64.0 / 6.0)),
        capture_L_at_E1=4.0)
    print(json.dumps(res, indent=1, default=float))
    json.dump(res, open(os.path.join(out, "nr_invariants.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"])
