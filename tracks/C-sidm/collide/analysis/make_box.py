#!/usr/bin/env python3
"""Particle files (NRPIC001) and metadata for the Minkowski-box tests of TESTS.md.

    python3 make_box.py KIND --out PREFIX [options]

KIND: mj | twotemp | step | mode | boosted | unequal
Writes PREFIX.nrp and PREFIX.json (all parameters, derived scales: number density,
mean free path lambda = 1/(rho_0 sigma/m), mean collision time 1/Gamma, the box, the
recommended mesh and step). Positions are a Poisson process (independent uniform draws)
in the box [x0, x0 + Lx) x [y0, y0 + Ly) x [z0, z0 + Lz); x0 = y0 = z0 = 10 keeps the box
away from the origin of the Kerr-Schild functor (bh_mass = 0 makes it flat, but it
divides by r). Momenta are drawn in mirrored pairs (u, -u) within each population, so
every population has zero net momentum exactly. All macroparticles have the same rest
mass M = rho_0 V / N unless KIND = unequal. Units G = c = 1, particle mass scale m = 1:
u is the four-velocity per unit mass, theta = T/m.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "REFERENCES"))
sys.path.insert(0, HERE)
import mj                      # noqa: E402
import rate                    # noqa: E402
import snap                    # noqa: E402

X0 = 10.0


def mirrored(n, theta, rng, sampler=None):
    h = (n + 1) // 2
    u = mj.sample_u(h, theta, rng, sampler)
    out = np.concatenate([u, -u])[:n]
    return out


def positions(n, box, rng):
    return X0 + rng.uniform(0.0, 1.0, (n, 3)) * np.asarray(box)[None, :]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["mj", "twotemp", "step", "mode", "boosted", "unequal"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=100000, help="number of particles")
    ap.add_argument("--box", type=float, nargs=3, default=[1.0, 1.0, 1.0])
    ap.add_argument("--rho0", type=float, default=1.0, help="rest-mass density (mean)")
    ap.add_argument("--sigma", type=float, default=1.0, help="cross-section per unit mass")
    ap.add_argument("--theta", type=float, default=0.01)
    ap.add_argument("--theta2", type=float, default=None, help="second temperature")
    ap.add_argument("--frac1", type=float, default=0.5, help="number fraction of pop. 1")
    ap.add_argument("--eps", type=float, default=0.1, help="mode amplitude dT/T")
    ap.add_argument("--kmode", type=int, default=1, help="mode number along x")
    ap.add_argument("--beta", type=float, default=0.5, help="drift velocity along x")
    ap.add_argument("--wratio", type=float, default=4.0, help="mass ratio of classes")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    box = np.array(a.box)
    V = float(np.prod(box))
    N = a.n
    meta = dict(kind=a.kind, n=N, box=box.tolist(), x0=X0, rho0=a.rho0, sigma=a.sigma,
                seed=a.seed, theta=a.theta)
    species = np.zeros(N, dtype=np.int32)
    m = np.full(N, a.rho0 * V / N)
    if a.kind == "mj":
        x = positions(N, box, rng)
        u = mirrored(N, a.theta, rng)
    elif a.kind == "twotemp":
        t2 = a.theta2 if a.theta2 is not None else a.theta / 3.0
        n1 = int(round(a.frac1 * N))
        x = positions(N, box, rng)
        u = np.concatenate([mirrored(n1, a.theta, rng), mirrored(N - n1, t2, rng)])
        species[n1:] = 1
        meta.update(theta1=a.theta, theta2=t2, n_pop1=n1, n_pop2=N - n1,
                    note="population 1 = tags [0, n_pop1), species 0; population 2 "
                         "species 1 (species are labels only; collisions must treat all "
                         "particles as one physical species)")
    elif a.kind == "step":
        t2 = a.theta2 if a.theta2 is not None else a.theta / 1.2
        # equal pressure: n1 theta1 = n2 theta2, slabs of equal volume
        w1 = 1.0 / a.theta
        w2 = 1.0 / t2
        n1 = int(round(N * w1 / (w1 + w2)))
        xl = positions(n1, [box[0] / 2, box[1], box[2]], rng)
        xr = positions(N - n1, [box[0] / 2, box[1], box[2]], rng)
        xr[:, 0] += box[0] / 2
        x = np.concatenate([xl, xr])
        u = np.concatenate([mirrored(n1, a.theta, rng), mirrored(N - n1, t2, rng)])
        species[n1:] = 1
        meta.update(theta1=a.theta, theta2=t2, n_left=n1, n_right=N - n1,
                    n_dens1=n1 / (V / 2), n_dens2=(N - n1) / (V / 2))
    elif a.kind == "mode":
        k = 2 * np.pi * a.kmode / box[0]
        # positions with density 1 - eps cos(kx): rejection
        xs = []
        have = 0
        while have < N:
            xx = rng.uniform(0, box[0], 2 * N)
            acc = rng.uniform(0, 1 + a.eps, 2 * N) < 1 - a.eps * np.cos(k * xx)
            xs.append(xx[acc]); have += acc.sum()
        xx = np.concatenate(xs)[:N]
        nb = 256 * a.kmode
        ib = np.minimum((xx / box[0] * nb).astype(int), nb - 1)
        u = np.empty((N, 3))
        for b in range(nb):
            sel = np.flatnonzero(ib == b)
            if sel.size == 0:
                continue
            xc = (b + 0.5) / nb * box[0]
            th = a.theta * (1 + a.eps * np.cos(k * xc))
            u[sel] = mirrored(sel.size, th, rng)
        x = np.empty((N, 3))
        x[:, 0] = X0 + xx
        x[:, 1:] = X0 + rng.uniform(0, 1, (N, 2)) * box[1:][None, :]
        meta.update(eps=a.eps, kmode=a.kmode, k=k, nbins_theta=nb)
    elif a.kind == "boosted":
        x = positions(N, box, rng)
        u = mj.sample_u_boosted(N, a.theta, np.array([a.beta, 0, 0]), rng)
        meta.update(beta=a.beta, note="lab-frame Juttner gas drifting along +x; "
                                      "net momentum not zero")
    elif a.kind == "unequal":
        # class A: mass M, class B: mass wratio*M, equal total rest mass in each class
        nB = int(round(N / (1 + a.wratio)))
        nA = N - nB
        MA = 0.5 * a.rho0 * V / nA
        MB = 0.5 * a.rho0 * V / nB
        t2 = a.theta2 if a.theta2 is not None else a.theta / 3.0
        x = positions(N, box, rng)
        u = np.concatenate([mirrored(nA, a.theta, rng), mirrored(nB, t2, rng)])
        m = np.concatenate([np.full(nA, MA), np.full(nB, MB)])
        species[nA:] = 1
        meta.update(n_classA=nA, n_classB=nB, MA=MA, MB=MB, thetaA=a.theta, thetaB=t2,
                    wratio=MB / MA)
    # derived scales (rest frame, homogeneous mean values)
    n_dens = N / V          # macroparticles per volume (equal masses)
    th_ref = a.theta
    gam = a.rho0 * a.sigma * float(rate.vmol_mean(th_ref))
    lam = 1.0 / (a.rho0 * a.sigma) if a.sigma > 0 else None     # None: collisionless
    meta.update(lambda_mfp=lam, Gamma_coll=gam, t_coll=1.0 / gam if gam > 0 else None,
                knudsen_x=lam / box[0] if lam else None,
                particles_per_lambda3=n_dens * lam ** 3 if lam else None,
                recommended=dict(
                    cells_x=int(np.ceil(4 * box[0] / lam)) if lam else None,
                    note="cells of at most lambda/4; at least 20 particles per cell; "
                         "dt at most 0.1 t_coll and below the cell crossing time"))
    snap.write_nrp(a.out + ".nrp", x, u, m, species)
    with open(a.out + ".json", "w") as fh:
        json.dump(meta, fh, indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
