#!/usr/bin/env python3
"""Particle files for the tests of the initial-data solver of the code
(<particles> id_solve; tracks/core/interfaces/id_solver.md).

    make_ic.py gaussian --mass 1 --sigma 2 --h 0.25 --out DIR
        Particles at rest on the lattice (k + 1/2) h inside r <= rcut sigma with masses
        rhot(x) psi_ex(x) h^3, where rhot is the normalised Gaussian conformal source of
        the nrpic_cf component "gaussian" and psi_ex = 1 + (m/2) erf(r/(sqrt 2 sigma))/r
        its conformal factor: the deposited density per coordinate volume is
        Etilde = rhot psi_ex, for which psi_ex solves lap psi = -2 pi psi^-1 Etilde.
    make_ic.py strain --in ball.nrp --e 0.05 --out DIR
        Copy of a particle file with the positions scaled by (1 + e, 1, 1 - e).
    make_ic.py boost --in gauss.nrp --u 0.1 --out DIR
        Copy of a particle file with the covariant velocity u_x of every particle set to
        the given value (the test of the vector equation, <particles> id_vector).
    make_ic.py wave --n 32 --box 2 --hubble 1 --amp 0.1 [--ppc 2] --out DIR
        Particles at rest on a lattice with ppc sites per cell and direction of an n^3
        mesh of side box (sites (k + 1/2) dx/ppc; ppc = 1: the cell centres), displaced
        along x by -(amp/k) sin(k x), k = 2 pi/box (density contrast amp cos(k x) to
        first order), equal masses with mean density 3 H^2/(8 pi).  With ppc = 1 every
        particle starts at the kink of the cloud-in-cell weight, and the deposited
        density has a jump of one cell where the displacement changes sign.

Each call writes the particle file and a JSON file with the parameters.
File formats: docs/FORMATS.md. Units G = c = 1.
"""
import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "python")))

import numpy as np  # noqa: E402
from scipy.special import erf  # noqa: E402

from nrpic import io as nio  # noqa: E402


def gaussian_psi(r, mass, sigma):
    """Conformal factor of the nrpic_cf component "gaussian"."""
    r = np.asarray(r, dtype=float)
    q = r/(np.sqrt(2.0)*sigma)
    out = np.full(r.shape, 1.0 + mass/(np.sqrt(2.0*np.pi)*sigma))
    big = q > 1.0e-6
    out[big] = 1.0 + 0.5*mass*erf(q[big])/r[big]
    return out


def gaussian_source(r, mass, sigma):
    """Its conformal source rhot: lap psi = -2 pi rhot."""
    return mass*np.exp(-0.5*(np.asarray(r)/sigma)**2)/(2.0*np.pi*sigma**2)**1.5


def cmd_gaussian(a):
    rc = a.rcut*a.sigma
    n = int(np.ceil(rc/a.h))
    c = (np.arange(-n, n) + 0.5)*a.h
    x, y, z = np.meshgrid(c, c, c, indexing="ij")
    r = np.sqrt(x*x + y*y + z*z).ravel()
    keep = r <= rc
    pos = np.stack([x.ravel()[keep], y.ravel()[keep], z.ravel()[keep]], axis=1)
    r = r[keep]
    m = gaussian_source(r, a.mass, a.sigma)*gaussian_psi(r, a.mass, a.sigma)*a.h**3
    stem = a.prefix or "gauss_h%g" % a.h
    stem = stem.replace(".", "p")
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), pos, np.zeros_like(pos), m)
    meta = dict(kind="gaussian", mass=a.mass, sigma=a.sigma, h=a.h, rcut=rc,
                N=int(len(m)), sum_m=float(m.sum()), particle_file=stem + ".nrp",
                psi_centre=float(gaussian_psi(np.zeros(1), a.mass, a.sigma)[0]),
                problem_block=dict(pgen_name="nrpic_cf", ncomp=1, comp0_type="gaussian",
                                   comp0_mass=a.mass, comp0_sigma=a.sigma))
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles, sum m = %.12g" % (stem, len(m), m.sum()))


