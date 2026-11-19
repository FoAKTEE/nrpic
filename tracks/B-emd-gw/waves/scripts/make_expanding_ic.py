#!/usr/bin/env python3
"""Initial data of test X (free tensor mode in the expanding box) for nrpic_cosmo.

    python3 make_expanding_ic.py --n 32 --out DIR [--L 4 --m 1,1,0 --eps-p 2e-6 --eps-x 1e-6 --phi-x 1]

Writes DIR/particles.nrp (lattice at rest, one particle per cell, positions and masses as
cosmo/ic/make_lattice.py --ppc 1: x = (i + 1) h, m = rho_0 h^3, rho_0 = 3 H^2/(8 pi)),
DIR/fields.bin (NRCOSMO1 through cosmo/ic/nrp_io.write_fields: psi = 1, K = -3 H,
alpha = 1, Ahat_ij = -(1/2) h'_ij at the cell centres, h'_ij = eps_+ e+_ij cos(k.x)
+ eps_x ex_ij cos(k.x + phi_x), e+, ex of gw_diag's pol_basis(khat)), DIR/id.json.
The data satisfy the momentum constraint exactly (Ahat is transverse and traceless,
psi and K uniform) and the Hamiltonian constraint up to the second-order term
Ahat_ij Ahat^ij (relative size eps^2/24 ~ 2e-13)."""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import refs  # noqa: E402  (also puts cosmo/ic and gw_diag on the path)
from nrp_io import write_fields, write_particles  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--L", type=float, default=4.0)
    ap.add_argument("--H0", type=float, default=1.0)
    ap.add_argument("--m", default="1,1,0", help="integer mode numbers of k")
    ap.add_argument("--eps-p", type=float, default=2e-6)
    ap.add_argument("--eps-x", type=float, default=1e-6)
    ap.add_argument("--phi-x", type=float, default=1.0)
    ap.add_argument("--out", default=None,
                    help="default: $NRPIC_RUN_DIR/N<n>/ic (a registered run of its own)")
    a = ap.parse_args()
    if a.out is None:
        a.out = os.path.join(os.environ["NRPIC_RUN_DIR"], f"N{a.n}", "ic")
    n, L = a.n, a.L
    h = L / n
    m = np.array([float(v) for v in a.m.split(",")])
    kv = 2 * np.pi / L * m
    ep, ex, _, _ = refs.basis(kv)
    # fields at the cell centres, arrays indexed [i, j, k] (x, y, z) for write_fields
    xc = (np.arange(n) + 0.5) * h
    X, Y, Z = np.meshgrid(xc, xc, xc, indexing="ij")
    ph = kv[0] * X + kv[1] * Y + kv[2] * Z
    hp = (a.eps_p * ep[:, :, None, None, None] * np.cos(ph)
          + a.eps_x * ex[:, :, None, None, None] * np.cos(ph + a.phi_x))
    ahat = [-0.5 * hp[i, j] for i, j in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))]
    one = np.ones((n, n, n))
    os.makedirs(a.out, exist_ok=True)
    write_fields(os.path.join(a.out, "fields.bin"), one, -3.0 * a.H0 * one, one, ahat)
    # particles: lattice at rest (make_lattice.py, ppc = 1)
    q = np.mod((np.arange(n) + 1.0) * h, L)
    Q1, Q2, Q3 = np.meshgrid(q, q, q, indexing="ij")
    x = np.stack([Q1.ravel(), Q2.ravel(), Q3.ravel()], axis=1)
    rho0 = 3.0 * a.H0 ** 2 / (8.0 * np.pi)
    mass = np.full(len(x), rho0 * h ** 3)
    write_particles(os.path.join(a.out, "particles.nrp"), x, np.zeros_like(x), mass)
    meta = {"n": n, "L": L, "H0": a.H0, "m": m.tolist(), "k": kv.tolist(),
            "kn": float(np.linalg.norm(kv)), "eps_p": a.eps_p, "eps_x": a.eps_x,
            "phi_x": a.phi_x, "rho0": rho0, "particles": int(len(x)),
            "max_abs_ahat": float(np.max(np.abs(ahat))),
            "trace_ahat_max": float(np.max(np.abs(ahat[0] + ahat[3] + ahat[5])))}
    with open(os.path.join(a.out, "id.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
