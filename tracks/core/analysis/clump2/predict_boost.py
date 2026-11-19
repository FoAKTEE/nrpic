#!/usr/bin/env python3
"""Continuum numbers for the predictions TB of tracks/core/JOURNAL-clump2.md (no
simulation): norms of the uncorrected momentum-constraint residual and of the
second-order Hamiltonian residual of one boosted cluster, as the history file defines
them (M-norm2 = int psi^2 sum M_i^2 d^3x, Mx-norm2 = int psi^6 M_x^2 d^3x,
H-norm2 = int psi^6 H^2 d^3x), inside the radius --rcut. Writes predict_boost.json.

    predict_boost.py [--out DIR] [--yc 0.819] [--rcut 14]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import boosted_cluster as bc  # noqa: E402
from nrpic import st_cluster as stc  # noqa: E402


def continuum(B, V, rcut, nr=6000, nmu=48):
    """dict of continuum norms for the linear-rule speed V (along x)."""
    md = B.model
    rs = B.rs
    # radial midpoints: uniform inside the matter, uniform outside to rcut
    ri = (np.arange(nr) + 0.5) * rs / nr
    ro = rs + (np.arange(nr) + 0.5) * (rcut - rs) / nr
    r = np.concatenate([ri, ro])
    dr = np.concatenate([np.full(nr, rs / nr), np.full(nr, (rcut - rs) / nr)])
    mu, wm = np.polynomial.legendre.leggauss(nmu)
    psi, alp = md.psi(r), md.alpha(r)
    rho, prs = md.rho(r), md.P(r)
    g = psi ** 6 * (rho + prs) * alp
    wa, wb = B.w_ab_iso(r)
    q, i4 = B.moments(r)
    a2, a4 = 1.5 * q * B.pmass / r ** 2, 0.5 * i4 * B.pmass / r ** 4
    a, b, c = a2 + a4, -a2 + a4, a2 - 5.0 * a4
    k2 = 2 * a * a + 4 * a * b + 4 * a * c + 3 * b * b + 2 * b * c + c * c
    vol = (2.0 * math.pi * r * r * dr)[:, None] * wm[None, :]
    m2 = mu[None, :] ** 2
    s2 = (g * g)[:, None] * V * V * ((wa * wa)[:, None] + m2 * (2 * wa * wb + wb * wb)[:, None])
    sx = g[:, None] * V * (wa[:, None] + m2 * wb[:, None])
    M2 = (8 * math.pi) ** 2 * np.sum(vol * psi[:, None] ** -10 * s2)
    Mx2 = (8 * math.pi) ** 2 * np.sum(vol * psi[:, None] ** -6 * sx ** 2)
    wbar2 = (alp ** 2 / psi ** 4)[:, None] * V * V * (
        (wa * wa)[:, None] + m2 * (2 * wa * wb + wb * wb)[:, None])
    ab2 = V * V * ((2 * a * a)[:, None] + m2 * k2[:, None])
    h_mat = -8.0 * math.pi * (rho + prs)[:, None] * wbar2
    h_cur = -psi[:, None] ** -12 * ab2
    p6 = psi[:, None] ** 6
    H2 = np.sum(vol * p6 * (h_mat + h_cur) ** 2)
    return dict(V=V, M_norm=math.sqrt(M2), Mx_norm=math.sqrt(Mx2),
                H2_norm=math.sqrt(H2),
                H2_norm_matter=math.sqrt(np.sum(vol * p6 * h_mat ** 2)),
                H2_norm_curvature=math.sqrt(np.sum(vol * p6 * h_cur ** 2)),
                H_matter_term_norm=math.sqrt(np.sum(vol * p6 * (16 * math.pi * rho[:, None]) ** 2)),
                H2_peak=float(np.max(np.abs(h_mat + h_cur))),
                second_order_mass=B.second_order_mass([V, 0, 0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", HERE))
    ap.add_argument("--yc", type=float, default=0.819)
    ap.add_argument("--rcut", type=float, default=14.0)
    a = ap.parse_args()
    md = stc.STModel(a.yc)
    B = bc.BoostedST(md)
    out = dict(yc=a.yc, rcut=a.rcut, rbar_s=B.rs, pmass=B.pmass)
    for v in (0.1, 0.3):
        V = v / math.sqrt(1.0 - v * v)
        out[f"v={v}"] = continuum(B, V, a.rcut)
        print(f"v = {v}: " + ", ".join(f"{k} = {x:.6g}" for k, x in out[f"v={v}"].items()))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "predict_boost.json"), "w") as f:
        json.dump(out, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