def cmd_strain(a):
    x, u, m, sp = nio.read_nrp(a.inp)
    x = np.array(x)
    x[:, 0] *= 1.0 + a.e
    x[:, 2] *= 1.0 - a.e
    stem = a.prefix or (os.path.splitext(os.path.basename(a.inp))[0]
                        + ("_e%g" % a.e).replace(".", "p"))
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), x, u, m, sp)
    meta = dict(kind="strain", source=os.path.basename(a.inp), e=a.e,
                scale=[1.0 + a.e, 1.0, 1.0 - a.e], N=int(len(m)),
                particle_file=stem + ".nrp")
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles" % (stem, len(m)))


def cmd_boost(a):
    x, u, m, sp = nio.read_nrp(a.inp)
    u = np.array(u)
    u[:, 0] = a.u
    stem = a.prefix or (os.path.splitext(os.path.basename(a.inp))[0]
                        + ("_u%g" % a.u).replace(".", "p"))
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), x, u, m, sp)
    meta = dict(kind="boost", source=os.path.basename(a.inp), u_x=a.u, N=int(len(m)),
                sum_m=float(np.sum(m)), P_x=float(a.u*np.sum(m)), particle_file=stem + ".nrp")
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles, sum m u_x = %.12g" % (stem, len(m), a.u*np.sum(m)))


def cmd_shift(a):
    x, u, m, sp = nio.read_nrp(a.inp)
    x = np.array(x) + np.array(a.d)[None, :]
    stem = a.prefix or (os.path.splitext(os.path.basename(a.inp))[0] + "_shift")
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), x, u, m, sp)
    meta = dict(kind="shift", source=os.path.basename(a.inp), d=list(a.d), N=int(len(m)),
                sum_m=float(np.sum(m)), sum_mu=[float(v) for v in (m[:, None]*u).sum(axis=0)],
                particle_file=stem + ".nrp")
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles" % (stem, len(m)))


def cmd_zeldovich(a):
    """Homogeneous Zel'dovich displacement of a ball in its growing mode: the Lagrangian
    position q goes to x_i = (1 + e_i) q_i and the particle gets the peculiar momentum
    u_i = H e_i q_i relative to the normal observers of the slice (physical displacement
    times the Hubble rate: growth factor proportional to the scale factor in a matter era)."""
    x, u, m, sp = nio.read_nrp(a.inp)
    q = np.array(x)
    e = np.array(a.strain if a.strain is not None else [a.e, 0.0, -a.e])
    x = q*(1.0 + e)[None, :]
    u = np.array(u) + a.hubble*e[None, :]*q
    stem = a.prefix or (os.path.splitext(os.path.basename(a.inp))[0]
                        + ("_z%g" % a.e).replace(".", "p"))
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), x, u, m, sp)
    meta = dict(kind="zeldovich", source=os.path.basename(a.inp), strain=[float(v) for v in e],
                hubble=a.hubble, N=int(len(m)), sum_m=float(np.sum(m)),
                sum_mu=[float(v) for v in (np.array(m)[:, None]*u).sum(axis=0)],
                particle_file=stem + ".nrp")
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles, strain %s, max|u| = %.4g" %
          (stem, len(m), e, np.abs(u).max()))


