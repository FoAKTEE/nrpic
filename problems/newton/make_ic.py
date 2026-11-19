#!/usr/bin/env python3
"""Particle files for the tests of the Newtonian mode (problems/newton/README.md).

    make_ic.py point --out point.nrp [--center X Y Z] [--ntracer 2000] [--seed 1]
    make_ic.py ball  --out ball.nrp  [--center X Y Z] [--radius 1] [--mass 1]
                     [--spacing 0.015625] [--ntracer 2000] [--seed 1]
                     [--velocity VX VY VZ] [--omega WX WY WZ]
                     [--axes S1 S2 S3] [--vgrad D1 D2 D3] [--rotate SEED]
                     [--background X0 X1 NB RHO]
    make_ic.py wave  --out wave.nrp  [--n 32] [--L 4] [--amp 0.25] [--hubble 1]

point  a unit mass and massless tracers at rest around it, log-uniform in distance
       between --rmin and --rmax, isotropic.
ball   a homogeneous ball at rest: equal-mass particles on a cubic lattice of the given
       spacing with nodes at center + (i + 1/2) spacing, kept where |x - center| <
       radius; massless tracers at rest, uniform in distance between --rmin and --rmax.
       --velocity adds a uniform velocity and --omega a rigid rotation about the centre
       to the massive particles.
       Deformed ball (Zel'dovich ellipsoid): with the lattice points xi relative to the
       centre, --axes maps the positions to x = center + S xi and --vgrad adds the
       velocity D xi, both diagonal (S = a0 (1 - a0 lambda_i), D = H0 a0 (1 - 2 a0
       lambda_i) is the Zel'dovich map of a homogeneous ball in physical coordinates;
       D = (V_i/R_i - H) S_i the peculiar momentum in comoving coordinates). --rotate
       turns the lattice by a random rotation (seed) before the selection, so that it is
       not aligned with the axes of the deformation. Centre of mass and net momentum of
       the ball are then set to the centre and to --velocity. The JSON records the
       volume radius of the lattice ball, (3 N spacing^3/(4 pi))^(1/3) (the density the
       deposit sees is that of a ball of this radius), and the radius sqrt(5 <xi_i^2>)
       of the ball with the second moment of the sample along each axis.
       --background X0 X1 NB RHO adds particles of species 1 at rest on the lattice
       X0 + (i + 1/2)(X1 - X0)/NB, i = 0 .. NB-1 in each direction, outside the
       (deformed) ball, each of mass RHO ((X1 - X0)/NB)^3: a homogeneous background of
       density RHO around the patch (species 0) in a periodic box.
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


def random_rotation(seed):
    """Uniform random rotation matrix (QR of a Gaussian matrix, signs fixed)."""
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q @ np.diag(np.sign(np.diag(r)))
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    return q


def deformed_ball(a, c):
    """Lattice ball with the options --axes, --vgrad, --rotate: positions, velocities,
    masses and the metadata of the sample."""
    S = np.ones(3) if a.axes is None else np.array(a.axes, dtype=float)
    D = np.zeros(3) if a.vgrad is None else np.array(a.vgrad, dtype=float)
    rot = random_rotation(a.rotate) if a.rotate is not None else None
    nh = int(np.ceil(a.radius/a.spacing)) + 2
    g = (np.arange(-nh, nh) + 0.5)*a.spacing
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    xi = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    if rot is not None:
        xi = xi @ rot.T
    xi = xi[(xi*xi).sum(axis=1) < a.radius**2]
    n = len(xi)
    m = np.full(n, a.mass/n)
    x = S[None, :]*xi
    v = D[None, :]*xi + np.cross(np.array(a.omega), x)
    x -= (m[:, None]*x).sum(axis=0)/m.sum()
    v -= (m[:, None]*v).sum(axis=0)/m.sum()
    meta = dict(axes=S.tolist(), vgrad=D.tolist(), rotate=a.rotate,
                rotation=None if rot is None else rot.tolist(),
                r_vol=float((3.0*n*a.spacing**3/(4.0*np.pi))**(1.0/3.0)),
                r_mom=np.sqrt(5.0*(xi*xi).sum(axis=0)/n).tolist(),
                semi_axes=(S*a.radius).tolist())
    return c + x, np.array(a.velocity) + v, m, meta


def background(a, c):
    """Lattice of the option --background outside the deformed ball."""
    x0, x1, nbg, rho = a.background
    nbg = int(round(nbg))
    h = (x1 - x0)/nbg
    S = np.ones(3) if a.axes is None else np.array(a.axes, dtype=float)
    g = x0 + (np.arange(nbg) + 0.5)*h
    out = []
    Y, Z = np.meshgrid(g, g, indexing="ij")
    for gx in g:                      # slab by slab: bounded memory
        r2 = ((gx - c[0])/S[0])**2 + ((Y - c[1])/S[1])**2 + ((Z - c[2])/S[2])**2
        k = r2 >= a.radius**2
        if k.any():
            out.append(np.stack([np.full(k.sum(), gx), Y[k], Z[k]], axis=1))
    xg = np.concatenate(out) if out else np.zeros((0, 3))
    return xg, np.full(len(xg), rho*h**3)


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
    ap.add_argument("--velocity", type=float, nargs=3, default=[0.0, 0.0, 0.0])
    ap.add_argument("--omega", type=float, nargs=3, default=[0.0, 0.0, 0.0])
    ap.add_argument("--axes", type=float, nargs=3, default=None)
    ap.add_argument("--vgrad", type=float, nargs=3, default=None)
    ap.add_argument("--rotate", type=int, default=None)
    ap.add_argument("--background", type=float, nargs=4, default=None,
                    metavar=("X0", "X1", "NB", "RHO"))
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
        deformed = (a.axes is not None or a.vgrad is not None or a.rotate is not None
                    or a.background is not None)
        if not deformed:
            nh = int(np.ceil(a.radius/a.spacing)) + 1
            g = (np.arange(-nh, nh) + 0.5)*a.spacing
            X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
            keep = X*X + Y*Y + Z*Z < a.radius**2
            xb = c + np.stack([X[keep], Y[keep], Z[keep]], axis=1)
            nb = len(xb)
            ub = np.array(a.velocity) + np.cross(np.array(a.omega), xb - c)
            mb = np.full(nb, a.mass/nb)
        else:
            xb, ub, mb, dmeta = deformed_ball(a, c)
            nb = len(xb)
            meta.update(dmeta)
        r = rng.uniform(a.rmin, a.rmax, size=a.ntracer)
        xt = c + r[:, None]*directions(rng, a.ntracer)
        x = np.vstack([xb, xt])
        m = np.concatenate([mb, np.zeros(a.ntracer)])
        uall = np.vstack([ub, np.zeros((a.ntracer, 3))])
        species = np.zeros(len(x), dtype=np.int32)
        if a.background is not None:
            xg, mg = background(a, c)
            # massive particles first: ball, background, then the tracers
            x = np.vstack([xb, xg, xt])
            m = np.concatenate([mb, mg, np.zeros(a.ntracer)])
            uall = np.vstack([ub, np.zeros((len(xg), 3)), np.zeros((a.ntracer, 3))])
            species = np.concatenate([np.zeros(nb, dtype=np.int32),
                                      np.ones(len(xg), dtype=np.int32),
                                      np.zeros(a.ntracer, dtype=np.int32)])
            meta.update(nbackground=len(xg), background=a.background,
                        background_mass=float(mg.sum()))
        meta.update(center=a.center, mass=a.mass, radius=a.radius, spacing=a.spacing,
                    nmassive=len(x) - a.ntracer, nball=nb, ntracer=a.ntracer,
                    velocity=a.velocity, omega=a.omega)
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
        if a.kind == "ball":
            nio.write_nrp(a.out, x, uall, m, species if species.any() else None)
        else:
            nio.write_nrp(a.out, x, np.zeros_like(x), m)
    with open(os.path.splitext(a.out)[0] + ".json", "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s: %d massive particles, %d tracers" % (a.out, meta["nmassive"],
                                                          meta["ntracer"]))


if __name__ == "__main__":
    main()
