#!/usr/bin/env python3
"""Particle file of a Zel'dovich-deformed homogeneous ball for AthenaK's Newtonian mode.

Work-around for what `problems/ic/make_ic.py` and `problems/newton/make_ic.py` lack
(SCAN.md section 4, item 2; README "What the generators lack"): this script writes the
existing particle format (`.nrp`, `python/nrpic/io.py` write_nrp; magic NRPIC001, N,
N x (x^i, u_i, m), N species) and feeds the code; it simulates nothing.

    make_deformed_ball.py --out ball.nrp (--dep DELTA_L E P | --abg A B G)
                          [--a0 A0] [--hxi 0.025] [--rotate SEED] [--json ball.json]

Units of arXiv:2605.04487 (tophat.py): G = c = 1, H_k = 1, t_k = 2/3, Lagrangian radius
R_L = 1, mass M = 1/2, r_g = 2 G M = 1. Isolated domain, physical coordinates, no
expansion in the code (`newton_expansion = none`): the momentum slots hold the velocity.

Lagrangian sample: equal-mass particles on the cubic lattice xi = (i + 1/2) hxi,
|xi| < 1, optionally rotated by a random rotation (seed) about the centre (the selection
sphere is rotation invariant, so the second-moment tensor of the sample stays isotropic).
Zel'dovich map at the start a0 (default 1/(2 lambda_1), the start of 2605.04487):
    x_i = a0 (1 - a0 lambda_i) xi_i,   v_i = H0 a0 (1 - 2 a0 lambda_i) xi_i,
    H0 = 2/(3 t0), t0 = t_k a0^(3/2)
(ellipsoid.za_initial; principal axes along the coordinate axes). Centre of mass and
net momentum are removed (zero by the inversion symmetry of the lattice, to rounding).

The JSON written next to the particle file records every parameter and the references
of this directory for the sampled ball: the volume radius R_vol = (3 N hxi^3/(4 pi))^(1/3)
of the lattice ball (its density is what the deposit sees) is used as R_L of the
reference, with M = 1/2; ellipsoid.evolve (placement "isolated") gives the first and
second collapse, the axes and the hoop ratio; for alpha = beta = gamma the cycloid
(tophat.cycloid) gives turnaround and collapse.
"""
import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

import numpy as np  # noqa: E402

import ellipsoid as el  # noqa: E402
import tophat as th  # noqa: E402
from nrpic import io as nio  # noqa: E402

M_PATCH = th.M_K          # 1/2


def random_rotation(seed):
    """Uniform random rotation matrix (QR of a Gaussian matrix, sign-fixed)."""
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q @ np.diag(np.sign(np.diag(r)))
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    return q


def lattice_ball(hxi, rot=None):
    """Lattice points (i + 1/2) hxi inside the unit sphere, optionally rotated."""
    nh = int(np.ceil(1.0 / hxi)) + 2
    g = (np.arange(-nh, nh) + 0.5) * hxi
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    xi = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    if rot is not None:
        xi = xi @ rot.T
    keep = (xi * xi).sum(axis=1) < 1.0
    return xi[keep]


def build(lams, a0=None, hxi=0.025, rotate=None):
    lams = np.asarray(lams, dtype=float)
    if a0 is None:
        a0 = 0.5 / lams.max()
    rot = random_rotation(rotate) if rotate is not None else None
    xi = lattice_ball(hxi, rot)
    n = len(xi)
    m = np.full(n, M_PATCH / n)
    t0 = float(th.t_of_a(a0))
    H0 = float(th.hubble(t0))
    x = a0 * (1.0 - a0 * lams)[None, :] * xi
    v = H0 * a0 * (1.0 - 2.0 * a0 * lams)[None, :] * xi
    x -= (m[:, None] * x).sum(0) / m.sum()
    v -= (m[:, None] * v).sum(0) / m.sum()
    r_vol = (3.0 * n * hxi ** 3 / (4.0 * np.pi)) ** (1.0 / 3.0)
    c_xi = (xi * xi).sum(0) / n                      # per-axis second moment of the sample
    r_mom = np.sqrt(5.0 * c_xi)                      # radius of the ball with that moment
    return dict(x=x, v=v, m=m, a0=a0, t0=t0, H0=H0, n=n, r_vol=r_vol,
                r_mom=r_mom.tolist(), rot=None if rot is None else rot.tolist())


def references(lams, a0, r_vol, n_collapse=2):
    lams = np.asarray(lams, dtype=float)
    out = {}
    ev = el.evolve(lams, a0=a0, model="isolated", RL=(r_vol,) * 3, M=M_PATCH,
                   n_collapse=n_collapse)
    out["ellipsoid_isolated"] = dict(
        t0=ev["t0"], collapses=[dict(t=c["t"], axis=c["axis"], A=c["A"], h=c["h"])
                                for c in ev["collapses"]],
        A_max=float(np.abs(ev["A"]).max()),
        turnarounds=ev["turnarounds"])
    if np.allclose(lams, lams[0]):
        R0, V0, t0 = th.za_sphere(lams[0], a0, r_vol)
        cyc = th.cycloid(R0, V0, t0, M=M_PATCH)
        out["cycloid"] = dict(R0=R0, V0=V0, t0=t0, t_ta=float(cyc["t_ta"]),
                              t_c=float(cyc["t_c"]), R_max=float(cyc["R_max"]),
                              A=float(cyc["A"]), B=float(cyc["B"]),
                              t_off=float(cyc["t_off"]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dep", nargs=3, type=float, metavar=("DELTA_L", "E", "P"))
    g.add_argument("--abg", nargs=3, type=float, metavar=("ALPHA", "BETA", "GAMMA"))
    ap.add_argument("--a0", type=float, default=None)
    ap.add_argument("--hxi", type=float, default=0.025)
    ap.add_argument("--rotate", type=int, default=None, help="seed of a random lattice rotation")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    lams = el.abg_from_dep(*a.dep) if a.dep else tuple(a.abg)
    b = build(lams, a.a0, a.hxi, a.rotate)
    nio.write_nrp(a.out, b["x"], b["v"], b["m"])
    e, p = el.ep_from_abg(*lams)
    meta = dict(generator="tracks/A-emd-pbh/newton/make_deformed_ball.py",
                units="2605.04487: G = c = 1, H_k = 1, t_k = 2/3, R_L = 1, M = 1/2, r_g = 1",
                time_origin="code time 0 is reference time t0",
                abg=list(map(float, lams)), deltaL=float(sum(lams)), e=float(e), p=float(p),
                a0=b["a0"], t0=b["t0"], H0=b["H0"], hxi=a.hxi, rotate=a.rotate,
                rotation=b["rot"], n=b["n"], mass=M_PATCH, r_vol=b["r_vol"],
                r_mom=b["r_mom"],
                semi_axes_start=(b["a0"] * (1.0 - b["a0"] * np.asarray(lams)) * b["r_vol"]).tolist(),
                reference=references(lams, b["a0"], b["r_vol"]))
    jpath = a.json or os.path.splitext(a.out)[0] + ".json"
    with open(jpath, "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print(f"wrote {a.out}: {b['n']} particles, r_vol = {b['r_vol']:.6f}, a0 = {b['a0']:.6f}, "
          f"t0 = {b['t0']:.6f}")


if __name__ == "__main__":
    main()