def cmd_wave(a):
    """Plane wave on the torus: lattice sites q displaced along x by -(A/k) sin(k q_x).
    --ppc lattice sites per cell and direction; --nest lo hi: inside the Lagrangian cube
    [lo, hi)^3 the lattice is twice finer and the masses eight times smaller (for a
    refined region of the mesh); --velocity: the momentum of the growing mode,
    u_x = H times the displacement."""
    h = a.box/(a.n*a.ppc)
    c = (np.arange(a.n*a.ppc) + 0.5)*h
    x, y, z = np.meshgrid(c, c, c, indexing="ij")
    q = np.stack([x.ravel(), y.ravel(), z.ravel()], axis=1)
    rho = 3.0*a.hubble**2/(8.0*np.pi)
    m = np.full(len(q), rho*h**3)
    if a.nest is not None:
        lo, hi = a.nest
        inside = np.all((q >= lo) & (q < hi), axis=1)
        nf = int(round((hi - lo)/(0.5*h)))
        cf = lo + (np.arange(nf) + 0.5)*0.5*h
        xf, yf, zf = np.meshgrid(cf, cf, cf, indexing="ij")
        qf = np.stack([xf.ravel(), yf.ravel(), zf.ravel()], axis=1)
        q = np.concatenate([q[~inside], qf])
        m = np.concatenate([m[~inside], np.full(len(qf), rho*h**3/8.0)])
    k = 2.0*np.pi/a.box
    disp = -(a.amp/k)*np.sin(k*q[:, 0])
    pos = np.array(q)
    pos[:, 0] = (q[:, 0] + disp) % a.box
    u = np.zeros_like(pos)
    if a.velocity:
        u[:, 0] = a.hubble*disp
    stem = a.prefix or ("wave_n%d" % a.n + ("_p%d" % a.ppc if a.ppc > 1 else ""))
    os.makedirs(a.out, exist_ok=True)
    nio.write_nrp(os.path.join(a.out, stem + ".nrp"), pos, u, m)
    meta = dict(kind="wave", n=a.n, ppc=a.ppc, box=a.box, hubble=a.hubble, amp=a.amp, k=k,
                rho_mean=rho, N=int(len(m)), particle_file=stem + ".nrp",
                nest=list(a.nest) if a.nest is not None else None, velocity=bool(a.velocity),
                sum_m=float(m.sum()), sum_mu_x=float((m*u[:, 0]).sum()))
    with open(os.path.join(a.out, stem + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("wrote %s.nrp: %d particles, mean density %.12g" % (stem, len(m),
                                                             m.sum()/a.box**3))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gaussian")
    g.add_argument("--mass", type=float, default=1.0)
    g.add_argument("--sigma", type=float, default=2.0)
    g.add_argument("--h", type=float, required=True, help="lattice spacing")
    g.add_argument("--rcut", type=float, default=7.0, help="radius of the lattice in sigma")
    g.add_argument("--out", default=".")
    g.add_argument("--prefix", default=None)
    g.set_defaults(func=cmd_gaussian)
    s = sub.add_parser("strain")
    s.add_argument("--in", dest="inp", required=True)
    s.add_argument("--e", type=float, default=0.05)
    s.add_argument("--out", default=".")
    s.add_argument("--prefix", default=None)
    s.set_defaults(func=cmd_strain)
    b = sub.add_parser("boost")
    b.add_argument("--in", dest="inp", required=True)
    b.add_argument("--u", type=float, default=0.1, help="covariant u_x of every particle")
    b.add_argument("--out", default=".")
    b.add_argument("--prefix", default=None)
    b.set_defaults(func=cmd_boost)
    sh = sub.add_parser("shift", help="a copy with every position displaced")
    sh.add_argument("--in", dest="inp", required=True)
    sh.add_argument("--d", type=float, nargs=3, required=True)
    sh.add_argument("--out", default=".")
    sh.add_argument("--prefix", default=None)
    sh.set_defaults(func=cmd_shift)
    z = sub.add_parser("zeldovich", help="triaxial Zel'dovich displacement with its momenta")
    z.add_argument("--in", dest="inp", required=True)
    z.add_argument("--e", type=float, default=0.05, help="strain (e, 0, -e)")
    z.add_argument("--strain", type=float, nargs=3, default=None, help="strain per axis")
    z.add_argument("--hubble", type=float, required=True, help="Hubble rate of the ball")
    z.add_argument("--out", default=".")
    z.add_argument("--prefix", default=None)
    z.set_defaults(func=cmd_zeldovich)
    w = sub.add_parser("wave")
    w.add_argument("--n", type=int, required=True)
    w.add_argument("--box", type=float, default=2.0)
    w.add_argument("--hubble", type=float, default=1.0)
    w.add_argument("--amp", type=float, default=0.1)
    w.add_argument("--ppc", type=int, default=1, help="lattice sites per cell and direction")
    w.add_argument("--nest", type=float, nargs=2, default=None,
                   help="Lagrangian cube [lo, hi)^3 with a lattice twice finer")
    w.add_argument("--velocity", action="store_true",
                   help="momentum of the growing mode, u_x = H times the displacement")
    w.add_argument("--out", default=".")
    w.add_argument("--prefix", default=None)
    w.set_defaults(func=cmd_wave)
    a = p.parse_args(argv)
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
