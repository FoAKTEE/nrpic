#!/usr/bin/env python3
"""Particle files for the tests of the Newtonian mode (problems/newton/README.md).

    make_ic.py point --out point.nrp [--center X Y Z] [--ntracer 2000] [--seed 1]
    make_ic.py ball  --out ball.nrp  [--center X Y Z] [--radius 1] [--mass 1]
                     [--spacing 0.015625] [--ntracer 2000] [--seed 1]
    make_ic.py wave  --out wave.nrp  [--n 32] [--L 4] [--amp 0.25] [--hubble 1]

point  a unit mass and massless tracers at rest around it, log-uniform in distance
       between --rmin and --rmax, isotropic.
ball   a homogeneous ball at rest: equal-mass particles on a cubic lattice of the given
       spacing with nodes at center + (i + 1/2) spacing, kept where |x - center| <
       radius; massless tracers at rest, uniform in distance between --rmin and --rmax.
wave   a plane wave along x in a matter-dominated background, Zel'dovich solution at
       a = 1 (python/nrpic/newton.py, zeldovich_wave): n^3 equal-mass particles on the
       lattice q = (i + 1/2) L/n, x = q + (amp/k) cos(k q_x), p_x = hubble (amp/k)
       cos(k q_x), k = 2 pi/L, mean density 3 hubble^2/(8 pi) (G = 1).
The tag of a particle in the run is its position in the file; a JSON file next to the
particle file records the parameters and the number of massive particles (they come
first).
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402

from nrpic import io as nio  # noqa: E402
from nrpic import newton as nw  # noqa: E402


def directions(rng, n):
    d = rng.normal(size=(n, 3))
    return d/np.sqrt((d*d).sum(axis=1))[:, None]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("point", "ball", "wave"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--center", type=float, nargs=3, default=[0.0, 0.0, 0.0])
    ap.add_argument("--radius", type=float, default=1.0)
    ap.add_argument("--mass", type=float, default=1.0)
    ap.add_argument("--spacing", type=float, default=1.0/64.0)
    ap.add_argument("--ntracer", type=int, default=2000)
    ap.add_argument("--rmin", type=float, default=0.05)
    ap.add_argument("--rmax", type=float, default=1.8)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--L", type=float, default=4.0)
    ap.add_argument("--amp", type=float, default=0.25)
    ap.add_argument("--hubble", type=float, default=1.0)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    c = np.array(a.center)
    meta = dict(kind=a.kind)

    if a.kind == "point":
        r = np.exp(rng.uniform(np.log(a.rmin), np.log(a.rmax), size=a.ntracer))
        xt = c + r[:, None]*directions(rng, a.ntracer)
        x = np.vstack([c[None, :], xt])
        m = np.concatenate([[a.mass], np.zeros(a.ntracer)])
        meta.update(center=a.center, mass=a.mass, nmassive=1, ntracer=a.ntracer)
    elif a.kind == "ball":
        nh = int(np.ceil(a.radius/a.spacing)) + 1
        g = (np.arange(-nh, nh) + 0.5)*a.spacing
        X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
        keep = X*X + Y*Y + Z*Z < a.radius**2
        xb = c + np.stack([X[keep], Y[keep], Z[keep]], axis=1)
        nb = len(xb)
        r = rng.uniform(a.rmin, a.rmax, size=a.ntracer)
        xt = c + r[:, None]*directions(rng, a.ntracer)
        x = np.vstack([xb, xt])
        m = np.concatenate([np.full(nb, a.mass/nb), np.zeros(a.ntracer)])
        meta.update(center=a.center, mass=a.mass, radius=a.radius, spacing=a.spacing,
                    nmassive=nb, ntracer=a.ntracer)
    else:
        k = 2.0*np.pi/a.L
        h = a.L/a.n
        q1 = (np.arange(a.n) + 0.5)*h
        Q = np.meshgrid(q1, q1, q1, indexing="ij")
        q = np.stack([f.ravel() for f in Q], axis=1)
        xx, px = nw.zeldovich_wave(q[:, 0], 1.0, a.amp, k, a.hubble)
        x = q.copy()
        x[:, 0] = np.mod(xx, a.L)
        u = np.zeros_like(x)
        u[:, 0] = px
        rho0 = 3.0*a.hubble**2/(8.0*np.pi)
        m = np.full(len(x), rho0*h**3)
        nio.write_nrp(a.out, x, u, m)
        meta.update(n=a.n, L=a.L, amp=a.amp, hubble=a.hubble, nmassive=len(x), ntracer=0)
        x = None
    if x is not None:
        nio.write_nrp(a.out, x, np.zeros_like(x), m)
    with open(os.path.splitext(a.out)[0] + ".json", "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s: %d massive particles, %d tracers" % (a.out, meta["nmassive"],
                                                          meta["ntracer"]))


if __name__ == "__main__":
    main()
